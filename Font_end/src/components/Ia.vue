<script setup>
import { nextTick, ref, watch } from 'vue'

const mensagem = ref('')
const historico = ref([])
const carregando = ref(false)
const chatMessages = ref(null)
const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').trim()

function scrollParaFim() {
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
}

watch(historico, () => {
  scrollParaFim()
}, { deep: true })

function formatarErro(error) {
  if (error instanceof Error) {
    if (error.message.includes('Failed to fetch')) {
      return 'Não foi possível conectar com o backend. Verifique se a API está rodando em http://localhost:8000.'
    }

    return error.message
  }

  return 'Ocorreu um erro ao se comunicar com a IA.'
}

async function enviarMensagem() {
  const textoUsuario = mensagem.value.trim()

  if (!textoUsuario || carregando.value) return

  historico.value.push({ autor: 'Você', texto: textoUsuario })
  mensagem.value = ''
  carregando.value = true

  try {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: textoUsuario })
    })

    let data = null

    try {
      data = await res.json()
    } catch {
      data = null
    }

    if (!res.ok || (data && data.error)) {
      throw new Error(data?.error || 'O backend respondeu com erro.')
    }

    historico.value.push({
      autor: 'IA',
      texto: data?.response || 'A IA não retornou uma resposta válida.'
    })
  } catch (err) {
    historico.value.push({
      autor: 'Erro',
      texto: formatarErro(err)
    })
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <div class="chat-shell">
    <div class="chat-header">
      <div class="header-title">
        <span class="badge">IA</span>
        <h1>Chat IA</h1>
      </div>
      <button class="clear-button" @click="historico = []" :disabled="historico.length === 0">
        Limpar
      </button>
    </div>

    <div class="quick-prompts">
      <button @click="mensagem = 'Explique IA de forma simples'">Resumo</button>
      <button @click="mensagem = 'Crie um roteiro rápido para apresentação'">Roteiro</button>
      <button @click="mensagem = 'Quero ideias de produtividade para hoje'">Produtividade</button>
    </div>

    <div ref="chatMessages" class="chat-messages" aria-live="polite">
      <div v-if="historico.length === 0" class="empty-state">
        <span class="emoji">✦</span>
        <span>Comece a conversa com a IA.</span>
      </div>

      <div
        v-for="(msg, i) in historico"
        :key="i"
        class="message-row"
        :class="msg.autor.toLowerCase()"
      >
        <div v-if="msg.autor === 'IA'" class="avatar">AI</div>
        <div class="message-bubble">
          <strong>{{ msg.autor }}:</strong>
          <span>{{ msg.texto }}</span>
        </div>
      </div>

      <div v-if="carregando" class="message-row ia typing-row">
        <div class="avatar">AI</div>
        <div class="message-bubble typing-bubble">
          <strong>IA:</strong>
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input">
      <input
        v-model="mensagem"
        @keyup.enter="enviarMensagem"
        placeholder="Digite sua mensagem..."
        :disabled="carregando"
      />
      <button @click="enviarMensagem" :disabled="carregando">
        {{ carregando ? 'Pensando...' : 'Enviar' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
:global(body) {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top, rgba(59, 130, 246, 0.22), transparent 30%),
    linear-gradient(135deg, #020817 0%, #0f172a 45%, #111827 100%);
  font-family: Inter, 'Segoe UI', sans-serif;
}

.chat-shell {
  width: min(820px, calc(100% - 2rem));
  margin: 2rem auto;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(16px);
  color: #e2e8f0;
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.15);
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.5);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 40%, #3b82f6 100%);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2rem;
  height: 2rem;
  padding: 0 0.5rem;
  border-radius: 999px;
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  background: rgba(255, 255, 255, 0.18);
  color: #eff6ff;
  font-weight: 700;
}

.chat-header h1 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
}

