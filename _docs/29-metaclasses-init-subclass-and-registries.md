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

A booking arrives with a carrier code, and the system needs the gateway class for that code. Other teams add carriers. A registry that fills as each carrier class is created spares the booking code from knowing the list, and it's the job a metaclass registry used to do. Since Python 3.6 the base class has a hook for it, so the pattern dissolves, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts it. What stays design is which classes register, what is refused at definition, which modules must be imported for a registration to exist, and how tests avoid each other's registrations. Three things go wrong in the obvious versions.

A carrier left out of a hand-kept dictionary is unavailable, and the code that books through the dictionary meets a `KeyError` (`test_a_forgotten_manual_registration_leaves_the_carrier_unavailable`).

An abstract class that is given a code would take its place in the registry if the hook couldn't tell that it's abstract. Experiment two below swaps in such a check and shows it there.

A metaclass registry meets another library's base class and raises a metaclass conflict when the module is imported (`test_a_second_metaclass_conflicts_with_the_bases_metaclass`).

{% include excalidraw.html name="29-metaclasses-init-subclass-and-registries" caption="Figure 29.1: Creating a carrier class runs any __set_name__ hooks and then __init_subclass__, which refuses a bad class and registers a concrete one in a read-only view. A metaclass can enforce the same rules, but it can conflict with another library's metaclass." %}

Read the figure from the top down. The top box, "a class statement", shows `class FastlineGateway(CarrierBase, code="FASTLINE")` as its example, and leads to a dashed box, `__prepare__` ("a metaclass can supply the class namespace"), and then to "class body runs". The next box, `type.__new__`, "creates the class object, then calls `__set_name__` and `__init_subclass__`". Below it sit `__set_name__`, which runs only if an attribute defines it, and an amber box, `CarrierBase.__init_subclass__`, listing three rules: an abstract class takes no code and isn't registered, a concrete class needs a code, and a duplicate code raises `DuplicateCarrierError`. An arrow labelled "if concrete" leads from it to `registry`, "read-only view: FASTLINE, AIRCO". The last box in the column is "class decorators", which run only if the class has any; `FastlineGateway` has neither a `__set_name__` attribute nor a decorator. A second dashed box at the bottom, "a metaclass comparison", reads "the same rules in the metaclass `__new__`", "its own registry", "can conflict with another metaclass" and "mypy skips its class keywords".

## A registry filled at class creation

The Python data model says "Whenever a class inherits from another class, __init_subclass__() is called on the parent class." That's the whole mechanism: `CarrierBase` defines the hook, and each subclass statement calls it with the new class. PEP 487, by Martin Teichmann, names this use: "Especially when writing a plugin system, one likes to register new subclasses of a plugin baseclass."

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

`registry` is a `MappingProxyType` over the private dictionary, so readers see the registrations and can't assign to them (`test_the_carrier_registry_is_a_read_only_view`). A carrier names its code as a class keyword and nothing else:

```python
class FastlineGateway(CarrierBase, code="FASTLINE"):
    def book(self, consignment_id: ConsignmentId, /) -> str:
        return f"FL-{consignment_id}"
```

Each of the two gateways registers under its keyword, and the registry maps `AIRCO` and `FASTLINE` to their classes (`test_the_registry_maps_each_code_to_its_gateway_class`). `gateway_for` books through it (`test_gateway_for_books_with_the_registered_carrier`) and raises `UnknownCarrierError`, "unknown carrier 'NOPE'", for a code nobody registered (`test_an_unknown_code_raises_unknown_carrier_error`).

A class keyword is an ordinary parameter of the hook, so mypy 2.4.1 checks it. `code=1` is an `[arg-type]` error that names `Argument "code" to "__init_subclass__" of "CarrierBase"` (`test_mypy_checks_the_type_of_a_class_keyword`). A misspelt `cod="X"` is `[call-arg]` with the suggestion `did you mean "code"?` (`test_mypy_reports_a_misspelt_class_keyword`).

