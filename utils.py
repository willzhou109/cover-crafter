from PyPDF2 import PdfReader
import docx

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        text = ""
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text

        if text.strip():
            print(f"Successfully read PDF: {file_path}")
        else:
            print(f"PDF read completed but no text was extracted (it might be scanned or image-based): {file_path}")
        return text

    elif file_path.endswith(".docx"):
        doc_file = docx.Document(file_path)
        text = "\n".join([para.text for para in doc_file.paragraphs])
        print(f"Successfully read DOCX: {file_path}")
        return text

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"Successfully read TXT: {file_path}")
        return text

    else:
        raise ValueError(f"Unsupported file type: {file_path}")
