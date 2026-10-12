## Security Improvements

This fork includes critical security hardening to prevent accidental misconfigurations:

1. **Empty API Key**: Now causes server startup to fail (was warning-only)
2. **CORS Wildcard**: `["*"]` without API key now causes startup failure (was warning-only)  
3. **API Monitor**: Enabling without API key now causes startup failure (was warning-only)
4. **Path Traversal**: `/web/` and `/fonts/` endpoints now block directory traversal attempts (return 400 instead of potentially serving arbitrary files)
5. **HTTP Security Headers**: Added security headers to all responses (X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Content-Security-Policy)
6. **Trusted Origins Check**: Fixed - now uses X-Forwarded-Host header when behind reverse proxies
7. **before_load Command**: Requires explicit acknowledgment to prevent arbitrary command execution
8. **Rate Limiting**: Added requests-per-minute limit per IP address (0 = disabled)

All changes convert warning-only conditions to hard errors that prevent server startup on insecure configurations.