That second report depends on a choice in the signature. The data model advises cooperating classes: "For compatibility with other classes using __init_subclass__, one should take out the needed keyword arguments and pass the others over to the base class". `CarrierBase` is the root of its hierarchy and has no mixins that would use the leftover keywords, so it takes none and calls `super().__init_subclass__()` with nothing. The run time refuses a misspelt keyword too, because the hook's own signature has no such parameter: the `unknown-keyword` row of `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry` raises `TypeError` with `unexpected keyword argument 'cod'`. Experiment one forwards the keywords and shows what that costs.

## Refusing a bad carrier class

The hook runs before the registry is touched, so it can refuse a class and leave the registry as it was. Four rules apply, in this order: an abstract class with a code is refused, an abstract class without one is skipped, a concrete class without a code is refused, and a code that's already taken raises `DuplicateCarrierError` naming the class that holds it. The second case matters: an abstract intermediate class, such as a `CarrierBase` subclass that adds an abstract `track`, is a base for carriers and not a carrier (`test_an_abstract_intermediate_class_is_not_registered`, and `test_a_concrete_carrier_under_an_abstract_intermediate_registers` for a concrete class beneath one).

A duplicate keeps the first class, and its message says which (`test_a_duplicate_code_keeps_the_first_class`). A concrete class that forgot its keyword is refused as well, so the forgotten code can't hide as a carrier that never registered (`test_a_concrete_class_without_a_code_is_refused`). The abstract class given a code raises `CarrierRegistrationError`, "is abstract and cannot take code 'HALF'". The refusal table runs these three cases and the misspelt keyword, and asserts after each that the registry still holds `AIRCO` and `FASTLINE`.

The abstract check needs care, because `ABCMeta` computes `__abstractmethods__` after the class is built, and the hook runs inside the build. Inside the hook the attribute isn't there yet, and `inspect.isabstract` still answers correctly (`test_isabstract_sees_abstractness_inside_init_subclass`). The `inspect` source on the 3.15 branch has a branch for the situation, and its comment says "we're probably in __init_subclass__". A `getattr` on `__abstractmethods__` doesn't, as experiment two shows. A metaclass `__new__` runs after `ABCMeta.__new__` returns, so the attribute is set there, which is why `_CarrierMeta` below reads it directly.

Three hooks can act on a new class, and their order matters. The data model lists the steps: `type.__new__` calls each attribute's `__set_name__`, then "The __init_subclass__() hook is called on the immediate parent of the new class in its method resolution order", and then "After the class object is created, it is passed to the class decorators included in the class definition (if any)". A test logs the three and gets `__set_name__`, `__init_subclass__`, `decorator`, in that order (`test_set_name_runs_before_init_subclass_and_a_class_decorator_after`). A descriptor's `__set_name__` has finished before the hook sees the class, and a class decorator sees a class that is already registered. [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) and [Decorators done right]({{ '/docs/26-decorators-done-right/' | relative_url }}) cover the other two hooks.

## Where registrations come from

`carrier_registry/__init__.py` imports no carrier module, so a carrier registers only when its module is imported. In a fresh interpreter, importing `carriers` gives an empty registry, importing `airco` adds `AIRCO`, and importing `fastline` adds `FASTLINE` (`test_a_carrier_module_registers_only_when_it_is_imported`). Moving the work to class creation moved the failure: a forgotten dictionary entry became a forgotten import, and something at start-up has to import every carrier module.

The registry is also a mutable global, and Brandon Rhodes describes what those cost in "The Global Object Pattern" on python-patterns.guide: "Tests that were previously independent are suddenly coupled through the global object". A test that defined a carrier would leave it registered for every later test, as experiment two shows. So no test registers a carrier in the test process: each class a test defines under `CarrierBase` is abstract or is refused before anything is inserted, and the refusal tests assert the registry is unchanged. A carrier that does register runs in a fresh `python -I` interpreter. The same discipline applies to a dispatcher whose registrations live in other modules, and [singledispatch: the Visitor the language gives you]({{ '/docs/28-singledispatch/' | relative_url }}) shows it there.

