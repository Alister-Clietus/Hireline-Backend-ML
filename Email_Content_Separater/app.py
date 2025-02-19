import re
import spacy
from rake_nltk import Rake

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

def extract_job_details(email_content):
    # Initialize output dictionary
    job_details = {
        "Company Name": "Not specified",
        "Job Description": "Not specified",
        "Apply Link": "Not specified",
        "Skills Required": [],
        "Selection Process": [],
        "Salary Package": "Not specified",
        "Benefits": []
    }

    # Extract Apply Link using regex
    apply_link = re.search(r'https?://[^\s]+', email_content)
    if apply_link:
        job_details["Apply Link"] = apply_link.group()

    # Extract entities using SpaCy
    doc = nlp(email_content)
    for ent in doc.ents:
        if ent.label_ == "ORG":  # Organization (Company Name)
            job_details["Company Name"] = ent.text

    # Extract skills using RAKE
    rake = Rake()
    rake.extract_keywords_from_text(email_content)
    job_details["Skills Required"] = rake.get_ranked_phrases()

    # Extract Selection Process (custom logic)
    selection_keywords = ["written test", "aptitude test", "technical interview", "hr interview", "group discussion"]
    for sentence in email_content.split("."):
        for keyword in selection_keywords:
            if keyword in sentence.lower():
                job_details["Selection Process"].append(keyword)

    # Extract Salary Package and Benefits (custom logic)
    salary_pattern = re.compile(r'(salary|package|ctc).*?\d+[\d,]*', re.IGNORECASE)
    salary_match = salary_pattern.search(email_content)
    if salary_match:
        job_details["Salary Package"] = salary_match.group()

    benefits_keywords = ["health insurance", "flexible hours", "work from home", "bonus"]
    for keyword in benefits_keywords:
        if keyword in email_content.lower():
            job_details["Benefits"].append(keyword)

    # Extract Job Description (first few sentences as a placeholder)
    sentences = [s.strip() for s in email_content.split(".") if s.strip()]
    if sentences:
        job_details["Job Description"] = sentences[0]  # Use the first sentence as the job description

    return job_details


# Example Usage
email_content = """
Dear Prof. Jyothi R L,  Greetings from Internshala!  We are excited to inform you that registrations for 'PepSheCo Supply Chain Star' are now live, a first-of-its-kind campus competition specially crafted for undergraduate female students.  Students can apply here - internshala.com/i/pepshesupply  Registrations Start date: 14th August 2024 Webinar: 22nd August 2024 Assessment: 22nd August to 26th August 2024 Technical Assessment: 27th August 2024 Interview and Final selection: 5th September 2024  What's in it for your college students?  Position: Full-Time Supply Chain Job Opportunity at PepsiCo India Mentorship: Direct mentorship from industry leaders at PepsiCo India Workshop & Certification: Live workshop conducted by PepsiCo leaders, with a certificate awarded upon attendance Eligibility Criteria -  Graduation Year: 2024 Pass-out female candidates only. Branch eligible to apply: BE / B.Tech in Mechanical, Chemical, Electrical, Electronics, Industrial, Instrumental, Food Technology. We kindly request you to share this message and registration link with all your female students so they can take full advantage of this incredible opportunity.  As PepsiCo India has exclusively invited your college to be a part of this program, we are expecting a good participation from your college.  For any questions or concerns, please feel free to reply to this email. We will be happy to assist you.  Regards, Surbhi Garg Manager - University Relations Internshala ~ Partner of AICTE
"""

result = extract_job_details(email_content)
print(result)