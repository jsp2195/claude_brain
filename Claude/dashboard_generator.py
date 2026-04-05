"""
dashboard_generator.py

Reads all project markdown files from current-projects/ and generates
a single self-contained HTML status dashboard at dashboard.html.

Parsing assumptions:
  - Each file uses H2 sections (## Section Name) as the primary structure.
  - Recognized sections: Overview, Status, Key Goals, Deadlines, People.
  - Bullet list items under a section are collected as a list of strings.
  - Prose paragraphs under a section are collected as a single string.
  - Missing sections are represented as empty strings or empty lists.
  - The project name is taken from the H1 title (first # line).
  - Files with no H1 title fall back to the filename stem.
"""

import os
import re
import sys
from datetime import date
from pathlib import Path


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------


def parse_project_markdown(file_path: Path) -> dict:
    """
    Parse a project markdown file into a structured dict with keys:
      project_name, overview, status, key_goals (list), deadlines, people (list)
    """
    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"Could not read project file '{file_path}': {exc}"
        ) from exc

    lines = raw_text.splitlines()

    project_name = _extract_h1_title(lines, fallback=file_path.stem)
    sections = _split_into_sections(lines)

    return {
        "project_name": project_name,
        "overview": _section_as_prose(sections.get("Overview", [])),
        "status": _section_as_prose(sections.get("Status", [])),
        "key_goals": _section_as_bullets(sections.get("Key Goals", [])),
        "deadlines": _section_as_prose(sections.get("Deadlines", [])),
        "people": _section_as_bullets(sections.get("People", [])),
        "source_file": file_path.name,
    }


def _extract_h1_title(lines: list[str], fallback: str) -> str:
    for line in lines:
        match = re.match(r"^#\s+(.+)$", line)
        if match:
            return match.group(1).strip()
    return fallback


def _split_into_sections(lines: list[str]) -> dict:
    """
    Walk the lines and collect content under each H2 heading.
    Returns {section_name: [content_lines]}.
    """
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in lines:
        h2_match = re.match(r"^##\s+(.+)$", line)
        if h2_match:
            section_title = h2_match.group(1).strip()
            current_section = section_title
            sections[current_section] = []
        elif current_section is not None:
            sections[current_section].append(line)

    return sections


def _section_as_prose(section_lines: list[str]) -> str:
    """
    Join non-empty, non-bullet lines into a single prose string.
    Bullet lines (starting with - or *) are included as sentence fragments.
    """
    parts = []
    for line in section_lines:
        stripped = line.strip()
        if stripped and not re.match(r"^#{1,6}\s", stripped):
            parts.append(stripped)
    return " ".join(parts)


def _section_as_bullets(section_lines: list[str]) -> list[str]:
    """
    Extract bullet-list items. Falls back to splitting comma-separated
    prose if no bullet markers are found (used for People sections
    that are written as plain prose).
    """
    bullets = []
    prose_lines = []

    for line in section_lines:
        stripped = line.strip()
        if not stripped:
            continue
        bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet_match:
            bullets.append(bullet_match.group(1).strip())
        else:
            prose_lines.append(stripped)

    if bullets:
        return bullets

    # People section uses comma-separated prose; split on commas
    combined = " ".join(prose_lines)
    if combined:
        items = [p.strip() for p in combined.split(",") if p.strip()]
        return [p for p in items if len(p) <= 50 and not p.lower().startswith("with")]
    return []


# ---------------------------------------------------------------------------
# Status classification for visual styling
# ---------------------------------------------------------------------------

STATUS_CLASS_MAP = {
    "active": "status-active",
    "early": "status-early",
    "exploratory": "status-exploratory",
    "proposal": "status-proposal",
}


def classify_status(status_text: str) -> str:
    """
    Map free-text status to a CSS class for color-coding.
    Uses keyword matching on lowercase status text.
    """
    lower = status_text.lower()
    if "early" in lower:
        return STATUS_CLASS_MAP["early"]
    if "exploratory" in lower:
        return STATUS_CLASS_MAP["exploratory"]
    if "proposal" in lower:
        return STATUS_CLASS_MAP["proposal"]
    if "active" in lower:
        return STATUS_CLASS_MAP["active"]
    return "status-unknown"


# ---------------------------------------------------------------------------
# Domain grouping
# ---------------------------------------------------------------------------

DOMAIN_ORDER = [
    "PBX / Materials Modeling",
    "Constitutive Mechanics",
    "Proposal Work",
    "Applied / External",
]

