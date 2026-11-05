---
title: "r10b plan: retrofit chapters 0-20 to lgtm-professional-voice #94-#96"
order: 10
output: false
render_with_liquid: false
---

# r10b: retrofit chapters 0-20 to the updated voice rules

Opus-planned 2026-11-05. Branch `release/r10b`, cut from main at b7e2a71 (the r10 merge, tagged r10.x). This file is the source of truth for r10b scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

Scope: prose in `_docs/00-*` to `_docs/20-*`, the example cards under `_examples/`, and the five pre-existing ban-tier hits plus two more the root scan finds (item 5). No toolchain work, no new tests, no figure changes. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3 and uv 0.13.7 are unchanged, and `uv.lock` must not change.

The rules come from lgtm-skills #94 (9c69056: intent before mechanism, no re-narration after code, no reference to something not set up, philosophy-teacher and self-validation catches), #95 (7682413: AI sidebar as problem, ready-to-paste prompt, one review line) and #96 (705ffc8: explain by example, objective-payoff close). #93 (185e5b1) added the importance-assertion flourish family, and #89 (165d381) moved the scan to the repo root. The repo's `CLAUDE.md` already carries the sidebar and structure rules and says chapters 0-20 are retrofitted in a separate iteration. Chapters 21-22 are the model.

## User decisions (owner confirmed 2026-11-05: all ten as recommended)

Standing, not a decision: step ids are `L*`. `grep -nE "^\| L[0-9]" _plans/*.md` matched nothing before this file, so `validate.py --claims` sees no collision.

1. **Every chapter 0-20 gets the objective-payoff close as a new `## What you can do now` heading**, placed directly before `## For deeper coverage` (after `## Build, run, observe`, and after `## Teardown` in chapter 0), with one bullet per learning objective, as in 21-22. This includes chapter 0 (prerequisites), the argument chapters 1-4 and the SOLID chapters 5-6. **Recommend: yes.** `validate.py`'s `check_spine` only tests that the required headings are present (a set, not an order), so an extra heading passes every kind today. Alternatives:
   - (b) Skip chapter 0. It is a setup chapter whose `## Teardown` already ends it, and its objectives map to commands rather than designs. The rule in `surfaces.md` says "close a chapter", with no exception for setup chapters.
   - (c) Skip the argument chapters 1-4, whose artifacts are worked cases and tables rather than tests. They still have artifacts (the rate-quote force analysis, the bucket table, the nineteen-test example in chapter 3), so the close is still possible.
2. **Make the close a spine heading in `validate.py`** by adding `"What you can do now"` to `SPINE["argument"]`, `SPINE["hands-on"]` and `SPINE["pattern"]` (not `"appendix"`), after L1 lands. **Recommend: yes, as an error.** Stubs 23-46 are `status = "stub"`, so `check_spine` doesn't run on them until they are drafted, and the self-test builds `full_spine` from `SPINE["pattern"]`, so it picks up the new heading by itself. This is a tooling change outside the prose-only scope, so it needs the owner's approval. Alternatives: a warning only; or leave `validate.py` alone and rely on criterion 5's script.
3. **No AI sidebar is added to chapters 0-4.** **Recommend: yes.** `validate.py` requires exactly one sidebar only for `kind == "pattern"` (chapters 12-20, which all have one). Chapter 0 (hands-on) and 1-4 (argument) are not checked, so having none is valid. Chapter 4 is the AI-naming chapter: its sections "Steering an AI assistant with names" and "Reviewing a name an assistant attached to its output" already are the sidebar's content, and it has 53 words of headroom. Alternative: add a sidebar to chapter 4 for consistency. That costs about 120 words, which means cutting a further 120 in a chapter that already needs about 140 cut.
4. **The hands-on chapters 5-11 keep their sidebars and convert them.** `validate.py` doesn't require them there, and `CLAUDE.md` says "one per pattern chapter". **Recommend: keep and convert.** Alternative: drop them. That would save 64-109 words each, and about 77 in chapter 11, the tightest chapter, but each one carries a decision rule the reader can use.
5. **The two r10 test-comment hits** (`examples/21-composite-and-flyweight/tests/test_flyweight.py:41` and `examples/22-observer/tests/test_lifetime.py:2`, "collect(s) deliberately"). Both are ban-tier, and neither is in the brief's list. The chapter 21 comment is quoted verbatim in the excerpt at `_docs/21-composite-and-flyweight.md:180`, so fixing it changes a quoted excerpt. **Recommend: reword to "collect explicitly" in both files and in the chapter 21 excerpt, in lockstep.** The excerpt stays byte-identical to its source, which is what the excerpt rule protects. The chapter 22 docstring is not quoted anywhere. Alternative: accept both as rule 2's permitted "once, with a reason" use and record that in Corrections. The canonical ban gate in criterion 10 then can't exit 0 without excluding test files.
6. **Two prose precision fixes.** `_docs/02-*.md:126` ("a mock object is typed as `Any` by the checker") and `_docs/06-*.md:149` ("to mypy, a mock is `Any`") contradict the spike finding in `CLAUDE.md` ("Mocks are assignable to every type, not literally `Any`") and chapter 11's own typeshed quotation (lines 129-133: `class NonCallableMock(Base, Any)`). **Recommend: reword both to "a mock is assignable to every type, so mypy checks nothing at the call site"**, which chapter 11 backs. The orchestrator adds a dated note to reconciliation row 35, whose text says "is `Any` to mypy". The tests are unchanged. Alternative: leave them under "facts stay put" and defer to a later iteration.
7. **Scan-gate exclusions.** Exclude `LICENSE-docs.md`, `CLAUDE.md`, `validate.py` and `host_ids.py` from the ban gate, and reword the one real phrase in `CLAUDE.md`. See the item 5 triage below. **Recommend: yes.** Alternative: rewrite `CLAUDE.md:99` so it doesn't spell the banned word. That reads badly in a file whose job is to name the banned words.
8. **Retitle the four example cards whose titles carry test counts** (03 "nineteen witnesses", 05 "fourteen witnesses", 06 "thirteen witnesses", 07 "twenty-two witnesses", plus their `card_title`s) to concept titles, as cards 08-22 already have. **Recommend: yes.** Rule 5 says a title names the concept, the counts go stale when a test is added, and "witnesses" is book-internal jargon. Alternative: keep them. The counts are correct today.
9. **No code callouts.** `surfaces.md` says to explain through `#A`/`#B` callouts. This book's excerpts are byte-exact copies of tested source, and r10b changes no fenced code. **Recommend: cut re-narration only, and add no callouts in r10b.** Alternative: a later iteration adds callout comments to the source and the excerpts in lockstep.
10. **Tag `r10b.x`** on main after the squash merge, from branch `release/r10b`, with a notes-only release. **Recommend: yes.** Alternative: `r10.1`.

## Planning evidence

All measured on main at b7e2a71, 2026-11-05.

### Word counts (`v.word_count`, the gate validate.py uses)

Command: `uv run python -c "import sys; sys.path.insert(0,'scripts'); import validate as v, pathlib; [print(p.name[:2], v.word_count(p.read_text())) for p in sorted(pathlib.Path('_docs').glob('[012]*.md'))[:21]]"`

Close cost is estimated at 19 words per objective (chapter 21's close is 121 words for 6 objectives, chapter 22's is 96 for 5). The sidebar cap is 120 words (21 has 115, 22 has 118). The handback target is at most 2,470 words, which leaves a 30-word margin for repair rounds.

| Ch | Kind | Words | Headroom | Objectives | Sidebar words | Estimate with close and new sidebar | Cut needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00 | hands-on | 2144 | 356 | 6 | - | 2258 | none |
| 01 | argument | 2446 | 54 | 6 | - | 2560 | at least 90 (plan 110) |
| 02 | argument | 2269 | 231 | 5 | - | 2364 | none |
| 03 | argument | 2355 | 145 | 6 | - | 2469 | plan 60 for margin |
| 04 | argument | 2447 | 53 | 7 | - | 2580 | at least 110 (plan 150) |
| 05 | hands-on | 2257 | 243 | 5 | 101 | 2371 | none |
| 06 | hands-on | 2271 | 229 | 5 | 109 | 2377 | none |
| 07 | hands-on | 2073 | 427 | 5 | 66 | 2222 | none |
| 08 | hands-on | 2095 | 405 | 5 | 72 | 2238 | none |
| 09 | hands-on | 1926 | 574 | 5 | 82 | 2059 | none |
| 10 | hands-on | 2045 | 455 | 5 | 64 | 2196 | none |
| 11 | hands-on | 2489 | 11 | 6 | 77 | 2646 | at least 176 (plan 185) |
| 12 | pattern | 2045 | 455 | 5 | 102 | 2158 | none |
| 13 | pattern | 1980 | 520 | 5 | 90 | 2105 | none |
| 14 | pattern | 2434 | 66 | 5 | 89 | 2560 | at least 90 (plan 120) |
| 15 | pattern | 2134 | 366 | 5 | 89 | 2260 | none |
| 16 | pattern | 2000 | 500 | 5 | 91 | 2124 | none |
| 17 | pattern | 2193 | 307 | 5 | 67 | 2341 | none |
| 18 | pattern | 2326 | 174 | 4 | 84 | 2438 | plan 35 for margin |
| 19 | pattern | 2099 | 401 | 5 | 95 | 2219 | none |
| 20 | pattern | 2448 | 52 | 4 | 107 | 2537 | at least 67 (plan 85) |
| 21 | pattern (model) | 2391 | 109 | 6 | 115 | has close (121) | - |
| 22 | pattern (model) | 2287 | 213 | 5 | 118 | has close (96) | - |

