---
title: "Dependency-breaking techniques for modern Python"
order: 34
layout: tutorial
sectionid: docs
part: "changing-inherited-code"
description: "Break a legacy engine's hard-wired carrier calls one small step at a time, and use a single table of expected quotes to show that no step changed what the code does."
---

## Learning objectives

By the end of this chapter you can:

- Pin what a legacy engine does today in a characterisation table, including behaviour you'd call a bug.
- Parameterise a constructor so a test passes fakes without a patch.
- Wrap a carrier SDK with a different shape so both carriers fit one callable type, and turn the class into a function bound at the root.
- Run one table across the steps, and show that the table can fail.
- Say which dependency-breaking moves Python makes unnecessary, and what subclass and override costs.

## Why this matters

Getting a first test around code you can't change yet is the job of a patch, and [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) covers it. The next move is to change the code so the test needs no patch. The risk is that changing code nobody has tested can change what it quotes: a tie-break moves, or a timeout gets swallowed. A dependency-breaking step is meant to change structure and leave behaviour alone, and the evidence of that is a record of the behaviour taken before the step.

The example is a rating engine that asks two carrier SDKs for a price, takes the cheaper, adds a margin and rounds. Both SDKs are stand-ins that do no I/O and raise `CarrierTimeoutError` where a real connection would time out, so a test that reaches one fails. Three failures show what an unpinned step risks. A parameter with a real default lets a test that forgets a fake reach the real carrier (`test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`). A step that also "improves" timeout handling changes what the engine does, and the first experiment below makes that visible. A misspelt override reaches the real carrier (`test_a_misspelt_override_falls_through_to_the_real_carrier`).

{% include excalidraw.html name="34-dependency-breaking-techniques" caption="Figure 34.1: Each step moves the enabling point from a patched name toward a parameter mypy checks, and one characterisation table runs at every step. Subclass and override passes it too, but a misspelt method reaches the real carrier." %}

Read the figure from the top. Four boxes step down the left: `legacy` ("enabling point: a patch on request_quote and airco.price"), `parameterised` ("keyword parameters; defaults are the real calls"), `wrapped` ("airco_quote fits CarrierQuoter") and, in the accent colour, `rating.quote` ("quoters required; quote_standard binds them"). A downward arrow labelled "one technique" joins each box to the next. On the right a tall box, "same characterisation table", has an arrow into each of the four. Beyond it a dashed box, "subclass and override", has a dashed arrow into the table box: it "also passes the same table", its seam is the overridden method names, and mypy reports a typo only with `@override`.

## Pin what the code does today

A characterisation test records what code does, so that a change can be told apart from a fix. Michael Feathers's *Working Effectively with Legacy Code* takes up the idea in the chapter "I Need To Make a Change but I Don't Know What Tests To Write". Here the expectation in each row is what the engine returns, whether or not anyone would have chosen it. Two rows of `CHARACTERISATION_ROWS`, the table for the legacy engine, are behaviour a reviewer might call wrong:

<!-- fmt:off -->
```python
    Row(
        "margin-rounds-half-up",
        "EU",
        Decimal("1"),
        Decimal("10.15"),
        2000,
        "FASTLINE",
        "11.17",
        [("AIRCO", "EU", "1000"), ("FASTLINE", "EU", "1")],
    ),
    Row(
        "grams-truncated",
        "EU",
        Decimal("0.0006"),
        Decimal("30.00"),
        1,
        "AIRCO",
        "0.01",
        [("AIRCO", "EU", "0"), ("FASTLINE", "EU", "0.0006")],
    ),
```
<!-- fmt:on -->

The margin of 1.10 on 10.15 is 11.165, and the engine rounds half up, so the row records 11.17. A half-to-even rule would give 11.16. The weight of 0.0006 kg converts to zero grams because `int` truncates, so AIRCO is asked about a weightless parcel and the quote is a cent. Neither is fixed here. The other three rows pin that the cheaper carrier wins in each direction and that a tie goes to AIRCO, and a separate test pins that a FASTLINE timeout fails the whole quote rather than falling back to AIRCO (`test_every_step_lets_a_carrier_timeout_fail_the_quote`).

