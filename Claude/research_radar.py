"""
research_radar.py

Reads all project files from current-projects/, queries the Semantic Scholar API
for recent papers (2024-2026), and generates a self-contained interactive HTML
visualization at research_radar.html.

No third-party dependencies. Stdlib only.
"""

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECTS_DIR = Path("/home/jarettpoliner/Desktop/Claude/current-projects")
OUTPUT_PATH = Path("/home/jarettpoliner/Desktop/Claude/research_radar.html")
SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
PAPER_FIELDS = "paperId,title,authors,year,abstract,citationCount,externalIds,publicationTypes"
MIN_YEAR = 2024
MAX_YEAR = 2026
PAPERS_PER_PROJECT = 15
API_SLEEP_SECONDS = 3.0
API_MAX_RETRIES = 3
API_RETRY_BACKOFF_BASE = 8.0  # seconds; multiplied by attempt number on 429
ABSTRACT_SNIPPET_LENGTH = 300
MAX_AUTHORS_BEFORE_ETAL = 4


# ---------------------------------------------------------------------------
# Domain classification
# ---------------------------------------------------------------------------

DOMAIN_KEYWORD_MAP = {
    "ml": [
        "machine learning", "generative model", "graph neural network", "autoencoder",
        "diffusion model", "deep learning", "neural network", "latent space",
        "variational", "representation learning", "transformer", "attention",
        "encoder", "decoder", "gnn", "graph autoencoder", "denoising",
        "score matching", "flow matching", "inference", "probabilistic",
        "audio", "signal processing", "hearing", "acoustic",
        "multi-agent", "reinforcement learning", "traffic",
    ],
    "mechanics": [
        "constitutive", "plasticity", "johnson-cook", "yield surface", "lode angle",
        "stress update", "finite element", "continuum mechanics", "damage model",
        "failure", "fracture", "hyperelastic", "viscoelastic", "creep",
        "hardening", "flow rule", "drucker", "von mises", "drucker-prager",
        "return mapping", "stress integration", "material model",
        "rate-dependent", "viscoplastic",
    ],
    "materials": [
        "pbx", "polymer-bonded explosive", "microstructure", "grain", "particle assembly",
        "heterogeneous material", "energetic material", "explosive", "rdx", "hmx",
        "composite", "binder", "packing", "morphology", "segmentation", "ct scan",
        "micro-ct", "granular", "polycrystal", "phase field", "representative volume",
    ],
}


def classify_domain(text: str) -> str:
    """Classify text into one of four domains based on keyword presence."""
    text_lower = text.lower()
    matched_domains = set()
    for domain, keywords in DOMAIN_KEYWORD_MAP.items():
        for keyword in keywords:
            if keyword in text_lower:
                matched_domains.add(domain)
                break
    if len(matched_domains) == 0:
        return "ml"  # default to ml if no match; projects are all ML-adjacent
    if len(matched_domains) == 1:
        return matched_domains.pop()
    return "multi"


# ---------------------------------------------------------------------------
# Phase 1: Parse project files
# ---------------------------------------------------------------------------

def extract_h1_title(text: str) -> str:
    """Extract the first H1 heading from markdown text."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return "Untitled Project"


def extract_section_text(text: str, section_header: str) -> str:
    """Extract text under a given ## section heading."""
    lines = text.splitlines()
    in_section = False
    collected = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == f"## {section_header.lower()}":
            in_section = True
            continue
        if in_section:
            if stripped.startswith("## "):
                break
            collected.append(line)
    return "\n".join(collected).strip()


def extract_bullet_items(section_text: str) -> list:
    """Extract bullet list items from a markdown section."""
    items = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def build_project_keywords(project_name: str, overview: str, goals_text: str) -> list:
    """
    Extract 5-8 search-worthy keywords/phrases from project content.
    Combines name-derived terms with technical terms found in text.
    """
    combined_text = f"{project_name} {overview} {goals_text}".lower()

    # Candidate technical phrases to scan for in the combined text
    candidate_phrases = [
        # ML / generative
        "graph autoencoder", "graph neural network", "diffusion model",
        "generative model", "variational autoencoder", "latent representation",
        "conditional generation", "denoising diffusion", "score-based generative",
        "representation learning", "encoder decoder", "graph convolutional",
        "message passing", "point cloud generation",
        # Materials / PBX
        "pbx microstructure", "polymer-bonded explosive", "particle assembly",
        "microstructure generation", "microstructure reconstruction",
        "energetic material microstructure", "ct segmentation",
        "heterogeneous microstructure", "granular packing",
        "explosive particle", "grain morphology",
        # Mechanics
        "constitutive model", "johnson-cook", "lode angle", "yield surface",
        "plasticity", "stress integration", "return mapping",
        "yield surface reconstruction", "data-driven constitutive",
        "physics-informed neural network", "material model",
        # Multi-modal
        "structure property relationship", "microstructure mechanical response",
        "uncertainty quantification", "multi-fidelity",
        # Traffic / audio
        "multi-agent traffic", "traffic flow", "agent-based model",
        "hearing augmentation", "audio signal processing",
        "machine learning hearing", "acoustic scene",
    ]

    found_phrases = []
    for phrase in candidate_phrases:
        if phrase in combined_text:
            found_phrases.append(phrase)

    # Supplement with project name tokens if needed
    name_tokens = [t for t in project_name.lower().split() if len(t) > 3]

    # Build final keyword list: found phrases first, then name tokens
    combined = found_phrases + [t for t in name_tokens if t not in " ".join(found_phrases)]
    # Deduplicate preserving order, limit to 8
    seen = set()
    result = []
    for kw in combined:
        if kw not in seen:
            seen.add(kw)
            result.append(kw)
        if len(result) >= 8:
            break

    # Ensure at least 5 entries by padding with name tokens
    if len(result) < 5:
        for token in name_tokens:
            if token not in seen and len(result) < 5:
                result.append(token)
                seen.add(token)

    return result[:8]


def make_short_name(project_name: str) -> str:
    """Produce a 3-4 word abbreviation of the project name."""
    # Remove common filler words
    filler = {"for", "of", "and", "the", "a", "an", "to", "in", "on", "with",
              "from", "by", "or", "at", "via", "--", "-"}
    words = [w for w in project_name.split() if w.lower() not in filler]
    return " ".join(words[:4])


