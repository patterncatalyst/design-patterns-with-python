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

## Voice pass (2026-11-07, D4b)

Rules applied: the house-voice rubric (meta-narration, flourishes, importance assertions, philosophy-teacher moves, self-validating asides, rule of three, scope words, uniform bullets, example-first openings), plus accuracy against the census and the chapters. Every note and slide was read. No chapter, appendix, book or internal-code pointer was found. The pointer grep was re-run after the pass: the remaining hits are plain words ("next band's price", "next prompt", "later" inside the Meszaros definition, "above 5 and 50 kg", `test_unittest_mock_patch_follows_the_same_lookup_rule`), `book` as the shipping verb, and "example directory" on the closing slide. The cross-language grep has 0 hits. The AI-claim grep hits are `never` in the experiment sentences and test names, and `often` inside Fowler's attributed quotation; no vendor, frequency or productivity word.

Two specific checks:
- The seams notes (slide 14) did not quote Feathers; they paraphrased his definition as "without editing in that place", a wording the chapter doesn't carry. The sentence now follows the chapter's own: a seam is a place where behaviour can be changed from outside the code, and the enabling point is the spot where the change is made. It stays attributed and carries no quotation marks.
- The slide-text sentence-length p90 of 270 is an extraction artefact: `notes.py --slides` joins code lines and table cells without full stops, so a whole listing counts as one sentence. The longest real prose sentence on a slide is about 167 characters (the closing slide's run instructions). No run-on was found.

Changes: 22. By kind: scope 10, flourish 4, accuracy 2, philosophy 2, example-first 2, self-validating 1, meta 1. Slide 18's "five forms" list named three; it now names all five forms the `step` fixture builds (accuracy).

`scan.sh --stats` on Markdown copies. Before: notes 5677 words, 275 sentences, 23/28 contractions, median 19 (p10 to p90 7 to 36), 29 triad candidates, 0 dashes; slides 2697 words, 31 sentences, 3/4, median 16 (12 to 270), 17 triad, 0 dashes. After: notes 5642 words, 272 sentences, 23/28, median 19 (7 to 36), 29 triad, 0 dashes; slides 2690 words, 31 sentences, 3/4, median 16 (12 to 270), 17 triad, 0 dashes. The triad candidates are lists of named items. The expanded forms left are inside code, test names and attributed quotations.

Rebuilt with `node deck-301.js` (42 slides, minimum notes words 63 on the Reference divider, floor 45; content slides stay above 90). Rendered with soffice (private profile) and `pdftoppm`; fonts unchanged (Overpass, Red Hat Text, Red Hat Mono). Pages 6, 20, 22, 24, 25 and 31 viewed, the pages whose slide text changed: no wrap, overflow or clipping. The other changes are in notes. No soffice process remains.

| Kind | Before | After |
| --- | --- | --- |
| flourish/example-first | A test is named as a claim, so a failure reads as a broken sentence. This one says what the engine does: it books only the winner. It also asserts | The engine books only the winner, and the test name says so, so a failure reads as a broken sentence. It also asserts |
| self-validating | A hand-written fake earns a static check, and mypy rejects | A hand-written fake gets a static check, and mypy rejects |
| scope | Only create_autospec copies the signatures of its target, so | create_autospec copies the signatures of its target, so |
| scope (slide) | Only create_autospec copies the signatures, so | create_autospec copies the signatures, so |
| meta | Fallback: the question about which vocabulary is the takeaway. | Fallback: the two rows. |
| scope | so every global that inherited code reads is a seam. | so a global that inherited code reads is a seam. |
| accuracy (Feathers wording) | Feathers's seam, a place where behaviour can change without editing in that place, and its enabling point are credited | Feathers's seam, a place where behaviour can be changed from outside the code, and its enabling point, the spot where the change is made, are credited |
| accuracy (five forms) | five forms of the engine: carriers as parameters, the engine as a function, and a subclass that overrides a method name. | five forms of the engine: the legacy engine, carriers as parameters, a wrapper that fits the quoter shape, the engine as a function, and a subclass that overrides a method name. |
| flourish | The price of the defaults is the other direction: a test | The defaults have a cost: a test |
| scope (slide) | each defaulting to the real call. | defaulting to the real calls. |
| scope | Each dependency-breaking move has a Python form, and this one stays as the comparison. | The parameter forms are the Python ones, and this form stays as the comparison. |
| scope | where each technique is set out in full. | where the techniques are set out in full. |
| philosophy | The golden file answers a different question: not "is this right" but "did this change" | The golden file asks "did this change" |
| scope | so a failure reads the same on every run and the first | so a failure reads the same from run to run and the first |
| scope (slide) | so a failure reads the same on every run. | so a failure reads the same from run to run. |
| example-first/flourish | A legacy engine holds behaviour somebody wanted and behaviour nobody chose. The parity test runs both engines over one table of rows. It fails on a new difference and on a stale entry, so the rewrite differs only where the accepted list says (test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted). The legacy engine prices an unknown zone as EU (test_the_legacy_engine_prices_an_unknown_zone_as_eu), and the rewrite refuses it (test_the_rewrite_refuses_an_unknown_zone). | The legacy engine prices an unknown zone as EU (test_the_legacy_engine_prices_an_unknown_zone_as_eu), and the rewrite refuses it (test_the_rewrite_refuses_an_unknown_zone). The parity test runs both engines over one table of rows. It fails on a new difference and on a stale entry, so the rewrite differs only where the accepted list says (test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted). |
| scope (slide) | Each step registers its inverse as it succeeds; a refusal | The slot and the booking register their inverses as they succeed; a refusal |
| example-first/aphorism | Something has to decide, and the fewer places that do, the fewer places change when a carrier does. This function chooses the pricing rule as well as the carrier and the subscriber | One function chooses the pricing rule as well as the carrier and the subscriber, so a new carrier changes one place |
| flourish/importance | a draft that passes all three has been checked on those rows and in those shapes, and no further ( | a draft that passes all three has been checked on those rows and in those shapes ( |
| flourish/importance | The gates verify accuracy at chosen points, and everything between those points is trust. | The gates verify accuracy at the rows and shapes they list. |
| scope (slide) | ["Each move", " has a Python form, and subclass and override is the one kept for comparison."] | ["The parameter forms", " are the Python ones, and subclass and override stays as the comparison."] |
| philosophy (slide) | ["A golden quote", " asks a different question: not is this right, but did this change."] | ["A golden quote", " asks whether anything changed."] |

## Repair round 1 (2026-11-08, D5)

Items applied to `presentation/deck-301.js` unless a path is named. Every new sentence was checked against its witness before it went in.

Blocking:

1. Slide 9 notes: three tests assert exact outcome counts of both runs, and `test_an_unknown_option_fails_under_strict_config` asserts `ExitCode.USAGE_ERROR` and the stderr line "Unknown config option". The same fix is in `_docs/42-appendix-b-pytest.md` and in the card blurb of `_examples/42-appendix-b-pytest.md`. The remaining "exact outcome counts" sentences in `_docs`, `_examples` and `examples/42-*` say "most" or name inner sessions in general and were left.
2. Slide 31 notes: the five-fail, 18-pass count and the mypy exit are now two separate causes.
3. Slide 33 notes: the desk takes each collaborator as a keyword parameter, which matches the composition-root section of the final-project chapter.
4. Slide 12 notes: `book_cheapest` calls the stub with the booking reference (`booking.py` calls `notify(reference)`); the same correction is in row 285 and the D2 dated note of `_plans/reconciliation-plan.md` and in the Step D2 note of `_plans/r24-plan.md`.
5. Slide 2: Reference entry removed, notes name the seven themes and add one sentence on the reference section, `fontSize: 18, gap: 14` in both calls. Notes: 120 words.
6. Figure 33: canvas 1020 x 420, positions as briefed, edge labels staggered beside their own arrows (left label right of the left arrow, right label left of the right arrow).
7. Figure 40: canvas 960 x 410; the amber arrow now rises from the gate row's top edge in the gap between the shape review and the oracle, labelled "propose: every gate's findings go back in the next prompt" (`propose` builds `findings` over every gate). The chapter walk-through and the slide 36 notes were updated to match. The include caption and `_data/diagrams.yml` caption still describe the drawing and were not changed.

Figure label sizes on the slide (points = 72 x min(12.09/W, 4.95/H) x 11): figure 33, 9.3 pt (was 6.4); figure 40, 9.6 pt.

Should-fix 8 to 14, nits, and items 15 to 21 are applied as briefed: slide 6 quotation, slide 11 caption, slide 5 notes and mypy cell, slide 38, slide 35, README lines of examples 36 and 35 (`CENT` matches the `refactored.py` docstring), slide 7 teardown sentence replaced by a sentence on what the slide shows (128 words), slide 12 Dummy Object passage cut to one sentence, slide 17 bullet, slide 21 closing sentence (91 words), slide 27 notes sentence (134 words), slide 40 notes, slide 42 two bullets, and the nits for slides 10, 30, 4, 3, 15, 23, 31 and the Stub cell.

Pointer grep (`follow|next|previous|earlier|later|above|below|before it|after it|chapter|appendix|book|this (deck|slide)|these slides|in order`) over notes and slide text: every hit is a verb or an identifier (`book`, `booked`, `booking`, `book_best`, `test_unittest_mock_patch_follows_the_same_lookup_rule`), "next band's price", "next prompt" (the loop's next request), or "books" on the reference slides. No positional pointer. The plan's step 8 list adds only allowed hits ("member" in a mypy test name and in "a missing member"; "above 5 kg" a weight). Case-sensitive cross-language grep: no hits. AI-claim grep (including "most ", typically, tend, assistants may/might/will, accura): two hits, both inside attributed quotations (Fowler's Strangler Fig "often" and OWASP's "accuracy").

Pages viewed after the rebuild: 2, 5, 6, 7, 9, 11, 12, 15, 17, 21, 27, 31, 33, 35, 36, 38, 40 and 42, plus both figure PNGs at full size. Decks 101 and 201 rebuild with only `docProps/core.xml` differing; the committed files were restored.
