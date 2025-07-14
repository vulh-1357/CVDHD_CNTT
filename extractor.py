from google import genai
from google.genai.types import GenerateContentConfig
from prompts import GRAPH_EXTRACTION_PROMPT
from utils import postprocess_result, embed_query
from constant import DEFAULT_RECORD_DELIMITER
from typing import Any
from uuid import uuid4

class ExtractorService:

    def __init__(self, client: genai.Client) -> None:
        self.client = client

    def extract_raw(self, markdown_content: str) -> list[str]:
        completion = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=markdown_content,
            config=GenerateContentConfig(
                system_instruction=GRAPH_EXTRACTION_PROMPT,
            ),
        )
        return completion.text.strip().split(DEFAULT_RECORD_DELIMITER + "\n")
    
    def extract_entities(self, raw_results: list[str]) -> list[dict[str, Any]]:
        entities = []
        for result in raw_results:
            tuple_data = postprocess_result(result)
            if tuple_data[0] == "entity":
                entities.append(
                    {
                        "name": tuple_data[1],
                        "type": tuple_data[2],
                        "uid": str(uuid4()),
                        "description": tuple_data[3],
                        "embeddings": embed_query(tuple_data[3]),
                    }
                )
        return entities
    
    def extract_relationships(self, raw_results: list[str]) -> list[dict[str, Any]]:
        relationships = []
        for result in raw_results:
            tuple_data = postprocess_result(result)
            if tuple_data[0] == "relationship":
                relationships.append(
                    {
                        "source_name": tuple_data[1],
                        "target_name": tuple_data[2],
                        "uid1": str(uuid4()),
                        "uid2": str(uuid4()),
                        "description": tuple_data[3],
                        "score": int(tuple_data[4]),
                        "embeddings": embed_query(tuple_data[3]),
                    }
                )
        return relationships
