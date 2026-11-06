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

A rating engine written before anyone tested it prices a consignment with the cheaper of FASTLINE and AIRCO and adds a margin. The two carrier calls sit inside the method, so a test of the engine can't run without them. Test code can still change what the calls do, because Python looks a global name up when the call runs. That makes a seam of each name the engine reads from its module, and a patch of the name is how a test gets in. The tools for the patch are `monkeypatch` and `mock.patch`. Both need the name they patch to be the one the engine reads, and neither is checked by mypy.

Three failures show what goes wrong. A test of the engine reaches the carrier and fails with `CarrierTimeoutError` (`test_the_legacy_engine_calls_the_real_carrier`). A patch on the module that defines the carrier call changes nothing (`test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`). A patched margin is ignored (`test_patching_a_module_constant_misses_a_default_captured_at_definition`). The stand-in SDKs in the example do no I/O: where a real one would open a connection, each raises the error a timeout would.

{% include excalidraw.html name="33-seams-in-python" caption="Figure 33.1: A patch replaces a name where the engine looks it up. The legacy module holds its own name for the FASTLINE call, so patching the carrier's module misses it, and so does patching the margin constant after the class is defined." %}

Read the figure from the top. A blue box, "test", holds `monkeypatch.setattr("seams.legacy.request_quote", fake)` and has one arrow down to an accent box, "namespace of seams.legacy", which lists `request_quote`, `airco`, `MARGIN` and `RateEngine`. Two arrows lead from that box to a box for `RateEngine`: one labelled "request_quote: looked up in seams.legacy" and one labelled "airco.price: looked up on seams.airco". Two dashed boxes sit at the right, each with a dashed arrow pointing left at a box. The upper one, with its arrow at the namespace box, "patch on seams.fastline.request_quote", says the patch has no effect on `RateEngine.quote` because `seams.legacy` holds its own name. The lower one, with its arrow at the `RateEngine` box, "margin=MARGIN in __init__", says the default was read when the class was defined and a later patch of `MARGIN` misses it. A bar across the bottom reads "mypy checks neither the target string nor the replacement".

## Seams and enabling points

Michael Feathers asks, in "The Seam Model" in *Working Effectively with Legacy Code*, where code you can't yet edit lets you change what it does. A seam is a place where that change can be made from outside. The enabling point is the separate spot where you make it. He describes other kinds of seam besides the one used here. In Python the one at hand comes from the language: a function reads a global name when it runs, so a global name is a seam, and rebinding it in the namespace the function reads from is the enabling point.

Three names in the legacy module matter to a test of its carriers. Here it is as found:

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

`request_quote` is a function imported by name, so `seams.legacy` holds its own binding of it. `airco` is a module object, and `quote` reaches into it with `airco.price`. `MARGIN` is a constant, which `__init__` reads once, as a default. The first two are seams. The third looks like one, and the section on patches that miss shows why it isn't. The engine passes `mypy --strict`, ruff and the idiom scan unchanged, so none of the three flags it. That shape is the subject, and it's kept as found.

An object seam, a parameter a caller fills, is the subject of [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}), and [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) covers how mypy checks its shape. The engine has no such parameter for either carrier yet.

## Patch where the name is looked up

