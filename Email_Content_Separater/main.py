import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')

from flask import Flask, request, jsonify
import re
import spacy
from rake_nltk import Rake

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)

# Function to extract job details
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

# Define Flask route
@app.route('/extract', methods=['POST'])
def extract():
    # Get email content from the request
    data = request.json
    email_content = data.get('email_content', '')

    # Extract job details
    result = extract_job_details(email_content)

    # Return the result as JSON
    return jsonify(result)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)