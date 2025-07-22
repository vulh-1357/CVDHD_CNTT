from typing import TypedDict
from typing import Any 

class ChatbotState(TypedDict):
    raw_question: str 
    rephrased_question: str
    sub_questions: list[str]
    conversation_history: list[dict[str, Any]]
    refined_contexts: list[str]
    answer: str
    
class SubAgentState(TypedDict):
    sub_question: str
    raw_context: str
    refined_context: str