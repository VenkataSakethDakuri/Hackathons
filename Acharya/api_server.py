"""
FastAPI Backend Server for Acharya
This file creates an API layer that connects the React frontend to the Python agentic system.
"""
import asyncio
import os
import uuid
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types
from teacher_agent.sub_agents.web_page_content_function.function import web_page_content_function
from teacher_agent.sub_agents.factory_agent.agent import factory_agent
from teacher_agent.sub_agents.topic_generator_agent.agent import topic_generator_agent

# Load environment variables
load_dotenv()

# Database setup
db_url = "sqlite+aiosqlite:///./Acharya.db"
session_service = DatabaseSessionService(db_url=db_url)

# In-memory store for session progress and results
# In production, use Redis or similar
session_store = {}

APP_NAME = "Acharya"


# Pydantic models for API
class TopicRequest(BaseModel):
    topic: str
    user_id: Optional[str] = "default_user"


class SessionResponse(BaseModel):
    session_id: str
    status: str
    message: str


class ContentResponse(BaseModel):
    session_id: str
    status: str  # "processing", "completed", "error"
    topic: str
    subtopics: list[str] = []
    content: list[dict] = []
    error: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Acharya API Server starting...")
    yield
    # Shutdown
    print("👋 Acharya API Server shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Acharya API",
    description="API for the Acharya AI-Powered Learning Companion",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate_content(session_id: str, topic: str, user_id: str):
    """
    Background task to run the agent pipeline and generate content.
    Updates session_store with progress and results.
    """
    try:
        session_store[session_id] = {
            "status": "processing",
            "topic": topic,
            "subtopics": [],
            "content": [],
            "progress": "Generating subtopics...",
            "error": None
        }

        # Create initial state
        initial_state = {"topic": topic}

        # Create a new ADK session
        adk_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            state=initial_state,
        )
        adk_session_id = adk_session.id
        
        # Store the ADK session ID for cleanup
        session_store[session_id]["adk_session_id"] = adk_session_id

        # Step 1: Run topic generator agent
        runner = Runner(
            agent=topic_generator_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        content = types.Content(
            role="user",
            parts=[types.Part(text=f"Please generate educational content for the topic: {topic}")]
        )

        async for response in runner.run_async(
            user_id=user_id,
            session_id=adk_session_id,
            new_message=content
        ):
            pass  # Process events

        # Wait for agent to complete and update state
        await asyncio.sleep(30)

        # Refresh session to get latest state
        adk_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=adk_session_id
        )

        # Extract subtopics
        if "subtopics" in adk_session.state and "subtopics" in adk_session.state["subtopics"]:
            subtopics_data = adk_session.state["subtopics"]
            subtopics_list = subtopics_data.get("subtopics", [])
            subtopic_count = subtopics_data.get("count", len(subtopics_list))

            session_store[session_id]["subtopics"] = subtopics_list
            session_store[session_id]["progress"] = f"Found {subtopic_count} subtopics. Generating content..."
            
            # Initialize empty content slots for each subtopic
            session_store[session_id]["content"] = [
                {
                    "webContent": "",
                    "flashcards": [],
                    "quiz": [],
                    "podcast": {"title": f"{subtopics_list[i]} Overview", "transcript": "", "audioUrl": ""},
                    "images": []
                } for i in range(subtopic_count)
            ]

            # Step 2: Create sub-agents for each subtopic
            sub_agents = []
            for i in range(subtopic_count):
                sub_agents.append(web_page_content_function(subtopics_list[i]))

            factory_agent.sub_agents = sub_agents

            # Step 3: Run factory agent (parallel content generation)
            runner = Runner(
                agent=factory_agent,
                app_name=APP_NAME,
                session_service=session_service,
            )

            await asyncio.sleep(30)
            
            # Start a background task to periodically update content
            update_task = asyncio.create_task(
                update_content_periodically(session_id, user_id, adk_session_id, subtopics_list, subtopic_count)
            )

            async for response in runner.run_async(
                user_id=user_id,
                session_id=adk_session_id,
                new_message=content
            ):
                pass  # Process events
            
            # Cancel the update task
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass

            # Final content extraction
            adk_session = await session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=adk_session_id
            )

            # Extract final content for each subtopic
            content_list = []
            for i in range(1, subtopic_count + 1):
                # Get podcast transcript/dialogue from state
                podcast_data = adk_session.state.get(f"podcast_content_{i}", {})
                podcast_transcript = ""
                if isinstance(podcast_data, dict) and "dialogue" in podcast_data:
                    # Format dialogue into readable transcript
                    for turn in podcast_data.get("dialogue", []):
                        podcast_transcript += f"{turn.get('speaker', 'Speaker')}: {turn.get('text', '')}\n"
                elif isinstance(podcast_data, str):
                    podcast_transcript = podcast_data

                subtopic_content = {
                    "webContent": adk_session.state.get(f"webpage_content_{i}", ""),
                    "flashcards": parse_flashcards(adk_session.state.get(f"flashcards_{i}", "")),
                    "quiz": parse_quiz(adk_session.state.get(f"quiz_{i}", "")),
                    "podcast": {
                        "title": f"{subtopics_list[i-1]} Overview",
                        "transcript": podcast_transcript,
                        # Serve local audio file via API endpoint
                        "audioUrl": f"http://localhost:8000/api/podcast/out_{i}.wav"
                    },
                    "images": [
                        # Serve local image file via API endpoint
                        {"url": f"http://localhost:8000/api/images/image_{i}.jpg", "title": f"{subtopics_list[i-1]} Visual"}
                    ]
                }
                content_list.append(subtopic_content)

            session_store[session_id]["content"] = content_list
            session_store[session_id]["status"] = "completed"
            session_store[session_id]["progress"] = "Content generation complete!"

            # Cleanup ADK session
            await session_service.delete_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=adk_session_id,
            )

        else:
            session_store[session_id]["status"] = "error"
            session_store[session_id]["error"] = "Failed to generate subtopics"

    except Exception as e:
        # Extract meaningful error message from potentially nested exceptions
        error_message = extract_error_message(e)
        
        session_store[session_id]["status"] = "error"
        session_store[session_id]["error"] = error_message
        print(f"Error generating content: {error_message}")
        
        # Also print full traceback for debugging
        import traceback
        traceback.print_exc()


