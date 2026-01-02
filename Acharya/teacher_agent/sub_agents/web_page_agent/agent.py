from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import google_search
from google.genai import types
from pydantic import BaseModel, Field
from .after_model_callback import citation_retrieval_after_model_callback
import asyncio

count = 0

async def after_agent_callback(callback_context: CallbackContext):
    await asyncio.sleep(45)

def web_page_agent_function() -> Agent: 
    global count
    count += 1

    web_page_agent = Agent(
        name = f"web_page_agent_{count}",
        model = "gemini-2.5-flash-lite", 
        description = "Generates web page content for a given topic",
        tools = [google_search],
        instruction = "You are a professional content writer. Write a detailed webpage about the user's topic.",
        output_key = f"webpage_content_{count}",
        after_model_callback = citation_retrieval_after_model_callback,
        after_agent_callback = after_agent_callback
    )

    return web_page_agent