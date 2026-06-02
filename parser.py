import os
from PyPDF2 import PdfReader

def parse_resume(filepath):
    """
    Parse a resume PDF and return structured data.
    Currently returns dummy structured data with extracted text.
    Replace with advanced NLP for real parsing.
    """
    data = {
        "Name": None,
        "Education": [],
        "Skills": [],
        "Contact": None,
        "RawText": ""
    }

    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError("Resume file not found")

        # Read PDF text
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        data["RawText"] = text.strip()

        # Dummy extraction rules (replace with NLP later)
        # Name: first line of text
        lines = text.splitlines()
        if lines:
            data["Name"] = lines[0].strip()

        # Education: look for keywords
        for line in lines:
            if "B.Tech" in line or "Bachelor" in line or "Master" in line or "M.Sc" in line:
                data["Education"].append(line.strip())

        # Skills: simple keyword split
        if "Skills" in text:
            idx = text.find("Skills")
            skills_section = text[idx:idx+200]  # grab 200 chars after "Skills"
            skills = skills_section.replace("Skills", "").replace(":", "").split(",")
            data["Skills"] = [s.strip() for s in skills if s.strip()]

        # Contact: look for email
        for word in text.split():
            if "@" in word and "." in word:
                data["Contact"] = word
                break

        # Fallbacks
        if not data["Name"]:
            data["Name"] = "Unknown"
        if not data["Education"]:
            data["Education"] = ["Not found"]
        if not data["Skills"]:
            data["Skills"] = ["Not found"]
        if not data["Contact"]:
            data["Contact"] = "Not found"

        return data

    except Exception as e:
        return {"error": f"Failed to parse resume: {str(e)}"}
