# Security Best Practices Report

## Executive Summary

The codebase is close to being deployable, but there are three meaningful security issues to address before treating it as safely internet-exposed. The largest risk is that the administrative surface becomes fully unauthenticated whenever `MCP_API_KEY` is left empty, which currently matches the documented default flow. There is also an API-key-in-query-string fallback that can leak administrative credentials into logs and browser history, plus missing request size limits on upload and base64-heavy endpoints that can be abused for memory or disk exhaustion.

## High Severity

### SEC-001

- Rule ID: FLASK-HTTP-001 / deployment hardening
- Severity: High
- Location: [src/perplexity_mcp.py](/E:/CODEX-testing/perplexo-simple/src/perplexity_mcp.py):104-121, [src/perplexity_mcp.py](/E:/CODEX-testing/perplexo-simple/src/perplexity_mcp.py):644-747, [src/perplexity_mcp.py](/E:/CODEX-testing/perplexo-simple/src/perplexity_mcp.py):1781-1802
- Evidence:

```python
if not MCP_API_KEY:
    return f(*args, **kwargs)
```

Administrative routes such as `/credentials/api/save`, `/credentials/api/clear`, `/tokens/*`, `/config/library`, and `/config/token` all rely on `require_api_key`.

- Impact: If the service is exposed publicly without `MCP_API_KEY`, any remote caller can overwrite credentials, erase credentials, toggle remote library persistence, or otherwise take over API administration.
- Fix: Fail closed for administrative endpoints when `MCP_API_KEY` is missing, or split auth into a dedicated required admin secret for credential-management and token-management routes.
- Mitigation: Until fixed, never expose this service publicly without `MCP_API_KEY` set and rotated.
- False positive notes: This is only not a finding if the service is guaranteed to stay private on an internal network.

## Medium Severity

### SEC-002

- Rule ID: FLASK-HTTP-001
- Severity: Medium
- Location: [src/perplexity_mcp.py](/E:/CODEX-testing/perplexo-simple/src/perplexity_mcp.py):113-116
- Evidence:

```python
provided_key = request.headers.get('X-API-Key', '')
if not provided_key:
    provided_key = request.args.get('api_key', '')
```

- Impact: Accepting the admin key via query string can leak it into reverse-proxy logs, browser history, analytics, referrers, and command history.
- Fix: Remove the `api_key` query parameter fallback and accept the secret only via header.
- Mitigation: If this cannot be removed immediately, ensure all access happens only over HTTPS and strip query strings from logs at the edge.
- False positive notes: This is still a risk even on otherwise authenticated endpoints because the problem is where the secret travels.

### SEC-003

- Rule ID: FLASK-LIMITS-001 / FLASK-UPLOAD-001
- Severity: Medium
- Location: [src/perplexity_mcp.py](/E:/CODEX-testing/perplexo-simple/src/perplexity_mcp.py):79-91, [src/perplexity_mcp.py](/E:/CODEX-testing/perplexo-simple/src/perplexity_mcp.py):1362-1374
- Evidence:

```python
class VisionRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    image_base64: str = Field(..., min_length=10)
```

```python
for key in request.files:
    file = request.files[key]
    if file.filename:
        tmp_path = upload_dir / safe_name
        file.save(tmp_path)
```

- Impact: A client can send arbitrarily large multipart uploads or extremely large base64 payloads, causing memory pressure, disk exhaustion, or worker starvation.
- Fix: Set `MAX_CONTENT_LENGTH` in Flask, cap `image_base64` size explicitly, and validate upload count/type/size before writing to disk.
- Mitigation: Enforce body limits at the reverse proxy or platform level immediately if app-level limits are not added yet.
- False positive notes: This is less severe only if an upstream gateway already enforces strict body-size limits, which is not visible in app code.

## Low Severity

### SEC-004

- Rule ID: Least-privilege information exposure
- Severity: Low
- Location: [src/token_manager.py](/E:/CODEX-testing/perplexo-simple/src/token_manager.py):895-918
- Evidence:

```python
"current_account": {
    "email": current_entry.get("email") if current_entry else None,
},
"complementary_cookies_keys": list(pool.get("cookies", {}).keys()),
"tokens": [
    {
        "email": e.get("email"),
        "preview": f"****{e['session_token'][-8:]}"
    }
]
```

- Impact: Once an operator key is compromised, the status endpoints reveal account identity, token previews, and supporting cookie names that help an attacker understand and persist access.
- Fix: Reduce status output to the minimum operational fields needed, especially for remotely accessible admin endpoints.
- Mitigation: Keep the admin API key isolated and rotate it if there is any suspicion of exposure.
- False positive notes: This is acceptable for tightly controlled internal-only tooling, but it is still more verbose than necessary.
