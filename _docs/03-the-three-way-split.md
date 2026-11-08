---
title: "The three-way split: dissolve, survive, disambiguate"
order: 3
layout: tutorial
sectionid: docs
part: "why-python-is-different"
description: "Two questions sort every catalogue pattern into dissolves, survives or needs disambiguating, shown on one runnable shipping example."
---

## Learning objectives

By the end of this chapter you can:

- Apply the two sorting questions to any catalogue pattern, name first: does the name mean two things in Python, and does a language feature do the pattern's job without its structure?
- Place each pattern of the catalogue in its bucket, and name the Python feature that dissolves it or the reason it survives.
- Keep the Decorator pattern and the `@decorator` syntax apart, and say what each one does to a rate calculation.
- Recognise the idioms that belong to no catalogue entry: the optional as Null Object, the frozen dataclass as Value Object, dict dispatch and EAFP.
- Explain why Command, Template Method and Visitor straddle two buckets.
- Run the three-way split example and break one placement to see which check fails.

## Why this matters

A team that shares pattern names can review a design in a sentence. Read without judgement, a catalogue produces two opposite mistakes:

- **Building every pattern as drawn**, with a class hierarchy where a function would do.
- **Declaring patterns obsolete**, and losing the judgement a few of them still carry.

The map below places each pattern by its name and by its force, the pressure that made it worth having. Every later pattern chapter names the bucket it sits in. Each placement is also a claim about code, and the three-way split example runs the ones a test can check: a `Surcharge` layer chosen per consignment at run time, an `@audited` function rebound when its definition executes, and a tariff table module that loads once however many modules import it.

