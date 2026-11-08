---
title: "Singleton: module, Borg, and metaclass"
order: 18
layout: tutorial
sectionid: docs
part: "creating-objects-under-control"
description: "Singleton needs disambiguating: the default is a module built at import time or on first use, with a parameter for tests and a double-checked lock for loads that need run-time input."
---

## Learning objectives

By the end of this chapter you can:

- Say which of three things "Singleton" means in a design: one object, one shared state, or one class that returns the same object.
- Climb the ladder in order: a module built at import time, a `lazy import` of it, the table passed in as a parameter, and a double-checked lock only when the load needs run-time input.
- Show with a forced race that `functools.cache` memoises and does not run a loader once under threads.
- Name the measured cost of Borg, of a metaclass singleton and of the `__new__` form.

## Why this matters

A tariff table is loaded from rates and read by every quote. The rates in this chapter are illustrative. Three things go wrong in the obvious versions.

A class that each call site constructs loads the table once per caller. Two call sites make two tables, and a log kept by the test records two loads where one was wanted.

A cached loader hands one test's table to the next. The first test overrides a rate and loads. The next test clears the override and still prices Asia at the first test's rate, because the cache held the table and not the override.

Two threads reach a cached loader together and both run it. The cache is correct as a cache, and it never promised a single call.

{% include excalidraw.html name="18-singleton-module-borg-metaclass" caption="Figure 18.1: Four ways to load the tariff table once, in the order to reach for them. A module, a lazy import and a parameter come first; the class forms beside them each cost something the tests measure." %}

