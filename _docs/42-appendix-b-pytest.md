---
title: "pytest reference"
order: 42
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "B"
description: "Reference for the pytest configuration, import mode, fixtures, parametrisation, exception assertions and command-line options the book relies on, each shown by a test or by the pytest page that describes it."
---

## Learning objectives

By the end of this appendix you can:

- Read the root `[tool.pytest.ini_options]` table and say what each setting refuses.
- Say what `--import-mode=importlib` allows and forbids, and where shared values go as a result.
- Pick the fixture form for a dependency, a cleanup, a scope, a factory or an indirect parameter.
- Assert an exception, an exception group or a warning precisely.
- Select, stop, list and rerun tests from the command line, and test a configuration line in an inner session.

## Why this matters

A suite's strength rests on a few lines of configuration and a handful of fixture rules, and each fails without a sound when misread. Under pytest's defaults, an unregistered marker, an `xfail` test that passes and a deprecation in the end-of-run summary all leave a green run. The method of naming a test after its claim and deleting the check to watch it fail belongs to [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}), along with its experiments. The rest of what the suites rely on is collected here, on pytest 9.2.0 and Python 3.15.2.

A row in the tables that follow names its witness: a test in the `pytest-reference` example, a test from another example, or, for settings and flags that have none, the page of the pytest documentation that describes them. The example's configuration and command-line tests run pytest inside pytest, and the section on inner sessions says how.

## The root configuration

One pytest table in the workspace's root `pyproject.toml` applies to the examples:

<!-- fmt:off -->
```toml
[tool.pytest.ini_options]
addopts = "--import-mode=importlib --strict-markers --strict-config"
xfail_strict = true
filterwarnings = ["error"]
```
<!-- fmt:on -->

The excerpt leaves out `testpaths`, the line that lists the directories holding the tests.

Four of its settings refuse what pytest's defaults let through. Each has a test that runs an inner session with the setting and without it. Three assert the outcome counts of both runs; the `--strict-config` test asserts the usage-error exit status and the message that names the option.

