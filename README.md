# Perplexo API

> API REST autossuficiente que expõe o poder de busca do [Perplexity.ai](https://perplexity.ai) via endpoints HTTP simples.
> Permite que qualquer aplicação, agente de IA ou automação faça buscas profundas na web com citações verificáveis — **sem precisar de chave da API oficial**.

🌐 **URL pública:** `https://perplexo.0api.cloud`

---

## Como Funciona

A API usa um `session-token` de uma conta Perplexity Pro/Max para autenticar-se no serviço, simulando um navegador real via [curl_cffi](https://github.com/yifeikong/curl_cffi). Toda a comunicação é feita com fingerprint de browser (TLS, headers, JA3) para evitar bloqueios.

**Fluxo simplificado:**

```
Seu App → POST /search → Perplexo API → curl_cffi (Chrome fingerprint) → Perplexity.ai → Resposta com citações
```

**Duas formas de receber a resposta:**

| Endpoint | Comportamento | Ideal para |
|---|---|---|
| `POST /search` | Aguarda e retorna JSON completo | Pipelines, bots, agentes de IA |
| `POST /search_stream` | Retorna eventos SSE em tempo real | Chat UI, terminal, streaming ao vivo |

---

## Instalação

### Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/sonyddr666/perplexo-api.git
cd perplexo-api

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com seu token e chave API

# 3. Suba o container
docker compose up -d
```

### Docker Compose com VPN (para VPS)

Se estiver rodando em uma VPS, o IP de datacenter pode ser bloqueado pelo Cloudflare. Use a versão com VPN:

```bash
docker compose -f docker-compose.vpn.yml up -d
```

### Local (Desenvolvimento)

```bash
# 1. Clone e instale dependências
git clone https://github.com/sonyddr666/perplexo-api.git
cd perplexo-api
pip install -r requirements.txt

# 2. Configure o .env
cp .env.example .env

# 3. Execute
python src/perplexity_mcp.py
```

A API sobe na porta `3000` por padrão.

---

## Configuração

### Variáveis de Ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `PERPLEXITY_SESSION_TOKEN` | ✅ | — | Cookie `__Secure-next-auth.session-token` da sua conta Perplexity |
| `MCP_API_KEY` | ✅ (prod) | — | Chave para proteger todos os endpoints sensíveis |
| `MCP_PORT` | | `3000` | Porta da API |
| `TOKENS_DIR` | | `./data/tokens` | Diretório para persistência de tokens |
| `CONVERSATIONS_DIR` | | `./data/conversations` | Diretório para histórico de conversas |
| `MAX_ACTIVE_CONVERSATIONS` | | `100` | Máximo de conversas simultâneas em memória |
| `CONVERSATION_TTL_SECONDS` | | `3600` | Tempo de vida de conversas inativas (segundos) |
| `TOKEN_ROTATION_ENABLED` | | `true` | Rotação automática entre múltiplos tokens |

### Como obter o Session Token

1. Acesse [perplexity.ai](https://perplexity.ai) e faça login
2. Abra as DevTools do navegador (F12)
3. Vá em **Application** → **Cookies** → `https://www.perplexity.ai`
4. Copie o valor do cookie `__Secure-next-auth.session-token`
5. Cole na variável `PERPLEXITY_SESSION_TOKEN`

---

## Endpoints

### Mapa de Endpoints

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `POST` | `/search` | ✅ | Busca — retorna JSON completo |
| `POST` | `/search_stream` | ✅ | Busca — streaming SSE em tempo real |
| `POST` | `/vision` | ✅ | Análise de imagem (base64) |
| `GET` | `/models` | ✅ | Lista modelos e focus modes |
| `GET` | `/health` | ❌ | Health check (sem auth) |
| `GET` | `/diagnostics` | ✅ | Status de autenticação Perplexity |
| `GET` | `/tokens/status` | ✅ | Métricas do pool de tokens |
| `POST` | `/clear` | ✅ | Limpa histórico de um `user_id` |
| `GET` | `/conversation-status` | ✅ | Status das conversas ativas |
| `GET` | `/last_response` | ✅ | Última resposta gerada (`?user_id=`) |
| `GET` | `/history/list` | ✅ | Lista conversas salvas (`?user_id=`) |
| `POST` | `/history/load` | ✅ | Restaura conversa salva pelo ID |
| `POST` | `/history/delete` | ✅ | Deleta conversa salva |
| `GET` | `/credentials` | ✅ | UI web para gerenciar credenciais |

> **Auth = ✅** significa que o header `X-API-Key: sua-chave` é obrigatório.

---

## 🔍 Busca — `POST /search`

Realiza uma busca no Perplexity e retorna a resposta **completa** com citações. Use quando não precisar de streaming.

**Headers:**
```
Content-Type: application/json
X-API-Key: sua-chave-aqui
```

**Body:**
```json
{
  "query": "Quais as diferenças entre ARM e x86 para servidores?",
  "user_id": "meu-app",
  "model": "sonar",
  "focus": "web",
  "time_range": "all",
  "citation_mode": "markdown"
}
```

### Parâmetros do Body

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `query` | `string` | **obrigatório** | A pergunta ou consulta |
| `user_id` | `string` | `"default"` | ID do usuário — mantém contexto de conversa entre chamadas |
| `model` | `string` | `"best"` | Modelo de IA (ver tabela completa abaixo) |
| `focus` | `string` | `"web"` | Foco da busca: `web`, `academic`, `social`, `finance`, `writing`, `all` |
| `time_range` | `string` | `"all"` | Filtro temporal: `all`, `day`, `week`, `month`, `year` |
| `citation_mode` | `string` | `"markdown"` | Formato de citações: `default`, `markdown`, `clean` |

> **Dica sobre `user_id`:** Cada `user_id` único mantém uma conversa independente. Você pode enviar múltiplas mensagens sequenciais com o mesmo `user_id` e a API se lembrará do contexto (como um chat). Use `POST /clear` para resetar.

### Resposta (200)

```json
{
  "status": "success",
  "answer": "## Diferenças Fundamentais\n\nA arquitetura ARM usa o design RISC...",
  "thinking": null,
  "citations": [
    {
      "title": "ARM vs x86: Server Architecture Comparison",
      "url": "https://example.com/article",
      "snippet": "Trecho relevante do artigo..."
    }
  ],
  "model_used": "sonar",
  "focus_mode": "web",
  "time_range": "all",
  "has_thinking": false,
  "conversation_info": {
    "id": "meu-app",
    "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "model": "sonar",
    "message_count": 1
  }
}
```

### Campos da Resposta

| Campo | Tipo | Descrição |
|---|---|---|
| `status` | `string` | `"success"` em caso de sucesso |
| `answer` | `string` | Resposta sintetizada pelo modelo |
| `thinking` | `string \| null` | Raciocínio interno do modelo — presente apenas em modelos `-thinking` |
| `citations` | `array` | Lista de fontes com `title`, `url` e `snippet` |
| `has_thinking` | `boolean` | `true` se o campo `thinking` foi preenchido |
| `model_used` | `string` | ID do modelo que processou a requisição |
| `focus_mode` | `string` | Focus utilizado |
| `time_range` | `string` | Filtro de data utilizado |
| `conversation_info.id` | `string` | O `user_id` da conversa |
| `conversation_info.message_count` | `number` | Quantas mensagens esta conversa já tem |

### Modos de Citação

| `citation_mode` | Formato no `answer` | Quando usar |
|---|---|---|
| `markdown` | `texto[1](https://url.com)` | Renderizar em Markdown/HTML |
| `default` | `texto[1]` | Processar citações manualmente |
| `clean` | `texto` | Exibir texto puro sem marcações |

---

## 📡 Busca Streaming — `POST /search_stream`

Retorna a resposta em tempo real via **Server-Sent Events (SSE)**. Ideal para interfaces de chat onde o usuário vê o texto aparecer progressivamente.

**Aceita os mesmos parâmetros do `/search`**, exceto `citation_mode`.

**Headers:**
```
Content-Type: application/json
X-API-Key: sua-chave-aqui
```

### Eventos SSE

A resposta é um stream `text/event-stream` onde cada linha tem o formato `data: {json}\n\n`.

| Evento | Quando chega | Payload exemplo |
|---|---|---|
| `status` | Início da busca | `{"status": "Iniciando busca..."}` |
| `thinking` | Modelos `-thinking` em raciocínio | `{"thinking": "Vou analisar os prós e contras..."}` |
| `citation` | Cada fonte encontrada | `{"citation": {"title": "Título", "url": "https://..."}}` |
| `chunk` | Cada pedaço da resposta | `{"chunk": "A arquitetura ARM..."}` |
| `file` | Canvas/código gerado pelo modelo | `{"file": {"filename": "app.py", "content": "...", "language": "python"}}` |
| `done` | Fim da resposta | `{"done": true, "answer": "...", "citations": [...], "conversation_id": "..."}` |
| `error` | Falha durante processamento | `{"error": "mensagem de erro"}` |

> **Importante:** O evento `done` contém a resposta **completa** no campo `answer` e todas as citações em `citations`. Use-o para persistir o resultado final.

### Exemplo JavaScript (fetch + ReadableStream)

```javascript
const API_URL = "https://perplexo.0api.cloud";
const API_KEY = "sua-chave";

async function searchStream(query, model = "sonar", onChunk, onDone) {
  const response = await fetch(`${API_URL}/search_stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({ query, model, user_id: "meu-chat" }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const lines = decoder.decode(value).split("\n");
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      try {
        const event = JSON.parse(line.slice(6));

        if (event.chunk) onChunk(event.chunk);         // Texto chegando
        if (event.thinking) console.log("🧠", event.thinking); // Raciocínio
        if (event.citation) console.log("📎", event.citation); // Nova fonte
        if (event.done) onDone(event);                 // Resposta completa
        if (event.error) throw new Error(event.error); // Erro
      } catch (e) { /* linha incompleta, ignorar */ }
    }
  }
}

// Uso
searchStream(
  "Explique como funciona o protocolo QUIC",
  "sonar",
  (chunk) => process.stdout.write(chunk),   // Texto em tempo real
  (result) => {
    console.log("\n\n✅ Concluído!");
    console.log(`Fontes: ${result.citations.length}`);
  }
);
```

### Exemplo Python (requests + iter_lines)

```python
import requests
import json

API_URL = "https://perplexo.0api.cloud"
API_KEY = "sua-chave"

def search_stream(query, model="sonar"):
    response = requests.post(
        f"{API_URL}/search_stream",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"query": query, "model": model, "user_id": "python-stream"},
        stream=True,
        timeout=300,
    )

    full_answer = ""
    for line in response.iter_lines():
        if not line or not line.startswith(b"data: "):
            continue
        try:
            event = json.loads(line[6:])
            if "chunk" in event:
                print(event["chunk"], end="", flush=True)
                full_answer += event["chunk"]
            if "thinking" in event:
                print(f"\n[🧠 Raciocínio]: {event['thinking'][:100]}...\n")
            if "done" in event:
                print(f"\n\n✅ {len(event['citations'])} fontes encontradas")
                return event["answer"], event["citations"]
            if "error" in event:
                raise RuntimeError(event["error"])
        except json.JSONDecodeError:
            pass

    return full_answer, []

