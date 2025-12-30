from google.adk.agents import SequentialAgent
from ..web_page_agent import web_page_agent_function
# from ..quiz_agent import quiz_agent
# from ..flashcard_agent import flashcard_agent
from ..flashcard_quiz_podcast_agent.agent import flashcard_quiz_podcast_agent_function


count = 0


def web_page_content_function(subtopic: str) -> SequentialAgent: 

    global count
    count += 1

    web_page_agent = web_page_agent_function()
    flashcard_quiz_podcast_agent = flashcard_quiz_podcast_agent_function()

    web_page_agent.instruction = """
    You are an expert technical writer and educator. Your task is to write high-quality web page content for the subtopic: "{subtopic}".

    Guidelines:
    1.  **Structure**: Use clear Markdown headings (##, ###), bullet points, and short paragraphs to make the content scannable.
    2.  **Tone**: Educational, engaging, and professional. Avoid overly academic jargon unless necessary, and explain terms if used.
    3.  **Depth**: Cover the key concepts, importance, and practical applications of the subtopic.
    4.  **Format**: Return *only* the Markdown content. Do not include conversational filler like "Here is the content."
    """

    flashcard_quiz_podcast_agent.sub_agents[0].instruction = """
    You are a specialist in learning retention and flashcard design. Create 5 high-quality flashcards based *strictly* on the provided webpage content for the subtopic: "{subtopic}".

    Source Content:
    {{webpage_content}}

    Guidelines for Flashcards:
    1.  **Focus**: Each card should test a single distinct concept or fact from the text.
    2.  **Clarity**: Questions should be unambiguous. Answers should be concise.
    3.  **Format**: Return the output as a list of pairs in the format:
        - Q: [Question]
          A: [Answer]
    """

    flashcard_quiz_podcast_agent.sub_agents[1].instruction = """
    You are an assessment expert. Create a 5-question Multiple Choice Quiz (MCQ) to test the user's understanding of the subtopic "{subtopic}", based *only* on the provided content.

    Source Content:
    {{webpage_content}}

    Guidelines:
    1.  **Difficulty**: Mix of recall (easy) and conceptual application (medium).
    2.  **Options**: Provide 4 options (A, B, C, D) for each question. Only one should be correct.
    3.  **Format**: Present the output clearly as follows:
        1. [Question Text]
           A) [Option]
           B) [Option]
           C) [Option]
           D) [Option]
           **Correct Answer:** [Option Letter] - [Brief Explanation]
    """



    web_page_content_agent = SequentialAgent(
        name = f"web_page_content_function_agent_{count}",
        description = "Generates web page content for a given topic",
        sub_agents=[
            web_page_agent,
            # flashcard_agent,
            # quiz_agent,
            flashcard_quiz_podcast_agent,
        ],
    )

    return web_page_content_agent