DOMAIN_ASSIGNMENT = {
    "coarse-to-fine-generative-pbx.md": "PBX / Materials Modeling",
    "graph-autoencoder-pbx.md": "PBX / Materials Modeling",
    "microstructure-to-response.md": "PBX / Materials Modeling",
    "pyumat-johnson-cook-lode.md": "Constitutive Mechanics",
    "yield-surface-reconstruction.md": "Constitutive Mechanics",
    "genesis-proposal.md": "Proposal Work",
    "cmt-traffic-flow.md": "Applied / External",
    "audio-hearing-technology.md": "Applied / External",
}


def assign_domain(source_file: str) -> str:
    return DOMAIN_ASSIGNMENT.get(source_file, "Other")


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

CSS = """
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    background: #f4f5f7;
    color: #1a1a2e;
    padding: 2rem 1.5rem;
    font-size: 15px;
    line-height: 1.55;
}
header {
    max-width: 1200px;
    margin: 0 auto 2.5rem auto;
    border-bottom: 2px solid #1a1a2e;
    padding-bottom: 1rem;
}
header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.01em;
}
header .subtitle {
    font-size: 0.9rem;
    color: #555;
    margin-top: 0.3rem;
}
.domain-section {
    max-width: 1200px;
    margin: 0 auto 3rem auto;
}
.domain-section h2 {
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #555;
    margin-bottom: 1rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid #ccc;
}
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.2rem;
}
.project-card {
    background: #fff;
    border-radius: 6px;
    padding: 1.4rem 1.5rem;
    border: 1px solid #dde1e7;
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.6rem;
}
.card-header h3 {
    font-size: 0.95rem;
    font-weight: 700;
    line-height: 1.3;
}
.status-badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.25rem 0.55rem;
    border-radius: 3px;
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    flex-shrink: 0;
}
.status-active    { background: #d4edda; color: #155724; }
.status-early     { background: #fff3cd; color: #856404; }
.status-exploratory { background: #d1ecf1; color: #0c5460; }
.status-proposal  { background: #e2d9f3; color: #4a235a; }
.status-unknown   { background: #e9ecef; color: #495057; }

.card-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #888;
    margin-bottom: 0.3rem;
}
.card-prose {
    font-size: 0.85rem;
    color: #333;
}
.card-prose.muted {
    color: #777;
    font-style: italic;
}
.goals-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
}
.goals-list li {
    font-size: 0.83rem;
    color: #333;
    padding-left: 1rem;
    position: relative;
}
.goals-list li::before {
    content: "–";
    position: absolute;
    left: 0;
    color: #aaa;
}
.people-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}
.person-tag {
    font-size: 0.72rem;
    background: #eef0f4;
    color: #444;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    font-weight: 500;
}
.deadline-text {
    font-size: 0.83rem;
    color: #7a4800;
    background: #fff8ed;
    padding: 0.4rem 0.6rem;
    border-radius: 4px;
    border-left: 3px solid #f0a030;
}
.deadline-text.none {
    background: none;
    border: none;
    color: #aaa;
    font-style: italic;
    padding: 0;
}
footer {
    max-width: 1200px;
    margin: 3rem auto 0 auto;
    padding-top: 1rem;
    border-top: 1px solid #ccc;
    font-size: 0.78rem;
    color: #888;
}
"""


