---
title: "r17 plan: chapters 35-36 (Fowler vs Feathers, contrasted and combined; Refactor or rewrite)"
order: 17
output: false
render_with_liquid: false
---

# r17: chapters 35-36, Fowler vs Feathers, contrasted and combined; Refactor or rewrite

Opus-planned 2026-11-06. Branch `release/r17`, cut from main at da1b362 (the r16 merge). This file is the source of truth for r17 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No toolchain work this iteration. Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4, uv 0.13.7 and uv_build 0.13.7 match PyPI and python.org (checked 2026-11-06: pytest 9.2.0 of 2026-10-27, pytest-mock 3.17.0 of 2026-10-17, ruff 0.17.4 of 2026-11-05, mypy 2.4.1 of 2026-10-28, uv and uv-build 0.13.7 of 2026-11-03; python.org lists 3.15.0 to 3.15.2 as releases, and its 3.16.0 directory holds only 3.16.0a1, a pre-release). T0 re-checks before any edit. `uv.lock` changes only because two members are added.

Exact chapter identities, from `scripts/chapters.toml` and the `_docs` front matter:
- ch35: slug `35-fowler-vs-feathers`, title "Fowler vs Feathers, contrasted and combined", part 11 (`changing-inherited-code`), `kind = "argument"`, `has_example = false` (T0 sets `true`, decision 1), `status = "stub"`. The stub carries a `## The argument` heading that the draft drops.
- ch36: slug `36-refactor-or-rewrite`, title "Refactor or rewrite", part 11, `kind = "argument"`, `has_example = false` (T0 sets `true`), `status = "stub"`. Same stub heading, also dropped.

`validate.py` SPINE for `argument`: Learning objectives, Why this matters, What you can do now, For deeper coverage. No sidebar count is enforced (the count check runs only for `kind == "pattern"`). One figure is required (any kind but `appendix`), and the word ceiling (2,500) is an error, the floor (1,900) a warning. `has_example` is metadata only: `validate.py` never reads it. The argument-with-example model is "Anti-patterns and pattern misuse" (ch32), which adds `## Build, run, observe` and one sidebar.

Work items: PDP-135a-c (ch35 example, figure, prose) and PDP-136a-c (ch36), `todo` in `_plans/iteration-plan.md`.

## User decisions (owner confirmed 2026-11-06: all as recommended)

0. **Step ids.** The steps are T0 to T7. `validate.py --claims` resolves `run: <id>` against the steps tables of every `_plans/r*-plan.md`. At planning time `grep -nE '^\| T[0-9]' _plans/*.md` and `grep -n 'run: T' _plans/*.md` both print nothing. Following r16's practice, only suffixed ids are cited as `run:` tokens: `T1a`, `T1b`, `T5a` and `T5b`. Plain T0, T2, T3, T4, T6 and T7 appear only in this plan's table.

   **Recommend: yes.**

1. **Both chapters build an example: `has_example = true`, `kind` stays `argument`.**
   - **Why ch35 needs one.** Domain row 35's failure ("a refactor without characterisation changes a rounding rule and a golden test fails") is a claim about code. Under the house rule it needs a test, and the chapter's contrast between "tests from the requirement" and "tests that record what the code does" is only convincing as a measured result: four intent rows pass a refactor that moves 18 totals by a cent (evidence C). Prose alone would assert it.
   - **Why ch36 needs one.** Domain row 36 names a parity test that fails on a boundary `Weight` and a strangler-style adapter. Both are code; a parity table that never ran is the anecdote the chapter is meant to replace.
   - **Precedent.** ch32 (r15 decision 1) and ch3 are `argument` chapters with `has_example = true`.
   - **H2s.** ch35 adds `## Two books, one activity`, `## The contrast`, `## Tests written from the requirement`, `## Golden values`, `## Refactoring under the golden quotes`, `## Characterise, then refactor` (holds the sidebar) and `## Build, run, observe`. ch36 adds `## The forces`, `## A legacy engine and its rewrite`, `## The parity table`, `## A strangler-style router`, `## Refactor or rewrite: the decision` (holds the sidebar) and `## Build, run, observe`. Neither has `## When not to use it`; neither is a pattern chapter.

   **Recommend: yes, both.** Alternative: ch35 argued in prose only, as ch1 is. That leaves row 35's failure without a witness, and ch34's table already shows a half-even mutant failing, so ch35 would have nothing new to measure.

2. **One AI sidebar per chapter** in the 2026-11-05 form: a problem, a nested prompt that bakes in the chapter's rule, at most one review line. No sentence says what assistants or models produce. A criterion enforces the count, because validate doesn't for argument chapters.

   **Recommend: yes.** Alternative: no sidebar, as in chapters 1 to 4. The part's deck (301) names the AI throughline, and ch32 set the argument-chapter precedent.

3. **No mocks, `mocker` or `monkeypatch` in r17.** The r16 exception (r16 decision 2) was scoped to ch33's tests and ch34's legacy fixture branch, and it is not extended.
   - ch35's starting engine is the one the dependency-breaking chapter produced after parameterising the constructor: it takes `fastline_quote`, `airco_price` and `margin` as keyword parameters with the real SDK calls as defaults. Tests pass plain fake functions. ch35 points to "Dependency-breaking techniques for modern Python" for that step and doesn't re-teach it.
   - ch36's engines are pure functions of a consignment, so they need no fakes at all; the router's tests use small plain quoters.

   **Recommend: yes.** Alternative: start ch35 from the unparameterised legacy engine and patch it. That would extend the mock exception and repeat the seams chapter.

4. **Golden values in plain pytest, no new dependency.**
   - **A golden file** `tests/golden/rate_quotes.json` (sorted keys, two-space indent, trailing newline) records what the legacy engine quotes over a generated grid of 120 consignments (evidence C). A test checks the file still equals the legacy engine's output (provenance), and another checks the refactored engine against it.
   - **Inline golden values** pin five named rows in the test module, readable in review.
   - **Comparison as an ordered list.** Tests assert `_mismatches(observed, golden) == []`, a list of `"<row>: golden <g>, now <o>"` strings in grid order. Never a dict equality: pytest 9.2.0's dict diff orders differing keys through a set, so the quoted failure changes between runs (evidence B).
   - **Regeneration.** A `--update-golden` option registered by `pytest_addoption` in the member's `tests/conftest.py`. With it, the provenance test writes the file from the legacy engine and calls `pytest.skip("golden file rewritten; review the diff")`. Without it, nothing writes. Evidence D shows the option works from the member directory and from the root under `--strict-config`.
   - **Approval libraries** (syrupy, approvaltests, inline-snapshot) are named with their PyPI pages and one clause each, as the tools that package this workflow. None is added. pytest's own list diff is enough for a table this size, and a dependency would be the only one in the book outside the dev group.

   **Recommend: yes.** Alternatives: (a) no writer, with the file kept by hand and guarded only by the provenance test; (b) add syrupy to the dev group. (a) is acceptable and smaller; (b) adds a pin for one chapter.

5. **ch35's refactorings and hazards.** The refactored engine `refactored.py` applies two catalogue refactorings whose names were verified on refactoring.com (evidence H): **Extract Function** (`_cheapest`, `_with_margin`) and **Replace Primitive with Object** (carrier prices become `Money`, kept at full precision). The hazards are test-only mutants and experiments:
   - `_CentFirstRateEngine`: Replace Primitive with Object done with a `Money` that is rounded to the cent when created. It changes 18 of 120 golden rows by a cent and passes every intent row.
   - `_RoundBuiltinRateEngine`: **Substitute Algorithm**, `round(amount, 2)` in place of `quantize(CENT, rounding=ROUND_HALF_UP)`. It changes exactly `EU-30` and `ASIA-30`, the only half-cent totals in the grid (evidence C, E).

   ch34 already showed a half-even mutant failing a hand-picked row, so ch35's distinct claims are: a test written from the requirement doesn't pin these; a generated grid finds boundaries nobody chose; and the failure reads in a stable order.

   **Recommend: yes.** Alternative: only the `round()` experiment. It overlaps ch34 more, and it fails only two rows.

6. **ch36's legacy engine, rewrite and divergence.**
   - **Legacy** (`legacy.py`): `RateEngine.quote` prices by weight band in an `if`/`elif` chain with inclusive upper limits (`kg <= 5`, `<= 20`, `<= 50`), adds the margin and rounds half up. The `else` branch prices every zone other than ASIA with EU prices, so an unknown zone gets EU prices. That's an inherited quirk, kept as found.
   - **Rewrite** (`rating.py`): a frozen `Tariff(upper_kg, prices)` with `STANDARD_TARIFF`, and `quote(consignment, /, *, tariff=STANDARD_TARIFF)` that finds the band with `bisect_left`, which keeps limits inclusive, and refuses an unknown zone with `RatingError`. It uses the domain's `Weight` (`kilograms: Decimal`, as in the Strategy and Command members).
   - **The divergence.** The test-only first draft `_exclusive_limits_quote` uses `bisect_right`: at exactly 5, 20 and 50 kg it moves the consignment to the next band, and at 50 kg it raises (evidence F). That's the domain row's boundary `Weight`.
   - **A deliberate difference** is recorded, not hidden: `ACCEPTED_DIFFERENCES = ["AFRICA-5"]` (the rewrite refuses an unknown zone). The parity test asserts the mismatch list equals it exactly, so it fails on a new divergence and on a stale accepted one.

   **Recommend: yes.** Alternative: a `float` against `Decimal` divergence. It exists (evidence F, last line) but needs a weight like 5.0000000000000001 kg, which reads as contrived.

