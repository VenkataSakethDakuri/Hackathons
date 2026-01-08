import requests
from dotenv import load_dotenv
import os

load_dotenv()

def create_phone_number(assistant_id: str):
    url = "https://api.vapi.ai/phone-number",
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('VAPI_API_KEY')}"
    },

    payload = {
        
        "TwilioPhoneNumber":
        {
            "provider": "twilio",
            "name": "Twilio number",
            "number": os.getenv('TWILIO_PHONE_NUMBER'),
            "twilioAccountSid": os.getenv('TWILIO_ACCOUNT_SID'),
            "twilioAuthToken": os.getenv('TWILIO_AUTH_TOKEN'),
            "twilioApiSecret": os.getenv('TWILIO_API_SECRET'),
            "twilioApiKey": os.getenv('TWILIO_API_KEY'),
            "assistantId": {assistant_id}
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("Phone number created successfully")
    else:
        print("Failed to create phone number")
        return None
    
    return response.json()