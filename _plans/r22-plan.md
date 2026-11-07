---
title: "r22 plan: Deck 101 (Patterns and SOLID in Python)"
order: 22
output: false
render_with_liquid: false
---

# r22: Deck 101, Patterns and SOLID in Python, and the three-deck arc

Opus-planned 2026-11-07. Branch `release/r22`, cut from main at db8f3ce (the r21 merge, tagged `r21.x`). This file is the source of truth for r22 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

Work item: PDP-150 ("Deck 101", r22, `todo` in `_plans/iteration-plan.md`). PDP-151 (Deck 201, r23) and PDP-152 (Deck 301, r24) plan against the arc in "The three-deck arc" below; r25 is the retro and QA sweep. CLAUDE.md: "Companion decks are built last: 101, 201, 301."

The deck is built with the lgtm-presentation skill (pptxgenjs builder plus the skill's `deck-helpers.js`) and voiced with lgtm-professional-voice. Every slide's content comes from a shipped chapter and its tested example. The book's text, code and figures are the only material; nothing is written for the deck that the book doesn't already say and test.

Pins this iteration (checked 2026-11-07, evidence D, H): pptxgenjs 4.0.1 (npm `dist-tags.latest`, published 2025-06-26; the only newer tag is `beta` 4.0.1-beta.2, a pre-release), image-size 2.1.0 (npm `version`, used only as an override, decision 4), cairosvg 2.9.1 (PyPI latest, uploaded 2026-09-07, run through `uv run --no-project`, never added to the workspace). The Python pins are unchanged from r21 (Python 3.15.2, uv 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4); Y0 re-checks all of them before any edit.

Lessons carried from r16 to r21: grep everywhere; the run wins over the plan; recount after every edit; status tokens are plain `done`; a row's `source:` URL that prose hasn't linked yet reads "source (open until prose links it)"; paths in plans and evidence are repo-relative, with `<repo>` and `<scratchpad>` for anything outside; only suffixed step ids are cited as `run:` tokens.


## Owner decisions, 2026-11-07

- O1: the three-deck arc as planned. Deck 101 has 62 slides, with each eligible figure on its own full-width slide. Concurrency (chapters 37 and 38) goes into 201.
- O2: build and publish as recommended: decisions 3 to 8, 11 and 15. That means pptxgenjs 4.0.1 pinned exactly, with the image-size override; the deck committed under a stable name; PatternCatalyst metadata; and `check_decks()`.
- O3: decision 10 as recommended, with every defect fixed in Y1d, and the registry resolved by amending CLAUDE.md. The orchestrator changed CLAUDE.md line 58 to "figure registry: name, section, title, caption" to match `_data/diagrams.yml`, so no `alt` key is added. Decisions 0, 1, 2, 9, 12, 13 and 14 are as recommended.

## Owner decisions

None recorded yet. The owner reviews the numbered decisions below; where an owner decision differs, it is recorded here with a date and the numbered decision is amended in place.

## User decisions

0. **Step ids.** The steps are Y0 to Y6. At planning `grep -nE '^\| Y[0-9]' _plans/*.md` and `grep -n 'run: Y' _plans/*.md` print nothing (evidence M). Only suffixed ids are cited as `run:` tokens: `Y1a`, `Y1b`, `Y1c`, `Y1d`, `Y4a`, `Y4b`. Plain Y0, Y2, Y3, Y5 and Y6 appear only in this plan's table. Two recorded files are cited as `run:` paths: `_plans/evidence/r22-deck-witness-census.md` (Y1b) and `_plans/evidence/r22-deck-qa.md` (Y4a).

   **Recommend: yes.**

1. **The three-deck arc** (section "The three-deck arc"). Every shipped chapter and appendix belongs to exactly one deck. 101 takes Parts 0 to 3, the catalogue Parts 5 to 8 and Appendices A, E and F; 201 takes Part 4 except the testing chapter, Parts 9 and 10 and Part 12; 301 takes the testing chapter, Part 11, Part 13 and Appendices B, C and D. Boundary rules settle the patterns that appear in two chapters.

   **Recommend: yes.** Alternative: leave Part 12 (the GIL and performance; asyncio and the patterns) out of every deck, as the PRD's "No fourth deck, there is no concurrency part to carry one" might be read. The book does have a concurrency Part, so the recommendation gives it to 201 as a closing section, under 201's "what Python gives you" theme.

2. **Deck 301's name.** The PRD (§8d) calls it "Testing, legacy code, and the AI throughline". Recommend the builder `presentation/deck-301.js` and the file `presentation/design-patterns-with-python-301-testing-legacy-and-ai.pptx`, following the C# sibling (`csharp-design-patterns-301-testing-legacy-and-ai.pptx`) and the PRD's three subjects; the C++ and Java siblings use `...-testing-legacy-ai.pptx`, which drops the conjunction. Deck 201: `deck-201.js`, `design-patterns-with-python-201-idiomatic-python.pptx`.

   **Recommend: yes.**

3. **Where the .pptx lives, and its name.** Commit it in `presentation/` under a stable name, `design-patterns-with-python-101-patterns-and-solid.pptx`, as every sibling does (evidence C). No release asset and no CI build. The skill's rule `<name>-rNN.x.pptx` is not followed: a per-release file name breaks the README link at every iteration, and an `rNN` marker inside the file is an internal code that reader-facing text may not carry (validate's `ITER_RE`). The release tag `r22.x` records which build shipped.

   **Recommend: yes.** Alternative: the skill's name `design-patterns-with-python-101-r22.x.pptx`, with the README link updated each iteration.

4. **Build tooling.** `presentation/package.json` with `"private": true`, `"pptxgenjs": "4.0.1"` exactly, `"overrides": {"image-size": "2.1.0"}`, and a committed `presentation/package-lock.json` (lockfileVersion 3); install with `npm ci` inside `presentation/` only. `node_modules/` (already in `.gitignore`), `presentation/qa/` and `presentation/*.pdf` are ignored. Never `npm install -g`, never set `NODE_PATH`, never resolve the user-level global copy (evidence E). The override clears the two high advisories `npm audit` reports for image-size 1.2.1 through pptxgenjs; pptxgenjs never requires image-size (evidence D), and the unzipped deck built with and without the override is identical apart from the `docProps/core.xml` timestamps. The siblings use caret ranges and ignore the lockfile; this repo pins exactly and commits it, per the latest-stable-pinned rule.

   **Recommend: yes, with the override.** Alternative: no override, `npm audit` findings recorded in the QA evidence as unreachable code.

5. **The helper.** Vendor the skill's `deck-helpers.js` (md5 abedd5abb9a98c475b1d050febc25ca7, the same in all four sibling decks) into `presentation/deck-helpers.js` with one recorded local delta: its 8 em-dash lines (7 comments and the default `pres.title`) recast with a colon or comma, so the repo-wide voice gate passes without a new exclusion. No code change; `deck-101.js` overrides `pres.title`, `pres.author`, `pres.company` and `pres.subject` after `newDeck()`. The delta and the new md5 are recorded in `presentation/build-notes.md`. Titles stay in Overpass, as the helper and every sibling have it (installed and embedded, evidence F, I); the skill's prose says Red Hat Display, its code says Overpass, and the code wins.

   **Recommend: yes.** Alternatives: vendor byte-identical and add `--exclude deck-helpers.js` to the voice gate (CLAUDE.md is the owner's file, so the owner makes that edit); or fix the helper upstream in lgtm-skills first (a separate repo and PR, owner approval needed).

6. **Metadata.** `docProps`: creator and lastModifiedBy "PatternCatalyst", company "PatternCatalyst", title "Design Patterns with Python: 101, Patterns and SOLID", subject "Companion deck to Design Patterns with Python". The siblings carry the owner's name and "Red Hat" (evidence C); the owner's name already appears in `LICENSE-docs.md`, so this is a choice, not a leak, but a fixed string keeps the deck check simple and makes the runtime-name check meaningful. The slide design keeps the skill's assets (cover and section panels, the white logo, `logo-candidate-2.png`), byte-identical to the siblings' (evidence V).

   **Recommend: PatternCatalyst for all four fields.** Alternative: match the siblings.

7. **How the site links the deck.** The siblings' sites don't link their decks; only the README and `LICENSE-docs.md` licence lines name `presentation/` (evidence C). Here `LICENSE-docs.md` already covers "the slide decks under `presentation/`". Recommend a short "Companion decks" section in `README.md` linking the 101 file, and the README licence line extended to name the slide decks under `presentation/`. No site page and no `_config.yml` change (`presentation/` is already excluded from the Jekyll build).

   **Recommend: yes.** Alternative: also a line on the site's home page linking the GitHub file (a site change the siblings don't have).

