from pydantic import BaseModel
from prompts import CONTEXT_REFINEMENT_PROMPT
import json
from pydantic import BaseModel
from state import SubAgentState
from langgraph.graph import StateGraph
from langgraph.graph import START, END
import httpx
from typing import Any
from utils import format_context

class ContextRefinement_Schema(BaseModel):
    refined_context: str

class ContextRefinementService:
    def __init__(self, client):
        self.client = client

    def refine_context(self, state: SubAgentState) -> dict[str, Any]:
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Refine the context for the sub-question '{state['sub_question']}': {state['raw_context']}",
            config={
                'system_instruction': CONTEXT_REFINEMENT_PROMPT,
                'response_mime_type': 'application/json',
                'response_schema': ContextRefinement_Schema,
            },
        )
        return {
            "refined_context": json.loads(response.text)['refined_context']
        }
    
def rag(state: SubAgentState) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "http://localhost:3010/query",
                json={"query": state["sub_question"], "threshold": 0.6}
            )
            if response.status_code == 200:
                return {
                    "raw_context": format_context(response.json()['results'])
                }
            else:
                return {
                    "raw_context": ""
                }
    except httpx.TimeoutException:
        return {
            "raw_context": ""
        }
    except httpx.ConnectError:
        return {
            "raw_context": ""
        }
    except Exception as e:
        return {
            "raw_context": ""
        }
            
class SubAgentService:
    def __init__(self, client):
        self.client = client
        self.context_refinement = ContextRefinementService(client)
        
    @property
    def compiled_graph(self):
        graph = StateGraph(SubAgentState)

        graph.add_node("rag", rag)
        graph.add_node("context_refinement", self.context_refinement.refine_context)
        graph.add_edge(START, "rag")
        graph.add_edge("rag", "context_refinement")
        graph.add_edge("context_refinement", END)
        return graph.compile()
    