# Resume Analysis and Scoring Script

This script is designed to analyze and score resumes based on their content and formatting. It uses machine learning to predict a resume score and provides suggestions for improvement.

## 1. Overall Workflow of the Script

The script follows these main steps:

### Extract Text & Fonts from PDF
- Reads the resume using PyMuPDF.
- Extracts all text and identifies font styles.

### Preprocess Resume Text
- Converts text to lowercase.
- Removes special characters.
- Uses spaCy for lemmatization (reducing words to their base form).

### Load or Train Machine Learning Model
- If a pre-trained model exists, load it.
- If no model is found, train a new one using sample data.

### Vectorize Resume Text
- Convert text into numerical format using TF-IDF Vectorization.

### Predict Resume Score
- The trained SVR model predicts a score for the resume.

### Check for Formatting Issues
- Ensure consistent fonts (not more than 3).
- Check if Skills & Technical Skills sections exist.
- Analyze Margins & Padding.

### Provide Suggestions for Improvement
- Recommend missing skills based on industry standards.
- Detect too many font styles or inconsistent margins.

## 2. Machine Learning Model Used

### Model Type: Support Vector Regression (SVR)
The model used for resume scoring is Support Vector Regression (SVR).

#### Why SVR?
- SVR is useful for predicting continuous values (like resume scores).
- It works well with high-dimensional text data.
- It finds a best-fit line that minimizes errors while ignoring outliers.

## 3. Step-by-Step Explanation of Model Training

### Step 1: Data Preparation
To train a model, we need resume texts and corresponding scores.

#### Sample Data in Script
python
resume_texts = [
    "experienced python developer with machine learning knowledge",
    "entry-level software engineer, familiar with java",
    "senior data scientist with 10 years experience",
    "graphic designer proficient in adobe photoshop illustrator",
    "motion designer skilled in after effects premiere pro"
]
resume_scores = [9, 5, 10, 7, 8]

The dataset consists of sample resumes with predefined scores.

The scores range from 1 to 10.

Step 2: Convert Text into Numerical Format (TF-IDF)
What is TF-IDF (Term Frequency-Inverse Document Frequency)?
TF-IDF is a method to convert text into numbers by measuring:

Term Frequency (TF): How often a word appears in a document.

Inverse Document Frequency (IDF): How unique the word is in the dataset.

### 4. Applying TF-IDF in the Script
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(resume_texts)  # Convert text to numerical format

Each resume is converted into a numerical feature vector.

Common words like "the" and "is" are ignored.

### Step 3: Train the SVR Model
model = SVR(kernel="linear")
model.fit(X_train, y_train)

The Support Vector Regression (SVR) model is trained on the TF-IDF vectors.

The model learns to map text features to resume scores.

### Step 4: Predict Resume Score
Once trained, the model can predict a score for any new resume:
text_vector = vectorizer.transform([new_resume_text])
score = model.predict(text_vector)[0]
The new resume text is vectorized using the trained TF-IDF model.
The SVR model predicts a score between 1 and 10.

### Resume Analysis & Formatting Checks
Checking for Key Sections
The script analyzes the resume for key sections:

"Skills" section must exist:

if "skills" not in resume_text:
    suggestions.append("🔹 Add a 'Skills' section to highlight your key competencies.")

if "technical skills" not in resume_text:
    suggestions.append("🔹 Add a 'Technical Skills' section for better clarity.")

### Checking Font Consistency
To ensure not too many font styles, the script collects all fonts:

fonts.add(span["font"])  # Store font styles used
if len(fonts) > 3:
    suggestions.append(f"⚠️ Too many font styles detected ({len(fonts)}). Limit to 2-3 for consistency.")


### Checking Margins & Padding
To ensure text is properly aligned, the script detects text position:
for block in text_blocks:
    x0, y0, x1, y1 = block[:4]  # Get text block bounding box
    if x0 < 20 or x1 > page_width - 20 or y0 < 20 or y1 > page_height - 20:
        margin_issues += 1

If text is too close to the edges, a warning is added:

if margin_issues > 0:
    suggestions.append("⚠️ Adjust margins to ensure text is not too close to the edges.")