7. **The strangler-style router** (`strangler.py`).
   - `type RateQuoter = Callable[[Consignment], RateQuote]`.
   - A frozen slotted `Mismatch(consignment_id, legacy: str, rewrite: str)`.
   - A frozen slotted `Router(legacy, rewrite, migrated: Container[str], report: Callable[[Mismatch], None] | None = None)`, with `__call__`: a migrated zone goes to the rewrite; any other is served by the legacy engine, and, when `report` is set, the rewrite also runs in shadow and any difference or `RatingError` is reported, never served. That's the Dark Launching pattern, cited by its fetched intent (evidence I).
   - `MIGRATED_ZONES = ("ASIA",)` and `quote_routed = Router(RateEngine().quote, quote, MIGRATED_ZONES)` at the module's root.
   - Prose calls it a strangler-style router (the domain row's "adapter") and says in one clause that it routes calls and converts no interface, so it isn't the Adapter pattern. One pointer to "Adapter, Facade, and Bridge".

   **Recommend: yes.** Alternative: a plain function with a `migrated` parameter. A frozen dataclass keeps the root binding inspectable (test 12) and the shadow callback optional.

8. **The decision rule rests on forces and tests, not on outcomes.** ch36 names four forces, each with a witness:
   - how much existing behaviour can be named: the parity table;
   - which behaviour should change: `ACCEPTED_DIFFERENCES`;
   - whether a seam exists to route by: the zone, and the router;
   - what the transitional code costs: the router is code that goes once every zone is migrated (test 11).

   No sentence claims how often rewrites or refactors succeed, how long they take, or any statistic. The outcome sentences on the fetched pages are not quoted or paraphrased: Strangler Fig's "go down in flames most of the time" and Feature Parity's "learnt the hard way". Criterion 20 greps for them.

   **Recommend: yes.**

9. **Citations** (evidence G to J). Every book is already in `bibliography.html` (Feathers, Prentice Hall 2004; Fowler, *Refactoring* 2nd ed., Addison-Wesley 2018).
   - **Feathers**, by verified chapter title (InformIT table of contents and the publisher's chapter 1 sample): "Changing Software", "I Need To Make a Change but I Don't Know What Tests To Write", "Dependency Breaking Techniques", "How Do I Know That I'm Not Breaking Anything?", and the appendix "Refactoring". Paraphrase only. ch35 paraphrases chapter 1's point that refactoring and optimisation hold functionality invariant while structure or resource use changes. ch36 paraphrases its three questions for reducing the risk of a change.
     - [Bracketed, unverified: Feathers's definition of legacy code as code without tests (Preface). Not used unless T5a verifies it on a fetched page; otherwise the book's subject is described through its chapter titles.]
   - **Fowler's *Refactoring* 2nd ed.** is cited by topic and book title only. InformIT's second-edition page lists first-edition chapters (evidence J), so no second-edition chapter title counts as verified.
     - [Bracketed: "Principles in Refactoring", "Building Tests". Use only if T5a verifies them against a second-edition source; otherwise "the book's chapter on building tests" by topic.]
     - Quotations come only from fetched Fowler pages: the Definition Of Refactoring bliki, refactoring.com's opening paragraph, the Self Testing Code bliki, Legacy Seam and Strangler Fig.
     - Refactoring names used (Extract Function, Replace Primitive with Object, Substitute Algorithm, Replace Magic Literal) were verified as second-edition entries in the refactoring.com catalogue.
   - **Cartwright, Horn and Lewis**, "Patterns of Legacy Displacement" on martinfowler.com: the intent sentences of Feature Parity, Transitional Architecture, Dark Launching and Legacy Mimic, quoted exactly and credited to the three authors. Web articles stay in the chapter, not in the bibliography.

   **Recommend: yes.**

10. **The contrast table is written fresh.** The Notion outline says "same contrast table as C++ ch29". CLAUDE.md makes the sibling books reference-only, never a source, so the table is built from the fetched sources and this example's tests, and nobody opens the C++ chapter for it.

    **Recommend: yes.**

11. **Domain names** come from `_plans/shipping-domain-model.md` rows 33 to 36, the Rating area (`Tariff` maps zone and weight band to `Money`; `RatingError`) and `Weight` (rows 0, 8, 12, 15). No new domain area, no new carrier code.
    - **ch35** (package `fowler_feathers`): `ConsignmentId`, `Consignment(id, zone, weight_kg: Decimal)`, `Money`, `RateQuote(consignment_id, carrier, total)`, `CarrierTimeoutError`, `fastline.request_quote`, `airco.price`, `FastlineQuote`, `AircoPrice`, `MARGIN`, `RateEngine`, plus `CENT` (new supporting name).
      - Test-only: `INTENT_ROWS`, `GRID`, `INLINE_GOLDEN`, `_CentFirstRateEngine`, `_RoundBuiltinRateEngine`, `_fastline_card`, `_airco_card`.
    - **ch36** (package `refactor_or_rewrite`): `ConsignmentId`, `Weight(kilograms: Decimal)`, `Consignment(id, zone, weight: Weight)`, `Money`, `RateQuote(consignment_id, total)`, `RatingError`, `MARGIN`, `RateEngine`, `Tariff`, `STANDARD_TARIFF`, `quote`, plus new supporting names `RateQuoter`, `Mismatch`, `Router`, `MIGRATED_ZONES`, `quote_routed`.
      - Test-only: `PARITY_ROWS`, `ACCEPTED_DIFFERENCES`, `_exclusive_limits_quote`, `_refusing_quoter`.
    - Zones `EU`, `ASIA`, and `AFRICA` as the unknown zone. Prices are illustrative.

    **Recommend: yes.**

12. **Scope cuts**, recorded here and in the T2 spikes note:
    - approval-library dependencies (decision 4);
    - property-based testing (hypothesis) for parity;
    - Branch by Abstraction, feature-flag libraries, percentage rollouts, which would need randomness;
    - Event Interception and the other displacement patterns beyond the four quoted;
    - coverage and mutation-testing tools;
    - the `float` against `Decimal` divergence (evidence F), kept as a spike note;
    - free-threading and asyncio.

    **Recommend: yes.**

13. **No cross-language wording.** Fowler's examples are in JavaScript and Feathers's mostly in Java and C++. Neither fact appears in reader text. Criterion 14's grep enforces it.

    **Recommend: yes.**

Also proposed for the owner (no decision needed unless declined):
- **No new books.**
- **A dated r17 note** in `_plans/spikes.md` at T2: evidence B to F and the decision 12 cuts.

## Planning evidence

Probes ran with the session scratchpad as the working directory, outside the repo, so the root config didn't apply. The scratch directory (`<scratchpad>/plan17`) was created for multi-file probes and deleted afterwards; the repo was unchanged (`git status --short` empty).
- Runtime: `<repo>/.venv/bin/python -I`, version `3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- mypy: `<repo>/.venv/bin/python -I -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary`, `mypy 2.4.1 (compiled: yes)`.
- ruff 0.17.4 with `--isolated --line-length 100 --select E,F,W,I,UP,B,SIM,RUF,PT,N --target-version py315`.
- pytest 9.2.0.

The models are reduced models: names differ from the member's dotted names, and every output is a prediction until the build quotes it as observed.

**A. Pins.** `pytest 9.2.0 2026-10-27`, `pytest-mock 3.17.0 2026-10-17`, `ruff 0.17.4 2026-11-05`, `mypy 2.4.1 2026-10-28`, `uv 0.13.7 2026-11-03`, `uv-build 0.13.7 2026-11-03`.
- python.org: 3.15.0, 3.15.1 and 3.15.2 are releases, and `ftp/python/3.16.0/` holds only `Python-3.16.0a1`. No bump.
- Named, not added: `syrupy 6.1.1 2026-09-13` ("Pytest Snapshot Test Utility"), `approvaltests 20.0.1 2026-10-25`, `inline-snapshot 0.36.1 2026-10-12`. Summaries come from PyPI JSON. Prose quotes nothing from them beyond the project name and its PyPI link.

**B. pytest's dict diff is not reproducible.** A golden dict of 120 entries against a refactor that changes 18. The plain `assert observed == golden` gives:
```
E       AssertionError: assert {'EU-0.5': 'F...NE 6.48', ...} == {'ASIA-0.5': ...E 24.92', ...}
E         Omitting 89 identical items, use -vv to show
E         Differing items:
E         {'ASIA-5.5': 'FASTLINE 18.40'} != {'ASIA-5.5': 'FASTLINE 18.41'}
```
- Three runs printed `ASIA-14.5`, then `ASIA-5.5`, then `ASIA-0.5` as the first differing item.
- The cause is in `_pytest/assertion/_compare_mapping.py`: `common = keys_left & keys_right` and `diff = {k for k in common if left[k] != right[k]}`, a set of strings in hash-seed order.
- A list comparison is stable: `assert ['EU-1', 'EU-1.5', 'EU-3.5'] == []` printed `Left contains 3 more items, first extra item: 'EU-1'` and `Use -v to get more diff`. An inline list of tuples printed `At index 1 diff: ('FASTLINE', '5.56') != ('FASTLINE', '5.55')`.
- The member asserts lists only (decision 4).
- A quick search of pytest's issues ("Differing items", "dict comparison order") found no report of this. Not filed.

(The counts in B came from an earlier grid; C is the grid the member uses.)

**C. The grid and the two rounding refactors.** The engine model is the parameterised legacy body:
- `min` over `{"AIRCO": cents / 100, "FASTLINE": price}` with key `(price, code)`;
- times `MARGIN = 1.10`;
- `quantize(Decimal("0.01"), ROUND_HALF_UP)`.

Rate cards:
- FASTLINE: `base + per_kg * weight_kg`, with EU `4.20 + 0.845/kg` and ASIA `9.50 + 1.315/kg`.
- AIRCO: `fixed + step * started 500 g`, with EU `300 + 48` cents and ASIA `800 + 70` cents.

Weights run from 0.5 to 30 kg in 0.5 kg steps, giving ids such as `EU-0.5` and `ASIA-30`: 120 rows. Results:
- **Carriers.** EU: AIRCO wins up to `EU-10`, FASTLINE above. ASIA: AIRCO wins 35 rows, FASTLINE 25.
- **Samples:** `EU-0.5 AIRCO 3.83`, `EU-11 FASTLINE 14.84`, `EU-30 FASTLINE 32.51`, `ASIA-0.5 AIRCO 9.57`, `ASIA-30 FASTLINE 53.85`.
- **Cent-first** (carrier prices quantised half up before the margin): 18 mismatches, in grid order `['EU-11', 'EU-13', 'EU-15', 'EU-16.5', 'EU-17', 'EU-18.5', 'EU-19', 'EU-21', 'EU-21.5', 'EU-23.5', 'EU-25.5', 'ASIA-19', 'ASIA-19.5', 'ASIA-20.5', 'ASIA-23', 'ASIA-25', 'ASIA-25.5', 'ASIA-26.5']`. The first is `EU-11 FASTLINE 14.84` against `FASTLINE 14.85`. No carrier flips.
- **`round(x, 2)`**: 2 mismatches, `['EU-30', 'ASIA-30']`: `FASTLINE 32.51` against `32.50`, and `53.85` against `53.84`. 29.55 x 1.10 is 32.505, the only exact half cent in the EU rows.
- **Intent rows.** `(25.00, 2800) -> FASTLINE 27.50`, `ASIA (60.00, 5450) -> AIRCO 59.95`, `(20.00, 2000) -> AIRCO 22.00` and `(10.15, 2000) -> FASTLINE 11.17`. Legacy and cent-first agree on all four. The member's fourth intent row is `(30.00, 4000) -> FASTLINE 33.00`, a round price, so both mutants pass every intent row (executor check for the round-builtin form).
- These agree with the r09 spikes note: per-step rounding to cents disagrees on a large share of per-kilogram prices.

**D. `pytest_addoption` in a member conftest.** A reduced workspace: a root `pyproject.toml` with the repo's `addopts` (`--import-mode=importlib --strict-markers --strict-config`), `testpaths = ["examples"]` and `filterwarnings = ["error"]`, plus `examples/m1/tests/conftest.py` adding `--update-golden` (`store_true`).
- A test reading `request.config.getoption("--update-golden")` passed from the member directory and from the root: `1 passed` both times.
- Risk: a second member registering the same option would conflict, so criterion 2 greps for that.

**E. `round()` and `Decimal`, from the docs** (https://docs.python.org/3/library/decimal.html, banner "Python 3.15.2 documentation"). Under `Decimal`:
- "If ndigits is an int, the context’s rounding mode is respected and a Decimal representing number rounded to the nearest multiple of Decimal('1E-ndigits') is returned". The apostrophe is curly on the page, so the quotation keeps it or stops before "context".
- The default context shows `rounding=ROUND_HALF_EVEN`.
- `ROUND_HALF_UP`: "Round to nearest with ties going away from zero."
- Runtime: `round(Decimal('11.165'), 2) = Decimal('11.16')`.
- mypy reveals `decimal.Decimal` for `round(Decimal("1.5"), 2)` and `int` for `round(Decimal("1.5"))`, exit 0.

**F. Parity, first draft and router (reduced model).** Legacy if-chain (EU via `else`, ASIA explicit; inclusive limits 5, 20, 50; `RatingError(f"no band for {kg} kg")` above 50); rewrite `bisect_left` over `(5, 20, 50)`; rows EU, ASIA and AFRICA at 0.5, 5, 5.001, 20, 20.5 and 50:
```
rewrite       ['AFRICA-0.5', 'AFRICA-5', 'AFRICA-5.001', 'AFRICA-20', 'AFRICA-20.5', 'AFRICA-50']
first draft   ['EU-5', 'EU-20', 'EU-50', 'ASIA-5', 'ASIA-20', 'ASIA-50', 'AFRICA-0.5', 'AFRICA-5', 'AFRICA-5.001', 'AFRICA-20', 'AFRICA-20.5', 'AFRICA-50']
first draft detail [('EU-0.5', '13.20', '13.20'), ('EU-5', '13.20', '27.50'), ('EU-5.001', '27.50', '27.50'), ('EU-20', '27.50', '52.80'), ('EU-20.5', '52.80', '52.80'), ('EU-50', '52.80', 'RatingError: no band for 50 kg')]
13.20 13.20 [Mismatch(consignment_id='CN-1', legacy='13.20', rewrite="RatingError: no tariff for zone 'AFRICA'")]
13.20 [Mismatch(consignment_id='CN-1', legacy='13.20', rewrite='27.50')]
True False
```
- The third line is a router with `migrated = {"ASIA"}` and a report list: AFRICA-5 is served `13.20` and reports the refusal. EU-5 is served `13.20` with no report.
- The fourth line is a router whose rewrite is the first draft: EU-5 is served `13.20` and reports `27.50`.
- The last line: `float(Decimal("5.0000000000000001")) <= 5.0` against `Decimal(...) <= 5`. That divergence is noted and cut (decision 6).
- The member uses one unknown-zone row (`AFRICA-5`) and adds a 60 kg row per zone (both engines raise the same message), so the planned first-draft list is `["EU-5", "EU-20", "EU-50", "ASIA-5", "ASIA-20", "ASIA-50", "AFRICA-5"]` (executor check).
- mypy on the model: exit 0. ruff: only two unused imports, which were probe leftovers. Idiom scan: 0 hits on the model.
- A rewrite of the wrong shape: `Router(RateEngine().quote, by_weight, ...)` with `by_weight(zone: str, weight: Weight) -> RateQuote` gives `error: Argument 2 to "Router" has incompatible type "Callable[[str, Weight], RateQuote]"; expected "Callable[[Consignment], RateQuote]"  [arg-type]`. `quote` with keyword-only defaults is accepted. (The probe's `...` body also gave `[empty-body]`; the member's snippet gives the function a body.)

**G. Feathers, fetched 2026-11-06.**
- InformIT table of contents (https://www.informit.com/store/working-effectively-with-legacy-code-9780131177055):
  - Part I "The Mechanics of Change": "1. Changing Software.", "2. Working with Feedback.", "3. Sensing and Separation.", "4. The Seam Model.", "5. Tools."
  - Part II includes "13. I Need To Make a Change but I Don't Know What Tests To Write.", "23. How Do I Know That I'm Not Breaking Anything?" and "24. We Feel Overwhelmed. It Isn't Going To Get Any Better."
  - Part III "25. Dependency Breaking Techniques.", then "Appendix: Refactoring." and "Glossary."
  - Apostrophes are curly on the page; prose uses straight ones, and titles are cited without the trailing full stop.
- The publisher's chapter 1 sample (`.../samplechapter/0131177052_ch01.pdf`), "Changing Software". For paraphrase only:
  - four reasons to change software (adding a feature, fixing a bug, improving the design, optimising resource usage);
  - improving design without changing behaviour is called refactoring, done in small steps with tests;
  - refactoring and optimisation hold functionality invariant while structure or resource usage changes;
  - three questions for reducing the risk of a change: what changes must be made, how to know they were made correctly, and how to know nothing was broken.
  - The sample's table and figure are not reproduced.

**H. Fowler, fetched 2026-11-06.** Prose quotes only these sentences, exactly as on the page. US spelling inside a quotation stays.
- Definition Of Refactoring (https://martinfowler.com/bliki/DefinitionOfRefactoring.html, 1 September 2004): "Refactoring (noun): a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior."
- refactoring.com (https://refactoring.com/): "Its heart is a series of small behavior preserving transformations."
- Self Testing Code (https://martinfowler.com/bliki/SelfTestingCode.html, 1 May 2014): "Self-Testing Code is the name I used in Refactoring to refer to the practice of writing comprehensive automated tests in conjunction with the functional software."
- Legacy Seam (https://martinfowler.com/bliki/LegacySeam.html, 4 January 2024): "When working with a legacy system it is valuable to identify and create seams: places where we can alter the behavior of the system without editing source code." The page credits Feathers for the term.
- Strangler Fig (https://martinfowler.com/bliki/StranglerFigApplication.html). The page `<title>` is "Strangler Fig", dated 22 August 2024; a footnote says the original post was titled "Strangler Application", later "Strangler Fig Application". Quotable:
  - "Replacements seem easy to specify, but often it's hard to figure out the details of existing behavior." (straight apostrophe in the raw HTML)
  - "As we do this we move bits of behavior from the legacy system into the new code base."
  - Not to be used: the sentences about how often replacement plans fail (decision 8).
- Catalogue (https://refactoring.com/catalog/). Second-edition entries (`data-books` contains `refactoring2`) include Extract Function, Replace Primitive with Object, Substitute Algorithm, Replace Magic Literal, Split Phase and Slide Statements.
- The book page (https://martinfowler.com/books/refactoring.html) gives "by Martin Fowler, with Kent Beck", 2018, and "around seventy refactorings". Prose gives no count.

**I. Patterns of Legacy Displacement** (Ian Cartwright, Rob Horn and James Lewis; https://martinfowler.com/articles/patterns-legacy-displacement/, 5 March 2024). Intent sentences:
- Feature Parity (`feature-parity.html`, 27 July 2021): "Replicate existing functionality of a legacy system using a new technology stack."
- Transitional Architecture (`transitional-architecture.html`, 28 March 2022): "Software elements installed to ease the displacement of a legacy system that we intend to remove when the displacement is complete."
- Dark Launching (`dark-launching.html`, a stub page): "Call a new back end feature without using results in order to assess its performance impact." Prose says the router's shadow mode borrows the idea for a comparison of results rather than a performance check, and quotes only this sentence.
- Legacy Mimic (`legacy-mimic.html`, 12 January 2022): "New system interacts with legacy system in such a way that the old system is not aware of any changes." Optional; used only if the router section needs it.
- Not used: Feature Parity's sentences about effort being underestimated (decision 8).

**J. Publisher defect.** https://www.informit.com/store/refactoring-improving-the-design-of-existing-code-9780134757599 is the second edition (2nd edition, copyright 2019 on the page, 448 pages), but its "Table of Contents" lists first-edition chapters ("6. Composing Methods" to "15. Putting It All Together"). Fowler's "Changes for the 2nd Edition" (https://martinfowler.com/articles/refactoring-2nd-changes.html, 5 September 2018) says the four narrative chapters remain and the testing chapter was redone. The O'Reilly search confirms the 2nd edition (Addison-Wesley Professional, 2018-11-27, 448 pages) but gives no chapter list; the O'Reilly page itself returned 403. Hence decision 9's bracketed titles. Not filed.

**K. Other docs, fetched 2026-11-06.**
- bisect (https://docs.python.org/3/library/bisect.html), `bisect_left`: "If x is already present in a, the insertion point will be before (to the left of) any existing entries." `bisect_right`: "Similar to bisect_left(), but returns an insertion point which comes after (to the right of) any existing entries of x in a."
- Built-in `round` (https://docs.python.org/3/library/functions.html): "if two multiples are equally close, rounding is done toward the even choice". Not needed if E's decimal sentence is used.
- json (https://docs.python.org/3/library/json.html): the T5a agent quotes the `sort_keys` sentence after fetching it.

**L. Repo facts.**
- **Reconciliation.** Rows run 1 to 198, so r17 adds 199 to 211. No row, legacy or enforced, names chapter 35 or 36 (`grep` for "Fowler", "Feathers", "strangler", "golden", "parity" and "rewrite" over the claims table matched none in a ch35 or ch36 row). `CLAIMS_FIRST_ENFORCED = 47`.
- **Figures.** `_data/diagrams.yml` has 35 entries; r17 makes 37.
- **Test names.** 815 unique `def test_` names across `examples` and `spikes`, with the three known duplicates. All 21 names in the Example spec were checked, and none clashes.
- **Members.** No member uses project `fowler-feathers` or `refactor-or-rewrite`, or package `fowler_feathers` or `refactor_or_rewrite`.
- **`Weight`** exists in ten members, as `kilograms: float` in older ones and `kilograms: Decimal` in "Strategy: the callable" and "Command, undo, and command queues". ch36 uses the `Decimal` form.
- **Promises these chapters must honour:**
  - The part blurb: "Seams in Python, dependency-breaking techniques, Fowler and Feathers contrasted and combined, and the decision between refactoring and rewriting."
  - r16 decision 9 deferred to "Fowler vs Feathers, contrasted and combined": golden files and approval libraries, Fowler's refactoring contrast, and an experiment that changes a rounding rule. It deferred to "Refactor or rewrite": the strangler adapter and parity tests. Both chapters take them.
  - `bibliography.html` notes: Fowler's *Refactoring* is "the behaviour-preserving refactoring catalogue contrasted with Feathers in the legacy track". Its citation discipline: a citation is a pointer, not a displacing summary.
  - "Dependency-breaking techniques for modern Python" names both titles as related, describing nothing.
- **Already taught, so pointed to and not repeated** (by title, at most one sentence each):
  - "Dependency-breaking techniques for modern Python": parameterising the constructor (no Feathers technique name: none could be verified in r16), the characterisation table across five forms, the half-even mutant failing one row. ch35 must not rebuild that table or rerun its mutants.
  - "Seams in Python: monkeypatch, injection, and duck typing": seams and enabling points. ch36's router is a seam at the root.
  - "Patterns as decisions under forces": forces, the weight-band `Tariff`, count-the-edits.
  - "Proving it works: pytest, pytest-mock, and mypy": a test counts once it has been seen to fail.
  - "Anti-patterns and pattern misuse": measuring structure.
  - "Adapter, Facade, and Bridge": the Adapter pattern, for the one clause that says the router isn't one.
- **Stubs whose ground must not be taken or described:** "asyncio and the patterns", "Working with AI and LLM tools", "pytest reference" (Appendix B; ch35 may point to it for `pytest_addoption` by title only) and "Final project".
- **Status board hygiene.**
  - r16 is merged (da1b362, tag `r16.x`), but `iteration-plan.md` marks r16 "(active)" and PDP-133a to 134c `active`, and r16's step S7 reads `todo`. The orchestrator closes them at T0.
  - The PRD page says "r16 shipped 2026-11-06; Next: r17".

## What is new in each chapter

**ch35 (the same activity from two starting conditions).**
- Fowler's refactoring is a behaviour-preserving change that assumes self-testing code. Feathers starts where that assumption fails.
- A test written from the requirement (`INTENT_ROWS`) records intended behaviour. A golden value records what the code does, including what nobody chose.
- Golden values over a generated grid, inline and in a file. The failure is read as an ordered list, because a dict diff isn't reproducible.
- Two catalogue refactorings applied under the golden quotes. Two plausible variants move a total by a cent and pass every intent row: rounding when `Money` is created, and `round()`.
- The combination: characterise, then refactor in named steps with the golden run after each. The contrast table says which book supplies which part.

**ch36 (rewriting as a sequence of checked slices).**
- The forces that decide, each tied to a test.
- A parity table that runs the legacy engine and the rewrite on the same consignments, with a recorded list of accepted differences.
- A first draft that passes its own tests and diverges at the band limits.
- A strangler-style router that sends migrated zones to the rewrite, serves the rest from the legacy engine, runs the rewrite in shadow, and is deleted once every zone is migrated.
- What mypy checks at the router.

## Approach

- **Thesis wording.**
  - ch35: Fowler and Feathers describe one activity, changing structure while holding behaviour, from two starting conditions. Fowler's method assumes tests that pin behaviour; Feathers's begins by producing them. On inherited code the tests that exist record intent, and a refactor can move a cent past all of them. Record what the code does first, then refactor in named steps.
  - ch36: the choice between refactoring and rewriting is made with the same evidence. A characterisation or parity table names the behaviour that must survive, a list names the behaviour that should change, and a seam lets the new code take over one slice at a time. With those, a rewrite becomes a sequence of checked slices. Without them, it's a guess about behaviour nobody has written down.
- **One uv member per chapter**, standalone and named after its package, with no `[tool.*]` table:
  - `examples/35-fowler-vs-feathers` (project `fowler-feathers`, package `fowler_feathers`);
  - `examples/36-refactor-or-rewrite` (project `refactor-or-rewrite`, package `refactor_or_rewrite`).
- **mypy witness (ch36 only).** Copy `_run` and `_codes` from `examples/34-dependency-breaking-techniques/tests/test_static.py` (`mypy_path` to the member's `src`, `--strict --warn-unreachable`, `--cache-dir os.devnull`; `_codes` returns a sorted list). The test asserts the exit status, the exact code list and one stable substring, never line numbers. ch35 has no static test: its "mypy passes the refactor" claim rests on the experiment runs (`run: T5a`).
- **Static-test mutation rule.** The static test names its credited thing and a mutation that fails it (Example spec).
- **Negative witness rule.** Every pinned behaviour in `src` has a test that fails when it's changed. The deletion tables (T1a, T1b) name the test and why.
- **A measurement test must be able to fail.**
  - ch35: test 6 runs two mutants and asserts their exact mismatch ids.
  - ch36: test 2 runs the first draft and asserts its exact ids.
  - The accepted-differences test fails on a stale entry (experiment b).
- **Comparison and mutant code.** `_CentFirstRateEngine`, `_RoundBuiltinRateEngine`, `_exclusive_limits_quote` and `_refusing_quoter` live in conftest and reach tests through fixtures.
  - Shared tables (`INTENT_ROWS`, `GRID`, `INLINE_GOLDEN`, `PARITY_ROWS`, `ACCEPTED_DIFFERENCES`) live in the test module that uses them (the r13 importlib correction).
  - Conftest types are imported under `TYPE_CHECKING` only (r14).
  - The legacy modules are the subject, not comparison forms.
- **Determinism.**
  - No `sleep`, clock, threads, randomness or `print(` in tests.
  - Every assertion that can fail compares lists or tuples of strings in table or grid order, never a dict or a set. Evidence B is the reason, and the chapter states it.
  - The golden file is written only under `--update-golden`.
  - JSON is written with `sort_keys=True, indent=2` and a trailing newline.
  - `filterwarnings = ["error"]` stays.
- **Counts** come from the code, and the pytest summary line wins.
- **Repair rule (r12).** After every repair the validator re-reads the paragraph and the close bullets that depend on it. Scope words name the test that covers the whole scope, or are cut.
- **Excerpt rule.**
  - No excerpt shows a mutant as the lesson's code. Each chapter shows at most one mutant excerpt: ch35 `_CentFirstRateEngine._prices`, ch36 `_exclusive_limits_quote`'s band line.
  - No `src` excerpt contains `mock`, `patch` or `monkeypatch`.
  - T6 checks each excerpt against decisions 3 to 7.

Rejected in either `src`: `monkeypatch`, `mock`, `patch`, `Any`, `cast`, `print(`, `Optional`, `float(`, `random`, `global`, `sys.modules`, `json`. JSON belongs to the tests.

## Per-chapter spec

### ch35: Fowler vs Feathers, contrasted and combined (argument, has_example = true)

Thesis: as above. Sections (about 2,350 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~110), five bullets, one per close bullet:
   - state what Fowler and Feathers each mean by changing code safely, and the condition each method assumes;
   - write tests from the requirement and say what they leave unpinned;
   - record golden values for a grid of inputs, inline and in a file, and compare them so that a failure reads the same on every run;
   - apply catalogue refactorings under the golden quotes and catch one that moves a cent;
   - combine the two: characterise first, then refactor in named steps.
2. `## Why this matters` (~180). Intent first: the rating engine has been given a constructor seam and has a handful of tests written from its requirement. A tidy-up that represents prices as `Money` passes all of them (test 1) and still moves 18 of 120 quotes by a cent (test 6). Both books describe this change as safe, under different conditions.
3. Figure plus one paragraph (~50).
4. `## Two books, one activity` (~350).
   - Fowler: quote the Definition Of Refactoring noun sentence and the refactoring.com "Its heart is" sentence. Quote the Self Testing Code sentence: his method assumes a test suite that would catch a change.
   - Feathers: paraphrase "Changing Software": refactoring and optimisation hold functionality invariant while structure or resource use changes. Describe the book's starting point through its chapter titles (decision 9's bracket).
   - Fowler's Legacy Seam credits Feathers for the seam (quote its first sentence). That's the combination in one place. One pointer each to the two seams-and-dependencies chapters, describing nothing.
5. `## The contrast` (~250). A table this book writes (decision 10). Columns: Fowler; Feathers; this example. Rows, each cell backed by a fetched source or a test:
   - **Starting condition:** self-testing code; code with no tests, as the chapter titles describe; `legacy.RateEngine` with a constructor seam and intent tests only.
   - **What a test records:** intended behaviour; what the code does now ("I Need To Make a Change but I Don't Know What Tests To Write"); `INTENT_ROWS` against `rate_quotes.json`.
   - **First move:** a named refactoring; getting the code under test ("Dependency Breaking Techniques"); the parameterised constructor (pointer), then recording golden values.
   - **Unit of change:** a small behaviour-preserving transformation; the same, for which Feathers's book has an appendix "Refactoring"; Extract Function, Replace Primitive with Object.
   - **Done when:** the tests pass; the characterisation still passes; the golden test and the intent tests both pass.
6. `## Tests written from the requirement` (~300).
   - Excerpt `INTENT_ROWS`: the cheaper carrier wins each way, a tie goes to AIRCO, and the margin is applied to a round price.
   - They pass the legacy and the refactored engine, and both rounding variants (test 1), and a timeout fails the quote (test 2).
   - One pointer to "Proving it works: pytest, pytest-mock, and mypy" for a test counting once seen to fail. Here the test was never shown a case that moves a cent.
7. `## Golden values` (~400).
   - `GRID` is generated, not chosen: 120 consignments.
   - The file records the legacy engine (test 3), and the refactored engine matches it (test 4). Excerpt `_mismatches`.
   - Why a list: pytest 9.2.0 orders a dict diff through a set (evidence B), so a quoted failure would change between runs.
   - Inline values pin rows a reviewer reads (test 5). The file scales and is recorded rather than typed.
   - `--update-golden` rewrites the file from the legacy engine, and the diff is the review (test 8 for the writer's format; the json docs' `sort_keys`).
   - One clause names syrupy, approvaltests and inline-snapshot with PyPI links as packaged versions of this workflow.
   - A golden value also pins behaviour that's wrong. Regenerate only for a deliberate change, in its own commit.
8. `## Refactoring under the golden quotes` (~350).
   - Excerpt `refactored.RateEngine` (`_prices`, `_cheapest`, `_with_margin`), linking the Extract Function and Replace Primitive with Object catalogue entries.
   - The mutant excerpt `_CentFirstRateEngine._prices`: a `Money` that rounds when it's made. Test 6 lists its 18 rows exactly.
   - Substitute Algorithm with `round(amount, 2)`: quote the decimal docs sentence (evidence E). The default context rounds half to even (test 7), so only `EU-30` and `ASIA-30` move (test 6). The grid found the boundary; no row was chosen for it.
9. `## Characterise, then refactor` (~200). Feathers to reach a state where Fowler's discipline holds, then Fowler's catalogue for the moves, with the golden run after each. The combined workflow in four sentences. Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Refactoring code whose tests record intent.** "Tidy up `RateEngine`" doesn't say what must not change, and a tidy-up can move a total by a cent while every existing test passes. Paste a prompt that orders the work:

   > Before changing `RateEngine`, record golden quotes: run the current engine over every zone and every weight from 0.5 to 30 kg in 0.5 kg steps with the test rate cards, and write the results to `tests/golden/rate_quotes.json` with sorted keys. Then refactor one named step at a time (Extract Function, then Replace Primitive with Object), keeping carrier prices at full precision until the total is quantised half up, and run the golden test after each step. Don't regenerate the golden file in the same change.

   If the diff touches `rate_quotes.json`, ask which step meant to change a quote.</blockquote>

   At most 120 words; every backticked name exists in `src`, the tests or the standard library.
10. `## Build, run, observe` (~200 plus output). From the repository root once `uv sync --locked --all-packages`, then `cd examples/35-fowler-vs-feathers`, `uv run pytest -v`, `uv run mypy --strict src tests`. Each experiment runs in a fresh scratch copy (delete the copy's `.venv`, `uv sync --locked --all-packages`, confirm `fowler_feathers.__file__` points into the copy). The stated filter is `uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'`, then `uv run mypy --strict src tests`. No repo script and no `host_ids.py` in any reader command.
    - (a) In `src/fowler_feathers/refactored.py`, quantise each carrier price half up to the cent in `_prices`, where it becomes `Money`.
      - Expected: test 4 fails with `Left contains 18 more items, first extra item: 'EU-11: golden FASTLINE 14.84, now FASTLINE 14.85'`; the intent rows pass; mypy exits 0.
      - Executor check: whether test 5[refactored] fails, which depends on the inline rows.
    - (b) Restore, then replace `.quantize(CENT, rounding=ROUND_HALF_UP)` in `_with_margin` with `round(..., 2)`.
      - Expected: test 4 fails with `Left contains 2 more items, first extra item: 'EU-30: golden FASTLINE 32.51, now FASTLINE 32.50'`; test 5[refactored] fails on `EU-30`; mypy exits 0.
      - Executor check: the exact lines.
11. `## What you can do now` (~130): five bullets in objective order. They name the contrast table; `INTENT_ROWS` with test 1; `rate_quotes.json`, `_mismatches` and `--update-golden`; `refactored.RateEngine` with test 6; the combined workflow. Every backticked token appears earlier.
12. `## For deeper coverage` (~120):
    - Fowler, *Refactoring* (2nd ed.), the refactoring.com catalogue, and the Definition Of Refactoring and Self Testing Code bliki entries;
    - Feathers, *Working Effectively with Legacy Code*: "Changing Software" and "I Need To Make a Change but I Don't Know What Tests To Write";
    - Legacy Seam;
    - the decimal and json docs;
    - one title pointer to "Refactor or rewrite", describing nothing;
    - the bibliography link.

Figure `35-fowler-vs-feathers` (vertical, two lanes, one bar):
- **Top:** `legacy.RateEngine`, labelled "constructor seam; carriers passed in".
- **Left lane** (muted): "INTENT_ROWS: tests from the requirement", then "Extract Function, Replace Primitive with Object", then a dashed box "intent rows pass; a cent moves unseen".
- **Right lane** (accent): "rate_quotes.json: recorded from the legacy engine", then the same refactor box, then "golden quotes list every row that moved".
- **Bottom bar:** "characterise first, then refactor in named steps; run the golden quotes after each".
- No digits in the SVG.

Caption draft (about 40 words with the prefix): "Figure 35.1: The same refactoring under two kinds of test. Tests written from the requirement pass a change that moves totals by a cent; golden quotes recorded from the legacy engine list every row it moved." T3 counts and adjusts.

### ch36: Refactor or rewrite (argument, has_example = true)

Thesis: as above. Sections (about 2,350 prose words; at most six excerpts):

1. `## Learning objectives` (~110), five bullets:
   - name the forces that decide between refactoring and rewriting, and the test that measures each;
   - write a parity table that runs the legacy engine and a rewrite on the same consignments and lists every difference;
   - record deliberate differences so the parity test fails on a new one and on a stale one;
   - route consignments between the engines with a strangler-style router and run the rewrite in shadow;
   - say what the router costs and when it can be deleted.
2. `## Why this matters` (~180). Intent first: the band tariff is hard-coded in an if-chain, and a data-driven rewrite is attractive. A first draft passes its own tests and quotes 5 kg in the wrong band (test 2). Quote Strangler Fig's "Replacements seem easy to specify" sentence. The point is the details of existing behaviour, not any claim about outcomes.
3. Figure plus one paragraph (~50).
4. `## The forces` (~400). Paraphrase Feathers's three risk questions ("Changing Software"). Four forces, each with its witness (decision 8). One pointer to "Patterns as decisions under forces" for forces as the frame. Refactoring changes structure in steps a characterisation table checks: one pointer each to "Dependency-breaking techniques for modern Python" and "Fowler vs Feathers, contrasted and combined", describing neither beyond that.
5. `## A legacy engine and its rewrite` (~300).
   - Excerpt the legacy chain (one zone's branch) and `rating.quote`.
   - The legacy prices an unknown zone as EU (test 3); the rewrite refuses it (test 4).
   - Both include the band limit (test 5). Quote the `bisect_left` sentence.
6. `## The parity table` (~400).
   - Excerpt `PARITY_ROWS` and `ACCEPTED_DIFFERENCES`.
   - The rewrite differs only where accepted (test 1). The first draft's `bisect_right` line (the mutant excerpt) fails exactly at 5, 20 and 50 kg in each zone (test 2). Quote the `bisect_right` sentence.
   - Quote Feature Parity's intent sentence. The parity table is how this example asks for parity on purpose, with the exceptions written down.
   - Rows sit either side of every limit and above the last band. The table's choice of rows is what makes the boundary visible.
7. `## A strangler-style router` (~400).
   - Excerpt `Router`. Cite Strangler Fig by title, with its "move bits of behavior" sentence.
   - The router is Transitional Architecture: quote its intent sentence.
   - Migrated zones go to the rewrite (test 6) and the rest to the legacy engine (test 7).
   - Shadow mode: quote the Dark Launching intent sentence and say the router compares results instead (tests 8 to 10).
   - With every zone migrated the legacy engine is never called (test 11), which is when the router and `legacy.py` can go. The root binding migrates ASIA only (test 12).
   - mypy holds the rewrite to the legacy call shape (test 13). One clause that the router isn't the Adapter pattern, with a pointer to "Adapter, Facade, and Bridge"; one to "Seams in Python: monkeypatch, injection, and duck typing" for the router as a seam.
8. `## Refactor or rewrite: the decision` (~250). The rule in one paragraph:
   - Refactor while the structure can reach the target shape in behaviour-preserving steps under a characterisation table.
   - Rewrite a slice when the target shape can't be reached that way, here a data-driven `Tariff` in place of a chain. Do it only with a parity table, an accepted-differences list and a seam to route by.
   - Without those, the rewrite has no oracle.

   Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Rewriting behind a router.** "Rewrite the rating engine" invites a new engine that passes its own tests and quotes a band limit differently from the old one. Paste a prompt that keeps both engines running:

   > Write `rating.quote` beside the legacy `RateEngine`, not in place of it. Add a parity table with every zone, each band limit, a weight either side of it and one above the last band, and assert that the list of rows where the two engines differ equals `ACCEPTED_DIFFERENCES`. Route consignments through `Router`: send only the zones in `migrated` to the rewrite, and run it in shadow for the rest.

   If `ACCEPTED_DIFFERENCES` grew in the diff, ask who decided that quote should change.</blockquote>
9. `## Build, run, observe` (~200 plus output). Same rules and filter as ch35 (confirm `refactor_or_rewrite.__file__`).
   - (a) In `src/refactor_or_rewrite/rating.py`, replace `bisect_left` with `bisect_right`.
     - Expected: test 1 fails, the left list holding the six boundary ids before `AFRICA-5`; test 5[rewrite] fails; mypy exits 0.
     - Executor check: whether any shadow test fails.
   - (b) Restore, then in `tests/test_parity.py` empty `ACCEPTED_DIFFERENCES`.
     - Expected: test 1 fails with `Left contains one more item: 'AFRICA-5'` (executor check on wording); mypy exits 0.
10. `## What you can do now` (~130): five bullets mapped to the objectives. They name the four forces with their tests; `PARITY_ROWS` with test 2; `ACCEPTED_DIFFERENCES` with test 1; `Router` with tests 8 and 11; `quote_routed` and test 13.
11. `## For deeper coverage` (~120):
    - Strangler Fig;
    - Patterns of Legacy Displacement (Feature Parity, Transitional Architecture, Dark Launching), credited to Cartwright, Horn and Lewis;
    - Feathers: "Changing Software" and "How Do I Know That I'm Not Breaking Anything?";
    - Fowler, *Refactoring*;
    - the bisect docs;
    - the bibliography link.

Figure `36-refactor-or-rewrite` (vertical):
- **Top:** `Consignment`, then the accent box `Router` with a diamond "zone in migrated?".
- **Yes:** `rating.quote` ("Tariff; bisect_left keeps limits inclusive").
- **No:** `legacy.RateEngine.quote` ("served"), with a dashed side arrow to "rewrite in shadow: result unused; Mismatch reported".
- **Bottom bar:** "parity table: the rows that differ must equal ACCEPTED_DIFFERENCES".
- **Muted dashed box:** "first draft with bisect_right: differs at each band limit".
- No digits in the SVG.

Caption draft (about 42 words): "Figure 36.1: A router sends migrated zones to the rewrite and serves the rest from the legacy engine, running the rewrite in shadow. A parity table holds both to the same quotes, except the differences someone decided to make." T3 counts and adjusts.

Citations, both chapters: verify each before writing and apply the bracketed fallbacks. Quote no sentence unless it was checked on a fetched page, stop each quotation where the page's sentence stops, make no outcome claim (decision 8), and make no comparison between languages.

## Example spec

### `examples/35-fowler-vs-feathers` (project `fowler-feathers`, package `fowler_feathers`)

`pyproject.toml` in the r16 shape (`requires-python = ">=3.15"`, `uv_build>=0.13.7,<0.14`, no `[tool.*]`).

- **`domain.py`, `fastline.py`, `airco.py`**: as ch34's, with package `fowler_feathers`. The stand-ins raise `CarrierTimeoutError` and do no I/O.
- **`legacy.py`**: `MARGIN = Decimal("1.10")`, `type FastlineQuote`, `class AircoPrice(Protocol)` and `RateEngine`, identical to ch34's `parameterised.py` apart from the package and with `MARGIN` defined here. The docstring says this is the engine after the constructor was parameterised, inherited with no tests beyond the intent rows.
- **`refactored.py`**:
  - `CENT = Decimal("0.01")` (Replace Magic Literal);
  - `RateEngine` with the same constructor;
  - `_prices(self, consignment) -> dict[str, Money]`, at full precision (Replace Primitive with Object);
  - `_with_margin(self, price: Money) -> Money`, which quantises once with `ROUND_HALF_UP`;
  - module function `_cheapest(prices: Mapping[str, Money]) -> tuple[str, Money]`, keyed `(amount, code)` (Extract Function);
  - `quote` composes them.

  The docstring names each catalogue move.
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`:
- `pytest_addoption` registering `--update-golden` (`store_true`, help "rewrite tests/golden/rate_quotes.json from the legacy engine").
- `_fastline_card(zone, weight_kg) -> Decimal` and `_airco_card(*, destination, grams) -> int`, the rate cards of evidence C.
- Fixture `engine_forms`: a mapping `legacy|refactored|cent-first|round-builtin` to a factory `(fastline, airco) -> Callable[[Consignment], RateQuote]`.
- `_CentFirstRateEngine(refactored.RateEngine)` overrides `_prices` (`@override`) to quantise each price half up to the cent.
- `_RoundBuiltinRateEngine(refactored.RateEngine)` overrides `_with_margin` with `round(..., 2)`.

`test_intent.py` (holds `INTENT_ROWS`, ids `fastline-cheaper`, `airco-cheaper`, `tie-goes-to-airco`, `margin-applied`; fixed-answer fakes):
1. `test_the_intent_rows_pass_every_engine_and_both_rounding_refactors` x form (4) x row (4) = 16. Asserts `(carrier, str(total))`.
2. `test_every_engine_lets_a_carrier_timeout_fail_the_quote` x (`legacy`, `refactored`): a FASTLINE fake raising `CarrierTimeoutError` makes the quote raise it.

`test_golden.py` (holds `GRID`, `GOLDEN_PATH = Path(__file__).parent / "golden" / "rate_quotes.json"`, `INLINE_GOLDEN` for `EU-0.5`, `EU-10`, `EU-30`, `ASIA-0.5`, `ASIA-30` with values read from the recorded file, and the helpers `_observed`, `_mismatches`, `_write_golden`, `_read_golden`):
3. `test_the_golden_file_records_the_legacy_engine`: with `--update-golden`, it writes and skips; otherwise `_mismatches(_observed(legacy), _read_golden()) == []`.
4. `test_the_refactored_engine_matches_the_golden_quotes`: `_mismatches(...) == []`.
5. `test_inline_golden_values_pin_the_rows_a_reviewer_reads` x (`legacy`, `refactored`): `[observed[k] for k in INLINE_GOLDEN] == list(INLINE_GOLDEN.values())`.
6. `test_the_golden_quotes_catch_a_refactor_that_changes_rounding` x (`cent-first`, `round-builtin`): the mismatch ids are exactly evidence C's 18-id list and `["EU-30", "ASIA-30"]`.
7. `test_round_with_two_digits_rounds_half_to_even_in_the_default_context`: `round(Decimal("32.505"), 2) == Decimal("32.50")` and `Decimal("32.505").quantize(CENT, rounding=ROUND_HALF_UP) == Decimal("32.51")`.
8. `test_the_golden_writer_sorts_and_indents`: in `tmp_path`, writing `{"EU-1": "AIRCO 4.36", "ASIA-0.5": "AIRCO 9.57"}` gives exactly `'{\n  "ASIA-0.5": "AIRCO 9.57",\n  "EU-1": "AIRCO 4.36"\n}\n'`, and it reads back equal.

The golden file `tests/golden/rate_quotes.json` is recorded once with `uv run pytest --update-golden` from the member directory, then run without the option. It is committed, and host-scrubbed (it holds no paths).

Planned: 8 test functions, 26 cases (`test_intent.py` 2/18, `test_golden.py` 6/8). The pytest summary line wins.

Also `README.md` and the card `_examples/35-fowler-vs-feathers.md`: `order: 35`, eyebrow "Changing inherited code · Fowler and Feathers", and a concept title with no count. Cards and READMEs carry only claims the tests back, use no unverified technique or chapter names, and describe no stub.

Deletion table (T1a; changed in a fresh scratch copy):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| full-precision `_prices` | quantised to cents (experiment a) | 4 | 18 rows move a cent; 1 passes |
| `ROUND_HALF_UP` in `_with_margin` | `round(..., 2)` (experiment b) | 4, 5[refactored] | `EU-30` and `ASIA-30` |
| `code` in the `_cheapest` key | removed, with FASTLINE first in `_prices` | 1[refactored-tie-goes-to-airco] | `FASTLINE` wins the tie |
| one value in `rate_quotes.json` | changed by a cent | 3, 4 | provenance and match both list it |
| `sort_keys=True` in `_write_golden` | removed | 8 | `EU-1` written first |
| `_mismatches` grid order | iterates `golden` keys sorted | 6 | id order differs from the expected list |
| timeout propagation in `refactored.py` | caught, AIRCO alone | 2[refactored] | `DID NOT RAISE` |

### `examples/36-refactor-or-rewrite` (project `refactor-or-rewrite`, package `refactor_or_rewrite`)

- **`domain.py`**:
  - `ConsignmentId` (`NewType`);
  - frozen slotted `Weight(kilograms: Decimal)`, which raises `ValueError` unless finite and positive;
  - frozen slotted `Consignment(id, zone, weight: Weight)`;
  - `Money(amount, currency="EUR")`;
  - `RateQuote(consignment_id, total: Money)`;
  - `RatingError(Exception)`.
- **`legacy.py`**: `MARGIN = Decimal("1.10")`. `RateEngine.quote` holds the if-chain of evidence F:
  - ASIA 30.00, 55.00, 98.00, and every other zone 12.00, 25.00, 48.00, with limits `<= 5`, `<= 20`, `<= 50`;
  - otherwise `RatingError(f"no band for {kg} kg")`;
  - then the margin, quantised half up.

  The docstring calls it inherited and keeps the unknown-zone fallback as found.
- **`rating.py`**:
  - frozen slotted `Tariff(upper_kg: tuple[Decimal, ...], prices: Mapping[str, tuple[Decimal, ...]])`;
  - `STANDARD_TARIFF`, with a `frozendict` of the same prices;
  - `quote(consignment, /, *, tariff=STANDARD_TARIFF) -> RateQuote`, which:
    - raises `RatingError(f"no tariff for zone {zone!r}")` for an unknown zone, `from None`;
    - finds the band with `bisect_left`;
    - raises `RatingError(f"no band for {kg} kg")` past the last limit, with the same text as legacy.
- **`strangler.py`**: `RateQuoter`, `Mismatch`, `Router`, `MIGRATED_ZONES = ("ASIA",)` and `quote_routed` (decision 7). In shadow mode only `RatingError` from the rewrite is caught. An error from the legacy engine propagates, because it is what's served.
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`:
- fixture `first_draft`, returning `_exclusive_limits_quote` (the rewrite with `bisect_right`);
- fixture `refusing_quoter`, returning a quoter that raises `RatingError("engine not expected to be called")`;
- fixture `consignment_for(zone, kg)`.

`test_parity.py` (holds `PARITY_ROWS`: EU and ASIA at 0.5, 5, 5.001, 20, 20.5, 50 and 60, plus `AFRICA-5`, 15 rows; `ACCEPTED_DIFFERENCES = ["AFRICA-5"]`; helpers `_outcome` and `_mismatches`):
1. `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted`: `_mismatches(quote) == ACCEPTED_DIFFERENCES`.
2. `test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries`: `== ["EU-5", "EU-20", "EU-50", "ASIA-5", "ASIA-20", "ASIA-50", "AFRICA-5"]`.
3. `test_the_legacy_engine_prices_an_unknown_zone_as_eu`: AFRICA 5 kg and EU 5 kg both give `"13.20"`.
4. `test_the_rewrite_refuses_an_unknown_zone`: `RatingError`, matching `no tariff for zone 'AFRICA'`.
5. `test_band_limits_include_the_boundary_weight` x (`legacy`, `rewrite`): `[_outcome(5), _outcome(5.001)] == ["13.20", "27.50"]`.

`test_strangler.py`:

6. `test_the_router_serves_migrated_zones_from_the_rewrite`: a refusing legacy engine, ASIA migrated; ASIA 5 kg gives `"33.00"`.
7. `test_the_router_serves_other_zones_from_the_legacy_engine`: a refusing rewrite, no report; EU 5 kg gives `"13.20"`.
8. `test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote`: the first draft in shadow; EU 5 kg is served `"13.20"`, and the reports are `[Mismatch(ConsignmentId("CN-1"), "13.20", "27.50")]`.
9. `test_shadow_mode_reports_a_refusal_as_a_mismatch`: AFRICA 5 kg reports `"RatingError: no tariff for zone 'AFRICA'"`.
10. `test_shadow_mode_is_silent_when_the_engines_agree`: EU 0.5 kg reports `[]`.
11. `test_with_every_zone_migrated_the_legacy_engine_is_never_called`: a refusing legacy engine with `("EU", "ASIA")` migrated; both zones quote.
12. `test_the_standard_router_migrates_asia_only`: `quote_routed.migrated == ("ASIA",)` and `quote_routed.rewrite is quote`.

`test_static.py`:

13. `test_mypy_requires_the_rewrite_to_take_a_consignment`: imports `src`. A `by_weight(zone: str, weight: Weight) -> RateQuote` with a real body, passed as `rewrite`, gives `["arg-type"]`, matching `expected "Callable[[Consignment], RateQuote]"`. Credits `RateQuoter` on `Router`. Mutation: annotating `rewrite: Callable[..., RateQuote]` empties the list.

Planned: 13 test functions, 14 cases (`test_parity.py` 5/6, `test_strangler.py` 7/7, `test_static.py` 1/1). The pytest summary line wins.

Also `README.md` and the card `_examples/36-refactor-or-rewrite.md`: `order: 36`, eyebrow "Changing inherited code · Refactor or rewrite".

Deletion table (T1b):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| `bisect_left` in `rating.quote` | `bisect_right` (experiment a) | 1, 5[rewrite] | boundary rows move a band |
| `KeyError` turned into `RatingError` | `KeyError` escapes | 1, 4, 9 | outcome text or exception type differs (executor check) |
| legacy `else` fallback | `elif zone == "EU"` plus a `RatingError` | 1, 3 | `AFRICA-5` stops differing; the accepted entry is stale (executor check) |
| `zone in self.migrated` | always legacy | 6, 11 | the refusing legacy engine raises |
| shadow comparison | reports every call | 10 | `[Mismatch(...)]`, not `[]` |
| `except RatingError` in shadow | removed | 9 | `RatingError` reaches the caller |
| `ACCEPTED_DIFFERENCES` | emptied (experiment b) | 1 | `['AFRICA-5'] == []` |
| `MIGRATED_ZONES` | `("ASIA", "EU")` | 12 | the tuple differs |

## Steps and status

Step ids are `T*` (decision 0). Only `T1a`, `T1b`, `T5a` and `T5b` are cited as `run:` tokens.

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| T0 | Bookkeeping, all with dated notes, plus re-checking the upstream pins and recording the decisions. In `iteration-plan.md`: PDP-135a-c and 136a-c `active`, r17 active, r16 closed, PDP-133a to 134c closed. In r16's plan: S7 closed. In `chapters.toml`: ch35-36 `has_example = true`. In the reconciliation plan: rows 199-211 `open`. In the domain model: rows 35-36 get the names and decisions 3-7 and 11. The ch35-36 stub `description` lines are written | - | done |
| T1a | ch35 member, golden file (recorded with `--update-golden`, then three green runs without it), card and README; one `uv lock`; one reverse-file-order run; the deletion table, each row in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `__file__`), deleted after use | T0 | done |
| T1b | ch36 member, card and README; one `uv lock` after T1a (sequenced for `uv.lock`); three green runs plus one reverse-order run; the deletion table; the static mutation run | T1a | done |
| T2 | Witness results into rows 199-209. The dated r17 note in `_plans/spikes.md` (evidence B-F, decision 12). A failed witness changes the thesis before prose. Every message, count or value that differs from Planning evidence goes in "Corrections after the build" | T1b | done |
| T3 | Two figures, specs `diagrams/specs/35-*.py` and `36-*.py`, and `_data/diagrams.yml` (single owner; 37 entries). Figures 00-34 unchanged. Every name drawn exists in `src`, conftest, the tests or the standard library | T2 | done |
| T4 | ch35-36 `status = "drafted"` (`kind` stays `argument`) | T3 | done |
| T5a | ch35 prose agent: re-fetch every source and quote exactly; verify or drop the bracketed titles (decision 9); run both experiments twice in fresh scratch copies with the stated filter; scrub before quoting; hand back the sources checked and a per-paragraph claims table | T3, T4 | done |
| T5b | ch36 prose agent, in parallel with T5a, with the same duties, plus checking that no outcome sentence from the fetched pages appears (decision 8) | T3, T4 | done |
| T6 | Opus validation, with up to two repair rounds. After every cut: a seam scan and a dependent-sentence re-read. Also: close-to-objective mapping, the excerpt check against decisions 3-7, pointer circularity (criterion 11), the cross-language and outcome greps (criteria 14 and 20), and the scope of the no-mock rule (criterion 2) | T5a, T5b | todo |
| T7 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r17.x` on main; notes-only release | T6 | todo |

Reconciliation rows (step T0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 199 | 35 | Tests written from the requirement pass the legacy engine, the refactored engine and two refactors that change rounding; a carrier timeout fails the quote | `test_the_intent_rows_pass_every_engine_and_both_rounding_refactors`, `test_every_engine_lets_a_carrier_timeout_fail_the_quote` |
| 200 | 35 | The golden file records the legacy engine over the grid, and the refactored engine matches it and the inline values | `test_the_golden_file_records_the_legacy_engine`, `test_the_refactored_engine_matches_the_golden_quotes`, `test_inline_golden_values_pin_the_rows_a_reviewer_reads` |
| 201 | 35 | The golden quotes list exactly the rows a cent-first refactor and a `round()` refactor change; `round(Decimal, 2)` in the default context rounds half to even | `test_the_golden_quotes_catch_a_refactor_that_changes_rounding`, `test_round_with_two_digits_rounds_half_to_even_in_the_default_context`, `source: https://docs.python.org/3/library/decimal.html` |
| 202 | 35 | The golden writer sorts keys and indents, so a regenerated file diffs line by line | `test_the_golden_writer_sorts_and_indents`, `source: https://docs.python.org/3/library/json.html` |
| 203 | 35 | Fowler defines refactoring as behaviour-preserving structural change in small steps, relies on self-testing code, and credits Feathers for the seam | `source: https://martinfowler.com/bliki/DefinitionOfRefactoring.html`, `source: https://refactoring.com/`, `source: https://martinfowler.com/bliki/SelfTestingCode.html`, `source: https://martinfowler.com/bliki/LegacySeam.html` |
| 204 | 36 | The rewrite differs from the legacy engine only where accepted; a first draft with exclusive band limits fails parity exactly at the boundary weights | `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted`, `test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries`, `source: https://docs.python.org/3/library/bisect.html` |
| 205 | 36 | The legacy engine prices an unknown zone as EU, the rewrite refuses it, and both include the band limit | `test_the_legacy_engine_prices_an_unknown_zone_as_eu`, `test_the_rewrite_refuses_an_unknown_zone`, `test_band_limits_include_the_boundary_weight` |
| 206 | 36 | The router serves migrated zones from the rewrite and the rest from the legacy engine; with every zone migrated the legacy engine is never called; the root binding migrates ASIA only | `test_the_router_serves_migrated_zones_from_the_rewrite`, `test_the_router_serves_other_zones_from_the_legacy_engine`, `test_with_every_zone_migrated_the_legacy_engine_is_never_called`, `test_the_standard_router_migrates_asia_only`, `source: https://martinfowler.com/bliki/StranglerFigApplication.html` |
| 207 | 36 | In shadow mode the router serves the legacy quote and reports a difference or a refusal, and reports nothing when the engines agree | `test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote`, `test_shadow_mode_reports_a_refusal_as_a_mismatch`, `test_shadow_mode_is_silent_when_the_engines_agree`, `source: https://martinfowler.com/articles/patterns-legacy-displacement/dark-launching.html` |
| 208 | 36 | mypy requires the rewrite to take a consignment at the router | `test_mypy_requires_the_rewrite_to_take_a_consignment` |
| 209 | 36 | Feature Parity and Transitional Architecture as their authors define them | `source: https://martinfowler.com/articles/patterns-legacy-displacement/feature-parity.html`, `source: https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html` |
| 210 | 35-36 | mypy `--strict`, ruff and the idiom scan pass both members, including the legacy modules | `run: T1a`, `run: T1b` |
| 211 | 35-36 | The "Build, run, observe" experiments behave as quoted, and mypy exits 0 on each | `run: T5a`, `run: T5b` |

No legacy row belongs to chapter 35 or 36 (evidence L).

## Corrections after the build
- Step T5: ch35 2,132 words, ch36 2,112. Prose agents reported loose README, card and docstring sentences, fixed by the orchestrator: ch35's "by a cent" (no test asserts the size) became "changes totals", and "Five tests" became "Five rows"; ch36's "either side of every limit" (only 5 and 50 kg have a row just above) and "moves into the next band" (at 50 kg there is no next band) were reworded, and the router docstring's "can be deleted" became "is never called", which a test shows. ch35's tie-break rule is pinned only with FASTLINE listed first (removing `code` from the key alone passes), so the chapter makes no tie-break claim.
- Step T3: figures 35 and 36 (37 entries). Figure 35 names the two refactors that change totals (`_CentFirstRateEngine`, Replace Primitive with Object; `_RoundBuiltinRateEngine`, Substitute Algorithm) rather than the spec's Extract Function, and says "changed" rather than "by a cent" (no test asserts the size). The orchestrator removed an arrow from `legacy.RateEngine` to `INTENT_ROWS`: intent rows come from the requirement, not the legacy engine. Figure 36 has no diamond (the generator has none), so the router's question is a line in its box; the shadow box says it compares only when `report` is set.
- Step T1b: member `refactor-or-rewrite` (package `refactor_or_rewrite`), 15 test functions, 19 cases (7/11, 7/7, 1/1), not the planned 13/14. The deletion run found unpinned checks, so two tests were added: `test_a_weight_must_be_positive_and_finite` (4 cases) and `test_the_rewrite_prices_from_the_tariff_it_is_given_and_rounds_half_up` (every standard price times 1.10 is an exact cent, so a one-band tariff at 0.15 lands the margin on 0.165). `PARITY_ROWS` has 17 rows: a 50.001 kg row per zone was added because moving the last limit from 50 to 51 passed every test. `MARGIN` lives in `domain.py` and `legacy.py` re-exports it, so the rewrite never imports from the module meant to be deleted. Experiment (a) (`bisect_right` in `rating.py`) fails four tests, mypy exit 0; its output is `At index 0 diff: 'EU-5' != 'AFRICA-5'` and `Left contains 6 more items, first extra item: 'EU-20'` (the six boundary ids are the extras). Unpinned and therefore not claimed in prose: the legacy engine's rounding mode (every legacy price times 1.10 is an exact cent and it takes no tariff, an equivalent mutant), and the first draft raising `RatingError` at exactly 50 kg (no test asserts the raise).
- Step T2: rows 199-209 resolve to the tests; the dated r17 note is in `_plans/spikes.md`.
- Step T1a: member `fowler-feathers` (package `fowler_feathers`), 8 test functions, 30 cases (2/22, 6/8). The planned 26 left gram truncation unpinned: every grid and intent weight was a multiple of 0.5 kg, so `int` to `round` passed. A `grams-truncated` intent row (EU, 0.0006 kg) was added; the mutation now fails `[grams-truncated-legacy]` in `legacy.py` and the three refactored forms in `refactored.py`. All planned numbers match: cent-first changes 18 of 120 totals starting at `EU-11` (14.84 to 14.85), `round(x, 2)` changes `EU-30` and `ASIA-30` (32.51 to 32.50). `_mismatches` also reports golden rows not observed (`now missing`). Mutants subclass the refactored engine, so each also fails the other mutant's case of the rounding test. `--update-golden` works from the member and from the root under `--strict-config`; a normal run leaves the file untouched.

(None yet. The orchestrator records here every handback that differs from this plan: messages, counts, which tests an experiment fails, word counts, declined findings, changed prompt wording.)

Lessons carried from r11-r16, which this plan applies up front:
- **Counts.** Per-file counts are summed from the spec, and the pytest summary line wins (r13 to r16 sum errors).
- **Members.** Named after the package, with no `[tool.*]` table (r13).
- **Shared tables** in the test module; conftest types under `TYPE_CHECKING`; classes through fixtures (r13, r14).
- **Determinism.** Lists or tuples only, never a set or dict in a failing assertion (r13 to r15). r17 adds pytest's own dict diff to the reasons (evidence B).
- **Experiment filters.** `E` plus 3, 7, 9 and 11 spaces as separate alternatives, and `(tests|src)/.*Error$` (r13 to r15); r17 adds `skipped`.
- **Reader commands.** No repo script, and never `host_ids.py` (r15).
- **Pointers.** None that describes a stub's content, and none circular (r14, r16). ch35 and ch36 point to each other by title only.
- **Claim scrutiny.** Cards, READMEs, conftest and `src` docstrings get the same review as chapters (r14, r16 round 1).
- **Unverified names.** No unverified technique or chapter name in any file (r16: Feathers's technique names). r17 adds Fowler's second-edition chapter titles (evidence J).
- **Voice.** "earns its place" is banned (r15).
- **Close.** Every artifact named in "What you can do now" appears earlier in the chapter (r16 round 1).
- **Paths.** Repo-relative only in plans (r09).

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs and once in reverse file order, with the same pass count.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|threading|random|print\("` over both members' `tests` prints nothing.
   - `grep -rnE "monkeypatch|mocker|unittest\.mock|\bpatch\b|\bAny\b|cast\(|print\(|Optional|float\(|random|\bglobal\b|sys\.modules|\bjson\b"` over both members' `src` prints nothing.
   - `grep -rnE "monkeypatch|mocker|unittest\.mock"` over both members' `tests` prints nothing.
   - `grep -rn "update-golden" examples/*/tests` matches only `examples/35-fowler-vs-feathers`.
3. Every test name cited in rows 199-208 is defined exactly once across `examples/*/tests`.
4. The static test asserts its exit status, an exact sorted code list and no line number. Every `# type: ignore[...]` and `# noqa` names a code, and there are no unused ignores.
5. The static test fails on its named mutation (T1b quotes the line).
6. Deletion tables: every row, changed in a fresh scratch copy, makes the named test fail for the stated reason. The handback quotes the failing line. Executor-check rows are resolved or moved to Corrections.
7. Every "catches", "misses", "passes", "refuses", "never called", "differs only" or "reports" sentence names a test with a deletion row, experiment or mutant that makes it fail. Scope words name the test that covers the whole scope, or are cut.
8. ch35-36 are drafted, with one figure each, captions of 20-45 words including `Figure N.1:`, and at most 2,500 prose words each by `validate.py` (a warning below 1,900 is reported, not padded).
9. Spine and sidebar:
   - Both pass the `argument` spine.
   - `grep -c "^## The argument"` is 0 in both.
   - `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere.
   - `## Build, run, observe` precedes `## What you can do now`, which is the second-to-last H2 with as many bullets as the objectives. Every backticked token in the close appears earlier.
   - Each sidebar opens with a bold lead and holds a nested `>` prompt; has at most two non-quoted paragraphs; matches no `\bCheck(:| that| three| four| whether)`; is at most 120 words; names only identifiers in the chapter, its `src`, tests or the standard library; and claims nothing about what assistants or models produce.
10. Thesis:
    - ch35 states the two starting conditions, shows the intent rows passing a cent-moving refactor and the golden quotes listing it, and gives the combined workflow.
    - ch36 ties each force to a test and states the decision rule.
11. Pointers:
    - ch35 points to "Dependency-breaking techniques for modern Python", "Seams in Python: monkeypatch, injection, and duck typing", "Proving it works: pytest, pytest-mock, and mypy" and "Refactor or rewrite", by title.
    - ch36 points to "Patterns as decisions under forces", "Dependency-breaking techniques for modern Python", "Fowler vs Feathers, contrasted and combined", "Seams in Python: monkeypatch, injection, and duck typing" and "Adapter, Facade, and Bridge", by title.
    - Neither rebuilds ch34's characterisation table, describes a stub, or covers asyncio or LLM output.
12. Voice:
    - `$S --tier ban --fail` exits 0 over both chapters, the READMEs, cards, specs and SVGs, with `--stats` reviewed. "earns its place" appears nowhere.
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per chapter outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|optimiz|characteriz|parameteriz|modeling)"` over prose (quotations, code and verified proper names excluded) prints nothing.
13. No em or en dash in any file touched in r17, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0.
14. `grep -nE "Java|JavaScript|C#|C\+\+|\.NET|Smalltalk|capstone|PDP-|\br[01][0-9]\b|spike|[Cc]hapter [0-9]"` over `_docs/35-*.md`, `_docs/36-*.md`, the new READMEs and the cards prints nothing.
15. Idiom scan: 0 ban-tier in both members, including `legacy.py`.
16. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs scrubbed before quoting.
17. Every excerpt matches its source byte for byte. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`. Excerpts containing `{{` are wrapped in `{% raw %}`.
18. Each experiment runs in a fresh scratch copy, changes one thing and is deleted afterwards. Its filter is stated in the chapter; its output is quoted as the filter's complete output followed by mypy's; and it is run twice with identical output apart from duration.
19. Attribution:
    - Feathers and Fowler are cited by book and verified chapter title or topic, paraphrased except for the evidence H sentences.
    - Cartwright, Horn and Lewis are credited for every displacement-pattern quotation.
    - Every quotation stops where the page's sentence stops. Every book cited is already in `bibliography.html`.
20. Claims:
    - Every factual sentence maps to a named test, a `run: T1a`/`T1b`/`T5a`/`T5b` token, or a fetched source URL linked in the chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0 with rows 199-211 resolved.
    - `grep -niE "go down in flames|learnt the hard way|most of the time|underestimate|percent of|% of (projects|rewrites)"` over both chapters prints nothing.
21. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 37 entries, and figures 00-34 are unchanged.
22. Reconciliation rows 199-211 are `verified` or `adjusted` with evidence.
23. Deterministic: no test depends on wall time, the environment, file paths, hash order or test order. `filterwarnings = ["error"]` stays in the root config.
24. CI `ci-ok` is green on the PR. Merge happens only after the owner's explicit approval.
25. Test counts in prose and handbacks come from a fresh pytest summary line.
26. `tests/golden/rate_quotes.json` equals the legacy engine's output (test 3 green without the option), ends with a newline and has sorted keys.
27. Repo-relative paths only: `grep -rnE "/home/|/Users/"` over the files touched in r17 prints nothing.

## Risks

- **Predicted messages and counts.** Expect differences in:
  - pytest's list-diff wording ("Left contains N more items, first extra item: ...", or "one more item");
  - the 18-row list if the member's rate cards or grid differ in any digit;
  - mypy's quoting of `Callable[[Consignment], RateQuote]` once the type alias is involved;
  - whether ch36 experiment (a) also fails a shadow test.

  Tests match codes and stable substrings only.
- **Golden file drift.** A reviewer may regenerate the file to make a red test green. The provenance test (3) ties it to `legacy.py`, and the sidebar's review line names the risk.
- **The `--update-golden` option** is root-visible once collected. A later member that adds the same name would fail at start-up; criterion 2 greps for it.
- **Overlap with ch34.** ch35 must not rebuild the five-form table or the half-even mutant. Its claims are the intent-against-golden contrast, the generated grid and the stable failure reading.
- **Unverified titles.** Fowler's second-edition chapter titles stay out unless verified (evidence J), and so does Feathers's Preface definition. Topic citations replace them.
- **Outcome claims** creep in through paraphrase of the displacement pages. Criterion 20's grep and T5b's duty guard it.
- **Word budgets.** ch35 shrinks first: the approval-library clause, then the Legacy Seam quotation. ch36 shrinks first: the Legacy Mimic mention, then the Feature Parity quotation. Their tests stay.
- **Legacy-shape drift.** A reviewer may "fix" ch36's unknown-zone fallback or ch35's `legacy.py`. Deletion rows make that visible.
- **`uv.lock` race.** T1a and T1b are sequenced.
- **Not upstream defects for prose:** pytest's set-ordered dict diff is stated as observed behaviour with its cause; the InformIT table of contents is not mentioned in reader text. Nothing is filed without the owner, through `lgtm-issue-reporting`.
