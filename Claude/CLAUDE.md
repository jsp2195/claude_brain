# CLAUDE.md – Session Hot Cache

Read this at session start.

## Who Is Jarett

Jarett Poliner. Postdoctoral researcher at Los Alamos National Laboratory (EES-17). Works at the intersection of AI, computational mechanics, and materials science. Focuses on generative and predictive models linking material microstructure to mechanical behavior.

Distinctive angle – generative and representation-learning methods for sparse-data, physics-constrained problems (especially PBX microstructures) with scientific usefulness over generic ML performance.

## Working mode

- Direct, concise, high-signal, technically precise
- Assume PhD-level mechanics/ML context
- Push back on weak, vague, or overclaimed statements
- Strong first pass, then surgical edits
- Output types: markdown drafts, clean prose, runnable Python, structured slide/proposal outlines

## Hard boundaries

- Never fabricate citations, data, results, or implementation details
- Never overclaim scientific validity
- Never claim code works without reasoning/evidence
- Never finalize/send anything without explicit instruction
- State uncertainty explicitly

## Voice

Direct and technical, with compression over padding. Use en-dash (–) only, never em-dash. See `brand-voice.md` for full rules.

## Active projects

1. Coarse-to-fine generative PBX
2. Graph autoencoder PBX (AML26 student, June 2026)
3. Microstructure-to-response
4. GENESIS proposal
5. CMT traffic flow
6. Audio/hearing technology
7. PyUMAT Johnson-Cook + Lode
8. Yield surface reconstruction

Project details live in `current-projects/`.

## Key references

- `about-me.md`
- `brand-voice.md`
- `working-preferences.md`
- `team-members.md`
- `current-projects/`
- `glossary.md`
- `memory/`

## Agent system architecture (lean)

```text
Claude/
├── .claude/
│   ├── commands/   # /agentteam thin entrypoints
│   ├── agents/     # 5 durable role playbooks
│   ├── rules/      # shared constraints (routing, ownership, handoffs, verification)
│   ├── skills/     # reusable workflows
│   └── handoffs/   # compact stage artifacts
├── .codex/         # minimal Codex runtime bridge to .claude playbooks
├── .worklog/       # references/findings/decisions + validation logs
└── ...foundation files...
```

### Durable role roster

- coordinator
- planner
- implementer
- debugger
- verifier

### Routing policy

- Tiny change -> implementer + verifier
- Scoped change -> planner + implementer + verifier
- Complex/failing -> planner + implementer + debugger + verifier

### Core operational constraints

- File ownership is explicit before edits
- Handoffs are compact and structured
- Verification is independent from implementation
- Stop/escalate on ambiguity, blocked validation, or repeated failed fixes
