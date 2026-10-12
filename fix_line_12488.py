with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 12488 (index 12487) is corrupted
# It should be: '        svc.before_load = None\n'
lines[12487] = '        svc.before_load = None\n'

with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed line 12488')