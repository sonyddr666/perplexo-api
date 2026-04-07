# Perplexo API

API REST para integrar Perplexity em skills, automações e clientes HTTP sem Telegram nem WhatsApp.

## O que ficou no projeto

- API Flask/MCP em `src/perplexity_mcp.py`
- Pool de tokens e refresh em `src/token_manager.py`
- Scraper bundled em `src/perplexity_webui_scraper/`
- Deploy Docker simples e versão com VPN

## Features

- Busca com histórico por `user_id`
- Streaming via SSE em `/search_stream`
- Vision via `/vision`
- Pool de tokens com rotação e refresh
- Persistência de histórico em `data/conversations`
- Autenticação opcional com `X-API-Key`
- Página simples de credenciais em `/credentials`

## Subir rápido com Docker

```bash
cp .env.example .env
```

Preencha pelo menos:

```env
PERPLEXITY_SESSION_TOKEN=seu_token
MCP_API_KEY=sua_chave_opcional
```

Depois:

```bash
docker compose up -d --build
```

API disponível em `http://localhost:5000`.

### Página de credenciais

Abra `http://localhost:5000/credentials` para:

- salvar token, cookie string ou JSON de cookies sem reexibir o valor salvo
- testar a credencial com um clique
- apagar as credenciais do armazenamento local e do runtime atual

Se `MCP_API_KEY` estiver configurada, a própria página pede a chave administrativa para autorizar as ações.

### Coolify

Para Coolify, o caminho recomendado é usar o `Dockerfile` diretamente.

Configuração mínima:

- porta interna: `5000`
- health check: `/health`
- volume persistente montado em `/app/data`
- variáveis: `PERPLEXITY_SESSION_TOKEN` opcional, `MCP_API_KEY` opcional e `MCP_PORT=5000`

O `docker-compose.yml` também foi ajustado para funcionar sem `env_file`, então ele pode receber variáveis direto da UI do painel.

## Rodar sem Docker

```bash
pip install -r requirements.txt
python src/perplexity_mcp.py
```

## Endpoints principais

| Método | Rota | Uso |
|---|---|---|
| `GET` | `/health` | Healthcheck |
| `GET` | `/models` | Lista modelos, focus modes e citation modes |
| `POST` | `/search` | Busca padrão com resposta JSON |
| `POST` | `/search_stream` | Busca com streaming SSE |
| `POST` | `/vision` | Busca com imagem em base64 |
| `POST` | `/clear` | Limpa a conversa de um `user_id` |
| `GET` | `/conversation-status` | Status da conversa atual |
| `GET` | `/history/list` | Lista históricos salvos |
| `POST` | `/history/load` | Reabre um histórico salvo |
| `GET` | `/config/library` | Consulta se o modo de salvar na biblioteca remota está ativo |
| `POST` | `/config/library` | Alterna salvar ou não a conversa na biblioteca do Perplexity |
| `POST` | `/tokens/set` | Atualiza token principal |
| `POST` | `/tokens/refresh` | Tenta renovar token |
| `GET` | `/tokens/status` | Estado do pool de tokens |
| `GET` | `/diagnostics` | Diagnóstico geral |

## Exemplo de chamada de skill

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua_chave" \
  -d '{
    "query": "Resuma as novidades sobre agentes de IA",
    "user_id": "skill-agent-1",
    "model": "sonar",
    "focus": "web",
    "time_range": "week",
    "citation_mode": "markdown"
  }'
```

Resposta típica:

```json
{
  "status": "success",
  "answer": "...",
  "thinking": null,
  "model_used": "sonar",
  "focus_mode": "web",
  "time_range": "week",
  "citations": [],
  "has_thinking": false,
  "conversation_info": {
    "id": "skill-agent-1",
    "uuid": null,
    "model": "sonar",
    "message_count": 1
  }
}
```

Sobre `conversation_info`:

- `id`: repete o `user_id` enviado e identifica o contexto local dentro da API
- `message_count`: conta os turnos acumulados dessa conversa local
- `model`: modelo usado na thread atual
- `uuid`: por padrão costuma vir `null`, porque o scraper roda em modo incógnito e não salva a conversa na biblioteca remota

Se você ativar `POST /config/library`, o modo incógnito é desligado e o `uuid` pode passar a vir preenchido com o identificador remoto da thread no Perplexity.

## Salvar na biblioteca remota

O comportamento padrão da API é **não salvar** as conversas na biblioteca da conta do Perplexity.

Isso acontece porque:

- o `ConversationConfig` nasce com `save_to_library = false`
- o scraper converte isso para `is_incognito = true`
- o Perplexity responde sem persistir a thread remota

Para verificar ou mudar isso:

```bash
curl -X GET http://localhost:5000/config/library
curl -X POST http://localhost:5000/config/library
```

## Upload de arquivo no `/search`

O endpoint aceita `multipart/form-data` além de JSON:

```bash
curl -X POST http://localhost:5000/search \
  -H "X-API-Key: sua_chave" \
  -F "query=Analise este PDF" \
  -F "user_id=skill-files" \
  -F "model=best" \
  -F "focus=web" \
  -F "file=@./arquivo.pdf"
```

## Streaming SSE

```bash
curl -N -X POST http://localhost:5000/search_stream \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua_chave" \
  -d '{
    "query": "Explique MCP em termos práticos",
    "user_id": "stream-demo",
    "model": "best",
    "focus": "web"
  }'
```

## Vision

```bash
curl -X POST http://localhost:5000/vision \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua_chave" \
  -d '{
    "query": "Descreva a imagem",
    "image_base64": "BASE64_AQUI",
    "model": "best"
  }'
```

## Variáveis de ambiente

| Variável | Uso |
|---|---|
| `PERPLEXITY_SESSION_TOKEN` | Token principal da sessão Perplexity |
| `MCP_API_KEY` | Chave opcional para proteger os endpoints |
| `MCP_PORT` | Porta da API |
| `TOKENS_DIR` | Diretório do pool de tokens |
| `CONVERSATIONS_DIR` | Diretório de histórico persistido |
| `MAX_ACTIVE_CONVERSATIONS` | Limite de conversas em memória |
| `CONVERSATION_TTL_SECONDS` | TTL do contexto em memória |
| `TOKEN_ROTATION_ENABLED` | Liga/desliga rotação do pool |
| `OPENVPN_USER` | Credencial para compose com VPN |
| `OPENVPN_PASSWORD` | Credencial para compose com VPN |
| `VPN_COUNTRY` | País no Gluetun |

## Estrutura

```text
perplexo-simple/
├── src/
│   ├── perplexity_mcp.py
│   ├── token_manager.py
│   └── perplexity_webui_scraper/
├── scripts/
│   └── refresh_token.py
├── data/
│   ├── conversations/
│   └── tokens/
├── Dockerfile
├── docker-compose.yml
├── docker-compose.vpn.yml
├── .env.example
└── requirements.txt
```

## Documentação adicional

- [ARQUITETURA.md](ARQUITETURA.md)
- [MANUAL.md](MANUAL.md)
- [DEPLOY-PAINEL.md](DEPLOY-PAINEL.md)

## Troubleshooting

- `503 Cliente não inicializado`: falta `PERPLEXITY_SESSION_TOKEN`
- `401 Unauthorized`: `MCP_API_KEY` enviada incorretamente
- `403/401` do Perplexity: use `/tokens/refresh` ou atualize `cookies.json`
- Streaming não chega: confira se o cliente suporta `text/event-stream`
