import os
from typing import Optional

from PyPDF2 import PdfReader
from docx import Document

def read_file(file_path: str) -> Optional[str]:
    """
    Reads the content of a txt, pdf, or docx file.
    
    Args:
        file_path (str): Path to the file

    Returns:
        str: Extracted text content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        elif ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""

        elif ext == ".docx":
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    except Exception as e:
        raise RuntimeError(f"Error reading {file_path}: {e}")

    return text.strip()
