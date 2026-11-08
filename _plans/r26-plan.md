---
title: "r26 plan: terse rewording, gates and pilot"
order: 26
output: false
render_with_liquid: false
---

# r26: terse rewording, gates and pilot

Opus-planned 2026-11-08. Branch `release/r26`, cut from main at 15cc747 (the r25 merge, tagged `r25.x`). This file is the source of truth for r26 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

Work item: PDP-022 ("Terse rewording: gates and pilot", r26), added at B0 in the infrastructure range of `_plans/iteration-plan.md`.

r26 builds the gates that keep the rewording honest, then rewrites four docs as a pilot: 01, 03, 23 and 24. It ends with an open PR and a reading packet. The owner reads the pilot and answers one question: **go** (r27 applies the rules as piloted) or **adjust** (name the rules to change). r27 takes the remaining pattern chapters; r28 the framing, foundations, legacy, AI, appendices and deck notes.

The rules are the terse pattern register in `~/.claude/skills/lgtm-professional-voice` (`SKILL.md`, "Terse pattern register", T1 to T12; examples in `references/terse-register.md`). The style study that led to them is recorded in the planning evidence (G).

## Settled rules (carried; not re-asked)

- **Fix now**, every recurrence grepped; **chapters stand alone**; no internal codes in reader files; **every claim tested**; decks stand alone; figures from specs only; no em or en dashes; one PR, squash-merge on the owner's word, tag `rNN.x`, notes-only release (r25 plan, "Settled rules").
- **Changed from r26 on** (owner, r25 O2): tests are named on a `*Tests:*` line after the paragraph, not inside the sentence; the 1,900-word floor is dropped and the 2,500 ceiling stays.
- **Code, fenced output, inline code, commands, URLs and quotations are never edited** by the rewording. Only prose around them moves.

## Owner decisions

2026-11-08, at the plan gate:

- O1: decision 1 takes the **alternative**, the Camel layout: one H2 per pattern with H3 subheads. "The pattern layout (O1)" below pins the shape; GT2, GT6, PL3, PL4, the targets, the excerpts and the criteria follow it.
- O2: decisions 2 to 6 as recommended.
- O3: the Feathers title takes the book's straight house form: "I Need to Make a Change, but I Don't Know What Tests to Write" (evidence H).
- O4: hub PR #62 was merged as 9a3b034; no open hub item remains.
- O5 (owner, 2026-11-08, during B1d): no git worktrees from now on. One branch (`release/r26`) and one PR. Parallel executors edit only the files they own and run no git command that writes (no add, commit, stash, checkout, reset, restore or pull). The orchestrator stages by path and commits each step. This replaces the worktree isolation in the B3 rows and the process section.
- O6 (owner, 2026-11-08): the Python version is stated only on setup surfaces: prerequisites (doc 00), Appendix A (doc 41), README, `_config.yml`, CI and the site front pages. Every other chapter and example README drops it. (1) Recorded pytest output is re-recorded with `--no-header`, so no fence carries a `platform ... Python 3.15.2` line. (2) `docs.python.org/3.15/` links become `docs.python.org/3/`, and quotations taken from those pages are re-checked against the `/3/` text. (3) Facts about a feature or a measurement keep their version ("`frozendict`, new in 3.15", "recorded on Python 3.15.2"). (4) Incidental mentions go. Step B4b does it, before the readers.

## The pattern layout (O1)

Read from Camel 07, 09, 11 and 13 (evidence G): an H2 `## Pattern: <Name>`, then `### The problem`, `### The solution` and `### How Camel models it` in that order (53 to 60 uses each across chapters 3 to 18), then topic H3s named for the point (`### Evaluation order matters`, `### Wire tap vs. multicast`). The book takes it as:

- `## Learning objectives`, `## Why this matters` (the shared domain story, at most 3 sentences), the figure with one sentence and its description (decision 4);
- per pattern, `## Pattern: <Name>`:
  - `### The problem`: the domain failure, at most 3 sentences; failure cases as one-sentence bullets;
  - `### The solution`: one bold definition (`A **Mediator** ...`), restating a definition the chapter or its cited source already gives, then the verdict line `**Bucket: survives.**` (or `dissolves.`, `needs disambiguating.`) with one reason sentence;
  - `### How Python models it`: code first, at most 2 sentences after each block, `*Tests:*` lines;
  - topic H3s, a comparison as `### X vs. Y` with a table;
- then the spine tail, in today's order: `## When not to use it` (bold-led bullets, one per pattern, and the one AI sidebar), `## Build, run, observe`, `## What you can do now`, `## For deeper coverage`.

**23** becomes `## Pattern: Chain of Responsibility` (problem, solution, How Python models it: the stage types and `clear`; `### The terminal and the order`; `### Linked chain vs. tuple`; `### Chain vs. match`) and `## Pattern: Mediator` (problem, solution, How Python models it: `receive` and `_try_release`; `### Mediator vs. choreography`; `### Mediator vs. signal`), each with its own Bucket line. **24** becomes one `## Pattern: Iterator` (problem, solution, How Python models it: the protocol and the generator `__iter__`), with today's four body H2s as topic H3s: `### One pass or many`, `### Read only what you need`, `### Delegating with yield from`, `### Who closes the source`. 01 and 03 hold no pattern and keep their own H2s.

**T6 under this layout.** Code, a table or the figure within 60 prose words applies per H3: to `### How Python models it` and every topic H3. `### The problem` and `### The solution` are exempt, capped by sentences instead (3, and 2 plus the Bucket line). `--terse-stats` measures per H2, and a pattern H2 now holds its whole treatment, so GT1 adds a per-H3 report (words and lead-in per H3) for the packet; the `--terse-stats` columns are recorded as they come.

**Appendix E** takes its Bucket cell from the Bucket line, its Force cell from `### The problem` and its When-not cell from the pattern's bullet.

