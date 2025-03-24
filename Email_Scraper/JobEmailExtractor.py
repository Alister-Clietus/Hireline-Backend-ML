import os
import pickle
import re
import base64
import mysql.connector
import time
from mysql.connector import errorcode
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

DB_CONFIG = {
    'user': 'root',
    'password': 'Alister123@',
    'host': 'localhost',
    'database': 'compiler',
}

TABLE_NAME = 'jobs'

KEYWORDS = [
    "Job opportunity", "Hiring Fresher", "Hiring", "Recruitment", "Campus Drive",
    "Placement Opportunity", "Placement", "VIRTUAL Job Drive", "Job Drive"
]

COMPANY_NAMES = [
    "Google", "Microsoft", "Apple", "Amazon", "IBM", "Oracle", "Intel", "Cisco", "SAP", "Adobe",
    "Salesforce", "Meta", "Twitter", "Netflix", "Tesla", "Uber", "Airbnb", "Spotify", "Dropbox",
    "Infosys", "TCS", "Wipro", "HCL", "Capgemini", "Accenture", "Cognizant", "Dell", "HP", "Nvidia", "Yahoo",
    "Qburst", "Interland", "Carestack", "IBS", "6D Technologies", "QSpiders", "Flipkart"
]


JOB_TITLES = [
    "Software Developer", "Software Engineer", "Full Stack Developer", "Frontend Developer",
    "Backend Developer", "Mobile Application Developer", "DevOps Engineer", "Cloud Engineer",
    "Embedded Systems Engineer", "Game Developer", "Systems Architect", "Firmware Engineer",
    "Site Reliability Engineer (SRE)", "Blockchain Developer", "Data Scientist", "Data Engineer",
    "Data Analyst", "Machine Learning Engineer", "AI Engineer", "Business Intelligence Analyst",
    "Big Data Engineer", "Cybersecurity Analyst", "Security Engineer", "Ethical Hacker",
    "Penetration Tester", "Network Security Engineer", "SOC Analyst", "Information Security Officer",
    "Network Engineer", "System Administrator", "Cloud Infrastructure Engineer", "IT Support Specialist",
    "Network Architect", "QA Engineer", "Test Automation Engineer", "Performance Tester",
    "Security Tester", "Product Manager", "Project Manager", "Scrum Master", "Agile Coach",
    "UI/UX Designer", "Interaction Designer", "Product Designer", "User Researcher",
    "IT Consultant", "Technical Support Engineer", "Database Administrator", "IT Auditor", "Technical Writer"
]

COMPANY_CATEGORIES = ["MNC", "Startup"]
TYPE_OF_COMPANY = ["Hybrid", "Remote", "Inperson"]
DEFAULT_COMPANY_LINK = "https://www.companyname.com/"
JOB_STATUS="PENDING"
SALARY=10000

def authenticate_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'PlacementPortalOAuth.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    print("Returning Authenticate Gmail Service Successfully")
    return service

def connect_to_db():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print("Connected to the database.")
        return connection, cursor
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Invalid username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist.")
        else:
            print(err)
        return None, None

def create_table_if_not_exists(cursor):
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email_id VARCHAR(255) UNIQUE,
        company_category VARCHAR(255),
        company_link VARCHAR(255) DEFAULT '{DEFAULT_COMPANY_LINK}',
        company_name VARCHAR(255),
        job_description TEXT,
        job_title VARCHAR(255),
        salary DOUBLE DEFAULT '{SALARY}',
        status VARCHAR(255) DEFAULT '{JOB_STATUS}',
        type_of_company VARCHAR(255)
    );
    """
    cursor.execute(create_table_query)

def email_exists(cursor, email_id):
    cursor.execute("SELECT 1 FROM jobs WHERE email_id = %s", (email_id,))
    return cursor.fetchone() is not None

def save_email_to_db(cursor, connection, email_id, company_name, job_title, job_description):
    if email_exists(cursor, email_id):
        print(f"Email with ID {email_id} already exists. Skipping.")
        return
    insert_query = f"""
    INSERT INTO {TABLE_NAME} (email_id, company_name, job_title, job_description, company_category, type_of_company)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, (email_id, company_name, job_title, job_description, COMPANY_CATEGORIES[0], TYPE_OF_COMPANY[0]))
    connection.commit()

def generate_job_description(company, job_title, company_category, job_type, salary):
    return f"{company} is hiring a {job_title} which is an {company_category} with a work culture of {job_type} with an LPA of {salary}."

def process_email_content(email_id, content, cursor, connection):
    salary_mapping = {
        "Software Developer": 40,
        "Software Engineer": 45,
        "Full Stack Developer": 50,
    }

    for company in COMPANY_NAMES:
        for job in JOB_TITLES:
            if company in content and job in content:
                salary = salary_mapping.get(job, 30)
                job_description = generate_job_description(
                    company,
                    job,
                    COMPANY_CATEGORIES[0],
                    TYPE_OF_COMPANY[0],
                    salary
                )
                save_email_to_db(cursor, connection, email_id, company, job, job_description)
                print(f"Saved job for {company} - {job} with Email ID: {email_id}")
                return

def get_all_emails(service, cursor, connection):
    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])

    if not messages:
        print('No emails found.')
        return

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg.get('payload', {})
        parts = payload.get('parts', [])
        content = ""

        for part in parts:
            if part['mimeType'] == 'text/plain':
                content = part.get('body', {}).get('data', '')
                break

        if content:
            content = base64.urlsafe_b64decode(content).decode('utf-8')

        process_email_content(message['id'], content, cursor, connection)

if __name__ == '__main__':
    service = authenticate_gmail()
    connection, cursor = connect_to_db()

    if not connection or not cursor:
        print("Database connection failed.")
        exit()

    create_table_if_not_exists(cursor)

    while True:
        print("Checking for new emails...")
        get_all_emails(service, cursor, connection)
        time.sleep(60)

    cursor.close()
    connection.close()
    print("Database connection closed.")