{% include excalidraw.html name="03-the-three-way-split" described="true" caption="Figure 3.1: The three-way split. Two questions sort every catalogue pattern: does the name mean two things in Python, and does a language feature resolve the force without the pattern's structure? The answers place each pattern in dissolves, survives or needs disambiguating." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-03-the-three-way-split" markdown="1">
The ladder reads top to bottom. A name that means two things goes to the needs-disambiguating band before anything else is asked, because arguing about the pressure behind an ambiguous name produces two arguments that never meet.

The first box asks whether the name means two things in Python. Yes leads right, to the band headed "Needs disambiguating": Decorator vs @decorator, Singleton, Proxy, and Protocol vs ABC. No leads down to the accent box, the second question. Yes leads to the band headed "Dissolves into a language feature": Strategy as a callable, Iterator as a generator, Factory Method as a dict of classes, Template Method as hook callables, Builder and Prototype as a dataclass, Visitor as singledispatch or match, and Null Object as a type that allows None. No leads to a box that says no feature resolves it, so the structure stays, and on to the band headed "Survives with its shape": State and Command with undo, Composite and Observer, Chain of Responsibility and Memento.
</div>
</details>

The figure asks about the name first.

## Two questions that sort a pattern

**Does the name mean two things in Python?** The Decorator pattern and the `@` syntax share a word and almost nothing else. A shared name puts the pattern in the needs-disambiguating bucket.

**Does a language feature resolve the force without the pattern's structure?** The catalogue assumes behaviour travels inside objects of declared classes, so Strategy needs a class to hand a caller a behaviour. With first-class functions, a caller still chooses behaviour at run time, but the language meets that need without the classes. When no feature does, the pattern survives as design.

Two rules keep the second question strict:

- **All of it.** A feature resolves a force only if it resolves all of it. A `functools.partial` defers a call but can't undo one, so Command survives.
- **"Dissolves" never means "forget it".** The force remains, and the name is still useful in conversation. Only the class structure the catalogue drew around it goes.

## Patterns that dissolve

The table places every pattern in all three buckets, with where each is developed. In the eleven Dissolves rows, a Python feature does the pattern's job without its structure.

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

The dissolved rows at their smallest:

| Pattern | In code |
| --- | --- |
| Strategy | A pricing rule is a `Callable[[Consignment], Money]`; `quote(consignment, rule)` accepts a `def`, a lambda or a `functools.partial`. No `RateStrategy` interface exists. |
| Factory Method | A class in the `GATEWAYS` dict is the factory: `GATEWAYS["AIRCO"]()` builds an `AircoGateway`, with no creator subclass. |
| Iterator | A paged view of a `TrackingHistory` is a generator over `itertools.batched`, pulling nothing until the first page is requested. |
| Builder | A booking request is a keyword-only dataclass; a positional call raises `TypeError`. |
| Prototype | A copy with one field changed is `dataclasses.replace`. |
| Visitor | An event visitor is `singledispatch`; the event classes have no `accept` method. |
| Registry | A carrier registry is `__init_subclass__`, which rejects a duplicate code with `DuplicateCarrierError`. |

A caller still chooses behaviour at run time, by passing a value in, and the registry still knows every carrier. Only the participant list goes: the creator, the product interface, the `accept` method, the builder.

## Patterns that survive

Each survivor keeps a force no language feature resolves. They fall into three groups:

| Group | Patterns | What stays design |
| --- | --- | --- |
| Lifecycle | State, Command with undo, resource acquisition | Which transitions are legal; what to reverse; release on every path |
| Structure | Adapter, Facade, Bridge, Composite, Flyweight | What is built and how its parts relate |
| Coordination | Observer, Mediator, Chain of Responsibility, Memento, Interpreter | How parties agree |

**Lifecycle.** A consignment goes from booked to loaded to departed to cleared to delivered. An enum and `match` help, but nobody writes the transition table for you. A deferred call is a `functools.partial` in a `collections.deque`, and queued partials change nothing until called. A partial has no `undo`, though: an `Amendment` that records the weight it replaces is a command object, because the reversal needs data the plain call never kept. Resource acquisition survives as the contract a context manager honours.

**Structure.** Duck typing removes an Adapter only when the shapes already match. A Facade narrows a subsystem to the calls a caller needs; a Bridge lets an abstraction and its implementations vary independently; a Composite gives a `ConsolidatedShipment` of consignments one interface; Flyweight shares immutable state. None of these is about how behaviour is passed, so first-class functions don't touch them.

**Coordination.** Observer is callbacks in Python, but the hard parts stay: the order subscribers are called in, whether one failure stops the rest, and how long a subscriber lives. A Mediator centralises who talks to whom, a Chain of Responsibility decides who handles a request, a Memento captures state to restore, and an Interpreter evaluates a small grammar.

## Names that need disambiguating

Four names mean two things in Python. Decorator comes first, because confusing its meanings produces wrong designs.

**Decorator, the pattern.** An object wraps another with the same interface and adds a responsibility, and a stack of wrappers is composed at run time, often per request. A `BaseRate` applies a pricing rule, and a `Surcharge` wraps any `RateCalculator` and adds a fixed fee:

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

The `inner` calculator is unchanged, so the `BaseRate` can still price alone. The layer is chosen per consignment, and the stack is data. `Surcharge` inherits only from `object`; it satisfies `RateCalculator` structurally.

**The `@decorator` syntax.** `@audited(sink)` above a `def` means "evaluate `audited(sink)`, call the result on the function, and bind the name to what comes back", once, when the definition executes:

```python
@audited(audit_trail.append)
def quote_carrier(consignment: Consignment, carrier: str) -> Money:
```

The rebound `quote_carrier` reports to the sink only when called. Nothing is chosen per consignment and no stack is composed from data: one function, replaced at definition time.

The two are independent. An audited function inside a `Surcharge` stack is reported once per call, and neither mechanism adds the other's attributes. A team that says "we use the Decorator pattern" while pointing at `@audited` has made a claim the code can't support. [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) develops both.

**Singleton.** The default is a module built at import time. `tariff_table` builds its `Tariff` once: two imports give the same module object and the same `TARIFF`, and a load log kept in a separate module records one load. (A counter inside the module would reset if the module were rebuilt.) Borg and metaclass versions have narrow uses. `functools.cache` doesn't make a singleton: it memoises calls, and under threads it isn't guaranteed to run a function once.

**Proxy.** The catalogue's proxy is a surrogate object; Python adds attribute interception with `__getattr__`, `property` or `cached_property`.

- `CarrierGatewayProxy` is the surrogate. It answers `book` from a per-consignment cache, forwards every attribute it doesn't define to the wrapped gateway, and raises `AttributeError` for unknown names.
- `LazyTrackingHistory` is lazy initialisation with no surrogate: a `cached_property` runs its loader on first access, and the value then sits in the instance dictionary.

**Interface.** A structural `Protocol` or a nominal ABC. A class that has never heard of `CarrierGateway` satisfies it because the shape matches, but it isn't a `CarrierBase`, and an incomplete subclass of that base can't be instantiated. Use the Protocol when the consumer defines the need, and a base class when the family shares code or joins a registry through `__init_subclass__`.

## Beyond the catalogue

Three idioms do a pattern's work without a catalogue entry:

**Null Object.** `find_gateway` returns `CarrierGateway | None`. mypy reports `[union-attr]` on an unguarded caller and passes this one:

```python
def book_with(consignment: Consignment) -> str:
    gateway = find_gateway("FASTLINE")
    if gateway is None:
        return "unknown carrier"
    return gateway.book(consignment)
```

**Value Object.** `Money` is a frozen dataclass: equal by value, no `__dict__` because of `slots=True`, and addition defined only within one currency. The declaration supplies equality, hashing and immutability; the same-currency `__add__` is the one method written by hand.

**Dict dispatch and EAFP.** An if-chain over carrier codes becomes a dict lookup, and the dict that holds the gateway classes also answers "which carrier?". A missing key is handled by the exception or by `.get`, the style the Python glossary calls EAFP, easier to ask for forgiveness than permission. Keep the branch when cases need different arguments or the order of the tests matters.

## Patterns that straddle two buckets

Each of these holds two forces, and a Python feature resolves only one:

| Pattern | Dissolves | Survives | Listed as |
| --- | --- | --- | --- |
| Command | The deferred call, as a `functools.partial` | Undo and queues | Survives |
| Template Method | The inheritance, as a function taking hooks | Overridable methods where steps share state | Dissolves |
| Visitor | The `accept` method, as `singledispatch` or `match` | Nothing in Visitor itself; Memento and Interpreter, in its chapter, survive | Dissolves |

`declare_customs` classifies, assesses duty and certifies, in that order, and a `CustomsHooks` value supplies the varying parts per destination. Where steps share state and code every hook would otherwise repeat, an object with overridable methods is still the right shape.

Visitor splits on whether the set of types is open or closed. For an open set others will extend, `singledispatch` holds one handler per class, as `describe` does for handling events. For a closed set, such as the five events in the `HandlingEvent` union, a `match` ending in `assert_never` makes the type checker report any event a handler forgot.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/03-three-way-split
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 19 cases pass, and mypy reports no issues in 11 source files. The Null Object case runs mypy on two source strings and checks the exact error code, so a green run is a statement about the type checker as well as the code.

- **Drop the guard.** In `tests/test_dissolve.py`, delete the `if gateway is None:` guard and its return from the `_GUARDED` string. The Null Object case fails, because mypy now reports `[union-attr]` for that snippet.
- **Always surcharge.** Make `calculator_for` return a `Surcharge` for every consignment. Only the Decorator pattern case fails, because a light consignment no longer gets the bare `BaseRate`; the other eighteen pass, and mypy stays clean.

## What you can do now

- Apply the two sorting questions: does the name mean two things in Python, and does a feature do the pattern's job without its structure?
- Place a pattern in its bucket with the reason, using the table: the feature that dissolves it, the reason it survives, or the name that needs clarifying.
- Keep `Surcharge` apart from `@audited`, and show they compose independently.
- Recognise the idioms that belong to no entry: `find_gateway` as the optional Null Object, `Money` as the frozen Value Object, and dict dispatch with EAFP in `GATEWAYS`.
- Explain the straddlers: Command, `declare_customs` and `describe`.
- Run the three-way split example and the `_GUARDED` experiment, and say what each placement claims.

## For deeper coverage

The canonical catalogue is *Design Patterns: Elements of Reusable Object-Oriented Software* by Gamma, Helm, Johnson and Vlissides; read the introduction on how a pattern is described and the Consequences sections for the forces. Null Object is a later addition to the pattern literature, described by Bobby Woolf in "Null Object" (*Pattern Languages of Program Design 3*, Addison-Wesley, 1998).

*Fluent Python* by Luciano Ramalho (second edition) covers first-class functions, the data model, decorators and dataclasses, which are the features behind the dissolved rows. *Effective Python: 125 Specific Ways to Write Better Python* by Brett Slatkin (third edition) gives short rules on closures, generators and decorators. *Python Object-Oriented Programming* by Steven F. Lott and Dusty Phillips (fifth edition) maps the catalogue onto Python classes. The book list is on the [bibliography page]({{ '/bibliography/' | relative_url }}).

Online, [python-patterns.guide](https://python-patterns.guide/) by Brandon Rhodes treats a selection of the catalogue, pattern by pattern, in Python. The language references are [PEP 544](https://peps.python.org/pep-0544/) on Protocols, [PEP 557](https://peps.python.org/pep-0557/) on data classes, [PEP 695](https://peps.python.org/pep-0695/) on type parameter syntax and the `type` statement, and the [functools documentation](https://docs.python.org/3/library/functools.html) for `partial`, `singledispatch`, `cached_property` and `wraps`.
