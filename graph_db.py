from neo4j import GraphDatabase
from uuid import uuid4
from cypher import *
from utils import embed_query

class GraphDBService:
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def run_query(self, query: str, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def import_data(self, file_name: str, chunk: str, entities: list[dict], relationships: list[dict]) -> None:
        self.run_query(CONSTRAINT_NAME_QUERY)
        self.run_query(CONSTRAINT_UID_DESCRIPTION_QUERY)
        self.run_query(CONSTRAINT_UID_RELATIONSHIP_QUERY)
        self.run_query(CONSTRAINT_UID_CHUNK_QUERY)
        self.run_query(CONSTRAINT_FILE_NAME_QUERY)
        
        # Tạo chunk embedding 1 lần duy nhất
        chunk_id = str(uuid4())
        chunk_embeddings = embed_query(chunk)
        
        for entity in entities:
            self.run_query(
                CREATE_ENTITY_QUERY,
                {   
                    "file_name": file_name,
                    "chunk_uid": chunk_id,
                    "chunk_text": chunk,
                    "chunk_embeddings": chunk_embeddings,  # Sử dụng embedding đã tạo
                    "name": entity["name"],
                    "type": entity["type"],
                    "description": entity["description"],
                    "uid": entity["uid"],
                    "embeddings": entity["embeddings"]
                }
            )
            
        for relationship in relationships:
            self.run_query(
                CREATE_RELATIONSHIP_QUERY,
                {
                    "source_name": relationship["source_name"],
                    "target_name": relationship["target_name"],
                    "uid1": relationship["uid1"],
                    "uid2": relationship["uid2"],
                    "description": relationship["description"],
                    "score": relationship["score"],
                    "embeddings": relationship["embeddings"]
                }
            )