`validate.py` today: 0 errors, 0 warnings. No chapter is under the 1,900 floor (lowest: 09 at 1,926), and no cut below takes a chapter near it.

### Sidebar inventory

There are exactly 16 sidebars, one each in chapters 05-20, and each sits right after the chapter's "when not to use it" section. Chapters 00-04 have none, which is correct per `validate.py`: the count check runs only for `kind == "pattern"`, and 12-20 each have exactly one. 05-11 (hands-on) have one each, which is permitted but not checked. Every one is in the old checklist form, and none has a nested prompt.

| Ch | Section it follows | Current lead | Current form | Words |
| --- | --- | --- | --- | --- |
| 05 | When the principle costs more than it buys | Reviewing assistant-proposed structure. | "Check three things" plus three questions | 101 |
| 06 | When the principle costs more than it buys | Review checklist for assistant-proposed seams. | "Check three things before accepting" | 109 |
| 07 | When a dunder costs more than it buys | Reviewing assistant-written dunders. | "Check four things" | 66 |
| 08 | When not to use it | Reviewing assistant-written value types. | "Check that ..." run | 72 |
| 09 | When not to use it | Reviewing assistant-written interfaces. | "Check that ..." run | 82 |
| 10 | When not to use it | Reviewing assistant-written cleanup. | "Check:" plus five questions | 64 |
| 11 | When a test proves less than it seems | Reviewing assistant-written tests. | "Check that ..." run | 77 |
| 12 | When not to use it | Reviewing assistant-written strategies. | "Check that ..." run | 102 |
| 13 | When not to use it | Reviewing assistant-written templates. | "Check:" plus five questions | 90 |
| 14 | When not to use it | Reviewing assistant-written state machines. | "Check:" plus five questions | 89 |
| 15 | When not to use it | Reviewing assistant-written commands. | "Check:" plus five questions | 89 |
| 16 | When not to use it | Reviewing assistant-written factories. | "Check:" plus five questions | 91 |
| 17 | When not to use it | Reviewing assistant-written builders. | "Check:" plus five questions | 67 |
| 18 | When not to use it | Reviewing assistant-written singletons. | "Check:" plus five questions | 84 |
| 19 | When not to use it | Reviewing assistant-written adapters. | "Check:" plus five questions | 95 |
| 20 | When not to use it | Reviewing assistant-written wrappers and proxies. | "Check whether ..." run | 107 |

### Voice scan (`bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh`, repo root)

- **Default tiers, root:** 205 matching lines, 26 of them ban-tier. The top watch patterns are defect framing (34), the trailing ", not a Y" kicker (34), ALL-CAPS (17), environment-specific noun (13) and hedging (12).
- **Default tiers, `_docs/00-20` only:** 63 lines, 0 ban-tier. Hits per chapter: 11:7, 01:6, 10:6, 06:5, 18:5, 03:4, 04:4, 05:4, 00:3, 02:3, 09:3, 16:3, 20:3, 08:2, 14:2, 07:1, 12:1, 15:1. Chapters 13, 17 and 19 have none.
- **The new catches, as the scanner counts them in 00-20:**
  - narrates-understanding, the-fix-is-recognizing, self-validation ("that's the right call") and in-every-sense: 0 each;
  - on faith: 1 (`_docs/01-*.md:37`);
  - importance flourish (has teeth, rubber meets the road, real magic, "the X that makes Y work", changes everything, where it gets interesting, that is what matters): 0 each.

  The scanner under-detects these families. The manual read below finds about 45 more instances, and that list, not the scanner count, is the work list.
- **`--stats`, chapters 00-20:**
  - 0 em-dashes, and no chapter is flagged `stiff`.
  - All 21 are flagged `check triads`. Triad candidates: 00:13, 01:9, 02:11, 03:12, 04:9, 05:9, 06:7, 07:8, 08:6, 09:7, 10:6, 11:8, 12:11, 13:4, 14:9, 15:13, 16:10, 17:7, 18:14, 19:16, 20:11.
  - Expanded (uncontracted) forms, used as the baseline for criterion 11: 00:1, 01:0, 02:7, 03:3, 04:10, 05:5, 06:9, 07:4, 08:3, 09:3, 10:0, 11:0, 12:2, 13:2, 14:2, 15:2, 16:1, 17:1, 18:6, 19:0, 20:1.
- **Landing pages:**
  - `index.html`: 0 hits, flagged `stiff` 0/1. The one expanded form is the button "Skip to why this is not a GoF retelling", which echoes the part title "Why This Is Not a GoF Retelling".
  - `_parts/*`: front matter only, 0 hits.
  - `_examples/*`: 5 watch hits (none a defect), and `stiff` on cards 00, 03, 05, 07, 15 and 16. There are 16 uncontracted forms across 10 cards: 00:2, 03:1, 05:3, 07:2, 08:1, 09:1, 10:1, 14:1, 15:1, 16:2.
- **British spelling, dashes, cross-references in 00-20 prose:** 0 dashes and 0 chapter cross-references. The only US-spelling matches are quotations, titles and front matter, all exempt: "A Behavioral Notion of Subtyping" (05), the reference section "Basic customization" (07), "Call-once behavior is not guaranteed" (18), "Favor object composition" (19), and `part: "selecting-varying-behavior"` (12-15).

### Item 5: ban-tier triage (root scan, 26 hits in 7 files)

| File | Hits | Pattern | Verdict | Fix |
| --- | --- | --- | --- | --- |
| `LICENSE-docs.md` | 9 | ` -- ` | False positive. It is the verbatim CC BY 4.0 legal code ("Section 1 -- Definitions."), and `CLAUDE.md` already says the voice ban scan excludes it. `validate.py` lists it in `EM_DASH_ONLY`. | `--exclude LICENSE-docs.md` in the canonical gate |
| `scripts/validate.py` | 11 | capstone (5), plan path (6) | False positive. They are the ban patterns themselves (`CAPSTONE_RE`, the `check_banned` docstring, `PLAN_REL`, `CLAIMS_REL`) and self-test fixtures. | `--exclude validate.py` |
| `CLAUDE.md` | 2 | capstone (line 99), plainly (line 134) | Line 99 is a false positive: the rule has to name the word it bans. Line 134 ("say plainly that mocks bypass the static check") is a real register hit in an internal file. | Exclude `CLAUDE.md`, and reword line 134 to "state that mocks bypass the static check" (fix-now) |
| `examples/09-protocol-and-structural-typing/src/structural_typing/pricing.py:26` | 1 | on purpose | Real. It is docstring prose, and nothing quotes it (`grep -rn "on purpose" _docs examples` finds only this line). | Reword to `"""Named shipment, not consignment: PricingRule's parameter is positional-only, so the name is free."""` (at most 100 columns; ruff format stays clean) |
| `spikes/S4a-findings.md:60` | 1 | deliberately | Real. Spike notes are public prose. | "a file with lint and format errors produced `I001` and a format difference." |
| `examples/21-composite-and-flyweight/tests/test_flyweight.py:41` | 1 | deliberately | Real, and not in the brief's list. It is quoted at `_docs/21-*.md:180`. | Decision 5: "so collect explicitly before asserting" in the test and the excerpt together |
| `examples/22-observer/tests/test_lifetime.py:2` | 1 | deliberately | Real, and not in the brief's list. Not quoted. | Decision 5: "collects explicitly before asserting" |

`scripts/host_ids.py` has 13 watch-tier hits and no ban-tier hits. It is vendored unchanged from lgtm-skills and must not be edited. Exclude it from the gate so its watch hits don't clutter reviews.

Canonical gate (criterion 10):
`bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh --tier ban --fail --exclude LICENSE-docs.md --exclude CLAUDE.md --exclude validate.py --exclude host_ids.py .`
After those exclusions, the scan on main reports exactly the four real hits in the table: pricing.py, the two r10 tests and S4a.

## Approach

- **Model chapters.** Chapter 21's sidebar (lines 236-242) and chapter 22's close (lines 317-323) are pasted verbatim into every executor brief as the target shape.
- **The sidebar shape.** The markup is unchanged, `<blockquote class="ai-sidebar" markdown="1">` ... `</blockquote>`, never `{: .ai-sidebar}`. Inside it, in order:
  1. A bold lead in the house form (`**Reviewing assistant-written X.**`), then the problem in one or two sentences: what an unspecific request returns, with the model's default tendency only as the reason to steer, in a clause.
  2. "Paste a prompt that states the form:" (or "...the contract:"), then a blank line, then the prompt as a nested `>` quote that bakes in the chapter's decision rule using the chapter's real names.
  3. At most one review line: "If the reply ..., ask ...".
  4. No checklist and no "Check:". At most 120 words.
