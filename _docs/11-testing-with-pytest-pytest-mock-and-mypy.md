---
title: "Proving it works: pytest, pytest-mock, and mypy"
order: 11
layout: tutorial
sectionid: docs
part: "python-substrate"
description: "A test is evidence for one named claim, and it counts once it has been seen to fail. Fixtures supply dependencies by name, a mock checks less than a fake, create_autospec checks call shapes, and mypy checks the tests too."
---

## Learning objectives

By the end of this chapter you can:

- Name a test after the claim it witnesses, and say what it takes for that test to count as evidence.
- Write fixtures that supply dependencies by parameter name, build fakes with a factory fixture, and clean up with `yield`.
- Say what a fake, a plain `Mock`, `Mock(spec=...)` and `create_autospec` each check, and what mypy checks in each.
- Make time and the environment deterministic by injecting the clock and restoring `os.environ` inside `monkeypatch.context()`.
- Use `assert_type` and typed `# type: ignore[code]` comments as static tests, and read a mypy run over `tests/` as part of the suite.
- Configure pytest so that an unknown marker, a surprising pass or a deprecation fails the run.

## Why this matters

Three suites that look healthy and prove little. The first asserts `loser.bok.assert_not_called()`, with `bok` a typo for `book`. Against a plain `Mock` the assertion passes, because every attribute of a `Mock` exists and has never been called. The second quotes a rate quote whose expiry is computed from the wall clock. It passes today and fails at midnight, or it passes because the assertion was loosened until nothing could fail it. The third is green after someone deletes the check it was written to guard, and nobody notices, because nobody ever saw the test fail.

The rating engine in this chapter asks carriers for a price, skips the ones that time out, and books the cheapest. It's small enough to test completely, and the tests are the subject. They show how pytest, pytest-mock and mypy each contribute a different kind of evidence, and where each one is silent.

{% include excalidraw.html name="11-testing-with-pytest-pytest-mock-and-mypy" caption="Figure 11.1: How a claim becomes evidence. A claim gets a witness test named after it, a negative fixture shows the failure it rules out, the test is seen failing when its check is deleted, and only a fresh, scrubbed run is quoted." %}

Read the figure from the top. The accent box holds the claim, "the engine books only the winner", with an arrow down to the witness test, `test_book_best_books_only_the_winner`. The negative fixture points into the witness, and below the witness sit "seen failing" and the quoted, scrubbed run.

## A claim, a witness, and a test you've seen fail

The examples in this book follow one method. A test is named as a claim: `test_book_best_books_only_the_winner` says what the engine does, so a failure reads as a broken sentence. Each claim has a witness, the test that asserts it. A negative fixture is a wrong object, written to be wrong, kept in `tests/` with an underscore prefix and a docstring that starts "Negative fixture:", which shows the failure the claim rules out. A check that was never seen to fail is a guess, so each check is deleted in a scratch copy, and the experiments record which named test failed. Every experiment at the end of a chapter changes one thing and quotes the result.

## Fixtures and parametrize

pytest passes a test what it names. A test that declares a parameter called `consignment` gets the fixture of that name, and a fixture defined in `conftest.py` is visible to every test file in its directory without an import. Brian Okken's *Python Testing with pytest*, second edition (Pragmatic Bookshelf, 2022), is the book-length treatment of fixtures, parametrization and configuration, and the [fixtures how-to](https://docs.pytest.org/en/stable/how-to/fixtures.html) is the primary source for what follows. The chapter titled [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}) lists the rest.

The example keeps three simple fixtures, `consignment`, `fixed_now` and `make_fake`. The last is a factory fixture: it returns a function, so a test builds as many fakes as it needs, each with its own carrier code and price. `FakeGateway` is a hand-written `CarrierGateway`, and it records the consignments it was asked to book. That record is what `test_book_best_books_the_winner_and_returns_its_reference` asserts on: the winner holds one booking and the loser holds none.

A fixture that needs cleanup uses `yield`. Everything before the `yield` is setup, and everything after it is teardown:

