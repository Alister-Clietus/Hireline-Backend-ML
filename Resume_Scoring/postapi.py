import requests
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Define the URL of the API endpoint
url = "http://127.0.0.1:5002/upload"

# Open a file dialog to select the file
Tk().withdraw()  # Hide the root Tkinter window
file_path = askopenfilename(title="Select a Resume PDF", filetypes=[("PDF Files", "*.pdf")])

if not file_path:
    print("No file selected. Exiting.")
else:
    # Open the selected file in binary mode and send it in the POST request
    try:
        with open(file_path, "rb") as file:
            response = requests.post(url, files={"file": file})
        
        # Print the response from the server
        if response.status_code == 200:
            print("Response from server:")
            print(response.json())
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            print(response.text)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")