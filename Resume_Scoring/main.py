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
        resume_scores = [9, 5, 10, 7, 8]

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
    details = {
        "email": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)),
        "phone": bool(re.search(r'\b\d{10}\b', text)),
        "github": "github.com" in text,
        "linkedin": "linkedin.com" in text,
        "portfolio": "portfolio" in text or "website" in text,
        "education": "education" in text,
        "skills": "skills" in text,
        "work_experience": "work experience" in text or "professional experience" in text,
        "projects": "projects" in text,
        "hobbies": "hobbies" in text,
        "achievements": "achievements" in text,
        "about": "summary" in text or "objective" in text
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
        "portfolio": 1
    }
    score = sum(weight for key, weight in section_weights.items() if details[key])
    return min(10, score)

# Individual section scoring dynamically
def calculate_section_scores(resume_text, details):
    grammar_errors = len(tool.check(resume_text))
    grammar_score = max(0, 10 - grammar_errors // 5)
    
    keyword_match = vectorizer.transform([resume_text])
    keyword_score = min(10, int(model.predict(keyword_match)[0]))
    
    brevity_score = 10 if 100 <= len(resume_text.split()) <= 500 else 5 if len(resume_text.split()) > 500 else 3
    
    alignment_score = 8  # Placeholder; can use PDF layout analysis for better results
    
    return {
        "Grammar_Score": grammar_score,
        "Alignment_Score": alignment_score,
        "Keywords_Score": keyword_score,
        "Brevity_Score": brevity_score,
        "Skills_Score": 10 if details["skills"] else 0,
        "Education_Score": 10 if details["education"] else 0,
        "About_Score": 10 if details["about"] else 0,
        "Projects_Score": 10 if details["projects"] else 0
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
    resume_text, fonts = extract_text_and_fonts(pdf_path)
    details = extract_resume_details(resume_text.lower())
    resume_score = score_resume(details)
    section_scores = calculate_section_scores(resume_text, details)
    suggestions = get_suggestions(details)
    os.remove(pdf_path)  # Cleanup temp file
    return jsonify({
        "resume_score": resume_score,
        "section_scores": section_scores,
        "suggestions": suggestions
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)
