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

# If modifying the scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Database configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'Alister123@',
    'host': 'localhost',
    'database': 'compiler',
}

TABLE_NAME = 'emails'

def authenticate_gmail():
    """Authenticate the user and return the Gmail API service."""
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

def extract_links(text):
    """Extract and return all links from the given text."""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.findall(url_pattern, text)

def connect_to_db():
    """Connect to the MySQL database and return the connection and cursor."""
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
    """Create the emails table if it doesn't already exist."""
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mail_id VARCHAR(255),
        subject VARCHAR(255),
        sender_id VARCHAR(255),
        content BLOB,
        links TEXT
    );
    """
    cursor.execute(create_table_query)

def save_email_to_db(cursor, connection, mail_id, subject, sender_id, content, links):
    """Save email data to the MySQL database."""
    insert_query = f"""
    INSERT INTO {TABLE_NAME} (mail_id, subject, sender_id, content, links)
    VALUES (%s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, (mail_id, subject, sender_id, content, links))
    connection.commit()

def is_email_in_db(cursor, mail_id):
    """Check if the email with the given mail_id already exists in the database."""
    query = f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE mail_id = %s"
    cursor.execute(query, (mail_id,))
    result = cursor.fetchone()
    return result[0] > 0  # Returns True if the count is greater than 0

def get_emails_with_label(service, label_name, cursor, connection):
    """Retrieve emails with the specified label and store them in the database."""
    query = f'label:{label_name}'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print(f'No emails found with label: {label_name}')
        return

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()

        # Check if the email already exists in the database
        if is_email_in_db(cursor, msg['id']):
            print(f"Email with ID {msg['id']} already exists. Skipping...")
            continue

        # Extract payload and headers
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])
        subject = None
        sender_id = None
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From':
                sender_id = header['value']

        # Extract email content (plain text or HTML)
        parts = payload.get('parts', [])
        content = ""
        for part in parts:
            if part['mimeType'] == 'text/plain':
                content = part.get('body', {}).get('data', '')
                break

        if content:
            # Decode the email content
            content = base64.urlsafe_b64decode(content).decode('utf-8')

        # Extract links from the content
        links = extract_links(content)
        links_str = '\n'.join(links)

        # Save to the database
        save_email_to_db(cursor, connection, msg['id'], subject, sender_id, content, links_str)
        print(f"Email with ID {msg['id']} saved successfully.")

if __name__ == '__main__':
    # Authenticate Gmail
    service = authenticate_gmail()

    # Connect to the database
    connection, cursor = connect_to_db()
    if not connection or not cursor:
        print("Database connection failed.")
        exit()

    # Create table if not exists
    create_table_if_not_exists(cursor)

    # Infinite loop to check emails every 1 minute
    while True:
        print("Checking for new emails...")
        get_emails_with_label(service, 'placement', cursor, connection)

        # Wait for 1 minute before checking again
        time.sleep(60)

    # Close the database connection (this will never be reached due to the infinite loop)
    cursor.close()
    connection.close()
    print("Database connection closed.")