answer, citations = search_stream("O que é computação quântica?")
```

---

## 🖼️ Visão — `POST /vision`

Analisa imagens usando os modelos do Perplexity. Envie a imagem como base64.

**Body (JSON):**
```json
{
  "query": "O que tem nesta imagem? Descreva em detalhes.",
  "image_base64": "data:image/png;base64,iVBOR...",
  "model": "best"
}
```

**Resposta (200):**
```json
{
  "answer": "A imagem mostra um diagrama de arquitetura de microsserviços..."
}
```

---

## ❤️ Health Check — `GET /health`

Verifica se a API está operacional. **Não requer autenticação.**

```json
{
  "status": "healthy",
  "version": "3.1.0"
}
```

Possíveis valores de `status`:
- `healthy` — tudo funcionando (scraper + cliente + conectividade)
- `degraded` — funcional, mas com possíveis problemas de rede
- `unhealthy` — scraper ou cliente não disponível

---

## 🗂️ Gerenciamento de Histórico

A API mantém automaticamente o contexto de conversa por `user_id`. Use estes endpoints para controlar o histórico.

### Limpar Conversa — `POST /clear`

```json
{ "user_id": "meu-app" }
```

Salva a conversa atual em disco antes de limpar. Retorna o ID da conversa salva:

```json
{
  "success": true,
  "message": "Conversa salva (5 mensagens) e limpa",
  "user_id": "meu-app",
  "saved_conversation_id": "a1b2c3d4"
}
```

### Status de Conversas — `GET /conversation-status`

```
GET /conversation-status?user_id=meu-app
```

```json
{
  "user_id": "meu-app",
  "has_active_conversation": true,
  "message_count": 3
}
```

### Última Resposta — `GET /last_response`

```
GET /last_response?user_id=meu-app
```

Útil para recuperar a resposta mais recente sem refazer a busca.

### Histórico Salvo

```bash
# Listar conversas salvas
GET /history/list?user_id=meu-app

# Carregar conversa pelo ID (restaura contexto)
POST /history/load
{ "user_id": "meu-app", "conversation_id": "a1b2c3d4" }

# Deletar conversa
POST /history/delete
{ "user_id": "meu-app", "conversation_id": "a1b2c3d4" }
```

---

## Modelos Disponíveis

> Use `GET /models` para ver a lista atualizada em tempo real.

### ⚡ Respostas Rápidas (3–15 segundos)

Modelos para buscas rotineiras do dia a dia.

| ID | Modelo | Descrição |
|---|---|---|
| `best` | **Auto** | Seleciona automaticamente o modelo mais responsivo |
| `sonar` | **Sonar** | Modelo proprietário do Perplexity — rápido e preciso |
| `gpt-5.4` | **GPT-5.4** | OpenAI — respostas factuais e articuladas |
| `claude-sonnet-4.6` | **Claude Sonnet 4.6** | Anthropic — excelente para análise e síntese |
| `gemini-3-flash` | **Gemini 3 Flash** | Google — ultra-rápido |
| `gemini-3.1-pro` | **Gemini 3.1 Pro** | Google — forte em multilíngue e raciocínio |
| `grok-4.1` | **Grok 4.1** | xAI — modelo recente da xAI |

### 🧠 Respostas com Raciocínio (30s–2min)

Modelos **Thinking**: processam a pergunta internamente antes de responder. Ideais para questões que exigem raciocínio lógico, análise multicritério ou comparações profundas.

O campo `thinking` na resposta contém o raciocínio interno completo.

| ID | Modelo | Descrição |
|---|---|---|
| `gpt-5.4-thinking` | **GPT-5.4 Thinking** | OpenAI com cadeia de pensamento |
| `claude-sonnet-4.6-thinking` | **Claude Sonnet 4.6 Thinking** | Raciocínio passo a passo da Anthropic |
| `gemini-3-flash-thinking` | **Gemini 3 Flash Thinking** | Google Flash com raciocínio |
| `gemini-3.1-pro-thinking` | **Gemini 3.1 Pro Thinking** | Google Pro com raciocínio expandido |
| `grok-4.1-thinking` | **Grok 4.1 Thinking** | xAI com raciocínio |
| `kimi-k2.5-thinking` | **Kimi K2.5 Thinking** | Moonshot AI com raciocínio |
| `nv-nemotron-3-super-thinking` | **Nemotron 3 Super** | NVIDIA 120B — pesado, extremamente detalhista |

### 🔬 Pesquisa Profunda (2–5 minutos)

Para perguntas complexas que exigem múltiplas buscas, cruzamento de fontes e síntese extensiva. **Configure o timeout do seu cliente HTTP para pelo menos 300 segundos.**

| ID | Modelo | Descrição |
|---|---|---|
| `deep-research` | **Deep Research** | Pesquisa multi-etapa com dezenas de fontes |

### 🏆 Modelos Premium (requer conta Perplexity Max)

| ID | Modelo | Descrição |
|---|---|---|
| `claude-opus-4.6` | **Claude Opus 4.6** | O mais avançado da Anthropic |
| `claude-opus-4.6-thinking` | **Claude Opus 4.6 Thinking** | Opus com raciocínio — máxima profundidade analítica |

---

## Focus Modes

O parâmetro `focus` direciona a busca para tipos específicos de fonte.

| `focus` | Fontes consultadas | Quando usar |
|---|---|---|
| `web` | Web geral | Notícias, tutoriais, documentações, uso geral |
| `academic` | Papers, periódicos científicos | Pesquisa científica, revisões de literatura |
| `social` | Reddit, Twitter/X, fóruns | Opiniões, discussões, tendências sociais |
| `finance` | Mercados, SEC EDGAR, Yahoo Finance | Dados financeiros, ações, resultados de empresas |
| `writing` | Sem busca externa | Auxílio à escrita, geração de texto, edição |
| `all` | Todas as fontes acima | Máxima cobertura, sem filtro |

> **Dica:** Use `writing` quando quiser que o modelo apenas escreva/edite texto sem fazer buscas na web. Use `academic` para perguntas que exigem embasamento científico.

---

## Timeouts Recomendados

Configure o timeout HTTP do seu cliente de acordo com o modelo escolhido:

| Modelo | Timeout Mínimo | Nota |
|---|---|---|
| `sonar`, `best`, `gemini-3-flash` | 30s | Buscas rápidas do dia a dia |
| `gpt-5.4`, `claude-sonnet-4.6`, `gemini-3.1-pro`, `grok-4.1` | 60s | Consultas detalhadas |
| `*-thinking` | 120s | Processamento de raciocínio interno |
| `nv-nemotron-3-super-thinking` | 180s | Modelo pesado — 120B parâmetros |
| `deep-research` | 300s | Pesquisas acadêmicas e extensivas |

---

## Exemplos de Integração

### cURL

```bash
# Busca simples
curl -X POST https://perplexo.0api.cloud/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"query": "O que são transformers em IA?", "model": "sonar"}'

