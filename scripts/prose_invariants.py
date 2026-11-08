#!/usr/bin/env python3
"""Prose invariants: what a rewording of a chapter must not lose.

Compares each doc in the reworded set with the same doc at a base revision and
fails on any difference in the protected content, unless a signed waiver in
the evidence file covers it. It needs git history for the base revision, so it
is separate from validate.py, which runs on a shallow checkout.

Protected:
  fence         fenced blocks, byte-exact, as a multiset (an order change is a note)
  test          test names (test_*) as a set, wherever they sit in prose
  link          link targets: Markdown links, bare URLs, relative_url targets, hrefs
  source        `source:` URLs of the doc's reconciliation rows still in the doc
  quote         quoted strings of 6 or more words, byte-exact, as a set
  number        digit tokens in prose, as a multiset
  code          inline code spans, as a set
  sidebar       the AI sidebar block, byte-exact
  caption       the figure include's caption
  front-matter  every front matter key except `description`

Allowed without a waiver: a test name moved onto a `*Tests:*` line, framing
deleted, paragraphs and sections reordered, prose turned into a table or list,
a walk-through moved into the figure description.

Waivers: one table in the evidence file, `| doc | kind | value | reason | signed |`.
A row without a reason and a signature is ignored. The value is the exact lost
value; a leading `+` means the value was added. A multiset kind needs one row
per occurrence.

Usage:
  prose_invariants.py [--base REV] [--all | DOC ...]   compare (default docs: the reworded set)
  prose_invariants.py --sections [DOC ...]             per-H3 report for the terse targets
  prose_invariants.py --baseline [--base REV] [DOC ...] invariant counts at the base revision
  prose_invariants.py --self-test
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate import (
    FENCE_RE,
    HTML_TAG_RE,
    INLINE_CODE_RE,
    LIQUID_RE,
    URL_RE,
)

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "_docs"
EVIDENCE = ROOT / "_plans" / "evidence" / "r26-pilot.md"
RECONCILIATION = ROOT / "_plans" / "reconciliation-plan.md"
DEFAULT_BASE = "15cc747"

# Docs the rewording has finished or is working on; r27 and r28 extend it.
REWORDED_DOCS: tuple[int, ...] = (1, 3, 23, 24)

KINDS = (
    "fence",
    "test",
    "link",
    "source",
    "quote",
    "number",
    "code",
    "sidebar",
    "caption",
    "front-matter",
)
MIN_QUOTE_WORDS = 6

# O6 (owner, 2026-11-08): the Python version is stated only on setup surfaces. These patterns
# normalise the base text before the comparison, and nothing else.
O6_LINK_RE = re.compile(r"docs\.python\.org/3\.15/")
O6_HEADER_RE = re.compile(
    r"(?m)^(=+ test session starts =+\n)"
    r"platform linux[ ]--[ ]Python 3\.\d+[^\n]*\n"
    r"(?:cachedir: [^\n]*\n)?(?:rootdir: [^\n]*\n)?(?:configfile: [^\n]*\n)?(?:plugins: [^\n]*\n)?"
)
O6_HAS_HEADER_RE = re.compile(r"(?m)^platform linux[ ]--[ ]Python 3\.\d+")
O6_TIMING_RE = re.compile(r"(?m)^(=+ .*\b(?:passed|failed|skipped)\b.* in )[0-9.]+(s =+)$")
O6_CMD_RE = re.compile(r"(?m)^uv run pytest -v$")
O6_CMD_INLINE = "`uv run pytest -v` runs"
O6_FLAG = "--no-header"

TEST_RE = re.compile(r"\btest_\w+")
MD_LINK_RE = re.compile(r"\]\(([^)]*)\)")
REL_URL_RE = re.compile(r"""['"]([^'"]+)['"]\s*\|\s*relative_url""")
HREF_RE = re.compile(r'href="([^"]+)"')
BARE_URL_RE = re.compile(r"""https?://[^\s)<>"'`]+""")
SIDEBAR_RE = re.compile(r'<blockquote class="ai-sidebar".*?</blockquote>', re.DOTALL)
CAPTION_RE = re.compile(r'caption="((?:[^"\\]|\\.)*)"')
QUOTE_RES = (re.compile(r'"([^"]+)"'), re.compile(r"“([^”]+)”"))
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")
LIST_MARKER_RE = re.compile(r"^\s*\d+[.)]\s+")
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
SOURCE_RE = re.compile(r"source:\s*(https?://[^\s`,|)]+)")
WALKTHROUGH_RE = re.compile(r"^Read the figure from the top down\.")
TABLE_SEP_RE = re.compile(r"^\|?[\s:|-]+\|?$")


