from google.adk.agents import ParallelAgent
from pydantic import BaseModel, Field
from ..quiz_agent.agent import quiz_agent_function
from ..flashcard_agent.agent import flashcard_agent_function
from ..podcast_agent.agent import podcast_agent_function
from ..image_agent.agent import image_agent_function

count = 0

def flashcard_quiz_podcast_image_agent_function() -> ParallelAgent:      
    global count
    count += 1

    flashcard_agent = flashcard_agent_function()
    quiz_agent = quiz_agent_function()
    podcast_agent = podcast_agent_function()
    image_agent = image_agent_function()
    
    # Parallel Agent preserves the order of results inherently.
    flashcard_quiz_podcast_image_agent = ParallelAgent(    
        name=f"flashcard_quiz_podcast_image_agent_{count}",
        sub_agents=[
            flashcard_agent,
            quiz_agent,
            podcast_agent,
            image_agent
        ],
        description="The pipeline that creates flashcards, quizzes, podcasts and images for a given topic parallelly"
    )

    return flashcard_quiz_podcast_image_agent
    


