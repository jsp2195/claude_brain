# Skill: Code Editing and Technical Debugging

Covers modifying research code, diagnosing model behavior, improving implementation logic, and building research-grade scientific ML systems.

---

## Context

Jarett's codebases are research-grade scientific ML in Python / PyTorch. Projects involve graph autoencoders, diffusion models, physics-aware losses, constitutive modeling, and particle-based microstructure representations. The goal is never just "working code" but technically coherent, research-grade systems where the implementation faithfully reflects the intended method.

## Principles

1. **Understand the method before touching the code.** Ask what the code is supposed to do mechanistically before proposing fixes. A syntactically correct change that breaks the intended physics or conditioning logic is worse than a bug.
2. **Diagnose before fixing.** When debugging, first identify what is actually going wrong and why, then propose a fix. Do not shotgun solutions.
3. **Surgical edits over rewrites.** Change what needs changing. Do not refactor, rename, or reorganize code that is not broken or requested.
4. **Keep the research logic visible.** Code should read so that the modeling decisions — loss terms, graph construction, conditioning mechanisms, parameterization choices — are traceable and inspectable. Avoid abstracting away the science.
5. **Modularity matters.** Functions and modules should have clear responsibilities. But do not over-engineer — this is research code, not production software.
6. **Never pretend code works.** If a proposed implementation has not been fully reasoned through, say so. Flag assumptions, edge cases, and untested paths explicitly.

## Output Format

- Fully runnable Python unless otherwise specified.
- Include brief inline comments where the logic is non-obvious, especially for loss terms, conditioning steps, and physics-related operations.
- When editing existing code, show only the changed sections with enough surrounding context to locate the edit. Do not reprint the entire file unless asked.
- When proposing architectural changes, explain the reasoning before showing code.

## Common Task Patterns

**"This model isn't conditioning properly"**
Diagnose the conditioning pathway. Check whether the conditioning signal is actually reaching the relevant layers, whether it is being diluted, and whether the loss incentivizes the model to use it. Propose targeted fixes.

**"The generated outputs have overlapping particles / bad geometry"**
Check overlap penalty terms, parameterization (e.g., rot6d, radii), and generation postprocessing. Distinguish between training-time and inference-time issues.

**"Help me implement [loss / layer / module]"**
Confirm the mathematical formulation first, then implement. Keep tensor shapes explicit. Document what each term does.

**"Review this code for bugs or logic issues"**
Read for correctness of the research logic, not just syntax. Flag silent failures (e.g., broadcasting that works but does the wrong thing).

## Don't

- Refactor or rename things that weren't asked about.
- Add unnecessary abstraction layers.
- Use idioms or patterns that obscure what the model is doing scientifically.
- Suggest libraries or tools without confirming they fit the existing stack.
- Produce code that looks clean but has not been reasoned through for correctness.

## Quality Checklist

- [ ] The fix addresses the actual diagnosed problem, not a guess.
- [ ] Tensor shapes are consistent and documented where non-obvious.
- [ ] The implementation matches the intended mathematical or physical formulation.
- [ ] No silent broadcasting or shape errors.
- [ ] Changes are minimal and targeted — no unnecessary refactoring.
- [ ] Assumptions and untested edge cases are flagged explicitly.
- [ ] The code is runnable as written (or clearly marked if pseudocode / partial).