## The same registry as a metaclass

The comparison is a metaclass that applies the four rules. It's a fixture beside the idiomatic form, and both run one table: `registry_form` is a parameter with two values, `init_subclass` and `metaclass`.

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

Both forms pass the same booking rows and refusal rows, and the same registry assertions after each refusal (`test_every_registry_form_books_through_the_registered_carrier` and `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry`). The metaclass keeps its own dictionary, `_META_CARRIERS`, so the two registries don't mix.

What the metaclass costs shows in four places. The first is conflicts. PEP 487 describes the problem: unrelated metaclasses on a class's parents can't be combined, and that is one of the reasons it added the hook. Because `ABC` is built by `ABCMeta`, the abc documentation warns that "multiple inheritance may lead to metaclass conflicts". A plain `type` subclass as `metaclass=` under `CarrierBase`, or under a `Protocol`, raises `TypeError` with "metaclass conflict" (`test_a_second_metaclass_conflicts_with_the_bases_metaclass`). Deriving from `ABCMeta`, as `_CarrierMeta` does, resolves it (`test_a_metaclass_derived_from_abcmeta_resolves_the_conflict`).

The other three are mypy's, and each is measured on a reduced model, a snippet inside the test that stands for code and isn't part of the example. mypy 2.4.1 doesn't check a metaclass's class keywords: a registry metaclass takes `code: str | None`, and `class Fastline(MetaBase, code=1)` exits 0 with no output, while the run registers an `int` key (`test_mypy_does_not_check_metaclass_class_keywords`). It refuses `Self` in a metaclass `__new__` with `[misc]`, "Self type cannot be used in a metaclass", although the class builds at run time (`test_mypy_refuses_self_in_a_metaclass_new`). And a class called from a dictionary of metaclass instances is typed `Any`: `reveal_type` prints `Any`, and a misspelt method `bok` passes mypy and fails with `AttributeError` at run time (`test_mypy_types_a_class_called_from_a_metaclass_registry_as_any`). The mypy documentation puts the limit this way: "Mypy does not and cannot understand arbitrary metaclass code." It also reports the conflict itself, as `[metaclass]` (`test_mypy_reports_a_metaclass_conflict`).

## What only a metaclass can do

The one case where the metaclass earns its cost is an operator on the class object. The data model says implicit invocations of special methods are "only guaranteed to work correctly if defined on an object’s type", and a class's type is its metaclass. `_CarrierMeta` defines `__contains__`, `__iter__` and `__len__`, so the class itself behaves as a collection of codes.

```python
def test_only_a_metaclass_gives_the_class_object_operators(
    meta_carrier_base: type[_MetaCarrierBase],
) -> None:
    assert "AIRCO" in meta_carrier_base
    assert list(meta_carrier_base) == _ALL_CODES
    assert len(meta_carrier_base) == 2
    with pytest.raises(TypeError, match="is not a container or iterable"):
        "AIRCO" in CarrierBase  # type: ignore[operator]  # noqa: B015
```

On `CarrierBase` the same `in` raises `TypeError`. The enum documentation names the standard library's case: "EnumType is the metaclass for enum enumerations." An enum is a collection of its members, which is why `in`, iteration and `len` belong on the class. A carrier registry gets the same reading from `CarrierBase.registry`, so the `src` code has no metaclass.

Two other metaclass hooks are dissolved or invisible. PEP 520, by Eric Snow, says of an ordered class namespace that "exactly this is by far the most common use case for using __prepare__". The data model says a class whose metaclass has no `__prepare__` gets "an empty ordered mapping", so the common reason to write `__prepare__` has been gone since 3.6, the version PEP 520 lists. And a metaclass `__call__` replaces what calling the class does. A `__call__` declared to return `int` makes `G("x")` evaluate to `1` at run time, while mypy reveals `G` (`test_mypy_ignores_a_metaclass_call_return_type`, another reduced model). [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) puts a metaclass `__call__` to work as a singleton and measures what it costs.

