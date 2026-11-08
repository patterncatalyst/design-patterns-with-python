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

## Voice pass (2026-11-07, Z4b)

Rules applied: rule of three, meta-narration, confessional or defensive phrasing, hedges and flourishes, importance-assertions, philosophy-teacher moves, unproven scope words, title shape, bullet shape, stiff expanded forms, cadence repeated across slides, slide-order pointers, book labels, accuracy. No chapter, appendix or internal-code pointer was found. The pointer grep (follow, next, previous, earlier, later, above, below, chapter, the book, .md and the rest) was re-run after the pass: the only hit is the test name `test_inspect_signature_follows_wrapped_to_the_original_parameters`, allowed.

Changes: 45. By rule: meta 10, stiff 8, flourish 7, philosophy 4, accuracy 4, cadence 3, defensive 2, title 1, importance 1, scope 1, confessional 1, redundancy 1, category 1, coaching 1.

`scan.sh --stats` on Markdown copies of the notes and the slide text. Before: notes 7046 words, 26/33 contractions, 30 triad candidates; slides 2660 words, 7/11, 13. After: notes 6951 words, 34/35, 30; slides 2654, 9/12, 13. The triad candidates that remain are lists of named items (credits, authors, test lists). The 'was not' and 'is not' expanded forms left on the slides sit inside code excerpts.

Rebuilt with `node deck-201.js` (45 slides, minimum notes words 48 on the Reference divider, floor 45). Rendered with soffice (private profile) and `pdftoppm`; fonts unchanged (Overpass, Red Hat Text, Red Hat Mono). Pages 2, 17, 23 and 43 viewed, the pages whose slide text changed: no wrap or overflow. The other changes are in notes. No soffice process remains.

