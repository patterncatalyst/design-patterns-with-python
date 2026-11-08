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

A patch gets a first test around code you can't change yet; [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) covers it. The next move is to change the code so tests need no patch. Changing code nobody has tested can change what it quotes: a tie-break moves, or a timeout gets swallowed. A dependency-breaking step changes structure and leaves behaviour alone, and the evidence is a record of the behaviour taken before the step.

The rating engine asks two carrier SDKs for a price, takes the cheaper, adds a margin and rounds. Both SDKs are stand-ins that do no I/O and raise `CarrierTimeoutError` where a real connection would time out, so code that reaches one fails. An unpinned step risks three things:

- A parameter with a real default lets a test that forgets a fake reach the real carrier.
- A step that also "improves" timeout handling changes what the engine does.
- A misspelt override reaches the real carrier.

{% include excalidraw.html name="34-dependency-breaking-techniques" described="true" caption="Figure 34.1: Each step moves the enabling point from a patched name toward a parameter mypy checks, and one characterisation table runs at every step. Subclass and override passes it too, but a misspelt method reaches the real carrier." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-34-dependency-breaking-techniques" markdown="1">
From the top. Four boxes step down the left: `legacy` ("enabling point: a patch on request_quote and airco.price"), `parameterised` ("keyword parameters; defaults are the real calls"), `wrapped` ("airco_quote fits CarrierQuoter") and, in the accent colour, `rating.quote` ("quoters required; quote_standard binds them"). A downward arrow labelled "one technique" joins each box to the next. On the right a tall box, "same characterisation table", has an arrow into each of the four. Beyond it a dashed box, "subclass and override", has a dashed arrow into the table box: it "also passes the same table", its seam is the overridden method names, and mypy reports a typo only with `@override`.
</div>
</details>

The figure shows the four steps down the left and the one table that every step must pass.

## Pin what the code does today

A characterisation test records what code does, so that a change can be told apart from a fix. Michael Feathers's *Working Effectively with Legacy Code* takes up the idea in "I Need to Make a Change, but I Don't Know What Tests to Write". Each row's expectation is what the engine returns, whether or not anyone would have chosen it. Two rows of `CHARACTERISATION_ROWS` are behaviour a reviewer might call wrong:

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

- **Half-up rounding.** A margin of 1.10 on 10.15 is 11.165, which rounds half up to 11.17. Half to even would give 11.16.
- **Gram truncation.** 0.0006 kg becomes zero grams because `int` truncates, so AIRCO prices a weightless parcel at a cent.

Neither is fixed here. The other three rows pin that the cheaper carrier wins in each direction and that a tie goes to AIRCO. A FASTLINE timeout fails the whole quote; it doesn't fall back to AIRCO. The `calls` column is compared after sorting, so it pins which carriers were asked and with what arguments, not the order.

The table runs against five forms of the engine through the `step` fixture in `tests/conftest.py`. Each form wires SDK-level fakes in at its own enabling point. The legacy engine takes no parameters, so its form is the one place that patches:

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

Nothing else patches, and nothing in `src` does. Five rows against five forms is 25 cases.

A table that can't fail proves nothing. Run against two altered engines, it fails exactly the row each one breaks: an engine that rounds grams fails `grams-truncated`, and one that rounds the margin half to even fails `margin-rounds-half-up`.

## Parameterise the constructor

The legacy engine reaches its carriers by names it looks up in its own module. A constructor that takes the carriers as parameters gives a test a seam without a patch, and existing callers don't change if each parameter defaults to the real call:

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

`parameterised.RateEngine()` still builds the production engine. `AircoPrice` is a callback Protocol because the AIRCO SDK takes keyword-only arguments and [a plain `Callable` can't say so](https://docs.python.org/3/library/typing.html#annotating-callable-objects); [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers Protocols.

mypy now checks the fake. A replacement that takes `zone` and `grams` positionally is `[arg-type]`, and the message names `AircoPrice`. A patch names its target by a string and mypy doesn't check the replacement. The price of the defaults runs the other way: a test that passes a FASTLINE fake and forgets AIRCO reaches the real SDK and fails with `AIRCO did not answer`. The stand-in raises, so the failure is loud; a real SDK would open a connection.

## Wrap the carrier with a different shape

FASTLINE takes a zone and kilograms and answers in euros. AIRCO takes keyword-only arguments and works in grams and cents. The engine hid that difference in its body. The step puts a function of your own shape between the engine and the library; Feathers's chapter "My Application Is All API Calls" covers applications that lean on a library's API:

```python
def airco_quote(zone: str, weight_kg: Decimal, /, *, price: AircoPrice = airco.price) -> Decimal:
    """Price a consignment with AIRCO, in euros. Grams are truncated, as they always were."""
    cents = price(destination=zone, grams=int(weight_kg * 1000))
    return Decimal(cents) / 100
```

The conversions are the ones the engine had inline. The truncation stays, because a step doesn't fix behaviour, and `grams-truncated` still passes through `airco_quote`. Both carriers now fit `CarrierQuoter`, so the engine holds them as a mapping from carrier code to function. The carrier code in the `min` key decides the tie-break, not the mapping's order: the function form lists FASTLINE first, and its tie still goes to AIRCO.

## The class becomes a function

The engine now holds a mapping of carriers and a margin, and nothing changes after construction. A class with one method and fixed fields is a function with arguments; [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) covers passing behaviour as a callable. The carriers become a required argument, and the production choice is made once at the root:

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

The parameterised engine kept defaults for existing callers, and paid with the forgotten fake. The function form drops them. Omitting `quoters` is `[call-arg]`, `Missing named argument "quoters"`, and a `TypeError` at run time. `STANDARD_QUOTERS` names both carriers and refuses assignment, and `quote_standard` is the one binding the root needs. [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers `functools.partial` at a composition root, and the [`functools.partial` entry](https://docs.python.org/3/library/functools.html) describes the `func` and `keywords` attributes the object holds.

## Subclass and override

Another move gets the same result with little change to the engine: move each SDK call into a method of its own, then override those methods in a test subclass. The extraction preserves behaviour, and the subclass form passes the same table as a fifth form. It's a comparison beside the parameter forms, which are the ones to keep:

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

The seam is a method name, and without `@override` nothing checks it before the quote runs. A subclass that spells `_airco_prices` for `_airco_price` still constructs, and its quote reaches the real SDK. With `@override` from `typing`, mypy reports `[misc]`, "no base method was found with this name"; without it, no error. [SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}) covers substitution. A callable parameter makes the same substitution visible at the call, where mypy checks the argument.

## Techniques Python makes unnecessary

Feathers's chapter "Dependency Breaking Techniques" is the catalogue; read each technique there in full. Each move has a Python form:

| Move | Python form |
| --- | --- |
| Give a constructor its collaborators as parameters | Keyword parameters with the real calls as defaults |
| Call through a stored function instead of a fixed one | Nothing to add: a function is a value, and `quote` takes a mapping of them |
| Introduce an abstraction for the collaborator | A `Callable` alias, or a callback Protocol the SDK needn't import |
| Subclass and override a method | Still works; `@override` makes a typo visible to mypy |
| Redirect a global reference | A patch where the name is looked up, as in Seams in Python |
| Wrap an API in your own shape | `airco_quote` |

<blockquote class="ai-sidebar" markdown="1">

**Breaking a dependency without changing behaviour.** "Make `RateEngine` testable" doesn't say how, and a rewrite can quietly change the tie-break or the timeout. Fix the order:

> Before changing `RateEngine`, write a characterisation table: for each row, the carriers' answers and the `(carrier, total, calls)` the code produces today, including the tie-break and the gram truncation. Change one thing per step and run the table after each: carriers as keyword parameters defaulting to the real calls; then `airco_quote` wrapping the AIRCO SDK into `CarrierQuoter`; then a `quote` function taking `quoters`, bound with `functools.partial`. Don't fix behaviour in the same step.

If an expected value in the table changed in the diff, ask which step meant to change behaviour.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/34-dependency-breaking-techniques
uv run pytest -q
uv run mypy --strict src tests
```

All 42 cases pass and mypy is clean. Run each experiment in a scratch copy of the repository with its own `.venv`, and check that `dependency_breaking.__file__` points into the copy:

- **Improve the timeout during a step.** In `src/dependency_breaking/parameterised.py`, catch `CarrierTimeoutError` around the FASTLINE call and quote AIRCO alone when FASTLINE times out. Two cases fail, both because the quote no longer raises the FASTLINE timeout; all 25 table cases still pass. mypy exits 0: the change is type-correct, and only the record of behaviour catches it.
- **Misspell an override.** Restore that file and rename `_FakeCarrierRateEngine._airco_price` to `_airco_prices` in `tests/conftest.py`, keeping `@override`. The five subclass rows fail with `CarrierTimeoutError: AIRCO did not answer`, because the base method runs. mypy exits 1 with one `[misc]` error on the renamed method.

## What you can do now

- Pin what the engine does today: `CHARACTERISATION_ROWS` records the tie-break, half-up rounding, gram truncation and the timeout.
- Parameterise a constructor: `parameterised.RateEngine` takes fakes as arguments, and mypy checks them.
- Wrap the SDK and bind at the root: `airco_quote` gives both carriers the `CarrierQuoter` shape, and `quote_standard` binds `STANDARD_QUOTERS` to `quote`.
- Run one table across the steps: five forms pass it, and two altered engines each fail the row they break.
- Choose the technique: the table above gives the Python form of each move, and `@override` prices subclass and override.

## For deeper coverage

Michael Feathers's *Working Effectively with Legacy Code* (2004) is the source for characterisation tests and for the catalogue of dependency-breaking techniques: read "I Need to Make a Change, but I Don't Know What Tests to Write", "My Application Is All API Calls" and "Dependency Breaking Techniques". The [`functools.partial` entry](https://docs.python.org/3/library/functools.html) documents the binding used at the root. [Fowler vs Feathers, contrasted and combined]({{ '/docs/35-fowler-vs-feathers/' | relative_url }}) and [Refactor or rewrite]({{ '/docs/36-refactor-or-rewrite/' | relative_url }}) are the related titles. The book is listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