async def update_content_periodically(session_id: str, user_id: str, adk_session_id: str, subtopics_list: list, subtopic_count: int):
    """Periodically check and update content as it becomes available."""
    while True:
        try:
            await asyncio.sleep(10)  # Check every 10 seconds
            
            # Get latest session state
            adk_session = await session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=adk_session_id
            )
            
            # Update content for each subtopic
            content_list = session_store[session_id].get("content", [])
            content_updated = False
            
            for i in range(1, subtopic_count + 1):
                idx = i - 1
                if idx >= len(content_list):
                    continue
                
                # Check for web content
                web_content = adk_session.state.get(f"webpage_content_{i}", "")
                if web_content and not content_list[idx].get("webContent"):
                    content_list[idx]["webContent"] = web_content
                    content_updated = True
                    session_store[session_id]["progress"] = f"Generated web content for: {subtopics_list[idx]}"
                
                # Check for flashcards
                flashcards = adk_session.state.get(f"flashcards_{i}", "")
                if flashcards and not content_list[idx].get("flashcards"):
                    content_list[idx]["flashcards"] = parse_flashcards(flashcards)
                    content_updated = True
                
                # Check for quiz
                quiz = adk_session.state.get(f"quiz_{i}", "")
                if quiz and not content_list[idx].get("quiz"):
                    content_list[idx]["quiz"] = parse_quiz(quiz)
                    content_updated = True
                
                # Check for podcast
                podcast_data = adk_session.state.get(f"podcast_content_{i}", {})
                if podcast_data and not content_list[idx].get("podcast", {}).get("transcript"):
                    podcast_transcript = ""
                    if isinstance(podcast_data, dict) and "dialogue" in podcast_data:
                        for turn in podcast_data.get("dialogue", []):
                            podcast_transcript += f"{turn.get('speaker', 'Speaker')}: {turn.get('text', '')}\n"
                    elif isinstance(podcast_data, str):
                        podcast_transcript = podcast_data
                    
                    if podcast_transcript:
                        content_list[idx]["podcast"]["transcript"] = podcast_transcript
                        content_list[idx]["podcast"]["audioUrl"] = f"http://localhost:8000/api/podcast/out_{i}.wav"
                        content_updated = True
                
                # Check for images
                image_url = adk_session.state.get(f"image_url_{i}", "")
                if image_url and not content_list[idx].get("images"):
                    content_list[idx]["images"] = [
                        {"url": f"http://localhost:8000/api/images/image_{i}.jpg", "title": f"{subtopics_list[idx]} Visual"}
                    ]
                    content_updated = True
            
            if content_updated:
                session_store[session_id]["content"] = content_list
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error updating content: {e}")
            continue


