# Verification Standard

Verifier must be independent from implementer.

## Evidence requirements

- Run relevant checks/tests directly.
- Record exact commands and exit status.
- Distinguish pass, fail, and blocked-by-environment.
- Reject claims without fresh evidence.

## Minimum checks

1. Targeted validation for changed behavior.
2. Reference integrity check (no stale links to removed files).
3. Sanity review for constraints from `CLAUDE.md` and `brand-voice.md`.
