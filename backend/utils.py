import io

from PyPDF2 import PdfReader
import docx


def extract_text_from_upload(filename: str, content: bytes) -> str:
    name = (filename or "").lower()

    if name.endswith(".pdf"):
        text = ""
        with io.BytesIO(content) as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text
        return text

    if name.endswith(".docx"):
        with io.BytesIO(content) as f:
            doc_file = docx.Document(f)
        return "\n".join([para.text for para in doc_file.paragraphs])

    if name.endswith(".txt"):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")

    raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")