The `unittest.mock` documentation states the rule: ["patch() works by (temporarily) changing the object that a name points to with another one."](https://docs.python.org/3/library/unittest.mock.html) A few sentences later it gives the principle: "The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined."

A test that follows it replaces both carriers:

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

Both forms rebind a name in a module namespace, and the engine then asks the replacements: FASTLINE answers 25.00, AIRCO 28.00, and the quote is FASTLINE at 27.50. Patching `seams.fastline.request_quote` instead rebinds the name in the module that defines it. `seams.legacy` holds its own binding from the `from` import, so the engine still calls the real carrier (`test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`).

AIRCO goes the other way. The engine doesn't hold a name for `price`. It holds the module `airco` and reads `price` from it on each call, so the patch goes on `seams.airco`, the module the attribute belongs to (`test_a_module_attribute_is_patched_on_the_module_it_belongs_to`). With a cheaper AIRCO fake the quote becomes AIRCO at 22.00.

`unittest.mock.patch` as a context manager follows the same rule. Its target `seams.legacy.request_quote` gives FASTLINE at 27.50, and `seams.fastline.request_quote` leaves the real carrier in place (`test_unittest_mock_patch_follows_the_same_lookup_rule`). The import form decides the target. Experiment (b) below changes one import in `legacy.py` and moves the patch that works.

## monkeypatch or mock.patch

pytest's how-to says the fixture helps you to "safely set/delete an attribute, dictionary item or environment variable, or to modify sys.path for importing." Its changes are undone: "All modifications will be undone after the requesting test function or fixture has finished." For a narrower scope, `monkeypatch.context()` ends them at the end of a `with` block. After that block the engine's `request_quote` is again the function from `seams.fastline`, and `airco.price` is no longer the fake (`test_monkeypatch_undoes_its_changes_when_the_context_ends`). `mocker.patch` from pytest-mock takes the same string targets, and the `patch` guard and the autospec test below use it. `mock.patch` as a context manager appears once above, to show the rule holds for it. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) owns the table of doubles, and the API is collected under [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}). Mocks and `monkeypatch` appear in this example's tests because the patch is what's under test, and nowhere in its `src`.

The choice between the two tools is the choice of guard. Each has a guard against a target the module doesn't have:

- `monkeypatch.setattr("seams.legacy.request_qoute", fake)` raises `AttributeError` matching `has no attribute 'request_qoute'` (`test_monkeypatch_refuses_a_misspelt_name`). With `raising=False` it creates the name, and the engine still calls the real carrier, because nothing reads the new name (`test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`).
- `mocker.patch("seams.legacy.price")` raises `AttributeError` matching `does not have the attribute 'price'`, since `seams.legacy` holds `airco` and no `price`. With `create=True` the patch succeeds and the engine still calls the real carrier (`test_patch_refuses_a_name_the_module_does_not_have`).

Both refuse by default, and each has a switch that turns the refusal into a silent miss. The matches reflect the wording of pytest 9.2.0 for `monkeypatch` and of Python 3.15.2's `unittest.mock` for `patch`.

The same patch can also accept a call the real function would refuse. The mock documentation says "A more powerful form of spec is autospec." The test patches the carrier call twice, with `autospec=True` and without it:

```python
@pytest.mark.parametrize(
    ("autospec", "outcome"),
    [
        pytest.param(True, "TypeError: missing a required argument: 'weight_kg'", id="autospec"),
        pytest.param(False, "accepted", id="plain"),
    ],
)
def test_autospec_refuses_a_call_with_the_wrong_signature(
    mocker: MockerFixture, autospec: bool, outcome: str
) -> None:
    mocker.patch("seams.legacy.request_quote", autospec=autospec)
    call = _looked_up("request_quote")
    assert callable(call)

    try:
        call("EU")
        result = "accepted"
    except TypeError as error:
        result = f"TypeError: {error}"

    assert result == outcome
```

With `autospec=True` the replacement has the real function's signature, and a call with one argument raises `TypeError: missing a required argument: 'weight_kg'`. The plain patch accepts the same call. A plain patch therefore lets a call with the wrong arguments pass silently, unless the patch copies the signature.

## Patches that miss

Not every name can be reached. `__init__` takes `margin: Decimal = MARGIN`, and a default is evaluated once, when the class is defined. The test patches `seams.legacy.MARGIN` to 2 with both carriers faked:

<!-- fmt:off -->
```python
def test_patching_a_module_constant_misses_a_default_captured_at_definition(
    monkeypatch: pytest.MonkeyPatch,
    consignment: Consignment,
    fastline_fake: FastlineFake,
    airco_fake: AircoFake,
) -> None:
    monkeypatch.setattr("seams.legacy.request_quote", fastline_fake)
    monkeypatch.setattr(airco, "price", airco_fake)
    monkeypatch.setattr("seams.legacy.MARGIN", Decimal("2"))

    patched = legacy.RateEngine().quote(consignment)
    passed = legacy.RateEngine(margin=Decimal("2")).quote(consignment)

    assert str(patched.total.amount) == "27.50"
    assert str(passed.total.amount) == "50.00"
```
<!-- fmt:on -->

Passing `margin=` quotes 50.00, where the patch leaves 27.50. A default argument is a value captured at definition, so a patch to the global it was copied from can't change it.

A reload is the other miss. The `importlib` documentation says "When a module is reloaded, its dictionary (containing the module’s global variables) is retained." A reload re-runs the module body into that dictionary, which overwrites a live patch. The same page says "If a module imports objects from another module using from … import …, calling reload() for the other module does not redefine the objects imported from it". So after `fastline` is reloaded, `seams.legacy` still holds the pre-reload function. Reloading `seams.legacy` creates a new `RateEngine` class, and an instance made earlier isn't an instance of it. The test runs these steps in a fresh interpreter, which writes four facts, and compares them as a list: the patch is overwritten, teardown restores the pre-reload object, the `from`-import isn't rebound, and the old instance isn't an instance of the new class (`test_reload_discards_a_patch_and_keeps_old_bindings`). The reload doesn't run in the pytest process, so no other test sees a replaced class.

Python has a third kind of seam at a module. The engine reads `price` from whatever object `airco` names, so an object with the right method can stand in for the module:

```python
class _FakeAirco:
    def price(self, *, destination: str, grams: int) -> int:
        return 2000


class _WrongAirco:
    def quote(self, *, destination: str, grams: int) -> int:
        return 2000
```

With `monkeypatch.setattr(legacy, "airco", _FakeAirco())` the engine quotes AIRCO at 22.00. With `_WrongAirco()` the patch is accepted, the engine is constructed, and `quote` raises `AttributeError` matching `'_WrongAirco' object has no attribute 'price'`, at the call (`test_an_object_with_the_right_method_can_stand_in_for_a_module`).

## What mypy checks at each enabling point

mypy 2.4.1 under `--strict` checks different things at each enabling point. The tests run snippets through mypy's API and assert the exit status and the error codes. One of them, the Protocol-parameter snippet, is a reduced model, written to stand for a parameter the engine doesn't have yet.

The snippet below patches the carrier with a function that takes one parameter, where the engine passes two:

```python
from decimal import Decimal

import pytest
from seams import legacy


def wrong(zone: str) -> Decimal:
    return Decimal("1")


def patch_it(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(legacy, "request_quote", wrong)
```

mypy exits 0 with no errors. The same patch makes `quote` raise `TypeError` matching `positional argument` at run time (`test_mypy_does_not_check_a_monkeypatched_replacement`). A misspelt target string passes mypy as well, and raises `AttributeError` only when `monkeypatch.setattr` runs (`test_mypy_accepts_a_misspelt_monkeypatch_target_string`).

A direct assignment is checked. `legacy.request_quote = wrong`, with the same one-parameter function, gives exit status 1:

```text
<string>:11: error: Module "seams.legacy" does not explicitly export attribute "request_quote"  [attr-defined]
<string>:11: error: Incompatible types in assignment (expression has type "Callable[[str], Decimal]", variable has type "Callable[[str, Decimal], Decimal]")  [assignment]
```

Two codes appear because `seams.legacy` imports `request_quote` without re-exporting it, which `--strict` reports apart from the assignment's type error. The assertion in `test_mypy_checks_a_direct_assignment_to_a_module_name` expects both. That's why the example's tests read patched names with `vars(legacy)[name]` when they need the value.

