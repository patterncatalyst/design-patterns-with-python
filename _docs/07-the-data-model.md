---
title: "The data model: dunder methods as the substrate"
order: 7
layout: tutorial
sectionid: docs
part: "python-substrate"
description: "Operators, builtins and f-strings are calls on the type, shown on shipping values whose equality, arithmetic, ordering, containers and text each fail somewhere distant when a method is missing or wrong."
---

## Learning objectives

By the end of this chapter you can:

- Say which special method an operator, builtin or f-string calls, and why Python looks it up on the type and not on the instance.
- Keep equality and hashing consistent, and explain why defining `__eq__` alone makes a class unhashable.
- Write an operator that returns `NotImplemented` for a foreign operand, and trace how the interpreter then tries the reflected method.
- Derive the full set of comparisons from one method with `functools.total_ordering`, and decide when a type shouldn't be ordered at all.
- Make a class sized, iterable and truthy through `__len__` and `__iter__`, and give a value a `repr`, a `str` and a format spec.

## Why this matters

Three failures in a shipping system look unrelated:

- Two cartons with the same extents, one stowed on a different face, are booked twice because a set holds both.
- A report multiplies a rate by a factor and raises `TypeError` three calls away from the type that should have answered.
- A list of rate quotes won't sort, and the error names neither a field nor a rule.

Each is a missing or wrong method. Python doesn't implement `==`, `*` or `sorted` for your types: the interpreter calls a named method on the type, so the fix belongs on the type, next to the data. The Python Language Reference calls this surface the data model, and Luciano Ramalho's *Fluent Python* (2nd ed., 2022) opens on the same idea: it's the interface a type implements so the language's syntax and builtins work on it.

