#!/usr/bin/env python3
"""Static checks for the book: manifest, front matter, figures, prose rules, pins.

Standard library only. Run from anywhere:

    uv run python scripts/validate.py
    uv run python scripts/validate.py --self-test

Every violation prints as `path:line: message`; the exit status is 1 if any
error was found. Warnings and info lines never change the exit status.
"""

from __future__ import annotations

import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_DOCS = 47
EM_DASH = "—"
PROSE_STATUSES = frozenset({"done", "drafted", "verified"})
MIN_WORDS = 1900
MAX_WORDS = 2500
CAPTION_MIN = 20
CAPTION_MAX = 45
SIDEBAR = '<blockquote class="ai-sidebar" markdown="1">'

XREF_RE = re.compile(r"\b(ch\.?|chapter)\s*\d+\b", re.IGNORECASE)
PDP_RE = re.compile(r"PDP-\d+")
ITER_RE = re.compile(r"\br\d{2}\b")
SPIKE_RE = re.compile(r"(?<![\w/])spikes?\b(?!/)", re.IGNORECASE)
CAPSTONE_RE = re.compile(r"capstone", re.IGNORECASE)
INCLUDE_RE = re.compile(r"\{%-?\s*include\s+excalidraw\.html\b(.*?)-?%\}", re.DOTALL)
PARAM_RE = re.compile(r'(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"')
FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*([\w+-]*)")
RAW_TOKEN_RE = re.compile(r"\{%-?\s*(raw|endraw)\s*-?%\}")
TEMPLATE_RE = re.compile(r"\{\{|\{%")
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
    errors: list[Finding]
    warnings: list[Finding]
    info: list[Finding]

    def __init__(self) -> None:
        self.errors = []
        self.warnings = []
        self.info = []


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
    count = 0
    for _, line in prose_lines(text):
        if line.lstrip().startswith("{%"):
            continue
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
    for n, line in prose_lines(text):
        for m in XREF_RE.finditer(line):
            errors.append(Finding(rel, n, f"chapter cross-reference {m.group(0)!r} in prose"))
    for n, line, _ in body_lines(text):
        if "{: .ai-sidebar}" in line:
            errors.append(Finding(rel, n, "use the blockquote markup, not {: .ai-sidebar}"))
    errors.extend(check_raw_wrapping(rel, text))
    if status in PROSE_STATUSES:
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


def check_raw_wrapping(rel: str, text: str) -> list[Finding]:
    out: list[Finding] = []
    in_raw = False
    for n, line, fence in body_lines(text):
        pos = 0
        for tok in RAW_TOKEN_RE.finditer(line):
            if fence == "python":
                out.extend(template_hits(rel, n, line[pos : tok.start()], in_raw))
            in_raw = tok.group(1) == "raw"
            pos = tok.end()
        if fence == "python":
            out.extend(template_hits(rel, n, line[pos:], in_raw))
    return out


def template_hits(rel: str, n: int, segment: str, in_raw: bool) -> list[Finding]:
    if in_raw or not TEMPLATE_RE.search(segment):
        return []
    return [Finding(rel, n, "unescaped '{{' or '{%' in python block; wrap in {% raw %}")]


def check_banned(rel: str, text: str, *, svg: bool) -> list[Finding]:
    """Em-dash, capstone, PDP ids, iteration ids and 'spike' in reader-facing text."""
    out: list[Finding] = []
    lines = text.split("\n")
    for n, line in enumerate(lines, start=1):
        if EM_DASH in line:
            out.append(Finding(rel, n, "em-dash (U+2014)"))
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


def check_pins(root: Path) -> list[Finding]:
    out: list[Finding] = []
    pyproject = root / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    for dep in data.get("dependency-groups", {}).get("dev", []):
        if isinstance(dep, str) and "==" not in dep:
            out.append(
                Finding("pyproject.toml", 1, f"dev dependency {dep!r} is not pinned with ==")
            )
    pv = root / ".python-version"
    if not pv.is_file() or not re.fullmatch(
        r"\d+\.\d+\.\d+", pv.read_text(encoding="utf-8").strip()
    ):
        out.append(Finding(".python-version", 1, "must be an exact x.y.z"))
    return out


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
    errors, _ = check_prose("a.md", doc, "pattern", "stub")
    expect("xref in prose only", len(errors) == 2)
    expect("ai-sidebar attr", bool(check_prose("a.md", "{: .ai-sidebar}\n", "argument", "stub")[0]))

    short = "---\ntitle: T\n---\nfew words\n"
    expect("short done", bool(check_prose("a.md", short, "argument", "done")[0]))
    expect("short stub ok", not check_prose("a.md", short, "argument", "stub")[0])
    expect("short in-progress ok", not check_prose("a.md", short, "argument", "in-progress")[0])
    long_body = "word " * 2000
    expect("pattern needs sidebar", bool(check_prose("a.md", long_body, "pattern", "done")[0]))
    ok = long_body + "\n" + SIDEBAR + "\n"
    expect("pattern with sidebar", not check_prose("a.md", ok, "pattern", "done")[0])
    expect("long warns", bool(check_prose("a.md", "word " * 2600, "argument", "done")[1]))

    bad = "```python\nx = '{{ a }}'\n```\n"
    good = "{% raw %}\n```python\nx = '{{ a }}'\n```\n{% endraw %}\n"
    other = "```text\n{{ a }}\n```\n"
    expect("raw missing", bool(check_raw_wrapping("a.md", bad)))
    expect("raw wrapped", not check_raw_wrapping("a.md", good))
    expect("non-python ignored", not check_raw_wrapping("a.md", other))

    expect("caption short", bool(caption_findings("a", 1, "too short")))
    expect("caption todo", bool(caption_findings("a", 1, "TODO " + "word " * 25)))
    expect("caption ok", not caption_findings("a", 1, "word " * 25))
    inc = '{% include excalidraw.html name="x" caption="short" %}'
    expect("include caption parsed", bool(check_figure_captions("a.md", inc)))

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
