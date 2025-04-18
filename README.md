# Project Structure

This project consists of multiple components for email extraction, chatbot functionality, and resume scoring.

## Folder Structure

### 1. ChatBot
- This folder contains the chatbot functionality.

### 2. Email_Scraper
- This folder is responsible for automatically fetching email data related to placement.
- **Main script to run:** `JobEmailExtractor.py`

### 3. Resume_Scoring
- This folder contains a script that runs a machine learning model to return a score for uploaded resumes.

## Setup Instructions

### 1. Create a Virtual Environment
Run the following command to create a virtual environment:
```sh
python -m venv venv
```

### 2. Activate the Virtual Environment
- **Windows (CMD/PowerShell):**  
  ```sh
  venv\Scripts\activate
  ```  
- **Mac/Linux:**  
  ```sh
  source venv/bin/activate
  ```  

### 3. Install Dependencies
Ensure you have `requirements.txt` in the project folder, then install the required packages:
```sh
pip install -r requirements.txt
```

### 4. Add Google Authentication File
- Place the Google authentication file (`authfile.json`) inside the **EMAIL_SCRAPER** folder.
- Rename it to:
  ```sh
  PlacementPortalOAuth.json
  ```

### 5. Run the Email Extractor Script
Once everything is set up, run the script using:
```sh
python Email_Scraper/JobEmailExtractor.py
```

## Environment Details
- **Python Version:** Python 3.10.11
- **Pip Version:** pip 23.0.1

This project handles chatbot interactions, email extraction, and resume scoring efficiently. 🚀