**CLAUDE.md's spine text** (B1a) becomes: "Every chapter: learning objectives; why this matters; the figure, with one sentence in the body and its walk-through in the figure description. A pattern chapter then has one `## Pattern: <Name>` per pattern, each with `### The problem`, `### The solution` (a bold one-sentence definition and the `**Bucket: ...**` line) and `### How Python models it` (code first), then topic H3s. Then 'When not to use it' on every pattern chapter, bold-led bullets holding the one AI sidebar; 'Build, run, observe' on hands-on chapters; 'What you can do now'; 'For deeper coverage' citing this book's `/bibliography/`, kept in step with the hub's `books.yml` (the chapter text never says 'the hub')."

## Decisions with recommendations

1. **Where the pattern block sits** (T1 against the spine). The spine fixes the H2s: Learning objectives, Why this matters, the figure, the body, When not to use it (with the sidebar), Build, run, observe, What you can do now, For deeper coverage. T1 wants Problem, Solution, Idiom, verdict, When not to use it. They conflict in three places: T1 has no "Why this matters"; the spine puts the figure before any code; CLAUDE.md's "intent before mechanism" says the opposite of T1's "problem before mechanism".
   - **Owner (O1): the alternative**, laid out in "The pattern layout (O1)". The recommendation was: keep every spine H2; "Why this matters" holds the **Problem** (at most 3 sentences; failure cases as one-sentence bullets), the **Solution** (one bold sentence per pattern, restating a definition the chapter or its cited source already gives) and the verdict line `**Bucket: survives.**` (or `dissolves.`, `needs disambiguating.`), once per pattern or once for a chapter whose patterns share it. Then the figure with one sentence. Each body H2 opens with code, a table or the figure within 60 words (T6). "When not to use it" becomes bold-led bullets. CLAUDE.md's structure line becomes "problem before mechanism" for pattern chapters.
   - Alternative (taken): Camel's form, an H2 per pattern with H3 subheads. Closer to the model, but `validate.py`'s spine and every pattern chapter's headings change, and r27 inherits a structural rewrite as well as a wording one.

2. **The thesis chapters' budgets** (T7, T11). T11 allows thesis framing in the chapters that set the thesis up. T7 caps "force" at 3 per chapter after the defining chapter. 01 is the defining chapter (43 uses today); 03 sets the bucket map, and its second sorting question is about the force (23 uses).
   - **Recommend:** 01 may frame the thesis and defines "force" and "Consequences" once; target "force(s)" at most 12 and ABSTR/k at most 10. 03 may frame the buckets; target "force(s)" at most 8 and ABSTR/k at most 5. 03's map table stays byte-identical (Deck 101 copies its cells verbatim, reconciliation row 317). 23 and 24 take the full T7: at most 3 and 1.5. T1 doesn't apply to 01 or 03 (no pattern block); 01 turns its four forces and three shapes into tables (T6), since it has no code.
   - Alternative: the full T7 everywhere, which would leave 01 unable to define its own subject.

3. **Quotations** (T9: at most one short quotation per body section). 24 quotes the Python docs and PEPs about 11 times; each quote is a witness for a claim.
   - **Recommend:** apply T9. A quotation over the budget becomes a paraphrase that keeps every fact of the quote, its source link stays in the chapter, and it's recorded as a waiver that the sources reader checks against the fetched page. The owner then sees T9 applied.
   - Alternative: keep every quotation in the pilot and judge T9 later. Safer, but 24 stays long and the owner can't judge the rule.

4. **The figure walk-through** (T10). 23 and 24 carry a box-by-box walk-through; the `<object>`'s only text alternative is the caption.
   - **Recommend:** the walk-through moves, unchanged in substance, into a collapsed `<details class="figure-description">` right after the include, its text in an inner `<div id="desc-<name>" markdown="1">`. The include gains `described="true"`, which adds `aria-describedby="desc-<name>"` to the `<object>`. The text stays in the chapter, so the invariants check sees it, screen readers get it as the figure's description, and sighted readers open it on demand. The body keeps one sentence about the figure.
   - Alternative: a `description:` key per figure in `_data/diagrams.yml`, rendered by the include. One file holds every description, but the text leaves the chapter, and the invariants check must read two files per doc.

5. **Files that copy pilot wording verbatim.** Appendix E (doc 45) quotes each developing chapter's Bucket, Force and When-not clauses verbatim (98 cells, all verbatim today); rows 68 to 70 come from 23 and 24 and break when those chapters change. The Feathers title also sits in Deck 301's notes (`presentation/deck-301.js:192`).
   - **Recommend:** update both in r26. Appendix E rows 68 to 70 take the new chapter wording, and a new `validate.py` check keeps all 98 cells verbatim, which protects r27 and r28 too. Deck 301 is rebuilt for the title through the r25 deck pipeline (QA step 6 there), and Deck 201 and 101 aren't touched.
   - Alternative: leave both to r28. Appendix E and Deck 301 would carry stale text for two iterations, against the fix-now rule.

6. **Test names inside sentences after a doc is reworded.**
   - **Recommend:** an error, for the docs the rewording has finished: `TERSE_DOCS = {1, 3, 23, 24}` in `validate.py`, extended by r27 and r28, and replaced by "all docs" when r28 ends. Other docs report nothing, so the 1,030 names elsewhere don't drown the output.
   - Alternative: a warning for the pilot docs only. CI ignores warnings, so a regression in a finished doc would pass.