| Setting | Without it | With it | Witness |
| --- | --- | --- | --- |
| `--strict-markers` | an unregistered marker is a warning and the test passes | collection fails and the message names the marker | `test_an_unregistered_marker_fails_collection_under_strict_markers` |
| `--strict-config` | an unknown option is a warning | a usage error naming the option | `test_an_unknown_option_fails_under_strict_config` |
| `xfail_strict` or `strict_xfail` | an `xfail` test that passes is reported as `xpassed` | the run fails | `test_a_passing_xfail_fails_the_run_under_strict_xfail` |
| `filterwarnings = ["error"]` | the warning is counted in the summary | the test fails with the warning | `test_filterwarnings_error_turns_a_warning_into_a_failure` |
| `testpaths` | pytest collects below the current working directory | pytest looks in the listed directories when the command line gives no directory, file or test id | [reference page](https://docs.pytest.org/en/stable/reference/reference.html), [customize page](https://docs.pytest.org/en/stable/reference/customize.html) |
| `--import-mode=importlib` | two test files with one basename collide | each file gets a unique module name, and test modules can't import each other | the tests in the import mode section |

pytest 9 renamed one of these. The [reference page](https://docs.pytest.org/en/stable/reference/reference.html) records "Changed in version 9.0: Renamed from xfail_strict to strict_xfail." and "xfail_strict is accepted as an alias for strict_xfail." The xfail test is parametrised over both names, and each fails the run.

The same release added a `strict` option. `strict = true` enables `strict_config`, `strict_markers`, `strict_parametrization_ids` and `strict_xfail`, and `test_strict_enables_the_four_strictness_options` has one case for each, with `strict = true` and no individual option set. The page adds a caution: "If pytest adds new strictness options in the future, they will also be enabled in strict mode." The root table spells the options out instead, and `strict_parametrization_ids` is the one that `strict = true` would add.

The [configuration page](https://docs.pytest.org/en/stable/reference/customize.html) offers two TOML forms: "Use [tool.pytest] to leverage native TOML types (supported since pytest 9.0)" and "Use [tool.pytest.ini_options] for INI-style configuration (supported since pytest 6.0)". The root file uses the second.

One configuration file applies to a run. The same page says "Options from multiple configfiles candidates are never merged", and that "the first match wins". `test_the_first_config_file_wins_and_is_not_merged` builds an inner root with `--strict-markers` and a subdirectory with its own table. Run on the root, an unregistered marker is a collection error. Run on the subdirectory, the same marker passes with one warning, because the root's options are gone. That's why the members carry no pytest table. `test_a_member_table_replaces_the_root_filter_and_names_its_own_file` builds the layout: a root table with `filterwarnings = ["error"]` and a member directory whose own `pyproject.toml` has a table with `addopts = ""`. Run with the root's file, the `DeprecationWarning` test fails. Run in the member, the same test passes with one warning, and the header names the member directory as the root and `pyproject.toml` as the configuration file.

## Inner sessions

Configuration and import mode belong to a whole run, so the example witnesses them from outside it. It writes a small project into a temporary directory with the `pytester` fixture, runs pytest on it and asserts the counts, as in `assert_outcomes(passed=1, warnings=1)`. Tests of configuration write the inner project's table themselves.

`pytester` is a plugin that a run has to enable with `pytest_plugins`. The [reference page](https://docs.pytest.org/en/stable/reference/reference.html) says to "include in your topmost conftest.py file" the line `pytest_plugins = "pytester"`. The workspace has no `conftest.py` at its root, so each test module that uses `pytester` carries `pytest_plugins = ["pytester"]` itself, and the [plugins page](https://docs.pytest.org/en/stable/how-to/plugins.html) allows that: "You can require plugins in a test module or a conftest file using pytest_plugins". The same page says "Requiring plugins using a pytest_plugins variable in non-root conftest.py files is deprecated." On pytest 9.2.0 the run fails instead. `test_pytest_plugins_in_a_non_root_conftest_fails_collection` gets one collection error, "Defining 'pytest_plugins' in a non-top-level conftest is no longer supported", from a `conftest.py` in a subdirectory, while the same line in a test module collects and passes. The example's `conftest.py` doesn't carry the line. With it in the test modules, the member collects from the root and from its own directory.

An inner session has a second trap. The [reference page](https://docs.pytest.org/en/stable/reference/reference.html) describes `runpytest()` as able to "Run pytest inline or in a subprocess", and these tests run it inline. An inline session inherits the warning filters of the run that started it. Under the root's `filterwarnings = ["error"]`, a lenient inner run that should report an unregistered marker as `PytestUnknownMarkWarning` in its summary raises it instead. The member resets the filters with an autouse fixture in `tests/test_config.py`:

```python
@pytest.fixture(autouse=True)
def fresh_warning_filters() -> Iterator[None]:
    """An in-process inner session inherits the process-wide warning filters, so clear the
    ``error`` filter the outer run applies and let each inner configuration decide."""
    with warnings.catch_warnings():
        warnings.resetwarnings()
        yield
```

Two tests there run a lenient inner session in which an unregistered marker is a warning, and both expect `passed=1, warnings=1`. Without `autouse=True` on the fixture, `test_an_unregistered_marker_fails_collection_under_strict_markers` and `test_the_first_config_file_wins_and_is_not_merged` fail, each with the outer run's filter raising `pytest.PytestUnknownMarkWarning`.

## Import mode and conftest.py

The default import mode puts each test file's directory on `sys.path`. The [import mechanisms page](https://docs.pytest.org/en/stable/explanation/pythonpath.html) states the cost for a tree without packages: "each test file needs to have a unique name compared to the other test files". The root table selects `importlib`, which the page describes in a different way: "Test module names do not need to be unique". The first of two tests puts the same pair of files through each mode:

```python
def _two_files_with_one_basename(pytester: pytest.Pytester) -> None:
    for zone in ("EU", "ASIA"):
        tests = pytester.mkdir(zone.lower()) / "tests"
        tests.mkdir()
        (tests / "test_zones.py").write_text(_ZONE_TEST.replace("{zone}", zone))


def test_same_basename_test_files_collide_under_prepend(pytester: pytest.Pytester) -> None:
    _two_files_with_one_basename(pytester)

    result = pytester.runpytest("--import-mode=prepend", "eu", "asia")

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*import file mismatch*"])
```

Under `prepend` pytest reports an import file mismatch and the run has one collection error. `test_importlib_mode_gives_each_test_file_a_unique_name` runs the same files under `importlib` and both tests pass.

The cost of `importlib` is on the same page: "Test modules can’t import each other." `test_importlib_mode_cannot_import_conftest_by_name` writes a `tests/conftest.py` with a constant and a test that runs `from conftest import LIMIT`. Under `prepend` it passes. Under `importlib` it errors with `ModuleNotFoundError: No module named 'conftest'`.

The book's habit follows. Shared values reach tests through fixtures, which pytest discovers without an import, and a test module imports a type from `conftest.py` under `TYPE_CHECKING`, so nothing is imported at run time. The example's test modules do that with `MakeConsignment` and `NodeIds`, and the tests of the chapter titled [Final project]({{ '/docs/39-final-project/' | relative_url }}) import `World` the same way.

## Fixtures

pytest passes a test the fixtures that its parameters name. `test_caplog_records_the_quote_message` asks for `consignment`, which lives in `conftest.py`, and needs no import to get it.

| Form | What it gives | Witness |
| --- | --- | --- |
| code after `yield` | teardown, in the reverse of setup order | `test_yield_fixtures_tear_down_in_reverse_order_of_setup` |
| `scope="module"` | one setup for the tests of the module | `test_a_module_scoped_fixture_is_set_up_once_for_the_module` |
| factory fixture | a function the test calls for as many objects as it needs | `test_a_factory_fixture_builds_a_fresh_object_per_call` |
| `autouse=True` | the fixture runs without being named | `test_an_autouse_fixture_runs_without_being_named` |
| `@pytest.mark.usefixtures` | a fixture applied for its effect, its value unused | `test_usefixtures_applies_a_fixture_whose_value_is_unused` |
| `indirect=["rated"]` | the parameter value reaches the fixture as `request.param` | `test_an_indirect_parameter_reaches_the_fixture_as_request_param` |
| `request.getfixturevalue` | a fixture looked up by name inside the test | `test_getfixturevalue_resolves_a_fixture_by_name` |

The order test writes a module with a module-scoped `outer` fixture and a function-scoped `inner` that depends on it, lets each step append a line to a file, and reads the file after the inner run. This is the assertion:

<!-- fmt:off -->
```python
    assert (pytester.path / "order.txt").read_text().splitlines() == [
        "setup outer",
        "setup inner",
        "first",
        "teardown inner",
        "setup inner",
        "second",
        "teardown inner",
        "teardown outer",
    ]
```
<!-- fmt:on -->

`outer` is set up once, before both tests, and torn down last. `inner` is built and torn down around each test. Teardown after a failing test is a separate question. The experiments in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) make a test fail to show it.

## Parametrize

`pytest.param` gives one case a name, a mark or both, and the stacked form multiplies.

| Form | What the test shows | Witness |
| --- | --- | --- |
| `pytest.param(..., id="europe")` | the id replaces the values in the node id: `test_zone[europe]` | `test_pytest_param_ids_name_the_cases` |
| `pytest.param(..., marks=...)` | a strict `xfail` on one case leaves `passed=2, xfailed=1` | `test_a_case_can_carry_its_own_mark` |
| two `parametrize` decorators | six cases from two zones and three weights | `test_stacked_parametrize_takes_the_cross_product` |
| duplicate ids | a numeric suffix, or an error under `strict_parametrization_ids` | `test_duplicate_ids_get_a_suffix_unless_strict_parametrization_ids` |

In the stacked test the decorator nearest the function names the weight, and the ids come out `[1-EU]`, `[1-ASIA]`, `[5-EU]`, so that decorator is first in the id and varies slowest across the six. For duplicates, two cases that share the id `same` collect as `same0` and `same1`. With the option set, the run has one collection error, and the page says why: "pytest emits an error if it detects non-unique parameter set IDs".

## Built-in fixtures

| Fixture | Annotation | What the test shows | Witness |
| --- | --- | --- | --- |
| `tmp_path` | `pathlib.Path` | two tests each get an empty directory, and the directories differ | `test_tmp_path_is_a_fresh_directory_per_test` |
| `capsys` | `pytest.CaptureFixture[str]` | what `write_quotes` writes to `sys.stdout` is captured | `test_capsys_captures_what_the_report_writes` |
| `caplog` | `pytest.LogCaptureFixture` | the INFO record of `quote`, read from `caplog.messages` | `test_caplog_records_the_quote_message` |
| `monkeypatch` | `pytest.MonkeyPatch` | `setenv`, `delenv` and `context()` restore the environment; `setattr` refuses a misspelt name; `raising=False` creates a name nothing reads | `test_validity_reads_the_environment_and_the_context_restores_it`, `test_monkeypatch_refuses_a_misspelt_name`, `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`, `test_monkeypatch_undoes_its_changes_when_the_context_ends` |
| `pytester` | `pytest.Pytester` | an inner session whose outcome counts, node ids or exit status the test asserts | the tests in the sections above |

`write_quotes` looks up `sys.stdout` when it's called, which is what lets `capsys` see it. Rewriting the signature as `out: TextIO = sys.stdout` fails the test, because the default is bound at import, before `capsys` replaces the stream. The test also passes an `io.StringIO` as `out` and finds the text there.

A typed fixture is checked by mypy. `test_mypy_checks_a_typed_fixture_use` type-checks a function with `capsys: pytest.CaptureFixture[str]`. Adding an integer to the captured text gives an `operator` error, and adding a string gives none. Annotating the parameter as `object` replaces `operator` with `attr-defined`, because `object` has no `readouterr`.

## Exceptions and warnings

`pytest.raises` tests the exception that a block raises. Its `match` argument is, in the words of the [reference page](https://docs.pytest.org/en/stable/reference/reference.html), "tested against the string representation of the exception and its PEP 678 __notes__ using re.search()". A pattern without an anchor therefore matches inside the message, and `test_raises_match_is_a_regex_search` shows `"zone MARS"` matching `no rate for zone MARS` and `^zone MARS` failing, with an `AssertionError` that starts `Regex pattern did not match`.

`check` takes a callable. The page says it is "called with the exception as a parameter after checking the type and the match regex if specified". In `test_raises_check_tests_the_exception_object`, a check that the message starts with `CN-1` passes for that consignment, and a check for `CN-2` fails with an `AssertionError` that ends `did not return True`.

For an exception group, the page directs the reader elsewhere: "When expecting exceptions wrapped in BaseExceptionGroup or ExceptionGroup, you should instead use pytest.RaisesGroup." `rate_batch` raises one group that holds the failures of a batch, and `RaisesGroup` takes the expectations for the group's members, and a bare exception class is one expectation. `RaisesExc` adds `match` or `check` to one, and the page says "You don’t need this if you only want to specify the type, since RaisesGroup accepts type[BaseException]."

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

If `rate_batch` raised the first failure alone, this test would fail, because that isn't a group.

`pytest.warns` does the same for warnings. `legacy_quote` is decorated with `@warnings.deprecated("use quote")`, and `test_warns_matches_the_deprecation` expects a `DeprecationWarning` that matches `use quote`. Under the root's `filterwarnings = ["error"]`, an unexpected warning is a failure, and inner runs show the message: `test_filterwarnings_error_turns_a_warning_into_a_failure` finds `DeprecationWarning: use quote` in the failing output. Other tests of `warns` are `test_an_undecorated_subprotocol_warns_on_isinstance` in the chapter titled [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) and `test_a_quote_that_is_never_awaited_warns_when_it_is_collected` in the chapter titled [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## Command-line options

Six options have a test. Each runs an inner session and asserts the outcome counts, the node ids or the exit status.

| Option | What it does | Witness |
| --- | --- | --- |
| `-k EXPRESSION` | runs the tests that match a keyword expression: `-k asia` selects `test_quote_asia` and deselects the other | `test_k_selects_by_name_expression` |
| `-m MARKEXPR` | runs the tests that match a marker expression: `-m bulk` selects the marked test, and `-m "not bulk"` lists the unmarked one | `test_m_selects_by_marker` |
| `-x` | stops at the first failure: `failed=1` where the full run has `failed=1, passed=1` | `test_x_stops_at_the_first_failure` |
| `--lf` | reruns the failures of the last run, with the header `run-last-failure: rerun previous 1 failure` | `test_lf_reruns_only_the_last_failures` |
| `--co` or `--collect-only` | lists node ids without running them | `test_collect_only_lists_without_running` |
| `-o NAME=VALUE` | overrides an ini option: `-o xfail_strict=false` turns the strict failure back into `xpassed=1` | `test_o_overrides_an_ini_option` |

`-m` needs the marker to be registered under `--strict-markers`, and the inner configuration in `test_m_selects_by_marker` registers `bulk`. The remaining flags have no test, and the reference page is their witness:

| Option | What the page says |
| --- | --- |
| `-q`, `--quiet` | "Decrease verbosity." |
| `-v`, `--verbose` | "Increase verbosity." |
| `-s` | "Shortcut for --capture=no." |
| `--tb=STYLE` | traceback print mode, with the styles `auto`, `long`, `short`, `line`, `native` and `no` |
| `-p NAME` | "Early-load given plugin module name or entry point (multi-allowed)." |

## Running the reference tests

From the root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/42-appendix-b-pytest
uv run pytest -q
uv run mypy --strict src tests
```

A fresh run of the member has 39 test functions and 44 cases, and ends `44 passed`. The mypy run ends `Success: no issues found in 14 source files`.

## For deeper coverage

The pytest documentation is the primary source for each row: the [reference page](https://docs.pytest.org/en/stable/reference/reference.html) for the options and the fixtures, the [configuration page](https://docs.pytest.org/en/stable/reference/customize.html) for files and their precedence, the [import mechanisms page](https://docs.pytest.org/en/stable/explanation/pythonpath.html) for the three modes and the [plugins how-to](https://docs.pytest.org/en/stable/how-to/plugins.html) for `pytest_plugins`. Brian Okken's *Python Testing with pytest*, second edition (Pragmatic Bookshelf, 2022), covers fixtures, parametrisation and configuration at book length, and it's on the [bibliography page]({{ '/bibliography/' | relative_url }}). The method and the four kinds of double are in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}), and the mock API is in [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}).
