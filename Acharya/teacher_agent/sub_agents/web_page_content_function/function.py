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

    web_page_agent.instruction = f"""
    You are an expert technical writer and educator. Your task is to write high-quality web page content for the subtopic: "{subtopic}".

    Guidelines:
    1.  **Structure**: Use clear Markdown headings (##, ###), bullet points, and short paragraphs to make the content scannable.
    2.  **Tone**: Educational, engaging, and professional. Avoid overly academic jargon unless necessary, and explain terms if used.
    3.  **Depth**: Cover the key concepts, importance, and practical applications of the subtopic.
    4.  **Format**: Return *only* the Markdown content. Do not include conversational filler like "Here is the content."
    """

    flashcard_quiz_podcast_agent.sub_agents[0].instruction = f"""
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

    flashcard_quiz_podcast_agent.sub_agents[1].instruction = f"""
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

    flashcard_quiz_podcast_agent.sub_agents[2].instruction = f"""
    You are a world-class podcast scriptwriter. Your task is to write a highly engaging, conversational script for a podcast episode about: "{subtopic}".

    **Source Material:**
    Base your script *strictly* on the following content:
    {{webpage_content}}

    **The Hosts:**
    1.  **Alice (The Host):** Energetic, curious, and represents the audience. She asks the "dumb questions" and drives the conversation forward.
    2.  **Bob (The Expert):** Knowledgeable but relatable. He explains complex ideas using simple analogies and metaphors. He is never boring or overly academic.

    **Critical Constraints (Optimized for Text-to-Speech):**
    1.  **Length:** The script MUST be between **800 to 1000 words**. This is strict to ensure the audio duration is 5-6 minutes.
    2.  **Format:** Write ONLY the spoken dialogue. Do NOT include stage directions like "(laughs)", "[Intro Music]", or "*sighs*" as the TTS engine will read these aloud.
    3.  **Tone:** Casual, fun, and fast-paced. Use contractions ("can't" instead of "cannot"), interjections ("Wow", "Right", "Exactly"), and rhetorical questions.
    4.  **Structure:**
        * **The Hook:** Start immediately with a surprising fact or question about the topic.
        * **The Deep Dive:** Alice and Bob unpack the source content. Alice challenges Bob to explain things simpler.
        * **The Outro:** A quick 1-sentence wrap-up and sign-off.

    **Output Format:**
    Return the script exactly in this pattern (and nothing else):

    Alice: [Dialogue]
    Bob: [Dialogue]
    Alice: [Dialogue]
    Bob: [Dialogue]
    ...
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