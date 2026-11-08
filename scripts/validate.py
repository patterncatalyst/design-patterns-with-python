#!/usr/bin/env python3
"""Static checks for the book: manifest, front matter, figures, prose rules, pins.

Standard library only. Run from anywhere:

    uv run python scripts/validate.py
    uv run python scripts/validate.py --self-test
    uv run python scripts/validate.py --claims

Every violation prints as `path:line: message`; the exit status is 1 if any
error was found. Warnings and info lines never change the exit status.
"""

import contextlib
import html
import os
import posixpath
import pwd
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

import host_ids

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_DOCS = 47
EM_DASH = "\u2014"
PROSE_STATUSES = frozenset({"done", "drafted", "verified"})
# Docs the terse rewording has finished (r26 plan, decision 6). r26 adds each pilot doc as it
# lands; r27 and r28 extend the set. Empty on an unreworded tree, so the checks cost nothing.
TERSE_DOCS: frozenset[int] = frozenset(range(47))
# Pattern-kind chapters about Python mechanisms (decorators, descriptors, singledispatch,
# metaclasses, dynamic attributes, shortcut idioms): they keep their own H2s, not `## Pattern:`.
IDIOM_DOCS: frozenset[int] = frozenset(range(26, 32))
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
    "argument": (
        "Learning objectives",
        "Why this matters",
        "What you can do now",
        "For deeper coverage",
    ),
    "appendix": ("Learning objectives", "Why this matters", "For deeper coverage"),
    "hands-on": (
        "Learning objectives",
        "Why this matters",
        "Build, run, observe",
        "What you can do now",
        "For deeper coverage",
    ),
    "pattern": (
        "Learning objectives",
        "Why this matters",
        "Build, run, observe",
        "When not to use it",
        "What you can do now",
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
STALE_RE = re.compile(r"(?<![\d.])(?:[Pp]ython ?3\.(\d+)|3\.(\d+)\.\d+)")
STALE_EXEMPT = ("since ", "before ", "until ", "new in ")
STALE_WINDOW = 16
PYTEST_MOCK_RE = re.compile(r"pytest[- ]mock[\s|=`*-]*$|\bmock-$", re.IGNORECASE)
COLLECTION_KEYS: dict[str, tuple[str, ...]] = {
    "_docs": ("layout", "title", "order", "part", "description"),
    "_parts": ("title", "order", "part_name"),
    "_examples": (
        "layout",
        "title",
        "order",
        "description",
        "github_path",
        "card_eyebrow",
        "card_blurb",
        "card_title",
    ),
}
CLAIMS_REL = "_plans/reconciliation-plan.md"
CLAIMS_FIRST_ENFORCED = 1
CLAIM_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")
CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")
CLAIM_TEST_RE = re.compile(r"`(?:[^`\s]*::)?(test_\w+)(?:\[[^`]*\])?`")
CLAIM_SOURCE_RE = re.compile(r"source:\s*(https?://[^\s`|)>]+)")
CLAIM_RUN_RE = re.compile(r"run:\s*([A-Za-z0-9_][\w./-]*)")
CLAIM_STATUS_RE = re.compile(r"\*\*(\w+)\*\*")
TEST_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+(test_\w+)", re.MULTILINE)
SVG_TEXT_RE = re.compile(r"<text\b[^>]*>(.*?)</text>", re.DOTALL)

DECK_OWNER = "PatternCatalyst"
DECK_NOTES_FLOOR = 90
DECK_NOTES_FLOOR_PANEL = 45
DECK_PANEL_FILL = "AB0000"
DECK_BANNED = (
    (re.compile("[\u2013\u2014]"), "em or en dash"),
    (PDP_RE, "PDP id"),
    (ITER_RE, "iteration id"),
    (SPIKE_RE, "word 'spike'"),
    (CAPSTONE_RE, "word 'capstone'"),
    (XREF_RE, "chapter reference"),
    (re.compile(r"\bslides?\s*\d+\b", re.IGNORECASE), "slide number reference"),
    (
        re.compile(
            r"\b(next|previous|following|closing|last|earlier|later)\s+(\w+\s+)?(slides?|sections?)\b"
            r"|\b(that|which)\s+follows?\b(?!\s+from)"
            r"|\b(listings?|slides?|figures?|tables?|sections?)\s+(before|after)\s+it\b"
            r"|\bclose\s+the\s+section\b"
            r"|\b(?:tables?|listings?|figures?|slides?|code|lists?|bullets?|diagrams?|examples?)"
            r"\s+(?:above|below)\b|\bthe\s+(?:above|below)\b|\b(?:above|below)\s*(?:[.,;:)]|$)"
            r"|\b(?:shown|listed|given|see|as)\s+(?:above|below)\b"
            r"|\bthe dividers\b|\bwhere they're used\b",
            re.IGNORECASE,
        ),
        "positional slide reference",
    ),
    (re.compile(r"\b(this|these) (deck|slides?)\b", re.IGNORECASE), "self-reference"),
    (
        re.compile(r"\b(chapters?|appendix|appendices)\b", re.IGNORECASE),
        "chapter or appendix pointer",
    ),
    (
        re.compile(r"Java|C#|C\+\+|\.NET|\bGo\b|Rust"),
        "cross-language word",
    ),
)
DECK_NUMBER_RE = re.compile(r"-(101|201|301)-")
# Deck 101 teaches the three-way split, so only 201 and 301 refuse its labels.
DECK_SPLIT_DECKS = frozenset({"201", "301"})
DECK_SPLIT_RE = re.compile(
    r"\b(?:dissolv(?:e|es|ed|ing)|surviv(?:e|es|ed|ing)|disambiguat(?:e|es|ed|ing)|disambiguation)\b",
    re.IGNORECASE,
)
DECK_SELF_RE = re.compile(r"\bthe\s+deck\b", re.IGNORECASE)
SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s")
FIGURE_BREAKOUT_PX = 982
FIGURE_FLOOR_PX = 8.0
SVG_VIEWBOX_RE = re.compile(r'<svg\b[^>]*\bviewBox="([^"]+)"')
SVG_FONT_RE = re.compile(r'<text\b[^>]*\bfont-size="([\d.]+)"')
DECK_BOOK_RE = re.compile(r"\b(the|this) book('s)?\b", re.IGNORECASE)
DECK_SLIDE_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")
DECK_FIELD_RE = re.compile(r"<a:fld\b.*?</a:fld>", re.DOTALL)
DECK_PARA_RE = re.compile(r"<a:p\b.*?</a:p>|<a:p/>", re.DOTALL)
DECK_RUN_RE = re.compile(r"<a:t(?:\s[^>]*)?>(.*?)</a:t>", re.DOTALL)
DECK_BG_RE = re.compile(r'<p:bg>.*?<a:srgbClr val="([0-9A-Fa-f]{6})"', re.DOTALL)
DECK_NOTES_REL_RE = re.compile(r'Target="[^"]*notesSlides/(notesSlide\d+\.xml)"')


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


def check_figure_legibility(rel: str, svg: str) -> list[Finding]:
    """The smallest label, scaled to the breakout width, must be at least the floor."""
    box = SVG_VIEWBOX_RE.search(svg)
    if box is None:
        return [Finding(rel, 1, "svg has no viewBox")]
    parts = box.group(1).replace(",", " ").split()
    try:
        width = float(parts[2])
    except IndexError, ValueError:
        return [Finding(rel, 1, f"viewBox {box.group(1)!r} has no width")]
    sizes = [float(m) for m in SVG_FONT_RE.findall(svg)]
    if not sizes or width <= 0:
        return []
    smallest = min(sizes) * FIGURE_BREAKOUT_PX / width
    if smallest < FIGURE_FLOOR_PX:
        return [
            Finding(
                rel,
                1,
                f"smallest label renders at {smallest:.1f} px at {FIGURE_BREAKOUT_PX} px, "
                f"floor {FIGURE_FLOOR_PX:g}",
            )
        ]
    return []


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
        # No floor (owner decision, r25 O2): length serves the reader. The ceiling stays.
        if words > MAX_WORDS:
            errors.append(Finding(rel, 1, f"prose has {words} words, above {MAX_WORDS}"))
        if kind == "pattern":
            count = text.count(SIDEBAR)
            if count != 1:
                errors.append(
                    Finding(rel, 1, f"pattern chapter has {count} ai-sidebar blocks, need 1")
                )
    return errors, warnings


# ------------------------------------------------- terse rewording checks (r26)

TESTS_LINE_RE = re.compile(r"^\s*[-*]?\s*\*Tests?:\*")
TEST_REF_RE = re.compile(r"`(test_\w+)(?:\[[^`]*\])?`")
TEST_TICK_RE = re.compile(r"`test_\w+")
FENCE_LINE_RE = re.compile(r"^\s*(```+|~~~+)")
H3_RE = re.compile(r"^###\s+(.+?)\s*$")
BUCKET_RE = re.compile(r"\*\*Bucket: (?:dissolves|survives|needs disambiguating)\.\*\*")
BUCKET_ANY_RE = re.compile(r"\*\*Bucket:")
BOLD_RE = re.compile(r"\*\*[^*]+\*\*")
RELATIVE_URL_RE = re.compile(r"\{\{\s*'([^']*)'\s*\|\s*relative_url\s*\}\}")
FORCE_RE = re.compile(r"\bforces?\b", re.IGNORECASE)
LAYOUT_H3 = ("The problem", "The solution", "How Python models it")
DETAILS_OPEN = '<details class="figure-description"'


def tests_line_findings(
    rel: str, lines: list[tuple[int, str, str | None]], defined: set[str]
) -> list[Finding]:
    """`*Tests:*` lines: position rules, and every name a defined test."""
    out: list[Finding] = []
    for i, (n, line, fence) in enumerate(lines):
        if fence is not None or not TESTS_LINE_RE.match(line):
            continue
        names = TEST_REF_RE.findall(line)
        rest = TEST_REF_RE.sub("", TESTS_LINE_RE.sub("", line, count=1))
        if not names or re.sub(r"[\s,.]|\band\b", "", rest):
            out.append(Finding(rel, n, "*Tests:* line must hold only backticked test names"))
        for name in names:
            if name not in defined:
                out.append(Finding(rel, n, f"*Tests:* names {name}, which is not a defined test"))
        if i == 0 or lines[i - 1][1].strip():
            out.append(Finding(rel, n, "*Tests:* line needs a blank line before it"))
        prior = next(((ln, fn) for _, ln, fn in reversed(lines[:i]) if ln.strip()), ("", None))
        if prior[0].lstrip().startswith("#") or prior[1] is not None:
            out.append(Finding(rel, n, "*Tests:* line must follow a paragraph, list or table"))
        if i + 1 < len(lines) and lines[i + 1][1].strip():
            out.append(Finding(rel, n, "*Tests:* line needs a blank line after it"))
    return out


def check_tests_lines(rel: str, text: str, defined: set[str]) -> list[Finding]:
    return tests_line_findings(rel, body_lines(text), defined)


def check_terse_tests(rel: str, text: str) -> list[Finding]:
    """A backticked test name on a prose line that is not a `*Tests:*` line.

    Counted on the lines `scan.sh --terse-stats` counts: tables, headings, HTML, Liquid and
    blockquote lines are skipped, as are fences and front matter.
    """
    out: list[Finding] = []
    for n, line in prose_lines(text):
        s = line.strip()
        if not s or s.startswith(("|", "#", "<", "{%", "{{", ">")):
            continue
        if TEST_TICK_RE.search(s) and not TESTS_LINE_RE.match(line):
            out.append(Finding(rel, n, "test name inside prose; move it to a *Tests:* line"))
    return out


def check_described_figures(rel: str, text: str) -> list[Finding]:
    """A `described="true"` include needs its `desc-<name>` description right after it."""
    out: list[Finding] = []
    for m in INCLUDE_RE.finditer(text):
        params = dict(PARAM_RE.findall(m.group(1)))
        if params.get("described") != "true":
            continue
        line = text.count("\n", 0, m.start()) + 1
        tail = text[m.end() :]
        nxt = re.search(r"\{%-?\s*include\s+excalidraw\.html|^##\s", tail, re.MULTILINE)
        window = tail[: nxt.start()] if nxt else tail
        want = f'id="desc-{params.get("name", "")}"'
        pos = window.find(want)
        head = window[:pos] if pos >= 0 else ""
        if pos < 0 or DETAILS_OPEN not in head or "</details>" in head or head.count("\n\n") > 2:
            out.append(Finding(rel, line, f"described figure needs {DETAILS_OPEN}> with {want}"))
    return out


def check_undescribed_figures(rel: str, text: str) -> list[Finding]:
    """In a `TERSE_DOCS` doc every figure include carries `described="true"` (its walk-through
    lives in the figure description, CLAUDE.md's spine)."""
    out: list[Finding] = []
    for m in INCLUDE_RE.finditer(text):
        params = dict(PARAM_RE.findall(m.group(1)))
        if params.get("described") != "true":
            line = text.count("\n", 0, m.start()) + 1
            out.append(
                Finding(rel, line, 'figure include needs described="true" and a description')
            )
    return out


def check_pattern_layout(rel: str, text: str) -> list[Finding]:
    """The O1 layout for a pattern chapter: one `## Pattern: <Name>` H2 per pattern."""
    out: list[Finding] = []
    lines = prose_lines(text)
    h2s = [(n, m.group(1)) for n, ln in lines if (m := H2_RE.match(ln))]
    starts = [i for i, (_, title) in enumerate(h2s) if title.startswith("Pattern: ")]
    if not starts:
        return [Finding(rel, 1, "pattern chapter has no '## Pattern: <Name>' H2")]
    titles = [t for _, t in h2s]
    why = titles.index("Why this matters") if "Why this matters" in titles else -1
    when = titles.index("When not to use it") if "When not to use it" in titles else -1
    for i in starts:
        n, title = h2s[i]
        if why < 0 or when < 0 or not why < i < when:
            msg = f"'## {title}' must sit between Why this matters and When not to use it"
            out.append(Finding(rel, n, msg))
        end = h2s[i + 1][0] if i + 1 < len(h2s) else 10**9
        block = [(ln_no, ln) for ln_no, ln in lines if n < ln_no < end]
        h3s = [(ln_no, m.group(1)) for ln_no, ln in block if (m := H3_RE.match(ln))]
        if tuple(t for _, t in h3s[:3]) != LAYOUT_H3:
            wanted = ", ".join(LAYOUT_H3)
            out.append(Finding(rel, n, f"'## {title}' must open with the H3s {wanted}, in order"))
            continue
        sol = [ln for ln_no, ln in block if h3s[1][0] < ln_no < h3s[2][0]]
        buckets = sum(len(BUCKET_RE.findall(ln)) for ln in sol)
        any_buckets = sum(len(BUCKET_ANY_RE.findall(ln)) for ln in sol)
        if buckets != 1 or any_buckets != 1:
            out.append(Finding(rel, h3s[1][0], "The solution needs exactly one Bucket line"))
        definitions = [ln for ln in sol if BOLD_RE.search(BUCKET_RE.sub("", ln))]
        if len(definitions) != 1:
            out.append(Finding(rel, h3s[1][0], "The solution needs one bold definition"))
    in_details = False
    for n, ln in lines:
        if "<details" in ln:
            in_details = True
        if "</details>" in ln:
            in_details = False
        if not in_details and ln.startswith("Read the figure"):
            out.append(Finding(rel, n, "the walk-through belongs in the figure description"))
    return out


def force_count(text: str) -> int:
    """Count "force" or "forces" (case-insensitive, whole word) in body prose.

    Excluded: front matter, fenced blocks, inline code and blockquote lines (the AI sidebar and
    quotations). Headings, tables and Liquid text count. This is the rule the r26 "force"
    budgets use. It is reported by `--force-count` and not enforced.
    """
    total = 0
    for _, line in prose_lines(text):
        if line.lstrip().startswith(">"):
            continue
        total += len(FORCE_RE.findall(INLINE_CODE_RE.sub(" ", line)))
    return total


def appendix_e_rows(text: str) -> list[tuple[int, list[str]]]:
    """Five-cell table rows (Pattern, Bucket, Force, When not, Chapter) with line numbers."""
    rows: list[tuple[int, list[str]]] = []
    for n, line in prose_lines(text):
        if not line.startswith("|"):
            continue
        line = RELATIVE_URL_RE.sub(r"\1", line)
        cells = [
            c.strip().replace("\\|", "|") for c in CELL_SPLIT_RE.split(line.strip().strip("|"))
        ]
        if len(cells) != 5 or cells[0] == "Pattern" or set(cells[0]) <= {"-", " "}:
            continue
        rows.append((n, cells))
    return rows


def squash(text: str) -> str:
    return " ".join(text.split())


def appendix_e_findings(
    rel: str, text: str, docs_by_slug: dict[str, str]
) -> tuple[list[Finding], int]:
    """Each Bucket, Force and When-not cell must appear verbatim in the chapter it links."""
    out: list[Finding] = []
    checked = 0
    for n, cells in appendix_e_rows(text):
        m = re.search(r"/docs/([\w-]+)/", cells[4])
        if not m or m.group(1) not in docs_by_slug:
            out.append(Finding(rel, n, f"row {cells[0]!r}: Chapter cell links no chapter"))
            continue
        chapter = squash(docs_by_slug[m.group(1)])
        for label, cell in zip(("Bucket", "Force", "When not"), cells[1:4], strict=True):
            if cell in ("", "-"):
                continue
            checked += 1
            if squash(cell) not in chapter:
                msg = f"row {cells[0]!r}: {label} cell is not verbatim in {m.group(1)}"
                out.append(Finding(rel, n, msg))
    return out, checked


def check_appendix_e(root: Path) -> list[Finding]:
    paths = sorted((root / "_docs").glob("45-*.md"))
    if not paths:
        return []
    docs = {p.stem: p.read_text(encoding="utf-8") for p in (root / "_docs").glob("*.md")}
    rel = f"_docs/{paths[0].name}"
    return appendix_e_findings(rel, paths[0].read_text(encoding="utf-8"), docs)[0]


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


def check_collection_front_matter(rel: str, text: str, keys: tuple[str, ...]) -> list[Finding]:
    """A collection file's front matter closes with a --- line and sets every key Jekyll needs."""
    fm, size = split_front_matter(text)
    if not size:
        return [Finding(rel, 1, "front matter is missing or never closes with a --- line")]
    missing = [key for key in keys if not fm.get(key)]
    if missing:
        return [Finding(rel, 1, f"front matter lacks {', '.join(missing)}")]
    return []


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


LINK_URL_RE = re.compile(r"https?://[^\s)\"'<>\]]+")
LINK_FILES = (
    "_docs/*.md",
    "_examples/*.md",
    "_parts/*.md",
    "bibliography.html",
    "index.html",
    "examples.html",
    "README.md",
    "examples/*/README.md",
)


def check_link_forms(rel: str, text: str) -> list[Finding]:
    """Python docs use /3/ (O6: only setup surfaces may name a minor), /latest/ only on
    typing.python.org, and canonical O'Reilly URLs."""
    out: list[Finding] = []
    for n, line in enumerate(text.split("\n"), start=1):
        for m in LINK_URL_RE.finditer(line):
            url = m.group(0)
            host = url.split("/")[2]
            if PY_DOCS_MINOR_RE.search(url) and rel not in SETUP_SURFACES:
                out.append(
                    Finding(rel, n, "docs.python.org/3.N/ link: use docs.python.org/3/ (O6)")
                )
            if "/latest/" in url and host != "typing.python.org":
                out.append(Finding(rel, n, "/latest/ outside typing.python.org"))
            if "oreilly.com/library/view/-/" in url:
                out.append(Finding(rel, n, "oreilly.com/library/view/-/ is not canonical"))
    return out


# O6 (owner, 2026-11-08): the Python version is stated only on setup surfaces. Everywhere else a
# docs link uses /3/, recorded pytest output is recorded with --no-header, and a bare version
# mention must be a fact about a feature or a measurement named in VERSION_ALLOW.
SETUP_SURFACES = frozenset(
    {
        "_docs/00-prerequisites.md",
        "_docs/41-appendix-a-build-and-toolchain.md",
        "README.md",
        "index.html",
        "examples.html",
        "examples/README.md",
        "examples/00-prerequisites/README.md",
        "_examples/00-prerequisites.md",
    }
)
PY_DOCS_MINOR_RE = re.compile(r"docs\.python\.org/3\.\d+/")
PYTEST_HEADER_RE = re.compile(r"^platform linux -- Python 3\.\d+")
VERSION_MENTION_RE = re.compile(r"(?<![\w./-])3\.1\d(?:\.\d+)?t?(?!\w|\.\d)")
VERSION_ALLOW: dict[str, tuple[str, ...]] = {
    "_docs/02-what-1994-assumed-and-python-dissolves.md": ("new in 3.12",),
    "_docs/09-protocol-and-structural-typing.md": (
        "new in 3.15",
        "Python 3.15 adds a `sentinel`",
        "On 3.15 there is a deprecation",
        "What's New in Python 3.15",
    ),
    "_docs/10-context-managers.md": (
        "changed in Python 3.15",
        "Python 3.15 makes UTF-8",
        "Python 3.15 changed what",
        "What's New in Python 3.15",
        "witnesses the 3.15 behaviour",
        "the latest 3.14 release",
        "On 3.15.2 it printed",
        "only the 3.15 behaviour",
    ),
    "_docs/11-testing-with-pytest-pytest-mock-and-mypy.md": ("a Python 3.15 deprecation",),
    "_docs/12-strategy-the-callable.md": ("new in 3.15",),
    "_docs/14-state-and-finite-state-machines.md": (
        "new in 3.15",
        "under Python 3.15.2 printed",
        "on Python 3.15.2 that",
    ),
    "_docs/15-command-undo-and-command-queues.md": (
        "Python 3.15 adds the type",
        "What's New page for 3.15",
        "[3.15 What's New]",
    ),
    "_docs/16-factory-method-and-abstract-factory.md": ("that Python 3.15 adds",),
    "_docs/17-builder-dataclasses-and-prototype.md": (
        "in version 3.13",
        "on Python 3.15.2, `copy.deepcopy",
    ),
    "_docs/18-singleton-module-borg-metaclass.md": (
        "Python 3.15 adds a second rung",
        "What's New page for 3.15",
        "that Python 3.15 adds",
    ),
    "_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md": (
        "889.35, 3.15 short",
        "consignment is 3.15 short",
    ),
    "_docs/21-composite-and-flyweight.md": (
        "on Python 3.15.2 on 5 November",
        "on CPython 3.15.2 that",
    ),
    "_docs/22-observer.md": ("A run on Python 3.15.2 of",),
    "_docs/24-iterator-generators-and-the-iterator-protocol.md": (
        "added in 3.12",
        "`strict` in 3.13",
    ),
    "_docs/25-visitor-memento-interpreter.md": ("lazily since 3.14",),
    "_docs/26-decorators-done-right.md": (
        "since Python 3.14",
        "On 3.15.2 `functools",
        "page for 3.15.2 still",
    ),
    "_docs/27-descriptors-and-properties.md": ("and on 3.15.2 the message", "New in 3.12"),
    "_docs/28-singledispatch.md": ("accepted since 3.11",),
    "_docs/29-metaclasses-init-subclass-and-registries.md": ("on the 3.15 branch",),
    "_docs/30-dynamic-attributes-and-proxy.md": (
        "On 3.15.2, `history.stauts",
        "On 3.15 the importing side",
    ),
    "_docs/31-shortcut-patterns-dict-dispatch-and-eafp.md": (
        "new in 3.15",
        "on Python 3.15.2 (best",
    ),
    "_docs/33-seams-in-python.md": ("Python 3.15.2's `unittest.mock`",),
    "_docs/37-the-gil-and-performance.md": (
        "the 3.14 release",
        "recorded probe runs on 3.15.2",
        "run on Python 3.15.2",
        "Python 3.15.2, default build",
        "Python 3.15.2, free-threading build",
        "python install 3.15.2t",
        "sync --python 3.15.2t",
    ),
    "_docs/38-asyncio-and-the-patterns.md": (
        "on Python 3.15.2 that called",
        "What's New in Python 3.15",
    ),
    "_docs/43-appendix-c-mocking.md": (
        "On Python 3.15.2 `unsafe=True`",
        "source for 3.17.0",
        "On 3.17.0 only",
    ),
    "_examples/09-protocol-and-structural-typing.md": (
        "A 3.15 `sentinel`",
        "on 3.15 an undecorated",
    ),
    "_examples/10-context-managers.md": ("## Python 3.15",),
    "_examples/12-strategy-the-callable.md": ("over a 3.15 `frozendict`",),
    "_examples/27-descriptors-and-properties.md": ("since 3.12 its getter",),
    "examples/09-protocol-and-structural-typing/README.md": (
        "is a 3.15 `sentinel`",
        "On 3.15 a sub-protocol",
    ),
    "examples/10-context-managers/README.md": (
        "Python 3.15.",
        "Before 3.15 it exited",
        "asserts the 3.15",
    ),
    "examples/12-strategy-the-callable/README.md": ("over a 3.15 `frozendict`",),
    "examples/14-state-and-finite-state-machines/README.md": ("What Python 3.15 changes",),
    "examples/21-composite-and-flyweight/README.md": ("CPython 3.15.2 behaviour",),
    "examples/27-descriptors-and-properties/README.md": ("Since 3.12 the getter",),
    "examples/37-the-gil-and-performance/README.md": (
        "python install 3.15.2t",
        "sync --python 3.15.2t",
    ),
    "examples/38-asyncio-and-the-patterns/README.md": (
        "python install 3.15.2t",
        "sync --python 3.15.2t",
    ),
}


def check_pytest_header(rel: str, text: str) -> list[Finding]:
    """O6: a recorded pytest run in a fence is recorded with --no-header."""
    out: list[Finding] = []
    in_fence = False
    for n, line in enumerate(text.split("\n"), start=1):
        if line.startswith("```"):
            in_fence = not in_fence
        elif in_fence and PYTEST_HEADER_RE.match(line):
            out.append(
                Finding(rel, n, "pytest platform header in a fence: record with --no-header")
            )
    return out


REPO_PATH_PHRASE = "with the repository path shown as `<repo>`"


def check_repo_path_phrase(rel: str, text: str) -> list[Finding]:
    """O6 sweep: the phrase promising a `<repo>` path must lead into a fence that shows one.
    A run recorded with --no-header prints no rootdir, so the phrase would be stale there."""
    out: list[Finding] = []
    lines = text.split("\n")
    for n, line in enumerate(lines, start=1):
        if REPO_PATH_PHRASE not in line:
            continue
        i = n
        while i < len(lines) and not lines[i].strip():
            i += 1
        fence: list[str] = []
        if i < len(lines) and lines[i].startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                fence.append(lines[j])
                j += 1
        if not any("<repo>" in ln for ln in fence):
            msg = "'shown as `<repo>`' before a fence with no <repo> path (a --no-header run)"
            out.append(Finding(rel, n, msg))
    return out


def check_version_mentions(
    rel: str, text: str, allow: Mapping[str, tuple[str, ...]] | None = None
) -> tuple[list[Finding], set[str]]:
    """O6: a Python 3.1x or bare 3.1x mention outside the setup surfaces must sit inside an
    allowlisted phrase for that file. Returns the findings and the phrases that were used."""
    phrases = (VERSION_ALLOW if allow is None else allow).get(rel, ())
    out: list[Finding] = []
    used: set[str] = set()
    for n, line in enumerate(text.split("\n"), start=1):
        for m in VERSION_MENTION_RE.finditer(line):
            if PYTEST_MOCK_RE.search(line[: m.start()]):
                continue  # a pytest-mock package version
            covered = False
            for phrase in phrases:
                start = line.find(phrase)
                while start != -1:
                    if start <= m.start() and m.end() <= start + len(phrase):
                        covered = True
                        used.add(phrase)
                    start = line.find(phrase, start + 1)
            if not covered:
                out.append(
                    Finding(rel, n, f"version mention {m.group(0)!r} outside the setup surfaces")
                )
    return out, used


def link_form_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in LINK_FILES:
        files.extend(p for p in sorted(root.glob(pattern)) if p.is_file())
    return sorted(set(files))


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


# ------------------------------------------------------- stale versions


def pinned_minor(python_version: str) -> str:
    """The minor of an exact x.y.z pin, for example '15' from '3.15.2'."""
    parts = python_version.strip().split(".")
    return parts[1] if len(parts) >= 2 else ""


def check_stale_versions(rel: str, text: str, minor: str) -> list[Finding]:
    """Flag Python 3.N, python3.N and 3.N.M where N is older than the pinned minor.

    A newer minor (a scheduled removal such as "in Python 3.20") is not stale.

    A match preceded within 16 characters by 'since ', 'before ', 'until ' or
    'new in ' is history, not a claim about the pin, and passes.
    """
    out: list[Finding] = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        for m in STALE_RE.finditer(line):
            found = m.group(1) or m.group(2)
            if int(found) >= int(minor):
                continue  # the pin itself, or a future version named by a deprecation
            if PYTEST_MOCK_RE.search(line[: m.start()]):
                continue  # pytest-mock 3.x is a package version, not the interpreter
            window = line[max(0, m.start() - STALE_WINDOW) : m.start()].lower()
            if any(word in window for word in STALE_EXEMPT):
                continue
            out.append(Finding(rel, lineno, f"stale version {m.group(0)!r}: the pin is 3.{minor}"))
    return out


# ----------------------------------------------------------- claims audit


@dataclass(frozen=True)
class ClaimResult:
    row: int
    chapter: str
    status: str
    evidence: tuple[str, ...]
    unresolved: tuple[str, ...]
    line: int

    @property
    def resolved(self) -> bool:
        return bool(self.evidence) and not self.unresolved


def chapter_numbers(cell: str) -> list[int]:
    """Chapter numbers in a Ch cell: '9', '9, 10', '9-11'."""
    nums: list[int] = []
    for part in re.split(r"[,/&]|\band\b", cell):
        m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", part)
        if m:
            lo = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) else lo
            nums.extend(range(lo, max(lo, hi) + 1))
    return nums