# Hardcoded search queries per project file stem -- these are used when keyword
# extraction from the project text is too thin to produce useful queries.
# Keys match the filename stems in current-projects/.
PROJECT_QUERY_OVERRIDES: dict[str, list[str]] = {
    "audio-hearing-technology": [
        "machine learning hearing augmentation",
        "audio deep learning signal processing",
        "neural network acoustic hearing aid",
    ],
    "cmt-traffic-flow": [
        "multi-agent traffic flow simulation",
        "agent-based traffic modeling deep learning",
        "traffic flow prediction graph neural network",
    ],
    "coarse-to-fine-generative-pbx": [
        "diffusion model microstructure generation",
        "conditional generative model particle assembly",
        "generative model heterogeneous microstructure",
    ],
    "genesis-proposal": [
        "AI materials discovery uncertainty quantification",
        "multi-fidelity machine learning materials design",
        "generative model materials microstructure design",
    ],
    "graph-autoencoder-pbx": [
        "graph autoencoder microstructure representation",
        "graph neural network material latent space",
        "variational graph autoencoder molecular graph",
    ],
    "microstructure-to-response": [
        "microstructure mechanical response machine learning",
        "structure property prediction graph neural network",
        "physics-informed neural network constitutive model",
    ],
    "pyumat-johnson-cook-lode": [
        "Johnson-Cook plasticity Lode angle constitutive model",
        "constitutive model stress state dependence plasticity",
        "return mapping algorithm plasticity finite element",
    ],
    "yield-surface-reconstruction": [
        "yield surface reconstruction machine learning",
        "data-driven yield criterion plasticity",
        "neural network yield surface constitutive",
    ],
}


def build_search_queries(keywords: list, project_name: str, file_stem: str = "") -> list:
    """
    Construct 2-3 search query strings from the project keywords.
    Uses PROJECT_QUERY_OVERRIDES when available; falls back to keyword extraction.
    """
    if file_stem and file_stem in PROJECT_QUERY_OVERRIDES:
        return PROJECT_QUERY_OVERRIDES[file_stem]

    multi_word = [kw for kw in keywords if " " in kw]
    single_word = [kw for kw in keywords if " " not in kw]

    queries = []

    # Query 1: top 2-3 multi-word phrases joined
    if len(multi_word) >= 2:
        queries.append(" ".join(multi_word[:3]))
    elif len(multi_word) == 1:
        queries.append(f"{multi_word[0]} {' '.join(single_word[:2])}")
    else:
        queries.append(" ".join(single_word[:3]))

    # Query 2: different angle using other keywords
    if len(multi_word) >= 3:
        queries.append(" ".join(multi_word[1:4]))
    elif len(keywords) >= 4:
        remaining = [kw for kw in keywords if kw not in queries[0]]
        if remaining:
            queries.append(" ".join(remaining[:3]))

    # Query 3: project name itself (can surface overview papers)
    name_query = " ".join(project_name.lower().split()[:5])
    if name_query not in queries:
        queries.append(name_query)

    # Filter out empty or too-short queries, and drop single-word or vague terms
    filler_queries = {"project", "technology", "proposal"}
    queries = [
        q.strip() for q in queries
        if len(q.strip()) > 8 and q.strip().lower() not in filler_queries
    ]
    return queries[:3]


def parse_project_file(md_path: Path, project_index: int) -> dict:
    """Parse a single project .md file into a structured dict."""
    text = md_path.read_text(encoding="utf-8")
    file_stem = md_path.stem

    project_name = extract_h1_title(text)
    overview = extract_section_text(text, "Overview")
    goals_text = extract_section_text(text, "Key Goals")

    keywords = build_project_keywords(project_name, overview, goals_text)
    search_queries = build_search_queries(keywords, project_name, file_stem=file_stem)
    domain = classify_domain(f"{project_name} {overview} {goals_text}")

    return {
        "id": f"proj_{project_index}",
        "name": project_name,
        "short_name": make_short_name(project_name),
        "domain": domain,
        "overview": overview,
        "goals": extract_bullet_items(goals_text),
        "keywords": keywords,
        "search_queries": search_queries,
    }


def load_all_projects() -> list:
    """Load and parse all .md files from the current-projects directory."""
    md_files = sorted(PROJECTS_DIR.glob("*.md"))
    if not md_files:
        sys.stderr.write(f"ERROR: No .md files found in {PROJECTS_DIR}\n")
        sys.exit(1)

    projects = []
    for idx, md_path in enumerate(md_files):
        try:
            project = parse_project_file(md_path, idx)
            projects.append(project)
            sys.stderr.write(f"Parsed project: {project['name']}\n")
        except Exception as exc:
            sys.stderr.write(f"WARNING: Failed to parse {md_path.name}: {exc}\n")

    return projects


# ---------------------------------------------------------------------------
# Phase 2: Semantic Scholar API
# ---------------------------------------------------------------------------

def fetch_papers_for_query(query: str, project_id: str) -> list:
    """
    Query Semantic Scholar for papers matching query string.
    Retries with exponential backoff on HTTP 429.
    Returns a list of raw paper dicts from the API.
    """
    params = {
        "query": query,
        "fields": PAPER_FIELDS,
        "limit": 50,
        "year": f"{MIN_YEAR}-{MAX_YEAR}",
    }
    url = f"{SEMANTIC_SCHOLAR_BASE}?{urllib.parse.urlencode(params)}"

    for attempt in range(API_MAX_RETRIES):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "research-radar/1.0 (academic use)"},
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                raw = json.loads(response.read().decode("utf-8"))
            data = raw.get("data", [])
            if not data:
                sys.stderr.write(f"  No results for query: '{query}'\n")
            return data

        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                wait = API_RETRY_BACKOFF_BASE * (attempt + 1)
                sys.stderr.write(
                    f"  Rate-limited (429) on attempt {attempt + 1} for '{query}'. "
                    f"Waiting {wait:.0f}s before retry...\n"
                )
                time.sleep(wait)
                continue
            sys.stderr.write(
                f"WARNING: HTTP {exc.code} for query '{query}' (project {project_id}): {exc.reason}\n"
            )
            return []

        except urllib.error.URLError as exc:
            sys.stderr.write(
                f"WARNING: URL error for query '{query}' (project {project_id}): {exc.reason}\n"
            )
            return []

        except json.JSONDecodeError as exc:
            sys.stderr.write(
                f"WARNING: JSON decode error for query '{query}' (project {project_id}): {exc}\n"
            )
            return []

        except Exception as exc:
            sys.stderr.write(
                f"WARNING: Unexpected error for query '{query}' (project {project_id}): {exc}\n"
            )
            return []

    sys.stderr.write(
        f"WARNING: Exhausted {API_MAX_RETRIES} retries for query '{query}' (project {project_id}). Skipping.\n"
    )
    return []


