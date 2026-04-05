# Claude Code Agent Team — Prompt Playbook

A complete set of prompts to build out your own agent team system in Claude Code, synthesized from Heeki Park's workflow, oh-my-claudecode's 19-agent catalog, A-Team's phased design system, and community best practices.

---

## Phase 0: Environment Setup

Run these in your terminal before anything else.

### 0A. Enable Agent Teams

```
Open your Claude Code settings and add the following to the env section:

"env": {
  "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
}

Then restart Claude Code.
```

### 0B. Set Up tmux + Worktrees (Terminal Prompt)

```
Set up my development environment for agent teams:
1. Create a tmux session named after this project
2. Window 1: runtime (split into backend pane + frontend pane)
3. Window 2: agent team workspace
4. Window 3: side exploration / ad-hoc tasks
Configure the status bar to show: branch, model, context window %.
```

---

## Phase 1: Project Foundation — CLAUDE.md

This is the most important prompt. Your CLAUDE.md is the "constitution" every agent reads on startup.

### 1A. Generate Your Project's CLAUDE.md

```
Create a CLAUDE.md file for this project that will serve as the shared context for all agents and agent teams. Include:

PROJECT OVERVIEW:
- Project name, purpose, and tech stack
- Repository structure with key directories explained
- How to build, test, and run (exact commands)

ARCHITECTURE:
- High-level system design (backend, frontend, database, external services)
- Key abstractions and patterns used in this codebase
- File ownership boundaries (which directories belong to which domain)

CODING STANDARDS:
- Naming conventions, import style, error handling patterns
- Test expectations (unit, integration, what coverage is expected)
- Commit message format (use conventional commits)

AGENT INSTRUCTIONS:
- Always explore the codebase before making changes (Glob, Grep, Read)
- Match existing code patterns — never introduce new abstractions for single-use logic
- Run lsp_diagnostics on every modified file before claiming completion
- Run the full test suite before marking any task done
- Keep changes as small as possible — smallest viable diff wins
- Never leave debug code (console.log, TODO, HACK, debugger statements)
- Update documentation (README, SPECIFICATIONS) after completing features

DOCUMENTATION:
- Link to any existing specs, API docs, or design documents
- List key environment variables needed

Scan the current codebase to auto-populate as much of this as possible.
```

---

## Phase 2: Define Your Agent Roles

### 2A. Create Agent Definition Files

```
Create an .claude/agents/ directory with markdown files defining each specialist agent for this project. Each file should include: role name, description, model recommendation, responsibilities, what they are NOT responsible for, constraints, success criteria, output format, and failure modes to avoid.

Create these agents:

1. **architect** (opus, READ-ONLY)
   - Analyzes code, diagnoses bugs, provides architectural guidance
   - Every finding must cite a specific file:line reference
   - Cannot write or edit files — analysis only
   - Hands off to: planner (for plans), executor (for implementation)

2. **planner** (opus, READ-ONLY)
   - Breaks down features into ordered implementation tasks
   - Identifies dependencies between tasks
   - Assigns file ownership per task to prevent merge conflicts
   - Outputs a numbered task list with acceptance criteria per task

3. **frontend** (sonnet)
   - Owns all UI components, styling, state management, and client-side routing
   - Must match existing component patterns and design system
   - Runs the dev server and visually verifies changes

4. **backend** (sonnet)
   - Owns API endpoints, database migrations, business logic, and server config
   - Must write or update integration tests for every endpoint change
   - Runs the test suite after every change

5. **tester** (sonnet)
   - Writes unit tests, integration tests, and end-to-end tests
   - Reviews test coverage gaps
   - Never modifies production code — only test files
   - Reports failures with exact reproduction steps

6. **reviewer** (opus, READ-ONLY)
   - Reviews all changes for correctness, style, security, and performance
   - Checks for: unused imports, dead code, missing error handling, race conditions
   - Cannot approve its own work — must review OTHER agents' output
   - Outputs a structured review: approved / changes-requested with specific file:line feedback

7. **docs** (haiku)
   - Updates README, SPECIFICATIONS, API docs, and inline comments
   - Ensures no sensitive or account-specific info leaks into docs
   - Runs after implementation is complete

For each agent, include a <Failure_Modes_To_Avoid> section listing the 3-5 most common mistakes for that role.
```

---

## Phase 3: Issue & Specification Workflow

### 3A. Create a Feature Issue

