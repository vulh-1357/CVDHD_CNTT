import ollama
from typing import Any
from constant import DEFAULT_TUPLE_DELIMITER, DEFAULT_RECORD_DELIMITER

def embed_query(query) -> list[float]: 
    response = ollama.embed(model="mxbai-embed-large", input=query)
    return response["embeddings"][0]

def postprocess_result(result: str) -> list[str]:
    return result.replace('(', '').replace(')', '').replace('"', '').replace(DEFAULT_RECORD_DELIMITER, '').split(DEFAULT_TUPLE_DELIMITER)


def format_context(context_data: list[dict[str, Any]]) -> str:
    if not context_data:
        return "No relevant information found."
    
    formatted_context = []
    for item in context_data:
        name = item.get('name', 'Unknown')
        descriptions = item.get('entity_description', [])
        relationships = item.get('relationship_descriptions', [])
        
        context_text = f"**{name}:**\n"
        if descriptions:
            context_text += f"Description: {' '.join(descriptions)}\n"
        if relationships:
            context_text += f"Relationships: {' '.join(relationships)}\n"
        
        formatted_context.append(context_text)
    
    return "\n".join(formatted_context)

def build_conversation(conversation_history: list[dict[str, str]]) -> str:
    if not conversation_history:
        return "No conversation history available."
    
    formatted_conversation = []
    for entry in conversation_history:
        role = entry.get('type', 'user')
        content = entry.get('content', '')
        formatted_conversation.append(f"{role.capitalize()}: {content}")
    
    return "\n".join(formatted_conversation)