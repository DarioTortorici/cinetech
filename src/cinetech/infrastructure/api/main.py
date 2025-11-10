from fastapi import FastAPI
from pydantic import BaseModel, Field

from cinetech.application.chat_service.chat_service import ChatService
from cinetech.domain.agent import get_context
from cinetech.infrastructure.api import ingest_fastapi
from cinetech.infrastructure.api.tmdb import tmdb_fastapi

app = FastAPI(
    title="Cinetech Agent API",
    description="Conversational movie recommendation API",
    docs_url="/docs",
)

# Include TMDb and ingestion routers
app.include_router(tmdb_fastapi.router, prefix="/tmdb", tags=["TMDb"])
app.include_router(ingest_fastapi.router, tags=["Ingestion"])


@app.get("/")
async def root():
    """
    Root endpoint for Cinetech API.
    Returns a welcome message and usage instructions.
    """
    return {"message": "Welcome to Cinetech API. Visit /docs for usage"}


class ChatRequest(BaseModel):
    """
    Pydantic model for chat request payload.
    """

    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User message to the chat")


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Conversational endpoint using ChatService to generate a reply from the model.
    The user context is automatically updated.

    Args:
        request (ChatRequest): Chat request payload with user ID and message.

    Returns:
        dict: Reply from the chat agent.
    """
    context = get_context(request.user_id)
    chat_service = ChatService(context)
    reply = chat_service.generate_reply(request.message)
    return {"reply": reply}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
