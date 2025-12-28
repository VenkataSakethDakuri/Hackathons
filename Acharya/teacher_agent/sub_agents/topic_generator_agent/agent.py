from google.adk.agents import Agent
from pydantic import BaseModel, Field
from instructions import topic_generator_agent_instruction

class TopicGenerator(BaseModel):
    """Model representing the generated subtopics for a given educational topic."""
    subtopics: str = Field(
        ..., 
        description="A numbered list of subtopics with proper formatting (e.g., '1. Subtopic Name\\n2. Another Subtopic\\n...')"
    )
    count: int = Field(
        ..., 
        description="The total number of subtopics generated (must match the number of items in the subtopics list)",
        ge=5,  # Minimum 5 subtopics
        le=10  # Maximum 10 subtopics
    )



topic_generator_agent = Agent(
    name="topic_generator_agent",
    model="gemini-3-flash-preview",  
    description="Analyzes topics and generates pedagogically sound subtopics for educational content creation",
    instruction=topic_generator_agent_instruction,
    tools=[],
    output_schema=TopicGenerator,
    output_key="subtopics",
    generate_content_config={
        "temperature": 0.3,  # Lower temperature for more deterministic subtopic generation
    }
)