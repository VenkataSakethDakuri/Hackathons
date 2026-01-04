import asyncio
import os
import sys
from pathlib import Path
import shutil

from dotenv import load_dotenv
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types
from teacher_agent.sub_agents.web_page_content_function.function import web_page_content_function
from teacher_agent.sub_agents.factory_agent.agent import factory_agent
from teacher_agent.sub_agents.topic_generator_agent.agent import topic_generator_agent

# Load environment variables
load_dotenv()

# Local storage - Use absolute path for SQLite
# Use relative path for SQLite to avoid Windows absolute path issues

# use sqlite + aiosqlite for async support
db_url = "sqlite+aiosqlite:///./Acharya.db"
session_service = DatabaseSessionService(db_url=db_url)


# async allows streaming
async def main_async():



    APP_NAME = "Acharya"
    USER_ID = "Saketh"
    
    topic = input("\nEnter the topic you want to learn about: ").strip()
    
    if not topic:
        print("Error: Topic cannot be empty!")
        return {"error": "No topic provided"}
    
    # Set initial state with the user's topic
    initial_state = {
        "topic": topic,  # This will be accessible to all agents via {topic}
    }

    existing_sessions = await session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    if existing_sessions and len(existing_sessions.sessions) > 0:
        # Use the most recent session
        SESSION_ID = existing_sessions.sessions[0].id
        print(f"Continuing existing session: {SESSION_ID}")
        
        # Update the session state with the new topic
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
    
    # await session_service.delete_session(
    #         app_name=APP_NAME,
    #         user_id=USER_ID,
    #         session_id=SESSION_ID,
    #     )
    
    print(session.state)




if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\nForce exit.")
        os._exit(0)
    
    print("Exiting process...")
    os._exit(0)
