import ollama
from constant import DEFAULT_TUPLE_DELIMITER, DEFAULT_RECORD_DELIMITER

def embed_query(query) -> list[float]: 
    response = ollama.embed(model="mxbai-embed-large", input=query)
    return response["embeddings"][0]

def postprocess_result(result: str) -> list[str]:
    return result.replace('(', '').replace(')', '').replace('"', '').replace(DEFAULT_RECORD_DELIMITER, '').split(DEFAULT_TUPLE_DELIMITER)