# Busca acadêmica
curl -X POST https://perplexo.0api.cloud/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"query": "Mecanismo de atenção em LLMs", "model": "sonar", "focus": "academic"}'

# Busca com raciocínio (aguarde 30s+)
curl --max-time 120 -X POST https://perplexo.0api.cloud/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"query": "Compare RISC-V vs ARM para IoT", "model": "gpt-5.4-thinking"}'

# Pesquisa profunda (aguarde até 5min)
curl --max-time 300 -X POST https://perplexo.0api.cloud/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"query": "Análise completa do mercado de semicondutores em 2025", "model": "deep-research"}'

# Streaming
curl -N -X POST https://perplexo.0api.cloud/search_stream \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"query": "O que é RAG?", "model": "sonar"}'
```

### Python

```python
import requests

API_URL = "https://perplexo.0api.cloud"
API_KEY = "sua-chave"

def search(query, model="sonar", focus="web", timeout=60):
    response = requests.post(
        f"{API_URL}/search",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"query": query, "model": model, "focus": focus, "user_id": "python-app"},
        timeout=timeout,
    )
    data = response.json()
    return data["answer"], data.get("citations", [])

# Busca rápida
answer, citations = search("O que é computação quântica?")
print(answer)
for c in citations:
    print(f"  - {c['title']}: {c['url']}")

# Busca acadêmica
answer, citations = search(
    "Impacto de transformers em NLP",
    focus="academic",
)

# Busca com raciocínio
answer, citations = search(
    "Compare os prós e contras de Rust vs Go para microsserviços",
    model="claude-sonnet-4.6-thinking",
    timeout=120,
)

# Pesquisa profunda
answer, citations = search(
    "Estado atual da fusão nuclear e previsões para 2030",
    model="deep-research",
    timeout=300,
)

# Conversa multi-turno (mesmo user_id)
search("Explique o que é Kubernetes", user_id="chat-1")
search("E como ele se compara ao Docker Swarm?", user_id="chat-1")  # lembra o contexto