@dataclass(frozen=True)
class Finding:
    kind: str
    value: str
    sign: str  # "-" lost, "+" added
    count: int = 1

    def waiver_value(self) -> str:
        return self.value if self.sign == "-" else "+" + self.value

    def show(self) -> str:
        v = self.value.replace("\n", "\\n")
        v = v if len(v) <= 110 else v[:107] + "..."
        n = f" x{self.count}" if self.count > 1 else ""
        return f"{self.kind}: {'lost' if self.sign == '-' else 'added'} {v!r}{n}"


@dataclass(frozen=True)
class Waiver:
    doc: int
    kind: str
    value: str
    reason: str
    signed: str


@dataclass
class Facts:
    front_matter: dict[str, str] = field(default_factory=dict)
    fences: list[str] = field(default_factory=list)
    prose: list[str] = field(default_factory=list)
    tests: set[str] = field(default_factory=set)
    links: set[str] = field(default_factory=set)
    urls: set[str] = field(default_factory=set)
    relative: set[str] = field(default_factory=set)
    quotes: set[str] = field(default_factory=set)
    numbers: Counter[str] = field(default_factory=Counter)
    numbers_with_tags: int = 0
    codes: set[str] = field(default_factory=set)
    sidebars: list[str] = field(default_factory=list)
    captions: list[str] = field(default_factory=list)
    walkthroughs: int = 0


