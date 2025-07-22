import json
from state import ChatbotState
from typing import Any
from prompts import ANSWER_AGGREGATION_PROMPT
from pydantic import BaseModel

class Aggregator_Schema(BaseModel):
    final_answer: str


class AggregatorService:
    def __init__(self, client):
        self.client = client

    def aggregate_answer(self, state: ChatbotState) -> dict[str, Any]:
        try:
            user_message = f"""
            Main Question: {state['rephrased_question']}
            Sub-questions and related information:
            """

            sub_questions = state.get('sub_questions', [])
            refined_contexts = state.get('refined_contexts', [])
            
            for i, (sub_q, context) in enumerate(zip(sub_questions, refined_contexts), 1):
                user_message += f"""
                {i}. {sub_q}
                Context:
                {context}
                """

            user_message += """
            Please answer the main question based on the information from the sub-questions and context provided.
            """

            completion = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config={
                    "system_instruction": ANSWER_AGGREGATION_PROMPT,
                    "response_mime_type": "application/json",
                    "response_schema": Aggregator_Schema,
                }
            )
            
            return {
                "answer": json.loads(completion.text)['final_answer'],
            }

        except Exception as e:
            return {
                "answer": f"Error occurred while aggregating answer: {str(e)}",
            }

