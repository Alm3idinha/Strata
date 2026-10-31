# Strata Security Audit Plan

## Executive Summary

**Project:** Strata - Local AI Model Server  
**Audit Scope:** Server-side security (Python), client-side security (JavaScript), configuration, dependencies  
**Status:** Partial audit completed, remaining tasks identified

---

## Security Findings

### ✅ Already Implemented (Good)

1. **Host Header Validation (DNS Rebinding Protection)**
   - Location: `serve/server.py:6679-6696`
   - `parse_request()` validates Host header before processing
   - Default allowlist: `127.0.0.1`, `localhost`, `::1`
   - Configurable via `allowed_hosts` or `STRATA_ALLOWED_HOSTS`
   - Test coverage: `serve/test_security.py`

2. **Origin/CORS Checking**
   - Location: `serve/server.py:6698-6717`, `6761-6780`
   - CORS headers only sent for configured origins
   - Wildcard `*` only allowed when API key is set
   - Separate `cors_origins` (API access) and `trusted_origins` (internal pages)

3. **API Key Authentication**
   - Bearer token or `x-api-key` header support
   - Separate `telemetry_key` for read-only access (0.1.45+)
   - Read-only key cannot perform inference or management operations

4. **Input Validation**
   - Image prompt limit: 16,000 characters (`serve/images.py:92-93`)
   - Content-Length validation with configurable limit (`body_limit()`)
   - Chunked body size validation

5. **Error Handling**
   - Stack traces NOT exposed to users
   - Generic error messages returned
   - Internal logging only

6. **Session/Conversation Security**
   - Slot save/restore requires ownership page verification
   - File names validated against path traversal

### ⚠️ Concerns to Investigate

1. **SSRF in Image URL Fetching**
   - Location: `serve/images.py:2853-2867` (`Vision.download()`)
   - **Issue:** Arbitrary URL fetching without SSRF protections
   - No allowlist for schemes/hosts
   - Checks Content-Length header but not resolved IP address
   - No redirect following restrictions

2. **Missing Security Headers**
   - CSP limited to `frame-src 'none'` for previews
   - Missing: `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`
   - No `Referrer-Policy`, `Permissions-Policy`

3. **No Rate Limiting on Inference Endpoints**
   - Queue admission limiting exists but not traditional rate limiting
   - No request/IP-based throttling for abuse prevention

4. **MCP Server Integration**
   - Location: `serve/mcp.py`
   - Need to verify URL allowlisting for tool servers

5. **Image Format Handling**
   - WebP, TIFF, AVIF converted via Pillow (`serve/images.py:2882-2911`)
   - Need to verify file type validation before processing

### 🔍 Code Review Needed (Not Reviewed in This Audit)

1. `serve/mcp.py` - MCP server integration, URL fetching
2. `serve/frontend.py` - Chat template processing, markdown rendering
3. `serve/runconfig.py` - Run configuration parsing
4. Authentication token generation and key rotation
5. Pillow/PIL usage in image normalization
6. JavaScript XSS vulnerabilities in web frontend (`serve/web/*.js`)

---

## Remaining Tasks

### High Priority

| Task | File(s) | Description |
|------|---------|-------------|
| SSRF Protection | `serve/images.py`, `serve/server.py` | Add IP allowlist/blocklist for `Vision.download()` URLs |
| Security Headers | `serve/server.py` | Add HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy |
| MCP URL Validation | `serve/mcp.py` | Validate tool server URLs for SSRF protection |
| Rate Limiting | `serve/server.py` | Implement request/IP-based rate limiting |

### Medium Priority

| Task | File(s) | Description |
|------|---------|-------------|
| Image Type Validation | `serve/images.py` | Verify magic bytes before Pillow processing |
| Secrets Detection | All | Check for hardcoded credentials in `.env` templates |
| CSP Enhancement | `serve/server.py` | Harden Content Security Policy |
| Dependency Audit | `package.json`, `requirements.txt` | Run `npm audit` and `pip-audit` |

### Lower Priority

| Task | File(s) | Description |
|------|---------|-------------|
| Telemetry Sanitization | `serve/server.py` | Verify no prompts in telemetry output |
| API Response Sanitization | `serve/*.py` | Remove any fields that shouldn't be exposed |
| WebSocket Security | Check for WebSocket endpoints | Validate origin headers |

---

## Investigation Details

### SSRF Attack Vector (Critical)

**Location:** `serve/images.py:2853-2867`

```python
@staticmethod
def download(url: str) -> bytes:
    too_big = f"the image URL's file is over {IMAGE_URL_MAX >> 20} MiB"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "strata"}), timeout=60) as r:
            # ... checks Content-Length but NOT the resolved IP
            data = r.read(IMAGE_URL_MAX + 1)
    except (OSError, HTTPException) as e:
        raise ValueError(f"the image URL could not be read: {e}") from None
    if len(data) > IMAGE_URL_MAX:
        raise ValueError(too_big)
    return data
```

**Vulnerable to:**
- `http://169.254.169.254/` (cloud metadata)
- `http://localhost/`, `http://127.0.0.1/`
- Private IP ranges via DNS rebinding
- Redirect chains to internal targets

**Recommended Fix (from security guidelines):**

```python
import ipaddr
from node:dns/promises import lookup

ALLOWED_HOSTS = new Set()  # Optional: specific hosts

async function assertSafeUrl(raw: string): Promise<URL> {
  const url = new URL(raw);
  if (url.protocol !== 'https:') throw new Error('https only');
  if (!ALLOWED_HOSTS.has(url.hostname)) throw new Error('host not allowed');
  const addrs = await lookup(url.hostname, { all: true });
  if (addrs.some((a) => ipaddr.parse(a.address).range() !== 'unicast')) {
    throw new Error('private/reserved IP');
  }
  return url;
}

await fetch(await assertSafeUrl(req.body.webhookUrl), { redirect: 'error' });
```

---

## Validation Plan

1. **Run existing tests:**
   - `python -m pytest serve/test_security.py -v`
   - `python -m pytest serve/test_images.py -v`

2. **Verify fixes:**
   - Test URL with `169.254.169.254` blocked
   - Test URL with private IP redirects blocked
   - Test valid public URL allowed
   - Test SSRF attempts logged and rejected

3. **Dependency audit:**
   - `npm audit` in `apps/host/`
   - `pip-audit` on `requirements.txt`

4. **Security headers check:**
   - Use browser DevTools Network tab
   - Verify CSP, HSTS, X-Frame-Options present

---

## Files Examined

```
serve/server.py (HTTP handler)
serve/images.py (image generation)
serve/test_security.py (security tests)
serve/images.py (Vision class for URL fetching)
serve/web/app.js (client-side JavaScript)
strata.py (CLI entry)
strata_control/update_keys.json (public keys only)
```

---

## Next Steps

1. Implement SSRF protections for image URL downloads
2. Add security headers to HTTP responses
3. Run dependency audits
4. Complete review of MCP server integration
5. Add rate limiting for inference endpoints
6. Verify CSP policy sufficiency

---

*Plan created: 2026-10-30*  
*Based on security-and-hardening guidelines from skill documentation*