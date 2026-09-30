<script setup>
import { nextTick, ref, watch } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || '/api/chat'
const model = import.meta.env.VITE_CHAT_MODEL || 'llama3.2'
const messages = ref([])
const draft = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const conversation = ref(null)
const messageList = ref(null)

const suggestions = [
  { icon: '✳', title: 'Destrave uma ideia', prompt: 'Me ajude a transformar uma ideia vaga em um plano claro.' },
  { icon: '⌘', title: 'Entenda sem complicação', prompt: 'Explique inteligência artificial de um jeito simples e com exemplos.' },
  { icon: '↗', title: 'Escreva com mais clareza', prompt: 'Me ajude a escrever uma mensagem profissional, mas natural.' },
]

watch(messages, async () => {
  await nextTick()
  if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight
}, { deep: true })

function startNewChat() {
  messages.value = []
  conversation.value = null
  draft.value = ''
  errorMessage.value = ''
}

async function sendMessage(text = draft.value, retry = false) {
  const content = text.trim()
  if (!content || isLoading.value) return

  errorMessage.value = ''
  draft.value = ''
  if (!retry) messages.value.push({ role: 'user', content })
  isLoading.value = true
  conversation.value ||= `Conversa ${new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' }).format(new Date())}`

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        messages: messages.value.map(({ role, content: messageContent }) => ({ role, content: messageContent })),
      }),
    })

    if (!response.ok) {
      let detail = ''
      try {
        detail = (await response.json()).detail || ''
      } catch {
        // Keep the HTTP status as a useful fallback when the response is not JSON.
      }
      throw new Error(detail || `O servidor respondeu com erro ${response.status}.`)
    }

    const data = await response.json()
    const reply = data.reply ?? data.message?.content ?? data.response
    if (typeof reply !== 'string' || !reply.trim()) {
      throw new Error('A resposta da API não contém texto. Verifique o formato retornado pelo backend.')
    }
    messages.value.push({ role: 'assistant', content: reply })
  } catch (error) {
    errorMessage.value = error instanceof TypeError
      ? `Não foi possível conectar à API em ${apiUrl}. Confirme se o backend está ativo.`
      : error.message || 'Não foi possível enviar sua mensagem.'
  } finally {
    isLoading.value = false
  }
}

function onComposerKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <main class="app-shell">
    <aside class="sidebar">
      <a class="brand" href="#" aria-label="Nexo, início" @click.prevent="startNewChat">
        <span class="brand-mark"><span></span><span></span><span></span></span>
        <span class="brand-name">nexo<span>.</span></span>
      </a>

      <button class="new-chat-button" type="button" @click="startNewChat">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>
        <span>Nova conversa</span>
        <kbd>⌘ K</kbd>
      </button>

      <div class="sidebar-label">ESPAÇO DE TRABALHO</div>
      <nav class="sidebar-nav" aria-label="Navegação principal">
        <button class="nav-item active" type="button" @click="startNewChat">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H5l1.4-3.1A7.5 7.5 0 1 1 20 11.5Z" /></svg>
          <span>Conversas</span>
        </button>
        <div v-if="conversation" class="history-item" :title="conversation">
          <span class="history-dot"></span>{{ conversation }}
        </div>
      </nav>

      <div class="sidebar-bottom">
        <div class="local-card">
          <span class="local-indicator"></span>
          <div><strong>Seu espaço, suas ideias</strong><span>Conexão via API local</span></div>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 18l6-6-6-6" /></svg>
        </div>
        <div class="profile-row">
          <div class="avatar">N</div>
          <div class="profile-copy"><strong>Seu workspace</strong><span>Plano pessoal</span></div>
          <button class="icon-button profile-menu" type="button" aria-label="Opções do perfil">···</button>
        </div>
      </div>
    </aside>

    <section class="main-panel">
      <header class="topbar">
        <div class="breadcrumb"><span>Conversas</span><span class="breadcrumb-slash">/</span><strong>{{ conversation || 'Nova conversa' }}</strong></div>
        <div class="topbar-right">
          <span class="model-chip"><span class="model-dot"></span>{{ model }}</span>
          <button class="icon-button more-button" type="button" aria-label="Mais opções">···</button>
        </div>
      </header>

      <section v-if="messages.length === 0" class="welcome-view">
        <div class="welcome-content">
          <div class="welcome-kicker"><span class="kicker-line"></span> UM BOM COMEÇO MUDA TUDO</div>
          <h1>O que vamos<br /><span>descobrir hoje?</span></h1>
          <p>Ideias, perguntas ou aquele projeto que está esperando para sair do papel. Vamos nessa.</p>

          <div class="suggestion-grid">
            <button v-for="suggestion in suggestions" :key="suggestion.title" class="suggestion-card" type="button" @click="sendMessage(suggestion.prompt)">
              <span class="suggestion-icon">{{ suggestion.icon }}</span>
              <span class="suggestion-title">{{ suggestion.title }}</span>
              <span class="suggestion-prompt">{{ suggestion.prompt }}</span>
              <span class="suggestion-arrow">↗</span>
            </button>
          </div>
        </div>
        <div class="welcome-index"><span>01</span><span class="index-rule"></span><span>03</span></div>
      </section>

      <section v-else ref="messageList" class="message-list" aria-live="polite" aria-label="Mensagens da conversa">
        <div v-for="(message, index) in messages" :key="index" class="message-row" :class="`message-${message.role}`">
          <div v-if="message.role === 'assistant'" class="assistant-avatar"><span class="brand-mark small"><span></span><span></span><span></span></span></div>
          <div class="message-content">
            <div class="message-author">{{ message.role === 'user' ? 'Você' : 'Nexo' }}</div>
            <p>{{ message.content }}</p>
          </div>
          <div v-if="message.role === 'user'" class="user-avatar">N</div>
        </div>
        <div v-if="isLoading" class="message-row message-assistant">
          <div class="assistant-avatar"><span class="brand-mark small"><span></span><span></span><span></span></span></div>
          <div class="message-content"><div class="message-author">Nexo</div><div class="typing-indicator" aria-label="Nexo está pensando"><i></i><i></i><i></i></div></div>
        </div>
        <div v-if="errorMessage" class="api-error" role="alert">
          <span>!</span><p>{{ errorMessage }}</p>
          <button type="button" @click="sendMessage(messages.at(-1)?.content, true)">Tentar novamente</button>
        </div>
      </section>

      <footer class="composer-area">
        <form class="composer" @submit.prevent="sendMessage()">
          <textarea v-model="draft" rows="1" :disabled="isLoading" placeholder="Escreva sua mensagem..." aria-label="Escreva sua mensagem" @keydown="onComposerKeydown"></textarea>
          <div class="composer-footer">
            <div class="composer-hint"><span class="hint-spark">✳</span><span>Respostas geradas por IA podem conter imprecisões.</span></div>
            <div class="composer-actions">
              <span class="key-hint">↵ <span>para enviar</span></span>
              <button class="send-button" type="submit" :disabled="!draft.trim() || isLoading" aria-label="Enviar mensagem" title="Enviar mensagem">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
              </button>
            </div>
          </div>
        </form>
        <div class="footer-note"><span class="footer-lock">◈</span> Seu assistente, rodando no seu ritmo <span class="footer-separator">·</span> <strong>{{ model }}</strong></div>
      </footer>
    </section>
  </main>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  font-family: 'DM Sans', sans-serif;
  color: #e9e8e2;
  background: #171917;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-optical-sizing: auto;
  font-weight: 400;
  --muted: #858880;
  --lime: #c5f36a;
}

* { box-sizing: border-box; }
body { margin: 0; min-width: 320px; min-height: 100vh; }
button, textarea { font: inherit; }
button { color: inherit; }
button:focus-visible, textarea:focus-visible { outline: 2px solid var(--lime); outline-offset: 3px; }

