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

Three failures in a shipping system look unrelated and have one cause. Two cartons with the same extents, one stowed on a different face, are booked twice because a set holds both. A report multiplies a rate by a factor and raises a `TypeError` three calls away from the type that should have answered. A list of rate quotes won't sort, and the error names neither a field nor a rule.

Each is a missing or wrong method. Python doesn't implement `==`, `*` or `sorted` for your types. The interpreter calls a named method on the type, and a type takes part in the language's own conventions by defining it. That is why the fix belongs on the type, next to the data, and not in the code that happened to trip over it. The Python Language Reference calls this surface the data model. Luciano Ramalho's *Fluent Python* (2nd ed., 2022) opens on the same idea: the data model is the interface a type implements so that the language's syntax and builtins work on it. The example for this chapter is one small model with twenty-two test functions, twenty-five cases in all, that witnesses each claim below.

{% include excalidraw.html name="07-the-data-model" caption="Figure 7.1: How Python evaluates factor times price. The interpreter asks the left operand's type first; Decimal returns NotImplemented for Money, so Money's reflected method answers, and only when both decline does the expression raise TypeError." %}

The figure reads top to bottom. The expression `factor * price` first goes to the left operand's type, `Decimal`, which declines by returning `NotImplemented`. The interpreter then asks `Money.__rmul__` with the operands swapped, and that method returns a `Money`. The dashed branch on the right is the failure path: if the reflected method declines as well, the expression raises `TypeError`.

## Syntax is a call on the type

Each operator and builtin in the table below is a spelling for a method call. The third column is what the interpreter does when the method is absent.

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

The lookup is on the type. The Python Language Reference, in the section on special method lookup, puts it directly: "implicit invocations of special methods are only guaranteed to work correctly if defined on an object's type, not in the object's instance dictionary." The test `test_special_methods_are_looked_up_on_the_type` shows the consequence. It builds a plain class instance, sets an attribute named `__len__` on that instance, and calls it directly, which works. `len(obj)` still raises `TypeError` with `has no len`, because the type defines none.

## Equality and hashing: one contract

Two weights of 1.5 kilograms should be one value. The default `__eq__` compares identity, so a plain class gives two set elements for two equal weights, and the example keeps such a class as a negative fixture, `_IdentityWeight`, to show it. The `Weight` in the model declares its fields as a frozen dataclass and gets a value `__eq__` and a matching `__hash__` from the declaration; what the declaration writes is the subject of [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}). `Weight` also rejects a weight that isn't finite and positive in `__post_init__`, which matters here for one reason: two weights built from `nan` compare unequal, and a value that fails to equal its own copy breaks the equality half of the contract.

The reference's section on basic customization sets the contract: equal values must hash alike. Python enforces part of it by default. A class that defines `__eq__` and not `__hash__` has its `__hash__` set to `None`, and an instance can't go in a set or serve as a dict key. `test_defining_eq_alone_makes_a_class_unhashable` checks that `vars(_EqOnlyWeight)["__hash__"]` is `None` and that building a set raises `TypeError` matching `unhashable type`.

`Dimensions` is the case where a hand-written pair is justified. A carton may be stowed on any face, so a 120 by 80 by 100 carton and an 80 by 120 by 100 carton are the same carton. The fields keep the declared orientation, so the type doesn't normalise at construction; that would be simpler if the orientation didn't matter, and here it does. So equality compares the sorted extents, and the hash hashes the same key:

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

`__eq__` takes `object`, not `Dimensions`, and returns `NotImplemented` for anything else. That's the signature `object.__eq__` declares, and mypy 2.4.1 holds subclasses to it. Narrowing the parameter is an `[override]` error, which the snippet in `test_mypy_rejects_an_eq_that_narrows_its_argument` produces; the first lines of the output are:

```text
<string>:9: error: Argument 1 of "__eq__" is incompatible with supertype "builtins.object"; supertype defines the argument type as "object"  [override]
<string>:9: note: This violates the Liskov substitution principle
```

Returning `NotImplemented` lets the other operand's `__eq__` answer, and if neither does, `==` falls back to identity, so `Dimensions(120, 80, 100) == (120, 80, 100)` is `False`. The test `test_a_turned_carton_is_one_set_element` checks equality, equal hashes, a set of one, and the unchanged `repr` of the turned carton.

The trap is in the hash. A frozen dataclass with a hand-written `__eq__` and no `__hash__` of its own keeps a hash generated over the fields, not the `None` the plain class gets. The fixture `_FieldHashDimensions` is `Dimensions` with the `__hash__` removed: its two orientations compare equal, hash differently, and sit in a set as two elements. mypy is silent about it. `test_mypy_cannot_see_a_broken_hash_contract` runs a snippet with the same shape through `mypy --strict` and asserts exit status 0 and empty output. A set test catches this and a reading of the class doesn't.

