# Manual da API

## Autenticação

Se `MCP_API_KEY` estiver preenchida no `.env`, envie:

```http
X-API-Key: sua_chave
```

Se a variável estiver vazia, a API aceita chamadas sem chave.

## Modelo de uso recomendado para skills

1. Gere um `user_id` estável por sessão ou usuário.
2. Consulte `GET /models` para mapear modelos/focus disponíveis.
3. Use `POST /search` para respostas JSON simples.
4. Use `POST /search_stream` quando quiser streaming incremental.
5. Chame `POST /clear` ao encerrar o contexto.

## Página de credenciais

Abra `GET /credentials` para usar uma tela simples de operação:

- cadastrar token, cookie string ou JSON de cookies
- testar a credencial sem exibir o segredo salvo
- apagar as credenciais locais com um clique

Se `MCP_API_KEY` estiver ativa, informe a chave no topo da página antes de salvar, testar ou apagar.

## Payload base de busca

```json
{
  "query": "texto da pergunta",
  "user_id": "skill-session-123",
  "model": "best",
  "focus": "web",
  "time_range": "all",
  "citation_mode": "markdown"
}
```

## Campos aceitos em `/search`

| Campo | Obrigatório | Observação |
|---|---|---|
| `query` | Sim | Texto da pergunta |
| `user_id` | Não | Mantém contexto entre chamadas |
| `model` | Não | Ex.: `best`, `sonar`, `gpt-5.4` |
| `focus` | Não | Ex.: `web`, `academic`, `social` |
| `time_range` | Não | `all`, `day`, `week`, `month`, `year` |
| `citation_mode` | Não | `default`, `markdown`, `clean` |

## Resposta de `/search`

| Campo | Tipo | Uso |
|---|---|---|
| `status` | string | `success` quando a busca conclui |
| `answer` | string | Resposta principal |
| `thinking` | string/null | Raciocínio quando disponível |
| `citations` | array | Fontes extraídas |
| `conversation_info` | object | Metadados da conversa |

## Busca com arquivo

O mesmo endpoint aceita `multipart/form-data`. O arquivo é salvo temporariamente, enviado ao Perplexity e depois removido.

Exemplo:

```bash
curl -X POST http://localhost:3000/search \
  -H "X-API-Key: sua_chave" \
  -F "query=Resuma este contrato" \
  -F "user_id=files-1" \
  -F "file=@./contrato.pdf"
```

## Streaming com SSE

O endpoint `/search_stream` responde em `text/event-stream`.

Eventos podem incluir:

- status
- thinking
- chunk
- citations
- done
- error

## Vision

`/vision` recebe:

```json
{
  "query": "O que aparece nesta imagem?",
  "image_base64": "....",
  "model": "best"
}
```

## Histórico e contexto

- `POST /clear` limpa a conversa ativa
- `GET /history/list` lista históricos persistidos
- `POST /history/load` reabre um histórico salvo
- `POST /history/delete` apaga um histórico salvo

## Tokens

### Atualizar token principal

```bash
curl -X POST http://localhost:3000/tokens/set \
  -H "Content-Type: application/json" \
  -d '{"token":"novo_token"}'
```

### Ver estado do pool

```bash
curl http://localhost:3000/tokens/status
```

### Tentar refresh

```bash
curl -X POST http://localhost:3000/tokens/refresh
```

## Códigos comuns

- `400`: payload inválido
- `401`: chave de API ausente/incorreta
- `429`: rate limit do servidor
- `500`: falha inesperada ou erro do scraper
- `503`: token ausente ou scraper indisponível
