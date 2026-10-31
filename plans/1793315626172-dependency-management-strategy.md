# Dependency Management Strategy for Strata

## Summary

Pinning exact versions (`==`) in `requirements.txt` gives reproducible builds but accumulates "security debt" over time — vulnerabilities accumulate until manual intervention. This plan migrates to **uv** lockfile management with automated security updates to balance reproducibility with ongoing security.

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Lockfile tool | **uv** | User selected; fast, modern, handles transitive deps correctly |
| Hash pinning | **Not initially** | Manual `pip hash` overhead; add later if needed |
| CI integration | **GitHub Actions** | Code is public on GitHub; native integration |
| Documentation | **In repo** (`CONTRIBUTING.md`, `SECURITY.md`) | User is sole maintainer but wants forkers to understand the process |

---

## Why Exact Pinning Causes Security Debt

1. **No automated path**: A pinned `pillow==13.0.0` stays forever until someone manually edits the file
2. **Manual triage**: Each new CVE requires finding the right version, testing, and merging
3. **Transitive deps hidden**: Direct deps may be pinned but transitive deps drift
4. **Drift risk**: `pip install -r requirements.txt` may not update transitive deps even if direct deps are pinned

---

## Implementation Plan

### Phase 1: Migrate to uv Lockfile

1. **Install uv** (if not present):
   ```bash
   pip install uv
   ```

2. **Create `pyproject.toml`** with dependency declarations:
   ```toml
   [project]
   name = "strata"
   version = "0.2.8"
   requires-python = ">=3.10"
   dependencies = [
       "numpy>=2.2.6",
       "jinja2>=3.1.6",
       "regex>=2026.9.10",
       "pyyaml>=6.0.3",
       "tqdm>=4.70.1",
       "requests>=2.34.2",
       "pillow>=13.0.0",
       "psutil>=7.2.2",
   ]
   ```

3. **Generate `uv.lock`**:
   ```bash
   uv lock
   ```

4. **Verify**:
   ```bash
   uv sync  # installs from lockfile
   python -m pip_audit  # should show 0 vulnerabilities
   ```

5. **Commit**: `uv.lock` to version control

### Phase 2: Update Pinning Strategy

Replace exact pins in `requirements.txt` with minor-range pins:

```txt
# Before (exact pins - no auto-updates)
pillow==13.0.0
urllib3==2.8.0

# After (minor-range - allows patch/minor security updates)
pillow>=13.0.0,<14.0.0
urllib3>=2.8.0,<3.0.0
```

**Rationale**: `>=13.0.0,<14.0.0` allows 13.0.1, 13.1.0, etc. (security patches) but blocks 14.0.0 (breaking changes).

### Phase 3: Automated Security Pipeline

Create `.github/workflows/dependency-security.yml`:

```yaml
name: Dependency Security

on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday 6 AM UTC
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.13' }
      - run: pip install uv
      - run: uv pip install -r requirements.txt
      - run: pip install pip-audit
      - run: pip-audit --format=json --output=audit-report.json
      - uses: actions/upload-artifact@v4
        with:
          name: audit-report
          path: audit-report.json
      - name: Check for high/critical
        run: |
          # Fail if any high or critical vulnerabilities found
          python -c "
          import json
          data = json.load(open('audit-report.json'))
          vulns = [v for v in data.get('dependencies', []) if v.get('vulns')]
          high_crit = [v for v in vulns if any(vv.get('severity', '').lower() in ('high', 'critical') for vv in v.get('vulns', []))]
          if high_crit:
              print(f'Found {len(high_crit)} packages with high/critical vulns')
              exit(1)
          print('No high/critical vulnerabilities')
          "
```

### Phase 4: Dependabot Configuration

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "security"
  - package-ecosystem: "npm"
    directory: "/apps/host"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "security"
```

### Phase 5: Documentation

**`CONTRIBUTING.md`** additions:
- How to update dependencies
- How to run `pip-audit`
- Security update policy

**`SECURITY.md`** (new file):
- Supported Python versions
- Dependency update cadence
- How to report vulnerabilities
- Known accepted risks (if any)

---

## Update Policy by Severity

| Severity | Response Time | Action |
|----------|---------------|--------|
| Critical (CVSS ≥ 9.0) | 24 hours | Emergency patch |
| High (CVSS 7.0-8.9) | 72 hours | Priority PR |
| Medium (CVSS 4.0-6.9) | 2 weeks | Regular PR |
| Low (CVSS < 4.0) | Next release | Batch update |

---

## Validation Checklist

- [ ] `uv.lock` committed and matches `requirements.txt`
- [ ] `pip-audit` shows 0 vulnerabilities
- [ ] `pip check` shows no conflicts
- [ ] All existing tests pass (56 security + 19 image + broader suite)
- [ ] GitHub Action runs weekly
- [ ] Dependabot creates PRs for updates
- [ ] `CONTRIBUTING.md` documents update process
- [ ] `SECURITY.md` created

---

## Rollback

If `uv` causes issues:
```bash
git checkout requirements.txt
pip install -r requirements.txt
```

---

## Open Question

**Hash pinning**: Should we add `--hash=sha256:...` to critical dependencies for supply-chain security?

- **Pros**: Prevents package substitution attacks
- **Cons**: Manual maintenance; `uv` handles this differently

**Recommendation**: Skip for now; revisit if threat model changes.