def parse_front_matter(text: str) -> tuple[dict[str, str], list[str]]:
    """Return (key -> raw value, body lines). Continuation lines join their key."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, lines
    fm: dict[str, str] = {}
    key: str | None = None
    for idx in range(1, len(lines)):
        line = lines[idx]
        if line.strip() == "---":
            return fm, lines[idx + 1 :]
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fm[key] = m.group(2)
        elif key is not None:
            fm[key] += "\n" + line
    return fm, lines


def split_blocks(body: list[str]) -> tuple[list[str], list[str]]:
    """Split body lines into (fenced blocks, prose lines)."""
    fences: list[str] = []
    prose: list[str] = []
    cur: list[str] = []
    fence: str | None = None
    for line in body:
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[0]
                cur = [line]
            else:
                prose.append(line)
        else:
            cur.append(line)
            if m and m.group(1)[0] == fence and not m.group(2):
                fences.append("\n".join(cur))
                fence = None
                cur = []
    if fence is not None:
        fences.append("\n".join(cur))
    return fences, prose


def paragraphs(prose: list[str]) -> list[str]:
    """Prose joined into blank-line paragraphs, blockquote markers dropped."""
    out: list[str] = []
    cur: list[str] = []
    for line in prose:
        stripped = re.sub(r"^\s*>\s?", "", line)
        if stripped.strip():
            cur.append(stripped)
        elif cur:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def extract(text: str) -> Facts:
    fm, body = parse_front_matter(text)
    fences, prose = split_blocks(body)
    f = Facts(front_matter=fm, fences=fences, prose=prose)
    joined = "\n".join(prose)
    f.tests = {
        m.group(0) for m in TEST_RE.finditer(joined) if joined[m.end() : m.end() + 3] != ".py"
    }
    f.codes = set(INLINE_CODE_RE.findall(joined))
    f.sidebars = SIDEBAR_RE.findall(joined)
    f.captions = CAPTION_RE.findall(joined)
    for target in MD_LINK_RE.findall(joined):
        if "relative_url" not in target:
            f.links.add(target.strip())
    for target in REL_URL_RE.findall(joined):
        f.relative.add(target)
    for target in HREF_RE.findall(joined):
        f.links.add(target)
    for url in BARE_URL_RE.findall(joined):
        f.urls.add(url.rstrip(".,;:"))
    f.links |= f.urls | {"relative_url:" + r for r in f.relative}
    # quotes: outside code spans, Liquid and HTML tags
    for para in paragraphs(prose):
        clean = INLINE_CODE_RE.sub(" ", para)
        clean = LIQUID_RE.sub(" ", clean)
        clean = HTML_TAG_RE.sub(" ", clean)
        for rx in QUOTE_RES:
            for q in rx.findall(clean):
                if len(q.split()) >= MIN_QUOTE_WORDS:
                    f.quotes.add(q)
        if WALKTHROUGH_RE.match(para):
            f.walkthroughs += 1
    # numbers: prose without code spans and Liquid tags. Link targets and URLs stay in
    # (a changed URL then shows twice, which is harmless); HTML tags go, so the
    # figure description's wrapper (an id with the figure name) adds no digits.
    for line in prose:
        line = LIST_MARKER_RE.sub("", line)
        line = INLINE_CODE_RE.sub(" ", line)
        line = LIQUID_RE.sub(" ", line)
        f.numbers_with_tags += len(NUMBER_RE.findall(line))
        line = HTML_TAG_RE.sub(" ", line)
        f.numbers.update(NUMBER_RE.findall(line))
    return f


Check = Callable[[Facts, Facts], list[Finding]]


def _set_diff(kind: str, a: set[str], b: set[str]) -> list[Finding]:
    return [Finding(kind, v, "-") for v in sorted(a - b)] + [
        Finding(kind, v, "+") for v in sorted(b - a)
    ]


def check_fence(a: Facts, b: Facts) -> list[Finding]:
    ca, cb = Counter(a.fences), Counter(b.fences)
    out: list[Finding] = []
    for v in sorted(ca.keys() | cb.keys()):
        d = ca[v] - cb[v]
        if d:
            out.append(Finding("fence", v, "-" if d > 0 else "+", abs(d)))
    return out


def check_test(a: Facts, b: Facts) -> list[Finding]:
    return _set_diff("test", a.tests, b.tests)


def check_link(a: Facts, b: Facts) -> list[Finding]:
    return _set_diff("link", a.links, b.links)


def check_quote(a: Facts, b: Facts) -> list[Finding]:
    return _set_diff("quote", a.quotes, b.quotes)


def check_number(a: Facts, b: Facts) -> list[Finding]:
    out: list[Finding] = []
    for v in sorted(a.numbers.keys() | b.numbers.keys()):
        d = a.numbers[v] - b.numbers[v]
        if d:
            out.append(Finding("number", v, "-" if d > 0 else "+", abs(d)))
    return out


def check_code(a: Facts, b: Facts) -> list[Finding]:
    return _set_diff("code", a.codes, b.codes)


def check_sidebar(a: Facts, b: Facts) -> list[Finding]:
    if a.sidebars == b.sidebars:
        return []
    return _set_diff("sidebar", set(a.sidebars), set(b.sidebars)) or [
        Finding("sidebar", "order or count changed", "-")
    ]


def check_caption(a: Facts, b: Facts) -> list[Finding]:
    if a.captions == b.captions:
        return []
    return _set_diff("caption", set(a.captions), set(b.captions)) or [
        Finding("caption", "order or count changed", "-")
    ]


def check_front_matter(a: Facts, b: Facts) -> list[Finding]:
    fa = {k: v for k, v in a.front_matter.items() if k != "description"}
    fb = {k: v for k, v in b.front_matter.items() if k != "description"}
    out: list[Finding] = []
    for k in sorted(fa.keys() | fb.keys()):
        if fa.get(k) != fb.get(k):
            out.append(Finding("front-matter", k, "-" if k in fa else "+"))
    return out


CHECKS: dict[str, Check] = {
    "fence": check_fence,
    "test": check_test,
    "link": check_link,
    "quote": check_quote,
    "number": check_number,
    "code": check_code,
    "sidebar": check_sidebar,
    "caption": check_caption,
    "front-matter": check_front_matter,
}


def check_sources(sources: list[str], after: Facts) -> list[Finding]:
    return [Finding("source", s, "-") for s in sources if s not in after.urls]


SOURCE_CHECKS: dict[str, Callable[[list[str], Facts], list[Finding]]] = {"source": check_sources}


@dataclass
class Result:
    failures: list[Finding]
    waived: list[Finding]
    notes: list[str]
    unused_waivers: list[Waiver]


def o6_mask_timing(text: str) -> str:
    """The pytest summary duration is re-recorded with each run, so it never differs."""
    return O6_TIMING_RE.sub(r"\g<1>0.00\g<2>", text)


def o6_normalise(base_text: str, after_text: str) -> tuple[str, bool]:
    """Owner decision O6 as two transforms of the base text, each applied only where the doc
    has taken it, so a setup surface that keeps its version still compares byte for byte:

    1. `docs.python.org/3.15/` becomes `docs.python.org/3/` (when the doc has no /3.15/ link left).
    2. The pytest header block (platform, cachedir, rootdir, configfile, plugins) is dropped from
       a recorded fence, and `uv run pytest -v` gains `--no-header` where it introduces the fence
       (when the doc has no header line left). The summary duration is masked on both sides.

    Returns the normalised base and whether the doc has taken O6.
    """
    out = base_text
    taken = False
    if "docs.python.org/3.15/" not in after_text and O6_LINK_RE.search(out):
        out = O6_LINK_RE.sub("docs.python.org/3/", out)
        taken = True
    if not O6_HAS_HEADER_RE.search(after_text) and O6_HEADER_RE.search(out):
        out = O6_HEADER_RE.sub(r"\g<1>", out)
        if O6_FLAG in after_text:
            out = O6_CMD_RE.sub("uv run pytest -v " + O6_FLAG, out)
            out = out.replace(O6_CMD_INLINE, "`uv run pytest -v " + O6_FLAG + "` runs")
        taken = True
    return out, taken


def compare(
    base_text: str,
    after_text: str,
    waivers: list[Waiver] | None = None,
    sources: list[str] | None = None,
) -> Result:
    """Pure comparison of two doc texts. No git, no files."""
    base_text, taken = o6_normalise(base_text, after_text)
    if taken:
        sources = [s.replace("docs.python.org/3.15/", "docs.python.org/3/") for s in sources or []]
    a = extract(o6_mask_timing(base_text))
    b = extract(o6_mask_timing(after_text))
    found: list[Finding] = []
    for check in CHECKS.values():
        found += check(a, b)
    for source_check in SOURCE_CHECKS.values():
        # Only sources the base doc itself carried can be required of the new one.
        found += source_check([s for s in (sources or []) if s in a.urls], b)
    notes: list[str] = []
    if "fence" in CHECKS and Counter(a.fences) == Counter(b.fences) and a.fences != b.fences:
        notes.append("fence order changed (same blocks, new sequence)")
    budget: Counter[tuple[str, str]] = Counter((w.kind, w.value) for w in (waivers or []))
    used: Counter[tuple[str, str]] = Counter()
    failures: list[Finding] = []
    waived: list[Finding] = []
    for fd in found:
        key = (fd.kind, fd.waiver_value())
        take = min(fd.count, budget[key])
        budget[key] -= take
        used[key] += take
        if take == fd.count:
            waived.append(fd)
        else:
            failures.append(Finding(fd.kind, fd.value, fd.sign, fd.count - take))
    unused = [w for w in (waivers or []) if used[(w.kind, w.value)] == 0]
    return Result(failures, waived, notes, unused)


def parse_waivers(evidence: str) -> tuple[list[Waiver], list[str]]:
    """Read the waiver table. Returns (signed waivers, notes on ignored rows)."""
    waivers: list[Waiver] = []
    notes: list[str] = []
    in_section = False
    for line in evidence.split("\n"):
        if line.startswith("## "):
            in_section = line.strip().lower() == "## waivers"
            continue
        if not in_section or not line.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if len(cells) != 5 or cells[0].lower() == "doc" or TABLE_SEP_RE.match(line.strip()):
            continue
        doc_s, kind, value, reason, signed = cells
        m = re.match(r"\d+", doc_s)
        value = value.strip("`")
        bare = value.removeprefix("+")
        if not m or kind not in KINDS or not bare:
            notes.append(f"waiver row ignored (doc or kind not valid): {line.strip()[:80]}")
        elif not reason or signed.lower() in {"", "-", "no", "none", "pending", "todo"}:
            notes.append(f"unsigned waiver ignored: doc {doc_s} {kind} {value[:50]!r}")
        else:
            waivers.append(Waiver(int(m.group(0)), kind, value, reason, signed))
    return waivers, notes


def git_show(base: str, path: str) -> str:
    out = subprocess.run(
        ["git", "show", f"{base}:{path}"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        raise SystemExit(f"cannot read {path} at {base}: {out.stderr.strip()}")
    return out.stdout


def doc_path(num: int) -> Path:
    found = sorted(DOCS_DIR.glob(f"{num:02d}-*.md"))
    if len(found) != 1:
        raise SystemExit(f"doc {num}: expected one _docs/{num:02d}-*.md, found {len(found)}")
    return found[0]


def reconciliation_sources(text: str, num: int) -> list[str]:
    """`source:` URLs of the rows whose chapter column is `num`."""
    out: list[str] = []
    for line in text.split("\n"):
        cells = line.split("|")
        if len(cells) > 5 and cells[2].strip() == str(num):
            out += [u.rstrip(".") for u in SOURCE_RE.findall(line)]
    return out


# ---------------------------------------------------------------- sections


def _words(line: str) -> int:
    line = LIQUID_RE.sub(" ", line)
    line = INLINE_CODE_RE.sub(" ", line)
    line = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = URL_RE.sub(" ", line)
    line = HTML_TAG_RE.sub(" ", line)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'_-]*", line))


def _is_block_start(line: str) -> bool:
    s = line.lstrip()
    return s.startswith("|") or "include excalidraw.html" in s


def _sentences(lines: list[str]) -> int:
    n = 0
    for ln in lines:
        s = ln.strip()
        if (
            not s
            or s.startswith(("|", "-", "*Tests:*", "{%", "<", "**Bucket"))
            or re.match(r"\d+\.", s)
        ):
            continue
        s = INLINE_CODE_RE.sub("x", s)
        n += len(re.findall(r"[.!?](?=\s|$)", s))
    return n


@dataclass
class Section:
    h2: str
    h3: str
    words: int
    lead: int
    sentences: int
    bullets: int
    has_block: bool
    flags: list[str]


def sections(text: str) -> list[Section]:
    """Per-H3 rows (and H2 rows that hold prose of their own)."""
    _, body = parse_front_matter(text)
    fences, _ = split_blocks(body)
    raw: list[tuple[str, str, list[tuple[str, bool]]]] = []
    h2 = ""
    cur: list[tuple[str, bool]] | None = None
    fence: str | None = None
    for line in body:
        m = FENCE_RE.match(line)
        if fence is not None:
            if cur is not None:
                cur.append((line, True))
            if m and m.group(1)[0] == fence and not m.group(2):
                fence = None
            continue
        if m:
            fence = m.group(1)[0]
            if cur is not None:
                cur.append((line, True))
            continue
        h = HEADING_RE.match(line)
        if h:
            if h.group(1) == "##":
                h2 = h.group(2)
            cur = []
            raw.append((h2, h.group(2) if h.group(1) == "###" else "", cur))
            continue
        if cur is not None:
            cur.append((line, False))
    del fences
    out: list[Section] = []
    h2_has_h3 = {r[0] for r in raw if r[1]}
    for h2n, h3n, lines in raw:
        if not h3n and h2n in h2_has_h3 and not any(not c and ln.strip() for ln, c in lines):
            continue
        words = lead = 0
        has_block = False
        prose = [ln for ln, c in lines if not c]
        for ln, c in lines:
            if c or _is_block_start(ln):
                has_block = True
            if not c and not ln.lstrip().startswith("|"):
                words += _words(ln)
                if not has_block:
                    lead += _words(ln)
        bullets = sum(
            1 for ln in prose if re.match(r"\s*[-*] ", ln) and not ln.startswith("*Tests")
        )
        sec = Section(h2n, h3n, words, lead, _sentences(prose), bullets, has_block, [])
        if h2n.startswith("Pattern:") and h3n:
            if h3n == "The problem":
                if sec.sentences > 3:
                    sec.flags.append("problem over 3 sentences")
            elif h3n == "The solution":
                if sec.sentences > 2:
                    sec.flags.append("solution over 2 sentences plus the Bucket line")
            else:
                if sec.lead > 60 or not sec.has_block:
                    sec.flags.append(
                        "lead-in over 60 words" if sec.has_block else "no code, table or figure"
                    )
                if sec.words > 150:
                    sec.flags.append("section over 150 words")
        out.append(sec)
    return out


def print_sections(num: int, text: str) -> None:
    print(f"\n{doc_path(num).name}")
    print(f"{'WORDS':>6} {'LEAD':>5} {'SENT':>5} {'BUL':>4}  H2 / H3  FLAGS")
    for s in sections(text):
        name = f"{s.h2} / {s.h3}" if s.h3 else s.h2
        flags = "; ".join(s.flags)
        lead = s.lead if s.has_block else f"{s.lead}*"
        print(f"{s.words:>6} {lead!s:>5} {s.sentences:>5} {s.bullets:>4}  {name}  {flags}")
    print("(* = no code, table or figure in the section)")


# ---------------------------------------------------------------- baseline


def baseline_row(num: int, text: str) -> str:
    f = extract(text)
    return (
        f"| {num:02d} | {len(f.fences)} | {len(f.tests)} | {len(f.urls)} | {len(f.relative)} "
        f"| {len(f.quotes)} | {sum(f.numbers.values())} | {f.numbers_with_tags} "
        f"| {f.walkthroughs} |"
    )


# ---------------------------------------------------------------- self-test

BASE_DOC = """---
title: "Clearance"
order: 99
layout: tutorial
description: "Old description."
---

