with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with the old x_forwarded_host assignment
for i, line in enumerate(lines):
    if 'x_forwarded_host = self.headers.get("X-Forwarded-Host")' in line and 'if svc.trusted_origins else None' not in line:
        print(f'Found old line at index {i}: {repr(lines[i])}')
        # Replace with the fixed version
        lines[i] = '            # Only use X-Forwarded-Host when trusted_origins is configured (reverse proxy scenario)\n'
        lines.insert(i+1, '            x_forwarded_host = self.headers.get("X-Forwarded-Host") if svc.trusted_origins else None\n')
        print('Fixed!')
        break

with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('File updated')