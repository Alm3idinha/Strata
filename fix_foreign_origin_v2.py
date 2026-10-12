with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace lines 5193-5198 (0-indexed: 5193-5198)
new_lines = [
    '            # Only use X-Forwarded-Host when trusted_origins is configured (reverse proxy scenario)\n',
    '            x_forwarded_host = self.headers.get("X-Forwarded-Host") if svc.trusted_origins else None\n',
    '            if x_forwarded_host:\n',
    '                host = x_forwarded_host.split(",")[0].strip()\n',
    '            else:\n',
    '                host = self.headers.get("Host", "")\n',
    '            return bool(origin) and (origin_host != host) and (origin not in svc.trusted_origins)\n'
]

# Replace lines 5193-5198 (0-indexed: 5193-5198, so slice 5193:5199)
lines[5193:5199] = new_lines

with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('SUCCESS: Updated _foreign_origin method')