## Arithmetic and the NotImplemented handshake

An operator method answers for operands it understands and returns `NotImplemented` for the rest. `NotImplemented` isn't an exception. It is a value a binary special method returns to say it can't handle that pair of operands, and the interpreter then tries the reflected operation. `Money` adds within one currency:

```python
    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)
```

A foreign operand gets `NotImplemented`, which hands the decision to the other operand's type. One refinement from the reference: if the right operand is an instance of a subclass that overrides the reflected method, Python asks that override first, so a subclass can change how it combines with its base class. For `price + 1` the `int` has no say either, `int.__radd__` declines too, and the result is a `TypeError` naming both types. Two amounts in different currencies are a domain error and raise `ValueError`. That is a choice, because a result in either currency would be a guess. The parameter is typed `Money`, not `object`, so mypy rejects `price + 1` at the call site. `test_mypy_rejects_operands_the_methods_do_not_accept` runs four bad operands and asserts exactly four `[operator]` errors. The guard stays in the body because annotations aren't checked at runtime and a caller without mypy still gets the `TypeError`.

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

`price * Decimal("2")` needs only `__mul__`, and `__rmul__` delegates to it, since multiplication by a factor is the same either way round. `Decimal("2") * price` is the case in the figure: `Decimal.__mul__` returns `NotImplemented` for a `Money`, and the interpreter calls `price.__rmul__(factor)`. The float factor shows the end of the path: `price * 1.5` gets `NotImplemented` from `Money.__mul__` and from `float.__rmul__`, and the result is `TypeError: unsupported operand type(s) for *`. `test_a_factor_times_money_uses_the_reflected_method` covers a `Decimal` and an `int` on the left, both float orders and the cent quantisation; `test_money_multiplication_rounds_half_up` pins the rounding mode, so a half cent rounds up.

`sum()` runs into the same rule from another side. It starts from the integer `0`, so `sum(prices)` evaluates `0 + price`, `int.__add__` declines, `Money` has no `__radd__`, and the call raises `TypeError`. The fix is `sum(prices, start=Money(Decimal("0.00"), "EUR"))`, which the test `test_sum_needs_a_money_start` uses. A `Money.__radd__` that accepted `0` would make the bare call work by teaching `Money` a special case for a number it isn't. `start=` says what the zero is, and it carries the currency.

## Ordering: one method and total_ordering

Sorting needs `<`, and `Money` answers it in one method:

```python
    def __lt__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"cannot compare {self.currency} with {other.currency}")
        return self.amount < other.amount
```

A class with only `__lt__` is half ordered. In `test_total_ordering_derives_the_other_comparisons` the fixture `_LtOnlyMoney` shows both halves: `high > low` works, because the inherited `object.__gt__` returns `NotImplemented` and Python tries the reflection `low.__lt__(high)`, while `low <= high` raises `TypeError` with `'<=' not supported`. `functools.total_ordering` closes the gap. Its documentation asks for one ordering method on the decorated class and an `__eq__` alongside it; the decorator fills in the rest. `Money` carries `@functools.total_ordering` above `@dataclass(frozen=True, slots=True)`, outermost, so the decorator sees the class the dataclass returns, and the test asserts that `__le__` appears in `vars(Money)`.

Ordering stops where the domain stops. Two quotes can't be ranked unless the caller says by what, so `RateQuote` defines no order. `sorted(quotes)` raises `TypeError` with `'<' not supported between instances of 'RateQuote' and 'RateQuote'`, and `sorted(quotes, key=lambda q: q.total)` orders the fixture quotes by total, cheapest first. The fixture nets are chosen so net order and total order differ, which makes the test fail if `total` stops adding tax. mypy sees the same boundary. The `[type-var]` ignore on the unkeyed call in that test would turn into an `unused-ignore` error under `--strict` if mypy stopped reporting it, and the unordered-`Money` snippet in `test_mypy_accepts_the_protocols_the_types_define` shows a keyed sort failing with `[arg-type]` and `[return-value]` when the key's type has no `__lt__`.

Across currencies `Money` raises `ValueError` from `<` and `<=`, as it does from `+`. Equality is different: two amounts in different currencies are unequal.

## Containers: length, iteration, membership, truth

A shipment history is a sequence of handling events, and `TrackingHistory` defines two methods to behave like one:

<!-- fmt:off -->
```python
    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self.events)
```
<!-- fmt:on -->

