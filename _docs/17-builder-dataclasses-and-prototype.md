---
title: "Builder, dataclasses, and Prototype"
order: 17
layout: tutorial
sectionid: docs
part: "creating-objects-under-control"
description: "Builder and Prototype dissolve into a frozen keyword-only dataclass that validates once and replace for copies, with the field types deciding what a shallow copy shares."
---

## Learning objectives

By the end of this chapter you can:

- Say why Builder and Prototype dissolve in Python, and what each one leaves behind.
- Write a booking as a frozen keyword-only dataclass whose cross-field rules run once, in `__post_init__`.
- Say what mypy checks on that call (a `Literal` value, a missing field, a misspelt keyword) and what it can't (two `str` arguments swapped).
- Keep Prototype as a read-only table of template values copied with `replace` or `copy.replace`.
- Choose a field type so that a shallow copy can't share state, and know what `copy.deepcopy` costs instead.

## Why this matters

A booking request has twelve fields. Four are required and eight have a sensible default. Three rules tie fields together: an insured booking needs a declared value, dangerous goods need a dangerous goods note among the documents, and the origin can't equal the destination. The obvious versions fail three ways:

- A twelve-argument positional constructor gets origin and destination swapped. The booking runs from Singapore to Rotterdam, mypy accepts the call because both are strings, and the rules pass because the ports still differ.
- A fluent builder leaves out `.destination(...)`. The chain still type-checks, and the mistake appears when `build()` runs.
- A template booking is copied for each new consignment. The copy shares the template's list of documents, so adding the dangerous goods note to one customer's copy adds it to the template.

