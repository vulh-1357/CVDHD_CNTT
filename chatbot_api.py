import uvicorn 
from fastapi import FastAPI, BackgroundTasks 
from chatbot import ChatbotService
from models import ChatbotInput

app = FastAPI(
    title="Chatbot API",
    description="API for the CV Chatbot",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Chatbot API is running"}

@app.post("/chat")
def chat(
    input: ChatbotInput,
    background_tasks: BackgroundTasks
):
    chatbot = ChatbotService()
    result = chatbot.process(input, background_tasks)
    return result

if __name__ == "__main__":
    uvicorn.run(
        "chatbot_api:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )