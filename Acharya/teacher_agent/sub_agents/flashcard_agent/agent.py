from google.adk.agents import Agent
from pydantic import BaseModel, Field

class Flashcard(BaseModel):
    """Model representing a flashcard with a question and answer."""
    question: str = Field(..., description="The question for the flashcard")
    answer: str = Field(..., description="The answer to the flashcard question")

count = 0

def flashcard_agent_function() -> Agent:
    global count
    count += 1

    flashcard_agent = Agent(
    name = f"flashcard_agent_{count}",
    description = "Generates flashcards for a given topic",
    tools = [],
    output_key = "flashcards",
    output_schema = Flashcard,

    )

    return flashcard_agent  