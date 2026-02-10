# Security Audit Roadmap — prusa_XL_soft

## Repository
- **Path:** D:/prusa_XL_soft
- **Primary stack:** Python, telemetry/monitoring
- **Data tier (initial):** confidential
- **Notes:** `.env` present at repo root; needs secret handling review.

## Phased roadmap (0–5)
### Phase0_TriageAndScope
- **Goal:** Run initial scan; review `.env` handling and exclusions.
- **Effort:** 0.5–1 day
- **Blast radius:** low

### Phase1_MetadataAndPolicy_Soft
- **Goal:** Add `project-metadata.yml` and non-blocking metadata check.
- **Effort:** 1 day
- **Blast radius:** low

### Phase2_SecretsAndDependabot
- **Goal:** Add secrets scanning + Dependabot for dependencies.
- **Effort:** 1–2 days
- **Blast radius:** medium

### Phase3_CodeQL
- **Goal:** Enable CodeQL for Python.
- **Effort:** 1–2 days
- **Blast radius:** medium

### Phase4_RemediationSprint
- **Goal:** Remove real secrets and move configs to env/secret store.
- **Effort:** 2–5 days
- **Blast radius:** medium

### Phase5_GovernanceHardening
- **Goal:** Make checks blocking.
- **Effort:** 1 day
- **Blast radius:** medium
