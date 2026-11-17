# Dual-CI free-tier operating policy

Status: policy documented; **automatic quota-aware failover is NOT implemented**.

## Providers and safety
- CircleCI is the preferred hosted test provider while GitHub Actions is billing-restricted.
- GitHub Actions workflows are retained as fallback, provided included usage is available.
- Neither service is permitted to automatically upgrade to paid resources or increase spending caps.
- Do not automatically rerun failed pipelines or launch multiple resource-heavy matrices.
- Keep repositories private; grant external CI only the necessary repository permissions.
- Never store provider API keys or other secrets in source control.

## Triggering and quota constraints
- CircleCI and GitHub Actions are independent; a Git push may trigger **both** if both have push triggers.
- **No quota-aware switch is active.** Operators must inspect provider usage and pause/enable triggers or run the available provider manually.
- Before any future automatic failover, require verified provider API access, billing/credit visibility, bounded retries, idempotent per-commit run selection, and an explicit $0 spending guard.
- An infrastructure/credit exhaustion result must not be confused with a failing test suite.
- Avoid duplicate runs where possible; keep smoke checks small and reserve costly integration runs for explicit requests.
- Do not assume provider free credits are unlimited or that a $0 spending budget means included minutes are exhausted.

## Change safety
- Back up every existing file before modification and commit the backup first.
- No automatic merges or destructive changes; keep project-specific functionality intact.
- Report tests as passing only after inspecting completed runner results.
- Prefer project-specific test commands and isolated development branches.

## Current limitations
- This document is a policy, not an executable cross-provider failover controller.
- CircleCI project registration, branch filters, and usage settings must be checked in the CircleCI dashboard.
- Do not enable paid CircleCI features or deployment workflows merely to test.
