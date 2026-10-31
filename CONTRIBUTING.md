# Contributing to Strata

**AI assistance is welcome. The contributor is responsible for understanding the change and supplying real evidence.**

These rules apply to issues, pull requests, benchmark reports, and the agents helping prepare them.
You should be able to explain every changed line and answer review questions about it.

## Before starting

1. Search [issues](https://github.com/Niko1221/Strata/issues) and
   [pull requests](https://github.com/Niko1221/Strata/pulls), including closed discussions. Add new evidence to an
   existing thread when it covers your problem.
2. Read [AGENTS.md](AGENTS.md) and the documentation for the component you want to change.
3. Get maintainer agreement on scope before substantial features, refactors, architecture changes, or changes to
   defaults. Describe the user problem, proposed behavior, and tradeoffs in an issue first. Agreement on scope
   does not guarantee a merge. Focused fixes and benchmark reports can go straight to a PR.
4. Keep one problem per PR. Update that PR after feedback; do not open competing attempts for the same change.

Do not resubmit a declined proposal under a different title or through another agent. If new evidence changes
the situation, bring it to the original discussion and let a maintainer decide whether to reopen it.

## Report a problem people can investigate

Use the matching [issue form](https://github.com/Niko1221/Strata/issues/new/choose). A bug report should include:

- The smallest steps or command that reproduce the problem, and the expected and actual behavior.
- Strata version or commit, OS, GPU and VRAM, and relevant model, quantization, and configuration.
- The exact error and relevant logs, with credentials and private content removed.
- Whether you reproduced it yourself. Label a finding based only on reading code or a scanner as
  **unconfirmed static analysis**, and explain the suspected path without presenting it as an observed failure.

Do not invent reproduction steps, errors, affected hardware, or severity. If you cannot reproduce something,
say what you inspected and what would verify the hypothesis. Feature requests should explain a concrete user
need and the current workaround. Questions should say what you tried and where you got stuck.

Example structure, with placeholders to replace with actual observations:

```text
Problem: <one observed behavior>
Environment: <commit, OS, GPU/VRAM, model/quant, relevant settings>
Reproduce: <exact command or short sequence>
Expected: <documented or intended behavior>
Actual: <observed behavior and exact error>
Evidence: <sanitized log attachment>
Reproduction status: <reproduced locally OR unconfirmed static analysis>
```

## Titles

Every issue and pull request title starts with its area in square brackets, then a short description: `[Engine]`, `[GUI]`, `[TUI]`,
`[Benchmark]`, `[Docs]` or `[Other]`. For example `[Engine] fix decode stop on long prompts` or `[GUI] keep the model list after a tab
switch`. The issue forms ask for the area and a check on the title fails when the prefix is missing.

## Prepare a focused pull request

Lead with the problem and resulting behavior. Explain why the approach is needed, the important limits, and
any compatibility effects. Link the issue and scope agreement when applicable. A file-by-file narration or
an AI-generated summary of the diff is not a substitute for this explanation.

- Keep unrelated formatting, cleanup, dependency changes, and speculative abstractions out of the PR.
- Add documentation where it changes what a user or developer needs to know. Avoid repeated summaries,
  speculative roadmaps, and generated documentation with no actionable information.
- Preserve existing behavior outside the intended change. New features are opt-in; follow the default-path
  and performance requirements in [AGENTS.md](AGENTS.md).
- Read the complete diff, including generated files, before submitting. Remove debugging output, secrets,
  private paths, and accidental files.
- Prefer a small relevant regression check over tests that only restate the implementation. Documentation-only
  changes need link, example, and consistency checks; they do not require GPU builds.

## Show the validation you actually performed

List exact commands, the revision and environment tested, and observed outcomes. Keep **passed**, **failed**,
and **not run** separate. Include relevant output or a log attachment. A command you suggest running is not
evidence that it passed; a CI run on a different revision is not validation of the submitted code.

Build every backend a code change touches, including CUDA, HIP, and SYCL where applicable, before requesting
review. For changes that need hardware execution, report that execution separately from compilation. A mock,
static check, or successful build does not establish hardware correctness. If you lack a required environment,
keep the PR as a draft, identify the missing checks, and ask for targeted help in the same thread. Do not claim
compatibility you have not tested.

Performance claims need before/after runs on the same hardware and workload, with every changed setting
identified. Preserve the individual runs, failures, and variability. Follow the
[community measurement guide](docs/COMMUNITY_BENCHMARKS.md); standard submissions will use the
[benchmark protocol](docs/BENCHMARK_PROTOCOL.md) once it is activated. One fast run does not justify changing a
default or claiming a speedup for other machines.

Example PR body; placeholders are not test results:

```text
Problem and result: <trigger; behavior before and after the change>
Related discussion: <issue URL and scope agreement, when required>
Approach: <why this fix; relevant compatibility effects>
Validation:
  Passed: <exact command, revision/environment, observed result, log>
  Failed: <exact command and failure, or none observed>
  Not run: <check, reason, and what remains unverified>
Limits: <known limitations or remaining work>
```

## Rules for AI-assisted work

Use agents to help investigate, implement, and explain work that you can review. Before submitting, verify
their claims against the source, actual command output, or a cited primary reference.

Never submit fabricated measurements, invented test results, fake logs, or copied claims you have not checked.
Do not turn a repository scan into a batch of speculative issues or PRs. Consolidate related findings, establish
their effect, and submit the useful evidence. Do not present an agent's confidence or another model's approval
as validation. Keep review replies concise and address the requested change or evidence directly.

Maintainers may request a smaller change, return a PR to draft, or close a submission that lacks evidence,
duplicates existing work, or ignores agreed scope. A smaller, understandable contribution with honest limits
is easier to review and maintain.

## Share a benchmark

A results-only PR should contain the human report, raw measurements, sanitized configuration, and supporting
logs. Keep it separate from engine changes and include poor results and failed requests.

The [current community benchmark guide](docs/COMMUNITY_BENCHMARKS.md) remains available for measurements made
with today's tools. The [new protocol](docs/BENCHMARK_PROTOCOL.md) defines the draft standard and future approval
workflow. Its draft status must remain visible: existing reports are not automatically standard or approved.

## Dependency Management

Strata uses **uv** for reproducible dependency management with automated security updates.

### Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata and dependency declarations (minor-range pins) |
| `uv.lock` | Exact versions for reproducible builds (committed) |
| `requirements.txt` | Minor-range pins for pip-based installs (legacy compatibility) |
| `requirements-*.txt` | Build/monitor/nvfp4 specific dependencies |

### Pinning Strategy

| Tier | Pattern | Examples |
|------|---------|----------|
| Core runtime | `>=X.Y.Z,<X.(Y+1).0` | `pillow>=13.0.0,<14.0.0` |
| Security-critical transitive | `>=X.Y.Z,<X.(Y+1).0` | `urllib3>=2.8.0,<3.0.0` |
| Build tools | `>=X.Y.Z,<X.(Y+1).0` | `cmake>=4.4.3,<5.0.0` |
| Platform-specific | Exact (`==`) | `colorama==0.4.6; sys_platform=="win32"` |

**Why minor-range?** `>=13.0.0,<14.0.0` allows patch/minor security updates (13.0.1, 13.1.0) but blocks breaking major changes (14.0.0).

### Updating Dependencies

**For maintainers:**
```bash
# Update a specific package to latest allowed version
uv lock --upgrade-package pillow

# Update all packages within allowed ranges
uv lock --upgrade

# Sync environment to lockfile
uv sync --all-extras
```

**CI validation:** Every PR runs `uv lock --check` and `uv run pip check` to ensure lockfile consistency.

### Automated Security Updates

| Tool | Schedule | Action |
|------|----------|--------|
| Dependabot | Weekly (Mon 06:00 UTC) | Creates grouped PRs for minor/patch updates |
| GitHub Action | Weekly (Mon 06:00 UTC) | Runs `pip-audit`, fails on high/critical CVEs |
| PR Check | Every PR | `uv lock --check` + `uv run pip check` |

**Severity response:**
| Severity | Response | Action |
|----------|----------|--------|
| Critical (CVSS ≥ 9.0) | 24 hours | Emergency patch |
| High (CVSS 7.0-8.9) | 72 hours | Priority PR |
| Medium (CVSS 4.0-6.9) | 2 weeks | Regular PR |
| Low (CVSS < 4.0) | Next release | Batch update |

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

### Accepting Risks

If a vulnerability cannot be fixed (e.g., transitive dep blocked by direct dep), document it in `SECURITY.md` with:
- CVE ID
- Affected package and version
- Reason it cannot be fixed
- Mitigation in place

### For Fork Maintainers

If you fork Strata, the automated dependency updates will work automatically via GitHub Actions and Dependabot. You only need to:
1. Enable Dependabot in your fork's settings (Settings → Security → Dependabot)
2. Ensure GitHub Actions are enabled
3. Review and merge the weekly Dependabot PRs
