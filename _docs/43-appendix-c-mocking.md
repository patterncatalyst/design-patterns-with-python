---
title: "Mocking reference: unittest.mock and pytest-mock"
order: 43
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "C"
description: "Reference for the unittest.mock and pytest-mock names the book uses, after the order in which it prefers them, each shown by a test."
---

## Learning objectives

By the end of this appendix you can:

- Choose between a fake, an autospec and a patch, and say what each one checks.
- Build a double that refuses the names and the calls its target refuses.
- Configure a double and read its calls back without asserting less than you meant.
- Patch through `mocker`, and say what it undoes and what it warns about.
- Say what mypy reports about a mock, and what it can't.

## Why this matters

A mock is the cheapest double to write and the one that checks the least. A plain `Mock` accepts any attribute and any call. mypy accepts a mock wherever a type is expected, because typeshed declares `NonCallableMock`, the base of `Mock` and `MagicMock`, as a subclass of `Any`; the chapter titled [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) quotes the comment and runs the check. A mock therefore bypasses the static check, and every check it makes is one you configured. That's the reason for the order the book follows:

1. **A fake passed as a parameter.** mypy holds a fake to the Protocol, and nothing is patched. The chapter titled [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) builds this form.
2. **`create_autospec`, when the calls are the claim.** An autospec copies the names and signatures of its target, so a wrong name or a wrong call fails at run time. "Proving it works: pytest, pytest-mock, and mypy" has the tests.
3. **A patch, only where the code takes no parameter.** The chapters titled [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) and [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) show where a patch is the only seam, and how to replace it with a parameter.

The reference that follows covers the second and third steps and the call checks they share. Each API row names a test on pytest-mock 3.17.0 and Python 3.15.2, in `examples/43-appendix-c-mocking` or in the example of the chapter the row names. In `examples/43-appendix-c-mocking` mocks appear only in the tests, whose subject is the mock API, and `src` holds none.

## Where the book uses mocks

Sixteen files in six examples name `mocker`, `unittest.mock`, `create_autospec`, `MagicMock` or `monkeypatch`. Every one is a test file or a test `conftest.py`, and no example's `src` directory names any of them. Eleven of the sixteen use `mocker` or `unittest.mock`; eight use `monkeypatch`.

| Chapter | File | What it uses |
| --- | --- | --- |
| The three-way split: dissolve, survive, disambiguate | `tests/test_dissolve.py`, `tests/test_disambiguate.py` | `monkeypatch.setattr(module, "NAME", value)`, once in each |
| ISP, DIP, and dependency injection without a framework | `tests/test_dip.py` | `mocker.create_autospec(..., instance=True)`, `assert_called_once_with` |
| Proving it works: pytest, pytest-mock, and mypy | `tests/test_doubles.py` | `create_autospec`, `Mock()`, `Mock(spec=...)`, `return_value`, `side_effect`, `assert_called_once_with`, `assert_not_called` |
| | `tests/test_environment.py` | `monkeypatch.context()` with `setenv` and `delenv` |
| | `tests/test_static.py` | `Mock`, `Mock(spec=...)`, `MagicMock(spec=...)` and `create_autospec` inside strings handed to mypy |
| Seams in Python: monkeypatch, injection, and duck typing | `tests/test_patching.py` | `mocker.patch` by string, with `create=True` and `autospec=`; `unittest.mock.patch` as a context manager; `monkeypatch.setattr` |
| | `tests/test_seams.py` | `monkeypatch.setattr` |
| | `tests/test_static.py` | `unittest.mock.patch` as a context manager and as a decorator, and `MagicMock`, inside strings handed to mypy; `AsyncMock` in an expected `reveal_type` string; `monkeypatch.setattr` |
| Dependency-breaking techniques for modern Python | `tests/conftest.py` | `monkeypatch.setattr`, taken with `request.getfixturevalue` |
| This appendix | six test files | the rest of the API, below |