def extract_error_message(e):
    """Extract a user-friendly error message from an exception, including nested ones."""
    error_messages = []
    
    def extract_from_exception(exc):
        exc_str = str(exc)
        
        # Check for known API errors
        if "503" in exc_str or "overloaded" in exc_str.lower():
            return "Gemini API is temporarily overloaded. Please try again in a few minutes."
        elif "429" in exc_str or "rate limit" in exc_str.lower():
            return "API rate limit exceeded. Please wait a moment and try again."
        elif "401" in exc_str or "unauthorized" in exc_str.lower():
            return "API authentication failed. Please check your API key."
        elif "400" in exc_str or "invalid" in exc_str.lower():
            return f"Invalid request: {exc_str[:200]}"
        elif "timeout" in exc_str.lower():
            return "Request timed out. Please try again."
        elif "connection" in exc_str.lower():
            return "Connection error. Please check your internet connection."
        else:
            # Return a truncated version of the error
            return exc_str[:300] if len(exc_str) > 300 else exc_str
    
    # Handle ExceptionGroup (from parallel agents)
    if hasattr(e, 'exceptions'):
        for sub_exc in e.exceptions:
            # Recursively handle nested ExceptionGroups
            if hasattr(sub_exc, 'exceptions'):
                msg = extract_error_message(sub_exc)
            else:
                msg = extract_from_exception(sub_exc)
            if msg and msg not in error_messages:
                error_messages.append(msg)
    else:
        error_messages.append(extract_from_exception(e))
    
    # Deduplicate and join
    unique_messages = list(dict.fromkeys(error_messages))
    
    if len(unique_messages) == 0:
        return "An unknown error occurred. Please try again."
    elif len(unique_messages) == 1:
        return unique_messages[0]
    else:
        return " | ".join(unique_messages[:3])  # Limit to 3 messages


def parse_flashcards(data):
    """Parse flashcards from Pydantic schema format.
    
    Expected format from agent:
    {
        "flashcards": [
            {"question": "...", "answer": "..."},
            ...
        ]
    }
    """
    if not data:
        return []
    
    import json
    
    # If it's already a list of flashcard dicts
    if isinstance(data, list):
        return data
    
    # If it's a dict with 'flashcards' key (Pydantic output)
    if isinstance(data, dict):
        flashcards = data.get("flashcards", [])
        if isinstance(flashcards, list):
            return flashcards
        return []
    
    # If it's a string (JSON)
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            # Handle {"flashcards": [...]} format
            if isinstance(parsed, dict) and "flashcards" in parsed:
                return parsed["flashcards"]
            # Handle direct list format
            if isinstance(parsed, list):
                return parsed
        except:
            pass
    
    return []


