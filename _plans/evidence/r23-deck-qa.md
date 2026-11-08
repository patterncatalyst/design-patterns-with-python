---
title: "Evidence: Deck 201 QA (r23, Z4a)"
output: false
render_with_liquid: false
---

# Deck 201 QA

Recorded 2026-11-07 for r23, step Z4a. Deck: `presentation/design-patterns-with-python-201-idiomatic-python.pptx`, built by `node deck-201.js` from `presentation/`.

## Pipeline

- `npm ci` was not needed: `presentation/node_modules` was present, and `require.resolve('pptxgenjs')` resolves under it.
- `node deck-201.js` prints `slides: 45 min notes words: 69`.
- `./render-png.sh --check` prints `same` for all sixteen figures.
- `soffice -env:UserInstallation=file://<scratchpad>/lo-qa --headless --convert-to pdf`, then `pdftoppm -jpeg -r 110`: 45 page images. No `soffice.bin` or `node` process remained afterwards.
- `python3 presentation/notes.py` and `--slides` wrote the notes and slide text used below.

## Counts

45 slides and 45 notes slides with text (`docProps/app.xml` says Slides 45, Notes 45). Minimum notes words by kind (extracted text, words per slide): cover 89, dividers 69 (floor 45), content slides 103 (floor 90). Builder floors are asserted in `finish()`.

| Slide | Kind | Notes words |
| --- | --- | --- |
| 1 | cover | 89 |
| 2 | route | 103 |
| 3 | divider | 84 |
| 4 | content | 163 |
| 5 | content | 144 |
| 6 | content | 158 |
| 7 | content | 121 |
| 8 | divider | 94 |
| 9 | content | 142 |
| 10 | content | 141 |
| 11 | content | 143 |
| 12 | content | 148 |
| 13 | content | 141 |
| 14 | content | 151 |
| 15 | divider | 72 |
| 16 | content | 117 |
| 17 | content | 131 |
| 18 | content | 146 |
| 19 | divider | 82 |
| 20 | content | 153 |
| 21 | content | 135 |
| 22 | content | 146 |
| 23 | content | 133 |
| 24 | divider | 81 |
| 25 | content | 133 |
| 26 | content | 134 |
| 27 | content | 148 |
| 28 | content | 120 |
| 29 | content | 160 |
| 30 | content | 178 |
| 31 | divider | 78 |
| 32 | content | 160 |
| 33 | content | 146 |
| 34 | content | 162 |
| 35 | divider | 76 |
| 36 | content | 152 |
| 37 | content | 167 |
| 38 | content | 164 |
| 39 | content | 135 |
| 40 | content | 118 |
| 41 | content | 153 |
| 42 | divider | 69 |
| 43 | content | 141 |
| 44 | content | 112 |
| 45 | content | 130 |

## Fonts and docProps

`pdffonts`: Overpass-Bold, RedHatText-Regular, RedHatText-Bold, RedHatMono-Bold and RedHatMono-Regular, all embedded; no other family.

`docProps/core.xml`: title "Design Patterns with Python: 201, Idiomatic Python", subject "Companion deck to Design Patterns with Python", creator "PatternCatalyst", lastModifiedBy "PatternCatalyst". `docProps/app.xml`: Company "PatternCatalyst".

## Pointer grep (QA step 8)

Case-insensitive grep over the extracted notes and slide text for `follow|next|previous|earlier|later|above|below|before it|after it|close the section|last section|closing slide|chapter|appendix|the book|dissolv|surviv|disambiguat|census|decision [0-9]|\bP[0-9]+\b|\.md`, plus `member`, `slide`, `last slide`, `in order`. Final result:

- One hit, allowed: the test identifier `test_inspect_signature_follows_wrapped_to_the_original_parameters` in the notes of the wraps slide. It names a test and doesn't point anywhere.
- First-pass hits that were fixed: "context managers" matched `next` as a substring (not a hit with word boundaries); "follows __wrapped__", "fails later", "wins on the next read", "after it the fields", "next to the function", "survives", "comes after it", "does not follow", "before it is repeated", "the booking is lost", "a slide uses it for" and "on the slide". The word "the book" matches nothing in notes or slide text; the site address on the closing slide is the only place the site and repository appear.
- Cross-language case-sensitive grep `Java|C#|C\+\+|\.NET|Rust|\bGo\b`: no hits. No em or en dash in `deck-201.js` or the extracted text.
- Scope-word grep (`every|all|only|each|always|never|any|whole|entire|best`): every remaining hit is a test identifier, a sentence a test or the census proves (for example "a failed open discards the partials of every writer entered", "the hook runs only when normal lookup fails", "both threads take the same slot"), or a chapter sentence. Unproven ones were reworded ("each call site", "any async generator", "every subscriber", "stops best").

## Voice gates

- Canonical ban scan: 0 hits after one fix ("keep a caller honest" became "hold a caller to what it promised").
- `scan.sh --stats`, notes: 7,046 words, contractions 26/33, 328 sentences, median length 19 (p10 8, p90 38), triad candidates 30, dashes 0. Slide text: 2,660 words, contractions 7/11, 28 sentences, triad candidates 13, dashes 0. The remaining triad candidates are lists of named items (authors, types, mechanisms) and not padding.
- `validate.py`: 0 errors (6 warnings, all appendix word-count floors), `--self-test` ok, `--claims` 0 errors. `host_ids.py check`: 0 hits. `ruff format --check`: 661 files already formatted. `scripts/verify.sh`: 1405 passed.

## Pages viewed

All 45 rendered pages were viewed in contact sheets of four (`magick montage`): 1 to 4, 5 to 8, 9 to 12, 13 to 16, 17 to 20, 21 to 24, 25 to 28, 29 to 32, 33 to 36, 37 to 40, 41 to 44, and 45 alone.

- Logo and page number present on every page; dividers keep the `AB0000` fill; divider 35 wraps its title onto two lines ("Concurrency and the patterns"), which is within the two-line limit.
- Code boxes fit their listings and every caption sits under its box on one line. The longest listing (slide 6, 92 characters) and slide 27 (15 lines) are not clipped.
- Figures 07, 09, 10, 31 and 37 show at their own aspect with legible labels; the unconnected `_NullGateway` box on slide 11 is intended.
- Tables on slides 28, 43 and 44 show no mid-word wraps.
- Slide 2 and the bullet slides leave blank space below the text, as Deck 101's do.
- No overflow, clipped code, lone wrapped word or missing logo was found, so no layout fix was made. Text fixes made after the first viewing (the scope words and pointer phrases above) were followed by a rebuild and a re-run of the grep, the scan and the validator.

## Deck 101 identity

`node deck-101.js` into the working tree, then an unzip against the committed deck: 342 parts each, and `diff -rq` reports only `docProps/core.xml`. The committed 101 file was restored with `git checkout`.