def format_authors(authors_raw: list) -> list:
    """
    Convert author dicts to 'Last, F.' format.
    Truncates to MAX_AUTHORS_BEFORE_ETAL authors then appends 'et al.' if needed.
    """
    formatted = []
    for author in authors_raw[:MAX_AUTHORS_BEFORE_ETAL]:
        name = author.get("name", "")
        parts = name.strip().split()
        if len(parts) >= 2:
            last = parts[-1]
            first_initial = parts[0][0].upper() + "."
            formatted.append(f"{last}, {first_initial}")
        elif parts:
            formatted.append(parts[0])
    if len(authors_raw) > MAX_AUTHORS_BEFORE_ETAL:
        formatted.append("et al.")
    return formatted


def clean_text(text: str) -> str:
    """Replace em-dashes with en-dashes and strip excess whitespace."""
    if not text:
        return ""
    text = text.replace("\u2014", "\u2013")  # em-dash to en-dash
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_paper(raw_paper: dict, project_id: str) -> dict | None:
    """
    Normalize a raw Semantic Scholar paper dict.
    Returns None if the paper lacks required fields or fails year filter.
    """
    paper_id = raw_paper.get("paperId")
    title = clean_text(raw_paper.get("title", ""))
    abstract = clean_text(raw_paper.get("abstract", "") or "")
    year = raw_paper.get("year")
    citation_count = raw_paper.get("citationCount") or 0
    authors_raw = raw_paper.get("authors") or []

    if not paper_id:
        return None
    if not title:
        return None
    if not abstract:
        return None
    if year is None or year < MIN_YEAR or year > MAX_YEAR:
        return None

    return {
        "id": paper_id,
        "title": title,
        "authors": format_authors(authors_raw),
        "year": year,
        "abstract_snippet": abstract[:ABSTRACT_SNIPPET_LENGTH],
        "citation_count": citation_count,
        "url": f"https://www.semanticscholar.org/paper/{paper_id}",
        "domain": classify_domain(f"{title} {abstract}"),
        "connected_projects": [project_id],
        "is_bridge": False,
        "relevance_score": 0.0,
    }


def fetch_all_papers(projects: list) -> tuple[list, list]:
    """
    Fetch papers for all projects, deduplicate, and return
    (papers_list, links_list).
    """
    # paper_id -> paper dict (with connected_projects accumulating)
    papers_by_id: dict[str, dict] = {}
    # project_id -> list of paper_ids fetched for that project
    project_paper_ids: dict[str, list] = {p["id"]: [] for p in projects}

    for project in projects:
        project_id = project["id"]
        queries = project["search_queries"]
        sys.stderr.write(
            f"\nFetching papers for: {project['name']}\n"
            f"  Queries: {queries}\n"
        )

        raw_papers_for_project: dict[str, dict] = {}

        for query in queries:
            time.sleep(API_SLEEP_SECONDS)
            raw_results = fetch_papers_for_query(query, project_id)
            sys.stderr.write(f"  Query '{query}': {len(raw_results)} raw results\n")

            for raw_paper in raw_results:
                paper = normalize_paper(raw_paper, project_id)
                if paper is None:
                    continue
                pid = paper["id"]

                # Merge into global registry
                if pid in papers_by_id:
                    if project_id not in papers_by_id[pid]["connected_projects"]:
                        papers_by_id[pid]["connected_projects"].append(project_id)
                else:
                    papers_by_id[pid] = paper

                # Track for this project
                raw_papers_for_project[pid] = papers_by_id[pid]

        # Rank by citation count and keep top N for this project
        ranked = sorted(
            raw_papers_for_project.values(),
            key=lambda p: p["citation_count"],
            reverse=True,
        )
        top_papers = ranked[:PAPERS_PER_PROJECT]
        project_paper_ids[project_id] = [p["id"] for p in top_papers]
        sys.stderr.write(
            f"  Kept {len(top_papers)} papers after ranking for {project['name']}\n"
        )

    # Compute which papers are actually referenced by at least one project's top list
    referenced_ids: set[str] = set()
    for pid_list in project_paper_ids.values():
        referenced_ids.update(pid_list)

    # Build final papers list (only papers in at least one project's top list)
    final_papers = [
        papers_by_id[pid] for pid in referenced_ids if pid in papers_by_id
    ]

    # Compute max citation count for normalization
    max_citations = max((p["citation_count"] for p in final_papers), default=1)
    total_projects = len(projects)

    for paper in final_papers:
        # Mark bridge papers
        paper["is_bridge"] = len(paper["connected_projects"]) >= 2

        # Compute relevance score
        normalized_citations = paper["citation_count"] / max(max_citations, 1)
        recency_score = (paper["year"] - 2023) / 3.0
        bridge_score = len(paper["connected_projects"]) / max(total_projects, 1)

        paper["relevance_score"] = round(
            0.4 * normalized_citations + 0.3 * recency_score + 0.3 * bridge_score,
            4,
        )

    # Build links list: project -> paper for all project top-list memberships
    links = []
    for project_id, pid_list in project_paper_ids.items():
        for pid in pid_list:
            if pid in referenced_ids:
                links.append({"source": project_id, "target": pid})

    return final_papers, links


# ---------------------------------------------------------------------------
# Phase 3: Assemble data payload
# ---------------------------------------------------------------------------

def build_data_payload(projects: list, papers: list, links: list) -> dict:
    """Assemble the final JSON payload for the HTML template."""
    # Strip internal search_queries key from output projects
    clean_projects = []
    for proj in projects:
        clean_projects.append({
            "id": proj["id"],
            "name": proj["name"],
            "short_name": proj["short_name"],
            "domain": proj["domain"],
            "overview": proj["overview"],
            "keywords": proj["keywords"],
        })

    return {
        "projects": clean_projects,
        "papers": papers,
        "links": links,
        "generated_on": str(date.today()),
    }