Read the ladder on the left from the top. Each box has an arrow down to the next: `tariff_table`, a module built at import time; `lazy from ... import tariff_table`, built on first use, once; `quote(..., table=...)`, where the table is passed in so tests and tenants get their own; and `LoadOnce`, a lock with a double check for a load that needs run-time input. A dashed arrow runs from `LoadOnce` to an accent box that says `functools.cache` memoises and is not call-once. The right-hand column is muted, with dashed borders and no arrows: `Borg` (shared state, distinct objects), `SingletonMeta` (second call's arguments ignored) and `__new__` (reruns `__init__`). Those three are test fixtures in the example, not part of `src/`.

## Three things called Singleton

Gamma, Helm, Johnson and Vlissides, in *Design Patterns* (1994), describe Singleton as a class that guards its own construction so the whole program shares one object, fetched through an operation on the class. Brandon Rhodes, on the python-patterns.guide page ["The Singleton Pattern"](https://python-patterns.guide/gang-of-four/singleton/), shows that Python programmers say "singleton" for several things, and the three that matter for design are these.

- **One object.** A module is built once and every later import returns the same object. Rhodes's page ["The Global Object Pattern"](https://python-patterns.guide/python/module-globals/) names the practice of assigning an instance to a module-level name.
- **One shared state.** Many objects whose attributes live in one place. Alex Martelli's recipe, ActiveState recipe 66531, "Singleton? We don't need no stinkin' singleton: the Borg design pattern", is where Borg comes from.
- **One class that returns the same object.** A metaclass `__call__` or a `__new__` that returns a stored instance, so `Table()` reads like construction and isn't.

The bucket is needs disambiguating, and the default answer to the force, "load this once and let everyone read it", is the first meaning: a module. [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) shows the module shape, and [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) places Singleton in its bucket.

`test_every_form_gives_each_caller_the_same_rates` runs six forms (the module, `LoadOnce`, Borg, a metaclass singleton, a cached function and the `__new__` form) and checks that two callers read equal rates and how many loads happened. Five load once. The `__new__` form loads twice, because `__init__` runs on every call.

## The module, at import time or on first use

`tariff_table.py` builds `TARIFF` at import time. `test_every_importer_gets_the_one_tariff_table` keeps the shape the three-way split already shows: two imports, one `TARIFF`, one load in the log that `loads.py` keeps.

Python 3.15 adds a second rung. `quoting.py` reaches the table through a lazy import:

```python
from decimal import Decimal

from singleton.domain import TariffTable
lazy from singleton import tariff_table


def quote(zone: str, kilograms: Decimal, *, table: TariffTable) -> Decimal:
    """Price a consignment from the table it is given."""
    return table.rate_for(zone) * kilograms


def quote_standard(zone: str, kilograms: Decimal) -> Decimal:
    """Price a consignment from the standard tariff, loaded on first use."""
    return quote(zone, kilograms, table=tariff_table.TARIFF)
```

[PEP 810](https://peps.python.org/pep-0810/) adds the `lazy` soft keyword, and the [What's New page for 3.15](https://docs.python.org/3.15/whatsnew/3.15.html) says what it does: "Python defers the actual module loading until the imported name is first used." Importing `quoting` loads nothing, and the first call to `quote_standard` loads the table. `test_a_lazy_import_loads_the_table_on_first_use` runs that in a fresh `python -I` interpreter, so test order can't decide the answer. After `import singleton.quoting` the load log is empty and `singleton.tariff_table` isn't in `sys.modules`. After the first quote the log holds one `"tariff"` and the module is present.

Threads racing on that first use load it once. PEP 810 says so in its thread-safety section: "Exactly one thread performs the import and atomically rebinds the importing module’s global to the resolved object." `test_threads_racing_on_a_lazy_import_load_the_table_once` releases eight threads together from a barrier and finds one load and eight equal quotes. The race isn't forced. Nothing makes the threads overlap inside the import, so the test asserts the outcome and the claim rests on the PEP. The recorded evidence agrees: twenty fresh interpreters ran the same code, and all twenty loaded once.

A lazy import moves failures as well as work. The What's New page puts it this way: "Python raises the exception at the point of first use rather than at import time." PEP 810 adds that a failed reification doesn't replace the lazy object, so "subsequent uses of the lazy object will retry the whole reification". A broken rates file shows up at the first quote, not at start-up.

Two limits. The What's New page says "Lazy imports are only permitted at module scope; using lazy inside a function, class body, or try/except/finally block raises a SyntaxError." And mypy treats the import as an ordinary one. `test_mypy_still_checks_attributes_through_a_lazy_import` misspells `TARIFF` as `TARIF` through a lazy import, and the test's own run prints:

```text
<string>:6: error: Returning Any from function declared to return "int"  [no-any-return]
<string>:6: error: Module has no attribute "TARIF"; maybe "TARIFF"?  [attr-defined]
```

Rhodes prefers the global object to the Singleton class for reasons that make this rung the default: a reader recognises a module-level assignment at a glance, and a test can still build a table of its own. His Global Object page also warns that mutable global objects "can wind up coupling distant code". The tariff table is a frozen dataclass over a `frozendict`, so readers can't change it.

## Pass the table in

A module-level table doesn't suit every caller. A test wants a table of its own, and a tenant wants theirs. `quote` takes the table as a parameter, and `quote_standard` is the one place that reaches for the module's.

`test_quote_takes_the_table_it_is_given` prices the same consignment against two tables and gets 12.00 from one and 50.00 from the other, with the load log unchanged. Nothing is patched and no module state is touched. [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers where a composition root passes such a parameter in. [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) covers the alternative, patching module state, and what it costs.

The failure this avoids is the cached loader. `test_isolation.py` holds `_cached_tariff`, decorated with `functools.cache`, which builds a `TariffTable` from the standard rates merged with a module-level `_OVERRIDES` dict. `test_a_cached_loader_carries_one_tests_table_into_the_next` sets an override for Asia and loads. The next phase clears the override and asks again, and the cache returns the table with the override still in it: Asia still reads 9, where the standard table says 2.40. The test's fixture calls `cache_clear()` after each test for that reason, and `test_cache_clear_resets_the_cached_loader` shows the reset working. `cache_clear` is the repair when a cache can't be avoided. It isn't a design: a test that touches the cache has to know to call it.

The [functools documentation](https://docs.python.org/3.15/library/functools.html) describes `functools.cache` as a "Simple lightweight unbounded function cache". It memoises a function's results by argument. A single instance is a different requirement.

## Once, under threads

Some loads can't run at import time or on first use of a module, because they need something that exists only at run time: a path from configuration, a connection, a tenant's identifier. The table is then built by a callable, and the question is what makes that callable run once.

Not `functools.cache`. The same page says: "Call-once behavior is not guaranteed because locks are not held during the function call." It also says it is "possible for the wrapped function to be called more than once if another thread makes an additional call before the initial call has been completed and cached". `test_functools_cache_runs_a_loader_twice_when_two_threads_arrive_together` puts a `Barrier(2)` inside the loader, so both threads are inside the call before either returns, and finds two loads and two different tables. The cache is thread-safe in the sense the docs give, a coherent dictionary, and not once.

`LoadOnce` is the lock with a double check:

<!-- fmt:off -->
```python
NOT_LOADED = sentinel("NOT_LOADED")


class LoadOnce[T]:
    """Call `load` the first time, keep the result, and read it without the lock afterwards.

    The lock is injected so a test can place both threads between the first check and the lock.
    """

    def __init__(
        self,
        load: Callable[[], T],
        *,
        lock: AbstractContextManager[object, None] | None = None,
    ) -> None:
        self._load = load
        self._lock = lock if lock is not None else threading.Lock()
        self._value: T | NOT_LOADED = NOT_LOADED

    def __call__(self) -> T:
        if self._value is NOT_LOADED:
            with self._lock:
                if self._value is NOT_LOADED:
                    self._value = self._load()
        return self._value
```
<!-- fmt:on -->

The first check lets a caller that finds a loaded value return without touching the lock. The second, inside the lock, lets a thread that waited find that someone else has loaded in the meantime. `test_a_loaded_value_is_read_without_taking_the_lock` uses a counting lock: the first call enters it once, and three more calls leave the count at one.

The inner check needs an interleaving, and the test forces it with a lock that makes two threads meet at its door:

<!-- fmt:off -->
```python
    def __init__(self) -> None:
        self._gate = threading.Barrier(2, timeout=_GUARD_SECONDS)
        self._lock = threading.Lock()
        self.entries = 0

    def __enter__(self) -> None:
        self._gate.wait()
        self._lock.acquire()
        self.entries += 1
```
<!-- fmt:on -->

The lock is injected through `lock=`, which defaults to `threading.Lock()`. Both threads have passed the first check by the time they wait on the barrier in `__enter__`, so the only way forward is through the second check. `test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check` finds one load, the same table from both threads and two entries to the lock. Nothing sleeps. The Barrier timeout is a guard that a healthy run never reaches. Why threads interleave at all is the subject of [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}).

The marker is `NOT_LOADED`, built with the `sentinel` type that Python 3.15 adds. The What's New page, for PEP 661 by Tal Einat, says the type is "for creating unique sentinel values with a concise representation". A loader may return `None`, so `None` can't mark "not loaded yet". `test_load_once_keeps_a_loader_that_returns_none` runs a loader that returns `None` three times and finds one call. A loader that raises leaves the marker in place, and `test_a_failed_load_is_tried_again` finds two attempts and then `"ok"`.

## Borg, the metaclass, and `__new__`

Three class forms sit beside the ladder. They are fixtures in `tests/conftest.py`, they stand for code a team inherits or an assistant writes, and each has one measured cost. They run the same behaviour table as the module. The `__new__` form:

<!-- fmt:off -->
```python
class _NewTariffTable:
    """The `__new__` form: one instance, and `__init__` runs on every call."""

    _instance: ClassVar[Self | None] = None
    loads: ClassVar[list[str]] = []

    def __new__(cls, source: str) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, source: str) -> None:
        self.loads.append(source)
        self.source = source
        self.rates = _SOURCES[source]
```
<!-- fmt:on -->

Rhodes's page notes the quirk that drives the cost: `__init__()` is called on the result of the class call "whether the object that’s being returned is new or not". `test_a_new_based_singleton_reruns_init_on_every_call` makes two calls with two sources. The two calls return the same object, and its `source` is now `express.csv`. The first caller's table was overwritten by the second caller's, and the load list records both.

The metaclass fixture has the opposite problem. `_SingletonMeta.__call__` builds the instance on the first call and returns it on every later one, so `test_a_singleton_metaclass_ignores_the_second_calls_arguments` finds that the second call, `meta_table("express.csv")`, gives back the standard table, with `source` still `standard.csv` and one entry in the load list. mypy doesn't flag the ignored argument, because it types the call by `__init__`. In a reduced model of the metaclass, `test_mypy_types_a_metaclass_singleton_call_by_init` accepts a second call with a different argument, and a call with none prints:

```text
<string>:18: error: Missing positional argument "source" in call to "TariffTable"  [call-arg]
```

The signature is checked on every call, and the singleton rule that makes later arguments meaningless isn't. The mechanics of `__call__` on a metaclass are the business of [Metaclasses, __init_subclass__, and registries]({{ '/docs/29-metaclasses-init-subclass-and-registries/' | relative_url }}).

Borg shares state and not identity. `test_borg_instances_share_state_but_are_distinct_and_unequal` makes two instances: they aren't the same object, they compare unequal, and they share one `__dict__`, so an attribute set through one is read through the other. Martelli's recipe is the source of the idea. mypy accepts the assignment of a shared dictionary to `__dict__`, and `test_mypy_accepts_borg_state_unless_the_class_has_slots`, on a reduced model, shows that mypy refuses the assignment with `[misc]` once the class declares `__slots__`. Code that compares two Borg instances for equality gets "different" about objects that hold identical state.

Borg suits code that must construct its own object and still share configuration with every other. A class form suits the case where the class itself has to be the access point, and Rhodes names it: an existing class that has become single and can't have its callers migrated. Neither is the default, and a module covers the rest.

## When not to use it

Pass a parameter when state differs per test, per tenant or per request. If the "singleton" is a cache, write a cache and name it one, with an eviction rule and a reset. When several threads write to one mutable global, the lock is the smaller problem, and the design needs a different shape. A class whose only reason to exist is to be single is a module.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a singleton.** "A singleton" leaves open when the instance is built, how a test or a tenant gets its own, and what happens when two threads ask first. Paste a prompt that states the form:

> Build `TARIFF` at import time in `tariff_table`, or reach it with `lazy from singleton import tariff_table` to load it on first use. Take the table as a parameter of `quote`, so tests and tenants pass their own. If the load needs run-time input, use `LoadOnce`: a lock with a double check and a `sentinel` marker. Don't use `functools.cache` as call-once, and don't override `__new__` or write a metaclass.

If the reply claims call-once under threads, ask for the `Barrier` test that forces the race.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/18-singleton-module-borg-metaclass
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
collecting ... collected 29 items

tests/test_isolation.py::test_a_naive_class_loads_the_table_once_per_caller PASSED [  3%]
tests/test_isolation.py::test_a_cached_loader_carries_one_tests_table_into_the_next PASSED [  6%]
tests/test_isolation.py::test_cache_clear_resets_the_cached_loader PASSED [ 10%]
tests/test_module.py::test_every_importer_gets_the_one_tariff_table PASSED [ 13%]
tests/test_module.py::test_a_lazy_import_loads_the_table_on_first_use PASSED [ 17%]
tests/test_module.py::test_threads_racing_on_a_lazy_import_load_the_table_once PASSED [ 20%]
tests/test_module.py::test_quote_takes_the_table_it_is_given PASSED      [ 24%]
tests/test_module.py::test_an_unknown_zone_is_a_rating_error PASSED      [ 27%]
tests/test_module.py::test_the_tariff_table_is_a_frozen_value PASSED     [ 31%]
tests/test_once.py::test_functools_cache_runs_a_loader_twice_when_two_threads_arrive_together PASSED [ 34%]
tests/test_once.py::test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check PASSED [ 37%]
tests/test_once.py::test_a_loaded_value_is_read_without_taking_the_lock PASSED [ 41%]
tests/test_once.py::test_load_once_keeps_a_loader_that_returns_none PASSED [ 44%]
tests/test_once.py::test_the_not_loaded_marker_is_a_sentinel_and_not_none PASSED [ 48%]
tests/test_once.py::test_a_failed_load_is_tried_again PASSED             [ 51%]
tests/test_static.py::test_mypy_types_a_metaclass_singleton_call_by_init[second-call] PASSED [ 55%]
tests/test_static.py::test_mypy_types_a_metaclass_singleton_call_by_init[missing-argument] PASSED [ 58%]
tests/test_static.py::test_mypy_accepts_borg_state_unless_the_class_has_slots[plain] PASSED [ 62%]
tests/test_static.py::test_mypy_accepts_borg_state_unless_the_class_has_slots[slotted] PASSED [ 65%]
tests/test_static.py::test_mypy_still_checks_attributes_through_a_lazy_import PASSED [ 68%]
tests/test_variants.py::test_every_form_gives_each_caller_the_same_rates[module] PASSED [ 72%]
tests/test_variants.py::test_every_form_gives_each_caller_the_same_rates[load-once] PASSED [ 75%]
tests/test_variants.py::test_every_form_gives_each_caller_the_same_rates[borg] PASSED [ 79%]
tests/test_variants.py::test_every_form_gives_each_caller_the_same_rates[metaclass] PASSED [ 82%]
tests/test_variants.py::test_every_form_gives_each_caller_the_same_rates[cache] PASSED [ 86%]
tests/test_variants.py::test_every_form_gives_each_caller_the_same_rates[new] PASSED [ 89%]
tests/test_variants.py::test_borg_instances_share_state_but_are_distinct_and_unequal PASSED [ 93%]
tests/test_variants.py::test_a_singleton_metaclass_ignores_the_second_calls_arguments PASSED [ 96%]
tests/test_variants.py::test_a_new_based_singleton_reruns_init_on_every_call PASSED [100%]

============================== 29 passed in 2.14s ==============================
Success: no issues found in 12 source files
```

The suite has 22 test functions and 29 cases. For how the tests and the mypy witnesses are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: drop the inner check.** In a fresh scratch copy, replace the inner `if self._value is NOT_LOADED:` and its body in `LoadOnce.__call__` with a bare `self._value = self._load()` inside the lock. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests` three times printed the same lines each time, apart from the duration:

```text
E       AssertionError: assert ['tariff', 'tariff'] == ['tariff']
tests/test_once.py:105: AssertionError
FAILED tests/test_once.py::test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check
1 failed, 28 passed in 2.16s
Success: no issues found in 12 source files
```

Both threads got through the first check before either took the lock, so both loaded. mypy still reports success, because a second load is a valid program.

**Experiment two: make the import eager.** In a fresh scratch copy, change `lazy from singleton import tariff_table` in `quoting.py` to `from singleton import tariff_table`. The same filtered run and mypy run, three times, printed:

```text
E       AssertionError: assert {'before': ['...r': True, ...} == {'before': []...r': True, ...}
tests/test_module.py:90: AssertionError
FAILED tests/test_module.py::test_a_lazy_import_loads_the_table_on_first_use
1 failed, 28 passed in 2.14s
Success: no issues found in 12 source files
```

The test's fresh interpreter finds the load log already holding `"tariff"` after the import alone, so the first-use claim fails. mypy stays green again, since an eager import is also a valid one.

## What you can do now

- Say which of three things "Singleton" means: `test_every_form_gives_each_caller_the_same_rates` runs six forms of one object, one shared state and one class that returns the same object, and five load once.
- Climb the ladder in order: `TARIFF`, the `lazy` import, `quote(..., table=...)` and `LoadOnce`.
- Show a forced race: the `Barrier(2)` test finds `functools.cache` running a loader twice.
- Name the cost of each class form: Borg shares state without identity, a metaclass ignores the second call's arguments, and `__new__` reruns `__init__`.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Singleton. Alex Martelli's [ActiveState recipe 66531](https://web.archive.org/web/20260325075452/https://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/), "Singleton? We don't need no stinkin' singleton: the Borg design pattern", is the source for Borg. Brandon Rhodes covers the two ends of the argument at [The Singleton Pattern](https://python-patterns.guide/gang-of-four/singleton/) and [The Global Object Pattern](https://python-patterns.guide/python/module-globals/). [PEP 810](https://peps.python.org/pep-0810/) specifies `lazy import`, [PEP 661](https://peps.python.org/pep-0661/) specifies `sentinel`, and the [functools](https://docs.python.org/3.15/library/functools.html) and [threading](https://docs.python.org/3.15/library/threading.html) documentation cover `cache`, `Lock` and `Barrier`. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
