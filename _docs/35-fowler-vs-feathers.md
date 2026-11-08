---
title: "Fowler vs Feathers, contrasted and combined"
order: 35
layout: tutorial
sectionid: docs
part: "changing-inherited-code"
description: "See what each book assumes before you touch code, record what an inherited engine really quotes, and refactor it in small steps while a table of those quotes tells you the moment a total moves."
---

## Learning objectives

By the end of this chapter you can:

- State what Martin Fowler and Michael Feathers each mean by changing code safely, and the condition each method assumes.
- Write tests from the requirement and say what they leave unpinned.
- Record golden values for a grid of inputs, inline and in a file, and compare them so a failure reads the same from one run to the next.
- Apply catalogue refactorings under the golden quotes and catch one that moves a total.
- Combine the two books: characterise first, then refactor in named steps.

## Why this matters

Refactoring and working with inherited code are one activity seen from two starting points. Both change the structure of a program and hold what it does fixed. Fowler's method needs tests that notice a change in behaviour. Feathers's method is for the case where nobody has written them. A team that has the first and inherits the second has to decide which book to follow, and the example below puts a number on what the choice costs.

The example is the rating engine from [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}), after its constructor was given keyword parameters. It asks two carriers for a price, takes the cheaper and adds a margin. Five rows written from the requirement describe it. One way of making carrier prices `Money` passes all five and still changes 18 of 120 recorded quotes (`test_the_intent_rows_pass_every_engine_and_both_rounding_refactors` and `test_the_golden_quotes_catch_a_refactor_that_changes_rounding`).

{% include excalidraw.html name="35-fowler-vs-feathers" caption="Figure 35.1: The same two rounding refactors under two kinds of test. Rows written from the requirement pass both, while golden quotes recorded from the legacy engine list the rows each refactor changed." %}

Read the figure from the top. On the right, `legacy.RateEngine` ("carrier functions arrive as keyword parameters") has an arrow down to an accent box, `rate_quotes.json` ("recorded from the legacy engine"). On the left, a grey box, `INTENT_ROWS` ("tests written from the requirement"), stands apart from the engine with no arrow into it. Both boxes send an arrow down to one wide box, "two rounding refactors of `refactored.RateEngine`", which names `_CentFirstRateEngine` for Replace Primitive with Object and `_RoundBuiltinRateEngine` for Substitute Algorithm. Below it the left path ends in a dashed box, "the intent rows pass both refactors" ("no failure names a changed total"), and the right path ends in "the golden quotes list the changed rows" ("the first row is named in the failure"). One arrow runs from that right-hand box to the bar along the bottom: "characterise first, then refactor in named steps; run the golden quotes after each".

## Two books, one activity

Fowler defines the noun in the Definition Of Refactoring entry on his bliki: "Refactoring (noun): a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior." On [refactoring.com](https://refactoring.com/) he adds: "Its heart is a series of small behavior preserving transformations." The method is a sequence of named moves, each small enough to be less likely to go wrong. It relies on something you have to bring along. His Self Testing Code entry says: "Self-Testing Code is the name I used in Refactoring to refer to the practice of writing comprehensive automated tests in conjunction with the functional software." The catalogue's safety depends on a suite that would fail when behaviour moved, and that suite is the condition his method assumes.

Feathers's *Working Effectively with Legacy Code* opens with a chapter called "Changing Software". In it, refactoring and optimisation are two ways of holding functionality invariant while something else changes: structure in one case, resource use in the other. The book then spends its length on the case Fowler's condition rules out. A chapter is titled "I Need to Make a Change, but I Don't Know What Tests to Write", another "Dependency Breaking Techniques", and the book has an appendix called "Refactoring". Fowler's Legacy Seam entry summarises the emphasis in one sentence: "Feathers's book focuses primarily on getting a legacy system under test, as that is often the key to being able to work with it in a sane way." The same entry opens: "When working with a legacy system it is valuable to identify and create seams: places where we can alter the behavior of the system without editing source code." It credits Feathers with coining the term "seam", so Fowler's account of legacy work starts from Feathers's vocabulary.

The seam half of that work is covered by [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) and [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}). Here the engine arrives with its seam already cut, and the question is what protects the next change.

## The contrast

| | Fowler | Feathers | This example |
| --- | --- | --- | --- |
| Starting condition | Self-testing code | A legacy system not yet under test; getting it under test is the first job | `legacy.RateEngine`: a constructor seam and the intent rows |
| What a test records | Intended behaviour, written alongside the code | The subject of the Feathers chapter "I Need to Make a Change, but I Don't Know What Tests to Write" | `INTENT_ROWS` against `rate_quotes.json` |
| First move | A named refactoring | Break the dependency that stops a test running | Parameterised carriers, then recorded quotes |
| Unit of change | A small behaviour-preserving transformation | The same, after the code is under test | Extract Function, Replace Primitive with Object |
| Done when | The suite passes | You can show that nothing was broken | The intent rows and the golden quotes both pass |