.clear-button {
  border: 1px solid rgba(255, 255, 255, 0.17);
  background: rgba(255, 255, 255, 0.08);
  color: #f8fafc;
  border-radius: 12px;
  padding: 0.6rem 0.9rem;
  cursor: pointer;
  transition: 0.2s ease;
}

.clear-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.clear-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.quick-prompts {
  display: flex;
  gap: 0.65rem;
  flex-wrap: wrap;
  padding: 0.9rem 1rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.7);
}

.quick-prompts button {
  border: 1px solid rgba(96, 165, 250, 0.28);
  background: rgba(37, 99, 235, 0.08);
  color: #dbeafe;
  border-radius: 999px;
  padding: 0.5rem 0.8rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.quick-prompts button:hover {
  transform: translateY(-1px);
  background: rgba(59, 130, 246, 0.18);
}

.chat-messages {
  min-height: 340px;
  max-height: 58vh;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.7), rgba(15, 23, 42, 1)),
    rgba(17, 24, 39, 0.9);
  scroll-behavior: smooth;
}

.empty-state {
  display: grid;
  place-items: center;
  text-align: center;
  color: #94a3b8;
  min-height: 260px;
  gap: 0.5rem;
}

.emoji {
  font-size: 2.1rem;
  color: #60a5fa;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
  width: 100%;
  animation: fadeIn 0.25s ease;
}

.message-row.you {
  justify-content: flex-end;
}

.message-row.ia,
.message-row.erro {
  justify-content: flex-start;
}

.avatar {
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #60a5fa, #2563eb);
  border: 1px solid rgba(191, 219, 254, 0.35);
  display: grid;
  place-items: center;
  font-size: 0.68rem;
  font-weight: 800;
  color: white;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.35);
}

.message-row.you .avatar {
  display: none;
}

.message-bubble {
  max-width: 84%;
  padding: 0.8rem 1rem;
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  line-height: 1.55;
  white-space: pre-wrap;
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.18);
}

.message-row.you .message-bubble {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #eff6ff;
  border-bottom-right-radius: 6px;
}

.message-row.ia .message-bubble {
  background: rgba(31, 41, 55, 0.9);
  color: #e5e7eb;
  border-bottom-left-radius: 6px;
}

.message-row.erro .message-bubble {
  background: rgba(127, 29, 29, 0.88);
  color: #fee2e2;
  border-bottom-left-radius: 6px;
}

.message-bubble strong {
  font-size: 0.78rem;
  opacity: 0.9;
}

.chat-input {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.9);
  border-top: 1px solid rgba(148, 163, 184, 0.12);
}

.chat-input input {
  flex: 1;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.7);
  color: #f8fafc;
  padding: 0.9rem 1rem;
  font-size: 1rem;
  transition: border 0.2s ease, box-shadow 0.2s ease;
}

.chat-input input:focus {
  outline: none;
  border-color: rgba(96, 165, 250, 0.7);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.15);
}

.chat-input button {
  border: none;
  border-radius: 14px;
  padding: 0.9rem 1.35rem;
  background: linear-gradient(135deg, #60a5fa, #2563eb);
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.3);
}

.chat-input button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 16px 28px rgba(37, 99, 235, 0.38);
}

.chat-input button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.typing-row {
  opacity: 0.9;
}

.typing-bubble {
  min-width: 118px;
}

.typing-dots {
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
  min-height: 1.1rem;
  padding-top: 0.15rem;
}

.typing-dots span {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: rgba(191, 219, 254, 0.95);
  animation: bounce 1.2s infinite ease-in-out;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.7);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 640px) {
  .chat-shell {
    width: min(100%, calc(100% - 1rem));
    margin: 1rem auto;
    border-radius: 18px;
  }

  .chat-header {
    padding: 0.9rem 1rem;
  }

  .chat-input {
    flex-direction: column;
  }

  .chat-input button {
    width: 100%;
  }

  .message-bubble {
    max-width: 90%;
  }
}
</style>