## Making a double

"Proving it works: pytest, pytest-mock, and mypy" compares `Mock()`, `Mock(spec=...)` and `create_autospec(..., instance=True)` in one table, so this section starts after them. Each row adds one refusal or one behaviour.

| Form | What it adds | Test |
| --- | --- | --- |
| `Mock(spec_set=Target)` | Setting or getting an unknown name raises `AttributeError`; `spec` allows the assignment | `test_spec_set_refuses_setting_a_name_the_spec_lacks` |
| `seal(mock)` | After sealing, a name nobody configured raises `AttributeError` | `test_seal_stops_new_attributes_on_a_configured_mock` |
| `Mock()` and an assertion typo | `assret_called_once()` raises `AttributeError`; `unsafe=True` on that mock allows it | `test_an_assertion_typo_raises_instead_of_passing` |
| `MagicMock()` | Supports magic methods such as `len`; `Mock()` raises `TypeError` | `test_a_magic_mock_supports_the_magic_methods_a_mock_lacks` |
| `Mock(wraps=real)` | Calls pass through to the real object and return its result | `test_wraps_passes_calls_through_to_the_real_gateway` |

`spec_set` closes a gap that `spec` leaves. The test builds both from `CarrierGateway`, assigns `cancel` to the `spec` mock without complaint, and gets `Mock object has no attribute 'cancel'` from the `spec_set` mock on a set and on a get.

`seal` suits a double that is fully configured, where a forgotten attribute should fail the test and not return a new mock. In the test, `book` is configured and still answers after `mocker.seal(gateway)`; `quote` raises.

A misspelt assertion method such as `assret_called_once` is refused, and a switch turns the refusal off. The `unittest.mock` page says: "unsafe: By default, accessing any attribute whose name starts with assert, assret, asert, aseert or assrt will raise an AttributeError." The excerpt shows both sides:

```python
def test_an_assertion_typo_raises_instead_of_passing(mocker: MockerFixture) -> None:
    gateway = mocker.Mock()
    unchecked = mocker.Mock(unsafe=True)

    with pytest.raises(AttributeError, match="assret_called_once"):
        gateway.assret_called_once()

    unchecked.assret_called_once()
    assert unchecked.assret_called_once.call_count == 1
    with pytest.raises(AttributeError, match="assret_called_once"):
        unchecked.book.assret_called_once()
```

On Python 3.15.2 `unsafe=True` applies to the mock it's passed to, not to that mock's children: the test's last line shows `unchecked.book.assret_called_once()` still raising.

`wraps` suits a double that should record calls and still behave like the real gateway. Where the real object is yours to call, `mocker.spy`, below, does the same without a wrapper.

The `mocker` fixture re-exports these names from `unittest.mock`, and the pytest-mock usage page lists them: `Mock`, `MagicMock`, `PropertyMock`, `AsyncMock`, `ANY`, `DEFAULT`, `call`, `sentinel`, `mock_open` and `seal`. Of those, the tests in this appendix cover `Mock`, `MagicMock`, `AsyncMock` and `seal` through `mocker`, and `call` and `ANY` through `unittest.mock`. The usage page and the standard library page describe the others.

## Configuring and inspecting calls

A double is configured before the code runs and read back afterwards. Configuration comes first.

