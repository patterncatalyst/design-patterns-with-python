---
title: "Evidence: r26 pilot"
output: false
render_with_liquid: false
---

# r26 pilot

Baseline taken at B0 on `release/r26` at ef103c2 (the r25 merge 15cc747 plus the plan and owner-decision commits). Every number below is a fresh run; the plan's figures are compared in "Differences from the plan". No doc, script or deck was changed to take them.

## Owner decisions (2026-11-08, plan gate)

- O1: decision 1 takes the alternative, the Camel layout: one H2 per pattern with H3 subheads (`## Pattern: <Name>`, then `### The problem`, `### The solution`, `### How Python models it`, then topic H3s). GT2, GT6, PL3, PL4, the targets, the excerpts and the criteria follow it.
- O2: decisions 2 to 6 as recommended.
- O3: the Feathers title takes the book's straight house form, "I Need to Make a Change, but I Don't Know What Tests to Write".
- O4: hub PR #62 was merged as 9a3b034; no open hub item remains.

The owner's go or adjust answer after the reading packet is recorded here at B6.

## Owner checks

(B2a copies evidence H of the plan here: the O'Reilly chapter title check of 2026-11-08, the link check, and the route for O'Reilly facts.)

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

## Waivers

| doc | kind | value | reason | signed |
| --- | --- | --- | --- | --- |

(Empty. `prose_invariants.py` reads this table from B1b on.)
