# Perplexo API

API REST autossuficiente que expõe o poder de busca do [Perplexity.ai](https://perplexity.ai) via endpoints HTTP simples. Permite que qualquer aplicação, agente de IA ou automação faça buscas profundas na web com citações verificáveis — sem precisar de chave da API oficial.

---

## Como Funciona

A API usa um `session-token` de uma conta Perplexity Pro/Max para autenticar-se no serviço, simulando um navegador real via [curl_cffi](https://github.com/yifeikong/curl_cffi). Toda a comunicação é feita com fingerprint de browser (TLS, headers, JA3) para evitar bloqueios.

**Fluxo simplificado:**

```
Seu App → POST /search → Perplexo API → curl_cffi (Chrome fingerprint) → Perplexity.ai → Resposta com fontes
```

---

## Instalação

### Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/perplexo-api.git
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
git clone https://github.com/seu-usuario/perplexo-api.git
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

### 🔍 Busca — `POST /search`

Realiza uma busca no Perplexity e retorna a resposta com citações.

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

**Resposta (200):**
```json
{
  "status": "success",
  "answer": "## Diferenças Fundamentais\n\nA arquitetura ARM usa o design RISC...",
  "search_results": [
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
    "message_count": 1,
    "model": "sonar"
  }
}
```

### Parâmetros da Busca

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `query` | `string` | *obrigatório* | A pergunta ou consulta |
| `user_id` | `string` | `"default"` | ID do usuário (mantém contexto entre buscas) |
| `model` | `string` | `"best"` | Modelo de IA (ver tabela abaixo) |
| `focus` | `string` | `"web"` | Foco da busca: `web`, `academic`, `social`, `finance`, `all` |
| `time_range` | `string` | `"all"` | Filtro de data: `all`, `day`, `week`, `month`, `year` |
| `citation_mode` | `string` | `"markdown"` | Formato de citações: `default`, `markdown`, `clean` |

### 🖼️ Visão — `POST /vision`

Analisa imagens usando os modelos do Perplexity.

**Body (JSON):**
```json
{
  "query": "O que tem nesta imagem?",
  "image_base64": "data:image/png;base64,iVBOR..."
}
```

### ❤️ Health Check — `GET /health`

Verifica se a API está operacional. **Não requer autenticação.**

```json
{ "status": "healthy", "version": "3.1.0" }
```

### 📋 Modelos — `GET /models`

Lista todos os modelos e focus modes disponíveis. Requer `X-API-Key`.

### 🔧 Diagnóstico — `GET /diagnostics`

Verifica o status de autenticação com o Perplexity. Requer `X-API-Key`.

### 🔑 Tokens — `GET /tokens/status`

Métricas operacionais do pool de tokens. Requer `X-API-Key`.

---

## Modelos Disponíveis

### ⚡ Respostas Rápidas (segundos)

Modelos para buscas rotineiras — respostas em 3-15 segundos.

| ID | Modelo | Descrição |
|---|---|---|
| `best` | **Pro** | Seleção automática do modelo mais responsivo |
| `sonar` | **Sonar** | Modelo proprietário do Perplexity, rápido e preciso |
| `gpt-5.4` | **GPT-5.4** | OpenAI — respostas factuais e articuladas |
| `claude-sonnet-4.6` | **Claude Sonnet 4.6** | Anthropic — excelente para análise e síntese |
| `gemini-3.1-pro` | **Gemini 3.1 Pro** | Google — forte em multilíngue e raciocínio |

### 🧠 Respostas com Raciocínio (30s–2min)

Modelos **Thinking**: processam a pergunta internamente antes de responder. Ideais para questões que exigem raciocínio lógico, análise multicritério ou comparações profundas. O campo `thinking` na resposta contém o raciocínio interno.

| ID | Modelo | Descrição |
|---|---|---|
| `gpt-5.4-thinking` | **GPT-5.4 Thinking** | OpenAI com cadeia de pensamento |
| `claude-sonnet-4.6-thinking` | **Claude Sonnet 4.6 Thinking** | Raciocínio passo a passo da Anthropic |
| `gemini-3.1-pro-thinking` | **Gemini 3.1 Pro Thinking** | Google com raciocínio expandido |
| `nv-nemotron-3-super-thinking` | **Nemotron 3 Super** | NVIDIA 120B — pesado, detalhista |

### 🔬 Pesquisa Profunda (2–5 min)

Para perguntas complexas que exigem múltiplas buscas, cruzamento de fontes e síntese extensiva. **As respostas podem demorar vários minutos** — configure o timeout do seu cliente HTTP para pelo menos 300 segundos.

| ID | Modelo | Descrição |
|---|---|---|
| `deep-research` | **Deep Research** | Pesquisa multi-etapa com dezenas de fontes |

### 🏆 Modelos Premium (requer Perplexity Max)

| ID | Modelo | Descrição |
|---|---|---|
| `claude-opus-4.6` | **Claude Opus 4.6** | O mais avançado da Anthropic |
| `claude-opus-4.6-thinking` | **Claude Opus 4.6 Thinking** | Opus com raciocínio — máxima profundidade |

---

## Exemplos de Integração

### cURL

```bash
# Busca simples
curl -X POST https://sua-api.com/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"query": "O que são transformers em IA?", "model": "sonar"}'

# Busca com raciocínio (aguarde 30s+)
curl --max-time 120 -X POST https://sua-api.com/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"query": "Compare RISC-V vs ARM para IoT em 2025", "model": "gpt-5.4-thinking"}'

# Pesquisa profunda (aguarde até 5min)
curl --max-time 300 -X POST https://sua-api.com/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"query": "Análise completa do mercado de semicondutores em 2025", "model": "deep-research"}'
```

### Python

```python
import requests

API_URL = "https://sua-api.com"
API_KEY = "sua-chave"

def search(query, model="sonar", focus="web", timeout=60):
    response = requests.post(
        f"{API_URL}/search",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"query": query, "model": model, "focus": focus, "user_id": "python-app"},
        timeout=timeout,
    )
    data = response.json()
    return data["answer"], data.get("search_results", [])

# Busca rápida
answer, sources = search("O que é computação quântica?")

# Busca com raciocínio (timeout maior)
answer, sources = search(
    "Compare os prós e contras de Rust vs Go para microsserviços",
    model="claude-sonnet-4.6-thinking",
    timeout=120,
)

# Pesquisa profunda (timeout 5min)
answer, sources = search(
    "Estado atual da fusão nuclear e previsões para 2030",
    model="deep-research",
    timeout=300,
)
```

### JavaScript / Node.js

```javascript
const API_URL = "https://sua-api.com";
const API_KEY = "sua-chave";

async function search(query, model = "sonar") {
  const res = await fetch(`${API_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({ query, model, user_id: "node-app" }),
    signal: AbortSignal.timeout(60000),
  });
  return await res.json();
}

// Uso
const result = await search("Últimas descobertas em exoplanetas");
console.log(result.answer);
console.log(result.search_results);
```

### Integração com Agentes de IA (Skill)

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
      "description": "sonar=rápido, best=auto, gpt-5.4-thinking=raciocínio profundo, deep-research=pesquisa extensiva (5min)"
    }
  },
  "endpoint": "POST /search",
  "auth": "X-API-Key header"
}
```

---

## Segurança

- Todos os endpoints sensíveis exigem `X-API-Key` via header
- Nenhum endpoint expõe dados internos (emails, tokens, IPs)
- Tokens são armazenados em volume Docker persistente
- Autenticação usa apenas o `session-token` — sem cookies extras injetados
- Rate limiting configurado via Flask-Limiter

---

## Monitoramento

### Uptime Kuma

| Campo | Valor |
|---|---|
| Tipo | `HTTP(s) - Keyword` |
| URL | `https://sua-api.com/health` |
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

## Timeouts Recomendados

| Modelo | Timeout Mínimo | Uso |
|---|---|---|
| `sonar`, `best` | 30s | Buscas rápidas do dia a dia |
| `gpt-5.4`, `claude-sonnet-4.6` | 60s | Consultas detalhadas |
| `*-thinking` | 120s | Perguntas que exigem raciocínio |
| `deep-research` | 300s | Pesquisas acadêmicas/extensivas |

---

## Licença

MIT
