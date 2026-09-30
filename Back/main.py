import os
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))

app = FastAPI(title="Nexo API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=100_000)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, content: str) -> str:
        if not content.strip():
            raise ValueError("A mensagem não pode estar vazia.")
        return content


class ChatRequest(BaseModel):
    model: str = Field(default=DEFAULT_MODEL, min_length=1, max_length=100)
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "model": DEFAULT_MODEL}


@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict[str, str]:
    ollama_request = {
        "model": request.model,
        "messages": [message.model_dump() for message in request.messages],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=ollama_request)
            response.raise_for_status()
    except httpx.ConnectError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Não foi possível conectar à Ollama em {OLLAMA_BASE_URL}.",
        ) from error
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=504,
            detail="A Ollama demorou muito para responder. Tente novamente.",
        ) from error
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail=f"A Ollama respondeu com erro HTTP {error.response.status_code}.",
        ) from error

    try:
        ollama_data = response.json()
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail="A Ollama retornou uma resposta JSON inválida.",
        ) from error

    ollama_message = ollama_data.get("message") if isinstance(ollama_data, dict) else None
    reply = ollama_message.get("content") if isinstance(ollama_message, dict) else None
    if not isinstance(reply, str) or not reply.strip():
        raise HTTPException(
            status_code=502,
            detail="A resposta da Ollama não contém texto.",
        )

    return {"reply": reply, "model": request.model}