`patch` itself has two types. Without `new=` it yields `MagicMock | AsyncMock`, as a union. With `new=` it yields the replacement's own type, so `reveal_type` prints `def (zone: str, weight_kg: decimal.Decimal) -> decimal.Decimal` (`test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement`). A test decorated with `@patch("seams.legacy.request_quote")` takes the injected mock as a parameter, and `--strict` wants it annotated: without `MagicMock` on the parameter mypy reports `[no-untyped-def]`, and with it the snippet is clean (`test_mypy_requires_an_annotation_on_a_decorator_injected_mock`).

A parameter is the seam mypy does check. In the reduced model, a callback Protocol, `FastlineQuote`, types a parameter that takes the carrier call, and passing a function of one parameter gives `[arg-type]` (`test_mypy_checks_a_fake_passed_to_a_protocol_parameter`).

## When a patch is the wrong seam

A patch is the way to get the first test around code that can't change yet. Each cost above can be measured, which is the comparison to a parameter:

- The target is a string tied to the import form. A `from` import needs the patch on the using module, and experiment (b) below moves it.
- mypy checks neither the target nor the replacement, so a misspelling or a wrong shape reaches run time.
- A default or a reload defeats the patch.
- A parameter is checked by mypy, and a fake of the wrong shape is rejected before the test runs.

The next step is the parameter. [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) makes it.

<blockquote class="ai-sidebar" markdown="1">
**Specifying where to patch.** "Mock the carrier in this test" leaves the target open, and a patch on the module that defines a `from`-imported function changes nothing. Paste a prompt that states the target:

> Patch `request_quote` where `seams.legacy` looks it up, with `monkeypatch.setattr("seams.legacy.request_quote", fake)`, not on `seams.fastline`. Keep `raising` at its default. With `mocker.patch`, pass `autospec=True`. Pass `margin=` instead of patching `MARGIN`, and don't call `importlib.reload` in a test. Then name the constructor parameter that would let this test drop the patch.

Run the test once with the fake returning another price; if the quote doesn't move, the patch missed.
</blockquote>

## Build, run, observe

From the repository root, once, run `uv sync --locked --all-packages`. Then, from `examples/33-seams-in-python`:

```bash
uv run pytest -q
uv run mypy --strict src tests
```

The suite is 19 test functions and 21 cases: 10 functions and 12 cases in the patching tests, 3 and 3 in the seams tests, and 6 and 6 in the static tests. On a clean copy the two commands end with:

```text
21 passed in 5.22s
Success: no issues found in 9 source files
```

Each experiment below changes one thing in a scratch copy of the repository: delete the copy's `.venv`, run `uv sync --locked --all-packages` and check that `seams.__file__` points into the copy. The first experiment uses this command and then runs mypy:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|errors?))'
uv run mypy --strict src tests
```

**Experiment (a).** In `tests/test_patching.py`, change the FASTLINE target in `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier` from `"seams.legacy.request_quote"` to `"seams.fastline.request_quote"`. The filter prints:

```text
E       seams.domain.CarrierTimeoutError: FASTLINE did not answer for 'EU'
src/seams/fastline.py:15: CarrierTimeoutError
FAILED tests/test_patching.py::test_patching_the_name_where_it_is_looked_up_replaces_the_carrier
1 failed, 20 passed in 5.12s
```

and mypy prints `Success: no issues found in 9 source files`. The patch is valid, so mypy has nothing to say, but it lands where the engine doesn't look, and the engine asks the real carrier.

**Experiment (b).** Restore the test. In `src/seams/legacy.py`, replace `from seams.fastline import request_quote` with `from seams import fastline`, and change the call in `quote` to `fastline.request_quote(consignment.zone, consignment.weight_kg)`. The full filter prints 44 lines for this change, so this run uses a narrower one:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|[0-9]+ (passed|failed|errors?))'
```

