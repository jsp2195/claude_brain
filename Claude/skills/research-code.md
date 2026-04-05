# Skill: Research Code

Covers editing, debugging, diagnosing model behavior, and improving implementation logic in scientific ML codebases.

---

## Language and Stack

- Primary: Python, PyTorch
- Common context: graph neural networks, diffusion models, variational autoencoders, constitutive modeling, FEM/DEM interfaces
- Simulation tools that may come up: LAMMPS, PyUMAT

## Standards

- **Research-grade, not production-grade.** Code should be correct, readable, and modular — but the priority is scientific coherence over software engineering polish.
- **Modularity matters.** Functions and classes should have clear responsibilities. Avoid monolithic training loops or data pipelines that can't be inspected piece by piece.
- **Make the physics visible.** Loss terms, constraints, parameterizations (e.g., rot6d), and conditioning logic should be clearly separated and labeled so the scientific content is readable in the code.
- **Diagnostics over trust.** Build in visualization, logging, and intermediate checks. Never assume a model is working — verify it.
- **Comments where they carry information.** Don't narrate obvious code. Do explain non-obvious design choices, physics constraints, and parameter meanings.

## Process

1. When debugging: diagnose before fixing. State what the expected behavior is, what the actual behavior is, and where the divergence likely originates — before proposing changes.
2. When editing: make targeted changes. Do not refactor unrelated code unless asked.
3. When writing new code: produce a complete, runnable first pass. Structure it so components can be tested and inspected independently.
4. When reviewing model behavior: check conditioning, loss landscape, gradient flow, reconstruction quality, and latent structure before concluding the architecture is the problem.

## Common Tasks

- Debugging graph-based generative models (VGAE, GraphRNN-style, diffusion)
- Diagnosing conditioning behavior (is the model actually using the conditioning input?)
- Overlap penalties, packing constraints, geometric realism checks
- Loss design: physics-aware terms, reconstruction losses, KL terms, regularizers
- Parameterization choices: rot6d, particle descriptors, graph encodings
- Data pipeline issues: sparse/heterogeneous data, CT-derived inputs, segmentation artifacts

## Quality Checklist

- [ ] Code runs without error on the stated inputs
- [ ] Scientific logic is visible and separated from boilerplate
- [ ] No silent assumptions smuggled into default parameters
- [ ] Diagnostic hooks exist (logging, visualization, intermediate outputs)
- [ ] Changes are targeted — unrelated code is untouched
- [ ] Any new function or class has a clear, single responsibility
- [ ] Physics constraints and loss terms are labeled and interpretable
- [ ] If uncertainty exists about correctness, it is flagged explicitly