The `calls` column of a row is compared after sorting, so the table pins which carriers were asked and with what arguments, and not the order of the asking.

The table runs against five forms of the engine through the `step` fixture in `tests/conftest.py`. Each form takes the two carriers' answers as SDK-level fakes and wires them in at its own enabling point, and returns a function that quotes plus a record of the calls made. The legacy engine takes no parameters, so its form is the one place in this example that patches:

<!-- fmt:off -->
```python
def _legacy_step(request: pytest.FixtureRequest) -> Step:
    # The only patch in these tests: the legacy engine takes no parameters, so the names it
    # looks up in its own module are the only enabling point.
    monkeypatch: pytest.MonkeyPatch = request.getfixturevalue("monkeypatch")

    def build(answers: CarrierAnswers) -> tuple[QuoteFor, Calls]:
        fastline_fake, airco_fake, calls = _fakes(answers)
        monkeypatch.setattr("dependency_breaking.legacy.request_quote", fastline_fake)
        monkeypatch.setattr(airco, "price", airco_fake)
        return legacy.RateEngine().quote, calls

    return build
```
<!-- fmt:on -->

That's a scoped exception: the legacy branch of one fixture, because a namespace patch is the only enabling point the legacy engine has. No other test file patches, and nothing in `src` does. The same five rows then run against each form (`test_every_step_matches_the_characterisation_table`), which is 25 cases.

A table that can't fail proves nothing. `test_the_table_catches_a_step_that_changes_behaviour` runs it against two altered engines built on the parameterised constructor shape. One rounds grams where the engine truncates them, and the other rounds the margin half to even. The first fails exactly the row `grams-truncated` and the second exactly `margin-rounds-half-up`, and the test asserts those lists.

## Parameterise the constructor

The legacy engine reaches its carriers by names it looks up in its own module, so a test needs a patch. A constructor that takes the carriers as parameters gives the test a seam it can use without one, and existing callers don't have to change if each parameter defaults to the real call:

<!-- fmt:off -->
```python
    def __init__(
        self,
        *,
        fastline_quote: FastlineQuote = request_quote,
        airco_price: AircoPrice = airco.price,
        margin: Decimal = MARGIN,
    ) -> None:
        self._fastline_quote = fastline_quote
        self._airco_price = airco_price
        self._margin = margin
```
<!-- fmt:on -->

