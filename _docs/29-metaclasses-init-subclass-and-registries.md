---
title: "Metaclasses, __init_subclass__, and registries"
order: 29
layout: tutorial
sectionid: docs
part: "idiomatic-python"
description: "Register subclasses by a class keyword, refuse a bad class when it is defined, and see what only a metaclass can still do."
---

## Learning objectives

By the end of this chapter you can:

- Register subclasses by a class keyword with `__init_subclass__`, and say what mypy checks about it.
- Refuse a bad carrier class at definition.
- Keep a class registry out of other tests' way.
- Name the costs of a metaclass registry.
- Say what only a metaclass can do, and when that's worth it.

## Why this matters

A booking arrives with a carrier code, and the system needs the gateway class for that code. Other teams add carriers. A registry that fills as each carrier class is created spares the booking code from knowing the list, and it's the job a metaclass registry used to do. Since Python 3.6 the base class has a hook for it, so the pattern dissolves, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts it. What stays design is which classes register, what's refused at definition, which modules must be imported for a registration to exist, and how tests avoid each other's registrations. The obvious versions fail three ways:

- A carrier left out of a hand-kept dictionary is unavailable, and booking through the dictionary meets a `KeyError`.
- An abstract class given a code takes a place in the registry when the hook can't tell that it's abstract.
- A metaclass registry meets another library's base class and raises a metaclass conflict when the module is imported.

