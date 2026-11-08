---
title: "pytest reference"
order: 42
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "B"
description: "Reference for the pytest configuration, import mode, fixtures, parametrisation, exception assertions and command-line options the examples rely on, each with the pytest page that describes it."
---

## Learning objectives

By the end of this appendix you can:

- Read the root `[tool.pytest.ini_options]` table and say what each setting refuses.
- Say what `--import-mode=importlib` allows and forbids, and where shared values go as a result.
- Pick the fixture form for a dependency, a cleanup, a scope, a factory or an indirect parameter.
- Assert an exception, an exception group or a warning precisely.
- Select, stop, list and rerun tests from the command line, and test a configuration line in an inner session.

## Why this matters

Under pytest's defaults, an unregistered marker, an `xfail` test that passes and a deprecation in the end-of-run summary all leave a green run. A few lines of configuration and a handful of fixture rules close those gaps, and each one fails silently when misread. Naming a test after its claim and deleting the check to watch it fail is covered in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}). Everything below is on pytest 9.2.0.

## The root configuration

One pytest table in the workspace's root `pyproject.toml` applies to every example:

<!-- fmt:off -->
```toml
[tool.pytest.ini_options]
addopts = "--import-mode=importlib --strict-markers --strict-config"
xfail_strict = true
filterwarnings = ["error"]
```
<!-- fmt:on -->

The excerpt leaves out `testpaths`.

| Setting | Without it | With it |
| --- | --- | --- |
| `--strict-markers` | an unregistered marker is a warning and the test passes | collection fails and the message names the marker |
| `--strict-config` | an unknown option is a warning | a usage error naming the option |
| `xfail_strict` or `strict_xfail` | an `xfail` test that passes is reported as `xpassed` | the run fails |
| `filterwarnings = ["error"]` | the warning is counted in the summary | the test fails with the warning |
| `testpaths` | pytest collects below the current working directory | pytest looks in the listed directories when the command line names none |
| `--import-mode=importlib` | two test files with one basename collide | each file gets a unique module name, and test modules can't import each other |