def test_names(root: Path) -> set[str]:
    names: set[str] = set()
    for path in sorted(root.glob("examples/*/tests/**/*.py")):
        names.update(TEST_DEF_RE.findall(path.read_text(encoding="utf-8")))
    return names


def chapter_docs(root: Path) -> dict[int, str]:
    docs: dict[int, str] = {}
    for path in sorted((root / "_docs").glob("*.md")):
        m = re.match(r"(\d+)-", path.name)
        if m:
            docs[int(m.group(1))] = path.read_text(encoding="utf-8")
    return docs


def claim_results(
    plan_text: str,
    tests: set[str],
    docs: dict[int, str],
    steps_text: str,
    evidence_files: frozenset[str] = frozenset(),
) -> list[ClaimResult]:
    """Parse the reconciliation table and resolve every evidence token.

    Tokens are read from the 'How to verify' and 'Status' cells: a backticked
    test_* name (must be defined under examples/*/tests), 'source: <url>' (the
    URL must appear in the chapter's _docs file) and 'run: <step id>' (the id
    must be the id of a row marked done in an iteration plan's steps table,
    '| 1c | ... | done |'), or 'run: <path>' for a
    recorded run under _plans/evidence/ (the file must exist).
    """
    results: list[ClaimResult] = []
    for lineno, line in enumerate(plan_text.split("\n"), start=1):
        m = CLAIM_ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in CELL_SPLIT_RE.split(line.strip().strip("|"))]
        if len(cells) < 5:
            continue
        chapter = cells[1]
        text = " ".join(cells[3:])
        sm = CLAIM_STATUS_RE.search(cells[-1])
        status = sm.group(1) if sm else cells[-1].split(" ")[0]
        chapter_text = "\n".join(docs.get(n, "") for n in chapter_numbers(chapter))
        evidence: list[str] = []
        unresolved: list[str] = []
        for name in CLAIM_TEST_RE.findall(text):
            evidence.append(name)
            if name not in tests:
                unresolved.append(name)
        for url in CLAIM_SOURCE_RE.findall(text):
            url = url.rstrip(".,;")
            evidence.append(f"source: {url}")
            if url not in chapter_text:
                unresolved.append(f"source: {url}")
        for step in CLAIM_RUN_RE.findall(text):
            step = step.rstrip(".,;")
            evidence.append(f"run: {step}")
            if "/" in step:
                found = step in evidence_files
            else:
                row = rf"^\|\s*{re.escape(step)}\s*\|.*\|\s*(?:\*\*)?done(?:\*\*)?\s*\|\s*$"
                found = re.search(row, steps_text, re.MULTILINE) is not None
            if not found:
                unresolved.append(f"run: {step}")
        results.append(
            ClaimResult(
                int(m.group(1)), chapter, status, tuple(evidence), tuple(unresolved), lineno
            )
        )
    return results