| Rule | Before | After |
| --- | --- | --- |
| meta-narration / hedge | Tests stand behind the claims, and the speaker notes name them, so a claim can be re-run when it matters. | Where a test witnesses a claim, its name is given, so the claim can be re-run. |
| title | addContentTitle(s, "ROUTE", "The route"); | addContentTitle(s, "THEMES", "Eight themes"); |
| meta-narration | What to show: nothing runs here. Fallback: each theme has a divider of its own that names it again. | What to show: nothing runs here. Fallback: the dividers name each theme. |
| meta-narration / scope | The hashing contract, reflected operands, the Value Object pattern as a declaration and the limits of frozen all belong to this theme. | The cases are the hashing contract, reflected operands, the Value Object pattern as a declaration and the limits of frozen. |
| meta-narration / cadence | Absence in the type, a silent null object, two meanings of interface, and both exits from a manifest write belong to this theme. | The cases range from absence in the type and a silent null object to two meanings of interface and both exits from a manifest write. |
| meta-narration / cadence | That is a different thing from the Decorator pattern, which composes wrapper objects at run time, and the two names stay apart here. | That's a different thing from the Decorator pattern, which composes wrapper objects at run time. The two names mean different things. |
| flourish | Class decorators and methods complete the picture. | Class decorators and methods add two more traps. |
| importance-assertion | The traps in the hooks are the substance of this theme. | The hooks carry traps: a stale cache, and a recursion through __getattr__. |
| philosophy / scope | The fallback, or the failure mode, is the design decision in each mechanism. | What happens for an unregistered kind is the design decision: singledispatch raises or answers, a class keyword refuses, and a table raises a named error. |
| scope | the price is still paid on each change. | the structure keeps costing something whenever the code changes. |
| flourish / accuracy | and what a pool shares matters more than which pool is fastest. | and the pool tests show what threads share and what processes and interpreters copy. |
| defensive / meta | The wording and the examples are new, and the short quotations are attributed. A table of sources and a table of books come with the site and the repository that hold the examples. | Short quotations are attributed. Two tables list the sources and the books. |
| meta-narration | "The design record behind each feature, with authors named in the notes" | "The design record behind the features cited" |
| stiff | It is shallow: a list inside | It's shallow: a list inside |
| philosophy | The question for any stand-in is what the caller needs to know that the stand-in hides. | A stand-in is wrong when it hides something the caller needs to know. |
| confessional | A manifest write has two exits, and neither may leak or lie. The first failure is a leak: without a with block an exception leaves the handle open (test_without_with_an_exception_leaves_the_handle_open). The second is a lie: a half-written file left in place reads as a finished manifest. The figure shows the writer's answer. | A manifest write has two exits, and each can fail differently. The first failure is a leak: without a with block an exception leaves the handle open (test_without_with_an_exception_leaves_the_handle_open). The second is a false manifest: a half-written file left in place reads as a finished one. The figure shows the writer's handling. |
| redundancy | so the call runs at definition, and so does any mistake in it. Decorator expressions are evaluated when the function is defined. The keyword-only | so the call runs at definition, and so does any mistake in it. The keyword-only |
| hedge / defensive | The benefit is real: the value is computed on first access and stored | The benefit: the value is computed on first access and stored |
| flourish | Lookup precedence explains the storage trick. | Lookup precedence explains where the cache sits. |
| flourish (caption) | the missing attribute calls __getattr__ again, without end. | the missing attribute calls __getattr__ again until RecursionError. |
| stiff | for a customs declaration that is right, because | for a customs declaration that's right, because |
| flourish | The price of an open set is what mypy can check. | An open set limits what mypy can check. |
| stiff | so the metaclass registry is not needed. | so the metaclass registry isn't needed. |
| accuracy (three raises, not four) | Fallback: the four refusals in the listing. | Fallback: the three refusals in the listing. |
| flourish | Otherwise a metaclass is the wrong tool. | Without that need, those costs buy nothing. |
| category label | What goes is the structure built around an if-chain; the dictionary of callables stays. | The dictionary of callables replaces the structure built around an if-chain. |
| philosophy | The scope of the guarantee is one gap: two readers that both miss both load, so EAFP doesn't make a load happen once | EAFP leaves one gap: two readers that both miss both load, so it doesn't make a load happen once |
| flourish | Two forms quote one table, and the table is the test. | Two forms quote one table of cases. |
| defensive | It answers a real need, since a collaborator is found without being passed down the signature, and it has a cost. | It meets a need: a collaborator is found without being passed down the signature. It also has a cost. |
| accuracy (listing is five lines) | Fallback: the four lines of the listing. | Fallback: the five lines of the listing. |
| accuracy (no pool table on the slide) | What to show: the pool table. Fallback: the listing. | What to show: run the serial loop and a pool on one batch. Fallback: the listing. |
| coaching | Two loops on one build moved in opposite directions, so measure your loop. | Two loops on one build moved in opposite directions, so one loop's ratio doesn't predict another's. |
| flourish | The iterator becomes an async generator, and the closing is the part that needs care.  | (removed) |
| philosophy | The question to ask of an async generator is who closes it. | An async generator needs an owner that closes it. |
| meta-narration / scope | Each source is named with what it is used for, and the speaker notes of the slides that rely on it name it again. | The table pairs sources with their use. |
| meta-narration | Fallback: the rows name each source and what it was used for. | Fallback: the rows pair source and use. |
| meta-narration | Eight books cover the ground the slides compress. | Eight books are credited. |
| cadence (name collision) | This CarrierBase is the registering one, which tells it apart from the reference-sharing base. | This CarrierBase registers subclasses; the other CarrierBase shares a reference. |
| cadence (name collision) | This TrackingHistory is the lazy one, which tells it apart from the eager history in the data model example. | This TrackingHistory is the lazy one, as against the eager history in the data model example. |
| cadence (name collision) | This quote is the CPU-bound one, which tells it from the async quote. | This quote is the CPU-bound one, not the async quote. |
| stiff (caption) | fail where it is written, and the check on seconds runs at definition. | fail where it's written, and the check on seconds runs at definition. |
| stiff | There is no stand-in object, so this is interception, not a surrogate. | There's no stand-in object, so this is interception, not a surrogate. |
| stiff | until they are asked for | until they're asked for |
| stiff | and others named where they are used | and others named where they're used |
| stiff | what it cannot check in a metaclass | what it can't check in a metaclass |
