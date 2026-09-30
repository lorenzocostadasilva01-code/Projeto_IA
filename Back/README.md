# Nexo API

API em Python que recebe mensagens do front e as encaminha para a Ollama local. Para o site publicado na Cloudflare acessar esta API na sua máquina, exponha a porta local com Cloudflare Tunnel.

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

## Conectar o site publicado

O Worker do site não consegue acessar `localhost` da sua máquina. Exponha o backend com [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/):

1. Gere um token privado no PowerShell: `$token = python -c "import secrets; print(secrets.token_urlsafe(32))"`.
2. Inicie o backend definindo o mesmo token: `$env:CHAT_API_TOKEN = "<token gerado>"` e execute o comando Uvicorn acima.
3. Em outro terminal, crie um túnel para `http://127.0.0.1:8000` com `cloudflared tunnel --url http://127.0.0.1:8000`. Para uso contínuo, configure um túnel nomeado com hostname próprio. Mantenha o túnel ativo.
4. Na pasta `Front`, cadastre o mesmo token como secret do Worker:

  ```powershell
  npx wrangler secret put BACKEND_API_TOKEN
  ```

  O endereço atual do túnel está configurado em `Front/worker.js`. Cole o token gerado em `BACKEND_API_TOKEN` quando o Wrangler solicitar.
5. Gere os arquivos do front e publique o Worker: `npm run build` e `npx wrangler deploy`.

O navegador continua chamando `/api/chat` no próprio domínio do site. O Worker encaminha a chamada pelo túnel e injeta o token secreto; o token não vai para o navegador. A rota pública do chat ainda pode ser chamada por visitantes do site. Configure rate limiting no Cloudflare ou proteja o site com Cloudflare Access se o chat for privado.

## Configuração

Por padrão, a API usa `http://localhost:11434` e o modelo `llama3.2`. Para alterar, defina antes de iniciar o Uvicorn:

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_DEFAULT_MODEL = "llama3.2"
$env:OLLAMA_TIMEOUT_SECONDS = "180"
```

`CHAT_API_TOKEN` é opcional para desenvolvimento local. Defina-o antes de iniciar o backend quando usar um túnel; o Vite encaminha automaticamente o mesmo token se ele também estiver definido no terminal onde `npm run dev` é executado.

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