8. **Figures.** Embed PNGs rendered from the committed `diagrams/*.svg` with cairosvg 2.9.1 (`presentation/render-png.sh`, output width 1600, as the siblings did), committed under `presentation/png/` like the siblings, with a QA check that each committed PNG equals a fresh render (the render is deterministic, evidence H). No Scene engine and no new drawing: a figure that is wrong is fixed in its spec (decision 10), never redrawn for the deck. A figure appears only if every arrow it draws is composed by code (section "Figure census"): 05, 06, 12, 19, 21 and 25 qualify now. 00 to 04 draw conceptual arrows; 13, 14, 16, 22 and 23 have defects that decision 10 fixes; 17, 18, 20 and 24 draw arrows no code composes and stay out. Each figure gets its own full-width slide (image about x 0.62, y 1.45, w 12.09, h 5.30, `sizing: contain`), because at 6 in wide every figure's sub-lines fall to 4 to 6 pt (evidence O, P, Q). A figure that QA can't read at full width is dropped from the deck, with the reason in the QA record.

   **Recommend: yes.** Alternative: admit the conceptual decision diagrams 01 to 03 as an exception, captioned as decisions rather than code.

9. **Length and shape.** 62 slides (inventory below): cover, route, nine sections each opened by a divider, 6 figure slides, 4 table slides, 26 code slides. The siblings' 101 decks run 35 to 49 slides; this one covers 21 chapters and 3 appendices, two to three slides a chapter. Rendered pages are eyeballed in two halves by two validator passes (QA pipeline).

   **Recommend: 62.** Alternative: about 48, dropping the six figure slides and folding the three map tables into one.

10. **Chapter and figure defects found while planning** (evidence T). The fix-now rule applies: each is fixed in this iteration at Y1d, before the deck quotes the chapter, with the chapter's tests green after each edit. Prose: 22.md:34 says "All three lead to `ExceptionGroup`", but only the failing subscriber raises; 22.md:213 says `Signal` "says so in its docstring", but the statement is in the module docstring; 23.md:65 says "`CLEARANCE_STAGES` is the default tuple", but `clear` has no default for `stages`; 25.md:218 "a booking whose originator is frozen" reads as a slip. Code docstring: `mediator_chain/mediator.py:1` says "once duty and inspection have both reported", while the code releases after only the reports still owed. Figure specs: 14 draws the refusal only from Delivered while the table refuses illegal pairs from every status; 22 draws `TrackingHistory.record` and the lambda into `ExceptionGroup`; 23 draws `Held` into `ClearanceMediator`, which nothing composes; 16 points `GATEWAYS` only at the Fastline gateway; 13's "refuse no commodities" is ambiguous. Registry: `_data/diagrams.yml` has no `alt` key, while CLAUDE.md says the registry holds name, caption and alt.

    **Recommend: fix every prose, docstring and figure-spec item at Y1d** (figures regenerated from their specs, never hand-edited; the alt text in each chapter's figure include is checked against the corrected figure). The fixed figures 14, 22 and 23 become eligible for the deck only if a re-run of the arrow census passes; the inventory doesn't depend on them. **For the registry, the owner chooses**: add an `alt` key to all 41 entries (only if a layout or include reads it; Y1d greps first), or amend CLAUDE.md's sentence (the owner's file). Figure 21's tree is smaller than the tested fixture (2 top-level parts against 3, one commodity against two); every arrow is composed, so it stays as an illustration and the notes say so.