`parameterised.RateEngine()` still builds the production engine, and the rows for `parameterised` pass with fakes passed as arguments and no patch. `AircoPrice` is a callback Protocol, declared in the same module, because the AIRCO SDK takes keyword-only arguments and [a plain `Callable` can't say so](https://docs.python.org/3/library/typing.html#annotating-callable-objects). [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) is the pointer for Protocols.

mypy now checks the fake. A replacement that takes `zone` and `grams` positionally is reported as `[arg-type]`, and the message names `AircoPrice` (`test_mypy_checks_a_fake_passed_as_a_constructor_argument`). A patch names its target by a string and mypy doesn't check the replacement, as [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) shows. The price of the defaults is the other direction: a test that passes a FASTLINE fake and forgets AIRCO reaches the real SDK and fails with `AIRCO did not answer`. In this example the failure is loud, because the stand-in raises. A real SDK would open a connection.

## Wrap the carrier with a different shape

The two SDKs differ in shape. FASTLINE takes a zone and kilograms and answers in euros. AIRCO takes keyword-only arguments and works in grams and cents. The engine hides that difference inside its body. The step is to put a function of your own shape between the engine and the library; Feathers's chapter "My Application Is All API Calls" is the place to read about applications that lean on a library's API:

```python
def airco_quote(zone: str, weight_kg: Decimal, /, *, price: AircoPrice = airco.price) -> Decimal:
    """Price a consignment with AIRCO, in euros. Grams are truncated, as they always were."""
    cents = price(destination=zone, grams=int(weight_kg * 1000))
    return Decimal(cents) / 100
```

The conversions are the ones the engine had inline: `int` truncates grams and cents become euros (`test_airco_quote_converts_kilograms_and_cents`). The truncation stays, because a step doesn't fix behaviour, and the `grams-truncated` row still passes through `airco_quote`. Both carriers now fit `CarrierQuoter`, so the engine holds them as a mapping from carrier code to function. The tie-break is decided by the carrier code in the `min` key and not by the order of the mapping: the `function` form lists FASTLINE first, and its tie row still goes to AIRCO.

## The class becomes a function

By now the engine holds a mapping of carriers and a margin, and nothing changes after construction. A class with one method and fixed fields is a function with arguments; [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) is the pointer for passing behaviour as a callable. Here the carriers become a required argument, and the production choice is made once at the root:

<!-- fmt:off -->
```python
STANDARD_QUOTERS: Mapping[str, CarrierQuoter] = frozendict(
    {"AIRCO": airco_quote, "FASTLINE": request_quote}
)


def quote(
    consignment: Consignment,
    /,
    *,
    quoters: Mapping[str, CarrierQuoter],
    margin: Decimal = MARGIN,
) -> RateQuote:
    """Quote a consignment with the cheapest of the given carriers, plus a margin."""
    prices = {
        code: quoter(consignment.zone, consignment.weight_kg) for code, quoter in quoters.items()
    }
    code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
    total = (cheapest * margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return RateQuote(consignment.id, code, Money(total))


quote_standard = partial(quote, quoters=STANDARD_QUOTERS)
```
<!-- fmt:on -->

The parameterised engine kept defaults so existing callers still work, and the cost was the forgotten fake; the function form drops them. Omitting `quoters` is `[call-arg]` with `Missing named argument "quoters"` (`test_mypy_reports_a_missing_quoters_argument`), and at run time it is a `TypeError` (`test_the_function_form_needs_its_quoters`). `STANDARD_QUOTERS` names both carriers and refuses assignment (`test_standard_quoters_name_both_carriers`), and `quote_standard` is the one binding the root needs: `test_quote_standard_binds_the_standard_quoters` checks it wraps `quote` with `STANDARD_QUOTERS`. [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers `functools.partial` at a composition root, and the [`functools.partial` entry](https://docs.python.org/3/library/functools.html) in the standard library documentation describes what the object holds, including the `func` and `keywords` attributes the test reads.

## Subclass and override

A different move gets the same result with little change to the engine: move each SDK call into a method of its own, then subclass and override those methods in a test. The extraction is behaviour-preserving, and the subclass form passes the same table as a fifth `step` param (`test_every_step_matches_the_characterisation_table`). It's the one comparison form in the chapter, and it sits beside the parameter forms, which are the ones to keep:

<!-- fmt:off -->
```python
class _FakeCarrierRateEngine(_ExtractedCallsRateEngine):
    """Subclass and override: both carrier calls forward to fakes."""

    def __init__(
        self,
        fastline_fake: Callable[[str, Decimal], Decimal],
        airco_fake: Callable[..., int],
    ) -> None:
        super().__init__()
        self._fastline_fake = fastline_fake
        self._airco_fake = airco_fake

    @override
    def _fastline_quote(self, zone: str, weight_kg: Decimal) -> Decimal:
        return self._fastline_fake(zone, weight_kg)

    @override
    def _airco_price(self, zone: str, grams: int) -> int:
        return self._airco_fake(destination=zone, grams=grams)
```
<!-- fmt:on -->

The seam is a method name, and without `@override` nothing checks the name until it runs. A subclass that spells `_airco_prices` for `_airco_price` still constructs, and its quote reaches the real SDK (`test_a_misspelt_override_falls_through_to_the_real_carrier`). `@override` from `typing` closes the gap. A reduced model of the pattern, a base with `_fastline_quote` and a subclass that spells it `_fastline_qoute`, gives `[misc]` with "no base method was found with this name" when the method carries `@override`, and no error without it (`test_mypy_reports_a_misspelt_override_only_with_the_override_decorator`). The check applies where a method carries the decorator. [SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}) is the pointer for substitution. A callable parameter makes the same substitution visible at the call, where mypy checks the argument.

## Techniques Python makes unnecessary

Each move above has a Python form. The table gives the move in plain words, the form it takes here and the test that backs it. Feathers's chapter "Dependency Breaking Techniques" is the catalogue; the book is the place to read each technique in full.

| Move | Python form | Backed by |
| --- | --- | --- |
| Give a constructor its collaborators as parameters | Keyword parameters with the real calls as defaults | `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults` |
| Call through a stored function instead of a fixed one | Nothing to add: a function is a value, and `quote` takes a mapping of them | the `function` rows of the table |
| Introduce an abstraction for the collaborator | A `Callable` alias, or a callback Protocol the SDK needn't import | `test_mypy_checks_a_fake_passed_as_a_constructor_argument` |
| Subclass and override a method | Still works; `@override` makes a typo visible to mypy | `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator` |
| Redirect a global reference | A patch where the name is looked up, as in Seams in Python | the `legacy` rows of the table |
| Wrap an API in your own shape | `airco_quote` | `test_airco_quote_converts_kilograms_and_cents` |

<blockquote class="ai-sidebar" markdown="1">

**Breaking a dependency without changing behaviour.** "Make `RateEngine` testable" leaves the method open, and a rewrite can quietly change the tie-break or the timeout. Paste a prompt that fixes the order:

> Before changing `RateEngine`, write a characterisation table: for each row, the carriers' answers and the `(carrier, total, calls)` the code produces today, including the tie-break and the gram truncation. Change one thing per step and run the table after each: carriers as keyword parameters defaulting to the real calls; then `airco_quote` wrapping the AIRCO SDK into `CarrierQuoter`; then a `quote` function taking `quoters`, bound with `functools.partial`. Don't fix behaviour in the same step.

If an expected value in the table changed in the diff, ask which step meant to change behaviour.

</blockquote>

## Build, run, observe

From the example directory, `uv run pytest` runs 13 test functions as 42 cases, and `uv run mypy --strict src tests` checks the example. Each experiment below runs in a scratch copy of the repository: delete the copy's `.venv`, run `uv sync --locked --all-packages` from its root and check that `dependency_breaking.__file__` points into the copy.

The first makes an "improvement" during the parameterise step. In `src/dependency_breaking/parameterised.py`, catch `CarrierTimeoutError` around the FASTLINE call and quote AIRCO alone when FASTLINE times out: import the error from `dependency_breaking.domain`, set the FASTLINE price to `None` in the `except` branch, and add `"FASTLINE"` to the `prices` mapping only when a price came back. Then:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed))'
uv run mypy --strict src tests
```

```text
E       Failed: DID NOT RAISE CarrierTimeoutError
E       AssertionError: Regex pattern did not match.
E         Expected regex: 'FASTLINE did not answer'
E         Actual message: "AIRCO did not answer for 'EU'"
tests/test_steps.py:25: AssertionError
FAILED tests/test_characterisation.py::test_every_step_lets_a_carrier_timeout_fail_the_quote[parameterised]
FAILED tests/test_steps.py::test_a_parameterised_engine_keeps_the_real_carriers_as_defaults
2 failed, 40 passed in 1.82s
Success: no issues found in 12 source files
```

Two tests fail and the 25 table cases all pass. The timeout test for the `parameterised` form fails because the quote no longer raises, and the defaults test fails because its first assertion expects the FASTLINE timeout and gets AIRCO's. mypy exits 0: the change is type-correct, and the record of behaviour is what catches it.

The second restores that file and renames `_FakeCarrierRateEngine._airco_price` to `_airco_prices` in `tests/conftest.py`, keeping `@override` on it. The same two commands print:

```text
E       dependency_breaking.domain.CarrierTimeoutError: AIRCO did not answer for 'EU'
src/dependency_breaking/airco.py:13: CarrierTimeoutError
E       dependency_breaking.domain.CarrierTimeoutError: AIRCO did not answer for 'ASIA'
src/dependency_breaking/airco.py:13: CarrierTimeoutError
E       dependency_breaking.domain.CarrierTimeoutError: AIRCO did not answer for 'EU'
src/dependency_breaking/airco.py:13: CarrierTimeoutError
E       dependency_breaking.domain.CarrierTimeoutError: AIRCO did not answer for 'EU'
src/dependency_breaking/airco.py:13: CarrierTimeoutError
E       dependency_breaking.domain.CarrierTimeoutError: AIRCO did not answer for 'EU'
src/dependency_breaking/airco.py:13: CarrierTimeoutError
FAILED tests/test_characterisation.py::test_every_step_matches_the_characterisation_table[subclass-fastline-cheaper]
FAILED tests/test_characterisation.py::test_every_step_matches_the_characterisation_table[subclass-airco-cheaper]
FAILED tests/test_characterisation.py::test_every_step_matches_the_characterisation_table[subclass-tie-goes-to-airco]
FAILED tests/test_characterisation.py::test_every_step_matches_the_characterisation_table[subclass-margin-rounds-half-up]
FAILED tests/test_characterisation.py::test_every_step_matches_the_characterisation_table[subclass-grams-truncated]
5 failed, 37 passed in 1.77s
tests/conftest.py:99: error: Method "_airco_prices" is marked as an override, but no base method was found with this name  [misc]
Found 1 error in 1 file (checked 12 source files)
```

The five `subclass` rows of the table fail, because the base class's `_airco_price` runs and reaches the real AIRCO SDK. The timeout test for `subclass` still passes, since FASTLINE is asked first and raises first. mypy exits 1 with one `[misc]` error on the renamed method, because it carries `@override` and no base method has that name.

## What you can do now

- Pin what the engine does today: `CHARACTERISATION_ROWS` records the tie-break, half-up rounding and gram truncation, and `test_every_step_lets_a_carrier_timeout_fail_the_quote` records the timeout.
- Parameterise a constructor: `parameterised.RateEngine` takes fakes as arguments, and `test_mypy_checks_a_fake_passed_as_a_constructor_argument` shows mypy checking them.
- Wrap the SDK and bind at the root: `airco_quote` gives both carriers the `CarrierQuoter` shape, and `quote_standard` binds `STANDARD_QUOTERS` to `quote`.
- Run one table across the steps: `test_every_step_matches_the_characterisation_table` runs it against five forms, and `test_the_table_catches_a_step_that_changes_behaviour` shows it failing the rows two altered engines break.
- Choose the technique: the table above says what Python needs for each move, and `test_mypy_reports_a_misspelt_override_only_with_the_override_decorator` prices subclass and override.

## For deeper coverage

Michael Feathers's *Working Effectively with Legacy Code* (2004) is the source for characterisation tests and for the catalogue of dependency-breaking techniques: read "I Need To Make a Change but I Don't Know What Tests To Write", "My Application Is All API Calls" and "Dependency Breaking Techniques". The [`functools.partial` entry](https://docs.python.org/3/library/functools.html) documents the binding used at the root. [Fowler vs Feathers, contrasted and combined]({{ '/docs/35-fowler-vs-feathers/' | relative_url }}) and [Refactor or rewrite]({{ '/docs/36-refactor-or-rewrite/' | relative_url }}) are the related titles. The book is listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
