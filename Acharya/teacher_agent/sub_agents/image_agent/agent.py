from google.adk.agents import Agent
from dotenv import load_dotenv, find_dotenv
from .tools import image_tool

load_dotenv(find_dotenv())

count = 0

def image_agent_function() -> Agent: 
    global count
    count += 1

    image_agent = Agent(
    name=f"image_agent_{count}",
    model="gemini-2.5-flash-lite",
    description="Generates images for a given topic",
    tools=[image_tool],
    output_key="image_url",
)

    return image_agent










