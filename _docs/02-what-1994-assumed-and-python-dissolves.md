---
title: "What 1994 assumed, and what Python dissolves"
order: 2
layout: tutorial
sectionid: docs
part: "why-not-gof"
description: "The assumptions the 1994 pattern catalogue was written under, and the Python 3.15 features (callables, generators, protocols, modules, optional types) that remove the scaffolding while the underlying force often remains."
---

## Learning objectives

By the end of this chapter you can:

- State the assumption about objects and classes that the 1994 catalogue was written under, and why a catalogue is tied to the language features its authors could rely on.
- Explain, for Strategy, Iterator, Adapter, Singleton and Null Object, which Python feature removes the scaffolding and what that feature does.
- Read a `Callable` type alias, a `Protocol` and a generator function as the replacements for a strategy hierarchy, an interface and an iterator class.
- Say what structural typing doesn't remove, and why an adapter is still needed when two shapes differ.
- Apply one test to any pattern: did the force move, or only the mechanism?

## Why this matters

A pattern catalogue is a record of decisions made with the tools on hand. Its authors say as much: the language you design in shapes the patterns you can state, and a catalogue written for one set of language features would read differently if the features changed. Read that way, the 1994 book isn't a rulebook that Python breaks. It is a snapshot of one set of assumptions, and the useful question about each entry is which assumption it depended on.

The practical stake is code review. A pull request that adds a `PricingStrategy` base class, three subclasses and a factory to price a consignment is faithful to the catalogue and wasteful in Python. A review that only says "that isn't Pythonic" teaches nothing. A review that names the assumption (behaviour has to arrive inside an object of a declared class) and the feature that removes it (a function is already an object) teaches the reader to make the call themselves, and to notice the other case, where the force is real and the pattern still pays for itself.

{% include excalidraw.html name="02-what-1994-assumed-and-python-dissolves" caption="Figure 2.1: Assumptions behind the classic patterns, each paired with the Python feature that removes it: functions as objects, structural typing, generators, modules imported once, and absence checked by the type checker." %}

Each row of the figure is a section below. The examples are short excerpts from the runnable [three-way split example]({{ '/examples/03-three-way-split/' | relative_url }}), so every name you see exists, passes its tests and satisfies `mypy --strict`.

## The object model the catalogue assumed

The catalogue's central working assumption is that a unit of behaviour reaches a call site wrapped in an object whose class you declared in advance. If a rule for pricing a consignment has to be swapped at run time, you declare an abstract class with one method, subclass it once per rule, and pass an instance. If a caller must walk a collection without knowing its layout, you declare an iterator class with the traversal methods and a state field for the cursor. If two parts disagree on a method name, you declare a class that wraps one and renames the call. If exactly one instance of something must exist, you hide the constructor behind a class method and a static field.

In that setting a class is the only way to name a behaviour, and an interface is the only way to promise one. Nothing in the assumption is wrong for a language whose functions can't be passed around, whose loops can't suspend, whose types are matched by declared name, and whose files have no identity at run time. It is a sound description of the tools. The patterns are the engineering that makes those tools do the job.

Python 3.15 differs on each count. Functions are objects with a type and can be stored, passed and returned. A function containing `yield` suspends and resumes. A `Protocol` lets the checker match types by shape instead of by declared name. A module is an object, created once, on first import. And `X | None` is a type the checker tracks through every branch.

## Functions are objects

Strategy, in the 1994 form, is a family of interchangeable algorithms behind one interface, so the caller chooses at run time. The force is real: pricing rules vary, and the code that quotes a price should not know which one it holds. The mechanism is a class hierarchy because the catalogue assumes behaviour travels inside objects of declared classes.

In Python the algorithm is a callable, and the interface is a type alias:

```python
type PricingRule = Callable[[Consignment], Money]

_CENT = Decimal("0.01")


def flat_rate(consignment: Consignment) -> Money:
    """A fixed price for any consignment."""
    return Money(Decimal("25.00"), "EUR")


def per_kg(consignment: Consignment, rate: Decimal = Decimal("1.20")) -> Money:
    """A price proportional to weight."""
    amount = (Decimal(str(consignment.weight.kilograms)) * rate).quantize(_CENT)
    return Money(amount, "EUR")


def quote(consignment: Consignment, rule: PricingRule) -> RateQuote:
    """Price a consignment with whichever rule the caller passes."""
    return RateQuote(consignment.id, rule(consignment))
```

`type PricingRule = ...` is the PEP 695 alias statement, new in 3.12 and the idiom for naming a type in 3.15. It says what a pricing rule is: anything that takes a `Consignment` and returns `Money`. `flat_rate` and `per_kg` satisfy it as plain functions, with no base class to inherit and no method to override. `quote` is the context of the 1994 pattern, reduced to one line that calls whatever it was given.

