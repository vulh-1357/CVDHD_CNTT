import psycopg2
import json
from state import ChatbotState
from functools import cached_property
from dotenv import load_dotenv
import os 
from typing import Any

load_dotenv()

class MemoryService:
    
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
            
            return connection  # Return connection, not cursor
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None
        
    def retrieve_memory(self, state: ChatbotState) -> dict[str, Any]:
        connection = self.db_connection
        if not connection:
            return {"conversation_history": ""}

        try:
            cursor = connection.cursor()
            query = "SELECT * FROM message"
            cursor.execute(query)
            results = cursor.fetchall()
            return {
                "conversation_history": self._build_conversation_history(results) if len(results) <= 5 else self._build_conversation_history(results[-5:])
            }
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return {"conversation_history": ""}
        finally:
            cursor.close()
            
    def memory_adding(self, state: ChatbotState) -> None:
        connection = self.db_connection
        if not connection:
            return

        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO message (question, rephrased_question, sub_questions, answer)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (
                state['raw_question'],
                state['rephrased_question'],
                json.dumps(state['sub_questions']),
                state.get('answer', '')
            ))
            connection.commit()  # Commit on connection, not cursor
        except Exception as e:
            print(f"Error adding memory: {e}")
        finally:
            cursor.close()
    
    def _build_conversation_history(self, results: list) -> str:
        history = []
        for record in results:
            history.append(f"User: {record[2]}\nAssistant: {record[4]}")
        return "\n".join(history)
