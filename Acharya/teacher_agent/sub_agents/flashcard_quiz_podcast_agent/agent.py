from google.adk.agents import ParallelAgent
from pydantic import BaseModel, Field
from ..web_page_agent.agent import web_page_agent
from ..quiz_agent.agent import quiz_agent
from ..flashcard_agent.agent import flashcard_agent
# from .podcast_agent.agent import podcast_agent



flashcard_quiz_podcast_agent = ParallelAgent(    
    name="flashcard_quiz_podcast_agent",
    sub_agents=[
        flashcard_agent,
        quiz_agent,

        # podcast_agent
    ],
    description="The pipeline that creates flashcards, quizzes, and podcasts for a given topic parallelly"
)
    


