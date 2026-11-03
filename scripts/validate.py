#!/usr/bin/env python3
"""Static checks for the book: manifest, front matter, figures, prose rules, pins.

Standard library only. Run from anywhere:

    uv run python scripts/validate.py
    uv run python scripts/validate.py --self-test

Every violation prints as `path:line: message`; the exit status is 1 if any
error was found. Warnings and info lines never change the exit status.
"""

import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_DOCS = 47
EM_DASH = "\u2014"
PROSE_STATUSES = frozenset({"done", "drafted", "verified"})
MIN_WORDS = 1900
MAX_WORDS = 2500
CAPTION_MIN = 20
CAPTION_MAX = 45
SIDEBAR = '<blockquote class="ai-sidebar" markdown="1">'

XREF_RE = re.compile(r"\b(ch\.?|chapter)\s*\d+\b", re.IGNORECASE)
FM_PROSE_KEYS = ("title", "description", "blurb")
FM_PROSE_PREFIX = "card_"
CODETABS_RE = re.compile(r"\{%-?\s*include\s+codetabs\.html\b(.*?)-?%\}", re.DOTALL)
PLAN_REL = "_plans/r01-build-plan.md"
PDP_RE = re.compile(r"PDP-\d+")
ITER_RE = re.compile(r"\br\d{2}\b")
SPIKE_RE = re.compile(r"(?<![\w/])spikes?\b(?!/)", re.IGNORECASE)
CAPSTONE_RE = re.compile(r"capstone", re.IGNORECASE)
INCLUDE_RE = re.compile(r"\{%-?\s*include\s+excalidraw\.html\b(.*?)-?%\}", re.DOTALL)
PARAM_RE = re.compile(r'(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"')
FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*([\w+-]*)")
RAW_TOKEN_RE = re.compile(r"\{%-?\s*(raw|endraw)\s*-?%\}")
TEMPLATE_RE = re.compile(r"\{\{|\{%")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
LIQUID_RE = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.DOTALL)
LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
URL_RE = re.compile(r"https?://\S+")
HTML_TAG_RE = re.compile(r"<[^>]+>")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")
FIGURE_RE = re.compile(r"\{%-?\s*include\s+excalidraw\.html\b")
SPINE = {
    "argument": ("Learning objectives", "Why this matters", "For deeper coverage"),
    "appendix": ("Learning objectives", "Why this matters", "For deeper coverage"),
    "hands-on": (
        "Learning objectives",
        "Why this matters",
        "Build, run, observe",
        "For deeper coverage",
    ),
    "pattern": (
        "Learning objectives",
        "Why this matters",
        "Build, run, observe",
        "When not to use it",
        "For deeper coverage",
    ),
}
TOOL_ALIASES = {"cpython": "python"}
EM_DASH_ONLY = (
    "LICENSE-docs.md",
    "diagrams/README.md",
    "_includes/**/*",
    "_layouts/**/*",
    "_data/diagrams.yml",
)
SVG_TEXT_RE = re.compile(r"<text\b[^>]*>(.*?)</text>", re.DOTALL)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


@dataclass
class Report:
    errors: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)
    info: list[Finding] = field(default_factory=list)


# ---------------------------------------------------------------- parsing


