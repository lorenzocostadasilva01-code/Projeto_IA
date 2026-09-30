# Nexo API

API em Python que recebe mensagens do front e as encaminha para a Ollama local.

## Requisitos

- Python 3.10 ou superior
- Ollama em execução, com o modelo `llama3.2` baixado

## Executar no Windows

No terminal, a partir da pasta `Back`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Em outro terminal, inicie o front com `npm run dev` na pasta `Front`. O Vite encaminha `/api` para esta API. A documentação interativa fica em `http://localhost:8000/docs` e a verificação de saúde em `http://localhost:8000/health`.

## Configuração

Por padrão, a API usa `http://localhost:11434` e o modelo `llama3.2`. Para alterar, defina antes de iniciar o Uvicorn:

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_DEFAULT_MODEL = "llama3.2"
$env:OLLAMA_TIMEOUT_SECONDS = "180"
```

## Endpoint

`POST /api/chat` recebe o modelo e o histórico:

```json
{
  "model": "llama3.2",
  "messages": [
    { "role": "user", "content": "Olá!" }
  ]
}
```

A API envia esse conteúdo para `POST /api/chat` da Ollama com `stream: false` e responde ao front com `{ "reply": "...", "model": "llama3.2" }`. Erros de conexão, timeout e respostas inválidas da Ollama retornam códigos HTTP apropriados e uma mensagem em `detail`.