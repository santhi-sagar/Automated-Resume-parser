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

        # Extract name using spaCy NER
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

        # Basic skill extraction
        skill_keywords = [
            "Python",
            "Java",
            "SQL",
            "C++",
            "Machine Learning",
            "Data Analysis",
            "JavaScript",
            "React",
            "Node.js",
            "AWS",
            "Docker",
        ]
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                skills.append(skill)

        # Basic education detection
        education_keywords = [
            "B.Tech",
            "M.Tech",
            "B.Sc",
            "M.Sc",
            "MBA",
            "BCA",
            "MCA",
        ]
        for word in education_keywords:
            if word in text:
                education.append(word)

        data = {
            "Name": name or "Not found",
            "Skills": ", ".join(skills) if skills else "Not found",
            "Education": ", ".join(education) if education else "Not found",
        }

        # Save to CSV with proper header handling
        csv_file = "extracted_data.csv"
        file_exists = os.path.isfile(csv_file)

        df = pd.DataFrame([data])
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