```
Create documentation for a GitHub issue for this project. This issue will be assigned to a Claude Code agent team.
Write the issue as a markdown file under tmp/issues/ and name it: ###-issue-name.md (where ### is the issue number).

Structure:
- **Overview**: What should be completed (2-3 sentences)
- **Context**: Why this matters, what problem it solves, any relevant background
- **Requirements**: Prefix each with "R#: <requirement-name>" and list expected behaviors as sub-bullets
- **Implementation Notes**: (optional) Suggested approach, files likely affected, patterns to follow
- **Acceptance Criteria**: Testable conditions that prove each requirement is met
- **Out of Scope**: Explicitly list what this issue does NOT cover

FEATURE:
[Describe your feature here — e.g., "Add user authentication with JWT tokens, login/register pages, and protected route middleware"]
```

### 3B. Refine an Issue with Requirements Analysis

```
Read the issue at tmp/issues/###-issue-name.md and act as a requirements analyst:

1. Identify any ambiguous requirements and list specific clarifying questions
2. Check for missing edge cases or error scenarios
3. Verify the requirements are testable and have clear acceptance criteria
4. Flag any requirements that conflict with the existing codebase architecture
5. Suggest a dependency order for implementation
6. Estimate complexity: trivial / scoped / complex for each requirement

Update the issue file with your analysis appended as a "## Analysis" section.
```

---

## Phase 4: Launch an Agent Team

### 4A. Full Feature Implementation Team

This is the main prompt you'll use repeatedly.

```
Create an agent team to work on this GitHub issue: [paste issue URL or path to tmp/issues/###-issue-name.md]

Team structure:
- Team Lead: reads the issue, creates the task list, assigns work, coordinates dependencies, synthesizes results
- Backend Agent: implements server-side requirements (API, database, business logic)
- Frontend Agent: implements client-side requirements (UI, components, state)
- Test Agent: writes tests for each requirement as it's completed

Rules:
1. Create a feature branch: git checkout -b ###-issue-name
2. Each agent owns specific files — no two agents edit the same file
3. After implementation, run the FULL test suite and fix any regressions
4. Update SPECIFICATIONS.md with design decisions
5. Update README.md with implementation details (no sensitive info)
6. When all requirements pass acceptance criteria, prepare a PR description but do NOT submit until I review

Start by having the team lead break down the issue into tasks with clear file ownership, then coordinate parallel execution.
```

### 4B. Lightweight 2-Agent Team (Smaller Features)

```
Create a small agent team for this task:
[Describe the task]

Team: one implementation agent and one review agent.
- Implementer: make the changes, run tests, verify with lsp_diagnostics
- Reviewer: review the diff after implementation, check for edge cases, style, and correctness

Use a single worktree. Keep it fast.
```

### 4C. Research & Investigation Team

```
Create an agent team to investigate: [describe the problem or question]

Team:
- Explorer 1: investigate [angle A — e.g., "the database query performance"]
- Explorer 2: investigate [angle B — e.g., "the frontend rendering bottleneck"]  
- Explorer 3: investigate [angle C — e.g., "the network request waterfall"]

Each explorer should:
1. Gather evidence with specific file:line references
2. Form a hypothesis
3. Test the hypothesis against the code
4. Report findings with confidence level (high/medium/low)

Team lead: synthesize all findings into a single diagnosis with recommended next steps. Do NOT implement fixes — just report.
```

### 4D. Debugging Team

```
Create an agent team to debug this issue: [describe the bug, paste error messages]

Team:
- Hypothesis A agent: investigate [theory 1 — e.g., "race condition in auth middleware"]
- Hypothesis B agent: investigate [theory 2 — e.g., "stale cache returning old data"]
- Hypothesis C agent: investigate [theory 3 — e.g., "database connection pool exhaustion"]

Each agent: trace the code path, check git blame for recent changes, find the root cause (not symptoms), cite file:line for every claim.

Team lead: compare findings, identify the actual root cause, and propose the minimal fix. Do NOT implement until I confirm.
```

---

## Phase 5: Parallel Multi-Feature Development

### 5A. Launch Multiple Teams on Separate Branches

```
I have 3 issues to work on in parallel. Create separate agent teams, each in its own worktree:

Issue 1: [issue URL or description] → worktree: .claude/worktrees/###-feature-a
Issue 2: [issue URL or description] → worktree: .claude/worktrees/###-feature-b  
Issue 3: [issue URL or description] → worktree: .claude/worktrees/###-feature-c

Rules for parallel work:
- Each team works ONLY in its own worktree
- Minimize overlap in files modified across teams
- Each team runs tests only within its worktree
- When a team finishes, prepare a PR but do not merge

I will review and merge sequentially, rebasing as needed.
```

