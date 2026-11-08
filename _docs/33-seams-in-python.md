---
title: "Seams in Python: monkeypatch, injection, and duck typing"
order: 33
layout: tutorial
sectionid: docs
part: "changing-inherited-code"
description: "Find the places in code you didn't write where a test can swap a dependency without editing it, and learn where a patch has to land for the swap to take effect."
---

## Learning objectives

By the end of this chapter you can:

- Name a seam and its enabling point, and find the seams the legacy `RateEngine` already has.
- Patch a name where it's looked up, and predict from the import form when a patch has no effect.
- Choose between `monkeypatch` and `mock.patch`, and use the guards that turn a silent miss into an error.
- Recognise patches that can't reach their target: a default captured at definition, and a reload.
- Say what mypy checks at each enabling point, and when to replace a patch with a parameter.

## Why this matters

A rating engine written before anyone tested it prices a consignment with the cheaper of FASTLINE and AIRCO and adds a margin. The two carrier calls sit inside the method, so a test of the engine can't run without them. Test code can still change what the calls do, because Python looks a global name up when the call runs. Each name the engine reads from its module is a way in, and `monkeypatch` and `mock.patch` are the tools. Both need the name they patch to be the one the engine reads, and mypy checks neither.

Three things go wrong:

- A test of the engine reaches the carrier and fails with `CarrierTimeoutError`.
- A patch on the module that defines the carrier call changes nothing.
- A patched margin is ignored.

The stand-in SDKs do no I/O: where a real one would open a connection, each raises the error a timeout would.