# ---------------------------------------------------------------------------
# Phase 4: HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Research Radar</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:           #0d1117;
    --surface:      #161b22;
    --border:       #30363d;
    --text-primary: #e6edf3;
    --text-muted:   #8b949e;
    --accent-blue:  #58a6ff;
    --accent-green: #3fb950;
    --accent-orange:#f0883e;
    --accent-purple:#bc8cff;
    --accent-teal:  #39d353;
    --domain-ml:    #58a6ff;
    --domain-mech:  #f0883e;
    --domain-mat:   #3fb950;
    --domain-multi: #bc8cff;
  }

  body {
    background: var(--bg);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
  }

  header h1 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 0.02em;
  }

  header .meta {
    color: var(--text-muted);
    font-size: 12px;
  }

  .main-layout {
    display: flex;
    flex: 1;
    overflow: hidden;
    min-height: 0;
  }

  /* Left sidebar */
  .sidebar-left {
    width: 280px;
    min-width: 280px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .filter-section h3 {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 8px;
  }

  .project-checkbox-row {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 5px;
    cursor: pointer;
    padding: 3px 0;
  }

  .project-checkbox-row:hover { opacity: 0.85; }

  .domain-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .project-checkbox-row input[type="checkbox"] {
    accent-color: var(--accent-blue);
    cursor: pointer;
  }

  .project-checkbox-row label {
    cursor: pointer;
    font-size: 12px;
    color: var(--text-primary);
    line-height: 1.3;
  }

  .year-range-wrap {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .year-range-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .year-range-row label {
    font-size: 12px;
    color: var(--text-muted);
    width: 30px;
  }

  .year-range-row input[type="range"] {
    flex: 1;
    accent-color: var(--accent-blue);
  }

  .year-display {
    font-size: 12px;
    color: var(--text-primary);
    text-align: center;
  }

  .domain-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }

  .domain-btn {
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
    font-size: 11px;
    cursor: pointer;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
  }

  .domain-btn.active-ml    { background: var(--domain-ml);   color: #0d1117; border-color: var(--domain-ml); }
  .domain-btn.active-mechanics { background: var(--domain-mech); color: #0d1117; border-color: var(--domain-mech); }
  .domain-btn.active-materials { background: var(--domain-mat);  color: #0d1117; border-color: var(--domain-mat); }
  .domain-btn.active-multi  { background: var(--domain-multi); color: #0d1117; border-color: var(--domain-multi); }
  .domain-btn:hover { opacity: 0.8; }

  .toggle-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 3px 0;
  }

  .toggle-row label { font-size: 12px; color: var(--text-primary); cursor: pointer; }
  .toggle-row input[type="checkbox"] { accent-color: var(--accent-teal); cursor: pointer; }

  .reset-btn {
    width: 100%;
    padding: 7px;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text-muted);
    font-size: 12px;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
  }

  .reset-btn:hover { background: var(--border); color: var(--text-primary); }

  /* Center graph area */
  .graph-area {
    flex: 1;
    position: relative;
    overflow: hidden;
    background: var(--bg);
    min-width: 0;
  }

  #graph-svg {
    width: 100%;
    height: 100%;
    display: block;
  }

  /* Tooltip */
  #tooltip {
    position: absolute;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 11px;
    font-size: 12px;
    color: var(--text-primary);
    pointer-events: none;
    opacity: 0;
    max-width: 260px;
    line-height: 1.5;
    z-index: 100;
    transition: opacity 0.1s;
  }

  /* Right sidebar */
  .sidebar-right {
    width: 320px;
    min-width: 320px;
    background: var(--surface);
    border-left: 1px solid var(--border);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }

  .sidebar-right-header {
    padding: 12px 14px;
    border-bottom: 1px solid var(--border);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    flex-shrink: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .paper-count-badge {
    background: var(--border);
    border-radius: 10px;
    padding: 2px 7px;
    font-size: 11px;
    color: var(--text-muted);
  }

  .paper-list {
    flex: 1;
    overflow-y: auto;
    padding: 6px 0;
  }

  .paper-item {
    padding: 9px 14px;
    border-bottom: 1px solid #1c2128;
    cursor: pointer;
    transition: background 0.12s;
  }

  .paper-item:hover { background: rgba(48,54,61,0.5); }
  .paper-item.highlighted { background: rgba(88,166,255,0.08); border-left: 2px solid var(--accent-blue); }

  .paper-item-title {
    font-size: 12px;
    color: var(--text-primary);
    line-height: 1.35;
    margin-bottom: 5px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .paper-item-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .year-badge {
    background: var(--border);
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 10px;
    color: var(--text-muted);
  }

  .cite-badge {
    font-size: 10px;
    color: var(--text-muted);
  }

  .bridge-tag {
    font-size: 10px;
    color: var(--accent-teal);
    border: 1px solid var(--accent-teal);
    border-radius: 3px;
    padding: 1px 4px;
  }

  .relevance-bar-wrap {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 5px;
  }

  .relevance-bar-bg {
    flex: 1;
    height: 3px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }

  .relevance-bar-fill {
    height: 100%;
    border-radius: 2px;
  }

  .relevance-val {
    font-size: 10px;
    color: var(--text-muted);
    width: 28px;
    text-align: right;
  }

  .proj-tag {
    font-size: 10px;
    border-radius: 3px;
    padding: 1px 5px;
  }

  /* Detail panel */
  #detail-panel {
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 14px 20px;
    flex-shrink: 0;
    display: none;
    position: relative;
    max-height: 240px;
    overflow-y: auto;
  }

  #detail-panel.visible { display: block; }

  #detail-close {
    position: absolute;
    top: 10px;
    right: 14px;
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 18px;
    cursor: pointer;
    line-height: 1;
    padding: 2px 6px;
  }

  #detail-close:hover { color: var(--text-primary); }

  #detail-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 6px;
    padding-right: 30px;
    line-height: 1.4;
  }

  #detail-authors {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 4px;
  }

  #detail-meta {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 8px;
    flex-wrap: wrap;
  }

  #detail-abstract {
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.6;
    margin-bottom: 10px;
  }

  #detail-footer {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
  }

  #detail-link {
    font-size: 12px;
    color: var(--accent-blue);
    text-decoration: none;
  }

  #detail-link:hover { text-decoration: underline; }

  .detail-proj-chip {
    font-size: 11px;
    border-radius: 4px;
    padding: 2px 7px;
    border: 1px solid;
    font-weight: 500;
  }

  /* SVG styles */
  .link-line {
    stroke-opacity: 0.4;
    pointer-events: none;
  }

  .node-circle {
    cursor: pointer;
  }

  .project-label {
    pointer-events: none;
    font-size: 11px;
    font-weight: 600;
    fill: #fff;
    text-anchor: middle;
    dominant-baseline: central;
  }

  .glow-filter { overflow: visible; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
</style>
</head>
<body>

<header>
  <h1>Research Radar</h1>
  <span class="meta" id="header-meta">Loading...</span>
</header>

<div class="main-layout">

  <!-- Left sidebar: filters -->
  <aside class="sidebar-left">

    <div class="filter-section">
      <h3>Projects</h3>
      <div id="project-checkboxes"></div>
    </div>

    <div class="filter-section">
      <h3>Year Range</h3>
      <div class="year-range-wrap">
        <div class="year-range-row">
          <label>From</label>
          <input type="range" id="year-min" min="2024" max="2026" value="2024" step="1">
        </div>
        <div class="year-range-row">
          <label>To</label>
          <input type="range" id="year-max" min="2024" max="2026" value="2026" step="1">
        </div>
        <div class="year-display" id="year-display">2024 – 2026</div>
      </div>
    </div>

    <div class="filter-section">
      <h3>Domain</h3>
      <div class="domain-buttons">
        <button class="domain-btn" data-domain="ml">ML</button>
        <button class="domain-btn" data-domain="mechanics">Mechanics</button>
        <button class="domain-btn" data-domain="materials">Materials</button>
        <button class="domain-btn" data-domain="multi">Multi</button>
      </div>
    </div>

    <div class="filter-section">
      <div class="toggle-row">
        <input type="checkbox" id="bridge-only">
        <label for="bridge-only">Bridge papers only</label>
      </div>
    </div>

    <button class="reset-btn" id="reset-btn">Reset filters</button>

  </aside>

  <!-- Center: D3 graph -->
  <div class="graph-area">
    <svg id="graph-svg"></svg>
    <div id="tooltip"></div>
  </div>

  <!-- Right sidebar: ranked paper list -->
  <aside class="sidebar-right">
    <div class="sidebar-right-header">
      Papers by Relevance
      <span class="paper-count-badge" id="paper-count-badge">0</span>
    </div>
    <div class="paper-list" id="paper-list"></div>
  </aside>

</div>

<!-- Bottom detail panel -->
<div id="detail-panel">
  <button id="detail-close" title="Close">&times;</button>
  <div id="detail-title"></div>
  <div id="detail-authors"></div>
  <div id="detail-meta"></div>
  <div id="detail-abstract"></div>
  <div id="detail-footer"></div>
</div>

<script>
const DATA = __DATA_PLACEHOLDER__;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const DOMAIN_COLOR = {
  ml:        "#58a6ff",
  mechanics: "#f0883e",
  materials: "#3fb950",
  multi:     "#bc8cff",
};

function domainColor(d) {
  return DOMAIN_COLOR[d] || "#8b949e";
}

function projectById(id) {
  return DATA.projects.find(p => p.id === id);
}

function paperById(id) {
  return DATA.papers.find(p => p.id === id);
}

function truncate(str, n) {
  return str.length <= n ? str : str.slice(0, n - 1) + "\\u2026";
}

function paperRadius(citationCount) {
  return Math.min(22, Math.max(6, 6 + Math.sqrt(citationCount) * 0.8));
}

// ---------------------------------------------------------------------------
// Filter state
// ---------------------------------------------------------------------------

const filterState = {
  activeProjects: new Set(DATA.projects.map(p => p.id)),
  yearMin: 2024,
  yearMax: 2026,
  activeDomains: new Set(),   // empty = all domains active
  bridgeOnly: false,
  selectedProjectId: null,    // single project highlight via node click
};

function paperPassesFilter(paper) {
  // Year range
  if (paper.year < filterState.yearMin || paper.year > filterState.yearMax) return false;

  // Domain filter
  if (filterState.activeDomains.size > 0 && !filterState.activeDomains.has(paper.domain)) return false;

  // Bridge only
  if (filterState.bridgeOnly && !paper.is_bridge) return false;

  // Project filter: paper must be connected to at least one active project
  const connectedActive = paper.connected_projects.some(pid => filterState.activeProjects.has(pid));
  if (!connectedActive) return false;

  // Selected project filter
  if (filterState.selectedProjectId && !paper.connected_projects.includes(filterState.selectedProjectId)) return false;

  return true;
}

// ---------------------------------------------------------------------------
// Sidebar: project checkboxes
// ---------------------------------------------------------------------------

function buildProjectCheckboxes() {
  const container = document.getElementById("project-checkboxes");
  DATA.projects.forEach(proj => {
    const row = document.createElement("div");
    row.className = "project-checkbox-row";

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.id = `cb-${proj.id}`;
    cb.checked = true;
    cb.addEventListener("change", () => {
      if (cb.checked) filterState.activeProjects.add(proj.id);
      else filterState.activeProjects.delete(proj.id);
      applyFilters();
    });

    const dot = document.createElement("span");
    dot.className = "domain-dot";
    dot.style.background = domainColor(proj.domain);

    const lbl = document.createElement("label");
    lbl.htmlFor = `cb-${proj.id}`;
    lbl.textContent = proj.short_name;
    lbl.title = proj.name;

    row.appendChild(cb);
    row.appendChild(dot);
    row.appendChild(lbl);
    container.appendChild(row);
  });
}

// ---------------------------------------------------------------------------
// Year range sliders
// ---------------------------------------------------------------------------

function initYearSliders() {
  const minSlider = document.getElementById("year-min");
  const maxSlider = document.getElementById("year-max");
  const display = document.getElementById("year-display");

  function updateDisplay() {
    const lo = parseInt(minSlider.value);
    const hi = parseInt(maxSlider.value);
    display.textContent = `${lo} \\u2013 ${hi}`;
    filterState.yearMin = lo;
    filterState.yearMax = hi;
    applyFilters();
  }

  minSlider.addEventListener("input", () => {
    if (parseInt(minSlider.value) > parseInt(maxSlider.value)) {
      minSlider.value = maxSlider.value;
    }
    updateDisplay();
  });

  maxSlider.addEventListener("input", () => {
    if (parseInt(maxSlider.value) < parseInt(minSlider.value)) {
      maxSlider.value = minSlider.value;
    }
    updateDisplay();
  });
}

// ---------------------------------------------------------------------------
// Domain buttons
// ---------------------------------------------------------------------------

function initDomainButtons() {
  document.querySelectorAll(".domain-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const domain = btn.dataset.domain;
      if (filterState.activeDomains.has(domain)) {
        filterState.activeDomains.delete(domain);
        btn.className = "domain-btn";
      } else {
        filterState.activeDomains.add(domain);
        btn.className = `domain-btn active-${domain}`;
      }
      applyFilters();
    });
  });
}