### 5B. Rebase and Resolve Conflicts

```
Feature branch ###-feature-b needs to be rebased onto main after ###-feature-a was merged.

1. git fetch origin main
2. git rebase origin/main
3. Resolve any merge conflicts — prefer the main branch version for structural changes, preserve this branch's feature additions
4. Run the full test suite after rebase
5. Fix any regressions introduced by the rebase
6. Show me the final diff for review
```

---

## Phase 6: Review & Quality Gates

### 6A. Code Review Pass

```
Review all changes on the current branch compared to main.

Check for:
- Correctness: Does the code do what the requirements specify?
- Edge cases: Missing null checks, empty arrays, error handling?
- Security: SQL injection, XSS, auth bypass, secrets in code?
- Performance: N+1 queries, unnecessary re-renders, missing indexes?
- Style: Does it match existing codebase patterns?
- Tests: Is every requirement covered by at least one test?
- Dead code: Unused imports, unreachable branches, leftover debug logs?

Output a structured review:
APPROVED / CHANGES REQUESTED
- [file:line] [severity: critical/warning/nit] [description]
```

### 6B. Pre-Merge Checklist

```
Run the full pre-merge quality gate:

1. Run all tests — report pass/fail count
2. Run type checking — report error count
3. Run linter — report warning/error count
4. Check for any TODO/FIXME/HACK/console.log in changed files
5. Verify all acceptance criteria from the issue are met
6. Verify documentation is updated
7. Generate a PR description summarizing: what changed, why, how to test, any breaking changes

Report: READY TO MERGE or BLOCKED (with specific items to fix).
```

---

## Phase 7: Post-Implementation

### 7A. Update Documentation

```
Update all project documentation after completing this feature:

1. SPECIFICATIONS.md — add design decisions, data models, API contracts
2. README.md — update setup instructions, feature list, architecture diagram (no secrets)
3. Any relevant API docs or changelog entries
4. Add inline code comments for any non-obvious logic

Commit documentation updates separately from code changes.
```

### 7B. Generate a Skill from This Session

```
Review the work we just completed and extract reusable patterns as a Claude Code skill.

Create a skill file at .claude/skills/[skill-name].md that captures:
- The workflow pattern (what steps we followed)
- Common pitfalls we encountered and how we solved them
- Prompt templates that worked well
- Codebase-specific conventions that future agents should know

This skill should help future agents working on similar features in this codebase.
```

### 7C. Retrospective

```
Analyze the agent team session that just completed:

1. What went well? (tasks completed smoothly, good parallel execution)
2. What went poorly? (merge conflicts, agents stepping on each other, wrong assumptions)
3. What was the bottleneck? (my review time, inter-agent coordination, unclear requirements)
4. How could the team structure be improved for next time?
5. Were there any tasks that should have been sequential instead of parallel?
6. Suggest updates to CLAUDE.md or agent definitions based on lessons learned.
```

---

## Quick Reference: Model Routing

| Role | Model | Why |
|------|-------|-----|
| Architect / Planner / Reviewer | Opus | Deep reasoning, read-only analysis |
| Frontend / Backend / Executor | Sonnet | Fast, capable implementation |
| Docs / Quick lookups / Triage | Haiku | Speed and cost efficiency |

---

## Quick Reference: When to Use What

| Situation | Approach |
|-----------|----------|
| Simple bug fix or small change | Single Claude Code session |
| Feature with 3-6 requirements | 2-3 agent team (impl + test + review) |
| Large feature spanning frontend + backend | Full agent team with file ownership |
| Multiple independent features | Parallel worktrees, separate teams |
| Debugging with unclear root cause | Investigation team with competing hypotheses |
| Codebase exploration / architecture review | Research team, all read-only |

---

## Tips from the Community

- **Write prompts in your IDE first**, then paste into Claude Code. The friction forces better thinking, and you keep a log.
- **Save your prompts** in files like `prompts/issue_###.md` — they become reusable templates.
- **Limit teams to 3-5 agents.** More agents = more coordination overhead and token burn.
- **Give every agent full context.** They don't retain history — spell out everything in the prompt.
- **Keep file ownership non-overlapping.** Two agents editing the same file = merge conflict hell.
- **Use `--dangerously-skip-permissions` sparingly.** Better to build up your `.permissions.allow[]` list explicitly.
- **After every merged feature, update CLAUDE.md.** Your agents are only as good as their shared context.
