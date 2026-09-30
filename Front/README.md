# Nexo · Assistente IA

Interface de chat em Vue 3 preparada para enviar mensagens ao backend, que faz a comunicação com a Ollama. O navegador não chama a Ollama diretamente.

## Executar

```sh
npm install
npm run dev
```

Na configuração local, o Vite encaminha `/api` para o backend pelo Cloudflare Tunnel. No deploy, o Worker encaminha `/api/chat` ao mesmo túnel. Veja [Back/README.md](../Back/README.md) para configurar o token e publicar o Worker. Para usar outro endpoint diretamente, crie um arquivo `.env.local` nesta pasta:

```env
VITE_API_URL=http://localhost:3000/api/chat
VITE_CHAT_MODEL=llama3.2
```

`VITE_API_URL` é opcional e, sem configuração, usa `/api/chat`. Reinicie o Vite após alterar variáveis de ambiente. Para iniciar o backend e conferir o contrato, consulte [Back/README.md](../Back/README.md).

## Contrato HTTP

O front envia `POST` para `VITE_API_URL`, com `Content-Type: application/json`:

```json
{
  "model": "llama3.2",
  "messages": [
    { "role": "user", "content": "Olá!" }
  ]
}
```

O backend deve encaminhar `model` e `messages` para a Ollama e responder com JSON em um destes formatos:

```json
{ "reply": "Olá! Como posso ajudar?" }
```

Também são aceitos os formatos nativos `{ "message": { "content": "..." } }` e `{ "response": "..." }`. Respostas HTTP de erro são exibidas no chat com opção para tentar novamente.

## Build

```sh
npm run build
```

utilizar cloudflared tunnel --url http://127.0.0.1:8000 no cmd do pc para pegar o link temporario da api back end e colocar no worker.js