// ---------------------------------------------------------------------------
// Bridge toggle + reset
// ---------------------------------------------------------------------------

function initToggles() {
  document.getElementById("bridge-only").addEventListener("change", e => {
    filterState.bridgeOnly = e.target.checked;
    applyFilters();
  });

  document.getElementById("reset-btn").addEventListener("click", () => {
    filterState.activeProjects = new Set(DATA.projects.map(p => p.id));
    filterState.yearMin = 2024;
    filterState.yearMax = 2026;
    filterState.activeDomains = new Set();
    filterState.bridgeOnly = false;
    filterState.selectedProjectId = null;

    document.querySelectorAll(".project-checkbox-row input").forEach(cb => cb.checked = true);
    document.getElementById("year-min").value = 2024;
    document.getElementById("year-max").value = 2026;
    document.getElementById("year-display").textContent = "2024 \\u2013 2026";
    document.querySelectorAll(".domain-btn").forEach(btn => btn.className = "domain-btn");
    document.getElementById("bridge-only").checked = false;

    applyFilters();
  });
}

// ---------------------------------------------------------------------------
// D3 force graph
// ---------------------------------------------------------------------------

const svg = d3.select("#graph-svg");
let width, height;
let simulation;
let svgGroup;

// SVG defs for glow filter
function addGlowFilter(svgEl) {
  const defs = svgEl.append("defs");
  const filter = defs.append("filter")
    .attr("id", "glow")
    .attr("x", "-50%")
    .attr("y", "-50%")
    .attr("width", "200%")
    .attr("height", "200%");
  filter.append("feGaussianBlur")
    .attr("stdDeviation", "3")
    .attr("result", "coloredBlur");
  const feMerge = filter.append("feMerge");
  feMerge.append("feMergeNode").attr("in", "coloredBlur");
  feMerge.append("feMergeNode").attr("in", "SourceGraphic");
}