Planner's choices (stated here; the owner can overturn any):
- **The invariants check is its own script**, `scripts/prose_invariants.py`, not part of `validate.py`. It needs git history (the base revision), and `validate.py` runs in CI on a shallow checkout and must stay history-free. It imports `validate.py`'s `body_lines` and `prose_lines`, so both tools agree on what's fenced.
- **Numbers are compared as a multiset per doc.** Numbers move between sentences, so a per-sentence binding would fail every honest reorder, and a script can't segment claims reliably. A set would let a repeated number vanish, which can be a second claim ("3 events" said of two tests). So: multiset, with each dropped duplicate recorded as a waiver, and the facts reader checks that every moved number still attaches to the same noun. Spelled-out numbers ("three decisions") are left to the reader: they're also ordinary words.
- **Test names, links and inline code spans are compared as sets.** A name or identifier said twice may be said once, but never dropped. Names are taken from prose only (fences excluded), or the pytest `-v` output in every pattern chapter would make the test-name check vacuous.
- **Base revision** is `15cc747`, passed as `--base`; CI uses the PR's merge base with `main`.
- **Claims coupling.** `--claims` checks a row's test tokens against `examples/*/tests`, not the chapter; only `source:` URLs must appear in the chapter. So a `*Tests:*` line needs no `--claims` change. To keep the claim tied to its chapter, a new rule applies to `TERSE_DOCS`: a row's test token that is defined in the chapter's own example must appear in that chapter. 0 misses in the pilot; 8 elsewhere (evidence D), fixed when r27 and r28 reach those docs.
- **The duplicate `<meta name="description">`.** jekyll-seo-tag already emits it, so the layout's own tag goes (`_layouts/default.html` lines 7 and 8), and `{% seo title=false %}` stays.

## Planning evidence

All runs on the release branch at 15cc747, read-only, with scratch scripts under `<scratchpad>`; nothing in the repo or on the host changed.

A. **Repo.** PR #26 merged 2026-11-08 as 15cc747; `git tag --points-at 15cc747` is `r25.x`; `gh release view r25.x` is "r25.x: Retro and QA sweep". The r25 plan still shows C6 and C7 `todo`; `iteration-plan.md` shows "r25 (active)" and PDP-021 `active`. Hub PR #63 (r25's URL fix) is merged; hub PR #62 ("Python book no longer cites Mythical Man-Month or Code Complete") was open at planning and has since merged as 9a3b034 (O4). Reconciliation rows run to 469, so r26 starts at 470. Step-row prefixes used in plans: A, C, D, G to N, P to Z. B, E, F and O have no step row; `grep -rnE '(run: |^\| )B[0-9]' _plans/` prints nothing, while E appears as row ids (`E11-1`) in the r24 census, so r26 uses B. `validate.py`: 0 errors, 6 warnings (all six are the appendix floors).

B. **Book baseline** (`scan.sh --terse-stats _docs`; median of 47 files, TESTS summed): WORDS 2,200, SECMED 228, LEAD 102, PAR 48, ABSTR/k 2.9, TESTS 1,030. `scan.sh --tier terse _docs`: 177 lines in 8 patterns (0 ban-tier). With a project row for "the bucket is", "sorts it" and "the force behind" the total is 209 (32 more lines in 14 files).

C. **Pilot baseline.** Words are `validate.py`'s count; the other columns are `--terse-stats` and `--stats`.

   | Doc | Words | SECMED | LEAD | PAR | ABSTR/k | TESTS | LEN med (p10 to p90) | "force(s)" |
   | --- | --- | --- | --- | --- | --- | --- | --- | --- |
   | 01 | 2,484 | 258 | 258 | 84 | 20.9 | 0 | 19 (7 to 33) | 43 |
   | 03 | 2,388 | 214 | 172 | 58 | 14.5 | 1 | 18 (8 to 34) | 23 |
   | 23 | 2,144 | 301.5 | 118.5 | 35.5 | 8.1 | 31 | 17 (7 to 31) | 2 |
   | 24 | 2,273 | 273 | 102 | 46 | 4.4 | 36 | 18 (8 to 40) | 1 |

   Invariant baselines (prose only, fences excluded): fenced blocks 0, 6, 13, 9; distinct test names 0, 1, 27, 39; URLs 0, 5, 2, 11; `relative_url` targets 2, 25, 5, 5; quoted strings of 6 or more words 0, 2, 3, 20; digit tokens 4, 10, 13, 63; walk-throughs 0, 0, 1, 1. Terse-tier hits: 01 has 7, 03 has 3, 23 has 9, 24 has 10; the provenance hits in each "For deeper coverage" and the hits on the chapter title "What 1994 assumed, and what Python dissolves" are correct as written.

D. **Validator facts.** `MIN_WORDS = 1900` is a warning and `MAX_WORDS = 2500` an error (`check_prose`). Nothing checks test names in prose: 1,133 backticked `test_*` tokens on non-fenced lines (tables included; the scanner skips tables and `>` lines, hence 1,030), and every one is a defined test except `test_model` in `00.md:91`, a module name. `--claims`: 1,191 test tokens across the rows; 61 don't appear in their chapter (45: 33, 2: 15, 46: 6, 3: 2, others 1 each), most of them cross-example witnesses; 8 are defined in the chapter's own example (rows 195, 308, 310 five times, 314; chapters 34, 46, 0). CI's `validate` job uses a default (shallow) checkout.

E. **What depends on pilot wording.**
   - Reconciliation rows: chapter 1: 313; chapter 3: 3, 4, 316, 317; chapter 23: 120 to 125, 133, 341, 342, 348; chapter 24: 126 to 133, 343.
   - Deck 101's witness census (`_plans/evidence/r22-deck-witness-census.md`) greps chapter sentences: 3 in 01, 8 in 03, 6 in 23, 6 in 24. Deck 101 copies 03's map table cells verbatim (census line 925).
   - Appendix E: 98 Bucket, Force and When-not cells, each verbatim in its developing chapter today; rows 68 (Chain of Responsibility), 69 (Mediator) and 70 (Iterator) come from 23 and 24.
   - No fragment link (`/docs/NN-slug/#id`) points into a pilot doc; titles don't change, so the 26 docs that link to them are unaffected.

F. **Carried items.**
   - Feathers title, old form "I Need To Make a Change but I Don't Know What Tests To Write": `git grep` gives 2 in `_docs/34` (lines 32, 268), 3 in `_docs/35` (34, 43, 232), 1 in `presentation/deck-301.js:192` and the Deck 301 `.pptx`. The plans and evidence that quote it (r16, r17, the r24 census) are history and stay.
   - `_layouts/default.html` emits `<meta name="description">` at lines 7 and 8, and `{% seo title=false %}` at line 9 emits a second one.
   - Typography: the docs write straight apostrophes in their own prose. A curly `’` appears only inside verbatim quotations of sources (21 lines in 12 docs, such as `33.md:159`, `37.md:52`, `42.md:104`), which keep the source's typography.

