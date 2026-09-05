# DevSecOps Pipeline — SAST, Secrets, SCA, Container & DAST Gates

A portfolio project: a small deliberately-vulnerable Flask app, paired with a
GitHub Actions pipeline that gates merges and deploys on five categories of
automated security testing.

## Pipeline stages (in order)

1. **Secrets scan** (Gitleaks) — runs first, blocks everything downstream on
   any detected credential.
2. **SAST** (Semgrep, OWASP Top 10 + Python rulesets) — static analysis of
   application code, results uploaded as SARIF to GitHub code scanning.
3. **SCA / dependency scan** (pip-audit) — flags known-CVE dependencies.
4. **Container scan** (Trivy) + **SBOM generation** (Syft/CycloneDX) — image
   built once, scanned for CRITICAL/HIGH OS and package vulnerabilities
   before it goes anywhere; SBOM stored as a build artifact.
5. **DAST** (OWASP ZAP baseline) — dynamic scan against the app running in an
   ephemeral container, PR-triggered only.
6. **Deploy** — a placeholder job, only reachable if every prior gate passed,
   gated further by a GitHub Environment manual-approval rule.

See `docs/hardening-notes.md` for the full vulnerability-to-fix mapping and
the reasoning behind gate ordering, severity thresholds, and what's
deliberately *not* zero-tolerance.

## The vulnerable app

`app/app.py` contains five intentional vulnerabilities (SQL injection,
command injection, a hardcoded secret, insecure deserialization, and debug
mode left on) plus a deliberately outdated Flask pin and base image — enough
for every stage of the pipeline to have something real to catch, without
needing a large or realistic codebase.

## What I'd do next

- Add a **policy-as-code** gate (OPA/Conftest or Checkov) once IaC is
  introduced for deployment — currently this pipeline secures the
  application and container, not infrastructure provisioning.
- Wire Dependabot/Renovate in alongside pip-audit so vulnerable dependencies
  get flagged continuously, not just at PR time.
- Add a **break-glass override** path (documented, logged, time-bounded) for
  the rare case a gate needs to be bypassed under incident pressure — right
  now every gate is hard-blocking with no escape hatch, which is fine for a
  demo but not realistic for a live pipeline under on-call pressure.

---
*Portfolio/preparation project. The app is intentionally vulnerable and
should never be deployed outside a local scan target. Pipeline is
structurally correct and runnable in a real GitHub repo with the relevant
Actions secrets configured.*
