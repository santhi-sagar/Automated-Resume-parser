import pdfplumber
import spacy
import re
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.error("spaCy model 'en_core_web_sm' not found. Install it with: python -m spacy download en_core_web_sm")
    raise


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise


def extract_email(text):
    """Extract email address from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else "Not found"


def extract_phone(text):
    """Extract phone number from text."""
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    matches = re.findall(phone_pattern, text)
    return matches[0] if matches else "Not found"


def parse_resume(pdf_path):
    """Parse resume and extract key information."""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        text = extract_text_from_pdf(pdf_path)

        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")

        doc = nlp(text)

        name = ""
        skills = []
        education = []
        email = "Not found"
        phone = "Not found"

        # Extract name using spaCy NER
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

        # Extract email and phone
        email = extract_email(text)
        phone = extract_phone(text)

        # Basic skill extraction
        skill_keywords = [
            "Python",
            "Java",
            "SQL",
            "C++",
            "C#",
            "JavaScript",
            "TypeScript",
            "React",
            "Angular",
            "Vue.js",
            "Node.js",
            "Express",
            "Django",
            "Flask",
            "Spring",
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Git",
            "MongoDB",
            "PostgreSQL",
            "MySQL",
            "HTML",
            "CSS",
            "REST API",
            "GraphQL",
            "Machine Learning",
            "Data Analysis",
            "Pandas",
            "NumPy",
            "Matplotlib",
        ]
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                skills.append(skill)

        # Remove duplicates while preserving order
        skills = list(dict.fromkeys(skills))

        # Basic education detection
        education_keywords = [
            "B.Tech",
            "M.Tech",
            "B.Sc",
            "M.Sc",
            "MBA",
            "BCA",
            "MCA",
            "Bachelor",
            "Master",
            "Ph.D",
            "Diploma",
        ]
        for word in education_keywords:
            if word in text:
                education.append(word)

        # Remove duplicates while preserving order
        education = list(dict.fromkeys(education))

        data = {
            "Name": name or "Not found",
            "Email": email,
            "Contact": phone,
            "Skills": skills if skills else ["Not found"],
            "Education": education if education else ["Not found"],
        }

        # Save to CSV with proper header handling
        csv_file = "extracted_data.csv"
        file_exists = os.path.isfile(csv_file)

        # Flatten lists for CSV
        csv_data = {
            "Name": data["Name"],
            "Email": data["Email"],
            "Contact": data["Contact"],
            "Skills": ", ".join(data["Skills"]),
            "Education": ", ".join(data["Education"]),
        }

        df = pd.DataFrame([csv_data])
        df.to_csv(
            csv_file,
            mode="a",
            index=False,
            header=not file_exists,
        )

        return data

    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise
