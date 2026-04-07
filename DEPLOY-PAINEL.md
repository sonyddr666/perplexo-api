# Deploy via painel Docker

## Portainer ou painel compatível

Use a stack com o conteúdo de `docker-compose.yml` para a versão normal, ou `docker-compose.vpn.yml` para a versão roteada por VPN.

## Variáveis mínimas

Preencha no painel:

```env
PERPLEXITY_SESSION_TOKEN=seu_token
MCP_API_KEY=sua_chave_opcional
MCP_PORT=5000
```

Se usar a stack com VPN:

```env
OPENVPN_USER=seu_usuario_nordvpn
OPENVPN_PASSWORD=sua_senha_nordvpn
VPN_COUNTRY=Brazil
```

## Passos

1. Crie uma nova stack.
2. Cole o conteúdo do compose escolhido.
3. Configure as variáveis de ambiente.
4. Faça o deploy.
5. Verifique `GET /health`.

## Testes rápidos

### Healthcheck

```bash
curl http://SEU_HOST:5000/health
```

### Busca

```bash
curl -X POST http://SEU_HOST:5000/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua_chave" \
  -d '{"query":"teste","user_id":"stack-check"}'
```

## Erros comuns

- `503 Cliente não inicializado`: token ausente ou inválido
- `401 Unauthorized`: ajuste `MCP_API_KEY`
- timeout no compose com VPN: confirme `OPENVPN_USER` e `OPENVPN_PASSWORD`
