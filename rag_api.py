from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import uvicorn
from utils import embed_query
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CV RAG Service",
    description="A RAG service for querying CV data using vector similarity",
    version="1.0.0"
)

# Neo4j connection
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

if not all([uri, user, password]):
    raise ValueError("Neo4j credentials are not properly configured in environment variables")

driver = GraphDatabase.driver(uri, auth=(user, password))

def run_query(query: str, parameters=None):
    """Execute a Neo4j query and return results"""
    try:
        with driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

class QueryRequest(BaseModel):
    query: str
    threshold: float = 0.6

class EntityResult(BaseModel):
    name: str
    entity_description: List[str]
    relationship_descriptions: List[str]
    score: float = None

class RAGResponse(BaseModel):
    query: str
    results: List[EntityResult]
    total_results: int

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "CV RAG Service is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        test_query = "RETURN 1 as test"
        run_query(test_query)
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.post("/query", response_model=RAGResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with a natural language question
    
    Args:
        request: QueryRequest containing the query string and optional threshold
        
    Returns:
        RAGResponse with matching entities and their descriptions
    """
    try:
        # Generate embeddings for the query
        embeddings = embed_query(request.query)
        
        # First query: Find entities with similar descriptions
        entity_query = """
        MATCH (e:Entity)-[:DESCRIBED]->(h:DESCRIPTION)
        WHERE h.embeddings IS NOT NULL
        WITH e, h, gds.similarity.cosine(h.embeddings, $embedding) AS score
        WHERE score > $threshold
        RETURN e.name as name, h.text as entity_description, score
        ORDER BY score DESC
        """
        
        entity_results = run_query(entity_query, {
            "embedding": embeddings, 
            "threshold": request.threshold
        })
        
        if not entity_results:
            return RAGResponse(
                query=request.query,
                results=[],
                total_results=0
            )
        
        # Extract entity names for relationship query
        names = [record["name"] for record in entity_results]
        # Second query: Find relationships for the matched entities
        relationship_query = """
        MATCH (r:RELATIONSHIP)-[:RELATED]->(e1:Entity)
        WHERE e1.name IN $names
        MATCH (r)-[:DESCRIBED]->(d:DESCRIPTION)
        RETURN e1.name as name, d.text as relationship_description
        """
        
        relationship_results = run_query(relationship_query, {"names": names})
        
        # Merge results
        merged_results = []
        for record in entity_results:
            merge_result = {
                "name": record["name"],
                "entity_description": [record["entity_description"]],
                "relationship_descriptions": [],
                "score": record["score"]
            }
            
            # Add relationship descriptions for this entity
            for rel_record in relationship_results:
                if rel_record["name"] == record["name"]:
                    merge_result["relationship_descriptions"].append(
                        rel_record["relationship_description"]
                    )
            
            merged_results.append(EntityResult(**merge_result))
        
        return RAGResponse(
            query=request.query,
            results=merged_results,
            total_results=len(merged_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/search/{query}")
async def search_get(query: str, threshold: float = 0.6):
    """
    GET endpoint for simple queries
    
    Args:
        query: The search query string
        threshold: Similarity threshold (default: 0.6)
        
    Returns:
        RAGResponse with matching results
    """
    request = QueryRequest(query=query, threshold=threshold)
    return await query_rag(request)

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    if driver:
        driver.close()

if __name__ == "__main__":
    uvicorn.run(
        "rag_api:app",
        host="0.0.0.0",
        port=3010,
        reload=True,
        log_level="info"
    )
