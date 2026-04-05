# References — Agentteam Refactor (2026-04)

## Target system reviewed (`Claude/`)

- `Claude/CLAUDE.md`
- `Claude/AGENTS.md`
- `Claude/about-me.md`
- `Claude/brand-voice.md`
- `Claude/working-preferences.md`
- `Claude/current-projects/*.md` (8 files)
- `Claude/memory/MEMORY.md`
- `Claude/memory/context/index.md`
- `Claude/memory/people/index.md`
- `Claude/memory/projects/index.md`
- `Claude/skills/*.md`
- `Claude/agent-team-playbook.md`
- `Claude/agent-team-prompts.md`

## Reference system reviewed (`A-Team-main/`, read-only)

- `A-Team-main/CLAUDE.md`
- `A-Team-main/AGENTS.md`
- `A-Team-main/readme.md`
- `A-Team-main/agents/team-architect.toml`
- `A-Team-main/agents/discovery/requirements-analyst.toml`
- `A-Team-main/agents/planning/skill-planner.toml`
- `A-Team-main/agents/review/dialogue-reviewer.toml`

## Requested reference targets not present in `A-Team-main`

The following paths were requested for inspection but do not exist in the checked-out reference tree:

- `A-Team-main/.claude/agents/`
- `A-Team-main/.claude/rules/`
- `A-Team-main/.claude/skills/`
- `A-Team-main/.codex/config.toml`
- `A-Team-main/.codex/agents/`

## Pattern extraction approach

- Preserve personal foundation files and voice from `Claude/` as source of truth.
- Borrow only high-leverage architecture patterns from `A-Team-main`: thin runtime config, authoritative playbooks, staged worklog, and explicit coordinator contract.
- Do not copy A-Team phase-heavy team-designer machinery.
