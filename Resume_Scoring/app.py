import fitz  # PyMuPDF for PDF processing
import re
import spacy
import joblib
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Step 1: Extract text and styles from PDF
def extract_text_and_fonts(pdf_path):
    """Extract text and font styles from a PDF."""
    doc = fitz.open(pdf_path)
    text = ""
    fonts = set()

    for page in doc:
        text += page.get_text("text") + "\n"
        for text_block in page.get_text("dict")["blocks"]:
            if "lines" in text_block:
                for line in text_block["lines"]:
                    for span in line["spans"]:
                        fonts.add(span["font"])  # Collect font styles
    
    return text.strip(), fonts

# Step 2: Preprocess text
def preprocess_text(text):
    """Clean and preprocess extracted text."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop]  # Lemmatization & stopword removal
    return " ".join(tokens)

# Step 3: Load or Train Model
def load_or_train_model():
    """Load or train the resume scoring model."""
    vectorizer_path = "tfidf_vectorizer.pkl"
    model_path = "svm_resume_scoring.pkl"

    if os.path.exists(vectorizer_path) and os.path.exists(model_path):
        print("Loading pre-trained model...")
        vectorizer = joblib.load(vectorizer_path)
        model = joblib.load(model_path)
    else:
        print("No pre-trained model found. Training a new one...")

        # Sample dataset
        resume_texts = [
            "experienced python developer with machine learning knowledge",
            "entry-level software engineer, familiar with java",
            "senior data scientist with 10 years experience",
            "graphic designer proficient in adobe photoshop illustrator",
            "motion designer skilled in after effects premiere pro"
        ]
        resume_scores = [9, 5, 10, 7, 8]  # Corresponding scores

        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(resume_texts)
        y = resume_scores

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = SVR(kernel="linear")
        model.fit(X_train, y_train)

        # Save trained models
        joblib.dump(vectorizer, vectorizer_path)
        joblib.dump(model, model_path)

    return vectorizer, model

# Step 4: Predict Resume Score
def score_resume(text, vectorizer, model):
    """Predict resume score using a trained model."""
    text_vector = vectorizer.transform([text])
    score = model.predict(text_vector)[0]
    return round(score, 2)

# Step 5: Provide Improvement Suggestions
def get_suggestions(resume_text, fonts):
    """Analyze the resume and provide suggestions for improvement."""
    
    industry_keywords = {
        "software engineer": ["python", "java", "c++", "algorithms", "data structures"],
        "data scientist": ["machine learning", "deep learning", "tensorflow", "pandas", "numpy"],
        "graphic designer": ["photoshop", "illustrator", "adobe xd", "figma", "branding"],
        "motion designer": ["after effects", "premiere pro", "cinema 4d", "animation", "storyboarding"]
    }

    found_keywords = set()
    missing_keywords = set()
    detected_field = None

    # Identify industry
    for field, keywords in industry_keywords.items():
        for keyword in keywords:
            if keyword in resume_text:
                found_keywords.add(keyword)
                detected_field = field

    if detected_field:
        missing_keywords = set(industry_keywords[detected_field]) - found_keywords

    suggestions = []

    if detected_field:
        if missing_keywords:
            suggestions.append(f"🔹 Add missing skills: {', '.join(missing_keywords)} for {detected_field}.")
        else:
            suggestions.append(f"✅ Your resume is well-optimized for {detected_field}!")

    if len(resume_text.split()) < 100:
        suggestions.append("🔹 Resume is too short. Add more details about experience and skills.")

    # Check if "Skills" and "Technical Skills" sections exist
    if "skills" not in resume_text:
        suggestions.append("🔹 Add a 'Skills' section to highlight your key competencies.")
    if "technical skills" not in resume_text:
        suggestions.append("🔹 Add a 'Technical Skills' section for better clarity.")

    # Check font consistency
    if len(fonts) > 3:
        suggestions.append(f"⚠️ Too many font styles detected ({len(fonts)}). Limit to 2-3 for consistency.")

    return suggestions

# Step 6: Check Formatting Issues
def check_margins_and_padding(pdf_path):
    """Check for consistent margins and padding in the resume."""
    doc = fitz.open(pdf_path)
    margin_issues = 0

    for page in doc:
        page_width = page.rect.width
        page_height = page.rect.height
        text_blocks = page.get_text("blocks")

        for block in text_blocks:
            x0, y0, x1, y1 = block[:4]  # Bounding box of text block
            if x0 < 20 or x1 > page_width - 20 or y0 < 20 or y1 > page_height - 20:
                margin_issues += 1

    if margin_issues > 2:
        return "⚠️ Margins are inconsistent. Ensure proper spacing around the text."
    return "✅ Margins and padding are well-aligned."

# Main Execution
if __name__ == "__main__":
    pdf_path = "E:/Users/Alister Clietus/Resume_Scoring/Basic_Resume.docx.pdf"  # Change this to your resume file path
    resume_text, fonts = extract_text_and_fonts(pdf_path)
    cleaned_resume = preprocess_text(resume_text)

    vectorizer, model = load_or_train_model()
    resume_score = score_resume(cleaned_resume, vectorizer, model)

    print(f"\n📌 Resume Score: {resume_score}/10\n")

    suggestions = get_suggestions(cleaned_resume, fonts)
    print("📌 Suggestions for Improvement:")
    for suggestion in suggestions:
        print(suggestion)

    # Check Margins and Padding
    margin_feedback = check_margins_and_padding(pdf_path)
    print("\n📌 Formatting Feedback:")
    print(margin_feedback)
