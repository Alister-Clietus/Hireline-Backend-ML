# Job Email Extractor

This project extracts emails from Gmail and saves them to a database.

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

### 5. Run the Script
Once everything is set up, run the script using:
```sh
python JobEmailExtractor.py
```

## Environment Details
- **Python Version:** Python 3.10.11
- **Pip Version:** pip 23.0.1

This script will extract emails from Gmail and save them to the database. 🚀