{% include excalidraw.html name="33-seams-in-python" described="true" caption="Figure 33.1: A patch replaces a name where the engine looks it up. The legacy module holds its own name for the FASTLINE call, so patching the carrier's module misses it, and so does patching the margin constant after the class is defined." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-33-seams-in-python" markdown="1">
From the top. A blue box, "test", holds `monkeypatch.setattr("seams.legacy.request_quote", fake)` and has one arrow down to an accent box, "namespace of seams.legacy", which lists `request_quote`, `airco`, `MARGIN` and `RateEngine`. Two arrows lead from that box to a box for `RateEngine`: one labelled "request_quote: looked up in seams.legacy" and one labelled "airco.price: looked up on seams.airco". Two dashed boxes sit at the right as notes, with no arrows to anything. The upper one, "patch on seams.fastline.request_quote", says the patch has no effect on `RateEngine.quote` because `seams.legacy` holds its own name. The lower one, "margin=MARGIN in __init__", says the default was read when the class was defined and a later patch of `MARGIN` misses it. A bar across the bottom reads "mypy checks neither the target string nor the replacement".
</div>
</details>

The figure traces the patch into the legacy module's namespace and marks the two patches that miss.

## Seams and enabling points

Michael Feathers asks, in "The Seam Model" in *Working Effectively with Legacy Code*, where code you can't yet edit lets you change what it does. A seam is a place where that change can be made from outside. The enabling point is the separate spot where you make it. Feathers describes several kinds. In Python the one at hand comes from the language: a function reads a global name when it runs, so a global name is a seam, and rebinding it in the namespace the function reads from is the enabling point.

The legacy module, as found:

```python
from decimal import ROUND_HALF_UP, Decimal

from seams import airco
from seams.domain import Consignment, Money, RateQuote
from seams.fastline import request_quote

MARGIN = Decimal("1.10")


class RateEngine:
    """Quote a consignment with the cheaper of two carriers, plus a margin."""

    def __init__(self, *, margin: Decimal = MARGIN) -> None:
        self._margin = margin

    def quote(self, consignment: Consignment) -> RateQuote:
        fastline_price = request_quote(consignment.zone, consignment.weight_kg)
        airco_cents = airco.price(
            destination=consignment.zone, grams=int(consignment.weight_kg * 1000)
        )
        prices = {"AIRCO": Decimal(airco_cents) / 100, "FASTLINE": fastline_price}
        code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
        total = (cheapest * self._margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, code, Money(total))
```

| Name | What `seams.legacy` holds | Seam? |
| --- | --- | --- |
| `request_quote` | its own binding, from a `from` import | yes, patched on `seams.legacy` |
| `airco` | the module object; `price` is read from it on each call | yes, patched on `seams.airco` |
| `MARGIN` | a constant `__init__` reads once, as a default | no |

The engine passes `mypy --strict`, ruff and the idiom scan unchanged. No tool flags this shape, and it stays as found.

An object seam, a parameter a caller fills, is the subject of [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}), and [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers how mypy checks its shape. The engine has no such parameter for either carrier yet.

## Patch where the name is looked up

The `unittest.mock` documentation states the rule: ["patch() works by (temporarily) changing the object that a name points to with another one."](https://docs.python.org/3/library/unittest.mock.html) It gives the principle: "The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined."

```python
def test_patching_the_name_where_it_is_looked_up_replaces_the_carrier(
    monkeypatch: pytest.MonkeyPatch,
    consignment: Consignment,
    fastline_fake: FastlineFake,
    airco_fake: AircoFake,
    airco_grams: list[int],
) -> None:
    monkeypatch.setattr("seams.legacy.request_quote", fastline_fake)
    monkeypatch.setattr(airco, "price", airco_fake)

    assert _answer(consignment) == ("FASTLINE", "27.50")
    assert airco_grams == [12500]
```

FASTLINE answers 25.00, AIRCO 28.00, and the quote is FASTLINE at 27.50. The string form and the object form both rebind a name in a module namespace. Where each patch lands:

| Target | Effect |
| --- | --- |
| `seams.legacy.request_quote` | the engine calls the fake |
| `seams.fastline.request_quote` | no effect: `seams.legacy` holds its own binding |
| `price` on `seams.airco` | the engine calls the fake; a cheaper one gives AIRCO at 22.00 |
| `unittest.mock.patch`, same targets | same results |

The import form decides the target. Change `from seams.fastline import request_quote` to `from seams import fastline` and the patch that works moves to `seams.fastline`.

## monkeypatch or mock.patch

pytest's how-to says the fixture helps you to "safely set/delete an attribute, dictionary item or environment variable, or to modify sys.path for importing." Its changes are undone: "All modifications will be undone after the requesting test function or fixture has finished." `monkeypatch.context()` ends them at the end of a `with` block instead. `mocker.patch` from pytest-mock takes the same string targets. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) owns the table of doubles, and [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}) collects the API. Mocks and `monkeypatch` appear only in tests, never in `src`.

The choice between the two is the choice of guard. Each refuses a target the module doesn't have, and each has a switch that turns the refusal into a silent miss:

| Call | Default | With the switch |
| --- | --- | --- |
| `monkeypatch.setattr("seams.legacy.request_qoute", fake)` | `AttributeError`, `has no attribute 'request_qoute'` | `raising=False` creates the name; nothing reads it, and the real carrier is called |
| `mocker.patch("seams.legacy.price")` | `AttributeError`, `does not have the attribute 'price'` | `create=True` succeeds; the real carrier is called |

The messages are the wording of pytest 9.2.0 for `monkeypatch` and of Python 3.15.2's `unittest.mock` for `patch`.

A patch can also accept a call the real function would refuse. The mock documentation says "A more powerful form of spec is autospec." With `mocker.patch("seams.legacy.request_quote", autospec=True)`, a call with one argument raises `TypeError: missing a required argument: 'weight_kg'`. Without `autospec` the same call is accepted.

## Patches that miss

`__init__` takes `margin: Decimal = MARGIN`, and a default is evaluated once, when the class is defined. Patching `seams.legacy.MARGIN` to 2 leaves the quote at 27.50; passing `margin=Decimal("2")` gives 50.00. A patch to the global a default was copied from can't change the default.

A reload is the other miss. The `importlib` documentation says "When a module is reloaded, its dictionary (containing the module’s global variables) is retained." A reload re-runs the module body into that dictionary, which overwrites a live patch. The same page says "If a module imports objects from another module using from … import …, calling reload() for the other module does not redefine the objects imported from it". Run in a fresh interpreter, a reload gives four results:

- the live patch is overwritten;
- teardown restores the pre-reload object;
- after `fastline` is reloaded, `seams.legacy` still holds the pre-reload function;
- reloading `seams.legacy` creates a new `RateEngine` class, and an instance made earlier isn't an instance of it.

Run a reload in its own interpreter: in the pytest process a replaced class leaks into other tests.

A module is also a duck-typed seam. The engine reads `price` from whatever object `airco` names, so an object with the right method can stand in for the module:

```python
class _FakeAirco:
    def price(self, *, destination: str, grams: int) -> int:
        return 2000


class _WrongAirco:
    def quote(self, *, destination: str, grams: int) -> int:
        return 2000
```

With `monkeypatch.setattr(legacy, "airco", _FakeAirco())` the engine quotes AIRCO at 22.00. With `_WrongAirco()` the patch is accepted, the engine is constructed, and `quote` raises `AttributeError` matching `'_WrongAirco' object has no attribute 'price'` at the call.

## What mypy checks at each enabling point

mypy 2.4.1 under `--strict` checks different things at each enabling point. This snippet patches the carrier with a function of one parameter, where the engine passes two:

```python
from decimal import Decimal

import pytest
from seams import legacy


def wrong(zone: str) -> Decimal:
    return Decimal("1")


def patch_it(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(legacy, "request_quote", wrong)
```

mypy exits 0, and `quote` raises `TypeError` matching `positional argument` at run time. A direct assignment, `legacy.request_quote = wrong`, is checked:

```text
<string>:11: error: Module "seams.legacy" does not explicitly export attribute "request_quote"  [attr-defined]
<string>:11: error: Incompatible types in assignment (expression has type "Callable[[str], Decimal]", variable has type "Callable[[str, Decimal], Decimal]")  [assignment]
```

`[attr-defined]` appears because `seams.legacy` imports `request_quote` without re-exporting it, which `--strict` reports apart from the type error. That's why the tests read patched names with `vars(legacy)[name]`.

| Enabling point | mypy `--strict` |
| --- | --- |
| `monkeypatch.setattr` with a wrong-shaped replacement | exit 0 |
| `monkeypatch.setattr` with a misspelt target string | exit 0; `AttributeError` at run time |
| direct assignment to the module name | `[attr-defined]` and `[assignment]` |
| `patch` without `new=` | yields `MagicMock \| AsyncMock` |
| `patch` with `new=` | yields the replacement's type, `def (zone: str, weight_kg: decimal.Decimal) -> decimal.Decimal` |
| `@patch(...)` with an unannotated injected mock | `[no-untyped-def]`; clean with `MagicMock` on the parameter |
| a one-parameter function passed to a `FastlineQuote` Protocol parameter | `[arg-type]` |

The last row is a reduced model of a parameter the engine doesn't have yet. A parameter is the seam mypy does check.

## When a patch is the wrong seam

A patch gets the first test around code that can't change yet. Its costs, against a parameter:

- **The target is a string tied to the import form.** A `from` import needs the patch on the using module.
- **mypy checks neither the target nor the replacement,** so a misspelling or a wrong shape reaches run time.
- **A default or a reload defeats the patch.**
- **A parameter is checked by mypy,** and a fake of the wrong shape is rejected before anything runs.

The next step is the parameter, which [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) makes.

> **🤖 Explore with your agent**
>
> "Patch `request_quote` where `seams.legacy` looks it up, with `monkeypatch.setattr("seams.legacy.request_quote", fake)`, not on `seams.fastline`. Keep `raising` at its default. With `mocker.patch`, pass `autospec=True`. Pass `margin=` instead of patching `MARGIN`, and don't call `importlib.reload` in a test. Then name the constructor parameter that would let a test drop the patch."
>
> Run it once with the fake returning another price; if the quote doesn't move, the patch missed.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/33-seams-in-python
uv run pytest -q
uv run mypy --strict src tests
```

All 21 cases pass and mypy is clean. Run each experiment in a scratch copy of the repository with its own `.venv`, and check that `seams.__file__` points into the copy:

- **Patch the defining module.** In `tests/test_patching.py`, change the FASTLINE target from `"seams.legacy.request_quote"` to `"seams.fastline.request_quote"`. One case fails with `CarrierTimeoutError: FASTLINE did not answer for 'EU'`, and mypy stays green: the patch is valid but lands where the engine doesn't look.
- **Change the import form.** In `src/seams/legacy.py`, replace `from seams.fastline import request_quote` with `from seams import fastline` and call `fastline.request_quote(...)`. Thirteen cases fail. Patches on `seams.legacy.request_quote` raise `AttributeError` because the name is gone, and the patch on `seams.fastline` that missed before now reaches the call. mypy still exits 0.

## What you can do now

- Name a seam and its enabling point: `legacy.py` holds a name imported by `from`, a module reached as `airco.price` and a default captured from `MARGIN`.
- Patch where the name is looked up: on `seams.legacy` for the `from` import, on `seams.airco` for the module attribute.
- Choose between the tools and keep their guards: `raising` and `create` at their defaults, and `autospec=True`.
- Recognise the patches that can't reach: a default captured at definition, and a reload.
- Say what mypy checks: nothing about a patch, and the shape of a parameter.

## For deeper coverage

The `unittest.mock` documentation has the [Where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch) and [Autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing) sections, and pytest's [monkeypatch how-to](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) describes the fixture's methods. The [`importlib.reload`](https://docs.python.org/3/library/importlib.html#importlib.reload) entry lists the reload caveats, and the [pytest-mock documentation](https://pytest-mock.readthedocs.io/en/stable/) covers `mocker`. Michael Feathers's *Working Effectively with Legacy Code* (Prentice Hall, 2004), in "The Seam Model", defines the seam and the enabling point. It's listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
