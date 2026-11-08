---
title: "What 1994 assumed, and what Python dissolves"
order: 2
layout: tutorial
sectionid: docs
part: "why-not-gof"
description: "The assumptions the 1994 pattern catalogue was written under, and the Python features (callables, generators, protocols, modules, optional types) that remove the scaffolding while the underlying force often remains."
---

## Learning objectives

By the end of this chapter you can:

- State the assumption about objects and classes that the 1994 catalogue was written under, and why a catalogue is tied to the language features its authors could rely on.
- Explain, for Strategy, Iterator, Adapter, Singleton and Null Object, which Python feature removes the scaffolding and what that feature does.
- Read a `Callable` type alias, a `Protocol` and a generator function as the replacements for a strategy hierarchy, an interface and an iterator class.
- Say what structural typing doesn't remove, and why an adapter is still needed when two shapes differ.
- Apply one test to any pattern: did the force move, or only the mechanism?

## Why this matters

A pull request adds a `PricingStrategy` base class, three subclasses and a factory to price a consignment. It's faithful to the catalogue and wasteful in Python. "That isn't Pythonic" teaches nothing. Naming the assumption (behaviour has to arrive inside an object of a declared class) and the feature that removes it (a function is already an object) lets the author make the call next time, and spot the other case, where the force is real and the pattern still pays.

The catalogue's authors say the language you design in shapes the patterns you can state. Each entry depended on some feature of the languages of 1994, and the question to ask is which one.

