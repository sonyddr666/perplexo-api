# Perplexo API — Arquitetura

## Visão geral

O projeto ficou com uma responsabilidade única: expor uma API HTTP para consulta ao Perplexity usando session token e o scraper bundled.

```text
cliente/skill
    |
    v
Perplexo API (Flask)
    |
    +--> TokenManager
    |      |
    |      +--> pool de tokens
    |      +--> cookies complementares
    |      +--> refresh/rotação
    |
    +--> perplexity_webui_scraper
           |
           +--> perplexity.ai
```

## Componentes

| Componente | Arquivo | Papel |
|---|---|---|
| API MCP | `src/perplexity_mcp.py` | Endpoints REST e SSE |
| Token Manager | `src/token_manager.py` | Pool, validação, rotação, refresh |
| Scraper bundled | `src/perplexity_webui_scraper/` | Conversa real com o Perplexity |
| Refresh script | `scripts/refresh_token.py` | Renovação manual/automatizada de token |

## Fluxo de `/search`

1. Cliente envia `query`, `user_id`, `model` e `focus`.
2. A API valida payload e autenticação.
3. O `TokenManager` seleciona o token/cookies ativos.
4. A conversa é criada ou reutilizada por `user_id`.
5. O scraper consulta o Perplexity.
6. A API devolve `answer`, `citations`, `thinking` e metadados.

## Contexto por `user_id`

- O histórico fica em memória enquanto a conversa está ativa.
- Em `clear`, timeout ou shutdown, a conversa pode ser persistida em `data/conversations`.
- Isso permite usar a API como backend de skill multi-turn sem um bot intermediário.

## Rotação e refresh

Quando há mais de um token no pool:

1. A chamada usa o token atual.
2. Se houver falha de autenticação, o pool tenta rotacionar.
3. Se necessário, o refresh usa cookies do navegador para recuperar a sessão.

## Endpoints por grupo

### Busca

- `POST /search`
- `POST /search_stream`
- `POST /vision`
- `GET /models`

### Conversa e histórico

- `POST /clear`
- `GET /conversation-status`
- `GET /history/list`
- `POST /history/load`
- `POST /history/delete`
- `GET /last_response`

### Tokens

- `GET /tokens/status`
- `POST /tokens/set`
- `POST /tokens/refresh`
- `POST /tokens/rotate`
- `GET|POST /tokens/pool`
- `POST /tokens/upload_cookies`
- `POST /tokens/reload`

## Topologias de deploy

### Compose simples

- Expõe a API em `5000`
- Mantém `data/` em volume Docker

### Compose com VPN

- O container `vpn` recebe o tráfego externo
- A API roda em `network_mode: service:vpn`
- Útil quando o acesso ao Perplexity precisa sair por outro IP
