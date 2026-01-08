import requests
from dotenv import load_dotenv
import os

load_dotenv()


def create_voice_agent(first_name: str, tool_ids: list):

    url = "https://api.vapi.ai/assistant"

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
                    "content":
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
        "firstMessage": f"Hello! am I speaking to {first_name}?",
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
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("Voice agent created successfully")
    else:
        print("Failed to create voice agent")
        return None
    
    return response.json()