| Name | What it does | Test |
| --- | --- | --- |
| `side_effect` as an iterable | Returns each item in turn, raises an item that is an exception, then raises `StopIteration` | `test_side_effect_iterable_returns_each_value_then_raises_stop_iteration` |
| `side_effect` as a callable | Computes the return value from the call's arguments | `test_side_effect_callable_computes_the_return_value` |
| `side_effect` as an exception | Drives a branch the happy path never reaches | `test_side_effect_drives_the_timeout_branch` ([Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }})) |
| `mock_calls` and `call` | Every call, child calls included, in order | `test_mock_calls_records_calls_in_order_with_call_objects` |
| `called`, `call_count`, `call_args`, `call_args_list`, `ANY` | The last call, all calls, and a wildcard argument | `test_call_args_list_and_any_match_arguments` |
| `assert_any_call` | Some call matched, wherever it falls | `test_call_args_list_and_any_match_arguments` |
| `assert_has_calls` | A contiguous, ordered run of calls; `any_order=True` drops both conditions | `test_assert_has_calls_checks_a_contiguous_ordered_run` |
| `reset_mock` | Clears the calls; keeps `return_value` unless asked | `test_reset_mock_clears_calls_but_keeps_return_value` |

An iterable `side_effect` is the way to give one double a sequence of answers, such as a carrier that answers once and then times out. The test lists a quote and a `CarrierTimeoutError` instance: the first call returns the quote, the second raises the error, and a third raises `StopIteration`, because the list is exhausted.

`mock_calls` records the calls on a mock and on every child of it, as `call` objects, which is what lets one assertion fix an order. Two autospecs have separate lists, so the test attaches both to one `mocker.Mock()` manager with `attach_mock`. `book_cheapest` asks the carriers in sorted code order and then books the winner, and the manager's list shows exactly that:

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

The call objects also show a limit. This test asserts on calls and never on the reference `book_cheapest` returns, so it can't say whether the customer got the right answer. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) lists that habit among the tests that prove less than they seem, and the rule there is to assert the result first.

`assert_has_calls` is stricter than its name suggests, and looser than `mock_calls ==`. The `unittest.mock` page says "If any_order is false then the calls must be sequential." Extra calls before or after the run are allowed, and a gap isn't:

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

CN-1 then CN-3 skips CN-2, and CN-3 then CN-2 reverses the order, so both raise. `any_order=True` accepts both shapes, which makes it the weaker check. To say the calls were exactly these, compare `mock_calls` with a list.

`call_args_list` compares with `call(...)` objects, and `ANY` equals any argument, so a test can pin one argument and leave the other free. `reset_mock()` clears `call_count` and `mock_calls` and leaves a configured `return_value` in place; `reset_mock(return_value=True)` clears that too, and the configured value is gone on the next call. The standard library page presents `reset_mock` for a series of assertions that reuse one object.

## Patching with mocker

A patch replaces a name for the length of a test. It's the last choice in the order, so the rule that makes it work comes first. The `unittest.mock` page puts it this way: "The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined." The tests of [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) show it for `monkeypatch.setattr` (`test_patching_the_name_where_it_is_looked_up_replaces_the_carrier` and `test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier`) and for `unittest.mock.patch` (`test_unittest_mock_patch_follows_the_same_lookup_rule`), and that chapter owns the lesson. The `monkeypatch` fixture does the same job from pytest itself, and the chapter titled [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}) has its rows.

| Call | What it does | Test |
| --- | --- | --- |
| `mocker.patch("pkg.module.name")` | Replaces the name in the module the dotted string names | `test_autospec_refuses_a_call_with_the_wrong_signature` ([Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }})) |
| `mocker.patch(..., create=True)` | Allows a name the module doesn't have; without it the patch raises `AttributeError` | `test_patch_refuses_a_name_the_module_does_not_have` ([Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }})) |
| `mocker.patch(..., autospec=True)` | Refuses a call with the wrong signature, with a `TypeError` | `test_autospec_refuses_a_call_with_the_wrong_signature` ([Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }})) |
| `mocker.patch.object(Target, "name", autospec=True)` | Replaces one attribute and checks the signature | `test_patch_object_replaces_an_attribute_for_the_test` |
| `mocker.patch.dict(mapping, values)` | Adds values to a mapping, restored on stop | `test_patch_dict_restores_the_mapping_after_the_test` |
| `mocker.stop(patched)` | Undoes one patch | `test_mocker_stop_undoes_one_patch` |
| `mocker.stopall()` | Undoes every patch the fixture made | `test_patch_object_replaces_an_attribute_for_the_test`, `test_patch_dict_restores_the_mapping_after_the_test` |

