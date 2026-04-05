#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "[1/4] required runtime files"
for p in \
  .claude/commands/agentteam.md \
  .claude/agents/coordinator.md \
  .claude/agents/planner.md \
  .claude/agents/implementer.md \
  .claude/agents/debugger.md \
  .claude/agents/verifier.md \
  .claude/rules/verification-standard.md; do
  test -f "$p"
done

echo "[2/4] slash entrypoints"
ls .claude/commands/agentteam*.md >/dev/null

echo "[3/4] stale reference scan"
! rg -n "agent-team-prompts\.md|skill-code-editing\.md|skill-slide-decks\.md|skill-proposal-framing\.md|skill-technical-writing\.md" .

echo "[4/4] codex bridge integrity"
for p in .codex/config.toml .codex/agents/coordinator.toml .codex/agents/verifier.toml; do
  test -f "$p"
done

echo "Validation OK"
