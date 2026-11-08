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
- Use `assert_type` and typed `# type: ignore[code]` comments as static tests, and read a mypy run over `tests/` as part of the run.
- Configure pytest so that an unknown marker, a surprising pass or a deprecation fails the run.

## Why this matters

Three suites look healthy and prove little:

- One asserts `loser.bok.assert_not_called()`, with `bok` a typo for `book`. Against a plain `Mock` it passes, because every attribute of a `Mock` exists and has never been called.
- One checks a rate quote whose expiry comes from the wall clock. It passes today and fails at midnight, or it passes because the assertion was loosened until nothing could fail it.
- One stays green after someone deletes the check it guards, and nobody notices, because nobody ever saw it fail.

The rating engine here asks carriers for a price, skips the ones that time out, and books the cheapest. It's small enough to test completely. pytest, pytest-mock and mypy each contribute a different kind of evidence about it, and each is silent somewhere.

{% include excalidraw.html name="11-testing-with-pytest-pytest-mock-and-mypy" described="true" caption="Figure 11.1: How a claim becomes evidence. A claim gets a witness test named after it, a negative fixture shows the failure it rules out, the test is seen failing when its check is deleted, and only a fresh, scrubbed run is quoted." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-11-testing-with-pytest-pytest-mock-and-mypy" markdown="1">
The accent box at the top holds the claim, "the engine books only the winner", with an arrow down to the witness test named after it. The negative fixture points into the witness, and below the witness sit "seen failing" and the quoted, scrubbed run.
</div>
</details>

The figure traces one claim from its statement to a quoted run.

## A claim, a witness, and a test you've seen fail

A test is named as a claim, so a failure reads as a broken sentence: "book best books only the winner". The test that asserts a claim is its witness. A negative fixture is a wrong object, written to be wrong, kept in `tests/` with an underscore prefix and a docstring that starts "Negative fixture:", and it shows the failure the claim rules out. A check that was never seen to fail is a guess, so delete each check in a scratch copy and confirm which test fails.

## Fixtures and parametrize

pytest passes a test what it names. A parameter called `consignment` gets the fixture of that name, and a fixture in `conftest.py` is visible to every test file in its directory without an import. Brian Okken's *Python Testing with pytest*, second edition (Pragmatic Bookshelf, 2022), covers fixtures, parametrization and configuration at book length, and the [fixtures how-to](https://docs.pytest.org/en/stable/how-to/fixtures.html) is the primary source. [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}) lists the rest.

Three fixtures do most of the work: `consignment`, `fixed_now` and `make_fake`. The last is a factory fixture: it returns a function, so a test builds as many fakes as it needs, each with its own carrier code and price. `FakeGateway` is a hand-written `CarrierGateway` that records the consignments it was asked to book, so after `book_best` the winner holds one booking and the loser none.

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

Teardown runs after a test finishes, in the reverse of setup order, and it runs when that test fails too.

`pytest.param` gives a parametrized case a name. With `pytest.param("10.00", "12.00", "fastline", id="fastline-cheaper")` the report prints `[fastline-cheaper]` after the function name, not a tuple of strings. A case named after its claim is easier to find when it fails.

## Fakes and mocks: what each one checks

Gerard Meszaros's *xUnit Test Patterns* (Addison-Wesley, 2007) supplies the vocabulary: *test double* for any stand-in for a collaborator, and dummy, fake, stub, spy and mock for the kinds. A fake is a working, simplified implementation. A mock, in his sense, checks the calls it receives. [xUnit test patterns (Meszaros)]({{ '/docs/44-appendix-d-xunit-test-patterns/' | relative_url }}) covers the taxonomy.

Python's `unittest.mock` blurs the lines, because one `Mock` object stands in for all of them. Each double refuses something different. Four doubles, each handed a gateway name that doesn't exist and a call with the wrong shape:

| Double | Unknown name, `bok` | Call with no consignment | mypy |
| --- | --- | --- | --- |
| `FakeGateway` | `AttributeError`; mypy `[attr-defined]` | `TypeError`; mypy `[call-arg]` | checked: a missing member is an error |
| `Mock()` | accepted | accepted | accepted |
| `Mock(spec=CarrierGateway)` | `AttributeError` | accepted | accepted |
| `create_autospec(CarrierGateway, instance=True)` | `AttributeError` | `TypeError` | accepted |

A plain `Mock` passes an assertion on a misspelled method:

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

The consignment was booked, and `loser.bok.assert_not_called()` passes anyway, because `bok` is a fresh attribute that nobody called. `Mock(spec=CarrierGateway)` closes the first gap and not the second: `gateway.bok` raises `AttributeError`, and `gateway.book()` with no argument goes through and is recorded. Only `create_autospec` copies the signatures, so the witness for the engine's claim uses it:

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

A misspelled `loser.bok` would raise here, so the assertion on `loser.book` is the one that can fail. Both refusals:

```python
def test_autospec_rejects_names_and_signatures(mocker: MockerFixture) -> None:
    gateway = mocker.create_autospec(CarrierGateway, instance=True)

    with pytest.raises(AttributeError, match="has no attribute 'bok'"):
        _ = gateway.bok

    with pytest.raises(TypeError, match="missing a required argument: 'consignment'"):
        gateway.book()
```

`side_effect` drives a branch the happy path never reaches: an autospec whose `quote` raises `CarrierTimeoutError` makes the engine skip that carrier and report it in `skipped`. [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) shows an autospec of the wrong Protocol, [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}) lists the rest of the mock API, and the standard library's [autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing) section is the source for what `create_autospec` copies.

