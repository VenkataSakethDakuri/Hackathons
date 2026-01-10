from fastapi import FastAPI, Request    
from dotenv import load_dotenv
import os
import psycopg2
from call_func import make_call
from datetime import datetime, timedelta
from decimal import Decimal


load_dotenv()


app = FastAPI()

db_config = {"host": "localhost", "database": "dhanamitra", "user": os.getenv("POSTGRESQL_USER"), "password": os.getenv("POSTGRESQL_PASSWORD")}



@app.post("/vapi-webhook")
async def webhook(request: Request):
    data = await request.json()

    if data["message"]["type"] == 'end-of-call-report':
        connection = None
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        
        call = data["message"]

        phone_number = call["customer"]["number"]
        vapi_call_id = call["call"]["id"]
        recording_url = call.get("recordingUrl")
        ended_reason = call.get("endedReason", "unknown")
        
        # Extract Analysis
        analysis = call.get("analysis", {})
        summary = analysis.get("summary", "No summary available")

        structured_data = analysis.get("structuredData", {})
        ai_outcome = structured_data.get("call_outcome")
        ai_sentiment = structured_data.get("customer_sentiment", "Neutral")

        #placeholder
        final_outcome = "FAILED" 
        new_customer_status = "PENDING" 
        next_call_time = datetime.now() + timedelta(hours=4)

        if ended_reason == 'customer-did-not-answer':
            final_outcome = 'NO_ANSWER'
            new_customer_status = 'PENDING'
            next_call_time = datetime.now() + timedelta(hours=4)
            
        elif ended_reason == 'busy':
            final_outcome = 'BUSY'
            new_customer_status = 'PENDING'
            next_call_time = datetime.now() + timedelta(hours=4)
        
        elif ended_reason == 'voicemail':
            final_outcome = 'VOICEMAIL'
            new_customer_status = 'PENDING'
            next_call_time = datetime.now() + timedelta(hours=4)
        
        elif ai_outcome:
            final_outcome = ai_outcome

            if ai_outcome == 'PAYMENT_COMPLETED':
                final_outcome = 'PAYMENT_COMPLETED'
                new_customer_status = 'COMPLETED'
                next_call_time = None
            
            elif ai_outcome in ['CALLBACK_REQUESTED', 'PROMISED_TO_PAY']:
                final_outcome = 'CALLBACK_REQUESTED'
                new_customer_status = 'PENDING'
                next_call_time = datetime.now() + timedelta(hours=4)
            
            elif ai_outcome == 'FAILED':
                final_outcome = 'FAILED'
                new_customer_status = 'PENDING'
                next_call_time = None
            
            elif ai_outcome == 'WRONG_NUMBER':
                final_outcome = 'WRONG_NUMBER'
                new_customer_status = 'DO_NOT_CALL'
                next_call_time = None

        # Get Customer ID
        cursor.execute("SELECT customer_id, outstanding_balance, due_date FROM customers WHERE phone_number = %s", (phone_number,))
        result = cursor.fetchone()

        if result:
            customer_id = result[0]
            outstanding_balance = Decimal(result[1])
            due_date = result[2]
        else:
            customer_id = None
            outstanding_balance = None
            due_date = None

        log_query = """
                    INSERT INTO call_logs 
                    (customer_id, vapi_call_id, call_outcome, call_summary, recording_url, customer_sentiment)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
        cursor.execute(log_query, (customer_id, vapi_call_id, final_outcome, summary, recording_url, ai_sentiment))

        update_query = """
                        UPDATE customers 
                        SET call_status = %s, next_call_scheduled_at = %s 
                        WHERE customer_id = %s
                    """
        cursor.execute(update_query, (new_customer_status, next_call_time, customer_id))

        assistant_id = call["call"]["assistantId"]
        customer_name = call["customer"]["name"]
        customer_email = call["customer"]["email"]
        phone_number_id = os.getenv('VAPI_PHONE_NUMBER_ID')

        if next_call_time != None:
            make_call(phone_number, customer_name, customer_email, assistant_id, next_call_time, phone_number_id, customer_id, outstanding_balance, due_date)

        connection.commit()

        cursor.close()
        connection.close()





