from pathlib import Path
import zipfile

from lxml import etree


def extract_resume_text(resume_file, resume_content=""):
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

        raise ValueError(
            "Unsupported file type. Please upload a PDF, DOCX, ODT, TXT, or MD file."
        )

    return (resume_content or "").strip()


def load_resume_into_textbox(resume_file):
    if not resume_file:
        return ""

    try:
        return extract_resume_text(resume_file, "")
    except Exception as exc:
        return f"Could not extract text from uploaded file: {exc}"