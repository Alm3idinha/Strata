import re

with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def _foreign_origin(self) -> bool:
            """A web page of another origin sent this.  The Origin must be this server's own address (host and port),
             or an origin the config trusts (trusted_origins: the web app behind a reverse proxy or tunnel); no Origin
             is a client that is no browser.  Headers a proxy adds (X-Forwarded-*, CF-Ray, CF-Connecting-IP) prove
             nothing about the page that sent the request, so they open nothing."""
            origin = (self.headers.get("Origin") or "").rstrip("/")
            if not origin:
                return False
            origin_host = origin.split("://", 1)[-1]
            x_forwarded_host = self.headers.get("X-Forwarded-Host")
            if x_forwarded_host:
                host = x_forwarded_host.split(",")[0].strip()
            else:
                host = self.headers.get("Host", "")
            return bool(origin) and (origin_host != host) and (origin not in svc.trusted_origins)'''

new = '''def _foreign_origin(self) -> bool:
            """A web page of another origin sent this.  The Origin must be this server's own address (host and port),
             or an origin the config trusts (trusted_origins: the web app behind a reverse proxy or tunnel); no Origin
             is a client that is no browser.  Headers a proxy adds (X-Forwarded-*, CF-Ray, CF-Connecting-IP) prove
             nothing about the page that sent the request, so they open nothing - UNLESS trusted_origins is configured,
             in which case X-Forwarded-Host is used to determine the server's apparent host."""
            origin = (self.headers.get("Origin") or "").rstrip("/")
            if not origin:
                return False
            origin_host = origin.split("://", 1)[-1]
            # Only use X-Forwarded-Host when trusted_origins is configured (reverse proxy scenario)
            x_forwarded_host = self.headers.get("X-Forwarded-Host") if svc.trusted_origins else None
            if x_forwarded_host:
                host = x_forwarded_host.split(",")[0].strip()
            else:
                host = self.headers.get("Host", "")
            return bool(origin) and (origin_host != host) and (origin not in svc.trusted_origins)'''

if old in content:
    content = content.replace(old, new)
    with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Updated _foreign_origin method')
else:
    print('FAILED: Could not find target text')