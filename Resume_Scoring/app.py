from flask import Flask, request, jsonify
import fitz  # PyMuPDF for PDF processing
import re
import spacy
import joblib
import os
import language_tool_python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins to access the API
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

# Load or Train Model
def load_or_train_model():
    vectorizer_path = "tfidf_vectorizer.pkl"
    model_path = "svm_resume_scoring.pkl"

    if os.path.exists(vectorizer_path) and os.path.exists(model_path):
        vectorizer = joblib.load(vectorizer_path)
        model = joblib.load(model_path)
    else:
        resume_texts = [
            "experienced python developer with machine learning knowledge",
            "entry-level software engineer, familiar with java",
            "senior data scientist with 10 years experience",
            "graphic designer proficient in adobe photoshop illustrator",
            "motion designer skilled in after effects premiere pro"
        ]

        # Dynamically calculate resume_scores based on the text
        resume_scores = []
        for text in resume_texts:
            details = extract_resume_details(text.lower())
            score = score_resume(details)
            resume_scores.append(score)

        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(resume_texts)
        y = resume_scores

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = SVR(kernel="linear")
        model.fit(X_train, y_train)

        joblib.dump(vectorizer, vectorizer_path)
        joblib.dump(model, model_path)

    return vectorizer, model

vectorizer, model = load_or_train_model()

# Extract text from PDF
def extract_text_and_fonts(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    fonts = set()

    for page in doc:
        text += page.get_text("text") + "\n"
        for text_block in page.get_text("dict")["blocks"]:
            if "lines" in text_block:
                for line in text_block["lines"]:
                    for span in line["spans"]:
                        fonts.add(span["font"])
    return text.strip(), fonts

# Preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(tokens)

# Extract specific details
def extract_resume_details(text):
    github_url = re.search(r'github\.com/[^\s]+', text)  # Match GitHub URLs
    linkedin_url = re.search(r'linkedin\.com/in/[^\s]+', text)  # Match LinkedIn URLs
    details = {
        "email": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)),
        "phone": bool(re.search(r'\b\d{10}\b', text)),
        "github": github_url.group() if github_url else None,  # Extract full GitHub URL
        "linkedin": linkedin_url.group() if linkedin_url else None,  # Extract full LinkedIn URL
        "portfolio": "portfolio" in text or "website" in text,
        "education": "education" in text,
        "skills": "skills" in text,
        "work_experience": "work experience" in text or "job experience" in text,
        "projects": "projects" in text,
        "hobbies": "hobbies" in text or "interests" in text,
        "achievements": "achievements" in text or "awards" in text,
        "about": "summary" in text or "objective" in text,
        "volunteering_experience": "volunteering experience" in text,
        "extracurricular_activities": "extracurricular activities" in text,
        "certifications_training": "certifications" in text or "training" in text,
        "publications_research": "publications" in text or "research" in text
    }
    return details

# Scoring functions
def score_resume(details):
    section_weights = {
        "education": 2,
        "skills": 3,
        "work_experience": 3,
        "projects": 2,
        "hobbies": 1,
        "achievements": 2,
        "email": 1,
        "phone": 1,
        "github": 1,
        "linkedin": 1,
        "portfolio": 1,
        "volunteering_experience": 2,
        "extracurricular_activities": 2,
        "certifications_training": 2,
        "publications_research": 2
    }
    # Calculate the total score based on the presence of sections
    total_score = sum(weight for key, weight in section_weights.items() if details[key])
    return total_score

# Individual section scoring dynamically
# Define a function to return the skills array
def get_skills_list():
    return [
        # Programming Languages
        "Python", "Java", "C", "C++", "JavaScript", "TypeScript", "C#", "Go", "Rust", 
        "Swift", "Kotlin", "PHP", "Ruby", "Perl", "Scala", "Dart", "R", "Lua", "Objective-C",

        # Web Development
        "HTML", "CSS", "JavaScript", "TypeScript", "React.js", "Angular", "Vue.js", 
        "Next.js", "Svelte", "Tailwind CSS", "Bootstrap", "Node.js", "Express.js", 
        "FastAPI", "Flask", "Django", "Spring Boot", "ASP.NET",

        # Databases
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Firebase", "Oracle Database", 
        "Microsoft SQL Server", "Cassandra", "Redis", "MariaDB", "DynamoDB",

        # DevOps & Cloud Technologies
        "Docker", "Kubernetes", "Git", "Jenkins", "Ansible", "Terraform", "AWS", "Azure", 
        "Google Cloud", "CI/CD", "Prometheus", "Grafana", "ELK Stack", "Cloudflare",

        # Cybersecurity
        "Penetration Testing", "OWASP", "Burp Suite", "Metasploit", "Wireshark", 
        "Nmap", "Snort", "Suricata", "Kali Linux", "Parrot OS", "SIEM", "SOC", 
        "Reverse Engineering", "Exploit Development",

        # Networking
        "TCP/IP", "HTTP/HTTPS", "DNS", "Load Balancing", "Nginx", "Apache", "Firewall Configuration",
        
        # Mobile Development
        "Flutter", "React Native", "Swift (iOS)", "Kotlin (Android)", "Jetpack Compose",

        # Machine Learning & Data Science
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", 
        "Seaborn", "Keras", "OpenCV", "NLTK", "Hugging Face Transformers",

        # System Programming & OS
        "Linux", "Unix", "Windows Server", "Shell Scripting", "PowerShell", "Bash",

        # Game Development
        "Unity", "Unreal Engine", "Godot",

        # Blockchain
        "Ethereum", "Solidity", "Hyperledger", "Web3.js",

        # Other Important Skills
        "Agile", "Scrum", "REST APIs", "GraphQL", "Microservices Architecture", 
        "Multithreading", "Distributed Systems", "Software Testing", "Unit Testing", "TDD", 
        "Figma", "Adobe XD", "WebAssembly"
    ]