{% include excalidraw.html name="07-the-data-model" described="true" caption="Figure 7.1: How Python evaluates factor times price. The left operand's type asks first and returns NotImplemented for a Money, so Money's reflected method answers. For a float factor that method declines too, and the expression raises TypeError." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-07-the-data-model" markdown="1">
The figure reads top to bottom. The expression `factor * price` first goes to the left operand's type, `type(factor).__mul__(factor, price)`. For a `Decimal` or an `int` that method returns `NotImplemented` for a `Money`, so the interpreter asks `Money.__rmul__(price, factor)` with the operands swapped, and that method returns a `Money`, the result. The dashed branch on the right is the failure path for a `float` factor: `float` declines, `Money.__rmul__` accepts only a `Decimal` or an `int` and declines as well, and the expression raises `TypeError`.
</div>
</details>

The left operand's type answers first, then the right operand's reflected method, then `TypeError`.

## Syntax is a call on the type

| Syntax | Method | Fallback when absent |
| --- | --- | --- |
| `a == b` | `__eq__` | identity comparison |
| `hash(a)`, set member, dict key | `__hash__` | the identity hash, or `TypeError` once `__eq__` is defined alone |
| `a + b` | `__add__`, then `b.__radd__` | `TypeError` |
| `factor * price` | `factor.__mul__`, then `price.__rmul__` | `TypeError` |
| `a < b` | `__lt__`, then `b.__gt__` | `TypeError` |
| `len(h)` | `__len__` | `TypeError` |
| `bool(h)` | `__bool__`, then `__len__` | truthy |
| `for e in h` | `__iter__`, then `__getitem__` | `TypeError` |
| `x in h` | `__contains__`, then `__iter__` | `TypeError` |
| `repr(a)`, `str(a)`, `format(a, spec)` | `__repr__`, `__str__`, `__format__` | the default `repr`, a `str` that uses it, a `TypeError` for a non-empty spec |

The lookup is on the type. The reference's section on special method lookup: "implicit invocations of special methods are only guaranteed to work correctly if defined on an object's type, not in the object's instance dictionary." Set an attribute named `__len__` on a plain instance and you can call it directly, but `len(obj)` still raises `TypeError` with `has no len`.

## Equality and hashing: one contract

Two weights of 1.5 kilograms should be one value. The default `__eq__` compares identity, so a plain class gives two set elements for two equal weights. `Weight` is a frozen dataclass, which writes a value `__eq__` and a matching `__hash__` ([Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers what the declaration writes). Its `__post_init__` rejects a weight that isn't finite and positive, because two weights built from `nan` compare unequal, and a value that doesn't equal its own copy breaks equality.

The reference's section on basic customization sets the contract: equal values must hash alike. Python enforces part of it. A class that defines `__eq__` and not `__hash__` gets `__hash__ = None`, so its instances can't go in a set or be dict keys: building the set raises `TypeError` matching `unhashable type`.

`Dimensions` is where a hand-written pair is justified. A carton may be stowed on any face, so 120 by 80 by 100 and 80 by 120 by 100 are the same carton. The fields keep the declared orientation, which matters, so the type doesn't normalise at construction. Equality compares the sorted extents, and the hash hashes the same key:

<!-- fmt:off -->
```python
    def _extents(self) -> tuple[int, ...]:
        return tuple(sorted((self.length_cm, self.width_cm, self.height_cm)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dimensions):
            return NotImplemented
        return self._extents() == other._extents()

    def __hash__(self) -> int:
        return hash(self._extents())
```
<!-- fmt:on -->

`__eq__` takes `object` and returns `NotImplemented` for anything else, because that's the signature `object.__eq__` declares, and mypy 2.4.1 holds subclasses to it. Narrowing the parameter gives:

```text
<string>:9: error: Argument 1 of "__eq__" is incompatible with supertype "builtins.object"; supertype defines the argument type as "object"  [override]
<string>:9: note: This violates the Liskov substitution principle
```

`NotImplemented` lets the other operand's `__eq__` answer, and if neither does, `==` falls back to identity, so `Dimensions(120, 80, 100) == (120, 80, 100)` is `False`. The turned carton compares equal, hashes equal, makes a set of one, and keeps its own `repr`.

The trap is in the hash. A frozen dataclass with a hand-written `__eq__` and no `__hash__` keeps a hash generated over the fields, not the `None` a plain class gets. With the orientation-blind `__eq__` and no `__hash__`, the two orientations compare equal, hash differently, and sit in a set as two elements. `mypy --strict` passes that class with no output. A set test catches it; reading the class doesn't.

## Arithmetic and the NotImplemented handshake

`NotImplemented` isn't an exception. A binary special method returns it to say it can't handle that pair of operands, and the interpreter tries the reflected operation. `Money` adds within one currency:

```python
    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)
```

| Expression | Result |
| --- | --- |
| `price + 1` | `int.__radd__` declines too: `TypeError` naming both types |
| EUR plus USD | `ValueError`, because a result in either currency would be a guess |
| `price + 1` under `mypy --strict` | `[operator]`, because the parameter is typed `Money` |

The `isinstance` guard stays because annotations aren't checked at run time, and a caller without mypy still gets the `TypeError`. One refinement from the reference: if the right operand is an instance of a subclass that overrides the reflected method, Python asks that override first.

Multiplication by a factor adds the reflected half:

<!-- fmt:off -->
```python
    def __mul__(self, factor: Decimal | int) -> Money:
        if not isinstance(factor, Decimal | int):
            return NotImplemented
        return Money((self.amount * factor).quantize(_CENT, rounding=ROUND_HALF_UP), self.currency)

    def __rmul__(self, factor: Decimal | int) -> Money:
        return self.__mul__(factor)
```
<!-- fmt:on -->

`Decimal("2") * price` is the figure's path: `Decimal.__mul__` returns `NotImplemented`, and the interpreter calls `price.__rmul__(factor)`. `price * 1.5` gets `NotImplemented` from `Money.__mul__` and from `float.__rmul__`, and raises `TypeError: unsupported operand type(s) for *`. Products are quantised to cents, and a half cent rounds up.

`sum(prices)` starts from the integer `0`, so it evaluates `0 + price`, `int.__add__` declines, `Money` has no `__radd__`, and the call raises `TypeError`. Write `sum(prices, start=Money(Decimal("0.00"), "EUR"))`. A `__radd__` that accepted `0` would teach `Money` a special case for a number it isn't; `start=` says what the zero is, and it carries the currency.

## Ordering: one method and total_ordering

```python
    def __lt__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"cannot compare {self.currency} with {other.currency}")
        return self.amount < other.amount
```

A class with only `__lt__` is half ordered. `high > low` works, because `object.__gt__` returns `NotImplemented` and Python tries `low.__lt__(high)`, but `low <= high` raises `TypeError` with `'<=' not supported`. `functools.total_ordering` closes the gap: give it one ordering method and an `__eq__`, and it fills in the rest. On `Money` it sits above `@dataclass(frozen=True, slots=True)`, outermost, so it sees the class the dataclass returns, and `__le__` appears in `vars(Money)`.

Ordering stops where the domain stops. Two quotes can't be ranked unless the caller says by what, so `RateQuote` defines no order:

| Call | Result |
| --- | --- |
| `sorted(quotes)` | `TypeError`, `'<' not supported between instances of 'RateQuote' and 'RateQuote'`; mypy reports `[type-var]` |
| `sorted(quotes, key=lambda q: q.total)` | Cheapest total first |
| A keyed sort whose key type has no `__lt__` | mypy reports `[arg-type]` and `[return-value]` |

Across currencies, `<` and `<=` raise `ValueError`, as `+` does. Equality is different: two amounts in different currencies are unequal.

## Containers: length, iteration, membership, truth

`TrackingHistory` behaves like a sequence of handling events with two methods:

<!-- fmt:off -->
```python
    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self.events)
```
<!-- fmt:on -->

`__iter__` returns a fresh iterator each call, so `list(history) == list(history)` holds; an object that returned itself from `__iter__` would be exhausted after one pass. Lazy production and paging belong to [Iterator: generators and the iterator protocol]({{ '/docs/24-iterator-generators-and-the-iterator-protocol/' | relative_url }}).

What comes free, and what doesn't:

- **`x in history`** has no `__contains__`, so Python iterates and compares.
- **`bool(history)`** has no `__bool__`, so Python calls `__len__`, and an empty history is falsy. An iterable without `__len__` is truthy while empty: truth follows length only where length exists.
- **`history[0]`** raises `TypeError` with `'TrackingHistory' object is not subscriptable`, and mypy reports `[index]`. Adding `__getitem__` is a decision about order and slicing.

`with` is another pair of method calls, `__enter__` and `__exit__`; see [Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}).

## Text: repr, str, and format

A value has three readers:

| Reader | Call | `Money` gives |
| --- | --- | --- |
| A developer or a log | `repr` | The dataclass's `Money(amount=Decimal('12.50'), currency='EUR')` |
| A manifest line | `str` | `EUR 12.50`, written by hand |
| An f-string with a spec | `format` | The `str` form, aligned |

<!-- fmt:off -->
```python
    def __str__(self) -> str:
        return f"{self.currency} {self.amount}"

    def __format__(self, spec: str) -> str:
        return format(str(self), spec)
```
<!-- fmt:on -->

Delegating to `str` lets `f"{price:>12}"` right-align `EUR 12.50` in twelve columns. A class with `__str__` and no `__format__` prints fine, but `f"{plain:>12}"` raises `TypeError` matching `unsupported format string`.

## When a dunder costs more than it buys

- **An operator is a promise about meaning.** `Money * Money` has no unit a reader can name, and `consignment + consignment` could mean merging or pooling. A named method such as `consolidate` costs one line and removes the question.
- **`__bool__` on an amount** makes zero falsy, which surprises code that tests `if amount:` to mean "has an amount", so `Money` leaves it out.
- **Equality across types**, such as `Money == Decimal`, would need a hash that agrees across both.

> **🤖 Explore with your agent**
>
> "`__eq__` takes `object` and returns `NotImplemented` for foreign types, and `__hash__` hashes the same key equality compares. Type each operator's operand, return `NotImplemented` for anything else, and raise `ValueError` for mixed currencies. Add `__rmul__` for a scalar factor. Derive ordering from `__lt__` with `functools.total_ordering`. No `__radd__` for `0`: callers pass `start=` to `sum`. Add a test that puts two equal values in a set."
>
> If equal values can hash differently, ask for that set test.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/07-the-data-model
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 25 cases pass, and mypy reports no issues in 11 source files. The underscore-prefixed classes in `tests/` are negative fixtures, kept out of the model so each failure above is reproducible. Make each experiment in a scratch copy:

- **Delete `Dimensions.__hash__`.** One case fails: the turned carton still compares equal, but the dataclass silently supplies a field hash, so the two orientations hash differently. mypy still reports no issues.
- **Delete `Money.__rmul__`.** Two cases fail: `Decimal * Money` raises `TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'Money'`, and a mypy snippet that multiplies a `Decimal` by a `Money` now errors. mypy on the tests reports 6 errors, starting with `Unsupported operand types for * ("Decimal" and "Money")  [operator]`.

A missing hash is invisible to the checker and a missing reflected method isn't, so you need both the set test and the operand tests.

## What you can do now

- Say which special method an operator, builtin or f-string calls, and why setting one on an instance does nothing for `len`.
- Keep equality and hashing consistent: `Dimensions` hashes the key it compares, and a frozen dataclass with a custom `__eq__` keeps a field hash unless you write one.
- Return `NotImplemented` for a foreign operand from `__add__` and `Money.__mul__`, and answer the reflected case with `Money.__rmul__`.
- Derive the comparisons with `functools.total_ordering` on `Money`, and leave `RateQuote` unordered so callers sort with a key.
- Make `TrackingHistory` sized, iterable and truthy with `__len__` and `__iter__`, and serve `Money`'s three readers with `__repr__`, `__str__` and `__format__`.

## For deeper coverage

The primary source is the Python Language Reference chapter [Data model](https://docs.python.org/3/reference/datamodel.html): the section on basic customization states the rule for `__eq__` and `__hash__`, the section on emulating numeric types covers reflected operands, and the section on special method lookup covers why the type is consulted. The [`NotImplemented` constant](https://docs.python.org/3/builtins/constants.html#NotImplemented) and the [`functools.total_ordering` documentation](https://docs.python.org/3/library/functools.html#functools.total_ordering) describe the other two ideas used here. [PEP 207](https://peps.python.org/pep-0207/), by Guido van Rossum and David Ascher, introduced rich comparisons and the separate comparison methods.

Luciano Ramalho's *Fluent Python*, second edition, covers the data model, Pythonic objects and operator overloading in greater depth: equality and hashing, the reflected scalar `__rmul__`, truth through `__len__` and `__format__`. It is on the [bibliography page]({{ '/bibliography/' | relative_url }}). Brett Slatkin's *Effective Python*, third edition, is a shorter companion for the idioms on the same topics.
