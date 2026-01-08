import requests
from dotenv import load_dotenv
import os

load_dotenv()

def upload_file(file_path: str):
    url = "https://api.vapi.ai/file"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('VAPI_API_KEY')}"
    }

    payload = {
        "file": open(file_path, "rb")
    }

    response = requests.post(url, headers=headers, files=payload)

    if response.status_code == 201:
        print("File uploaded successfully")
    else:
        print("Failed to upload file")
        return None
    
    return response.json()