.app-shell { display: flex; min-height: 100vh; background: #171917; }
.sidebar { width: 256px; flex: 0 0 256px; display: flex; flex-direction: column; padding: 29px 17px 16px; background: #1c1f1c; border-right: 1px solid #2b2e2a; }
.brand { display: flex; align-items: center; gap: 11px; width: fit-content; margin: 0 0 43px 8px; color: #f3f3ec; text-decoration: none; }
.brand-name { font: 800 23px/1 'Manrope', sans-serif; letter-spacing: 0; }
.brand-name > span { color: var(--lime); }
.brand-mark { display: flex; align-items: center; justify-content: center; gap: 2px; width: 25px; height: 25px; }
.brand-mark span { width: 4px; border-radius: 4px; background: var(--lime); transform: skew(-18deg); }
.brand-mark span:nth-child(1) { height: 10px; opacity: .7; }
.brand-mark span:nth-child(2) { height: 18px; }
.brand-mark span:nth-child(3) { height: 13px; opacity: .82; }
.new-chat-button { height: 43px; display: flex; align-items: center; gap: 10px; padding: 0 10px; border: 1px solid #393d36; border-radius: 6px; background: #242723; color: #e8e9e1; font-size: 12px; text-align: left; cursor: pointer; transition: border-color .2s, background .2s; }
.new-chat-button:hover { border-color: #626a56; background: #292d27; }
.new-chat-button svg, .nav-item svg { width: 16px; height: 16px; flex: none; fill: none; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.new-chat-button kbd { margin-left: auto; color: #75796f; font: 10px 'DM Mono', monospace; }
.sidebar-label { margin: 34px 9px 12px; color: #74786e; font: 10px 'DM Mono', monospace; letter-spacing: 0; }
.sidebar-nav { display: grid; gap: 4px; }
.nav-item { height: 37px; display: flex; align-items: center; gap: 11px; padding: 0 10px; border: 0; border-radius: 5px; background: transparent; color: #bcbeb5; font-size: 12px; text-align: left; cursor: pointer; }
.nav-item.active { background: #292d27; color: #ecede6; }
.nav-item.active svg { color: var(--lime); }
.history-item { overflow: hidden; margin: 4px 0 0 10px; padding: 9px 8px; color: #858980; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.history-dot { display: inline-block; width: 5px; height: 5px; margin: 0 9px 1px 0; border-radius: 50%; background: #74786e; }
.sidebar-bottom { margin-top: auto; }
.local-card { min-height: 57px; display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px solid #343832; border-radius: 5px; background: #222521; }
.local-indicator, .model-dot { width: 7px; height: 7px; flex: none; border-radius: 50%; background: var(--lime); box-shadow: 0 0 10px #c5f36662; }
.local-card div, .profile-copy { display: grid; gap: 4px; min-width: 0; }
.local-card strong, .profile-copy strong { color: #dfe1d8; font-size: 10px; font-weight: 600; }
.local-card div span, .profile-copy span { color: #83877d; font-size: 10px; }
.local-card > svg { width: 14px; height: 14px; margin-left: auto; fill: none; stroke: #80847a; stroke-width: 1.7; }
.profile-row { display: flex; align-items: center; gap: 9px; margin-top: 18px; padding: 0 3px; }
.avatar, .user-avatar { display: grid; place-items: center; width: 28px; height: 28px; flex: none; border-radius: 50%; background: #363b31; color: var(--lime); font: 600 11px 'DM Mono', monospace; }
.profile-copy { gap: 3px; }
.profile-copy strong { font-size: 11px; }
.profile-copy span { font-size: 10px; }
.icon-button { display: grid; place-items: center; width: 30px; height: 30px; border: 0; border-radius: 5px; background: transparent; color: #92968c; font-size: 19px; letter-spacing: 1px; cursor: pointer; }
.icon-button:hover { background: #2a2d28; color: #e9e8e2; }
.profile-menu { margin-left: auto; }

.main-panel { position: relative; display: flex; flex: 1; flex-direction: column; min-width: 0; min-height: 100vh; background: radial-gradient(ellipse at 50% 42%, #22251f 0, #1b1e1a 42%, #171917 78%); }
.topbar { height: 68px; display: flex; align-items: center; justify-content: space-between; padding: 0 42px; border-bottom: 1px solid #2b2e29; }
.breadcrumb { display: flex; align-items: center; gap: 10px; color: #83877e; font-size: 11px; }
.breadcrumb-slash { color: #53574f; }
.breadcrumb strong { color: #c5c7be; font-weight: 500; }
.topbar-right { display: flex; align-items: center; gap: 17px; }
.model-chip { display: inline-flex; align-items: center; gap: 8px; height: 27px; padding: 0 10px; border: 1px solid #383c34; border-radius: 4px; color: #b9bdb2; font: 10px 'DM Mono', monospace; }
.model-dot { width: 6px; height: 6px; }
.more-button { font-weight: 700; }

.welcome-view { position: relative; display: grid; flex: 1; place-items: center; min-height: 450px; overflow: hidden; }
.welcome-view::before { position: absolute; top: 14%; left: 50%; width: 490px; height: 490px; border: 1px solid #ffffff05; border-radius: 50%; content: ''; transform: translateX(-50%); }
.welcome-view::after { position: absolute; top: 19%; left: 50%; width: 390px; height: 390px; border: 1px solid #ffffff04; border-radius: 50%; content: ''; transform: translateX(-50%); }
.welcome-content { position: relative; z-index: 1; width: min(672px, calc(100% - 48px)); padding: 34px 0 25px; animation: arrive .65s ease both; }
.welcome-kicker { display: flex; align-items: center; gap: 10px; color: #a6aa9c; font: 10px 'DM Mono', monospace; }
.kicker-line { width: 20px; height: 1px; background: var(--lime); }
.welcome-content h1 { margin: 22px 0 14px; color: #f0f0e9; font: 500 54px/.99 'Manrope', sans-serif; letter-spacing: 0; }
.welcome-content h1 span { color: var(--lime); }
.welcome-content > p { max-width: 440px; margin: 0; color: #9a9d92; font-size: 13px; line-height: 1.75; }
.suggestion-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 11px; margin-top: 37px; }
.suggestion-card { position: relative; min-height: 139px; display: flex; flex-direction: column; align-items: flex-start; padding: 15px 14px; border: 1px solid #383b34; border-radius: 5px; background: #222520ad; text-align: left; cursor: pointer; transition: transform .2s, border-color .2s, background .2s; }
.suggestion-card:hover { transform: translateY(-3px); border-color: #727c5d; background: #292d25; }
.suggestion-icon { display: grid; place-items: center; width: 23px; height: 23px; margin-bottom: 15px; border: 1px solid #42483a; border-radius: 4px; color: var(--lime); font-size: 13px; }
.suggestion-title { color: #e1e3da; font-size: 11px; font-weight: 600; }
.suggestion-prompt { max-width: 180px; margin-top: 6px; color: #898d82; font-size: 10px; line-height: 1.5; }
.suggestion-arrow { position: absolute; top: 15px; right: 13px; color: #767b70; font-size: 12px; }
.welcome-index { position: absolute; right: 42px; bottom: 34px; display: flex; align-items: center; gap: 9px; color: #696d64; font: 9px 'DM Mono', monospace; }
.welcome-index span:first-child { color: var(--lime); }
.index-rule { width: 30px; height: 1px; background: #474b42; }

.message-list { width: min(760px, calc(100% - 48px)); flex: 1; align-self: center; overflow-y: auto; padding: 48px 0 28px; scrollbar-color: #42463d transparent; scrollbar-width: thin; }
.message-row { display: flex; align-items: flex-start; gap: 13px; margin: 0 0 29px; animation: arrive .25s ease both; }
.message-user { justify-content: flex-end; }
.message-content { max-width: min(620px, 82%); }
.message-author { margin: 3px 0 8px; color: #a9aca2; font-size: 11px; font-weight: 600; }
.message-content p { margin: 0; color: #e2e3dc; font-size: 13px; line-height: 1.75; white-space: pre-wrap; overflow-wrap: anywhere; }
.message-user .message-content { padding: 13px 16px; border: 1px solid #3d4238; border-radius: 6px 2px 6px 6px; background: #252923; }
.message-user .message-author { margin-top: 0; }
.assistant-avatar { display: grid; place-items: center; width: 27px; height: 27px; flex: none; margin-top: 1px; border: 1px solid #444a3b; border-radius: 5px; background: #282d24; }
.brand-mark.small { gap: 1px; width: 16px; height: 16px; }
.brand-mark.small span { width: 2px; }
.brand-mark.small span:nth-child(1) { height: 6px; }
.brand-mark.small span:nth-child(2) { height: 11px; }
.brand-mark.small span:nth-child(3) { height: 8px; }
.user-avatar { width: 27px; height: 27px; margin-top: 14px; }
.typing-indicator { display: flex; align-items: center; gap: 4px; height: 17px; }
.typing-indicator i { width: 5px; height: 5px; border-radius: 50%; background: var(--lime); animation: pulse 1s infinite ease-in-out; }
.typing-indicator i:nth-child(2) { animation-delay: .15s; }
.typing-indicator i:nth-child(3) { animation-delay: .3s; }
.api-error { display: flex; align-items: center; gap: 11px; margin: 0 0 20px 40px; padding: 12px 14px; border: 1px solid #765647; border-radius: 5px; background: #392a24; color: #e8c5b2; }
.api-error > span { display: grid; place-items: center; width: 17px; height: 17px; flex: none; border: 1px solid #b77d63; border-radius: 50%; font: 11px 'DM Mono', monospace; }
.api-error p { flex: 1; margin: 0; font-size: 11px; line-height: 1.5; }
.api-error button { flex: none; border: 0; background: transparent; color: #f0c3a8; font-size: 11px; text-decoration: underline; cursor: pointer; }

.composer-area { width: min(760px, calc(100% - 48px)); align-self: center; padding: 14px 0 22px; }
.composer { padding: 14px 14px 10px 17px; border: 1px solid #42463e; border-radius: 7px; background: #232621; box-shadow: 0 9px 35px #00000020; transition: border-color .2s; }
.composer:focus-within { border-color: #697458; }
.composer textarea { display: block; width: 100%; min-height: 29px; max-height: 130px; resize: vertical; border: 0; outline: 0; background: transparent; color: #eeefe8; font-size: 13px; line-height: 1.55; }
.composer textarea::placeholder { color: #777c71; }
.composer textarea:disabled { opacity: .65; }
.composer-footer { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 8px; }
.composer-hint { display: flex; align-items: center; gap: 7px; color: #777b71; font-size: 9px; }
.hint-spark { color: var(--lime); font-size: 11px; }
.composer-actions { display: flex; align-items: center; gap: 12px; }
.key-hint { color: #8b8f85; font: 10px 'DM Mono', monospace; }
.key-hint span { font: 9px 'DM Sans', sans-serif; }
.send-button { display: grid; place-items: center; width: 31px; height: 31px; border: 0; border-radius: 4px; background: var(--lime); color: #20241a; cursor: pointer; transition: transform .18s, background .18s; }
.send-button:hover:not(:disabled) { transform: translateX(2px); background: #d6ff83; }
.send-button:disabled { background: #41463a; color: #858a7c; cursor: not-allowed; }
.send-button svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.footer-note { display: flex; align-items: center; justify-content: center; gap: 7px; margin-top: 13px; color: #73776e; font-size: 9px; }
.footer-lock { color: #a5aa99; }
.footer-separator { color: #50544c; }
.footer-note strong { color: #979b90; font: 9px 'DM Mono', monospace; }

@keyframes arrive { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulse { 0%, 60%, 100% { opacity: .38; transform: translateY(0); } 30% { opacity: 1; transform: translateY(-3px); } }

@media (max-width: 760px), (max-height: 500px) and (max-width: 900px) {
  .app-shell { min-height: 100vh; height: 100vh; min-height: 100dvh; height: 100dvh; flex-direction: column; }
  .sidebar { width: 100%; height: 56px; flex: 0 0 56px; flex-direction: row; justify-content: space-between; align-items: center; padding: 0 14px; border-right: 0; border-bottom: 1px solid #2b2e2a; }
  .brand { margin: 0; gap: 8px; }
  .brand-name { display: block; font-size: 20px; }
  .new-chat-button { width: auto; height: 40px; justify-content: center; gap: 8px; padding: 0 11px; }
  .new-chat-button span { display: inline; }
  .new-chat-button kbd, .sidebar-label, .sidebar-nav, .sidebar-bottom { display: none; }
  .main-panel { height: calc(100vh - 56px); height: calc(100dvh - 56px); min-height: 0; }
  .topbar { height: 58px; flex: none; padding: 0 19px; }
  .welcome-view { min-height: 0; overflow-y: auto; }
  .message-list { min-height: 0; }
  .topbar-right { gap: 8px; }
  .welcome-content { width: min(600px, calc(100% - 40px)); }
  .welcome-content h1 { font-size: clamp(42px, 8vw, 54px); }
  .suggestion-grid { gap: 8px; }
  .suggestion-card { min-height: 142px; padding: 12px 10px; }
  .suggestion-title { font-size: 10px; }
  .suggestion-prompt { font-size: 9px; }
  .welcome-index { right: 20px; bottom: 22px; }
  .message-list, .composer-area { width: calc(100% - 34px); }
  .composer-area { flex: none; }
}

@media (max-width: 500px) {
  .breadcrumb { gap: 7px; font-size: 10px; }
  .model-chip { gap: 6px; padding: 0 7px; font-size: 9px; }
  .welcome-view { min-height: 0; align-items: start; overflow-y: auto; }
  .welcome-content { padding: 25px 0; }
  .welcome-content h1 { margin-top: 19px; font-size: 43px; }
  .welcome-content > p { max-width: 340px; font-size: 12px; }
  .suggestion-grid { grid-template-columns: 1fr; gap: 7px; margin-top: 24px; }
  .suggestion-card { min-height: 67px; display: grid; grid-template-columns: 29px minmax(0, 1fr) 15px; grid-template-rows: minmax(15px, auto) minmax(15px, auto); column-gap: 9px; padding: 10px; }
  .suggestion-icon { grid-column: 1; grid-row: 1 / 3; margin: 0; }
  .suggestion-title { grid-column: 2; grid-row: 1; align-self: end; font-size: 10px; }
  .suggestion-prompt { grid-column: 2; grid-row: 2; max-width: 100%; margin-top: 2px; }
  .suggestion-arrow { grid-column: 3; grid-row: 1 / 3; top: 50%; right: 11px; align-self: center; transform: translateY(-50%); }
  .composer-area { width: calc(100% - 25px); flex: none; padding-bottom: max(12px, env(safe-area-inset-bottom)); }
  .composer { padding: 12px 10px 9px 12px; }
  .composer-hint { max-width: 190px; font-size: 8px; line-height: 1.35; }
  .composer-actions { gap: 7px; }
  .key-hint span { display: none; }
  .footer-note { font-size: 8px; }
  .message-list { width: calc(100% - 26px); min-height: 0; padding-top: 27px; }
  .message-content { max-width: 84%; }
  .message-content p { font-size: 12px; }
  .api-error { flex-wrap: wrap; margin-left: 0; }
  .api-error button { margin-left: 28px; }
}

@media (max-height: 700px) and (max-width: 760px) {
  .welcome-view { place-items: start center; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
}
</style>
