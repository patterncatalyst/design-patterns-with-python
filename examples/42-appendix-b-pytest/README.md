# pytest reference

The tests in this example show the pytest features the book's suites rely on, each on the pinned
pytest. Where a row depends on configuration, collection or the order of several tests, the test
writes a project into a temporary directory, runs pytest on it with the `pytester` fixture and
asserts the outcome counts, the node ids or the exit status. The remaining rows run directly.
Nothing here uses a mock or a patch.

## What it witnesses

The module under test is small. `quote` prices a `Consignment` by weight and zone from the
read-only `RATES` table and logs the result. `rate_batch` quotes a list and raises one
`ExceptionGroup` holding every `RatingError` and `OverweightError`. `legacy_quote` is marked
`@warnings.deprecated`. `write_quotes` writes one line per consignment to `out`, or to the current
`sys.stdout` when none is given.

| Area | What the tests show |
| --- | --- |
| Fixtures | yield order, module scope, a factory, `autouse`, `usefixtures`, `indirect` and `getfixturevalue` |
| Parametrisation | `pytest.param` ids and marks, stacked decorators, duplicate ids |
| Built-in fixtures | `tmp_path`, `capsys` and `caplog` |
| Exceptions and warnings | `match`, `check`, `RaisesGroup` with `RaisesExc`, and `warns` |
| Configuration | the strictness options, `strict = true` and the first configuration file |
| Import modes | a basename collision, and `conftest` imports under `importlib` |
| Command line | `-k`, `-m`, `-x`, `--lf`, `--collect-only` and `-o` |

## Layout

- `src/pytest_reference/domain.py`: `ConsignmentId`, `Weight`, `Consignment`.
- `src/pytest_reference/rating.py`: `RATES`, `CENT`, `MAX_KILOGRAMS`, `RatingError`,
  `OverweightError`, `quote`, `rate_batch`, `legacy_quote`.
- `src/pytest_reference/report.py`: `write_quotes`.
- `tests/conftest.py`: the `consignment`, `make_consignment`, `ran`, `note_autouse`,
  `note_usefixtures`, `rated` and `node_ids` fixtures.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
```

## What the tests verify

`tests/test_fixtures.py`

- `test_yield_fixtures_tear_down_in_reverse_order_of_setup`: a module-scoped fixture is set up
  first and torn down last around two tests.
- `test_a_module_scoped_fixture_is_set_up_once_for_the_module`
- `test_a_factory_fixture_builds_a_fresh_object_per_call`
- `test_an_autouse_fixture_runs_without_being_named`
- `test_usefixtures_applies_a_fixture_whose_value_is_unused`
- `test_an_indirect_parameter_reaches_the_fixture_as_request_param`: one case per zone.
- `test_getfixturevalue_resolves_a_fixture_by_name`

`tests/test_parametrize.py`

- `test_pytest_param_ids_name_the_cases`
- `test_a_case_can_carry_its_own_mark`
- `test_stacked_parametrize_takes_the_cross_product`: six collected, in the order listed.
- `test_duplicate_ids_get_a_suffix_unless_strict_parametrization_ids`

`tests/test_builtin_fixtures.py`

- `test_tmp_path_is_a_fresh_directory_per_test`
- `test_capsys_captures_what_the_report_writes`: also shows `out=` taking the text instead.
- `test_caplog_records_the_quote_message`

`tests/test_raises.py`

- `test_raises_match_is_a_regex_search`
- `test_raises_check_tests_the_exception_object`
- `test_raises_group_matches_the_batch_failures`
- `test_warns_matches_the_deprecation`

`tests/test_config.py`

- `test_an_unregistered_marker_fails_collection_under_strict_markers`
- `test_a_passing_xfail_fails_the_run_under_strict_xfail`: once for `xfail_strict` and once for
  `strict_xfail`.
- `test_an_unknown_option_fails_under_strict_config`
- `test_filterwarnings_error_turns_a_warning_into_a_failure`
- `test_strict_enables_the_four_strictness_options`: one case per option, with `strict = true`
  and no individual option.
- `test_the_first_config_file_wins_and_is_not_merged`
- `test_a_member_table_replaces_the_root_filter_and_names_its_own_file`

`tests/test_import_modes.py`

- `test_same_basename_test_files_collide_under_prepend`
- `test_importlib_mode_gives_each_test_file_a_unique_name`
- `test_importlib_mode_cannot_import_conftest_by_name`
- `test_pytest_plugins_in_a_non_root_conftest_fails_collection`: the same line in a test module
  loads the plugin.

`tests/test_cli.py`

- `test_k_selects_by_name_expression`
- `test_m_selects_by_marker`
- `test_x_stops_at_the_first_failure`
- `test_lf_reruns_only_the_last_failures`
- `test_collect_only_lists_without_running`
- `test_o_overrides_an_ini_option`

`tests/test_rating.py`

- `test_a_non_positive_weight_is_refused`
- `test_a_quote_rounds_half_up_to_the_cent`
- `test_a_clean_batch_returns_its_quotes_in_order`

`tests/test_static.py`

- `test_mypy_checks_a_typed_fixture_use`

An in-process inner session inherits the warning filters of the run that started it, so the
tests in `test_config.py` clear them first and let each inner configuration decide. No test
sleeps or reads a clock, and none asserts on a path. The static test runs
`mypy --strict --warn-unreachable` through `mypy.api`.