def parse_quiz(data):
    """Parse quiz from Pydantic schema format and transform for frontend.
    
    Expected format from agent:
    {
        "quiz": [
            {
                "questions": ["q1", "q2", ...],
                "options": [["a", "b", "c", "d"], ...],
                "correct_answers": ["answer1 with explanation", ...]
            }
        ]
    }
    
    Output format for frontend:
    [
        {
            "question": "q1",
            "options": ["a", "b", "c", "d"],
            "correctIndex": 0  # index of correct answer in options
        },
        ...
    ]
    """
    if not data:
        return []
    
    import json
    
    # Parse JSON string if needed
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return []
    
    # Handle direct list (already parsed format)
    if isinstance(data, list):
        # Check if it's already in frontend format
        if len(data) > 0 and "question" in data[0] and "correctIndex" in data[0]:
            return data
        # Otherwise try to parse as quiz schema
        quiz_data = data
    # Handle dict with 'quiz' key (Pydantic output)
    elif isinstance(data, dict):
        quiz_data = data.get("quiz", [])
    else:
        return []
    
    # Transform quiz data to frontend format
    result = []
    for quiz in quiz_data:
        if not isinstance(quiz, dict):
            continue
            
        questions = quiz.get("questions", [])
        options_list = quiz.get("options", [])
        correct_answers = quiz.get("correct_answers", [])
        
        for i, question in enumerate(questions):
            if i >= len(options_list):
                continue
                
            options = options_list[i]
            correct_answer = correct_answers[i] if i < len(correct_answers) else ""
            
            # Find the correct index by matching the answer to options
            correct_index = 0
            for j, opt in enumerate(options):
                # Check if the correct answer starts with or contains the option
                if opt.lower() in correct_answer.lower() or correct_answer.lower().startswith(opt.lower()):
                    correct_index = j
                    break
            
            result.append({
                "question": question,
                "options": options,
                "correctIndex": correct_index,
                "explanation": correct_answer  # Include full explanation
            })
    
    return result


def parse_images(data):
    """Parse images from various formats."""
    if not data:
        return []
    
    if isinstance(data, list):
        return [{"url": img, "title": f"Image {i+1}"} if isinstance(img, str) else img for i, img in enumerate(data)]
    
    if isinstance(data, str):
        # Single URL
        return [{"url": data, "title": "Image"}]
    
    return []


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    return {"message": "Welcome to Acharya API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/generate", response_model=SessionResponse)
async def start_content_generation(request: TopicRequest, background_tasks: BackgroundTasks):
    """
    Start content generation for a topic.
    Returns a session_id that can be used to poll for results.
    """
    if not request.topic or not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    session_id = str(uuid.uuid4())
    
    # Start background task
    background_tasks.add_task(
        generate_content,
        session_id,
        request.topic.strip(),
        request.user_id
    )

    return SessionResponse(
        session_id=session_id,
        status="processing",
        message=f"Content generation started for topic: {request.topic}"
    )


@app.get("/api/status/{session_id}", response_model=ContentResponse)
async def get_generation_status(session_id: str):
    """
    Get the status and results of content generation.
    Poll this endpoint until status is 'completed' or 'error'.
    """
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    data = session_store[session_id]
    
    return ContentResponse(
        session_id=session_id,
        status=data["status"],
        topic=data["topic"],
        subtopics=data["subtopics"],
        content=data["content"],
        error=data.get("error")
    )


@app.get("/api/progress/{session_id}")
async def get_progress(session_id: str):
    """Get generation progress for UI updates."""
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    data = session_store[session_id]
    return {
        "status": data["status"],
        "progress": data.get("progress", ""),
        "subtopics_count": len(data["subtopics"])
    }


# Serve podcast audio files from the podcasts folder
@app.get("/api/podcast/{filename}")
async def get_podcast(filename: str):
    # Use absolute path to the podcasts folder
    podcast_path = Path(r"C:\Users\DELL\OneDrive\Desktop\Project\Hackathons\Acharya\podcasts") / filename
    if podcast_path.exists():
        # WAV files need audio/wav media type
        return FileResponse(podcast_path, media_type="audio/wav")
    raise HTTPException(status_code=404, detail=f"Podcast not found: {filename}")


# Serve images from the images folder
@app.get("/api/images/{filename}")
async def get_image(filename: str):
    # Use absolute path to the images folder
    image_path = Path(r"C:\Users\DELL\OneDrive\Desktop\Project\Hackathons\Acharya\images") / filename
    if image_path.exists():
        return FileResponse(image_path, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail=f"Image not found: {filename}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
