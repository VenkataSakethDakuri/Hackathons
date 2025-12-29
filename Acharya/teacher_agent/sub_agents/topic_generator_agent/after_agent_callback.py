from typing import List, Dict
from google.adk.agents.callback_context import CallbackContext
from google.genai import types


def after_agent_callback(callback_context: CallbackContext) -> Dict[str, List[str]]:
    """
    This function takes a list of subtopics and returns a dictionary with the subtopics formatted.
    """  
    
    initial_list = callback_context.session.state["subtopics"]["subtopics"]
    formatted_list = [subtopic.lower().strip().replace(" ", "_") for subtopic in initial_list]

    callback_context.session.state["subtopics"]["subtopics"] = formatted_list

    print("AAC")
    print(callback_context.session.state["subtopics"]["subtopics"])

    return None
    
    


