from pydantic import BaseModel
from prompts import QUESTION_DECOMPOSITION_PROMPT
import json
from typing import List
from state import ChatbotState
from typing import Any

class Decomposer_Schema(BaseModel):
    sub_questions: List[str]
    
class DecomposerService:
    def __init__(self, client):
        self.client = client

    def decompose_question(self, state: ChatbotState) -> dict[str, Any]:
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Decompose this question into specific sub-questions: {state['rephrased_question']}",
            config={
                'system_instruction': QUESTION_DECOMPOSITION_PROMPT,
                'response_mime_type': 'application/json',
                'response_schema': Decomposer_Schema,
            },
        )
        sub_questions = json.loads(response.text)['sub_questions']
        return {
            "sub_questions": sub_questions
        }
    