from pydantic import BaseModel
from prompts import REPHRASED_QUESTION_PROMPT
import json
from typing import Any
from state import ChatbotState

class Rephraser_Schema(BaseModel):
    rephrased_question: str
    need_rag: bool
    
class RephraserService:
    def __init__(self, client):
        self.client = client

    def rephrase_question(self, state: ChatbotState) -> dict[str, Any]:
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"The raw question is: {state['raw_question']}. Here is the conversation history: {state['conversation_history']}.",
            config={
                'system_instruction': REPHRASED_QUESTION_PROMPT,
                'response_mime_type': 'application/json',
                'response_schema': Rephraser_Schema,
            },
        )
        return {
            "rephrased_question": json.loads(response.text)['rephrased_question'],
            "need_rag": json.loads(response.text).get('need_rag', False)
        }