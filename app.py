import pdfplumber
import spacy
import re
import pandas as pd

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def parse_resume(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    doc = nlp(text)

    name = ""
    skills = []
    education = []

    # Simple regex for name (first line capitalized words)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    # Basic skill extraction
    skill_keywords = ["Python", "Java", "SQL", "C++", "Machine Learning", "Data Analysis"]
    for skill in skill_keywords:
        if skill.lower() in text.lower():
            skills.append(skill)

    # Basic education detection
    for word in ["B.Tech", "M.Tech", "B.Sc", "M.Sc", "MBA", "BCA", "MCA"]:
        if word in text:
            education.append(word)

    data = {"Name": [name], "Skills": [", ".join(skills)], "Education": [", ".join(education)]}
    df = pd.DataFrame(data)
    df.to_csv("extracted_data.csv", mode="a", index=False, header=False)

    return data