pytest 9 renamed one option: "Changed in version 9.0: Renamed from xfail_strict to strict_xfail", and "xfail_strict is accepted as an alias for strict_xfail" ([reference](https://docs.pytest.org/en/stable/reference/reference.html)). Both names fail the run.

The same release added `strict = true`, which enables `strict_config`, `strict_markers`, `strict_parametrization_ids` and `strict_xfail`. "If pytest adds new strictness options in the future, they will also be enabled in strict mode." The root table spells the options out instead, so a pytest upgrade can't add one. `strict_parametrization_ids` is the one `strict = true` would add.

The [configuration page](https://docs.pytest.org/en/stable/reference/customize.html) offers `[tool.pytest]` with native TOML types (since pytest 9.0) and `[tool.pytest.ini_options]` in INI style (since 6.0). The root file uses the second.

**One configuration file applies to a run.** "Options from multiple configfiles candidates are never merged", and "the first match wins". A subdirectory with its own table loses every root option: an unregistered marker that's a collection error at the root passes with a warning there. A member table with `addopts = ""` lets a `DeprecationWarning` through that the root's filter fails, and the run header names the member as the root. That's why members carry no pytest table.

## Inner sessions

Configuration and import mode belong to a whole run, so they're tested from outside it. The `pytester` fixture writes a small project into a temporary directory, runs pytest on it and checks the counts with `assert_outcomes(passed=1, warnings=1)`.

`pytester` is a plugin enabled with `pytest_plugins`. The reference page says to put `pytest_plugins = "pytester"` in the topmost `conftest.py`. The workspace has no root `conftest.py`, so each test module that uses `pytester` carries `pytest_plugins = ["pytester"]`, which the [plugins page](https://docs.pytest.org/en/stable/how-to/plugins.html) allows. In a non-root `conftest.py` the line is a collection error on pytest 9.2.0: "Defining 'pytest_plugins' in a non-top-level conftest is no longer supported".

`runpytest()` runs "inline or in a subprocess", and inline is the default here. An inline session inherits the outer run's warning filters, so under `filterwarnings = ["error"]` a lenient inner run raises `PytestUnknownMarkWarning` instead of counting it. An autouse fixture resets the filters:

```python
@pytest.fixture(autouse=True)
def fresh_warning_filters() -> Iterator[None]:
    """An in-process inner session inherits the process-wide warning filters, so clear the
    ``error`` filter the outer run applies and let each inner configuration decide."""
    with warnings.catch_warnings():
        warnings.resetwarnings()
        yield
```

Without `autouse=True`, every inner run that expects a marker warning fails with the outer filter's `pytest.PytestUnknownMarkWarning`.

## Import mode and conftest.py

| Mode | Behaviour | Source |
| --- | --- | --- |
| `prepend` (default) | Puts each test file's directory on `sys.path`; "each test file needs to have a unique name compared to the other test files". Two `tests/test_zones.py` files give an `import file mismatch` collection error. | [import mechanisms](https://docs.pytest.org/en/stable/explanation/pythonpath.html) |
| `importlib` | "Test module names do not need to be unique", and "Test modules can’t import each other." `from conftest import LIMIT` fails with `ModuleNotFoundError: No module named 'conftest'`. | same page |

So shared values reach tests as fixtures, which pytest discovers without an import. A test module that needs a type from `conftest.py` imports it under `TYPE_CHECKING`, so nothing is imported at run time:

```python
if TYPE_CHECKING:
    from conftest import MakeConsignment
```

## Fixtures

pytest passes a test the fixtures its parameters name; a fixture in `conftest.py` needs no import.

| Form | What it gives |
| --- | --- |
| code after `yield` | teardown, in the reverse of setup order |
| `scope="module"` | one setup for every test in the module |
| factory fixture | a function the test calls for as many objects as it needs |
| `autouse=True` | the fixture runs without being named |
| `@pytest.mark.usefixtures("name")` | a fixture applied for its effect, its value unused |
| `indirect=["rated"]` | the parameter value reaches the fixture as `request.param` |
| `request.getfixturevalue("name")` | a fixture looked up by name inside the test |

A factory fixture returns a builder, so each call is a fresh object:

```python
@pytest.fixture
def make_consignment() -> MakeConsignment:
    """A factory fixture: the test decides how many consignments to build, and with what."""

    def make(
        consignment_id: str = "CN-1", /, *, zone: str = "EU", kilograms: str = "10"
    ) -> Consignment:
        return Consignment(ConsignmentId(consignment_id), zone, Weight(Decimal(kilograms)))

    return make
```

An indirect parameter goes to the fixture, which builds the object the test receives:

```python
@pytest.fixture
def rated(request: pytest.FixtureRequest) -> Consignment:
    """A ten-kilogram consignment in the zone given as the indirect parameter."""
    zone: str = request.param
    return Consignment(ConsignmentId("CN-9"), zone, Weight(Decimal("10")))
```

```python
@pytest.mark.parametrize(
    ("rated", "expected"),
    [("EU", Decimal("4.50")), ("ASIA", Decimal("12.00"))],
    indirect=["rated"],
)
```

Without `indirect`, `rated` is the zone name, not a `Consignment`.

With a module-scoped `outer` and a function-scoped `inner` that depends on it, the order over two tests is: setup outer, setup inner, first, teardown inner, setup inner, second, teardown inner, teardown outer.

## Parametrize

| Form | Result |
| --- | --- |
| `pytest.param("EU", "4.50", id="europe")` | the id replaces the values in the node id: `test_zone[europe]` |
| `pytest.param("MARS", marks=pytest.mark.xfail(strict=True, raises=RatingError))` | one case carries its own mark: `passed=2, xfailed=1` |
| two stacked `parametrize` decorators | the cross product; zones by weights gives six cases |
| duplicate ids | `same0`, `same1`, or a collection error under `strict_parametrization_ids` |

In a stack, the decorator nearest the function comes first in the id and varies slowest: `[1-EU]`, `[1-ASIA]`, `[5-EU]`. Under `strict_parametrization_ids`, "pytest emits an error if it detects non-unique parameter set IDs".

## Built-in fixtures

| Fixture | Annotation | Behaviour |
| --- | --- | --- |
| `tmp_path` | `pathlib.Path` | an empty directory, different for each test |
| `capsys` | `pytest.CaptureFixture[str]` | captures `sys.stdout` and `sys.stderr`; read with `readouterr()` |
| `caplog` | `pytest.LogCaptureFixture` | captures log records; `caplog.messages` holds the formatted messages |
| `monkeypatch` | `pytest.MonkeyPatch` | `setenv`, `delenv` and `setattr` undone at teardown or at the end of `context()`; `setattr` refuses a misspelt name unless `raising=False`, which creates a name nothing reads |
| `pytester` | `pytest.Pytester` | an inner session whose counts, node ids or exit status you assert |

`capsys` sees only code that looks up `sys.stdout` when it's called. A signature `out: TextIO = sys.stdout` binds the stream at import, before `capsys` replaces it, and captures nothing.

mypy checks a typed fixture: with `capsys: pytest.CaptureFixture[str]`, adding an integer to the captured text is an `operator` error. Annotated as `object`, the parameter gives `attr-defined` on `readouterr` instead.

## Exceptions and warnings

| API | Checks |
| --- | --- |
| `pytest.raises(E, match=...)` | the type, then `re.search` against the message and its PEP 678 `__notes__` |
| `pytest.raises(E, check=fn)` | `fn(exception)` returns true, "after checking the type and the match regex if specified" |
| `pytest.RaisesGroup(...)` | an `ExceptionGroup` and the expectations for its members |
| `pytest.RaisesExc(E, match=..., check=...)` | one member of a group, with a pattern or a check |
| `pytest.warns(W, match=...)` | a warning of that type whose message matches |

An unanchored `match` finds its pattern anywhere: `"zone MARS"` matches `no rate for zone MARS` and `^zone MARS` doesn't. `check` takes the exception object:

```python
    with pytest.raises(OverweightError, check=lambda error: str(error).startswith("CN-1")):
        quote(heavy)
```

A failed check raises `AssertionError` ending `did not return True`.

For an exception group, the reference page says "you should instead use pytest.RaisesGroup". A bare exception class is one expectation, and `RaisesExc` adds `match` or `check` to one:

```python
def test_raises_group_matches_the_batch_failures() -> None:
    batch = [
        _consignment("CN-1", "MARS", "1"),
        _consignment("CN-2", "EU", "10"),
        _consignment("CN-3", "EU", "1001"),
    ]

    with pytest.RaisesGroup(
        pytest.RaisesExc(RatingError, match="^no rate for zone MARS$"), OverweightError
    ):
        rate_batch(batch)
```

A function that raised only the first failure wouldn't match, because that isn't a group. `pytest.warns` works the same way for a function decorated with `@warnings.deprecated("use quote")`:

```python
    with pytest.warns(DeprecationWarning, match="use quote"):
        total = legacy_quote(consignment)
```

Under `filterwarnings = ["error"]`, any warning nobody expects fails the test with `DeprecationWarning: use quote` in its output.

## Command-line options

| Option | What it does |
| --- | --- |
| `-k EXPRESSION` | runs tests matching a keyword expression: `-k asia` selects `test_quote_asia` |
| `-m MARKEXPR` | runs tests matching a marker expression: `-m bulk`, `-m "not bulk"`; the marker must be registered under `--strict-markers` |
| `-x` | stops at the first failure |
| `--lf` | reruns the last run's failures; the header reads `run-last-failure: rerun previous 1 failure` |
| `--co`, `--collect-only` | lists node ids without running them |
| `-o NAME=VALUE` | overrides an ini option: `-o xfail_strict=false` turns a strict failure back into `xpassed` |
| `-q`, `--quiet` | "Decrease verbosity." |
| `-v`, `--verbose` | "Increase verbosity." |
| `-s` | "Shortcut for --capture=no." |
| `--tb=STYLE` | traceback style: `auto`, `long`, `short`, `line`, `native` or `no` |
| `-p NAME` | "Early-load given plugin module name or entry point (multi-allowed)." |

## Running the reference tests

From the root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/42-appendix-b-pytest
uv run pytest -q
uv run mypy --strict src tests
```

All 44 cases pass and mypy is clean.

## For deeper coverage

The pytest documentation is the primary source for each row: the [reference page](https://docs.pytest.org/en/stable/reference/reference.html) for the options and the fixtures, the [configuration page](https://docs.pytest.org/en/stable/reference/customize.html) for files and their precedence, the [import mechanisms page](https://docs.pytest.org/en/stable/explanation/pythonpath.html) for the three modes and the [plugins how-to](https://docs.pytest.org/en/stable/how-to/plugins.html) for `pytest_plugins`. Brian Okken's *Python Testing with pytest*, second edition (Pragmatic Bookshelf, 2022), covers fixtures, parametrisation and configuration at book length, and it's on the [bibliography page]({{ '/bibliography/' | relative_url }}). The method and the four kinds of double are in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}), and the mock API is in [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}).
