# AGENTS.md — Claude Runtime Contract (Lean)

This repository uses `Claude/` as the canonical system.

## Purpose

Run a disciplined, token-efficient coding-agent workflow with a small durable role set. Preserve Jarett's foundation files and voice rules as non-negotiable constraints.

## Source of truth

- Personal/project foundation: `CLAUDE.md`, `about-me.md`, `brand-voice.md`, `working-preferences.md`
- Agent runtime policy: `.claude/rules/`
- Role playbooks: `.claude/agents/`
- Command entrypoints: `.claude/commands/agentteam*.md`
- Reusable workflows: `.claude/skills/`

## Durable role roster (5)

1. **coordinator** — orchestration and routing
2. **planner** — scoped plan and ownership map
3. **implementer** — minimal diffs in owned files
4. **debugger** — root-cause diagnosis and focused fix path
5. **verifier** — independent evidence-based validation

## Operating rules

- Use minimum team size that preserves quality.
- Assign each writable file to exactly one role.
- Keep handoffs compact using `.claude/rules/handoff-contract.md`.
- Never skip independent verifier pass for write operations.
- Stop and escalate on ambiguity, blocked validation, or repeated failed fixes.

## Task routing

- Tiny change: implementer + verifier
- Scoped change: planner + implementer + verifier
- Complex/failing system: planner + implementer + debugger + verifier

## Codex bridge

Minimal Codex runtime config lives in `.codex/` and points back to `.claude/` playbooks to avoid dual-system drift.
