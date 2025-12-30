import asyncio
import os
import sys

from dotenv import load_dotenv
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types
from teacher_agent.agent import teacher_agent

# Load environment variables
load_dotenv()

# Local storage - Use absolute path for SQLite
# Use relative path for SQLite to avoid Windows absolute path issues

# use sqlite + aiosqlite for async support
db_url = "sqlite+aiosqlite:///./Acharya.db"
session_service = DatabaseSessionService(db_url=db_url)


# async allows streaming
async def main_async():

    try:

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

            session.state["topic"] = topic
            
        else:
            # Create a new session with initial state
            # Session = Events + State
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                state=initial_state,
            )

            SESSION_ID = session.id
            print(f"Created new session: {SESSION_ID}")

        runner = Runner(
            agent=teacher_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )
        
        # Send a message to trigger the agent workflow
        content = types.Content(
            role="user", 
            parts=[types.Part(text=f"Please generate educational content for the topic: {topic}")]
        )
        
        final_response = None
        async for response in runner.run_async(
            user_id=USER_ID, 
            session_id=SESSION_ID, 
            new_message=content
        ):
            if response.is_final_response():
                final_response = response.content
            
            text_content = final_response.parts[0].text
        
        if final_response:
            print(f"\n{text_content}\n")

        print("Session completed. Cleaning up...")
        
        print(session.state["subtopics"]["subtopics"])

        await session_service.delete_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )   
        
        print("Session data deleted.")

        return {"final_response": final_response}      

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        os._exit(0)
    except Exception as e:
        print(f"\n\nError occurred: {type(e).__name__}: {str(e)}")
        os._exit(1)



if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\nForce exit.")
        os._exit(0)
    
    print("Exiting process...")
    os._exit(0)
