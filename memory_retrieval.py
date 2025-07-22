import psycopg2
from state import ChatbotState
from functools import cached_property
from dotenv import load_dotenv
import os 
from typing import Any

load_dotenv()

class MemoryRetrievalService:
    
    @cached_property
    def db_connection(self):
        try:
            connection = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', '15432'),
                database=os.getenv('POSTGRES_DB', 'chatbot'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres')
            )
            
            return connection.cursor()
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None
        
    def retrieve_memory(self, state: ChatbotState) -> dict[str, Any]:
        cursor = self.db_connection
        if not cursor:
            return []

        try:
            query = "SELECT * FROM message"
            cursor.execute(query)
            results = cursor.fetchall()
            return {
                "conversation_history": self._build_conversation_history(results)
            }
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return {"conversation_history": ""}
        finally:
            cursor.close()
            
    
    def _build_conversation_history(self, results: list) -> str:
        history = []
        for record in results:
            history.append(f"User: {record[2]}\nAssistant: {record[4]}")
        return "\n".join(history)
