from typing import Any
from pydantic import BaseModel

class ChatbotInput(BaseModel):
    raw_question: str 
    rephrased_question: str
    sub_questions: list[str]
    conversation_history: list[Any]
    refined_contexts: list[str]
    answer: str