def claim_findings(results: list[ClaimResult]) -> list[Finding]:
    """Errors: every row from CLAIMS_FIRST_ENFORCED on must resolve its evidence tokens."""
    errors: list[Finding] = []
    for r in results:
        if r.resolved or r.row < CLAIMS_FIRST_ENFORCED:
            continue
        if r.evidence:
            why = "unresolved evidence: " + ", ".join(r.unresolved)
        else:
            why = "no evidence token (test_ name, source: url or run: step)"
        errors.append(Finding(CLAIMS_REL, r.line, f"claim {r.row}: {why}"))
    return errors


def load_claims(root: Path) -> list[ClaimResult]:
    plan = root / CLAIMS_REL
    if not plan.is_file():
        return []
    steps = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted((root / "_plans").glob("r[0-9]*-plan.md"))
    )
    evidence = frozenset(
        p.relative_to(root).as_posix() for p in (root / "_plans" / "evidence").glob("*.md")
    )
    return claim_results(
        plan.read_text(encoding="utf-8"), test_names(root), chapter_docs(root), steps, evidence
    )


def claims_table(results: list[ClaimResult]) -> str:
    lines = [
        "| row | chapter | status | evidence | resolved |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in results:
        resolved = "yes" if r.resolved else "no"
        evidence = ", ".join(f"`{e}`" for e in r.evidence) or "none"
        lines.append(f"| {r.row} | {r.chapter} | {r.status} | {evidence} | {resolved} |")
    return "\n".join(lines)


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

    defined_tests = test_names(root)
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
        rep.errors.extend(check_tests_lines(rel, text, defined_tests))
        if entry.get("number") in TERSE_DOCS:
            rep.errors.extend(check_terse_tests(rel, text))
            rep.errors.extend(check_described_figures(rel, text))
            rep.errors.extend(check_undescribed_figures(rel, text))
            if kind == "pattern" and entry.get("number") not in IDIOM_DOCS:
                rep.errors.extend(check_pattern_layout(rel, text))
        rep.errors.extend(check_figure_captions(rel, text))
        rep.errors.extend(check_figure_files(root, rel, text))
        if status == "in-progress":
            rep.info.append(Finding(rel, 1, "status in-progress: prose rules not applied"))

    for folder, keys in COLLECTION_KEYS.items():
        for path in sorted((root / folder).glob("*.md")):
            rel = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
            rep.errors.extend(check_collection_front_matter(rel, text, keys))

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

    for path in sorted((root / "diagrams").glob("*.svg")):
        rel = path.relative_to(root).as_posix()
        rep.errors.extend(check_figure_legibility(rel, path.read_text(encoding="utf-8")))

    for path in em_dash_only(root):
        rel = path.relative_to(root).as_posix()
        rep.errors.extend(check_em_dash(rel, path.read_text(encoding="utf-8")))

    for path in link_form_files(root):
        rel = path.relative_to(root).as_posix()
        rep.errors.extend(check_link_forms(rel, path.read_text(encoding="utf-8")))

    seen: dict[str, set[str]] = {}
    for path in reader_facing(root):
        if path.suffix != ".svg":
            rel = path.relative_to(root).as_posix()
            rep.errors.extend(check_repo_path_phrase(rel, path.read_text(encoding="utf-8")))

    for path in reader_facing(root):
        rel = path.relative_to(root).as_posix()
        if path.suffix == ".svg" or rel in SETUP_SURFACES:
            continue
        body = path.read_text(encoding="utf-8")
        rep.errors.extend(check_pytest_header(rel, body))
        found, used = check_version_mentions(rel, body)
        rep.errors.extend(found)
        seen[rel] = used
    for rel, phrases in sorted(VERSION_ALLOW.items()):
        for phrase in phrases:
            if phrase not in seen.get(rel, set()):
                rep.errors.append(Finding(rel, 0, f"stale version allowlist phrase {phrase!r}"))

    minor = pinned_minor((root / ".python-version").read_text(encoding="utf-8"))
    for path in reader_facing(root):
        rel = path.relative_to(root).as_posix()
        rep.errors.extend(check_stale_versions(rel, path.read_text(encoding="utf-8"), minor))

    rep.errors.extend(claim_findings(load_claims(root)))
    rep.errors.extend(check_appendix_e(root))

    rep.errors.extend(check_pins(root))
    rep.errors.extend(check_decks(root))
    return rep


# ------------------------------------------------------------------ decks


def deck_text(xml: str, *, drop_fields: bool) -> str:
    """Paragraph text of a slide or notes part; slide-number fields are dropped on request."""
    if drop_fields:
        xml = DECK_FIELD_RE.sub("", xml)
    paragraphs = [
        "".join(html.unescape(r) for r in DECK_RUN_RE.findall(p)) for p in DECK_PARA_RE.findall(xml)
    ]
    return "\n".join(p for p in paragraphs if p.strip())


def deck_owner_names() -> tuple[str, ...]:
    """The account's full name and git's user.name, read now and never stored."""
    names: list[str] = []
    with contextlib.suppress(KeyError):
        names.append(pwd.getpwuid(os.getuid()).pw_gecos.split(",")[0])
    try:
        done = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True, check=False
        )
        names.append(done.stdout)
    except OSError:
        pass
    # The organisation name is the sanctioned creator, so it is never an owner hit.
    kept = (n.strip() for n in names)
    return tuple(
        dict.fromkeys(n for n in kept if len(n) >= 3 and n.casefold() != DECK_OWNER.casefold())
    )


