---
title: "Protocol, duck typing, and structural typing with mypy"
order: 9
layout: tutorial
sectionid: docs
part: "python-substrate"
description: "An interface in Python is a shape the checker compares where a value is used, absence is a member of that shape's type so Null Object dissolves into an optional return, and Protocol and ABC are two mechanisms behind one word."
---

## Learning objectives

By the end of this chapter you can:

- Say what mypy compares when a value is passed where a Protocol is expected, and where it reports a mismatch.
- Replace a do-nothing stand-in with an optional return, narrow it four ways, and name the case where the stand-in is still right.
- Use a `sentinel` when `None` is itself a meaningful argument.
- Read an inferred-variance error on a generic Protocol, and write a callback Protocol that ignores parameter names.
- Choose between a Protocol and an ABC, and say what `runtime_checkable` does and doesn't check.

## Why this matters

Three failures come from the same place:

- A booking names a carrier that isn't in the registry. The lookup returns `None`, and the `AttributeError` surfaces three calls later, nowhere near the lookup.
- A test fixture stands in for the missing carrier with a gateway that returns an empty reference, and a lost booking looks like a success.
- A quoter written for hazmat consignments is passed to code that prices every consignment, and it fails on the first ordinary one.

Each is a question about what a caller may assume about a collaborator: whether it exists, and whether its shape and its construction are right. Python answers with three mechanisms that look alike and check at different moments, and telling them apart decides which mistakes the checker catches.

