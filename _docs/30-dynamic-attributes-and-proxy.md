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

A tracking history comes from a carrier feed that is slow to read, and most callers want only the consignment id. The virtual proxy in *Design Patterns* (1994) answers that with a stand-in that creates the expensive object when it's first needed. In Python the object can do it for itself: `__getattr__` runs when ordinary lookup fails, so a history declares its fields, loads them on the first read and keeps them as plain attributes. That's interception with no surrogate, which is where Proxy is disambiguated in [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}). The surrogate itself is in [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}). Martin Fowler's *Patterns of Enterprise Application Architecture* (2002) catalogues Lazy Load for the same need.

What stays design is which names may load, and how the object behaves under the rest of the language. The obvious versions fail three ways:

- A `__getattr__` that reads an attribute it doesn't own recurses as soon as the history is copied.
- A `__getattr__` that answers every name turns a misspelt field into `None`.
- mypy accepts a misspelt field read, and reports only what the program does with the result.

{% include excalidraw.html name="30-dynamic-attributes-and-proxy" described="true" caption="Figure 30.1: A read that ordinary lookup can't answer reaches __getattr__, which loads the declared fields once into the instance dictionary and refuses any other name. Later reads skip it, and a class that relies on forwarding fails iter() and len()." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-30-dynamic-attributes-and-proxy" markdown="1">
From the top down, `history.status` goes to `__getattribute__` ("normal lookup: class, instance dict"). An arrow labelled "found" runs right to a box reading "value", and an arrow labelled `AttributeError` runs down to the accent box `TrackingHistory.__getattr__` ("runs when ordinary lookup fails"). Two arrows leave that box. The left one goes to "name in the lazy set" (`events`, `status` or `last_port`), then `load(consignment_id)` ("reads the feed once per history"), then `vars(self).update`, then "value" ("later reads find it in the instance dict"). The right one goes to "any other name" ("refused before anything is loaded") and then `AttributeError`, "a near miss gets a Did you mean hint built from `__dir__`". Two dashed boxes sit at the bottom right. The first reads "iter() and len() look up the type", for a class that relies on forwarding through `__getattr__`. The second reads "a `__getattr__` that reads a missing attribute recurses when copy builds an instance".
</div>
</details>

The figure traces one read through normal lookup into `__getattr__`, which either loads the declared fields or refuses the name.

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

`TrackingHistory` declares `events`, `status` and `last_port` as class annotations with no values, so mypy knows their types and the instance dictionary holds only `consignment_id` and `_load` until a field is read. `load` arrives as a parameter, so a test counts loads with a recording callable and needs no mock.

The first read of any lazy name calls `load` once and fills all three fields. From then on they're ordinary instance attributes. The data model gives the rule: "Note that if the attribute is found through the normal mechanism, __getattr__() is not called." Iterating a history reads `events`, so it loads too. A consignment with no events gets `None` for both `status` and `last_port`.

The alternative is a `cached_property` with one read-only property per field:

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

| | `__getattr__` form | `cached_property` form |
| --- | --- | --- |
| Feed reads | one, for every field | one |
| Reads after the load | plain instance attributes | a property call each time |
| A new field | a name in `_LAZY` | another property |
| A misspelt field in mypy | typed `object`, not reported | `maybe "status"?` |

Both give the same fields for the same consignments. The `__getattr__` form suits a record whose fields arrive together. [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) covers `cached_property` itself.

## When each hook runs

Brandon Rhodes's page on the Decorator pattern, in its section on dynamic wrappers, says `__getattr__()` is "only invoked for attributes that are in fact missing on the wrapper". Three reads of `status` call `__getattr__` once, and a read of `consignment_id` doesn't call it. `__getattribute__` is the hook that sees every read: an override logs `status` three times after three reads.

The data model warns that overriding `__getattribute__` invites recursion: to avoid it, "its implementation should always call the base class method with the same name to access any attributes it needs, for example, object.__getattribute__(self, name)." `TrackingHistory` defines no `__getattribute__`. It would charge every read for a job the first failed read does once.

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

On an instance whose `__init__` never ran, reading `self._load` is a failed lookup, which calls `__getattr__("_load")`, which reads `self._load` again, and the result is `RecursionError`.

`copy` builds such an instance. The copy documentation says "Classes can use the same interfaces to control copying that they use to control pickling", and the pickle documentation says "When a class instance is unpickled, its __init__() method is usually not invoked." It also says "At unpickling time, some methods like __getattr__(), __getattribute__(), or __setattr__() may be called upon the instance." So `copy.copy`, `copy.deepcopy` and a `pickle` round trip over `_SelfHealing` each raise `RecursionError`. A loader that answered every name would make `deepcopy` fail first, with a `TypeError`, on the string it got back for `__deepcopy__`.

Three fixes keep the hook out of the loop, and each is enough on its own:

- Refuse names outside a fixed set, which `TrackingHistory` does.
- Read the loader with `object.__getattribute__`.
- Read it from `vars(self)`.

Each makes a bare instance raise `AttributeError` for `events`. `TrackingHistory` copies correctly before loading, where the copy loads nothing, and after, where the copy keeps the fields.

The set also guards against the opposite mistake. A `__getattr__` that answers every name from a mapping returns `None` for `stauts`, where the allow-list raises `AttributeError`.

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

The loaded fields are a fact from the feed, so assigning one is refused. The data model says `__setattr__` "is called instead of the normal mechanism (i.e. store the value in the instance dictionary)", which is why the load writes through `vars(self)` and goes around it. The same page calls the pair "an intentional asymmetry": `__setattr__` runs on every assignment, and `__getattr__` only on a failed lookup.

The built-ins documentation for `dir` says a `__dir__` method "allows objects that implement a custom __getattr__() or __getattribute__() function to customize the way dir() reports their attributes". Without it, `dir(history)` omits fields that haven't loaded. With it, `dir()` lists them and loads nothing, and a misspelt field earns the interpreter's suggestion. On 3.15.2, `history.stauts` raises `AttributeError: 'TrackingHistory' object has no attribute 'stauts'. Did you mean '.status' instead of '.stauts'?`, and a subclass whose `__dir__` leaves the names out gets no hint.

Special methods are looked up on the type. The data model says that "For custom classes, implicit invocations of special methods are only guaranteed to work correctly if defined on an object’s type, not in the object’s instance dictionary." So a class that relies on `__getattr__` to forward `__iter__` has none: `iter()` and `len()` raise `TypeError` without the hook running, although reading `forwarding.__iter__` by name reaches it. That's why `TrackingHistory` writes `__iter__`.

`hasattr(history, "status")` is a read, so checking for a lazy field reads the feed.

## What mypy sees

The declared annotations keep their types: assigning `h.status` to an `int` is an `[assignment]` error about `ConsignmentStatus | None`. A name that isn't declared is typed as `__getattr__`'s return, `object`. mypy reveals `h.stauts` as `object` and reports one `[attr-defined]` error, on `.upper()` and not on the misspelling. The typo is reported only when the result is used in a way `object` rejects.

mypy accepts two assignments the run treats differently:

| Assignment | mypy | Run time |
| --- | --- | --- |
| `h.status = None` | matches the declared type | `AttributeError`, "is loaded, not assigned" |
| `h.anything = 1` | accepted, since `__setattr__` takes any name | creates an attribute |

A forwarding `__getattr__` typed `Any` accepts a typo outright, which [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) measures.

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

`tracking.LazyTrackingHistory` warns and returns `TrackingHistory`, and `stacklevel=2` attributes the warning to the file that asked for the name. Any other missing name raises `AttributeError` naming the module, and `dir(tracking)` lists the old name. The data model limits the hook: "only affect lookups made using the attribute access syntax". A read through `globals()` inside the module never calls it.

mypy accepts any name imported through the hook. `from dynamic_attributes.tracking import Anything` type-checks as `type[TrackingHistory]` and fails with `ImportError` at run time.

PEP 562 also names a second use: "Another widespread use case for __getattr__ would be lazy submodule imports." On 3.15 the importing side has `lazy import`, from [PEP 810](https://peps.python.org/pep-0810/) by Pablo Galindo Salgado and co-authors, which [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) uses. Deprecation is the use that stays with the module hook.

## When not to use it

- **One lazy field** is a `cached_property`, which says so in one place; [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) covers it.
- **Unknown fields.** Fields that aren't known when the class is written belong in a mapping, not in attributes.
- **Wrapping another object's interface** wants an explicit proxy, as [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) shows.
- **A computed value** that a plain `property` states more directly doesn't need an interception hook.

> **🤖 Explore with your agent**
>
> "Declare `TrackingHistory`'s loaded fields as class annotations. Write `__getattr__` to load only the names in a fixed set, store them with `vars(self).update(...)`, and raise `AttributeError` for every other name. Refuse assignment to loaded fields in `__setattr__`, list them in `__dir__`, and define `__iter__` explicitly. For a single lazy value, use `functools.cached_property` instead."
>
> If `__getattr__` reads an attribute it doesn't own, ask what `copy.copy` does.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/30-dynamic-attributes-and-proxy
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 41 cases pass and mypy is clean. Two experiments, each in a scratch copy:

- **Delete `__dir__`.** Remove the method from `TrackingHistory`. Two tests fail: `dir()` no longer lists the lazy fields, and a misspelt field gets no "Did you mean" suffix. mypy stays green, since no type mentions `__dir__`.
- **Delete the allow-list.** Remove the `if name not in _LAZY:` check and its `raise` from `__getattr__`. Four tests fail. A typo now loads the feed and then fails in `vars(self)[name]` with `KeyError` where `AttributeError` is expected, and the two copy checks fail with `RecursionError`, because the bare instance `copy` builds has no `_load`. mypy stays green.

## What you can do now

- Load a record's fields once with `TrackingHistory`: one feed read for three fields, then plain attributes.
- Predict the hooks: `__getattr__` runs only when normal lookup fails, and `__getattribute__` on every read.
- Keep `__getattr__` out of recursion under `copy` and `pickle` with an allow-list, `object.__getattribute__` or `vars(self)`.
- Make the object consistent: `__dir__` for `dir()` and the "Did you mean" hint, an explicit `__iter__` for `iter()`, and declared annotations for mypy.
- Deprecate a module name with a module-level `__getattr__` that warns and returns `TrackingHistory`.

## For deeper coverage

The data model's [customising attribute access](https://docs.python.org/3/reference/datamodel.html) and special method lookup sections are the reference for the hooks, and the [built-in functions](https://docs.python.org/3/builtins/functions.html), [copy](https://docs.python.org/3/library/copy.html) and [pickle](https://docs.python.org/3/library/pickle.html) pages cover `dir`, `copy` and unpickling. [PEP 562](https://peps.python.org/pep-0562/), by Ivan Levkivskyi, specifies module `__getattr__` and `__dir__`, and [PEP 810](https://peps.python.org/pep-0810/) specifies `lazy import`. Brandon Rhodes's [The Decorator Pattern](https://python-patterns.guide/gang-of-four/decorator-pattern/) describes the dynamic wrapper. *Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Proxy, Martin Fowler's *Patterns of Enterprise Application Architecture* for Lazy Load, and *Fluent Python*, second edition, by Luciano Ramalho, is the broader reference for the data model and dynamic attributes. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