def deck_field(xml: str, tag: str) -> str | None:
    m = re.search(rf"<{tag}(?:\s[^>]*)?>(.*?)</{tag}>", xml, re.DOTALL)
    return html.unescape(m.group(1)) if m else None


def check_deck(
    rel: str,
    path: Path,
    names: tuple[str, ...],
    rules: list[host_ids.Rule],
) -> list[Finding]:
    """Notes, metadata, banned text, host identifiers and the owner's name in one pptx."""
    out: list[Finding] = []

    def err(message: str) -> None:
        out.append(Finding(rel, 1, message))

    try:
        zf = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as exc:
        return [Finding(rel, 1, f"not a readable pptx: {exc}")]
    with zf:
        parts = {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}
    xml: dict[str, str] = {}
    for name, raw in parts.items():
        if name.endswith((".xml", ".rels")):
            try:
                xml[name] = raw.decode("utf-8")
            except UnicodeDecodeError:
                err(f"{name}: part is not UTF-8")

    slides = sorted((int(m.group(1)), n) for n in xml if (m := DECK_SLIDE_RE.search(n)))
    texts: list[tuple[str, str]] = []
    with_notes = 0
    for number, name in slides:
        body = xml[name]
        slide_text = deck_text(body, drop_fields=False)
        texts.append((f"slide {number}", slide_text))
        rels = xml.get(posixpath.join("ppt/slides/_rels", f"slide{number}.xml.rels"), "")
        m = DECK_NOTES_REL_RE.search(rels)
        notes = (
            deck_text(xml.get(f"ppt/notesSlides/{m.group(1)}", ""), drop_fields=True) if m else ""
        )
        texts.append((f"notes {number}", notes))
        bg = DECK_BG_RE.search(body.split("</p:bg>")[0] + "</p:bg>") if "<p:bg>" in body else None
        panel = number == 1 or (bg is not None and bg.group(1).upper() == DECK_PANEL_FILL)
        floor = DECK_NOTES_FLOOR_PANEL if panel else DECK_NOTES_FLOOR
        words = word_count(notes)
        if words:
            with_notes += 1
        if words < floor:
            err(f"slide {number}: notes have {words} words, floor {floor}")
    if with_notes != len(slides):
        err(f"{len(slides)} slides but {with_notes} notes slides with text")
    if not slides:
        err("no slides")

    core = xml.get("docProps/core.xml", "")
    app = xml.get("docProps/app.xml", "")
    for label, value in (
        ("creator", deck_field(core, "dc:creator")),
        ("lastModifiedBy", deck_field(core, "cp:lastModifiedBy")),
        ("company", deck_field(app, "Company")),
    ):
        if value != DECK_OWNER:
            err(f"docProps {label} is {value!r}, expected {DECK_OWNER!r}")

    for where, text in texts:
        for pattern, label in DECK_BANNED:
            if pattern.search(text):
                err(f"{where}: {label}")
    # Only the closing slide may point to the book as a whole.
    closing = f" {len(slides)}"
    for where, text in texts:
        if not where.endswith(closing) and DECK_BOOK_RE.search(text):
            err(f"{where}: book pointer")

    deck_id = DECK_NUMBER_RE.search(path.name)
    for where, text in texts:
        if where == "notes 1":
            # The cover notes may name the deck once, in their opening sentence.
            text = (
                SENTENCE_END_RE.split(text, maxsplit=1)[-1] if SENTENCE_END_RE.search(text) else ""
            )
        if DECK_SELF_RE.search(text):
            err(f"{where}: self-reference 'the deck'")
    if deck_id is not None and deck_id.group(1) in DECK_SPLIT_DECKS:
        for where, text in texts:
            if DECK_SPLIT_RE.search(text):
                err(f"{where}: three-way-split label")

    cfg = host_ids.Config()
    for name, body in xml.items():
        if host_ids.scrub_text(body, rules, cfg, "-") != body:
            err(f"{name}: host_ids filter changes this part")
        lowered = body.lower()
        if any(n.lower() in lowered for n in names):
            err(f"{name}: contains the owner's name")
    return out


