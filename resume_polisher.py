import os
import tempfile
from pathlib import Path
import zipfile

import gradio as gr

from hf_client import generate_text


def extract_resume_text(resume_file, resume_content):
    if resume_file:
        file_path = Path(resume_file)
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(str(file_path))
            pages_text = []
            for page in reader.pages:
                pages_text.append(page.extract_text() or "")
            return "\n".join(pages_text).strip()

        if suffix == ".docx":
            from docx import Document

            doc = Document(str(file_path))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()

        if suffix in {".txt", ".md"}:
            return file_path.read_text(encoding="utf-8", errors="ignore").strip()

        if suffix == ".odt":
            from lxml import etree
            import zipfile

            with zipfile.ZipFile(str(file_path)) as zf:
                with zf.open("content.xml") as content_xml:
                    tree = etree.parse(content_xml)

            namespaces = {
                "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
                "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
            }

            paragraphs = tree.xpath("//text:p", namespaces=namespaces)
            lines = [("".join(p.itertext()).strip()) for p in paragraphs]
            return "\n".join(line for line in lines if line).strip()

        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, ODT, or TXT file.")

    return (resume_content or "").strip()


def make_pdf(output_text: str) -> str:
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

    def looks_like_heading(line: str) -> bool:
        normalized = line.strip().lower().rstrip(":")
        heading_terms = {
            "summary",
            "professional summary",
            "profile",
            "experience",
            "work experience",
            "employment history",
            "education",
            "skills",
            "technical skills",
            "projects",
            "certifications",
            "additional experience",
            "contact",
        }
        return normalized in heading_terms

    def looks_like_bullet(line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith(("-", "•", "*"))

    def clean_bullet(line: str) -> str:
        return line.strip().lstrip("-•*").strip()

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

    lines = [line.rstrip() for line in output_text.splitlines()]
    story = []
    buffer_para = []
    current_bullets = []
    heading_terms = {
        "summary",
        "professional summary",
        "profile",
        "experience",
        "work experience",
        "employment history",
        "education",
        "skills",
        "technical skills",
        "projects",
        "certifications",
        "additional experience",
        "contact",
    }

    def flush_paragraph():
        nonlocal buffer_para
        text = " ".join(part.strip() for part in buffer_para if part.strip()).strip()
        if text:
            story.append(Paragraph(text, body_style))
            story.append(Spacer(1, 4))
        buffer_para = []

    def flush_bullets():
        nonlocal current_bullets
        if current_bullets:
            bullet_items = [
                ListItem(Paragraph(bullet, bullet_style), leftIndent=10)
                for bullet in current_bullets
            ]
            story.append(ListFlowable(bullet_items, bulletType="bullet", leftIndent=18))
            story.append(Spacer(1, 4))
        current_bullets = []

    if lines:
        first_nonempty = next((line.strip() for line in lines if line.strip()), "")
        if first_nonempty:
            story.append(Paragraph(first_nonempty, title_style))
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.8, color="#666666"))
            story.append(Spacer(1, 8))

    skip_title = True
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            flush_bullets()
            continue

        if skip_title and line == first_nonempty:
            skip_title = False
            continue

        if looks_like_heading(line):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(line.rstrip(":").title(), section_style))
            continue

        if looks_like_bullet(line):
            cleaned = clean_bullet(line)
            if cleaned.lower().rstrip(":") in heading_terms:
                flush_paragraph()
                flush_bullets()
                story.append(Paragraph(cleaned.rstrip(":").title(), section_style))
            else:
                flush_paragraph()
                current_bullets.append(cleaned)
            continue

        if line.endswith(":") and len(line.split()) <= 4:
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(line.rstrip(":").title(), section_style))
            continue

        if current_bullets:
            flush_bullets()

        buffer_para.append(line)

    flush_paragraph()
    flush_bullets()

    if not story:
        story.append(Paragraph(output_text.replace("\n", "<br/>"), body_style))

    doc.build(story)
    return pdf_path


def polish_resume(position_name, resume_file=None, resume_content="", polish_prompt=""):
    resume_text = extract_resume_text(resume_file, resume_content)

    if not resume_text:
        return "Please provide either a resume upload or pasted resume text.", None

    if polish_prompt and polish_prompt.strip():
        prompt_use = (
            f"Rewrite this resume content for the position {position_name}.\n\n"
            f"Resume:\n{resume_text}\n\n"
            f"Additional instructions:\n{polish_prompt}\n\n"
            f"Use only the information provided. Do not invent details. "
            f"Make the result clear, professional, ATS-friendly, and easy to scan. "
            f"Format the result as a polished resume with clear section headings and bullet points."
        )
    else:
        prompt_use = (
            f"Rewrite this resume content for the position {position_name}.\n\n"
            f"Resume:\n{resume_text}\n\n"
            f"Additional instructions:\n{polish_prompt}\n\n"
            "Format the result as a clean, professional resume with clear section headings "
            "such as Professional Summary, Experience, Education, Skills, and Certifications if applicable.\n"
            "Use concise bullet points under experience entries when appropriate.\n"
            "Prefer short lines, consistent structure, and clean professional formatting over long paragraphs.\n"
            "Keep the wording ATS-friendly, direct, and easy to scan.\n"
            "Do not invent experience, employers, dates, metrics, or skills.\n"
            "Do not use tables, icons, emojis, decorative symbols, or unusual punctuation.\n"
            "Do not wrap the response in markdown code fences.\n"
            "Make the output look like a polished resume that can be converted into a readable PDF."
        )

    polished_text = generate_text(prompt_use, max_tokens=800, temperature=0.7)
    pdf_path = make_pdf(polished_text)
    return polished_text, pdf_path