`patch.object` with `autospec=True` on a class attribute keeps `self` in the signature, so the recorded call includes the instance: the test asserts `patched.assert_called_once_with(gateway, CN1, TEN)`, and a call with no arguments raises `TypeError` matching `missing a required argument`. After `mocker.stopall()` the real `quote` answers again.

`patch.dict` is the way to set an environment variable or a registry entry for one test. The test runs it against `os.environ` twice, with the key absent before and with the key present, and after `mocker.stopall()` the key is absent in the first case and back to its earlier value in the second. A patch is also undone without any call: pytest-mock's own warning text says "The mocker fixture automatically undoes mocking at the end of a test." That sentence is in the plugin's source for 3.17.0. Reach for `stop` and `stopall` when the test needs the real object back part-way through.

The same warning is raised when a `mocker` patch is used as a context manager. The usage page gives the reason: the plugin's purpose is "to make the use of context managers and function decorators for mocking unnecessary". On 3.17.0 only the context-manager form warns, because the plugin attaches the warning to the mock's `__enter__`. The repository's `filterwarnings = ["error"]` turns that warning into an exception, and the test expects it:

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

With the filter lowered to `default` for one run, the same test fails with `DID NOT RAISE PytestMockWarning` and the run reports one warning. The usage page names `mocker.patch.context_manager` for the case where the mocked object is a context manager.

Outside pytest there's no fixture to undo anything, so `unittest.mock.patch` is used as a decorator or a context manager. The standard library page says of `patch.object()` that it "can be used as a decorator, class decorator or a context manager." The static test of [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) shows how mypy types a patch used that way, and that a decorator-injected argument needs an annotation (`test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement`).

## Spies and stubs

A spy and a stub are the two doubles that avoid a configured answer. A spy runs the real code and records it. A stub, in pytest-mock's sense, is a callable that records how it was called, for a callback the code under test is given.

The usage page describes a spy this way: "The mocker.spy object acts exactly like the original method in all cases, except the spy also tracks function/method calls, return values and exceptions raised." The attributes that hold the records are `spy_return`, `spy_return_list` and `spy_exception`:

| Name | What it holds | Test |
| --- | --- | --- |
| `spy_return` | The last returned value | `test_spy_keeps_the_real_behaviour_and_records_returns` |
| `spy_return_list` | Every returned value | `test_spy_keeps_the_real_behaviour_and_records_returns` |
| `spy_exception` | The exception from the last call that raised | `test_spy_records_the_exception_it_let_through` |
| `mocker.stub(name=...)` | A recording callable | `test_stub_records_a_callback` |

The spy test keeps the real quote: 10 kg at 0.45 is `Decimal("4.50")`, the call went through, and `spy_return_list` is a list of that one quote. The exception test calls `quote` above the weight limit, so the real gateway raises `CarrierTimeoutError`; `spy_exception` is that exact object and `spy_return` is `None`.

A stub is the double for `book_cheapest`'s `notify` parameter, a callback, so there's nothing to configure: `mocker.stub(name="notify")` is passed in and `notify.assert_called_once_with("FASTLINE:CN-1")` checks the reference it received. The tie, timeout and all-timed-out tests in `tests/test_booking.py` pass stubs the same way, and the last of them checks with `assert_not_called` that no reference was sent.

`mocker.resetall()` resets some of these doubles and leaves others alone. The usage page says it "calls reset_mock() on the mocks created through mocker so far: those from mocker.patch (and its variants), mocker.spy and mocker.create_autospec", and that "Mocks created with mocker.stub(), mocker.async_stub() or mocker.Mock() and the other aliases are not tracked, so they are not reset." The test makes one of each and calls each once before it resets:

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