{% include excalidraw.html name="09-protocol-and-structural-typing" described="true" caption="Figure 9.1: Three checks behind one booking call. The optional return makes absence a branch to narrow, the CarrierGateway Protocol is compared where a gateway is passed, and the CarrierBase ABC is checked at construction." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-09-protocol-and-structural-typing" markdown="1">
The accent box at the top is the call, `book_with(code, consignment)`, with three checks behind it side by side. The left lane is absence: `find_gateway` returns `CarrierGateway | None`, narrowed before use. The middle lane is shape: `CarrierGateway` is compared where a gateway is passed, and `FastlineGateway` has no base class. The right lane is declaration: `CarrierBase` is checked at construction, and `AircoGateway` inherits it. Below the absence lane, connected to nothing, sits the `_NullGateway` test fixture, labelled "absence hidden: accepted, books nothing": a test assigns it directly, and no arrow stands for that.
</div>
</details>

The figure puts the three checks side by side, with the moment each one runs.

## Shape at the point of use

The comparison happens where the value is used, not where the class is written. [PEP 544](https://peps.python.org/pep-0544/), by Ivan Levkivskyi, Jukka Lehtosalo and Łukasz Langa, defines the mechanism: a class is a subtype of a Protocol when it has the members the Protocol names, with compatible types, whether or not it says so. The [typing specification's section on protocols](https://typing.python.org/en/latest/spec/protocol.html) and the [mypy documentation on protocols](https://mypy.readthedocs.io/en/stable/protocols.html) cover the rules in full.

```python
class CarrierGateway(Protocol):
    """What a caller needs: book a consignment and get a carrier reference."""

    def book(self, consignment: Consignment, /) -> str: ...


class FastlineGateway:
    """Satisfies CarrierGateway by shape alone: no base class."""

    def book(self, consignment: Consignment, /) -> str:
        return f"FASTLINE:{consignment.id}"
```

`FastlineGateway` never mentions `CarrierGateway`. A mismatch is reported on the line that passes the value. Assigning a class with only a `quote` method to a `CarrierGateway` variable gives:

```text
<string>:11: error: Incompatible types in assignment (expression has type "QuoteOnly", variable has type "CarrierGateway")  [assignment]
```

When the one required member is wholly absent, mypy 2.4.1 adds no explanatory note. When a member exists with the wrong types, it adds `Following member(s) of "WrongParameter" have conflicts` with the expected and actual signatures. For who owns a Protocol and how small to make it, see [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}).

The registry that maps carrier codes to gateway classes is a `frozendict`, new in 3.15 ([PEP 814](https://peps.python.org/pep-0814/)). It isn't a `dict`, and item assignment raises `TypeError`.

## Absence in the type: Null Object dissolves

Bobby Woolf's "Null Object", in *Pattern Languages of Program Design 3* (Addison-Wesley, 1998), names the force and the structure. The force: a caller that asks for a collaborator that may not exist must not go on as though it did. The structure: a stand-in object with the same interface that does nothing, so the caller never tests for absence.

This pattern dissolves. The collaborator's type says "or nothing", and the checker refuses the call until the caller has handled that case.

```python
def find_gateway(code: str) -> CarrierGateway | None:
    """The gateway for a carrier code, or None when the code is unknown."""
    factory = GATEWAYS.get(code)
    return None if factory is None else factory()


def book_with(code: str, consignment: Consignment) -> str:
    """Book through the named carrier. An unknown carrier is a BookingError."""
    gateway = find_gateway(code)
    if gateway is None:
        raise BookingError(f"unknown carrier {code!r}")
    return gateway.book(consignment)
```

mypy rejects the unguarded call, `find_gateway(code).book(c)`, with `[union-attr]`; see [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}). Four narrowings are clean: a walrus, a `match` with `case None`, an early return and an `assert`. The `assert` has a catch. The [reference for the `assert` statement](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) says: "The current code generator emits no code for an assert statement when optimization is requested at compile time." Under `python -O` the check disappears and the `None` reaches the attribute access. Use an explicit branch where the check must survive.

With the guard, an unknown code raises `BookingError` (`unknown carrier 'UNKNOWN'`) at the lookup, with the code in the message.

Now the stand-in, a test fixture:

```python
class _NullGateway:
    """Negative fixture: a null object that does nothing and reports success."""

    def book(self, consignment: Consignment, /) -> str:
        return ""
```

Booking through it returns `""` and raises nothing, and mypy accepts it as a `CarrierGateway` with no output. The shape is right, so the checker is satisfied, and nothing was booked. A null object turns "no carrier" into a success that carries no information.

A null object is right where doing nothing is the correct answer. `no_discount` returns `Money(Decimal("0.00"), "EUR")`, and `quote` subtracts the discount from the gross. Zero is a discount, so no caller is misled.

### When None is data

Sometimes `None` is a legitimate argument. `carriers_to_ask` takes a preferred carrier, where "not given" means the account's carrier and `None` means ask all of them. A `None` default can't tell the two apart. Python 3.15 adds a `sentinel` built-in ([PEP 661](https://peps.python.org/pep-0661/), by Tal Einat and Jelle Zijlstra) for this.

```python
ACCOUNT_DEFAULT = sentinel("ACCOUNT_DEFAULT")
```

`carriers_to_ask` takes it as the default for `preferred`:

```python
def carriers_to_ask(
    preferred: str | ACCOUNT_DEFAULT | None = ACCOUNT_DEFAULT,
    *,
    account_carrier: str = "FASTLINE",
) -> tuple[str, ...]:
    """Which carriers to quote. Not given means the account's carrier, None means all of them."""
    if preferred is ACCOUNT_DEFAULT:
        return (account_carrier,)
    if preferred is None:
        return tuple(sorted(GATEWAYS))
    if preferred in GATEWAYS:
        return (preferred,)
    raise BookingError(f"unknown carrier {preferred!r}")
```

No argument gives `("FASTLINE",)`, `None` gives `("AIRCO", "FASTLINE")`, and an unknown code raises `BookingError`. `copy.copy(ACCOUNT_DEFAULT) is ACCOUNT_DEFAULT`, and the sentinel is truthy, so `if not preferred` would treat it as given. Compare with `is`. mypy narrows on `is` too: calling `.upper()` unguarded gets `[union-attr]` for both the `sentinel` and the `None` member of the union, and returning early on `is ACCOUNT_DEFAULT or preferred is None` is clean.

## Generic protocols and inferred variance

A quoter prices consignments of one type, and the type parameter belongs in the Protocol. With the syntax from [PEP 695](https://peps.python.org/pep-0695/), nothing declares variance:

```python
class Quoter[T: Consignment](Protocol):
    """Prices consignments of type T. Variance is inferred from how T is used."""

    def quote(self, consignment: T, /) -> Money: ...
```

The PEP says type parameters "are inferred to be invariant, covariant, or contravariant depending on how they are used." Here `T` appears only as a parameter, so a quoter of the general type can stand in for a quoter of a narrower one, and the reverse can't. Passing a `HazmatQuoter` where `Quoter[Consignment]` is expected:

```text
<string>:5: error: Argument 1 to "price_all" has incompatible type "HazmatQuoter"; expected "Quoter[Consignment]"  [arg-type]
<string>:5: note: Following member(s) of "HazmatQuoter" have conflicts:
<string>:5: note:     Expected:
<string>:5: note:         def quote(self, Consignment, /) -> Money
<string>:5: note:     Got:
<string>:5: note:         def quote(self, HazmatConsignment, /) -> Money
```

A `GeneralQuoter` passed to `price_hazmat`, which wants `Quoter[HazmatConsignment]`, is clean and prices a hazmat consignment at runtime. The error exists for a reason: suppress it, and the hazmat quoter raises an `AttributeError` naming `un_number`, because a plain consignment has no such field.

## Callback protocols

A rule that prices a consignment is a callable, and a Protocol with `__call__` describes it. Parameter names are part of a callable's shape when it can be called by keyword. Marking the parameter positional-only, as in `PricingRule.__call__(self, consignment, /)`, removes them from the comparison, so `flat_rate(consignment)` and `per_kg(shipment)` both qualify. Without the `/`, `per_kg` is rejected:

```text
<string>:12: error: Incompatible types in assignment (expression has type "Callable[[Consignment], Money]", variable has type "KwRule")  [assignment]
<string>:12: note: "KwRule.__call__" has type "def __call__(self, consignment: Consignment) -> Money"
```

| Use | When |
| --- | --- |
| `Callable[[Consignment], Money]` alias | a plain positional signature; it's shorter |
| Callback Protocol | keyword parameters, overloads or attributes on the callable |

## Protocol or ABC: two mechanisms, one word

"Interface" needs disambiguating: the word covers two mechanisms, and they check at different times. A Protocol is structural and is checked where the value is passed. An ABC, from the [`abc` module](https://docs.python.org/3/library/abc.html), is nominal: a class declares that it inherits, the abstract methods must be filled in, and the check happens when an instance is built. An ABC can also carry shared code.

```python
class CarrierBase(ABC):
    """Shared code for carriers that declare themselves: references are built here."""

    code: ClassVar[str]

    def reference(self, consignment: Consignment) -> str:
        return f"{self.code}:{consignment.id}"

    @abstractmethod
    def book(self, consignment: Consignment, /) -> str: ...


class AircoGateway(CarrierBase):
    """Inherits the shared code and still satisfies CarrierGateway by shape."""

    code = "AIRCO"

    @override
    def book(self, consignment: Consignment, /) -> str:
        return self.reference(consignment)
```

An ABC refuses an incomplete subclass at construction, in both worlds: the runtime raises a `TypeError` naming the missing method, and mypy reports `Cannot instantiate abstract class "Half" with abstract attribute "book"  [abstract]` on the instantiation line.

The two don't compete. A `FastlineGateway` and an `AircoGateway` sit in one `list[CarrierGateway]` and both book. Only the second is a `CarrierBase`, and it reuses `reference()` from there. The caller sees the shape; the implementer chooses whether to inherit.

Subclassing a Protocol explicitly is a third thing. It makes the class nominal, and mypy and the runtime disagree about it. For a class that inherits `CarrierGateway` and implements nothing, mypy says `Cannot instantiate abstract class "Declared" with abstract attribute "book"  [abstract]`, yet the runtime builds it, and the inherited `...` body returns `None`. A `str` annotation over a `None` result survives review. Implement a Protocol by shape and leave it out of the bases.

`typing.override` ([PEP 698](https://peps.python.org/pep-0698/)) guards the ABC side. `AircoGateway.book` carries the `__override__` marker, and a misspelled `boook` gets `Method "boook" is marked as an override, but no base method was found with this name  [misc]`.

| | Protocol | ABC |
| --- | --- | --- |
| Typing | structural | nominal |
| Checked | where the value is passed | when an instance is built |
| Shared code | none | yes |
| Use it when | a consumer states a capability it needs | a family shares construction or a skeleton |

The shared-skeleton case is [Template Method and the function alternative]({{ '/docs/13-template-method-and-the-function-alternative/' | relative_url }}).

## What runtime_checkable checks

A Protocol marked `@runtime_checkable` can be used with `isinstance`, and the check is for names only. A class whose `book` takes no consignment and returns an `int` passes, and so does a class where `book = 3`. A data Protocol, one with a non-method member such as `code: str`, refuses `issubclass` with `TypeError` (`Protocols with non-method members don't support issubclass`), though `isinstance` on an instance works.

On 3.15 there is a deprecation. The [What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) page says: "It is deprecated to call isinstance() and issubclass() checks on protocol classes that were not explicitly decorated with runtime_checkable() but that inherit from a runtime-checkable protocol class." The page adds that the call will raise `TypeError` in 3.20. An undecorated sub-protocol emits a `DeprecationWarning` saying it isn't explicitly decorated. Put the decorator on each Protocol that is meant for `isinstance`. The Protocols here aren't runtime-checkable, because `mypy --strict` already compares them at every call.

## When not to use it

- **One implementation.** A Protocol with one implementation and no substitute is ceremony: the class is the contract.
- **No shared code.** An ABC hierarchy for classes that share no code adds a base nobody uses.
- **Absence everywhere.** A `| None` threaded through ten signatures costs ten branches where one guard at the boundary would do, as `book_with` does for the lookup.
- **A redundant sentinel.** A sentinel where `None` already means "absent" adds a name and a third branch for no distinction.

> **🤖 Explore with your agent**
>
> "Return `CarrierGateway | None` from `find_gateway` and narrow it once, at the boundary, with an explicit branch, because `assert` vanishes under `-O`. Satisfy `CarrierGateway` by shape, with no Protocol in the bases. Keep a do-nothing object only where doing nothing is correct, as `no_discount` is. Use a `sentinel` when `None` is a valid argument. Mark callback Protocol parameters positional-only with `/`. Leave signature checks to `mypy --strict`, not `@runtime_checkable`."
>
> If a stand-in returns an empty reference, ask what the caller learns when a booking is lost.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/09-protocol-and-structural-typing
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 40 cases pass, including mypy runs over snippets that pin each error quoted above, and mypy reports `Success: no issues found in 11 source files`. Two experiments, each in a scratch copy:

- **Delete the guard in `book_with`.** mypy reports `Item "None" of "CarrierGateway | None" has no attribute "book"  [union-attr]`, and one test fails with `AttributeError: 'NoneType' object has no attribute 'book'`. mypy catches it before the program runs, and pytest catches the error the guard exists to prevent.
- **Delete the `/` from `PricingRule.__call__`.** mypy reports three errors, for `no_discount`, `per_kg` and a local `ten_euro_off`, and the static check on the `PricingRule` snippet fails. Runtime behaviour is unchanged: the change is in what the checker accepts.

## What you can do now

- Say what mypy compares: the members a Protocol names, checked on the line that passes the value.
- Replace a do-nothing stand-in with `CarrierGateway | None`, narrow it with a branch that survives `-O`, and keep `no_discount` as the case where the stand-in is right.
- Use a `sentinel`, as `carriers_to_ask` does, to separate "not given" from `None`.
- Read the variance error that rejects a `HazmatQuoter` where a general quoter is wanted, and write `PricingRule.__call__` with `/` so `per_kg` qualifies.
- Choose Protocol or ABC: `CarrierBase` shares code, `CarrierGateway` compares shape, and `runtime_checkable` checks names only.

## For deeper coverage

Bobby Woolf's "Null Object", in *Pattern Languages of Program Design 3* (Addison-Wesley, 1998), is the source for the pattern, and it's on the [bibliography page]({{ '/bibliography/' | relative_url }}).

The sources for the language features are [PEP 544](https://peps.python.org/pep-0544/) for Protocols, the [typing specification](https://typing.python.org/en/latest/spec/protocol.html) and the [mypy protocols documentation](https://mypy.readthedocs.io/en/stable/protocols.html) for the rules, [PEP 695](https://peps.python.org/pep-0695/) for variance inference, [PEP 698](https://peps.python.org/pep-0698/) for `override`, [PEP 661](https://peps.python.org/pep-0661/) for `sentinel`, [PEP 814](https://peps.python.org/pep-0814/) for `frozendict`, and [What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) for the `runtime_checkable` deprecation.

Luciano Ramalho's *Fluent Python*, second edition, and Brett Slatkin's *Effective Python*, third edition, both treat typing and protocols, and both are in the bibliography.