```python
@pytest.fixture
def quote_log(tmp_path: Path) -> Iterator[Path]:
    """A log file for the test; after the yield, the teardown appends a line and prints its name."""
    log = tmp_path / "quotes.log"
    log.write_text("setup\n", encoding="utf-8")
    yield log
    with log.open("a", encoding="utf-8") as handle:
        handle.write("teardown\n")
    sys.stdout.write(f"quote_log teardown: {log.name}\n")
```

The fixtures how-to describes teardown as running after the test finishes, in the reverse of setup order. Experiment three at the end makes a test fail and shows the line this teardown prints. `test_quote_validity_comes_from_the_injected_clock` requests `quote_log` and appends a line to it.

`pytest.param` gives a parametrized case a name. `test_best_quote_picks_the_cheapest_carrier` takes three cases such as `pytest.param("10.00", "12.00", "fastline", id="fastline-cheaper")`, and the report prints `[fastline-cheaper]` after the test name, not a tuple of strings. A case named after the claim it carries is easier to find when it fails.

## Fakes and mocks: what each one checks

Gerard Meszaros's *xUnit Test Patterns* (Addison-Wesley, 2007) supplies the vocabulary this chapter uses: *test double* for any stand-in for a collaborator, and the names dummy, fake, stub, spy and mock for the kinds. A fake is a working, simplified implementation. A mock, in his sense, is an object that checks the calls it receives. The chapter titled [xUnit test patterns (Meszaros)]({{ '/docs/44-appendix-d-xunit-test-patterns/' | relative_url }}) covers the taxonomy. This chapter needs only the names.

Python's `unittest.mock` blurs the lines, because one `Mock` object stands in for all of them. Each kind of double refuses something different. Four doubles, each handed a gateway name that doesn't exist and a call with the wrong shape:

| Double | Unknown name, `bok` | Call with no consignment | mypy |
| --- | --- | --- | --- |
| `FakeGateway` | `AttributeError`; mypy `[attr-defined]` | `TypeError`; mypy `[call-arg]` | checked: a missing member is an error |
| `Mock()` | accepted | accepted | accepted |
| `Mock(spec=CarrierGateway)` | `AttributeError` | accepted | accepted |
| `create_autospec(CarrierGateway, instance=True)` | `AttributeError` | `TypeError` | accepted |

The `FakeGateway` row is witnessed by `test_a_fake_rejects_unknown_names_and_wrong_signatures`, whose two `# type: ignore` comments name the codes mypy reports. In this example the plain `Mock` row, built inline, plays the part of the negative fixture for the engine's claim; it is not an underscore-prefixed object. `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method` builds it:

```python
def test_a_plain_mock_passes_an_assertion_on_a_misspelled_method(
    mocker: MockerFixture, consignment: Consignment
) -> None:
    loser = mocker.Mock()
    loser.book(consignment)

    loser.bok.assert_not_called()

    with pytest.raises(AssertionError, match="Expected 'book' to not have been called"):
        loser.book.assert_not_called()
```

The consignment was booked, and `loser.bok.assert_not_called()` passes anyway, because `bok` is a fresh attribute that nobody called.

`Mock(spec=CarrierGateway)` closes the first gap and not the second. `test_spec_rejects_unknown_names_but_not_wrong_signatures` shows `gateway.bok` raising `AttributeError` with `has no attribute 'bok'`, and `gateway.book()` with no argument going through and being recorded. Only `create_autospec` copies the signatures, so the witness for the engine's claim uses it:

```python
def test_book_best_books_only_the_winner(
    mocker: MockerFixture, consignment: Consignment, fixed_now: datetime
) -> None:
    winner = mocker.create_autospec(CarrierGateway, instance=True)
    loser = mocker.create_autospec(CarrierGateway, instance=True)
    winner.quote.return_value = CarrierQuote("airco", _usd("10.00"))
    loser.quote.return_value = CarrierQuote("fastline", _usd("12.00"))
    winner.book.return_value = "AIRCO:CN-00000001"
    engine = RateEngine(
        {"airco": winner, "fastline": loser}, clock=lambda: fixed_now, validity=timedelta(hours=1)
    )

    assert engine.book_best(consignment) == "AIRCO:CN-00000001"

    winner.book.assert_called_once_with(consignment)
    loser.book.assert_not_called()
```