H. **Owner checks in O'Reilly** (2026-11-08, the owner's own account; O'Reilly answers 403 to scripted requests, so a script can't fetch these pages).
   - **The Feathers title.** Chapter 13 of *Working Effectively with Legacy Code* (https://learning.oreilly.com/library/view/-/0131177052/) is titled "I Need to Make a Change, but I Don’t Know What Tests to Write": the book prints a curly apostrophe. The owner chose the book's straight house form, "I Need to Make a Change, but I Don't Know What Tests to Write" (O3). This is the evidence for CA1. B2a copies this entry into `_plans/evidence/r26-pilot.md` ("Owner checks"), which row 473 cites.
   - **The O'Reilly links.** The three canonical links r25 put in `bibliography.html` (Architecture Patterns with Python, Effective Python, Python Object-Oriented Programming) and the uncanonical `/library/view/-/<isbn>/` originals all open their book pages. This stands as the owner's check of r25's LK2, which the r25 link sweep could follow only by redirect.
   - **Route for O'Reilly facts from now on.** The book's HTML page on O'Reilly lists the chapter titles, so an owner check of that page, recorded with its date and URL in the iteration's evidence file, is the evidence for a title or table-of-contents fact. A planner or validator asks the owner for it rather than scripting a fetch.

G. **The style study** (read-only, 2026-11-08, `<scratchpad>/style/`). Against the model books (Camel EIP, cloud-native-design-patterns, datamesh): 1,026 test names inside sentences (models: 0 to 1), 221 "force(s)" (3 to 11), 62 bucket or "force behind" meta sentences, 108 words of lead-in before the first code (Camel 55), median section 244 words (Camel 143), no bold one-line definitions (Camel 3.4 per doc). Sentence length is not the problem: median 18 against the models' 15 to 22. Camel 07 and 09 were read for the target: a bold one-sentence definition, the domain problem, code within a paragraph, comparisons as tables, bold-led "when" bullets.

## Work items

**Gates and tooling (GT)**, built and self-tested before any prose changes.
- GT1: `scripts/prose_invariants.py`, with a `--sections` report (words and lead-in per H3, for T6 under O1), comparing each changed doc with `--base`. It fails on any difference, unless waived, in:
  - the fenced blocks, byte-exact, as a multiset (an order change is reported);
  - the set of test names in prose and on `*Tests:*` lines;
  - the set of link targets: Markdown links, bare URLs, `relative_url` targets, `href`s;
  - the `source:` URLs of the doc's reconciliation rows (each still in the doc);
  - the set of quoted strings of 6 or more words, byte-exact;
  - the multiset of digit tokens in prose (tables, captions and the figure description included);
  - the set of inline code spans;
  - the AI sidebar block, byte-exact;
  - the figure include's `caption`, and every front matter key except `description`.

  Allowed without a waiver: a test name moved onto a `*Tests:*` line, framing deleted, paragraphs and sections reordered, prose turned into a table or list, a walk-through moved into the figure description. Waivers live in one table in `_plans/evidence/r26-pilot.md` (`| doc | kind | value | reason | signed |`), and the script reads it. `--self-test` holds synthetic base and after pairs: one fails for each kind of loss above, and four pass (a moved test name, a deleted framing sentence, a reordered paragraph, a waived removal). Each check is disabled in turn to show the self-test then fails (the r25 mutation proof). Its pure compare function takes two texts and the waivers, so the self-test needs no git. ruff and `mypy --strict` clean (`verify.sh` covers scripts).
- GT2: `validate.py`:
  - drop `MIN_WORDS` and the floor warning; keep the ceiling error; the self-test proves a 1,500-word doc gives no warning and a 2,600-word doc an error;
  - parse `*Tests:*` lines (`*Tests:* `test_a`, `test_b[id]`.`): a blank line before, after a paragraph, list or table, never directly after a heading or fence; every name a defined test (error);
  - for `TERSE_DOCS`, a backticked test name on any prose line except a `*Tests:*` line is an error, counted on the lines `--terse-stats` counts (tables, headings, HTML, Liquid and `>` lines excluded);
  - for `TERSE_DOCS` pattern chapters, the O1 layout: at least one `## Pattern: <Name>` H2, each opening with `### The problem`, `### The solution` and `### How Python models it` in that order; inside `### The solution`, one bold definition and exactly one `**Bucket: (dissolves|survives|needs disambiguating).**` line; every `## Pattern:` H2 between `## Why this matters` and `## When not to use it`; and no "Read the figure" paragraph in the body;
  - a `described="true"` include needs the matching `desc-<name>` description right after it;
  - Appendix E: each Bucket, Force and When-not cell appears verbatim in the doc its Chapter cell links (98 of 98 today);
  - the claims coupling (planner's choices).

  Each new check has a self-test that fails with the check disabled.
- GT3: CI: the `validate` job checks out with `fetch-depth: 0` and runs `prose_invariants.py --self-test` always, and `--base origin/${{ github.base_ref }}` on pull requests. `ci-ok` already depends on `validate`.
- GT4: site. `_includes/excalidraw.html` takes `described`; `assets/css/site.css` styles `.figure-description` (body text size, a summary that reads "Describe the figure"); the duplicate meta goes (decision on the layout above). Verified in the built site: every page has exactly one `<meta name="description">`, its content is listed against the old one for every page and any change explained (a part page that falls back to an excerpt gets its old value as a `description` key); in 23 and 24 the `aria-describedby` id resolves, the description's code spans render as `<code>`, and nothing scrolls sideways at 390 px.
- GT5: `.voice-patterns.tsv` at the root with the project's T11 rows (terse tier: "the bucket is", "sorts it", "the force behind", "That's the force"), used as `scan.sh --tier terse --patterns .voice-patterns.tsv _docs`.
- GT6: CLAUDE.md: the spine (the walk-through moves to the figure description), the word rule (ceiling 2,500, no floor), the `*Tests:*` line, the spine text in "The pattern layout (O1)", "problem before mechanism" for pattern chapters in the Structure line, `TERSE_DOCS`, the invariants script in the per-chapter gates, and a dated r26 note under O2 saying `validate.py` now enforces it.

**Pilot (PL)**, under T1 to T12 and decisions 1 to 4.
- PL1: doc 01. The thesis chapter: framing allowed, "force" and "Consequences" defined once, the four forces and the three shapes as tables, no T1 block. Targets in decision 2.
- PL2: doc 03. The map chapter: bucket framing allowed, the map table byte-identical, the two sorting questions and the disambiguation entries bold-led. Its one in-prose test name (the `_GUARDED` experiment) moves to a `*Tests:*` line.
- PL3: doc 23. The O1 layout with two `## Pattern:` H2s, the walk-through to the description, 31 test names onto `*Tests:*` lines, both experiments still re-runnable from their sentences.
- PL4: doc 24. The O1 layout with one `## Pattern: Iterator` and four topic H3s; quotations to one per H3 under decision 3; provenance (the GoF credit, PEP authors) to "For deeper coverage".
- PL5: Appendix E rows 68 to 70 take the new wording of 23 and 24, verbatim (decision 5).
- PL6: reconciliation. Every existing row for chapters 1, 3, 23 and 24 (evidence E) is re-read against the new text and gets an r26 note (claim unchanged, or adjusted with the new wording). New rows for each claim the pilot changed or added: each bold definition and Bucket line, the Appendix E rows, and the gates.
- PL7: the 23 deck-census sentences (evidence E) each get the new sentence that carries the same fact, re-grepped, in the evidence file. The census file itself is history and stays.

  Each pilot executor records, for its doc: base and after words, `--terse-stats`, `--stats`, terse-tier hits (fixed or kept, with a reason), the invariants result and every waiver.

**Carried (CA)**
- CA1: the Feathers title to the owner's form, "I Need to Make a Change, but I Don't Know What Tests to Write", straight apostrophe (O3, evidence H). A count-asserted replace: exactly 2 hits in `_docs/34`, 3 in `_docs/35` and 1 in `presentation/deck-301.js`, then 0 of the old form in any tracked file outside `_plans/`. Deck 301 is rebuilt and run through the r25 deck pipeline on the changed notes page; 101 and 201 are untouched.
- CA2: the duplicate meta (GT4).

**Bookkeeping (BK)**
- BK1: the r25 plan's C6 and C7 set to `done`, with a dated Corrections note: PR #26 squash-merged as 15cc747, tagged `r25.x`, notes-only release "r25.x: Retro and QA sweep", hub PR #63 merged; and under O2, the PRD status says the rewording is in progress rather than complete.
- BK2: `iteration-plan.md`: PDP-021 `done`, r25 closed, PDP-022 `active`, r26 marked active, dated note.

## Before and after, one per doc

Short excerpts showing the target; the executors write the real text.

**01, line 45** (T2, T7):
> **Carrier tariffs change on the carrier's schedule.** A carrier such as FASTLINE or AIRCO publishes a `Tariff`: a price for each combination of zone and weight band. The carrier reissues it when it chooses, often on a fixed date each year, and sometimes with little warning in between. Nothing in your codebase decides when this happens. The force is that the largest block of numbers feeding every quote is owned by someone outside the team.

> **Carrier tariffs change on the carrier's schedule.** A carrier such as FASTLINE or AIRCO publishes a `Tariff`: a price for each zone and weight band. It reissues the tariff when it chooses, often on a fixed date each year, sometimes at short notice. Your code doesn't decide when. So someone outside the team owns the largest block of numbers in every quote.

**03, line 37** (T3, T5; framing allowed, the fact Deck 101 cites kept):
> Two precautions keep the second question strict. A feature resolves a force only when it resolves all of it, not just the easy half. And "dissolves" never means "forget it": the force remains, and the vocabulary is still useful when a team talks about it. What dissolves is the class structure the catalogue drew around the force.

> Two rules keep the second question strict:
> - **All of it.** A feature resolves a force only if it resolves all of it, not just the easy half.
> - **"Dissolves" never means "forget it".** The force remains, and a team still uses the name. Only the catalogue's class structure goes.

**23, line 67** (T8, T5), landing under `## Pattern: Chain of Responsibility`, `### How Python models it`:
> The first stage that decides wins. `test_the_first_stage_that_decides_wins` gives a declaration with no documents and unpaid duty, and the reason is the missing invoice, because `check_documents` runs before `assess_duty`. Stages after the winner don't run: `test_stages_after_a_decision_are_not_called` records the names of the stages that were called and gets `["passing", "holding"]`, with a third stage left out. A clean declaration reaches the final stage and is released (`test_a_clean_declaration_is_released`). [...]

> The first stage that decides wins. A declaration with no documents and unpaid duty is held for the missing invoice, because `check_documents` runs before `assess_duty`. Later stages don't run: the recorded calls are `["passing", "holding"]`, without the third stage.
>
> *Tests:* `test_the_first_stage_that_decides_wins`, `test_stages_after_a_decision_are_not_called`.
>
> A clean declaration reaches the final stage and is released. [...]

**24, lines 22 and 47** (O1 layout, T9, T11; a waived quotation and a waived duplicate number):
> A tracking history is read page by page by a display and a report. Both want the events one at a time and neither should care how the history stores them. That's the force behind Iterator, and Python resolves it inside the language: a generator function writes the cursor for you. [...]
>
> A function with `yield` is a generator function, and calling it returns a generator iterator. The glossary says "Each yield temporarily suspends processing, remembering the execution state (including local variables and pending try-statements)." The suspended frame holds the position a cursor class would keep in a field. Schemenauer, Peters and Hetland introduced generators in PEP 255, "Simple Generators". The bucket is dissolves, as the sorting in [What 1994 assumed, and what Python dissolves](...) puts it.

> ## Pattern: Iterator
>
> ### The problem
>
> A display and a report read a tracking history page by page. Both want the events one at a time, and neither should care how the history stores them.
>
> ### The solution
>
> An **Iterator** walks a collection without exposing how it's stored.
>
> **Bucket: dissolves.** A generator function writes the cursor for you.
>
> ### How Python models it
>
> ```python
>     def __iter__(self) -> Iterator[HandlingEvent]:
>         yield from self._events
> ```
>
> A function with `yield` is a generator function, and calling it returns a generator iterator. Each `yield` suspends the function and keeps its local variables and pending `try` statements, so the frame holds the position a cursor class kept in a field.

   The PEP 255 credit joins its link in "For deeper coverage". Waivers: the glossary quotation (paraphrased; the glossary link stays), and one "255" (the number now appears once, beside its link).

## The owner's reading packet

The top section of `_plans/evidence/r26-pilot.md`, one screen per doc, written at B4a and finished at B6:
- before and after `--terse-stats`, `--stats` LEN and words, with each target from decision 2 and the list below marked met or missed, and every miss explained in one line;
- the waiver count and each waiver's reason;
- two links: the doc's diff in the PR (`.../pull/<n>/files#diff-<sha256 of the path>`, GitHub's file anchor) and the doc on the branch;
- the four before and after excerpts above, replaced by the real ones.

Targets: TESTS 0 (gate); LEN median at most 15, p90 at most 30 (T4); PAR at most 40 (T5); per H3 (GT1's report), lead-in at most 60 and section at most 150 for `### How Python models it` and topic H3s, `### The problem` at most 3 sentences and `### The solution` at most 2 plus the Bucket line, with `--terse-stats` LEAD and SECMED recorded per H2 (T6); ABSTR/k at most 1.5 in 23 and 24, and decision 2's budgets in 01 and 03 (T7); no floor, the 2,500 ceiling, and a 1,600-word aim for 23 and 24 (T12, the study's figure, not a gate).

**The question for the owner:** go, or adjust? Go means r27 applies T1 to T12 as piloted to the 21 pattern chapters. Adjust means naming the rules to change (for example the Bucket line, the quotation budget, the `*Tests:*` form or a target); r26 then applies the change to the four docs in one more round, with a confirmation, before the merge.

## Acceptance criteria

1. The gates land before any prose: GT1 to GT6 are merged on the branch before the first PL commit (`git log`).
2. `prose_invariants.py --self-test` passes, and fails with each check disabled (recorded); CI runs it on the PR.
3. `validate.py`: no floor (the six appendix warnings are gone), the ceiling error kept, and every new GT2 check passing on the tree, each with a self-test that fails when the check is disabled.
4. The four pilot docs: TESTS 0; `prose_invariants.py --base 15cc747` passes with only waivers the facts reader signed; the sidebars byte-identical and `grep -c` 1 in 23 and 24; captions and 03's map table byte-identical; spine headings present; 23 and 24 in the O1 layout (GT2's check); 23 and 24's walk-throughs in the figure description, with `aria-describedby` resolving in the built HTML.
5. Every claim keeps its witness: the facts and sources readers pass; `--claims` has 0 unresolved; every row in evidence E carries an r26 note; new rows from 470 resolve.
6. Appendix E: 98 of 98 cells verbatim (the GT2 check).
7. CA1: the counts asserted (2, 3, 1), the new form byte-equal to O3's straight-apostrophe title, 0 old forms outside `_plans/`, Deck 301 rebuilt and through the deck pipeline, 101 and 201 unchanged.
8. Every built page has exactly one `<meta name="description">`; changed contents are listed and explained.
9. BK1 and BK2 done; no stale status in the plans.
10. All gates green (QA step 2) and `ci-ok` green on the PR.
11. The reading packet is complete; the owner's go or adjust answer is recorded under "Owner decisions".
12. Every QA round, repair and confirmation is recorded in `_plans/evidence/r26-pilot.md`, and a confirmation follows the last repair.
13. The owner approves the merge; `r26.x` is on main; the release is notes-only.
14. No worktree, process or scratch tree left behind.

## QA pipeline

1. **Isolation.** Each parallel executor gets its own git worktree (`isolation: worktree`) and commits there. The orchestrator merges the worktree branches into `release/r26` one at a time, then removes the worktree. Nobody runs `git stash`, `git pull --autostash`, `git reset` or `git checkout` on files they don't own (r25 lost work to two of these). Only the orchestrator writes `_plans/`, the reconciliation table, the evidence file and doc 45; executors hand their records over as text. Integration gates run only when `git worktree list` shows the main tree alone, because worktrees inside the repo would be scanned by ruff, `host_ids` and the voice scan.
2. **Gates:** `bash scripts/verify.sh` (no example changes expected: `git diff --stat 15cc747 -- examples spikes` empty); `uv run python scripts/validate.py` with `--self-test` and `--claims`; `prose_invariants.py --self-test` and `--base 15cc747` over the changed docs; `python3 scripts/host_ids.py check`; the repo-wide ban gate from CLAUDE.md; `scan.sh --stats`, `--terse-stats` and `--tier terse --patterns .voice-patterns.tsv` over `_docs`, before and after; `bash scripts/site-build.sh` with `Gemfile.lock` unchanged and the GT4 checks on the built pages; the deck pipeline for 301 (CA1).
3. **Experiments.** The five experiments in 03, 23 and 24 are re-run in a fresh copy from the rewritten sentences, and must give the quoted output. The fences are byte-identical by GT1, so no other output is re-run.
4. **Independent Opus readers**, separate agents that never see each other's findings or this plan's conclusions:
   - **facts reader**: base against new, paragraph by paragraph, for all four docs: no fact dropped, none added, every moved number bound to its noun, every bold definition and Bucket line supported by the base text, each waiver signed or refused;
   - **register reader**: the new docs alone, against T1 to T12 and the house-voice rubric, as an engineer meeting them cold: plain, readable, no choppy fragments left by deletion, no philosophy;
   - **sources reader**: each `*Tests:*` line against the bodies of the tests it names (do they assert the paragraph's claim?), every paraphrased quotation against the fetched page, at least one in three named tests re-run, and the built pilot pages at 1280 and 390 px.
5. **Opus validation:** every criterion and work item, the readers' findings, named "blocking item N of round M".
6. **Repair and confirmation:** at most two repair rounds. After each, a fresh Opus confirmation that didn't do the repair re-runs step 2, re-reads every changed sentence against its witness, and supplies tested replacement strings for anything it fails; they're applied verbatim with an exact-match assert. A confirmation follows the last repair too. An "adjust" round from the owner follows the same rule.

## Steps and status

Only suffixed ids are cited as `run:` tokens: B1a to B1d, B2a, B3a to B3e, B4a, B5a.

| id | what | depends on | status |
| --- | --- | --- | --- |
| B0 | Bookkeeping BK1 and BK2; record the owner's decisions; evidence file started with the baseline (evidence B, C) | - | done |
| B1a | `validate.py` GT2 and CLAUDE.md GT6, with self-tests and the mutation proof (worktree) | B0 | done |
| B1b | `prose_invariants.py` GT1 and CI GT3, with self-tests and the mutation proof (worktree) | B0 | done |
| B1c | Site GT4 and `.voice-patterns.tsv` GT5; a site build and the built-page checks (worktree) | B0 | done |
| B1d | Orchestrator: merge B1a to B1c in that order, remove the worktrees, run QA step 2 on the unchanged docs (everything green, the invariants check finds no change) | B1a, B1b, B1c | done |
| B2a | CA1, the Feathers title, with Deck 301's rebuild and pipeline (worktree); the evidence H owner checks handed to the orchestrator for the evidence file | B0 | done |
| B3a | Doc 01, PL1 (worktree), committed as bfd43f5 | B1d | done |
| B3b | Doc 03, PL2 (worktree), committed as 1da9483 | B1d | done |
| B3c | Doc 23, PL3 (worktree), committed as de7c17f | B1d | done |
| B3d | Doc 24, PL4 (worktree), committed as 077cc25 | B1d | done |
| B3e | Orchestrator: merge B2a and B3a to B3d, remove the worktrees, then PL5 (Appendix E rows 68 to 70), committed as ba96856 | B2a, B3a to B3d | done |
| B4a | Integration: QA steps 2 and 3, PL6 rows, PL7 census, the reading packet drafted | B3e | done |
| B5a | Readers and validation (QA steps 4 and 5) | B4a | todo |
| B5b | Repairs, at most two, each with its confirmation (QA step 6) | B5a | todo |
| B6 | PR, `ci-ok` green, reading packet linked; ask the owner: go or adjust, then the merge. An adjust round follows QA step 6 | B5b | todo |
| B7 | After the owner's word: squash-merge, delete the branch, tag `r26.x`, notes-only release; `iteration-plan.md` closes r26; the PRD status line updated | B6 | todo |

## Reconciliation rows

Rows 470 onward go in at B4a with resolving tokens; "Sweep:" rows start `open` and B5a closes them.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 470 | 1, 3, 23, 24 | Sweep: the reworded docs keep every fenced block, test name, link, `source:` URL, long quotation, number, inline code span, sidebar and caption of 15cc747, apart from signed waivers | run: B4a, run: _plans/evidence/r26-pilot.md |
| 471 | 1, 3, 23, 24 | Sweep: no test name inside a sentence; every `*Tests:*` name is a defined test that asserts its paragraph's claim | run: B1a, run: B5a |
| 472 | 45 | Every Bucket, Force and When-not cell of Appendix E is verbatim in its developing chapter | run: B1a, run: B3e |
| 473 | 34, 35 | The Feathers chapter is titled "I Need to Make a Change, but I Don't Know What Tests to Write" (owner check in O'Reilly, 2026-11-08: the book's curly apostrophe in the house's straight form) | run: B2a, run: _plans/evidence/r26-pilot.md |
| 474 | 0-46 | Every built page has one `<meta name="description">` | run: B1c |

Then one row per bold definition and Bucket line the pilot adds, each with the test or `source:` token that witnesses it, and the r26 notes on the rows in evidence E.

## Risks

- **A fact lost in the rewrite.** The invariants catch tokens, not meaning. Mitigation: the facts reader, paragraph by paragraph, and the claims coupling rule.
- **Waivers as a loophole.** Mitigation: every waiver has a reason, the facts reader signs it, and the packet shows the count per doc.
- **Fragments.** Deleting framing can leave choppy text. Mitigation: the register reader reads cold.
- **Shared tree.** r25 lost work twice to `stash` and `--autostash`. Mitigation: worktrees, the forbidden commands, one owner per shared file (QA step 1).
- **Worktrees under the repo** get scanned by the integration gates. Mitigation: gates run only with the main tree alone.
- **Verbatim followers.** Appendix E, Deck 101's map table and the deck census copy chapter text. Mitigation: the Appendix E check, 03's table frozen, PL7.
- **kramdown and `<details>`.** `markdown="1"` inside `<details>` may not parse. Mitigation: GT4 checks the built HTML; the fallback is `markdown="block"` on the inner `div`.
- **The measurement counts the description.** `--terse-stats` counts the description's words in the section that holds the figure. Mitigation: the packet reports that section's words with and without it.
- **The owner adjusts the rules.** Mitigation: one adjust round in r26, confirmed, so r27 starts from a pilot that matches the rules.

## Corrections

- Step B0: done (2026-11-08).
  - BK1: the r25 plan's C6 and C7 are `done`, with a Corrections note (PR #26 as 15cc747, tag `r25.x`, hub PRs #63 as 903c077 and #62 as 9a3b034). The PRD status line (O2) lives outside the repo and is not changed by B0.
  - BK2: `iteration-plan.md` shows r25 closed, r26 active, PDP-021 `done`, PDP-022 `active` (added in the infrastructure range), and a dated note.
  - The owner decisions O1 to O4 are copied into `_plans/evidence/r26-pilot.md`, which also holds the baseline (evidence B, C) from a fresh run.
  - Differences from the plan, none affecting a target: "force(s)" counts 49, 24, 2, 1 against the plan's 43, 23, 2, 1 (counting rule), and terse-tier hits 8 and 9 in 23 and 24 against 9 and 10. Everything else matches. The invariant baselines wait for `prose_invariants.py` (B1b).
- Step B1a: done at a0b91bc. `validate.py` has no floor (the 6 warnings are gone), keeps the ceiling, parses `*Tests:*` lines everywhere and enforces test-name, O1 layout and described-figure rules for `TERSE_DOCS` (empty until the pilot lands). Appendix E: 98 of 98 cells verbatim. The "force" rule (whole word, case-insensitive, excluding fences, inline code, blockquotes and front matter) gives 46, 24, 2 and 1 for docs 01, 03, 23 and 24 (reported by `--force-count`, not a gate). CLAUDE.md updated.
- Step B1b: done at 36f51c6. `scripts/prose_invariants.py` checks fences, test names, links, `source:` URLs, quotations of 6 or more words, numbers, inline code, the sidebar, captions and front matter (all but `description`), reads signed waivers, and gives `--sections` (per H3) and `--baseline`. 24 self-test cases each fail when their check is removed. The unchanged tree shows no difference for all 47 docs. CI runs the self-test always and the merge-base comparison on PRs (`fetch-depth: 0`); `ci-ok` is unchanged.
- Step B1c: done at 411ebd8. The figure walk-through mechanism: `described="true"` adds `aria-describedby`, with a collapsed `<details class="figure-description">`, proven on a scratch page; unchanged docs render byte-identically. One `<meta name="description">` and one `<title>` on all 108 pages. `.voice-patterns.tsv` has four T11 rows. Regression: seo-tag's markdown step dropped dunder underscores on four pages, fixed at B1d.
- Step B2a: done at d7a4033, merged at B1d, not at B3e: its files don't overlap the pilot. The Feathers title (O3, straight apostrophe) is replaced 2 times in doc 34, 3 in doc 35 and 1 in `deck-301.js`, with the old form now at 0. Deck 301 is rebuilt: only `docProps/core.xml` and notes slide 19 differ, `render-png.sh --check` reports the same for 2, and Decks 101 and 201 are identical apart from `core.xml`.
- Step B1d: done (2026-11-08). The claims coupling the plan describes is in `validate.py` (`coupling_checks`, `load_coupling`): for a doc in `TERSE_DOCS`, each reconciliation row's test token defined in the chapter's own example must appear in the chapter, on a `*Tests:*` line or elsewhere. Its self-test fails with the check disabled, and with `TERSE_DOCS` empty it reports nothing. In a scratch run with `TERSE_DOCS` {1, 3, 23, 24} it checks 0, 27, 33 and 39 (token, doc) pairs for docs 1, 3, 23 and 24, 99 in all, with 0 misses now. The dunder regression is fixed in the front matter of docs 10 and 30 and examples 29 and 30 by writing the underscores as `&#95;` entities: seo-tag's markdown step turns them back into `__` in the meta description, and the page lead and part-page cards render them as `__` in the browser; no other `description` has a markdown-sensitive character (`blurb` and `card_blurb` are not run through markdown). `prose_invariants.py` skips `description`, and `validate.py` and the voice scan accept the entities. `prose_invariants.py` joins the mypy line in `verify.sh`. Evidence file: owner checks, invariant baseline (doc 24 has 35 test names, not 39: 4 were module filenames) and the `.voice-patterns.tsv` count (217 lines, 207 without the double count, against 177). Deck 301 slide 29 is a divider (panel fill AB0000, floor 45) with 74 notes words, and `check_decks` covers it. Steps B1a to B1d and B2a are `done`.
- Step B4a: done (2026-11-08), committed with this note. B3a to B3e are `done`: PL1 bfd43f5 (doc 01), PL2 1da9483 (doc 03), PL3 de7c17f (doc 23), PL4 077cc25 (doc 24, with Appendix E row 70's Bucket cell) and PL5 ba96856 (Appendix E rows 68 to 70). B4a ran QA steps 2 and 3, PL6, PL7 and drafted the reading packet; every record is in `_plans/evidence/r26-pilot.md`.
  - Waivers: the 12 rows of doc 24 are in the waiver table, `signed` still `pending`; in a scratch copy with a signature, `prose_invariants.py 24` reports "12 waived". The facts reader signs them at B5a. `--all` therefore fails only on doc 24, with those 12 losses (10 quotations, the numbers 255 and 1994).
  - Experiments: the two in chapter 23 and the two in chapter 24, re-run in scratch copies from the rewritten sentences, give the quoted output (only the timings differ). Chapter 3's `_GUARDED` experiment was outside B4a's scope and was not re-run.
  - Built pages: docs 23 and 24 (and 03) carry `aria-describedby` with a matching id inside a collapsed `<details class="figure-description">` that renders as HTML; at 390 px an opened one fits (headless Firefox, measured numbers, not seen by eye); every `*Tests:*` line renders as an italic label then code spans. The 1280 px view is left to the sources reader.
  - Gates: `verify.sh` 1407 passed; `validate.py` 0 errors, 0 warnings, `--self-test` and `--claims` pass; `prose_invariants.py --self-test` passes; `host_ids.py check` 0 hits; the ban scan 0; `ruff format --check` clean; `site-build` ok with the lock unchanged; `render-png.sh --check` same for decks 101, 201 and 301.
  - PL6: rows 3, 4, 120 to 133, 313, 316, 317, 341 to 343 and 348 carry an r26 note (every claim unchanged). Rows 470 to 483 are added; 470, 471 and 475 to 479 are `open` for B5a. Row 471 omits the plan's `run: B5a` token, because `--claims` resolves a step only once it is `done`; B5a closes the row.
  - PL7: 23 census sentences (3, 8, 6, 6), each new string one `grep -cF` hit; 9 changed, 14 unchanged; the total equals the plan's 23.
  - Differences from the plan: the rows' count is 14 (470 to 483), not 5, because each bold definition and Bucket line, the doc 3 fact fix, the built-page checks and the census get a row. The step table's "(worktree)" wording is stale since O5 and is left as it was.
