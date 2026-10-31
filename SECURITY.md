# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | ✅ Active |
| < 0.2.0 | ❌ End of life |

## Dependency Security

Strata uses **uv** for reproducible dependency management with automated security updates.

### Automated Scans

| Tool | Schedule | Scope |
|------|----------|-------|
| GitHub Action | Weekly (Mon 06:00 UTC) | All Python + Node.js deps |
| Dependabot | Weekly (Mon 06:00 UTC) | All ecosystems |
| PR Check | Every PR | Lockfile + conflict check |

### Update Policy by Severity

| Severity | CVSS Range | Response Time | Action |
|----------|------------|---------------|--------|
| Critical | ≥ 9.0 | 24 hours | Emergency patch |
| High | 7.0 - 8.9 | 72 hours | Priority PR |
| Medium | 4.0 - 6.9 | 2 weeks | Regular PR |
| Low | < 4.0 | Next release | Batch update |

### Reporting a Vulnerability

**Please do NOT open a public issue for security vulnerabilities.**

Instead, report via:

1. **GitHub Security Advisories**: Use the "Report a vulnerability" button on the Security tab
2. **Email**: niko@strata.ai (PGP key available on GitHub profile)

Include:
- Affected component and version
- Steps to reproduce (if applicable)
- Impact assessment
- Suggested fix (if known)

We aim to acknowledge within 48 hours and provide a fix timeline within 5 business days.

### Dependency Pinning Strategy

Strata uses **minor-range pins** (`>=X.Y.Z,<X.(Y+1).0`) for direct dependencies, allowing patch/minor security updates while blocking breaking changes.

| Tier | Pattern | Examples |
|------|---------|----------|
| Core runtime | `>=X.Y.Z,<X.(Y+1).0` | `pillow>=13.0.0,<14.0.0` |
| Security-critical transitive | `>=X.Y.Z,<X.(Y+1).0` | `urllib3>=2.8.0,<3.0.0` |
| Platform-specific | Exact (`==`) | `colorama==0.4.6; sys_platform=="win32"` |

**Why minor-range?** `>=13.0.0,<14.0.0` allows patch/minor security updates (13.0.1, 13.1.0) but blocks breaking major changes (14.0.0).

### Automated Updates

| Tool | Schedule | Action |
|------|----------|--------|
| Dependabot | Weekly (Mon 06:00 UTC) | Grouped PRs for minor/patch updates |
| GitHub Action | Weekly (Mon 06:00 UTC) | `pip-audit`, fails on high/critical |
| PR Check | Every PR | `uv lock --check` + `uv run pip check` |

### Accepted Risks

The following vulnerabilities are tracked as accepted risks (cannot be fixed without breaking core functionality):

| Package | Version | CVE | Reason | Mitigation |
|---------|---------|-----|--------|------------|
| None currently | — | — | — | — |

*Reviewed and updated quarterly.*

### Running Security Checks Locally

```bash
# Full security audit
pip-audit

# Dependency conflict check
pip check

# Verify lockfile matches declared dependencies
uv lock --check

# Check for conflicts
uv run pip check
```

### Supply Chain Security

- All dependencies resolved via `uv.lock` (exact versions, content-addressed)
- GitHub Actions use `astral-sh/setup-uv@v4` with pinned version
- SARIF reports uploaded to GitHub Security tab
- Dependabot grouped PRs reduce review burden

---

*This policy is reviewed quarterly. Last updated: 2026-10-31*