A misspelled `loser.bok` would raise here, so the assertion on `loser.book` is the one that can fail. `test_autospec_rejects_names_and_signatures` checks both refusals:

```python
def test_autospec_rejects_names_and_signatures(mocker: MockerFixture) -> None:
    gateway = mocker.create_autospec(CarrierGateway, instance=True)

    with pytest.raises(AttributeError, match="has no attribute 'bok'"):
        _ = gateway.bok

    with pytest.raises(TypeError, match="missing a required argument: 'consignment'"):
        gateway.book()
```

`side_effect` is how a double drives a branch the happy path never reaches. `test_side_effect_drives_the_timeout_branch` gives one autospec a `CarrierTimeoutError` to raise from `quote`, and asserts that the engine skips that carrier and reports it in `skipped`. The first demonstration of autospec, with an autospec of the wrong Protocol, is in the chapter titled [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}). The chapter titled [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}) lists the rest of the mock API, and the standard library's [autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing) section is the source for what `create_autospec` copies.

mypy accepts every one of the mocks where a `CarrierGateway` is expected. `test_mypy_accepts_every_mock_where_a_gateway_is_expected` passes `Mock()`, `Mock(spec=...)`, `MagicMock(spec=...)` and an autospec to a function that takes a `CarrierGateway`, and each run exits 0 with empty output. The reason is in typeshed's [`unittest/mock.pyi`](https://github.com/python/typeshed/blob/main/stdlib/unittest/mock.pyi), where `NonCallableMock`, the base of `Mock` and `MagicMock`, is declared as `class NonCallableMock(Base, Any)`, under this comment:

> We subclass with "Any" because mocks are explicitly designed to stand in for other types, something that can't be expressed with our static type system.

A mock is assignable to every type, so mypy has nothing to check at the call site. A hand-written fake gets the opposite treatment. `test_mypy_checks_a_hand_written_fake` runs a class that has `quote` and lacks `book`:

<!-- fmt:off -->
```python
class QuoteOnly:
    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        raise NotImplementedError
```
<!-- fmt:on -->

Put in a dictionary of gateways, the test's own `_run` helper gets a bare error:

```text
<string>:19: error: Dict entry 0 has incompatible type "str": "QuoteOnly"; expected "str": "CarrierGateway"  [dict-item]
```

Assigned to a variable annotated `CarrierGateway`, the same class gets the explanation:

```text
<string>:17: error: Incompatible types in assignment (expression has type "QuoteOnly", variable has type "CarrierGateway")  [assignment]
<string>:17: note: "QuoteOnly" is missing following "CarrierGateway" protocol member:
<string>:17: note:     book
```

mypy rejects the fake in both, and names the missing member only in the second. The practical rule: a fake earns a static check and an autospec earns a runtime check, and a plain mock earns neither.

## Time, environment, and other process state

`RateEngine` takes `clock: Callable[[], datetime]` and a `validity` as constructor arguments. A test that passes `clock=lambda: fixed_now` and asserts `quote.valid_until == fixed_now + timedelta(minutes=45)` has nothing to patch and nothing to wait for. The fixed instant is a fixture, so two tests agree on it.

A tie between two carriers is the other source of drift. The engine asks carriers in sorted code order and picks the minimum by `(amount, carrier)`, so the winner never depends on how the mapping happens to be ordered. `test_carriers_are_asked_in_code_order` witnesses the order, and `test_a_tie_is_broken_by_the_carrier_code_in_the_quote` uses mapping keys that are account aliases rather than carrier codes, so that only the code inside the quote can break the tie.

The environment is process state that can't be injected away entirely, because `validity_from_env` defaults to `os.environ`. Every case but one passes an `environ` mapping, which needs no patching. The one test that touches the real environment does it inside a context:

```python
def test_validity_reads_the_environment_and_the_context_restores_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = os.environ.get(VALIDITY_VARIABLE)

    with monkeypatch.context() as patch:
        patch.setenv(VALIDITY_VARIABLE, "45")
        assert validity_from_env() == timedelta(minutes=45)
        patch.delenv(VALIDITY_VARIABLE)
        assert validity_from_env() == timedelta(minutes=30)
        patch.setenv(VALIDITY_VARIABLE, "7")

    assert os.environ.get(VALIDITY_VARIABLE) == before
```

The test captures the value before, whatever the shell left there, and compares after the `with` block. It doesn't assume the variable is unset. The [monkeypatch how-to](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) documents `context()`. When the fix is to patch a module's name rather than the environment, that's a seam, and the chapter titled [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) compares the options.

## mypy as a test

`uv run mypy --strict src tests` checks the tests as well as the code. That puts two tools in the suite that pytest doesn't have.

`assert_type` from `typing` is a static assertion. `test_quote_validity_comes_from_the_injected_clock` includes `assert_type(quote.total, Money)`, and the mypy run fails if `total` stops being a `Money`. In a scratch copy, changing that line to `assert_type(quote.total, str)` made the pytest run pass (9 tests in `test_engine.py`) and made mypy fail:

```text
tests/test_engine.py:75: error: Expression is of type "Money", not "str"  [assert-type]
```

At runtime `assert_type` returns its first argument and does nothing else. `test_assert_type_is_static_only` shows both halves. Through the test's `_run`, the snippet `assert_type(1, str)` exits with status 1:

```text
<string>:4: error: Expression is of type "Literal[1]", not "str"  [assert-type]
```

The test then calls `assert_type(1, str)` itself and asserts that it returns `1`, with `# type: ignore[assert-type]` on that line. The ignore names its code, and `--strict` includes `warn_unused_ignores`. If mypy stopped reporting the error, the comment would become the error. In the scratch copy, replacing the call on that line with `1 == 1` gave:

```text
tests/test_static.py:142: error: Unused "type: ignore" comment  [unused-ignore]
```

So the ignore is a regression test: it holds for as long as mypy reports the thing the test is about.

The `_run` helper in `test_static.py` is the same idea turned into a function. It writes a `mypy.ini`, calls `mypy.api.run` with `--strict` and no cache, and returns the output and exit status. Each test asserts the exit status and the exact set of error codes, then either an empty output or the message text it quotes: one substring for the dictionary entry and for `assert_type`, three for the assignment. A snippet is checked against the interpreter that runs the test, so the checks are about the Python the suite uses.

## Configuration that refuses silence

Three lines of the workspace's root `pyproject.toml` turn quiet failures into loud ones, and the [pytest reference](https://docs.pytest.org/en/stable/reference/reference.html) documents each:

