# AGENTS.md – Multi-Agent Orchestration Contract

Top-level behavioral contract for the local multi-agent system. Read this before dispatching any agent team.

---

## Delegation Principles

1. **Delegate, don't inline.** If a task spans 2+ files or crosses domain boundaries, delegate to specialist agents instead of implementing in the orchestrator context.
2. **Minimum sufficient team.** Spawn the fewest agents that preserve quality. Trivial: 2. Scoped: 3–4. Complex: 4–5. Never exceed 5 unless 5+ disjoint file-ownership domains exist.
3. **Strict file ownership.** Every writable file is assigned to exactly one agent before edits begin. No shared files. If two tasks need the same file, merge ownership or serialize.
4. **Staged execution.** Explore → Plan → Execute → Verify → Fix → Report. Stages may be skipped only where the Task Classifier permits (Trivial skips Plan; Research skips Execute/Verify).

## Agent Roster

| Agent | Model | Mode | Purpose |
|-------|-------|------|---------|
| architect | opus | READ-ONLY | Structural diagnosis, root cause analysis, design guidance |
| planner | opus | READ-ONLY | Task decomposition, file ownership, dependency ordering |
| critic | opus | READ-ONLY | Challenge plans before expensive implementation |
| reviewer | opus | READ-ONLY | Code/document review with severity-tagged findings |
| security-reviewer | opus | READ-ONLY | Security-focused review for risky code paths |
| explorer | haiku | READ-ONLY | Fast codebase reconnaissance before implementation |
| backend | sonnet | WRITE | Python scripts, ML models, data pipelines, config |
| frontend | sonnet | WRITE | Documents, proposals, slides, human-facing content |
| tester | sonnet | WRITE (tests only) | Test authoring and coverage auditing |
| debugger | sonnet | WRITE | Root-cause bug tracing with 4-phase protocol |
| verifier | sonnet | READ-ONLY | Post-implementation verification with fresh evidence |
| docs | haiku | WRITE (docs only) | Documentation updates mirroring real state |

## When to Use Which Agent

- **Feature build**: explorer → planner → backend/frontend → verifier
- **Bug fix**: debugger → backend → verifier
- **Small change**: backend or frontend → verifier
- **Research**: explorer + optionally critic/architect
- **Review/audit**: reviewer + security-reviewer (conditional)
- **Complex/risky plan**: planner → critic → then proceed or revise

## Verification Expectations

- Verification is mandatory. Even for Trivial tasks.
- Verifier runs as a separate pass from implementation.
- Every VERIFIED claim requires fresh command output with exit status.
- "Should work," "looks fine," and "no errors" are not evidence.
- See `.claude/rules/verification-standard.md` for full standard.

## Context Compression

- At stage boundaries, write handoff files to `.claude/handoffs/`.
- Subagents return structured results per their agent definition's output format.
- Do not carry full exploration context into execution stages.
- On crash recovery, continue from handoff artifacts, not memory.
- See `.claude/rules/context-management.md` for full rules.

## Stop Conditions

- 3 failed fix attempts on the same issue → stop and report
- Ambiguous requirements with no resolution path → stop and ask
- Missing dependency blocking verification → stop and report
- Tests/build cannot run locally → state explicitly, downgrade confidence
- Scope creep detected → pause and reassess before continuing

## System Architecture

```
.claude/
├── agents/          # Agent role definitions (12 agents)
│                    # Each defines: role, responsibilities, constraints,
│                    # output format, failure modes
│
├── commands/        # Slash command entrypoints
│   ├── agentteam.md           # Full orchestrator (v3)
│   ├── agentteam-runtime.md   # Runtime efficiency policy
│   ├── agentteam-plan.md      # Stage 2 only
│   ├── agentteam-exec.md      # Stage 3 only
│   ├── agentteam-verify.md    # Stage 4 only
│   ├── agentteam-fix.md       # Stage 5 only
│   └── agentteam-review.md    # Standalone review
│
├── rules/           # Operational rules loaded by context
│   ├── coordinator-mandate.md  # Orchestrator behavior
│   ├── context-management.md   # Artifact-based recovery
│   ├── output-structure.md     # Standard output schemas
│   ├── anti-sycophancy.md      # Evaluation integrity
│   ├── verification-standard.md # What counts as verified
│   └── path-scoped/            # Per-domain rules
│       ├── frontend.md
│       ├── backend.md
│       ├── tests.md
│       └── docs.md
│
├── skills/          # Thin reusable entrypoints
│   ├── agent-team-playbook.md
│   ├── agentteam/SKILL.md
│   ├── agentteam-verify/SKILL.md
│   ├── agentteam-debug/SKILL.md
│   └── agentteam-review/SKILL.md
│
├── state/           # File-based persistent state
│   ├── tasks/       # Task tracking
│   ├── reviews/     # Review persistence
│   ├── locks/       # File ownership locks
│   └── processes/   # Runtime notes
│
└── handoffs/        # Stage transition artifacts for crash recovery
```

### How the Pieces Connect

- **Agents** define what each specialist can do and how it reports results.
- **Commands** are entrypoints that dispatch agents through the staged pipeline.
- **Rules** are operational constraints loaded by the orchestrator and agents at runtime.
- **Skills** are thin wrappers that route to specific pipeline flows.
- **State** provides lightweight persistence for tasks, reviews, and file locks.
- **Handoffs** carry structured context between stages, enabling crash recovery.
