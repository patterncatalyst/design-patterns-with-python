---
title: "r25 plan: retro and QA sweep"
order: 25
output: false
render_with_liquid: false
---

# r25: retro and QA sweep

Opus-planned 2026-11-08. Branch `release/r25`, cut from main at e32dea5 (the r24 merge, tagged `r24.x`). This file is the source of truth for r25 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

r25 is the last roadmap iteration. The book is complete: 47 docs (chapters 0 to 40 and Appendices A to F), 41 example members with 41 cards (chapters 1, 2 and 4 are argument chapters and Appendices A, D and E have no member; the brief's "47 example members" is the doc count), 41 figures, three companion decks and one spike member. No new chapter, example or deck is written. r25 reads the whole book against its rules, fixes what it finds in this iteration (the fix-now rule), settles the questions earlier iterations handed to it, and ends with the final release.

Work item: r25 has no PDP id. C0 adds PDP-021 ("Retro and QA sweep", r25) to the infrastructure range of `_plans/iteration-plan.md`.

Pins this iteration (re-checked 2026-11-08, evidence P): CPython 3.15.2 (endoflife.date cycle 3.15), uv and uv-build 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1, ruff 0.17.4, cairosvg 2.9.1 (PyPI latest); pptxgenjs 4.0.1 (`dist-tags.latest`), image-size 2.1.0; Node v22.22.2 and npm 10.9.7 (host); actions/checkout 7.0.1, configure-pages 6.0.0, deploy-pages 5.0.1, upload-pages-artifact 5.0.0, setup-uv 10.3.3, ruby/setup-ruby 1.338.0 behind `@v1`; ruby:4.0.9; Jekyll 4.4.1 and its plugins. Every pin is still the latest stable. Two transitive gems lag within their constraints (sass-embedded 1.106.1 against 1.108.1, addressable 2.9.0 against 2.9.2; decision 11).

Lessons carried from r16 to r24: grep everywhere, including front matter, cards, READMEs, docstrings, captions and the appendices; the run wins over the plan; recount after every edit; status tokens are plain `done`; paths in plans and evidence are repo-relative, with `<repo>` and `<scratchpad>` for anything outside; only suffixed step ids are cited as `run:` tokens. From r23 and r24 validation: every orchestrator-applied repair introduced at least one new overclaim or slip that the next round caught (r23: a wrong section count and self-tests that couldn't fail; r24: slide 33's subscriber), so a confirmation pass after every repair is mandatory here, its tested replacement strings are applied verbatim with an exact-match assert, and each round is recorded in the repo (evidence K).

## Settled rules (owner, carried from r10b to r24; not re-asked)

- **Fix now.** A defect in the book is fixed in this iteration with every recurrence grepped (front matter, cards, READMEs, docstrings, captions, `_data/diagrams.yml`, `_docs/41` to `46`, the decks). Nothing that belongs to the book is deferred; there is no later iteration to defer to.
- **Chapters stand alone.** No chapter-number cross-reference, no "as we saw", no cross-language comparison, no internal code (PDP-, rNN, spike, step or defect id) in reader-facing files, "final project" never "capstone", Arabic part numbers.
- **Every claim tested.** A sentence that states behaviour names a test, a recorded run or a fetched source. Quoted output matches a fresh run modulo timings and `<repo>`. Mutation sentences that state their own edit are re-runnable from the sentence and stay (r24 evidence O).
- **The decks stand alone** (r22 O4 and the r24 settled rules). A deck change keeps them: no chapter, book or slide pointer, no "this deck", no three-way-split label in 201 or 301, no timing, no claim about what assistants do. The committed decks rebuild identically apart from `docProps/core.xml` when their builder doesn't change.
- **Figures.** Specs in `diagrams/specs/` are the source of truth; never hand-edit an SVG; a changed figure's walk-through paragraph, include caption and registry caption are brought into line in the same commit.
- **Voice.** lgtm-professional-voice is a gate: 0 ban-tier, `--stats` reviewed, the house-voice rubric applied by reading. No em or en dashes anywhere, plans included.
- **Comparison code** is allowed as the exception when it teaches, tested on the same table (owner, 2026-11-04).
- **Word counts.** The 2,500 ceiling is an error; the 1,900 floor is a warning; length serves the reader, never pad and never cut a fact to fit (owner, 2026-11-05).
- **Release.** One PR, squash-merge after the owner says so, tag `rNN.x` on main, notes-only release (CLAUDE.md).

## Owner decisions

2026-11-08, at the plan gate:

- O1: every numbered decision is taken as recommended (0 to 13), with one exception. **Purely stylistic prose edits are dropped from r25**, because the terse rewording in r26 to r28 will rewrite that prose. Dropped: VO1 (the 33 "Build, run, observe" lead sentences), VO2 (the appendix closes), and any VO3 to VO9 item that changes only wording, not a fact. Correctness fixes stay: wrong claims, counts, links and names, the 18 sidebar openings (SB1 to SB18, decision 1), and every CD, LK, QO, TS, FG, DK, SC, VA and BK item.
- O2: the owner approved a terse rewording of the whole book, to run after r25 as r26 (gates, tooling and a pilot on docs 01, 03, 23 and 24, which the owner reads before r27 starts), r27 and r28. The rules go into `lgtm-professional-voice` as a "terse pattern register" through a lgtm-skills PR. Two settled rules change from r26 on:
  - tests are named on a `*Tests:*` line after the paragraph, not inside the sentence;
  - the 1,900-word floor is dropped.

  Because r26 to r28 follow, decision 10 changes. The r25.x release is titled "r25.x: Retro and QA sweep" and does **not** declare the book complete. The README "Status" section and the PRD say the terse rewording is in progress. C0 adds r26 to r28 to the iteration plan's roadmap.

## Decisions with recommendations

0. **Step ids and defect ids.** The steps are C0 to C7. At planning, `grep -rnE '(run: |^\| )C[0-9]' _plans/` prints nothing (evidence A). Only suffixed ids are cited as `run:` tokens: `C1a`, `C1b`, `C2a` to `C2g`, `C3a`, `C3b`, `C4a`, `C5a`. Plain C0, C6 and C7 appear only in this plan's table. One recorded file is cited as a `run:` path: `_plans/evidence/r25-qa-sweep.md`.

   Defect ids are two capital letters and a number, by kind: BK (bookkeeping), VA (validator and gates), LK (links), SB (AI sidebars), VO (voice and claims in prose), QO (quoted output), CD (cards and READMEs), TS (tests and docstrings), FG (figures and site legibility), DK (decks), SC (site chrome and README). No step prefix in any plan has two letters, so none can be read as a step id (the single letters A, D, G to N, P to Z are all step prefixes somewhere, R1a and R1b among them, evidence A). Validation findings are named "blocking item N of round M".

   **Recommend: yes.**

1. **The AI sidebar wording** (r24 O3 handed this to r25; evidence F). CLAUDE.md says a sidebar states the problem, gives a ready-to-paste prompt and at most one review line, and is "Not a description of what an assistant gets wrong". The census:
   - 36 sidebars, one in each of chapters 5 to 40.
   - 18 (chapters 5 to 22) open by describing what an assistant writes. Seventeen use "an assistant may" (chapters 7 and 8 as "An assistant writing dunders may ...", "An assistant writing a value type may ..."); chapter 21 says "'a composite' arrives as a `Component` base class with `add` on its leaves". The r24 plan counted 20 ("`11.md:228` and 19 pattern-chapter sidebars"); the grep gives 18, and the r24 figure goes in Corrections at C0 (BK3).
   - 18 (chapters 23 to 40) open by stating what the request leaves open, the form CLAUDE.md describes. Examples: chapter 33, "'Mock the carrier in this test' leaves the target open, and a patch on the module that defines a `from`-imported function changes nothing"; chapter 40, "'Write the pricing strategies' leaves the shape and the rounding open."
   - Examples of the first form: chapter 12 (`12.md:188`), "Asked for 'the Strategy pattern', an assistant may write an abstract `PricingStrategy`, a subclass per rule and a factory, or record `rule.__name__` on the quote."; chapter 11 (`11.md:228`), "An assistant may use a plain `Mock` for a typed collaborator, assert only that a method was called, patch a module global, or read the clock inside the code under test."; chapter 22 (`22.md:220`), "Asked for 'an event system', an assistant may write an `Observer` base class with `update`, a bus keyed by strings, ...".
   - "An assistant may write X" is a claim about what assistants do, which no test in the book witnesses, which the chapter 40 rules and the r24 deck decision 8 forbid elsewhere, and which `before-after.md` in lgtm-professional-voice lists as a "before" row almost word for word (the Template Method case). The prompts and the review lines are not in question; only the opening sentence and the bold lead-in are.

   Options:
   1. **Reword the 18 openings** to the request-leaves-open form used in chapters 23 to 40, and retitle the 18 bold lead-ins from "Reviewing assistant-written X" to "Specifying X" (or the chapter's noun). The prompt quote and the review line stay byte-identical. CLAUDE.md is unchanged. 18 sentence edits in 18 docs (SB1 to SB18).
   2. **Amend CLAUDE.md** to allow "an assistant may ..." as a hedged opening, and leave the sidebars. The book keeps two sidebar forms, and an untested claim about assistants in 18 chapters.
   3. Reword the opening sentence only and keep the "Reviewing ..." lead-ins.

   **Recommend: option 1.** It makes the 36 sidebars one form, matches CLAUDE.md and the deck rule, and removes 18 untested claims; the r10b approval was of the problem-prompt-review shape, which option 1 keeps.

2. **`check_decks()` coverage** (r24 hand-off; evidence G). Today `check_decks()` has no per-deck logic; it globs `presentation/*.pptx` and the only identity is the file path. Counts in the committed decks (whole words, so snake_case identifiers never match):

   | Deck | Positional words, slides | Positional words, notes | Three-way labels, slides | Three-way labels, notes |
   | --- | --- | --- | --- | --- |
   | 101 | 1 | 10 | 13 | 44 |
   | 201 | 0 | 0 | 0 | 0 |
   | 301 | 3 | 2 | 0 | 0 |

   The five 301 hits are ordinary uses, none positional: "for later verification" (slide 12, the Test Spy definition), "just above 5 and 50 kg" (slide 27 and its notes), "go back in the next prompt" (slide 36), "the next band's price" (notes 26). The decks also refer to themselves in ways the validator misses: 101 notes 2 "The deck runs in nine sections." and notes 3 "The code in the deck was held to a standard ..." (DK2).

   Options:
   1. **Labels and self-reference in the validator, bare positional words in the QA grep.** `check_deck` reads the deck number from the stable file name (`-(101|201|301)-`, r22 decision 2). For 201 and 301 it refuses "dissolve", "survive", "disambiguate" in any inflection, in slide text and notes (0 hits today). For every deck it refuses "the deck" outside the cover notes' opening sentence (two 101 hits, fixed by DK2). Bare "next", "earlier", "later", "follows", "above", "below" stay in the QA grep, because 5 of 5 hits in 301 are legitimate and an allow-list would be a list of phrases, not a rule. Self-tests use a synthetic deck named `x-201-y.pptx` and fail when the new check is disabled.
   2. Option 1 plus bare positional words for 201 and 301, with an allow-list of the five collocations.
   3. No validator change; the QA grep stays the only guard.

   **Recommend: option 1.**

3. **Cross-deck consistency** (evidence G). Drift found, deck by deck:
   - 101 is the odd one on: slide 2's title "The route" (201's voice pass renamed exactly this title as positional at r23; 201 now says "Eight themes"); `dc:title` "Design Patterns with Python: 101, Patterns and SOLID" against the cover "101: Patterns and SOLID in Python"; the two "the deck" notes (decision 2); cover notes without the re-run sentence 201 and 301 share; divider subtitles that list patterns instead of naming the section's idea; credits in prose with no "Credits:" label; the closing slide's "The book is at" (allowed there); the README entry's shape.
   - 301 is the odd one on: slide 2 "Seven themes" for eight sections, whose notes promise "versions" that no 301 slide shows; full author names in "Reading further"; sources table rows that put titles in the "Used for" column, and one merged "OWASP; mypy; Ruff" row; the run instruction split over two bullets; "What to show:" on the cover and dividers.
   - Shared: `presentation/build-notes.md` still says "the slide helpers that both builders use", "The deck builder overrides" and, in the identity proof, "Deck 301 has no committed predecessor to compare", which are now false.
   - Five PNGs (`13`, `14`, `16`, `22`, `23`) are committed and listed in `render-png.sh`'s `figs_101`, but no builder uses them; `build-notes.md` says "101: eleven figures" (DK5).

   Options:
   1. **Fix the substantive drifts and record the stylistic ones.** Fix: 101 slide 2's title (a 2 to 5 word noun phrase naming the sections, as 201's), 101's `dc:title` to match its cover, 101 notes 2 and 3 (DK2), 301 slide 2 (count the reference section, or retitle, and drop "versions" from its notes unless a slide gives them), `build-notes.md`, the README 101 entry to the 201/301 template, and the five unused PNGs removed from `figs_101` and `png/` (DK1 to DK6). Record as accepted variation, with reasons, in the QA evidence: divider subtitle style, credit table row shapes, author name forms, the "Credits:" label, the closing run instruction's split, and "What to show:" on dividers (each deck is internally consistent, and changing them re-opens three validated decks for no reader gain). Decks 101 and 301 are rebuilt and re-run through the r24 QA pipeline on the changed pages; Deck 201 is not rebuilt.
   2. Harmonise every listed drift in all three decks (a third pass over 149 slides and their notes).
   3. Record only.

   **Recommend: option 1.**

