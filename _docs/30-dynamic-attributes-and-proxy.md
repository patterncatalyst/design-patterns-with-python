---
title: "Dynamic attributes: __getattr__ and Proxy as a feature"
order: 30
layout: tutorial
sectionid: docs
part: "idiomatic-python"
description: "An object that loads its own fields on first access, and how to keep &#95;&#95;getattr&#95;&#95; out of recursion and consistent with dir, copy and mypy."
---

## Learning objectives

By the end of this chapter you can:

- Load a record's fields once, on first access, with `__getattr__`.
- Predict when `__getattr__` and `__getattribute__` run.
- Keep `__getattr__` out of recursion, under `copy` too.
- Make a dynamic object consistent with `dir()`, special-method lookup and mypy.
- Deprecate a module name with a module-level `__getattr__`.

## Why this matters

A tracking history comes from a carrier feed that is slow to read, and most callers want only the consignment id. The catalogue's virtual proxy answers that with a stand-in that creates the expensive object when it's first needed, and *Design Patterns* by Gamma, Helm, Johnson and Vlissides (1994) lists it under Proxy. In Python the object can do that for itself: `__getattr__` runs when ordinary lookup fails, so a history declares its fields, loads them on the first read and keeps them as plain attributes. That's interception with no surrogate, which is where Proxy is disambiguated in [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}). The surrogate itself is in [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}). Martin Fowler's *Patterns of Enterprise Application Architecture* (2002) catalogues Lazy Load for the same need.

What stays design is which names may load, and how the object behaves under the rest of the language. Three things go wrong in the obvious versions.

A `__getattr__` that reads an attribute it doesn't own recurses as soon as the history is copied (`test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute`).

A `__getattr__` that answers every name turns a misspelt field into `None` (`test_a_getattr_that_returns_none_hides_a_typo`).

mypy accepts a misspelt field read, and reports only what the program does with the result (`test_mypy_types_an_unknown_attribute_by_the_getattr_return_type`).

{% include excalidraw.html name="30-dynamic-attributes-and-proxy" caption="Figure 30.1: A read that ordinary lookup can't answer reaches __getattr__, which loads the declared fields once into the instance dictionary and refuses any other name. Later reads skip it, and a class that relies on forwarding fails iter() and len()." %}

Read the figure from the top down. `history.status` goes to `__getattribute__` ("normal lookup: class, instance dict"). An arrow labelled "found" runs right to a box reading "value", and an arrow labelled `AttributeError` runs down to the accent box `TrackingHistory.__getattr__` ("runs when ordinary lookup fails"). Two arrows leave that box. The left one goes to "name in the lazy set" (`events`, `status` or `last_port`), then `load(consignment_id)` ("reads the feed once per history"), then `vars(self).update`, then "value" ("later reads find it in the instance dict"). The right one goes to "any other name" ("refused before anything is loaded") and then `AttributeError`, "a near miss gets a Did you mean hint built from `__dir__`". Two dashed boxes sit at the bottom right. The first reads "iter() and len() look up the type", for a class that relies on forwarding through `__getattr__`. The second reads "a `__getattr__` that reads a missing attribute recurses when copy builds an instance".

## A history that loads itself

<!-- fmt:off -->
```python
    def __init__(
        self,
        consignment_id: ConsignmentId,
        load: Callable[[ConsignmentId], Iterable[HandlingEvent]],
    ) -> None:
        self.consignment_id = consignment_id
        self._load = load

    def __getattr__(self, name: str) -> object:
        """Load the lazy fields once.

        The allow-list comes first because this method reads ``self._load``: on an instance whose
        ``__init__`` never ran (``copy`` and ``pickle`` build one), that read would reach this
        method again for a name it does not own. Refusing every name outside ``_LAZY`` ends it.
        """
        if name not in _LAZY:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        events = tuple(self._load(self.consignment_id))
        # Write around __setattr__, which refuses the lazy names.
        vars(self).update(
            events=events,
            status=_STATUS_AFTER[events[-1].kind] if events else None,
            last_port=events[-1].port if events else None,
        )
        return vars(self)[name]
```
<!-- fmt:on -->