function initGraph() {
  const container = document.querySelector(".graph-area");
  width = container.clientWidth;
  height = container.clientHeight;

  svg.attr("viewBox", [0, 0, width, height]);

  addGlowFilter(svg);

  const zoomBehavior = d3.zoom()
    .scaleExtent([0.15, 4])
    .on("zoom", (event) => {
      svgGroup.attr("transform", event.transform);
    });

  svg.call(zoomBehavior);

  svgGroup = svg.append("g").attr("class", "zoom-group");
  svgGroup.append("g").attr("class", "links-layer");
  svgGroup.append("g").attr("class", "nodes-layer");

  simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(d => d.type === "project" ? -300 : -80))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(d => (d.type === "project" ? 28 : paperRadius(d.citation_count || 0)) + 8))
    .on("tick", ticked);
}

let currentNodes = [];
let currentLinks = [];
let linkSelection, nodeSelection;

function buildGraphData() {
  const visiblePapers = DATA.papers.filter(paperPassesFilter);
  const visiblePaperIds = new Set(visiblePapers.map(p => p.id));

  // Always include all active projects as nodes
  const projectNodes = DATA.projects
    .filter(p => filterState.activeProjects.has(p.id))
    .map(p => ({ ...p, type: "project", node_radius: 28 }));

  const paperNodes = visiblePapers.map(p => ({
    ...p,
    type: "paper",
    node_radius: paperRadius(p.citation_count || 0),
  }));

  const nodes = [...projectNodes, ...paperNodes];

  const links = DATA.links
    .filter(l => {
      const sourceActive = filterState.activeProjects.has(l.source.id || l.source);
      const targetVisible = visiblePaperIds.has(l.target.id || l.target);
      return sourceActive && targetVisible;
    })
    .map(l => ({ ...l }));

  return { nodes, links };
}

function renderGraph() {
  const { nodes, links } = buildGraphData();
  currentNodes = nodes;
  currentLinks = links;

  const linksLayer = svgGroup.select(".links-layer");
  const nodesLayer = svgGroup.select(".nodes-layer");

  // Links
  linkSelection = linksLayer.selectAll("line.link-line")
    .data(links, d => `${d.source.id || d.source}-${d.target.id || d.target}`)
    .join(
      enter => enter.append("line")
        .attr("class", "link-line")
        .attr("stroke-width", 1)
        .attr("stroke", d => {
          const src = d.source.id || d.source;
          const proj = projectById(src);
          return proj ? domainColor(proj.domain) : "#8b949e";
        }),
      update => update,
      exit => exit.remove()
    );

  // Nodes
  const nodeGroups = nodesLayer.selectAll("g.node-group")
    .data(nodes, d => d.id)
    .join(
      enter => {
        const g = enter.append("g")
          .attr("class", "node-group")
          .call(d3.drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded)
          );

        // Glow ring for bridge papers
        g.filter(d => d.type === "paper" && d.is_bridge)
          .append("circle")
          .attr("class", "bridge-ring")
          .attr("r", d => d.node_radius + 4)
          .attr("fill", "none")
          .attr("stroke", "#39d353")
          .attr("stroke-width", 1.5)
          .attr("filter", "url(#glow)")
          .attr("opacity", 0.6);

        g.append("circle")
          .attr("class", "node-circle")
          .attr("r", d => d.node_radius)
          .attr("fill", d => domainColor(d.domain))
          .attr("stroke", d => d.type === "project" ? "#fff" : "transparent")
          .attr("stroke-width", d => d.type === "project" ? 2 : 0);

        // Labels for project nodes only
        g.filter(d => d.type === "project")
          .append("text")
          .attr("class", "project-label")
          .text(d => {
            // Fit short_name into node; show abbreviated if needed
            const words = d.short_name.split(" ");
            return words.length <= 2 ? d.short_name : words.slice(0, 2).join("\\n");
          })
          .call(wrapProjectLabel);

        return g;
      },
      update => update,
      exit => exit.remove()
    );

  nodeGroups
    .select("circle.node-circle")
    .attr("r", d => d.node_radius)
    .attr("fill", d => domainColor(d.domain));

  // Event handlers
  nodeGroups
    .on("mouseover", handleNodeMouseover)
    .on("mouseout", handleNodeMouseout)
    .on("click", handleNodeClick);

  simulation.nodes(nodes);
  simulation.force("link").links(links);
  simulation.alpha(0.5).restart();

  updateRankedList();
  updateHeaderMeta();
}

