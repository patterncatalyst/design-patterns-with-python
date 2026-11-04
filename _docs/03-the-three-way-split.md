---
title: "The three-way split: dissolve, survive, disambiguate"
order: 3
layout: tutorial
sectionid: docs
part: "why-python-is-different"
description: "Two questions sort every catalogue pattern into dissolves, survives or needs disambiguating, shown on one shipping example whose tests witness each claim."
---

## Learning objectives

By the end of this chapter you can:

- Apply the two sorting questions to any catalogue pattern: does the name mean two things in Python, and does a language feature resolve the force without the pattern's structure?
- Place each pattern of the catalogue in the bucket this book uses and name the Python feature or the surviving force behind that placement.
- Keep the Decorator pattern and the `@decorator` syntax apart, and say what each one does to a rate calculation.
- Recognise the idioms that belong to no catalogue entry: the optional as Null Object, the frozen dataclass as Value Object, dict dispatch and EAFP.
- Explain why Command, Template Method and Visitor straddle two buckets.
- Run the example for this chapter and read its nineteen tests as witnesses for the map.

## Why this matters

A pattern catalogue is a list of names, and a team that shares the names can review a design in a sentence. A catalogue read without judgement produces two opposite mistakes. One is to build every pattern as drawn, with a class hierarchy where a function would do. The other is to declare patterns obsolete and lose the design thinking that a few of them still carry. This chapter gives a map that avoids both: each pattern is placed by asking about its force, the pressure that made the pattern worth having, and about its name.

The map is the book's thesis in table form, and every later pattern chapter names the bucket it sits in. Each placement is also a claim about code, so the example for this chapter checks the claims that can be checked by running something: that a `Surcharge` layer is chosen per consignment while the program runs, that an `@audited` function is rebound when its definition executes, that a tariff table module loads once however many modules import it.

{% include excalidraw.html name="03-the-three-way-split" caption="Figure 3.1: The three-way split. Two questions sort every catalogue pattern: does the name mean two things in Python, and does a language feature resolve the force without the pattern's structure? The answers place each pattern in dissolves, survives or needs disambiguating." %}

The ladder in the figure reads top to bottom. A name that means two things goes to the third band before anything else is asked, because arguing about the force of an ambiguous name produces two arguments that never meet.

## Two questions that sort a pattern

The first question is about the name. Does the word mean one thing, or does Python attach a second meaning to it? Decorator is the clearest case: the catalogue pattern and the `@` syntax share a word and almost nothing else. If the name is shared, the pattern goes in the third bucket and the chapter that develops it keeps both meanings visible.

The second question is about the force. Does a language feature resolve the force without the pattern's structure? Every pattern resolves a force in a context. The catalogue assumes that behaviour travels inside objects of declared classes, so Strategy needs a class to hand a caller a behaviour. When functions are first-class values, the force (a caller must choose behaviour at runtime) is still there, but the language resolves it without the classes. When no feature does, the pattern survives as design.

Two precautions keep the second question strict. A feature resolves a force only when it resolves all of it, not just the easy half. And "dissolves" never means "forget it": the force remains, and the vocabulary is still useful when a team talks about it. What dissolves is the class structure the catalogue drew around the force.

## Patterns that dissolve

The first eleven rows of the table are the ones where a Python feature resolves the force without the structure. The table lists every pattern the book places, in all three buckets, with the chapter that develops it.

