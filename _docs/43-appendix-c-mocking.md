---
title: "Mocking reference: unittest.mock and pytest-mock"
order: 43
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "C"
description: "Reference for the unittest.mock and pytest-mock names the examples use, in the order they're preferred, each with the call that shows it."
---

## Learning objectives

By the end of this appendix you can:

- Choose between a fake, an autospec and a patch, and say what each one checks.
- Build a double that refuses the names and the calls its target refuses.
- Configure a double and read its calls back without asserting less than you meant.
- Patch through `mocker`, and say what it undoes and what it warns about.
- Say what mypy reports about a mock, and what it can't.

## Why this matters

A mock is the cheapest double to write and the one that checks the least. A plain `Mock` accepts any attribute and any call, and mypy accepts a mock wherever a type is expected, because typeshed declares `NonCallableMock`, the base of `Mock` and `MagicMock`, as a subclass of `Any` ([Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) runs the check). A mock bypasses the static check, and every check it makes is one you configured. So prefer, in order:

1. **A fake passed as a parameter.** mypy holds it to the Protocol, and nothing is patched. See [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}).
2. **`create_autospec`, when the calls are the claim.** An autospec copies the names and signatures of its target, so a wrong name or a wrong call fails at run time.
3. **A patch, only where the code takes no parameter.** See [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) and [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) for where a patch is the only seam and how to replace it.

Everything below is on pytest-mock 3.17.0. Mocks appear only in test files and test `conftest.py` files, never in an example's `src`.

| Where | What it uses |
| --- | --- |
| [The three-way split]({{ '/docs/03-the-three-way-split/' | relative_url }}) | `monkeypatch.setattr(module, "NAME", value)` |
| [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) | `mocker.create_autospec(..., instance=True)`, `assert_called_once_with` |
| [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) | `create_autospec`, `Mock()`, `Mock(spec=...)`, `return_value`, `side_effect`, `assert_not_called`, `monkeypatch.context()` |
| [Seams in Python]({{ '/docs/33-seams-in-python/' | relative_url }}) | `mocker.patch` by string with `create=True` and `autospec=`, `unittest.mock.patch`, `monkeypatch.setattr` |
| [Dependency-breaking techniques]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) | `monkeypatch.setattr`, taken with `request.getfixturevalue` |

## Making a double

`Mock()`, `Mock(spec=...)` and `create_autospec(..., instance=True)` are compared in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}). Each form below adds one refusal or one behaviour.

| Form | Example | What it adds |
| --- | --- | --- |
| `spec_set` | `mocker.Mock(spec_set=CarrierGateway)` | Setting or getting an unknown name raises `Mock object has no attribute 'cancel'`; `spec` allows the assignment |
| `seal` | `mocker.seal(gateway)` | A name nobody configured raises `AttributeError`; configured names still answer |
| `unsafe` | `mocker.Mock(unsafe=True)` | Allows `assret_called_once()` and similar typos, which otherwise raise `AttributeError` |
| `MagicMock` | `mocker.MagicMock()` | Supports magic methods such as `len`; `Mock()` raises `TypeError` |
| `wraps` | `mocker.Mock(wraps=fastline)` | Calls pass through to the real object and return its result, and are recorded |

`seal` suits a double that's fully configured, where a forgotten attribute should fail and not return a new mock. `wraps` suits a double that should record calls and still behave like the real gateway; for an object you own, `mocker.spy` does the same without a wrapper.

The `unittest.mock` page on typo protection: "unsafe: By default, accessing any attribute whose name starts with assert, assret, asert, aseert or assrt will raise an AttributeError." On Python 3.15.2 `unsafe=True` applies to the mock it's passed to, not to its children:

```python
    unchecked.assret_called_once()
    assert unchecked.assret_called_once.call_count == 1
    with pytest.raises(AttributeError, match="assret_called_once"):
        unchecked.book.assret_called_once()
```

`mocker` re-exports `Mock`, `MagicMock`, `PropertyMock`, `AsyncMock`, `ANY`, `DEFAULT`, `call`, `sentinel`, `mock_open` and `seal` from `unittest.mock`.

## Configuring and inspecting calls

| Name | What it does |
| --- | --- |
| `side_effect = [value, Error("late")]` | Returns each item in turn, raises an item that's an exception, then raises `StopIteration` |
| `side_effect = fn` | Computes the return value from the call's arguments |
| `side_effect = Error(...)` | Drives a branch the happy path never reaches |
| `mock_calls`, `call` | Every call, child calls included, in order |
| `called`, `call_count`, `call_args`, `call_args_list` | Whether, how often, the last call, every call |
| `ANY` | Equals any argument |
| `assert_any_call` | Some call matched, wherever it falls |
| `assert_has_calls` | A contiguous, ordered run of calls; `any_order=True` drops both conditions |
| `reset_mock()` | Clears the calls and keeps `return_value`; `reset_mock(return_value=True)` clears that too |

An iterable `side_effect` gives one double a sequence of answers, such as a carrier that answers once and then times out:

```python
    gateway.quote.side_effect = [CarrierQuote("FASTLINE", ONE), CarrierTimeoutError("late")]
```

