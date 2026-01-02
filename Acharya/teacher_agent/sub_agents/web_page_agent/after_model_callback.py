from google.adk.models import LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

def citation_retrieval_after_model_callback(
    llm_response: LlmResponse,
    callback_context: CallbackContext,) -> LlmResponse:
    """Adds citations to the response if grounding metadata is present."""
    chunks = llm_response.grounding_metadata.grounding_chunks

    if not chunks:
        return llm_response
    
    parts = llm_response.content.parts
    if not parts:
        return llm_response

    citation_text = "\n\n## References\n"

    count = 0

    for chunk in chunks:
        if chunk.web and count < 5:
            url = chunk.web.uri
            title = chunk.web.title
            citation_text += f"- [{title}]({url})\n"
            count += 1
        
        if count == 5:
            break
            
    parts.append(types.Part(text=citation_text))

    return LlmResponse(content=types.Content(parts=parts))