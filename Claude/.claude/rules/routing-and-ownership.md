# Routing and Ownership

## Team-size routing

- **Tiny (single file, low risk)**: implementer + verifier
- **Scoped (2–6 files or moderate risk)**: planner + implementer + verifier
- **Complex (cross-domain, unclear root cause)**: planner + implementer + debugger + verifier

## File ownership contract

- Every writable file is assigned to one role.
- Planner proposes ownership map.
- Coordinator confirms before implementation starts.
- If ownership conflict emerges, halt and re-plan.