def _html_escape(text: str) -> str:
    # Normalize em-dashes from source markdown to en-dashes before escaping.
    # The source project files may contain em-dashes authored previously;
    # the generated dashboard uses en-dashes throughout.
    return (
        text.replace("\u2014", "\u2013")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def _has_hard_deadline(deadline_text: str) -> bool:
    """
    Returns True only when deadline text signals a concrete upcoming date.
    Phrases like 'no fixed' or 'no single' are treated as soft.
    """
    lower = deadline_text.lower()
    soft_indicators = ["no fixed", "no single", "no hard", "proposal-cycle"]
    return not any(phrase in lower for phrase in soft_indicators)


def render_project_card(project: dict) -> str:
    name_escaped = _html_escape(project["project_name"])
    status_text = project["status"] or "Unknown"
    status_class = classify_status(status_text)

    # Derive a compact status label from the first meaningful phrase
    status_label = _derive_status_label(status_text)

    overview_escaped = _html_escape(project["overview"] or "No overview provided.")
    overview_class = "card-prose" if project["overview"] else "card-prose muted"

    goals_html = _render_goals(project["key_goals"])
    people_html = _render_people(project["people"])
    deadline_html = _render_deadline(project["deadlines"])

    return f"""
    <div class="project-card">
        <div class="card-header">
            <h3>{name_escaped}</h3>
            <span class="status-badge {status_class}">{_html_escape(status_label)}</span>
        </div>
        <div>
            <div class="card-section-label">Overview</div>
            <p class="{overview_class}">{overview_escaped}</p>
        </div>
        {goals_html}
        {deadline_html}
        {people_html}
    </div>"""


def _derive_status_label(status_text: str) -> str:
    lower = status_text.lower()
    if "early" in lower:
        return "Early Stage"
    if "exploratory" in lower:
        return "Exploratory"
    if "proposal" in lower:
        return "Proposal"
    if "active" in lower:
        return "Active"
    return "Unknown"


def _render_goals(goals: list[str]) -> str:
    if not goals:
        return ""
    items = "\n".join(
        f'            <li>{_html_escape(goal)}</li>' for goal in goals
    )
    return f"""
        <div>
            <div class="card-section-label">Current Focus</div>
            <ul class="goals-list">
{items}
            </ul>
        </div>"""


def _render_people(people: list[str]) -> str:
    if not people:
        return ""
    tags = "\n".join(
        f'            <span class="person-tag">{_html_escape(p)}</span>'
        for p in people
    )
    return f"""
        <div>
            <div class="card-section-label">Team</div>
            <div class="people-list">
{tags}
            </div>
        </div>"""


def _render_deadline(deadline_text: str) -> str:
    if not deadline_text:
        return ""
    has_hard = _has_hard_deadline(deadline_text)
    css_class = "deadline-text" if has_hard else "deadline-text none"
    return f"""
        <div>
            <div class="card-section-label">Deadlines</div>
            <div class="{css_class}">{_html_escape(deadline_text)}</div>
        </div>"""


def render_domain_section(domain_name: str, projects: list[dict]) -> str:
    cards_html = "\n".join(render_project_card(p) for p in projects)
    return f"""
    <section class="domain-section">
        <h2>{_html_escape(domain_name)}</h2>
        <div class="card-grid">
{cards_html}
        </div>
    </section>"""


def render_html(all_projects: list[dict], generated_on: str) -> str:
    # Group by domain, preserving DOMAIN_ORDER
    domain_map: dict[str, list[dict]] = {d: [] for d in DOMAIN_ORDER}
    for project in all_projects:
        domain = assign_domain(project["source_file"])
        if domain not in domain_map:
            domain_map[domain] = []
        domain_map[domain].append(project)

    sections_html = ""
    for domain in DOMAIN_ORDER:
        projects_in_domain = domain_map.get(domain, [])
        if projects_in_domain:
            sections_html += render_domain_section(domain, projects_in_domain)

    project_count = len(all_projects)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Project Dashboard</title>
    <style>
{CSS}
    </style>
</head>
<body>
    <header>
        <h1>Research Project Dashboard</h1>
        <div class="subtitle">
            {project_count} projects &ndash; generated {_html_escape(generated_on)}
        </div>
    </header>
{sections_html}
    <footer>
        Generated from <code>current-projects/*.md</code>
        &ndash; Jarett Poliner, EES-17, Los Alamos National Laboratory
    </footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    workspace_root = Path(__file__).parent.resolve()
    projects_dir = workspace_root / "current-projects"
    output_path = workspace_root / "dashboard.html"

    if not projects_dir.is_dir():
        sys.exit(
            f"Error: expected directory '{projects_dir}' does not exist. "
            "Run this script from the workspace root or ensure current-projects/ is present."
        )

    md_files = sorted(projects_dir.glob("*.md"))
    if not md_files:
        sys.exit(f"Error: no markdown files found in '{projects_dir}'.")

    all_projects = []
    for md_file in md_files:
        project_data = parse_project_markdown(md_file)
        all_projects.append(project_data)

    generated_on = date.today().isoformat()
    html_content = render_html(all_projects, generated_on)

    try:
        output_path.write_text(html_content, encoding="utf-8")
    except OSError as exc:
        sys.exit(f"Error: could not write dashboard to '{output_path}': {exc}")

    print(f"Dashboard written to: {output_path}")
    print(f"Projects parsed: {len(all_projects)}")
    for project in all_projects:
        print(f"  {project['source_file']:45s}  ->  {project['project_name']}")


if __name__ == "__main__":
    main()