{% include excalidraw.html name="17-builder-dataclasses-and-prototype" described="true" caption="Figure 17.1: Building and copying a booking request. A template is copied into a frozen keyword-only request whose checks rerun on every replace, and only an immutable field type keeps two copies from sharing one list." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-17-builder-dataclasses-and-prototype" markdown="1">
From the top: `TEMPLATES`, "read-only: name to template request", feeds `from_template`, "replace(template, ...)", which feeds `BookingRequest(...)`, "keyword-only, frozen". An arrow runs on to `__post_init__`, "cross-field checks: insured, dangerous goods, ports". Two dashed arrows leave that box. One runs right to a dashed box, "both replace functions rerun it: replace, copy.replace". The other runs down to the accent box at the bottom, "a list field is shared by copy and replace; a tuple field cannot be".
</div>
</details>

The figure follows a template through `replace` into a validated request, and marks where a list field would be shared.

## Pattern: Builder

### The problem

A long positional signature is the shape that signals the problem. This comparison fixture stands for a constructor a team inherits, with the same three checks in its body as the dataclass below:

<!-- fmt:off -->
```python
class _LegacyBookingRequest:
    """A twelve-argument positional constructor with the same checks as the dataclass."""

    def __init__(
        self,
        consignment_id: ConsignmentId,
        origin: str,
        destination: str,
        weight: Weight,
        carrier: str,
        service: str,
        insured: bool,
        declared_value: Money | None,
        dangerous_goods: bool,
        reference: str | None,
        notify_party: str | None,
        documents: tuple[str, ...],
    ) -> None:
```
<!-- fmt:on -->

Swapped ports give a booking from `SGSIN` to `NLRTM`, and nothing raises. mypy accepts a swap of the ports, the carrier and service, or the two flags, and catches a swap of the weight and the declared value:

```text
<string>:37: error: Argument 4 to "LegacyBookingRequest" has incompatible type "Money"; expected "Weight"  [arg-type]
<string>:37: error: Argument 8 to "LegacyBookingRequest" has incompatible type "Weight"; expected "Money | None"  [arg-type]
```

A type system finds the swaps that cross types, and two arguments of one type pass whatever their order.

### The solution

A **Builder** assembles a product with many parts step by step, so that one construction process can produce different representations.

**Bucket: dissolves.** The force that remains is an object with many parts, several of them optional, that has to be complete and valid before anyone uses it. Python resolves that force with a class declaration.

Gamma, Helm, Johnson and Vlissides, in *Design Patterns* (1994), have a director walk through the steps while interchangeable builders decide the product. Brandon Rhodes, in [The Builder Pattern](https://python-patterns.guide/gang-of-four/builder/), observes that Python programs reach for builders for convenience, a short series of calls that hides a tangle of construction, and rarely for several representations.

### How Python models it

A keyword-only dataclass is the builder:

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    """Every argument is named, and the rules run once, in `__post_init__`."""

    consignment_id: ConsignmentId
    origin: str
    destination: str
    weight: Weight
    carrier: CarrierCode = "FASTLINE"
    service: ServiceLevel = "standard"
    insured: bool = False
    declared_value: Money | None = None
    dangerous_goods: bool = False
    reference: str | None = None
    notify_party: str | None = None
    documents: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.origin == self.destination:
            raise BookingError("origin and destination must differ")
        if self.insured and self.declared_value is None:
            raise BookingError("an insured booking needs a declared value")
        if self.dangerous_goods and DANGEROUS_GOODS_NOTE not in self.documents:
            raise BookingError(f"dangerous goods need a {DANGEROUS_GOODS_NOTE}")
```
<!-- fmt:on -->

The class is frozen and slotted, so assignment raises `FrozenInstanceError` and there's no `__dict__`. `__post_init__` runs at construction, so a request that exists passed the rules. `Weight` has its own rule, rejecting zero, a negative and NaN.

[Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) shows how `kw_only` makes a positional call a `TypeError`.

### What mypy checks on the call

The carrier and the service level are `Literal` types, `CarrierCode` and `ServiceLevel`.

| Mistake on a keyword call | mypy 2.4.1 |
| --- | --- |
| `Literal` values swapped | `[arg-type]` on both |
| `destination` left out | `Missing named argument "destination" for "BookingRequest"  [call-arg]` |
| `servce=` misspelt | `Unexpected keyword argument "servce" for "BookingRequest"; did you mean "service"?  [call-arg]` |
| `origin` and `destination` swapped | accepted: both are `str` |

The keyword swap still type-checks, but the call site now says which is which, so a reviewer can read it. The check stays a human one.

### What a builder costs

A four-case booking table (a minimal request, an insured one without a declared value, dangerous goods without the note, and equal ports) gives the same fields or the same `BookingError` message through the dataclass, the positional constructor and a fluent builder. The checks are the same in all three, so the difference is where the mistakes show up.

The fluent fixture has one method per field, each returning `self`, and a `build()` that checks the required parts. Leaving out the destination gives a plain `ValueError`, "builder is missing: destination", from `build()`, and mypy exits 0 on the same code. The builder moved the required-field check from the type checker to run time.

A dataclass call already gives defaults for optional values and a product complete the moment it exists. A builder adds an incomplete, mutable intermediate object. It keeps a job where the value is assembled in stages from parts that arrive over time, and the incomplete state is the point. Luciano Ramalho's *Fluent Python* covers dataclasses, and Brett Slatkin's *Effective Python* covers keyword-only arguments.

## Pattern: Prototype

### The problem

New bookings start from a configured one: a Rotterdam to Singapore express booking with a notify party and a commercial invoice, or a dangerous goods booking with its note. Each new consignment changes the id and the weight, and the template must not change.

### The solution

A **Prototype** creates an object by asking an existing, configured object to produce another like it, without naming its class.

**Bucket: dissolves.** The force that remains is a new object that starts as a copy of a configured one, and `replace` makes that copy with a few fields changed, with no `clone` method on every product.

Rhodes's [The Prototype Pattern](https://python-patterns.guide/gang-of-four/prototype/) makes the Python case: classes and functions are ordinary values, so a table of them and their arguments does the work.

### How Python models it

The templates are a read-only table of finished requests, and `from_template` copies one:

<!-- fmt:off -->
```python
TEMPLATES: Mapping[str, BookingRequest] = frozendict(
    {
        "rotterdam-singapore": BookingRequest(
            consignment_id=_PLACEHOLDER,
            origin="NLRTM",
            destination="SGSIN",
            weight=Weight(Decimal("1")),
            carrier="AIRCO",
            service="express",
            notify_party="Harbour Agency",
            documents=("commercial invoice",),
        ),
        "dangerous-goods": BookingRequest(
            consignment_id=_PLACEHOLDER,
            origin="NLRTM",
            destination="DEHAM",
            weight=Weight(Decimal("1")),
            dangerous_goods=True,
            documents=("commercial invoice", DANGEROUS_GOODS_NOTE),
        ),
    }
)


def from_template(name: str, *, consignment_id: ConsignmentId, weight: Weight) -> BookingRequest:
    """A new request from a named template; an unknown name is a `BookingError`."""
    try:
        template = TEMPLATES[name]
    except KeyError:
        raise BookingError(f"no template {name!r}") from None
    return replace(template, consignment_id=consignment_id, weight=weight)
```
<!-- fmt:on -->

The copy is a new object with the new id and weight, and the template keeps its placeholder id. An unknown name such as `'air-freight'` raises `BookingError`, with the `KeyError` suppressed. Assigning into `TEMPLATES` raises `TypeError`.

A read-only module-level table is a small case of the shared state that [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) takes up. Choosing which class to construct by name is [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}); here every template is the same class.

### replace reruns the checks

`replace` is Prototype's `clone`, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) notes. `dataclasses.replace` builds the copy by calling `__init__`, and the [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) says this "ensures that `__post_init__()`, if present, is also called." The [copy documentation](https://docs.python.org/3/library/copy.html) adds a generic `copy.replace(obj, /, **changes)`, "Added in version 3.13", which a class supports through `__replace__`. Dataclasses support it.

| Call | Result |
| --- | --- |
| either replace with `insured=True` and no value | `BookingError` matching "declared value"; template unchanged |
| `copy.replace(template, service="standard")` | a standard request; template unchanged |
| `copy.replace` on a plain class | `TypeError: replace() does not support Plain objects` |

A replace can't build an invalid request. mypy checks `copy.replace` the way it checks `dataclasses.replace`. A misspelt keyword prints:

```text
<string>:14: error: Unexpected keyword argument "wieght" for "replace"; did you mean "weight"?  [call-arg]
<string>:14: note: "replace" defined in "copy"
```

A wrong type, `origin=1`, gives `[arg-type]`, and a plain class is refused with `expected "_SupportsReplace[[str], Never]"`. [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) uses `replace` to build each amended request.

### Shallow copies share

`replace` and `copy.copy` are shallow. The copy documentation: "A shallow copy constructs a new compound object and then (to the extent possible) inserts references into it to the objects found in the original."

The comparison fixture `_LooseRequest` is a mutable slotted dataclass with `documents: list[str] = field(default_factory=list)`. Copy a one-document template with `copy.copy` or `replace` and append a dangerous goods note through the copy, and the template reads `["commercial invoice", "dangerous goods note"]`: both hold the same list. `default_factory` runs only "when a default value is needed for this field", and a copy takes whatever list the original holds. mypy exits 0 on the same code.

| Remedy | Effect | Cost |
| --- | --- | --- |
| `copy.deepcopy` | the lists are separate | copies everything; on Python 3.15.2, `copy.deepcopy(threading.Lock())` raises `TypeError: cannot pickle '_thread.lock' object` |
| `documents: tuple[str, ...]` | nothing to share that can change | a longer list is a new tuple |

The field type is the better answer. A tuple has no `append`, so `replace(clone, documents=(*clone.documents, "packing list"))` builds a new tuple and the template still holds `("commercial invoice",)`. Frozen is shallow, as [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) covers, and an immutable field type is the remedy there too.

## When not to use it

- **Builder.** A value with three fields needs a plain frozen dataclass or an ordinary constructor. An object whose construction is a process, such as opening a connection or calling a service, is a function. A builder kept only for a fluent style gives up the type checker's missing-argument report in exchange for a chain of method calls.
- **Prototype.** `replace` and the copy functions fit a request that holds no resources. Don't deep-copy a lock; build another.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a builder.** "A builder" leaves open where the cross-field rules run, how a template is copied and whether a class is needed at all. Paste a prompt that states the form:

> Write `BookingRequest` as `@dataclass(frozen=True, slots=True, kw_only=True)` with the cross-field rules in `__post_init__`, closed choices as `Literal` types and `documents` as a `tuple`. Keep templates in a read-only `frozendict` and copy them with `dataclasses.replace` or `copy.replace`, which rerun `__post_init__`. No builder class and no `clone` method.

If a template field is a `list`, ask for a check that appends through a copy.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/17-builder-dataclasses-and-prototype
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 42 cases pass and mypy is clean. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) covers how the mypy checks are built. Two experiments, each in a fresh scratch copy:

- **Delete a rule.** Remove the two lines in `BookingRequest.__post_init__` that raise for an insured booking without a declared value. Three cases fail with `DID NOT RAISE BookingError`: the keyword booking and both replace functions. The positional and builder cases pass, because the positional fixture holds its own copy of the check. mypy is clean: a missing rule is valid code.
- **Make the field a list.** Change `documents` to `list[str] = field(default_factory=list)`. Only the field-table check fails, because the templates still hand over tuples at run time. mypy reports six errors, including the two template literals in `templates.py` that pass tuples where a list is declared.

## What you can do now

- Replace a twelve-argument positional constructor with a frozen keyword-only dataclass.
- Put cross-field rules in `__post_init__` so they run once, and again on every `replace`.
- Rely on mypy for a swapped `Literal`, a missing field and a misspelt keyword, and on review for two swapped `str` fields.
- Keep templates in a read-only `TEMPLATES` table and copy them with `replace` or `copy.replace`.
- Use a tuple field so a shallow copy can't share state, instead of `copy.deepcopy`.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Builder and Prototype. Brandon Rhodes's [The Builder Pattern](https://python-patterns.guide/gang-of-four/builder/) and [The Prototype Pattern](https://python-patterns.guide/gang-of-four/prototype/) give the Python view. The [`dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html) covers `kw_only`, `replace` and `__post_init__`, and the [`copy` documentation](https://docs.python.org/3/library/copy.html) covers `copy.replace`, `__replace__` and deep copies. [PEP 557](https://peps.python.org/pep-0557/) specifies dataclasses. Luciano Ramalho's *Fluent Python* and Brett Slatkin's *Effective Python* are in the [bibliography page]({{ '/bibliography/' | relative_url }}).
