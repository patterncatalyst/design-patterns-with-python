---
title: "Evidence: Deck 301 QA (r24, D4a)"
output: false
render_with_liquid: false
---

# Deck 301 QA

Recorded 2026-11-07 for r24, step D4a. Paths are repo-relative; `<scratch>` is the session scratch directory.

## Build and render

- `node deck-301.js` from `presentation/` (node_modules present, no install): 42 slides, 42 notes slides. Output `presentation/design-patterns-with-python-301-testing-legacy-and-ai.pptx`.
- `soffice -env:UserInstallation=file://<scratch>/lo --headless --convert-to pdf`, then `pdftoppm -jpeg -r 90`: 42 page images. `pgrep -x soffice.bin` and `pgrep -x node` print nothing afterwards.
- `pdffonts`: Overpass-Bold, RedHatText-Regular and Bold, RedHatMono-Regular and Bold, all embedded; no other family.
- `docProps`: creator, lastModifiedBy and Company are PatternCatalyst; title "Design Patterns with Python: 301, Testing, legacy code and AI"; subject "Companion deck to Design Patterns with Python"; Slides 42, Notes 42.

## Notes word counts

Floors: 90 on content slides, 45 on the cover and dividers. Minimum by kind: cover 95; dividers 63 (slide 39); content slides 98 (slide 21, the lowest of 31 content and 2 figure slides, floor 90).

| Slide | Words | Slide | Words | Slide | Words |
| --- | --- | --- | --- | --- | --- |
| 1 | 95 | 15 | 127 | 29 | 74 |
| 2 | 117 | 16 | 106 | 30 | 123 |
| 3 | 91 | 17 | 117 | 31 | 136 |
| 4 | 134 | 18 | 90 | 32 | 117 |
| 5 | 115 | 19 | 150 | 33 | 119 |
| 6 | 127 | 20 | 111 | 34 | 87 |
| 7 | 126 | 21 | 98 | 35 | 138 |
| 8 | 91 | 22 | 122 | 36 | 135 |
| 9 | 113 | 23 | 89 | 37 | 131 |
| 10 | 128 | 24 | 119 | 38 | 139 |
| 11 | 114 | 25 | 137 | 39 | 63 |
| 12 | 139 | 26 | 130 | 40 | 127 |
| 13 | 90 | 27 | 128 | 41 | 111 |
| 14 | 125 | 28 | 101 | 42 | 124 |

(Counts by whitespace split of `notes.py` output including the slide-number field, so they may sit one above `finish()`'s count; every slide clears its floor in `finish()` and in `check_decks()`.)

## Greps over the extracted notes and slide text

1. Pointer grep (case-insensitive: follow, next, previous, earlier, later, above, below, before it, after it, close the section, last section, closing slide, the dividers, chapter, appendix, book, dissolv, surviv, disambiguat, census, decision N, P-codes, D-codes, .md, this deck or slide, these slides, example). After the first pass the hits were fixed or recorded:
   - Fixed: "in this example" (now "this test file"), "follows the same rule" (now "applies"), "a later step" (now "a step that runs afterwards"), "after its attempts" (now "once its attempts run out"), "last slide" and "book-length" (found by `check_decks()`).
   - Allowed, plain words: "before it asserts"; "above 5 and 50 kg" in a bullet (a weight, not a pointer); "the next band's price" (a band of the tariff); `book`, `books`, `booked`, `booking` as the shipping verb and the carrier gateway's `book` method, in code listings and test names; "Books" in the Reference divider and "books" in the themes bullet (the reading list); "Book" as the column head of the reading table; "an example" and "example directory" on the closing slide and in the notes that describe running one (the repository's own term for an example directory).
2. Cross-language grep (case-sensitive: Java, C#, C++, .NET, Rust, `\bGo\b`): 0 hits.
3. AI-claim grep (always, never, often, usually, most, percent, %, faster, productiv, Copilot, ChatGPT, Claude, GPT, Gemini): 0 hits on a vendor, a figure or a productivity word. `never` hits, each justified: "was never seen to fail" (the chapter's sentence on the experiments), "never reaches" (the happy path, the chapter's sentence), "never reads it" (the stub, `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first`), `test_with_every_zone_migrated_the_legacy_engine_is_never_called`. `often` appears once, inside Fowler's attributed Strangler Fig quotation. `not always` was reworded to "not necessarily".

## Scans

- `scan.sh --tier ban --fail` over the notes, the slide text and `deck-301.js`: 0 ban-tier.
- `scan.sh --stats`: notes 5677 words, 23/28 contractions, 275 sentences, median length 19 (p10 to p90 7 to 36), 29 triad candidates, 0 dashes. Slides 2697 words, 3/4 contractions, 31 sentences, 17 triad candidates, 0 dashes. The triad candidates are lists of named items (test names, credits, authors).

## Pages viewed

Every page was viewed in contact sheets of four (`magick montage`). Findings:

| Page | Finding | Fix |
| --- | --- | --- |
| 5 | "attr-defined" and "call-arg" wrapped at the hyphen in the table | column widths changed to 3.9, 3.4, 2.6, 2.19 and the mypy cell shortened to "checked: a missing member errors"; page re-rendered and viewed |
| 41 | the last book title wrapped onto a second line | title shortened to "Effective Python, third edition" |
| 15 | figure 33 renders at 8.28 by 4.95 inches; its small labels are legible but the smallest on any deck | none; the QA drop rule did not trigger on the page view |
| all others | no overflow, clipped code, lone wrapped word, missing logo or caption on the code box | none |

## Identity of Decks 101 and 201

`node deck-101.js` and `node deck-201.js` into the working tree, unzipped against `git show HEAD:<deck>`: `diff -rq` reports only `docProps/core.xml` for each. Both committed files were restored with `git checkout`.
`deck-lib.js` and `deck-helpers.js` are unchanged.

## Gates

`validate.py` 0 errors, `--self-test` ok, `--claims` resolves rows 399 to 429; `host_ids.py check` 0 hits in 883 files; the repo-wide ban scan 0; `render-png.sh --check` prints `same` for 18 figures; `ruff format --check` clean; `verify.sh` passed (1406 tests).
