from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()


db_config = {"host": "localhost", "database": "dhanamitra", "user": os.getenv("POSTGRESQL_USER"), "password": os.getenv("POSTGRESQL_PASSWORD")}


connection = None

connection = psycopg2.connect(**db_config)

cursor = connection.cursor()

create_customer_table = """

CREATE TABLE IF NOT EXISTS customers (
            customer_id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT,
            phone_number TEXT UNIQUE NOT NULL,
            timezone TEXT DEFAULT 'Asia/Kolkata',
            language TEXT DEFAULT 'en',
            
            loan_reference_id TEXT UNIQUE NOT NULL,
            outstanding_balance DECIMAL(10, 2) NOT NULL,
            due_date DATE,
            last_payment_date DATE,
            
            call_status TEXT DEFAULT 'PENDING' CHECK (call_status IN ('PENDING', 'RESOLVED', 'DO_NOT_CALL')),
            next_call_scheduled_at TIMESTAMP,
            email TEXT UNIQUE
        )
"""

create_call_logs_table = """

CREATE TABLE IF NOT EXISTS call_logs (
            log_id SERIAL PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            vapi_call_id TEXT,
            call_outcome TEXT CHECK (call_outcome IN (
                -- Success Scenarios
                'PAYMENT_COMPLETED',

                -- Follow-up Needed
                'CALLBACK_REQUESTED',
                'PROMISED_TO_PAY',
                
                -- No Contact Made
                'VOICEMAIL',
                'NO_ANSWER',
                'BUSY',
                'FAILED',
                
                -- Stop Calling
                'WRONG_NUMBER'
            )),
            call_summary TEXT,
            recording_url TEXT,
            customer_sentiment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- This links the log to the customer table
            FOREIGN KEY (customer_id)
                REFERENCES customers (customer_id)
                ON DELETE CASCADE
        )
"""

cursor.execute(create_customer_table)
cursor.execute(create_call_logs_table)

connection.commit()
connection.close()