def check_decks(
    root: Path,
    names: tuple[str, ...] | None = None,
    rules: list[host_ids.Rule] | None = None,
) -> list[Finding]:
    """Check every presentation/*.pptx; green when there is none."""
    decks = sorted((root / "presentation").glob("*.pptx"))
    if not decks:
        return []
    if names is None:
        names = deck_owner_names()
    if rules is None:
        rules = host_ids.all_rules(host_ids.gather(None))
    out: list[Finding] = []
    for deck in decks:
        out.extend(check_deck(deck.relative_to(root).as_posix(), deck, names, rules))
    return out


# -------------------------------------------------------------- self-test


def full_arg_spine() -> str:
    return "".join(f"## {h}\n\n" for h in SPINE["argument"])


GOOD_PATTERN = """---
title: T
---
## Why this matters

Story.

## Pattern: Mediator

### The problem

A failure.

### The solution

A **Mediator** is a hub.

**Bucket: survives.** Reason.

### How Python models it

```python
x = 1
```

Prose.

*Tests:* `test_a`, `test_b[x]`.

### Another point

More.

## When not to use it

Bullets.
"""

GOOD_DESCRIBED = """{% include excalidraw.html name="fig" caption="c" described="true" %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-fig" markdown="1">
Walk.
</div>
</details>
"""

