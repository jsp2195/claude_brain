# Agent Team Setup — Paste This Into Claude Code

Read the file `agent-team-playbook.md` in this project root. Using it as your reference, do the following:

## 1. Enable Agent Teams
Update `~/.claude/settings.json` to add `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` to the `env` section. Create the env section if it doesn't exist. Don't overwrite any existing settings.

## 2. Generate CLAUDE.md
Scan this entire codebase and generate a `CLAUDE.md` at the project root following the Phase 1A template in the playbook. Auto-populate everything you can find: tech stack, directory structure, build/test/run commands, architecture patterns, coding conventions. Include the full AGENT INSTRUCTIONS section from the playbook.

## 3. Create Agent Definitions
Create `.claude/agents/` with these markdown files, following the Phase 2A template in the playbook:
- `architect.md` (opus, READ-ONLY)
- `planner.md` (opus, READ-ONLY)
- `frontend.md` (sonnet)
- `backend.md` (sonnet)
- `tester.md` (sonnet)
- `reviewer.md` (opus, READ-ONLY)
- `docs.md` (haiku)

Each agent file must include: role, description, model, responsibilities, NOT responsible for, constraints, success criteria, output format, and a Failure_Modes_To_Avoid section.

## 4. Create the /agentteam Skill
Create `.claude/commands/agentteam.md` with the content below. This is the slash command I'll use for all future agent team work.

```markdown
# Agent Team Launcher

You are a team orchestrator. The user has invoked `/agentteam` with an instruction. Your job is to interpret what they want and launch the right kind of agent team.

## How to Interpret the Instruction

Match the user's request to one of these patterns:

### Pattern: Feature Build
Triggers: describes a feature, says "build", "add", "create", "implement"
Action: Launch a full agent team (team lead + backend + frontend + tester). Create a feature branch. Each agent owns specific files — no overlapping edits. Run the full test suite before marking done. Prepare a PR description but do NOT submit until the user reviews.

### Pattern: Bug Fix / Debug
Triggers: describes a bug, says "fix", "debug", "broken", pastes an error message
Action: Launch a debugging team with 2-3 hypothesis agents investigating different theories in parallel. Each agent traces code paths, checks git blame, cites file:line for every claim. Team lead synthesizes findings and proposes the minimal fix. Do NOT implement until the user confirms.

### Pattern: Small Change
Triggers: clearly a small/quick task, single-file change, says "quick", "just", "simple"
Action: Launch a lightweight 2-agent team (implementer + reviewer). Implementer makes the change and runs tests. Reviewer checks the diff for edge cases and correctness. Keep it fast.

### Pattern: Research / Investigation
Triggers: says "investigate", "explore", "understand", "why does", "how does"
Action: Launch a research team with 2-3 explorer agents, each investigating a different angle. Each gathers evidence with file:line references, forms a hypothesis, tests it against the code, and reports findings with a confidence level. Team lead synthesizes into a single report. Do NOT implement anything.

### Pattern: Review
Triggers: says "review", "check", "audit", mentions a PR or branch
Action: Launch a review team checking: correctness, edge cases, security, performance, style consistency, test coverage, dead code. Output a structured review with APPROVED or CHANGES REQUESTED and file:line feedback for every issue found.

### Pattern: Multi-Feature Parallel
Triggers: lists multiple features/issues, says "parallel", "all of these"
Action: Create separate agent teams in separate worktrees, one per feature. Each team works independently. Prepare PRs but don't merge. Tell the user you'll merge sequentially with rebasing.

## Rules for ALL Patterns

1. Read CLAUDE.md first for project context, conventions, and agent instructions
2. Read agent definitions from .claude/agents/ to understand each role
3. Each agent owns specific files — never let two agents edit the same file
4. Run lsp_diagnostics on every modified file
5. Run the full test suite before claiming completion
6. Keep changes as small as possible — smallest viable diff
7. No debug code left behind (console.log, TODO, HACK, debugger)
8. Update docs after implementation when relevant
9. Limit teams to 3-5 agents unless the task clearly needs more

## After Completion

When the team finishes, report:
- What was done (changes made, with file references)
- Verification results (tests, type checking, linting)
- Any open questions or follow-up suggestions

$ARGUMENTS
```

## 5. Create the Playbook Reference
Save the full `agent-team-playbook.md` content as `.claude/skills/agent-team-playbook.md` so it's always available as a reference for agents.

## 6. Confirm
After completing all steps, show me:
- What was added to settings.json
- A summary of CLAUDE.md contents
- The list of agent files created
- Confirmation that `/agentteam` is ready to use

Then tell me to restart Claude Code to activate agent teams.
