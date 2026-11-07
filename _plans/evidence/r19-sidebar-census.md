# r19 AI sidebar census

Date: 2026-11-07. Counted over `_docs/` on the release/r19 branch at step V2, before chapters 39 and 40
were written (both are stubs, so they show as having no sidebar). Reconciliation row 246 rests on
this file. Run each command from the repository root; the counts below are the output of that run.

## Commands and counts

1. Documents in `_docs/`:

   ```bash
   ls _docs/*.md | wc -l
   ```

   47.

2. Sidebars per document (the book's check, `grep -c` equals 1), tallied by count:

   ```bash
   grep -c '<blockquote class="ai-sidebar"' _docs/*.md | awk -F: '{n[$2]++} END{for(k in n) print k, n[k]}'
   ```

   `1 34` and `0 13`: 34 documents have exactly one sidebar, 13 have none, and no document has two or more.

3. Documents with a sidebar, and the total of opening tags:

   ```bash
   grep -l '<blockquote class="ai-sidebar"' _docs/*.md | wc -l
   grep -h '<blockquote class="ai-sidebar"' _docs/*.md | wc -l
   ```

   34 and 34.

4. The explicit form, and the kramdown form that must not appear:

   ```bash
   grep -h '<blockquote class="ai-sidebar" markdown="1">' _docs/*.md | wc -l
   grep -c '{: .ai-sidebar}' _docs/*.md | grep -v ':0$' | wc -l
   ```

   34 and 0.

5. The documents with no sidebar:

   ```bash
   grep -L '<blockquote class="ai-sidebar"' _docs/*.md
   ```

   `00-prerequisites`, `01-patterns-as-decisions-under-forces`, `02-what-1994-assumed-and-python-dissolves`,
   `03-the-three-way-split`, `04-naming-patterns-for-teams-and-ai`, `39-final-project`,
   `40-working-with-ai-and-llm-tools` and the six appendices `41` to `46`. That is 13: chapters 0 to 4, the two stubs
   (39 and 40, which the plan gives one sidebar each) and the six appendices.

6. Shape of each sidebar. Inside each `<blockquote class="ai-sidebar"` ... `</blockquote>`, count the
   nested prompts (a run of lines that start `> `) and the review lines (a plain paragraph line, not
   bold, not quoted, after the prompt):

   ```bash
   awk 'FNR==1{inb=0} /<blockquote class="ai-sidebar"/{inb=1;p=0;r=0;st=0;next} inb&&/<\/blockquote>/{inb=0; printf "%s prompts=%d review=%d\n", FILENAME,p,r; next} inb{ if($0 ~ /^> /){ if(!st){p++;st=1} } else if($0 ~ /^[^ >*\r]/ && $0 !~ /^\*\*/ ){ st=0; r++ } else st=0 }' _docs/*.md | awk '{print $2,$3}' | sort | uniq -c
   ```

   `34 prompts=1 review=1`: every one of the 34 sidebars has exactly one nested prompt and one review line.

7. The heading each sidebar sits under:

   ```bash
   awk 'FNR==1{h=""} /^## /{h=$0} /<blockquote class="ai-sidebar"/{print h}' _docs/*.md | sort | uniq -c
   ```

   23 under `## When not to use it`; 2 under `## When the principle costs more than it buys`; and 1 each under
   `## Characterise, then refactor`, `## Refactor or rewrite: the decision`, `## Techniques Python makes unnecessary`,
   `## When a dunder costs more than it buys`, `## When a patch is the wrong seam`, `## When asyncio is the wrong tool`,
   `## When a test proves less than it seems`, `## When the structure is justified` and `## When threads are the wrong tool`.
   The total is 34.

## What the chapter may say

The book's sidebar has one form in 34 of its 47 documents: a problem in a sentence or two, one nested prompt that
names the chapter's rule, and one review line. Chapters 39 and 40 are planned to add one each, which would make 36; the
greps are repeated after they are written and the chapter quotes the counts of that run.

## Re-run after chapters 39 and 40, 2026-11-07

The same commands, run from the repository root on the release/r19 branch after both chapters were written. The
counts below are the output of that run.

1. Documents in `_docs/`: 47.
2. Sidebars per document: `1 36` and `0 11`. Thirty-six documents have exactly one sidebar, 11 have none, and no
   document has two or more.
3. Documents with a sidebar and the total of opening tags: 36 and 36.
4. The explicit form and the kramdown form: 36 and 0.
5. The documents with no sidebar are chapters 0 to 4 (`00-prerequisites`, `01-patterns-as-decisions-under-forces`,
   `02-what-1994-assumed-and-python-dissolves`, `03-the-three-way-split`, `04-naming-patterns-for-teams-and-ai`) and
   the six appendices `41` to `46`. That is 11. Chapters 5 to 38 carry one each, and so do chapters 39 and 40.
6. Shape: `36 prompts=1 review=1`. Every one of the 36 sidebars has exactly one nested prompt and one review line.
7. Headings: the 34 counted above, plus one under `## When the composition is the wrong shape` (chapter 39) and one
   under `## When the gates aren't enough` (chapter 40). The total is 36.
