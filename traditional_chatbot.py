import json
from state import ChatbotState
from typing import Any
from prompts import TRADITIONAL_CHATBOT_PROMPT
from pydantic import BaseModel

class TraditionalChatbot_Schema(BaseModel):
    final_answer: str


class TraditionalChatbotService:
    def __init__(self, client):
        self.client = client

    def traditional_answer(self, state: ChatbotState) -> dict[str, Any]:
        try:

            completion = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"The question is: {state['rephrased_question']}. Here is the conversation history: {state['conversation_history']}.",
                config={
                    "system_instruction": TRADITIONAL_CHATBOT_PROMPT,
                    "response_mime_type": "application/json",
                    "response_schema": TraditionalChatbot_Schema,
                }
            )
            
            return {
                "answer": json.loads(completion.text)['final_answer'],
            }

        except Exception as e:
            return {
                "answer": f"Error occurred while aggregating answer: {str(e)}",
            }