{% include excalidraw.html name="29-metaclasses-init-subclass-and-registries" described="true" caption="Figure 29.1: Creating a carrier class runs any __set_name__ hooks and then __init_subclass__, which refuses a bad class and registers a concrete one in a read-only view. A metaclass can enforce the same rules, but it can conflict with another library's metaclass." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-29-metaclasses-init-subclass-and-registries" markdown="1">
From the top down, the first box, "a class statement", shows `class FastlineGateway(CarrierBase, code="FASTLINE")` as its example, and leads to a dashed box, `__prepare__` ("a metaclass can supply the class namespace"), and then to "class body runs". The next box, `type.__new__`, "creates the class object, then calls `__set_name__` and `__init_subclass__`". Below it sit `__set_name__`, which runs only if an attribute defines it, and an amber box, `CarrierBase.__init_subclass__`, listing three rules: an abstract class takes no code and isn't registered, a concrete class needs a code, and a duplicate code raises `DuplicateCarrierError`. An arrow labelled "if concrete" leads from it to `registry`, "read-only view: FASTLINE, AIRCO". The last box in the column is "class decorators", which run only if the class has any; `FastlineGateway` has neither a `__set_name__` attribute nor a decorator. A second dashed box at the bottom, "a metaclass comparison", reads "the same rules in the metaclass `__new__`", "its own registry", "can conflict with another metaclass" and "mypy skips its class keywords".
</div>
</details>

The figure follows a class statement through class creation to the registry, with the metaclass form beside it.

## A registry filled at class creation

The data model says "Whenever a class inherits from another class, __init_subclass__() is called on the parent class." That's the whole mechanism: `CarrierBase` defines the hook, and each subclass statement calls it with the new class. PEP 487, by Martin Teichmann, names this use: "Especially when writing a plugin system, one likes to register new subclasses of a plugin baseclass."

```python
class CarrierBase(ABC):
    """Root of the carrier gateways. A concrete subclass names its code as a class keyword.

    A carrier exists only once its module has been imported, because the class statement is what
    registers it.
    """

    registry: ClassVar[Mapping[str, type[CarrierBase]]] = MappingProxyType(_CARRIERS)
    code: ClassVar[str]

    def __init_subclass__(cls, *, code: str | None = None) -> None:
        """Register a concrete subclass under its code, or refuse the class.

        The signature forwards no extra keywords: this class is the root of the hierarchy and has
        no cooperating mixins, so a misspelt class keyword is a call error that mypy names. Every
        refusal happens before the insertion, so a refused class leaves the registry unchanged.
        """
        super().__init_subclass__()
        if inspect.isabstract(cls):
            if code is not None:
                raise CarrierRegistrationError(
                    f"{cls.__name__} is abstract and cannot take code {code!r}"
                )
            return
        if code is None:
            raise CarrierRegistrationError(f"{cls.__name__} is concrete and needs a code")
        if code in _CARRIERS:
            raise DuplicateCarrierError(
                f"carrier code {code!r} is already registered to {_CARRIERS[code].__name__}"
            )
        cls.code = code
        _CARRIERS[code] = cls
```

`registry` is a `MappingProxyType` over the private dictionary, so readers see the registrations and can't assign to them. A carrier names its code as a class keyword and nothing else:

```python
class FastlineGateway(CarrierBase, code="FASTLINE"):
    def book(self, consignment_id: ConsignmentId, /) -> str:
        return f"FL-{consignment_id}"
```

The registry maps `AIRCO` and `FASTLINE` to their classes. `gateway_for` books through it, and raises `UnknownCarrierError`, "unknown carrier 'NOPE'", for a code nobody registered.

A class keyword is an ordinary parameter of the hook, so mypy checks it. `code=1` is `[arg-type]`, naming `Argument "code" to "__init_subclass__" of "CarrierBase"`. A misspelt `cod="X"` is `[call-arg]` with the suggestion `did you mean "code"?`.

That second report depends on the signature. The data model advises cooperating classes: "For compatibility with other classes using __init_subclass__, one should take out the needed keyword arguments and pass the others over to the base class". `CarrierBase` is the root of its hierarchy, with no mixins that would use leftover keywords, so it takes none and calls `super().__init_subclass__()` with nothing. The run time refuses `cod="X"` too, with `TypeError`, `unexpected keyword argument 'cod'`. The first experiment below forwards the keywords and shows what that costs.

## Refusing a bad carrier class

The hook runs before the registry is touched, so it can refuse a class and leave the registry as it was. Four rules apply, in order:

| Class | Result |
| --- | --- |
| abstract, with a code | `CarrierRegistrationError`, "is abstract and cannot take code 'HALF'" |
| abstract, no code | skipped: a base for carriers, not a carrier |
| concrete, no code | `CarrierRegistrationError`, so a forgotten code can't hide |
| concrete, code already taken | `DuplicateCarrierError` naming the class that holds it; the first class stays |

After each refusal the registry still holds `AIRCO` and `FASTLINE`. An abstract intermediate, such as a `CarrierBase` subclass that adds an abstract `track`, isn't registered, and a concrete carrier beneath it is.

The abstract check needs care, because `ABCMeta` computes `__abstractmethods__` after the class is built, and the hook runs inside the build. Inside the hook the attribute isn't there yet, and `inspect.isabstract` still answers correctly. The `inspect` source on the 3.15 branch has a branch for the situation, and its comment says "we're probably in __init_subclass__". A `getattr` on `__abstractmethods__` doesn't, as the second experiment shows. A metaclass `__new__` runs after `ABCMeta.__new__` returns, so the attribute is set there, which is why `_CarrierMeta` below reads it directly.

Three hooks can act on a new class, and their order matters. The data model lists the steps: `type.__new__` calls each attribute's `__set_name__`, then "The __init_subclass__() hook is called on the immediate parent of the new class in its method resolution order", and then "After the class object is created, it is passed to the class decorators included in the class definition (if any)". So a descriptor's `__set_name__` has finished before the hook sees the class, and a class decorator sees a class that's already registered. [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) and [Decorators done right]({{ '/docs/26-decorators-done-right/' | relative_url }}) cover the other two hooks.

## Where registrations come from

`carrier_registry/__init__.py` imports no carrier module, so a carrier registers only when its module is imported. In a fresh interpreter, importing `carriers` gives an empty registry, importing `airco` adds `AIRCO`, and importing `fastline` adds `FASTLINE`. Moving the work to class creation moved the failure: a forgotten dictionary entry became a forgotten import, and something at start-up has to import every carrier module.

The registry is also a mutable global, and Brandon Rhodes describes what those cost in "The Global Object Pattern" on python-patterns.guide: "Tests that were previously independent are suddenly coupled through the global object". A carrier defined in one test stays registered for every later test. So in a pytest run, define only classes that are abstract or refused before insertion, and assert the registry is unchanged. Run a carrier that does register in a fresh `python -I` interpreter. The same discipline applies to a dispatcher whose registrations live in other modules; see [singledispatch: the Visitor the language gives you]({{ '/docs/28-singledispatch/' | relative_url }}).

## The same registry as a metaclass

Here are the four rules in a metaclass:

```python
class _CarrierMeta(ABCMeta):
    """The comparison: the same four rules as ``CarrierBase.__init_subclass__``, in a metaclass."""

    code: str

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, object],
        /,
        *,
        code: str | None = None,
    ) -> _CarrierMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        if cls.__abstractmethods__:
            if code is not None:
                raise CarrierRegistrationError(f"{name} is abstract and cannot take code {code!r}")
            return cls
        if code is None:
            raise CarrierRegistrationError(f"{name} is concrete and needs a code")
        if code in _META_CARRIERS:
            raise DuplicateCarrierError(
                f"carrier code {code!r} is already registered to {_META_CARRIERS[code].__name__}"
            )
        cls.code = code
        _META_CARRIERS[code] = cls
        return cls

    def __contains__(cls, code: object) -> bool:
        return code in _META_CARRIERS

    def __iter__(cls) -> Iterator[str]:
        return iter(sorted(_META_CARRIERS))

    def __len__(cls) -> int:
        return len(_META_CARRIERS)
```

Both forms book through the same carriers and refuse the same bad classes, with the same registry after each refusal. The metaclass keeps its own dictionary, `_META_CARRIERS`, so the two registries don't mix.

The metaclass costs show in four places. The first is conflicts. PEP 487 describes the problem: unrelated metaclasses on a class's parents can't be combined, and that's one of the reasons it added the hook. Because `ABC` is built by `ABCMeta`, the abc documentation warns that "multiple inheritance may lead to metaclass conflicts". A plain `type` subclass as `metaclass=` under `CarrierBase`, or under a `Protocol`, raises `TypeError` with "metaclass conflict". Deriving from `ABCMeta`, as `_CarrierMeta` does, resolves it.

The other three are mypy's:

| Metaclass code | mypy | Run time |
| --- | --- | --- |
| `class Fastline(MetaBase, code=1)`, where `__new__` takes a `str` code | accepted | registers an `int` key |
| `Self` in a metaclass `__new__` | `[misc]`, "Self type cannot be used in a metaclass" | the class builds |
| a class called from a dictionary of metaclass instances | typed `Any`; a misspelt `bok` passes | `AttributeError` |

The mypy documentation puts the limit this way: "Mypy does not and cannot understand arbitrary metaclass code." It does report the conflict itself, as `[metaclass]`.

## What only a metaclass can do

The one case where the metaclass earns its cost is an operator on the class object. The data model says implicit invocations of special methods are "only guaranteed to work correctly if defined on an object’s type", and a class's type is its metaclass. `_CarrierMeta` defines `__contains__`, `__iter__` and `__len__`, so a base class built by it behaves as a collection of codes: `"AIRCO" in` it is true, `list()` gives the sorted codes and `len()` gives 2. On `CarrierBase` the same `in` raises `TypeError`, "is not a container or iterable".

The enum documentation names the standard library's case: "EnumType is the metaclass for enum enumerations." An enum is a collection of its members, which is why `in`, iteration and `len` belong on the class. A carrier registry gets the same reading from `CarrierBase.registry`, so the `src` code has no metaclass.

Two other metaclass hooks are dissolved or invisible. PEP 520, by Eric Snow, says of an ordered class namespace that "exactly this is by far the most common use case for using __prepare__". The data model says a class whose metaclass has no `__prepare__` gets "an empty ordered mapping", so the common reason to write `__prepare__` has been gone since 3.6, the version PEP 520 lists. And a metaclass `__call__` replaces what calling the class does: one declared to return `int` makes `G("x")` evaluate to `1` at run time, while mypy reveals `G`. [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) puts a metaclass `__call__` to work and measures what it costs.

## When not to use it

- **A fixed set** that one module owns is a `frozendict` of constructors; [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) shows it.
- **Entries that aren't classes** belong in a function and a dictionary.
- **A metaclass.** A metaclass is the wrong tool for anything `__init_subclass__`, a class decorator or a descriptor does.
- **Uncertain imports.** Registration that depends on modules nobody is sure will be imported leaves a carrier missing until a booking asks for its code and gets `UnknownCarrierError`.

> **🤖 Explore with your agent**
>
> "Register carrier classes with `__init_subclass__(cls, *, code: str | None = None)` on `CarrierBase`, with no `**kwargs` and no metaclass. Use `inspect.isabstract(cls)`: an abstract class takes no code, a concrete class must have one, and a duplicate code raises `DuplicateCarrierError`. Expose the registry as a read-only `MappingProxyType`. In tests, define only classes that are refused or abstract, and check a carrier that registers in a fresh interpreter."
>
> If the reply adds a metaclass, ask what it does that `__init_subclass__` can't.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/29-metaclasses-init-subclass-and-registries
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 35 cases pass and mypy is clean. For how the mypy checks run from pytest, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}). Two experiments, each in a fresh scratch copy:

- **Forward the keywords.** In `CarrierBase.__init_subclass__`, add `**kwargs: object` and pass it to `super().__init_subclass__(**kwargs)`, the form the data model shows. Two tests fail. `object.__init_subclass__`, which "does nothing, but raises an error if it is called with any arguments", now refuses `cod="X"` with `takes no keyword arguments`, a message that names the class and not the keyword. And mypy no longer reports the misspelling, so the typo goes unreported until the class statement runs.
- **Read `__abstractmethods__`.** Replace `inspect.isabstract(cls)` with `bool(getattr(cls, "__abstractmethods__", ()))`. Seven tests fail. Inside the hook the attribute is missing, so every abstract class counts as concrete: an abstract intermediate raises "Intermediate is concrete and needs a code", and the abstract class given a code registers `HALF`, which then breaks the registry checks that follow. mypy stays green.

## What you can do now

- Register by a class keyword with `CarrierBase.__init_subclass__`, and keep its signature closed so mypy reports a misspelt keyword.
- Refuse a bad class at definition with `CarrierRegistrationError` and `DuplicateCarrierError`, before anything is inserted.
- Keep the registry out of other tests' way: a read-only view, refusals that raise before insertion, and a fresh interpreter for a carrier that registers.
- Name what a metaclass registry costs: `_CarrierMeta` must derive from `ABCMeta` to avoid a conflict, and mypy skips its class keywords.
- Say what only a metaclass can do: give the class object operators such as `in`, iteration and `len`.

## For deeper coverage

The [data model](https://docs.python.org/3/reference/datamodel.html) sections on customising class creation and metaclasses are the primary source. Martin Teichmann's [PEP 487](https://peps.python.org/pep-0487/) added `__init_subclass__`, Talin's [PEP 3115](https://peps.python.org/pep-3115/) introduced the `__prepare__` namespace hook, and Eric Snow's [PEP 520](https://peps.python.org/pep-0520/) preserved the order of class attribute definitions. The [abc](https://docs.python.org/3/library/abc.html) and [enum](https://docs.python.org/3/library/enum.html) pages cover `ABCMeta` and `EnumType`, the [mypy metaclasses page](https://mypy.readthedocs.io/en/stable/metaclasses.html) lists what the checker can't follow, and the `isabstract` branch is in CPython's [inspect module](https://github.com/python/cpython/blob/3.15/Lib/inspect.py). Brandon Rhodes's [The Global Object Pattern](https://python-patterns.guide/python/module-globals/) covers the mutable global. *Fluent Python*, second edition, by Luciano Ramalho, is the broader reference for the data model these hooks sit in. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