GOOD_ROW = (
    "| Mediator | The bucket is survives. | The force is a hub. | Skip it. "
    "| [M]({{ '/docs/23-m/' | relative_url }}) |"
)


def terse_self_test(expect: Callable[[str, bool], None]) -> None:
    defined = {"test_a", "test_b", "test_c"}
    good = "Para.\n\n*Tests:* `test_a`, `test_b[x]`.\n\nNext.\n"
    expect("tests line ok", not check_tests_lines("a.md", good, defined))
    expect(
        "tests line unknown name",
        bool(check_tests_lines("a.md", good.replace("test_a", "test_zzz"), defined)),
    )
    expect(
        "tests line needs blank before",
        bool(check_tests_lines("a.md", good.replace("Para.\n\n", "Para.\n"), defined)),
    )
    expect(
        "tests line needs blank after",
        bool(check_tests_lines("a.md", good.replace("\n\nNext.", "\nNext."), defined)),
    )
    expect(
        "tests line not after heading",
        bool(check_tests_lines("a.md", "## H\n\n*Tests:* `test_a`.\n", defined)),
    )
    expect(
        "tests line not after fence",
        bool(check_tests_lines("a.md", "```\nx\n```\n\n*Tests:* `test_a`.\n", defined)),
    )
    expect(
        "tests line only names",
        bool(check_tests_lines("a.md", "Para.\n\n*Tests:* `test_a` proves it.\n", defined)),
    )
    expect(
        "tests line after a table",
        not check_tests_lines("a.md", "| a |\n| - |\n\n*Tests:* `test_a`.\n", defined),
    )

    prose_name = "Para with `test_a` inside.\n\n*Tests:* `test_a`.\n"
    expect("terse prose name flagged", len(check_terse_tests("a.md", prose_name)) == 1)
    exempt = "*Tests:* `test_a`.\n| `test_a` |\n> `test_b`\n```\ndef test_c(): ...\n```\n"
    expect("terse exempt lines", not check_terse_tests("a.md", exempt))

    expect("layout good", not check_pattern_layout("a.md", GOOD_PATTERN))
    expect(
        "layout needs a pattern H2",
        bool(check_pattern_layout("a.md", GOOD_PATTERN.replace("Pattern: ", ""))),
    )
    expect(
        "layout h3 order",
        bool(check_pattern_layout("a.md", GOOD_PATTERN.replace("The problem", "The solution"))),
    )
    expect(
        "layout missing bucket",
        bool(check_pattern_layout("a.md", GOOD_PATTERN.replace("**Bucket: survives.**", ""))),
    )
    expect(
        "layout bad bucket word",
        bool(check_pattern_layout("a.md", GOOD_PATTERN.replace("survives.", "persists."))),
    )
    two_buckets = GOOD_PATTERN.replace("Reason.", "Reason. **Bucket: dissolves.**")
    expect("layout two buckets", bool(check_pattern_layout("a.md", two_buckets)))
    expect(
        "layout needs a definition",
        bool(
            check_pattern_layout("a.md", GOOD_PATTERN.replace("A **Mediator** is", "A Mediator is"))
        ),
    )
    expect(
        "layout position",
        bool(check_pattern_layout("a.md", GOOD_PATTERN.replace("## Why this matters", "## Why"))),
    )
    read_figure = GOOD_PATTERN.replace("Story.", "Read the figure from the top.")
    expect("layout read the figure", bool(check_pattern_layout("a.md", read_figure)))
    in_details = GOOD_PATTERN.replace(
        "Story.", '<details class="figure-description">\nRead the figure from the top.\n</details>'
    )
    expect("layout read the figure in description ok", not check_pattern_layout("a.md", in_details))

    expect("described ok", not check_described_figures("a.md", GOOD_DESCRIBED))
    expect(
        "described needs desc id",
        bool(check_described_figures("a.md", GOOD_DESCRIBED.replace("desc-fig", "desc-other"))),
    )
    expect(
        "described needs details",
        bool(check_described_figures("a.md", GOOD_DESCRIBED.replace("<details", "<div"))),
    )
    plain = '{% include excalidraw.html name="fig" caption="c" %}\n'
    expect("undescribed include ignored", not check_described_figures("a.md", plain))
    expect("terse figure needs described", len(check_undescribed_figures("a.md", plain)) == 1)
    expect("terse described figure ok", not check_undescribed_figures("a.md", GOOD_DESCRIBED))

    force_text = (
        "---\nt: x\n---\nA Force and forces, `force`, reinforce.\n> a force\n```\nforce\n```\n"
    )
    expect("force count rule", force_count(force_text) == 2)

    chapter = {"23-m": "The force is a hub.   It   spans lines. Survives here. Skip it."}
    row = GOOD_ROW.replace("The bucket is survives.", "Survives here.")
    row = row.replace("The force is a hub.", "The force is a hub. It spans lines.")
    found, checked = appendix_e_findings("e.md", row, chapter)
    expect("appendix e verbatim ok", not found and checked == 3)
    drifted = row.replace("Skip it.", "Skip it now.")
    expect("appendix e drift flagged", len(appendix_e_findings("e.md", drifted, chapter)[0]) == 1)
    no_link = row.replace("/docs/23-m/", "/docs/99-x/")
    expect("appendix e missing chapter", bool(appendix_e_findings("e.md", no_link, chapter)[0]))
    header = "| Pattern | Bucket | Force | When not to use it | Chapter |\n| - | - | - | - | - |\n"
    expect("appendix e skips header", appendix_e_findings("e.md", header, chapter)[1] == 0)
    dash = row.replace("Skip it.", "-")
    expect("appendix e dash cell skipped", appendix_e_findings("e.md", dash, chapter)[1] == 2)


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
    keys = ("title", "order")
    expect("collection front matter ok", not check_collection_front_matter("e.md", clean, keys))
    flowed = '---\nlayout: example order: 5 title: "T" ---\nbody\n'
    expect(
        "collection front matter reflowed",
        bool(check_collection_front_matter("e.md", flowed, keys)),
    )
    expect(
        "collection front matter lacks a key",
        bool(check_collection_front_matter("e.md", clean, ("title", "card_title"))),
    )
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
    long_errors = check_prose("a.md", "word " * 2600, "argument", "done")[0]
    expect("long errors", any("above" in f.message for f in long_errors))
    floor_doc = full_arg_spine() + "word " * 1500 + "\n"
    floor_figure = floor_doc + '{% include excalidraw.html name="x" caption="c" %}\n'
    floor_result = check_prose("a.md", floor_figure, "argument", "done")
    expect("no floor warning at 1,500 words", not floor_result[1] and not floor_result[0])
    over_doc = full_arg_spine() + "word " * 2600 + "\n"
    expect("2,600 words errors", bool(check_prose("a.md", over_doc, "appendix", "done")[0]))
    terse_self_test(expect)

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
    spine_text = (
        "## Learning objectives\n## Why this matters\n## What you can do now\n"
        "## For deeper coverage\n"
    )
    no_close = spine_text.replace("## What you can do now\n", "")
    expect("spine close required", bool(check_spine("a.md", no_close, "argument")))
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
    table = "| Tool | Version | Role |\n| --- | --- | --- |\n| CPython | 3.15.1 | x |\n"
    table += "| uv | 0.1.0 | x |\n| ruff | 1.0.0 | x |\n"
    ci = '- uses: astral-sh/setup-uv@v10\n  with:\n    version: "0.1.0"\n'
    expect("pins agree", not pin_findings(pyproject, lock, "3.15.1", table, ci))
    bad_row = table.replace("| ruff | 1.0.0", "| ruff | 1.0.1")
    expect("chapter row mismatch", bool(pin_findings(pyproject, lock, "3.15.1", bad_row, ci)))
    bad_lock = lock.replace("1.0.0", "0.9.0")
    expect("lock mismatch", bool(pin_findings(pyproject, bad_lock, "3.15.1", table, ci)))
    expect("python mismatch", bool(pin_findings(pyproject, lock, "3.15.2", table, ci)))
    expect(
        "ci uv mismatch",
        bool(pin_findings(pyproject, lock, "3.15.1", table, ci.replace("0.1.0", "0.2.0"))),
    )

    plan = "## Verified toolchain\n\n| Item | Version |\n| --- | --- |\n"
    plan += "| CPython | 3.15.1 (released x) | d |\n| uv | 0.1.0 (d) | d |\n"
    plan += "| ruff | 1.0.0 | d |\n\n## Next\n\n| ruff | 9.9.9 | d |\n"
    expect("plan agrees", not pin_findings(pyproject, lock, "3.15.1", table, ci, plan))
    expect(
        "plan ruff mismatch",
        bool(
            pin_findings(
                pyproject,
                lock,
                "3.15.1",
                table,
                ci,
                plan.replace("| ruff | 1.0.0", "| ruff | 1.0.2"),
            )
        ),
    )
    expect(
        "plan python mismatch",
        bool(
            pin_findings(pyproject, lock, "3.15.1", table, ci, plan.replace("3.15.1 (", "3.15.0 ("))
        ),
    )

    expect("pinned minor", pinned_minor("3.15.2\n") == "15")
    stale = "Python 3.14 and python3.13 and 3.12.4 here.\n"
    expect("stale hits", len(check_stale_versions("a.md", stale, "15")) == 3)
    expect("stale pin passes", not check_stale_versions("a.md", "Python 3.15.2, 3.15.\n", "15"))
    expect(
        "stale since passes", not check_stale_versions("a.md", "Since Python 3.14 it works.", "15")
    )
    expect(
        "stale new in passes",
        not check_stale_versions("a.md", "Added (new in 3.12.1) later.", "15"),
    )
    expect("stale before passes", not check_stale_versions("a.md", "before Python 3.13 ran", "15"))
    expect(
        "stale too far fails",
        bool(check_stale_versions("a.md", "since then, much later, Python 3.14", "15")),
    )
    expect(
        "future version passes",
        not check_stale_versions("a.md", "raises TypeError in Python 3.20.", "15"),
    )
    expect("stale line number", check_stale_versions("a.md", "ok\nPython 3.9\n", "15")[0].line == 2)
    expect(
        "stale pytest-mock passes",
        not check_stale_versions("a.md", "| pytest-mock | 3.17.0 |\nplugins: mock-3.17.0", "15"),
    )
    expect("stale not in dotted", not check_stale_versions("a.md", "uv 0.13.7 and 1.3.12.1", "15"))

    claims = "| # | Ch | Claim | How | Status |\n| --- | --- | --- | --- | --- |\n"
    claims += "| 46 | 8 | old | prose only | **verified** |\n"
    claims += "| 47 | 9 | ok | `test_alpha[x-1]` and `test_beta` | **verified** |\n"
    claims += "| 48 | 9-10 | src | source: https://docs.python.org/x. | **verified** |\n"
    claims += "| 49 | 10 | miss | `test_gone` | **open** |\n"
    claims += "| 50 | 10 | bare | nothing | **open** |\n"
    claims += "| 51 | 11 | run | run: B3 | **open** |\n| 52 | 11 | run | run: Z9 | **open** |\n"
    claims += "| 53 | 11 | src | source: https://nope.example/y | **open** |\n"
    claims += "| 54 | 11 | run | run: 1c | **open** |\n"
    claims += "| 55 | 11 | rec | run: _plans/evidence/a.md | **open** |\n"
    claims += "| 56 | 11 | rec | run: _plans/evidence/gone.md | **open** |\n"
    claims += "| 57 | 11 | word | run: B4 | **open** |\n"
    claims += "| 58 | 11 | self | run: 58 | **open** |\n| 59 | 11 | hdr | run: Step | **open** |\n"
    claims += "| 60 | 11 | todo | run: T1 | **open** |\n"
    tests = {"test_alpha", "test_beta"}
    docs = {9: "x", 10: "see https://docs.python.org/x here", 11: "none"}
    res = {
        r.row: r
        for r in claim_results(
            claims,
            tests,
            docs,
            "| Step | What | Depends | Status |\n| B3 | x | - | done |\n| 1c | x | - | **done** |\n"
            "| T1 | x | - | todo |\nB4 appears only in prose",
            frozenset({"_plans/evidence/a.md"}),
        )
    }
    expect("claim rows parsed", sorted(res) == list(range(46, 61)))
    expect(
        "claim test resolved", res[47].resolved and res[47].evidence == ("test_alpha", "test_beta")
    )
    expect("claim source resolved", res[48].resolved and res[48].status == "verified")
    expect("claim test unresolved", not res[49].resolved and res[49].unresolved == ("test_gone",))
    expect("claim run", res[51].resolved and not res[52].resolved)
    expect("claim run digit id", res[54].resolved and res[54].evidence == ("run: 1c",))
    expect("claim run evidence file", res[55].resolved and not res[56].resolved)
    expect("claim run needs a steps row", not res[57].resolved)
    expect(
        "claim run ignores claim rows, headers and unfinished steps",
        not res[58].resolved and not res[59].resolved and not res[60].resolved,
    )
    expect("claim source unresolved", not res[53].resolved)
    errs = claim_findings(list(res.values()))
    expect("claims are enforced from row 1", CLAIMS_FIRST_ENFORCED == 1)
    expect(
        "claim errors include row 46 with no token and every unresolved row",
        sorted(int(e.message.split(":")[0].split()[1]) for e in errs)
        == [46, 49, 50, 52, 53, 56, 57, 58, 59, 60],
    )
    expect(
        "claim row 1 without a token is an error",
        [
            e.message.split(":")[0]
            for e in claim_findings(
                claim_results("| 1 | 2 | bare | prose only | **open** |\n", set(), {}, "")
            )
        ]
        == ["claim 1"],
    )
    table = claims_table(list(res.values()))
    expect(
        "claims table",
        "| 46 | 8 | verified | none | no |" in table
        and "| 47 | 9 | verified | `test_alpha`, `test_beta` | yes |" in table,
    )
    expect("claims chapter range", chapter_numbers("9-11") == [9, 10, 11])

    entries = parse_diagram_yaml("- name: a\n  caption: >-\n    one two\n    three\n- name: b\n")
    expect("yaml parse", len(entries) == 2 and entries[0][1]["caption"] == "one two three")

    fm, size = split_front_matter('---\ntitle: "Q"\norder: 3\n---\nbody')
    expect("front matter", fm == {"title": "Q", "order": "3"} and size == 4)

    legible = (
        '<svg viewBox="0 0 1000 500"><text font-size="9">a</text>'
        '<text font-size="13">b</text></svg>'
    )
    tiny = '<svg viewBox="0 0 1300 500"><text font-size="7.5">a</text></svg>'
    expect("figure legible passes", not check_figure_legibility("a.svg", legible))
    expect("figure too small fails", bool(check_figure_legibility("a.svg", tiny)))
    narrow = '<svg viewBox="0 0 700 300"><text font-size="7">a</text></svg>'
    expect("figure scales up to the breakout width", not check_figure_legibility("a.svg", narrow))
    expect("figure floor edge", not check_figure_legibility("a.svg", legible.replace("9", "8.2")))
    expect("figure without viewBox fails", bool(check_figure_legibility("a.svg", "<svg></svg>")))

    good_links = (
        "[a](https://docs.python.org/3/library/abc.html) "
        "[t](https://typing.python.org/en/latest/spec/) "
        "[b](https://www.oreilly.com/library/view/fluent-python/9781492056348/)"
    )
    expect("link forms pass", not check_link_forms("a.md", good_links))
    expect(
        "docs.python.org/3/ passes",
        not check_link_forms("a.md", "[a](https://docs.python.org/3/library/abc.html)"),
    )
    expect(
        "docs.python.org/3.N/ fails outside the setup surfaces",
        bool(check_link_forms("a.md", "[a](https://docs.python.org/3.15/library/abc.html)")),
    )
    expect(
        "docs.python.org/3.N/ passes on a setup surface",
        not check_link_forms(
            "_docs/00-prerequisites.md", "[a](https://docs.python.org/3.15/library/abc.html)"
        ),
    )
    header = "platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- x/python"
    expect(
        "pytest header in a fence fails",
        bool(check_pytest_header("a.md", f"```text\n{header}\n```")),
    )
    expect("pytest header outside a fence passes", not check_pytest_header("a.md", header))
    phrase = f"A fresh run, {REPO_PATH_PHRASE}:\n\n"
    no_header = phrase + "```text\ncollecting ... collected 1 item\n```\n"
    expect(
        "repo phrase before a --no-header fence fails",
        len(check_repo_path_phrase("a.md", no_header)) == 1,
    )
    with_repo = phrase + "```text\nrootdir: <repo>\n```\n"
    expect(
        "repo phrase before a fence with <repo> passes",
        not check_repo_path_phrase("a.md", with_repo),
    )
    expect(
        "repo phrase with no fence fails", bool(check_repo_path_phrase("a.md", phrase + "Text.\n"))
    )
    expect("no repo phrase passes", not check_repo_path_phrase("a.md", "A fresh run produces:\n"))
    expect(
        "pytest output without the header passes",
        not check_pytest_header("a.md", "```text\ncollecting ... collected 1 item\n```"),
    )
    allow = {"a.md": ("new in 3.15", "889.35, 3.15 short")}

    def mentions(text: str, rel: str = "a.md") -> int:
        return len(check_version_mentions(rel, text, allow)[0])

    expect("version: an allowlisted phrase passes", mentions("A frozendict, new in 3.15.") == 0)
    expect("version: a money amount phrase passes", mentions("give 889.35, 3.15 short.") == 0)
    expect("version: an incidental Python 3.15 fails", mentions("Python 3.15 differs.") == 1)
    expect("version: a bare 3.14 fails", mentions("Since 3.14 it works.") == 1)
    expect("version: the same phrase in another file fails", mentions("new in 3.15", "b.md") == 1)
    expect("version: a patch version fails", mentions("On Python 3.15.2 it ran.") == 1)
    expect("version: a free-threaded build fails", mentions("uv python install 3.15.2t") == 1)
    expect("version: a duration passes", mentions("6 failed, 25 passed in 3.13s") == 0)
    expect("version: a pytest-mock version passes", mentions("pytest-mock 3.17.0") == 0)
    expect(
        "version: a phrase must cover the whole token",
        mentions("new in 3.15.2 of it") == 1,
    )
    expect("version: two mentions need two phrases", mentions("new in 3.15 and in 3.15") == 1)
    expect(
        "/latest/ outside typing fails",
        bool(check_link_forms("a.md", "https://docs.pytest.org/en/latest/")),
    )
    expect(
        "oreilly view/-/ fails",
        bool(check_link_forms("a.md", "https://www.oreilly.com/library/view/-/9781492056348/")),
    )

    deck_self_test(expect)

    for f in failures:
        print(f"self-test FAILED: {f}", file=sys.stderr)
    print(f"self-test: {'FAILED' if failures else 'ok'}")
    return 1 if failures else 0