| Pattern | Bucket | What Python gives you | Developed in |
| --- | --- | --- | --- |
| Strategy | Dissolves | A callable or `functools.partial` | [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) |
| Iterator | Dissolves | A generator or `__iter__` | [Iterator: generators and the iterator protocol]({{ '/docs/24-iterator-generators-and-the-iterator-protocol/' | relative_url }}); async form in [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}) |
| Factory Method | Dissolves | A class or function in a dict | [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) |
| Template Method | Dissolves | A function taking hook callables; an ABC hook only where steps share state | [Template Method and the function alternative]({{ '/docs/13-template-method-and-the-function-alternative/' | relative_url }}) |
| Builder | Dissolves | A keyword-only dataclass | [Builder, dataclasses, and Prototype]({{ '/docs/17-builder-dataclasses-and-prototype/' | relative_url }}) |
| Prototype | Dissolves | `dataclasses.replace` or `copy` | [Builder, dataclasses, and Prototype]({{ '/docs/17-builder-dataclasses-and-prototype/' | relative_url }}) |
| Visitor | Dissolves | `singledispatch` for an open set, `match` with `assert_never` for a closed set | [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}); [singledispatch: the Visitor the language gives you]({{ '/docs/28-singledispatch/' | relative_url }}) |
| Null Object | Dissolves | `X | None` checked by mypy | [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) |
| Value Object | Dissolves | A frozen dataclass | [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) |
| Metaclass registry | Dissolves | `__init_subclass__` | [Metaclasses, __init_subclass__, and registries]({{ '/docs/29-metaclasses-init-subclass-and-registries/' | relative_url }}) |
| If-chain dispatch | Dissolves | A dict of callables, with EAFP | [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}) |
| State | Survives | Enums, `match` and small classes help; the transition table remains design | [State and finite state machines]({{ '/docs/14-state-and-finite-state-machines/' | relative_url }}) |
| Command | Survives | A `functools.partial` for the plain deferred call; undo and queues remain | [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) |
| Abstract Factory | Survives | A family of related factories stays a design decision | [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) |
| Adapter | Survives | Duck typing removes it only when the shapes already match | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| Facade | Survives | A module or class that narrows a subsystem | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| Bridge | Survives | Two hierarchies varying independently, joined by a Protocol | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| Composite | Survives | A uniform interface over a tree | [Composite and Flyweight]({{ '/docs/21-composite-and-flyweight/' | relative_url }}) |
| Flyweight | Survives | Shared immutable state; `__slots__` and interning help | [Composite and Flyweight]({{ '/docs/21-composite-and-flyweight/' | relative_url }}) |
| Observer | Survives | Callbacks, but delivery order, failure isolation and subscriber lifetime remain | [Observer]({{ '/docs/22-observer/' | relative_url }}) |
| Mediator | Survives | Coordination in one place | [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}) |
| Chain of Responsibility | Survives | Ordered handlers with a pass-along rule | [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}) |
| Memento | Survives | A frozen dataclass snapshot; what to capture remains | [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) |
| Interpreter | Survives | A grammar and its evaluator remain design | [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) |
| Resource acquisition | Survives | The `with` statement and context managers | [Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) |
| Decorator pattern vs `@decorator` syntax | Needs disambiguating | Wrapper objects composed at runtime vs a function rebinding at definition time | [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}); [Decorators done right]({{ '/docs/26-decorators-done-right/' | relative_url }}) |
| Singleton | Needs disambiguating | A module built at import time by default; Borg and metaclass as variants | [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) |
| Proxy | Needs disambiguating | A surrogate object vs attribute interception with `__getattr__`, `property` and `cached_property` | [Dynamic attributes: __getattr__ and Proxy as a feature]({{ '/docs/30-dynamic-attributes-and-proxy/' | relative_url }}); [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) |
| "Interface" | Needs disambiguating | `Protocol` (structural) vs an ABC (nominal) | [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) |

The example shows the dissolved rows at their smallest. A pricing rule is a `Callable[[Consignment], Money]`, so `quote(consignment, rule)` accepts a `def`, a lambda or a `functools.partial` in the same slot and no `RateStrategy` interface exists. A factory is a class sitting in the `GATEWAYS` dict: `GATEWAYS["AIRCO"]()` builds an `AircoGateway`, and no creator subclass is involved. A paged view of a `TrackingHistory` is a generator over `itertools.batched` that pulls nothing until the first page is requested. A booking request is a keyword-only dataclass, so a positional call fails with `TypeError` and no builder class is needed to name the arguments. A copy with one field changed is `dataclasses.replace`. An event visitor is `singledispatch`, and the event classes carry no `accept` method. A carrier registry is `__init_subclass__`, which also rejects a duplicate code with `DuplicateCarrierError`.

Each of these resolves its force with a feature, not a class. The strategy's force, a caller choosing behaviour at runtime, is still met, by a value passed in. The registry's force, knowing every carrier, is still met, by a dict filled at class creation. What disappears is the participant list: the creator, the product interface, the `accept` method, the builder.

