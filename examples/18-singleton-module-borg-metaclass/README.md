# Singleton: module, Borg, and metaclass

The tariff table, loaded once and read everywhere. The chapter's thesis is that Singleton needs
disambiguating: the default is a module, `lazy import` defers the load to first use, a parameter
gives a test or tenant its own table, and a lock with a double check is for the rare load that needs
run-time input. Rates and zones are illustrative.

## What it witnesses

The module and the lazy import.

- `tariff_table.TARIFF` is built when the module is first imported, and every importer gets that
  object. `quoting.py` reaches it through `lazy from singleton import tariff_table`, so importing
  `quoting` loads nothing and the first quote does. Both run in fresh `-I` interpreters.
- `quote` prices from the table it is given, and `quote_standard` passes the module's table.
- mypy still checks attributes through a lazy import.

Isolation and threads.

- A class each call site constructs loads once per caller. A `functools.cache` loader carries one
  test's table into the next until `cache_clear`.
- `functools.cache` runs a loader twice when two threads arrive together. `LoadOnce` runs it once. A
  gated lock, whose `__enter__` waits on a `Barrier(2)`, puts both threads past the first check
  before either takes the lock, so the interleaving is forced and nothing sleeps.
- A loaded value is read without the lock, and a loader that returns `None` still runs once because
  the marker is the `NOT_LOADED` sentinel.

Comparison fixtures (test only).

- Borg, a metaclass singleton and a `__new__` singleton run the same "every caller reads the same
  rates" table as the module, `LoadOnce` and the cache; five load once and the `__new__` form twice.
  Borg instances are distinct and unequal, the metaclass ignores a second call's arguments and mypy
  types the call by `__init__`, the `__new__` form reruns `__init__` and rewrites the shared table,
  and slots refuse Borg.

## Layout

- `src/singleton/domain.py`: `TariffTable`, `RatingError`.
- `src/singleton/loads.py`: `LOAD_LOG`, `record_load`.
- `src/singleton/tariff_table.py`: `STANDARD_RATES`, `load_tariff`, `TARIFF`.
- `src/singleton/quoting.py`: `quote`, `quote_standard`.
- `src/singleton/once.py`: `NOT_LOADED`, `LoadOnce`.

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

`tests/test_module.py`

- `test_every_importer_gets_the_one_tariff_table`: one object and one load.
- `test_a_lazy_import_loads_the_table_on_first_use`: an empty load log after the import, one entry after the first quote.
- `test_threads_racing_on_a_lazy_import_load_the_table_once`: eight threads, one load. This race is not forced.
- `test_quote_takes_the_table_it_is_given`: two tables, two prices, no load.
- `test_an_unknown_zone_is_a_rating_error`: the original `KeyError` is suppressed.
- `test_the_tariff_table_is_a_frozen_value`: assignment is refused.

`tests/test_isolation.py`

- `test_a_naive_class_loads_the_table_once_per_caller`: two call sites, two loads.
- `test_a_cached_loader_carries_one_tests_table_into_the_next`: the override is gone and the table is not.
- `test_cache_clear_resets_the_cached_loader`: the standard rate returns.

`tests/test_once.py`

- `test_functools_cache_runs_a_loader_twice_when_two_threads_arrive_together`: two loads, two objects.
- `test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check`: one load, one object, two lock entries.
- `test_a_loaded_value_is_read_without_taking_the_lock`: one entry for the first call, none after.
- `test_load_once_keeps_a_loader_that_returns_none`: one load over three calls.
- `test_the_not_loaded_marker_is_a_sentinel_and_not_none`: its repr and identity.
- `test_a_failed_load_is_tried_again`: a failure is not kept.

`tests/test_variants.py`

- `test_every_form_gives_each_caller_the_same_rates`: six forms; five load once and the `__new__` form twice.
- `test_borg_instances_share_state_but_are_distinct_and_unequal`: one `__dict__`, two objects.
- `test_a_singleton_metaclass_ignores_the_second_calls_arguments`: the first source stays.
- `test_a_new_based_singleton_reruns_init_on_every_call`: the first caller's object changes.

`tests/test_static.py`

- `test_mypy_types_a_metaclass_singleton_call_by_init`: clean for a second call, `[call-arg]` for a missing one.
- `test_mypy_accepts_borg_state_unless_the_class_has_slots`: clean, then `[misc]`.
- `test_mypy_still_checks_attributes_through_a_lazy_import`: `[attr-defined]` with a suggestion.

Classes named with a leading underscore in the test modules are test fixtures and aren't part of
the model code. The metaclass and Borg snippets in `test_static.py` are reduced models of the
fixtures in `conftest.py`. Fixtures that hold class-level state clear it before and after each test.
