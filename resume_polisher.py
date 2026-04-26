import json
import os
import tempfile

import gradio as gr

from hf_client import generate_text
from resume_utils import extract_resume_text


def _safe_json_loads(raw_text: str, fallback):
    try:
        return json.loads(raw_text)
    except Exception:
        return fallback


def _extract_json_block(text: str):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def _generate_json(prompt: str, fallback):
    raw = generate_text(prompt, max_tokens=1200, temperature=0.2)
    json_text = _extract_json_block(raw)
    return _safe_json_loads(json_text, fallback)


def manager_chunk_resume(resume_text: str, position_name: str, polish_prompt: str = "") -> dict:
    prompt = (
        f"You are the Manager agent for a resume polishing pipeline.\n"
        f"Task: split the resume into structured sections for the target role: {position_name}.\n\n"
        f"Resume text:\n{resume_text}\n\n"
        f"Additional instructions:\n{polish_prompt}\n\n"
        "Return JSON ONLY with this schema:\n"
        "{\n"
        '  "title": string,\n'
        '  "name_line": string,\n'
        '  "contact_line": string,\n'
        '  "sections": [\n'
        '    {"type": "summary" | "experience" | "education" | "other", "heading": string, "content": string}\n'
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- Do not invent facts.\n"
        "- Preserve only information present in the source.\n"
        "- Group resume content into the most appropriate sections.\n"
        "- If a section is missing, omit it.\n"
        "- Output valid JSON only, no markdown, no explanation."
    )

    fallback = {
        "title": "",
        "name_line": "",
        "contact_line": "",
        "sections": [],
    }
    return _generate_json(prompt, fallback)


def worker_summary(section_text: str, position_name: str, polish_prompt: str = "") -> dict:
    prompt = (
        f"You are the Summary worker agent for a resume.\n"
        f"Target role: {position_name}\n\n"
        f"Source content:\n{section_text}\n\n"
        f"Additional instructions:\n{polish_prompt}\n\n"
        "Return JSON ONLY with this schema:\n"
        "{\n"
        '  "summary": string\n'
        "}\n\n"
        "Rules:\n"
        "- Write a concise ATS-friendly professional summary.\n"
        "- Use only source facts.\n"
        "- Output valid JSON only."
    )
    return _generate_json(prompt, {"summary": ""})


def worker_experience(section_text: str, position_name: str, polish_prompt: str = "") -> dict:
    prompt = (
        f"You are the Experience worker agent for a resume.\n"
        f"Target role: {position_name}\n\n"
        f"Source content:\n{section_text}\n\n"
        f"Additional instructions:\n{polish_prompt}\n\n"
        "Return JSON ONLY with this schema:\n"
        "{\n"
        '  "entries": [\n'
        "    {\n"
        '      "company": string,\n'
        '      "role": string,\n'
        '      "location": string,\n'
        '      "dates": string,\n'
        '      "bullets": [string]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- Keep bullet points concise and measurable when supported by the source.\n"
        "- Do not invent metrics, employers, or dates.\n"
        "- Every bullet must be a plain string.\n"
        "- Output valid JSON only."
    )
    return _generate_json(prompt, {"entries": []})


def worker_education(section_text: str, position_name: str, polish_prompt: str = "") -> dict:
    prompt = (
        f"You are the Education worker agent for a resume.\n"
        f"Target role: {position_name}\n\n"
        f"Source content:\n{section_text}\n\n"
        f"Additional instructions:\n{polish_prompt}\n\n"
        "Return JSON ONLY with this schema:\n"
        "{\n"
        '  "entries": [\n'
        "    {\n"
        '      "institution": string,\n'
        '      "credential": string,\n'
        '      "field": string,\n'
        '      "dates": string,\n'
        '      "details": [string]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- Preserve only education facts present in the source.\n"
        "- Keep details as plain strings.\n"
        "- Output valid JSON only."
    )
    return _generate_json(prompt, {"entries": []})


