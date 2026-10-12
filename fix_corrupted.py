import re

with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the corrupted section (the one with literal \n characters)
corrupted = '''    # #1642: before_load can execute arbitrary commands - requires explicit acknowledgment`n    before_load_val = a.before_load or cfg.get("before_load")`n    if before_load_val is not None:`n        # Require explicit acknowledgment of security risk`n        before_load_acknowledged = cfg.get("before_load_acknowledge_risk", False)`n        if not before_load_acknowledged:`n            print("[strata] before_load can execute arbitrary commands and poses a security risk. "`n                  "To enable, set \"before_load_acknowledge_risk\": true in the config.", file=sys.stderr)`n            return 2`n        svc.before_load = before_load_val`n    else:`n        svc.before_load = None'''

fixed = '''    # #1642: before_load can execute arbitrary commands - requires explicit acknowledgment
    before_load_val = a.before_load or cfg.get("before_load")
    if before_load_val is not None:
        # Require explicit acknowledgment of security risk
        before_load_acknowledged = cfg.get("before_load_acknowledge_risk", False)
        if not before_load_acknowledged:
            print("[strata] before_load can execute arbitrary commands and poses a security risk. " +
                  "To enable, set 'before_load_acknowledge_risk': true in the config.", file=sys.stderr)
            return 2
        svc.before_load = before_load_val
    else:
        svc.before_load = None'''

if corrupted in content:
    content = content.replace(corrupted, fixed)
    with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Fixed corrupted before_load section')
else:
    print('FAILED: Could not find corrupted section')
    # Try to find what's there
    idx = content.find('# #1642: before_load can execute arbitrary commands')
    if idx >= 0:
        print('Found at index:', idx)
        print('Context:', repr(content[idx:idx+200]))