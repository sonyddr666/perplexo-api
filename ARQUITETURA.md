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

- O histórico ativo fica primeiro em memória RAM, indexado por `user_id`.
- Em `clear`, timeout, cleanup periódico, load/save explícito de histórico ou shutdown gracioso, a conversa pode ser persistida em `data/conversations`.
- Isso permite usar a API como backend de skill multi-turn sem um bot intermediário.

## Ciclo de memória local

1. A primeira chamada de um `user_id` cria uma conversa ativa em RAM.
2. As próximas chamadas com o mesmo `user_id` reutilizam essa conversa e preservam contexto.
3. O disco não é atualizado a cada request normal.
4. A persistência em `data/conversations` acontece quando a API decide salvar o contexto.

Consequência prática:

- se o processo for encerrado de forma graciosa, a API tenta salvar as conversas pendentes
- se o container ou processo morrer abruptamente, o contexto que estava só em RAM pode ser perdido

`message_count` no retorno de `conversation_info` representa esse contexto local da API, não a contagem oficial da biblioteca remota do Perplexity.

## Save To Library e modo incógnito

Por padrão, a API trabalha para não poluir a conta base do Perplexity com o histórico dos robôs ou integrações.

Fluxo:

1. O wrapper cria `ConversationConfig` com `save_to_library = false`.
2. O scraper transforma isso em `is_incognito = true` no payload enviado ao Perplexity.
3. A conversa executa normalmente, mas sem persistência remota por padrão.

Resultado:

- o `conversation_info.uuid` normalmente vem `null`
- o contexto continua existindo localmente na RAM da API
- o histórico remoto da conta principal fica limpo

Se `POST /config/library` for usado para ativar o modo de biblioteca:

- o modo incógnito deixa de ser usado
- o Perplexity pode devolver `backend_uuid`
- esse valor aparece como `conversation_info.uuid` nas respostas da API

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
- `GET /config/library`
- `POST /config/library`

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
