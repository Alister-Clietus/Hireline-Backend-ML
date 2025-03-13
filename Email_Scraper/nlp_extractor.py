# nlp_extractor.py

import spacy
import re

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_company_name(text):
    """Extract company name using NER and custom rules."""
    doc = nlp(text)
    
    # Look for ORG entities using spaCy's NER
    for ent in doc.ents:
        if ent.label_ == "ORG":
            return ent.text
    
    # Fallback: Look for company names using regex (e.g., "at Google" or "from Amazon")
    company_pattern = r'\b(at|from|by|joining)\s+([A-Z][a-zA-Z]+)\b'
    match = re.search(company_pattern, text, re.IGNORECASE)
    if match:
        return match.group(2)
    
    return None

def extract_job_title(text):
    """Extract job title using NER and custom rules."""
    doc = nlp(text)
    
    # Look for specific keywords indicating job titles
    job_keywords = ["engineer", "developer", "analyst", "scientist", "manager", "designer", "intern", "specialist"]
    for token in doc:
        if token.text.lower() in job_keywords:
            # Return the noun phrase containing the keyword
            return token.text
    
    # Fallback: Look for job titles using regex (e.g., "Job Title: Software Engineer")
    title_pattern = r'\b(job\s*title|role|designation)\s*:\s*([A-Za-z\s]+)\b'
    match = re.search(title_pattern, text, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    
    return None

def extract_lpa_provided(text):
    """Extract LPA provided using regex."""
    lpa_pattern = r'\b(\d+)\s*(LPA|lakh|lakhs|L)\b'
    match = re.search(lpa_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def extract_contact_details(text):
    """Extract contact details using regex."""
    phone_pattern = r'\+?\d[\d -]{8,12}\d'
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    phone_numbers = re.findall(phone_pattern, text)
    emails = re.findall(email_pattern, text)
    
    return {
        'phone_numbers': phone_numbers,
        'emails': emails
    }

def extract_bond_info(text):
    """Extract bond information using regex."""
    bond_pattern = r'\b(bond|agreement|contract)\b'
    match = re.search(bond_pattern, text, re.IGNORECASE)
    return bool(match)

def extract_all_info(content, subject):
    """Extract all required information from content and subject."""
    combined_text = f"{subject} {content}"
    
    company_name = extract_company_name(combined_text)
    job_title = extract_job_title(combined_text)
    lpa_provided = extract_lpa_provided(combined_text)
    contact_details = extract_contact_details(combined_text)
    bond_info = extract_bond_info(combined_text)
    
    # Print the extracted data
    print("\nExtracted Details:")
    print(f"Company Name: {company_name}")
    print(f"Job Title: {job_title}")
    print(f"LPA Provided: {lpa_provided}")
    print(f"Contact Details: {contact_details}")
    print(f"Bond Info: {bond_info}")
    print("-" * 40)
    
    return {
        'company_name': company_name,
        'job_title': job_title,
        'lpa_provided': lpa_provided,
        'contact_details': contact_details,
        'bond_info': bond_info
    }