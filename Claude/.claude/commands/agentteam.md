# /agentteam

Thin orchestrator entrypoint.

## Load order
1. `CLAUDE.md`
2. `.claude/rules/coordinator-mandate.md`
3. `.claude/rules/routing-and-ownership.md`
4. `.claude/rules/handoff-contract.md`
5. `.claude/rules/verification-standard.md`

## Procedure
1. Classify task size/risk.
2. Select minimum team.
3. Generate ownership map.
4. Run staged flow: plan (if needed) -> implement/debug -> verify.
5. Return concise report: changes, evidence, risks, next options.

## Team routing
- Tiny: implementer + verifier
- Scoped: planner + implementer + verifier
- Complex: planner + implementer + debugger + verifier
