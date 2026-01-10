from dotenv import load_dotenv
import os
import psycopg2
import time
import json
from decimal import Decimal

from voice_agent import create_voice_agent
from call_func import make_call
from query_tool import Query_tool
from phone_no import create_phone_number
from file_upload import upload_file

load_dotenv()

db_config = {"host": "localhost", "database": "dhanamitra", "user": os.getenv("POSTGRESQL_USER"), "password": os.getenv("POSTGRESQL_PASSWORD")}

def dispatch_calls(voice_agent: dict, phone_number: dict, file_list: list, due_calls: list, connection: object, cursor: object):

    if not due_calls:
        print("No due calls found right now.")
        return
    
    for call in due_calls:
        customer_id = call[0]
        customer_name = call[1]
        customer_number = call[2]
        loan_reference_id = call[3]
        outstanding_balance = Decimal(call[4])
        due_date = call[5]
        next_call_scheduled_at = call[6]
        customer_email = call[7]
        
        assistant_id = voice_agent['id']
        phone_number_id = phone_number['id']

        dialed_call =  make_call(customer_number, customer_name, customer_email, assistant_id, next_call_scheduled_at, phone_number_id, customer_id, outstanding_balance, due_date)



if __name__ == "__main__":

    file_list = []

    for file in os.listdir("./kb_files"):
        file_path = os.path.join("./kb_files", file)  
        response = upload_file(file_path)
        file_list.append(response['id'])

    connection = psycopg2.connect(**db_config)

    cursor = connection.cursor()

    # Find due calls
    query = """
        SELECT customer_id, first_name, phone_number, loan_reference_id, outstanding_balance, due_date, next_call_scheduled_at, email
        FROM customers
        WHERE call_status = 'PENDING' 
        AND next_call_scheduled_at <= NOW()
    """
    cursor.execute(query)
    due_calls = cursor.fetchall()

    query_tool = Query_tool(file_list)
    query_tool_id = query_tool['id']

    tool_id_list = [query_tool_id]

    voice_agent = create_voice_agent(tool_id_list)
    phone_number = create_phone_number(voice_agent['id'])

    phone_number_id = phone_number['id']
    os.environ["VAPI_PHONE_NUMBER_ID"] = phone_number_id
    
    dispatch_calls(voice_agent, phone_number, file_list, due_calls, connection, cursor)