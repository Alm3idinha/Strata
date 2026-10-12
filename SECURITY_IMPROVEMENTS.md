# Security Improvements in This Fork

This fork includes critical security hardening to prevent accidental misconfigurations that could expose the server or leak data.

## Fixed Vulnerabilities

### 1. Empty API Key Authentication Bypass
- **Original Behavior:** Empty `api_key` in config logged a warning but started server without authentication
- **Fixed Behavior:** Empty `api_key` now causes server startup to fail with clear error message
- **Security Impact:** Prevents accidental public exposure of the AI model

### 2. CORS Wildcard Open Proxy
- **Original Behavior:** `cors_origins: ["*"]` without API key logged a warning but allowed any website to use the model
- **Fixed Behavior:** `cors_origins: ["*"]` without API key now causes server startup to fail
- **Security Impact:** Prevents creation of open proxy that could consume GPU resources from any website

### 3. API Monitor Data Leakage
- **Original Behavior:** `api_monitor: true` without API key logged a warning but allowed anyone to read stored prompts/responses
- **Fixed Behavior:** `api_monitor: true` without API key now causes server startup to fail
- **Security Impact:** Prevents leakage of sensitive user inputs and model responses

### 4. Path Traversal in Web Endpoints
- **Original Behavior:** `/web/` and `/fonts/` endpoints only checked for `/` and `\` in the request path, allowing directory traversal via `..` or URL-encoded sequences (e.g., `%2e%2e%2f`)
- **Fixed Behavior:** Added proper path normalization and verification that the resolved path is within the intended directory. Returns 400 Bad Request for traversal attempts.
- **Security Impact:** Prevents reading arbitrary files from the server filesystem (e.g., `/web/..%2Fserver.py` could leak source code)

### 5. Missing HTTP Security Headers
- **Original Behavior:** No security headers were included in HTTP responses, leaving the application vulnerable to clickjacking, MIME sniffing, and other attacks.
- **Fixed Behavior:** Added security headers to all responses:
  - `X-Frame-Options: DENY` (prevents clickjacking)
  - `X-Content-Type-Options: nosniff` (prevents MIME sniffing)
  - `Referrer-Policy: strict-origin-when-cross-origin` (controls referrer information)
  - `Content-Security-Policy`: restrictive policy allowing only same-origin resources
- **Security Impact:** Adds defense-in-depth against various web-based attacks.

### 6. Trusted Origins Check Behind Reverse Proxies (Fixed)
- **Issue:** The `_foreign_origin` method compared the `Origin` header with the `Host` header directly, which broke when a reverse proxy modified the `Host` header but not the `Origin` header.
- **Fixed:** Now uses the `X-Forwarded-Host` header (if present) to determine the original host for comparison, falling back to the `Host` header.
- **Location:** `serve/server.py` lines 5162-5170

### 7. before_load Arbitrary Command Execution (HIGH)
- **Original Behavior:** `before_load` config could execute arbitrary shell commands without acknowledgment
- **Fixed Behavior:** `before_load` now requires explicit acknowledgment via `before_load_acknowledge_risk: true` in config
- **Security Impact:** Prevents accidental or malicious execution of arbitrary commands
- **Files:** `serve/server.py` lines 6292-6304

### 8. Rate Limiting Missing (CRITICAL)
- **Original Behavior:** No rate limiting - server vulnerable to denial of service, GPU exhaustion, and memory exhaustion
- **Fixed Behavior:** Added token-bucket rate limiter per IP address with configurable requests per minute
- **Security Impact:** Prevents abuse, resource exhaustion, and denial of service attacks
- **Files:**
  - Command line argument: `serve/server.py` lines 6122-6124
  - Service attribute: `serve/server.py` lines 6307-6308
  - Handler fields: `serve/server.py` lines 4476-4479
  - Rate limit check: `serve/server.py` lines 4482-4487
  - Rate limit algorithm: `serve/server.py` lines 4489-4504
- **Files:** 

### 7. before_load Arbitrary Command Execution (HIGH)`n- **Original Behavior:** `before_load` config could execute arbitrary shell commands without acknowledgment`n- **Fixed Behavior:** `before_load` now requires explicit acknowledgment via `before_load_acknowledge_risk: true` in config`n- **Security Impact:** Prevents accidental or malicious execution of arbitrary commands`n- **Files:** `serve/server.py` lines 6292-6304`n`n### 8. Rate Limiting Missing (CRITICAL)`n- **Original Behavior:** No rate limiting - server vulnerable to denial of service, GPU exhaustion, and memory exhaustion`n- **Fixed Behavior:** Added token-bucket rate limiter per IP address with configurable requests per minute`n- **Security Impact:** Prevents abuse, resource exhaustion, and denial of service attacks`n- **Files:** `n  - Command line argument: `serve/server.py` lines 6122-6124`n  - Service attribute: `serve/server.py` lines 6307-6308`n  - Handler fields: `serve/server.py` lines 4476-4479`n  - Rate limit check: `serve/server.py` lines 4482-4487`n  - Rate limit algorithm: `serve/server.py` lines 4489-4504`n`n## Verification
- All original security tests pass (23/23)
- New verification tests confirm fixes work correctly
- Server fails fast on insecure configurations instead of running with vulnerabilities

These changes convert warning-only conditions into hard startup failures, following the principle that insecure configurations should not be allowed to run.