## Why this matters

The bucket is a decision. A customs declaration waits for 3 reports, and
the stage `check_documents` runs first. Read it at [the PEP](https://peps.python.org/pep-0255/).

Next, `test_a_clean_declaration_is_released` shows it, and the docs say
"If the iterator is exhausted, StopIteration is raised." Speed is 40 percent.

{% include excalidraw.html name="99-x" caption="Figure 99.1: A declaration moves along stages." %}

## Body

First paragraph about duty.

Second paragraph about inspection.

```python
def clear(d):
    return d
```

<blockquote class="ai-sidebar" markdown="1">
**Specifying a chain.** State the final stage.
</blockquote>

See [the split]({{ '/docs/03-the-three-way-split/' | relative_url }}).
"""


def _sub(old: str, new: str) -> str:
    assert old in BASE_DOC, old
    return BASE_DOC.replace(old, new, 1)


Case = tuple[str, str, str | None, list[Waiver]]  # label, after text, expected kind or None


def _cases() -> list[Case]:
    framing = "The bucket is a decision. "
    moved = _sub(
        "Next, `test_a_clean_declaration_is_released` shows it, and the docs say",
        "Next, the docs say",
    ).replace("## Body", "*Tests:* `test_a_clean_declaration_is_released`\n\n## Body", 1)
    swapped = _sub(
        "First paragraph about duty.\n\nSecond paragraph about inspection.",
        "Second paragraph about inspection.\n\nFirst paragraph about duty.",
    )
    as_table = _sub(
        "Second paragraph about inspection.",
        "| stage | role |\n| --- | --- |\n| inspection | second |",
    )
    walk_moved = _sub(
        "First paragraph about duty.",
        '<details class="figure-description"><summary>Describe the figure</summary>\n'
        "First paragraph about duty.\n</details>",
    )
    waiver_num = Waiver(99, "number", "40", "folded into the table", "reader")
    dropped_num = _sub(" Speed is 40 percent.", "")
    return [
        ("a moved test name passes", moved, None, []),
        ("a deleted framing sentence passes", _sub(framing, ""), None, []),
        ("a reordered paragraph passes", swapped, None, []),
        ("prose turned into a table passes", as_table, None, []),
        ("a walk-through moved into the figure description passes", walk_moved, None, []),
        ("a changed description passes", _sub("Old description.", "New."), None, []),
        ("a signed waiver covers a removal", dropped_num, None, [waiver_num]),
        ("an unsigned waiver covers nothing", dropped_num, "number", []),
        ("a changed fenced block fails", _sub("return d", "return d + 1"), "fence", []),
        (
            "a dropped fenced block fails",
            _sub("```python\ndef clear(d):\n    return d\n```\n", ""),
            "fence",
            [],
        ),
        (
            "a dropped test name fails",
            _sub("`test_a_clean_declaration_is_released`", "the test"),
            "test",
            [],
        ),
        (
            "a dropped link fails",
            _sub("[the PEP](https://peps.python.org/pep-0255/)", "the PEP"),
            "link",
            [],
        ),
        (
            "a dropped relative_url target fails",
            _sub(
                "{{ '/docs/03-the-three-way-split/' | relative_url }}",
                "{{ '/docs/03/' | relative_url }}",
            ),
            "link",
            [],
        ),
        (
            "a paraphrased long quotation fails",
            _sub("StopIteration is raised.", "an error is raised."),
            "quote",
            [],
        ),
        ("a dropped number fails", dropped_num, "number", []),
        ("a changed number fails", _sub("3 reports", "4 reports"), "number", []),
        (
            "a dropped inline code span fails",
            _sub("`check_documents`", "the first check"),
            "code",
            [],
        ),
        (
            "an edited sidebar fails",
            _sub("State the final stage.", "State the stage."),
            "sidebar",
            [],
        ),
        ("an edited caption fails", _sub("moves along stages", "moves on"), "caption", []),
        ("an edited front matter key fails", _sub("order: 99", "order: 98"), "front-matter", []),
    ]


O6_BASE = """---
title: "T"
order: 98
layout: tutorial
description: "d"
---

## Build, run, observe

Read [the module](https://docs.python.org/3.15/library/abc.html) first.

```bash
uv run pytest -v
```

```text
============================= test session starts ==============================
platform linux @@ Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 @@ <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 1 item

tests/test_a.py::test_a PASSED                                           [100%]

============================== 1 passed in 3.09s ===============================
```
""".replace("@@", "-" * 2)


def o6_self_test() -> int:
    """Each case: label, after text, expected failing kind or None, the base text."""
    link_done = O6_BASE.replace("docs.python.org/3.15/", "docs.python.org/3/")
    header = (
        "platform linux @@ Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 @@ <repo>/.venv/bin/python\n"
        "cachedir: .pytest_cache\nrootdir: <repo>\nconfigfile: pyproject.toml\n"
        "plugins: mock-3.17.0\n"
    ).replace("@@", "-" * 2)
    rerecorded = (
        link_done.replace(header, "")
        .replace("uv run pytest -v\n", "uv run pytest -v --no-header\n")
        .replace("in 3.09s", "in 3.41s")
    )
    cases: list[tuple[str, str, str | None]] = [
        ("O6: the rewritten link and the re-recorded fence pass", rerecorded, None),
        ("O6: a setup surface that keeps both passes", O6_BASE, None),
        (
            "O6: a link moved to another minor fails",
            rerecorded.replace("docs.python.org/3/", "docs.python.org/3.14/"),
            "link",
        ),
        (
            "O6: a changed test line in the fence fails",
            rerecorded.replace("test_a PASSED", "test_b PASSED"),
            "fence",
        ),
        (
            "O6: a changed result count in the fence fails",
            rerecorded.replace("1 passed", "2 passed"),
            "fence",
        ),
        (
            "O6: a flag added while the header stays fails",
            link_done.replace("uv run pytest -v\n", "uv run pytest -v --no-header\n"),
            "fence",
        ),
        (
            "O6: a header line changed while the rest is dropped fails",
            rerecorded.replace("collecting ...", "plugins: x\ncollecting ..."),
            "fence",
        ),
        (
            "O6: a dropped number still fails",
            rerecorded.replace("## Build, run, observe\n", "## Build, run, observe\n\nSee 12.\n"),
            "number",
        ),
    ]
    base_with_number = O6_BASE.replace(
        "## Build, run, observe\n", "## Build, run, observe\n\nSee 12.\n"
    )
    bad = 0
    for label, after, expect in cases:
        base = base_with_number if "number" in label else O6_BASE
        if "number" in label:
            after = rerecorded
        res = compare(base, after, [], [])
        kinds = {f.kind for f in res.failures}
        ok = (not res.failures) if expect is None else (expect in kinds)
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
        bad += not ok
    src = ["https://docs.python.org/3.15/library/abc.html"]
    res = compare(O6_BASE, rerecorded, [], src)
    ok = not res.failures
    print(f"  {'ok  ' if ok else 'FAIL'} O6: a reconciliation source URL follows the link rewrite")
    bad += not ok
    return bad


def self_test() -> int:
    failed = 0
    base_sources = ["https://peps.python.org/pep-0255/"]
    for label, after, expect, waivers in _cases():
        res = compare(BASE_DOC, after, waivers, base_sources)
        kinds = {f.kind for f in res.failures}
        ok = (not res.failures) if expect is None else (expect in kinds)
        if expect == "link" and "link" not in kinds:
            ok = False
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
        if not ok:
            failed += 1
    # source: a reconciliation URL must stay in the doc
    res = compare(
        BASE_DOC,
        _sub(
            "[the PEP](https://peps.python.org/pep-0255/)",
            "[the PEP](https://peps.python.org/pep-0256/)",
        ),
        [],
        base_sources,
    )
    ok = any(f.kind == "source" for f in res.failures)
    print(f"  {'ok  ' if ok else 'FAIL'} a source URL missing from the doc fails")
    failed += not ok
    # the identity comparison finds nothing
    res = compare(BASE_DOC, BASE_DOC, [], base_sources)
    ok = not res.failures and not res.notes
    print(f"  {'ok  ' if ok else 'FAIL'} an unchanged doc reports no change")
    failed += not ok
    # waiver table: only signed rows count
    table = (
        "## Waivers\n\n| doc | kind | value | reason | signed |\n| --- | --- | --- | --- | --- |\n"
        "| 23 | number | 255 | now beside its link | reader |\n"
        "| 23 | quote | x | no signature |  |\n"
    )
    ws, notes = parse_waivers(table)
    ok = len(ws) == 1 and ws[0].value == "255" and len(notes) == 1
    print(f"  {'ok  ' if ok else 'FAIL'} the waiver table accepts only signed rows")
    failed += not ok
    # a section report on a pattern layout flags long lead-ins
    layout = (
        "## Pattern: X\n\n### The problem\n\nOne. Two. Three. Four.\n\n"
        "### The solution\n\nA **X** is y.\n\n"
        "**Bucket: survives.** Because.\n\n### How Python models it\n\n"
        + "word " * 70
        + "\n\n```python\nx = 1\n```\n"
    )
    flags = {fl for s in sections(layout) for fl in s.flags}
    ok = "problem over 3 sentences" in flags and "lead-in over 60 words" in flags
    print(
        f"  {'ok  ' if ok else 'FAIL'} the section report flags a long problem and a long lead-in"
    )
    failed += not ok
    # O6: the link rewrite and the dropped pytest header are the only losses it normalises
    failed += o6_self_test()
    if failed:
        print(f"prose_invariants self-test FAILED ({failed})")
        return 1
    print("prose_invariants self-test passed")
    return 0


# ---------------------------------------------------------------- main


def run_compare(base: str, nums: list[int], evidence: Path) -> int:
    waivers, notes = (
        parse_waivers(evidence.read_text(encoding="utf-8")) if evidence.exists() else ([], [])
    )
    recon = git_show(base, RECONCILIATION.relative_to(ROOT).as_posix())
    bad = 0
    for n in notes:
        print(f"note: {n}")
    for num in nums:
        path = doc_path(num)
        rel = path.relative_to(ROOT).as_posix()
        res = compare(
            git_show(base, rel),
            path.read_text(encoding="utf-8"),
            [w for w in waivers if w.doc == num],
            reconciliation_sources(recon, num),
        )
        if res.failures:
            bad += 1
            print(f"FAIL {path.name}")
            for f in res.failures:
                print(f"  {f.show()}")
        else:
            tail = f", {len(res.waived)} waived" if res.waived else ", no difference"
            print(f"ok   {path.name}{tail}")
        for note in res.notes:
            print(f"  note: {note}")
        for w in res.unused_waivers:
            print(f"  note: unused waiver {w.kind} {w.value[:50]!r}")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("docs", nargs="*", type=int, help="doc numbers (default: the reworded set)")
    ap.add_argument("--base", default=DEFAULT_BASE, help=f"base revision (default {DEFAULT_BASE})")
    ap.add_argument(
        "--all", action="store_true", help="compare every doc, not just the reworded set"
    )
    ap.add_argument(
        "--waivers", type=Path, default=EVIDENCE, help="evidence file holding the waiver table"
    )
    ap.add_argument("--sections", action="store_true", help="per-H3 report of the working tree")
    ap.add_argument(
        "--baseline", action="store_true", help="invariant counts of the docs at --base"
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    nums = args.docs or (
        [int(p.name[:2]) for p in sorted(DOCS_DIR.glob("[0-9][0-9]-*.md"))]
        if args.all
        else list(REWORDED_DOCS)
    )
    if args.sections:
        for num in nums:
            print_sections(num, doc_path(num).read_text(encoding="utf-8"))
        return 0
    if args.baseline:
        print(
            "| doc | fences | test names | URLs | relative_url | quotations | numbers "
            "| numbers, tags kept | walk-throughs |"
        )
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for num in nums:
            print(
                baseline_row(num, git_show(args.base, doc_path(num).relative_to(ROOT).as_posix()))
            )
        return 0
    return run_compare(args.base, nums, args.waivers)


if __name__ == "__main__":
    sys.exit(main())
