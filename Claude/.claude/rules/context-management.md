# Context Management

Use artifacts, not memory, across stages.

- Store stage notes in `.claude/handoffs/` or `.worklog/` when tasks are multi-step.
- Summarize before dispatch; do not forward raw exploration dumps.
- Keep only decision-relevant context in active prompts.
- On interruption, restart from latest handoff artifact.
