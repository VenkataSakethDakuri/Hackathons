from google.adk.agents import Agent
from pydantic import BaseModel, Field
import asyncio
from google.adk.agents.callback_context import CallbackContext

class Flashcard(BaseModel):
    """Model representing a flashcard with a question and answer."""
    question: str = Field(..., description="The question for the flashcard")
    answer: str = Field(..., description="The answer to the flashcard question")

count = 0

async def after_agent_callback(callback_context: CallbackContext):
    await asyncio.sleep(60)

def flashcard_agent_function() -> Agent:
    global count
    count += 1

    flashcard_agent = Agent(
    name = f"flashcard_agent_{count}",
    model = "gemini-2.5-flash-lite",
    description = "Generates flashcards for a given topic",
    tools = [],
    output_key = "flashcards",
    output_schema = Flashcard,
    after_agent_callback = after_agent_callback

    )

    return flashcard_agent  