{% include excalidraw.html name="02-what-1994-assumed-and-python-dissolves" described="true" caption="Figure 2.1: Assumptions behind the classic patterns, each paired with the Python feature that removes it: functions as objects, structural typing, generators, modules imported once, and absence checked by the type checker." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-02-what-1994-assumed-and-python-dissolves" markdown="1">
Five rows, each an assumption on the left with an arrow labelled "becomes" to a Python feature on the right. Behaviour travels inside an object, one rule class per pricing variant, becomes `PricingRule` and `per_kg`: functions are objects. A shared interface declared by inheriting from a base class becomes `CarrierGateway`, structural typing through a Protocol. Traversal needing its own object to hold the position becomes `pages`, a generator pulling one page at a time. One instance needing a guarded class with a private constructor becomes `tariff_table`, a module imported once with `TARIFF` built then. Absence needing a do-nothing stand-in becomes `CarrierGateway | None` from `find_gateway`, checked by the type checker.
</div>
</details>

Each row of the figure is a section below. The listings come from the runnable [three-way split example]({{ '/examples/03-three-way-split/' | relative_url }}).

## The object model the catalogue assumed

The catalogue assumes behaviour reaches a call site inside an object whose class you declared in advance:

| Need | 1994 mechanism | Python feature |
| --- | --- | --- |
| Swap a pricing rule at run time | Abstract class, one subclass per rule | Functions are objects |
| Walk a collection without knowing its layout | Iterator class with a cursor field | A function with `yield` suspends and resumes |
| Promise a method to code written separately | A named interface each class declares | A `Protocol` matches by shape |
| Exactly one instance | Hidden constructor, static field, accessor | A module is created once, on first import |
| A thing that may not exist | An object whose methods do nothing | An optional type the checker tracks through every branch |

That's a sound description of a language whose functions can't be passed around, whose loops can't suspend, whose types match by declared name and whose files have no run-time identity. The patterns are the engineering that makes those tools do the job.

## Functions are objects

Strategy is a family of interchangeable algorithms behind one interface, so the caller chooses at run time. The force is real: pricing rules vary, and the code that quotes a price shouldn't know which one it holds. In Python the algorithm is a callable, and the interface is a type alias:

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

`type PricingRule = ...` is the PEP 695 alias statement, new in 3.12. `flat_rate` and `per_kg` satisfy it as plain functions, and the 1994 Context class shrinks to the one-line `quote`. A rule that needs configuration needs its argument fixed in advance, not a constructor and a field:

```python
from_partial: PricingRule = partial(per_kg, rate=Decimal("2.00"))
```

A `partial`, a lambda and a `def` all type-check as `PricingRule` and all price through `quote`. The force is unchanged; a first-class value replaces the hierarchy.

The deferred half of Command goes the same way: a request to run later is a call with its arguments bound, a partial or a closure. The half that records what to undo, or orders a queue, survives.

## Generators

Iterator's force is that a consumer pulls elements one at a time without knowing how the producer stores them. The 1994 mechanism is a class holding a cursor, with a method to advance and one to test for the end. Python builds the protocol into the data model: any object whose `__iter__` returns an object with `__next__` works in `for`, a comprehension, `list()` and `sum()`.

A function containing `yield` returns an object that already implements the protocol, with the cursor held in the suspended frame (PEP 255). Paging a tracking history:

```python
def pages(history: TrackingHistory, size: int) -> Iterator[tuple[HandlingEvent, ...]]:
    """Yield the history in pages of at most ``size`` events, reading lazily."""
    yield from batched(history, size, strict=False)
```

The first page of three from a seven-event source pulls three events. A consumer that stops after the first page never touches the rest.

The language didn't remove the decision to expose a sequence without exposing its storage. A `TrackingHistory` that hides how events are fetched is still the right boundary; only the classes are gone.

## Structural typing

A 1994 interface is checked by name: two classes with identical methods but no shared declaration are strangers to the compiler. A `Protocol` (PEP 544) checks by shape. The booking code needs one thing from a carrier:

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

Neither gateway refers to `CarrierGateway`, so either could live in a module that never imports it, and a third-party client can satisfy it unedited.

That removes Adapter's scaffolding only where two parts already agree on shape. If a carrier's client exposed `submit_shipment(payload)` instead of `book(consignment)`, no checker bridges that. Adapter's force is a mismatch of shape, and that still needs a class that translates.

Two cautions:

- **`@runtime_checkable` checks names only.** `isinstance` confirms the methods exist and nothing about their signatures.
- **A mock is assignable to every type**, so it satisfies any protocol whether or not it matches.

Rely on `mypy --strict`, not run-time checks, for the shape.

## Modules

Singleton's force is that some things must exist once: a tariff table, a configuration, a registry. In Python a module is an object, the import system builds it on first import, and every later `import` returns the same object from `sys.modules`:

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

Importing `tariff_table` twice loads it once. `MappingProxyType` lets callers read the mapping but not reassign entries. There's no accessor and no guard, because an import is the only way to get the object. `importlib.reload` re-runs the module body and builds a second one.

When each test needs a clean instance, or you need one per tenant, pass the object in as a parameter. [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) compares the alternatives.

## Absence in the type

A caller that asks for something that may not exist shouldn't have to test for absence everywhere. Null Object, from the later pattern literature (Bobby Woolf, "Null Object", in *Pattern Languages of Program Design 3*, Addison-Wesley, 1998), returns a real object whose methods do nothing. The cost is that absence becomes invisible: a `NullGateway.book` that returns an empty string books nothing, and the caller never finds out. Python lets the type say so instead:

```python
def find_gateway(code: str) -> CarrierGateway | None:
    """Return a gateway for a carrier code, or None when the code is unknown."""
    factory = GATEWAYS.get(code)
    if factory is None:
        return None
    return factory()
```

Calling `find_gateway("FASTLINE").book(consignment)` with no guard fails the type check at that expression:

```text
<string>:7: error: Item "None" of "CarrierGateway | None" has no attribute "book"  [union-attr]
```

The guarded form (`if gateway is None: return "unknown carrier"`) passes clean. Absence is a branch the checker makes you write, not a do-nothing object or a run-time `AttributeError`.

The force remains: callers still need protecting from a missing object. Null Object made the missing case look present; the checker makes it impossible to ignore. Where a do-nothing default is the correct behaviour, such as a logger that discards output or a discount of zero, a null object is still the right design.

## Did the force move, or only the mechanism?

State the force a pattern resolves in one sentence, then ask whether a language feature resolves it without the pattern's structure.

| Pattern | Force | What goes |
| --- | --- | --- |
| Strategy | Vary the algorithm at run time | The class hierarchy |
| Iterator | Traverse without exposing storage | The cursor class |
| Singleton | One instance | The guard |

In each, the force is intact, the name stays useful, and the scaffolding becomes a function, a generator or a module.

Other patterns keep their shape because the force isn't about mechanism:

- **Composite.** One item and a group go through the same interface. A `Protocol` makes that cheaper to declare but doesn't decide the recursive structure, how a total is computed across children, or what a leaf does with `add`.
- **State.** Behaviour depends on a history of transitions that must be explicit and checkable. A dict of functions can store the table, but the table is the design.
- **Command with undo.** It needs a record of what to reverse and an order to reverse it in, and no callable holds that.

In review, "this should be a function" means the force remains and the mechanism doesn't need a class. "This needs a real object" means the force itself has state, structure or ordering a callable can't carry. [The three-way split]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts the whole catalogue this way.

## What you can do now

- State the object-model assumption: behaviour had to arrive inside an object of a declared class, and a catalogue is tied to the features its authors could rely on.
- Say which feature removes each scaffold: `PricingRule` and `functools.partial` for Strategy, a generator function for Iterator, `CarrierGateway` for Adapter, `TARIFF` through `sys.modules` for Singleton, and `find_gateway("FASTLINE").book(consignment)` with the mypy error for Null Object.
- Read the alias, the Protocol and the generator as the replacements for a strategy hierarchy, an interface and an iterator class.
- Spot the mismatch that still needs an adapter: the `submit_shipment(payload)` case.
- Apply the force-or-mechanism test, with Composite, State and Command as the survivors.

## For deeper coverage

- *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides; Addison-Wesley, 1994). The Introduction's account of what a design pattern is, and its remark that the language you assume determines which patterns you state, is the source for the argument above. Read it for the forces, not the class diagrams.
- *Fluent Python*, second edition (Luciano Ramalho; O'Reilly). The data model, first-class functions, protocols, generators and the import system.
- *Effective Python*, third edition (Brett Slatkin; Addison-Wesley). Short rules on generators, closures, `partial`, typing and module-level state; read by topic.
- PEP 544, [Protocols: Structural subtyping](https://peps.python.org/pep-0544/); PEP 255, [Simple Generators](https://peps.python.org/pep-0255/); PEP 695, [Type Parameter Syntax](https://peps.python.org/pep-0695/), which also introduces the `type` statement.
- The Python reference, [data model](https://docs.python.org/3/reference/datamodel.html), for `__iter__`, `__next__` and callables.
- Brandon Rhodes, [python-patterns.guide](https://python-patterns.guide/), for the catalogue read through Python.

The full list of books, with editions and links, is on the [bibliography]({{ '/bibliography/' | relative_url }}) page.