A rule that needs configuration doesn't need a constructor and a field. It needs its argument fixed in advance, which is what `functools.partial` does:

```python
from_partial: PricingRule = partial(per_kg, rate=Decimal("2.00"))
```

The test assigns that value to a variable annotated `PricingRule`, alongside a lambda and a `def`, and passes all three through `quote`. The checker accepts each because each is a callable with the right signature. That is the dissolve, stated precisely: the force (swap the algorithm) is unchanged, and the mechanism (a declared hierarchy) is replaced by a first-class value.

The deferred half of Command goes the same way. A request packaged as an object to run later is a call with its arguments bound, which is again a partial or a closure. The half of Command that records what to undo, or orders a queue, is a different matter: it survives.

## Generators

Iterator is the clearest case of a pattern the language absorbed. The force is that a consumer should pull elements one at a time without knowing how the producer stores them. The 1994 mechanism is an iterator class holding a cursor, plus a method to advance and a method to test for the end. Python builds the protocol into the data model: any object whose `__iter__` returns an iterator, an object with `__next__`, works in a `for` loop, a comprehension, `list()` and `sum()`.

You rarely write that class. A function containing `yield` is a generator function, and calling it returns an object that already implements the protocol, with the cursor held in the suspended frame (PEP 255 introduced the mechanism). The example pages a tracking history:

```python
def pages(history: TrackingHistory, size: int) -> Iterator[tuple[HandlingEvent, ...]]:
    """Yield the history in pages of at most ``size`` events, reading lazily."""
    yield from batched(history, size, strict=False)
```

`TrackingHistory` is a small class whose `__iter__` returns an iterator over a source of `HandlingEvent` values, and `pages` groups them into tuples of at most `size`. The word "lazily" in the docstring is checked by a test: the test builds a source that counts how many events it has produced, asks for the first page of three, and asserts that three were pulled, not seven. Nothing is read until the caller asks. A consumer that stops after the first page never touches the rest.

What the language did not remove is the decision to expose a sequence of items without exposing its storage. That decision is still the design, and a `TrackingHistory` that hides how events are fetched is still the right boundary. Only the classes are gone. When the sequence is asynchronous, the same idea has an `async` form with one extra rule about cleanup, which belongs with the asyncio material.

## Structural typing

The 1994 mechanism for promising a method is an interface: a named type that classes must declare they implement. The promise is checked by name, so two classes with identical methods but no shared declaration are, to the compiler, strangers. The cost shows up whenever the code that needs the promise and the code that keeps it are written separately.

A `Protocol`, defined in PEP 544, checks by shape. The booking code in the example needs one thing from a carrier:

```python
@runtime_checkable
class CarrierGateway(Protocol):
    """What the booking code needs from a carrier."""

    def book(self, consignment: Consignment, /) -> str: ...


class FastlineGateway:
    code: ClassVar[str] = "FASTLINE"

    def book(self, consignment: Consignment, /) -> str:
        return f"FASTLINE:{consignment.id}"


class AircoGateway:
    code: ClassVar[str] = "AIRCO"

    def book(self, consignment: Consignment, /) -> str:
        return f"AIRCO:{consignment.id}"
```

Each has a `book` with a compatible signature, so each is accepted wherever the protocol is expected. Neither gateway refers to `CarrierGateway`, so either could live in a module that never imports it, and a third-party client class can satisfy it without being edited.

That removes the scaffolding Adapter used to supply in one common situation: two parts already agree on shape and only disagree on declaration. It doesn't remove the Adapter pattern. If a carrier's client exposed `submit_shipment(payload)` instead of `book(consignment)`, no checker can bridge that. The force of Adapter is a mismatch of shape, and a mismatch of shape needs code that translates. Duck typing removes the adapter only when the shapes already match; when they don't, you write the wrapper, and it's the same class it has always been.

Two cautions apply. `@runtime_checkable` makes `isinstance` work against a protocol, but it checks that the names exist and nothing about signatures, so it's a weaker guarantee than the static check. And a mock object is typed as `Any` by the checker, so it satisfies any protocol whether or not it matches. Both are reasons to rely on `mypy --strict`, not runtime checks, for the shape.

## Modules

Singleton's force is that some things must exist once: a tariff table, a configuration, a registry. In 1994 that took a class that hides its constructor, holds its single instance in a static field and exposes an accessor. In Python the default answer is already there. A module is an object, the import system builds it once on first import, and every later `import` returns the same object from `sys.modules`.

The example builds its tariff that way:

```python
def _load() -> Tariff:
    record_load("tariff_table")
    return Tariff(
        MappingProxyType(
            {
                "EUROPE": Money(Decimal("1.20"), "EUR"),
                "ASIA": Money(Decimal("2.40"), "EUR"),
            }
        )
    )


TARIFF = _load()
```

