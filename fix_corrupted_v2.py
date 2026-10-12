with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the corrupted section starting at index 740448
idx = 740448
# Find the end of the corrupted section - look for 'def write_temporary'
end_idx = content.find('def write_temporary', idx)
if end_idx == -1:
    end_idx = idx + 500

# Create the fixed version
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

# Replace from idx to end_idx
content = content[:idx] + fixed + content[end_idx:]

with open(r'C:\Users\Almeidinha\Desktop\PROJETOS\Strata\serve\server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('SUCCESS: Fixed corrupted section')