The page adds "By default only the recorded calls are reset." A stub's count survives, so a test that reuses one after `resetall()` has to reset it with `stub.reset_mock()`.

## Async doubles

A double for an `async def` returns something awaitable, and its await is recorded apart from its call. `create_autospec` of the async function `confirm` does both.

```python
def test_autospec_of_an_async_function_records_the_await(mocker: MockerFixture) -> None:
    confirm_double: MagicMock = mocker.create_autospec(confirm)
    confirm_double.return_value = "CONFIRMED:FASTLINE:CN-1"

    result = asyncio.run(confirm_double("FASTLINE:CN-1"))

    assert result == "CONFIRMED:FASTLINE:CN-1"
    confirm_double.assert_awaited_once_with("FASTLINE:CN-1")
```

`test_async_mock_return_value_is_awaited` shows `mocker.AsyncMock(return_value=...)` awaited through a plain `asyncio.run` and checked with `assert_awaited_once_with`. The usage page warns about the shortcut: "Do not use called or call_count alone to check that an asynchronous callback was awaited."

## What mypy sees

Annotate the fixture as `MockerFixture`, and mypy gives each `mocker` call a type. `test_mypy_types_mocker_objects_as_mocks` reveals five of them under `mypy --strict --warn-unreachable`:

| Call | `reveal_type` |
| --- | --- |
| `mocker.patch("os.getcwd")` | `unittest.mock.MagicMock \| unittest.mock.AsyncMock \| unittest.mock.NonCallableMagicMock` |
| `mocker.patch.object(Gateway, "book")` | the same union |
| `mocker.spy(Gateway(), "book")` | `pytest_mock.plugin.SpyType` |
| `mocker.stub()` | `unittest.mock.MagicMock` |
| `mocker.Mock()` | `Any` |

`patch` and `patch.object` return a union of three mock classes, `spy` returns `SpyType`, and `mocker.Mock()` is `Any`, so mypy accepts every use of it.

What's left for mypy to check is the code on either side of the double. `test_mypy_accepts_a_stub_where_a_callback_is_expected` passes `mocker.stub()` as the `notify` argument of `book_cheapest`, declared as `Notify`, and mypy reports nothing. It passes a hand-written `def notify(reference: int) -> None` in the same position and gets exactly one error code, `arg-type`, with `Callable[[str], None]` in the message. A real callback is held to the signature; a stub isn't.

## Running the reference tests

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/43-appendix-c-mocking
uv run pytest -v
uv run mypy --strict src tests
```

The example has 26 test functions and 32 cases, and the pytest summary line ends `32 passed`. The context-manager test needs the repository's `filterwarnings = ["error"]`, which pytest finds from the example directory.

## For deeper coverage

The standard library's [`unittest.mock`](https://docs.python.org/3.15/library/unittest.mock.html) page is the reference for every name here, and its companion [`unittest.mock` getting started](https://docs.python.org/3.15/library/unittest.mock-examples.html) works through the API by example. The pytest-mock [usage page](https://pytest-mock.readthedocs.io/en/stable/usage.html) covers the `mocker` fixture, including `mocker.patch.multiple`, `mocker.async_stub` and the fixtures of other scopes, which the tests here don't use. Typeshed's [`unittest/mock.pyi`](https://github.com/python/typeshed/blob/d03a581a8ebf525cba072b3e24e97f64825505b9/stdlib/unittest/mock.pyi) holds the comment about `Any` that explains what mypy does with a mock.

Martin Fowler's article [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) sets state verification against the behaviour verification that mocks make possible, which is the choice behind the order of preference. Gerard Meszaros's *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007) supplies the names dummy, fake, stub, spy and mock, and is on the [bibliography page]({{ '/bibliography/' | relative_url }}). For the checks a double should make and the patching rule, read "Proving it works: pytest, pytest-mock, and mypy" and "Seams in Python: monkeypatch, injection, and duck typing".