The table is this book's own reading of the sources above and of the example's tests.

## Tests written from the requirement

A test written from the requirement says what the engine should do, and a reviewer can check the row against the business rule. These are the five the engine arrives with:

```python
INTENT_ROWS = {
    "fastline-cheaper": IntentRow("EU", "25.00", 2800, "FASTLINE", "27.50"),
    "airco-cheaper": IntentRow("ASIA", "60.00", 5450, "AIRCO", "59.95"),
    "tie-goes-to-airco": IntentRow("EU", "20.00", 2000, "AIRCO", "22.00"),
    "margin-applied": IntentRow("EU", "30.00", 4000, "FASTLINE", "33.00"),
    # AIRCO answers 1 cent only for 0 g; any other weight gets a price FASTLINE beats.
    "grams-truncated": IntentRow("EU", "30.00", 1, "AIRCO", "0.01", "0.0006", 0),
}
```

Each row fixes both carrier answers, so the expected quote is a number a person can derive by hand. The rows pass four forms of the engine, the two that match the golden file and the two that don't, 20 cases in all (`test_the_intent_rows_pass_every_engine_and_both_rounding_refactors`). A carrier timeout fails the quote in the legacy and the refactored engine (`test_every_engine_lets_a_carrier_timeout_fail_the_quote`).

The rows pass the refactors that move totals because the carrier prices in them are already whole cents and no margined price sits on a half cent, so the two roundings agree. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) makes the point that a test counts once you have seen it fail. These five rows were never shown a case that moves a cent.

## Golden values

A golden value is the answer the code gave on a day you chose to trust it, stored beside the test. It answers a different question from the intent rows: not "is this right" but "did this change". The example keeps the answers in two places. A file holds the quotes for a generated grid, and five inline values hold rows a reviewer can read without opening the file.

```python
GRID = [
    Consignment(ConsignmentId(f"{zone}-{kilograms}"), zone, kilograms)
    for zone in ("EU", "ASIA")
    for kilograms in (Decimal(halves) / 2 for halves in range(1, 61))
]
```

That makes 120 consignments, two zones from 0.5 kg to 30 kg in 0.5 kg steps, and none of them was chosen for being awkward. `tests/golden/rate_quotes.json` records what the legacy engine quotes for each, and a test checks that the file still equals the legacy engine's output (`test_the_golden_file_records_the_legacy_engine`). The refactored engine is compared to the same file (`test_the_refactored_engine_matches_the_golden_quotes`). Five rows are also written in the test module, such as `"EU-30": "FASTLINE 32.51"`, and both engines must reproduce them (`test_inline_golden_values_pin_the_rows_a_reviewer_reads`). The file scales and is recorded, not typed. The inline rows are the ones a review reads.

The comparison returns a list of lines:

```python
def _mismatches(observed: list[tuple[str, str]], golden: Mapping[str, str]) -> list[str]:
    """One line for every row whose quote differs from the golden one, in grid order."""
    lines = [
        f"{row}: golden {golden.get(row, 'missing')}, now {text}"
        for row, text in observed
        if golden.get(row) != text
    ]
    observed_rows = {row for row, _ in observed}
    missing = [
        f"{row}: golden {text}, now missing"
        for row, text in golden.items()
        if row not in observed_rows
    ]
    return lines + missing
```

The list is deliberate. On pytest 9.2.0, comparing two dicts with `==` builds the list of differing items from a set of keys, so the item a failure names first changes with the hash seed. A list in grid order fails the same way each time, and `_mismatches(...) == []` puts the first changed row at the top of the report. The comparisons that detect a moved quote are lists for this reason.