def write_synthetic_deck(
    path: Path,
    slides: list[tuple[str, str]],
    *,
    creator: str = DECK_OWNER,
    core_extra: str = "",
    panel: tuple[int, ...] = (),
) -> None:
    """A tiny pptx: slide text and notes text per slide, pptxgenjs-style parts."""
    ns = 'xmlns:a="a" xmlns:p="p" xmlns:dc="d" xmlns:cp="c"'
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(
            "docProps/core.xml",
            f"<cp:coreProperties {ns}><dc:creator>{creator}</dc:creator>"
            f"<cp:lastModifiedBy>{DECK_OWNER}</cp:lastModifiedBy>{core_extra}</cp:coreProperties>",
        )
        zf.writestr("docProps/app.xml", f"<Properties><Company>{DECK_OWNER}</Company></Properties>")
        for i, (text, notes) in enumerate(slides, start=1):
            bg = f'<p:bg><a:srgbClr val="{DECK_PANEL_FILL}"/></p:bg>' if i in panel else ""
            zf.writestr(
                f"ppt/slides/slide{i}.xml",
                f"<p:sld {ns}>{bg}<a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:sld>",
            )
            zf.writestr(
                f"ppt/slides/_rels/slide{i}.xml.rels",
                "<Relationships>"
                f'<Relationship Target="../notesSlides/notesSlide{i}.xml"/></Relationships>',
            )
            run = f"<a:p><a:r><a:t>{notes}</a:t></a:r></a:p>" if notes else ""
            zf.writestr(
                f"ppt/notesSlides/notesSlide{i}.xml",
                f'<p:notes {ns}>{run}<a:p><a:fld type="slidenum"><a:t>{i}</a:t></a:fld></a:p>'
                "</p:notes>",
            )


