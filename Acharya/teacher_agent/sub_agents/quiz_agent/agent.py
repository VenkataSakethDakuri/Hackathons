from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List

class Quiz(BaseModel):
    """Model representing a quiz with questions and answers."""
    questions: List[str] = Field(..., description="A list of questions for the quiz")
    options: List[List[str]] = Field(..., description="A list of options for each question")
    correct_answers: List[str] = Field(..., description="A list of correct answers for each question along with explanation")

quiz_agent = Agent(
    name = "quiz_agent",
    description = "Generates a quiz for a given topic",
    tools = [],
    output_key = "quiz",
    output_schema = Quiz,
)