## Patterns that survive

The survivors keep a force that no language feature resolves. They fall into three groups, and the grouping is by the force, which is also how a team reviewing a design meets them.

**Lifecycle.** State, Command with undo, and resource acquisition belong here. A consignment passes from booked to loaded to departed to cleared to delivered, and which transitions are legal is a business rule that someone has to write down in one place; an enum and a `match` help, but the transition table is the design. Command survives where history matters. A deferred call is a `functools.partial` in a `collections.deque`, and the example witnesses that queued partials change nothing until called. Undo is different: a partial has no `undo`, and an `Amendment` that records the weight it replaces is a command object, because the reversal needs data the plain call never kept. Resource acquisition is the lifecycle of something that must be released on every path, which is the force the `with` statement serves; the pattern survives as the contract a context manager honours.

**Structure.** Adapter, Facade, Bridge, Composite and Flyweight are about the shape of what is built. Duck typing removes an Adapter only when the shapes already match. A Facade narrows a large subsystem to the few calls a caller needs, a Bridge lets an abstraction and its implementations vary independently, and a Composite gives a `ConsolidatedShipment` of consignments one interface. Flyweight shares immutable state that would otherwise repeat. None of these forces concerns how a behaviour is passed, so no feature that makes functions values touches them.

**Coordination.** Observer, Mediator, Chain of Responsibility, Memento and Interpreter govern how parties agree. Observer is callbacks in Python, but the hard parts of the pattern are untouched by that: in what order subscribers are called, whether one failing subscriber stops the rest, and how long a subscriber stays alive. A Mediator centralises who talks to whom, a Chain of Responsibility decides who handles a request, a Memento captures state to restore later, and an Interpreter evaluates a small grammar. Each of these is still a decision about relationships, and the code is shorter in Python without the decision being smaller.

## Names that need disambiguating

Four names mean two things in Python. The first, Decorator, matters most, because confusing the two produces wrong designs.

**Decorator, the pattern.** In the catalogue, a decorator is an object that wraps another object with the same interface and adds a responsibility, and a stack of such wrappers is composed at runtime, often per request. In the example, a `BaseRate` applies a pricing rule and a `Surcharge` wraps any `RateCalculator` and adds a fixed fee:

```python
@dataclass(frozen=True, slots=True)
class Surcharge:
    """Adds a fixed fee to whatever the wrapped calculator prices."""

    inner: RateCalculator
    fee: Money

    def price(self, consignment: Consignment, /) -> Money:
        return self.inner.price(consignment) + self.fee


def calculator_for(
    consignment: Consignment,
    base: RateCalculator,
    *,
    heavy_over: Weight,
    heavy_fee: Money,
) -> RateCalculator:
    """Choose the layers for this consignment while the program runs."""
    if consignment.weight.kilograms > heavy_over.kilograms:
        return Surcharge(base, heavy_fee)
    return base
```

The witness test shows what makes this the pattern. For a light consignment `calculator_for` returns the `BaseRate` itself; for a heavy one it returns a `Surcharge` whose `inner` is that same `BaseRate`, which is left unchanged and can still price on its own. The layer is chosen per consignment at runtime, the stack is data, and `Surcharge` has no base class beyond `object`: it satisfies `RateCalculator` structurally, so the Protocol, and no inheritance, makes it interchangeable with the thing it wraps.

**The `@decorator` syntax.** The syntax is a statement about a function name. `@audited(sink)` above a `def` means "evaluate `audited(sink)`, call the result on the function, and bind the name to what comes back", and it happens once, when the definition executes:

```python
@audited(audit_trail.append)
def quote_carrier(consignment: Consignment, carrier: str) -> Money:
```

The witness for this is about timing. `quote_carrier` is no longer the function written under it: the rebound name is a wrapper that keeps the original's name, reaches it through `__wrapped__`, and reports to the sink only when called. Nothing is chosen per consignment and no stack is composed from data; there is one function, replaced at definition time.

