---
title: "r24 plan: Deck 301 (Testing, legacy code and AI)"
order: 24
output: false
render_with_liquid: false
---

# r24: Deck 301, Testing, legacy code and AI

Opus-planned 2026-11-07. Branch `release/r24`, cut from main at 6c27a6f (the r23 merge, tagged `r23.x`). This file is the source of truth for r24 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

Work item: PDP-152 ("Deck 301", r24, `todo` in `_plans/iteration-plan.md`). The arc it plans against is "The three-deck arc" in `_plans/r22-plan.md`: 301 takes the testing chapter (11), Part 11 (33 to 36), Part 13 (39, 40) and Appendices B, C and D, about 40 slides, with the boundary rules for the composition root (301 owns the final project's), AI (301 owns working with AI tools and the gates on their output) and anti-patterns (301 refers to them by concept only). It is the last of the three companion decks; r25 is the retro and QA sweep.

The deck is built with the r22 scaffold and the r23 shared module in `presentation/` (pptxgenjs 4.0.1, the vendored helper, `deck-lib.js`, `render-png.sh`, `notes.py`) and voiced with lgtm-professional-voice. Every slide's content comes from a shipped chapter or appendix and its tested example. The book's text, code and figures are the only material. Nothing is written for the deck that the book doesn't already say and test.

Pins this iteration (re-checked 2026-11-07, evidence D): pptxgenjs 4.0.1 (npm `dist-tags.latest`; `beta` is 4.0.1-beta.2, a pre-release), image-size 2.1.0 (override only), cairosvg 2.9.1 (PyPI latest), Node v22.22.2 and npm 10.9.7 (host tools). Python pins unchanged: CPython 3.15.2 (endoflife.date cycle 3.15), uv 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4, each the PyPI latest. D0 re-checks all of them before any edit.

Lessons carried from r16 to r23: grep everywhere, including front matter, cards, READMEs, docstrings, captions and the appendices; the run wins over the plan; recount after every edit; status tokens are plain `done`; paths in plans and evidence are repo-relative, with `<repo>` and `<scratchpad>` for anything outside; only suffixed step ids are cited as `run:` tokens. From r22 and r23 validation: positional and book pointers in notes were the commonest blocking finding in both decks, so the pointer grep runs before validation (QA step 8); two of r23's round-2 findings were slips introduced by the orchestrator's own repair 1 (a wrong section count; self-tests that could not fail), so every orchestrator-applied repair is followed by an independent confirmation pass (QA step 14); r23's confirmation pass is recorded only in the PRD build log, not in the repo (K2), so this plan names where each validation round is recorded.

## Settled rules (owner, carried from r22 and r23; not re-asked)

- **The deck stands alone.** No slide text or note points to:
  - a chapter or an appendix, by number, title or phrase;
  - "the book's" text, or "this book" (only the closing slide may give the site and the repository);
  - another slide, by number or by position: "follows", "next", "earlier", "later", "above", "below", "before it", "close the section", "the dividers", "where they're used";
  - another example by its title ("the descriptor example").

  Also: no "this deck" or "these slides"; no three-way-split labels ("dissolves", "survives", "disambiguates", in any inflection); no internal codes; a claim names its witness test. The evidence files still map each slide to its chapter sentence and tests.
- **Build and layout.** The shared `deck-lib.js`; Decks 101 and 201 must still rebuild identically apart from `docProps/core.xml` timestamps. Project-local pptxgenjs 4.0.1 with the committed lockfile. The stable name `presentation/design-patterns-with-python-301-testing-legacy-and-ai.pptx` (r22 decision 2). Metadata PatternCatalyst for creator, lastModifiedBy and company. A README "Companion decks" entry. Figures are PNGs rendered from the committed SVGs, admitted only if code composes every arrow they draw and their smallest label is at least 6.3 pt at full width. Code slides are byte-exact, anchor-asserted, and each range is a contiguous run of one chapter fence. One chapter's definitions per slide. Notes floors: 90 words on content slides, 45 on the cover and dividers; dividers keep the `AB0000` fill. Credits on "Sources credited" and "Reading further" and in the notes of the slide that uses each source.
- **Voice.** Titles are 2 to 5 word noun phrases. Bullets open with a bold subject noun. Notes say what the slide shows, then "What to show:", then the fallback. British spelling and contractions; no em or en dashes; no rule of three, no meta-narration, no unproven scope words; none of the case-sensitive words Java, C#, C++, .NET, Rust or Go (so no sentence starts with "Go", and "JavaScript" is out). The PRD's "Java-in-Python" is worded with the book's own terms (decision 8). Shipping-domain names only.
- **No overlap.** No test name, code range or claim repeats one in Deck 101 or Deck 201 (section "Boundary with Decks 101 and 201").
- **Fix now.** A book defect found in this iteration is fixed in it (D1c), with every recurrence grepped.

## Owner decisions

2026-11-07, at the plan gate:

- O1: 42 slides as planned. Decisions 0 to 4 and 6 to 11 are taken as recommended, with figures 33 and 40 after F1 and F2, and no toolchain slide.
- O2, which **differs from the recommendation for P5**: narrow the six "teardown runs when the test fails" sentences so each cites only what the chapter 11 experiment shows. Add no pytester witness, and leave chapter 11's counts unchanged. Every other defect in decision 5 (P1 to P4, P6 to P21, F1, F2, K1 to K3 and V1) is fixed as recommended.
- O3: the AI sidebar wording ("An assistant may ...") stays as approved at r10b. The r25 retro decides between rewording the sidebars and amending CLAUDE.md. The deck carries none of those sentences.

## Decisions with recommendations

0. **Step ids.** The steps are D0 to D6. At planning, `grep -nE '^\| D[0-9]' _plans/*.md` and `grep -n 'run: D' _plans/*.md _plans/evidence/*.md` print nothing (evidence P). Only suffixed ids are cited as `run:` tokens: `D1a`, `D1b`, `D1c`, `D4a`, `D4b`. Plain D0, D2, D3, D5 and D6 appear only in this plan's table. Two recorded files are cited as `run:` paths: `_plans/evidence/r24-deck-witness-census.md` (D1b) and `_plans/evidence/r24-deck-qa.md` (D4a).

   Defect ids in this plan are P1 to P21 (prose, docstrings, tests, cards, links), F1 and F2 (figures), K1 to K3 (bookkeeping) and V1 (validator). They are labels, never `run:` tokens. The r23 plan used B1 to B3 twice, once for bookkeeping and once for round-2 blocking items; neither set is a step id and none is cited here. Validation findings in this iteration are named "blocking item N of round M", never with a letter-digit id.

   **Recommend: yes.**

1. **Length and shape: 42 slides in eight sections** (inventory below): cover, themes, eight dividers, 18 code slides, 2 figure slides, 5 table slides (three content, two reference), 7 bullet slides including the closing slide. Ten source docs give 29 content slides. The reasons for the count:
   - The arc estimated about 40. Three slides a chapter for the seven chapters and four for the three appendices together is 25; the legacy chapters 33 and 34 get a fourth each because they carry the deck's headline subject ("easy seams", PRD §8d), giving 27; the final project and AI chapters get four each, giving 29.
   - Eight sections keep each divider to one chapter or one tightly related pair, and give the testing material, the legacy track and the AI throughline their own dividers.
   - A first cut at 47 folded five slides into the notes of a neighbour from the same doc, keeping their witnesses: the plain mock that passes a misspelt assertion, the `side_effect` timeout branch, `resetall` leaving stubs, the techniques Python makes unnecessary, and the decision rule for refactor or rewrite.

   **Recommend: 42.** Alternative: 38, folding slides 17 (seams mypy checks) and 22 (a misspelt override) into their neighbours' notes.

2. **The boundary with Decks 101 and 201** (section "Boundary with Decks 101 and 201", evidence M). No in-scope test name or code range appears in either earlier deck. Three areas sit close: 101's composition-root slide (chapter 6's `build_app`, "the policy modules don't import the adapters", Seemann's Composition Root), 101's "Names for assistants" and "Prompting for a pattern", and 201's ExitStack test in the generator-form notes and its misuse section (the nine-class engine, the located dependency). Each gets a stated 301 angle, and the D5 boundary check reads both earlier decks' extracted text against 301's.

   **Recommend: yes.**

3. **Build.** `deck-301.js` requires `deck-lib.js` unchanged (md5 ab6f6022fbc519933a8dde0898ef020d) and `deck-helpers.js` unchanged (md5 47af3889bef56eba4736bb1565e17054). `render-png.sh` gains `figs_301=(33 40)` and `--deck 301`; a bare `--check` then covers 18 figures. `build-notes.md` names `deck-301.js` and extends the identity proof to Deck 201. The spike (evidence F, G) rebuilt Deck 101 and Deck 201 from the committed builders in a scratch copy: each differs from its committed file only in `docProps/core.xml`. A six-slide 301 skeleton built through `deck-lib.js` with no change to it, set the 98-character `test_doubles.py:19-34` at 13.5 pt and the 96-character `app.py:11-21` at 14 pt, and both fit the box when rendered.

   **Recommend: yes.** No change to `deck-lib.js` is needed; if D3 finds one, the identity proof for both earlier decks is re-run and recorded.

4. **Figures.** Two figures go in, each on its own full-width slide: 33 and 40 (evidence H, I).
   - 33 becomes eligible after F1 drops its two dashed annotation arrows (smallest label 6.4 pt, the lowest in any deck; the QA drop rule applies if a viewer can't read it).
   - 40 passes the census on r23's precedent (outcome arrows into "accepted" are witnessed by the asserts of `test_the_idiomatic_module_passes_every_gate` and the gate table test, as figure 37's were), after F2 corrects two box labels.
   - Out on legibility: 35 (6.2 pt), 36 (6.1 pt) and 39 (5.9 pt), although all three pass the census.
   - Out on the census: 11 (all four arrows are a process: claim, witness, seen failing, quoted run) and 34 (the "one technique" arrows between step modules are a refactoring sequence, not calls).
   - Neither 11 nor 34 is a defect in the book: a conceptual figure is allowed there. They stay out of the deck only.

   **Recommend: yes.** Alternative: leave 33 out as too close to the floor; the deck then has one figure, and slide 15 becomes a bullet slide on the patch targets with the same witnesses.

5. **Book defects found while planning** (evidence O). Each is fixed at D1c, before the census, with the doc's example tests and `validate.py` green after each edit and every recurrence grepped (front matter, `_examples/` card, example README, docstrings, captions, `_data/diagrams.yml`, `_docs/41` to `46`). Figures are fixed in `diagrams/specs/` and regenerated, never hand-edited; each changed figure's walk-through paragraph, include caption and registry caption are brought into line.

   Chapter 11 (Proving it works):
   - P1: `11.md:33` "the table of deletions records which named test failed". The chapter has no such table; the experiments record it in prose. Reword to "and the experiments record which named test failed".
   - P2: `11.md:33` defines a negative fixture as an underscore-prefixed object with a "Negative fixture:" docstring, and figure 11 draws one, but example 11 has none (`grep -rn "Negative fixture" examples/11-*` prints nothing; twelve other examples carry the docstring). The negative case here is the inline plain `Mock` of `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method` (`11.md:72`). Fix `11.md:72` to say that test plays the negative fixture's part in this example.
   - P3: `11.md:205` "then one or two substrings of the message". `test_static.py:109-113` checks three, and `test_static.py:56-60` checks an empty output. Reword to what the tests do.
   - P4: quoted output wider than its filter. `11.md:298` says experiments one, two and six quote `grep -E '^(>|E  |FAILED|[0-9]+ (passed|failed))'`, but the experiment-six block (`11.md:371-373`) omits the two `>` lines that filter prints (the `isinstance` line and the `warnings.warn` line from `typing`). Re-run experiment six in a scratch copy and quote the filter's output exactly, scrubbed.
   - P5: a claim resting on a probe. "Teardown runs when the test fails" is stated in the `quote_log` docstring (`tests/conftest.py:55`, quoted at `11.md:46`), `11.md:55` and `:345`, `examples/11-*/README.md:13-14`, the chapter 11 card (lines 17-18) and `44.md:92`, and only experiment three shows it (`_plans/evidence/yield-fixture-teardown-on-failure.md` is the planning record). **Recommend adding a witness** in example 11, a `pytester` test (module-level `pytest_plugins = ["pytester"]`, as example 42 does) whose inner test fails and whose fixture's teardown line is asserted, named `test_quote_log_teardown_runs_when_the_test_fails`, cited where the claim is made. Every count in chapter 11's quoted runs moves by one (23 functions and 34 cases become 24 and 35; the experiment summaries), so D1c re-captures them all. Alternative: put the witness in example 42 (one count sentence moves) and cite it across examples.

   Appendix B (pytest reference):
   - P6: `42.md:170` "an `AssertionError` that starts `Regex pattern did not match`" and `42.md:172` "ends `did not return True`". The tests (`test_raises.py:28`, `:41`) match unanchored. Anchor them (`^` and `$`), so the quoted position is tested.
   - P7: `42.md:59`, the member-table sentence ("appended to a member's `pyproject.toml`, a table with `addopts = ""` turned a failing `DeprecationWarning` test into a pass with one warning, and the header named the member's file as the configuration file"). No test covers it, and the survey couldn't reproduce it from the sentence. Add a `pytester` test in `test_config.py` that builds that layout; the sentence follows the run.
   - P8: card `_examples/42-appendix-b-pytest.md:14` says `write_quotes` "writes lines to the current `sys.stdout`"; it writes to `out` when given (`report.py:13`). Reword.

   Appendix C (mocking reference):
   - P9: card `_examples/43-appendix-c-mocking.md`. Line 24 lists `wraps` among doubles with "a test for what it refuses", and `wraps` refuses nothing (`test_wraps_passes_calls_through_to_the_real_gateway`). Line 9's card title "A mock that checks the most" reads against `43.md:23` ("the one that checks the least"). Reword both.

   Appendix D (xUnit test patterns):
   - P10: `44.md:102` ("`notify=mocker.stub()`, passed and never read") and `44.md:143` ("passes one that is never read, which makes it a Dummy Object"). `book_cheapest` calls `notify(reference)` (`examples/43-appendix-c-mocking/src/mocking_reference/booking.py:35`), so the stub is used; only the test never reads it. Meszaros's Dummy is never used. Mark the row qualified, as the appendix does for three others, and say what holds. Also `44.md:106`: `airco_fake` "always returns `2800`", and the closures also record the grams asked (34 `tests/test_steps.py:35-37`, 33 `tests/conftest.py:30-33`). Add that.

   Seams, dependency breaking, refactoring and rewriting (33 to 36):
   - P11: `33.md:202-203` quotes two full mypy lines; `test_static.py:158-159` asserts the codes and one substring. Tighten the assertion to the quoted message text (the r23 P7 treatment).
   - P12: `35.md:142` quotes "`EU-11: golden FASTLINE 14.84, now FASTLINE 14.85`"; `test_golden.py:130` asserts only `startswith("EU-11: golden ")`. Assert the full line.
   - P13: the `refactored.py:1` docstring says "after two catalogue refactorings" and lists three (lines 3-7); `examples/35-fowler-vs-feathers/README.md:12` repeats "two". Say three in both (`35.md:110` names no count).
   - P14: `examples/36-refactor-or-rewrite/README.md:86` "The engines are pure functions of a consignment"; the legacy engine is a class whose `quote` is a method. Reword to what holds: each engine's quote depends only on the consignment.

   Final project and AI (39, 40):
   - P15: `39.md:188` "a message that names `CarrierGateway`" and `40.md:201` "a message that names `Assistant`". The tests (`39 test_static.py:73`, `40 test_static.py:59`) assert the name anywhere in stdout. Assert it in the `[arg-type]` line.
   - P16: `40.md:61` attributes UP045 and UP037 to two annotations and the mypy codes to the unannotated methods and one call; `test_the_static_gate_reports_the_untyped_draft` asserts only the set of codes. The drafts are fixed text, so assert each code with its line (ruff 36:16, 36:25, 38:25; mypy `no-untyped-def` at 11, 16, 24, 27, 30 and `no-untyped-call` at 52, as the survey's probe printed; D1c re-reads them).
   - P17: `40.md:201` and `examples/40-*/README.md:5` "No test calls a network". The witness (`test_the_package_imports_no_network_module`) scans the package only, and `tests/conftest.py:11` imports `subprocess` to run ruff locally. Reword to what the test proves: the package imports no network module, and the tests run mypy in-process and ruff as a local process.
   - P18: `40.md:59` "Ruff runs with the repository's rule selection". The gate passes a hardcoded copy with `--isolated` (`tests/conftest.py:74-81`), equal to the root `[tool.ruff.lint]` today. Reword to "a copy of the repository's rule selection".
   - P19: `examples/39-final-project/README.md:36` "Two mypy checks run over small snippets"; it is one test with two `mypy.api` runs (`test_static.py:68-69`). Reword.

   Repo-wide:
   - P20: 39 example cards say "Then from the example directory:" and then `cd examples/<dir>`, which runs from the repository root (`grep -ln 'from the example directory' _examples/*.md` lists 39 files, each followed by `cd examples`). Reword to "Then, in the example's directory:" or equivalent, in all 39, with one grep before and after.
   - P21: `11.md:389` and `33.md` cite `pytest-mock.readthedocs.io/en/latest/`; Appendices C and D use `/en/stable/`. Both return 200, but `latest` follows the development branch, the same drift r23's P10 fixed for What's New. Normalise to `/en/stable/`.

   Figure specs:
   - F1, 33: the two dashed arrows from the ghost boxes ("patch on seams.fastline.request_quote" into the `seams.legacy` namespace, "margin=MARGIN in __init__" into `RateEngine`, spec lines 93-94) are annotations. The first draws a patch reaching a namespace it never touches (`test_patching.py:43-53` shows it doesn't), the r23 F2 case. Drop both edges, leave the two boxes unconnected as notes, and fix `33.md:28`.
   - F2, 40: the shape-review box says "reports typed_hierarchy" and the oracle box "reports rounded_callable" (spec lines 28, 36). Both gates also report `untyped_factory` (`test_gates.py:38-42`). Name every draft each gate reports, and fix `40.md:30`. The caption stays true.

   Bookkeeping (D0):
   - K1: `_plans/iteration-plan.md` still says "r23 (active)" and PDP-151 `active`. D0 closes r23 (PDP-151 `done`), marks PDP-152 and r24 `active`, with a dated note.
   - K2: `_plans/r23-plan.md` shows Z6 `todo`, though r23 is merged (6c27a6f), tagged `r23.x` and released (`gh release view r23.x`). The PRD build log records "two repair rounds, then an Opus confirmation (PASS)"; neither the r23 plan nor `_plans/evidence/r23-deck-qa.md` records the confirmation. D0 sets Z6 `done` and appends a dated Corrections note to the r23 plan saying the confirmation pass is recorded only in the PRD build log.
   - K3: `presentation/render-png.sh` and `build-notes.md` name two decks. D1a adds Deck 301.

   Validator (D1a):
   - V1: `DECK_BOOK_RE` matches "the book" and "the book's" only, so "this book" in a note passes `check_decks()`. Add it, with a self-test that fails without the change (the r23 B3 lesson: a self-test that can't fail proves nothing). Neither earlier deck contains "this book" (evidence M), so neither changes.

   Checked, not a defect:
   - Every URL in the ten docs returns 200 with no redirect; every quotation from a web source is verbatim on the fetched page.
   - No stale `file.py:N` reference: every one sits inside recorded output and matches a re-run.
   - The fences that join ranges (`35.md:114-124`, `40.md:67-85`, `40.md:97-112`, `40.md:162-195`) are allowed in chapters, as in r22 and r23; the deck uses contiguous runs only.
   - Mutation sentences that state their own edit (seven in chapter 39, four in 36, three in Appendix B, one in C) were reproduced by the surveys. They are re-runnable from the sentence, so they stay; the census reproduces any the deck quotes.
   - `43.md:165` quotes pytest-mock's warning text and says it is from the plugin's source for 3.17.0; `43.md:33`'s file counts were reproduced by grep.
   - "member" in the `_run` docstrings of 37 examples and in Appendix B is the workspace term; "survive" at `36.md:34` and "survives" at `43.md:230` are plain English in the book. Both are slide constraints only (section "Standalone wording").
   - `test_money_refuses_to_order_across_currencies` is defined in examples 07 and 11; the deck cites neither.
   - The sidebar form "An assistant may ..." at `11.md:228` (decision 8).

   **Recommend: fix P1 to P21, F1, F2, K1 to K3 and V1 in this iteration as stated, taking the recommended option in P5.**

6. **Code on slides.** As r22 decision 11 and r23 decision 6:
   - Each code slide names a file and a 1-based range; the builder asserts the first line against the anchor and sizes the font from the longest line. The longest here is 98 characters (`test_doubles.py:19-34`, 13.5 pt); two more exceed 95 (`app.py:11-21` at 96, `rating.py:21-34` of chapter 34 at 97), each at 14 pt. Evidence G shows 13.5 pt fits and reads.
   - Every range is a contiguous run of one chapter fence; the census records the fence. Ranges shorter than their fence: `test_acceptance.py:35-49` (fence 31-49), `desk.py:43-52` and `desk.py:53-60` (fence 43-60), `rating.py:21-34` (fence 16-37), `legacy.py:17-31` of chapter 33 (fence 8-31), `test_characterisation.py:67-76` (fence 57-76), `assistant.py:42-56` (a contiguous segment of the joined fence at `40.md:162-195`).
   - No range shows a docstring that carries "member", "the book" or a chapter title (evidence L lists them: `shape.py:1`, `:46`, `:67`, `:77-78`, the drafts' first line, the `_run` docstrings).
   - Where names collide (evidence N), each slide draws on one doc only and the notes name the concept.

   **Recommend: yes.**

7. **Quoted test output in notes.** The testing and legacy docs quote runs, and every quoted block carries a timing ("in 4.13s"). The rule:
   - Slide text carries no run output and no timing.
   - Notes may give a recorded experiment's result as counts and test names ("with `pop_all()` deleted, five tests fail and 18 pass, and mypy still exits 0"), with the edit that produced it, when the doc records that experiment and the census re-ran it (D1b). Never a duration, never "in N s", never a speed comparison.
   - A message is quoted in notes only when a test asserts that text (after P6, P11, P12, P15, P16); otherwise the notes name the exception type or the error code.
   - Counts that P5 moves are taken from the fixed tree.
   - No benchmark or measured number appears anywhere in this deck; none of the ten docs has one.

   **Recommend: yes.**

8. **The AI material.** Chapter 40 and the sidebars carry no outcome statistic, no frequency word ("often", "usually", "most"), no vendor or model name and no productivity claim (evidence K). The only statements about models are two attributed OWASP quotations. The deck may claim:
   - that the three drafts were written by hand and stand in for replies, so the results describe these drafts and make no claim about what any assistant writes (`40.md:26`, `test_every_draft_says_it_was_written_for_the_book`);
   - which gates report which draft, and that only the idiomatic module passes all three (the gate table tests);
   - how the loop behaves against a recorded fake, and that the package imports no network module (as narrowed by P17);
   - that the gates verify what they list and no further (`40.md:205`);
   - that a prompt can name the gates before any reply exists (`40.md:152`);
   - the two OWASP sentences, quoted and attributed, as the only statements about models.

   It may not claim anything about what assistants or models do, how often, or how well; may not name a vendor, model or product beyond the tools the gates run; and does not carry the sidebars' "An assistant may ..." sentences (`11.md:228` and the 19 pattern-chapter sidebars written in that form at r10b). Where a slide uses sidebar material, it states what the request leaves open ("'Mock the carrier in this test' leaves the target open", `33.md:224`), which is a statement about the request.

   The PRD's "reviewing Java-in-Python LLM output" is worded with the book's own terms: "the class-per-strategy shape", "no base classes, no static-only classes, no getters or setters" (`40.md:55`, `:213`), and the four shape rules' advice ("use a callable type alias", "use module-level functions", "use a plain attribute", "use a module-level instance", `shape.py:54, 63, 73, 82`). Not "nine classes", which is 201's misuse claim.

   On the sidebar form: CLAUDE.md says a sidebar is "not a description of what an assistant gets wrong", while `11.md:228` and 19 sidebars retrofitted at r10b open with "an assistant may ...". The owner approved that retrofit, so this plan doesn't treat it as a defect. **Owner's choice:** leave the 20 sidebars as they are (recommended), or reword their opening sentence to state what the request leaves open, as `33.md:224` to `36.md:155` already do, as a separate fix-now item.

   **Recommend: yes, and leave the sidebars.**

9. **Credits.** As r23 decision 8: a "Sources credited" table of the online sources the slides use, as the docs word them, and a "Reading further" table of the books (evidence S). Each source is also named in the notes of the slide that uses it. Nothing is copied beyond the docs' own attributed short quotes.

   **Recommend: yes.**

10. **No toolchain slide.** Deck 101 has one. The closing slide's notes name the pinned CPython, uv, pytest, pytest-mock, ruff and mypy versions, which this deck's subject leans on. No QR slide.

    **Recommend: yes.** Alternative: a toolchain table slide (43 slides).

11. **README and closing slide.** The README "Companion decks" list gains the 301 entry (slide count and the rebuild pointer). No site page and no `_config.yml` change. The cover, the README line and the closing slide's "two further decks" bullet name 301's theme, "proving it works, changing inherited code, and AI on pattern-heavy code". The 101 and 201 closing bullets already name 301 by theme ("testing, inherited code and working with AI tools"), so neither earlier deck changes for this.

    **Recommend: yes.**

## Planning evidence

All trials ran in a scratch copy of the tree at HEAD under `<scratchpad>/plan24` (`git archive`, then `uv sync --locked --all-packages` and a local `npm ci` there). Nothing was installed in the repo or globally, nothing on the host changed, and the scratch tree was deleted before the plan commit. Three read-only survey agents covered the docs (J, K, L); their line numbers, anchors and test names came from commands they ran, and the planner re-read each defect at the cited lines.

A. **Repo state.** `release/r24` was cut from main at 6c27a6f; `git tag --points-at 6c27a6f` prints `r23.x`; the tree was clean at the start. `_plans/iteration-plan.md` still says "r23 (active)" and PDP-151 `active` (K1). `_plans/r23-plan.md` shows Z6 `todo` (K2). Reconciliation rows run to 398 (`verified (r23)`), so r24 starts at 399. README "Companion decks" lists 101 and 201; `LICENSE-docs.md` line 7 already covers the decks under `presentation/`.

B. **Intent.** PRD §8d: 301 is "Testing, legacy code, and the AI throughline, including easy-seams and reviewing Java-in-Python LLM output". §2: "The series' legacy-code track (Feathers), reframed for Python's reality that dynamism makes seams easy". The PRD's r19 build log: chapter 40 has "No network, no vendor names, model statements only as attributed OWASP quotations". Its r23 entry records "two Opus rounds with independent page viewers, two repair rounds, then an Opus confirmation (PASS). Two round-2 findings were orchestrator slips in repair 1".

C. **r22 and r23 lessons.**
   - Both decks' round-1 failures were pointer phrases in notes; r23's round 2 found slips the orchestrator introduced in repair 1 and self-tests that couldn't fail.
   - `check_decks()` (`scripts/validate.py:984-1082`) refuses dashes, internal codes, "spike", "capstone", chapter and appendix words, slide numbers, positional forms (`next|previous|following|closing|last|earlier|later` before slide or section, "that follows", "before it", "close the section", "above" and "below" in pointer forms, "the dividers", "where they're used"), "this deck" and "these slides", the cross-language words, and "the book" except on the closing slide. It does not catch bare "next", "earlier", "later" or "follows", the three-way-split labels, or "this book" (V1). QA step 8's grep covers the rest.
   - `pgrep -f soffice` matches its own command line; QA uses `pgrep -x soffice.bin`.

D. **Pins** (2026-11-07). `npm view pptxgenjs dist-tags`: `latest 4.0.1`, `beta 4.0.1-beta.2`. `npm view image-size version`: 2.1.0. `npm audit` after `npm ci` in the scratch copy: 0 vulnerabilities. PyPI: cairosvg 2.9.1, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4, uv 0.13.7. endoflife.date: Python 3.15 latest 3.15.2. Node v22.22.2, npm 10.9.7. `require.resolve('pptxgenjs')` resolves under the scratch copy's own `presentation/node_modules`.

E. **Spike: earlier decks.** In the scratch copy, `node deck-101.js` printed `slides: 62 min notes words: 50` and `node deck-201.js` printed `slides: 45 min notes words: 45`. Unzipped against the committed files, `diff -rq` reports only `docProps/core.xml` for each. md5: `deck-helpers.js` 47af3889bef56eba4736bb1565e17054, `deck-lib.js` ab6f6022fbc519933a8dde0898ef020d.

F. **Spike: 301 skeleton.** A six-slide builder (cover by `bump()`, a divider, two code slides, two figure slides) required `deck-lib.js` unchanged and built. `codeSlide` returned `longest 98, fontSize 13.5` for `test_doubles.py:19-34` and `longest 96, fontSize 14` for `app.py:11-21`. `./render-png.sh 33 40` rendered both figures. soffice converted the deck with a private profile and `pdftoppm` rendered six pages; no `soffice.bin` remained.

G. **Spike: pages.** The 16-line, 98-character listing fits the box with its caption below. Figure 33 at full width (slide 5 of the skeleton, viewed at 160 dpi) reads; its edge labels are the smallest text in either new figure.

H. **Legibility** (smallest SVG `font-size` scaled into the 12.09 by 4.95 in box; floor 6.3 pt, Deck 101's smallest accepted figure).

| Fig | viewBox | Smallest label, pt | Note |
| --- | --- | --- | --- |
| 11 | 840x470 | 8.7 | out on the census |
| 33 | 1020x610 | 6.4 | in after F1 |
| 34 | 1300x520 | 7.4 | out on the census |
| 35 | 1100x660 | 6.2 | below floor |
| 36 | 1160x640 | 6.1 | below floor |
| 39 | 920x820 | 5.9 | below floor |
| 40 | 960x500 | 7.8 | in after F2 |

I. **Figure census** (arrow by arrow, from the specs and the code; D1b re-runs it after D1c). Every in-scope registry caption equals its include caption with the "Figure N.1: " prefix removed, with 31 to 42 words.

| Fig | Every arrow composed by code? | Deck |
| --- | --- | --- |
| 11 | No: claim to witness, witness to seen failing, seen failing to quoted output, negative fixture to witness are a process | out |
| 33 | The test's patch (`test_patching.py:36`) and the two lookups (`legacy.py:24`, `:25-27`) are composed; the two dashed annotation arrows are not (spec 93-94) | F1, then in |
| 34 | The table to each step box is composed (`conftest.py:133-167`, `:184-199`); legacy to parameterised to wrapped is a sequence of modules, not calls | out |
| 35 | Yes, except the edge into the workflow bar (conceptual) | out on legibility |
| 36 | Yes (`strangler.py:40-56`, `test_parity.py:32-57`) | out on legibility |
| 39 | Yes (`desk.py:43-59`, `clearance.py:68`) | out on legibility |
| 40 | Draft to each gate composed in the tests (`conftest.py:98`, `shape.py:104`, `test_gates.py:45-64`); the propose loop composed (`assistant.py:49-55`); the three edges into "accepted" witnessed by asserts (`test_gates.py:61-67`, `:74-78`); two box labels incomplete | F2, then in |

J. **Survey: chapter 11 and Appendices B, C, D** (agent s1).
   - Runs: 11 has 23 functions and 34 passed; 42 has 38 and 43 passed; 43 has 26 and 32 passed. Appendix D has no example of its own and quotes ranges from 11, 39 and 42. Every stated count matches.
   - Every python fence in the four docs is a byte-exact contiguous run of one source file. Every URL returns 200.
   - Quoted runs in chapter 11 match a fresh run apart from timings, except experiment six (P4).
   - Neither chapter 11 nor the appendices has a bucket line or a "When not" heading; chapter 11's nearest is "When a test proves less than it seems" (`11.md:217`).
   - Defects P1 to P10. Phrases no slide may carry: `11.md:33` "The examples in this book", the chapter-title references in all four docs, "member" at `11.md:318` and throughout `42.md:59-67`, and Appendix D's "the book's" column headers.

K. **Survey: chapters 39 and 40 and the sidebars** (agent s3).
   - Runs: 39 has 19 functions and 23 passed; 40 has 18 and 26 passed. Quoted blocks and both experiments in each match apart from timings.
   - Chapter 40: no outcome statistic, frequency word, vendor or model name; model statements are the two OWASP quotations (`40.md:24`, `:207`), verbatim on pages that return 200. No real model is called: `RecordedAssistant` replays fixed strings keyed by prompt; mypy runs through `mypy.api` and ruff as a local subprocess.
   - The final project's own listings: `BookingDesk.ship`, `build_desk`, `acceptance_failures` and the end-to-end and left-out tests, `_EagerBookingDesk`, the rollback, tracking-order, structure and gateway mypy tests, and billing. Its other parts re-implement earlier patterns under shared names (`Signal`, `TrackingHistory`, `FastlineGateway`, `CarrierGateway`, `per_kg`), which the deck shows only through the desk.
   - Defects P15 to P19 and F2.

L. **Survey: chapters 33 to 36** (agent s2).
   - Runs: 33 has 19 functions and 21 passed; 34 has 13 and 42; 35 has 8 and 30; 36 has 15 and 19. Every quoted block and experiment matches apart from timings. All 25 URLs return 200; all 20 web quotations are verbatim.
   - None is a pattern chapter: no bucket sentence. Force sentences: `33.md:22`, `34.md:22`, `35.md:22`, `36.md:22` and `:32`.
   - Defects P11 to P14 and F1. Phrases no slide may carry: "this chapter" in each, the Feathers chapter titles named as "chapter", "the next chapter" (`35.md:232`), "experiment (b) below" (`33.md:92`), "survive" (`36.md:34`), and "member" in the `_run` docstrings.

M. **Overlap with Decks 101 and 201** (grep of both builders and of the extracted text in `presentation/qa/`).
   - No code range from examples 11, 33 to 36, 39, 40, 42 or 43 is in either deck.
   - No in-scope test name is in either deck (`comm -12` of the decks' test names against the 194 distinct names in those examples prints nothing). Appendix D cites `test_two_threads_parked_between_read_and_write_take_the_same_slot`, which Deck 201 uses; 301 doesn't cite it.
   - Deck 101 has: the composition-root code slide (chapter 6's `build_app`, with "the policy modules don't import the adapters" and Seemann's Composition Root credited), the "Fail fast" principle row, "Names for assistants", "Prompting for a pattern", the toolchain table naming pytest-mock, and *Refactoring* and *Architecture Patterns with Python* in its reading list.
   - Deck 201 has: `test_exit_stack_unwinds_entered_writers_in_reverse_order` in the generator-form notes, the misuse section ("A quote as a function" with the nine-class engine, "A located dependency"), and Fowler's inversion-of-control article.
   - "this book" appears in neither deck's text (V1 changes neither). The three-way-split labels appear in Deck 101 only (11 slide hits, 25 notes hits), as its subject.

N. **Name collisions inside Deck 301's sources.**
   - `RateEngine`: chapter 11's (gateways mapping, clock, validity); 33's and 34's `legacy.RateEngine` (identical, no carrier parameters); 34's `parameterised.RateEngine` and `wrapped.RateEngine`; 35's legacy (keyword carriers) and `refactored.RateEngine`; 36's band if-chain.
   - `quote`: 34's `rating.quote(consignment, /, *, quoters, margin)` against 36's `rating.quote(consignment, /, *, tariff)`.
   - `Consignment` and `RateQuote`: carrier field in 33 to 35, none in 36; `Consignment(id, zone, weight)` in 42.
   - `CarrierGateway`: 11 (`quote`, `book`), 39 (`book`, `cancel`), 43 (`quote(consignment_id, weight_kg)`, `book`).
   - `_mismatches`: 35 returns "row: golden X, now Y" lines; 36 returns row ids. `_observed` differs between 34 and 35.
   - Tables: 34's characterisation rows, 35's intent rows and golden quotes, 36's parity rows and `ACCEPTED_DIFFERENCES`; row ids `fastline-cheaper`, `airco-cheaper`, `tie-goes-to-airco`, `grams-truncated` shared by 34 and 35.
   - Altered copies: 34's `_GramsRoundedRateEngine` and `_HalfEvenRateEngine` against 35's `_CentFirstRateEngine` and `_RoundBuiltinRateEngine`; both families involve half-even rounding.
   - `GRID`: 35's weight grid against 40's oracle grid.

O. **Defects** (decision 5). Located by the surveys and re-read by the planner at: `11.md:33`, `:205`, `:298`, `:371-376`; `44.md:102`, `:106`, `:143` against `booking.py:30-36`; `refactored.py:1-8`; `_examples/43-appendix-c-mocking.md:9`, `:24`; `_examples/42-appendix-b-pytest.md:14` against `report.py:10-15`; `42.md:59`; the "from the example directory" lines in all 39 cards; `diagrams/specs/40-*.py:20-36`; `diagrams/specs/33-*.py:93-94` and `33.md:28`; the `pytest-mock.readthedocs.io/en/latest` hits (two files).

P. **Step letter.** `grep -nE '^\| D[0-9]' _plans/*.md` and `grep -n 'run: D' _plans/*.md _plans/evidence/*.md` print nothing. No plan has a `| B1 |` step row either; the r23 B ids are prose labels.

Q. **URLs.** The site `https://patterncatalyst.github.io/design-patterns-with-python/` and the repository `https://github.com/patterncatalyst/design-patterns-with-python` returned 200 at r23 and are re-checked at D4a.

R. **Registry.** PDP-152 is `todo`; PDP-151 and r23 are `active` (K1); every other row of a tagged iteration is `done`, apart from the two `n.a.` rows and the `covered by` row.

S. **Books and sources the 301 docs cite** (from the surveys; D1b confirms each against `bibliography.html` and the doc that cites it).
   - Books:
     - *Working Effectively with Legacy Code* (Feathers, Prentice Hall, 2004);
     - *Refactoring*, second edition (Fowler, Addison-Wesley, 2018);
     - *xUnit Test Patterns: Refactoring Test Code* (Meszaros, Addison-Wesley, 2007);
     - *Python Testing with pytest*, second edition (Okken, Pragmatic Bookshelf, 2022);
     - *Architecture Patterns with Python* (Percival, Gregory, O'Reilly, 2020);
     - *Effective Python*, third edition (Slatkin, 2024), cited by chapter 11.
   - Online:
     - pytest documentation (fixtures, parametrize, monkeypatch, capture-warnings, reference, configuration, import mechanisms, plugins);
     - pytest-mock usage page;
     - the Python library documentation (`unittest.mock` with "Where to patch" and "Autospeccing", `importlib`, `contextlib`, `decimal`, `bisect`, `ast`, `typing`, `functools.partial`, `json`) and typeshed's `unittest/mock.pyi`;
     - the mypy command-line page and the ruff rules index;
     - Martin Fowler's bliki ("Mocks Aren't Stubs", "Definition Of Refactoring", "Self Testing Code", "Legacy Seam", "Strangler Fig", "Dark Launching") and the refactoring.com catalogue;
     - Ian Cartwright, Rob Horn and James Lewis, "Patterns of Legacy Displacement" (Feature Parity, Transitional Architecture);
     - xunitpatterns.com, Meszaros's pre-publication pages;
     - OWASP Top 10 for LLM Applications, LLM05:2025 and LLM09:2025;
     - syrupy, approvaltests and inline-snapshot on PyPI.
   - The slides credit only what they use; D1b builds both tables from the census.

## Boundary with Decks 101 and 201

Each row is an earlier-deck slide, row or note that a 301 slide sits near, and the angle 301 takes so that no slide repeats it.

| Earlier deck has | Deck 301 teaches instead |
| --- | --- |
| 101 "The composition root" (chapter 6's `build_app`; "the policy modules don't import the adapters"; Seemann credited) and the "Fail fast" row | the final project's root choosing the pricing rule and the subscriber as well as the carrier, and mypy refusing a gateway without `cancel`; the ast structure test appears only in the notes, as the final project's check; Percival and Gregory's bootstrap chapter credited, not Seemann (slide 33) |
| 101 "Names for assistants" (a pattern name as a checkable claim) | nothing on naming; the gates check the reply, whatever it is called (slides 35 to 38) |
| 101 "Prompting for a pattern" (the prompt states the decisions) | a prompt that lists the gates the reply will be measured against, and the review line for a diff that moves an answer the gates hold (slide 38 notes) |
| 101 toolchain table (pytest-mock as the mocker fixture) | what each double refuses and what mypy sees of it; no tool table (slides 5, 6) |
| 201 generator-form notes (`test_exit_stack_unwinds_entered_writers_in_reverse_order`, ExitStack unwinding entered writers) | `ExitStack.callback` registering inverses and `pop_all()` as the commit; the 201 test and "entered writers" never appear (slide 31) |
| 201 "A quote as a function" (the nine-class engine, two forms on one table) | the drafts' class-per-strategy shape as one row of a gate table, with no class count and no "nine classes" (slide 35); anti-patterns by concept only |
| 201 "A located dependency" (service locator, Fowler's article, Seemann's post) | no locator; the composition root is the only place that names a concrete carrier (slide 33) |
| 201 "Absence in the type", "A silent null object" | the acceptance test's stand-ins that "do nothing useful" are stage removals, not null objects (slide 30 notes) |

Deck wording: "the class-per-strategy shape" and "no base classes, no static-only classes, no getters or setters" for the PRD's "Java-in-Python"; "inherited code" and "the legacy engine" for the code under change; "an assistant's reply" or "a draft" for model output, never a claim about what assistants do.

## Deck 301 slide inventory

Columns, as in r23: # (build order); section; title (2 to 5 word noun phrase); claim and its source sentence (`NN.md:line`); witness tests; code (file and lines, anchor in the census) or figure; what the notes cover. Code paths are under `examples/<doc dir>/src/<package>/` unless they start with `tests/`. Line numbers are from the tree at 6c27a6f; D1c moves some (P1 to P5 in chapter 11, P10 in 44, P16 to P18 in 40, F1 in 33), and D1b re-finds every sentence, line, anchor and test after D1c. Anything that differs goes in Corrections; a claim that can't be witnessed is cut before the builder runs.

| # | Section | Title | Claim (source) | Witness | Code or figure | Notes cover |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Cover | Design Patterns with Python | 301: Testing, legacy code and AI | - | cover panel | proving it works, changing inherited code, AI replies held to gates; the shipping domain; tested code |
| 2 | Cover | Seven themes | the seven themes and the reference, two columns | - | bullets | each theme by concept |
| 3 | Proving it works | divider | - | - | section panel | a claim, its witness, and a check seen failing |
| 4 | Proving it works | Tests named as claims | 11.md:33 "A test is named as a claim ... so a failure reads as a broken sentence."; 11.md:221 asserts the return value before the calls | `test_book_best_books_only_the_winner`, `test_book_best_books_the_winner_and_returns_its_reference` | `tests/test_doubles.py:19-34` (16 lines, max 98, 13.5 pt) | a check deleted in a scratch copy must fail (11.md:223); experiment one's edit and its failing tests as counts (decision 7); the negative case after P2 |
| 5 | Proving it works | What each double refuses | 11.md:63 "Each kind of double refuses something different." | `test_a_fake_rejects_unknown_names_and_wrong_signatures`, `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method`, `test_spec_rejects_unknown_names_but_not_wrong_signatures`, `test_autospec_rejects_names_and_signatures` | table from 11.md:65-70: Double, Unknown name, Wrong call, mypy | the plain mock's misspelt assertion passing (11.md:23); Fowler's "Mocks Aren't Stubs" credited |
| 6 | Proving it works | Autospec copies signatures | 11.md:89 "Only `create_autospec` copies the signatures"; 11.md:125 "mypy accepts every one of the mocks where a `CarrierGateway` is expected."; 11.md:153 the practical rule | `test_autospec_rejects_names_and_signatures`, `test_mypy_accepts_every_mock_where_a_gateway_is_expected`, `test_mypy_checks_a_hand_written_fake` | `tests/test_doubles.py:59-66` (max 86) | why mypy accepts a mock (typeshed's comment, 11.md:127); `side_effect` drives the timeout branch (11.md:123, `test_side_effect_drives_the_timeout_branch`); the unittest.mock autospeccing docs |
| 7 | Proving it works | An injected clock | 11.md:157 "has nothing to patch and nothing to wait for"; 11.md:159 code order and the tie-break | `test_quote_validity_comes_from_the_injected_clock`, `test_validity_reads_the_environment_and_the_context_restores_it`, `test_carriers_are_asked_in_code_order`, `test_a_tie_is_broken_by_the_carrier_code_in_the_quote` | `tests/test_engine.py:68-80` (max 95) | the environment as a mapping and `monkeypatch.context()` for the one real-environment test; yield-fixture teardown on failure, witnessed after P5 (`test_quote_log_teardown_runs_when_the_test_fails`) |
| 8 | Fixtures and test doubles | divider | - | - | section panel | configuration that refuses silence; doubles by what they record; two vocabularies |
| 9 | Fixtures and test doubles | Settings that refuse silence | 42.md:23 "an unregistered marker, an `xfail` test that passes and a deprecation ... all leave a green run"; 42.md:42 "Four of its settings refuse what pytest's defaults let through." | `test_an_unregistered_marker_fails_collection_under_strict_markers`, `test_a_passing_xfail_fails_the_run_under_strict_xfail`, `test_an_unknown_option_fails_under_strict_config`, `test_filterwarnings_error_turns_a_warning_into_a_failure` | bullets | one configuration file per run (42.md:59, `test_the_first_config_file_wins_and_is_not_merged`, and P7's test); the pytest reference and configuration pages |
| 10 | Fixtures and test doubles | Same-name test files | 42.md:102 "Under `prepend` pytest reports an import file mismatch and the run has one collection error."; 42.md:104 the cost of importlib | `test_same_basename_test_files_collide_under_prepend`, `test_importlib_mode_gives_each_test_file_a_unique_name`, `test_importlib_mode_cannot_import_conftest_by_name` | `tests/test_import_modes.py:15-28` (max 91) | shared values through fixtures, types under `TYPE_CHECKING` (42.md:106); the import-mechanisms page |
| 11 | Fixtures and test doubles | Calls recorded in order | 43.md:129 "`assert_has_calls` is stricter than its name suggests, and looser than `mock_calls ==`."; 43.md:103 | `test_assert_has_calls_checks_a_contiguous_ordered_run`, `test_mock_calls_records_calls_in_order_with_call_objects` | `tests/test_calls.py:81-91` (max 89) | `spec_set` and the assertion-typo refusal (43.md:60, 64; `test_spec_set_refuses_setting_a_name_the_spec_lacks`, `test_an_assertion_typo_raises_instead_of_passing`); a mock bypasses the static check (43.md:23); stubs keep their count after `resetall` (43.md:230, worded without "survives") |
| 12 | Fixtures and test doubles | Two vocabularies | 44.md:147 "When a test says "stub" or "spy", ask which vocabulary it is in." | `test_stub_records_a_callback`, `test_spy_keeps_the_real_behaviour_and_records_returns`, `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` | table: Word, pytest-mock meaning, Meszaros meaning (cells worded from 44.md:143-145 after P10, census) | Meszaros's book and xunitpatterns.com; the pytest-mock usage quote; state against behaviour verification (44.md:162) |
| 13 | Seams in Python | divider | - | - | section panel | Python looks a name up when the call runs, so every global the code reads is a seam |
| 14 | Seams in Python | An engine kept as found | 33.md:22 force sentence; 33.md:63 "`seams.legacy` holds its own binding of it." | `test_the_legacy_engine_calls_the_real_carrier` | `src/seams/legacy.py:17-31` (max 91) | Feathers's seam and enabling point (33.md:32); the stand-in SDKs do no I/O and raise what a timeout would; "this RateEngine is the inherited one, before any parameter" |
| 15 | Seams in Python | Patch where it's looked up | 33.md:69 the mock docs' principle (quoted, credited); 33.md:88; 33.md:92 "The import form decides the target." | `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`, `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`, `test_a_module_attribute_is_patched_on_the_module_it_belongs_to`, `test_unittest_mock_patch_follows_the_same_lookup_rule` | figure 33 (after F1) | each box and arrow; the two unconnected notes; `33.md:224`'s request-leaves-the-target-open line (decision 8) |
| 16 | Seams in Python | A default captured early | 33.md:157 "a patch to the global it was copied from can't change it."; 33.md:159 a reload overwrites a live patch | `test_patching_a_module_constant_misses_a_default_captured_at_definition`, `test_reload_discards_a_patch_and_keeps_old_bindings` | `tests/test_seams.py:64-78` (max 76) | the switches that turn a refusal into a silent miss (33.md:103, `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`, `test_patch_refuses_a_name_the_module_does_not_have`); the importlib docs |
| 17 | Seams in Python | What mypy sees of a patch | 33.md:197 "mypy exits 0 with no errors."; 33.md:199 "A direct assignment is checked."; 33.md:219 | `test_mypy_does_not_check_a_monkeypatched_replacement`, `test_mypy_checks_a_direct_assignment_to_a_module_name`, `test_mypy_accepts_a_misspelt_monkeypatch_target_string`, `test_mypy_checks_a_fake_passed_to_a_protocol_parameter` | bullets | a patch is the way to get the first test in, and the parameter is the next step (33.md:214, 221); the quoted mypy lines only after P11 |
| 18 | Breaking dependencies | divider | - | - | section panel | change the structure, keep the behaviour, and record the behaviour first |
| 19 | Breaking dependencies | A characterisation table | 34.md:32 "A characterisation test records what code does, so that a change can be told apart from a fix."; 34.md:59 the truncation row | `test_every_step_matches_the_characterisation_table`, `test_the_table_catches_a_step_that_changes_behaviour`, `test_every_step_lets_a_carrier_timeout_fail_the_quote` | `tests/test_characterisation.py:67-76` (max 61) | 34.md:84 "A table that can't fail proves nothing."; the half-up margin row; Feathers credited; experiment one as counts, with mypy exiting 0 (34.md:231) |
| 20 | Breaking dependencies | Carriers as parameters | 34.md:88; 34.md:107 "mypy now checks the fake." and the price of the defaults | `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`, `test_mypy_checks_a_fake_passed_as_a_constructor_argument` | `src/dependency_breaking/parameterised.py:27-36` (max 54) | the typing docs on callable objects; "this RateEngine takes the carriers as parameters" |
| 21 | Breaking dependencies | The engine as a function | 34.md:153 "the function form drops them." | `test_the_function_form_needs_its_quoters`, `test_mypy_reports_a_missing_quoters_argument`, `test_quote_standard_binds_the_standard_quoters` | `src/dependency_breaking/rating.py:21-34` (max 97, 14 pt) | `airco_quote` keeps the truncation (34.md:120, `test_airco_quote_converts_kilograms_and_cents`); `functools.partial` docs; "this quote takes quoters, not a tariff" |
| 22 | Breaking dependencies | A misspelt override | 34.md:183 "The seam is a method name, and without `@override` nothing checks the name before the quote runs." and "`@override` from `typing` closes the gap." | `test_a_misspelt_override_falls_through_to_the_real_carrier`, `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator` | bullets | subclass and override as the one comparison form; techniques Python makes unnecessary (34.md:185-196, as concepts) |
| 23 | Refactor or rewrite | divider | - | - | section panel | tests that record intent, golden values that record behaviour, and a rewrite held to parity |
| 24 | Refactor or rewrite | Intent rows and golden quotes | 35.md:24 "passes all five and still changes 18 of 120 recorded quotes"; 35.md:71 "not "is this right" but "did this change"" | `test_the_intent_rows_pass_every_engine_and_both_rounding_refactors`, `test_the_golden_quotes_catch_a_refactor_that_changes_rounding`, `test_the_golden_file_records_the_legacy_engine` | bullets | why the rows pass (35.md:67); Fowler's definition of refactoring and Self Testing Code, Feathers's Changing Software; characterise, then refactor (35.md:148, 150) |
| 25 | Refactor or rewrite | A golden comparison | 35.md:106 "A golden value pins whatever the code did, including behaviour you would call wrong."; 35.md:144 half even in the default context | `test_the_refactored_engine_matches_the_golden_quotes`, `test_round_with_two_digits_rounds_half_to_even_in_the_default_context`, `test_the_golden_quotes_catch_a_refactor_that_changes_rounding` | `tests/test_golden.py:66-79` (max 89) | regenerating the file as its own commit (35.md:106); the EU-11 line only after P12; the decimal docs; "these mismatches are lines, not row ids" |
| 26 | Refactor or rewrite | The rewrite's quote | 36.md:24 the `bisect_left` against `bisect_right` trap; 36.md:83 both engines put a limit in the lower band | `test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries`, `test_band_limits_include_the_boundary_weight` | `src/refactor_or_rewrite/rating.py:30-42` (max 90) | Fowler's Strangler Fig quote (36.md:24); the bisect docs; "this quote takes a tariff" |
| 27 | Refactor or rewrite | Parity and accepted differences | 36.md:100 "The list records a decision, so a reviewer who sees it grow can ask who made that decision."; 36.md:36 | `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted`, `test_the_legacy_engine_prices_an_unknown_zone_as_eu`, `test_the_rewrite_refuses_an_unknown_zone` | bullets | Feature Parity (Cartwright, Horn, Lewis); the 50.001 rows that pin the last limit (36.md:98); "these mismatches are row ids" |
| 28 | Refactor or rewrite | A router with a shadow | 36.md:135 the router and the legacy engine deleted together; 36.md:137 a mismatch holds both amounts | `test_the_router_serves_migrated_zones_from_the_rewrite`, `test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote`, `test_with_every_zone_migrated_the_legacy_engine_is_never_called` | `src/refactor_or_rewrite/strangler.py:35-46` (max 62) | Transitional Architecture, Dark Launching; the decision: parity table, accepted list, seam (36.md:149, 151); mypy holds the rewrite to the call shape (36.md:139, `test_mypy_requires_the_rewrite_to_take_a_consignment`) |
| 29 | The final project | divider | - | - | section panel | one booking through every step, undone on a refusal, published after the commit |
| 30 | The final project | An acceptance test first | 39.md:34; 39.md:68 "a failing run says which stage is absent, not only that something is." | `test_a_booking_request_ships_end_to_end`, `test_the_acceptance_test_fails_when_a_stage_is_left_out` | `tests/test_acceptance.py:35-49` (max 88) | the four left-out stages as a spoken table (39.md:70-75); Percival and Gregory's high gear and low gear chapter; 39.md:79 |
| 31 | The final project | Undo in reverse | 39.md:101 "a refusal runs them newest first"; 39.md:126 "`pop_all()` is the commit"; 39.md:141 | `test_the_undo_runs_in_reverse_order_of_the_steps`, `test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking`, `test_a_full_sailing_books_nothing_with_the_carrier` | `src/final_project/desk.py:43-52` (max 59) | the three contextlib sentences, credited; experiment one (delete `pop_all()`) as counts with mypy exiting 0; the when-not: a restart, a step that can't be undone, Unit of Work credited (39.md:198) |
| 32 | The final project | Publish after the commit | 39.md:147 "An event can't be taken back."; 39.md:166 "effects other parts can see go after `pop_all()`." | `test_a_held_booking_publishes_no_tracking_event`, `test_an_eager_publisher_reports_a_booking_that_was_rolled_back` | `src/final_project/desk.py:53-60` (max 89) | experiment two as counts, "publish order isn't a type" (39.md:309); billing's two-currency refusal (`test_an_invoice_in_two_currencies_has_no_total`) |
| 33 | The final project | One composition root | 39.md:170 "the fewer places that do, the fewer places change when a carrier does." | `test_the_pricing_rule_is_chosen_at_the_composition_root`, `test_mypy_refuses_a_gateway_without_cancel`, `test_only_the_composition_root_names_a_concrete_carrier` | `src/final_project/app.py:11-21` (max 96, 14 pt) | the boundary angle (leads with the rule and the cancel guard); Percival and Gregory's bootstrap chapter; the message assertion after P15 |
| 34 | Working with AI tools | divider | - | - | section panel | a reply trusted as far as the checks it has passed |
| 35 | Working with AI tools | Three drafts, three gates | 40.md:53 "Each gate alone accepts at least one draft that another gate stops"; 40.md:26 the drafts are hand-written stand-ins | `test_each_draft_fails_exactly_the_gates_in_the_table`, `test_the_idiomatic_module_passes_every_gate`, `test_every_draft_says_it_was_written_for_the_book` | table from 40.md:46-51: Draft, Static gate, Shape review, Behaviour oracle | the drafts' shapes in the book's words (decision 8); OWASP LLM05:2025 quoted and credited (40.md:24) |
| 36 | Working with AI tools | Gates in parallel | 40.md:53 "The gates answer different questions."; 40.md:89 the typed draft passes mypy and ruff | `test_mypy_and_ruff_pass_the_typed_hierarchy`, `test_the_static_gate_reports_the_untyped_draft`, `test_the_oracle_lists_the_half_cent_rows` | figure 40 (after F2) | each box and arrow; the half-cent rows as the oracle's evidence; the mypy and ruff pages credited; the codes only as P16 tests them |
| 37 | Working with AI tools | A seam for the model | 40.md:158 "Code that asks an assistant for a reply has a dependency like any other"; 40.md:199 "a test can't pass on a prompt nobody recorded" | `test_a_rejected_reply_is_sent_back_with_its_findings`, `test_the_loop_stops_at_the_first_accepted_reply`, `test_the_loop_gives_up_after_its_attempts`, `test_an_unrecorded_prompt_is_refused`, `test_the_package_imports_no_network_module`, `test_mypy_refuses_an_assistant_without_reply` | `src/review_gate/assistant.py:42-56` (max 91) | `RecordedAssistant` described; the network sentence as narrowed by P17; a real client would be an adapter behind the Protocol |
| 38 | Working with AI tools | Limits of the gates | 40.md:205 "The gates verify what they list."; "checked on those rows and in those shapes, and no further"; 40.md:207 OWASP LLM09:2025 | `test_the_oracle_lists_the_half_cent_rows`, `test_mypy_and_ruff_pass_the_typed_hierarchy` | bullets | a diff that edits the expected rows moves the answer (40.md:205); a prompt that names the gates before any reply exists (40.md:152), with the review line; OWASP credited |
| 39 | Reference | divider | - | - | section panel | sources, books, where the examples live |
| 40 | Reference | Sources credited | the online sources the slides use (evidence S) | census | table: Source, Used for | each, as the docs word them |
| 41 | Reference | Reading further | the books the 301 docs cite (evidence S) | census | table: Book, Authors, Year | what each adds |
| 42 | Reference | Site and repository | the site and repository URLs (evidence Q) | URLs return 200 at D4a | bullets | how to run an example; pins (decision 10); the other two decks by theme |

Section names: "Proving it works", "Fixtures and test doubles", "Seams in Python", "Breaking dependencies", "Refactor or rewrite", "The final project", "Working with AI tools", "Reference". Slide 2's title counts seven themes plus the reference, as Deck 201's "Eight themes" did; D4b may retitle it if the voice pass finds a better noun phrase, never a positional one.

## Standalone wording

The executor brief carries this list; D1b extends it from the census.

- No slide or note says "this book", "the book's", "in this chapter", "the chapter titled", "earlier chapter", "the pattern chapters", "experiment (b) below", "the parts table", or a doc's title as a pointer. Notes give an outside source's chapter titles only as a credit ("Feathers's 'The Seam Model'"), and never the word "chapter" (`check_decks()` refuses it): "in *Working Effectively with Legacy Code*, under 'The Seam Model'".
- No "member" in the workspace sense: "an example", "the example's directory".
- No "dissolves", "survives", "disambiguates" or inflections (`36.md:34`, `43.md:230` reworded).
- No "Written for the book" quoted; the drafts are "written by hand as stand-ins".
- Collisions named by concept (evidence N): "the inherited engine", "the engine with carrier parameters", "the quote that takes quoters", "the quote that takes a tariff", "golden mismatch lines", "parity row ids".

## Build setup

```
presentation/
  deck-helpers.js       # unchanged (md5 47af3889bef56eba4736bb1565e17054)
  deck-lib.js           # unchanged (md5 ab6f6022fbc519933a8dde0898ef020d)
  deck-101.js           # unchanged
  deck-201.js           # unchanged
  deck-301.js           # new builder
  render-png.sh         # figs_301=(33 40), --deck 301; bare --check covers 18
  build-notes.md        # gains deck-301.js and the identity proof for 101 and 201
  png/                  # gains 33 and 40
  design-patterns-with-python-101-patterns-and-solid.pptx   # not rebuilt
  design-patterns-with-python-201-idiomatic-python.pptx     # not rebuilt
  design-patterns-with-python-301-testing-legacy-and-ai.pptx  # new
```

Build, from `<repo>/presentation`: `npm ci`; `./render-png.sh --deck 301`; `node deck-301.js`. The builder sets the metadata: title "Design Patterns with Python: 301, Testing, legacy code and AI", subject "Companion deck to Design Patterns with Python", author, company and lastModifiedBy "PatternCatalyst". It writes the cover in the 201 layout with the subtitle "301: Testing, legacy code and AI", and every slide through the `deck-lib.js` helpers with notes as plain strings. `finish()` asserts the floors and the notes count.

## QA pipeline (D4a, D4b, D5)

1. `npm ci` in `presentation/`; `node -e "console.log(require.resolve('pptxgenjs'))"` shows the local copy (recorded scrubbed); `npm audit` 0.
2. `./render-png.sh --check` prints `same` for all eighteen PNGs.
3. `node deck-301.js` prints 42 slides. The identity proof runs for both earlier decks: `node deck-101.js` and `node deck-201.js`, unzip each against `git show HEAD:<deck>`, `diff -rq` shows only `docProps/core.xml`, then `git checkout` restores both committed files.
4. `soffice -env:UserInstallation=file://<scratchpad>/lo-qa --headless --convert-to pdf --outdir presentation/qa <deck>.pptx`. Afterwards `pgrep -x soffice.bin` prints nothing.
5. `pdffonts`: Overpass, Red Hat Text and Red Hat Mono embedded; no other text family except OpenSymbol.
6. `pdftoppm -jpeg -r 110`: one image per slide, 42 in all.
7. `python3 presentation/notes.py <deck>` and `--slides` into `presentation/qa/deck-301-notes.txt` and `deck-301-slides.txt`.
8. **Pointer grep, before validation.** A case-insensitive grep over both text files and `deck-301.js`'s strings for `follow`, `next`, `previous`, `earlier`, `later`, `before it`, `after it`, `above`, `below`, `closing slide`, `last slide`, `close the section`, `section that`, `the dividers`, `where they`, `the book`, `this book`, `book's`, `chapter`, `appendix`, `member`, `slide [0-9]`, `this deck`, `these slides`, `dissolv`, `surviv`, `disambiguat`, `written for the book`, `\.md`, `\bP[0-9]+\b`, `\bF[12]\b`, `\bD[0-6]`, `census`. Each hit is recorded in the QA file as allowed (a test identifier or a non-positional use, quoted) or fixed. Only the closing slide may name the site and repository. Then the case-sensitive `Java|C#|C\+\+|\.NET|Rust|\bGo\b`, and an AI-claim grep (`often|usually|most |typically|tend|assistants? (may|might|will)|productiv|accura`), each hit justified against decision 8 or fixed.
9. `scan.sh --tier ban --fail` on `deck-301.js` and both text files, then `--stats` on the notes and the house-voice rubric applied by reading.
10. `uv run python scripts/validate.py` (runs `check_decks` over all three decks), `--self-test`, `--claims`; `scripts/verify.sh`; `python3 scripts/host_ids.py check`.
11. `unzip -p <deck> docProps/core.xml docProps/app.xml` is shown in the QA record.
12. **Eyeballing.**
    - At D4a the executor views every page image once and fixes what it sees.
    - At D5 two Opus validators view the images independently, one per half: slides 1 to 21 and slides 22 to 42. They run as separate agents, and neither sees the other's findings before reporting. Each gets the code and the rendered pages, not this plan's conclusions.
    - Checklist: logo and page number placed; no text overflow or clipped code; the code box fits the listing; the caption under the box on one line; figure text legible and the frame matching the PNG aspect (XML `a:ext` ratio against the PNG to three decimals); table cells not wrapping mid-word; divider titles on at most two lines; notes present and over the floor; no pointer or positional phrase (from step 8).
    - Findings go to the QA record with the page number.
13. A rebuild changes only `docProps/core.xml`; the committed deck is the last build after the final repair, and a no-change rebuild is reverted rather than committed.
14. **Confirmation after any orchestrator-applied repair.** When the orchestrator applies a repair (any edit after a D5 round reports), a fresh Opus validator that did not run that round re-runs steps 2 to 11 on the repaired tree, views every page whose slide text changed, re-reads every changed note against step 8 and the census, and runs the self-tests with any new check disabled to show they fail. Its verdict is appended to `_plans/evidence/r24-deck-qa.md` as "Confirmation after repair round N" before any row closes or D5 is marked done. A repair that touches Deck 101 or 201 re-runs step 3 and that deck's step 8 grep as well.

## Evidence files

- `_plans/evidence/r24-deck-witness-census.md` (D1b), after D1c. Per slide it records:
  - the doc's exact title and the cited sentence with `NN.md:line`, re-found by `grep -nF` hitting one line;
  - each test with file, line and a definition count of 1;
  - each code range with its anchor, line count, longest line, and the fence it is a contiguous run of;
  - the table cells for slides 5, 12, 35, 40 and 41 with their `grep -F` result;
  - each recorded experiment the notes quote, re-run in a scratch copy, with counts and failing test names (no timings);
  - the credits per slide;
  - the figure census re-run after D1c, with legibility;
  - the boundary check against both earlier decks' extracted text;
  - one forward run and one reverse run of every witness test in a fresh scratch copy.
- `_plans/evidence/r24-deck-qa.md` (D4a, appended at D4b and D5). It holds the pipeline commands and outputs (scrubbed with `host_ids.py filter`), `pdffonts` and `docProps`, the notes word-count table, the step 8 greps, the scan results, the eyeballing findings per page with their fixes, each D5 round's verdict, each repair round, and each confirmation (step 14).

## Steps and status

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| D0 | Bookkeeping with dated notes: `iteration-plan.md` closes r23 (PDP-151 `done`), marks PDP-152 and r24 `active` (K1); the r23 plan's Z6 `done` and its confirmation note (K2); re-check every pin; record the owner's decisions; `verify.sh` and `validate.py` green | - | done |
| D1a | `render-png.sh` figs_301 and `--deck 301`, `build-notes.md` (K3); V1 in `check_decks()` with a self-test that fails without it; the identity proof for 101 and 201; the two PNGs after D1c's figure fixes | D0, D1c for the PNGs | done |
| D1b | `_plans/evidence/r24-deck-witness-census.md`, after D1c, so lines, anchors, counts and the figure census are taken from the fixed tree | D1c | done |
| D1c | Decision 5's book fixes P1 to P21, F1 and F2, each with its example's tests, `verify.sh` and `validate.py` green and every recurrence grepped; quoted runs re-captured where counts moved (P4, P5); figures regenerated through `diagrams/specs`; `site-build.sh` green | D0 | done |
| D2 | Rows 399 to 429 into `_plans/reconciliation-plan.md` with a dated note; every quote, line or test that differs from this plan goes in Corrections; a failed witness cuts the slide | D1b | done |
| D3 | `deck-301.js` (Sonnet executor) from the inventory, the census and the standalone wording, notes to the settled voice rules and decisions 7 and 8 | D1a, D2 | done |
| D4a | QA pipeline steps 1 to 12 (executor view of every page); `_plans/evidence/r24-deck-qa.md`; README "Companion decks" entry | D3 | done |
| D4b | Voice pass on `deck-301.js` and the extracted text: ban tier, `--stats`, the house-voice rubric, the step 8 greps; rebuild and re-run steps 3 to 10 | D4a | done |
| D5 | Opus validation: two independent page viewers (step 12); every witness row checked and at least one in three re-run; the excerpt check against each source; `validate.py --claims`; the boundary check against both earlier decks; rows 430 to 436 added and closed; up to two repair rounds, each followed by the confirmation pass (step 14) | D4b | done |
| D6 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r24.x` on main; notes-only release | D5 | todo |

## Reconciliation rows

Rows 399 to 429 go in at D2, after the census exists (so its `run:` path resolves) and with only test names the census confirmed. Rows 430 to 436 cite `run: D4a`, `run: D4b` and the QA file, and go in at D5 after those steps are `done`. The Ch cell is the source doc's number, so `chapter_numbers` parses it. Rows whose claim begins "Deck:" start `open`, and D5 closes them; fix rows close at D1c or D1a.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 399 | 11 | Deck: a test named as a claim asserts the returned reference before the calls | `test_book_best_books_only_the_winner`, `test_book_best_books_the_winner_and_returns_its_reference` |
| 400 | 11 | Deck: each kind of double refuses something different | `test_a_fake_rejects_unknown_names_and_wrong_signatures`, `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method`, `test_spec_rejects_unknown_names_but_not_wrong_signatures` |
| 401 | 11 | Deck: only autospec copies signatures, and mypy accepts every mock | `test_autospec_rejects_names_and_signatures`, `test_mypy_accepts_every_mock_where_a_gateway_is_expected` |
| 402 | 11 | Deck: an injected clock and environment leave nothing to patch | `test_quote_validity_comes_from_the_injected_clock`, `test_validity_reads_the_environment_and_the_context_restores_it` |
| 403 | 42 | Deck: four settings refuse what pytest's defaults let through | `test_an_unregistered_marker_fails_collection_under_strict_markers`, `test_a_passing_xfail_fails_the_run_under_strict_xfail`, `test_filterwarnings_error_turns_a_warning_into_a_failure` |
| 404 | 42 | Deck: same-basename test files collide under prepend and not under importlib | `test_same_basename_test_files_collide_under_prepend`, `test_importlib_mode_gives_each_test_file_a_unique_name` |
| 405 | 43 | Deck: assert_has_calls checks a contiguous ordered run | `test_assert_has_calls_checks_a_contiguous_ordered_run`, `test_mock_calls_records_calls_in_order_with_call_objects` |
| 406 | 44 | Deck: stub and spy mean different things in the two vocabularies | `test_stub_records_a_callback`, `test_spy_keeps_the_real_behaviour_and_records_returns` |
| 407 | 33 | Deck: the inherited engine calls the real carrier | `test_the_legacy_engine_calls_the_real_carrier` |
| 408 | 33 | Deck: a patch goes where the name is looked up | `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`, `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier` |
| 409 | 33 | Deck: a captured default and a reload both defeat a patch | `test_patching_a_module_constant_misses_a_default_captured_at_definition`, `test_reload_discards_a_patch_and_keeps_old_bindings` |
| 410 | 33 | Deck: mypy checks a parameter seam and not a monkeypatched replacement | `test_mypy_does_not_check_a_monkeypatched_replacement`, `test_mypy_checks_a_fake_passed_to_a_protocol_parameter` |
| 411 | 34 | Deck: a characterisation table pins behaviour at every step | `test_every_step_matches_the_characterisation_table`, `test_the_table_catches_a_step_that_changes_behaviour` |
| 412 | 34 | Deck: carriers as parameters, with real defaults a forgotten fake reaches | `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`, `test_mypy_checks_a_fake_passed_as_a_constructor_argument` |
| 413 | 34 | Deck: the function form needs its quoters | `test_the_function_form_needs_its_quoters`, `test_mypy_reports_a_missing_quoters_argument` |
| 414 | 34 | Deck: a misspelt override reaches the real carrier unless marked override | `test_a_misspelt_override_falls_through_to_the_real_carrier`, `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator` |
| 415 | 35 | Deck: intent rows pass a refactor that golden quotes catch | `test_the_intent_rows_pass_every_engine_and_both_rounding_refactors`, `test_the_golden_quotes_catch_a_refactor_that_changes_rounding` |
| 416 | 35 | Deck: golden quotes pin the refactored engine; round rounds half to even | `test_the_refactored_engine_matches_the_golden_quotes`, `test_round_with_two_digits_rounds_half_to_even_in_the_default_context` |
| 417 | 36 | Deck: a first draft with exclusive limits fails parity at the boundaries | `test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries`, `test_band_limits_include_the_boundary_weight` |
| 418 | 36 | Deck: the rewrite differs from the legacy engine only where accepted | `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted`, `test_the_legacy_engine_prices_an_unknown_zone_as_eu` |
| 419 | 36 | Deck: a router serves migrated zones and shadows the rest | `test_the_router_serves_migrated_zones_from_the_rewrite`, `test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote` |
| 420 | 39 | Deck: the acceptance test names the stage that is missing | `test_a_booking_request_ships_end_to_end`, `test_the_acceptance_test_fails_when_a_stage_is_left_out` |
| 421 | 39 | Deck: a refusal undoes the completed steps newest first | `test_the_undo_runs_in_reverse_order_of_the_steps`, `test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking` |
| 422 | 39 | Deck: tracking is published after the commit | `test_a_held_booking_publishes_no_tracking_event`, `test_an_eager_publisher_reports_a_booking_that_was_rolled_back` |
| 423 | 39 | Deck: the composition root chooses the pricing rule and the carrier | `test_the_pricing_rule_is_chosen_at_the_composition_root`, `test_mypy_refuses_a_gateway_without_cancel` |
| 424 | 40 | Deck: each draft fails exactly its gates, and only the idiomatic module passes all three | `test_each_draft_fails_exactly_the_gates_in_the_table`, `test_the_idiomatic_module_passes_every_gate` |
| 425 | 40 | Deck: a rejected reply goes back with its findings, against a recorded fake | `test_a_rejected_reply_is_sent_back_with_its_findings`, `test_an_unrecorded_prompt_is_refused` |
| 426 | 11-44 | Deck: the doubles, vocabulary, gate, sources and books tables match the docs | run: _plans/evidence/r24-deck-witness-census.md |
| 427 | 11-44 | Book fixes P1 to P21: the deletions sentence, the negative case, the substrings sentence, experiment six's block, the teardown witness, the anchored matches, the subdirectory-table witness, the cards, the Dummy and Hard-Coded rows, the tightened message tests, the refactoring count, the README sentences, the network and rule-selection sentences, the example-directory lines, the pytest-mock links | run: D1c |
| 428 | 33-40 | Figure fixes F1 and F2 regenerated from their specs; figures 33 and 40 pass the arrow census | run: D1c |
| 429 | 11-44 | check_decks refuses "this book" outside the closing slide, with a self-test that fails without the check | run: D1a |
| 430 | 11-44 | Deck: every code slide is byte-exact with its source range | run: D4a |
| 431 | 11-44 | Deck: 42 slides, 42 notes slides, every notes slide over its floor | run: D4a |
| 432 | 11-44 | Deck: Red Hat Text, Red Hat Mono and Overpass embedded in the render | run: _plans/evidence/r24-deck-qa.md |
| 433 | 11-44 | Deck: metadata PatternCatalyst, no host identifier or runtime name in any part | run: D4a |
| 434 | 11-44 | Deck: ban-tier scan, pointer grep and AI-claim grep clean on the builder, slide text and notes | run: D4b |
| 435 | 11-44 | Deck: committed PNGs equal a fresh render, and Decks 101 and 201 rebuild unchanged from the shared module | run: _plans/evidence/r24-deck-qa.md |
| 436 | 11-44 | Deck: every rendered page viewed and passed by two independent viewers, and every repair confirmed | run: _plans/evidence/r24-deck-qa.md |

## Acceptance criteria

1. `presentation/design-patterns-with-python-301-testing-legacy-and-ai.pptx` is committed and builds with `npm ci && node deck-301.js` from the committed lockfile. `package.json` is unchanged (pptxgenjs exactly 4.0.1) and `npm audit` reports 0.
2. Nothing is installed globally, and `require.resolve('pptxgenjs')` points under `presentation/node_modules`.
3. `deck-helpers.js` and `deck-lib.js` are unchanged (the md5s in decision 3), or, if D3 needed a `deck-lib.js` change, the identity proof for both earlier decks is recorded after it. A fresh `node deck-101.js` and `node deck-201.js` each give a deck whose unzipped parts equal the committed one's except `docProps/core.xml`. The committed 101 and 201 files change in this iteration only under the fix-now rule (a defect a validator or check finds in them), each such change recorded in Corrections with the slides and notes it touched, and each changed deck rebuilt, re-grepped and re-viewed on the changed pages.
4. There are 42 slides (or the Corrections count after a witnessed cut), equal to the notes-slide count. Every notes slide meets its floor (90 words content, 45 cover and dividers), and every divider keeps the `AB0000` fill.
5. Every content slide's claim traces to a doc sentence or a test in the census. Every cited test is defined once, and no slide is without a witness. No 301 slide reuses a test name, code range or claim of Deck 101 or Deck 201 (section "Boundary with Decks 101 and 201").
6. Every code slide is read from source by path and range with its anchor asserted, from a contiguous run of a chapter fence. Each slide draws on one doc's definitions.
7. Every figure in the deck passes the arrow census and the 6.3 pt floor, its frame matches the PNG aspect, and the committed PNGs equal a fresh render.
8. Slide text and notes contain:
   - no em or en dash, `PDP-`, `rNN`, "spike", "capstone" or cross-language word;
   - no chapter, appendix, book or slide pointer, no positional phrase, no "this deck" or "these slides", no three-way-split label (`check_decks` and the QA step 8 grep);
   - no timing anywhere, and run results in notes only as decision 7 allows;
   - no claim about what assistants or models do beyond decision 8.

   The ban-tier scan is clean on `deck-301.js` and the extracted text.
9. `docProps` creator, lastModifiedBy and company are "PatternCatalyst"; every part passes `host_ids.py filter` unchanged; no runtime name appears in any part; `host_ids.py check` is clean on the tree.
10. `pdffonts` shows Overpass, Red Hat Text and Red Hat Mono embedded. Every rendered page has been viewed by the executor and by one of two independent Opus viewers, with findings closed, and every orchestrator-applied repair has a recorded confirmation (QA step 14).
11. Sources are credited on the two reference slides and in the notes of each slide that uses one. No text is copied beyond the docs' own attributed quotes.
12. Decision 5's fixes are merged with their examples' tests green and every recurrence fixed; rows 427 to 429 are closed; `iteration-plan.md` and the r23 plan carry no stale status.
13. README "Companion decks" lists 301; `LICENSE-docs.md` is unchanged.
14. `scripts/verify.sh`, `scripts/validate.py` (with `--self-test` and `--claims`), `scripts/site-build.sh` and the repo-wide voice gate are green; CI `ci-ok` is green.
15. Rows 399 to 436 are closed; no `soffice.bin` or `node` process is left running; scratch trees are deleted.

## Risks

- **Pointer phrases in notes.** The commonest blocking finding in r22 and r23. Mitigation: the standalone wording in the executor brief, V1, the step 8 grep before validation, two independent viewers.
- **Repairs that add defects.** r23's round 2 found slips from repair 1. Mitigation: QA step 14, a confirmation by a fresh validator after any orchestrator-applied repair, with self-tests run against a disabled check.
- **Repeating Deck 101 or 201.** The composition root, prompting, ExitStack and the misuse claims sit close. Mitigation: the boundary table, the D5 boundary check against both decks' extracted text.
- **Claims about AI tools.** A note could slide into "assistants often...". Mitigation: decision 8, the AI-claim grep, the drafts described as hand-written stand-ins.
- **Name collisions.** Six `RateEngine`s, two `rating.quote`s, three `CarrierGateway`s. Mitigation: one doc per slide; the notes name the concept (standalone wording).
- **Fixes moving lines and counts.** P5 moves every count in chapter 11's quoted runs; P1 to P4, P10 and P16 to P18 move sentences. Mitigation: D1b runs after D1c; anchors fail the build loudly; quoted runs are re-captured at D1c and re-run at D1b.
- **Figure 33 at 6.4 pt.** The smallest label of any deck figure. Mitigation: full-width slide, the QA drop rule; decision 4's alternative has the bullet slide ready.
- **Scope of D1c.** 21 small prose and test fixes and two figures across ten docs plus 39 cards. Mitigation: each is a small edit with its example's tests and `validate.py` re-run; P20 is one grep-checked rewording.
- **Line lengths.** Three ranges exceed 95 characters. Mitigation: per-call font size; evidence F and G show 13.5 pt fits.
- **Orphaned processes.** `pgrep -f soffice` matches itself. Mitigation: `pgrep -x soffice.bin`.

## Corrections after the build
- Step D5 round 2: the Opus confirmation of round 1 failed on one new claim (slide 33's notes gave the subscriber as a desk parameter) plus page 9's orphan word and two record errors. Repair round 2, the last, applied its tested strings verbatim; see `_plans/evidence/r24-deck-qa.md`. D5 is done with row 436 verified. Acceptance criterion 5 is met after round 2; criteria 8 and 12 are met after rounds 1 and 2.
- Step D5 round 1: 21 blocking, should-fix and nit repairs are applied to `presentation/deck-301.js`, with the matching book fixes (Appendix B strict-config sentence, the README lines of the Fowler-versus-Feathers and refactor-or-rewrite examples, figure 40's walk-through) and the figure specs for 33 and 40 regenerated (label sizes 9.3 and 9.6 pt on the slide). Rows 399 to 435 of `_plans/reconciliation-plan.md` are verified (r24); row 436 stays open until the confirmation pass. D5 stays `todo`. Evidence is in `_plans/evidence/r24-deck-qa.md`.
- Step D3: `presentation/deck-301.js` builds the 42-slide deck through `deck-lib.js` unchanged (42 notes slides, every floor met). Deviations from the inventory: slide 11 is titled "Ordered call records" (the plan's "Calls recorded in order" holds the banned phrase "in order"); the other titles that were claims or imperatives are noun phrases ("Doubles and refusals", "Autospec and signatures", "The patch target", "Patches and mypy", "A stack of inverses", "Events after the commit"); `test_every_draft_says_it_was_written_for_the_book` is not named on any slide; the sources table groups the 30 sources into 10 rows and its notes name each one.
- Step D4b: voice pass on `presentation/deck-301.js` and the extracted text, 22 edits (22 sentences rewritten; two accuracy fixes: the Feathers seam wording now follows the chapter, and slide 18 lists all five forms). The slide-text sentence-length p90 of 270 is an extraction artefact of joined code lines. Greps, `--stats` before and after and the pages viewed (6, 20, 22, 24, 25, 31) are in `_plans/evidence/r24-deck-qa.md`.
- Step D4a: `_plans/evidence/r24-deck-qa.md` records the render, fonts, docProps, word counts, the three greps, the scans, the pages viewed (fixes on pages 5 and 41) and the identity proof for Decks 101 and 201. README "Companion decks" lists 301.
- Step D2: rows 399 to 429 are in `_plans/reconciliation-plan.md`, all `open`, with resolving tokens: the `test_` names the census confirmed, `source:` URLs that appear in the row's own chapter file (rows 400 and 401, 403 to 406, 408, 409, 412, 413, 415 to 419, 421 and 424) and the `run:` tokens `D1a`, `D1c` and the census path. Two rows differ from the plan's text. Row 427 says "the narrowed teardown sentences" where the plan said "the teardown witness", because owner decision O2 added no pytester witness. Row 402 keeps the clock test and the environment test, which are the witnesses of slide 7 after its narrowing. Row 285 ("stub as a dummy") was re-read against Appendix D's qualified Dummy paragraph and was wider than the text: `book_cheapest` calls the stub with the booking reference and only the test never reads it. It now says the dummy use holds only in the qualified sense, and its status reads "verified (r21); amended (r24)". A dated note closes the file. `validate.py --claims` reports every row from 47 on resolved.
- Step D1b: `_plans/evidence/r24-deck-witness-census.md` is written from the tree at 4b7ee31. 41 of the 42 slides are kept, one is narrowed and none is cut; the deviations from the inventory below override it for D3.
  - Slide 7: the plan's range `tests/test_engine.py:68-80` (the clock test) is no run of any chapter fence. The slide shows `tests/test_environment.py:8-20` (13 lines, longest 68, a whole fence at `11.md:163-177`), is titled "Clock and environment" instead of "An injected clock", and keeps the clock, code-order and tie-break tests as witnesses. Its teardown note rests on experiment three alone (O2).
  - Tests: 91 distinct names, each defined once at column 0, not the plan's 90. `test_quote_log_teardown_runs_when_the_test_fails` is dropped (O2; it does not exist). `test_a_member_table_replaces_the_root_filter_and_names_its_own_file` (slide 9 notes) and `test_resetall_resets_patches_spies_and_autospecs_but_not_stubs` (slide 11 notes) are added. Fresh-copy runs: 155 cases pass in three forward runs and one reverse run.
  - Slide 12 is a two-row table (Stub, Spy); the qualified Dummy Object paragraph is a note. Slides 17, 25, 33, 36 and 37 may quote what P11, P12, P15, P16 and P17 now assert, and nothing wider.
  - Code: all 18 ranges are contiguous runs of a chapter fence and byte-exact with it; the longest lines are 98 (slide 4, 13.5 pt), 97 (slide 21, 14 pt) and 96 (slide 33, 14 pt).
  - Figures: 33 (6.43 pt smallest label, three edges) and 40 (7.84 pt, seven edges) pass the arrow census after F1 and F2; `render-png.sh --check` prints `same` for all 18 figures in the copy.
  - Experiments: the twelve a note may quote were re-run and every count equals the chapter's; counts are recorded without a duration. Credits: 30 sources and six books; of 78 URLs checked with `curl -sI`, 76 answer 200 and the two bibliography links for Effective Python and Architecture Patterns with Python answer 301 to the same book's canonical address (recorded for r25).
  - Boundary: test names, code ranges and claim phrases all read 0 against both earlier decks' extracted text and builders; the near terms (composition root, Percival and Gregory, ExitStack, the run-an-example closing sentence) are listed with their angles.
- Step D1a (part 2): the orchestrator rendered `png/33-seams-in-python.png` (1600x957) and `png/40-working-with-ai-and-llm-tools.png` (1600x833) from the D1c SVGs and viewed both. Figure 33 now shows the two dashed boxes as unconnected notes, and each figure 40 gate box lists what that gate reports. `render-png.sh --check` prints `same` for all 18 figures.
- Step D1a (part 1): `render-png.sh` gains `figs_301=(33 40)` and `--deck 301` (the default list is now 18 figures). `build-notes.md` covers Deck 301 and the identity proof for both earlier decks (101: 342 parts; 201: 255 parts; only the `core.xml` timestamps differ). V1: `DECK_BOOK_RE` is now `\b(the|this) book('s)?\b`, with an "as this book says" self-test; reverting the regex makes `--self-test` fail. Commit 9e5c08c. The two 301 PNGs follow D1c.
- Step D1c: P1 to P21, F1 and F2 are applied (6a9b430).
  - P5 follows O2: six sentences, plus the conftest docstring, now cite only experiment three, and chapter 11's counts are unchanged.
  - P7 adds `test_a_member_table_replaces_the_root_filter_and_names_its_own_file`, so example 42 is now 39 functions and 44 cases.
  - P16 moves chapter 40's quoted `tests/test_gates.py:109` to `:114`, re-run.
  - P10 qualifies the Dummy row in Appendix D. Reconciliation row 285 ("stub as a dummy") must be re-read at D2.
  - P20 also fixed `43.md:273`.
  - P4's quoted block keeps the timing that pytest prints, as every chapter's quoted runs do. The decks carry no timing.
  - The orchestrator re-ran the gates at 6a9b430: `validate.py` reports 0 errors and `verify.sh` passes.

- Step D0: K1 and K2 are applied in `_plans/iteration-plan.md` and `_plans/r23-plan.md`. Every pin was re-checked on 2026-11-07 against upstream and is unchanged: pptxgenjs 4.0.1 (`dist-tags.latest`; `beta` 4.0.1-beta.2 not used), image-size 2.1.0, cairosvg 2.9.1, CPython 3.15.2 (endoflife.date cycle 3.15), uv 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4. No pin row changed, so `r01-build-plan.md` is untouched.

## Hand-off to r25 (retro and QA sweep)

- **Three-deck consistency.** Compare the three decks' route slides, divider subtitle style, closing slides and reference tables; record any drift for one pass, without re-opening a settled rule.
- **`check_decks()` coverage.** Bare "next", "earlier", "later", "follows" and the three-way-split labels are caught only by the QA grep. Decide whether a per-deck rule (301 and 201 ban the labels; 101 teaches them) belongs in the validator.
- **The sidebar form.** If the owner keeps decision 8's recommendation, CLAUDE.md's "Not a description of what an assistant gets wrong" and the 20 "An assistant may ..." openings still disagree; r25 settles the wording of one or the other.
- **Validation records.** Check that every iteration's validation rounds and confirmations are recorded in the repo, not only in the PRD build log (K2 is the r23 case).
- **Figures out of every deck.** List figures excluded by legibility (26 to 30, 32, 35, 36, 39) and by the census, and decide whether any is worth a spec change for the book's own sake; no deck depends on it.
- **Link drift.** A repo-wide pass for `/3/` and `/latest/` documentation links (r23 P10, r24 P21).
- **Cards.** After P20, a repo-wide reading of the 47 cards against their READMEs.
