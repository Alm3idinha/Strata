import json

# Read the file
with open('serve/server.py', 'r') as f:
    content = f.read()

# Define the old and new strings exactly as they appear in the file
old_str = '''            return bool(origin) and origin.split("://", 1)[-1] != self.headers.get("Host", "") and \\
                origin not in svc.trusted_origins
'''

new_str = '''            if not origin:
                return False
            origin_host = origin.split("://", 1)[-1]
            x_forwarded_host = self.headers.get("X-Forwarded-Host")
            if x_forwarded_host:
                host = x_forwarded_host.split(",")[0].strip()
            else:
                host = self.headers.get("Host", "")
            return bool(origin) and (origin_host != host) and (origin not in svc.trusted_origins)
'''

# Replace
if old_str in content:
    content = content.replace(old_str, new_str)
    with open('serve/server.py', 'w') as f:
        f.write(content)
    print('SUCCESS: Replaced _foreign_origin method')
else:
    print('FAILED: String not found')
    # Let's try to see if we can find the old_str by printing the first 50 chars of the content around the area
    lines = content.splitlines()
    for i in range(5160, 5165):
        if i < len(lines):
            print(f'{i+1}: {repr(lines[i])}')