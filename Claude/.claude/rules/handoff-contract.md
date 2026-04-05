# Handoff Contract

Every stage handoff must fit this schema.

## Required fields

- `objective`: one sentence
- `scope_in`: what is included
- `scope_out`: what is excluded
- `owned_files`: explicit file list
- `changes`: concise diff summary
- `evidence`: command outputs or file references
- `open_risks`: unresolved concerns
- `next_action`: exact next step

Keep handoffs concise: maximum ~200 tokens unless user requested detail.
