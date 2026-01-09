import requests
from dotenv import load_dotenv
import os

load_dotenv()


def create_voice_agent(tool_ids: list):

    url = "https://api.vapi.ai/assistant"
    server_url = os.getenv('NGROK_SERVER_URL')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('VAPI_API_KEY')}"
    }   

    payload = {

        "name" : "Loan recovery agent",
        "model" : {

            "provider": "google",
            "model": "gemini-2.5-flash-lite",
            "messages": [

                # {
                #     "role": "assistant",
                #     "content": f"Hello! am I speaking to {first_name}?"
                # },

                {
                    "role": "system",
                    "content": "You are a loan recovery agent, your task is to recover the loan amount from the customer."

                }
                
            ],
            "toolIds": tool_ids,
            "emotionRecognitionEnabled": True,
        },
        "voice": {

            "provider": "deepgram",
            "voiceId": "pandora"
        },
        "transcriber": {

            "provider": "deepgram",
            "model": "nova-2-phonecall",
            "language": "en-IN"
        },
        "firstMessageInterruptionsEnabled": True,
        "voicemailDetection": {

            "provider": "google",
            "type": "audio"
        },
        "credentials": [

        {
            "provider": "google",
            "apiKey": os.getenv("GOOGLE_API_KEY"),
            "name": "GOOGLE_API_KEY"
        },

        {
            "provider": "deepgram",
            "apiKey": os.getenv("DEEPGRAM_API_KEY"),
            "name": "DEEPGRAM_API_KEY"
        }
        
    ],
        "voicemailMessage": "Hey! I am Dhanamitra, I am here to help you with your loan recovery, I will call you back at the earliest.",
        "endCallMessage": "Thank you for your time, have a great day!",
        "server": {

            "url": f"{server_url}/vapi-webhook"
        },

        "analysisPlan": {

            "structuredDataPlan": {
                "enabled": True,

                "schema": {
                    "type": "object",
                    "properties": {
                        "call_outcome": {
                            "type": "string",
                            "enum": ["PAYMENT_COMPLETED", "CALLBACK_REQUESTED", "PROMISED_TO_PAY", "VOICEMAIL", "NO_ANSWER", "BUSY", "FAILED", "WRONG_NUMBER"]
                        },
                        "customer_sentiment": {
                            "type": "string",
                            "enum": ["Positive", "Neutral", "Negative"]
                        }
                    },
                    "required": ["call_outcome", "customer_sentiment"]
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("Voice agent created successfully")
    else:
        print("Failed to create voice agent")
        return None
    
    return response.json()