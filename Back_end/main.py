import os

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="IA API", version="1.0.0")

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:5173",
    "https://127.0.0.1:5173",
]

extra_origins = os.getenv("ALLOWED_ORIGINS", "")
if extra_origins:
    default_origins.extend([origin.strip() for origin in extra_origins.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=default_origins,
    allow_origin_regex=r"https://.*\.ngrok(?:-free)?\.(?:app|io)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Pergunta enviada para a IA")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "Backend da IA funcionando corretamente.",
    }


@app.post("/api/chat")
def chat(req: ChatRequest):
    prompt = req.prompt.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt obrigatório.")

    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

    try:
        response = requests.post(
            ollama_url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )

        if response.status_code >= 400:
            try:
                detail = response.json()
            except ValueError:
                detail = {"error": response.text}
            raise HTTPException(status_code=500, detail=detail)

        payload = response.json()
        text = payload.get("response")

        if not text:
            raise HTTPException(status_code=500, detail="A IA não retornou uma resposta válida.")

        return {"response": text}

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível conectar com o Ollama. Verifique se ele está rodando em localhost:11434.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(exc)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)