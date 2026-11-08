---
title: "r23 plan: Deck 201 (Idiomatic Python)"
order: 23
output: false
render_with_liquid: false
---

# r23: Deck 201, Idiomatic Python

Opus-planned 2026-11-07. Branch `release/r23`, cut from main at 3ad24b8 (the r22 merge, tagged `r22.x`). This file is the source of truth for r23 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

Work item: PDP-151 ("Deck 201", r23, `todo` in `_plans/iteration-plan.md`). The arc it plans against is "The three-deck arc" in `_plans/r22-plan.md`: 201 takes chapters 7 to 10, 26 to 32, 37 and 38, with concurrency as a closing section. PDP-152 (Deck 301, r24) follows; r25 is the retro and QA sweep.

The deck is built with the r22 scaffold in `presentation/` (pptxgenjs 4.0.1, the vendored helper, `render-png.sh`, `notes.py`) and voiced with lgtm-professional-voice. Every slide's content comes from a shipped chapter and its tested example. The book's text, code and figures are the only material. Nothing is written for the deck that the book doesn't already say and test.

Pins this iteration (re-checked 2026-11-07, evidence D): pptxgenjs 4.0.1 (npm `dist-tags.latest`; `beta` is 4.0.1-beta.2, a pre-release), image-size 2.1.0 (override only), cairosvg 2.9.1 (PyPI latest), Node v22.22.2 and npm 10.9.7 (host tools). The Python pins are unchanged from r22 (CPython 3.15.2, uv 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4); Z0 re-checks all of them before any edit.

Lessons carried from r16 to r22: grep everywhere, including front matter, cards, READMEs, docstrings, captions and the appendices; the run wins over the plan; recount after every edit; status tokens are plain `done`; paths in plans and evidence are repo-relative, with `<repo>` and `<scratchpad>` for anything outside; only suffixed step ids are cited as `run:` tokens. From r22's Y5 repairs: positional pointers in notes were the commonest failure, so a positional-pointer grep runs before validation (QA step 8); figure frames come from the PNG's own aspect; a fixed sentence is grepped across every recurrence before the fix is called done.

## Settled rules (owner, carried from r22; not re-asked)

- **Standalone deck** (r22 O4, extended 2026-11-07). No slide text or note points to a chapter, an appendix or "the book's" text, by number, title or phrase. Nothing points to another slide by number or position ("follows", "next", "earlier", "later", "close the section", "before it"). Each slide states the idea itself. Only the closing slide gives the book's site and repository. The evidence files still map each slide to its chapter sentence and tests.
- **Toolchain and storage as r22**: project-local pptxgenjs 4.0.1 with the committed lockfile; the deck committed as `presentation/design-patterns-with-python-201-idiomatic-python.pptx`; PatternCatalyst for creator, lastModifiedBy and company; a README "Companion decks" entry; figures as PNGs rendered from the committed SVGs, admitting only figures whose every arrow is composed by code; code read byte-exact from source with an asserted anchor; one chapter's definitions per slide; notes of at least 90 words on content slides and 45 on the cover and dividers, with dividers keeping the `AB0000` fill; credits on a "Sources credited" slide and in the notes; `check_decks()` applies unchanged.
- **Voice**: titles are 2 to 5 word noun phrases; bullets open with a bold subject noun; notes follow "what the slide shows", then "What to show:", then the fallback; British spelling and contractions; no em or en dashes; no rule of three, no meta-narration, no unproven scope words; none of the case-sensitive words Java, C#, C++, .NET, Rust or Go, so no sentence starts with "Go"; shipping-domain names only; no internal codes.
- **Process**: a defect found in the book is fixed in this iteration (Z1c), with every recurrence grepped.

## Owner decisions

2026-11-07, at the plan gate:

- O1: 45 slides in 8 sections, as planned (decisions 0 to 4 and 6 to 10 as recommended). Figures 07, 09, 10, 31 and 37. A shared `deck-lib.js`, with the identity proof for Deck 101. No toolchain slide.
- O2: decision 5 as recommended. Fix P1 to P14, F1 to F9 and B1 to B3 in this iteration. For P1, narrow the manifest "all or none" sentences, in chapter 10 and in the `manifest.py` docstring, to what the tests prove. For P12, add the chapter 37 lost-update probe to the example's `bench/`, so that the two chapter 37 sentences have a witness.

## User decisions

0. **Step ids.** The steps are Z0 to Z6. At planning, `grep -nE '^\| Z[0-9]' _plans/*.md` and `grep -n 'run: Z' _plans/*.md _plans/evidence/*.md` print nothing (evidence P); the only `Z9` in the repo is a synthetic self-test string in `scripts/validate.py`. Only suffixed ids are cited as `run:` tokens: `Z1a`, `Z1b`, `Z1c`, `Z4a`, `Z4b`. Plain Z0, Z2, Z3, Z5 and Z6 appear only in this plan's table. Two recorded files are cited as `run:` paths: `_plans/evidence/r23-deck-witness-census.md` (Z1b) and `_plans/evidence/r23-deck-qa.md` (Z4a).

   **Recommend: yes.**

1. **Length and shape: 45 slides in eight sections** (inventory below). Cover, route, eight dividers, 5 figure slides, 22 code slides, 4 bullet slides, 3 table slides, and the closing slide. Thirteen chapters come to 32 content slides, two or three a chapter. Decorators, descriptors and dispatch, the PRD's headline subjects for this deck, get the most. The reasons for the count:
   - A first cut of three slides a chapter came to 53. Eight slides were folded into the notes of a neighbour from the same chapter, keeping their witnesses: ordering, entity, Protocol at the point of use, class decorators, lookup precedence, handlers that hide bugs, accessors, and queue shutdown.
   - Eight sections keep each divider to two or three chapters on one theme.
   - The siblings' 201 decks and the arc's estimate sit at about 45.

   **Recommend: 45.** Alternative: 53, restoring the eight folded slides as their own code or bullet slides (their witnesses and ranges are already in evidence J to L).

2. **The boundary with Deck 101** (section "Boundary with Deck 101"). Deck 101 names Null Object, Value Object, "Interface", Resource acquisition, Metaclass registry, If-chain dispatch and Proxy as attribute interception only as one-line table rows, and it already uses an EAFP race test, a dict-dispatch totality test and three class-counting tests from chapters 31 and 32 (evidence M). 201 teaches those patterns, and no 201 slide reuses a 101 test as its headline witness, a 101 code range, or a 101 claim. The boundary section lists each near-repeat and the angle 201 takes instead.

   **Recommend: yes.**

3. **Sharing code with `deck-101.js`.** Factor the builder helpers out of `deck-101.js` (lines 27 to 164: `words`, `notes`, `S`, `divider`, `runsFor`, `bullets`, `bulletSlide`, `tableSlide`, `codeSlide`, `figSlide`, plus the floor check and the write) into a new `presentation/deck-lib.js` exporting `createDeck(pres)`. Both builders require it. `deck-helpers.js` stays byte-for-byte as vendored in r22 (md5 47af3889bef56eba4736bb1565e17054). Evidence F and G give the reasons:
   - The spike moved the helpers into a module and rebuilt Deck 101 from it. Every XML part, rels file and media file came out identical to the committed deck except `docProps/core.xml` (timestamps). The unmodified r22 builder gives the same result, so Deck 101 is reproducible today and stays so.
   - Re-vendoring the fixed upstream helper (md5 ce44b9de9820ba7e115d729c5de9e63a, plus the same eight em-dash rewordings, giving d816b5e4dd0555d4ff31bac21b21ae64) changes the picture XML of all six of Deck 101's figure slides. The geometry is identical, but the fill changes from `srcRect` plus a bare `stretch` to `stretch/fillRect`.
   - The upstream fix adds nothing a builder needs, because `figSlide` already fits the frame to the PNG's aspect (r22 repair 1) and passes the fitted box.
   - Copying the helpers into `deck-201.js` would leave two copies to drift. r22's repair round 2 changed `codeSlide` and the divider sizes, and a copy would have missed that.

   Z1a does the refactor and records the proof. `node deck-101.js` from the refactored builder gives a deck whose unzipped parts equal the committed deck's, `docProps/core.xml` aside. The committed 101 `.pptx` is not rebuilt or recommitted. `build-notes.md` records the module and its proof.

   **Recommend: factor into `deck-lib.js`; keep the vendored helper unchanged.** Alternatives: re-vendor the upstream helper and recommit Deck 101 with six changed figure parts (visually the same); or copy the helpers into `deck-201.js`.