## When not to use it

A fixed set that one module owns is a `frozendict` of constructors, and [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) shows it. A registry whose entries aren't classes is a function and a dictionary. A metaclass is the wrong tool for anything `__init_subclass__`, a class decorator or a descriptor does. And registration that depends on modules nobody is sure will be imported leaves a carrier missing until a booking asks for its code and gets `UnknownCarrierError`.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a class registry.** "A plugin registry" leaves open how classes register and what is refused. State the form:

> Register carrier classes with `__init_subclass__(cls, *, code: str | None = None)` on `CarrierBase`, with no `**kwargs` and no metaclass. Use `inspect.isabstract(cls)`: an abstract class takes no code, a concrete class must have one, and a duplicate code raises `DuplicateCarrierError`. Expose the registry as a read-only `MappingProxyType`. In tests, define only classes that are refused or abstract, and check a carrier that registers in a fresh interpreter.

If the reply adds a metaclass, ask what it does that `__init_subclass__` can't.
</blockquote>

## Build, run, observe

The run shows both registry forms passing one table of bookings and refusals, then the import-order tests. From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/29-metaclasses-init-subclass-and-registries
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
collecting ... collected 35 items

tests/test_metaclass.py::test_a_second_metaclass_conflicts_with_the_bases_metaclass[abc] PASSED [  2%]
tests/test_metaclass.py::test_a_second_metaclass_conflicts_with_the_bases_metaclass[protocol] PASSED [  5%]
tests/test_metaclass.py::test_a_metaclass_derived_from_abcmeta_resolves_the_conflict PASSED [  8%]
tests/test_metaclass.py::test_only_a_metaclass_gives_the_class_object_operators PASSED [ 11%]
tests/test_registry.py::test_every_registry_form_books_through_the_registered_carrier[init_subclass-FASTLINE-FL-CN-1] PASSED [ 14%]
tests/test_registry.py::test_every_registry_form_books_through_the_registered_carrier[init_subclass-AIRCO-AC-CN-1] PASSED [ 17%]
tests/test_registry.py::test_every_registry_form_books_through_the_registered_carrier[metaclass-FASTLINE-FL-CN-1] PASSED [ 20%]
tests/test_registry.py::test_every_registry_form_books_through_the_registered_carrier[metaclass-AIRCO-AC-CN-1] PASSED [ 22%]
tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[init_subclass-duplicate] PASSED [ 25%]
tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[init_subclass-concrete-without-code] PASSED [ 28%]
tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[init_subclass-abstract-with-code] PASSED [ 31%]
tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[init_subclass-unknown-keyword] PASSED [ 34%]
tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[metaclass-duplicate] PASSED [ 37%]
tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[metaclass-concrete-without-code] PASSED [ 40%]
tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[metaclass-abstract-with-code] PASSED [ 42%]
tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[metaclass-unknown-keyword] PASSED [ 45%]
tests/test_registry.py::test_the_registry_maps_each_code_to_its_gateway_class PASSED [ 48%]
tests/test_registry.py::test_gateway_for_books_with_the_registered_carrier PASSED [ 51%]
tests/test_registry.py::test_an_unknown_code_raises_unknown_carrier_error PASSED [ 54%]
tests/test_registry.py::test_the_carrier_registry_is_a_read_only_view PASSED [ 57%]
tests/test_registry.py::test_a_duplicate_code_keeps_the_first_class PASSED [ 60%]
tests/test_registry.py::test_an_abstract_intermediate_class_is_not_registered PASSED [ 62%]
tests/test_registry.py::test_a_concrete_class_without_a_code_is_refused PASSED [ 65%]
tests/test_registry.py::test_isabstract_sees_abstractness_inside_init_subclass PASSED [ 68%]
tests/test_registry.py::test_set_name_runs_before_init_subclass_and_a_class_decorator_after PASSED [ 71%]
tests/test_registry.py::test_a_forgotten_manual_registration_leaves_the_carrier_unavailable PASSED [ 74%]
tests/test_registry.py::test_a_carrier_module_registers_only_when_it_is_imported PASSED [ 77%]
tests/test_registry.py::test_a_concrete_carrier_under_an_abstract_intermediate_registers PASSED [ 80%]
tests/test_static.py::test_mypy_checks_the_type_of_a_class_keyword PASSED [ 82%]
tests/test_static.py::test_mypy_reports_a_misspelt_class_keyword PASSED  [ 85%]
tests/test_static.py::test_mypy_does_not_check_metaclass_class_keywords PASSED [ 88%]
tests/test_static.py::test_mypy_reports_a_metaclass_conflict PASSED      [ 91%]
tests/test_static.py::test_mypy_refuses_self_in_a_metaclass_new PASSED   [ 94%]
tests/test_static.py::test_mypy_types_a_class_called_from_a_metaclass_registry_as_any PASSED [ 97%]
tests/test_static.py::test_mypy_ignores_a_metaclass_call_return_type PASSED [100%]