The two mechanisms are independent, and one test pins that: an audited function placed inside a `Surcharge` stack is reported once per call, and neither mechanism adds the other's attributes. Either can be used without the other, and a team that says "we use the Decorator pattern here" while pointing at `@audited` has made a claim that the code can't support. The pattern gets its own treatment, with Proxy, in [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}).

**Singleton.** The default answer is a module built at import time. The `tariff_table` module builds its `Tariff` once when it is first imported, and the witness imports it twice, checks both imports give back the same module object and the same `TARIFF`, and reads a separate load log that records exactly one load. The log lives in another module, since a counter inside the module being loaded would reset whenever that module was rebuilt. Borg and metaclass versions exist and have narrow uses. `functools.cache` doesn't make a singleton: it memoises calls, and under threads it isn't guaranteed to run a function once.

**Proxy.** The catalogue's proxy is a surrogate object standing in for another. Python adds a second sense: intercepting attribute access with `__getattr__`, `property` or `cached_property`. They are different tools. `CarrierGatewayProxy` is the surrogate: it answers `book` from its own per-consignment cache and forwards every attribute it doesn't define to the wrapped gateway, and unknown names raise `AttributeError`. `LazyTrackingHistory` is lazy initialisation without any surrogate: a `cached_property` runs its loader on first access only, and the value then sits in the instance dictionary.

**Interface.** The word means a structural `Protocol` or a nominal ABC, and they behave differently. In the example, a class that has never heard of `CarrierGateway` satisfies it, because the shape matches, but it is not a `CarrierBase`; and an incomplete subclass of that base can't be instantiated. Pick the Protocol when the consumer defines the need, a nominal base class when the family shares code or registers through `__init_subclass__`.

## Beyond the catalogue

Three idioms do the work a catalogue entry would have done, and they are not in the catalogue. They appear in the map because a reader looking for the pattern should be pointed at them.

**Null Object.** A later addition to the pattern literature, described by Bobby Woolf in "Null Object" (*Pattern Languages of Program Design 3*, Addison-Wesley, 1998), it replaces a missing collaborator with an object that does nothing. Here `find_gateway` returns `CarrierGateway | None`, and the witness asserts `[union-attr]` from mypy on the unguarded caller and a clean pass on the guarded one:

```python
def book_with(consignment: Consignment) -> str:
    gateway = find_gateway("FASTLINE")
    if gateway is None:
        return "unknown carrier"
    return gateway.book(consignment)
```

**Value Object.** `Money` is a frozen dataclass: equal by value, with no `__dict__` because of `slots=True`, and addition defined only within one currency. The declaration supplies equality, hashing and immutability; the same-currency `__add__` is the one method written by hand.

**Dict dispatch and EAFP.** An if-chain over carrier codes becomes a dict lookup. The same dict that holds the gateway classes answers "which carrier?" and a missing key is handled by the exception or by `.get`, the style Python calls easier to ask forgiveness than permission. Keep the branch when cases need different arguments or the order of the tests matters.

## Patterns that straddle two buckets

Three patterns don't sit cleanly in one bucket, because the catalogue entry holds two forces and a feature resolves only one.

Command is the plain case already seen: the deferred call dissolves into a `functools.partial` and the undoable, queued command survives. The map lists Command under survives because the part that remains is the part that needed design.

Template Method fixes the order of steps and lets variants supply some of them. The example's `declare_customs` is a function that takes hooks: it classifies, assesses duty and certifies in that order, and a `CustomsHooks` value supplies the varying parts per destination. That dissolves the inheritance structure. Where the steps share mutable state that must be threaded through them, an object with overridable methods remains the right shape, and the Template Method chapter says where that line falls.

Visitor splits by whether the set of types is open or closed. For an open set that others will extend, `singledispatch` registers a handler per class, as `describe` does for handling events. For a closed set, such as the five events in the `HandlingEvent` union, a `match` statement ending in `assert_never` makes the type checker report any event a handler forgot. Either way the `accept` method goes. The pattern is classed as dissolved because both forms apply a Python feature, and Memento and Interpreter, its chapter companions, are survivors.

## Build, run, observe

From the repository root, run the one-time sync, then work from the example directory:

```bash
uv sync --locked --all-packages
cd examples/03-three-way-split
uv run pytest -v
uv run mypy --strict src tests
```