`TrackingHistory` declares `events`, `status` and `last_port` as class annotations with no values, so mypy knows their types and the instance dictionary holds only `consignment_id` and `_load` (`test_nothing_is_loaded_until_a_field_is_read`). `load` arrives as a parameter, so the tests count loads with a recording callable and need no mock. The first read of any lazy name calls `load` and fills all three fields, so one feed read serves them all (`test_every_history_form_loads_once_for_every_field`). From then on they're ordinary instance attributes (`test_a_loaded_history_reads_its_fields_from_the_instance_dict`). The data model gives the rule: "Note that if the attribute is found through the normal mechanism, __getattr__() is not called." Iterating a history reads `events`, so it loads too (`test_iterating_a_history_loads_it`). A consignment with no events gets `None` for both `status` and `last_port`, as the `empty` row of `test_every_history_form_reads_the_loaded_fields` checks.

The same table runs against a `cached_property` form that lives in the test fixtures, with four consignments, one of them empty (`test_every_history_form_reads_the_loaded_fields`), and both forms pass.

<!-- fmt:off -->
```python
    @cached_property
    def _events(self) -> tuple[HandlingEvent, ...]:
        return tuple(self._load(self.consignment_id))

    @property
    def status(self) -> ConsignmentStatus | None:
        return _STATUS_OF[self._events[-1].kind] if self._events else None
```
<!-- fmt:on -->

That form needs one read-only property per field, so a fourth field is a fourth property. [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) owns `cached_property` and its mechanics. Both forms load once. After the load, the `cached_property` form still runs a property on every read, while the `__getattr__` form leaves plain instance attributes. The `__getattr__` form pays for that with the care the next sections describe, and it suits a record whose fields arrive together.

## When each hook runs

Brandon Rhodes's page on the Decorator pattern, in its section on dynamic wrappers, says `__getattr__()` is "only invoked for attributes that are in fact missing on the wrapper". A counting subclass shows it. Three reads of `status` log one `__getattr__` call, and a read of `consignment_id` logs none (`test_getattr_runs_only_when_normal_lookup_fails`). `__getattribute__` is the hook that sees every read:

<!-- fmt:off -->
```python
    class Counting(TrackingHistory):
        def __getattribute__(self, name: str) -> object:
            seen.append(name)
            return super().__getattribute__(name)
```
<!-- fmt:on -->

Its log holds `consignment_id` after one read of that name, and `status` three times after three reads (`test_getattribute_runs_on_every_access`). The data model warns that overriding it invites recursion: it says that, to avoid infinite recursion, "its implementation should always call the base class method with the same name to access any attributes it needs, for example, object.__getattribute__(self, name)." `TrackingHistory` defines no `__getattribute__`. It would charge every read for a job that the first failed read does once, and the load needs no other hook.

## The recursion trap

<!-- fmt:off -->
```python
class _SelfHealing:
    """The trap: ``__getattr__`` reads ``self._load``, which is missing on a bare instance."""

    def __init__(self, load: Callable[[str], str]) -> None:
        self._load = load

    def __getattr__(self, name: str) -> object:
        value = self._load(name)
        vars(self)[name] = value
        return value
```
<!-- fmt:on -->

This is a reduced model. On one whose `__init__` never ran, reading `self._load` is a failed lookup, which calls `__getattr__("_load")`, which reads `self._load` again (`test_a_getattr_that_reads_a_missing_attribute_recurses`, a `RecursionError`).

