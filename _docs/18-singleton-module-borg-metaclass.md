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
- Show with a forced race that `functools.cache` memoises and doesn't run a loader once under threads.
- Name the cost of Borg, of a metaclass singleton and of the `__new__` form.

## Why this matters

A tariff table is loaded from rates and read by every quote. The rates are illustrative. The obvious versions fail three ways:

- A class that each call site constructs loads the table once per caller, so two call sites make two loads.
- A cached loader hands one test's table to the next. The first test overrides a rate and loads; the next clears the override and still prices Asia at the first test's rate, because the cache held the table and not the override.
- Two threads reach a cached loader together and both run it. The cache is correct as a cache, and it never promised a single call.

{% include excalidraw.html name="18-singleton-module-borg-metaclass" described="true" caption="Figure 18.1: Four ways to load the tariff table once, in the order to reach for them. A module, a lazy import and a parameter come first; the class forms beside them each cost something the tests measure." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-18-singleton-module-borg-metaclass" markdown="1">
The ladder on the left runs from the top, each box with an arrow down to the next: `tariff_table`, a module built at import time; `lazy from ... import tariff_table`, built on first use, once; `quote(..., table=...)`, where the table is passed in so tests and tenants get their own; and `LoadOnce`, a lock with a double check for a load that needs run-time input. A dashed arrow runs from `LoadOnce` to an accent box that says `functools.cache` memoises and is not call-once. The right-hand column is muted, with dashed borders and no arrows: `Borg` (shared state, distinct objects), `SingletonMeta` (second call's arguments ignored) and `__new__` (reruns `__init__`). Those three are fixtures, not part of `src/`.
</div>
</details>

The figure puts the four rungs in the order to reach for them, with the class forms set aside.

## Pattern: Singleton

### The problem

Every quote reads the same tariff table. It should load once, under threads too, and tests and tenants still need tables of their own.

### The solution

A **Singleton** is a class that guards its own construction so the whole program shares one object, fetched through an operation on the class.

**Bucket: needs disambiguating.** Python programmers say "singleton" for three things, and the default answer to the force, "load this once and let everyone read it", is the first of them: a module.

That's the *Design Patterns* (1994) definition. Brandon Rhodes, on ["The Singleton Pattern"](https://python-patterns.guide/gang-of-four/singleton/), shows the several meanings; three matter for design:

| Meaning | Python form | Source |
| --- | --- | --- |
| One object | a module, built once; every import returns it | Rhodes, ["The Global Object Pattern"](https://python-patterns.guide/python/module-globals/) |
| One shared state | Borg: many objects whose attributes live in one place | Alex Martelli, ActiveState recipe 66531, "Singleton? We don't need no stinkin' singleton: the Borg design pattern" |
| One class that returns the same object | a metaclass `__call__` or a `__new__` that returns a stored instance | the GoF shape |

[What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) shows the module shape, and [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) places Singleton in its bucket.

### How Python models it

`tariff_table.py` builds `TARIFF` at import time. Two imports give one `TARIFF` and one load. Across six forms (the module, `LoadOnce`, Borg, a metaclass singleton, a cached function and `__new__`), two callers read equal rates, and five load once. The `__new__` form loads twice, because `__init__` runs on every call.

Rhodes prefers the global object to the Singleton class: a reader recognises it at a glance, and a test can still build a table of its own. He warns that mutable global objects "can wind up coupling distant code", so the tariff table is a frozen dataclass over a `frozendict`.

### On first use, with a lazy import

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

[PEP 810](https://peps.python.org/pep-0810/) adds the `lazy` soft keyword. The [What's New page for 3.15](https://docs.python.org/3/whatsnew/3.15.html): "Python defers the actual module loading until the imported name is first used." In a fresh `python -I` interpreter, importing `singleton.quoting` loads nothing and leaves `singleton.tariff_table` out of `sys.modules`. The first quote loads the table once.

Threads racing on that first use load it once. PEP 810's thread-safety section: "Exactly one thread performs the import and atomically rebinds the importing module’s global to the resolved object." Eight threads released together from a barrier give one load and eight equal quotes. Nothing forces them to overlap inside the import, so the claim rests on the PEP.

| Lazy-import fact | Consequence |
| --- | --- |
| "Python raises the exception at the point of first use rather than at import time." | A broken rates file shows up at the first quote, not at start-up. |
| A failed reification "will retry the whole reification" on the next use (PEP 810) | The next quote tries the load again. |
| "Lazy imports are only permitted at module scope" | `lazy` in a function, class body or `try` block is a `SyntaxError`. |
| mypy treats it as an ordinary import | A misspelt attribute is still reported. |

Misspelling `TARIFF` as `TARIF` through a lazy import gives:

```text
<string>:6: error: Returning Any from function declared to return "int"  [no-any-return]
<string>:6: error: Module has no attribute "TARIF"; maybe "TARIFF"?  [attr-defined]
```

### Pass the table in

A test wants a table of its own, and so does a tenant. `quote` takes the table as a parameter, and `quote_standard` is the one place that reaches for the module's. The same consignment priced against two tables gives 12.00 and 50.00, with no load, no patch and no module state touched. [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) covers where a composition root passes it in, and [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}) covers what patching module state costs instead.

The failure this avoids is the cached loader: `_cached_tariff`, decorated with `functools.cache`, merges the standard rates with a module-level `_OVERRIDES` dict. Set an override for Asia and load, then clear the override and ask again, and Asia still reads 9 where the standard table says 2.40. `cache_clear()` after each test resets it. That's the repair when a cache can't be avoided, and it isn't a design: every test that touches the cache has to know to call it.

### Once, under threads

Some loads need something that exists only at run time: a path from configuration, a connection, a tenant's identifier. A callable builds the table, and the question is what makes it run once.

Not `functools.cache`. The [functools documentation](https://docs.python.org/3/library/functools.html) calls it a "Simple lightweight unbounded function cache" and says: "Call-once behavior is not guaranteed because locks are not held during the function call." With a `Barrier(2)` inside the loader, so both threads are inside the call before either returns, a cached loader runs twice and gives two different tables. The cache is thread-safe in the sense the docs give, a coherent dictionary, and not once.

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

| Check | Lets |
| --- | --- |
| outer, before the lock | a caller that finds a loaded value return without the lock |
| inner, inside the lock | a thread that waited find that another thread loaded meanwhile |

Once loaded, reads don't touch the lock. An injected lock that makes two threads meet at a `Barrier(2)` in `__enter__`, after both passed the outer check, forces the inner check: one load, the same table from both threads, and nothing sleeps. [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}) covers why threads interleave at all.

The marker is `NOT_LOADED`, built with the `sentinel` type that Python 3.15 adds under PEP 661 by Tal Einat and Jelle Zijlstra, "for creating unique sentinel values with a concise representation". A loader may return `None`, so `None` can't mark "not loaded yet": a loader that returns `None` is called once across three reads. A loader that raises leaves the marker in place, so the next call tries again.

### Borg, the metaclass, and `__new__`

Three class forms stand for code a team inherits. They're fixtures, not model code, and each has one cost. The `__new__` form:

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

| Form | Cost |
| --- | --- |
| `__new__` | `__init__` reruns: a second call with `express.csv` overwrites the first caller's table, and both loads are recorded |
| metaclass `__call__` | the second call's arguments are ignored: `meta_table("express.csv")` returns the standard table |
| Borg | shared state without identity: two instances share one `__dict__` but compare unequal |

Rhodes notes the `__new__` quirk: `__init__()` is called on the result "whether the object that’s being returned is new or not". mypy types a metaclass singleton's call by `__init__`, so it accepts a second call with a different argument and only reports a call with none:

```text
<string>:18: error: Missing positional argument "source" in call to "TariffTable"  [call-arg]
```

[Metaclasses, __init_subclass__, and registries]({{ '/docs/29-metaclasses-init-subclass-and-registries/' | relative_url }}) covers `__call__` on a metaclass. mypy accepts Borg's assignment of a shared dictionary to `__dict__`, and refuses it with `[misc]` once the class declares `__slots__`.

Borg suits code that must construct its own object and still share configuration. A class form suits an existing class that has become single and can't have its callers migrated, the case Rhodes names.

## When not to use it

- **Singleton.** Pass a parameter when state differs per test, per tenant or per request. If the "singleton" is a cache, write a cache and name it one, with an eviction rule and a reset. When several threads write to one mutable global, the lock is the smaller problem; change the shape. A class whose only reason to exist is to be single is a module.

> **🤖 Explore with your agent**
>
> "Build `TARIFF` at import time in `tariff_table`, or reach it with `lazy from singleton import tariff_table` to load it on first use. Take the table as a parameter of `quote`, so tests and tenants pass their own. If the load needs run-time input, use `LoadOnce`: a lock with a double check and a `sentinel` marker. Don't use `functools.cache` as call-once, and don't override `__new__` or write a metaclass."
>
> If the reply claims call-once under threads, ask for the `Barrier` test that forces the race.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/18-singleton-module-borg-metaclass
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 29 cases pass and mypy is clean. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) covers how the mypy checks are built. Two experiments, each in a fresh scratch copy:

- **Drop the inner check.** Replace the inner `if self._value is NOT_LOADED:` and its body in `LoadOnce.__call__` with a bare `self._value = self._load()` inside the lock. The forced race records `['tariff', 'tariff']` where one load was wanted, on every run. mypy is clean: a second load is a valid program.
- **Make the import eager.** Change `lazy from singleton import tariff_table` in `quoting.py` to `from singleton import tariff_table`. The fresh interpreter finds `"tariff"` in the load log after the import alone, so the first-use check fails. mypy is clean again.

## What you can do now

- Say which of three things "Singleton" means: one object, one shared state, or one class that returns the same object.
- Reach for `TARIFF`, then the `lazy` import, then `quote(..., table=...)`, and `LoadOnce` last.
- Force the race with `Barrier(2)` and watch `functools.cache` run a loader twice.
- Name each class form's cost: Borg shares state without identity, a metaclass ignores the second call's arguments, and `__new__` reruns `__init__`.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Singleton. Alex Martelli's [ActiveState recipe 66531](https://web.archive.org/web/20260325075452/https://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/), "Singleton? We don't need no stinkin' singleton: the Borg design pattern", is the source for Borg. Brandon Rhodes covers the two ends of the argument at [The Singleton Pattern](https://python-patterns.guide/gang-of-four/singleton/) and [The Global Object Pattern](https://python-patterns.guide/python/module-globals/). [PEP 810](https://peps.python.org/pep-0810/) specifies `lazy import`, [PEP 661](https://peps.python.org/pep-0661/) specifies `sentinel`, and the [functools](https://docs.python.org/3/library/functools.html) and [threading](https://docs.python.org/3/library/threading.html) documentation cover `cache`, `Lock` and `Barrier`. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
