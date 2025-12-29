from google.adk.agents import Agent
from pydantic import BaseModel, Field
from .instructions import topic_generator_agent_instruction
from .after_agent_callback import after_agent_callback
from typing import List, Dict

class TopicGenerator(BaseModel):
    """Model representing the generated subtopics for a given educational topic."""
    subtopics: List[str] = Field(
        ..., 
        description="A list of subtopics with proper formatting (e.g., 'Subtopic Name, Another Subtopic, Third Subtopic')"
    )
    count: int = Field(
        ..., 
        description="The total number of subtopics generated (must match the number of items in the subtopics list)",
        ge=5,  # Minimum 5 subtopics
        le=10  # Maximum 10 subtopics
    )



topic_generator_agent = Agent(
    name="topic_generator_agent",
    model="gemini-2.5-flash",  
    description="Analyzes topics and generates pedagogically sound subtopics for educational content creation",
    instruction=topic_generator_agent_instruction,
    tools=[],
    output_schema=TopicGenerator,
    output_key="subtopics",
    generate_content_config={
        "temperature": 0.3,  # Lower temperature for more deterministic subtopic generation
    },
    after_agent_callback = after_agent_callback
)

# {"subtopics": "1. Origins and the Tim Berners-Lee Vision\n2. The Client-Server Architecture of the Web\n3. Uniform Resource Locators (URLs) and Domain Name System (DNS)\n4. Hypertext Transfer Protocol (HTTP) and Secure Communication (HTTPS)\n5. The Role of HTML in Structuring Web Content\n6. Styling and Layout with Cascading Style Sheets (CSS)\n7. Client-Side Scripting and Web Interactivity with JavaScript\n8. Web Browser Functionality and Rendering Engines\n9. Search Engine Mechanics: Crawling, Indexing, and Ranking\n10. The Evolution of the Web: From Static Pages to Semantic and Decentralized Webs", "count": 10}