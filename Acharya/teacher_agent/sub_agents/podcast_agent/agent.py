from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List
import asyncio
from google.adk.agents.callback_context import CallbackContext
from .after_agent_callback import after_agent_callback
from typing import List
from typing import Literal

count = 0

class DialogueLine(BaseModel):
    """Represents a single line of dialogue in the podcast script."""
    speaker: Literal["Alice", "Bob"] = Field(
        ..., 
        description="The name of the speaker. Must be strictly 'Alice' or 'Bob'."
    )
    text: str = Field(
        ..., 
        description="The spoken text for this turn. strictly exclude stage directions like '(laughs)'."
    )

class PodcastScript(BaseModel):
    """Represents the full script of the podcast."""
    dialogue: List[DialogueLine] = Field(
        ..., 
        description="The sequence of conversation between Alice and Bob."
    )

def podcast_agent_function() -> Agent: 
    global count
    count += 1

    podcast_agent = Agent(
        name=f"podcast_agent_{count}",
        model = "gemini-2.5-flash-lite",
        description="Generates podcast content for a given topic",
        tools=[],
        output_key="podcast_content",
        output_schema=PodcastScript,
        after_agent_callback=after_agent_callback,
    )

    return podcast_agent
