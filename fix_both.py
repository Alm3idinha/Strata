import re

with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all occurrences of the old line
pattern = r'x_forwarded_host = self\.headers\.get\("X-Forwarded-Host"\)'
matches = list(re.finditer(pattern, content))
print(f'Found {len(matches)} occurrences of old line')

for match in matches:
    start = match.start()
    # Show context
    context_start = max(0, match.start() - 100)
    context_end = min(len(content), match.end() + 100)
    print(f'--- Occurrence at {match.start()} ---')
    print(content[context_start:context_end])
    print()

# Replace all occurrences
old_line = 'x_forwarded_host = self.headers.get("X-Forwarded-Host")'
new_block = '''# Only use X-Forwarded-Host when trusted_origins is configured (reverse proxy scenario)
            x_forwarded_host = self.headers.get("X-Forwarded-Host") if svc.trusted_origins else None'''

count = content.count('x_forwarded_host = self.headers.get("X-Forwarded-Host")')
print(f'Replacing {count} occurrences...')

content = content.replace(
    'x_forwarded_host = self.headers.get("X-Forwarded-Host")',
    '# Only use X-Forwarded-Host when trusted_origins is configured (reverse proxy scenario)\n            x_forwarded_host = self.headers.get("X-Forwarded-Host") if svc.trusted_origins else None'
)

with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('File updated - both methods fixed')