def deck_self_test(expect: Callable[[str, bool], None]) -> None:
    long = " ".join(["word"] * 95)
    short = " ".join(["word"] * 50)
    names = ("Zed Quux",)

    def run(
        slides: list[tuple[str, str]],
        *,
        panel: tuple[int, ...] = (2,),
        creator: str = DECK_OWNER,
        core_extra: str = "",
        name: str = "d.pptx",
    ) -> list[Finding]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "presentation").mkdir()
            write_synthetic_deck(
                root / "presentation" / name,
                slides,
                creator=creator,
                core_extra=core_extra,
                panel=panel,
            )
            return check_decks(root, names)

    good = [("Cover", short), ("Section", short), ("Body", long)]
    expect("deck passes", not run(good))
    expect("deck panel floor needs panel fill", bool(run(good, panel=())))
    expect("deck absent is green", not check_decks(Path("/nonexistent-root"), names))
    expect("deck empty notes", bool(run([*good[:2], ("Body", "")])))
    expect("deck short notes", bool(run([*good[:2], ("Body", short)])))
    expect("deck wrong creator", bool(run(good, creator="Someone")))
    expect("deck em dash", bool(run([*good[:2], ("Body", long + " a \u2014 b")])))
    expect("deck iteration id", bool(run([*good[:2], ("Body r22 here", long)])))
    expect(
        "deck chapter ref",
        bool(run([*good[:2], ("Body", long + " see Chapter 7")])),
    )
    expect("deck slide ref", bool(run([*good[:2], ("Body", long + " on slide 4")])))
    expect("deck positional ref", bool(run([*good[:2], ("Body", long + " the next slide shows")])))
    # The trailing good[2] keeps the bad slide off the closing position and meets its floor,
    # so each case fails only on its phrase.
    for bad in (
        "the table above",
        "as the book says",
        "as this book says",
        "this deck covers",
        "these slides rest on",
        "the dividers name it",
    ):
        expect(
            f"deck pointer: {bad}",
            bool(run([*good[:2], ("Body", long + " " + bad), good[2]])),
        )
    expect("deck pointer control", not run([*good[:2], ("Body", long), good[2]]))
    expect(
        "deck plain above",
        not run([*good[:2], ("Body", long + " a weight above 30 kg"), good[2]]),
    )
    expect(
        "deck book pointer on the closing slide",
        not run([*good, ("Body", long + " the book's site and repository")]),
    )
    expect(
        "deck this-book pointer on the closing slide",
        not run([*good, ("Body", long + " this book's site and repository")]),
    )
    expect(
        "deck positional ref 2",
        bool(run([*good[:2], ("Body", long + " the last catalogue section covers")])),
    )
    expect(
        "deck positional ok",
        not run(
            [
                *good[:2],
                (
                    "Body",
                    long + " a rule that follows from the force; it validates before it saves",
                ),
            ]
        ),
    )
    expect(
        "deck chapter pointer",
        bool(run([*good[:2], ("Body", long + " as the Observer chapter shows")])),
    )
    expect("deck appendix pointer", bool(run([*good[:2], ("Body", long + " in Appendix A")])))
    expect("deck cross-language", bool(run([*good[:2], ("Body", long + " in Java")])))
    for label in ("dissolves", "survived", "disambiguating", "disambiguation", "dissolve"):
        body = [*good[:2], ("Body", long + f" it {label} here"), good[2]]
        expect(f"deck 201 refuses label {label}", bool(run(body, name="x-201-y.pptx")))
        expect(f"deck 301 refuses label {label}", bool(run(body, name="x-301-y.pptx")))
        expect(f"deck 101 allows label {label}", not run(body, name="x-101-y.pptx"))
    expect(
        "deck 201 refuses label in slide text",
        bool(run([*good[:2], ("It dissolves", long), good[2]], name="x-201-y.pptx")),
    )
    expect("deck 201 label control", not run(good, name="x-201-y.pptx"))
    expect(
        "deck 201 near-miss words",
        not run(
            [*good[:2], ("Body", long + " a survey of dissolution"), good[2]], name="x-201-y.pptx"
        ),
    )
    expect(
        "deck refuses the deck",
        bool(run([*good[:2], ("Body", long + " the deck shows"), good[2]])),
    )
    expect(
        "deck refuses the deck in slide text",
        bool(run([*good[:2], ("The deck", long), good[2]])),
    )
    expect(
        "deck cover notes may open with the deck",
        not run([("Cover", "The deck runs in nine sections. " + short), *good[1:]]),
    )
    expect(
        "deck cover notes refuse the deck after the opening sentence",
        bool(run([("Cover", "Opening. The deck runs on. " + short), *good[1:]])),
    )
    expect(
        "deck owner name in core.xml",
        bool(run(good, core_extra="<dc:title>Zed Quux</dc:title>")),
    )
    expect(
        "deck host path",
        bool(run([*good[:2], ("Body " + "/".join(["", "home", "someone", "x"]), long)])),
    )


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if "--force-count" in argv:
        for path in sorted((ROOT / "_docs").glob("*.md")):
            print(f"{force_count(path.read_text(encoding='utf-8')):4d}  _docs/{path.name}")
        return 0
    if "--claims" in argv:
        results = load_claims(ROOT)
        print(claims_table(results))
        errors = claim_findings(results)
        for f in errors:
            print(f"error: {f}", file=sys.stderr)
        return 1 if errors else 0
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