def make_pdf(resume_json: dict) -> str:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable,
        ListFlowable,
        ListItem,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
    )

    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=6,
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "ResumeSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        alignment=1,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        spaceBefore=8,
        spaceAfter=6,
        textColor="#111111",
    )
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        leftIndent=14,
        firstLineIndent=0,
        spaceAfter=2,
    )

    story = []

    title = (resume_json.get("title") or "").strip()
    name_line = (resume_json.get("name_line") or "").strip()
    contact_line = (resume_json.get("contact_line") or "").strip()

    if title:
        story.append(Paragraph(title, title_style))
    elif name_line:
        story.append(Paragraph(name_line, title_style))

    if contact_line:
        story.append(Paragraph(contact_line, subtitle_style))

    if title or name_line or contact_line:
        story.append(HRFlowable(width="100%", thickness=0.8, color="#666666"))
        story.append(Spacer(1, 8))

    def add_bullet_list(items):
        if not items:
            return
        list_items = [
            ListItem(Paragraph(str(item), bullet_style), leftIndent=10)
            for item in items
            if str(item).strip()
        ]
        if list_items:
            story.append(ListFlowable(list_items, bulletType="bullet", leftIndent=18))
            story.append(Spacer(1, 4))

    def add_summary(section_data: dict):
        summary = (section_data.get("summary") or "").strip()
        if summary:
            story.append(Paragraph(summary, body_style))
            story.append(Spacer(1, 4))

    def add_experience(section_data: dict):
        entries = section_data.get("entries") or []
        if not entries:
            return
        for entry in entries:
            company = (entry.get("company") or "").strip()
            role = (entry.get("role") or "").strip()
            location = (entry.get("location") or "").strip()
            dates = (entry.get("dates") or "").strip()
            header_parts = [part for part in [role, company] if part]
            header = " - ".join(header_parts) if header_parts else ""
            meta_parts = [part for part in [location, dates] if part]
            meta = " | ".join(meta_parts)

            if header:
                story.append(Paragraph(header, body_style))
            if meta:
                story.append(Paragraph(meta, body_style))

            add_bullet_list(entry.get("bullets") or [])
            story.append(Spacer(1, 2))

    def add_education(section_data: dict):
        entries = section_data.get("entries") or []
        if not entries:
            return
        for entry in entries:
            institution = (entry.get("institution") or "").strip()
            credential = (entry.get("credential") or "").strip()
            field = (entry.get("field") or "").strip()
            dates = (entry.get("dates") or "").strip()
            details = entry.get("details") or []

            header_parts = [part for part in [credential, field] if part]
            header = " - ".join(header_parts) if header_parts else ""
            meta_parts = [part for part in [institution, dates] if part]
            meta = " | ".join(meta_parts)

            if header:
                story.append(Paragraph(header, body_style))
            if meta:
                story.append(Paragraph(meta, body_style))
            add_bullet_list(details)
            story.append(Spacer(1, 2))

    section_handlers = {
        "summary": add_summary,
        "experience": add_experience,
        "education": add_education,
    }

    sections = resume_json.get("sections") or []
    for section in sections:
        section_type = (section.get("type") or "other").strip().lower()
        heading = (section.get("heading") or "").strip()
        content = section.get("content")

        if heading:
            story.append(Paragraph(heading.rstrip(":").title(), section_style))

        handler = section_handlers.get(section_type)
        if handler:
            if section_type == "summary":
                handler({"summary": content or section.get("summary") or ""})
            elif section_type in {"experience", "education"}:
                handler(section)
        else:
            if isinstance(content, str) and content.strip():
                story.append(Paragraph(content.strip(), body_style))
                story.append(Spacer(1, 4))

    if not story:
        story.append(Paragraph("No resume content available.", body_style))

    doc.build(story)
    return pdf_path


def polish_resume(position_name, resume_file=None, resume_content="", polish_prompt=""):
    resume_text = extract_resume_text(resume_file, resume_content)

    if not resume_text:
        return "Please provide either a resume upload or pasted resume text.", None

    manager_json = manager_chunk_resume(resume_text, position_name, polish_prompt)

    polished_resume = {
        "title": manager_json.get("title", ""),
        "name_line": manager_json.get("name_line", ""),
        "contact_line": manager_json.get("contact_line", ""),
        "sections": [],
    }

    for section in manager_json.get("sections", []):
        section_type = (section.get("type") or "").strip().lower()
        section_text = (section.get("content") or "").strip()

        if section_type == "summary":
            polished_resume["sections"].append(
                {
                    "type": "summary",
                    "heading": section.get("heading") or "Professional Summary",
                    "summary": worker_summary(section_text, position_name, polish_prompt).get("summary", ""),
                }
            )
        elif section_type == "experience":
            polished_resume["sections"].append(
                {
                    "type": "experience",
                    "heading": section.get("heading") or "Experience",
                    **worker_experience(section_text, position_name, polish_prompt),
                }
            )
        elif section_type == "education":
            polished_resume["sections"].append(
                {
                    "type": "education",
                    "heading": section.get("heading") or "Education",
                    **worker_education(section_text, position_name, polish_prompt),
                }
            )
        else:
            polished_resume["sections"].append(
                {
                    "type": "other",
                    "heading": section.get("heading", ""),
                    "content": section.get("content", ""),
                }
            )

    polished_text = json.dumps(polished_resume, indent=2, ensure_ascii=False)
    pdf_path = make_pdf(polished_resume)
    return polished_text, pdf_path