- **The close.** `## What you can do now` sits directly before `## For deeper coverage`, with one bullet per objective, in the objectives' order. Each bullet names the capability and the artifact that delivered it: a type, a function, a test name, an experiment or a table that already appears in the chapter. A close adds no new fact and no new identifier (criterion 6). It is not a summary.
- **Structure fixes.**
  - Cut prose that re-describes a code block shown directly above it, keeping any sentence that adds a force, a trade-off, a test name or a fact the code can't show.
  - Move intent ahead of mechanism in the section openers listed below.
  - Replace references to things not yet set up with the fact itself.
  - Remove the flourishes, the meta-narration, the self-rating asides and the philosophy-teacher sentences listed below.
- **Cut order** for chapters near the ceiling:
  1. re-narration;
  2. flourishes and meta-narration;
  3. the old summary paragraph that the close replaces;
  4. trimming the figure-description paragraph, keeping every element it names that is still in the figure.

  No test name, number, quotation, credit or source link is cut (criterion 4 checks test names and URLs mechanically).
- **Do not change** fenced code, quoted output, excerpts, `{% include %}` lines and captions, front matter (apart from card titles under decision 8), link targets, test names, numbers or quotations. The only fenced-code change in the whole iteration is the chapter 21 comment line under decision 5.
- **House rules** stay in force: British spelling, contractions in new text, no em-dash or en-dash, no chapter numbers in reader text, quotations exact, "final project" not "capstone", and no description of a stub chapter's content.
- **Objectives** keep their wording, with one exception: chapter 12's objective 5 says "the review checks that catch assistant-written over-structure", and the checks become a prompt. The executor changes it to "and the prompt that keeps assistant-written code from over-structuring it". No other objective names the sidebar.

Rejected:
- `#A`/`#B` code callouts (decision 9).
- New tests, re-runs of experiments, or new quoted output.
- Sidebars in chapters 0-4 (decision 3).
- A close written as a summary paragraph.
- Moving or renaming any existing heading.

## Per-chapter findings and spec

Line numbers are on main at b7e2a71. Executors locate each finding by the quoted text, because lines shift as they edit. "Cut" means delete the sentence. "Rewrite" means keep the fact and change the register. Each close spec lists the artifact for each objective, in order. The sidebar prompts are drafts: the executor checks every name against `examples/<NN-slug>/src`, keeps the decision rule, and may tighten the wording to the 120-word cap.

### 00 Prerequisites and the toolchain (hands-on, 6 objectives, no sidebar)
- Not yet set up, line 144: "The `reweigh` experiment in Build, run, observe shows the asymmetry in one direction". The experiment comes 70 lines later. Rewrite as the fact: "Changing `reweigh` to return `str` makes mypy fail and leaves pytest green, and a malformed id shows the other direction".
- Re-narration, line 128: "`reweigh` calls `dataclasses.replace`, which builds a new instance from the old one with one field changed." restates the excerpt. Keep the `__post_init__`-reruns fact and the PEP 649 sentence.
- Meta, line 206: "Note `rootdir` and `configfile`:" becomes "`rootdir` and `configfile` show that pytest found the root `pyproject.toml` from inside the example."
- Close, placed after `## Teardown`:
  1. the installer plus `.python-version`;
  2. `uv sync --locked --all-packages` and the root `.venv`;
  3. `scripts/check-prereqs.sh` and its table;
  4. the four gates and `bash scripts/verify.sh`, with mypy per member;
  5. `Consignment`, `ConsignmentId`, `Weight` and the 26 cases in `tests/test_consignment.py`, plus the `reweigh` experiment;
  6. `.venv/bin/python` and the Teardown commands.

### 01 Patterns as decisions under forces (argument, 6 objectives; cut about 110)
- Scanner catch, line 37: "A pattern whose Consequences you can't state is a pattern you adopted on faith." Rewrite: "A pattern whose Consequences you can't state has a cost nobody has counted."
- Importance flourish, line 33: "The word that matters is the one inside the problem: forces." Rewrite: "Alexander's problems are made of forces."
- Importance, line 25: "That reading changes what you do with a pattern." Cut.
- Philosophy-teacher, line 65: "You haven't moved along a ladder of sophistication. You've read your forces and picked the compromise they select." Cut both.
- Self-rating, line 73: "and that's the useful fact", plus the cadence pair "The mechanism moved. The force stayed." Cut. Line 75 restates the test.
- Self-rating, line 79: "and it's worth having". Cut.
- Meta, line 85: "A practical test helps." Cut, and lead with "Pick the change that actually happens...".
- Old close, line 87 (about 55 words): "Name the forces before choosing a shape..." becomes the payoff close. Cut the paragraph.
- Close:
  1. the template sections and Alexander's forces;
  2. Consequences as the ledger;
  3. the four forces with their owners (carrier, commercial team, tax authority, the disputed invoice);
  4. the three shapes chosen by the dominant force (a function over `Tariff`, rule callables returning `Money`, a `RateCalculator` Protocol);
  5. the class-per-rule to callable move;
  6. the one-carrier case and the count-the-edits test.

### 02 What 1994 assumed, and what Python dissolves (argument, 5 objectives)
- Precision, line 126 (decision 6): "a mock object is typed as `Any` by the checker" becomes "a mock is assignable to every type".
- Reflex, line 22: "isn't a rulebook that Python breaks. It is a snapshot..." Rewrite in the positive: "The 1994 book is a snapshot of one set of assumptions".
- Re-narration, line 66: "`flat_rate` and `per_kg` satisfy it as plain functions, with no base class to inherit and no method to override. `quote` is the context of the 1994 pattern, reduced to one line that calls whatever it was given." Keep the first clause about the PEP 695 alias. Shorten the rest to one clause: "the 1994 context is the one-line `quote`".
- Meta and self-rating, line 74: "That is the dissolve, stated precisely:" Cut the lead-in and keep the force-versus-mechanism clause.
- Re-narration, line 90, first sentence ("`TrackingHistory` is a small class whose `__iter__` returns ..."). Keep the laziness test.
- Self-rating, line 177: "a real null object remains a fine design, and now it's a deliberate choice rather than the only option" becomes "a null object is still the right design, and now it is one option among several".
- Flourish, line 187: "The practical consequence is a rule of proportion." Cut.
- Close:
  1. the object-model assumption;
  2. per pattern: `PricingRule` and `partial`, `pages`, `CarrierGateway`, `TARIFF` through `sys.modules`, and `find_gateway` with the `[union-attr]` line;
  3. reading the alias, the Protocol and the generator;
  4. the `submit_shipment` mismatch that still needs an adapter;
  5. the force-or-mechanism test, with Composite, State and Command as the survivors.

### 03 The three-way split (argument, 6 objectives; cut about 60)
- Importance setup plus re-narration, line 120: "The witness test shows what makes this the pattern. For a light consignment `calculator_for` returns the `BaseRate` itself; ..." Keep the facts the excerpt doesn't show (the layer is chosen per consignment, `inner` is unchanged, Protocol not inheritance) and drop the restatement of `calculator_for`'s branches.
- Re-narration, line 129, second sentence ("the rebound name is a wrapper that keeps the original's name, reaches it through `__wrapped__`..."). Keep "and reports to the sink only when called".
- Philosophy-teacher, line 87: "and the code is shorter in Python without the decision being smaller". Cut.
- Importance, line 91: "The first, Decorator, matters most, because confusing the two produces wrong designs." Keep the reason and drop "matters most": "Decorator comes first: confusing its two meanings produces wrong designs."
- Summary marker, line 216: "Read the test names as the map's claims in short form." Cut.
- Close:
  1. the two questions;
  2. the table;
  3. `Surcharge` against `@audited`, plus the independence test;
  4. the idioms `find_gateway`, `Money` and `GATEWAYS`;
  5. the straddlers (Command, `declare_customs`, `describe`);
  6. the nineteen tests and the `_GUARDED` experiment.

### 04 Naming patterns for teams and AI assistants (argument, 7 objectives; cut about 150)
- Not set up, line 46: "In the example for this part". The chapter has no example. Name it: "In the [three-way split example]" (the link already used in chapter 2, line 28).
- Duplication, line 32: "A request that names only the pattern leaves the mechanism open. A request that names the role and the mechanism..." restates line 28. Cut the paragraph (about 35 words).
- Importance, line 38: "Pattern names raise the stakes because they are compressed claims." becomes "Pattern names are compressed claims."
- Meta, line 40: "That's what 'checkable' means here." Cut, and keep the next two sentences.
- Flourish, line 78: "and names are where the confusion either spreads or stops". Cut.
- Line 98 (about 35 words): "These are the practices that make a request to a colleague checkable..." Cut. It restates the section.
- Line 112: "This is the review you'd run on a human contributor. Run the same checklist on an assistant's output." Cut. Line 102 says it.
- Old close, line 122: "The test is the same at every step..." Cut. The close replaces it.
- Close, 7 terse bullets:
  1. `RateStrategy` and its three questions;
  2. `type PricingRule`, the docstring, the PR description and `GATEWAYS` under PEP 8;
  3. `Booked` to `Delivered` in `HandlingEvent`;
  4. the `PricingRule`, `make_consignment` and Manager/Helper renames;
  5. `Surcharge` against `audited`;
  6. the prompt naming `PricingRule` and `per_kg`, plus the four review checks;
  7. the rename in its own commit, or the retired label.