def count_projects(resume_text):
    """
    Extract and count the number of projects in the resume text.
    """
    # Define a pattern to identify project-related sections
    project_pattern = re.compile(r'projects?\s*[:\-]?\s*(.*)', re.IGNORECASE)

    # Find all matches for the project section
    matches = project_pattern.findall(resume_text)

    # Initialize project count
    project_count = 0

    # If matches are found, process them
    if matches:
        for match in matches:
            # Split the project descriptions by newlines or bullet points
            project_lines = re.split(r'\n|\•|\-', match)
            project_count += len([line for line in project_lines if line.strip()])  # Count non-empty lines
    else:
        # If no bullet points or matches are found, look for bold headings
        bold_project_pattern = re.compile(r'(projects?\s*[:\-]?\s*.*?)(?=\n[A-Z])', re.IGNORECASE | re.DOTALL)
        bold_matches = bold_project_pattern.findall(resume_text)

        for bold_match in bold_matches:
            # Split the bold section into lines and count non-empty lines
            project_lines = re.split(r'\n', bold_match)
            project_count += len([line for line in project_lines if line.strip()])

    # Print the number of projects for debugging
    print(f"\nNumber of Projects Found: {project_count}")

    return project_count

# Function to calculate the skills score
def calculate_skills_score(resume_text):
    # Get the skills list
    skills = get_skills_list()

    # Count the number of skills found in the resume
    found_skills = [skill for skill in skills if skill.lower() in resume_text.lower()]
    total_skills = len(skills)  # Total number of skills in the list
    skills_score = (len(found_skills) / total_skills) * 10 if total_skills > 0 else 0  # Normalize to 10

    # Print the found skills in the terminal for debugging
    print("\nSkills Found in Resume:")
    print(", ".join(found_skills) if found_skills else "No skills found.")
    print(f"Skills Score (Normalized to 10): {skills_score:.2f}")

    return round(skills_score, 2)  # Return the normalized score rounded to 2 decimal places

# Update the calculate_section_scores function to use the get_skills_list function
def calculate_section_scores(resume_text, details):
    grammar_errors = len(tool.check(resume_text))
    grammar_score = max(0, 10 - grammar_errors // 5)
    
    keyword_match = vectorizer.transform([resume_text])
    keyword_score = min(10, int(model.predict(keyword_match)[0]))
    
    brevity_score = 10 if 100 <= len(resume_text.split()) <= 500 else 5 if len(resume_text.split()) > 500 else 3
    
    alignment_score = 8  # Placeholder; can use PDF layout analysis for better results

    # Use the calculate_skills_score function to calculate the skills score
    skills_score = calculate_skills_score(resume_text)

    return {
        "Grammar_Score": grammar_score,
        "Alignment_Score": alignment_score,
        "Keywords_Score": keyword_score,
        "Brevity_Score": brevity_score,
        "Skills_Score": skills_score,  # Now uses the calculate_skills_score function
        "Education_Score": 10 if details["education"] else 0,
        "About_Score": 10 if details["about"] else 0,
        "Projects_Score": 10 if details["projects"] else 0,
        "Interests_Score": 10 if details["hobbies"] else 0  # Added score for interests
    }

# Provide improvement suggestions
def get_suggestions(details):
    suggestions = []
    for key, present in details.items():
        if not present:
            suggestions.append(f"Consider adding {key.replace('_', ' ')} to improve your resume.")
    return suggestions

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    pdf_path = "temp_resume.pdf"
    file.save(pdf_path)

    # Extract text and fonts from the uploaded PDF
    resume_text, fonts = extract_text_and_fonts(pdf_path)

    # Print the extracted text in a structured format
    print("\nExtracted Text from PDF:")
    print("=" * 50)
    print(resume_text)
    print("=" * 50)

    # Extract details from the resume text
    details = extract_resume_details(resume_text.lower())

    # Count the number of projects
    project_count = count_projects(resume_text)

    # Print found details in the terminal
    print("\nDetails Found in Resume:")
    if details["email"]:
        email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text).group()
        print(f"Email: {email}")
    if details["github"]:
        print("GitHub: Found")
    if details["linkedin"]:
        print("LinkedIn: Found")
    if details["phone"]:
        phone = re.search(r'\b\d{10}\b', resume_text).group()
        print(f"Phone: {phone}")

    # Calculate individual section scores
    section_scores = calculate_section_scores(resume_text, details)

    # Print section scores in the terminal
    print("\nSection Scores:")
    for section, score in section_scores.items():
        print(f"{section}: {score}")

    # Calculate the overall resume score (normalized to 10)
    total_possible_score = sum(section_scores.values())
    resume_score = round((total_possible_score / (len(section_scores) * 10)) * 10, 2)

    # Print the overall resume score in the terminal
    print(f"\nOverall Resume Score: {resume_score}/10")

    # Generate suggestions for missing sections
    suggestions = get_suggestions(details)

    # Cleanup temporary file
    os.remove(pdf_path)

    # Return detailed response
    return jsonify({
        "resume_score": resume_score,
        "section_scores": section_scores,
        "project_count": project_count,  # Include project count in the response
        "suggestions": suggestions
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)
