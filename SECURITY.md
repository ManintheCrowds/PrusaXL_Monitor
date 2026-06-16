# Reporting security issues

Thanks for taking the time to disclose responsibly.

## How to report

Please use GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)
on this repository. That keeps the report visible to the maintainer without
exposing the details publicly.

If private reporting is unavailable for any reason, open a regular issue
titled `security: brief description` **without** any exploit details, and
the maintainer will reply with a private channel.

## What to include

- A description of the issue and its potential impact.
- Steps to reproduce — minimal is fine, a full PoC is not required.
- Affected versions if you've narrowed them down.
- Whether you'd like to be credited in the eventual fix.

## What to expect

- Initial acknowledgement within a few days.
- A fix or mitigation plan within ~30 days for confirmed issues; longer for
  cases that require coordinated disclosure with upstream dependencies.
- Public credit once a fix has shipped, if you'd like.

## Scope

PrusaXL_Monitor is a **local or LAN-deployed** observability stack: Flask
API, read-only collectors (PrusaLink, OctoPrint, log files), PostgreSQL
telemetry storage, and optional Redis/Grafana. Printer credentials belong
in environment variables only (see `.env.example`).

Issues we care about:

- Unauthenticated or broken-auth access to the Flask troubleshoot API or
  other write paths.
- Credential leakage via logs, API responses, or error handlers.
- SSRF or path escape via collector URLs or log paths supplied through
  config or API input.
- SQL injection or unsafe deserialization in the API or knowledge-base
  ingest paths.
- Secrets committed to the repository or included in build artifacts.

Issues that are **out of scope**:

- Issues that require physical LAN access to the printer with no impact on
  this application's host or data store.
- Bugs that require a malicious operator who already controls `.env` and
  the deployment host.
- Upstream PrusaLink, OctoPrint, or firmware vulnerabilities (report to
  the upstream project; mention here only if our integration amplifies
  impact).

## Operational hygiene

- Keep PrusaLink/OctoPrint credentials in `.env` only; never commit real
  values. `.env` is gitignored.
- Before pushing, run from repo root:
  `gitleaks detect --config .gitleaks.toml --no-git`
- Do not expose the Flask API to the public internet without authentication
  and TLS. Treat PostgreSQL and Redis as sensitive on the same network
  segment.
