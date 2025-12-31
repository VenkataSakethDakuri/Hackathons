from google.adk.agents import Agent
import asyncio
from google.adk.agents.callback_context import CallbackContext

count = 0

async def after_agent_callback(callback_context: CallbackContext):
    await asyncio.sleep(60)

def web_page_agent_function() -> Agent: 

    global count
    count += 1

    web_page_agent = Agent(
        name = f"web_page_agent_{count}",
        model = "gemini-2.5-flash-lite",
        description = "Generates web page content for a given topic",
        tools = [],
        output_key = "webpage_content",
        after_agent_callback = after_agent_callback
    )

    return web_page_agent