11. **Code on slides.** Each code slide names a source file and a 1-based line range in `deck-101.js`; the builder reads the lines at build time, asserts the first line equals a recorded anchor string, and fails the build otherwise, so the slide is byte-exact with the source by construction and a source edit that moves the range breaks the build loudly. Font size is chosen per call so the longest line fits the box (Red Hat Mono advance 0.6 em: `max_len × 0.6 × size ≤ box width in pt`), and `opts.h` is set from the line count so a short listing doesn't sit in an empty box (evidence I). Only ranges the chapter itself quotes, or that the census confirms byte-exact against the chapter, are used. Where two chapters define the same name differently (evidence S), each slide draws on one chapter only, and the deck never shows the three-way-split chapter's `CarrierGatewayProxy`, `quote_carrier`, `audited`, `Surcharge` or `BaseRate` (the Decorator and Proxy chapter's are the ones shown).

    **Recommend: yes.**

12. **Notes.** Every slide has notes, written thick: at least 90 words on content, code, table and figure slides (target 110 to 180, like the siblings' p50 of 111 to 133), and at least 45 on the cover and dividers. Notes say what the slide shows, the force, the tests that witness it and the sources it credits; they never coach delivery. Cross-references go by concept ("the composition root", "the three-way split"), never by slide or chapter number. British spelling, contractions, no em or en dash, no rule-of-three cadence, no meta-narration, no internal codes, the word "spike" nowhere, "final project" never "capstone", and no cross-language comparison (the r21 criterion-14 word list).

    **Recommend: yes.**

13. **Credits.** Sources are credited as the chapters credit them: a "Sources credited" slide (online sources, as the chapters word them) and a "Reading further" slide (the bibliography books the 101 chapters cite), plus each source named in the notes of the slide that uses it. Nothing is copied: quotes are only the short quotes the chapters already make, attributed as the chapters attribute them.

    **Recommend: yes.**

14. **No QR slide.** The C# sibling's QR slides need a decoder to verify; `zbarimg` and `qrencode` are absent and installing them is a host change (evidence G). The closing slide gives the site, repo and hub URLs as text.

    **Recommend: yes.**

15. **The deck check in `validate.py`** (`check_decks()`, Y1c, with `--self-test` cases). It runs over every tracked `presentation/*.pptx`, so CI covers the deck with no `ci.yml` change and no Node in CI. It checks: slide count equals notes-slide count and every notes slide meets its word floor (evidence J: pptxgenjs writes a notes slide for every slide, so a count alone can't fail); `docProps` creator, lastModifiedBy and company equal "PatternCatalyst"; no em or en dash in slide or notes text; `PDP_RE`, `ITER_RE`, `SPIKE_RE`, `CAPSTONE_RE` and `XREF_RE` find nothing, nor "slide N"; none of the r21 criterion-14 cross-language words; every XML part comes back unchanged through `scripts/host_ids.py filter`; and the account's full name from the password database and `git config user.name`, read at run time and never written down, appear in no part (each skipped when empty, as on a CI runner). `host_ids.py` stays unedited.

    **Recommend: yes.**

## Planning evidence

All trials ran in scratch copies under `<scratchpad>/plan22` with a local `npm install` there only; nothing was installed in the repo or globally, nothing on the host changed, and the scratch tree was deleted before the plan commit.

A. **Repo state.** `release/r22` cut from main at db8f3ce; `git tag --points-at db8f3ce` prints `r21.x`; `git status` clean at the start. `_plans/iteration-plan.md` still says "r21 (active)" and PDP-144 to 146 `active`; Y0 closes r21. Reconciliation rows run to 312, so r22 starts at 313. `_config.yml` already excludes `presentation/`; `.gitignore` has `node_modules/`. `LICENSE-docs.md` line 3 names the slide decks under `presentation/`; the README licence line doesn't yet.

B. **Intent.** PRD §8d: 101 "Patterns and SOLID in Python", the series opener, adapted; 201 "Idiomatic Python: the data model, decorators, descriptors, singledispatch, Protocol", the "what Python gives you so you don't write the pattern" deck; 301 "Testing, legacy code, and the AI throughline", including easy seams and reviewing pattern-heavy LLM output; "No fourth deck". PRD §12a deck lessons: 1 to 2 line bullets with the detail in notes; check notes parity at the PPTX level; long code clips the box, so pass a per-call font size and don't edit the helper; rebuilds are not byte-deterministic.

C. **Siblings** (`cpp-design-patterns`, `design-patterns-with-java`, `csharp-design-patterns`, read only). Each has `presentation/` with `deck-101.js`, `deck-201.js`, a third builder, `deck-helpers.js`, `assets/`, `png/` (committed cairosvg renders at width 1600), `build-notes.md` and `package.json` (caret ranges: `^4.0.1`, Java `^3.12.0`); `.gitignore` drops `node_modules`, `package-lock.json`, `qa/` and `*.pdf`. Committed decks have stable names with no revision, e.g. `<repo>-101-patterns-and-solid.pptx`. No release assets; no site links; only the licence lines name `presentation/`. `docProps`: creator and lastModifiedBy the owner's name, company "Red Hat". Slide and notes-slide counts equal (47, 49, 35). 101 notes word counts: C# n=35, min 44, p50 111, max 153; Java n=49, min 44, p50 133, max 179. The C# 101 plan: chapters 0 to 6 plus appendices, no catalogue, about 35 slides; its acceptance list grepped for em dash, capstone, chapter or slide references and cross-language words, decoded the QR codes and checked logo and notes.

D. **pptxgenjs.** `npm view pptxgenjs dist-tags` gives `latest 4.0.1`, `beta 4.0.1-beta.2` (re-checked 2026-11-07). A scratch install of `"pptxgenjs": "4.0.1"` resolves 19 packages (lockfileVersion 3), including jszip 3.10.2, image-size 1.2.1, `https` 1.0.0 (an empty placeholder package) and @types/node 22.20.5. `npm audit`: 2 high, image-size GHSA-5p2g-fcmc-qvqq and GHSA-w3rx-r6r6-pgpr (denial of service in its JXL, HEIF and ICNS parsers). The pptxgenjs dist never requires `image-size` or `https` (the only size code is commented out and names `sizeof`). With `"overrides": {"image-size": "2.1.0"}` (npm `version` 2.1.0): 0 vulnerabilities, and the unzipped deck is identical except the `core.xml` timestamps.

E. **Global copy.** The user's npm prefix already holds a pptxgenjs 4.0.1 under the user-level global directory. The plan never uses it: no `NODE_PATH`, no `require` outside `presentation/node_modules`, and Y4a runs `node -e "console.log(require.resolve('pptxgenjs'))"` from `presentation/` to show the local path (scrubbed).

F. **Fonts.** `fc-list | grep -ci 'red hat'` prints 34: Red Hat Display, Red Hat Text and Red Hat Mono faces from the distribution's redhat-display, redhat-text and redhat-mono font packages (4.1.0); overpass-fonts 3.0.4 is installed too. `fc-match` resolves "Red Hat Text", "Red Hat Mono" and "Overpass" to themselves. Nothing to install; nothing for the owner to do.

G. **Tools.** node v22.22.2, npm 10.9.7, LibreOffice 26.2.6.3 (`soffice`), pdftoppm and pdffonts 26.01.0, ImageMagick present. Absent: rsvg-convert, inkscape, zbarimg, qrencode. System python3 has no cairosvg.

H. **SVG to PNG.** `uv run --no-project --python 3.15 --with cairosvg==2.9.1 python -I render.py <svg> <png>` renders with cairo 1.18.6; cairosvg 2.9.1 is LGPL-3.0-or-later, PyPI latest (2.9.0 was tried first and replaced). The SVGs set `font-family: 'Red Hat Text', system-ui, sans-serif`, so the renders use Red Hat Text. Output is deterministic (equal md5 on re-render); chunks are IHDR, IDAT, bKGD and IEND only, with no text metadata. Figure 03 renders at 1600x1210. The repo's `uv.lock` is untouched.

I. **Scratch deck** (cover, divider, bullets with a figure, a code slide, a table; metadata set to PatternCatalyst). It builds; `docProps` show creator, lastModifiedBy and company PatternCatalyst. Two builds in the same second are byte-identical; `dcterms:created` and `modified` change otherwise. `soffice -env:UserInstallation=file://<scratchpad>/lo-profile --headless --convert-to pdf` converts it, with no soffice process left behind; `pdffonts` lists Overpass-Bold, RedHatText-Regular and Bold, RedHatMono-Regular and Bold and OpenSymbol (bullets), all embedded; the PDF author is PatternCatalyst. `pdftoppm` renders every page. Seen on the renders: a figure at 6.25 in beside bullets has 5 to 7 pt labels (too small); a short listing in a default-height code box leaves most of the dark box empty (pass `opts.h`); logo and page number sit correctly.

J. **Notes trap.** pptxgenjs writes `ppt/notesSlides/notesSlideN.xml` for every slide even without `addNotes`, holding empty text plus the slide-number field. Counting notes files therefore can't fail; the check must read each notes slide's text. The scratch extractor reads the `<a:t>` runs of each notes slide in numeric order and drops the final slide-number run.

K. **Scrubbing.** `host_ids.py check` decodes only UTF-8 and gzip, so it skips a `.pptx`. `host_ids.py filter` doesn't treat the owner's real name as an identifier, so a `dc:creator` carrying it passes the filter. The full name in the password database and `git config user.name` are both set on this host and differ; a check must read them at run time and never record them. Hence decision 15.

L. **Voice scan.** `scan.sh --tier ban --fail` and `--stats` run on a `.js` builder and on extracted notes text (0 hits on the scratch deck); the scanner prunes `node_modules`. On the skill's `deck-helpers.js` it reports 8 ban-tier hits, all em dashes (decision 5). The scanner has no `rNN` pattern; `ITER_RE` in `validate.py` covers it for the deck.

M. **Step letter.** `grep -nE '^\| Y[0-9]' _plans/*.md` and `grep -n 'run: Y' _plans/*.md` print nothing.

N. **URLs.** The site `https://patterncatalyst.github.io/design-patterns-with-python/` and the hub `https://patterncatalyst.github.io/patterncatalyst-workshops-tutorials-list/` return 200; the repo is public with its homepage set.

O. **Survey, chapters 0 to 6 and Appendices A, E and F** (three read-only survey agents, cross-checked by grep). Example and test facts: chapter 0, 9 test functions and 26 cases; the three-way split, 19 tests in `test_dissolve`, `test_disambiguate` and `test_survive`; chapter 5, 14 functions and 19 cases; chapter 6, 13 functions and 17 cases; Appendix F's member, 12 functions and 18 cases. Every test name the inventory cites is defined once under `examples/*/tests`. Chapters 1 and 4 have no example: their slides rest on chapter sentences only, and the census records the sentence and line. The three-way split has no "When not" section. Among chapters 0 to 6, only chapters 5 and 6 carry an AI sidebar. Appendix E: 4 tables, 33 rows, 22 of them mapping to chapters 12 to 25. Appendix A: uv 0.13.7, ruff 0.17.4, mypy 2.4.1; chapter 0: CPython 3.15.2, pytest 9.2.0, pytest-mock 3.17.0. Excerpts confirmed byte-exact: `dissolve.py:35-48`, `pricing.py:16-27` (max 87 chars), `booking.py:12-17` (chapter 6), `app.py:32-45` (lines of 91 and 90 chars), `tax.py:23-28`, `billing.py:40-44`.

P. **Survey, chapters 12 to 18.** Bucket, force and when-not sentences located with line numbers (inventory). 154 test names defined once; fences byte-exact. Excerpts: `rules.py:50-56` (RATE_RULES), `hooks.py:28-35` (CustomsHooks), `table.py:7-14` (TRANSITIONS, line 7 of 93 chars), `booking.py:25-34` (chapter 15, amend and undo, max 71), `factories.py:8-15`, `kits.py:49-60`, `booking.py:14-23` (chapter 17), `quoting.py:3-16`. Comparison tests on one table per chapter (inventory). Figures at 6 in: sub-lines 5 to 6 pt, edge labels 4.8 to 5.3 pt; only figure 12 keeps titles above 7 pt.

Q. **Survey, chapters 19 to 25.** Every cited test defined once; function counts 19=21, 20=35, 21=31, 22=27, 23=28, 24=37, 25=28. Excerpts: `bookings.py:9-17` (max 73), `layers.py:45-53` (max 69), `syntax.py:46-49` (max 85), `consolidation.py:8-16` (max 82), `signal.py:66-81` (16 lines, max 67), `clearance.py:65-68`, `mediator.py:64-74` (max 55), `iterator_protocol/domain.py:30-43` (max 85; the chapter quotes 42-43), `events.py:42-56` (15 lines, max 72), `memento.py:61-70` (max 80), `tariff.py:44-59` (`evaluate`, max 84). The chapter blocks at 20.md:50-71 and 25.md:108-135 and 156-191 join separate source ranges; the deck uses single contiguous ranges only. Figures 19 to 25 at 6 in: sub-lines 4 to 5 pt; figure 25 (viewBox 1250 wide) is the worst; full width raises its sub-lines to about 7 pt.

R. **Figure census** (arrow by arrow, from the specs and the code; Y1b re-runs it after Y1d).

| Fig | Every arrow composed by code? | Deck |
| --- | --- | --- |
| 00 | No: mirrors the `verify.sh` order, omits the mypy-on-scripts step, draws sync inside the loop | out |
| 01, 02, 03 | No: conceptual ("becomes", decision ladder) | out (decision 8 alternative) |
| 04 | No: names `RateStrategy`, which is not code | out |
| 05 | Yes: data flow coordinated by `quote` (`rating.py:24-26`) | in |
| 06 | Yes: `app.py:40-45` and the annotations | in |
| 12 | Yes | in |
| 13 | Yes, but "refuse no commodities" is ambiguous | Y1d, then eligible |
| 14 | Refusal drawn only from Delivered | Y1d, then eligible |
| 15 | Yes, but omits `amend`'s direct call to `apply` | out (omission; slide uses code) |
| 16 | No: a dashed "mypy ties" arrow; `GATEWAYS` to Fastline only | Y1d, then eligible |
| 17 | No: `__post_init__` to "list field shared" | out |
| 18 | No: `quote` to `LoadOnce`, `LoadOnce` to `functools.cache` | out |
| 19 | Yes (registrations at `desk.py:14`; the dashed `Weight.pounds` read at `gateways.py:31`) | in |
| 20 | No: `layers_for` to `compose` is composed only in tests; the `@` arrows are reading order | out |
| 21 | Yes (fixture smaller than the tests' tree) | in, notes say illustration |
| 22 | No: record and lambda drawn into `ExceptionGroup` | Y1d, then eligible |
| 23 | No: `Held` to `ClearanceMediator` | Y1d, then eligible |
| 24 | No: the `__iter__` and `close()` arrows are conceptual | out |
| 25 | Yes (`memento.py:53-68`, `tariff.py:80-83`) | in |

S. **Name collisions** (same name, different definition, across 101 chapters). `Consignment` (25 definitions), `Weight` (19), `Money` (24; `__add__` raises `RatingError` in chapter 20 and `ValueError` in chapter 25), `Booking` (frozen value in chapter 19, mutable entity in chapter 25), `CarrierGateway` (9), `HandlingEvent` (one class in chapters 22 to 24, a five-class union in chapter 25), `TrackingHistory` (`events` in 22 and 23, `__iter__` in 24), `describe` (23 and 25), `Commodity` (21 and 23), `RateCalculator`, `BaseRate`, `Surcharge`, `quote_carrier`, `CarrierGatewayProxy` (three-way split against chapter 20, where the split's proxy forwards through `__getattr__`, the form chapter 20 argues against), the tariff zones ("EU" against "EUROPE"). Decision 11 keeps each slide to one chapter's definitions, and the notes name the chapter's concept where a reader could confuse two.

T. **Defects found** (decision 10). Located by the surveys and re-read at the cited lines: 22.md:34, 22.md:213, 23.md:65, 25.md:218, `examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/mediator.py:1`, figure specs 13, 14, 16, 22, 23, and the missing `alt` key in `_data/diagrams.yml`. Checked and not a defect: the two `docs.python.org/3/builtins/...` links in chapter 24 return 200.

U. **Books the 101 chapters cite** (from `bibliography.html` and the chapters): *Design Patterns* (Gamma, Helm, Johnson, Vlissides, 1994); *Fluent Python* (Ramalho, 2022); *Effective Python*, third edition (Slatkin, 2024); *Architecture Patterns with Python* (Percival, Gregory, 2020); *Python Object-Oriented Programming*, fifth edition (Lott, Phillips, 2025); *Agile Software Development* (Martin, 2002); *Object-Oriented Software Construction* (Meyer, 1997); *Domain-Driven Design* (Evans, 2003); *Patterns of Enterprise Application Architecture* (Fowler, 2002); *The Pragmatic Programmer* and *Clean Code* where Appendix F cites them. Y1b confirms each against the chapter that cites it; a book no 101 chapter cites is left to the deck that covers its chapter.

V. **Assets.** `cover-panel.png`, `section-panel.png`, `redhat-logo-white.png` and `logo-candidate-2.png` in the skill's `assets/` match every sibling's copy by md5.

## The three-deck arc

Every chapter and appendix sits in exactly one deck. A deck may name a pattern another deck develops, by concept only, in one bullet at most.

| Deck | Theme | Chapters | Slides (est.) |
| --- | --- | --- | --- |
| 101, Patterns and SOLID in Python (r22) | Patterns as decisions under forces, the three-way split, SOLID, and the catalogue patterns as Python writes them | Part 0 (0), Part 1 (1), Part 2 (2 to 4), Part 3 (5, 6), Parts 5 to 8 (12 to 25); Appendices A, E, F | 62 |
| 201, Idiomatic Python (r23) | What the language gives you so you don't write the pattern | Part 4 (7 to 10), Part 9 (26 to 30), Part 10 (31, 32), Part 12 (37, 38) | about 45 |
| 301, Testing, legacy code and AI (r24) | Proving it works, changing inherited code, and AI on pattern-heavy code | Part 4's testing chapter (11), Part 11 (33 to 36), Part 13 (39, 40); Appendices B, C, D | about 40 |

Boundary rules:
- **Visitor.** 101: the closed set, `match` with `assert_never` ("Visitor, Memento, and Interpreter"). 201: the open set ("singledispatch: the Visitor the language gives you").
- **Decorator.** 101: the disambiguation, the pattern against the syntax. 201: writing decorators well ("Decorators done right").
- **Proxy.** 101: the surrogate object that keeps the interface. 201: attribute interception ("Descriptors and properties"; "Dynamic attributes: __getattr__ and Proxy as a feature").
- **Null Object, Value Object, "Interface", Resource acquisition, Metaclass registry, If-chain dispatch.** 201 develops them; 101 shows them only as rows of the three-way split's map.
- **Composition root.** 101: the composition root as dependency inversion. 301: the final project's composition root.
- **AI.** 101: naming patterns for teams and assistants, and the catalogue chapters' prompt sidebars. 301: working with AI tools and the gates on their output.
- **Anti-patterns.** 201 ("Anti-patterns and pattern misuse"); 301 refers to them by concept only.
- **Testing.** 101 cites tests as witnesses and never teaches testing; 301 teaches it.

Notes for r23 and r24: the PRD's 301 line names "Java-in-Python" output; the decks use the book's own wording for that chapter's concept, since a language name there trips the cross-language word check. Both decks reuse this iteration's `presentation/` scaffold, helper, `render-png.sh` and `check_decks()` unchanged, and the figure census rule.

## Deck 101 slide inventory

Columns: # (build order); section; title (2 to 5 word noun phrase); claim and its chapter sentence (`NN.md:line`); witness (tests, or "prose" where the chapter has no example); code (file and lines) or figure; what the notes cover. Chapter exact titles are in the witness table (Y1b). Code paths are under `examples/<chapter dir>/src/<package>/`. Y1b confirms every line number, quote and test against the source; anything that differs is recorded in Corrections, and a claim that can't be witnessed is cut before the builder runs.

| # | Section | Title | Claim (source) | Witness | Code or figure | Notes cover |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Cover | Design Patterns with Python | 101: Patterns and SOLID in Python | - | cover panel | what the book is, who the deck is for, the shipping domain every example uses |
| 2 | Cover | The deck's route | the nine sections in order | - | bullets | how the sections build on each other, by concept |
| 3 | Why patterns | divider | - | - | section panel | why a pattern book for a dynamic language |
| 4 | Why patterns | Decisions under forces | a pattern is a decision a force asks for, with consequences (ch1, census line) | prose | bullets | the force, the consequence ledger, when a pattern is the wrong answer |
| 5 | Why patterns | Proof that runs | every claim runs under the toolchain; the consignment is a frozen value (ch0) | `test_equal_values_compare_equal`, `test_reweigh_returns_new_consignment_and_leaves_original_unchanged`, `test_instance_rejects_assignment` | `consignments/consignment.py`, the range chapter 0 quotes (Y1b fixes it; summary 36-43) | uv, ruff, mypy and pytest as the bar every slide's code passed |
| 6 | What 1994 assumed | divider | - | - | section panel | the catalogue's assumptions and what changed |
| 7 | What 1994 assumed | The 1994 assumptions | the catalogue assumed no first-class functions, no structural types (ch2, census lines) | prose plus the three-way split's dissolve tests | bullets | each assumption and the feature that removed it |
| 8 | What 1994 assumed | Three ways out | each pattern dissolves, survives or needs disambiguating (03.md, bucket definitions) | `test_strategy_slot_accepts_def_lambda_and_partial`, `test_undo_needs_a_command_object`, `test_the_two_decorators_are_independent` | bullets | the two questions that sort a pattern |
| 9 | What 1994 assumed | What dissolves | the eleven "Dissolves" rows (03.md:45-55) | the split's `test_dissolve` tests | table: Pattern, What Python gives you | how a feature resolves the force without the structure |
| 10 | What 1994 assumed | What survives | the fourteen "Survives" rows (03.md:56-69) | `test_survive` tests | table | what stays design in each |
| 11 | What 1994 assumed | One name, two meanings | the four "Needs disambiguating" rows (03.md:70-73) | `test_disambiguate` tests | table | why a shared name misleads, by concept |
| 12 | What 1994 assumed | Dissolved in code | a rule is a `Callable[[Consignment], Money]` and `quote` takes any (03.md:75) | `test_strategy_slot_accepts_def_lambda_and_partial` | `three_way_split/dissolve.py:35-48` | `def`, lambda and `partial` in one slot; no `RateStrategy` |
| 13 | What 1994 assumed | Names for assistants | a pattern name tells a team and an assistant which decision was made (ch4, census lines) | prose | bullets | naming in prompts and reviews; the deck's prompt sidebars build on it |
| 14 | SOLID in Python | divider | - | - | section panel | SOLID as forces Python meets with functions, Protocols and modules |
| 15 | SOLID in Python | One reason to change | each change moves only the fields it feeds (ch5) | `test_each_change_moves_only_the_fields_it_feeds`, `test_pricing_and_tax_run_alone`, `test_audit_receives_exactly_the_quote_returned` | bullets | pricing, tax and audit as separate reasons |
| 16 | SOLID in Python | How a quote flows | figure 05 | its arrows (census R) | figure 05 full width | each box and arrow, read from the code |
| 17 | SOLID in Python | Open to a new tax | a tax rule is added without editing `quote` (ch5) | `test_a_new_tax_rule_is_added_without_editing_quote`, `test_default_tax_table_is_read_only` | `srp_ocp_lsp/tax.py:23-28` | the read-only table as the extension point |
| 18 | SOLID in Python | The rate contract | the contract is the docstring plus tests; mypy can't see a behavioural violation (ch5) | `test_calculator_honours_the_rate_contract`, `test_contract_catches_a_strengthened_precondition`, `test_mypy_cannot_see_a_behavioural_violation` | `srp_ocp_lsp/pricing.py:16-27` | Liskov and Wing, Meyer, credited as chapter 5 does |
| 19 | SOLID in Python | Narrow roles | a narrow Protocol per role (ch6) | `test_adapters_satisfy_every_role_without_naming_one`, `test_a_fat_protocol_forces_fakes_to_stub_unused_methods` | `isp_dip_di/booking.py:12-17` | role interfaces, fakes that stub nothing |
| 20 | SOLID in Python | The composition root | one function wires the application (ch6) | `test_build_app_shares_one_gateway_between_booking_and_tracking`, `test_composition_root_accepts_a_substitute_without_patching`, `test_policy_modules_do_not_import_the_adapters` | `isp_dip_di/app.py:32-45` (font size from the 91-char line) | Fowler's injection article and Seemann's Composition Root, as chapter 6 credits them |
| 21 | SOLID in Python | Wiring the application | figure 06 | census R | figure 06 full width | what each arrow is in `build_app` |
| 22 | SOLID in Python | Principles beyond SOLID | Appendix F's principles and their witnesses (46.md table) | F member tests, census | table: Principle, Witness | each principle as F states it |
| 23 | SOLID in Python | Ask the shipment | the reader asks the shipment for the amount due (46.md, Demeter) | `test_a_credit_reaches_only_the_reader_that_asks_the_shipment`, `test_both_readers_give_the_same_line_without_credits` | `principles_reviewed/billing.py:40-44` | the Demeter project pages, credited as F credits them |
| 24 | Selecting and varying behaviour | divider | - | - | section panel | the behaviour patterns |
| 25 | Selecting and varying behaviour | Strategy as a callable | 12.md:34 "This pattern dissolves, because a feature resolves the force without the pattern's structure." | `test_a_class_per_strategy_passes_the_same_table`, `test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one` | `strategy_callable` package `rules.py:50-56` (Y1b fixes the package path) | the registry, `partial`, a callable class; when-not 12.md:184 |
| 26 | Selecting and varying behaviour | Rules in a registry | figure 12 | census R | figure 12 full width | each rule and how `quote` reaches it |
| 27 | Selecting and varying behaviour | Hooks, not subclasses | 13.md:36 "The pattern straddles two buckets." | `test_declare_customs_runs_its_steps_in_order`, `test_a_hook_left_out_takes_its_default`, `test_a_required_hook_cannot_be_left_out`, the `declare` fixture's hooks and template params | `hooks.py:28-35` | the `final` ABC where steps share state; when-not 13.md:214 |
| 28 | Selecting and varying behaviour | State as a table | 14.md:34 "The pattern survives, and the transition table is the design." | `test_state_objects_pass_the_same_lifecycle_table`, `test_an_illegal_event_is_a_transition_error`, `test_the_transition_table_is_read_only` | `table.py:7-14` (93-char line sets the size) | the table against state objects; when-not 14.md:200 |
| 29 | Selecting and varying behaviour | Command with undo | 15.md:42 "So the bucket is survives, with the deferred call dissolving." | `test_apply_returns_the_amendment_that_reverses_it`, `test_a_failing_batch_leaves_the_booking_unchanged`, `test_amendments_compare_by_value_and_partials_do_not` | `booking.py:25-34` (chapter 15) | the force 15.md:36; when-not 15.md:220 |
| 30 | Creating objects under control | divider | - | - | section panel | the creational patterns |
| 31 | Creating objects under control | Factories in a dict | 16.md:38 "The creator subclass becomes a value in a slot." | `test_a_registered_constructor_builds_each_carrier_gateway`, `test_the_creator_design_declares_three_classes_where_the_registry_declares_none`, `test_an_unknown_carrier_code_is_an_unknown_carrier_error` | `factories.py:8-15` | the heading "Factory Method dissolves" as the bucket |
| 32 | Creating objects under control | A family of gateways | 16.md:130 "The bucket is survives." | the kit tests (census) | `kits.py:49-60` | why a family is still a decision; when-not 16.md:189 |
| 33 | Creating objects under control | Builder as a dataclass | 17.md:36 Builder "...so the bucket is dissolves"; Prototype 17.md:130 | `test_both_constructors_pass_the_booking_table`, `test_a_positional_constructor_accepts_a_swapped_origin_and_destination`, `test_a_template_and_replace_give_a_new_request` | `booking.py:14-23` (chapter 17) | `kw_only`, `dataclasses.replace`; when-not 17.md:199 |
| 34 | Creating objects under control | Singleton as a module | 18.md:41; 18.md:193 "A class whose only reason to exist is to be single is a module." | `test_every_form_gives_each_caller_the_same_rates`, `test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check` | `quoting.py:3-16` | lazy import, Borg and metaclass as the variants |
| 35 | Composing and adapting structure | divider | - | - | section panel | the structural patterns |
| 36 | Composing and adapting structure | Adapter, Facade and Bridge | 19.md:36 "All three patterns in this chapter survive." and 19.md:50 | `test_a_client_whose_shape_matches_needs_no_adapter`, `test_mypy_rejects_a_client_with_a_different_shape`, `test_ship_books_each_carrier_through_one_call`, `test_a_carrier_rejection_becomes_a_carrier_error` | bullets | each force (19.md:38, 136, 166); when-not 19.md:221; Rhodes's page, credited |
| 37 | Composing and adapting structure | A bridge over a Protocol | 19.md:203 "That's N×M against N+M." | `test_every_booking_kind_works_with_every_carrier`, `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier`, `test_a_new_booking_kind_needs_no_gateway_change` | `bookings.py:9-17` | 19.md:209 the cost and the benefit |
| 38 | Composing and adapting structure | One call, two axes | figure 19 | census R | figure 19 full width | each arrow, including the dashed unit read |
| 39 | Composing and adapting structure | Two things called Decorator | 20.md:41 bucket; 20.md:37 the one-line contrast | `test_the_layers_for_a_consignment_are_chosen_while_the_program_runs`, `test_the_at_sign_rebinds_the_name_once_at_definition_time`, `test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped`, `test_mypy_rejects_a_decorated_function_where_a_calculator_belongs` | bullets | the naming rule 20.md:43; PEP 318's own words, as the chapter quotes them |
| 40 | Composing and adapting structure | Wrapper objects at run time | 20.md:39 force; 20.md:76 "Order matters once a layer adds a fixed amount." | `test_a_layer_wraps_a_calculator_and_leaves_it_unchanged`, `test_layer_order_changes_the_price_when_a_fee_is_added`, `test_compose_wraps_the_last_layer_outermost` | `decorator_proxy/layers.py:45-53` | Rhodes's Decorator page, credited; when-not 20.md:200 |
| 41 | Composing and adapting structure | A name rebound once | 20.md:102 "The `@` form is a statement about a name."; 20.md:119 | `test_the_at_sign_rebinds_the_name_once_at_definition_time`, `test_syntax_stacking_order_decides_whether_each_attempt_is_audited`, `test_rebound_functions_do_not_compare_by_value` | `decorator_proxy/syntax.py:46-49` | the idempotency when-not (20.md:200, prose); the 201 deck writes decorators well, by concept |
| 42 | Composing and adapting structure | A proxy keeps the interface | 20.md:125 force; 20.md:125 "a proxy returns what the subject returns"; Proxy's bucket from the three-way split's map row | `test_the_proxy_asks_the_gateway_once_per_consignment`, `test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price`, `test_mypy_reports_a_typo_on_the_explicit_proxy`, `test_mypy_accepts_a_typo_through_a_forwarding_proxy` | bullets | explicit against forwarding; when-not 20.md:200 |
| 43 | Composing and adapting structure | One weight question | 21.md:23 "Both patterns survive in Python..."; 21.md:103 | `test_a_consignment_and_a_consolidation_answer_weight_the_same_way`, `test_a_flat_sum_misses_nested_consolidations`, `test_mypy_refuses_adding_to_a_frozen_consolidation` | `composite_flyweight/consolidation.py:8-16` | Rhodes's Composite page quoted as the chapter quotes it; Flyweight 21.md:134, 169, 195 with `test_the_weak_pool_drops_a_commodity_nobody_holds`, `test_split_port_codes_are_equal_but_distinct_objects` |
| 44 | Composing and adapting structure | Shared commodities | figure 21 | census R | figure 21 full width | that the figure draws a smaller tree than the tests build |
| 45 | Coordinating and traversing | divider | - | - | section panel | the behavioural patterns that coordinate and traverse |
| 46 | Coordinating and traversing | What a signal decides | 22.md:58 bucket and the two sentences after it | `test_subscribers_are_called_in_subscription_order`, `test_one_failing_subscriber_does_not_stop_the_rest`, `test_every_failure_is_reported_after_delivery`, `test_a_bound_method_subscriber_is_dropped_when_its_owner_goes`, `test_an_event_published_during_delivery_waits_its_turn` | `observer/signal.py:66-81` | PEP 654 credited; when-not 22.md:217 |
| 47 | Coordinating and traversing | A chain of stages | 23.md:38 bucket and "The class that carries the successor link is the part Python removes." | `test_the_first_stage_that_decides_wins`, `test_stages_after_a_decision_are_not_called`, `test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage` | `mediator_chain/clearance.py:65-68` | 23.md:113 order is a property of the tuple; when-not 23.md:182 |
| 48 | Coordinating and traversing | One release rule | 23.md:127; 23.md:166 | `test_the_mediator_releases_in_either_order`, `test_a_choreography_loses_a_settlement_that_arrives_before_inspection`, `test_a_duplicate_settlement_releases_once` | `mediator_chain/mediator.py:64-74` | 23.md:178 the cost; when-not 23.md:182 |
| 49 | Coordinating and traversing | Generators as iterators | 24.md:47 bucket; 24.md:30 | `test_a_tracking_history_can_be_walked_twice`, `test_a_self_iterating_history_is_empty_on_the_second_pass`, `test_the_first_page_reads_only_one_page`, `test_breaking_out_of_a_loop_leaves_a_named_reader_open` | `iterator_protocol/domain.py:30-43` | one pass or many, how much to read, who closes; Rhodes's Iterator page, credited; when-not 24.md:151 |
| 50 | Coordinating and traversing | Visitor as a match | 25.md:36 bucket | `test_mypy_reports_an_event_left_out_of_a_match`, `test_status_after_maps_each_event_to_a_consignment_status`, `test_every_visitor_form_describes_a_journey_the_same_way` | `visitor_memento_interpreter/events.py:42-56` | the closed set here, the open set in the 201 deck, by concept; when-not 25.md:218 |
| 51 | Coordinating and traversing | Snapshot and rollback | 25.md:105 bucket; 25.md:138 | `test_rollback_keeps_the_audit_trail`, `test_a_deepcopy_memento_erases_the_audit_trail_on_rollback`, `test_rollback_restores_the_attached_documents` | `visitor_memento_interpreter/memento.py:61-70` | what to capture and what must not roll back |
| 52 | Coordinating and traversing | A tariff, two readings | 25.md:153 bucket; 25.md:202 | `test_explain_writes_the_tariff_as_text`, `test_every_rule_form_prices_the_same_consignments`, `test_mypy_reports_a_tariff_node_left_out_of_evaluate` | `visitor_memento_interpreter/tariff.py:44-59` | frozen nodes under `type Expr`; PEP 634 and 636 credited |
| 53 | Coordinating and traversing | Match, snapshot, tariff tree | figure 25 | census R | figure 25 full width | each column, read from the code |
| 54 | Choosing well | divider | - | - | section panel | choosing, and not choosing, a pattern |
| 55 | Choosing well | When not to | when-not sentences quoted from the catalogue chapters (12.md:184, 14.md:200, 18.md:193, 19.md:221, 22.md:217, 24.md:151) | prose (the chapters give no test for these) | table: Pattern, Skip it when | the force that is absent in each case |
| 56 | Choosing well | Pattern to force | Appendix E rows mapping to the catalogue chapters (45.md, census picks at most 12 rows verbatim) | census `grep -F` per cell | table | how to read the reference by force |
| 57 | Choosing well | Prompting for a pattern | a catalogue chapter's sidebar prompt and review line, quoted (25.md:220-226) | prose | bullets plus the quoted prompt | naming the decision, then asking for the failing test |
| 58 | Reference | divider | - | - | section panel | where to go next |
| 59 | Reference | The toolchain | Appendix A and chapter 0 versions | Y0 pin check; `scripts/verify.sh` | table: Tool, Version | uv, ruff, mypy, pytest, pytest-mock, CPython |
| 60 | Reference | Sources credited | the online sources the 101 chapters cite (Rhodes's python-patterns.guide pages, the PEPs, Fowler, Seemann, Liskov and Wing, the Demeter project) | census | table: Source, Used for | each, as the chapters word them |
| 61 | Reference | Reading further | the books in evidence U | census | table: Book, Author, Year | what each adds |
| 62 | Reference | Take it with you | the site, repository and hub URLs (evidence N) | URLs return 200 at Y4a | bullets | the examples, how to run them, the next two decks by theme |

## Build setup

```
presentation/
  package.json          # private, "pptxgenjs": "4.0.1", overrides image-size 2.1.0
  package-lock.json     # committed, lockfileVersion 3; install with `npm ci`
  deck-helpers.js       # the skill's, em dashes recast (decision 5)
  deck-101.js           # the builder
  render-png.sh         # diagrams/<name>.svg -> png/<name>.png via uv + cairosvg 2.9.1
  notes.py              # extracts slide and notes text for the voice scan (stdlib only)
  build-notes.md        # pins, the helper delta, how to build
  assets/               # the skill's four PNGs (decision 6)
  png/                  # committed renders of the figures the deck uses
  design-patterns-with-python-101-patterns-and-solid.pptx
```

Build, from `<repo>/presentation`: `npm ci`; `./render-png.sh 05 06 12 19 21 25`; `node deck-101.js`. The builder: `newDeck()`, then the metadata of decision 6; an `S()` content-slide wrapper and a `divider()` helper as the siblings use; a `code(slideTitle, path, first, last, anchor, opts)` helper that reads the source lines (decision 11) and computes `fontSize` and `h`; a `fig(name)` slide at full width; `addNotes` on every slide, with notes held in the builder as plain strings; a final assertion that every slide was given notes of at least its floor. `.gitignore` gains `presentation/qa/` and `presentation/*.pdf`.

## QA pipeline (Y4a, Y4b, Y5)

1. `npm ci` in `presentation/`; `node -e "console.log(require.resolve('pptxgenjs'))"` shows the local copy (recorded scrubbed).
2. `./render-png.sh` for the deck's figures; `git diff --exit-code presentation/png` after a fresh render.
3. `node deck-101.js`.
4. `soffice -env:UserInstallation=file://<scratchpad>/lo-qa --headless --convert-to pdf --outdir presentation/qa <deck>.pptx`; afterwards `pgrep -f soffice` prints nothing.
5. `pdffonts presentation/qa/<deck>.pdf`: Overpass, Red Hat Text and Red Hat Mono present and embedded, no other text family except OpenSymbol.
6. `pdftoppm -jpeg -r 110 presentation/qa/<deck>.pdf presentation/qa/p`: one image per slide; count equals 62.
7. `python3 presentation/notes.py <deck>.pptx > presentation/qa/deck-101-notes.txt` and `--slides` into `deck-101-slides.txt`.
8. `bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh --tier ban --fail` on `deck-101.js` and both text files, then `--stats` on the notes text, with the house-voice rubric applied by reading.
9. `uv run python scripts/validate.py` (runs `check_decks`), `--self-test`, `--claims`; `scripts/verify.sh`; `python3 scripts/host_ids.py check`.
10. `unzip -p <deck> docProps/core.xml docProps/app.xml` shown in the QA record.
11. Eyeballing. The Y4a executor views every page image once and fixes what it sees. At Y5 two Opus validator passes view the images independently: pass one slides 1 to 31, pass two slides 32 to 62, each against a checklist: logo and page number placed, no text overflow or clipped code, code box height fits the listing, one-line code captions, figure text legible at slide size, table cells not wrapping mid-word, divider titles, notes present (from the text file). Findings go to the QA record with the page number.
12. A rebuild changes only the `core.xml` timestamps; the committed deck is the last build after Y5's final repair, and the diff of a no-change rebuild is reverted rather than committed.

## Evidence files

- `_plans/evidence/r22-deck-witness-census.md` (Y1b): per slide, the chapter's exact title, the cited sentence quoted with `NN.md:line`, the test names with file and line and a `grep -c 'def <name>('` of 1, each code range with its anchor and max line length and a byte-exact check against the chapter fence where the chapter quotes it, the Appendix E cells with their `grep -F` result, the credits per slide, and the figure census re-run after Y1d.
- `_plans/evidence/r22-deck-qa.md` (Y4a, appended at Y4b and Y5): the pipeline commands and outputs (scrubbed with `host_ids.py filter`), `pdffonts`, `docProps`, notes word-count table, scan results, and the eyeballing findings per page and their fixes.

## Steps and status

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| Y0 | Bookkeeping with dated notes: `iteration-plan.md` r21 closed, PDP-144 to 146 `done`, PDP-150 `active`, r22 active; re-check every pin (decisions 4 and the header); record the decisions; `verify.sh` and `validate.py` green | - | done |
| Y1a | `presentation/` scaffold: `package.json`, `npm ci` and the committed lockfile, the helper with its delta, the assets, `render-png.sh`, `notes.py`, `build-notes.md`, `.gitignore` lines, the six figure PNGs | Y0 | done |
| Y1b | `_plans/evidence/r22-deck-witness-census.md`, in parallel with Y1a and Y1c; re-run of the figure census after Y1d | Y0, Y1d | todo |
| Y1c | `check_decks()` in `validate.py` with self-test cases (a deck with an empty notes slide, a wrong creator, an em dash in notes, an `rNN` token, a chapter number reference, a runtime name in `core.xml`; each must fail); green with no deck present | Y0 | done |
| Y1d | Decision 10's fixes: four prose edits, one docstring, five figure specs regenerated through `diagrams/specs`, the registry decision; each chapter's tests, `verify.sh` and `validate.py` green after the edits | Y0 | done |
| Y2 | Rows 313 to 349 into `_plans/reconciliation-plan.md` with a dated note; every quote, line or test that differs from this plan goes in Corrections; a failed witness cuts the slide | Y1b, Y1c, Y1d | todo |
| Y3 | `deck-101.js` (Sonnet executor) from the inventory and the census, notes written to decision 12 | Y1a, Y2 | todo |
| Y4a | Build and the QA pipeline steps 1 to 11 (executor view of every page); `_plans/evidence/r22-deck-qa.md`; README "Companion decks" section and licence line | Y3 | todo |
| Y4b | Voice pass on `deck-101.js` and the extracted notes: ban tier, `--stats`, the house-voice rubric; rebuild and re-run pipeline steps 3 to 9 | Y4a | todo |
| Y5 | Opus validation: two independent page passes (QA step 11), every witness row checked (at least one in three re-run), the excerpt check (each code slide against its source), the claims audit (`validate.py --claims`), the overlap check against the arc, rows 350 to 356 added and closed; up to two repair rounds, each followed by a full pipeline re-run | Y4b | todo |
| Y6 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r22.x` on main; notes-only release | Y5 | todo |

## Reconciliation rows

Rows 313 to 349 go in at Y2, after the census exists (their `run:` path then resolves) and with only test names the census confirmed. Rows 350 to 356 cite `run: Y4a` and `run: Y4b` and go in at Y5, after those steps are `done`. The Ch cell is the source chapter's number, so `chapter_numbers` parses it.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 313 | 1 | Deck: a pattern is a decision a force asks for | quoted sentence; run: _plans/evidence/r22-deck-witness-census.md |
| 314 | 0 | Deck: the consignment is a frozen value | `test_equal_values_compare_equal`, `test_instance_rejects_assignment`; run: _plans/evidence/r22-deck-witness-census.md |
| 315 | 2 | Deck: the 1994 assumptions and the features that removed them | quoted sentences; run: _plans/evidence/r22-deck-witness-census.md |
| 316 | 3 | Deck: dissolve, survive, disambiguate | `test_strategy_slot_accepts_def_lambda_and_partial`, `test_undo_needs_a_command_object`, `test_the_two_decorators_are_independent` |
| 317 | 3 | Deck: the three map tables match the chapter's rows verbatim | run: _plans/evidence/r22-deck-witness-census.md |
| 318 | 4 | Deck: names for teams and assistants | quoted sentences; run: _plans/evidence/r22-deck-witness-census.md |
| 319 | 5 | Deck: one reason to change | `test_each_change_moves_only_the_fields_it_feeds`, `test_pricing_and_tax_run_alone` |
| 320 | 5 | Deck: a tax rule added without editing `quote` | `test_a_new_tax_rule_is_added_without_editing_quote`, `test_default_tax_table_is_read_only` |
| 321 | 5 | Deck: the rate contract and what mypy can't see | `test_calculator_honours_the_rate_contract`, `test_mypy_cannot_see_a_behavioural_violation` |
| 322 | 6 | Deck: narrow roles | `test_adapters_satisfy_every_role_without_naming_one`, `test_a_fat_protocol_forces_fakes_to_stub_unused_methods` |
| 323 | 6 | Deck: the composition root | `test_build_app_shares_one_gateway_between_booking_and_tracking`, `test_composition_root_accepts_a_substitute_without_patching` |
| 324 | 46 | Deck: principles beyond SOLID and the Demeter reader | `test_a_credit_reaches_only_the_reader_that_asks_the_shipment`, `test_both_readers_give_the_same_line_without_credits` |
| 325 | 12 | Deck: Strategy dissolves into a callable | `test_a_class_per_strategy_passes_the_same_table` |
| 326 | 13 | Deck: Template Method straddles two buckets | `test_declare_customs_runs_its_steps_in_order`, `test_a_required_hook_cannot_be_left_out` |
| 327 | 14 | Deck: State survives as a transition table | `test_state_objects_pass_the_same_lifecycle_table`, `test_an_illegal_event_is_a_transition_error` |
| 328 | 15 | Deck: Command survives for undo | `test_apply_returns_the_amendment_that_reverses_it`, `test_a_failing_batch_leaves_the_booking_unchanged` |
| 329 | 16 | Deck: Factory Method dissolves into a registry | `test_a_registered_constructor_builds_each_carrier_gateway` |
| 330 | 16 | Deck: Abstract Factory survives as a kit | kit tests named in the census; run: _plans/evidence/r22-deck-witness-census.md |
| 331 | 17 | Deck: Builder dissolves into a keyword-only dataclass | `test_both_constructors_pass_the_booking_table`, `test_a_template_and_replace_give_a_new_request` |
| 332 | 18 | Deck: Singleton as a module | `test_every_form_gives_each_caller_the_same_rates` |
| 333 | 19 | Deck: Adapter, Facade and Bridge survive | `test_a_client_whose_shape_matches_needs_no_adapter`, `test_ship_books_each_carrier_through_one_call` |
| 334 | 19 | Deck: a bridge is N+M against N×M | `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier`, `test_every_booking_kind_works_with_every_carrier` |
| 335 | 20 | Deck: the Decorator pattern composes at run time | `test_the_layers_for_a_consignment_are_chosen_while_the_program_runs`, `test_layer_order_changes_the_price_when_a_fee_is_added` |
| 336 | 20 | Deck: the `@` form rebinds a name once | `test_the_at_sign_rebinds_the_name_once_at_definition_time`, `test_syntax_stacking_order_decides_whether_each_attempt_is_audited` |
| 337 | 20 | Deck: the two don't blur | `test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped`, `test_mypy_rejects_a_decorated_function_where_a_calculator_belongs` |
| 338 | 20 | Deck: a proxy keeps the interface | `test_the_proxy_asks_the_gateway_once_per_consignment`, `test_mypy_reports_a_typo_on_the_explicit_proxy` |
| 339 | 21 | Deck: Composite and Flyweight survive | `test_a_consignment_and_a_consolidation_answer_weight_the_same_way`, `test_the_weak_pool_drops_a_commodity_nobody_holds` |
| 340 | 22 | Deck: what a signal decides | `test_one_failing_subscriber_does_not_stop_the_rest`, `test_a_bound_method_subscriber_is_dropped_when_its_owner_goes` |
| 341 | 23 | Deck: the first stage that decides wins | `test_the_first_stage_that_decides_wins`, `test_stages_after_a_decision_are_not_called` |
| 342 | 23 | Deck: one release rule in a mediator | `test_the_mediator_releases_in_either_order`, `test_a_duplicate_settlement_releases_once` |
| 343 | 24 | Deck: a generator replaces the cursor class | `test_a_tracking_history_can_be_walked_twice`, `test_a_self_iterating_history_is_empty_on_the_second_pass` |
| 344 | 25 | Deck: Visitor dissolves into a match | `test_mypy_reports_an_event_left_out_of_a_match` |
| 345 | 25 | Deck: a snapshot that leaves the audit alone | `test_rollback_keeps_the_audit_trail` |
| 346 | 25 | Deck: one tariff, two readings | `test_explain_writes_the_tariff_as_text`, `test_every_rule_form_prices_the_same_consignments` |
| 347 | 45 | Deck: Appendix E rows quoted verbatim | run: _plans/evidence/r22-deck-witness-census.md |
| 348 | 22-23 | Chapter fixes: the delivery sentence, the docstring sentence, the default-tuple sentence, the mediator docstring | run: Y1d |
| 349 | 13-23 | Figure fixes: specs 13, 14, 16, 22, 23 regenerated and every arrow composed | run: Y1d |
| 350 | 0-46 | Deck: every code slide is byte-exact with its source range | run: Y4a |
| 351 | 0-46 | Deck: 62 slides, 62 notes slides, every notes slide over its floor | run: Y4a |
| 352 | 0-46 | Deck: Red Hat Text, Red Hat Mono and Overpass embedded in the render | run: _plans/evidence/r22-deck-qa.md |
| 353 | 0-46 | Deck: metadata PatternCatalyst, no host identifier or runtime name in any part | run: Y4a |
| 354 | 0-46 | Deck: ban-tier scan clean on the builder, slide text and notes | run: Y4b |
| 355 | 0-46 | Deck: committed figure PNGs equal a fresh render | run: _plans/evidence/r22-deck-qa.md |
| 356 | 0-46 | Deck: every rendered page viewed and passed | run: _plans/evidence/r22-deck-qa.md |

## Corrections after the build
- Step Y1c: `check_decks()` reads the slide kinds from the deck itself. Slide 1 is the cover, and a divider is any slide whose `<p:bg>` fill is `AB0000`, the fill the dividers in the sibling decks use. So **every divider must keep the `AB0000` background**, or the divider's notes are held to 90 words instead of 45. The cross-language check is case-sensitive and matches `\bGo\b`, so notes must not start a sentence with "Go". The "slide N" pattern is a separate regex. The check finds decks by globbing `presentation/*.pptx`, not with `git ls-files`. It reads the owner's name at run time from GECOS and `git config user.name`. It has 13 self-test cases.
- Step Y1d: four prose fixes and the `mediator.py` docstring, shortened to 97 characters for E501. Chapter 23 repeated the wrong "a held declaration goes to the mediator" claim in its front matter, its intro, its wrap-up list, its card body, its README and its caption, and every copy is fixed. Figures: in 13 the guard is "refuse an empty consignment". In 14 a refusal box takes dashed arrows from all five statuses, the canvas is 620 high, and the caption adds "and any other pair is refused". In 16 both dashed arrows are removed, leaving GATEWAYS and the mypy note as unconnected annotations. In 22 only the failing subscriber's edge goes to `ExceptionGroup`. In 23 the Held to mediator arrow is removed, and mediator to `record` stays, composed through `release=` (conftest.py:148). Row 348's text should read "the delivery sentence, the module-docstring sentence, the tuple sentence (not a default), the mediator docstring". Verified at 9f608b2: `verify.sh` passes, and validate reports 0 errors and 6 warnings.

- **Step Y0:** (2026-11-07) `iteration-plan.md`: r21 closed, PDP-144 to 146 `done`, PDP-150 and r22 `active`, dated note added. The owner decisions were already recorded in this plan's "Owner decisions, 2026-11-07" section, so nothing was added for them. The pin re-check found every pin unchanged: pptxgenjs 4.0.1 (`dist-tags.latest`; `beta` is 4.0.1-beta.2), image-size 2.1.0, cairosvg 2.9.1, CPython 3.15.2, uv 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4. The three new rows (pptxgenjs, image-size, cairosvg) went into the dated toolchain table in `r01-build-plan.md`, with a dated line under it. `verify.sh` passed on the working tree (1405 passed). Y1d edits were in flight in the same tree, so `validate.py` was run on a copy of HEAD plus the Y0 plan edits and printed `0 error(s), 6 warning(s)`; the working tree's `validate.py` showed two caption-length errors that belong to the Y1d figure work.
- **Step Y1a:** (2026-11-07) `package-lock.json` is lockfileVersion 3 with 19 packages and image-size resolved at 2.1.0; `npm install` then `npm ci` ran inside `presentation/` only, and `npm audit` printed `found 0 vulnerabilities` for both. `require.resolve('pptxgenjs')` printed `<repo>/presentation/node_modules/pptxgenjs/dist/pptxgen.cjs.js`. `deck-helpers.js` changed on 8 lines only (comments and the default `pres.title`), md5 abedd5abb9a98c475b1d050febc25ca7 to 47af3889bef56eba4736bb1565e17054, and `node --check` passes. `render-png.sh` rendered the six figures (05, 06, 12, 19, 21, 25) and `render-png.sh --check` printed `same` for all six; it takes figure numbers, defaults to those six, and the `--check` mode is the Y4a step 2 comparison. `.gitignore` already held `node_modules/` and `*.pdf`; `presentation/qa/` and `presentation/*.pdf` were added. `build-notes.md` records the helper delta as a table of what changed per line, without quoting the dashes, so the voice gate needs no exclusion for it.

## Acceptance criteria

1. `presentation/design-patterns-with-python-101-patterns-and-solid.pptx` is committed and builds from `npm ci && node deck-101.js` with the committed lockfile; `package.json` pins `pptxgenjs` at exactly `4.0.1`; `npm audit` reports 0 vulnerabilities.
2. Nothing installed globally; `require.resolve('pptxgenjs')` points under `presentation/node_modules`.
3. Slide count 62 (or the Corrections count after a witnessed cut), equal to the notes-slide count; every notes slide meets its floor (90 words content, 45 cover and dividers).
4. Every content slide's claim traces to a chapter sentence or a test in the census; every cited test is defined once; no slide without a witness.
5. Every code slide is read from source by path and range with its anchor asserted; no code is typed into the builder.
6. Shipping-domain names only; each slide draws on one chapter's definitions (decision 11).
7. Every figure in the deck passes the arrow census; the committed PNGs equal a fresh render.
8. No em or en dash, `PDP-`, `rNN`, "spike", "capstone", chapter or slide number reference, or cross-language word in slide text or notes (`check_decks`), and the ban-tier scan is clean on the builder and the extracted text.
9. `docProps` creator, lastModifiedBy and company are "PatternCatalyst"; every part passes `host_ids.py filter` unchanged; no runtime name in any part; `host_ids.py check` clean on the tree.
10. `pdffonts` shows Overpass, Red Hat Text and Red Hat Mono embedded; every rendered page viewed by the executor and by one of the two validator passes, with findings closed.
11. Sources credited on the two reference slides and in the notes of each slide that uses one; no copied text beyond the chapters' own attributed quotes.
12. Decision 10's fixes merged with their chapters' tests green; rows 348 and 349 closed.
13. README "Companion decks" section and licence line; `LICENSE-docs.md` unchanged.
14. `scripts/verify.sh`, `scripts/validate.py` (with `--self-test` and `--claims`) and the repo-wide voice gate green; CI `ci-ok` green.
15. Rows 313 to 356 closed; no soffice or node process left running; scratch trees deleted.

## Risks

- **Figure legibility.** Every figure was drawn for a page; at slide size sub-lines are small even at full width (figure 25 about 7 pt). Mitigation: full-width figure slides, QA drop rule, no redraw.
- **Name collisions.** Readers can confuse two chapters' `HandlingEvent` or `CarrierGatewayProxy`. Mitigation: one chapter per slide; notes name the concept.
- **Notes trap.** A notes count can't fail (evidence J). Mitigation: `check_decks` reads text and word counts.
- **Metadata leak.** The helper's defaults carry the owner's name. Mitigation: builder override and the runtime-name check.
- **Non-deterministic rebuilds.** Timestamps change every build. Mitigation: commit only the final build; revert a no-change rebuild.
- **Prose-only slides.** Chapters 1, 2 and 4 and the when-not table rest on sentences, not tests. Mitigation: quoted with line numbers in the census; no claim beyond the sentence.
- **Line lengths.** Some ranges run to 93 characters. Mitigation: per-call font size from the longest line, asserted in the builder.
- **Source drift.** Y1d edits and later chapters' edits can move ranges. Mitigation: anchor assertion fails the build.
- **Length.** 62 slides takes longer to view and voice. Mitigation: two validator halves; decision 9's alternative if the owner prefers.
- **Scope of Y1d.** Chapter fixes widen the iteration. Mitigation: each fix is a small edit with the chapter's tests and `validate.py` re-run, kept out of the deck's critical path.
