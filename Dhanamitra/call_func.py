import requests
from dotenv import load_dotenv
import os
import pytz
from datetime import datetime

load_dotenv()

def timestamp_to_ISO(timestamp: datetime):
    ist = pytz.timezone('Asia/Kolkata')
    iso_time = timestamp.astimezone(ist).isoformat()
    return iso_time


def make_call(customer_number: str, customer_name: str, customer_email: str, assistant_id: str, next_call_time: datetime, phone_number_id: str):

    url = "https://api.vapi.ai/call"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('VAPI_API_KEY')}"
    }

    payload = {
        "name": "Loan recovery call",
        "customers": [
            {
                "number": {customer_number},
                "name": {customer_name},
                "email": {customer_email}
            }
        ],

        "assistantId": {assistant_id},
        "schedulePlan": {
            "earliestAt": timestamp_to_ISO(next_call_time),
            "latestAt": timestamp_to_ISO(next_call_time)
        },
        "phoneNumber": {

            "name": "Caller Number",
            "assistantId": {assistant_id},
            "phoneNumberId": {phone_number_id}
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("Call scheduled successfully")
    else:
        print("Failed to schedule call")
        return None
    
    return response.json()