def split_front_matter(text: str) -> tuple[dict[str, str], int]:
    """Return (front matter map, number of lines the block occupies)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, 0
    data: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return data, i + 1
        key, sep, value = lines[i].partition(":")
        if sep and key.strip() and not key.startswith((" ", "\t", "#")):
            data[key.strip()] = unquote(value.strip())
    return {}, 0


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def body_lines(text: str) -> list[tuple[int, str, str | None]]:
    """Body lines as (1-based line number, text, fence language or None).

    A line is tagged with the language of the fenced block it is inside
    (empty string for an untagged fence). Fence delimiter lines are tagged too.
    """
    _, offset = split_front_matter(text)
    out: list[tuple[int, str, str | None]] = []
    fence: str | None = None
    lang = ""
    for idx, line in enumerate(text.split("\n")[offset:], start=offset + 1):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence, lang = m.group(1)[0], m.group(2)
                out.append((idx, line, lang))
            else:
                out.append((idx, line, None))
        else:
            out.append((idx, line, lang))
            if m and m.group(1)[0] == fence and not m.group(2):
                fence = None
    return out


def prose_lines(text: str) -> list[tuple[int, str]]:
    return [(n, ln) for n, ln, fence in body_lines(text) if fence is None]


def word_count(text: str) -> int:
    """Count prose words only.

    Drops fenced code, Liquid tags, inline code, link and image targets (link text
    stays), bare URLs, HTML tags, heading lines and table rows.
    """
    joined = "\n".join(line for _, line in prose_lines(text))
    joined = LIQUID_RE.sub(" ", joined)
    count = 0
    for line in joined.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(("#", "|")):
            continue
        line = INLINE_CODE_RE.sub(" ", line)
        line = LINK_RE.sub(r"\1", line)
        line = URL_RE.sub(" ", line)
        line = HTML_TAG_RE.sub(" ", line)
        count += len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'_-]*", line))
    return count


def parse_diagram_yaml(text: str) -> list[tuple[int, dict[str, str]]]:
    """Parse the flat list-of-maps in _data/diagrams.yml. Returns (line, entry)."""
    entries: list[tuple[int, dict[str, str]]] = []
    current: dict[str, str] | None = None
    key: str | None = None
    for n, raw in enumerate(text.split("\n"), start=1):
        if not raw.strip() or raw.lstrip().startswith("#") or raw.strip() == "[]":
            continue
        stripped = raw.strip()
        if stripped.startswith("- "):
            current = {}
            entries.append((n, current))
            stripped = stripped[2:].strip()
            key = None
        elif current is None:
            continue
        k, sep, v = stripped.partition(":")
        if sep and re.fullmatch(r"[A-Za-z_]\w*", k) and not raw.startswith("      "):
            key = k
            value = v.strip()
            current[key] = "" if value in (">", ">-", "|", "|-") else unquote(value)
        elif key is not None:
            current[key] = (current[key] + " " + stripped).strip()
    return entries


# ----------------------------------------------------------------- checks


def check_figure_captions(rel: str, text: str) -> list[Finding]:
    out: list[Finding] = []
    for m in INCLUDE_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        params = dict(PARAM_RE.findall(m.group(1)))
        out.extend(caption_findings(rel, line, params.get("caption", "")))
    return out


def caption_findings(rel: str, line: int, caption: str) -> list[Finding]:
    out: list[Finding] = []
    words = len(caption.split())
    if not CAPTION_MIN <= words <= CAPTION_MAX:
        out.append(
            Finding(rel, line, f"caption has {words} words, need {CAPTION_MIN}-{CAPTION_MAX}")
        )
    if "TODO" in caption:
        out.append(Finding(rel, line, "caption contains TODO"))
    return out


def check_figure_files(root: Path, rel: str, text: str) -> list[Finding]:
    out: list[Finding] = []
    for m in INCLUDE_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        name = dict(PARAM_RE.findall(m.group(1))).get("name")
        if name is None:
            out.append(Finding(rel, line, "figure include has no name"))
            continue
        out.extend(missing_diagram_files(root, rel, line, name))
    return out


def missing_diagram_files(root: Path, rel: str, line: int, name: str) -> list[Finding]:
    return [
        Finding(rel, line, f"missing diagrams/{name}{ext}")
        for ext in (".svg", ".excalidraw")
        if not (root / "diagrams" / f"{name}{ext}").is_file()
    ]


def check_prose(rel: str, text: str, kind: str, status: str) -> tuple[list[Finding], list[Finding]]:
    """Prose rules for one chapter. Returns (errors, warnings)."""
    errors: list[Finding] = []
    warnings: list[Finding] = []
    for n, line, _ in body_lines(text):
        if "{: .ai-sidebar}" in line:
            errors.append(Finding(rel, n, "use the blockquote markup, not {: .ai-sidebar}"))
    if status in PROSE_STATUSES:
        errors.extend(check_spine(rel, text, kind))
        figures = len(FIGURE_RE.findall(text))
        if kind != "appendix" and figures != 1:
            errors.append(Finding(rel, 1, f"{figures} figure includes, need exactly 1"))
        words = word_count(text)
        if words < MIN_WORDS:
            errors.append(Finding(rel, 1, f"prose has {words} words, minimum {MIN_WORDS}"))
        elif words > MAX_WORDS:
            warnings.append(Finding(rel, 1, f"prose has {words} words, above {MAX_WORDS}"))
        if kind == "pattern":
            count = text.count(SIDEBAR)
            if count != 1:
                errors.append(
                    Finding(rel, 1, f"pattern chapter has {count} ai-sidebar blocks, need 1")
                )
    return errors, warnings


def check_xrefs(rel: str, text: str) -> list[Finding]:
    """Chapter cross-references are banned in reader-facing prose (fenced code exempt)."""
    return [
        Finding(rel, n, f"chapter cross-reference {m.group(0)!r} in prose")
        for n, line in prose_lines(text)
        for m in XREF_RE.finditer(line)
    ]


def check_front_matter_xrefs(rel: str, text: str) -> list[Finding]:
    """Chapter cross-references in the prose-valued front-matter keys (not order, part, etc.)."""
    fm, _ = split_front_matter(text)
    lines = text.split("\n")
    out: list[Finding] = []
    for key, value in fm.items():
        if key not in FM_PROSE_KEYS and not key.startswith(FM_PROSE_PREFIX):
            continue
        line = next((i for i, t in enumerate(lines, 1) if t.startswith(f"{key}:")), 1)
        out.extend(
            Finding(rel, line, f"chapter cross-reference {m.group(0)!r} in front matter {key}")
            for m in XREF_RE.finditer(value)
        )
    return out


def check_codetabs(rel: str, text: str) -> list[Finding]:
    """Every codetabs include must pass an explicit, non-empty labels parameter."""
    out: list[Finding] = []
    for m in CODETABS_RE.finditer(text):
        labels = dict(PARAM_RE.findall(m.group(1))).get("labels", "")
        if not labels.strip():
            line = text.count("\n", 0, m.start()) + 1
            out.append(Finding(rel, line, "codetabs include has no labels parameter"))
    return out


def check_spine(rel: str, text: str, kind: str) -> list[Finding]:
    headings = {m.group(1) for _, line in prose_lines(text) if (m := H2_RE.match(line))}
    return [
        Finding(rel, 1, f"missing spine heading '## {need}' for kind {kind!r}")
        for need in SPINE.get(kind, ())
        if need not in headings
    ]


def check_templates(rel: str, text: str) -> list[Finding]:
    """Unescaped Liquid in fenced blocks or inline code, outside {% raw %}...{% endraw %}."""
    out: list[Finding] = []
    in_raw = False
    for n, line, fence in body_lines(text):
        pos = 0
        segments: list[tuple[str, bool]] = []
        for tok in RAW_TOKEN_RE.finditer(line):
            segments.append((line[pos : tok.start()], in_raw))
            in_raw = tok.group(1) == "raw"
            pos = tok.end()
        segments.append((line[pos:], in_raw))
        for segment, raw in segments:
            if raw:
                continue
            if fence is not None:
                hit = bool(TEMPLATE_RE.search(segment))
                where = "fenced block"
            else:
                hit = any(TEMPLATE_RE.search(m.group(0)) for m in INLINE_CODE_RE.finditer(segment))
                where = "inline code"
            if hit:
                out.append(Finding(rel, n, f"unescaped '{{{{' or '{{%' in {where}; wrap in raw"))
    return out


def check_em_dash(rel: str, text: str) -> list[Finding]:
    return [
        Finding(rel, n, "em-dash (U+2014)")
        for n, line in enumerate(text.split("\n"), start=1)
        if EM_DASH in line
    ]


def check_banned(rel: str, text: str, *, svg: bool) -> list[Finding]:
    """Em-dash, capstone, PDP ids, iteration ids and 'spike' in reader-facing text."""
    out: list[Finding] = []
    lines = text.split("\n")
    out.extend(check_em_dash(rel, text))
    scoped: list[tuple[int, str]]
    if svg:
        scoped = []
        for m in SVG_TEXT_RE.finditer(text):
            scoped.append((text.count("\n", 0, m.start()) + 1, m.group(1)))
        rules = [(PDP_RE, "PDP id"), (ITER_RE, "iteration id"), (SPIKE_RE, "word 'spike'")]
    else:
        scoped = list(enumerate(lines, start=1))
        rules = [
            (CAPSTONE_RE, "word 'capstone'"),
            (PDP_RE, "PDP id"),
            (ITER_RE, "iteration id"),
            (SPIKE_RE, "word 'spike'"),
        ]
    for n, line in scoped:
        for pattern, label in rules:
            if pattern.search(line):
                out.append(Finding(rel, n, label))
    if svg:
        for n, line in enumerate(lines, start=1):
            if CAPSTONE_RE.search(line):
                out.append(Finding(rel, n, "word 'capstone'"))
    return out


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def chapter_table(text: str) -> dict[str, tuple[int, str]]:
    """Version-table rows of Chapter 0: tool name -> (line, version)."""
    known = {"python", "uv", "pytest", "pytest-mock", "ruff", "mypy"}
    rows: dict[str, tuple[int, str]] = {}
    for n, line in enumerate(text.split("\n"), start=1):
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = TOOL_ALIASES.get(normalize(cells[0]), normalize(cells[0]))
        if name in known and re.fullmatch(r"\d+(\.\d+)+", cells[1]):
            rows.setdefault(name, (n, cells[1]))
    return rows


def lock_versions(lock_text: str) -> dict[str, tuple[int, str]]:
    out: dict[str, tuple[int, str]] = {}
    lines = lock_text.split("\n")
    for i, line in enumerate(lines):
        m = re.fullmatch(r'name = "([^"]+)"', line)
        if m and i + 1 < len(lines):
            v = re.fullmatch(r'version = "([^"]+)"', lines[i + 1])
            if v:
                out[normalize(m.group(1))] = (i + 1, v.group(1))
    return out


def ci_uv_versions(ci_text: str) -> list[tuple[int, str]]:
    lines = ci_text.split("\n")
    found: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if "astral-sh/setup-uv" not in line:
            continue
        for j in range(i + 1, min(i + 6, len(lines))):
            m = re.match(r"\s*version:\s*[\"']?([\w.]+)", lines[j])
            if m:
                found.append((j + 1, m.group(1)))
                break
    return found


def pin_findings(
    pyproject: str, lock: str, python_version: str, chapter: str, ci: str, plan: str = ""
) -> list[Finding]:
    """Cross-check pyproject pins, uv.lock, .python-version, Chapter 0 and ci.yml."""
    out: list[Finding] = []
    table = chapter_table(chapter)
    chapter_rel = "_docs/00-prerequisites.md"
    locked = lock_versions(lock)
    pin_lines = pyproject.split("\n")
    data = tomllib.loads(pyproject)
    for dep in data.get("dependency-groups", {}).get("dev", []):
        if not isinstance(dep, str):
            continue
        line = next((i for i, t in enumerate(pin_lines, 1) if f'"{dep}"' in t), 1)
        name, sep, version = dep.partition("==")
        if not sep:
            out.append(
                Finding("pyproject.toml", line, f"dev dependency {dep!r} is not pinned with ==")
            )
            continue
        key = normalize(name)
        if key not in locked:
            out.append(Finding("uv.lock", 1, f"{key} is pinned in pyproject.toml but not locked"))
        elif locked[key][1] != version:
            out.append(
                Finding(
                    "uv.lock",
                    locked[key][0],
                    f"{key} locked at {locked[key][1]}, pyproject.toml pins {version}",
                )
            )
        if key not in table:
            out.append(Finding(chapter_rel, 1, f"version table has no row for {key}"))
        elif table[key][1] != version:
            out.append(
                Finding(
                    chapter_rel,
                    table[key][0],
                    f"{key} row says {table[key][1]}, pyproject.toml pins {version}",
                )
            )
    if not re.fullmatch(r"\d+\.\d+\.\d+", python_version):
        out.append(Finding(".python-version", 1, "must be an exact x.y.z"))
    elif "python" not in table:
        out.append(Finding(chapter_rel, 1, "version table has no row for CPython"))
    elif table["python"][1] != python_version:
        out.append(
            Finding(
                chapter_rel,
                table["python"][0],
                f"CPython row says {table['python'][1]}, .python-version is {python_version}",
            )
        )
    if "uv" not in table:
        out.append(Finding(chapter_rel, 1, "version table has no row for uv"))
    else:
        uv_line, uv_version = table["uv"]
        for line, version in ci_uv_versions(ci):
            if version != uv_version:
                out.append(
                    Finding(
                        ".github/workflows/ci.yml",
                        line,
                        f"setup-uv version {version}, {chapter_rel}:{uv_line} says {uv_version}",
                    )
                )
    out.extend(plan_findings(plan, data, python_version, table.get("uv")))
    return out


def plan_table(text: str) -> dict[str, tuple[int, str]]:
    """Rows of the plan's 'Verified toolchain' table: tool name -> (line, leading version)."""
    known = {"cpython": "python", "uv": "uv", "pytest": "pytest", "pytest-mock": "pytest-mock"}
    known.update({"ruff": "ruff", "mypy": "mypy"})
    rows: dict[str, tuple[int, str]] = {}
    in_section = False
    for n, line in enumerate(text.split("\n"), start=1):
        if line.startswith("## "):
            in_section = line.lower().startswith("## verified toolchain")
            continue
        if not in_section or not line.lstrip().startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        name = known.get(normalize(cells[0])) if len(cells) >= 2 else None
        m = re.match(r"\d+(\.\d+)+", cells[1]) if name else None
        if name and m:
            rows.setdefault(name, (n, m.group(0)))
    return rows


