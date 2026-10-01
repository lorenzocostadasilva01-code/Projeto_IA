const BACKEND_URL = 'https://meanwhile-nuts-indie-handy.trycloudflare.com ' //modificar esse link quando criar um novo worker no cloudflare, esse link é do meu worker, então não vai funcionar para você.

function jsonResponse(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
    },
  })
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url)

    if (url.pathname !== '/api/chat') {
      return env.ASSETS.fetch(request)
    }

    if (request.method !== 'POST') {
      return jsonResponse({ detail: 'Use POST para enviar uma mensagem.' }, 405)
    }

    if (!env.BACKEND_API_TOKEN) {
      return jsonResponse({ detail: 'Configure BACKEND_API_TOKEN nos secrets do Worker.' }, 503)
    }

    let backendUrl
    try {
      backendUrl = new URL('/api/chat', BACKEND_URL)
      if (!['http:', 'https:'].includes(backendUrl.protocol)) throw new Error('Protocolo inválido')
    } catch {
      return jsonResponse({ detail: 'BACKEND_URL precisa ser uma URL HTTP ou HTTPS válida.' }, 500)
    }

    try {
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': request.headers.get('Content-Type') || 'application/json',
          Authorization: `Bearer ${env.BACKEND_API_TOKEN}`,
        },
        body: request.body,
        redirect: 'manual',
      })
      const headers = new Headers(response.headers)
      headers.set('Cache-Control', 'no-store')
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers,
      })
    } catch {
      return jsonResponse({ detail: 'Não foi possível conectar ao backend pelo túnel.' }, 502)
    }
  },
}