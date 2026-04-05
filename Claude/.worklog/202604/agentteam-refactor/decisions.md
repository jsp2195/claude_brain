# Decisions — Agentteam Refactor (2026-04)

## 1) Adopt a 5-role durable roster

**Decision**: Standardize on 5 roles: coordinator, planner, implementer, debugger, verifier.

**Why**:
- Meets serious coding/research execution needs without coordination overhead.
- Preserves verification independence.
- Removes role overlap (architect/critic/reviewer/tester/docs/front-end splits were not justified for this repo).

**Alternatives considered**:
- 3-role minimal team (too weak for non-trivial debugging and independent verification).
- 7+ specialized team (high token cost and overlap).

## 2) Make `/agentteam` a thin orchestrator

**Decision**: Move stable policy to shared rule files and keep command entrypoints short.

**Why**:
- Reduces command token footprint.
- Prevents policy drift across entrypoints.
- Makes updates easier and safer.

## 3) Introduce explicit compact handoff schema

**Decision**: Require fixed handoff fields (objective, scope, owned files, evidence, open risks, next action).

**Why**:
- Better context compaction and recoverability.
- Lower chance of lost constraints across stages.

## 4) Keep Claude foundation as canonical

**Decision**: Preserve personal/project files and only update architecture-facing references.

**Why**:
- User-specific memory/voice is the non-transferable core.
- A-Team is used only for selected structural patterns.

## 5) Add minimal Codex-native support

**Decision**: Add `Claude/.codex/config.toml` + thin `Claude/.codex/agents/*.toml` that point to `.claude/agents/*` playbooks.

**Why**:
- Enables Codex runtime registration without creating a second architecture.
- Keeps one authoritative behavior layer (`.claude/`).

## 6) Remove stale/duplicative prompt dump

**Decision**: Delete `Claude/agent-team-prompts.md`; replace `agent-team-playbook.md` with concise runtime guidance.

**Why**:
- Eliminates duplicate long-form content and generic assumptions.
- Improves token efficiency and maintainability.
