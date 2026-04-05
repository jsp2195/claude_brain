# Agent Team Playbook (Current)

This file is a concise human-facing summary of the runtime in `.claude/`.

## Use this workflow

1. Run `/agentteam` for normal coding tasks.
2. Let routing pick the minimum team size.
3. Require explicit file ownership before edits.
4. Require independent `/agentteam-verify` before sign-off.

## Commands

- `/agentteam` – end-to-end orchestrator
- `/agentteam-plan` – planning only
- `/agentteam-exec` – implementation only (with ownership map)
- `/agentteam-debug` – root-cause first
- `/agentteam-verify` – independent verification
- `/agentteam-review` – evidence-focused review

## Canonical policy locations

- Rules: `.claude/rules/`
- Roles: `.claude/agents/`
- Skills: `.claude/skills/`
- Codex bridge: `.codex/`

Legacy prompt-dump workflows were removed to reduce drift and token waste.
