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
    "uuid": "backend-uuid",
    "model": "sonar",
    "message_count": 1
  }
}
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