### 05 SRP, OCP, and LSP (hands-on, 5 objectives)
- Re-narration, line 79: the whole paragraph ("`quote` chooses nothing about how a price is computed... It looks up the rule by the first two letters of the destination code...") restates the excerpt at 59-77. Cut.
- Reflex, line 22: "The cost is not the edit. It is the review and the retest..." becomes "The cost is the review and the retest that follow an edit...".
- Importance, line 36: "The useful reading is about people:" becomes "A reason to change is a person or a process..."
- Meta, line 81: "That's the sense of the principle in this chapter," Cut, and keep the clause about the expected set.
- Importance flourish, line 111: "What matters is the shape:" Cut. Start with "`percent` is a closure...".
- Consistency, line 156: "Three negative fixtures..." followed by "The other, `DollarRate`". Change to "The second, `DollarRate`".
- Sidebar draft:
  - Problem: "Asked to split a rate calculation, an assistant may add a Protocol for every piece, a registry with one entry, or an override that narrows its argument."
  - Prompt: "Split `quote` into pricing, tax and audit. Pricing is a `RateCalculator` Protocol, tax a `TaxRule` looked up by destination country in a read-only mapping, audit an `AuditSink` callable. Add no Protocol or base class without a second implementation. An override may accept more and promise more, never less. Write one parametrised contract test that every `RateCalculator` must pass."
  - Review: "If an override narrows `price`, ask for the contract case it fails."
- Close:
  1. `RateCalculator`, `TaxRule` and `AuditSink`, with `test_each_change_moves_only_the_fields_it_feeds`;
  2. `{**TAX_RULES, "HK": exempt}` with `test_a_new_tax_rule_is_added_without_editing_quote`;
  3. the `[override]` Liskov note against `test_mypy_cannot_see_a_behavioural_violation`;
  4. the contract helper and `test_calculator_honours_the_rate_contract`;
  5. the one-country and one-calculator cases.

### 06 ISP, DIP, and DI without a framework (hands-on, 5 objectives)
- Precision, line 149 (decision 6): "to mypy, a mock is `Any`" becomes "a mock is assignable to every type".
- Importance, line 28: "the dashed arrows lead to the point of the design:" becomes "the dashed arrows show that the adapter satisfies both Protocols structurally and imports neither."
- Re-narration, line 141, first sentence ("`GATEWAYS` is a read-only mapping ... The function builds one gateway and gives that same object to both consumers"). Keep "`app` is the one module that imports `carriers`" and the two test names.
- Summary marker, line 212: "The test names are the claims in short form." Cut.
- Sidebar: the lead becomes `**Reviewing assistant-proposed seams.**`
  - Problem: "Asked to make booking testable, an assistant may reach for a container library, a base class per adapter, or one wide gateway Protocol every consumer shares."
  - Prompt: "Have each policy module declare a Protocol with only the methods it calls: `BookingGateway` with `book` and `cancel`, `TrackingGateway` with `track`, parameters positional-only. Adapters inherit nothing and import no policy module. Inject through a frozen dataclass field or `functools.partial`. Choose the adapter in one `build_app` function, the only module that imports `carriers`. No container library. Add an `ast` test that policy modules don't import adapters."
  - Review: "If a fake has to stub a method its consumer never calls, ask for the narrower Protocol."
- Close:
  1. the two Protocols and `test_a_fat_protocol_forces_fakes_to_stub_unused_methods`;
  2. the `ast` import tests in both directions;
  3. the `BookingService` field and `partial(tracking_history, gateway=...)`;
  4. `build_app` and `test_build_app_shares_one_gateway_between_booking_and_tracking`;
  5. `test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment` and `test_autospec_bypasses_mypy`.

### 07 The data model (hands-on, 5 objectives)
- Importance, line 51: "which matters here for one reason:" Cut, and keep the `nan` fact.
- Re-narration, line 112, first sentence ("`price * Decimal("2")` needs only `__mul__`, and `__rmul__` delegates to it"). Keep the figure's `Decimal` path and the float path.
- Aside, line 173: "and the contract above is hard enough within one class". Cut.
- Sidebar draft:
  - Problem: "An assistant writing dunders may type `__eq__` with the class, define `__eq__` without `__hash__`, or add a `__radd__` that accepts `0` so that `sum()` works."
  - Prompt: "`__eq__` takes `object` and returns `NotImplemented` for foreign types, and `__hash__` hashes the same key equality compares. Type each operator's operand, return `NotImplemented` for anything else, and raise `ValueError` for mixed currencies. Add `__rmul__` for a scalar factor. Derive ordering from `__lt__` with `functools.total_ordering`. No `__radd__` for `0`: callers pass `start=` to `sum`. Add a test that puts two equal values in a set."
  - Review: "If equal values can hash differently, ask for that set test."
- Close:
  1. the table and `test_special_methods_are_looked_up_on_the_type`;
  2. `Dimensions` and `test_defining_eq_alone_makes_a_class_unhashable`, plus experiment one;
  3. `Money.__rmul__` and experiment two;
  4. `total_ordering` on `Money` and the unordered `RateQuote`;
  5. `TrackingHistory` and `__format__`.

### 08 Dataclasses and value semantics (hands-on, 5 objectives)
- Intent before mechanism, line 42: "The example is a member called `value-semantics`. Its first value is a weight:" opens a section with packaging. Replace with intent: "A weight is the smallest value: equal by content, safe to share, never zero."
- Self-rating, line 36: "Each piece is correct and none is interesting, and" Cut that clause.
- In-every-sense family, line 65: "has stopped being immutable in any sense a reader can rely on" becomes "is no longer immutable".
- Re-narration, line 56, first sentence. Keep the `inf > 0` fact.
- Sidebar draft:
  - Problem: "An assistant writing a value type may produce private fields with accessors, a mutable dataclass used as a dict key, a `list` inside a frozen class, or `object.__setattr__` in `__post_init__`."
  - Prompt: "Write each value as `@dataclass(frozen=True, slots=True)` with immutable field types (`tuple`, `frozenset`, `Decimal`). `__post_init__` only validates and raises; normalise in a classmethod such as `Money.of` before construction. Amend with `dataclasses.replace`. Use `order=True` only where field order is the meaning, and `eq=False` for an entity such as `StowagePlan`. Add a test that puts two equal values in a set."
  - Review: "If `__post_init__` assigns through `object.__setattr__`, ask for the normalising constructor."
- Close:
  1. the generated members and `test_frozen_is_a_setattr_guard_not_a_seal`;
  2. `_MutableSlotId` and `_FrozenWithList`;
  3. the `replace` amendment test;
  4. `StowagePlan` with `eq=False`;
  5. `order=True` against `_OrderedMoney`, `kw_only` and `field(compare=False)`, with their static cases.