def plan_findings(
    plan: str,
    pyproject: dict[str, object],
    python_version: str,
    uv_row: tuple[int, str] | None,
) -> list[Finding]:
    """Cross-check the plan's Verified toolchain rows against the pins."""
    if not plan:
        return []
    rows = plan_table(plan)
    expected: dict[str, str] = {"python": python_version}
    if uv_row is not None:
        expected["uv"] = uv_row[1]
    groups = pyproject.get("dependency-groups", {})
    devs = groups.get("dev", []) if isinstance(groups, dict) else []
    for dep in devs:
        name, sep, version = str(dep).partition("==")
        if sep:
            expected[normalize(name)] = version
    out: list[Finding] = []
    for key, want in sorted(expected.items()):
        if key not in rows:
            out.append(Finding(PLAN_REL, 1, f"Verified toolchain table has no row for {key}"))
        elif rows[key][1] != want:
            out.append(
                Finding(
                    PLAN_REL,
                    rows[key][0],
                    f"{key} row says {rows[key][1]}, pins say {want}",
                )
            )
    return out


def check_pins(root: Path) -> list[Finding]:
    def read(rel: str) -> str:
        path = root / rel
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    return pin_findings(
        read("pyproject.toml"),
        read("uv.lock"),
        read(".python-version").strip(),
        read("_docs/00-prerequisites.md"),
        read(".github/workflows/ci.yml"),
        read(PLAN_REL),
    )