# Limpar histórico
requests.post(
    f"{API_URL}/clear",
    headers={"X-API-Key": API_KEY},
    json={"user_id": "chat-1"},
)
```

### JavaScript / Node.js

```javascript
const API_URL = "https://perplexo.0api.cloud";
const API_KEY = "sua-chave";

async function search(query, { model = "sonar", focus = "web", userId = "node-app" } = {}) {
  const res = await fetch(`${API_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({ query, model, focus, user_id: userId }),
    signal: AbortSignal.timeout(60000),
  });
  const data = await res.json();
  return {
    answer: data.answer,
    citations: data.citations ?? [],      // ← campo correto: citations
    thinking: data.thinking ?? null,
    hasThinking: data.has_thinking,
  };
}

// Busca simples
const result = await search("Últimas descobertas em exoplanetas");
console.log(result.answer);
result.citations.forEach(c => console.log(`  - ${c.title}: ${c.url}`));

// Conversa multi-turno
await search("O que é TypeScript?", { userId: "chat-ts" });
await search("Quais as vantagens sobre JavaScript?", { userId: "chat-ts" }); // lembra contexto

// Limpar histórico
await fetch(`${API_URL}/clear`, {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
  body: JSON.stringify({ user_id: "chat-ts" }),
});
```

### Integração com Agentes de IA (Tool/Skill)

Se você está construindo um agente de IA que precisa de acesso a informações atualizadas da web, esta API pode ser usada como uma **tool/skill**:

```json
{
  "name": "web_search",
  "description": "Busca informações atualizadas na web usando Perplexity AI. Retorna resposta sintetizada com citações verificáveis. Use para perguntas que precisem de dados recentes ou verificação factual.",
  "parameters": {
    "query": {
      "type": "string",
      "description": "A pergunta ou consulta de busca"
    },
    "model": {
      "type": "string",
      "enum": ["sonar", "best", "gpt-5.4-thinking", "deep-research"],
      "default": "sonar",
      "description": "sonar=rápido (padrão), best=auto, gpt-5.4-thinking=raciocínio profundo, deep-research=pesquisa extensiva (até 5min)"
    },
    "focus": {
      "type": "string",
      "enum": ["web", "academic", "social", "finance", "writing", "all"],
      "default": "web",
      "description": "web=geral, academic=papers científicos, social=Reddit/X, finance=mercados, writing=sem busca externa"
    }
  },
  "endpoint": "POST /search",
  "auth": "X-API-Key header",
  "response_field": "answer",
  "citations_field": "citations"
}
```

---

## Segurança

- Todos os endpoints sensíveis exigem `X-API-Key` via header `X-API-Key` ou query param `?api_key=`
- Nenhum endpoint expõe dados internos (emails, tokens, IPs)
- Tokens são armazenados em volume Docker persistente
- Autenticação usa apenas o `session-token` — sem cookies extras injetados
- Rate limiting configurado via Flask-Limiter (20 req/min em `/search` e `/search_stream`)

---

## Monitoramento

### Uptime Kuma

| Campo | Valor |
|---|---|
| Tipo | `HTTP(s) - Keyword` |
| URL | `https://perplexo.0api.cloud/health` |
| Keyword | `healthy` |
| Intervalo | `60s` |

---

## Estrutura do Projeto

```
perplexo-api/
├── src/
│   ├── perplexity_mcp.py            # API Flask principal
│   ├── token_manager.py             # Gerenciamento de pool de tokens
│   └── perplexity_webui_scraper/    # Scraper integrado
│       ├── core.py                  # Lógica principal de comunicação
│       ├── http.py                  # Cliente HTTP com curl_cffi
│       ├── config.py                # ConversationConfig / ClientConfig
│       ├── models.py                # Definição dos modelos disponíveis
│       ├── constants.py             # Constantes (URLs, headers)
│       ├── types.py                 # Tipos e Literals
│       ├── exceptions.py            # Exceções customizadas
│       ├── resilience.py            # Retry com backoff
│       └── logging.py              # Logger com loguru
├── Dockerfile
├── docker-compose.yml
├── docker-compose.vpn.yml           # Compose com VPN (para VPS)
├── requirements.txt
└── .env.example
```

---

## Licença

MIT