mypy accepts `Mock()`, `Mock(spec=...)`, `MagicMock(spec=...)` and an autospec wherever a `CarrierGateway` is expected, with no output. The reason is in typeshed's [`unittest/mock.pyi`](https://github.com/python/typeshed/blob/d03a581a8ebf525cba072b3e24e97f64825505b9/stdlib/unittest/mock.pyi), where `NonCallableMock`, the base of `Mock` and `MagicMock`, is declared as `class NonCallableMock(Base, Any)`, under this comment:

> We subclass with "Any" because mocks are explicitly designed to stand in for other types, something that can't be expressed with our static type system.

A mock is assignable to every type, so mypy has nothing to check at the call site. A hand-written fake gets the opposite treatment. Take a class that has `quote` and lacks `book`:

<!-- fmt:off -->
```python
class QuoteOnly:
    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        raise NotImplementedError
```
<!-- fmt:on -->

Put in a dictionary of gateways, it gets a bare error:

```text
<string>:19: error: Dict entry 0 has incompatible type "str": "QuoteOnly"; expected "str": "CarrierGateway"  [dict-item]
```

Assigned to a variable annotated `CarrierGateway`, it gets the explanation:

```text
<string>:17: error: Incompatible types in assignment (expression has type "QuoteOnly", variable has type "CarrierGateway")  [assignment]
<string>:17: note: "QuoteOnly" is missing following "CarrierGateway" protocol member:
<string>:17: note:     book
```

The rule: a fake earns a static check, an autospec earns a runtime check, and a plain mock earns neither.

## Time, environment, and other process state

`RateEngine` takes `clock: Callable[[], datetime]` and a `validity` as constructor arguments. Pass `clock=lambda: fixed_now` and `quote.valid_until == fixed_now + timedelta(minutes=45)` holds, with nothing to patch and nothing to wait for. The fixed instant is a fixture, so every test agrees on it.

A tie between two carriers is the other source of drift. The engine asks carriers in sorted code order and picks the minimum by `(amount, carrier)`, so the winner never depends on mapping order. A tie still resolves on the carrier code inside the quote when the mapping keys are account aliases.

The environment can't be injected away entirely, because `validity_from_env` defaults to `os.environ`. Every case but one passes an `environ` mapping, which needs no patching. The one that touches the real environment does it inside a context:

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

It captures the value before, whatever the shell left there, and compares after the block, without assuming the variable is unset. The [monkeypatch how-to](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) documents `context()`. Patching a module's name instead of the environment is a seam; [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) compares the options.

## mypy as a test

`uv run mypy --strict src tests` checks the tests as well as the code, which adds two tools pytest doesn't have.

`assert_type` from `typing` is a static assertion. With `assert_type(quote.total, Money)` in a test, mypy fails if `total` stops being a `Money`. Changed to `assert_type(quote.total, str)` in a scratch copy, pytest still passes and mypy fails:

```text
tests/test_engine.py:75: error: Expression is of type "Money", not "str"  [assert-type]
```

At runtime `assert_type` returns its first argument and does nothing else. Statically, `assert_type(1, str)` exits with status 1:

```text
<string>:4: error: Expression is of type "Literal[1]", not "str"  [assert-type]
```

Called at runtime with `# type: ignore[assert-type]`, it returns `1`. The ignore names its code, and `--strict` includes `warn_unused_ignores`, so if mypy stopped reporting the error, the comment would become the error. Replacing the call on that line with `1 == 1` gives:

```text
tests/test_static.py:142: error: Unused "type: ignore" comment  [unused-ignore]
```

So a typed ignore is a regression test: it holds for as long as mypy reports the thing it's about.

A small `_run` helper turns the same idea into a function. It writes a `mypy.ini`, calls `mypy.api.run` with `--strict` and no cache, and returns the output and exit status, so an assertion can pin the exit status, the exact set of error codes and the quoted message. A snippet is checked against the interpreter that runs pytest.

## Configuration that refuses silence

Three settings in the workspace's root `pyproject.toml` turn quiet failures into loud ones. The [pytest reference](https://docs.pytest.org/en/stable/reference/reference.html) documents each:

| Setting | Effect | Without it |
| --- | --- | --- |
| `--strict-markers` | an unregistered marker is a collection error | `PytestUnknownMarkWarning`, and the tests run |
| `--strict-config` | a configuration warning is an error | a warning |
| `xfail_strict = true` | an `xfail` test that passes fails the run | reported as `xpassed`, exit status 0 |
| `filterwarnings = ["error"]` | every warning is an exception | a summary at the end of the run that is easy to scroll past |

