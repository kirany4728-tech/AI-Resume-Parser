import pdfplumber
from docx import Document

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text
    except Exception as e:
        print("PDF error:", e)

    return text
def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)

        text = "\n".join(
            [para.text for para in doc.paragraphs]
        )
        return text

    except Exception as e:
        print("DOCX error:", e)

        return ""