`ANY` pins one argument and leaves the other free:

```python
    assert gateway.quote.call_args_list == [
        mock.call("CN-1", mock.ANY),
        mock.call(mock.ANY, Decimal("2")),
    ]
```

`mock_calls` records the calls on a mock and every child, which lets one assertion fix an order across doubles. Two autospecs have separate lists, so attach both to one manager with `attach_mock`:

```python
def test_mock_calls_records_calls_in_order_with_call_objects(mocker: MockerFixture) -> None:
    airco = mocker.create_autospec(CarrierGateway, instance=True)
    fastline = mocker.create_autospec(CarrierGateway, instance=True)
    airco.quote.return_value = CarrierQuote("AIRCO", Decimal("12.00"))
    fastline.quote.return_value = CarrierQuote("FASTLINE", Decimal("9.00"))
    fastline.book.return_value = "FASTLINE:CN-1"
    manager = mocker.Mock()
    manager.attach_mock(airco, "airco")
    manager.attach_mock(fastline, "fastline")
    notify = mocker.stub(name="notify")

    book_cheapest({"fastline": fastline, "airco": airco}, CN1, Decimal("20"), notify=notify)

    assert manager.mock_calls == [
        mock.call.airco.quote(CN1, Decimal("20")),
        mock.call.fastline.quote(CN1, Decimal("20")),
        mock.call.fastline.book(CN1),
    ]
    assert fastline.mock_calls == [mock.call.quote(CN1, Decimal("20")), mock.call.book(CN1)]
```

That assertion checks calls and never the reference `book_cheapest` returns, so it can't say whether the customer got the right answer. Assert the result first.

`assert_has_calls` is stricter than its name suggests and looser than `mock_calls ==`: "If any_order is false then the calls must be sequential." Extra calls before or after the run are allowed; a gap or a reversal isn't:

```python
def test_assert_has_calls_checks_a_contiguous_ordered_run(mocker: MockerFixture) -> None:
    gateway = mocker.create_autospec(CarrierGateway, instance=True)
    for number in ("CN-1", "CN-2", "CN-3"):
        gateway.book(ConsignmentId(number))

    gateway.book.assert_has_calls([mock.call("CN-2"), mock.call("CN-3")])
    with pytest.raises(AssertionError, match="Calls not found"):
        gateway.book.assert_has_calls([mock.call("CN-1"), mock.call("CN-3")])
    with pytest.raises(AssertionError, match="Calls not found"):
        gateway.book.assert_has_calls([mock.call("CN-3"), mock.call("CN-2")])
    gateway.book.assert_has_calls([mock.call("CN-3"), mock.call("CN-1")], any_order=True)
```

`any_order=True` is the weaker check. To say the calls were exactly these, compare `mock_calls` with a list.

## Patching with mocker

A patch replaces a name for the length of a test, and it's the last choice. "The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined." [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) shows the rule for `monkeypatch.setattr` and `unittest.mock.patch`, and [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}) covers `monkeypatch`.

| Call | What it does |
| --- | --- |
| `mocker.patch("pkg.module.name")` | Replaces the name in the module the dotted string names |
| `mocker.patch(..., create=True)` | Allows a name the module doesn't have; without it the patch raises `AttributeError` |
| `mocker.patch(..., autospec=True)` | Refuses a call with the wrong signature, with a `TypeError` |
| `mocker.patch.object(Target, "name", autospec=True)` | Replaces one attribute and checks the signature |
| `mocker.patch.dict(os.environ, {"CARRIER_REGION": "EU"})` | Adds values to a mapping, restored on stop whether the key existed or not |
| `mocker.stop(patched)` | Undoes one patch |
| `mocker.stopall()` | Undoes every patch the fixture made |

`patch.object` with `autospec=True` on a class attribute keeps `self` in the signature, so the recorded call includes the instance:

```python
    patched = mocker.patch.object(FastlineGateway, "quote", autospec=True, return_value=canned)
    gateway = FastlineGateway()

    assert gateway.quote(CN1, TEN) == canned
    patched.assert_called_once_with(gateway, CN1, TEN)
```

A call with no arguments raises `TypeError` matching `missing a required argument`. Patches are also undone without any call: "The mocker fixture automatically undoes mocking at the end of a test." That sentence is in the plugin's source for 3.17.0. Use `stop` and `stopall` when the test needs the real object back part-way through.

The same warning is raised when a `mocker` patch is used as a context manager, because the plugin exists "to make the use of context managers and function decorators for mocking unnecessary". On 3.17.0 only the context-manager form warns, because the plugin attaches the warning to the mock's `__enter__`. Under `filterwarnings = ["error"]` the warning is an exception:

```python
def test_mocker_patch_used_as_a_context_manager_fails_under_the_warning_filter(
    mocker: MockerFixture,
) -> None:
    with (
        pytest.raises(PytestMockWarning, match="do not need to be used as context managers"),
        mocker.patch.object(FastlineGateway, "book"),
    ):
        pass
```

Use `mocker.patch.context_manager` when the mocked object is itself a context manager. Outside pytest, `unittest.mock.patch` "can be used as a decorator, class decorator or a context manager"; a decorator-injected argument needs an annotation for mypy.

