import os
from PyPDF2 import PdfReader

def parse_resume(filepath):
    """
    Dummy parser: extracts text from PDF and returns structured data.
    """
    if not os.path.exists(filepath):
        return {"error": "File not found"}

    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    lines = text.splitlines()
    data = {
        "Name": lines[0].strip() if lines else "Unknown",
        "Education": [line for line in lines if any(keyword in line for keyword in ["B.Tech", "Bachelor", "Master", "M.Sc"])],
        "Skills": ["Python", "Flask", "Machine Learning"],  # dummy skills
        "Contact": next((word for word in text.split() if "@" in word), "Not found"),
        "RawText": text.strip()
    }
    return data
