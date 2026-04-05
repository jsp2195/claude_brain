# Findings — Agentteam Refactor (2026-04)

## keep

- Strong personal foundation in `CLAUDE.md`, `about-me.md`, `brand-voice.md`, `working-preferences.md`.
- Clear non-negotiables: no fabrication, no overclaiming, en-dash-only style rule.
- Project/memory structure already useful and compact for research context.

## tighten

- `Claude/AGENTS.md` is over-scoped for this workspace (12 agents, broad software-stack assumptions, duplicated policy text).
- Team guidance is duplicated and inconsistent between `CLAUDE.md`, `AGENTS.md`, and root playbook files.
- Existing playbook content assumes web/full-stack product workflows that do not match this research workspace.
- Verification language exists but is diffused across long text blocks; no compact handoff schema.

## merge

- Duplicate skill pairs in `Claude/skills/`:
  - `proposal-framing.md` + `skill-proposal-framing.md`
  - `technical-writing.md` + `skill-technical-writing.md`
- Duplicate long-form prompt artifacts:
  - `agent-team-playbook.md` and `agent-team-prompts.md` substantially overlap.
- Shared operational constraints should move to `.claude/rules/*` and be referenced by commands/agents instead of repeated.

## delete

- `Claude/agent-team-prompts.md` (duplicative, generic, high token cost, stale assumptions).
- Old 12-agent roster in `Claude/AGENTS.md` (replaced by lean Codex runtime contract).

## add

- A new `Claude/.claude/` runtime with:
  - thin `agentteam*.md` command entrypoints
  - 5-role durable agent roster
  - compact shared rules for routing, handoffs, verification, ownership, escalation
  - reusable workflow skills (team run, verify, debug, review)
- Minimal `Claude/.codex/` bridge (single config + lean agent manifests) to keep Codex-native execution maintainable.
- Worklog trail under `Claude/.worklog/202604/agentteam-refactor/` with references/findings/decisions and validation output.
