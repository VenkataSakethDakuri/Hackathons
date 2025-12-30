from google.adk.agents import Agent

count = 0

def web_page_agent_function() -> Agent: 

    global count
    count += 1

    web_page_agent = Agent(
        name = f"web_page_agent_{count}",
        description = "Generates web page content for a given topic",
        tools = [],
        output_key = "webpage_content",
    )

    return web_page_agent