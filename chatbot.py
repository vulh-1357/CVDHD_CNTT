from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.graph import END 
from rephraser import RephraserService
from decomposer import DecomposerService
from sub_agent import SubAgentService
from aggregator import AggregatorService
from memory import MemoryService
from functools import cached_property
from google import genai
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda
from concurrent.futures import ThreadPoolExecutor
from fastapi import BackgroundTasks
import os 
from state import ChatbotState, SubAgentState
from typing import Any
from models import ChatbotInput

load_dotenv()

class ChatbotService:
    
    @cached_property
    def client(self) -> genai.Client:
        return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    @property
    def rephraser(self) -> RephraserService:
        return RephraserService(self.client)

    @property
    def decomposer(self) -> DecomposerService:
        return DecomposerService(self.client)

    @property
    def sub_agent(self) -> SubAgentService:
        return SubAgentService(self.client)

    @property
    def aggregator(self) -> AggregatorService:
        return AggregatorService(self.client)

    @property
    def memory_service(self) -> MemoryService:
        return MemoryService()

    @property
    def nodes(self) -> dict[str, Any]:
        return {
            "rephrase_question": self.rephraser.rephrase_question,
            "decompose_question": self.decomposer.decompose_question,
            "sub_agent": RunnableLambda(
                self.gather_refined_contexts,
            ),
            "answer_aggregator": self.aggregator.aggregate_answer,
            "memory_retrieval": self.memory_service.retrieve_memory,
        }
        
    def gather_refined_contexts(self, state: ChatbotState) -> dict[str, Any]:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.sub_agent.compiled_graph.invoke, SubAgentState(
                    sub_question=sub_question,
                    raw_context="",
                    refined_context=""
                )): sub_question for sub_question in state['sub_questions']
            }
            results = []
            for future in futures:
                result = future.result()
                if result and 'refined_context' in result:
                    results.append(result['refined_context'])
            return {
                "refined_contexts": results
            }
            
    @property
    def compiled_graph(self) -> StateGraph:
        graph = StateGraph(ChatbotState)
        for key, tool in self.nodes.items():
            graph.add_node(key, tool)
        
        graph.add_edge(START, "memory_retrieval")
        graph.add_edge("memory_retrieval", "rephrase_question")
        graph.add_edge("rephrase_question", "decompose_question")
        graph.add_edge("decompose_question", "sub_agent")
        graph.add_edge("sub_agent", "answer_aggregator")
        graph.add_edge("sub_agent", END)
        
        return graph.compile()

    def process(self, input: ChatbotInput, background_tasks: BackgroundTasks) -> dict[str, Any]:
        result = self.compiled_graph.invoke(
            ChatbotState(
                raw_question=input.raw_question,
                rephrased_question=input.rephrased_question,
                sub_questions=input.sub_questions or [],
                answer=input.answer or "",
                conversation_history=input.conversation_history or [],
                refined_contexts=input.refined_contexts or []
            )
        )
        background_tasks.add_task(
            self.memory_service.memory_adding,
            state=result
        )
        return {
            "answer": result.get('answer', 'No answer found.')
        }