`TARIFF` is built when `tariff_table` is first imported, and the test that imports the module twice sees one load. The mapping sits behind `MappingProxyType`, so callers read it but can't reassign entries. There's no accessor and no guard, because there is no second way to get an instance.

A module-level object doesn't always suffice. If each test needs a clean instance, or you need one per tenant, pass the object in as a parameter; Borg and metaclass variants answer other needs, and [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) compares them.

## Absence in the type

Absence raises a different force: a caller that asks for a thing which may not exist should not have to test for absence everywhere. The classic answer, the Null Object pattern from the later pattern literature, is to return a real object whose methods do nothing, so the caller proceeds without branching. The cost is that absence becomes invisible. A `NullGateway.book` that silently returns an empty string books nothing, and the caller never finds out.

Python lets the type say so instead:

```python
def find_gateway(code: str) -> CarrierGateway | None:
    """Return a gateway for a carrier code, or None when the code is unknown."""
    factory = GATEWAYS.get(code)
    if factory is None:
        return None
    return factory()
```

The return type is a union, and the checker won't let a caller treat it as the protocol. A test runs mypy on a snippet that calls `find_gateway("FASTLINE").book(consignment)` with no guard. Here is the line it observes:

```text
<string>:7: error: Item "None" of "CarrierGateway | None" has no attribute "book"  [union-attr]
```

The mistake is caught before the code runs, at the exact expression that forgot the case. The same test confirms that the guarded form (`if gateway is None: return "unknown carrier"`) passes with no output. Absence is neither hidden behind a do-nothing object nor left as a run-time `AttributeError`; it's a branch the checker makes you write.

The force remains here: callers still need protecting from a missing object. Null Object protected them by making the missing case look present. The type checker protects them by making the missing case impossible to ignore. Where a do-nothing default is the correct behaviour (a logger that discards output, a discount of zero), a real null object remains a fine design, and now it's a deliberate choice rather than the only option.

## Did the force move, or only the mechanism?

The five sections share one test, and it sorts patterns you have not read about yet. State the force the pattern resolves in one sentence. Then ask whether a language feature resolves the force without the pattern's structure. A dissolved pattern keeps its force; the feature resolves it without the classes.

For Strategy, the force (vary the algorithm at run time) is intact and the class hierarchy is gone. For Iterator, the force (traverse without exposing storage) is intact and the cursor class is gone. For Singleton, the force (one instance) is intact and the guard is gone. In each, the pattern's vocabulary stays useful for naming the decision, and its scaffolding becomes a function, a generator or a module.

Some patterns fail the dissolve test because the force isn't about mechanism. Composite exists because clients must treat one item and a group of items through the same interface; a `Protocol` makes that cheaper to declare but doesn't decide the recursive structure, how a total is computed across children, or what a leaf does with `add`. State exists because behaviour depends on a history of transitions that must be explicit and checkable; a dictionary of functions can store the table, but the table is the design. Command with undo needs a record of what to reverse and an order in which to do it, and no callable holds that for you. These keep their shape, and later chapters develop each.

The practical consequence is a rule of proportion. When a review comment says "this should be a function", the justification is that the force remains and the mechanism doesn't need a class. When the comment says "this needs a real object", the justification is that the force itself has state, structure or ordering that a callable can't carry. Both comments are about forces, and the grouping of the whole catalogue into what dissolves, what survives and what needs a clearer name is the job of the three-way split chapter.

## For deeper coverage

- *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides; Addison-Wesley, 1994). The Introduction's account of what a design pattern is, and its remark that the language you assume determines which patterns you state, is the source for the argument above. Read it for the forces, not the class diagrams.
- *Fluent Python*, second edition (Luciano Ramalho; O'Reilly). The data model, first-class functions, protocols, generators and the import system, which are the features this chapter relies on.
- *Effective Python*, third edition (Brett Slatkin; Addison-Wesley). Short rules on generators, closures, `partial`, typing and module-level state; read by topic.
- PEP 544, [Protocols: Structural subtyping](https://peps.python.org/pep-0544/); PEP 255, [Simple Generators](https://peps.python.org/pep-0255/); PEP 695, [Type Parameter Syntax](https://peps.python.org/pep-0695/), which also introduces the `type` statement.
- The Python reference, [data model](https://docs.python.org/3/reference/datamodel.html), for `__iter__`, `__next__` and callables.
- Brandon Rhodes, [python-patterns.guide](https://python-patterns.guide/), for the catalogue read through Python.

The full list of books, with editions and links, is on the [bibliography]({{ '/bibliography/' | relative_url }}) page.
