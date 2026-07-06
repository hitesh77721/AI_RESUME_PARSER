# ==========================
# parser.py (Part 1)
# ==========================

import os
import re
import fitz
import spacy
import nltk
import unicodedata

from docx import Document

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from spacy.matcher import PhraseMatcher


# ==========================================
# Download Required NLTK Resources
# ==========================================

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("wordnet")


# ==========================================
# Load spaCy Model (Only Once)
# ==========================================
import subprocess
import sys
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(
        [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
        check=True,
    )

nlp = spacy.load("en_core_web_sm")


# ==========================================
# NLTK Objects
# ==========================================

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


# ==========================================
# Utility Functions
# ==========================================

def load_skills(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def load_degrees(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def load_certifications(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


# ==========================================
# Load Resources (Only Once)
# ==========================================

skills = load_skills("skills.txt")
degrees = load_degrees("degrees.txt")
certifications = load_certifications("certifications.txt")


# ==========================================
# Skill Matcher
# ==========================================

skill_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

skill_patterns = [nlp(skill) for skill in skills]

skill_matcher.add("SKILLS", skill_patterns)


# ==========================================
# Degree Matcher
# ==========================================

degree_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

degree_patterns = [nlp(degree) for degree in degrees]

degree_matcher.add("DEGREES", degree_patterns)


# ==========================================
# Certification Matcher
# ==========================================

certification_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

certification_patterns = [nlp(cert) for cert in certifications]

certification_matcher.add("CERTIFICATIONS", certification_patterns)


# ==========================================
# PDF Extraction
# ==========================================

def extract_pdf_text(file_path):

    document = fitz.open(file_path)

    text = ""

    for page in document:
        text += page.get_text() + "\n\n"

    document.close()

    return text


# ==========================================
# DOCX Extraction
# ==========================================

def extract_docx_text(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


# ==========================================
# TXT Extraction
# ==========================================

def extract_txt_text(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# ==========================================
# Common Text Extractor
# Supports:
# PDF
# DOCX
# TXT
# ==========================================

def extract_text(file_path):

    file_path = str(file_path)

    if file_path.lower().endswith(".pdf"):
        return extract_pdf_text(file_path)

    elif file_path.lower().endswith(".docx"):
        return extract_docx_text(file_path)

    elif file_path.lower().endswith(".txt"):
        return extract_txt_text(file_path)

    else:
        raise ValueError(
            f"Unsupported File Format : {file_path}"
        )


# ==========================================
# Text Preprocessing
# ==========================================

def preprocess_text(text):

    text = unicodedata.normalize("NFKC", text)

    text = text.replace("\t", " ")

    text = re.sub(r"[ ]+", " ", text)

    text = re.sub(r"\n+", "\n", text)

    text = text.strip()

    return text


# ==========================================
# Contact Details Extraction
# ==========================================

def extract_email(text):

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def extract_phone(text):

    pattern = r"(?:\+91[-\s]?)?[6-9]\d{9}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def extract_linkedin(text):

    pattern = r"https?://(?:www\.)?linkedin\.com/in/[^\s]+"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def extract_github(text):

    pattern = r"https?://(?:www\.)?github\.com/[^\s]+"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def extract_portfolio(text):

    pattern = r"https?://[^\s]+"

    matches = re.findall(pattern, text)

    return matches


def extract_contact_details(text):

    return {

        "email": extract_email(text),

        "phone": extract_phone(text),

        "linkedin": extract_linkedin(text),

        "github": extract_github(text),

        "websites": extract_portfolio(text)

    }


# ==========================================
# Named Entity Extraction
# ==========================================

def extract_entities(text):

    doc = nlp(text)

    entities = []

    for entity in doc.ents:

        entities.append(

            (entity.text, entity.label_)

        )

    return entities


def organize_entities(entities):

    data = {

        "name": [],

        "organization": [],

        "location": [],

        "date": []

    }

    for text, label in entities:

        if label == "PERSON":

            data["name"].append(text)

        elif label == "ORG":

            data["organization"].append(text)

        elif label == "GPE":

            data["location"].append(text)

        elif label == "DATE":

            data["date"].append(text)

    data["name"] = list(set(data["name"]))
    data["organization"] = list(set(data["organization"]))
    data["location"] = list(set(data["location"]))
    data["date"] = list(set(data["date"]))

    return data


# ==========================================
# Skills Extraction
# ==========================================

def extract_skills(text):

    doc = nlp(text)

    matches = skill_matcher(doc)

    extracted_skills = []

    for match_id, start, end in matches:

        extracted_skills.append(

            doc[start:end].text

        )

    return sorted(

        list(

            set(extracted_skills)

        )

    )


# ==========================================
# Education Extraction
# ==========================================

def extract_education(text):

    doc = nlp(text)

    education = {

        "degrees": [],

        "institutions": [],

        "years": []

    }

    matches = degree_matcher(doc)

    for match_id, start, end in matches:

        education["degrees"].append(

            doc[start:end].text

        )

    for entity in doc.ents:

        if entity.label_ == "ORG":

            if any(

                keyword in entity.text.lower()

                for keyword in [

                    "college",

                    "university",

                    "institute",

                    "school"

                ]

            ):

                education["institutions"].append(

                    entity.text

                )

    years = re.findall(

        r"\b(?:19|20)\d{2}\b",

        text

    )

    education["years"] = years

    education["degrees"] = sorted(

        list(

            set(

                education["degrees"]

            )

        )

    )

    education["institutions"] = sorted(

        list(

            set(

                education["institutions"]

            )

        )

    )

    education["years"] = sorted(

        list(

            set(

                education["years"]

            )

        )

    )

    return education

# ==========================================
# Experience Extraction
# ==========================================

def extract_experience(text):

    pattern = r"EXPERIENCE(.*?)(PROJECTS|CERTIFICATIONS|EDUCATION|LANGUAGES|INTERESTS|ACHIEVEMENTS|$)"

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not match:
        return None

    experience = match.group(1).strip()

    return experience


# ==========================================
# Projects Extraction
# ==========================================

def extract_projects(text):

    pattern = r"PROJECTS?(.*?)(CERTIFICATIONS|ACHIEVEMENTS|LANGUAGES|INTERESTS|EXPERIENCE|EDUCATION|$)"

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not match:
        return None

    projects = match.group(1).strip()

    return projects


# ==========================================
# Certifications Extraction
# ==========================================

def extract_certifications(text):

    doc = nlp(text)

    matches = certification_matcher(doc)

    extracted = []

    for match_id, start, end in matches:

        extracted.append(
            doc[start:end].text
        )

    return sorted(list(set(extracted)))


# ==========================================
# Resume Parser
# Parses ONE Resume
# ==========================================

def parse_resume(file_path):

    raw_text = extract_text(file_path)

    clean_text = preprocess_text(raw_text)

    resume_data = {

        "filename": os.path.basename(file_path),

        "contact": extract_contact_details(clean_text),

        "entities": organize_entities(
            extract_entities(clean_text)
        ),

        "skills": extract_skills(clean_text),

        "education": extract_education(clean_text),

        "experience": extract_experience(clean_text),

        "projects": extract_projects(clean_text),

        "certifications": extract_certifications(clean_text)

    }

    return resume_data


# ==========================================
# Multiple Resume Parser
# HR can upload many resumes
# ==========================================

def parse_multiple_resumes(files):

    parsed_resumes = []

    for file in files:

        try:

            parsed_resume = parse_resume(file)

            parsed_resumes.append(parsed_resume)

        except Exception as e:

            parsed_resumes.append({

                "filename": os.path.basename(str(file)),

                "error": str(e)

            })

    return parsed_resumes


# ==========================================
# Optional Helper
# Parse an Entire Folder
# ==========================================

def parse_resume_folder(folder_path):

    supported_extensions = (".pdf", ".docx", ".txt")

    files = []

    for file in os.listdir(folder_path):

        if file.lower().endswith(supported_extensions):

            files.append(

                os.path.join(folder_path, file)

            )

    return parse_multiple_resumes(files)


# ==========================================
# Optional Main
# For Local Testing
# ==========================================

if __name__ == "__main__":

    resumes = [

        "resume1.pdf",

        "resume2.docx",

        "resume3.txt"

    ]

    parsed_data = parse_multiple_resumes(resumes)

    from pprint import pprint

    pprint(parsed_data)