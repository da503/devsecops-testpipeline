# DevSecOps Pipeline — SAST, Secrets, SCA, Container & DAST Gates

A portfolio project: a small deliberately-vulnerable Flask app, paired with a
GitHub Actions pipeline that gates merges and deploys on five categories of
automated security testing.
## AI Notes
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

## AI Next Steps

- Add a **policy-as-code** gate (OPA/Conftest or Checkov) once IaC is
  introduced for deployment — currently this pipeline secures the
  application and container, not infrastructure provisioning. -- IAC Project completed
- Wire Dependabot/Renovate in alongside pip-audit so vulnerable dependencies
  get flagged continuously, not just at PR time.
- Add a **break-glass override** path (documented, logged, time-bounded) for
  the rare case a gate needs to be bypassed under incident pressure — right
  now every gate is hard-blocking with no escape hatch, which is fine for a
  demo but not realistic for a live pipeline under on-call pressure.
  
## Fox Notes

## The problem we're solving
Before code gets merged into the main version of a project we want to catch security problems before they hit live or having a (over)reliance on manual checks. Essentially have put together a quick pipeline to complete this

## Target involved
Five vulnerabilities in a Flask web app, to make it lighter to work with. Rocking five vulnerabilities:
-SQL injection in one endpoint
-Command injection in another
-Hardcoded fake API key sitting in the code
-Unsafe deserialization function- fun one for RCE's
-Debug mode left on

## Five Stages
-Gitleaks for secrets scan, looking for creds and passwords in the code itself, we start this off first as no point in doing checks if someones creds are in code
-SAST with Semgrep- Reading the source code without running it, looking for dangerous patters like unsanitised shell commands.
-SCA*Software Composition Analysis with pip-audit - We on dependency watch with this one checking libraries and published CVEs. Cache poisoning CVE and outdated Flask version
-Container Scan with Trivy - Once in a Docker container we scan the container image, involving OS package and app dependencies, SBOM created so we can see a list of everything running inside the container
-DAST - OWASP ZAP- Instead of reading , we run it in a temp container and attack live, only on pull requests as it's feedbacks a lot more and slower to do
We pace it in this way so that the faster and arguably more sensitive areas are ran first i.e. secret scans block everything and DAST relying on a working container to attack so has dependancy on a tool like Trivy

##Container Hardening best practice
-Edited the docker file to add in a dedicated Non-root user which I committed from "container hardening" so that it would no longer run as root
-Pinned the Dockerfile's base image from a floating tag i.e. the Python version, to an exact content digest that checks a hash value
-Further fixes would require bumping the python up so that the issues the pipeline are picking up are patched to stop it erroring out

A pull request can't reach a live deployment unless it goes through the afformentioned categories, with failures in the deployment(where the scans have yielded something) block until a fix is completed
---