In pytest 9 the `xfail_strict` option is named `strict_xfail`, and `xfail_strict` remains an alias. The [capture warnings how-to](https://docs.pytest.org/en/stable/how-to/capture-warnings.html) shows the default warning summary.

Without `error`, a Python 3.15 deprecation scrolls past. A Protocol that inherits a `@runtime_checkable` Protocol without its own decorator gets a `DeprecationWarning` on `isinstance` and will raise `TypeError` in Python 3.20. With the filter, that is a failing test today.

## When a test proves less than it seems

- **Asserting that a mock was called, not what happened.** `assert_called_once_with` on a gateway records that the engine asked. It doesn't say whether the customer got the right reference, so assert the return value, `"AIRCO:CN-00000001"`, before the calls.
- **A mock where a fake would be checked.** A plain `Mock` is assignable everywhere. A `FakeGateway` is held to the Protocol by mypy.
- **A test never seen failing.** If its check can be deleted with every test still green, it measures nothing.
- **One parametrize case per line of the implementation.** The cases should be the claims. Three named cases for the cheapest carrier say more than ten that restate the sort.

> **🤖 Explore with your agent**
>
> "Name each test after the claim it witnesses. Build doubles for `CarrierGateway` with `mocker.create_autospec(CarrierGateway, instance=True)` or a hand-written fake, never a plain `Mock`. Assert the returned reference before the calls. Inject the clock and the environment mapping instead of patching, and use `monkeypatch.context()` for the one real-environment test. Keep `--strict-markers`, `xfail_strict` and `filterwarnings = ["error"]`."
>
> If a test has never been seen failing, delete its check in a scratch copy and confirm it fails.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/11-testing-with-pytest-pytest-mock-and-mypy
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 34 cases pass, and mypy reports `Success: no issues found in 10 source files`. Six experiments, each in a scratch copy:

- **Book every carrier.** In `RateEngine.book_best`, book every gateway in a dictionary comprehension and return the winner's entry. The return value is still right, but two tests fail: `loser.book.assert_not_called()` reports `Called 1 times`, and the fake loser's record isn't empty. mypy stays green.
- **Weaken the autospec.** Replace `create_autospec(CarrierGateway, instance=True)` with `Mock(spec=CarrierGateway)` in the refusal test. The name check passes, and the signature check fails with `DID NOT RAISE TypeError`.
- **Fail a test that uses a `yield` fixture.** Add a wrong assertion to a test that requests `quote_log`, and run it alone with `-s`. The fixture prints `quote_log teardown: quotes.log` straight after the `F`, before pytest's failure report.
- **Add an unregistered marker.** `@pytest.mark.slow` fails collection with ``'slow' not found in `markers` configuration option``, and no test runs. Without the strict options, the file passes with one warning.
- **Mark a passing test `xfail`.** The run fails with `[XPASS(strict)] known gap`. With `-o xfail_strict=false` it reports `1 xpassed` and exits 0.
- **Trigger the deprecation.** An `isinstance` check against an undecorated sub-protocol fails with `DeprecationWarning: ... isn't explicitly decorated with @runtime_checkable`. With `-o filterwarnings=default` the same test passes with one warning.

## What you can do now

- Name a test after its claim, and see it fail: the witness for "books only the winner" fails when the engine books every carrier.
- Supply dependencies by name with fixtures, build fakes with the `make_fake` factory, and clean up after `yield` in `quote_log`.
- Say what each double checks, using the table of four doubles, and that mypy accepts every mock.
- Make time and the environment deterministic with an injected clock and `monkeypatch.context()`.
- Use `assert_type(quote.total, Money)` and typed ignores as static tests.
- Make silence loud with `--strict-markers`, `xfail_strict` and `filterwarnings = ["error"]`.

## For deeper coverage

The pytest documentation covers these tools: [fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), [parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html), [monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html), [capturing warnings](https://docs.pytest.org/en/stable/how-to/capture-warnings.html) and the [reference](https://docs.pytest.org/en/stable/reference/reference.html) for configuration options. The [pytest-mock documentation](https://pytest-mock.readthedocs.io/en/stable/) describes the `mocker` fixture, and the standard library's [autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing) section explains what `create_autospec` copies. Typeshed's [`unittest/mock.pyi`](https://github.com/python/typeshed/blob/d03a581a8ebf525cba072b3e24e97f64825505b9/stdlib/unittest/mock.pyi) holds the comment quoted above.

Gerard Meszaros's *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007) is the source for the double names and the long catalogue behind them. Martin Fowler's article [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) argues the difference between asserting on state and asserting on interactions, which is the second habit in the list of tests that prove less than they seem. Brian Okken's *Python Testing with pytest*, second edition (Pragmatic Bookshelf, 2022), covers fixtures, parametrization and configuration at book length, and Brett Slatkin's *Effective Python*, third edition, has short rules on testing and typing. Both books are on the [bibliography page]({{ '/bibliography/' | relative_url }}).
