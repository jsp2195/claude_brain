# Skill: Slide Decks and Talk Scripts

Covers converting technical work into clean presentations, concise speaker notes, and high-level framing for mixed audiences.

## Core Principle

A talk is a structured argument, not a document read aloud. Each slide should advance exactly one idea. The audience should always know where they are in the logic and why the current point matters.

## Slide Structure

**Opening (1–2 slides)**: State the problem and why it matters. No generic motivation slides. Get to the point.

**Setup (2–3 slides)**: What is the gap in current approaches? What makes this problem hard? Establish just enough context for the audience to understand why your approach is needed.

**Method (3–5 slides)**: What did you build or do? Architecture, key design choices, and the reasoning behind them. Diagrams over text. One idea per slide.

**Results (2–4 slides)**: What did you find? Lead with the main insight, not the experiment index. Figures should be self-explanatory with clear labels and captions.

**So what (1–2 slides)**: What does this mean? What does it enable? What is next? End with substance, not a generic "future work" list.

## Voice

- Concise, structured, direct.
- Speak to the logic, not to the audience's emotions.
- Technical precision for specialist talks. Accessible framing for mixed or leadership audiences (e.g., DLT presentations).
- No filler slides. No "outline" slides unless the talk is 30+ minutes.
- No hype language. Let the work speak.

## Speaker Notes

- Write as compressed talking points, not full sentences to be read.
- Each note should capture the *one thing* the speaker needs to convey on that slide.
- Flag transitions explicitly: "This motivates the next design choice..." or "Now we shift from representation to generation."
- For mixed audiences, note where to adjust depth or add a plain-language gloss.

## Formatting

- Prefer diagrams, figures, and equations over bullet-point text.
- If text is needed, keep it to 3–5 short lines per slide maximum.
- Titles should be assertions, not topics: "Graph autoencoder preserves local topology" not "Graph autoencoder results."
- Consistent notation throughout. Define symbols on first use.

## Audience Calibration

- **Technical peers (conference, group meeting)**: Full depth. Notation, architecture details, ablations.
- **Adjacent fields (seminar, interdisciplinary talk)**: Lead with the physical problem. Explain the method in terms of what it does, not how it is implemented. Minimize notation.
- **Leadership / non-specialist (DLT, review panels)**: Lead with the mission context and the capability gap. Focus on what was achieved and what it enables. Minimal technical detail.

## Quality Checklist

- [ ] Each slide advances exactly one idea
- [ ] Opening states the problem within the first two slides
- [ ] Method slides explain design choices, not just list components
- [ ] Figures are self-explanatory with clear labels
- [ ] No filler slides or generic motivation
- [ ] Speaker notes are compressed and useful, not scripted paragraphs
- [ ] Audience calibration is appropriate for the setting
- [ ] No hype language
- [ ] Talk has a clear arc: problem → gap → method → result → implication