4. **Figures.** Five figures go in, each on its own full-width slide: 07, 09, 10, 31 and 37 (evidence H, I).
   - 10 passes the arrow census now. 07, 09, 31 and 37 become eligible after their Z1c spec fixes, and Z1b re-runs the census after Z1c.
   - Out on legibility, whatever their arrows: 26, 27, 28, 29, 30 and 32. These tall figures (viewBox height 760 to 1060) render their smallest labels at 3.7 to 5.6 pt in the 12.09 by 4.95 in box. Deck 101's smallest accepted figure (25) was 6.3 pt.
   - Out on the census: 08 (six fan-in arrows to "Value Object force" are conceptual, and the chapter's prose describes them) and 38 (a catalogue figure whose one edge is inheritance).
   - The legibility floor is 6.3 pt at the full-width box, computed from the viewBox and the smallest `font-size`.
   - `render-png.sh`'s default list grows from 101's eleven figures to sixteen, so `--check` covers both decks.
   - A figure QA can't read at full width is dropped, with the reason in the QA record.

   **Recommend: yes.** Alternative: leave 37 out rather than drop its two conceptual summary-bar edges (decision 5, F9). The deck then has four figures and 44 slides.

5. **Book defects found while planning** (evidence O). Each is fixed at Z1c, before the deck quotes the chapter, with the chapter's tests and `validate.py` green after each edit and every recurrence grepped (front matter, `_examples/` card, example README, docstrings, captions, `_data/diagrams.yml`, `_docs/41` to `46`). Figures are fixed in `diagrams/specs/` and regenerated, never hand-edited; each changed figure's paragraph, include caption and registry caption are brought into line, and its PNG re-rendered if the deck uses it.

   Prose, docstrings and code:
   - P1: `10.md:147` ("committed together or not at all") and the `write_manifests` docstring (`manifest.py:96`, quoted at `10.md:133`, "Write every manifest or none"). The tests witness only a failed open. On success the writers commit one at a time as the stack unwinds, and no test covers a commit-time failure. **Recommend narrowing both sentences** to what the tests show (a failed open discards the partials of every writer entered). Alternative: add a test with a failing `replace`, then restate the guarantee from its result.
   - P2: `09.md:93` "assigns the same class to a `CarrierGateway` variable". The mypy snippet defines its own `NullGateway` (`test_static.py:300-311`). Fix: "a class of the same shape".
   - P3: `examples/08-dataclasses-and-value-semantics/README.md:83` "a dict lookup raises". The test builds a dict literal (`test_aliasing.py:67`), as `08.md:73` says.
   - P4: the `Weight` message "kilograms must be positive" is also raised for `inf` and `nan` (`08 values.py:23`, fence `08.md:53`, `09 domain.py:26`). Fix the message to name both conditions, as chapters 0 and 7 do ("finite and positive"), together with the matching `match=` strings (`08 test_values.py:39`, `test_aliasing.py:56`, `09 test_domain.py:9`). Slide 6's range includes `values.py:23`, so Z1b re-checks the range after Z1c.
   - P5: `07.md:81` describes `_FieldHashDimensions` as `Dimensions` "with the `__hash__` removed"; the fixture also lacks `__post_init__` (`test_equality.py:36-53`). Reword.
   - P6: `26.md:336` "half unused: member mypy exits 1" has a dropped word. Reword with "the member's mypy run".
   - P7: quoted error messages wider than the tests. `26.md:155` quotes "cannot use 'tuple' as a dict key (unhashable type: 'list')" and `test_factories.py:75` matches "unhashable type". `27.md:57` quotes "property 'payload_kg' of 'Container' object has no setter" and `test_fields.py:134` matches "has no setter". Fix by tightening each `match=` to the quoted message (`re.escape`), so the quote is tested.
   - P8: cards. `_examples/27-*.md:29` "a slot that accepts a negative weight", where the slotted field is a length (`27 test_static.py:84-87`). `_examples/28-*.md:44` reads as two dispatch arguments, while `surcharges.py:39-40` dispatches on one. Reword both.
   - P9: docs links that redirect (301) to `builtins/`. `07.md:282` (`library/constants.html`), `22.md:327` (`library/exceptions.html`), `30.md:261` and `31.md:106` (`library/functions.html`), `31.md:100` and `31.md:216` (`library/stdtypes.html`). r11 recorded the house rule ("Chapters cite the `builtins/` URLs"); these six were missed.
   - P10: What's New links. Chapters 9, 15, 18 and 38 use `docs.python.org/3/whatsnew/3.15.html`, and chapter 10 uses `docs.python.org/3.15/whatsnew/3.15.html`. Both return 200, but the `/3/` form moves to 3.16's page when 3.16 ships. Normalise every What's New 3.15 link to the `/3.15/` form.
   - P11: `37.md:253-254` and `examples/37-*/README.md:67-68`, `examples/38-*/README.md:68-69` say `uv python install 3.15t` and `--python 3.15t`, where CI (`ci.yml:60,62`) and Appendix A (`41.md:33`) pin `3.15.2t`. Use the exact pin.
   - P12: `37.md:24` ("In one example run, 300 trials ...") and `37.md:52` ("A run on 3.15.2 reads 0.005") rest on a probe that is not in the example (`_plans/evidence/r18-gil-benchmark.md:108`), so a reader can't re-run them. **Recommend adding the probe** as `examples/37-the-gil-and-performance/bench/lost_update_probe.py`, with its output recorded beside it and scrubbed, run on both builds as the r18 record was, and the two sentences reworded to name it. Alternative: reword both sentences as a recorded measurement, with no re-run path.
   - P13: `37.md:250` and the chapter 37 card run `bench/gil_bench.py` without `--cpu-class`, which prints "machine: unspecified" (`gil_bench.py:102`), while the recorded runs used `--cpu-class "16-thread x86-64 CPU"`. Add the flag to the instruction.
   - P14: `31.md:170` runs `mypy --strict src tests` ("8 source files", `31.md:187`), where the chapter 31 card and `examples/31-*/README.md` run `mypy --strict src tests bench`. `scripts/verify.sh:23` checks `src tests`. Align the card and README to the gate.

   Figure specs:
   - F1, 07: the second box names `Decimal.__mul__(factor, price)`, and the dashed "NotImplemented again" branch from `Money.__rmul__` can't happen for a `Decimal` factor (`money.py:29` accepts `Decimal | int`). It happens for a float (`test_arithmetic.py:23-24`). Make the second box `type(factor).__mul__(factor, price)` and label the dashed edge for a float factor. Then fix `07.md:26-28` and `_data/diagrams.yml:72` ("only when both decline").
   - F2, 09: the dashed "swapped in" edge to `_NullGateway (test fixture)` draws a swap no code makes; the test assigns the fixture directly (`test_absence.py:37`). Drop the edge, leave the fixture node unconnected, and fix `09.md:28`.
   - F3, 10: the label `__exit__(type, exc, tb)` should be `__exit__(exc_type, exc, traceback)`, the code's parameter names (`manifest.py:63-65`). Fix the spec and `10.md:28`.
   - F4, 26: "render_bill, the function both stacks wrap". Only the timer-outside stack wraps `render_bill` (`test_wraps.py:91-92`); the stacking test wraps a test-local `render` (`test_factories.py:142-147`). Relabel.
   - F5, 28: the amber chain `InstantCoffee` to `Coffee` to `object` continues past a registered class, where `test_tariff.py:47-48` shows dispatch stopping at `InstantCoffee`. Label the chain "next in the MRO when unregistered", or start the dispatch arrow at an unregistered class.
   - F6, 29: the figure walks `FastlineGateway` through `__set_name__` and class decorators it doesn't have (`fastline.py:6-8`). Name the top box "a class statement", or mark the two steps as running only when present.
   - F7, 31: the look-first edge leaves `DutyRateCache.rate_for`, which has no look-first path. The comparison form is `_LookFirstDutyRateCache.rate_for` (`tests/conftest.py:26-34`), so give that edge its own source node with that name.
   - F8, 32: the factory arrow enters `_RateEngine.quote`, while the factory is called in `_RateEngine.__init__` (`tests/conftest.py:93`). Retitle the target box `_RateEngine`.
   - F9, 37: the two edges into the summary bar are conceptual. This is an eligibility edit, not a defect. Drop the two edges and keep the bar as an unconnected note, as r22 did for figure 16. Fix `37.md:28`.

   Repo bookkeeping (Z0):
   - B1: `_plans/iteration-plan.md` still lists 31 rows `todo` for r01 and r02 and 48 rows `active` for r03 to r09, though every iteration to r22 is tagged (evidence R). Z0 sets each row of a tagged iteration to `done`, except the two `n.a.` rows and the `covered by` row, with a dated note.
   - B2: `presentation/render-png.sh` defaults to Deck 101's eleven figures. Z1a extends the default list to sixteen.
   - B3: `presentation/build-notes.md` names only `deck-101.js`. Z1a adds `deck-lib.js` and `deck-201.js`.

   Checked, not a defect:
   - The non-contiguous listings `30.md:73-81` and `38.md:63-76`, `38.md:115-128`. As in r22, the chapters may join ranges, and the deck uses only contiguous sub-ranges.
   - The chapter 32 words "compile-time" (inside a quoted article), "interface" and "container". These are not language names; the deck words them differently (boundary section).

   **Recommend: fix all of P1 to P14, F1 to F9 and B1 to B3 at Z0, Z1a and Z1c as stated, taking the recommended option in P1 and P12.**

6. **Code on slides.** As r22 decision 11:
   - Each code slide names a file and a 1-based range. The builder asserts the first line against a recorded anchor and sizes the font from the longest line. The longest here is 95 characters (`rating.py:49-57`), which sets about 14 pt.
   - Only ranges the chapter quotes as a contiguous run of one fence are used, and the census confirms each byte-exact. Six ranges (`manifest.py:61-74`, `rendering.py:28-37`, `rendering.py:42-50`, `fields.py:29-38`, `tracking.py:75-84`, `carriers.py:44-52` of chapter 29) are contiguous runs inside a longer fence; the census records the fence's lines.
   - No 101 code range is reused.
   - Where two chapters define a name differently (evidence N), each slide draws on one chapter only, and the notes name the concept. Examples: the carton's dimensions and the container's extents; the reference-sharing carrier base and the registering carrier base; the threaded stowage plan.

   **Recommend: yes.**

7. **Measured numbers.** No timing appears in slide text. Notes may quote two recorded measurements, each with its label, and say that no test asserts a time:
   - the ratio sentence at `31.md:149` (labelled Python 3.15.2, best of 5 repeats of 1,000,000 calls, 2026-11-06);
   - the warm ratios at `37.md:197` (labelled Python 3.15.2, default and free-threading builds, workers 4, best of 3, 16-thread x86-64 CPU, 2026-11-06).

   The chapter 37 lost-update counts are quoted only after P12 lands; otherwise they stay out. The free-threaded build appears as the chapter presents it: tested on both builds in CI, measured, and not promoted.

   **Recommend: yes.**

8. **Credits.** As r22 decision 13: a "Sources credited" table of the online sources the 201 chapters cite, as they word them, and a "Reading further" table of the books they cite (evidence S). Each source is also named in the notes of the slide that uses it. Nothing is copied beyond the chapters' own attributed short quotes.

   **Recommend: yes.**

9. **No toolchain slide.** Deck 101 has one. A second would repeat it, and the standalone rule is met by the closing slide's run instructions, which name the pinned CPython, uv, pytest and mypy versions in its notes. There's no QR slide, as in r22 (no decoder on the host).

   **Recommend: yes.** Alternative: a toolchain table slide as in 101, giving 46 slides.

10. **README and site.** The README "Companion decks" list gains the 201 entry (slide count and the rebuild pointer, as 101's). There's no site page and no `_config.yml` change (`presentation/` is already excluded). The deck's README line, the cover and the closing slide's "two further decks" bullet name 201's theme, "what the language gives you so you don't write the pattern". The 101 deck's closing bullet already names it by theme, so 101 needs no change.

    **Recommend: yes.**

## Planning evidence

All trials ran in scratch copies under `<scratchpad>/plan23`. There was a local `npm ci` there only. Nothing was installed in the repo or globally, nothing on the host changed, and the scratch tree was deleted before the plan commit. Three read-only survey agents covered the chapters (J, K, L); their line numbers, anchors and test names came from commands they ran, and the planner re-read each defect at the cited lines.

A. **Repo state.** `release/r23` was cut from main at 3ad24b8; `git tag --points-at HEAD` prints `r22.x`; the tree was clean at the start. `_plans/iteration-plan.md` still says "r22 (active)" and PDP-150 `active`; Z0 closes r22. Reconciliation rows run to 356 (`verified (r22)`), so r23 starts at 357. README has "Companion decks" with the 101 entry; `LICENSE-docs.md` line 7 already covers the slide decks under `presentation/`.

B. **Intent.** PRD §8d: 201 is "Idiomatic Python: the data model, decorators, descriptors, `singledispatch`, `Protocol`. The 'what Python gives you so you don't write the pattern' deck". §12a deck lessons: 1 to 2 line bullets with the detail in notes; notes parity at the PPTX level; per-call font size; non-deterministic rebuilds. §13: free threading is not promoted, but "we need to discuss how the GIL impacts performance and asynchronous code". The PRD's build log records r22's O4 rule and the helper stretch fixed upstream.

C. **r22 lessons.**
   - Y5 round 1 failed on O4 positional pointers, stretched figures and a missed Appendix E recurrence. Round 2 failed on three positional divider notes.
   - `check_decks()` keys dividers on the `AB0000` fill.
   - The cross-language check matches `\bGo\b` case-sensitively and `Java` with no word boundary, so "JavaScript" would trip it.
   - `deck_owner_names()` drops the organisation name.
   - The notes extractor drops the slide-number field.
   - Slide 2's "The deck's route" became "The route", because the longer form is meta-narration.

D. **Pins.**
   - `npm view pptxgenjs dist-tags`: `latest 4.0.1`, `beta 4.0.1-beta.2`.
   - `npm view image-size version`: 2.1.0.
   - `npm audit` in the scratch copy after `npm ci`: 0 vulnerabilities (18 packages added).
   - PyPI cairosvg 2.9.1.
   - Node v22.22.2, npm 10.9.7.
   - `require.resolve('pptxgenjs')` in the scratch copy resolves under its own `presentation/node_modules`.

E. **Helper delta.** The upstream helper changed since r22 in one place (lgtm-skills ea323fd, "addDiagramSlide fits the PNG's own aspect"). It adds `const fs = require("fs")` and replaces the `contain` call with an aspect fit read from the PNG's IHDR. The upstream file still carries the eight em-dash lines the r22 delta rewords.

F. **Spike: re-vendor.** Build A used the vendored helper; build B used upstream plus the eight rewordings (md5 d816b5e4dd0555d4ff31bac21b21ae64, `grep -c` for the dash gives 0). Comparing the unzipped decks, the differences are `docProps/core.xml` and `ppt/slides/slide{16,21,26,38,44,53}.xml`. In each of those six, `<a:off>` and `<a:ext>` are equal; the picture's `blipFill` changes from `<a:srcRect l="0" r="0" t="0" b="0"/><a:stretch/>` to `<a:stretch><a:fillRect/></a:stretch>`, and the rest of the part is equal.

G. **Spike: shared module.** Deck 101's helper region (lines 27 to 164) moved into `deck-lib.js` as `createDeck(pres)` (161 lines), and the cover's `pageNum += 1` became a `bump()` call. `node --check` passes on both files, and `node deck-101.js` printed `slides: 62 min notes words: 50`. `diff -rq` against the unzipped committed deck reports only `docProps/core.xml`. The unmodified r22 builder gives the same one-file difference, so the committed 101 deck is reproducible from source.

H. **Legibility** (smallest SVG `font-size` scaled into the 12.09 by 4.95 in box; 101's accepted figures shown for reference).

| Fig | viewBox | Smallest label, pt | Note |
| --- | --- | --- | --- |
| 05, 06 (101) | 820x560 | 7.0 | accepted in 101 |
| 25 (101) | 1250x620 | 6.3 | smallest accepted in 101 |
| 07 | 820x560 | 7.0 | |
| 08 | 1140x560 | 7.3 | |
| 09 | 890x430 | 9.1 | |
| 10 | 820x600 | 6.8 | |
| 26 | 1000x980 | 4.2 | below floor |
| 27 | 1000x760 | 5.2 | below floor |
| 28 | 1000x780 | 5.0 | below floor |
| 29 | 1000x1060 | 3.7 | below floor |
| 30 | 1000x1000 | 3.9 | below floor |
| 31 | 1220x480 | 8.2 | |
| 32 | 1080x860 | 4.8 | below floor |
| 37 | 860x560 | 7.3 | |
| 38 | 980x640 | 6.4 | |

I. **Figure census** (arrow by arrow, from the specs and the code; Z1b re-runs it after Z1c). Every in-scope registry caption equals its include caption with the "Figure N.1: " prefix removed, and each has 20 to 45 words.

| Fig | Every arrow composed by code? | Deck |
| --- | --- | --- |
| 07 | Arrows to the reflected method and its return are interpreter dispatch, witnessed by `test_arithmetic.py:18` and composed by `money.py:33-34`. The dashed decline can't happen for the `Decimal` the box names | F1, then in |
| 08 | Six fan-out arrows composed by the decorator (`values.py:52`); six fan-in arrows to "Value Object force" are conceptual and the prose (`08.md:28`) describes them | out |
| 09 | `book_with` to the three lanes composed (`carriers.py:47-63`); dashed "swapped in" not composed | F2, then in |
| 10 | Yes: `manifest.py:54-74`, with the `with` line at `test_static.py:42` | in (F3 is a label fix) |
| 26 | `functools.wraps` to `inspect.signature` and `ParamSpec` to mypy are conceptual; the decorator-stack arrow is reading order | out (also legibility; F4 fixes a label) |
| 27 | Lookup-order chain, tested but not composed | out (also legibility) |
| 28 | MRO chain drawn past a registered class | out on legibility; F5 fixes the defect |
| 29 | Class-creation order, tested at `test_registry.py:211`, not composed | out (also legibility; F6) |
| 30 | E3 to E8 composed (`tracking.py:75-84`); E0 to E2 are interpreter calls into the hook | out on legibility |
| 31 | Four dispatch arrows composed (`documents.py:51-62`); the look-first edge has no source path in `src` | F7, then in |
| 32 | The factory arrow enters `quote`, but the call is in `__init__` | out on legibility; F8 |
| 37 | Lock and no-lock lanes composed (`test_stowage.py:31,49`, `stowage.py:30,40`); outcome arrows witnessed by asserts; two edges into the summary bar conceptual | F9, then in |
| 38 | One dashed inheritance edge; catalogue figure | out |

J. **Survey, chapters 7 to 10** (agent s1).
   - All four chapters are `hands-on` in `scripts/chapters.toml`, with one AI sidebar each.
   - Runs: 07 has 22 functions and 25 passed; 08 has 23 and 32 passed; 09 has 27 and 40 passed; 10 has 16 and 25 passed.
   - Every cited witness is defined once, except three names defined twice that the deck must not cite: `test_weight_must_be_positive_and_finite`, `test_money_addition_needs_one_currency` (chapters 8 and 9) and `test_money_refuses_to_order_across_currencies` (chapters 7 and 11).
   - Buckets: Value Object dissolves (`08.md:38`), Null Object dissolves (`09.md:62`), "Interface" needs disambiguating (`09.md:162`), Resource acquisition survives (`10.md:36`). Chapter 7 has no bucket; its when-not section is at `07.md:171`.
   - Phrases a slide must not carry: `10.md:32` "the label this book uses" and `07.md:284` "the book this chapter leans on".

K. **Survey, chapters 26 to 30** (agent s2).
   - Runs: 26 has 33 functions and 40 passed; 27 has 29 and 43 passed; 28 has 18 and 33 passed; 29 has 24 and 35 passed; 30 has 26 and 40 passed. All 130 test names are defined once.
   - Buckets: 26 survives (`26.md:22`); 27 survives, with `cached_property` disambiguating Proxy (`27.md:22`); 28 dissolves for an open set (`28.md:22`); 29 dissolves (`29.md:22`); 30 is interception with no surrogate (`30.md:22`).
   - The non-overlap rules 20/26 and 20/30 hold.
   - Phrases a slide must not carry: `27.md:195` "Nothing in this member shares a consignment" ("member" is the workspace term) and `30.md:157` (both sentences: the forwarding-proxy typo, which Deck 101 shows).

L. **Survey, chapters 31, 32, 37 and 38** (agent s3).
   - Runs: 31 has 30 functions and 42 passed; 32 has 16 and 20 passed; 37 has 11 and 15 passed; 38 has 26 and 28 passed. The chapters state the same counts.
   - Buckets: if-chain dispatch dissolves (`31.md:36`); 38's bucket table is at `38.md:48-55`. Chapters 32 and 37 have no bucket.
   - Benchmarks: `37.md:148-192` is byte-identical to `bench/gil_bench.out.txt` and `bench/gil_bench.ft.out.txt` and to `_plans/evidence/r18-gil-benchmark.md`. `31.md:149` matches `_plans/evidence/eafp-lookup-cost.md`, whose output prints only the version (no build, no machine class).
   - CI runs examples 37 and 38 on `3.15.2t` (`ci.yml:51-64`), and `ci-ok` needs that job.
   - No language name appears in the four chapters.

M. **Overlap with Deck 101** (grep of `presentation/deck-101.js` for every in-scope example path and test name).
   - No code range from examples 7 to 10 or 26 to 38 is in Deck 101.
   - Test names Deck 101 uses:
     - `test_every_document_kind_has_an_issuer` (notes, js:275);
     - `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read` (EAFP row, js:371);
     - `test_the_fuel_surcharge_lives_in_one_definition_of_the_function`, `test_the_engine_needs_more_classes_functions_and_lines_than_the_function` and `test_one_engine_quote_makes_more_python_calls_than_the_function` (js:366-368).
   - Rows and claims Deck 101 makes (js lines):
     - `X | None` (270), frozen dataclass (271), `__init_subclass__` (272), dict of callables (273);
     - singledispatch for an open set, match for a closed set (269);
     - the with statement (292);
     - `__getattr__`, property and `cached_property` (300), Protocol against ABC (301);
     - a Protocol matching by shape (250);
     - the forwarding-proxy typo (494);
     - the `@` form rebinding once, with stacking order fixed at definition (484-488);
     - a frozendict registry of callables, `RATE_RULES` (390).
   - Deck 101 titles to avoid reusing: "Proxy as stand-in", "Builder as a dataclass", "Snapshot and rollback", "Generators as iterators".

N. **Name collisions inside Deck 201's sources.**
   - `Dimensions`: chapter 7, `int` extents, order-insensitive equality; chapter 27, `Decimal`, `Positive` fields.
   - `CarrierBase`: chapter 9 shares `reference()`; chapter 29 registers by class keyword; chapter 3's forwards `**kwargs`.
   - `StowagePlan`: an entity in 8, threaded in 37, async in 38.
   - `TrackingHistory`: chapter 7 against chapter 30.
   - `Manifest`: chapter 10 against chapter 26.
   - `Money` and `Weight`: differ across 7, 8, 9, 28, 32, 37 and 38.
   - `quote`: chapter 32 takes a tariff; 37 is CPU-bound; 38 is async.
   - "registry": a mutable dict in 26, `tariff_code.registry` in 28, a `MappingProxyType` in 29. "Read-only" is true only of 28 and 29.
   - `Consignment`: chapter 0's (the 101 listing) against 8 and 9.
   - `BookingRequest`: chapter 8 against chapter 17 (the 101 listing, same decorator line).

O. **Defects** (decision 5). Located by the surveys and re-read by the planner at the cited lines:
   - figure 07 against `money.py:20-34` and `test_arithmetic.py:15-24`;
   - `manifest.py:93-104` and `10.md:147`;
   - `09.md:93`;
   - `examples/08-*/README.md:83`;
   - card 27 line 29 and card 28 line 44;
   - `26.md:336`;
   - the six old docs URLs (each returns 301 to `builtins/`);
   - the `3.15t` lines;
   - `37.md:24` and `:52`;
   - the figure 31 and 37 spec edges (`31` spec lines 84-89, `37` spec lines 69-74).

P. **Step letter.** `grep -nE '^\| Z[0-9]' _plans/*.md` and `grep -n 'run: Z' _plans/*.md _plans/evidence/*.md` print nothing.

Q. **URLs.** The site `https://patterncatalyst.github.io/design-patterns-with-python/` and the repository `https://github.com/patterncatalyst/design-patterns-with-python` return 200. Both What's New 3.15 URL forms return 200 (P10).

R. **Registry.** `_plans/iteration-plan.md` status counts: 67 `done`, 49 `active`, 33 `todo`, 2 `n.a.`, 1 `covered by`. Of the `active` rows, 48 are r03 to r09 and one is PDP-150. Of the `todo` rows, 31 are r01 and r02, and two are PDP-151 and 152. Tags `r01.x` to `r22.x` all exist.

S. **Books and sources the 201 chapters cite** (from the surveys; Z1b confirms each against `bibliography.html` and the chapter that cites it).
   - Books:
     - *Fluent Python*, second edition (Ramalho, 2022);
     - *Effective Python*, third edition (Slatkin, 2024);
     - *Patterns of Enterprise Application Architecture* (Fowler, 2002);
     - *Domain-Driven Design* (Evans, 2003);
     - *Pattern Languages of Program Design 3* (Woolf's "Null Object", 1998);
     - *Pattern-Oriented Software Architecture*, Volume 2 (Schmidt, Stal, Rohnert, Buschmann, 2000; Monitor Object, Active Object) and Volume 3 (Kircher, Jain, 2004);
     - *Design Patterns* (Gamma, Helm, Johnson, Vlissides, 1994).
   - Online:
     - the Python Language Reference (data model, `with`, compound statements);
     - the library documentation (`functools`, `contextlib`, `inspect`, `dataclasses`, `typing`, `abc`, `enum`, `copy`, built-ins, `concurrent.futures`, `threading`, `asyncio`, `queue`, `sys`);
     - the Descriptor Guide and the free-threading how-to;
     - PEPs 207, 252, 318, 343, 443, 487, 520, 544, 557, 562, 612, 661, 686, 695, 698, 703, 749, 779, 810, 814, 3115 and 3129, each with the authors as the chapter words them;
     - the mypy documentation and the typing spec;
     - ruff rules B019 and RUF006;
     - Martin Fowler's "Inversion of Control Containers and the Dependency Injection pattern";
     - Mark Seemann's "Service Locator is an Anti-Pattern";
     - Brandon Rhodes's "The Global Object Pattern", "The Decorator Pattern" and "The Factory Method Pattern";
     - Bobby Woolf's Null Object entry, as cited.
   - The slide set credits only those its slides use; Z1b builds both tables from the census.

## Boundary with Deck 101

Each row is a 101 slide or table row that a 201 slide sits near, and the angle 201 takes so that no slide repeats it.

| Deck 101 has | Deck 201 teaches instead |
| --- | --- |
| "Null Object: X \| None checked by mypy" row | the branch mypy requires, and a null object that hides a lost booking (slides 9, 10) |
| "Value Object: A frozen dataclass" row; chapter 0's frozen consignment listing; `dataclasses.replace` on the Builder slide | `Weight` declared once (a different listing), frozen being a `__setattr__` guard and shallow, an amendment as a new value (slides 6, 7) |
| "Interface: Protocol vs ABC" row; "Narrow roles" (a Protocol per role) | checked at use against checked at construction, an explicit Protocol subclass, `runtime_checkable` checking names only (slide 11 notes) |
| "Resource acquisition: the with statement" row; the rollback context manager | commit or discard on each exit path, the generator form's `try`, swallowing narrowly (slides 12 to 14) |
| "A name rebound once", stacking fixed at definition | what `wraps` copies, a factory that refuses bare use, what each stacking order measures (slides 16 to 18) |
| "`__getattr__`, property and `cached_property`" row; the forwarding-proxy typo | one descriptor for many fields, the four costs of `cached_property`, lazy load by allow-list, the recursion trap; never the typo point or `30.md:157` (slides 20 to 23) |
| "singledispatch for an open set" row; "Visitor as a match" | the fallback as the design decision, registration from another module, what a union fallback lets mypy check; it doesn't lead with the match contrast (slides 25, 26) |
| "Metaclass registry: `__init_subclass__`" row | a class keyword that registers and refuses at definition, and a table of what a metaclass costs; chapter 3's forwarding `CarrierBase` is never shown or endorsed (slides 27, 28) |
| "If-chain dispatch: dict of callables, with EAFP" row; `RATE_RULES`; the EAFP race row and the issuer-totality test | only the lookup inside `try`, an issuer's own `KeyError` passing through, one read and one gap; the `ISSUERS` listing and the two 101 tests appear in no headline (slides 29, 30) |
| YAGNI, DRY and simple-design rows (class counts) | two forms passing one table, a Visitor that breaks on a new charge, a located dependency mypy can't see (slides 32 to 34) |

Deck wording for chapter 32: "an error mypy reports before the program runs" for "compile-time"; "a Protocol or ABC with one implementation" for "an interface with one implementation"; "pass the tariff as an argument" for "without a container". The Fowler article title is named only as a credit in the notes.

## Deck 201 slide inventory

Columns, as in r22: # (build order); section; title (2 to 5 word noun phrase); claim and its chapter sentence (`NN.md:line`); witness tests; code (file and lines, anchor in the census) or figure; what the notes cover. Code paths are under `examples/<chapter dir>/src/<package>/` unless they start with `tests/`. Z1b confirms every line, quote, anchor and test against the source after Z1c. Anything that differs is recorded in Corrections, and a claim that can't be witnessed is cut before the builder runs.

| # | Section | Title | Claim (source) | Witness | Code or figure | Notes cover |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Cover | Design Patterns with Python | 201: Idiomatic Python | - | cover panel | what the language gives so the pattern isn't written; the shipping domain; tested code |
| 2 | Cover | The route | the eight sections in order | - | bullets, two columns | the themes of the sections, by concept |
| 3 | The data model | divider | - | - | section panel | syntax as calls on the type; values declared, not hand-written |
| 4 | The data model | One hashing contract | 07.md:53 "equal values must hash alike"; 07.md:81 "A set test catches this and a reading of the class doesn't." | `test_a_turned_carton_is_one_set_element`, `test_defining_eq_alone_makes_a_class_unhashable`, `test_custom_eq_in_a_frozen_dataclass_keeps_a_field_hash`, `test_mypy_cannot_see_a_broken_hash_contract`, `test_special_methods_are_looked_up_on_the_type` | `data_model/cargo.py:32-41` (max 77) | 07.md:47 lookup on the type; the Data model reference credited; "the carton's dimensions" named to keep it apart from the container's |
| 5 | The data model | The reflected operand | 07.md:85 "`NotImplemented` isn't an exception."; 07.md:114 "`start=` says what the zero is" | `test_a_factor_times_money_uses_the_reflected_method`, `test_sum_needs_a_money_start` | figure 07 (after F1) | each box and arrow; the float path; ordering in one currency (07.md:131, `test_total_ordering_derives_the_other_comparisons`, `test_quotes_sort_by_total_but_not_by_themselves`); `NotImplemented` and `total_ordering` docs, PEP 207 |
| 6 | The data model | Value Object as declaration | 08.md:38 "This pattern dissolves." and "What remains is the part no decorator can supply."; force 08.md:34 | `test_equal_values_are_interchangeable`, `test_a_frozen_value_refuses_assignment`, `test_mypy_checks_the_generated_methods`, `test_slots_remove_dict_and_weakref_until_asked` | `value_semantics/values.py:15-23` (max 81; re-checked after P4) | Fowler's definition as 08.md:32 quotes it, Evans, PEP 557; entity against value (08.md:163, `test_stowage_plan_is_an_entity`, `test_mutable_default_is_refused_at_class_creation`) |
| 7 | The data model | Frozen, not sealed | 08.md:65 "Frozen guards attribute assignment; it doesn't seal the object."; 08.md:75; 08.md:81 "An amendment isn't an edit." | `test_frozen_is_a_setattr_guard_not_a_seal`, `test_frozen_is_shallow`, `test_a_mutable_dataclass_is_not_a_dict_key`, `test_a_mutable_consignment_aliased_between_bookings_changes_both`, `test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old`, `test_replace_runs_post_init`, `test_mypy_cannot_see_value_semantics_mistakes` | bullets | aliasing between bookings; validation without repair (08.md:157) |
| 8 | Contracts and cleanup | divider | - | - | section panel | absence in the type, shape at the point of use, release on every path |
| 9 | Contracts and cleanup | Absence in the type | 09.md:62 bucket; 09.md:79 "Use an explicit branch where the check must survive." | `test_find_gateway_returns_none_for_an_unknown_code`, `test_book_with_turns_absence_into_a_booking_error`, `test_mypy_requires_a_branch_for_absence` | `structural_typing/carriers.py:52-63` (max 79) | the force 09.md:60; Woolf's Null Object credited; the sentinel for "not given" (09.md:123, `test_a_sentinel_separates_not_given_from_none`, PEP 661) |
| 10 | Contracts and cleanup | A silent null object | 09.md:93 "A null object turns "no carrier" into a success that carries no information."; 09.md:95 | `test_a_null_gateway_hides_a_lost_booking`, `test_mypy_accepts_a_null_gateway`, `test_no_discount_is_a_null_object_that_loses_nothing` | `tests/test_absence.py:18-22` (max 80) | where doing nothing is right (the discount) and where it hides a loss |
| 11 | Contracts and cleanup | The carrier lookup | 09.md:162 bucket; 09.md:32 "The comparison happens where the value is used"; 09.md:191 | `test_mypy_checks_protocols_at_use_and_abcs_at_construction`, `test_abc_refuses_an_incomplete_subclass_at_construction`, `test_both_carriers_satisfy_the_protocol_one_by_inheritance`, `test_explicit_protocol_subclass_is_nominal_and_still_instantiable`, `test_runtime_checkable_checks_names_only` | figure 09 (after F2) | each lane; Protocol or ABC by who owns the need (09.md:195); PEP 544; "the reference-sharing carrier base" named |
| 12 | Contracts and cleanup | Exits from a block | 10.md:24 "The first failure is a leak and the second is a lie." | `test_without_with_an_exception_leaves_the_handle_open`, `test_writer_commits_only_on_success`, `test_writer_closes_and_discards_on_an_exception` | figure 10 (F3 label) | each arrow; PEP 343 and the Kircher and Jain credit |
| 13 | Contracts and cleanup | Commit or discard | 10.md:36 bucket survives; 10.md:74 "Returning nothing is the decision to let the failure be seen." | `test_writer_is_single_use`, `test_a_truthy_exit_swallows_the_exception`, `test_suppress_swallows_only_the_named_exception`, `test_mypy_reads_exit_return_type_for_reachability` | `context_managers/manifest.py:61-74` (max 64) | swallowing narrowly (10.md:151, 153); the `with` statement reference |
| 14 | Contracts and cleanup | Try in the generator form | 10.md:120 "That's why `try` isn't optional." and "The type checker has nothing to say, so a test that raises mid-write is the only guard." | `test_the_generator_form_needs_try`, `test_mypy_cannot_see_a_missing_try`, `test_exit_stack_unwinds_entered_writers_in_reverse_order` | `context_managers/manifest.py:77-90` (max 81) | `contextlib` credited; ExitStack order (10.md:145) stated within P1's narrowed wording; the 3.15 change to a decorated generator (`test_a_context_manager_decorating_a_generator_spans_iteration`, What's New 3.15) |
| 15 | Decorators done right | divider | - | - | section panel | the `@` syntax written well; the syntax kept apart from the Decorator pattern |
| 16 | Decorators done right | What wraps copies | 26.md:38 "`functools.wraps` makes the replacement look like the original."; 26.md:72 | `test_wraps_keeps_the_name_qualname_doc_and_module`, `test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring`, `test_inspect_signature_follows_wrapped_to_the_original_parameters`, `test_wrapped_points_one_level_down_and_unwrap_reaches_the_original`, `test_mypy_keeps_the_signature_through_a_wrapper_without_wraps` | `decorators_done_right/rendering.py:28-37` (max 60) | `wraps` for runtime tools, `ParamSpec` for mypy; `partial` when the decorator supplies an argument (26.md:78, two tests); PEP 612, functools docs |
| 17 | Decorators done right | Factories refusing bare use | 26.md:82 "The call runs at definition, and so does any mistake in it." | `test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator`, `test_a_keyword_only_factory_used_bare_fails_at_definition`, `test_mypy_refuses_a_keyword_only_factory_used_bare` | `decorators_done_right/rendering.py:42-50` (max 92) | PEP 695 type parameters; the keyword-only factory as the refusal |
| 18 | Decorators done right | Where the timer sits | 26.md:165 "The inside order measures the renderer. The outside order measures what the caller waited, hits included." | `test_stacking_order_decides_whether_a_cache_hit_is_timed`, `test_cached_for_renders_again_once_the_window_has_passed` | bullets | which dashboard wants which order; class decorators and methods (26.md:205, 209: `test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class`, `test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none`, `test_functools_cache_on_a_method_keeps_the_instance_alive`); ruff B019 |
| 19 | Attribute access | divider | - | - | section panel | the language owns attribute lookup; descriptors, properties and hooks |
| 20 | Attribute access | One validator, many fields | 27.md:75 force; 27.md:79 "A descriptor puts the rule in one place and lets any number of fields use it." | `test_every_field_form_validates_the_same_extents`, `test_a_copy_pasted_property_validator_drifts`, `test_one_descriptor_class_validates_every_field`, `test_set_name_gives_each_field_its_own_storage` | `descriptors_properties/fields.py:29-38` (max 81) | the Descriptor Guide, PEP 487; "the container's extents" named; the property pair as the when-not (27.md:201) |
| 21 | Attribute access | Costs of cached_property | 27.md:190 "The cache lives in the instance dictionary, and it has four costs."; 27.md:194 | `test_chargeable_weight_is_computed_on_first_access_and_stored`, `test_cached_property_needs_an_instance_dict`, `test_a_frozen_dataclass_cannot_clear_a_cached_property`, `test_a_cached_property_over_mutable_state_goes_stale`, `test_a_cached_property_getter_can_run_twice_under_threads` | `descriptors_properties/cargo.py:50-53` (22 pt) | lookup precedence (27.md:131, 135: `test_a_data_descriptor_takes_precedence_over_the_instance_dict`, `test_an_instance_dict_entry_takes_precedence_over_cached_property`); functools docs, What's New 3.12 |
| 22 | Attribute access | A self-loading history | 30.md:22 "That's interception with no surrogate, which is where Proxy is disambiguated" | `test_every_history_form_loads_once_for_every_field`, `test_nothing_is_loaded_until_a_field_is_read`, `test_a_loaded_history_reads_its_fields_from_the_instance_dict`, `test_getattr_runs_only_when_normal_lookup_fails` | `dynamic_attributes/tracking.py:75-84` (max 93) | Fowler's Lazy Load credited; the allow-list as the design (30.md:24, 124); "Did you mean" through `__dir__` (`test_a_misspelt_field_suggests_the_declared_name_through_dir`) |
| 23 | Attribute access | The recursion trap | 30.md:120 "`copy` builds such an instance." | `test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute`, `test_each_fix_keeps_getattr_out_of_recursion`, `test_copy_keeps_a_history_before_and_after_loading` | `tests/test_lookup.py:35-44` (max 94) | copy and pickle docs; `hasattr` is a read (30.md:149, `test_hasattr_loads_the_history`); special methods on the type (30.md:147, `test_implicit_special_method_lookup_bypasses_getattr`) |
| 24 | Dispatch and registries | divider | - | - | section panel | choosing behaviour by type, by class creation and by value |
| 25 | Dispatch and registries | Dispatch by registered type | 28.md:22 "For an open set of kinds like this one it dissolves into a single generic function"; 28.md:56 | `test_every_fallback_form_gives_registered_commodities_their_codes`, `test_the_most_specific_registration_wins`, `test_an_unregistered_subclass_gets_its_base_class_code`, `test_a_raising_fallback_names_an_unregistered_kind` | `singledispatch_visitor/tariff.py:17-31` (max 75) | the fallback as a design choice (28.md:66, 78, `test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently`); Design Patterns credited for Visitor |
| 26 | Dispatch and registries | Registration from another module | 28.md:121 "The design question is who imports the extension"; 28.md:103 "A union fallback is what closes the set." | `test_another_module_extends_the_set_when_it_is_imported`, `test_the_registry_is_read_only`, `test_mypy_refuses_a_kind_outside_a_union_fallback`, `test_mypy_checks_calls_and_registrations_against_the_fallback` | `singledispatch_visitor/dangerous_goods.py:8-14` (max 64) | PEP 443; start-up imports the extension; the price of an open set (28.md:103) |
| 27 | Dispatch and registries | Registration by class keyword | 29.md:22 "so the pattern dissolves"; 29.md:89 "The hook runs before the registry is touched" | `test_every_registry_form_books_through_the_registered_carrier`, `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry`, `test_the_carrier_registry_is_a_read_only_view`, `test_isabstract_sees_abstractness_inside_init_subclass`, `test_mypy_reports_a_misspelt_class_keyword` | `carrier_registry/carriers.py:44-52` (max 90) | PEP 487; imports decide the registry (29.md:99, `test_a_carrier_module_registers_only_when_it_is_imported`, Rhodes's Global Object page); "the registering carrier base" named |
| 28 | Dispatch and registries | Metaclass costs | 29.md:149 "What the metaclass costs shows in four places."; 29.md:151 (mypy docs quote); 29.md:155 | `test_a_second_metaclass_conflicts_with_the_bases_metaclass`, `test_a_metaclass_derived_from_abcmeta_resolves_the_conflict`, `test_mypy_does_not_check_metaclass_class_keywords`, `test_mypy_types_a_class_called_from_a_metaclass_registry_as_any`, `test_only_a_metaclass_gives_the_class_object_operators` | table: Cost, What the test shows (rows worded from 29.md:149-155, census) | the one case a metaclass pays (operators on the class); the enum docs quote (29.md:168); the when-not (29.md:174) |
| 29 | Dispatch and registries | A narrow try | 31.md:36 bucket; 31.md:87 "The `try` holds the lookup and nothing else." | `test_an_issuers_own_key_error_passes_through_issue`, `test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind`, `test_an_unsupported_kind_raises_unsupported_document_error` | `shortcut_patterns/documents.py:58-62` (22 pt) | totality mypy can't see (31.md:52, `test_mypy_accepts_a_table_that_misses_a_kind`); handlers that hide bugs (31.md:104, 108, `test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property`, `test_suppress_skips_the_rest_of_its_block_after_the_first_exception`); the glossary's EAFP and PEP 814 |
| 30 | Dispatch and registries | Dispatch tables and EAFP | 31.md:65 "A table wins when the set is data."; 31.md:147 "The scope of the guarantee is one gap." | `test_an_eafp_read_reloads_when_another_thread_evicts_first`, `test_two_eafp_readers_that_both_miss_both_load`, `test_every_cache_form_reads_loads_and_evicts_the_same_way` | figure 31 (after F7) | each arrow; the measured ratio as decision 7 labels it; "no test asserts a time" |
| 31 | Pattern misuse | divider | - | - | section panel | 32.md:22 when the forces leave and the structure stays |
| 32 | Pattern misuse | A quote as a function | 32.md:62 "The behaviour is identical, so what differs is the cost of the structure."; 32.md:22 | `test_every_rating_form_quotes_the_same_table`, `test_every_rating_form_refuses_an_unknown_zone` | `pattern_misuse/rating.py:49-57` (max 95) | the definition of an anti-pattern; accessors against fields (32.md:84, 109: `test_an_accessor_consignment_has_no_value_equality`, `test_a_setter_lets_a_quoted_consignment_change_its_quote`, `test_a_frozen_consignment_refuses_assignment`, PEP 8) |
| 33 | Pattern misuse | A misplaced Visitor | 32.md:78 "Declaring the method on the visitor base is the fix, and it moves the failure." and "A Visitor suits a fixed set of kinds that gains operations." | `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time`, `test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract`, `test_mypy_reports_a_visitor_missing_a_new_visit_method` | bullets | the cost of a new charge kind; Design Patterns credited |
| 34 | Pattern misuse | A located dependency | 32.md:129 "Passing the tariff as a parameter turns the unseen failure into the seen one." | `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`, `test_a_located_engine_quotes_once_its_tariff_is_registered`, `test_mypy_does_not_see_a_missing_registration`, `test_mypy_reports_a_missing_tariff_argument` | `tests/conftest.py:175-179` (max 78) | Fowler's article and Seemann's "Service Locator is an Anti-Pattern" credited; the boundary wording; 32.md:133 as the when-structure-pays line |
| 35 | Concurrency and the patterns | divider | - | - | section panel | what the GIL protects and doesn't; coroutines change the edges of the patterns |
| 36 | Concurrency and the patterns | Build and GIL state | 37.md:48 "Two functions are needed because the build and the running state can differ." | `test_the_build_flag_and_the_runtime_gil_state_agree`, `test_sys_version_names_the_free_threading_build_only_on_that_build`, `test_mypy_types_the_build_flag_as_any` | `gil_and_performance/build.py:11-19` (max 87) | PEP 703, PEP 779, the free-threading how-to; both builds tested; the free-threaded build not promoted |
| 37 | Concurrency and the patterns | Locks over read and write | 37.md:91 "because it never promised that the steps run together"; 37.md:93 "The fix is a lock that covers the read as well as the write." | `test_two_threads_parked_between_read_and_write_take_the_same_slot`, `test_a_lock_across_read_and_write_gives_each_thread_its_own_slot`, `test_an_attribute_increment_is_a_separate_load_add_and_store` | figure 37 (after F9) | each arrow; the Barrier seam; POSA2 Monitor Object and Scoped Locking; the lost-update counts only after P12 |
| 38 | Concurrency and the patterns | What a pool shares | 37.md:122 "What differs is what the workers can see."; 37.md:197 "Two loops on one build moved in opposite directions, so measure your loop." | `test_every_pool_rates_the_batch_as_the_serial_loop_does`, `test_threads_share_the_argument_and_processes_and_interpreters_copy_it`, `test_a_process_pool_cannot_send_a_lambda` | `gil_and_performance/pools.py:18-33` (16 lines, max 85) | `concurrent.futures`; the recorded ratios as decision 7 labels them |
| 39 | Concurrency and the patterns | A coroutine as a value | 38.md:25 "A quote that is assigned and never awaited doesn't fail where it was written."; 38.md:40 | `test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote`, `test_a_quote_that_is_never_awaited_warns_when_it_is_collected`, `test_mypy_reports_a_quote_returned_without_await`, `test_mypy_accepts_a_coroutine_bound_to_underscore` | bullets | the asyncio development guide, RUF006; an await as a switch point (38.md:44, `test_an_await_between_read_and_write_double_books_a_slot`, `test_an_asyncio_lock_gives_each_task_its_own_slot`), with "the async stowage plan" named |
| 40 | Concurrency and the patterns | Closing a feed early | 38.md:48-55 bucket table, Iterator row (census picks the line) | `test_breaking_out_of_async_for_leaves_the_feed_open`, `test_first_departure_closes_the_feed_when_it_stops_early`, `test_the_session_closes_the_feed_when_its_task_is_cancelled` | `asyncio_patterns/feed.py:54-60` (max 88) | `contextlib.aclosing`; who closes an async generator |
| 41 | Concurrency and the patterns | Task groups and subscribers | 38.md:166 "A task group is right for quotes, where one failure makes the rest worthless, and wrong for notifications" | `test_a_failing_subscriber_does_not_stop_the_others`, `test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails`, `test_a_failing_carrier_cancels_the_other_quote`, `test_the_first_answer_cancels_the_rest_of_the_group` | `asyncio_patterns/signal.py:25-31` (max 92) | What's New 3.15 `TaskGroup.cancel`; queue shutdown over a sentinel (38.md:189, `test_shutdown_lets_the_worker_drain_the_queue_then_stop`, POSA2 Active Object) |
| 42 | Reference | divider | - | - | section panel | sources, books, where the examples live |
| 43 | Reference | Sources credited | the online sources the slides use (evidence S) | census | table: Source, Used for | each, as the chapters word them |
| 44 | Reference | Reading further | the books the 201 chapters cite (evidence S) | census | table: Book, Authors, Year | what each adds |
| 45 | Reference | Site and repository | the site and repository URLs (evidence Q) | URLs return 200 at Z4a | bullets | how to run an example and the pinned versions; the other two decks by theme |

## Build setup

```
presentation/
  deck-helpers.js       # unchanged from r22 (md5 47af3889bef56eba4736bb1565e17054)
  deck-lib.js           # new: createDeck(pres) with S, divider, bullets, bulletSlide,
                        #   tableSlide, codeSlide, figSlide, notes, bump, finish
  deck-101.js           # refactored to require deck-lib.js; output proven unchanged
  deck-201.js           # new builder
  render-png.sh         # default list 05 06 07 09 10 12 13 14 16 19 21 22 23 25 31 37
  build-notes.md        # gains deck-lib.js, deck-201.js and the 101 identity proof
  png/                  # gains 07, 09, 10, 31 and 37
  design-patterns-with-python-101-patterns-and-solid.pptx   # not rebuilt
  design-patterns-with-python-201-idiomatic-python.pptx     # new
```

Build, from `<repo>/presentation`: `npm ci`; `./render-png.sh 07 09 10 31 37`; `node deck-201.js`. The builder sets the metadata: title "Design Patterns with Python: 201, Idiomatic Python", subject "Companion deck to Design Patterns with Python", author, company and lastModifiedBy "PatternCatalyst". It writes the cover in the 101 layout with the subtitle "201: Idiomatic Python", and every slide from the `deck-lib.js` helpers with notes as plain strings. `finish()` asserts the floors and the notes count. The `deck-lib.js` `divider()` keeps the `AB0000` background.

## QA pipeline (Z4a, Z4b, Z5)

1. `npm ci` in `presentation/`; `node -e "console.log(require.resolve('pptxgenjs'))"` shows the local copy (recorded scrubbed); `npm audit` 0.
2. `./render-png.sh --check` prints `same` for all sixteen PNGs.
3. `node deck-201.js` prints 45 slides. The Z1a identity proof is re-run: `node deck-101.js` into a temporary name, unzip, and `diff -rq` against the committed 101 deck shows only `docProps/core.xml`; the temporary build is deleted.
4. `soffice -env:UserInstallation=file://<scratchpad>/lo-qa --headless --convert-to pdf --outdir presentation/qa <deck>.pptx`. Afterwards `pgrep -f soffice` prints nothing.
5. `pdffonts`: Overpass, Red Hat Text and Red Hat Mono present and embedded; no other text family except OpenSymbol.
6. `pdftoppm -jpeg -r 110`: one image per slide, 45 in all.
7. `python3 presentation/notes.py <deck>` and `--slides` into `presentation/qa/deck-201-notes.txt` and `deck-201-slides.txt`.
8. **Positional and pointer grep, before validation.** A case-insensitive grep over both text files and the builder's strings for `follow`, `next`, `previous`, `earlier`, `later`, `before it`, `after it`, `above`, `below`, `closing slide`, `last slide`, `close the section`, `section that`, `the book`, `this book`, `book's`, `chapter`, `appendix`, `member` and `slide [0-9]`. Each hit is recorded in the QA file as allowed (a non-positional use, quoted) or fixed. Only the closing slide may name the site and repository. A case-sensitive grep for `Java|C#|C\+\+|\.NET|Rust|\bGo\b` follows.
9. `scan.sh --tier ban --fail` on `deck-201.js`, `deck-lib.js` and both text files, then `--stats` on the notes and the house-voice rubric applied by reading.
10. `uv run python scripts/validate.py` (runs `check_decks` over both decks), `--self-test`, `--claims`; `scripts/verify.sh`; `python3 scripts/host_ids.py check`.
11. `unzip -p <deck> docProps/core.xml docProps/app.xml` is shown in the QA record.
12. Eyeballing.
    - At Z4a the executor views every page image once and fixes what it sees.
    - At Z5 two Opus validators view the images independently, one per half: slides 1 to 23 and slides 24 to 45. They run as separate agents and neither sees the other's findings before reporting.
    - Checklist: logo and page number placed; no text overflow or clipped code; the code box fits the listing; the caption sits under the box on one line; figure text legible and the frame matching the PNG aspect (XML `a:ext` ratio against the PNG to three decimals); table cells not wrapping mid-word; divider titles on at most two lines; notes present and over the floor (from the text file); no pointer or positional phrase (from step 8).
    - Findings go to the QA record with the page number.
13. A rebuild changes only `docProps/core.xml`; the committed deck is the last build after Z5's final repair, and a no-change rebuild is reverted rather than committed.

## Evidence files

- `_plans/evidence/r23-deck-witness-census.md` (Z1b), after Z1c. Per slide it records:
  - the chapter's exact title and the cited sentence with `NN.md:line`, re-found by `grep -nF` hitting one line;
  - each test with file, line and a definition count of 1;
  - each code range with its anchor, its line count and longest line, and the fence it is a contiguous run of;
  - the table cells for slides 28, 43 and 44 with their `grep -F` result;
  - the credits per slide;
  - the figure census re-run after Z1c, with legibility;
  - one forward run and one reverse run of every witness test in a fresh scratch copy.
- `_plans/evidence/r23-deck-qa.md` (Z4a, appended at Z4b and Z5). It holds:
  - the pipeline commands and outputs (scrubbed with `host_ids.py filter`);
  - `pdffonts` and `docProps`;
  - the notes word-count table;
  - the step 8 grep results;
  - the scan results;
  - the eyeballing findings per page, with their fixes.

## Steps and status

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| Z0 | Bookkeeping with dated notes: `iteration-plan.md` closes r22 (PDP-150 `done`), marks PDP-151 and r23 `active`, and fixes the stale rows (B1); re-check every pin; record the owner's decisions; `verify.sh` and `validate.py` green | - | done |
| Z1a | `deck-lib.js` and the `deck-101.js` refactor with the identity proof (decision 3); `render-png.sh` default list (B2); `build-notes.md` (B3); the five new PNGs after Z1c's figure fixes | Z0, Z1c for the PNGs | done |
| Z1b | `_plans/evidence/r23-deck-witness-census.md`, after Z1c, so lines, anchors and the figure census are taken from the fixed tree | Z1c | done |
| Z1c | Decision 5's book fixes P1 to P14 and F1 to F9, each with its chapter's tests, `verify.sh` and `validate.py` green and every recurrence grepped; figures regenerated through `diagrams/specs` | Z0 | done |
| Z2 | Rows 357 to 391 into `_plans/reconciliation-plan.md` with a dated note; every quote, line or test that differs from this plan goes in Corrections; a failed witness cuts the slide | Z1b | done |
| Z3 | `deck-201.js` (Sonnet executor) from the inventory and the census, notes written to the settled voice rules, with no chapter, appendix, book or positional pointer | Z1a, Z2 | done |
| Z4a | Build and QA pipeline steps 1 to 12 (executor view of every page); `_plans/evidence/r23-deck-qa.md`; README "Companion decks" entry | Z3 | done |
| Z4b | Voice pass on `deck-201.js` and the extracted text: ban tier, `--stats`, the house-voice rubric, the step 8 grep; rebuild and re-run pipeline steps 3 to 10 | Z4a | done |
| Z5 | Opus validation: two independent page viewers (QA step 12); every witness row checked, at least one in three re-run; the excerpt check against each source; the claims audit (`validate.py --claims`); the boundary check against Deck 101 (section "Boundary with Deck 101"); rows 392 to 398 added and closed; up to two repair rounds, each followed by a full pipeline re-run | Z4b | done |
| Z6 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r23.x` on main; notes-only release | Z5 | todo |

## Reconciliation rows

Rows 357 to 391 go in at Z2, after the census exists (so its `run:` path resolves) and with only test names the census confirmed. Rows 392 to 398 cite `run: Z4a` and `run: Z4b` and go in at Z5, after those steps are `done`. The Ch cell is the source chapter's number, so `chapter_numbers` parses it. Rows whose claim begins "Deck:" start `open`, and Z5 closes them; fix rows close at Z1c.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 357 | 7 | Deck: equal values must hash alike, and a set test catches a broken hash | `test_a_turned_carton_is_one_set_element`, `test_defining_eq_alone_makes_a_class_unhashable` |
| 358 | 7 | Deck: the reflected operand answers when the left operand declines | `test_a_factor_times_money_uses_the_reflected_method`, `test_sum_needs_a_money_start` |
| 359 | 8 | Deck: Value Object dissolves into a frozen, slotted dataclass | `test_equal_values_are_interchangeable`, `test_a_frozen_value_refuses_assignment` |
| 360 | 8 | Deck: frozen is a setattr guard, shallow, and an amendment is a new value | `test_frozen_is_a_setattr_guard_not_a_seal`, `test_frozen_is_shallow`, `test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old` |
| 361 | 9 | Deck: absence in the type, with the branch mypy requires | `test_mypy_requires_a_branch_for_absence`, `test_book_with_turns_absence_into_a_booking_error` |
| 362 | 9 | Deck: a null object can hide a lost booking | `test_a_null_gateway_hides_a_lost_booking`, `test_no_discount_is_a_null_object_that_loses_nothing` |
| 363 | 9 | Deck: a Protocol is checked at use and an ABC at construction | `test_mypy_checks_protocols_at_use_and_abcs_at_construction`, `test_abc_refuses_an_incomplete_subclass_at_construction` |
| 364 | 10 | Deck: a writer commits on success and discards on an exception | `test_writer_commits_only_on_success`, `test_writer_closes_and_discards_on_an_exception` |
| 365 | 10 | Deck: a truthy exit swallows, and suppress names one exception | `test_a_truthy_exit_swallows_the_exception`, `test_suppress_swallows_only_the_named_exception` |
| 366 | 10 | Deck: the generator form needs try, and mypy can't see it missing | `test_the_generator_form_needs_try`, `test_mypy_cannot_see_a_missing_try` |
| 367 | 26 | Deck: wraps copies the metadata and signature tools follow it | `test_wraps_keeps_the_name_qualname_doc_and_module`, `test_inspect_signature_follows_wrapped_to_the_original_parameters` |
| 368 | 26 | Deck: a keyword-only factory refuses bare use at definition | `test_a_keyword_only_factory_used_bare_fails_at_definition`, `test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator` |
| 369 | 26 | Deck: stacking order decides whether a cache hit is timed | `test_stacking_order_decides_whether_a_cache_hit_is_timed` |
| 370 | 27 | Deck: one descriptor validates every field, where copied setters drift | `test_one_descriptor_class_validates_every_field`, `test_a_copy_pasted_property_validator_drifts` |
| 371 | 27 | Deck: the costs of cached_property | `test_cached_property_needs_an_instance_dict`, `test_a_cached_property_over_mutable_state_goes_stale` |
| 372 | 30 | Deck: a history loads once, on the first lazy read | `test_every_history_form_loads_once_for_every_field`, `test_nothing_is_loaded_until_a_field_is_read` |
| 373 | 30 | Deck: copy recurses through a careless getattr | `test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute`, `test_each_fix_keeps_getattr_out_of_recursion` |
| 374 | 28 | Deck: singledispatch per registered type, with the fallback as design | `test_the_most_specific_registration_wins`, `test_a_raising_fallback_names_an_unregistered_kind` |
| 375 | 28 | Deck: another module extends the set when imported | `test_another_module_extends_the_set_when_it_is_imported`, `test_mypy_refuses_a_kind_outside_a_union_fallback` |
| 376 | 29 | Deck: a class keyword registers and refuses at definition | `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry`, `test_mypy_reports_a_misspelt_class_keyword` |
| 377 | 29 | Deck: what a metaclass costs | `test_a_second_metaclass_conflicts_with_the_bases_metaclass`, `test_mypy_does_not_check_metaclass_class_keywords`, `test_only_a_metaclass_gives_the_class_object_operators` |
| 378 | 31 | Deck: the try holds only the lookup | `test_an_issuers_own_key_error_passes_through_issue`, `test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind` |
| 379 | 31 | Deck: EAFP's guarantee covers one gap | `test_an_eafp_read_reloads_when_another_thread_evicts_first`, `test_two_eafp_readers_that_both_miss_both_load` |
| 380 | 32 | Deck: two rating forms quote one table | `test_every_rating_form_quotes_the_same_table`, `test_every_rating_form_refuses_an_unknown_zone` |
| 381 | 32 | Deck: a Visitor breaks on a new charge kind | `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time`, `test_mypy_reports_a_visitor_missing_a_new_visit_method` |
| 382 | 32 | Deck: a located dependency fails at first use, unseen by mypy | `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered`, `test_mypy_does_not_see_a_missing_registration` |
| 383 | 37 | Deck: the build flag and the runtime GIL state | `test_the_build_flag_and_the_runtime_gil_state_agree`, `test_mypy_types_the_build_flag_as_any` |
| 384 | 37 | Deck: a lock over read and write gives each thread its own slot | `test_two_threads_parked_between_read_and_write_take_the_same_slot`, `test_a_lock_across_read_and_write_gives_each_thread_its_own_slot` |
| 385 | 37 | Deck: threads share the argument, processes and interpreters copy it | `test_threads_share_the_argument_and_processes_and_interpreters_copy_it`, `test_a_process_pool_cannot_send_a_lambda` |
| 386 | 38 | Deck: an unawaited coroutine is a value, warned at collection | `test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote`, `test_a_quote_that_is_never_awaited_warns_when_it_is_collected` |
| 387 | 38 | Deck: stopping early closes the feed | `test_first_departure_closes_the_feed_when_it_stops_early`, `test_breaking_out_of_async_for_leaves_the_feed_open` |
| 388 | 38 | Deck: a task group for quotes, isolation for subscribers | `test_a_failing_subscriber_does_not_stop_the_others`, `test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails` |
| 389 | 7-38 | Deck: the metaclass-cost, sources and books tables match the chapters | run: _plans/evidence/r23-deck-witness-census.md |
| 390 | 7-37 | Chapter fixes P1 to P14: the manifest contract, the null-gateway sentence, the dict-key line, the weight message, the fixture sentence, the mypy sentence, the quoted messages under test, the cards, the docs and What's New links, the free-threaded pin, the probe, the bench flag, the mypy command | run: Z1c |
| 391 | 7-37 | Figure fixes F1 to F9 regenerated from their specs, and figures 07, 09, 10, 31 and 37 pass the arrow census | run: Z1c |
| 392 | 7-38 | Deck: every code slide is byte-exact with its source range | run: Z4a |
| 393 | 7-38 | Deck: 45 slides, 45 notes slides, every notes slide over its floor | run: Z4a |
| 394 | 7-38 | Deck: Red Hat Text, Red Hat Mono and Overpass embedded in the render | run: _plans/evidence/r23-deck-qa.md |
| 395 | 7-38 | Deck: metadata PatternCatalyst, no host identifier or runtime name in any part | run: Z4a |
| 396 | 7-38 | Deck: ban-tier scan and the pointer grep clean on the builder, slide text and notes | run: Z4b |
| 397 | 7-38 | Deck: committed figure PNGs equal a fresh render, and Deck 101 rebuilds unchanged from the shared module | run: _plans/evidence/r23-deck-qa.md |
| 398 | 7-38 | Deck: every rendered page viewed and passed by two independent viewers | run: _plans/evidence/r23-deck-qa.md |

## Acceptance criteria

1. `presentation/design-patterns-with-python-201-idiomatic-python.pptx` is committed and builds with `npm ci && node deck-201.js` from the committed lockfile. `package.json` is unchanged (pptxgenjs exactly 4.0.1) and `npm audit` reports 0.
2. Nothing is installed globally, and `require.resolve('pptxgenjs')` points under `presentation/node_modules`.
3. `deck-helpers.js` is unchanged (md5 47af3889bef56eba4736bb1565e17054). Both builders require `deck-lib.js`. A fresh `node deck-101.js` gives a deck whose unzipped parts equal the committed 101 deck's except `docProps/core.xml`, and the committed 101 `.pptx` is unchanged in the diff.
4. There are 45 slides (or the Corrections count after a witnessed cut), equal to the notes-slide count. Every notes slide meets its floor (90 words content, 45 cover and dividers), and every divider keeps the `AB0000` fill.
5. Every content slide's claim traces to a chapter sentence or a test in the census. Every cited test is defined once, and no slide is without a witness. No 201 slide reuses a 101 code range, a 101 headline test or a 101 claim (boundary section).
6. Every code slide is read from source by path and range with its anchor asserted, from a contiguous run of a chapter fence. Each slide draws on one chapter's definitions.
7. Every figure in the deck passes the arrow census and the 6.3 pt legibility floor, its frame matches the PNG aspect, and the committed PNGs equal a fresh render.
8. Slide text and notes contain:
   - no em or en dash, `PDP-`, `rNN`, "spike", "capstone" or cross-language word;
   - no chapter, appendix, book or slide pointer, and no positional phrase (`check_decks` and the QA step 8 grep);
   - no timing in slide text, and measured numbers in notes only with their labels.

   The ban-tier scan is clean on both builders, `deck-lib.js` and the extracted text.
9. `docProps` creator, lastModifiedBy and company are "PatternCatalyst"; every part passes `host_ids.py filter` unchanged; no runtime name appears in any part; `host_ids.py check` is clean on the tree.
10. `pdffonts` shows Overpass, Red Hat Text and Red Hat Mono embedded. Every rendered page has been viewed by the executor and by one of two independent Opus viewers, with findings closed.
11. Sources are credited on the two reference slides and in the notes of each slide that uses one. No text is copied beyond the chapters' own attributed quotes.
12. Decision 5's fixes are merged with their chapters' tests green and every recurrence fixed; rows 390 and 391 are closed; `iteration-plan.md` carries no stale status.
13. README "Companion decks" lists 201; `LICENSE-docs.md` is unchanged.
14. `scripts/verify.sh`, `scripts/validate.py` (with `--self-test` and `--claims`) and the repo-wide voice gate are green; CI `ci-ok` is green, including the free-threaded job.
15. Rows 357 to 398 are closed; no soffice or node process is left running; scratch trees are deleted.

## Risks

- **Repeating Deck 101.** The 201 subjects sit beside 101's table rows. Mitigation: the boundary table, the Z5 boundary check, and no 101 test as a headline.
- **Deck 101 drift from the refactor.** Moving the helpers could change 101's output. Mitigation: the identity proof at Z1a and again at QA step 3; the committed 101 file is never rebuilt into the commit.
- **Positional pointers in notes.** These were r22's commonest repair. Mitigation: settled rule in the executor brief, the QA step 8 grep before validation, and two independent viewers.
- **Name collisions inside 201.** Examples: `Dimensions` (slides 4 and 20), `CarrierBase` (slides 11 and 27), `StowagePlan`. Mitigation: one chapter per slide; the notes name the concept that tells them apart.
- **Fixes moving ranges.** P4 edits a line inside slide 6's range; F-fixes rewrite figure paragraphs. Mitigation: Z1b runs after Z1c, and anchors fail the build loudly.
- **Measurements read as guarantees.** Benchmark ratios and the lost-update probe. Mitigation: decision 7 labels, no timing on slides, P12 before any probe number is used.
- **Free threading oversold.** The PRD keeps it unpromoted. Mitigation: slides state what the tests show on both builds and what was measured; the notes recommend nothing beyond 37.md:205.
- **Figure legibility.** Five figures, smallest 6.8 pt. Mitigation: full-width slides, the QA drop rule, no redraw.
- **Scope of Z1c.** Fourteen prose fixes and nine figure fixes across thirteen chapters plus chapter 22. Mitigation: each is a small edit with its chapter's tests and `validate.py` re-run, off the deck's critical path except P4, F1, F2, F3, F7 and F9.
- **Line lengths.** Ranges run to 95 characters. Mitigation: per-call font size from the longest line.

## Corrections after the build
- Step Z5 round 2: FAIL on B1 (a wrong section count and positional naming in Deck 101 notes 2, introduced in round 1), B2 (Deck 201 notes 33 cited an alternative the example never shows) and B3 (vacuous pointer self-tests). Repair round 2, the second and last, applied the validator's tested text; see `_plans/evidence/r23-deck-qa.md`, "Repair round 2". Acceptance criterion 3's "the committed 101 .pptx is unchanged" no longer holds as written. Deck 101 changed under the fix-now rule in notes 2, 4, 13, 21, 26, 38, 53 and 57, its slide text is unchanged, and it still rebuilds identically from `deck-lib.js` apart from timestamps. Rows 357 to 389 are verified, and rows 392 to 398 are added and verified.
- Step Z5 round 1: FAIL on seven pointer notes. The orchestrator applied repair round 1 with the validator's exact strings, plus should-fix items 1 to 7 and the nits; see `_plans/evidence/r23-deck-qa.md`, "Repair round 1". This corrects the earlier orchestrator note: the sign-only setter is at test_fields.py line 122, not 121, and only now keeps "must be positive". Deck 101 notes 2, 13 and 57 were changed by the new `check_decks()` rules, and Deck 101 was rebuilt.
- Orchestrator, after Z1b: under the fix-now rule, the P4 treatment is applied to chapter 27. `Positive.__set__` (`fields.py:37`), the three property setters in `conftest.py`, the `27.md` fences at lines 70 and 104, and the quoted messages at 27.md lines 111 and 160 now say "must be positive and finite". All of these validators reject NaN and infinity. Two `match=` strings were updated: test_fields.py:76 and test_dataclasses.py:57. The test-local setter at test_fields.py:121 checks only the sign, so it keeps "must be positive". Chapter 27's 43 tests pass, `validate.py` reports 0 errors and `verify.sh` passes. The slide 20 range and anchor are unchanged.
- Step Z1a (part 1): `deck-lib.js` exports `{ createDeck, ROOT }`. `createDeck(pres)` returns `{ S, divider, bullets, bulletSlide, tableSlide, codeSlide, figSlide, notes, words, bump, finish }`. The slide counter and the notes floors live in the closure. `finish(out)` asserts the floors and writes the deck. The helper region was lines 27 to 165, not 27 to 164. Identity proof: rebuilt and committed Deck 101 each have 342 parts, and only the `docProps/core.xml` timestamps differ. `render-png.sh` has the per-deck lists `figs_101` and `figs_201`, plus `--deck`. A bare `--check` covers all sixteen figures and passes only once the 201 PNGs are committed. `deck-helpers.js` is unchanged (md5 47af...). Commit 1033893.
- Step Z1c: P1 to P14 and F1 to F9 are applied (e074ef7).
  - P4 also fixed the same message in the chapter 11 example, which the plan didn't list.
  - P7 made the tests match the full quoted messages, so the quoted lines in chapter 26's experiment two moved from 121/123 to 123/125. They were re-run.
  - P12 added `bench/lost_update_probe.py` with recorded outputs: 0 of 300 trials lost an update on the default build and 300 of 300 on the free-threaded build. The chapter 37 sentences now cite it, and the chapter was trimmed to stay under 2,500 words.
  - The P9 and P10 link changes moved the `source:` URLs in reconciliation rows 170, 177, 178 and 225.
  - Nine figures were regenerated: 07, 09, 10, 26, 28, 29, 31, 32 and 37.
  - The orchestrator re-ran the gates at e074ef7 in the real repo: `verify.sh` passes, `validate.py` reports 0 errors and `site-build.sh` passes.
- Step Z1a (part 2): `render-png.sh --deck 201` rendered figures 07, 09, 10, 31 and 37 into `presentation/png/`, and `./render-png.sh --check` prints `same` for all sixteen figures. Z1a is done.
- Step Z1b: `_plans/evidence/r23-deck-witness-census.md` is written. All 147 witness and notes-witness names are defined once, and the four runs (three forward, one reverse) each report 215 passed on 2026-11-07. No slide is cut. Differences from this plan:
  - Slide 6: the range `values.py:15-23` is unchanged, but its longest line is now 92 characters (plan: 81), after P4.
  - Slide 7: `test_money_validates_and_of_normalises` is added as a notes witness for 08.md validation without repair.
  - Slide 16: the two `partial` tests are `test_a_decorator_that_supplies_an_argument_reports_the_original_parameters` and `test_partial_reports_the_parameters_that_remain`.
  - Slide 22: the claim is reworded, because "where Proxy is disambiguated" uses the book's bucket vocabulary.
  - Slide 27: the range is widened from 44-52 to 44-58, so the slide shows the registration (a contiguous run of the chapter's fence, block lines 18 to 32).
  - Slide 28: `test_mypy_refuses_self_in_a_metaclass_new` is added, because the chapter's "four places" include the `Self` limit; the table has four cost rows and one row for what a metaclass buys.
  - Slide 40: the claim is the Iterator row at 38.md:50.
  - Figure 09: the smallest label is 9.5 pt, not 9.1. All five figures pass the arrow census and the 6.3 pt floor (6.8 to 9.5 pt).
  - Deck 101's `js:NNN` references in the boundary section are stale since the Z1a refactor. The conclusion holds, with two near repeats (slides 30 and 32) that need the notes to lead with the EAFP read and the shared table.
  - The census lists 19 standalone-wording items for the executor brief, mostly the bucket vocabulary and internal codes.
  - Observation for the validation step: `Positive.__set__` in chapter 27 (`fields.py:37`) raises "must be positive" for non-finite values, the pattern P4 fixed for `Weight`. The tests match `must be positive`, so it is tested as written; it is not changed here.
- Step Z2: rows 357 to 391 are added to `_plans/reconciliation-plan.md` with a dated note. Rows that begin "Deck:" start `open`; rows 390 and 391 (the Z1c fixes) are `verified (r23)`. Row 377 gains the `Self` test, and row 389 cites the census path. `validate.py --claims` reports 0 errors; every new token resolves.

- Step Z3: `presentation/deck-201.js` builds 45 slides and 45 notes slides from the census, through `deck-lib.js` unchanged. Deviations from the inventory: the Sources credited slide carries ten theme rows (the PEPs are one row, authors named in the notes of the slides that use them); slide 41's caption describes the `gather` form the listing shows, with the task group in the notes; slide 30's notes lead with the EAFP read and slide 32's with the shared table and the zone refusal. Slide titles, ranges and anchors are as the census has them.
- Step Z4a: `_plans/evidence/r23-deck-qa.md` records the pipeline, counts, fonts, docProps, the pointer grep, the scan and `--stats` tables, and all 45 pages viewed. Minimum notes words: cover 89, dividers 69, content 103. The pipeline found no layout defect. Text fixes were made for scope words and pointer phrases the grep caught, and one ban-tier word. The README "Companion decks" list now has the 201 entry. Deck 101 rebuilds identically apart from `docProps/core.xml`.
- Step Z4b: voice pass on `deck-201.js`: 45 sentence-level changes, recorded before and after in the Voice pass section of `_plans/evidence/r23-deck-qa.md`. They fix three accuracy slips (the class-keyword listing has three refusals, not four; the located-engine listing is five lines, not four; the pool slide has no pool table to show), a positional title ("The route" is now "Eight themes"), meta-narration, flourishes, philosophy-teacher sentences and stiff forms. Stats: notes contractions 26/33 to 34/35, slides 7/11 to 9/12. Rebuilt, 45 slides, notes floors met, pages 2, 17, 23 and 43 viewed; pointer grep, ban scan, `validate.py`, `--claims` and `host_ids.py` clean.

Step Z0: `iteration-plan.md` closes r22 (PDP-150 `done`), marks PDP-151 and r23 `active`, and sets the 80 stale rows to `done` (B1): the 31 `todo` rows for r01 and r02 (PDP-001, 003 to 020, 100a to 104c less the three exceptions below), PDP-105a to PDP-120c (48 `active` rows for r03 to r09), and PDP-150 (the 49th `active` row). PDP-101a and PDP-104a keep `n.a. (argument chapter)` and PDP-102a keeps `covered by PDP-103a`. A dated 2026-11-07 (r23) note is appended. Pins re-checked 2026-11-07 against upstream and unchanged: pptxgenjs 4.0.1 (`dist-tags.latest`; `beta` 4.0.1-beta.2 not used), image-size 2.1.0, cairosvg 2.9.1, CPython 3.15.2 (endoflife.date and python.org cycle 3.15), uv 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4. No pin row changed, so `r01-build-plan.md` is untouched.

