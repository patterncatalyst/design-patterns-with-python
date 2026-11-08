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

Refactoring and working with inherited code are one activity seen from two starting points. Both change the structure of a program and hold what it does fixed. Fowler's method needs tests that notice a change in behaviour. Feathers's method is for the case where nobody has written them. A team that has the first and inherits the second has to choose, and the choice has a measurable cost.

The rating engine from [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) arrives with keyword parameters on its constructor. It asks two carriers for a price, takes the cheaper and adds a margin, and five rows written from the requirement describe it. One way of making carrier prices `Money` passes all five and still changes 18 of 120 recorded quotes.

{% include excalidraw.html name="35-fowler-vs-feathers" described="true" caption="Figure 35.1: The same two rounding refactors under two kinds of test. Rows written from the requirement pass both, while golden quotes recorded from the legacy engine list the rows each refactor changed." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-35-fowler-vs-feathers" markdown="1">
From the top. On the right, `legacy.RateEngine` ("carrier functions arrive as keyword parameters") has an arrow down to an accent box, `rate_quotes.json` ("recorded from the legacy engine"). On the left, a grey box, `INTENT_ROWS` ("tests written from the requirement"), stands apart from the engine with no arrow into it. Both boxes send an arrow down to one wide box, "two rounding refactors of `refactored.RateEngine`", which names `_CentFirstRateEngine` for Replace Primitive with Object and `_RoundBuiltinRateEngine` for Substitute Algorithm. Below it the left path ends in a dashed box, "the intent rows pass both refactors" ("no failure names a changed total"), and the right path ends in "the golden quotes list the changed rows" ("the first row is named in the failure"). One arrow runs from that right-hand box to the bar along the bottom: "characterise first, then refactor in named steps; run the golden quotes after each".
</div>
</details>

The figure runs the same two refactors under both kinds of test: the intent rows pass them, the golden quotes name the rows they change.

## Two books, one activity

Fowler defines the noun in the Definition Of Refactoring entry on his bliki: "Refactoring (noun): a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior." On [refactoring.com](https://refactoring.com/) he adds: "Its heart is a series of small behavior preserving transformations." The method is a sequence of named moves, each small enough to be less likely to go wrong. It relies on something you bring along. His Self Testing Code entry says: "Self-Testing Code is the name I used in Refactoring to refer to the practice of writing comprehensive automated tests in conjunction with the functional software." The catalogue is safe only with a suite that fails when behaviour moves, and that suite is the condition his method assumes.

Feathers's *Working Effectively with Legacy Code* opens with "Changing Software", where refactoring and optimisation are two ways of holding functionality invariant while something else changes: structure in one case, resource use in the other. The rest covers the case Fowler's condition rules out, in chapters such as "I Need to Make a Change, but I Don't Know What Tests to Write" and "Dependency Breaking Techniques", with an appendix called "Refactoring". Fowler's Legacy Seam entry sums it up: "Feathers's book focuses primarily on getting a legacy system under test, as that is often the key to being able to work with it in a sane way." The same entry opens: "When working with a legacy system it is valuable to identify and create seams: places where we can alter the behavior of the system without editing source code." It credits Feathers with coining "seam", so Fowler's account of legacy work starts from Feathers's vocabulary.

[Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) and [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) cover the seam half. Here the seam is already cut, and the question is what protects the next change.

## The contrast

| | Fowler | Feathers | Here |
| --- | --- | --- | --- |
| Starting condition | Self-testing code | A legacy system not yet under test; getting it under test is the first job | `legacy.RateEngine`: a constructor seam and the intent rows |
| What a test records | Intended behaviour, written alongside the code | The subject of "I Need to Make a Change, but I Don't Know What Tests to Write" | `INTENT_ROWS` against `rate_quotes.json` |
| First move | A named refactoring | Break the dependency that stops a test running | Parameterised carriers, then recorded quotes |
| Unit of change | A small behaviour-preserving transformation | The same, after the code is under test | Extract Function, Replace Primitive with Object |
| Done when | The suite passes | You can show that nothing was broken | The intent rows and the golden quotes both pass |

## Tests written from the requirement

A test written from the requirement says what the engine should do, and a reviewer can check the row against the business rule. The engine arrives with five:

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

Each row fixes both carrier answers, so the expected quote is a number a person can derive by hand. The rows pass four forms of the engine: the two that match the golden file and the two that don't. A carrier timeout fails the quote in the legacy and the refactored engine.

The rows pass the refactors that move totals because their carrier prices are already whole cents and no margined price sits on a half cent, so the two roundings agree. A test counts once you've seen it fail, as [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) puts it, and these five rows were never shown a case that moves a cent.

## Golden values

A golden value is the answer the code gave on a day you chose to trust it, stored beside the tests. It answers "did this change", not "is this right". A file holds the quotes for a generated grid:

```python
GRID = [
    Consignment(ConsignmentId(f"{zone}-{kilograms}"), zone, kilograms)
    for zone in ("EU", "ASIA")
    for kilograms in (Decimal(halves) / 2 for halves in range(1, 61))
]
```

That's 120 consignments, two zones from 0.5 kg to 30 kg in 0.5 kg steps, none chosen for being awkward. `tests/golden/rate_quotes.json` records what the legacy engine quotes for each; the file must still equal the legacy engine's output, and the refactored engine is compared to it. Five inline values, such as `"EU-30": "FASTLINE 32.51"`, sit in `tests/test_golden.py` for a reviewer to read without opening the file. The file scales and is recorded, not typed. The inline rows are the ones a review reads.

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

On pytest 9.2.0, comparing two dicts with `==` builds the list of differing items from a set of keys, so the item a failure names first changes with the hash seed. A list in grid order fails the same way each time, and `_mismatches(...) == []` puts the first changed row at the top of the report.

`uv run pytest --update-golden`, an option registered in `tests/conftest.py`, rewrites the file from the legacy engine. The writer sorts keys and indents by two spaces, so a regenerated file diffs line by line. The [json documentation](https://docs.python.org/3/library/json.html) says sorted keys suit regression tests that compare serialisations from day to day. [syrupy](https://pypi.org/project/syrupy/), [approvaltests](https://pypi.org/project/approvaltests/) and [inline-snapshot](https://pypi.org/project/inline-snapshot/) package this workflow; for a table of this size pytest's list comparison is enough.

A golden value pins whatever the code did, including behaviour you'd call wrong. The diff of a regenerated file is the review, so regenerate it only for a chosen change to the legacy quotes, in its own commit, apart from any refactor.

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

`Money` keeps the carrier's price at full precision, and the total is rounded once, half up. Two mutants try other ways to write the same refactoring:

| Mutant | Change | Intent rows | Golden quotes |
| --- | --- | --- | --- |
| `_CentFirstRateEngine` (Replace Primitive with Object) | rounds each carrier price to the cent, then adds the margin | pass | 18 of 120 rows change, `EU-11` to `ASIA-26.5` |
| `_RoundBuiltinRateEngine` ([Substitute Algorithm](https://refactoring.com/catalog/substituteAlgorithm.html)) | `round(amount, 2)` in place of the half-up quantise | pass | `EU-30` and `ASIA-30` change |

The cent-first mutant rounds when the `Money` is made:

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

Its first changed row reads `EU-11: golden FASTLINE 14.84, now FASTLINE 14.85`. Nobody chose `EU-11` as a row.

For the second, the Python documentation for [`round` on a `Decimal`](https://docs.python.org/3/library/decimal.html) says that with an integer second argument "the context’s rounding mode is respected". The default context rounds half to even, so 32.505 becomes 32.50 where the engine's rule gives 32.51. A reviewer who sees `round(x, 2)` replace a `quantize` call has to know the half-even rule to object; the grid objects without anyone knowing it.

## Characterise, then refactor

Feathers gets the code to a state where Fowler's discipline holds, and Fowler's catalogue supplies the moves. In order:

1. Cut a seam so the code runs under test.
2. Record what it does over a grid nobody curated, and keep the intent rows for what it should do.
3. Refactor one named step at a time.
4. Run the golden quotes after each step, and read the first changed row when one fails.

That order also fixes the question to ask of a failing run. A red intent row says the code no longer meets the requirement. A red golden row says a total moved, and the next question is whether this step was meant to move it. Regenerating the file to turn the run green answers a different question.

<blockquote class="ai-sidebar" markdown="1">

**Refactoring code whose tests record intent.** "Tidy up `RateEngine`" doesn't say what must not change, and a tidy-up can move a total while the existing tests pass. Order the work:

> Before changing `RateEngine`, record golden quotes: run the current engine over both zones and the weights from 0.5 to 30 kg in 0.5 kg steps, and write the results to `tests/golden/rate_quotes.json` with sorted keys. Then refactor one named step at a time, keeping carrier prices at full precision until the total is quantised half up, and run the golden test after each. Don't regenerate the file in the same change.

If the diff touches `rate_quotes.json`, ask which step meant to change a quote.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/35-fowler-vs-feathers
uv run pytest -q
uv run mypy --strict src tests
```

All 30 cases pass and mypy is clean. Run each experiment in a scratch copy of the repository with its own `.venv`:

- **Round carrier prices first.** In `_prices` of `refactored.py`, wrap each price in `.quantize(CENT, rounding=ROUND_HALF_UP)` before `Money(...)`. Every intent row passes and mypy exits 0. The golden comparison fails with 18 rows, the first `EU-11: golden FASTLINE 14.84, now FASTLINE 14.85`; the `round(x, 2)` mutant also fails, because it extends the refactored engine and inherits the edit.
- **Substitute `round`.** Restore the file and replace the quantise in `_with_margin` with `round(price.amount * self._margin, 2)`. The intent rows pass and mypy exits 0. The golden file lists `EU-30` and `ASIA-30`, the inline `EU-30` value fails with 32.50 for 32.51, and the cent-first mutant inherits the edit and fails.

Each experiment gives identical output on a second run, apart from the duration.

## What you can do now

- State each book's condition: Fowler's self-testing code against Feathers's legacy system not yet under test.
- Write tests from the requirement: `INTENT_ROWS` fixes both carrier answers, and passes refactors that move totals.
- Record golden values and compare them so a failure reads the same each run: `rate_quotes.json`, `_mismatches` and `--update-golden`, with the inline rows for review.
- Apply catalogue refactorings and catch a bad one: `refactored.RateEngine` keeps `Money` at full precision, and the golden quotes list the rows each mutant changes.
- Combine the two: characterise over a generated grid, refactor in named steps, run the golden quotes after each, and regenerate the file in its own commit.

## For deeper coverage

Martin Fowler's *Refactoring* (second edition, Addison-Wesley, 2018) is the source for the catalogue, with [refactoring.com](https://refactoring.com/) for the entries, the [Definition Of Refactoring](https://martinfowler.com/bliki/DefinitionOfRefactoring.html) and [Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html) entries, and [Legacy Seam](https://martinfowler.com/bliki/LegacySeam.html). Michael Feathers's *Working Effectively with Legacy Code* (Prentice Hall, 2004) covers the starting condition: read "Changing Software" and "I Need to Make a Change, but I Don't Know What Tests to Write" first. The [decimal](https://docs.python.org/3/library/decimal.html) and [json](https://docs.python.org/3/library/json.html) documentation cover the rounding and sorting rules. [Refactor or rewrite]({{ '/docs/36-refactor-or-rewrite/' | relative_url }}) is the next step. Both books are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