A fresh run, with the repository path shown as `<repo>`:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 19 items

tests/test_disambiguate.py::test_gof_decorator_wraps_an_instance_at_runtime PASSED [  5%]
tests/test_disambiguate.py::test_decorator_syntax_rebinds_the_name_at_definition_time PASSED [ 10%]
tests/test_disambiguate.py::test_the_two_decorators_are_independent PASSED [ 15%]
tests/test_disambiguate.py::test_module_is_one_instance_for_every_importer PASSED [ 21%]
tests/test_disambiguate.py::test_cached_property_is_lazy_initialisation_without_a_proxy PASSED [ 26%]
tests/test_disambiguate.py::test_proxy_forwards_only_missing_attributes PASSED [ 31%]
tests/test_disambiguate.py::test_protocol_is_structural_and_abc_is_nominal PASSED [ 36%]
tests/test_dissolve.py::test_strategy_slot_accepts_def_lambda_and_partial PASSED [ 42%]
tests/test_dissolve.py::test_a_class_is_already_a_factory_method PASSED  [ 47%]
tests/test_dissolve.py::test_iterator_is_a_lazy_generator PASSED         [ 52%]
tests/test_dissolve.py::test_template_method_is_a_function_taking_hooks PASSED [ 57%]
tests/test_dissolve.py::test_builder_is_a_keyword_only_dataclass PASSED  [ 63%]
tests/test_dissolve.py::test_prototype_is_replace PASSED                 [ 68%]
tests/test_dissolve.py::test_visitor_is_singledispatch_without_accept PASSED [ 73%]
tests/test_dissolve.py::test_null_object_is_an_optional_checked_by_mypy PASSED [ 78%]
tests/test_dissolve.py::test_value_object_is_a_frozen_dataclass PASSED   [ 84%]
tests/test_dissolve.py::test_registry_is_init_subclass PASSED            [ 89%]
tests/test_survive.py::test_deferred_command_is_a_partial_in_a_deque PASSED [ 94%]
tests/test_survive.py::test_undo_needs_a_command_object PASSED           [100%]

============================== 19 passed in 0.97s ==============================
```

```text
Success: no issues found in 11 source files
```

Read the test names as the map's claims in short form. The Decorator pair and the independence test sit together in the disambiguation file; the singleton test passes only because the load log shows a single load; the Null Object test runs mypy on two source strings and asserts the exact error code, so a green run is a statement about the type checker as well as the code.

One experiment: in `tests/test_dissolve.py`, delete the `if gateway is None:` guard and its return from the `_GUARDED` string and run `uv run pytest`. `test_null_object_is_an_optional_checked_by_mypy` fails, because mypy now reports `[union-attr]` for that snippet. Restore the guard and it passes. A second experiment uses the same loop: edit `calculator_for` to return a `Surcharge` for every consignment, and see which test notices.

## For deeper coverage

The canonical catalogue is *Design Patterns: Elements of Reusable Object-Oriented Software* by Gamma, Helm, Johnson and Vlissides; read the introduction on how a pattern is described and the Consequences sections for the forces. *Fluent Python* by Luciano Ramalho (second edition) covers first-class functions, the data model, decorators and dataclasses, which are the features behind the dissolved rows. *Effective Python: 125 Specific Ways to Write Better Python* by Brett Slatkin (third edition) gives short rules on closures, generators and decorators. *Python Object-Oriented Programming* by Steven F. Lott and Dusty Phillips (fifth edition) maps the catalogue onto Python classes. The book list is on the [bibliography page]({{ '/bibliography/' | relative_url }}).

Online, [python-patterns.guide](https://python-patterns.guide/) by Brandon Rhodes treats the catalogue pattern by pattern in Python. The language references are [PEP 544](https://peps.python.org/pep-0544/) on Protocols, [PEP 557](https://peps.python.org/pep-0557/) on data classes, [PEP 695](https://peps.python.org/pep-0695/) on type parameter syntax and the `type` statement, and the [functools documentation](https://docs.python.org/3/library/functools.html) for `partial`, `singledispatch`, `cached_property` and `wraps`.
