# Hardening Notes

This app is intentionally vulnerable — it exists to give the pipeline
something real to catch. This doc records what each pipeline stage should
flag, and what the actual fix would be in a production remediation pass.

| # | Vulnerability | Location | Caught by | Production fix |
|---|---|---|---|---|
| 1 | SQL injection | `app.py` `/user` | Semgrep (SAST) | Use parameterised queries (`cursor.execute(query, (user_id,))`) |
| 2 | Command injection | `app.py` `/ping` | Semgrep (SAST) | Use `subprocess.run(["ping", "-c", "1", host], shell=False)` with input validation on `host` |
| 3 | Hardcoded secret | `app.py` | Gitleaks | Move to a secrets manager (Key Vault / Secrets Manager); rotate the exposed credential |
| 4 | Insecure deserialization | `app.py` `/load-session` | Semgrep (SAST) | Never unpickle untrusted input — use JSON with schema validation instead |
| 5 | Debug mode enabled | `app.py` entrypoint | Semgrep / manual review | `debug=False` in any non-local entrypoint; gate via environment variable |
| 6 | Outdated dependency | `requirements.txt` | pip-audit (SCA) | Bump Flask to a current patched version; add Dependabot/Renovate for ongoing updates |
| 7 | Outdated base image | `Dockerfile` | Trivy (container scan) | Pin a current slim or distroless base image; rebuild regularly, not just on app changes |
| 8 | Running as root in container | `Dockerfile` | Trivy config check | Add a non-root `USER` directive |

## Design decisions worth defending in interview

- **Gate ordering is deliberate**: secrets scan runs first and blocks
  everything else, because a leaked credential is time-critical in a way
  code-quality findings aren't — no point spending CI minutes on SAST if
  there's a live AWS key in the diff.
- **SARIF everywhere**: Semgrep and Trivy both upload SARIF to GitHub code
  scanning rather than just failing the build silently. That gives the team
  a persistent, queryable findings history in the Security tab, not just a
  red X that disappears once someone re-runs the job.
- **DAST only runs on PRs against an ephemeral container**, not on every
  push to main — it's slower and noisier than the static gates, so it's
  positioned as a pre-merge check rather than blocking every commit.
- **SBOM generation** (CycloneDX via Syft) is produced on every container
  build and stored as an artifact — increasingly a compliance expectation
  (e.g. under EU/UK supply-chain guidance) even before anyone asks for it.
- **Severity thresholds are tuned, not zero-tolerance**: Trivy only fails on
  CRITICAL/HIGH, and the ZAP rules file downgrades low-value informational
  findings to WARN. A pipeline that fails on every informational finding
  trains engineers to ignore it; the goal is a gate people trust enough to
  not routinely override.