```text
FAILED tests/test_patching.py::test_patching_the_name_where_it_is_looked_up_replaces_the_carrier
FAILED tests/test_patching.py::test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier
FAILED tests/test_patching.py::test_a_module_attribute_is_patched_on_the_module_it_belongs_to
FAILED tests/test_patching.py::test_unittest_mock_patch_follows_the_same_lookup_rule[using-module]
FAILED tests/test_patching.py::test_unittest_mock_patch_follows_the_same_lookup_rule[defining-module]
FAILED tests/test_patching.py::test_autospec_refuses_a_call_with_the_wrong_signature[autospec]
FAILED tests/test_patching.py::test_autospec_refuses_a_call_with_the_wrong_signature[plain]
FAILED tests/test_patching.py::test_monkeypatch_undoes_its_changes_when_the_context_ends
FAILED tests/test_seams.py::test_patching_a_module_constant_misses_a_default_captured_at_definition
FAILED tests/test_seams.py::test_reload_discards_a_patch_and_keeps_old_bindings
FAILED tests/test_seams.py::test_an_object_with_the_right_method_can_stand_in_for_a_module
FAILED tests/test_static.py::test_mypy_does_not_check_a_monkeypatched_replacement
FAILED tests/test_static.py::test_mypy_checks_a_direct_assignment_to_a_module_name
13 failed, 8 passed in 5.29s
```

The two tests the move was aimed at tell the story. The full filter on those two prints:

```bash
uv run pytest -q tests/test_patching.py::test_patching_the_name_where_it_is_looked_up_replaces_the_carrier tests/test_patching.py::test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|errors?))'
```

```text
E           AttributeError: module 'seams.legacy' has no attribute 'request_quote'. Did you mean '.fastline.request_quote' instead of '.request_quote'?
E           AttributeError: 'module' object at seams.legacy has no attribute 'request_quote'
E       Failed: DID NOT RAISE CarrierTimeoutError
FAILED tests/test_patching.py::test_patching_the_name_where_it_is_looked_up_replaces_the_carrier
FAILED tests/test_patching.py::test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier
2 failed in 0.02s
```

The patch on `seams.legacy.request_quote` now has no name to rebind, so `monkeypatch` raises. The patch on `seams.fastline.request_quote`, which missed before, now reaches the call, so the test that expected the real carrier gets a fake and fails with `DID NOT RAISE`. Of the other eleven failures, nine fail the same way, because the test patches or reads `request_quote` on `seams.legacy`, which no longer holds it, and two flip. `test_unittest_mock_patch_follows_the_same_lookup_rule[defining-module]` now gets FASTLINE at 27.50 where it expected `CarrierTimeoutError`, and `test_mypy_checks_a_direct_assignment_to_a_module_name` loses `[assignment]` and reports only `[attr-defined]`, because the assignment targets a name the module no longer has. mypy still exits 0: `Success: no issues found in 9 source files`.

## What you can do now

- Name a seam and its enabling point: `legacy.py` holds a name imported by `from`, a module reached as `airco.price` and a default captured from `MARGIN`.
- Patch where the name is looked up: `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier` replaces both carriers, and `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier` shows the patch that misses.
- Choose between the tools and use their guards: `test_monkeypatch_refuses_a_misspelt_name` and `test_autospec_refuses_a_call_with_the_wrong_signature` fail where a plain patch accepts.
- Recognise the patches that can't reach: `test_patching_a_module_constant_misses_a_default_captured_at_definition` and `test_reload_discards_a_patch_and_keeps_old_bindings`.
- Say what mypy checks and when to use a parameter: `test_mypy_does_not_check_a_monkeypatched_replacement` against `test_mypy_checks_a_fake_passed_to_a_protocol_parameter`.

## For deeper coverage

The `unittest.mock` documentation has the [Where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch) and [Autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing) sections, and pytest's [monkeypatch how-to](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) describes the fixture's methods. The [`importlib.reload`](https://docs.python.org/3/library/importlib.html#importlib.reload) entry lists the caveats the reload test witnesses, and the [pytest-mock documentation](https://pytest-mock.readthedocs.io/en/latest/) covers `mocker`. Michael Feathers's *Working Effectively with Legacy Code* (Prentice Hall, 2004), in the chapter "The Seam Model", defines the seam and the enabling point. It's listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
