import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import uvicorn
import asyncio

load_dotenv()

from orchestrator.agent import orchestrator

app = FastAPI(
    title="Productivity Agent API",
    description="Multi-agent AI system for tasks, schedules and notes",
    version="1.0.0"
)

session_service = InMemorySessionService()
runner = Runner(
    agent=orchestrator,
    app_name="productivity_agent",
    session_service=session_service
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
def root():
    return {
        "name": "Productivity Agent",
        "status": "running",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

from orchestrator.agent import orchestrator

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        final_response = await orchestrator.run(request.message, request.session_id)
        return ChatResponse(response=final_response, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session = await session_service.get_session(
            app_name="productivity_agent",
            user_id="user",
            session_id=request.session_id
        )
        if not session:
            session = await session_service.create_session(
                app_name="productivity_agent",
                user_id="user",
                session_id=request.session_id
            )

        content = Content(
            role="user",
            parts=[Part(text=request.message)]
        )

        final_response = ""
        async for event in runner.run_async(
            user_id="user",
            session_id=request.session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text

        return ChatResponse(
            response=final_response,
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")