The file is rewritten by `uv run pytest --update-golden`, an option registered in `tests/conftest.py`. With it, the provenance test writes the file from the legacy engine and skips. The writer sorts keys and indents by two spaces, so a regenerated file diffs line by line (`test_the_golden_writer_sorts_and_indents`). The [json documentation](https://docs.python.org/3/library/json.html) says sorted keys suit regression tests that compare serialisations from day to day. Packaged versions of this workflow exist: [syrupy](https://pypi.org/project/syrupy/), [approvaltests](https://pypi.org/project/approvaltests/) and [inline-snapshot](https://pypi.org/project/inline-snapshot/) store and diff such values. The example uses none of them, because pytest's list comparison is enough for a table of this size.

A golden value pins whatever the code did, including behaviour you would call wrong. The diff of a regenerated file is the review, so regenerate it for a deliberate change to the legacy quotes and put that in its own commit, apart from any refactor.

## Refactoring under the golden quotes

`refactored.py` applies catalogue refactorings to the legacy engine. [Extract Function](https://refactoring.com/catalog/extractFunction.html) gives the cheaper-carrier choice and the margin their own names. [Replace Primitive with Object](https://refactoring.com/catalog/replacePrimitiveWithObject.html) turns each carrier price into a `Money`.

<!-- fmt:off -->
```python
def _cheapest(prices: Mapping[str, Money]) -> tuple[str, Money]:
    """The carrier with the lowest price."""
    return min(prices.items(), key=lambda item: (item[1].amount, item[0]))

    def _with_margin(self, price: Money) -> Money:
        total = (price.amount * self._margin).quantize(CENT, rounding=ROUND_HALF_UP)
        return Money(total, price.currency)

    def quote(self, consignment: Consignment) -> RateQuote:
        code, cheapest = _cheapest(self._prices(consignment))
        return RateQuote(consignment.id, code, self._with_margin(cheapest))
```
<!-- fmt:on -->

The `Money` in `_prices` keeps the carrier's price at full precision, and the total is rounded once, half up. A `Money` that rounds when it is made is another way to write the same refactoring, and a test-only engine does so:

<!-- fmt:off -->
```python
    @override
    def _prices(self, consignment: Consignment) -> dict[str, Money]:
        prices = super()._prices(consignment)
        return {
            code: Money(price.amount.quantize(CENT, rounding=ROUND_HALF_UP))
            for code, price in prices.items()
        }
```
<!-- fmt:on -->

`_CentFirstRateEngine` rounds each carrier price to the cent and then adds the margin. It passes the five intent rows. The golden quotes list 18 of the 120 rows, from `EU-11` to `ASIA-26.5`, in grid order (`test_the_golden_quotes_catch_a_refactor_that_changes_rounding`). The first reads `EU-11: golden FASTLINE 14.84, now FASTLINE 14.85`. Nobody chose `EU-11` as a row.

The second mutant is [Substitute Algorithm](https://refactoring.com/catalog/substituteAlgorithm.html): `_RoundBuiltinRateEngine` replaces the half-up quantise with `round(amount, 2)`. The Python documentation for [`round` on a `Decimal`](https://docs.python.org/3/library/decimal.html) says that with an integer second argument "the context’s rounding mode is respected". The default context rounds half to even, so a total of 32.505 becomes 32.50 where the engine's rule gives 32.51 (`test_round_with_two_digits_rounds_half_to_even_in_the_default_context`). Two grid rows round differently under the two rules, and the golden quotes list those two and no others: `EU-30` and `ASIA-30`. The intent rows pass this refactor as well. A reviewer who sees `round(x, 2)` replace a `quantize` call has to know the half-even rule to object, whereas the grid objects without anyone knowing it.

## Characterise, then refactor

Feathers gets the code to a state where Fowler's discipline holds, and Fowler's catalogue supplies the moves. Put in order, the workflow is four steps. Cut a seam so the code runs under test. Record what it does over a grid nobody curated, and keep the intent rows for what it should do. Refactor one named step at a time. Run the golden quotes after each step, and read the first changed row when one fails.

That order also fixes the question to ask of a failing run. A red intent row says the code no longer meets the requirement. A red golden row says a total moved, and the next question is whether this step was meant to move it. Regenerating the file to turn the run green answers a different question from the one the run asked.

<blockquote class="ai-sidebar" markdown="1">

**Refactoring code whose tests record intent.** "Tidy up `RateEngine`" doesn't say what must not change, and a tidy-up can move a total while the existing tests pass. Paste a prompt that orders the work:

> Before changing `RateEngine`, record golden quotes: run the current engine over both zones and the weights from 0.5 to 30 kg in 0.5 kg steps, and write the results to `tests/golden/rate_quotes.json` with sorted keys. Then refactor one named step at a time, keeping carrier prices at full precision until the total is quantised half up, and run the golden test after each. Don't regenerate the file in the same change.

If the diff touches `rate_quotes.json`, ask which step meant to change a quote.

</blockquote>

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then, from `examples/35-fowler-vs-feathers`, `uv run pytest -v` runs 8 test functions as 30 cases and ends with `30 passed in 0.04s`, and `uv run mypy --strict src tests` prints `Success: no issues found in 9 source files`. The two experiments below each change one thing in a scratch copy of the repository, after deleting the copy's `.venv` and running `uv sync --locked --all-packages` again. Each uses this filter, and then runs mypy:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|skipped|errors?))'
uv run mypy --strict src tests
```

Experiment one rounds each carrier price half up to the cent in `_prices` of `refactored.py`, where it becomes `Money`: wrap each of the two prices in `.quantize(CENT, rounding=ROUND_HALF_UP)` before `Money(...)`.

```text
E       AssertionError: assert ['EU-11: gold...E 21.81', ...] == []
E         Left contains 18 more items, first extra item: 'EU-11: golden FASTLINE 14.84, now FASTLINE 14.85'
E         Use -v to get more diff
tests/test_golden.py:107: AssertionError
E       AssertionError: assert ['EU-11', 'EU...EU-18.5', ...] == ['EU-30', 'ASIA-30']
E         At index 0 diff: 'EU-11' != 'EU-30'
E         Left contains 14 more items, first extra item: 'EU-15'
E         Use -v to get more diff
tests/test_golden.py:129: AssertionError
FAILED tests/test_golden.py::test_the_refactored_engine_matches_the_golden_quotes
FAILED tests/test_golden.py::test_the_golden_quotes_catch_a_refactor_that_changes_rounding[round-builtin-expected1]
2 failed, 28 passed in 0.04s
Success: no issues found in 9 source files
```

All 22 cases in `tests/test_intent.py` pass, and mypy exits 0. The refactored engine fails against the golden file with the 18 rows. The second failure belongs to the `round(x, 2)` mutant, which extends the refactored engine and inherits the edit, so it now changes the cent-first rows as well and its exact list no longer matches.

Experiment two restores `refactored.py`, then replaces `(price.amount * self._margin).quantize(CENT, rounding=ROUND_HALF_UP)` in `_with_margin` with `round(price.amount * self._margin, 2)`.

```text
E       AssertionError: assert ['EU-30: gold...STLINE 53.84'] == []
E         Left contains 2 more items, first extra item: 'EU-30: golden FASTLINE 32.51, now FASTLINE 32.50'
E         Use -v to get more diff
tests/test_golden.py:107: AssertionError
E       AssertionError: assert ['AIRCO 3.83'...STLINE 53.84'] == ['AIRCO 3.83'...STLINE 53.85']
E         At index 2 diff: 'FASTLINE 32.50' != 'FASTLINE 32.51'
E         Use -v to get more diff
tests/test_golden.py:115: AssertionError
E       AssertionError: assert ['EU-11', 'EU...EU-18.5', ...] == ['EU-11', 'EU...EU-18.5', ...]
E         At index 7 diff: 'EU-21.5' != 'EU-21'
E         Right contains 2 more items, first extra item: 'ASIA-25.5'
E         Use -v to get more diff
tests/test_golden.py:129: AssertionError
FAILED tests/test_golden.py::test_the_refactored_engine_matches_the_golden_quotes
FAILED tests/test_golden.py::test_inline_golden_values_pin_the_rows_a_reviewer_reads[refactored]
FAILED tests/test_golden.py::test_the_golden_quotes_catch_a_refactor_that_changes_rounding[cent-first-expected0]
3 failed, 27 passed in 0.04s
Success: no issues found in 9 source files
```

The intent rows pass again and mypy exits 0. The golden file lists `EU-30` and `ASIA-30`, and the inline `EU-30` value names the change a reviewer would read. The third failure is the cent-first mutant again, which extends the refactored engine and so inherits this edit too. Each experiment ran twice with identical output apart from the duration.

## What you can do now

- State each book's condition: the contrast table puts Fowler's self-testing code against Feathers's legacy system not yet under test, and sets each book's test beside the example's.
- Write tests from the requirement: `INTENT_ROWS` fixes both carrier answers, and `test_the_intent_rows_pass_every_engine_and_both_rounding_refactors` shows they pass refactors that move totals.
- Record golden values and compare them so a failure reads the same each run: `rate_quotes.json`, `_mismatches` and `--update-golden`, with the inline rows for review.
- Apply catalogue refactorings and catch a bad one: `refactored.RateEngine` keeps `Money` at full precision, and `test_the_golden_quotes_catch_a_refactor_that_changes_rounding` lists the 18 rows and the two rows its mutants change.
- Combine the two: characterise over a generated grid, refactor in named steps, run the golden quotes after each, and regenerate the file in its own commit.

## For deeper coverage

Martin Fowler's *Refactoring* (second edition, Addison-Wesley, 2018) is the source for the catalogue, with [refactoring.com](https://refactoring.com/) for the entries, the [Definition Of Refactoring](https://martinfowler.com/bliki/DefinitionOfRefactoring.html) and [Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html) entries, and [Legacy Seam](https://martinfowler.com/bliki/LegacySeam.html). Michael Feathers's *Working Effectively with Legacy Code* (Prentice Hall, 2004) covers the starting condition: read "Changing Software" and "I Need to Make a Change, but I Don't Know What Tests to Write" first. The [decimal](https://docs.python.org/3/library/decimal.html) and [json](https://docs.python.org/3/library/json.html) documentation cover the rounding and sorting rules the tests rely on. [Refactor or rewrite]({{ '/docs/36-refactor-or-rewrite/' | relative_url }}) is the next chapter. Both books are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