`__iter__` returns a fresh iterator on each call, which is why `list(history) == list(history)` holds in `test_history_is_sized_and_reiterable`. An object that returned itself from `__iter__` would be exhausted after one pass. Producing events lazily, with paging, is the territory of [Iterator: generators and the iterator protocol]({{ '/docs/24-iterator-generators-and-the-iterator-protocol/' | relative_url }}); here the iterator is the tuple's own.

Two more operations arrive without being written. `x in history` has no `__contains__` to call, so Python iterates and compares, and the same test checks one member present and one absent. `bool(history)` has no `__bool__`, so Python calls `__len__`: an empty history is falsy. The fixture `_IterOnlyHistory` is iterable without a `__len__`, and `test_empty_history_is_falsy_through_len` shows it is truthy while empty, so truth follows length only where length exists.

Iteration doesn't give indexing. `history[0]` raises `TypeError` with `'TrackingHistory' object is not subscriptable`, and mypy reports `[index]` on the same line; adding `__getitem__` would be a decision about order and slicing. One more syntax that is a pair of method calls is `with`, which calls `__enter__` and `__exit__`; [Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) covers it.

## Text: repr, str, and format

A value has three readers. `repr` is for a developer and a log, and the dataclass supplies one: `Money(amount=Decimal('12.50'), currency='EUR')`. `str` is for a manifest line, and `Money` writes it by hand. `format` is what an f-string calls with its spec:

<!-- fmt:off -->
```python
    def __str__(self) -> str:
        return f"{self.currency} {self.amount}"

    def __format__(self, spec: str) -> str:
        return format(str(self), spec)
```
<!-- fmt:on -->

Delegating to `str` lets `f"{price:>12}"` align a `Money` like text, giving `   EUR 12.50`. Without `__format__`, a spec raises: `_StrOnlyMoney` has `__str__`, prints fine, and `f"{plain:>12}"` raises `TypeError` matching `unsupported format string`. All three forms are in `test_repr_str_and_format_serve_different_readers`, which asserts that they differ.

## When a dunder costs more than it buys

An operator is a promise about meaning. `Money * Money` has no unit a reader can name, and `consignment + consignment` could mean merging or pooling. If a reader has to look up what the operator does, a named method such as `consolidate` costs one line and removes the question. A `__bool__` on an amount makes zero falsy, which surprises code that tests `if amount:` to mean "has an amount", so `Money` leaves it out. Equality across types, say `Money == Decimal`, would need a hash that agrees across both, and the contract above is hard enough within one class.

<blockquote class="ai-sidebar" markdown="1">

**Reviewing assistant-written dunders.** An assistant may type `__eq__` with the class instead of `object`, define `__eq__` without `__hash__`, or add `__radd__` that accepts `0` to make `sum()` work. Check four things. Does `__eq__` take `object` and return `NotImplemented` for foreign types? Do equal values hash equal, shown by a set test and not by a reading? Are operands typed so mypy rejects the ones the method refuses? Is `start=` used in place of a special case in `__radd__`?

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then from the example directory:

```bash
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
collecting ... collected 25 items

tests/test_arithmetic.py::test_money_adds_within_one_currency_only PASSED [  4%]
tests/test_arithmetic.py::test_a_factor_times_money_uses_the_reflected_method PASSED [  8%]
tests/test_arithmetic.py::test_money_multiplication_rounds_half_up PASSED [ 12%]
tests/test_arithmetic.py::test_sum_needs_a_money_start PASSED            [ 16%]
tests/test_containers.py::test_history_is_sized_and_reiterable PASSED    [ 20%]
tests/test_containers.py::test_empty_history_is_falsy_through_len PASSED [ 24%]
tests/test_containers.py::test_history_is_not_subscriptable PASSED       [ 28%]
tests/test_equality.py::test_special_methods_are_looked_up_on_the_type PASSED [ 32%]
tests/test_equality.py::test_equal_weights_are_one_set_element PASSED    [ 36%]
tests/test_equality.py::test_defining_eq_alone_makes_a_class_unhashable PASSED [ 40%]
tests/test_equality.py::test_a_turned_carton_is_one_set_element PASSED   [ 44%]
tests/test_equality.py::test_custom_eq_in_a_frozen_dataclass_keeps_a_field_hash PASSED [ 48%]
tests/test_equality.py::test_dimensions_reject_a_non_positive_extent PASSED [ 52%]
tests/test_equality.py::test_weight_rejects_a_value_that_is_not_finite_and_positive[0.0] PASSED [ 56%]
tests/test_equality.py::test_weight_rejects_a_value_that_is_not_finite_and_positive[-1.0] PASSED [ 60%]
tests/test_equality.py::test_weight_rejects_a_value_that_is_not_finite_and_positive[inf] PASSED [ 64%]
tests/test_equality.py::test_weight_rejects_a_value_that_is_not_finite_and_positive[nan] PASSED [ 68%]
tests/test_ordering.py::test_total_ordering_derives_the_other_comparisons PASSED [ 72%]
tests/test_ordering.py::test_money_refuses_to_order_across_currencies PASSED [ 76%]
tests/test_ordering.py::test_quotes_sort_by_total_but_not_by_themselves PASSED [ 80%]
tests/test_static.py::test_mypy_rejects_an_eq_that_narrows_its_argument PASSED [ 84%]
tests/test_static.py::test_mypy_rejects_operands_the_methods_do_not_accept PASSED [ 88%]
tests/test_static.py::test_mypy_accepts_the_protocols_the_types_define PASSED [ 92%]
tests/test_static.py::test_mypy_cannot_see_a_broken_hash_contract PASSED [ 96%]
tests/test_text.py::test_repr_str_and_format_serve_different_readers PASSED [100%]

============================== 25 passed in 2.31s ==============================
```