4. **Links** (evidence B, C). 212 distinct URLs in `_docs`, `_examples`, `bibliography.html`, the READMEs, `_parts`, the site pages, `_layouts`, `_includes`, `_config.yml`, `_data` and the deck builders were checked with `curl -sIL`. 202 answer 200 with no redirect. None is dead. The other 10 are eight redirects, the Liquid template and the site's `url:` value:
   - three bibliography links (Architecture Patterns with Python, Effective Python and Python Object-Oriented Programming, the brief named two) use O'Reilly's `/library/view/-/<isbn>/` form and 301 to the canonical slug; the hub's `_data/books.yml` uses the same three forms (lines 1008, 1017, 1044);
   - `https://docs.pytest.org/` and `https://mypy.readthedocs.io/` (`00.md:231-232`) 301 to `/en/stable/`;
   - `https://www.cosmicpython.com/book/preface.html` (`15.md:325`) 301 to `/book/preface`;
   - `https://github.com/patterncatalyst/design-patterns-with-python.git` (`00.md:61`) and `https://astral.sh/uv/install.sh` (`00.md:51`) redirect, but both are commands the reader runs, not links, and stay;
   - `https://github.com/{{ ...` is the Liquid footer and example-page template, which renders to the repository URL (200 on the built site), and `https://patterncatalyst.github.io` is `_config.yml`'s `url:` key, not a link.

   Every fragment (13 URLs with `#`) names an `id` present on the fetched page. `docs.python.org/3/builtins/stdtypes.html` is correct: 3.15 moved the page there, and `/3/library/stdtypes.html` now 301s to it.

   Link forms: 155 `docs.python.org/3/` occurrences in 40 docs (50 distinct URLs) and 62 `source:` tokens in `_plans/reconciliation-plan.md`; one `docs.python.org/3.15/` (What's New, r23 P10). `/3/` follows the newest release, so every verbatim quotation from a library page (the book quotes dozens, and `contextlib` already changed in 3.15) is one release away from no longer matching its link. All 50 `/3.15/` forms answer 200 with no redirect. `typing.python.org/en/latest/` (2 URLs, 4 uses) has no `stable` build (both `/en/stable/` forms 404) and stays. `pytest-mock` and `mypy` links already use `/en/stable/`. typeshed is cited at `blob/main` three times (`11.md:125`, `:391`, `43.md:285`) for a quoted comment.

   Options:
   1. **Pin the Python docs to the book's version and make every redirect final.** Rewrite `docs.python.org/3/` to `docs.python.org/3.15/` everywhere (docs, cards, READMEs, the 62 reconciliation `source:` tokens in the same commit so `--claims` still resolves), use the three canonical O'Reilly URLs in `bibliography.html` and the hub (a one-file hub PR, decision 12), the two `/en/stable/` roots in chapter 0 and the cosmicpython `/book/preface` URL; pin the three typeshed links to the commit whose `mock.pyi` holds the quoted comment (C1b fetches `main`, checks the quote, and uses that SHA). `validate.py` gains a link-form check: no `docs.python.org/3/`, no `/latest/` outside `typing.python.org`, no `oreilly.com/library/view/-/`, with a self-test (VA3).
   2. Option 1 without the `/3/` pin (fix the redirects only).
   3. Record only.

   **Recommend: option 1.**

5. **Figures and a site legibility floor** (r24 hand-off; evidence H). The decks admit a figure only if its smallest label is at least 6.3 pt in the 12.09 by 4.95 in slide box. r24 called 6.3 pt "Deck 101's smallest accepted figure", but Deck 101 shows figures 19 and 21 at 5.86 pt and 25 at 6.32 pt (measured from the SVGs and the committed slides' `a:ext`), so the floor was never Deck 101's minimum (BK4). Excluded from every deck: 00 to 04, 08, 11, 13 to 18, 20, 22 to 24, 26 to 30, 32, 34 to 36, 38 and 39 (24 figures; 13, 14, 16, 22 and 23 passed r22's census and were rendered but never placed).

   On the site the picture is worse. A chapter body is the 720 px prose column less its padding, so a figure's SVG renders about 622 CSS px wide. 27 of the 41 figures are wider than that and scale down, and their smallest labels render at 5.3 to 7.6 CSS px (figure 34 at 5.26, 25 at 5.47, 31 at 5.86, 36 at 5.90, 08 at 6.27). A headless screenshot of the built chapter 34 page at a 1280 px window (evidence H) shows figure 34's box labels and edge labels unreadable at page size. The cause is the column, not the specs: with the figure allowed to break out of the prose column to the 1080 px container (about 982 px of SVG), all 41 figures have smallest labels of at least 8 CSS px (the lowest is 34 at 8.3).

   Options:
   1. **A site floor of 8 CSS px, met by layout.** `.excalidraw-figure` breaks out of the prose column to the container width on viewports wide enough for it (CSS only, `assets/css/site.css`; no spec change), and the figure's SVG links to the full-size SVG in a new tab for narrower screens (`_includes/excalidraw.html`). `validate.py` gains a check that computes each SVG's smallest label at 982 px and fails under 8 px, with a self-test (VA4). No figure spec changes; no deck changes. The 6.3 pt slide rule stays as the r24 decks applied it; the record of Deck 101's minimum is corrected (BK4).
   2. Option 1 plus spec changes that raise the smallest label of the 24 excluded figures to deck legibility. No deck uses them, so this is work for a slide that doesn't exist.
   3. No floor; record only.

   **Recommend: option 1.**

6. **The 32 legacy reconciliation rows** (evidence J). `CLAIMS_FIRST_ENFORCED = 47` in `scripts/validate.py`; rows 1 to 46 are "legacy" unless they carry a token. 32 rows have none: 1 to 5, 17 to 27 and 31 to 46. Three are still `open`:
   - row 5 (chapter 20, runtime decorator objects against `@retry`/`@audited`) says "witnessed by rows 101-103 (r09)" and was never closed;
   - row 26 (chapter 14, a seeded probabilistic machine) has witnesses today: `test_a_seeded_transit_is_reproducible`, `test_a_shared_generator_gives_a_different_second_run`, `test_the_model_leaves_the_module_generator_alone`;
   - row 27 (chapter 9, "`Optional` plus mypy makes Null Object unnecessary in most cases") has witnesses (`test_mypy_requires_a_branch_for_absence`, `test_book_with_turns_absence_into_a_booking_error`, `test_no_discount_is_a_null_object_that_loses_nothing`), but "in most cases" is a scope word the chapter doesn't claim: chapter 9 says Null Object dissolves into an optional return and keeps it where doing nothing is the correct answer.

   Options:
   1. **Re-witness all 32 and enforce from row 1.** C4a gives each row the test names (or `run:`/`source:` tokens) that witness it today, runs exactly those tests in a fresh copy three times forward and once in reverse, closes 5 and 26 as `verified (r25)`, sets 27 to `adjusted (r25)` with the chapter's wording, and records any row whose claim no longer matches its chapter as `adjusted (r25)` with the reason. Then `CLAIMS_FIRST_ENFORCED` becomes 1 and the legacy branch and its self-test go (VA5); `--claims` reports every row resolved.
   2. Close only rows 5, 26 and 27; leave 29 rows legacy.
   3. Leave all 32.

   **Recommend: option 1.** The book's "every claim tested" rule has 32 unwitnessed rows on the record only because they predate tokens.

7. **The standing validate warnings** (evidence D). `validate.py` reports 0 errors and 6 warnings, all appendix word floors: 41 (1,595), 42 (1,703), 43 (1,880), 44 (1,824), 45 (917) and 46 (1,896). Each was accepted when its appendix shipped (r20 and r21), and CLAUDE.md says the floor is a warning that is never padded to. The recount after C2 may move them.

   **Recommend: confirm them as owner-accepted and record that in CLAUDE.md's dated notes; no padding.** Alternative: exempt appendices from the floor in `validate.py` (a rule change for six warnings that are already understood).

8. **The figure walk-through paragraphs and "the hub"** (evidence E). Two book-wide conventions the house-voice rubric flags:
   - 29 docs carry a "Read the figure from the top ..." paragraph that re-tells the figure box by box. lgtm-professional-voice's "Code callouts over re-narration" row says to trim such a paragraph to one concrete case plus a pointer. Every iteration since r02 required and validated these paragraphs, and the figure is an `<object>` whose only alternative text is the caption, so the paragraph is also the figure's text alternative.
   - 23 docs end "For deeper coverage" with an unlinked "the hub" ("It is in the hub's list", "and the hub carries the same list"). CLAUDE.md's spine asks for it ("citing the hub's `books.yml`"), and its Voice section bans cross-references to sibling sites inside chapters. The reader gets no link and no definition.

   Options:
   1. **Keep the walk-throughs and drop "the hub".** Walk-throughs stay as the figure's text alternative (CLAUDE.md records it as a convention); each "the hub" clause is removed so the sentence cites the bibliography page only, and CLAUDE.md's spine line becomes "citing this book's `/bibliography/`, kept in step with the hub's `books.yml`" (SB, VO and a CLAUDE.md edit).
   2. Drop "the hub" and trim all 29 walk-throughs to one case each.
   3. Link "the hub" to the hub site in all 23 docs and keep the walk-throughs.

   **Recommend: option 1.**

9. **Conditional Test Logic and the "test seam" wording** (r21 decision 13 handed these to r25; evidence L).
   - `examples/43-appendix-c-mocking/tests/test_patching.py:32`: an `if before is None` branch in the arrange phase of a parametrised test; one assert, one path through the verification.
   - `examples/35-fowler-vs-feathers/tests/test_golden.py:97`: the `--update-golden` branch writes the file and skips; it is the golden-master workflow chapter 35 teaches.
   - `examples/05-srp-ocp-lsp/tests/test_srp.py:43-61`: a `match` in the arrange phase and an `if replaced == "audit-sink":` in the verification, so two parameter rows check different assertions.
   - `stowage.py:18`, `37.md:78` and `examples/37-*/README.md:12` call `gap` "a test seam". `gap` is a parameter that takes a callable, which is an object seam in Feathers's sense; the word isn't wrong.

   **Recommend: fix the third (TS1): move the expected sink records into the parameter table so the verification has no branch; the test name, ids and chapter 5's quoted run don't change. Keep the first two and the "test seam" wording, with the reasons above recorded in the QA evidence.** Alternative: fix all three tests.

10. **The final release** (evidence M). The tag convention is `rNN.x`. The Java sibling closed with `r15.0` titled "Companion decks; book complete", and its README still says "Everything else in the table of contents is still to come", a stale status a final iteration should not leave. This repo's README has no status line.

    Options:
    1. **Tag `r25.x`**, release title "r25.x: Retro and QA sweep, book complete", notes-only. README gains a two-line "Status" section saying the book is complete (41 chapters, six appendices, 41 tested examples, 41 figures, three decks) and linking the releases page; no internal code in it. After the merge the orchestrator updates the PRD's status line and series line to complete.
    2. Also tag `v1.0` on the same commit. A second scheme no other iteration or sibling uses.
    3. `r25.x` with no README status.

    **Recommend: option 1.**

11. **Transitive gem bumps** (evidence P). `bundle outdated` in the `ruby:4.0.9` container: sass-embedded 1.106.1 to 1.108.1 and addressable 2.9.0 to 2.9.2 are allowed by their constraints; json 3, liquid 5, rouge 5, terminal-table 4 and unicode-display_width 3 are held by Jekyll 4.4.1's own constraints (an actual incompatibility, so they stay); wdm is Windows-only.

    **Recommend: bump the two at C0 with `bundle lock --update sass-embedded addressable` in the container, build the site, and record it in the build plan's dated table.** Alternative: leave the lockfile (the site build rule says `Gemfile.lock` comes out unchanged from a build, which this deliberate update doesn't break).

12. **The hub** (evidence C). The hub's `_data/books.yml` lists every book in `bibliography.html` (18 of 18), with the same three redirecting O'Reilly URLs. **Recommend: a one-file hub PR that changes those three URLs, opened at C6, merged only on the owner's word.** Alternative: leave the hub.

13. **Defects found while planning** (evidence B to O). Every item in "Defect list" below is fixed in this iteration as stated. **Recommend: yes.**

## Planning evidence

All trials ran in a scratch copy under `<scratchpad>/plan25`, made with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <dir>`, then `rm -rf .venv .venv-ft` and `uv sync --locked` followed by `uv sync --locked --all-packages`. Nothing was installed in the repo or globally, nothing on the host changed, the site was built and served only from the copy, and the scratch tree was deleted before the plan commit. Four read-only survey agents covered the cards (evidence N), quoted output (evidence O), the decks (evidence G) and a house-voice sample (evidence E); the planner re-read each finding it lists as a defect at the cited lines.

A. **Repo and ids.** `release/r25` is at e32dea5, which `git tag --points-at` gives as `r24.x`; `gh release view r24.x` shows "r24.x: Deck 301", notes-only. PR #25 merged 2026-11-08; CI and Pages are green on e32dea5; the `main` ruleset is active; the repository is public and its homepage is the Pages URL. `grep -rnE '(run: |^\| )C[0-9]' _plans/` prints nothing. Step prefixes used in earlier plans: A, D, G to N, P to Z (R0 to R6 in r15, with `run: R1a`, `run: R1b`); B, C, E, F and O are free. `_plans/r24-plan.md` shows D6 `todo` and `_plans/iteration-plan.md` shows "r24 (active)" and PDP-152 `active` (BK1, BK2). Reconciliation rows run to 436, so r25 starts at 437.

B. **Link sweep.** 467 URL hits, 212 distinct, from `grep -rnoE 'https?://...'` over `_docs _examples bibliography.html README.md examples/README.md examples/*/README.md _parts index.html chapters.html examples.html diagrams.html _layouts _includes _config.yml _data presentation/deck-*.js`. `curl -sIL` (with a GET retry on anything not 200): 210 answer 200 (202 directly, 8 after one redirect), one is the `_config.yml` `url:` value (404 at the bare host, not a link), one is the Liquid template. Redirects and their final targets, each 200 with no further redirect: the three O'Reilly `/-/` links, `docs.pytest.org/` to `/en/stable/`, `mypy.readthedocs.io/` to `/en/stable/`, `cosmicpython.com/book/preface.html` to `/book/preface`, the `.git` clone URL and the uv installer. 13 fragment URLs: each `id` exists on the page. `docs.python.org/3/` 155 hits in 40 docs (50 distinct); `/3.15/` 1; all 50 `/3.15/` forms 200 with 0 redirects. `typing.python.org/en/stable/...` 404 for both pages. No dead link.

C. **Hub and bibliography.** `bibliography.html` lists 18 books; every book italicised in `_docs` is among them (journal names aside). The hub clone's `_data/books.yml` has each of the 18 and the three `/-/` URLs. The hub clone is on a stale branch (`books-python-r21`); C6 works from a fresh checkout of the hub's `main`.

D. **Validator and gates.** `python3 scripts/validate.py`: 0 errors, 6 warnings (the appendix floors in decision 7). `--self-test`: ok. `--claims`: every row from 47 resolved; 32 legacy rows (decision 6). Word counts: maximum 2,499 (chapter 37), then 2,468 (20), 2,458 (01), 2,453 (11), 2,447 (40), 2,431 (14), 2,426 (26); none over 2,500. 41 include captions, 30 to 43 words. Liquid: no `{{` inside any fenced block in `_docs` (0 `{% raw %}` blocks needed). Sidebars: exactly one in each of chapters 5 to 40, none in 0 to 4 or the appendices. `host_ids.py check`: 885 files, 0 hits; `host_ids.py history`: 69 commits, 2,005 path objects, clean. `verify.sh` in the fresh copy: `1406 passed`, "verify: all steps passed". `site-build.sh` in the copy built 48 docs pages, 15 part pages and 41 example pages plus the index; `/plans/` is not in `_site` (`plans` has `output: false`) and no built page links to it. (The script's final `git diff` check fails in a copy without `.git`; in the repo it runs.)

E. **House-voice sample** (agent, docs 02, 13, 24, 30, 37, 46; `--stats-hits` on each). Verdicts: 02 minor, 13 needs edits, 24 minor, 30 needs edits, 37 needs edits, 46 needs edits; 20 must-fix and about 40 nits. None has an em dash, a chapter number or a cross-language comparison. Book-wide patterns it found, which the planner counted:
   - "Build, run, observe" should open by saying what the run proves (lgtm-professional-voice, "Per surface"). 38 docs have the section; 5 (21, 26, 27, 28, 29) open that way; 33 open on the sync command or on a test count (VO1).
   - 29 docs carry a "Read the figure from the top" walk-through (decision 8).
   - 23 docs say "the hub" in "For deeper coverage" (decision 8).
   - None of the six appendices has a closing "What you can do now", though each states learning objectives (VO2).
   - Must-fix sentences, re-read by the planner: `02.md:28` "so every name you see exists, passes its tests and satisfies `mypy --strict`" (defensive, three-beat); `02.md:126` states two behaviours (runtime-checkable checks names only; a mock is assignable to every type) whose witnesses are in other examples (`test_runtime_checkable_checks_names_only` in 09, `test_mypy_accepts_every_mock_where_a_gateway_is_expected` in 11) and are not named; `13.md:22` opens "Why this matters" on mechanism with the intent at 34-36; `30.md:36`, `:101`, `:126` open sections on a bare code block and `30.md:68` re-tells the listing; `30.md:120` states a `TypeError` from `deepcopy` that only a docstring (`tests/test_lookup.py:28`) mentions; `37.md:142` a mutation sentence ("Adding an `await asyncio.sleep(0)` ... makes the test fail") with no recorded run; `46.md:30`, `:183-185` process narration and defensive register. `37.md:194` ("A second run of each build agreed ... within about 0.4") is witnessed by `_plans/evidence/r18-gil-benchmark.md` line 92 and is not a defect.

F. **Sidebar census.** `grep -c '<blockquote class="ai-sidebar"'` is 1 in each of chapters 5 to 40. The first sentence of each, read from the files: chapters 5, 6, 9 to 20 and 22 say "an assistant may"; 7 and 8 "An assistant writing ... may"; 21 "'a composite' arrives as"; 23 to 40 state what the request leaves open ("'A chain of responsibility' doesn't say what 'pass it on' means", "'Make the history iterable' doesn't say whether ...", "'Lazy loading' leaves open which names ...", "'Add an insurance step' names no place for the undo"). Bold lead-ins: "Reviewing assistant-..." in 5 to 22, "Specifying ..." or a noun phrase in 23 to 40. Sidebar lines: `05.md:173`, `07.md:176`, `11.md:228`, `12.md:188`, `21.md:237`, `22.md:220`.

G. **Decks** (agent; text extracted with `presentation/notes.py` from the committed files). 101: 62 slides, 201: 45, 301: 42, each equal to its notes count. Metadata: creator, lastModifiedBy and company PatternCatalyst in all three; subject identical; 101's `dc:title` differs from its cover. Notes minimums (whitespace words): 101 cover 97, divider 50, content 94; 201 85, 45, 99; 301 95, 63, 91; all at or over the floors (201's divider 42 sits exactly on 45). Positional and label counts as in decision 2. Clean: em and en dashes 0, cross-language words 0, chapter or appendix 0, internal codes 0, "the book" only on 101's closing slide and notes. `render-png.sh` lists 11 figures for 101; `deck-101.js` uses 05, 06, 12, 19, 21 and 25.

H. **Figure legibility** (smallest SVG `font-size` and `viewBox`; slide box 12.09 by 4.95 in; site column 622 CSS px, breakout 982 CSS px).

   | Fig | viewBox | Slide pt | Site px (622) | Deck |
   | --- | --- | --- | --- | --- |
   | 05, 06, 07 | 820x560 | 7.0 | 8.3 | 101, 101, 201 |
   | 08 | 1140x560 | 7.3 | 6.3 | - |
   | 13 | 980x700 | 5.9 | 7.3 | - (PNG unused) |
   | 15 | 990x715 | 5.5 | 6.9 | - |
   | 16 | 1000x730 | 5.4 | 6.8 | - (PNG unused) |
   | 19 | 1100x700 | 5.9 | 6.5 | 101 |
   | 21 | 1040x700 | 5.9 | 6.9 | 101 |
   | 25 | 1250x620 | 6.3 | 5.5 | 101 |
   | 26 | 1000x980 | 4.2 | 7.2 | - |
   | 29 | 1000x1060 | 3.7 | 6.8 | - |
   | 30 | 1000x1000 | 3.9 | 6.8 | - |
   | 31 | 1220x480 | 8.2 | 5.9 | 201 |
   | 33 | 1020x420 | 9.3 | 6.7 | 301 |
   | 34 | 1300x520 | 7.4 | 5.3 | - |
   | 35 | 1100x660 | 6.2 | 6.5 | - |
   | 36 | 1160x640 | 6.1 | 5.9 | - |
   | 39 | 920x820 | 5.9 | 9.1 | - |
   | 40 | 960x410 | 9.6 | 7.1 | 301 |

   27 of 41 figures fall under 8 px at 622; 0 of 41 at 982. Deck 101's figure slides measure 6625844 by 4526280 EMU for figure 05 (7.25 by 4.95 in, 7.0 pt), so the box is the same 4.95 in height for every deck. The headless Firefox screenshot (`--window-size=1280,3000`, the copy's `_site` served on 127.0.0.1 and stopped afterwards, a scratch profile) of chapter 34 shows the figure about 620 px wide with unreadable labels.

I. **Gates as written.** CLAUDE.md's repo-wide voice gate (`scan.sh --tier ban --fail --exclude LICENSE-docs.md --exclude CLAUDE.md --exclude validate.py --exclude host_ids.py .`) exits 1 in this working tree with 398 ban-tier lines, all under `.venv-ft/lib` (the free-threaded environment from r18; the scanner prunes `.venv` but not `.venv-ft`). With `--exclude .venv-ft` it reports 0. r19's corrections already ran it with that flag (VA1). `_plans/` alone: 276 ban-tier lines (plans may name banned patterns; no em dash in `_plans`). The idiom scan over `examples/`: 31 ban-tier, all `print()` in the three benchmark scripts r10 and r18 sanctioned (`21 bench/commodity_memory.py` 16, `37 bench/gil_bench.py` 10, `37 bench/lost_update_probe.py` 5), and one watch-tier false positive (`mocker.patch.dict` matched as a Pydantic v1 call).

J. **Legacy rows.** `validate.py --claims` lists rows 1 to 5, 17 to 27 and 31 to 46 as legacy with no token; 5, 26 and 27 are `open`. Witness names for 26 and 27 from `grep -n '^def test_'` in examples 14 and 09 (decision 6).

K. **Validation records.** r22: repair round 2 is recorded, with no confirmation after it. r23: the final confirmation is recorded only in the PRD build log (r24's K2 note). r24: the confirmation of repair round 1 is recorded in `_plans/evidence/r24-deck-qa.md`; repair round 2 applied the confirmation's strings verbatim and "Every gate was re-run", with no confirmation after it; D6 is `todo`. C0 records these as Corrections in the r24 plan (BK1) and r25 records every round, including a confirmation after its last repair (QA pipeline).

L. **r21 hand-off.** `_plans/evidence/r21-test-pattern-map.md` "Conditional Test Logic instances for r25" lists the three tests and the `StowagePlan` docstring (decision 9). Re-read at the cited lines; unchanged since r21.

M. **PRD and sibling.** The PRD (Notion `40361a5f-8a3b-812f-8403-e349b440ae34`) has no section on a retro or final release; §8c fixes the standards (1,900 to 2,500 words, one paired figure per chapter, one runnable example per hands-on chapter, the same spine), §12 the process, §12a the lessons, and its status line reads "IN PROGRESS: r24 shipped 2026-11-08 ... Next: r25 (retro and QA sweep)". The Java sibling's last iterations (`r14-build-plan.md`, a cleanup: bibliography reconciliation, a diagram audit, a book-wide voice sweep, a hub re-sync as its own PR; `r15.0` "Companion decks; book complete") were read for process only; its README status still describes r01.

N. **Cards and READMEs** (agent; the planner re-read findings 1, 5, 6, 8, 11 and 14 at the cited lines). All 41 cards against their READMEs, tests and `src`. Mechanically clean across all 41: every backticked `test_*` name and file path exists, every backticked identifier exists in the member, every test function is named in its README, every card's `github_path` is its directory and `order` its prefix, and each card's doc exists. Test counts per member (ast for functions, `pytest --collect-only -q` for cases) agree with every count a card or README states, from 03's "nineteen tests" to 42's "six collected". No card or README still says "from the example directory". Cards and READMEs are different files: the card is the site page, the README the GitHub page (SC2). Both clean apart from line length and run blocks: 30 pairs. Findings, fixed as CD1 to CD16:
   - 42: three places say pytester tests "assert the exact outcome counts" (`_examples/42-appendix-b-pytest.md:5`, `:18-20`, `examples/42-appendix-b-pytest/README.md:4-6`), as do `42.md:162` and `:196`. 21 of the 24 pytester tests call `assert_outcomes`; `test_an_unknown_option_fails_under_strict_config` (`test_config.py:100`) and the `[strict_config]` case of `test_strict_enables_the_four_strictness_options` (`:150-152`) assert `ret == pytest.ExitCode.USAGE_ERROR`; `test_pytest_param_ids_name_the_cases` compares node ids only. The card blurb (`:8`) already says "asserts the outcome counts or the exit status".
   - 36: `README.md:86` is 131 characters in a file that wraps at 96 (and `:24` is 120); card `:17-18` and README `:23-24` describe the seventeen parity rows with six weights per zone where `_WEIGHTS` (`test_parity.py:16`) has eight (0.5 and 20.5 undescribed); README `:87` "plain functions", where the tests also pass a bound method.
   - 05: README `:78-93` lists 13 of the 14 tests (missing `test_contract_catches_an_accepted_unknown_zone`); card `:19-20` "Replacing one moves only the output it owns" contradicts `test_srp.py:53-54` (a tariff moves net and tax).
   - 09 README `:97` "naming the non-method member" (the match at `test_runtime_checkable.py:55` names none); 18 README `:96` omits `[no-any-return]` (`test_static.py:121`); 26 README `:115` omits `[no-untyped-def]` (`test_static.py:169`).
   - 19 README `:104` "naming the protocol member" and 20 README `:47`, `:127` "naming `book`": `test_mypy_reports_an_implementor_missing_a_primitive` (19 `test_static.py:123-128`) and `test_mypy_reports_a_member_missing_from_an_explicit_proxy` (20 `:248-253`) assert only `"protocol member" in stdout`.
   - 19 README `:30` and card `:25-26`: `ship` picks the gateway "from a read-only `frozendict`"; `ship` takes a `Mapping`, only `default_gateways()` builds the `frozendict`, and the tests pass a dict.
   - 21 README `:18-19`: `carries_dangerous_goods` "use[s] `match` ... with `assert_never`"; it is one `any(...)` over `consignments(shipment)` (`consolidation.py:19-21`).
   - 22 README `:37-38` and the `test_lifetime.py` module docstring: "Every lifetime test ... calls `gc.collect()`"; `test_a_slotted_subscriber_without_a_weakref_slot_is_refused` doesn't, and `test_a_lambda_subscriber_is_held_strongly` uses neither a helper nor `del`.
   - 24 README `:72-73` pair two tests per line and give both the second test's result ("nine pairs", "two pairs"); `test_a_tracking_history_can_be_walked_twice` asserts equal lists of three.
   - Run blocks: 36 of 41 cards are identical with the slug masked. `_examples/11-*.md:45` "and run:"; `_examples/00-prerequisites.md:41` `uv run pytest` without `-v`; the 21 and 31 cards omit the bench line their READMEs give (`README:71`, `README:70`); 21's `bench/commodity_memory.py:3` docstring omits README's `-I`.
   - Line length: unwrapped sentences left by earlier edits in READMEs 05, 09, 10, 21, 23, 25, 26, 35, 36, 42 and unwrapped bullet lists in 11, 12, 13, 15, 16, 19, 24 (each over the file's 93 to 99 wrap by 15 or more); card lines `_examples/36-*.md:18` (125) and `_examples/42-*.md:14` (108), and a short orphan line at `_examples/42-*.md:20`. Tables and code lines (43, 46, 37) are left as they are.
   - Left out after re-reading, not defects: 23 README `:22`, 30 README `:107`, 32 card `:27-28`.

O. **Quoted output re-runs** (agent, fresh copy; experiments edited the copy and were restored, `diff -r` against the repo clean afterwards). 13 docs: 00, 03, 06, 09, 14, 18, 22, 26, 29, 32, 38, 41 and 43. 49 fenced output blocks re-run; all 49 match modulo timings and `<repo>` (09's experiment-two block omits mypy's `note:` lines, which the sentence before it says). Every stated test count in the 13 docs matches (`26 passed` in 00 through "26 test functions and 32 cases" in 43). Experiments re-run where the doc states its edit: 00's `reweigh -> str` (4 errors in 2 files), 03's `_GUARDED` (`1 failed, 18 passed`), 06's two, 14's two (`4 failed, 36 passed`), 18's two (three runs each, identical), 22's (`6 failed, 25 passed`), 26's (`5 failed, 35 passed`), 29's (`7 failed, 28 passed`), 32's (`7 failed, 13 passed`, 3 mypy errors), 38's two, and 41's `uv` and mypy claims (stale-lock error, `Failed to spawn: pytest`, two `[unreachable]` errors, `Redundant cast`, `[deprecated]`, `--no-strict` refused). One prose mismatch: `41.md:43` "took the environment from 54 distributions to 13. It removed all 41 members"; a fresh run gives 55 to 13, and the workspace has 42 members (41 examples and the spike); the figures come from `_plans/evidence/r20-toolchain-runs.md:808-809`, recorded before r21 added example 46 (QO1). Not re-run: 18's "twenty fresh interpreters" evidence and 41's `.venv-ft` ruff findings (C3a covers both). The remaining 34 docs are C3a's.

P. **Pins** (2026-11-08). PyPI `info.version`: pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4, mypy 2.4.1, uv 0.13.7, uv-build 0.13.7, cairosvg 2.9.1. endoflife.date: 3.15 latest 3.15.2, 3.14 latest 3.14.10. `npm view pptxgenjs dist-tags`: `latest 4.0.1`, `beta 4.0.1-beta.2`; image-size 2.1.0; node v22.22.2, npm 10.9.7. `gh api repos/<r>/releases/latest`: actions/checkout v7.0.1, configure-pages v6.0.0, deploy-pages v5.0.1, upload-pages-artifact v5.0.0, astral-sh/setup-uv v10.3.3, ruby/setup-ruby v1.338.0 (the build plan says 1.336.0; the workflow pins `@v1`). Docker Hub: newest `ruby` 4.0.x tag is 4.0.9. rubygems: jekyll 4.4.1, jekyll-seo-tag 2.9.1, jekyll-sitemap 1.4.0, jekyll-redirect-from 0.17.0, jekyll-sass-converter 3.1.0, csv 3.3.7 (the build plan row still says "csv 3.3.6 -> bump to 3.3.7"; the lock has 3.3.7). `bundle outdated` as decision 11; `Gemfile.lock` unchanged by the probe.

Q. **Site chrome.** Homepage, part pages, examples index, footer and bibliography read in source and in the built copy. Footer: CC BY 4.0, Apache 2.0, source and issues links, all 200. Part pages: 15, titles and blurbs current. Homepage "Fourteen parts and the appendices" matches 14 numbered parts plus Part 14 Appendices. Defects SC1 to SC3 below.

## Defect list

Each defect has an id, its evidence and its fix. All are fixed in this iteration (decision 13); the step that owns each is in brackets.

**Bookkeeping (BK)**
- BK1: `_plans/r24-plan.md` D6 `todo` though PR #25 merged as e32dea5, tagged `r24.x` and released; r24's repair round 2 has no recorded confirmation (evidence K). Set D6 `done` with a dated Corrections note. [C0]
- BK2: `_plans/iteration-plan.md` "r24 (active)", PDP-152 `active`, no r25 row active and no PDP id. Close r24 (PDP-152 `done`), add PDP-021 for r25 `active`, mark r25 active, dated note. [C0]
- BK3: the r24 plan's sidebar count "`11.md:228` and 19 pattern-chapter sidebars" (decision 8 there) is 18 by grep (evidence F). Corrections note in the r24 plan. [C0]
- BK4: the r24 plan's "floor 6.3 pt, Deck 101's smallest accepted figure" (evidence H there): Deck 101 shows 19 and 21 at 5.86 pt. Corrections note; the decks don't change (decision 5). [C0]
- BK5: `_plans/r01-build-plan.md` pin table: ruby/setup-ruby "v1 (1.336.0)" (now 1.338.0) and Jekyll's "csv 3.3.6 -> bump to 3.3.7" (done). Dated r25 note and the two cells. [C0]

**Validator and gates (VA)**
- VA1: CLAUDE.md's repo-wide voice gate lacks `--exclude .venv-ft`, so it fails on any tree with the free-threaded environment (evidence I). Add the flag in CLAUDE.md "Per-chapter gates" and in this plan's QA pipeline. [C1a]
- VA2: decision 2, option 1: per-deck label check for 201 and 301, "the deck" self-reference check, self-tests that fail with the check disabled. [C1a]
- VA3: decision 4: link-form check (`docs.python.org/3/`, `/latest/` outside `typing.python.org`, `oreilly.com/library/view/-/`), self-test. [C1a, after C1b's rewrite]
- VA4: decision 5: figure legibility check at 982 px, 8 px floor, self-test. [C1a]
- VA5: decision 6: `CLAIMS_FIRST_ENFORCED` to 1, legacy branch and its self-test replaced by one that fails when a row from 1 has no token. [C4a, after the rows are witnessed]

**Links (LK)**
- LK1: 155 `docs.python.org/3/` to `/3.15/` in `_docs` (and any in `_examples`, READMEs, docstrings, diagrams registry), with the 62 matching `source:` tokens in `_plans/reconciliation-plan.md` (orchestrator) in the same commit. [C1b]
- LK2: `bibliography.html` lines 36, 43, 50: the three canonical O'Reilly URLs (evidence B). [C1b]
- LK3: `00.md:231-232`: `https://docs.pytest.org/en/stable/` and `https://mypy.readthedocs.io/en/stable/`. [C1b]
- LK4: `15.md:325`: `https://www.cosmicpython.com/book/preface`. [C1b]
- LK5: `11.md:125`, `:391`, `43.md:285`: typeshed `blob/main` to `blob/<sha>` once the quoted comment is confirmed at that commit. [C1b]

**AI sidebars (SB)**
- SB1 to SB18: chapters 5 to 22, the opening sentence and the bold lead-in, decision 1 option 1. Each new opening states what the request in the chapter's prompt leaves open, in the chapter's own terms; the nested prompt and the review line stay byte-identical (checked by diff). [C2a, C2b]

**Voice and claims in prose (VO)**
- VO1: 33 "Build, run, observe" sections (chapters 0, 3, 5 to 20, 22 to 25, 30 to 40) open on the command or a test count. Each gains a lead sentence stating what the run proves, taken from the section's own content, before the command; inventory sentences ("The example has 26 test functions and 40 cases") move after it. Chapter 37 is at 2,499 words: its lead replaces an equal number of words in the section. [C2a to C2d by doc range]
- VO2: the six appendices state learning objectives and have no closing map. Each gains a short "What you can do now" mapping each objective to the table or example that delivers it (validate.py's spine for appendices doesn't require it; CLAUDE.md's structure rule does). [C2d]
- VO3: decision 8 option 1: remove "the hub" from 23 docs; CLAUDE.md's spine line amended. [C2a to C2d by doc range; CLAUDE.md at C1a]
- VO4: `02.md:28` defensive three-beat; `02.md:126` names the two witnesses in other examples by test name (or the chapter cuts the clause); `02.md:150` "no second way to get an instance" narrowed (`importlib.reload` is a second way, and chapter 33 tests it). [C2a]
- VO5: `13.md:22` "Why this matters" leads with the intent; `13.md:40` defensive disclaimer cut; `13.md:166` re-narration trimmed. [C2a]
- VO6: `30.md:36`, `:101`, `:126` each gain a lead sentence before the listing; `30.md:68` trimmed to what the code doesn't show; `30.md:120` either gains a test that asserts the `TypeError` (in `tests/test_lookup.py`) or the sentence goes. [C2b; TS2 if a test]
- VO7: `37.md:142` re-run in a scratch copy; the sentence gains the failing test's name and the recorded result, or is cut. `37.md:197`, `:250` defensive and internal-policy phrasing. Word-neutral (2,499). [C2c]
- VO8: `46.md:8`, `:30`, `:74`, `:113`, `:183-185`: process narration and defensive register reworded to state the decision; the 70-word sentence at 183 split. [C2d]
- VO9: the house-voice rubric over every doc not in the sample (C2a to C2d each read their range against the rubric and fix must-fix items of the kinds in evidence E, recording each fix and each kept nit with a reason). [C2a to C2d]

**Quoted output (QO)**
- QO1: `41.md:43`: re-run in a fresh copy and quote the counts it prints (55 and 13 today, 42 members), with the evidence lines in `_plans/evidence/r20-toolchain-runs.md` left as the r20 record and the new run recorded in `_plans/evidence/r25-qa-sweep.md`. [C2d]
- QO2 onward: whatever C3a finds in the 34 docs not sampled, each fixed by the doc's owner with the fresh, scrubbed block. [C3a]

**Cards and READMEs (CD)** (evidence N; all C2g, except doc lines, which go to the doc's owner)
- CD1: example 42's "exact outcome counts" in the card (`:5`, `:18-20`) and README (`:4-6`) become "the outcome counts, the node ids or the exit status", as the blurb says; `42.md:162` and `:196` the same [C2d]; the orphan line at card `:20` rewrapped.
- CD2: 05 README: add `test_contract_catches_an_accepted_unknown_zone` to the list.
- CD3: 05 card `:19-20`: the tariff moves the net and the tax from it, a tax rule moves only the tax, the sink moves neither.
- CD4: 09 README `:97`: drop "naming the non-method member".
- CD5: 18 README `:96` and CD6: 26 README `:115`: name both codes each test asserts.
- CD7: 19 README `:104` and 20 README `:47`, `:127`: the tests gain `assert "insure" in stdout` and `assert '"book"' in stdout` (TS3, TS4), so the READMEs stay as written; if a chapter quotes the line, its quote is re-checked.
- CD8: 19 README `:30` and card `:25-26`: `ship` takes the gateway registry, and `default_gateways()` returns a read-only `frozendict`.
- CD9: 21 README `:18-19`: only `consignments` matches with `assert_never`; `carries_dangerous_goods` is built on it.
- CD10: 22 README `:37-38`: "Every test that asserts a subscriber was dropped or kept alive calls `gc.collect()` first"; the `test_lifetime.py` docstring the same [C2e].
- CD11: 24 README `:72-73`: one line per test with what each asserts.
- CD12: 36 card `:17-18` and README `:23-24`: the eight weights per zone; README `:87` "plain callables"; README `:24` and `:86` rewrapped.
- CD13: run blocks: 11 card "and run" dropped; 00 card `-v` added; the bench line added to the 21 and 31 cards; 21's bench docstring gains `-I` [C2e].
- CD14: READMEs 05, 09, 10, 21, 23, 25, 26, 35, 42 and 11, 12, 13, 15, 16, 19, 24 rewrapped to their file's width (prose and bullets only; tables and code untouched); card `_examples/36-*.md:18` and `_examples/42-*.md:14` rewrapped.

**Tests and docstrings (TS)**
- TS1: `examples/05-srp-ocp-lsp/tests/test_srp.py:43-61`: the verification branch moves into the parameter table (decision 9). Run the member three times and in reverse; chapter 5's quoted run (`05.md:216-218`) re-checked. [C2e]
- TS2: only if VO6 keeps `30.md:120`: a test in example 30 that asserts the `TypeError`, seen failing when its cause is removed. [C2e]
- TS3: `examples/19-adapter-facade-bridge/tests/test_static.py:128`: also assert the missing member's name (`insure`), seen failing on a draft that omits a different member. [C2e]
- TS4: `examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_static.py:253`: also assert `book` is named, seen failing likewise. [C2e]

**Figures and site legibility (FG)**
- FG1: `assets/css/site.css`: `.excalidraw-figure` breaks out of the prose column to the container width when the viewport allows (decision 5); `_includes/excalidraw.html` links the SVG to its full-size file. Screenshots of three wide-figure chapters (25, 31, 34) at 1280 px and of one at 390 px recorded in the evidence file. [C2f]
- FG2: `presentation/render-png.sh` `figs_101` and `presentation/png/`: drop 13, 14, 16, 22 and 23 (no builder uses them); `--check` then covers 13 figures (DK5 updates `build-notes.md`). [C2g]

**Decks (DK)** (decision 3, option 1)
- DK1: 101 slide 2 "The route" retitled as a noun phrase naming the sections (as 201's "Eight themes"); notes unchanged except a positional word if one remains.
- DK2: 101 notes 2 "The deck runs in nine sections." and notes 3 "The code in the deck was held to a standard ..." reworded with no self-reference.
- DK3: 101 `pres.title` to "Design Patterns with Python: 101, Patterns and SOLID in Python", matching its cover.
- DK4: 301 slide 2: the title and bullets count the reference section, and its notes drop "versions" (no slide shows them) or name where the closing notes give them without a position word.
- DK5: `presentation/build-notes.md`: three builders, "each builder", the identity proof for all three decks with 301's part count.
- DK6: `README.md` 101 entry to the 201/301 template ("..., on <subject>. Code on the slides is read ...; `presentation/build-notes.md` says how to rebuild it.").
  [all C2g]

**Site chrome and README (SC)**
- SC1: `index.html:85` "each proving a pattern the chapters make" (a pattern isn't made; the chapters make points). Reword. [C2f]
- SC2: `examples.html` "Every card links to the example's page on this site (a rendering of the README with cross-references)". The page is the card, a separate file from the README (evidence N). Reword to what the page is. [C2f]
- SC3: `README.md`: the Status section (decision 10). [C2f]

**Checked, not a defect**
- Every pin is the latest stable (evidence P); liquid, rouge, json, terminal-table and unicode-display_width are held by Jekyll's constraints.
- No dead link; every fragment resolves; the clone URL and the uv installer redirect by design.
- `host_ids` check and history clean; no em dash in any tracked text; the voice ban tier is 0 with `.venv-ft` excluded; the idiom scan's 31 `print()` lines are the three sanctioned benchmark reports.
- 0 Liquid braces in fences; every caption 30 to 43 words; one sidebar in each of chapters 5 to 40; the spine check passes; no doc over 2,500 words.
- `37.md:194`'s second-run sentence rests on `_plans/evidence/r18-gil-benchmark.md:92`.
- The `if before is None` and `--update-golden` branches, and "test seam" (decision 9).
- No `/plans/` link in the built site.
- 201's divider 42 notes at exactly 45 words meets the floor.

## Parallel groups (Sonnet executors, disjoint files)

C1a and C1b run first, alone, because they touch many files mechanically. Then C2a to C2g run in parallel; each owns only the files listed and never edits a plan.

| Group | Owns | Defects |
| --- | --- | --- |
| C2a | `_docs/00` to `_docs/13` | SB1 to SB9 (chapters 5 to 13), VO1, VO3, VO4, VO5, VO9 and QO items in that range |
| C2b | `_docs/14` to `_docs/30` | SB10 to SB18 (chapters 14 to 22), VO1, VO3, VO6, VO9 and QO items in that range |
| C2c | `_docs/31` to `_docs/40` | VO1, VO3, VO7, VO9 and QO items in that range |
| C2d | `_docs/41` to `_docs/46` | VO2, VO3, VO8, VO9, QO1, CD1's two lines in `42.md` and QO items in that range |
| C2e | `examples/*/src`, `examples/*/tests`, `examples/*/bench` | TS1 to TS4, the CD10 and CD13 docstrings and any docstring fix from QO; re-captures quoted output for the doc owner of that range (handed over as text, never written into `_docs`) |
| C2f | `assets/css/site.css`, `_includes/`, `_layouts/`, `index.html`, `examples.html`, `README.md` (Status only) | FG1, SC1 to SC3 |
| C2g | `_examples/*.md`, `examples/*/README.md`, `presentation/` (builders, `build-notes.md`, `render-png.sh`, `png/`, the 101 and 301 `.pptx`), `README.md` (Companion decks only) | CD1 to CD14 (card and README lines), DK1 to DK6, FG2 |

`README.md` is split by section between C2f and C2g; C2g lands first and C2f rebases. A doc whose quoted output TS1 changes takes the new block from C2e through the orchestrator.

## QA pipeline

1. **Fresh copy for every check that runs code**: the three commands of the planning evidence preamble; `.venv-ft` added with `uv sync --python 3.15t` only where the free-threaded job is re-run.
2. **Gates**: `bash scripts/verify.sh`; `uv run python scripts/validate.py` with `--self-test` and `--claims`; `python3 scripts/host_ids.py check`; `bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh --tier ban --fail --exclude LICENSE-docs.md --exclude CLAUDE.md --exclude validate.py --exclude host_ids.py --exclude .venv-ft .`; `scan.sh --stats _docs` before and after, recorded; the idiom scan over `examples/ spikes/ scripts/` with the survivors listed; `bash scripts/site-build.sh` with `Gemfile.lock` unchanged (after decision 11's deliberate update).
3. **Quoted output, whole book**: every fenced output block in all 47 docs re-run in a fresh copy (C3a), not a sample; mismatches beyond timings and `<repo>` fixed in prose.
4. **Links**: the B sweep re-run after C1b and again at C5a; 0 non-200 apart from the two command URLs; every `source:` token still in its chapter.
5. **Legibility**: the VA4 check, and screenshots at 1280 and 390 px of chapters 25, 31 and 34 in the built copy, viewed.
6. **Decks** (C2g): for 101 and 301, the r24 QA pipeline steps 1 to 11 (`npm ci`; `render-png.sh --check` prints `same` for 13; build; identity proof for 201; soffice with a private profile, `pgrep -x soffice.bin` empty after; `pdffonts`; page images; `notes.py`; the step 8 pointer grep and AI-claim grep; ban scan; `validate.py`), and every changed page viewed.
7. **Independent Opus readers** (C5a), separate agents that never see each other's findings or this plan's conclusions, each given the files and the rules:
   - reader 1: chapters 5 to 22 for the new sidebar openings and every VO1 lead sentence, claims and voice;
   - reader 2: a sample of eight docs chosen at C5a by the validator (two per part range, at least one appendix), read for voice against the rubric and for claims against tests and sources, with at least one in three cited tests re-run;
   - reader 3: the site in the built copy (homepage, two part pages, examples index, bibliography, three figure pages at 1280 and 390 px) and the two rebuilt decks' changed pages.
8. **Opus validation** (C5a): every acceptance criterion, every defect id closed with its evidence, `--claims`, the link sweep, the deck pipeline, and the readers' findings; findings named "blocking item N of round M".
9. **Repair and confirmation** (C5b): up to two repair rounds. After each, a fresh Opus confirmation that did not run the round re-runs steps 2, 4 and 6 on the repaired tree, re-reads every changed sentence against its test or source, runs any new self-test with its check disabled to show it fails, and supplies tested replacement strings for anything it fails; those strings are applied verbatim with an exact-match assert. A confirmation follows the last repair as well: the iteration doesn't close on an unconfirmed repair. Every round and confirmation is appended to `_plans/evidence/r25-qa-sweep.md` with its verdict.

## Evidence file

`_plans/evidence/r25-qa-sweep.md` (written from C1a on, appended by each step; host-scrubbed). It records:
- the link sweep before and after (counts, every redirect and its final URL, the typeshed SHA and the quote found at it);
- the sidebar census before and after, with each new opening sentence;
- the VO1 lead sentences, the rubric findings per doc (fixed or kept, with a reason);
- the whole-book quoted-output re-run (C3a): per doc, blocks checked, matched, fixed;
- the legacy-row witnesses (C4a): each row's tokens and the forward and reverse runs;
- the legibility table and the screenshots' findings;
- the deck pipeline for 101 and 301 and the accepted-variation list (decision 3);
- the decision 9 judgements;
- every validation round, repair and confirmation.

## Steps and status

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| C0 | Bookkeeping with dated notes: BK1 to BK5; record the owner's decisions; re-check every pin; decision 11's `bundle lock --update` in the container and a site build; `verify.sh` and `validate.py` green | - | done |
| C1a | Validator and CLAUDE.md: VA1, VA2, VA4 (and VA3 after C1b); CLAUDE.md's sidebar, spine (decision 8) and dated notes (decision 7); every new check has a self-test that fails without it; `--self-test` green | C0 | done |
| C1b | The mechanical link pass LK1 to LK5, with the reconciliation `source:` tokens moved in the same commit by the orchestrator; the link sweep re-run; `validate.py --claims` green | C0 | done |
| C2a | Docs 00 to 13 (group table) | C1a, C1b | done |
| C2b | Docs 14 to 30 | C1a, C1b | done |
| C2c | Docs 31 to 40 | C1a, C1b | done |
| C2d | Docs 41 to 46 | C1a, C1b | done |
| C2e | Example code and tests: TS1, TS2, docstring items; three runs and a reverse run per changed member | C1a | done |
| C2f | Site chrome, CSS figure breakout, README Status; screenshots | C1a | done |
| C2g | Cards and READMEs (CD), decks DK1 to DK6 and FG2 with QA pipeline step 6 | C1a | done |
| C3a | Whole-book quoted-output re-run in a fresh copy after C2a to C2e; mismatches returned to the doc owner and fixed | C2a to C2e | todo |
| C3b | Integration: every gate (QA step 2), the link sweep, the legibility check, `site-build.sh`; evidence file brought up to date | C3a, C2f, C2g | todo |
| C4a | Reconciliation: the 32 legacy rows re-witnessed (decision 6), VA5, rows 437 onward added with resolving tokens | C3b | todo |
| C5a | Opus validation with the three independent readers (QA steps 7 and 8); rows that start `open` closed | C4a | todo |
| C5b | Repair rounds (at most two), each followed by a confirmation, the last one included (QA step 9) | C5a | todo |
| C6 | PR, `ci-ok` green, the hub PR (decision 12) opened; ask the owner before merging either | C5b | todo |
| C7 | After the owner's word: squash-merge, delete the branch, tag `r25.x` on main, notes-only release; PRD status and series line set to complete; `iteration-plan.md` closes r25 | C6 | todo |

## Reconciliation rows

Rows 437 to 451 go in at C4a with resolving tokens; rows whose claim starts "Sweep:" start `open` and C5a closes them. Ch cells name the docs, so `chapter_numbers` parses them.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 437 | 5-22 | Sweep: the 18 sidebar openings state what the request leaves open, and each prompt and review line is unchanged | run: C2a, run: C2b |
| 438 | 0-40 | Sweep: every "Build, run, observe" section opens with what the run proves | run: C2a, run: C2b, run: C2c |
| 439 | 41-46 | Sweep: each appendix closes by mapping its learning objectives | run: C2d |
| 440 | 0-46 | Sweep: Python docs links pin 3.15, every link answers 200 with no redirect but the two command URLs, and every fragment resolves | run: C1b, run: _plans/evidence/r25-qa-sweep.md |
| 441 | 0-46 | Sweep: every quoted output block in the 47 docs matches a fresh run modulo timings and the repo path | run: C3a |
| 442 | 5 | Replacing one collaborator changes only the fields it feeds, checked with no branch in the verification | `test_each_change_moves_only_the_fields_it_feeds` |
| 443 | 19 | mypy names the protocol member an implementor is missing | `test_mypy_reports_an_implementor_missing_a_primitive` |
| 444 | 20 | mypy names the member missing from an explicit proxy | `test_mypy_reports_a_member_missing_from_an_explicit_proxy` |
| 445 | 0-46 | Sweep: every figure's smallest label is at least 8 CSS px at the breakout width, and wide figures render at container width | run: C1a, run: C2f |
| 446 | 0-46 | check_decks refuses the three-way-split labels in Decks 201 and 301 and "the deck" outside the cover, with self-tests that fail without the checks | run: C1a |
| 447 | 0-46 | Sweep: Decks 101 and 301 rebuilt with the consistency fixes, pass the deck pipeline, and Deck 201 is unchanged | run: C2g |
| 448 | 0-46 | Sweep: every card and README agrees with its tests, and the run blocks match | run: C2g |
| 449 | 0-46 | Every reconciliation row from 1 carries a resolving token, and validate.py enforces them all | run: C4a |
| 450 | 0-46 | Sweep: every gate green, including the voice gate with the free-threaded environment excluded | run: C3b |
| 451 | 0-46 | Sweep: three independent readers and the validation passed, and every repair was confirmed | run: _plans/evidence/r25-qa-sweep.md |

Row 30's deepcopy claim (VO6) gets a row at C4a only if TS2 adds its test. A defect kind added during the build (risk "Scope") gets its own row at C4a.

## Acceptance criteria

1. Every defect id in "Defect list" is closed, with its evidence in `_plans/evidence/r25-qa-sweep.md`, and every recurrence grepped.
2. The 36 sidebars state what the request leaves open (decision 1 option 1, or as the owner decides); each nested prompt and review line is byte-identical to e32dea5 (diff recorded); `grep -c` gives 1 in each of chapters 5 to 40; `grep -rniE 'an assistant (may|might|writing)' _docs` prints nothing in a sidebar.
3. Every "Build, run, observe" opens by saying what the run proves; the six appendices close by mapping their objectives; "the hub" appears in no doc; CLAUDE.md's spine line matches.
4. The link sweep reports 0 dead links and no redirect other than the clone URL and the uv installer; no `docs.python.org/3/`, no `/latest/` outside `typing.python.org`, no `oreilly.com/library/view/-/` in any tracked reader-facing file; every reconciliation `source:` token appears in its chapter; the VA3 check passes and its self-test fails with the check disabled.
5. Every quoted output block in all 47 docs matches a fresh run modulo timings and `<repo>` (C3a's table).
6. Every figure's smallest label is at least 8 CSS px at the breakout width (VA4); the screenshots at 1280 px show the wide figures at container width and the 390 px screenshot shows the figure fitted with its full-size link; no figure spec changed unless a defect required it.
7. Decks: 101 and 301 rebuilt with DK1 to DK4; 201 not rebuilt; `render-png.sh --check` prints `same` for 13 figures; the five unused PNGs are gone; every changed page viewed by the executor and by reader 3; `check_decks()` with VA2 passes on all three decks and its new self-tests fail with the check disabled; 101's `dc:title` matches its cover.
8. `validate.py --claims` reports every row from 1 resolved (VA5); rows 5 and 26 `verified (r25)`, 27 `adjusted (r25)`; rows 437 onward closed.
9. `scripts/verify.sh`, `scripts/validate.py` (0 errors; the 6 floor warnings or fewer, recorded as owner-accepted), `--self-test`, `--claims`, `host_ids.py check`, the repo-wide voice gate with `--exclude .venv-ft` (0 ban-tier), the idiom scan (only the sanctioned benchmark `print()` lines) and `site-build.sh` are green; CI `ci-ok` is green on the PR.
10. The decisions 9 and 3 judgements and the accepted deck variations are recorded with reasons.
11. `iteration-plan.md`, the r24 plan and the build plan's pin table carry no stale status; the build plan's dated table records the r25 re-check and decision 11.
12. Every validation round, repair round and confirmation is recorded in `_plans/evidence/r25-qa-sweep.md`, and a confirmation follows the last repair.
13. README has the Status section; nothing in reader-facing files names an internal code; `LICENSE-docs.md` is unchanged.
14. The owner approves the merge; `r25.x` is on main; the release is notes-only; the hub PR is merged or closed on the owner's word.
15. No process left running (`soffice.bin`, `node`, an HTTP server, Firefox); scratch trees deleted.

## Risks

- **Repairs that add overclaims.** Both r23 and r24 caught a new slip after each repair. Mitigation: QA step 9, a confirmation after every repair including the last, with tested strings applied verbatim.
- **Word ceilings.** VO1 adds a sentence to 33 docs; seven sit within 80 words of 2,500 (37 at 2,499). Mitigation: in those seven the lead replaces words in the same section; `validate.py` after every doc edit.
- **The link pass breaking `--claims`.** 62 `source:` tokens move with LK1. Mitigation: one commit for the docs and the tokens, `--claims` before the commit.
- **Sidebar rewrites drifting into new claims.** A request-leaves-open sentence can still describe assistants. Mitigation: the AI-claim grep (`assistants? (may|might|will|tend)|often|usually|typically`) over the 36 sidebars, and reader 1.
- **The CSS breakout on narrow screens.** A wide figure must not cause horizontal scroll. Mitigation: the breakout only above the container width, the 390 px screenshot, the full-size link.
- **Deck rebuilds.** 101 and 301 change; a rebuild could move more than the edited slides. Mitigation: the r24 pipeline, the pointer grep, every changed page viewed, 201's identity proof.
- **Scope.** A whole-book sweep over 47 docs can grow without end. Mitigation: the defect kinds are fixed in this plan; a new kind found during C2 goes to the orchestrator, who adds it to Corrections and to the defect list with the same treatment, never silently.
- **Shared files.** `README.md` has two owners by section; `_plans/reconciliation-plan.md` is the orchestrator's alone. Mitigation: the group table, C2g before C2f for the README.
- **Orphaned processes.** soffice, node, the HTTP server and headless Firefox. Mitigation: `pgrep -x soffice.bin`, `pgrep -af 'http.server|firefox'` before handback.

## Corrections after the build
- Step C1a: done in 3621f97.
  - **VA1:** CLAUDE.md's gate now has `--exclude .venv-ft` (the command reports 0).
  - **VA2:** Decks 201 and 301 refuse the three-way-split labels in every inflection, with 101 exempt. Every deck refuses "the deck" outside the opening sentence of the cover notes.
  - **VA4:** `check_figure_legibility()` puts an 8 px floor on each figure at the 982 px breakout width; all 41 figures pass.
  - **Mutation proof:** every new check makes `--self-test` fail when it's disabled. A width-scaling case was added after the first mutation passed.
  - **CLAUDE.md:** the sidebar rule, the spine (decision 8), and dated notes for decision 7 and O2.
  - The new checks flag Deck 101 notes 2 and 3 ("the deck"), which are DK2 and fixed at C2g. Until then `validate.py` shows those 2 errors.
  - **Incident:** C1a ran `git stash` in the shared tree and briefly took C1b's uncommitted edits. The pop restored them, and C1b re-applied one lost token move. Parallel briefs now forbid `git stash` and `git checkout` of files an agent doesn't own.
- VA3: done in 2f47474. `check_link_forms()` runs over the reader files. It refuses `docs.python.org/3/`, `/latest/` outside `typing.python.org`, and `oreilly.com/library/view/-/`. Its self-test fails when the check is disabled, and the tree is clean after C1b.
- Step C2a: done in 9722376.
  - SB1 to SB9 (docs 05 to 13) have "Specifying X" lead-ins and openings that say what the request leaves open; the prompts and review lines are untouched.
  - VO3: "the hub" is removed from 06, 07, 08, 10 and 13.
  - VO4: `02.md` lines 28, 126 and 150 are narrowed to named tests, with `importlib.reload` as the second-instance witness in example 33.
  - Skipped under O1: VO1, the VO5 wording, and the VO9 nits. VO5's factual claims were checked and hold.
- Step C2b: done in a311eda.
  - SB10 to SB18 (docs 14 to 22) were reworded the same way.
  - "The hub" is removed from 14 to 28 and 30.
  - `30.md:120` cites `test_deepcopy_fails_with_a_type_error_when_the_loader_answers_every_name`, which was added by C2e as TS2 (C2b read it in the shared tree before C2e committed).
  - Skipped under O1: VO1, the VO6 lead sentences, and the VO9 reading.
- Step C2c: done in 92396c3.
  - VO3: "the hub" is removed from 31.
  - VO7: 37's `sleep(0)` sentence was re-run in a fresh copy (the test fails with "tracking polled" at index 1) and now names the test and the result. The "No cause is claimed" and "never a model" clauses are cut.
  - VO1 was skipped under O1.
  - Incident: C2c used `git pull --rebase --autostash`, which briefly stashed the others' edits. Nothing was lost (checked by each owner).
- Step C2d: done in fde2113.
  - QO1: `41.md:43` now reads 55 distributions to 13, with 42 workspace members (41 examples plus `spikes/feature-spikes`), re-run in a fresh copy.
  - CD1: `42.md` lines 42, 162 and 196 are narrowed to the counts, node ids or exit status that the tests assert.
  - VO2 and VO8 were skipped under O1.
- Step C2e: done in fe60751.
  - TS1: a parameter table with explicit ids; chapter 5's quoted run is unchanged.
  - TS2: a new `deepcopy` `TypeError` test, which moves the `30.md:223`/`:225` quoted `test_lookup.py` lines 195 and 218 to 201 and 224 (C3a re-captures them).
  - TS3 and TS4: the missing member's name is asserted (`note:     insure`, `note:     book`), and each was seen failing on a draft that omits a different member.
  - CD10 and CD13: the docstrings.
  - Members 05, 19, 20, 21, 22 and 30 were run three times forward and once in reverse, with `mypy --strict`, in a fresh copy.
  - The decision 9 kept branches (`test_patching.py`, `test_golden.py`) are recorded in the QA evidence.
- Step C2f: done in e6ed0ed.
  - FG1: the figure breakout to the 1080 px container at 900 px and wider, plus an "Open full size" link below 900 px.
  - A 390 px overflow fix for the header nav and long inline code.
  - SC1 and SC2 reworded; SC3 adds a README Status section (the terse rewording in progress, with no completion claim).
  - Screenshots of 25, 31 and 34 at 1280 and 390 px from a fresh-copy build. Not every post-fix view was taken, so C5a re-checks with a measured `scrollWidth`.
- Step C2g: done in 1b2b899.
  - CD1 to CD14 fixed in the cards and READMEs (CD7 holds by TS3 and TS4 in fe60751).
  - DK1 to DK6: Deck 101 slide 2 is "Nine sections", with the `dc:title` and notes 2 and 3 fixed. Deck 301's notes 2 drop "versions". Deck 201 rebuilt identically apart from timestamps, and `render-png.sh --check` reports the same for 13 figures.
  - FG2: five unused PNGs removed.
  - `validate.py` 0 errors.
- Step C1b: done in a5473f7.
  - 155 `/3/` to `/3.15/` rewrites in 40 docs, and none elsewhere. 62 reconciliation `source:` lines moved (73 tokens).
  - 3 O'Reilly canonicals, the 2 chapter 0 roots, the cosmicpython link, and 3 typeshed links pinned to d03a581a (the quote is confirmed at that commit), with their tokens moved.
  - All 57 changed URLs end at 200 with no redirect, and all 11 fragments resolve. `--claims` shows 0 unresolved.
  - No deck builder carries a changed URL.
- Step C0: BK1 to BK5 are recorded as dated 2026-11-08 notes (r24 plan D6 `done` with notes for BK1, BK3 and BK4; `iteration-plan.md` closes r24, marks r25 active, adds PDP-021 and the r26 to r28 roadmap rows per O2; the build plan's ruby/setup-ruby and csv cells corrected). Every pin was re-checked against upstream and is still the latest stable. Decision 11: `bundle lock --update sass-embedded addressable` in the ruby:4.0.9 container moved sass-embedded 1.106.1 to 1.108.1 and addressable 2.9.0 to 2.9.2; `scripts/site-build.sh` passes twice with the new lock.