## Spies and stubs

A spy runs the real code and records it: "The mocker.spy object acts exactly like the original method in all cases, except the spy also tracks function/method calls, return values and exceptions raised." A stub is a recording callable for a callback the code under test is given.

| Name | What it holds or does |
| --- | --- |
| `spy = mocker.spy(fastline, "quote")` | Wraps the real method |
| `spy.spy_return` | The last returned value |
| `spy.spy_return_list` | Every returned value |
| `spy.spy_exception` | The exception from the last call that raised; `spy_return` is then `None` |
| `mocker.stub(name="notify")` | A recording callable with no configured answer |

```python
    notify = mocker.stub(name="notify")

    book_cheapest({"fastline": fastline}, CN1, TEN, notify=notify)

    notify.assert_called_once_with("FASTLINE:CN-1")
```

Check with `assert_not_called()` that a path sent no reference.

`mocker.resetall()` resets some doubles and not others. It "calls reset_mock() on the mocks created through mocker so far: those from mocker.patch (and its variants), mocker.spy and mocker.create_autospec", and "Mocks created with mocker.stub(), mocker.async_stub() or mocker.Mock() and the other aliases are not tracked, so they are not reset":

```python
def test_resetall_resets_patches_spies_and_autospecs_but_not_stubs(
    mocker: MockerFixture, fastline: FastlineGateway
) -> None:
    patched = mocker.patch.object(FastlineGateway, "book", return_value="PATCHED")
    spy = mocker.spy(fastline, "quote")
    autospec = mocker.create_autospec(CarrierGateway, instance=True)
    stub = mocker.stub(name="notify")
    alias = mocker.Mock()
    fastline.book(CN1)
    fastline.quote(CN1, TEN)
    autospec.quote(CN1, TEN)
    stub("x")
    alias("x")

    mocker.resetall()

    counts: list[int] = [
        patched.call_count,
        spy.call_count,
        autospec.quote.call_count,
        stub.call_count,
        alias.call_count,
    ]
    assert counts == [0, 0, 0, 1, 1]
```

"By default only the recorded calls are reset." Reset a reused stub with `stub.reset_mock()`.

## Async doubles

A double for an `async def` returns something awaitable, and its await is recorded apart from its call. `create_autospec` of an async function does both:

```python
def test_autospec_of_an_async_function_records_the_await(mocker: MockerFixture) -> None:
    confirm_double: MagicMock = mocker.create_autospec(confirm)
    confirm_double.return_value = "CONFIRMED:FASTLINE:CN-1"

    result = asyncio.run(confirm_double("FASTLINE:CN-1"))

    assert result == "CONFIRMED:FASTLINE:CN-1"
    confirm_double.assert_awaited_once_with("FASTLINE:CN-1")
```

`mocker.AsyncMock(return_value=...)` works the same way. "Do not use called or call_count alone to check that an asynchronous callback was awaited."

## What mypy sees

With the fixture annotated `MockerFixture`, `mypy --strict --warn-unreachable` reveals:

| Call | `reveal_type` |
| --- | --- |
| `mocker.patch("os.getcwd")` | `unittest.mock.MagicMock \| unittest.mock.AsyncMock \| unittest.mock.NonCallableMagicMock` |
| `mocker.patch.object(Gateway, "book")` | the same union |
| `mocker.spy(Gateway(), "book")` | `pytest_mock.plugin.SpyType` |
| `mocker.stub()` | `unittest.mock.MagicMock` |
| `mocker.Mock()` | `Any` |

`mocker.Mock()` is `Any`, so mypy accepts every use of it. mypy still checks the code on either side of the double. `mocker.stub()` passed as a `Notify` callback is accepted. A hand-written `def notify(reference: int) -> None` in the same position is one `arg-type` error naming `Callable[[str], None]`. A real callback is held to the signature; a stub isn't.

## Running the reference tests

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then:

```bash
cd examples/43-appendix-c-mocking
uv run pytest -v
uv run mypy --strict src tests
```

All 32 cases pass and mypy is clean. The context-manager warning case needs the root `filterwarnings = ["error"]`, which pytest finds from the member directory.

## For deeper coverage

The standard library's [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html) page is the reference for every name here, and its companion [`unittest.mock` getting started](https://docs.python.org/3/library/unittest.mock-examples.html) works through the API by example. The pytest-mock [usage page](https://pytest-mock.readthedocs.io/en/stable/usage.html) covers the `mocker` fixture, including `mocker.patch.multiple`, `mocker.async_stub` and the fixtures of other scopes, which aren't used here. Typeshed's [`unittest/mock.pyi`](https://github.com/python/typeshed/blob/d03a581a8ebf525cba072b3e24e97f64825505b9/stdlib/unittest/mock.pyi) holds the comment about `Any` that explains what mypy does with a mock.

Martin Fowler's article [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) sets state verification against the behaviour verification that mocks make possible, which is the choice behind the order of preference. Gerard Meszaros's *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007) supplies the names dummy, fake, stub, spy and mock, and is on the [bibliography page]({{ '/bibliography/' | relative_url }}).