### 09 Protocol and structural typing (hands-on, 5 objectives)
- Intent before mechanism, line 32: the section opens with the PEP credit and the mechanism, and its point comes last ("The comparison happens where the value is used, not where the class is written."). Move that sentence first and keep the credit.
- Meta, line 79: "Here the interest is in what satisfies the checker." Cut.
- Cadence, line 93: "which is the opposite of what a booking needs" Cut.
- Review and keep, line 191: "is the kind of lie that survives review". The subject is an annotation reporting a wrong type (the machine sense, rule 1's exception). Keep.
- Sidebar draft:
  - Problem: "An assistant may add a `NullGateway` that returns empty values, inherit from a Protocol to implement it, or treat `isinstance` on a runtime-checkable Protocol as a signature check."
  - Prompt: "Return `CarrierGateway | None` from `find_gateway` and narrow it once, at the boundary, with an explicit branch, not `assert`. Satisfy `CarrierGateway` by shape, with no Protocol in the bases. Keep a do-nothing object only where doing nothing is correct, as `no_discount` is. Use a `sentinel` when `None` is a valid argument. Mark callback Protocol parameters positional-only with `/`. Leave signature checks to `mypy --strict`, not `@runtime_checkable`."
  - Review: "If a stand-in returns an empty reference, ask what the caller learns when a booking is lost."
- Close:
  1. the `[protocol-use]` assignment error;
  2. the four narrowings, and `_NullGateway` against `no_discount`;
  3. `ACCOUNT_DEFAULT`;
  4. the `Quoter[T]` variance error and `PricingRule.__call__` with `/`;
  5. `CarrierBase` against `CarrierGateway`, and the names-only `runtime_checkable` test.

### 10 Context managers (hands-on, 5 objectives)
- Intent before mechanism, line 44: "The example is a member called `context-managers`." becomes intent first: "A manifest should appear whole or not at all, so `ManifestWriter` writes to `<name>.partial` and commits only if the block succeeds."
- Re-narration, line 72: "Both branches close the handle first. Success then renames..." Keep only the `Path.replace` whole-or-none fact and the three tests.
- Philosophy-teacher, line 95: "So an annotation is a claim about behaviour." Cut.
- Review and keep, line 24: "the second is a lie". The subject is a file reporting a wrong state (machine sense). Keep.
- Sidebar draft:
  - Problem: "An assistant may open a file without `with`, write a `@contextmanager` with no `try`, return `True` from `__exit__`, or write straight to the final path."
  - Prompt: "Write `ManifestWriter` to write `<name>.partial`, close on every path, replace the final path only on success and delete the partial on failure, with `__exit__` returning `None`. In the `@contextmanager` form, wrap the `yield` in `try`/`except`/`else`. Open several writers on an `ExitStack`. Swallow only a named exception, with `contextlib.suppress`. Add a test that raises mid-write and asserts the handle is closed."
  - Review: "If the generator form has no `try`, ask for that test run against it."
- Close:
  1. the three decisions and `ManifestWriter`;
  2. `manifest_file` and `test_the_generator_form_needs_try`;
  3. `write_manifests` and the reverse-unwind test;
  4. the `[unreachable]` witness and `suppress`;
  5. the 3.15 decorator test.

### 11 Proving it works (hands-on, 6 objectives; cut about 185, the tightest)
- Meta, line 33: "and it can be stated once" Cut.
- Meta, line 35 (about 30 words): "Here a fault is planted by hand, one check at a time, to see whether the suite notices, which is enough for a suite this size and leaves nothing to configure." Cut.
- Meta, line 37 (about 35 words): "Here a plain `Mock`, built inline, plays the negative fixture... The next sections show how..." Cut. Line 76 says it.
- Importance, line 67: "What matters in practice is what each kind of double refuses." becomes "Each kind of double refuses something different."
- Self-validation plus aphorism, line 91: "The assertion on the correct name fails, as it should. An assertion that can't fail tells you nothing." Cut both.
- Flourish, line 129: "The last column is the surprise." Cut.
- Aphorism, line 209: "A mock-versus-fake claim like the ones above is only as good as the assertion on the code set." Cut.
- Pointer, line 221: "The `--import-mode=importlib` option ... is explained in the chapter titled [Prerequisites and the toolchain]". Cut. It is the third pointer in a light section.
- Figure description, line 29: trim to about 40 words, keeping the claim box, the witness, the negative fixture, "seen failing" and the scrubbed run.
- Sidebar draft:
  - Problem: "An assistant may use a plain `Mock` for a typed collaborator, assert only that a method was called, patch a module global, or read the clock inside the code under test."
  - Prompt: "Name each test after the claim it witnesses. Build doubles for `CarrierGateway` with `mocker.create_autospec(CarrierGateway, instance=True)` or a hand-written fake, never a plain `Mock`. Assert the returned reference before the calls. Inject the clock and the environment mapping instead of patching, and use `monkeypatch.context()` for the one real-environment test. Keep `--strict-markers`, `xfail_strict` and `filterwarnings = ["error"]`."
  - Review: "Delete each test's check in a scratch copy and confirm the test fails."
- Close:
  1. claim-named tests and the deletion method;
  2. the `quote_log` yield fixture with experiment three, and `make_fake`;
  3. the doubles table and `test_mypy_accepts_every_mock_where_a_gateway_is_expected`;
  4. the injected clock and the `monkeypatch.context()` test;
  5. `assert_type` and the unused-ignore regression;
  6. experiments four to six.

### 12 Strategy: the callable (pattern, 5 objectives)
- Meta, line 34: "and this chapter doesn't repeat it" Cut.
- Meta, line 52: "The one class that remains is justified below:" becomes "The one class that remains holds a configuration...".
- Objective 5 wording: see Approach.
- Sidebar draft:
  - Problem: "Asked for "the Strategy pattern", an assistant may write an abstract `PricingStrategy`, a subclass per rule and a factory, or record `rule.__name__` on the quote."
  - Prompt: "Type the slot as `type PricingRule = Callable[[Consignment], Money]`. Register rules in a read-only `frozendict` typed `Mapping[str, PricingRule]`: a function, a `partial` that binds every parameter its rule needs, or a frozen dataclass with `__call__` when the configuration must compare by value. Raise an unknown name as `RatingError`. Record the registry key on `RateQuote`, not `__name__`. A rule's result depends only on its argument. No base class."
  - Review: "If a `partial` entry binds nothing, ask for the call that fails."
- Close:
  1. the slot and the class-count test;
  2. `RATE_RULES`, `RatingError` and `RateQuote.rule`;
  3. the five-form table and `ZoneRate`;
  4. the registry mypy cases and the unbound `partial`;
  5. `_make_loyalty_discount` and the sidebar prompt.

### 13 Template Method (pattern, 5 objectives)
- Re-narration, line 77: "The order is the one in the figure. The guard comes first, then one classification per commodity, then the total, then duty, then the document list..." Cut the first three sentences and keep "A hook can't remove the guard or drop the invoice, because neither is a hook" and the tests.
- Re-narration, line 166, sentences 2-3 ("The constructor takes the classification and the schedule once. `classify` and `duty` are concrete steps that read them."). Cut.
- Re-narration, line 168, first sentence, and all of line 170 ("The `country` attribute is a class variable..."). Cut.
- Cadence, line 296: "Three signals see one deletion." Cut.
- Sidebar draft:
  - Problem: "An assistant may write an abstract base class whose subclasses must remember `super()`, put an invariant inside an overridable step, or give a Protocol default bodies and expect matching classes to inherit them."
  - Prompt: "Write `declare_customs` as a function that fixes the order and the invariant steps (refuse an empty consignment, total in one currency, commercial invoice first) and takes `CustomsHooks`, a frozen keyword-only dataclass with `classify` and `duty` undefaulted and `extra_documents` defaulted. Use an ABC only when destinations share a table and a schedule, and mark its `declare` with `@typing.final`. No default bodies in a Protocol."
  - Review: "If an invariant sits inside a hook, ask for the test where a variant skips it."
- Close:
  1. `declare_customs` and `CustomsHooks`;
  2. the required-hook and default-hook tests;
  3. `test_protocol_defaults_reach_only_explicit_subclasses`;
  4. `@final`, static against runtime;
  5. `CustomsDeclarer` and the shared-schedule test.

### 14 State and finite state machines (pattern, 5 objectives; cut about 120)
- Watch hit and self-validation, line 148: "and that is deliberate". Rewrite: "The table and the `match` say the same thing in different places, so a test can hold each to the other."
- Self-rating, line 178: "That's a good report, though it lands..." becomes "The report lands...".
- Importance, line 194: "explains why that matters:" becomes "says:".
- Line 198: "carries a warning that matters if someone reuses the pattern for tokens:" becomes "warns:". "The model is a simulation, and [`random`] is the right module for it." becomes "The model is a simulation." The `random` URL stays in For deeper coverage.
- Flourish, line 26 (about 25 words): "Each is a lifecycle problem that the type system and the test suite can be made to see, once the lifecycle is written down as something they can read." Cut.
- Re-narration, line 120, first sentence. Keep the `assert_never` quotations.
- Figure description, line 30: trim to about 70 words, keeping the two forms, the five states, the delay box and the illegal-event arrow.
- Sidebar draft:
  - Problem: "Asked for "the State pattern", an assistant may propose a class per status with a method per event, a mutable `status` field, or a `match` whose last arm raises for anything else."
  - Prompt: "Write the lifecycle as `TRANSITIONS`, a read-only `frozendict` from `(ConsignmentStatus, HandlingKind)` to the next status, raising `TransitionError` that names both halves for an absent pair. Where states carry data, make them frozen dataclasses in a union and write `apply_event` as a `match` on the state with an arm per state and `assert_never` last, no wildcard. Pass a `random.Random` in for delays. Test that every status is reachable and `DELIVERED` is terminal."
  - Review: "If the `match` ends in `case _: raise`, ask what mypy reports when a state is added."
- Close:
  1. the survives argument;
  2. `TRANSITIONS`, the `[illegal-pair]` case and the graph tests;
  3. `apply_event`, `assert_never` and the wildcard and tuple cases;
  4. the state-object fixture and `test_mypy_accepts_a_state_object_nothing_returns`;
  5. `test_a_seeded_transit_is_reproducible` and the shared-generator test.

### 15 Command, undo, and command queues (pattern, 5 objectives)
- Re-narration, line 149, sentences 2-4 ("`amend` applies an amendment and pushes ... `undo` pops an inverse ... `redo` runs the same move the other way."). Keep "The stacks hold inverses." and the three tests.
- Re-narration, line 212, first sentence ("The loop works on a local deque built from the queue and a local request..."). Keep the tests.
- Philosophy-teacher, line 176: "Here the consequence is concrete: an inverse is only as good as the data it holds, and a mutable field makes that data a moving target." Cut.
- Near the ban phrase "for free", line 186: "One more property comes free." becomes "Every `BookingRequest` is a frozen value, so...".
- School framing:
  - line 101: "the technique is the one taught in [State...]" becomes "the technique is the one in [State...]";
  - line 176: "which [Dataclasses and value semantics] teaches" becomes "which [Dataclasses and value semantics] covers".
- Sidebar draft:
  - Problem: "Asked for "the Command pattern", an assistant may write a `Command` base with `execute` and `undo`, record the old value when the command is built, or store the caller's `dict` in a command."
  - Prompt: "Make each amendment a frozen, slotted dataclass in a closed union, with immutable field types (`frozendict`, `tuple`). Write one `apply(request, amendment)` that matches on the kind, ends in `assert_never`, and returns the new request and the inverse read from the request it changed. Keep undo and redo in `deque`s, the undo stack with `maxlen`, and clear redo on a new amendment. Apply a queue on a local request, so a failure leaves the booking unchanged."
  - Review: "If the inverse is recorded when the command is queued, ask for the two-amendment undo test."
- Close:
  1. `test_amendments_compare_by_value_and_partials_do_not`;
  2. `apply` and the inverse test;
  3. `Booking`'s stacks and the stale-inverse fixture;
  4. `_LooseSetInstructions` against `frozendict`;
  5. `apply_pending` and `test_a_failing_batch_leaves_the_booking_unchanged`.

### 16 Factory Method and Abstract Factory (pattern, 5 objectives)
- School framing: line 38 "teaches the class-in-a-dict move" becomes "shows"; line 128 "teaches `assert_never`" becomes "covers".
- Self-validation, line 106: "That's the check you want." Cut.
- Re-narration, line 53, first sentence ("`GATEWAYS` maps a carrier code to a constructor that takes the settings and returns a gateway."). Keep "Each entry is a classmethod:".
- Re-narration, line 150, first clause ("Each field is a constructor in a `Callable` slot, as in the registry."). Keep the explanation of `R`, the subtle part.
- Sidebar draft:
  - Problem: "Asked for "a factory", an assistant may write a `GatewayFactory` class with a method per carrier, repeat an if-chain on the carrier code, or type a registry `type[CarrierGateway]`."
  - Prompt: "Register constructors in a read-only `frozendict` of `GatewayFactory`, each a `from_settings` classmethod returning `Self`, and raise an unknown code as `UnknownCarrierError`. Put each carrier's gateway, label printer and rate source in one frozen `CarrierKit[R]`, choose the kit once by carrier code, and tie the gateway to the label printer through the reference type `R`. No `type[...]` slot and no if-chain."
  - Review: "If two modules branch on the carrier code, ask for the kit."
- Close:
  1. `GATEWAYS`, `from_settings` and the subclass test;
  2. the `Callable` slot against the `type` slot;
  3. the if-chain fixture, 12.00 against 48.00;
  4. `CarrierKit[R]` and `test_mypy_rejects_a_kit_that_mixes_reference_types`;
  5. `test_mypy_accepts_kits_that_mix_untied_products`.

### 17 Builder, dataclasses, and Prototype (pattern, 5 objectives)
- School framing: line 72 "teaches how `kw_only`..." becomes "shows how"; line 195 "is the lesson of [Dataclasses...]" becomes "is covered in [Dataclasses...]".
- Defensive self-validation, line 118: "The comparison is fair because the checks are the same, and the difference is where the mistakes show up." becomes "The checks are the same in all three, so the difference is where the mistakes show up."
- Meta, line 172: "The new ground is what a copy goes through." Cut.
- Importance, line 187: "That's the whole difficulty when a field holds a list." Cut.
- Philosophy-teacher, line 305: "A field type is a design decision that the type checker enforces everywhere the field is used." Cut.
- Not set up, line 126: "The [Final project] is the place to weigh that choice in a larger build." points at an unwritten chapter. Cut. The pointer rule says keep pointers light.
- Sidebar draft:
  - Problem: "Asked for "a builder", an assistant may write a fluent `BookingRequestBuilder` whose `build()` checks for missing parts at run time, a dozen positional parameters, or a `clone()` that copies `self.__dict__`."
  - Prompt: "Write `BookingRequest` as `@dataclass(frozen=True, slots=True, kw_only=True)` with the cross-field rules in `__post_init__`, closed choices as `Literal` types and `documents` as a `tuple`. Keep templates in a read-only `frozendict` and copy them with `dataclasses.replace` or `copy.replace`, which rerun `__post_init__`. No builder class and no `clone` method."
  - Review: "If a template field is a `list`, ask for the test that appends through a copy."
- Close:
  1. `_LegacyBookingRequest` against the dataclass;
  2. the field-table test and `__post_init__`;
  3. `test_mypy_checks_literal_fields_and_keyword_names` and the same-type swap that passes;
  4. `TEMPLATES` and `from_template`;
  5. the tuple field against `copy.deepcopy`.

### 18 Singleton (pattern, 4 objectives; cut about 35 for margin)
- Flourish, line 43: "One table of behaviour holds them all." Cut.
- Defensive, line 70: "That is an unforced observation and not a proof." Cut. The preceding sentence already says the race isn't forced.
- Summary flourish, line 177: "That's the cost: one shared object, rewritten by each call." Cut.
- Cadence, line 179: "The caller asked for one thing and got another, silently." Cut.
- Sidebar draft:
  - Problem: "Asked for "a singleton", an assistant may override `__new__` with an `_instance` attribute, write a `SingletonMeta`, or describe `functools.cache` as loading something once."
  - Prompt: "Build `TARIFF` at import time in `tariff_table`, or reach it with `lazy from singleton import tariff_table` to load it on first use. Take the table as a parameter of `quote`, so tests and tenants pass their own. If the load needs run-time input, use `LoadOnce`: a lock with a double check and a `sentinel` marker. Don't use `functools.cache` as call-once, and don't override `__new__` or write a metaclass."
  - Review: "If the reply claims call-once under threads, ask for the `Barrier` test that forces the race."
- Close:
  1. the three meanings and the six-form table;
  2. the ladder (`TARIFF`, `lazy` import, `quote(..., table=...)`, `LoadOnce`);
  3. the `Barrier(2)` cache test;
  4. the `__new__`, metaclass and Borg tests.

### 19 Adapter, Facade, and Bridge (pattern, 5 objectives)
- Meta and importance, line 38: "and the first half of that is the point here:" becomes "and it applies here:".
- Aphorism, line 123: "A unit in a type is a check, and a unit in a name is a comment." Cut. Lines 112-121 show it.
- Importance, line 164: "The surface is the facade, and choosing it is the design work." Cut. Start with "`ship` takes a consignment...".
- Re-narration, line 203, first sentence ("Each kind holds a gateway and builds its operation from `book` and `insure`."). Cut. School framing in the same paragraph: "which is the mechanism [ISP...] teaches" becomes "covers".
- Re-narration, line 90, first sentence, which restates 54. Cut.
- Sidebar draft:
  - Problem: "Asked to "integrate a carrier", an assistant may write an `AbstractCarrierAdapter`, adapt a client whose shape already matches, pass a `float` weight to an API that expects pounds, or return the SDK's receipt from the facade."
  - Prompt: "Register a client that already satisfies `CarrierGateway` as it is. For one that doesn't, write an object adapter that holds the client, converts units through `Weight.pounds` and `Weight.from_pounds`, and raises `CarrierError` from the SDK's error. Write the facade as a module function, `ship`, whose signature names only domain types. Make booking kinds a bridge over the narrow Protocol, not a class per kind and carrier."
  - Review: "If a weight crosses as a `float`, ask for a `Weight` parameter."
- Close:
  1. `AircoClient` registered as is, and the shape mismatch;
  2. `test_mypy_cannot_see_pounds_passed_as_kilograms_through_a_float` against `Weight`;
  3. the class-adapter leak test;
  4. `ship` and `test_the_desk_names_no_sdk_type_in_its_public_surface`;
  5. the class-count test and `test_mypy_reports_an_implementor_missing_a_primitive`.

### 20 Decorator the pattern vs @decorator the syntax, and Proxy (pattern, 4 objectives; cut about 85)
- Meta, line 37: "Here are the two, side by side." Cut, and keep the two example expressions (the explain-by-example lead).
- Intent before mechanism, line 47: the section opens with mechanism ("A rate calculator is anything with a `price` method"). Prefix one clause of intent: "Adjustments chosen per consignment need wrappers that nest:".
- Scope aside, line 117: "There's no delay parameter, because backoff is out of scope." Cut.
- Re-narration, line 74, first sentence. Keep the two tests.
- Figure description, line 33: trim to about 70 words, keeping both columns, the dashed note and the proxy row.
- Sidebar draft:
  - Problem: "Asked for "a decorator", an assistant may write an `@` function where a stack chosen per consignment was needed, or a wrapper class where `@retry` would do, call either "the Decorator pattern", and put the audit beneath the retry."
  - Prompt: "For price adjustments, write frozen layers that hold a `RateCalculator` and satisfy the same Protocol, composed per consignment by `layers_for`, with fixed fees inside the tax layer. For call behaviour, write `@` factories with `functools.wraps` and a `ParamSpec`, `@audited` above `@retry`. Write the proxy as a class that defines every member of `CarrierGateway`, with no `__getattr__` forwarding. Say "Decorator" only for the layer stack."
  - Review: "If the proxy forwards through `__getattr__`, ask what mypy reports for a typo."
- Close:
  1. the two mechanisms and PEP 318's own complaint;
  2. `layers_for`, `compose` and the fee-order and rounding tests;
  3. `CarrierGatewayProxy` against `Tax`, plus the explicit-proxy mypy report;
  4. the four forwarding costs.

## Landing pages

- `index.html`: needs no edit. The one expanded form echoes the part title "Why This Is Not a GoF Retelling", and the hero copy has no ban or watch hit. The tagline "Design patterns, taught in Python" is site branding and stays.
- `_parts/*.md`: front-matter blurbs only, with no hits. No edit.
- `_examples/*.md` (cards), assigned to L1e:
  - Decision 8: retitle 03, 05, 06 and 07, both `title` and `card_title`, to concept titles, for example "The three-way split: one example per bucket" and "The data model: special methods as calls on the type". The executor proposes the wording and keeps it within the facts of the card body.
  - Contract the 16 expanded forms outside code in cards 00, 03, 05, 07, 08, 09, 10, 14, 15 and 16. Example: card 07 line 38, "do not accept ... cannot see", becomes "don't accept ... can't see".
  - Change nothing else. Card blurbs stay factual and are not re-written.
- Site chrome: the ALL-CAPS hits in `_includes/codetabs.html` sit inside an HTML comment for authors, not reader text. No edit.

## Batching (Sonnet executors, disjoint files)

| Agent | Files | Work | Words to cut |
| --- | --- | --- | --- |
| L1a | `_docs/00-*` to `_docs/04-*` | 5 closes; structure and flourish fixes; precision fix in 02 (decision 6) | 01: 110, 03: 60, 04: 150 |
| L1b | `_docs/05-*` to `_docs/10-*` | 6 sidebars, 6 closes; fixes; precision fix in 06 | none |
| L1c | `_docs/11-*` to `_docs/15-*` | 5 sidebars, 5 closes; fixes; chapter 12 objective wording | 11: 185, 14: 120 |
| L1d | `_docs/16-*` to `_docs/20-*` | 5 sidebars, 5 closes; fixes | 18: 35, 20: 85 |
| L1e | `examples/09-*/src/structural_typing/pricing.py`, `examples/21-*/tests/test_flyweight.py`, `_docs/21-composite-and-flyweight.md` (the one excerpt line only), `examples/22-*/tests/test_lifetime.py`, `spikes/S4a-findings.md`, `_examples/*.md` | Item 5 code and spike fixes (decision 5); card retitles and contractions (decision 8); `bash scripts/verify.sh` | - |

Each executor brief contains:
- the audience contract;
- the ranked rules (1-14);
- the house-voice section of `SKILL.md`;
- the Prose and AI-sidebar sections of `surfaces.md`;
- the chapter 21 sidebar and chapter 22 close, verbatim;
- this plan's Approach and its chapters' findings and specs;
- the do-not-change list;
- the criterion 4-7 check script;
- its files' `scan.sh --hits all` and `--stats-hits` output.

A subagent does not inherit the skill, so the rules are pasted in.

Each executor runs `uv run python scripts/validate.py`, the check script and `scan.sh --tier ban --fail` plus `--stats` over its own files. It hands back, per chapter: the word count before and after, the sentences cut (quoted), the sidebar and close text, and any finding it declined, with the reason.

## Steps and status

Step ids are `L*` (see User decisions).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| L0 | Branch `release/r10b` from main at b7e2a71. This plan file. Owner answers decisions 1-10, recorded here. `iteration-plan.md` row r10b marked active (dated note) | - | done |
| L1a | Chapters 00-04, per batching | L0 | done |
| L1b | Chapters 05-10, per batching | L0 | done |
| L1c | Chapters 11-15, per batching | L0 | done |
| L1d | Chapters 16-20, per batching | L0 | done |
| L1e | Item 5 fixes and landing cards; `bash scripts/verify.sh` green; the chapter 21 excerpt still byte-identical to its source | L0 | done |
| L2 | Orchestrator: `CLAUDE.md` line 134 reworded; the sidebar note "Chapters 0-20 still use the older checklist form..." replaced with a dated r10b note; the canonical ban-gate command with its four exclusions added to Per-chapter gates step 3; decision 2's `SPINE` change and `--self-test`; decision 6's dated note on reconciliation row 35; all gates (criteria 1-3) | L1a-L1e | done |
| L3 | Opus validation round 1: criteria 1-17 plus a read of every changed paragraph against the house-voice rubric and `before-after.md`, and every sidebar prompt checked against its chapter's decision rule and `src` names. Findings recorded per batch as blocker, should-fix or nit | L2 | todo |
| L4 | Repair round 1: Sonnet, same partition, flagged files only | L3 | todo |
| L5 | Opus validation round 2 | L4 | todo |
| L6 | Repair round 2 if L5 finds a blocker or should-fix; orchestrator re-runs criteria 1-17. There is no third round: anything left goes to Corrections and to the owner | L5 | todo |
| L7 | `scripts/site-build.sh`; `git status` clean (`Gemfile.lock` unchanged); rendered check of one converted sidebar and one close (nested quote inside the sidebar renders as in chapter 21) | L6 | todo |
| L8 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r10b.x` on main; notes-only release | L7 | todo |

## Corrections after the build
- L1a-L1e (Sonnet, 2026-11-05): all 21 closes and 16 sidebars in the new form; r10b-check ok; words 1,999-2,467. Planned cuts in 11 and 14 were smaller net than planned because each chapter also gained a sidebar and close; both are under 2,470. Chapter 17's pointer to the unwritten Final project was cut (plan item). L1e shortened the `pricing.py` docstring further than the plan's wording to fit 100 columns.
- L2 (orchestrator): three reader-text pointers to `_plans/evidence/` (chapters 14 and 20, example 20 README) replaced with "a recorded run", as r10 did for chapter 21; the claim rows still cite the evidence files. `validate.py` SPINE requires "What you can do now" for argument, hands-on and pattern kinds, with a self-test case. The r10b plan's "Critical files" list carried absolute home paths in the first pushed commit; the commit was rebuilt with repo-relative paths and the branch force-pushed before any PR (host_ids history clean).

(None yet. Orchestrator records here every handback that differs from this plan: word counts, declined findings, changed prompt wording, any rendering difference.)

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and `git diff --quiet main -- uv.lock pyproject.toml` succeeds.
2. `uv run python scripts/validate.py` reports 0 errors and 0 warnings. `--self-test` and `--claims` exit 0, with rows 1-119 resolving exactly as on main. If decision 2 is approved, `SPINE` contains "What you can do now" for argument, hands-on and pattern, and validate still passes.
3. `python3 scripts/host_ids.py check` exits 0.
4. Facts stay put. The check script below exits 0. For each of chapters 00-20 against `main` it checks that:
   - the fenced-code lines are unchanged;
   - every `test_*` name in the prose on main is still in the prose;
   - every `http(s)` URL in the prose on main is still in the prose;
   - the figure include lines are unchanged.
5. The close (same script): each of 00-20 has exactly one `## What you can do now`, as the second-to-last H2, directly before `## For deeper coverage`. Its bullet count equals the learning-objective bullet count.
6. The close adds nothing (same script): every backticked token in a close appears earlier in the same chapter.
7. Sidebars (same script):
   - 05-20 have exactly one sidebar each, and 00-04 have none.
   - Each sidebar opens with a bold lead and contains a nested `>` prompt.
   - Each has at most two non-quoted paragraphs (the problem and the review line).
   - None matches `\bCheck(:| that| three| four| whether)`.
   - Every backticked name in a sidebar appears elsewhere in the chapter or in `examples/<NN>-*/src`.
   - `v.word_count` of each sidebar body is at most 120 (spot-check with the snippet in Planning evidence).
   - `grep -c "{: .ai-sidebar}" _docs/*.md` prints 0 for every file.

   ```bash
   uv run python - <<'EOF'
   import pathlib, re, subprocess, sys
   sys.path.insert(0, "scripts")
   import validate as v
   TICK = re.compile(r"`([^`\n]+)`")
   TEST = re.compile(r"\btest_\w+")
   URL = re.compile(r"https?://[^\s)>\]]+")
   errs = []
   code = lambda t: [ln for _, ln, f in v.body_lines(t) if f is not None]
   prose = lambda t: "\n".join(ln for _, ln in v.prose_lines(t))
   figs = lambda t: [ln for ln in t.splitlines() if "include excalidraw.html" in ln]
   for p in sorted(pathlib.Path("_docs").glob("[012]*.md"))[:21]:
       n, new = p.name[:2], p.read_text()
       old = subprocess.run(["git", "show", f"main:{p}"], capture_output=True, text=True, check=True).stdout
       if code(old) != code(new): errs.append(f"{n}: fenced code changed")
       if figs(old) != figs(new): errs.append(f"{n}: figure include changed")
       for label, rx in (("test name", TEST), ("URL", URL)):
           lost = set(rx.findall(prose(old))) - set(rx.findall(prose(new)))
           if lost: errs.append(f"{n}: {label} dropped: {sorted(lost)}")
       if (w := v.word_count(new)) > 2500: errs.append(f"{n}: {w} words")
       lines = new.splitlines()
       heads = [m.group(1) for _, ln in v.prose_lines(new) if (m := v.H2_RE.match(ln))]
       if heads.count("What you can do now") != 1 or heads[-2:] != ["What you can do now", "For deeper coverage"]:
           errs.append(f"{n}: close missing or misplaced")
           continue
       def section(name):
           i = lines.index(f"## {name}")
           j = next(k for k in range(i + 1, len(lines)) if lines[k].startswith("## "))
           return i, lines[i + 1 : j]
       _, objs = section("Learning objectives")
       ci, close = section("What you can do now")
       nobj = sum(ln.startswith("- ") for ln in objs)
       nbul = sum(ln.startswith("- ") for ln in close)
       if nobj != nbul: errs.append(f"{n}: {nbul} close bullets for {nobj} objectives")
       before = "\n".join(lines[:ci])
       for tok in TICK.findall("\n".join(close)):
           if f"`{tok}`" not in before: errs.append(f"{n}: close introduces `{tok}`")
       count = new.count(v.SIDEBAR)
       if count != (1 if n >= "05" else 0): errs.append(f"{n}: {count} sidebars")
       if count == 1:
           body = new.split(v.SIDEBAR, 1)[1].split("</blockquote>", 1)[0].strip()
           blines = body.splitlines()
           plain = [b for b in "\n".join(ln for ln in blines if not ln.startswith(">")).split("\n\n") if b.strip()]
           if not blines[0].startswith("**"): errs.append(f"{n}: sidebar lacks bold lead")
           if not any(ln.startswith(">") for ln in blines): errs.append(f"{n}: sidebar has no prompt")
           if len(plain) > 2: errs.append(f"{n}: sidebar has {len(plain)} prose paragraphs")
           if re.search(r"\bCheck(:| that| three| four| whether)", body): errs.append(f"{n}: checklist left")
           src = " ".join(q.read_text() for q in pathlib.Path("examples").glob(f"{n}-*/src/**/*.py"))
           rest = new.replace(body, "")
           for tok in TICK.findall(body):
               name = re.split(r"[(\[ .=:]", tok)[0]
               if f"`{tok}`" not in rest and name not in src and name not in rest:
                   errs.append(f"{n}: sidebar names `{tok}` found nowhere else")
           if (sw := v.word_count(body)) > 120: errs.append(f"{n}: sidebar {sw} words")
   print("\n".join(errs) or "r10b checks: ok")
   sys.exit(1 if errs else 0)
   EOF
   ```
8. Word counts: every chapter 00-20 is at most 2,500 by `v.word_count` (error) and at most 2,470 at L1 handback (target). The before and after table goes in Corrections. No chapter falls below 1,900.
9. Figures and data are unchanged: `git diff --quiet main -- diagrams _data` succeeds.
10. Voice, ban tier: `bash $S --tier ban --fail --exclude LICENSE-docs.md --exclude CLAUDE.md --exclude validate.py --exclude host_ids.py .` exits 0. `grep -n "plainly" CLAUDE.md` prints nothing.
11. Voice, stats:
    - `for f in _docs/0*.md _docs/1*.md _docs/20-*.md; do bash $S --stats "$f" | tail -1; done` shows 0 in DASH for every chapter.
    - No chapter's expanded-form count (CONTR total minus contracted) is above its Planning-evidence baseline.
    - No chapter is flagged `stiff`.
12. Voice, the new catches:
    - `bash $S --hits "on faith" _docs` prints no hits.
    - The finding phrases are gone, so this prints nothing:
      `grep -nE "adopted on faith|The word that matters|ladder of sophistication|that's the useful fact|it's worth having|A practical test helps|That is the dissolve, stated precisely|remains a fine design|rule of proportion|without the decision being smaller|what makes this the pattern|claims in short form|raise the stakes|either spreads or stops|What matters is the shape|That's the sense of the principle|the point of the design|which matters here for one reason|none is interesting|in any sense a reader can rely on|Here the interest is in|So an annotation is a claim|it can be stated once|What matters in practice|An assistant that can't fail|An assertion that can't fail|The last column is the surprise|doesn't repeat it|is justified below|Three signals see one deletion|and that is deliberate|That's a good report|explains why that matters|is the right module for it|a moving target|comes free|That's the check you want|The comparison is fair|The new ground is|That's the whole difficulty|is the lesson of|One table of behaviour holds them all|not a proof|That's the cost:|is the point here|choosing it is the design work|Here are the two, side by side|taught in|\}\) teaches" _docs/0*.md _docs/1*.md _docs/20-*.md`
    - The L3 reader confirms every structure finding above is resolved or recorded as declined in Corrections with a reason.
13. House rules:
    - The British-spelling grep (r10 criterion 10's regex over prose, code and quotations excluded) finds only the exempt items listed in Planning evidence.
    - `grep -cP "\x{2014}|\x{2013}"` is 0 in every file touched, including this plan.
    - `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]" _docs/0*.md _docs/1*.md _docs/20-*.md _examples/*.md` prints nothing.
    - Every quotation in a changed paragraph is unchanged character for character (L3 compares `git diff` hunks).
14. Item 5:
    - `grep -rn "on purpose" examples/09-*/src` prints nothing.
    - `grep -rn "deliberately" spikes/S4a-findings.md examples/21-*/tests examples/22-*/tests _docs/21-*.md` prints nothing (decision 5).
    - `git diff main -- _docs/21-composite-and-flyweight.md` shows exactly one changed line, the comment.
    - This prints `ok`:
      ```bash
      uv run python - <<'EOF'
      import pathlib
      src = pathlib.Path("examples/21-composite-and-flyweight/tests/test_flyweight.py").read_text()
      doc = pathlib.Path("_docs/21-composite-and-flyweight.md").read_text()
      block = doc.split("def test_the_weak_pool_drops_a_commodity_nobody_holds", 1)[1].split("```", 1)[0]
      print("ok" if block in src else "MISMATCH")
      EOF
      ```
15. Landing pages:
    - `grep -nE "^(title|card_title):.*\b(nineteen|fourteen|thirteen|twenty-two|witnesses)\b" -i _examples/*.md` prints nothing (decision 8).
    - `bash $S --stats _examples` flags no card `stiff`.
    - `git diff --quiet main -- index.html _parts` succeeds.
16. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). In the built page of one converted chapter, the sidebar's nested quote renders as a nested blockquote, as in `_site/docs/21-composite-and-flyweight/`.
17. Every sidebar prompt states the same decision rule as its chapter's prose and "When not to use it" (L3 reads all 16 side by side with their chapters). No prompt contradicts a measured result. For example, chapter 9's prompt says "an explicit branch, not `assert`", which matches line 79's `-O` quotation.
18. CI `ci-ok` is green on the PR. Merge happens only after the owner's explicit approval.

## Risks

- **The ceiling.**
  - Chapters 01, 04, 11, 14 and 20 overflow without cuts, and the new sidebars are 10-55 words longer than the old ones.
  - Repairs add words, which is why the handback target is 2,470.
  - If a chapter can't reach 2,500 without cutting a fact, the executor stops and reports it. The orchestrator then shortens the close bullets first, then the figure description, and never a claim.
- **Cutting a fact by accident.** Re-narration often carries the only prose mention of a test name or a number. Criterion 4 mechanically catches dropped test names and URLs, but not numbers. Executors quote every cut sentence in the handback so L3 can check each one.
- **Prompt drift.** A pasteable prompt that restates a rule more strongly than the chapter measured becomes a new, unbacked claim. Examples would be "never `assert`" where the chapter says "where the check must survive", or "no Protocol" where it says "no Protocol without a second implementation". Criterion 17 is a reading check for that reason, and criterion 7 checks every name against `src`.
- **Identifier mismatches.** The drafts use names read from the chapters (`Money.of`, `LoadOnce`, `CarrierSettings`, `Weight.from_pounds`). An executor that renames one, or invents a parameter, fails criterion 7 only if the name appears nowhere. L3 also greps each prompt's names in `src`.
- **Close as summary.** The obvious failure is a close that restates the chapter. Criterion 6 forbids new identifiers but can't detect a summary, so L3 reads the closes against chapter 22's model.
- **Editing inside code or quotations.** Contraction and spelling passes are tempting inside quoted output and quotations. Criterion 4 (fenced code) and criterion 13 (quotations) catch it, and the scanner blanks code, so its counts never ask for such an edit.
- **Rendering.** The nested `>` inside `<blockquote markdown="1">` relies on kramdown-GFM parsing, as chapters 21-22 do today. Copy their exact markup: a blank line before and after the quoted prompt, and no indentation. L7 checks the built HTML.
- **Line-number drift.** The findings cite main's line numbers. Executors work by quoted text, and L3 re-reads the sections rather than the lines.
- **Decision 2 timing.** Adding the close to `SPINE` before L1 lands would make validate fail on the branch while the executors work. Do it only at L2.
- **Decision 5 and the excerpt.** The chapter 21 comment changes in the test and the chapter in one commit. Criterion 14's containment check is the guard.
- **Scanner blind spots.** The scanner found 1 of the roughly 46 new-catch instances. Passing the scan is necessary and not sufficient, which is why criterion 12 lists phrases and L3 reads the paragraphs.
- **Parallel agents.** The five batches share no file. Only L1e touches a member and runs `verify.sh`. No agent runs `uv lock`.
- **The chapter 12 objective** is the only objective changed. Any further objective edit changes the close's bullet count, and criterion 5 recounts.

### Critical files for implementation
- scripts/validate.py
- _docs/21-composite-and-flyweight.md
- _docs/22-observer.md
- _docs/11-testing-with-pytest-pytest-mock-and-mypy.md
- CLAUDE.md
- ~/.claude/skills/lgtm-professional-voice/references/surfaces.md