function wrapProjectLabel(textSel) {
  // D3 text wrapping for multi-word project labels inside a 28px radius circle
  textSel.each(function(d) {
    const el = d3.select(this);
    el.text(null);
    const words = (d.short_name || d.name).split(" ").slice(0, 4);
    const lineHeight = 13;
    const lines = [];
    // Try to fit on 2 lines max
    if (words.length <= 2) {
      lines.push(words.join(" "));
    } else if (words.length === 3) {
      lines.push(words.slice(0, 2).join(" "));
      lines.push(words[2]);
    } else {
      lines.push(words.slice(0, 2).join(" "));
      lines.push(words.slice(2).join(" "));
    }
    const startY = -(lines.length - 1) * lineHeight / 2;
    lines.forEach((line, i) => {
      el.append("tspan")
        .attr("x", 0)
        .attr("dy", i === 0 ? `${startY}px` : `${lineHeight}px`)
        .text(line);
    });
  });
}

function ticked() {
  if (linkSelection) {
    linkSelection
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
  }

  svgGroup.selectAll("g.node-group")
    .attr("transform", d => `translate(${d.x},${d.y})`);
}

function dragStarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragEnded(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

// ---------------------------------------------------------------------------
// Tooltip
// ---------------------------------------------------------------------------

const tooltip = document.getElementById("tooltip");

function handleNodeMouseover(event, d) {
  let html = "";
  if (d.type === "project") {
    html = `<strong>${d.name}</strong><br><span style="color:var(--text-muted);font-size:11px">Domain: ${d.domain}</span>`;
  } else {
    const citeStr = d.citation_count !== undefined ? `${d.citation_count} citations` : "";
    html = `<strong>${truncate(d.title, 80)}</strong><br>` +
      `<span style="color:var(--text-muted);font-size:11px">${d.year} \\u2013 ${citeStr}</span>`;
    if (d.is_bridge) {
      html += `<br><span style="color:var(--accent-teal);font-size:10px">Bridge paper</span>`;
    }
  }
  tooltip.innerHTML = html;
  tooltip.style.opacity = "1";

  // Highlight connected links
  if (d.type === "paper") {
    svgGroup.selectAll("line.link-line")
      .attr("stroke-opacity", l => {
        const tgt = l.target.id || l.target;
        return tgt === d.id ? 1.0 : 0.1;
      });
  }

  positionTooltip(event);
}

function handleNodeMouseout(event, d) {
  tooltip.style.opacity = "0";
  // Restore link opacity
  svgGroup.selectAll("line.link-line").attr("stroke-opacity", 0.4);
}

function positionTooltip(event) {
  const containerRect = document.querySelector(".graph-area").getBoundingClientRect();
  let x = event.clientX - containerRect.left + 12;
  let y = event.clientY - containerRect.top - 10;
  const ttW = 260;
  if (x + ttW > containerRect.width) x = x - ttW - 20;
  tooltip.style.left = `${x}px`;
  tooltip.style.top = `${y}px`;
}

svg.on("mousemove", (event) => {
  if (tooltip.style.opacity !== "0") positionTooltip(event);
});

// ---------------------------------------------------------------------------
// Node click: show detail + project filter
// ---------------------------------------------------------------------------

function handleNodeClick(event, d) {
  event.stopPropagation();

  if (d.type === "project") {
    if (filterState.selectedProjectId === d.id) {
      filterState.selectedProjectId = null;
    } else {
      filterState.selectedProjectId = d.id;
    }
    applyFilters();
    return;
  }

  // Paper node
  showDetailPanel(d);
  highlightPaperInList(d.id);
}

svg.on("click", () => {
  if (filterState.selectedProjectId) {
    filterState.selectedProjectId = null;
    applyFilters();
  }
});

// ---------------------------------------------------------------------------
// Detail panel
// ---------------------------------------------------------------------------

function showDetailPanel(paper) {
  const panel = document.getElementById("detail-panel");
  panel.classList.add("visible");

  document.getElementById("detail-title").textContent = paper.title;
  document.getElementById("detail-authors").textContent = (paper.authors || []).join(", ");

  const metaEl = document.getElementById("detail-meta");
  metaEl.innerHTML = `
    <span class="year-badge">${paper.year}</span>
    <span class="cite-badge">${paper.citation_count} citations</span>
    ${paper.is_bridge ? '<span class="bridge-tag">Bridge</span>' : ""}
    <span style="color:var(--text-muted);font-size:11px">Relevance: ${paper.relevance_score.toFixed(2)}</span>
  `;

  document.getElementById("detail-abstract").textContent = paper.abstract_snippet
    ? paper.abstract_snippet + (paper.abstract_snippet.length >= 300 ? "\\u2026" : "")
    : "No abstract available.";

  const footerEl = document.getElementById("detail-footer");
  let footerHtml = `<a id="detail-link" href="${paper.url}" target="_blank" rel="noopener">View on Semantic Scholar \\u2192</a>`;
  (paper.connected_projects || []).forEach(pid => {
    const proj = projectById(pid);
    if (proj) {
      footerHtml += `<span class="detail-proj-chip" style="color:${domainColor(proj.domain)};border-color:${domainColor(proj.domain)}">${proj.short_name}</span>`;
    }
  });
  footerEl.innerHTML = footerHtml;
}

document.getElementById("detail-close").addEventListener("click", () => {
  document.getElementById("detail-panel").classList.remove("visible");
});

// ---------------------------------------------------------------------------
// Right sidebar: ranked paper list
// ---------------------------------------------------------------------------

function updateRankedList() {
  const visiblePapers = DATA.papers
    .filter(paperPassesFilter)
    .sort((a, b) => b.relevance_score - a.relevance_score);

  document.getElementById("paper-count-badge").textContent = visiblePapers.length;

  const container = document.getElementById("paper-list");
  container.innerHTML = "";

  visiblePapers.forEach(paper => {
    const item = document.createElement("div");
    item.className = "paper-item";
    item.dataset.paperId = paper.id;

    const titleEl = document.createElement("div");
    titleEl.className = "paper-item-title";
    titleEl.textContent = paper.title;

    const metaEl = document.createElement("div");
    metaEl.className = "paper-item-meta";

    const yearBadge = document.createElement("span");
    yearBadge.className = "year-badge";
    yearBadge.textContent = paper.year;

    const citeBadge = document.createElement("span");
    citeBadge.className = "cite-badge";
    citeBadge.textContent = `${paper.citation_count} cit.`;

    metaEl.appendChild(yearBadge);
    metaEl.appendChild(citeBadge);

    if (paper.is_bridge) {
      const bridgeTag = document.createElement("span");
      bridgeTag.className = "bridge-tag";
      bridgeTag.textContent = "Bridge";
      metaEl.appendChild(bridgeTag);
    }

    (paper.connected_projects || []).forEach(pid => {
      const proj = projectById(pid);
      if (!proj) return;
      const tag = document.createElement("span");
      tag.className = "proj-tag";
      tag.style.color = domainColor(proj.domain);
      tag.style.borderColor = domainColor(proj.domain);
      tag.style.border = `1px solid ${domainColor(proj.domain)}`;
      tag.textContent = proj.short_name.split(" ")[0];
      metaEl.appendChild(tag);
    });

    const relWrap = document.createElement("div");
    relWrap.className = "relevance-bar-wrap";

    const relBg = document.createElement("div");
    relBg.className = "relevance-bar-bg";
    const relFill = document.createElement("div");
    relFill.className = "relevance-bar-fill";
    relFill.style.width = `${Math.round(paper.relevance_score * 100)}%`;
    relFill.style.background = domainColor(paper.domain);
    relBg.appendChild(relFill);

    const relVal = document.createElement("div");
    relVal.className = "relevance-val";
    relVal.textContent = paper.relevance_score.toFixed(2);

    relWrap.appendChild(relBg);
    relWrap.appendChild(relVal);

    item.appendChild(titleEl);
    item.appendChild(metaEl);
    item.appendChild(relWrap);

    item.addEventListener("click", () => {
      showDetailPanel(paper);
      highlightPaperInList(paper.id);
      centerOnPaperNode(paper.id);
    });

    container.appendChild(item);
  });
}

function highlightPaperInList(paperId) {
  document.querySelectorAll(".paper-item").forEach(el => {
    el.classList.toggle("highlighted", el.dataset.paperId === paperId);
  });
  const highlighted = document.querySelector(".paper-item.highlighted");
  if (highlighted) highlighted.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

function centerOnPaperNode(paperId) {
  const node = currentNodes.find(n => n.id === paperId);
  if (!node || node.x === undefined) return;

  const container = document.querySelector(".graph-area");
  const w = container.clientWidth;
  const h = container.clientHeight;

  const transform = d3.zoomTransform(svg.node());
  const newTransform = d3.zoomIdentity
    .translate(w / 2 - transform.k * node.x, h / 2 - transform.k * node.y)
    .scale(transform.k);

  svg.transition().duration(600).call(
    d3.zoom().transform,
    newTransform
  );
}

// ---------------------------------------------------------------------------
// Header meta
// ---------------------------------------------------------------------------

function updateHeaderMeta() {
  const visiblePapers = DATA.papers.filter(paperPassesFilter);
  const bridgeCount = visiblePapers.filter(p => p.is_bridge).length;
  document.getElementById("header-meta").textContent =
    `${visiblePapers.length} papers \\u2013 ${bridgeCount} bridge \\u2013 generated ${DATA.generated_on}`;
}

// ---------------------------------------------------------------------------
// Apply filters
// ---------------------------------------------------------------------------

function applyFilters() {
  renderGraph();
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

function init() {
  buildProjectCheckboxes();
  initYearSliders();
  initDomainButtons();
  initToggles();
  initGraph();
  renderGraph();
}

window.addEventListener("load", init);
window.addEventListener("resize", () => {
  const container = document.querySelector(".graph-area");
  width = container.clientWidth;
  height = container.clientHeight;
  svg.attr("viewBox", [0, 0, width, height]);
  if (simulation) {
    simulation.force("center", d3.forceCenter(width / 2, height / 2));
    simulation.alpha(0.3).restart();
  }
});
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(data_payload: dict) -> str:
    """Inject the JSON data payload into the HTML template."""
    json_str = json.dumps(data_payload, ensure_ascii=False, separators=(",", ":"))
    return HTML_TEMPLATE.replace("__DATA_PLACEHOLDER__", json_str)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    sys.stderr.write("=== Research Radar: starting ===\n\n")

    # Phase 1: parse project files
    sys.stderr.write("--- Phase 1: Parsing project files ---\n")
    projects = load_all_projects()
    sys.stderr.write(f"Loaded {len(projects)} projects.\n\n")

    # Phase 2: fetch papers
    sys.stderr.write("--- Phase 2: Fetching papers from Semantic Scholar ---\n")
    papers = []
    links = []
    api_error_occurred = False

    try:
        papers, links = fetch_all_papers(projects)
    except Exception as exc:
        sys.stderr.write(f"ERROR: API phase failed completely: {exc}\n")
        api_error_occurred = True
        papers = []
        links = []

    # Phase 3: build data payload
    sys.stderr.write("\n--- Phase 3: Building data payload ---\n")
    data_payload = build_data_payload(projects, papers, links)

    # Summary stats
    total_papers = len(papers)
    bridge_papers = [p for p in papers if p.get("is_bridge")]
    sys.stderr.write(f"Total unique papers: {total_papers}\n")
    sys.stderr.write(f"Bridge papers: {len(bridge_papers)}\n")

    # Per-project paper counts
    for proj in projects:
        proj_papers = [
            p for p in papers if proj["id"] in p.get("connected_projects", [])
        ]
        sys.stderr.write(f"  {proj['short_name']}: {len(proj_papers)} papers\n")

    if total_papers < 5:
        sys.stderr.write(
            "WARNING: Fewer than 5 papers fetched total. HTML will be generated with limited data.\n"
        )

    # Phase 4: generate HTML
    sys.stderr.write("\n--- Phase 4: Generating HTML ---\n")
    html_content = generate_html(data_payload)

    if api_error_occurred:
        error_notice = (
            "<!-- WARNING: API phase failed completely. "
            "No paper data is present. Check network connectivity and retry. -->\n"
        )
        html_content = error_notice + html_content

    OUTPUT_PATH.write_text(html_content, encoding="utf-8")
    sys.stderr.write(f"Output written to: {OUTPUT_PATH}\n")
    sys.stderr.write("=== Research Radar: done ===\n")


if __name__ == "__main__":
    main()