- `--strict-markers` raises an error for a marker that isn't registered. `--strict-config` does the same for a configuration warning.
- `xfail_strict = true` makes a test marked `xfail` that passes fail the run. In pytest 9 the option is named `strict_xfail`, and `xfail_strict` remains an alias.
- `filterwarnings = ["error"]` turns every warning into an exception. The [capture warnings how-to](https://docs.pytest.org/en/stable/how-to/capture-warnings.html) shows the default, a summary at the end of the run that is easy to scroll past.

Without `error`, a Python 3.15 deprecation scrolls past. A Protocol that inherits a `@runtime_checkable` Protocol without its own decorator gets a `DeprecationWarning` on `isinstance` and will raise `TypeError` in Python 3.20. With the filter, that is a failing test today. The experiments reproduce all but `--strict-config`.

## When a test proves less than it seems

Four habits make a green run mean less than it appears to.

- **Asserting that a mock was called, not what happened.** `assert_called_once_with` on a gateway records that the engine asked. It doesn't say whether the customer got the right reference. `test_book_best_books_only_the_winner` also asserts the return value, `"AIRCO:CN-00000001"`, before it asserts on the calls.
- **A mock where a fake would be checked.** A plain `Mock` is assignable everywhere. A `FakeGateway` is held to the Protocol by mypy.
- **A test never seen failing.** If its check can be deleted with the suite still green, the test measures nothing.
- **One parametrize case per line of the implementation.** The cases should be the claims. Three named cases for the cheapest carrier say more than ten that restate the sort.

<blockquote class="ai-sidebar" markdown="1">

**Reviewing assistant-written tests.** An assistant may use a plain `Mock` for a typed collaborator, assert only that a method was called, patch a module global, or read the clock inside the code under test. Paste a prompt that states the form:

> Name each test after the claim it witnesses. Build doubles for `CarrierGateway` with `mocker.create_autospec(CarrierGateway, instance=True)` or a hand-written fake, never a plain `Mock`. Assert the returned reference before the calls. Inject the clock and the environment mapping instead of patching, and use `monkeypatch.context()` for the one real-environment test. Keep `--strict-markers`, `xfail_strict` and `filterwarnings = ["error"]`.

If a test has never been seen failing, delete its check in a scratch copy and confirm it fails.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then from the example directory:

```bash
uv run pytest -v
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 34 items

tests/test_domain.py::test_weight_rejects_a_mass_that_is_not_positive_and_finite[zero] PASSED [  2%]
tests/test_domain.py::test_weight_rejects_a_mass_that_is_not_positive_and_finite[negative] PASSED [  5%]
tests/test_domain.py::test_weight_rejects_a_mass_that_is_not_positive_and_finite[nan] PASSED [  8%]
tests/test_domain.py::test_weight_rejects_a_mass_that_is_not_positive_and_finite[infinite] PASSED [ 11%]
tests/test_domain.py::test_money_orders_by_amount_within_one_currency PASSED [ 14%]
tests/test_domain.py::test_money_refuses_to_order_across_currencies PASSED [ 17%]
tests/test_doubles.py::test_book_best_books_only_the_winner PASSED       [ 20%]
tests/test_doubles.py::test_a_plain_mock_passes_an_assertion_on_a_misspelled_method PASSED [ 23%]
tests/test_doubles.py::test_spec_rejects_unknown_names_but_not_wrong_signatures PASSED [ 26%]
tests/test_doubles.py::test_autospec_rejects_names_and_signatures PASSED [ 29%]
tests/test_doubles.py::test_a_fake_rejects_unknown_names_and_wrong_signatures PASSED [ 32%]
tests/test_doubles.py::test_side_effect_drives_the_timeout_branch PASSED [ 35%]
tests/test_engine.py::test_best_quote_picks_the_cheapest_carrier[fastline-cheaper] PASSED [ 38%]
tests/test_engine.py::test_best_quote_picks_the_cheapest_carrier[airco-cheaper] PASSED [ 41%]
tests/test_engine.py::test_best_quote_picks_the_cheapest_carrier[equal-amounts] PASSED [ 44%]
tests/test_engine.py::test_a_tie_is_broken_by_the_carrier_code_in_the_quote PASSED [ 47%]
tests/test_engine.py::test_quote_validity_comes_from_the_injected_clock PASSED [ 50%]
tests/test_engine.py::test_a_timed_out_carrier_is_skipped PASSED         [ 52%]
tests/test_engine.py::test_carriers_are_asked_in_code_order PASSED       [ 55%]
tests/test_engine.py::test_every_carrier_timing_out_is_a_rating_error PASSED [ 58%]
tests/test_engine.py::test_book_best_books_the_winner_and_returns_its_reference PASSED [ 61%]
tests/test_environment.py::test_validity_reads_the_environment_and_the_context_restores_it PASSED [ 64%]
tests/test_environment.py::test_validity_defaults_to_thirty_minutes_when_unset PASSED [ 67%]
tests/test_environment.py::test_validity_accepts_a_positive_int PASSED   [ 70%]
tests/test_environment.py::test_validity_rejects_a_value_that_is_not_a_positive_int[zero] PASSED [ 73%]
tests/test_environment.py::test_validity_rejects_a_value_that_is_not_a_positive_int[negative] PASSED [ 76%]
tests/test_environment.py::test_validity_rejects_a_value_that_is_not_a_positive_int[text] PASSED [ 79%]
tests/test_static.py::test_mypy_accepts_every_mock_where_a_gateway_is_expected[Mock] PASSED [ 82%]
tests/test_static.py::test_mypy_accepts_every_mock_where_a_gateway_is_expected[Mock-spec] PASSED [ 85%]
tests/test_static.py::test_mypy_accepts_every_mock_where_a_gateway_is_expected[MagicMock-spec] PASSED [ 88%]
tests/test_static.py::test_mypy_accepts_every_mock_where_a_gateway_is_expected[autospec] PASSED [ 91%]
tests/test_static.py::test_mypy_checks_a_hand_written_fake[dict-entry] PASSED [ 94%]
tests/test_static.py::test_mypy_checks_a_hand_written_fake[assignment] PASSED [ 97%]
tests/test_static.py::test_assert_type_is_static_only PASSED             [100%]

============================== 34 passed in 4.13s ==============================
```

```text
Success: no issues found in 10 source files
```

The suite has 23 test functions and 34 cases. The experiments run in a scratch copy, and each changes one thing. Experiments one, two and six quote the output of `grep -E '^(>|E  |FAILED|[0-9]+ (passed|failed))'`; the other blocks drop pytest's banners and source lines.

**Experiment one: book every carrier.** In `RateEngine.book_best`, replace the last line so that it books every gateway with `gateway.book(consignment)` in a dictionary comprehension over `self._gateways.items()` and then returns the entry for the winner's code.

The engine still returns the winner's reference, so the return-value assertion passes. Two tests fail and 32 pass:

```text
>       loser.book.assert_not_called()
E       AssertionError: Expected 'book' to not have been called. Called 1 times.
E       Calls: [call(Consignment(id='CN-00000001', weight=Weight(kilograms=100.0), destination='SGSIN'))].
>       assert loser.booked == []
E       AssertionError: assert [Consignment(...tion='SGSIN')] == []
E         
E         Left contains one more item: Consignment(id='CN-00000001', weight=Weight(kilograms=100.0), destination='SGSIN')
E         Use -v to get more diff
FAILED tests/test_doubles.py::test_book_best_books_only_the_winner - Assertio...
FAILED tests/test_engine.py::test_book_best_books_the_winner_and_returns_its_reference
2 failed, 32 passed in 4.17s
```

The witness fails on `loser.book.assert_not_called()`, and the fake-based test fails on the loser's record. The member's mypy run still says `Success: no issues found in 10 source files`, since no type changed. Restore the line.

**Experiment two: weaken the autospec.** In `test_autospec_rejects_names_and_signatures`, replace `mocker.create_autospec(CarrierGateway, instance=True)` with `mocker.Mock(spec=CarrierGateway)`:

```text
>       with pytest.raises(TypeError, match="missing a required argument: 'consignment'"):
E       Failed: DID NOT RAISE TypeError
FAILED tests/test_doubles.py::test_autospec_rejects_names_and_signatures - Fa...
1 failed, 33 passed in 4.12s
```

The name check still passes, since `spec` rejects `bok`, and the signature check no longer has anything to raise. Restore the line.

**Experiment three: fail a test that uses a `yield` fixture.** Add `assert quote.carrier == "airco"` to `test_quote_validity_comes_from_the_injected_clock`, where the only carrier is `fastline`, and run it alone with `-k test_quote_validity_comes_from_the_injected_clock`, adding `-s` so the fixture's output isn't captured:

```text
tests/test_engine.py Fquote_log teardown: quotes.log
>       assert quote.carrier == "airco"
E       AssertionError: assert 'fastline' == 'airco'
E         
E         - airco
E         + fastline
tests/test_engine.py:79: AssertionError
FAILED tests/test_engine.py::test_quote_validity_comes_from_the_injected_clock
======================= 1 failed, 33 deselected in 0.05s =======================
```

The `F` is the failing test, and the teardown line follows it before pytest prints the failure report. In this run the code after `yield` ran, and printed its line, for the failed test. Remove the line.

**Experiment four: an unregistered marker.** Add `@pytest.mark.slow` above `test_money_orders_by_amount_within_one_currency`. With `--strict-markers` from the root configuration, `uv run pytest -q tests/test_domain.py` fails at collection and no test runs:

```text
'slow' not found in `markers` configuration option
ERROR tests/test_domain.py - Failed: 'slow' not found in `markers` configurat...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.05s
```

With `-o addopts="--import-mode=importlib" -o filterwarnings=default`, which drops the strict option and the warning filter, the same file passes with a `PytestUnknownMarkWarning` and the line `6 passed, 1 warning in 0.01s`. A typo in a marker name would otherwise deselect nothing and say so only in a summary.

**Experiment five: a test that passes but is marked `xfail`.** Add `@pytest.mark.xfail(reason="known gap")` above the same test. With `xfail_strict = true`, `uv run pytest -q tests/test_domain.py` gives:

```text
[XPASS(strict)] known gap
FAILED tests/test_domain.py::test_money_orders_by_amount_within_one_currency
1 failed, 5 passed in 0.01s
```

Running again with `-o xfail_strict=false` gives `5 passed, 1 xpassed in 0.01s`, and the exit status is 0. A known gap that has quietly been fixed no longer goes unnoticed.

**Experiment six: a deprecation.** Add a test file with a runtime-checkable Protocol, a second Protocol, `Narrow`, that inherits from it without its own `@runtime_checkable`, and one assertion, `assert isinstance(object(), Narrow) is False`. With `filterwarnings = ["error"]` in force, `uv run pytest -q tests/test_scratch_warning.py` filtered through `grep -E '^(>|E  |FAILED|[0-9]+ (passed|failed))'` gives:

```text
>       assert isinstance(object(), Narrow) is False
>           warnings.warn(depr_message, category=DeprecationWarning, stacklevel=2)
E           DeprecationWarning: <class 'examples.11-testing-with-pytest-pytest-mock-and-mypy.tests.test_scratch_warning.Narrow'> isn't explicitly decorated with @runtime_checkable but it is used in issubclass() or isinstance(). Instance and class checks can only be used with @runtime_checkable protocols. This will raise a TypeError in Python 3.20.
FAILED tests/test_scratch_warning.py::test_isinstance_against_a_protocol_that_inherits_runtime_checkable
1 failed in 0.04s
```

With `-o filterwarnings=default`, the same test prints `1 passed, 1 warning in 0.01s`. The warning exists in both runs, and only the configured one stops the suite.

## What you can do now

- Name a test after its claim and show it counts: `test_book_best_books_only_the_winner` fails when experiment one books every carrier.
- Supply dependencies by name: the `quote_log` fixture prints its teardown line after a failing test (experiment three), and `make_fake` builds each `FakeGateway`.
- Say what each double checks: the table of four doubles, and `test_mypy_accepts_every_mock_where_a_gateway_is_expected` for the mypy column.
- Make time and the environment deterministic: the injected clock, and the one test that restores `os.environ` inside `monkeypatch.context()`.
- Use static tests: `assert_type(quote.total, Money)` and the unused-ignore regression in `test_assert_type_is_static_only`.
- Make silence loud: `--strict-markers`, `xfail_strict` and `filterwarnings = ["error"]`, with experiments four to six.

## For deeper coverage

The pytest documentation covers the tools in this chapter: [fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), [parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html), [monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html), [capturing warnings](https://docs.pytest.org/en/stable/how-to/capture-warnings.html) and the [reference](https://docs.pytest.org/en/stable/reference/reference.html) for configuration options. The [pytest-mock documentation](https://pytest-mock.readthedocs.io/en/stable/) describes the `mocker` fixture, and the standard library's [autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing) section explains what `create_autospec` copies. Typeshed's [`unittest/mock.pyi`](https://github.com/python/typeshed/blob/main/stdlib/unittest/mock.pyi) holds the comment quoted above.

Gerard Meszaros's *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007) is the source for the double names and the long catalogue behind them. Martin Fowler's article [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) argues the difference between asserting on state and asserting on interactions, which is the second habit in the list of tests that prove less than they seem. Brian Okken's *Python Testing with pytest*, second edition (Pragmatic Bookshelf, 2022), covers fixtures, parametrization and configuration at book length, and Brett Slatkin's *Effective Python*, third edition, has short rules on testing and typing. Both books are on the [bibliography page]({{ '/bibliography/' | relative_url }}).
