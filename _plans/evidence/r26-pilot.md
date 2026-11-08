---
title: "Evidence: r26 pilot"
output: false
render_with_liquid: false
---

# r26 pilot

Baseline taken at B0 on `release/r26` at ef103c2 (the r25 merge 15cc747 plus the plan and owner-decision commits). Every number below is a fresh run; the plan's figures are compared in "Differences from the plan". No doc, script or deck was changed to take them.

## Reading packet

Drafted at B4a on `release/r26` at ba96856 plus the B4a edits. One screen per doc; every figure is a fresh run (words are `validate.py`'s count). "met" and "missed" are against decision 2 and the plan's target list. The PR number and the diff links are filled at B6; the anchor is the sha256 of the doc's path.

### Doc 01: Patterns as decisions under forces

| measure | before | after | target | |
| --- | --- | --- | --- | --- |
| words | 2,484 | 2,235 | ceiling 2,500 | met |
| TESTS | 0 | 0 | 0 | met |
| LEN median (p10 to p90) | 19 (7 to 33) | 14 (7 to 27) | at most 15, p90 at most 30 | met |
| PAR | 84 | 39 | at most 40 | met |
| ABSTR/k | 20.9 | 6.7 | at most 10 | met |
| "force(s)" | 46 | 12 | at most 12 | met, at the budget |
| SECMED | 258 | 244 | 150 | missed |
| LEAD | 258 | 126 | 60 | missed |
| terse-tier hits | 7 | 2 | | both kept: "the force is" is the book's own question, "1994 assumed" is link text |

- Missed: SECMED and LEAD. The chapter has no code, and two argued sections have no table. Its longest sections are the 240-word "Forces outlive the structures that resolved them" and the 268-word "What a pattern records".
- Waivers: 0. Diff: `.../pull/<n>/files#diff-df665012adb822506b3cd9438cd6e55e0cd368942e990314b1df0828ded2ffc1`. Doc: https://github.com/patterncatalyst/design-patterns-with-python/blob/release/r26/_docs/01-patterns-as-decisions-under-forces.md
- Structure: three headings renamed ("Four pressures on a rate quote", "The dominant pressure picks the shape", "When nothing argues for a pattern"); "pressure" is the plain word after the one definition of "force". New tables: the template sections, the four pressures with owner and schedule, the three shapes, the count-the-edits verdict.

Before:
> **Carrier tariffs change on the carrier's schedule.** A carrier such as FASTLINE or AIRCO publishes a `Tariff`: a price for each combination of zone and weight band. The carrier reissues it when it chooses, often on a fixed date each year, and sometimes with little warning in between. Nothing in your codebase decides when this happens. The force is that the largest block of numbers feeding every quote is owned by someone outside the team.

After:
> **Carrier tariffs change on the carrier's schedule.** A carrier such as FASTLINE or AIRCO publishes a `Tariff`: a price for each zone and weight band. It reissues the tariff when it chooses, often on a fixed date each year, sometimes at short notice. Your code doesn't decide when. So someone outside the team owns the largest block of numbers in every quote.

### Doc 03: The three-way split

| measure | before | after | target | |
| --- | --- | --- | --- | --- |
| words | 2,388 | 2,293 | ceiling 2,500 | met |
| TESTS | 1 | 0 | 0 | met |
| LEN median (p10 to p90) | 18 (8 to 34) | 15 (7 to 28) | at most 15, p90 at most 30 | met |
| PAR | 58 | 36 | at most 40 | met |
| ABSTR/k | 14.5 | 4.7 | at most 5 | met |
| "force(s)" | 24 | 8 | at most 8 | met, at the budget |
| SECMED | 214 | 204 | 150 | missed |
| LEAD | 172 | 151 | 60 | missed |
| terse-tier hits | 3 | 2 | | both kept: the bold rule "The force remains" states the thesis; the Woolf credit is in "For deeper coverage" |

- Missed: SECMED and LEAD. "Patterns that survive" (317 words) and "Patterns that straddle two buckets" (213) are argued prose with no code or table, and the map table is frozen because Deck 101 copies its cells.
- Waivers: 0. Diff: `.../pull/<n>/files#diff-ff38068effcb3664a785b27877ecd0fc3761b417dc3990874c4d08e3fee04cb9`. Doc: https://github.com/patterncatalyst/design-patterns-with-python/blob/release/r26/_docs/03-the-three-way-split.md
- Structure: the map table is byte-identical (31 of 31 table lines); the figure walk-through moved into the collapsed description (37 words); the two sorting questions are bold-led and the two rules are a bold-led list; the Woolf credit moved to "For deeper coverage"; the one in-prose test name moved to a `*Tests:*` line. One fact fix: the description says the name question goes to the "needs-disambiguating" band, as the spec draws it; the base text said "third band".

Before:
> **Lifecycle.** State, Command with undo, and resource acquisition belong here. A consignment passes from booked to loaded to departed to cleared to delivered, and which transitions are legal is a business rule that someone has to write down in one place; an enum and a `match` help, but the transition table is the design. Command survives where history matters. A deferred call is a `functools.partial` in a `collections.deque`, and the example witnesses that queued partials change nothing until called.

After:
> **Lifecycle.** State, Command with undo, and resource acquisition belong here. A consignment passes from booked to loaded to departed to cleared to delivered. Which transitions are legal is a business rule that someone has to write down in one place: an enum and a `match` help, but nothing writes the transition table for you.
>
> Command survives where history matters. A deferred call is a `functools.partial` in a `collections.deque`, and the example shows that queued partials change nothing until called.

### Doc 23: Mediator and Chain of Responsibility

| measure | before | after | target | |
| --- | --- | --- | --- | --- |
| words | 2,144 | 1,974 | ceiling 2,500; aim 1,600 | ceiling met, aim missed |
| TESTS | 31 | 0 | 0 | met |
| LEN median (p10 to p90) | 17 (7 to 31) | 15 (5 to 26) | at most 15, p90 at most 30 | met |
| PAR | 35.5 | 24.5 | at most 40 | met |
| ABSTR/k | 8.1 | 2.1 | at most 1.5 | missed |
| "force(s)" | 2 | 0 | at most 3 | met |
| per H3: lead-in | | 16 to 51 | at most 60 | met |
| per H3: section | | 51 to 252 | at most 150 | missed in 3 |
| terse-tier hits | 8 | 1 | | kept: the credit in "For deeper coverage" |

- Missed: ABSTR/k 2.1 has 2 hits on the book title *Design Patterns* and 2 on "decision" in experiment one, which stays so it runs as written. Over 150 words: Chain "How Python models it" 197, "The terminal and the order" 201, Mediator "How Python models it" 252: fences, and the two mypy checks with no topic H3 of their own. `--terse-stats` per H2 rises (SECMED 301.5 to 341.5, LEAD 118.5 to 135.5) because a pattern H2 now holds its whole treatment; the section that holds the figure is 159 words, 65 without its 94-word description.
- Waivers: 0 (the fence order changed, the same blocks). Diff: `.../pull/<n>/files#diff-895043755ed172528a6193bc4ec606893223a47400e17a329735a622a076d897`. Doc: https://github.com/patterncatalyst/design-patterns-with-python/blob/release/r26/_docs/23-mediator-and-chain-of-responsibility.md
- Structure: the O1 layout, `## Pattern: Chain of Responsibility` (problem, solution, How Python models it, three topic H3s) and `## Pattern: Mediator` (the same, two topic H3s), each with a bold definition and a `**Bucket: survives.**` line; "Why this matters" is 3 sentences; the walk-through is in the description; 31 test names sit on 13 `*Tests:*` lines; "When not to use it" has one bullet per pattern; the GoF and Eric Traut credits are in "For deeper coverage". Appendix E rows 68 and 69 take the new cells.

Before:
> The first stage that decides wins. `test_the_first_stage_that_decides_wins` gives a declaration with no documents and unpaid duty, and the reason is the missing invoice, because `check_documents` runs before `assess_duty`. Stages after the winner don't run: `test_stages_after_a_decision_are_not_called` records the names of the stages that were called and gets `["passing", "holding"]`, with a third stage left out. A clean declaration reaches the final stage and is released (`test_a_clean_declaration_is_released`).

After:
> The first stage that decides wins. A declaration with no documents and unpaid duty is held for the missing invoice, because `check_documents` runs before `assess_duty`. Later stages don't run. A test records the names of the stages that were called and gets `["passing", "holding"]`, without the third stage.
>
> *Tests:* `test_the_first_stage_that_decides_wins`, `test_stages_after_a_decision_are_not_called`.
>
> A clean declaration reaches the final stage and is released.

### Doc 24: Iterator: generators and the iterator protocol

| measure | before | after | target | |
| --- | --- | --- | --- | --- |
| words | 2,273 | 2,146 (92 in the description) | ceiling 2,500; aim 1,600 | ceiling met, aim missed |
| TESTS | 36 | 0 | 0 | met |
| LEN median (p10 to p90) | 18 (8 to 40) | 15 (1 to 33) | at most 15, p90 at most 30 | median met, p90 missed |
| PAR | 46 | 24.5 | at most 40 | met |
| ABSTR/k | 4.4 | 0.5 | at most 1.5 | met |
| "force(s)" | 1 | 0 | at most 3 | met |
| SECMED | 273 | 135 | | per H3 below |
| LEAD | 102 | 103 | | per H3 below |
| per H3: lead-in | | 13 to 42 | at most 60 | met |
| per H3: section | | 197 to 314 | at most 150 | missed in all 5 code H3s |
| terse-tier hits | 9 | 3 | | kept: the credit in "For deeper coverage", the description's own "Read the figure from the top down", and link text |

- Missed: the five code H3s hold 35 tests and every fact (216, 255, 314, 197 and 264 words); cutting further would drop a fact or a test name. The p90 of 33 counts each fence as a one-line sentence (p10 1).
- Waivers: 12, all pending until the facts reader signs at B5a. Ten are source quotations paraphrased under decision 3 (T9), each keeping every fact and its link, checked against the page fetched 2026-11-08: the glossary on generator iterators and on one pass, five itertools sentences (`batched` twice, `islice`, `pairwise`, `chain.from_iterable`), PEP 479's abstract, `close()` and `contextlib.closing`. Two are number tokens: 255 now appears once beside its PEP link, and 1994 lost one sentence that became the Bucket line (the second link to the 1994 chapter stays).
- Diff: `.../pull/<n>/files#diff-775ca205fdb9d93132e8b74de960adb97eded29adc59ade975945723f7d1f508`. Doc: https://github.com/patterncatalyst/design-patterns-with-python/blob/release/r26/_docs/24-iterator-generators-and-the-iterator-protocol.md
- Structure: one `## Pattern: Iterator` (problem in 3 sentences and 3 bullets, solution with a bold definition and `**Bucket: dissolves.**`, How Python models it) with four topic H3s ("One pass or many", "Read only what you need", "Delegating with yield from", "Who closes the source"); 35 test names on 20 `*Tests:*` lines; the suite-count sentence is a 4-row table; one source quotation per H3; the PEP credits moved to "For deeper coverage". Appendix E row 70's Bucket cell is now "Bucket: dissolves."; its Force and When-not cells are unchanged. The front-matter description still says "decisions" and is not counted.

Before:
> The `itertools` page says of `batched` "The input is consumed lazily, just enough to fill a batch." The tests count what the source produced. A counting source of 1,000,000 events gives its first page of 3 after producing 3 (`test_the_first_page_reads_only_one_page`), and the eager `list(source)[:3]` produces 1,000,000 (`test_an_eager_list_reads_every_event_to_get_the_first_page`). The page says "The last batch may be shorter than n", and `test_pages_keep_a_short_last_page` gets sizes 3, 3 and 1 from 7 events.

After:
> The `itertools` page says of `batched` "The input is consumed lazily, just enough to fill a batch." A counting source of 1,000,000 events gives its first page of 3 after producing 3. The eager `list(source)[:3]` produces 1,000,000.
>
> *Tests:* `test_the_first_page_reads_only_one_page`, `test_an_eager_list_reads_every_event_to_get_the_first_page`.
>
> The same page says the last batch may be shorter than n, and 7 events give pages of 3, 3 and 1.

### The question for the owner

**Go, or adjust?** Go means r27 applies T1 to T12 as piloted to the 21 pattern chapters. Adjust means naming the rules to change (for example the Bucket line, the quotation budget, the `*Tests:*` form or a target); r26 then applies the change to the four docs in one more round, with a confirmation, before the merge.

## Owner decisions (2026-11-08, plan gate)

- O1: decision 1 takes the alternative, the Camel layout: one H2 per pattern with H3 subheads (`## Pattern: <Name>`, then `### The problem`, `### The solution`, `### How Python models it`, then topic H3s). GT2, GT6, PL3, PL4, the targets, the excerpts and the criteria follow it.
- O2: decisions 2 to 6 as recommended.
- O3: the Feathers title takes the book's straight house form, "I Need to Make a Change, but I Don't Know What Tests to Write".
- O4: hub PR #62 was merged as 9a3b034; no open hub item remains.

The owner's go or adjust answer after the reading packet is recorded here at B6.

## Owner checks

2026-11-08, the owner, in their own O'Reilly account: (1) read Chapter 13's title on the book page for *Working Effectively with Legacy Code* (https://learning.oreilly.com/library/view/-/0131177052/): "I Need to Make a Change, but I Don’t Know What Tests to Write". The book prints a curly apostrophe; the owner chose the straight house form, "I Need to Make a Change, but I Don't Know What Tests to Write" (O3). (2) confirmed that the four O'Reilly links open their book pages: the three canonical ones r25 put in `bibliography.html` (Architecture Patterns with Python, Effective Python, Python Object-Oriented Programming) and the original uncanonical `/library/view/-/<isbn>/` link.

## Baseline commands

```
bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh --terse-stats _docs
bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh --tier terse _docs
bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh --stats <the four pilot docs>
bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh --terse-stats <the four pilot docs>
```

## Evidence B: book baseline

`--terse-stats _docs`, the summary row (median of 47 files, TESTS summed):

```
  2200    228   102    48     2.9  1030  median of 47 files (TESTS: total)
```

`--tier terse _docs`:

```
 LINES	FILES	TIER 	PATTERN
    38	   19	terse	abstract subject ("the force is")
    34	   18	terse	provenance in the body (move to the end)
    30	   30	terse	figure walk-through (move to the description)
    24	   18	terse	nominalised verb ("what remains")
    19	   18	terse	nominalised decision ("X is a decision")
    16	   11	terse	meta-claim about the pattern ("the force behind")
    15	    8	terse	thesis framing ("Read that way")
     1	    1	terse	stacked qualifier (whose ... whose ... whose)
--
total: 177 matching lines (0 ban-tier) under _docs
```

0 ban-tier. The plan's project-pattern variant (a row for "the bucket is", "sorts it" and "the force behind", 209 lines) is built at GT5 and is not re-run here.

## Evidence C: pilot baseline

`--terse-stats` over the four pilot docs:

```
 WORDS SECMED  LEAD   PAR ABSTR/k TESTS  FILE  FLAGS
  2488    258   258    84    20.9     0  _docs/01-patterns-as-decisions-under-forces.md  long sections; late code; long paragraphs; abstract
  2414    214   172    58    14.5     1  _docs/03-the-three-way-split.md  long sections; late code; long paragraphs; abstract; tests in prose
  2105  301.5 118.5  35.5     8.1    31  _docs/23-mediator-and-chain-of-responsibility.md  long sections; late code; abstract; tests in prose
  2260    273   102    46     4.4    36  _docs/24-iterator-generators-and-the-iterator-protocol.md  long sections; late code; long paragraphs; abstract; tests in prose
--
  2337  265.5 145.25    52    11.3    68  median of 4 files (TESTS: total)
```

`--stats` over the four pilot docs:

```
 WORDS    CONTR  SENT  LEN med (p10-p90) TRIAD DASH  FILE  FLAGS
  2488    15/15   126          19 (7-33)    12    0  _docs/01-patterns-as-decisions-under-forces.md  check triads
  2414      6/9   118          18 (8-34)    12    0  _docs/03-the-three-way-split.md  check triads
  2105    21/22   110          17 (7-31)     8    0  _docs/23-mediator-and-chain-of-responsibility.md  check triads
  2260    11/13   105          18 (8-40)     7    0  _docs/24-iterator-generators-and-the-iterator-protocol.md  check triads
```

`--tier terse --files` over the four pilot docs:

```
  HITS	FILE
     9	_docs/24-iterator-generators-and-the-iterator-protocol.md
     8	_docs/23-mediator-and-chain-of-responsibility.md
     7	_docs/01-patterns-as-decisions-under-forces.md
     3	_docs/03-the-three-way-split.md
```

Summary table. Words are `validate.py`'s `word_count`; the other columns are `--terse-stats` and `--stats`. "force(s)" is a case-insensitive whole-word count over the whole file (the count over body lines only, from `validate.py`'s `body_lines`, is in brackets where it differs).

| Doc | Words | SECMED | LEAD | PAR | ABSTR/k | TESTS | LEN med (p10 to p90) | "force(s)" | Terse-tier hits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | 2,484 | 258 | 258 | 84 | 20.9 | 0 | 19 (7 to 33) | 49 [46] | 7 |
| 03 | 2,388 | 214 | 172 | 58 | 14.5 | 1 | 18 (8 to 34) | 24 | 3 |
| 23 | 2,144 | 301.5 | 118.5 | 35.5 | 8.1 | 31 | 17 (7 to 31) | 2 | 8 |
| 24 | 2,273 | 273 | 102 | 46 | 4.4 | 36 | 18 (8 to 40) | 1 | 9 |

Book-wide medians: WORDS 2,200 (terse-stats count), SECMED 228, LEAD 102, PAR 48, ABSTR/k 2.9, TESTS 1,030 in total. Terse tier: 177 lines in 8 patterns.

## Differences from the plan

- Book baseline (B): identical (2,200 / 228 / 102 / 48 / 2.9 / 1,030; 177 lines in 8 patterns, 0 ban-tier).
- Pilot columns Words, SECMED, LEAD, PAR, ABSTR/k, TESTS and LEN: identical to the plan's table (C).
- "force(s)": the plan gives 43, 23, 2 and 1; this run gives 49, 24, 2 and 1 by a case-insensitive whole-word count of the whole file (46, 24, 2, 1 over body lines). The plan's method is not stated; the gap in 01 and 03 is a counting rule, not a text change. The T7 budgets (decision 2) are measured with the rule recorded here.
- Terse-tier hits: the plan gives 01: 7, 03: 3, 23: 9, 24: 10; this run gives 7, 3, 8 and 9 (`--hits all` lists 8 matching lines in 23 and 9 in 24). The plan's counts for 23 and 24 are each one higher; the cause is not known, so the baseline here is the measured one.
- The invariant baselines of C (fenced blocks, distinct test names, URLs, `relative_url` targets, long quotations, digit tokens, walk-throughs) are not re-run at B0: they need `scripts/prose_invariants.py`, which B1b builds, and B1b records the base figures from it.
- The terse-stats WORDS column (2,488 / 2,414 / 2,105 / 2,260) differs from `validate.py`'s count (2,484 / 2,388 / 2,144 / 2,273) because the two tools exclude different lines; the 2,500 ceiling is measured with `validate.py`'s.

## Invariant baseline (B1d)

From `uv run python scripts/prose_invariants.py --baseline 1 3 23 24` on the unchanged tree at B1d:

| doc | fences | test names | URLs | relative_url | quotations | numbers | numbers, tags kept | walk-throughs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | 0 | 0 | 0 | 2 | 0 | 4 | 4 | 0 |
| 03 | 6 | 1 | 5 | 25 | 2 | 10 | 10 | 0 |
| 23 | 13 | 27 | 2 | 5 | 3 | 12 | 13 | 1 |
| 24 | 9 | 35 | 11 | 5 | 20 | 62 | 63 | 1 |

The plan's doc 24 count of 39 test names included 4 module filenames; the measured count is 35.

## Project voice patterns (B1d)

`scan.sh --tier terse --patterns .voice-patterns.tsv _docs` gives 217 matching lines (0 ban-tier), against a baseline of 177 without the project rows. 207 remain once the double count with the skill's row 123 ("the force behind") is removed.

## Waivers

| doc | kind | value | reason | signed |
| --- | --- | --- | --- | --- |
| 34 | quote | I Need To Make a Change but I Don't Know What Tests To Write | CA1: the Feathers chapter title corrected to the book's wording (O3) | owner check, evidence H, 2026-11-08 |
| 34 | quote | +I Need to Make a Change, but I Don't Know What Tests to Write | CA1: the corrected title, checked by the owner in the book's O'Reilly page (O3) | owner check, evidence H, 2026-11-08 |
| 35 | quote | I Need To Make a Change but I Don't Know What Tests To Write | CA1: the Feathers chapter title corrected to the book's wording (O3) | owner check, evidence H, 2026-11-08 |
| 35 | quote | +I Need to Make a Change, but I Don't Know What Tests to Write | CA1: the corrected title, checked by the owner in the book's O'Reilly page (O3) | owner check, evidence H, 2026-11-08 |
| 24 | quote | Each yield temporarily suspends processing, remembering the execution state (including local variables and pending try-statements). | Decision 3, T9: second quotation in "How Python models it" (the `next()` quotation stays). Paraphrased with every fact kept: "each yield suspends processing for the moment and remembers the execution state, local variables and pending try-statements included". Source: https://docs.python.org/3.15/glossary.html "generator iterator", fetched 2026-11-08. | pending |
| 24 | quote | This iterator is good for one pass over the set of values. | Decision 3, T9: second quotation in "One pass or many". Paraphrased: "the iterator `iter()` returns for an iterable is good for a single pass over its values". Source: https://docs.python.org/3.15/glossary.html "iterable", fetched 2026-11-08. | pending |
| 24 | quote | The last batch may be shorter than n | Decision 3, T9: extra quotation in "Read only what you need". Paraphrased: "The same page says the last batch may be shorter than n". Source: https://docs.python.org/3.15/library/itertools.html `batched`, fetched 2026-11-08. | pending |
| 24 | quote | If strict is true, will raise a ValueError if the final batch is shorter than n. | Decision 3, T9: extra quotation in "Read only what you need". Paraphrased: "With strict set to true, `batched` raises a ValueError if the final batch is shorter than n." Source: itertools `batched`, fetched 2026-11-08. | pending |
| 24 | quote | Make an iterator that returns selected elements from the iterable. | Decision 3, T9: extra quotation in "Read only what you need". Paraphrased: "`islice`, in the page's terms, makes an iterator that returns selected elements of the iterable." Source: itertools `islice`, fetched 2026-11-08. | pending |
| 24 | quote | Return successive overlapping pairs taken from the input iterable. | Decision 3, T9: extra quotation in "Read only what you need". Paraphrased: "`pairwise`, which returns successive overlapping pairs from its input". Source: itertools `pairwise`, fetched 2026-11-08. | pending |
| 24 | quote | Gets chained inputs from a single iterable argument that is evaluated lazily. | Decision 3, T9: extra quotation in "Read only what you need". Paraphrased: "`chain.from_iterable`, which takes its chained inputs from a single iterable argument evaluated lazily". Source: itertools `chain.from_iterable`, fetched 2026-11-08. | pending |
| 24 | quote | This PEP proposes a change to generators: when StopIteration is raised inside a generator, it is replaced with RuntimeError. | Decision 3, T9: second quotation in "Delegating with yield from". Paraphrased: "PEP 479 changed generators so that a `StopIteration` raised inside one is replaced with `RuntimeError`." Source: https://peps.python.org/pep-0479/ Abstract, fetched 2026-11-08. | pending |
| 24 | quote | Raises a GeneratorExit exception at the point where the generator function is currently suspended (equivalent to calling  ). | Decision 3, T9: extra quotation in "Who closes the source". Paraphrased: "`close()` raises a GeneratorExit exception where the generator function is suspended, the same as calling `throw(GeneratorExit)`." Source: https://docs.python.org/3.15/builtins/stdtypes.html `generator.close()`, fetched 2026-11-08. | pending |
| 24 | quote | Return a context manager that closes thing upon completion of the block. | Decision 3, T9: extra quotation in "Who closes the source". Paraphrased: "`contextlib.closing` returns a context manager that closes its argument when the block completes". Source: https://docs.python.org/3.15/library/contextlib.html `closing`, fetched 2026-11-08. | pending |
| 24 | number | 255 | PL4, T9: the PEP 255 credit moved from the body to "For deeper coverage", where "PEP 255" appears once beside its link. | pending |
| 24 | number | 1994 | The sentence linking to the 1994 chapter became the Bucket line (T11, O1); the second link to that chapter stays in "Read only what you need", and the GoF "(1994)" credit moved to "For deeper coverage". | pending |
| 2 | number | 3.15 | O6: "Python 3.15 differs on each count" became "Python differs on each count" (incidental mention) | owner O6, 2026-11-08 |
| 2 | number | 3.15 | O6: "the idiom for naming a type in 3.15" became "the idiom for naming a type" (incidental mention; "new in 3.12" stays) | owner O6, 2026-11-08 |
| 6 | number | 3.15 | O6: "In Python 3.15 both forces remain" became "In Python both forces remain" (incidental mention) | owner O6, 2026-11-08 |
| 8 | number | 3.15 | O6: "In Python 3.15 one decorator writes most of it" became "In Python one decorator writes most of it" (incidental mention; the 3.15 error-message fact in the same chapter stays) | owner O6, 2026-11-08 |
| 42 | number | 3.15.2 | O6: "on pytest 9.2.0 and Python 3.15.2" became "on pytest 9.2.0" (incidental mention of the interpreter version; Appendix A states it) | owner O6, 2026-11-08 |
| 43 | number | 3.15.2 | O6: "names a test on pytest-mock 3.17.0 and Python 3.15.2" became "names a test on pytest-mock 3.17.0" (incidental mention; the per-row 3.15.2 measurements stay) | owner O6, 2026-11-08 |

The 12 rows for doc 24 are unsigned (`pending`) until the facts reader signs them at B5a. `prose_invariants.py` reads this table and ignores unsigned rows.

## B4a: integration record

QA steps 2 and 3, PL6 and PL7, run on `release/r26` at ba96856 with the working tree holding only the B4a edits (`git worktree list` shows the main tree alone; `git diff --stat 15cc747 -- examples spikes` is empty). Scratch under the session scratchpad, deleted at the end.

### Waivers prove out

The 12 rows of doc 24 were appended byte for byte, `signed` left as `pending`. In a scratch copy of this file with `pending` replaced by a signature, `uv run python scripts/prose_invariants.py 24 --waivers <scratch>` prints `ok   24-iterator-generators-and-the-iterator-protocol.md, 12 waived`. With the real file the same command reports the 12 waivers as unsigned and ignored and lists the 12 losses (10 quote, 2 number), so only doc 24 fails `--all` (46 docs ok, 1 FAIL) until the facts reader signs at B5a.

### Experiments (QA step 3)

Each ran in a fresh scratch copy of the chapter's example (root `pyproject.toml`, `uv.lock` and the one member, `UV_OFFLINE=1`), after a clean run of the unmodified copy (44 passed in 23, 42 passed in 24). The edit and the command are the chapter's sentence; the timings differ from the quoted ones and nothing else does.

| chapter | experiment | result | quoted output |
| --- | --- | --- | --- |
| 23 | one: compute every decision first | 1 failed, 43 passed in 3.49s; `test_stages_after_a_decision_are_not_called` fails with `assert ['passing', '...ing', 'never'] == ['passing', 'holding']` at `tests/test_chain.py:107`; mypy: no issues in 8 source files | matches (3.34s quoted) |
| 23 | two: drop the released check | 1 failed, 43 passed in 3.51s; `test_a_duplicate_settlement_releases_once` fails with `assert 2 == 1` at `tests/test_mediator.py:91`; mypy: no issues in 8 source files | matches (3.37s quoted) |
| 24 | one: store one iterator | 3 failed, 39 passed in 3.50s; `test_a_tracking_history_can_be_walked_twice`, `test_nested_walks_of_a_tracking_history_are_independent` and `test_iter_of_an_iterator_is_the_iterator_itself` fail with the three quoted assertion lines (`assert 2 == 9` among them); mypy: no issues in 9 source files | matches (3.41s quoted) |
| 24 | two: open without `with` | 8 failed, 34 passed in 3.61s; the 8 quoted `FAILED` lines in the quoted order; mypy: no issues in 9 source files | matches (3.47s quoted), compared by script after dropping the timing |

Chapter 3's `_GUARDED` experiment was not in this step's scope and was not re-run.

### Built pages (QA step 3)

`bash scripts/site-build.sh` ended `site-build: ok (Gemfile.lock unchanged)`.

- Docs 23 and 24: each `<object>` carries `aria-describedby="desc-<name>"`; exactly one `<div id="desc-<name>">` with that id exists, inside one `<details class="figure-description">` with no `open` attribute and the summary "Describe the figure"; its content is a `<p>` with `<code>` spans and curly quotes, with no backtick or asterisk left in it. Doc 3 builds the same way.
- 390 px: headless Firefox (already on the host, nothing installed) loaded the built pages from a throwaway local server, killed by its PID afterwards. With the details opened, the document's `scrollWidth` is 378 against an `innerWidth` of 390, the details' right edge is at 354 and its `scrollWidth` equals its `clientWidth` (328), in both docs: nothing scrolls sideways. The collapsed state was captured too. The screenshots showed only the page top, so the opened description was checked by those numbers, not by eye.
- `*Tests:*` lines: every one renders as `<p><em>Tests:</em> <code>...</code>, <code>...</code>.</p>`: 1 line with 1 code span in doc 3, 13 lines with 33 spans in doc 23, 20 lines with 36 spans in doc 24 (35 names; `test_iter_of_an_iterator_is_the_iterator_itself` is named again under experiment one), none with any other content, and no literal `*Tests:*` in any of the four pages. Doc 1 has none.
- Not checked: the 1280 px view of the details (the sources reader at B5a), and the opened description by eye at 390 px.

### Gates (QA step 2)

- `bash scripts/verify.sh`: `1407 passed in 172.58s (0:02:52)`, `verify: all steps passed`.
- `uv run python scripts/validate.py`: `validate: 0 error(s), 0 warning(s)`; `--self-test`: `self-test: ok`; `--claims`: exit 0, every row resolved, rows 470 to 483 included.
- `prose_invariants.py --self-test`: `prose_invariants self-test passed`. `--all`: 46 docs `ok`; the only FAIL is doc 24 with its 12 pending waivers (the quotations "Each yield temporarily suspends processing...", "This iterator is good for one pass...", "The last batch may be shorter than n", "If strict is true...", "Make an iterator that returns selected elements...", "Return successive overlapping pairs...", "Gets chained inputs from a single iterable argument...", the PEP 479 abstract, "Raises a GeneratorExit exception..." and "Return a context manager that closes thing...", and the numbers 255 and 1994). Docs 1, 3 and 23 pass with no waiver.
- `python3 scripts/host_ids.py check`: `host_ids check: 891 text file(s), 0 hit(s)`.
- The canonical ban scan: `total: 0 matching lines (0 ban-tier) under .`.
- `uv run ruff format --check .`: `670 files already formatted`.
- `render-png.sh --check --deck 101`, `201` and `301`: every PNG `same`, exit 0 for all three.
- Voice scan over the four docs, `--tier terse`: 8 matching lines (01: 2, 03: 2, 23: 1, 24: 3), 0 ban-tier, and no more with `.voice-patterns.tsv`. `--stats` DASH 0 in all four.

### Deck census (PL7)

The 22 sentences of the r22 census for chapters 1, 3, 23 and 24 (3, 8, 6 and 5), plus the Appendix E citation of chapter 24's "Pass the tuple" sentence that the census lists as its sixth, give the plan's 23. Old line numbers are in 15cc747 (the r22 census recorded the lines of an older tree). Each new string was confirmed with `grep -cF -- <string> <doc>` giving 1. Chapter 3's seventh sentence is now two strings (the lead-in and the Strategy bullet), so the table has 24 rows. A pipe inside a string is written `\|` here. No sentence was lost.

| doc | old line | old sentence | new sentence | line | grep -cF | change |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | 25 | `A pattern is a solution to a problem in a context, and the problem is a set of forces pulling against each other.` | `A pattern is a solution to a problem in a context, and the problem is a set of forces pulling against each other.` | 35 | 1 | unchanged |
| 01 | 37 | `Consequences is the ledger.` | `Consequences is the ledger.` | 49 | 1 | unchanged |
| 01 | 39 | `every pattern has a price, paid whether or not the benefit turns up.` | `every pattern has a price, paid whether or not the benefit turns up.` | 51 | 1 | unchanged |
| 03 | 33 | `The first question is about the name.` | `**Does the name mean two things in Python?**` | 49 | 1 | changed |
| 03 | 35 | `The second question is about the force.` | `**Does a language feature resolve the force without the pattern's structure?**` | 51 | 1 | changed |
| 03 | 37 | `And "dissolves" never means "forget it": the force remains` | `**"Dissolves" never means "forget it".** The force remains` | 58 | 1 | changed |
| 03 | 41 | `The first eleven rows of the table are the ones where a Python feature resolves the force without the structure.` | `In the first eleven rows of the table, a Python feature does the pattern's job without its structure.` | 62 | 1 | changed |
| 03 | 79 | `Patterns that survive` | `## Patterns that survive` | 108 | 1 | unchanged |
| 03 | 91 | `Four names mean two things in Python.` | `Four names mean two things in Python.` | 132 | 1 | unchanged |
| 03 | 75 | `` The example shows the dissolved rows at their smallest. A pricing rule is a `Callable[[Consignment], Money]`, so `quote(consignment, rule)` accepts a `def`, a lambda or a `functools.partial` in the same slot and no `RateStrategy` interface exists. `` | `The example shows the dissolved rows at their smallest:` | 96 | 1 | changed |
| 03 | 75 | `` The example shows the dissolved rows at their smallest. A pricing rule is a `Callable[[Consignment], Money]`, so `quote(consignment, rule)` accepts a `def`, a lambda or a `functools.partial` in the same slot and no `RateStrategy` interface exists. `` | `` - **Strategy.** A pricing rule is a `Callable[[Consignment], Money]`, so `quote(consignment, rule)` accepts a `def`, a lambda or a `functools.partial` in the same slot. `` | 98 | 1 | changed |
| 03 | 72 | `\| Proxy \| Needs disambiguating \| A surrogate object vs attribute interception` | `\| Proxy \| Needs disambiguating \| A surrogate object vs attribute interception` | 93 | 1 | unchanged |
| 23 | 38 | `The class that carries the successor link is the part Python removes.` | `Python removes the class that carries the successor link, not the order or the final stage.` | 48 | 1 | changed |
| 23 | 30 | `Each is a decision, and both patterns survive because Python's syntax doesn't make those decisions for you.` | `Python's syntax makes neither choice for you, so both patterns survive` | 22 | 1 | changed |
| 23 | 182 | `With one check, call the function.` | `With one check, call the function.` | 284 | 1 | unchanged |
| 23 | 127 | `Mediator is for a group of parties whose actions depend on one another.` | `A **Mediator** is an object that coordinates a group of parties whose actions depend on one another.` | 191 | 1 | changed |
| 23 | 166 | `The choreography is the other form.` | `The choreography is the other form.` | 260 | 1 | unchanged |
| 23 | 178 | `A mediator knows the messages its colleagues send and decides who acts next` | `A mediator knows the messages its colleagues send and decides who acts next` | 273 | 1 | unchanged |
| 24 | 30 | `The cursor class dissolves, and those three decisions remain.` | `so the cursor class dissolves. Three choices remain: one pass or many, how much to read, and who closes the source.` | 22 | 1 | changed |
| 24 | 47 | `` A function with `yield` is a generator function, and calling it returns a generator iterator. `` | `` A function with `yield` is a generator function, and calling it returns a generator iterator. `` | 60 | 1 | unchanged |
| 24 | 151 | `Pass the tuple when the data is already in a list that callers index or measure.` | `Pass the tuple when the data is already in a list that callers index or measure.` | 224 | 1 | unchanged |
| 24 | 276 | `https://python-patterns.guide/gang-of-four/iterator/` | `https://python-patterns.guide/gang-of-four/iterator/` | 360 | 1 | unchanged |
| 24 | 276 | `https://peps.python.org/pep-0255/` | `https://peps.python.org/pep-0255/` | 360 | 1 | unchanged |
| 24 | 151 | `Pass the tuple when the data is already in a list that callers index or measure.` | `Pass the tuple when the data is already in a list that callers index or measure.` | 70 in 45 | 1 | unchanged (the Appendix E Iterator row holds it; the census cites it a second time) |

Totals: 3 + 8 + 6 + 6 = 23, the plan's figure, with no difference. Chapter 1: 3 of 3 unchanged. Chapter 3: 5 of 8 changed (the two questions, the "dissolves" rule, the first-eleven-rows sentence and the "example shows" sentence). Chapter 23: 3 of 6 changed. Chapter 24: 1 of 6 changed. 9 of 23 changed, 14 unchanged.

### Reconciliation (PL6)

Rows 3, 4, 120 to 133, 313, 316, 317, 341 to 343 and 348 carry an r26 note (the claim is unchanged in every one); rows 470 to 483 are added. `validate.py --claims` passes. Rows 470, 471 and 475 to 479 are `open`: B5a closes them (the invariants sweep, the `*Tests:*` sweep, the three definitions with their Bucket lines, the doc 3 wording and the 12 waivers).