# ------------------------------------------------------------ whole tree


def reader_facing(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in (
        "_docs/*.md",
        "_parts/*.md",
        "_examples/*.md",
        "*.html",
        "README.md",
        "examples/**/README.md",
        "diagrams/*.svg",
    ):
        files.extend(sorted(root.glob(pattern)))
    return sorted(set(files))


def em_dash_only(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in EM_DASH_ONLY:
        files.extend(p for p in sorted(root.glob(pattern)) if p.is_file())
    return sorted(set(files))


def liquid_processed(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    top = rel.parts[0]
    return top in {"_docs", "_parts", "_examples"} or (
        len(rel.parts) == 1 and path.suffix == ".html"
    )


def load_manifest(root: Path) -> list[dict[str, object]]:
    data = tomllib.loads((root / "scripts" / "chapters.toml").read_text(encoding="utf-8"))
    chapters = data.get("chapter", [])
    return [c for c in chapters if isinstance(c, dict)]


def validate(root: Path) -> Report:
    rep = Report()
    docs = sorted((root / "_docs").glob("*.md"))
    if len(docs) != EXPECTED_DOCS:
        rep.errors.append(Finding("_docs", 1, f"{len(docs)} docs, expected {EXPECTED_DOCS}"))

    part_names: dict[str, int] = {}
    for p in sorted((root / "_parts").glob("*.md")):
        fm, _ = split_front_matter(p.read_text(encoding="utf-8"))
        if "part_name" in fm:
            part_names[fm["part_name"]] = int(fm["order"]) if fm.get("order", "").isdigit() else -1

    manifest = {str(c.get("slug")): c for c in load_manifest(root)}
    doc_slugs = {d.stem for d in docs}
    for slug in sorted(set(manifest) - doc_slugs):
        rep.errors.append(Finding("scripts/chapters.toml", 1, f"slug {slug!r} has no _docs file"))
    for slug in sorted(doc_slugs - set(manifest)):
        rep.errors.append(Finding(f"_docs/{slug}.md", 1, "doc is not listed in chapters.toml"))

    for doc in docs:
        rel = f"_docs/{doc.name}"
        text = doc.read_text(encoding="utf-8")
        fm, _ = split_front_matter(text)
        part = fm.get("part", "")
        if part not in part_names:
            rep.errors.append(Finding(rel, 1, f"part {part!r} matches no _parts part_name"))
        entry = manifest.get(doc.stem)
        if entry is None:
            continue
        if str(entry.get("title")) != fm.get("title"):
            rep.errors.append(Finding(rel, 1, "title differs from chapters.toml"))
        if str(entry.get("number")) != fm.get("order"):
            rep.errors.append(Finding(rel, 1, "order differs from chapters.toml number"))
        number = entry.get("part")
        if part in part_names and number != part_names[part]:
            rep.errors.append(Finding(rel, 1, "part differs from chapters.toml part number"))
        status = str(entry.get("status", "stub"))
        kind = str(entry.get("kind", ""))
        errs, warns = check_prose(rel, text, kind, status)
        rep.errors.extend(errs)
        rep.warnings.extend(warns)
        rep.errors.extend(check_figure_captions(rel, text))
        rep.errors.extend(check_figure_files(root, rel, text))
        if status == "in-progress":
            rep.info.append(Finding(rel, 1, "status in-progress: prose rules not applied"))

    diagrams_yml = root / "_data" / "diagrams.yml"
    if diagrams_yml.is_file():
        for line, item in parse_diagram_yaml(diagrams_yml.read_text(encoding="utf-8")):
            rel = "_data/diagrams.yml"
            name = item.get("name")
            if not name:
                rep.errors.append(Finding(rel, line, "entry has no name"))
                continue
            rep.errors.extend(missing_diagram_files(root, rel, line, name))
            rep.errors.extend(caption_findings(rel, line, item.get("caption", "")))

    for path in reader_facing(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        rep.errors.extend(check_banned(rel, text, svg=path.suffix == ".svg"))
        if path.suffix != ".svg":
            rep.errors.extend(check_xrefs(rel, text))
            rep.errors.extend(check_front_matter_xrefs(rel, text))
            rep.errors.extend(check_codetabs(rel, text))
        if liquid_processed(path, root):
            rep.errors.extend(check_templates(rel, text))

    for path in em_dash_only(root):
        rel = path.relative_to(root).as_posix()
        rep.errors.extend(check_em_dash(rel, path.read_text(encoding="utf-8")))

    rep.errors.extend(check_pins(root))
    return rep


# -------------------------------------------------------------- self-test


def self_test() -> int:
    failures: list[str] = []

    def expect(label: str, condition: bool) -> None:
        if not condition:
            failures.append(label)

    expect("em-dash", bool(check_banned("a.md", f"a {EM_DASH} b", svg=False)))
    expect("capstone", bool(check_banned("a.md", "The Capstone", svg=False)))
    expect("spike", bool(check_banned("a.md", "a spike here", svg=False)))
    expect("spikes dir word", not check_banned("a.md", "spikier", svg=False))
    expect("iteration id", bool(check_banned("a.md", "see r01 notes", svg=False)))
    expect("pdp id", bool(check_banned("a.md", "PDP-006", svg=False)))
    svg = '<svg><text x="1">spike</text><path d="r12"/></svg>'
    expect(
        "svg text only",
        [f.message for f in check_banned("a.svg", svg, svg=True)] == ["word 'spike'"],
    )

    doc = "---\ntitle: T\n---\nSee chapter 5 and Ch. 6.\n```\nchapter 7\n```\n"
    expect("xref in prose only", len(check_xrefs("a.md", doc)) == 2)
    part = '---\ntitle: "P"\norder: 3\nblurb: "Intro, see chapter 5."\n---\nbody\n'
    expect("xref in part blurb", len(check_front_matter_xrefs("p.md", part)) == 1)
    card = '---\ncard_blurb: "Compare with Ch. 2"\ndescription: "fine"\norder: 5\n---\n'
    expect("xref in card blurb", len(check_front_matter_xrefs("e.md", card)) == 1)
    clean = '---\ntitle: "T"\norder: 5\nchapter: 7\nblurb: "No refs."\n---\n'
    expect("front matter clean", not check_front_matter_xrefs("p.md", clean))
    bare_tabs = '{% include codetabs.html %}\n{% include codetabs.html labels="A|B" %}\n'
    expect("codetabs without labels", len(check_codetabs("a.md", bare_tabs)) == 1)
    expect("ai-sidebar attr", bool(check_prose("a.md", "{: .ai-sidebar}\n", "argument", "stub")[0]))

    short = "---\ntitle: T\n---\nfew words\n"
    expect("short done", bool(check_prose("a.md", short, "argument", "done")[0]))
    expect("short stub ok", not check_prose("a.md", short, "argument", "stub")[0])
    expect("short in-progress ok", not check_prose("a.md", short, "argument", "in-progress")[0])
    long_body = "word " * 2000
    figure_line = '{% include excalidraw.html name="x" caption="c" %}\n'
    expect("pattern needs sidebar", bool(check_prose("a.md", long_body, "pattern", "done")[0]))
    full_spine = "".join(f"## {h}\n" for h in SPINE["pattern"])
    ok = full_spine + long_body + "\n" + SIDEBAR + "\n" + figure_line
    expect("pattern with sidebar", not check_prose("a.md", ok, "pattern", "done")[0])
    expect("long warns", bool(check_prose("a.md", "word " * 2600, "argument", "done")[1]))

    bad = "```python\nx = '{{ a }}'\n```\n"
    good = "{% raw %}\n```python\nx = '{{ a }}'\n```\n{% endraw %}\n"
    other = "```text\n{{ a }}\n```\n"
    bare = "```\n{% if x %}\n```\n"
    inline = "Use `{{ a }}` here.\n"
    inline_raw = "{% raw %}Use `{{ a }}` here.{% endraw %}\n"
    expect("raw missing", bool(check_templates("a.md", bad)))
    expect("raw wrapped", not check_templates("a.md", good))
    expect("text fence flagged", bool(check_templates("a.md", other)))
    expect("bare fence flagged", bool(check_templates("a.md", bare)))
    expect("inline code flagged", bool(check_templates("a.md", inline)))
    expect("inline code raw ok", not check_templates("a.md", inline_raw))
    expect("plain prose ok", not check_templates("a.md", "Use {{ a }} outside code.\n"))

    expect("caption short", bool(caption_findings("a", 1, "too short")))
    expect("caption todo", bool(caption_findings("a", 1, "TODO " + "word " * 25)))
    expect("caption ok", not caption_findings("a", 1, "word " * 25))
    inc = '{% include excalidraw.html name="x" caption="short" %}'
    expect("include caption parsed", bool(check_figure_captions("a.md", inc)))

    wc = "---\nt: x\n---\n# Heading words here\n| a | b words |\n"
    wc += "Real [link text](http://example.com/very/long) and `code span` and http://x.io/y.\n"
    wc += '```\nfenced words\n```\n{% include a.html name="x" %}\n<b>bold</b> end\n'
    expect("word count prose only", word_count(wc) == 7)
    spine_text = "## Learning objectives\n## Why this matters\n## For deeper coverage\n"
    expect("spine hands-on missing", bool(check_spine("a.md", spine_text, "hands-on")))
    expect("spine argument ok", not check_spine("a.md", spine_text, "argument"))
    expect("spine pattern missing", len(check_spine("a.md", spine_text, "pattern")) == 2)
    fig = figure_line
    body = "word " * 2000
    expect("zero figures", bool(check_prose("a.md", body, "argument", "done")[0]))
    expect(
        "two figures",
        any(
            "figure" in f.message
            for f in check_prose("a.md", fig * 2 + body, "argument", "done")[0]
        ),
    )
    expect(
        "appendix no figure ok",
        not any("figure" in f.message for f in check_prose("a.md", body, "appendix", "done")[0]),
    )

    pyproject = '[dependency-groups]\ndev = [\n    "ruff==1.0.0",\n]\n'
    lock = 'name = "ruff"\nversion = "1.0.0"\n'
    table = "| Tool | Version | Role |\n| --- | --- | --- |\n| CPython | 3.14.1 | x |\n"
    table += "| uv | 0.1.0 | x |\n| ruff | 1.0.0 | x |\n"
    ci = '- uses: astral-sh/setup-uv@v10\n  with:\n    version: "0.1.0"\n'
    expect("pins agree", not pin_findings(pyproject, lock, "3.14.1", table, ci))
    bad_row = table.replace("| ruff | 1.0.0", "| ruff | 1.0.1")
    expect("chapter row mismatch", bool(pin_findings(pyproject, lock, "3.14.1", bad_row, ci)))
    bad_lock = lock.replace("1.0.0", "0.9.0")
    expect("lock mismatch", bool(pin_findings(pyproject, bad_lock, "3.14.1", table, ci)))
    expect("python mismatch", bool(pin_findings(pyproject, lock, "3.14.2", table, ci)))
    expect(
        "ci uv mismatch",
        bool(pin_findings(pyproject, lock, "3.14.1", table, ci.replace("0.1.0", "0.2.0"))),
    )

    plan = "## Verified toolchain\n\n| Item | Version |\n| --- | --- |\n"
    plan += "| CPython | 3.14.1 (released x) | d |\n| uv | 0.1.0 (d) | d |\n"
    plan += "| ruff | 1.0.0 | d |\n\n## Next\n\n| ruff | 9.9.9 | d |\n"
    expect("plan agrees", not pin_findings(pyproject, lock, "3.14.1", table, ci, plan))
    expect(
        "plan ruff mismatch",
        bool(
            pin_findings(
                pyproject,
                lock,
                "3.14.1",
                table,
                ci,
                plan.replace("| ruff | 1.0.0", "| ruff | 1.0.2"),
            )
        ),
    )
    expect(
        "plan python mismatch",
        bool(
            pin_findings(pyproject, lock, "3.14.1", table, ci, plan.replace("3.14.1 (", "3.14.0 ("))
        ),
    )

    entries = parse_diagram_yaml("- name: a\n  caption: >-\n    one two\n    three\n- name: b\n")
    expect("yaml parse", len(entries) == 2 and entries[0][1]["caption"] == "one two three")

    fm, size = split_front_matter('---\ntitle: "Q"\norder: 3\n---\nbody')
    expect("front matter", fm == {"title": "Q", "order": "3"} and size == 4)

    for f in failures:
        print(f"self-test FAILED: {f}", file=sys.stderr)
    print(f"self-test: {'FAILED' if failures else 'ok'}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    rep = validate(ROOT)
    for f in rep.info:
        print(f"info: {f}")
    for f in rep.warnings:
        print(f"warning: {f}")
    for f in rep.errors:
        print(f"error: {f}")
    print(f"validate: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