`copy` builds such an instance. The copy documentation says "Classes can use the same interfaces to control copying that they use to control pickling", and the pickle documentation says "When a class instance is unpickled, its __init__() method is usually not invoked." It also says "At unpickling time, some methods like __getattr__(), __getattribute__(), or __setattr__() may be called upon the instance." The test runs `copy.copy`, `copy.deepcopy` and a `pickle` round trip over `_SelfHealing`, and each raises `RecursionError` (`test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute`). The loader in that test knows only the one field and raises `AttributeError` for other names. A loader that answered every name would make `deepcopy` fail first, with a `TypeError`, on the string it got back for `__deepcopy__` (`test_deepcopy_fails_with_a_type_error_when_the_loader_answers_every_name`).

Three fixes keep the hook out of the loop (`test_each_fix_keeps_getattr_out_of_recursion`). Refuse names outside a fixed set, which `TrackingHistory` does. Read the loader with `object.__getattribute__`. Or read it from `vars(self)`. Each is enough on its own, and each makes a bare instance raise `AttributeError` for `events`. `TrackingHistory` copies correctly both before loading, where the copy holds `_load` and `consignment_id` and loads nothing, and after, where the copy keeps the fields (`test_copy_keeps_a_history_before_and_after_loading`).

The set is also the defence against the opposite mistake. A `__getattr__` that answers every name from a mapping returns `None` for `stauts` (`test_a_getattr_that_returns_none_hides_a_typo`), where the allow-list raises `AttributeError` (`test_every_history_form_raises_attribute_error_for_a_misspelt_field`).

## Consistent with the rest of Python

<!-- fmt:off -->
```python
    def __setattr__(self, name: str, value: object) -> None:
        if name in _LAZY:
            raise AttributeError(f"{name!r} is loaded, not assigned")
        object.__setattr__(self, name, value)

    def __dir__(self) -> list[str]:
        return sorted({*object.__dir__(self), *_LAZY})

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self.events)
```
<!-- fmt:on -->

The loaded fields are a fact from the feed, so assigning one is refused, in both forms (`test_every_history_form_refuses_assignment_to_a_loaded_field`). The data model says `__setattr__` "is called instead of the normal mechanism (i.e. store the value in the instance dictionary)", which is why the load writes through `vars(self)` and goes around it. The same page calls the pair "an intentional asymmetry": `__setattr__` runs on every assignment, and `__getattr__` only on a failed lookup.

The built-ins documentation for `dir` says a `__dir__` method "allows objects that implement a custom __getattr__() or __getattribute__() function to customize the way dir() reports their attributes". Without it, `dir(history)` omits fields that haven't loaded. With it, `dir()` lists them and loads nothing (`test_dir_lists_the_lazy_fields_before_loading`), and a misspelt field earns the interpreter's suggestion. On 3.15.2, `history.stauts` raises `AttributeError: 'TrackingHistory' object has no attribute 'stauts'. Did you mean '.status' instead of '.stauts'?`, and a subclass whose `__dir__` leaves the names out gets no hint (`test_a_misspelt_field_suggests_the_declared_name_through_dir`). The suggestion's wording comes from the interpreter.

Special methods are looked up on the type. The data model says that "For custom classes, implicit invocations of special methods are only guaranteed to work correctly if defined on an object’s type, not in the object’s instance dictionary." So a class that relies on `__getattr__` to forward `__iter__` has none: `iter()` and `len()` raise `TypeError` without the hook running, although reading `forwarding.__iter__` by name reaches the hook (`test_implicit_special_method_lookup_bypasses_getattr`, a forwarding class defined in the test). That's why `TrackingHistory` writes `__iter__`. [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) quotes the same rule for its forwarding proxy.

`hasattr(history, "status")` is a read, so checking for a lazy field reads the feed (`test_hasattr_loads_the_history`).

## What mypy sees

The declared annotations keep their types: assigning `h.status` to an `int` is an `[assignment]` error about `ConsignmentStatus | None` (`test_mypy_keeps_the_declared_field_types`). A name that isn't declared is typed as `__getattr__`'s return, `object`. mypy 2.4.1 reveals `h.stauts` as `object` and reports one `[attr-defined]` error, on `.upper()` and not on the misspelling (`test_mypy_types_an_unknown_attribute_by_the_getattr_return_type`). The typo is reported only when the result is used in a way `object` rejects.

