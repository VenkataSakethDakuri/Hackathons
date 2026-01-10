import requests
from dotenv import load_dotenv
import psycopg2
import os
import pytz
from datetime import datetime, timedelta
from decimal import Decimal

load_dotenv()

db_config = {"host": "localhost", "database": "dhanamitra", "user": os.getenv("POSTGRESQL_USER"), "password": os.getenv("POSTGRESQL_PASSWORD")}

def timestamp_to_ISO(timestamp: datetime):
    ist = pytz.timezone('Asia/Kolkata')
    iso_time = timestamp.astimezone(ist).isoformat()
    return iso_time


def get_past_history(customer_id: int):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    query = """
        SELECT call_outcome, call_summary, created_at 
        FROM call_logs 
        WHERE customer_id = %s
        ORDER BY created_at DESC 
        LIMIT 3
    """
    cursor.execute(query, (customer_id,))
    logs = cursor.fetchall()

    connection.close()
    cursor.close()
    
    if not logs:
        return "No previous calls."

    history_text = ""
    for log in logs:
        outcome, summary, date = log
        date_str = date.strftime("%d-%b")
        history_text += f"- On {date_str} ({outcome}): {summary}\n"
    
    return history_text


def make_call(customer_number: str, customer_name: str, customer_email: str, assistant_id: str, next_call_time: datetime, phone_number_id: str, customer_id: int, outstanding_balance: Decimal, due_date: datetime):

    url = "https://api.vapi.ai/call"
    history_text = get_past_history(customer_id)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('VAPI_API_KEY')}"
    }

    payload = {
        "name": "Loan recovery call",
        "customer": {
                "number": customer_number,
                "name": customer_name,
                "email": customer_email
            },

        "assistantId": assistant_id,
        "schedulePlan": {
            "earliestAt": timestamp_to_ISO(next_call_time),
            "latestAt": timestamp_to_ISO(next_call_time + timedelta(seconds=30))
        },
        
        "phoneNumberId": phone_number_id,

        "assistantOverrides": {
            "firstMessage": f"Hello! am I speaking to {customer_name}?",

            "model": {
                "messages": [
                    {
                        "role": "system",
                        "content": f"""
                        You are a loan recovery agent.
                        
                        Here is the history of previous calls with this customer:
                        {history_text}
                        
                        Here is the loan details:
                        Outstanding balance: {outstanding_balance}
                        Due date: {due_date}
                        
                        Use this context however needed.
                        """
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("Call scheduled successfully")
    else:
        print("Failed to schedule call")
        return None
    
    return response.json()