============================== 35 passed in 3.24s ==============================
Success: no issues found in 8 source files
```

The suite has 24 test functions and 35 cases. For how the mypy tests are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

- `tests/test_registry.py` holds the shared table, the hook order and the fresh-interpreter runs.
- `tests/test_metaclass.py` holds the conflicts and the class-level operators.
- `tests/test_static.py` holds the mypy witnesses: two that import the example and five reduced models.

Each experiment runs in a fresh scratch copy with its own environment, and the filter is the same for both: `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {9}[^ ]|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'`, followed by `uv run mypy --strict src tests`.

**Experiment one: forward the keywords.** In `CarrierBase.__init_subclass__`, add `**kwargs: object` to the signature and pass it to `super().__init_subclass__(**kwargs)`, the form the data model shows. The filter and then mypy print:

```text
E       AssertionError: Regex pattern did not match.
E         Expected regex: "unexpected keyword argument 'cod'"
E         Actual message: 'Refused.__init_subclass__() takes no keyword arguments'
tests/test_registry.py:137: AssertionError
E       assert 0 == 1
tests/test_static.py:173: AssertionError
FAILED tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[init_subclass-unknown-keyword]
FAILED tests/test_static.py::test_mypy_reports_a_misspelt_class_keyword - ass...
2 failed, 33 passed in 3.05s
Success: no issues found in 8 source files
```

Two tests fail. The run time still refuses `cod="X"`, but the leftover keyword now reaches `object.__init_subclass__`, which the data model says "does nothing, but raises an error if it is called with any arguments". The message is `'Refused.__init_subclass__() takes no keyword arguments'`: it names the class the test defined and not the keyword, so the refusal test, which expects `unexpected keyword argument 'cod'`, fails. The static test fails because mypy no longer reports the misspelling: it expects exit status 1, and `assert 0 == 1` is the status it got. mypy exits 0 with "Success", so the typo goes unreported until the class statement runs. Two runs gave the same output apart from the duration.

**Experiment two: read `__abstractmethods__` instead of calling `inspect.isabstract`.** Replace `inspect.isabstract(cls)` with `bool(getattr(cls, "__abstractmethods__", ()))`. The same filter, then mypy, prints:

```text
E       Failed: DID NOT RAISE CarrierRegistrationError
E       AssertionError: assert ['AIRCO', 'FASTLINE', 'HALF'] == ['AIRCO', 'FASTLINE']
E         Left contains one more item: 'HALF'
E         Use -v to get more diff
tests/test_registry.py:139: AssertionError
E       AssertionError: assert [('AIRCO', 'A...', 'Refused')] == [('AIRCO', 'A...lineGateway')]
E         Left contains one more item: ('HALF', 'Refused')
E         Use -v to get more diff
tests/test_registry.py:144: AssertionError
E       AssertionError: assert ['AIRCO', 'FASTLINE', 'HALF'] == ['AIRCO', 'FASTLINE']
E         Left contains one more item: 'HALF'
E         Use -v to get more diff
tests/test_registry.py:186: AssertionError
E       AssertionError: Traceback (most recent call last):
E         carrier_registry.carriers.CarrierRegistrationError: Intermediate is concrete and needs a code
E       assert 1 == 0
tests/test_registry.py:104: AssertionError
FAILED tests/test_metaclass.py::test_a_metaclass_derived_from_abcmeta_resolves_the_conflict
FAILED tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[init_subclass-abstract-with-code]
FAILED tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry[init_subclass-unknown-keyword]
FAILED tests/test_registry.py::test_the_registry_maps_each_code_to_its_gateway_class
FAILED tests/test_registry.py::test_an_abstract_intermediate_class_is_not_registered
FAILED tests/test_registry.py::test_a_concrete_class_without_a_code_is_refused
FAILED tests/test_registry.py::test_a_concrete_carrier_under_an_abstract_intermediate_registers
7 failed, 28 passed in 3.15s
Success: no issues found in 8 source files
```

Seven tests fail. Inside the hook the attribute is missing, so every abstract class counts as concrete. An abstract intermediate raises "Intermediate is concrete and needs a code", and so do the abstract class in `test_a_metaclass_derived_from_abcmeta_resolves_the_conflict` and the one in the fresh-interpreter run. The `abstract-with-code` row no longer raises, `DID NOT RAISE CarrierRegistrationError`, and registers `HALF`. That leaked class fails the registry assertions that run after it: the `unknown-keyword` row, the mapping test and `test_a_concrete_class_without_a_code_is_refused`. Two runs gave the same output apart from the duration. mypy exits 0 again.

## What you can do now

- Register by a class keyword and say what mypy checks: `CarrierBase.__init_subclass__` with its closed signature, where `test_mypy_reports_a_misspelt_class_keyword` shows the `[call-arg]` report that forwarding `**kwargs` removes.
- Refuse a bad class at definition: `CarrierRegistrationError` for a concrete class with no code, where `test_a_concrete_class_without_a_code_is_refused` shows the forgotten keyword raising and the registry unchanged.
- Keep the registry out of other tests' way: a read-only view, refusals that raise before insertion and a fresh interpreter for a carrier that registers, with `test_a_carrier_module_registers_only_when_it_is_imported` showing the import order.
- Name what a metaclass registry costs: `_CarrierMeta` has to derive from `ABCMeta` to avoid the conflict that `test_a_second_metaclass_conflicts_with_the_bases_metaclass` shows for a plain metaclass under `ABC` and `Protocol` bases, and mypy skips its class keywords (`test_mypy_does_not_check_metaclass_class_keywords`).
- Say what only a metaclass can do: operators on the class object, where `test_only_a_metaclass_gives_the_class_object_operators` shows `in`, `list` and `len` working on the metaclass-built base and `in` failing on `CarrierBase`.

## For deeper coverage

The [data model](https://docs.python.org/3/reference/datamodel.html) sections on customising class creation and metaclasses are the primary source. Martin Teichmann's [PEP 487](https://peps.python.org/pep-0487/) added `__init_subclass__`, Talin's [PEP 3115](https://peps.python.org/pep-3115/) introduced the `__prepare__` namespace hook, and Eric Snow's [PEP 520](https://peps.python.org/pep-0520/) preserved the order of class attribute definitions. The [abc](https://docs.python.org/3/library/abc.html) and [enum](https://docs.python.org/3/library/enum.html) pages cover `ABCMeta` and `EnumType`, the [mypy metaclasses page](https://mypy.readthedocs.io/en/stable/metaclasses.html) lists what the checker can't follow, and the `isabstract` branch is in CPython's [inspect module](https://github.com/python/cpython/blob/3.15/Lib/inspect.py). Brandon Rhodes's [The Global Object Pattern](https://python-patterns.guide/python/module-globals/) covers the mutable global. *Fluent Python*, second edition, by Luciano Ramalho, is the broader reference for the data model these hooks sit in. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books, and the hub carries the same list.
