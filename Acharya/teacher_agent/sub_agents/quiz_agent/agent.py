from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List
import asyncio
from google.adk.agents.callback_context import CallbackContext
from typing import List

class Quiz(BaseModel):
    """Model representing a quiz with questions and answers."""
    questions: List[str] = Field(..., description="A list of questions for the quiz")
    options: List[List[str]] = Field(..., description="A list of options for each question")
    correct_answers: List[str] = Field(..., description="A list of correct answers for each question along with explanation")

class QuizList(BaseModel):
    quiz: List[Quiz] = Field(..., description="A list of quizzes",
    min_length = 5,
    max_length = 5,
    )

count = 0


async def after_agent_callback(callback_context: CallbackContext):
    await asyncio.sleep(60)

def quiz_agent_function() -> Agent:
    global count
    count += 1

    quiz_agent = Agent(
    name = f"quiz_agent_{count}",
    model = "gemini-2.5-flash-lite",
    description = "Generates a quiz for a given topic",
    tools = [],
    output_key = "quiz",
    output_schema = QuizList,
    after_agent_callback = after_agent_callback
)

    return quiz_agent