mypy accepts `h.status = None`, which matches the declared type, and, because `__setattr__` takes any name, `h.anything = 1`. At run time the first raises `AttributeError` with "is loaded, not assigned", and the second creates an attribute (`test_mypy_accepts_an_assignment_that_setattr_refuses`).

The `cached_property` form has no `__getattr__`, so mypy names the typo. On a reduced model with one `cached_property`, it prints `maybe "status"?` (`test_mypy_reports_a_typo_on_the_cached_property_form`). A forwarding `__getattr__` typed `Any` accepts a typo outright, which [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) measures.

## A module-level __getattr__

A module can define `__getattr__` too. PEP 562, by Ivan Levkivskyi, gives its first use: "A typical example is managing deprecation warnings." Suppose `LazyTrackingHistory` is the history's old name, kept for old imports:

<!-- fmt:off -->
```python
def __getattr__(name: str) -> type[TrackingHistory]:
    """The module's old name for the history, which warns and returns the new one."""
    if name == "LazyTrackingHistory":
        warnings.warn(
            "LazyTrackingHistory is deprecated; use TrackingHistory",
            DeprecationWarning,
            stacklevel=2,
        )
        return TrackingHistory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*globals(), "LazyTrackingHistory"})
```
<!-- fmt:on -->

`tracking.LazyTrackingHistory` warns and returns `TrackingHistory`, and the warning is attributed to the file that asked for the name, because of `stacklevel=2` (`test_a_deprecated_name_warns_and_returns_the_tracking_history`). Any other missing name raises `AttributeError` naming the module (`test_an_unknown_module_attribute_raises_attribute_error`), and `dir(tracking)` lists the old name (`test_module_dir_lists_the_deprecated_name`). The data model limits the hook: "only affect lookups made using the attribute access syntax". A read through `globals()` inside the module never calls it.

mypy accepts any name imported through the hook. `from dynamic_attributes.tracking import Anything` type-checks with exit 0, as `type[TrackingHistory]`, and fails with `ImportError` at run time (`test_mypy_accepts_any_name_imported_through_a_module_getattr`).