```text
Success: no issues found in 11 source files
```

The classes prefixed with an underscore in the test modules are negative fixtures, kept out of the model so that each failure the chapter describes is reproducible. Two edits in a scratch copy show the tests reacting.

**Experiment one: delete `Dimensions.__hash__`.** Remove the `__hash__` method and run `uv run pytest -q`. One test fails and twenty-four pass. The dataclass supplies a field hash without any signal, so the turned carton still compares equal and the failure is the hash assertion (the `E` and summary lines):

```text
E       assert 1560272766170198271 == 805556732051977890
E        +  where 1560272766170198271 = hash(Dimensions(length_cm=120, width_cm=80, height_cm=100))
E        +  and   805556732051977890 = hash(Dimensions(length_cm=80, width_cm=120, height_cm=100))
FAILED tests/test_equality.py::test_a_turned_carton_is_one_set_element - asse...
```

`uv run mypy --strict src tests` still prints `Success: no issues found in 11 source files`. The checker sees nothing wrong with the class. Restore the method.

**Experiment two: delete `Money.__rmul__`.** Run both commands. pytest reports two failures and twenty-three passes. The first is the reflected case, and the second is the mypy test; pytest prints each `E` line under its failing test, and the summary names both (the `E` and summary lines):

```text
E       TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'Money'
E       assert 1 == 0
FAILED tests/test_arithmetic.py::test_a_factor_times_money_uses_the_reflected_method
FAILED tests/test_static.py::test_mypy_accepts_the_protocols_the_types_define
```

The mypy test fails because its snippet multiplies a `Decimal` by a `Money`. This time mypy objects as well:

```text
tests/test_arithmetic.py:18: error: Unsupported operand types for * ("Decimal" and "Money")  [operator]
tests/test_arithmetic.py:19: error: Non-overlapping equality check (left operand type: "int", right operand type: "Money")  [comparison-overlap]
tests/test_arithmetic.py:19: error: Unsupported operand types for * ("int" and "Money")  [operator]
tests/test_arithmetic.py:20: error: Statement is unreachable  [unreachable]
tests/test_arithmetic.py:22: error: Unused "type: ignore" comment  [unused-ignore]
tests/test_arithmetic.py:24: error: Unused "type: ignore" comment  [unused-ignore]
Found 6 errors in 1 file (checked 11 source files)
```

A missing hash is invisible to the checker and a missing reflected method isn't, which is why the set test and the operand tests are both in the suite. Restore the method.

## For deeper coverage

The primary source is the Python Language Reference chapter [Data model](https://docs.python.org/3/reference/datamodel.html): the section on basic customization states the rule for `__eq__` and `__hash__`, the section on emulating numeric types covers reflected operands, and the section on special method lookup covers why the type is consulted. The [`NotImplemented` constant](https://docs.python.org/3/library/constants.html#NotImplemented) and the [`functools.total_ordering` documentation](https://docs.python.org/3/library/functools.html#functools.total_ordering) describe the other two ideas used here. [PEP 207](https://peps.python.org/pep-0207/), by Guido van Rossum and David Ascher, introduced rich comparisons and the separate comparison methods.

Luciano Ramalho's *Fluent Python*, second edition, is the book this chapter leans on most. Its treatment of the data model, Pythonic objects and operator overloading covers the topics here, equality and hashing, the reflected scalar `__rmul__`, truth through `__len__` and `__format__`, in greater depth. It is in the hub's list and on the [bibliography page]({{ '/bibliography/' | relative_url }}). Brett Slatkin's *Effective Python*, third edition, is a shorter companion for the idioms on the same topics.