PEP 562 also names a second use: "Another widespread use case for __getattr__ would be lazy submodule imports." On 3.15 the importing side has `lazy import`, from [PEP 810](https://peps.python.org/pep-0810/) by Pablo Galindo Salgado and co-authors, which [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) uses. Deprecation is the use that stays with the module hook.

## When not to use it

One lazy field is a `cached_property`, which says so in one place: [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) covers it. Fields that aren't known when the class is written belong in a mapping, not in attributes. Wrapping another object's interface wants an explicit proxy, as [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) shows. And anything a plain `property` says more directly doesn't need an interception hook.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a lazy object.** "Lazy loading" leaves open which names `__getattr__` may load, and a hook that fetches or forwards whatever name is missing recurses under `copy` and turns a typo into a fetch. Paste a prompt that states the form:

> Declare `TrackingHistory`'s loaded fields as class annotations. Write `__getattr__` to load only the names in a fixed set, store them with `vars(self).update(...)`, and raise `AttributeError` for every other name. Refuse assignment to loaded fields in `__setattr__`, list them in `__dir__`, and define `__iter__` explicitly. For a single lazy value, use `functools.cached_property` instead.

If `__getattr__` reads an attribute it doesn't own, ask what `copy.copy` does.
</blockquote>

## Build, run, observe

The example has 27 test functions and 41 cases. From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/30-dynamic-attributes-and-proxy
uv run pytest -v
uv run mypy --strict src tests
```

All 41 cases pass, and mypy reports no issues. Both experiments below run in a fresh scratch copy of the repository, so the real example doesn't change. Each prints the output of this filter, then mypy:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'
uv run mypy --strict src tests
```

**Experiment one: delete `__dir__`.** Remove the `__dir__` method from `TrackingHistory`. The filter, then mypy, prints:

```text
E       AssertionError: assert [] == ['events', 'l...rt', 'status']
E         Right contains 3 more items, first extra item: 'events'
E         Use -v to get more diff
tests/test_lookup.py:201: AssertionError
E       assert False
tests/test_lookup.py:224: AssertionError
FAILED tests/test_lookup.py::test_dir_lists_the_lazy_fields_before_loading - ...
FAILED tests/test_lookup.py::test_a_misspelt_field_suggests_the_declared_name_through_dir
2 failed, 39 passed in 2.51s
Success: no issues found in 7 source files
```

Two tests fail. `dir()` no longer lists the lazy fields, and the misspelt field gets no "Did you mean" suffix. Nothing else notices, and mypy exits 0, since no type mentions `__dir__`.

**Experiment two: delete the allow-list.** Remove the `if name not in _LAZY:` check and its `raise` from `__getattr__`, so every missing name loads. The filter, then mypy, prints:

```text
E       KeyError: 'stauts'
E   RecursionError: maximum recursion depth exceeded
E   RecursionError: maximum recursion depth exceeded
E       KeyError: 'stauts'
FAILED tests/test_history.py::test_every_history_form_raises_attribute_error_for_a_misspelt_field[getattr]
FAILED tests/test_lookup.py::test_copy_keeps_a_history_before_and_after_loading
FAILED tests/test_lookup.py::test_each_fix_keeps_getattr_out_of_recursion[allow-list]
FAILED tests/test_lookup.py::test_a_misspelt_field_suggests_the_declared_name_through_dir
4 failed, 37 passed in 2.49s
Success: no issues found in 7 source files
```

A typo now loads the feed, then fails in `vars(self)[name]` with a `KeyError` where `AttributeError` is expected, in the misspelt-field test and in the hint test. The two copy-related tests fail with `RecursionError`: the bare instance that `copy` builds has no `_load`, and the unguarded hook keeps asking for it. mypy exits 0 again, because deleting a guard leaves every type as it was.

## What you can do now

- Load a record's fields once: `TrackingHistory`, with `test_every_history_form_loads_once_for_every_field` showing one feed read for three fields.
- Predict the hooks: `test_getattr_runs_only_when_normal_lookup_fails` for the one `__getattr__` call and `test_getattribute_runs_on_every_access` for the call on every read.
- Keep `__getattr__` out of recursion: `test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute` for the trap and `test_each_fix_keeps_getattr_out_of_recursion` for the three fixes.
- Make the object consistent with `dir()`, special-method lookup and mypy: `__dir__` with `test_a_misspelt_field_suggests_the_declared_name_through_dir`, an explicit `__iter__` because `test_implicit_special_method_lookup_bypasses_getattr` shows `iter()` skipping the hook, and the `object` that mypy reveals in `test_mypy_types_an_unknown_attribute_by_the_getattr_return_type`.
- Deprecate a module name: `LazyTrackingHistory`, with `test_a_deprecated_name_warns_and_returns_the_tracking_history`.

## For deeper coverage

The data model's [customising attribute access](https://docs.python.org/3/reference/datamodel.html) and special method lookup sections are the reference for the hooks, and the [built-in functions](https://docs.python.org/3/builtins/functions.html), [copy](https://docs.python.org/3/library/copy.html) and [pickle](https://docs.python.org/3/library/pickle.html) pages cover `dir`, `copy` and unpickling. [PEP 562](https://peps.python.org/pep-0562/), by Ivan Levkivskyi, specifies module `__getattr__` and `__dir__`, and [PEP 810](https://peps.python.org/pep-0810/) specifies `lazy import`. Brandon Rhodes's [The Decorator Pattern](https://python-patterns.guide/gang-of-four/decorator-pattern/) describes the dynamic wrapper. *Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Proxy, Martin Fowler's *Patterns of Enterprise Application Architecture* for Lazy Load, and *Fluent Python*, second edition, by Luciano Ramalho, is the broader reference for the data model and dynamic attributes. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
