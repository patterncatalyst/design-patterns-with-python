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

Three failures come from the same place. A booking names a carrier that isn't in the registry, the lookup returns `None`, and the `AttributeError` surfaces three calls later, nowhere near the lookup. A test fixture stands in for the missing carrier with a gateway that returns an empty reference, and a lost booking looks like a success. A quoter written for hazmat consignments is passed to code that prices every consignment, and it fails on the first ordinary one.

Each is a question about what a caller may assume about a collaborator: whether it exists, and whether its shape and its construction are right. Python's answer is spread over three mechanisms that look alike and check at different moments. Telling them apart decides which mistakes the checker catches.

{% include excalidraw.html name="09-protocol-and-structural-typing" caption="Figure 9.1: Three checks behind one booking call. The optional return makes absence a branch to narrow, the CarrierGateway Protocol is compared where a gateway is passed, and the CarrierBase ABC is checked at construction." %}

Read the figure from the top. The accent box is the call, `book_with(code, consignment)`, with three checks behind it side by side. The left lane is absence: `find_gateway` returns `CarrierGateway | None`, narrowed before use. The middle lane is shape: `CarrierGateway` is compared where a gateway is passed, and `FastlineGateway` has no base class. The right lane is declaration: `CarrierBase` is checked at construction, and `AircoGateway` inherits it. Below the absence lane, connected to nothing, sits the `_NullGateway` test fixture, labelled "absence hidden: accepted, books nothing": a test assigns it directly, and no arrow stands for that.

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

`FastlineGateway` never mentions `CarrierGateway`. A mismatch is reported on the line that passes it. `test_mypy_checks_protocols_at_use_and_abcs_at_construction[protocol-use]` assigns a class with only a `quote` method to a `CarrierGateway` variable, and mypy reports:

```text
<string>:11: error: Incompatible types in assignment (expression has type "QuoteOnly", variable has type "CarrierGateway")  [assignment]
```

When the one required member is wholly absent, mypy 2.4.1 adds no explanatory note. When a member exists with the wrong types it does: `test_mypy_explains_a_conflicting_member_but_not_a_wholly_absent_one` shows `Following member(s) of "WrongParameter" have conflicts` with the expected and actual signatures. For who owns a Protocol and how small to make it, see the chapter titled [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}).

The registry that maps carrier codes to gateway classes is a `frozendict`, new in 3.15 ([PEP 814](https://peps.python.org/pep-0814/)). `test_the_registry_is_a_frozendict` shows that item assignment raises `TypeError` and that the registry isn't a `dict`.

## Absence in the type: Null Object dissolves

Bobby Woolf's "Null Object", in *Pattern Languages of Program Design 3* (Addison-Wesley, 1998), names the force and the structure. The force: a caller that asks for a collaborator that may not exist must not go on as though it did. The structure: a stand-in object with the same interface that does nothing, so the caller never tests for absence.

This pattern dissolves. A feature resolves the force without the pattern's structure. In Python the collaborator's type says "or nothing", and the checker refuses the call until the caller has handled that case.

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

The unguarded call, `find_gateway(code).book(c)`, is rejected, as the chapter titled [What 1994 assumed, and what Python dissolves]({{ '/docs/02-what-1994-assumed-and-python-dissolves/' | relative_url }}) shows. `test_mypy_requires_a_branch_for_absence` runs five snippets through `mypy --strict`: the unguarded one gets `[union-attr]`, and a walrus, a `match` with `case None`, an early return and an `assert` are all clean. The `assert` has a catch the others don't. The [reference for the `assert` statement](https://docs.python.org/3.15/reference/simple_stmts.html#the-assert-statement) says: "The current code generator emits no code for an assert statement when optimization is requested at compile time." Under `python -O` the check disappears and the `None` reaches the attribute access. Use an explicit branch where the check must survive.

`test_book_with_turns_absence_into_a_booking_error` shows the guard doing its job: an unknown code raises `BookingError` with `unknown carrier 'UNKNOWN'`, at the lookup, with the code in the message.

Now the stand-in. This is the fixture from `tests/test_absence.py`:

```python
class _NullGateway:
    """Negative fixture: a null object that does nothing and reports success."""

    def book(self, consignment: Consignment, /) -> str:
        return ""
```

`test_a_null_gateway_hides_a_lost_booking` books through it and gets `""` back with nothing raised. `test_mypy_accepts_a_null_gateway` assigns a class of the same shape to a `CarrierGateway` variable and mypy exits 0 with no output. The shape is right, so the checker is satisfied, and nothing was booked. A null object turns "no carrier" into a success that carries no information.

A null object is right where doing nothing is the correct answer. `no_discount` returns `Money(Decimal("0.00"), "EUR")`, and `quote` subtracts the discount from the gross. `test_no_discount_is_a_null_object_that_loses_nothing` shows that the default changes nothing and that a real discount subtracts. Zero is a discount, so no caller is misled.

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

`test_a_sentinel_separates_not_given_from_none` checks the branches: no argument gives `("FASTLINE",)`, `None` gives `("AIRCO", "FASTLINE")`, an unknown code raises `BookingError`, `copy.copy(ACCOUNT_DEFAULT) is ACCOUNT_DEFAULT`, and `bool(ACCOUNT_DEFAULT)` is `True`. A sentinel is truthy, so `if not preferred` would treat it as given. Compare with `is`. mypy narrows on `is` too: `test_mypy_requires_a_branch_for_the_sentinel` gets `[union-attr]` for both the `sentinel` and the `None` member of the union when `.upper()` is called unguarded, and a clean run once `is ACCOUNT_DEFAULT or preferred is None` returns early.

## Generic protocols and inferred variance

A quoter prices consignments of one type, and the type parameter belongs in the Protocol. With the syntax from [PEP 695](https://peps.python.org/pep-0695/), nothing declares variance:

```python
class Quoter[T: Consignment](Protocol):
    """Prices consignments of type T. Variance is inferred from how T is used."""

    def quote(self, consignment: T, /) -> Money: ...
```

The PEP says type parameters "are inferred to be invariant, covariant, or contravariant depending on how they are used." Here `T` appears only as a parameter, so a quoter of the general type can stand in for a quoter of a narrower one, and the reverse can't. `test_mypy_infers_quoter_variance` passes a `HazmatQuoter` where `Quoter[Consignment]` is expected:

```text
<string>:5: error: Argument 1 to "price_all" has incompatible type "HazmatQuoter"; expected "Quoter[Consignment]"  [arg-type]
<string>:5: note: Following member(s) of "HazmatQuoter" have conflicts:
<string>:5: note:     Expected:
<string>:5: note:         def quote(self, Consignment, /) -> Money
<string>:5: note:     Got:
<string>:5: note:         def quote(self, HazmatConsignment, /) -> Money
```

Passing a `GeneralQuoter` to `price_hazmat`, which wants `Quoter[HazmatConsignment]`, is clean. `test_a_general_quoter_serves_hazmat_consignments` prices a hazmat consignment through it at runtime. The error exists for a reason: `test_a_hazmat_quoter_fails_on_a_general_consignment_at_runtime` suppresses it and gets an `AttributeError` naming `un_number`, because a plain consignment has no such field.

## Callback protocols

A rule that prices a consignment is a callable, and a Protocol with `__call__` describes it. Parameter names are part of a callable's shape when it can be called by keyword. Marking the parameter positional-only, as in `PricingRule.__call__(self, consignment, /)`, removes them from the comparison. With the `/`, `flat_rate(consignment)` and `per_kg(shipment)` both qualify, and `test_callback_protocol_accepts_any_parameter_name` prices through both held as `PricingRule`. Without it, `per_kg` is rejected. `test_mypy_matches_callback_parameter_names_without_slash` declares the Protocol without the `/` and assigns `per_kg` to it:

```text
<string>:12: error: Incompatible types in assignment (expression has type "Callable[[Consignment], Money]", variable has type "KwRule")  [assignment]
<string>:12: note: "KwRule.__call__" has type "def __call__(self, consignment: Consignment) -> Money"
```

Choose a callback Protocol over a `Callable[[Consignment], Money]` alias when the signature needs keyword parameters, overloads or attributes on the callable. For a plain positional signature the alias is shorter.

## Protocol or ABC: two mechanisms, one word

"Interface" needs disambiguating: the word covers two mechanisms, and they check at different times. A Protocol is structural and is checked where the value is passed. An ABC, from the [`abc` module](https://docs.python.org/3.15/library/abc.html), is nominal: a class declares that it inherits, the abstract methods must be filled in, and the check happens when an instance is built. An ABC can also carry shared code.

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

The ABC refuses an incomplete subclass at construction, in both worlds. `test_abc_refuses_an_incomplete_subclass_at_construction` builds a subclass without `book` and gets a `TypeError` naming the missing method; mypy reports `Cannot instantiate abstract class "Half" with abstract attribute "book"  [abstract]` on the instantiation line. The Protocol check is the assignment error shown earlier.

The two don't compete. `test_both_carriers_satisfy_the_protocol_one_by_inheritance` puts a `FastlineGateway` and an `AircoGateway` in one `list[CarrierGateway]` and books through both. Only the second is a `CarrierBase`, and it reuses `reference()` from there. The caller sees the shape; the implementer chooses whether to inherit.

Subclassing a Protocol explicitly is a third thing. It makes the class nominal, and mypy and the runtime disagree about it. `test_explicit_protocol_subclass_is_nominal_and_still_instantiable` builds a class that inherits `CarrierGateway` and implements nothing. mypy says `Cannot instantiate abstract class "Declared" with abstract attribute "book"  [abstract]` (`[declared-protocol]` case of the static test), yet the runtime builds it, and the inherited `...` body returns `None`. A `str` annotation over a `None` result is the kind of lie that survives review. Implement a Protocol by shape and leave it out of the bases.

`typing.override` ([PEP 698](https://peps.python.org/pep-0698/)) guards the ABC side. `AircoGateway.book` is marked, and `test_airco_marks_its_book_as_an_override` checks the `__override__` marker is set. A misspelled name is reported: in the `[override-typo]` case, `boook` gets `Method "boook" is marked as an override, but no base method was found with this name  [misc]`.

Choose by who owns the need and whether code is shared. A consumer that needs a capability states a Protocol, and any class with the shape qualifies. A family that shares construction or a skeleton uses an ABC. The chapter titled [Template Method and the function alternative]({{ '/docs/13-template-method-and-the-function-alternative/' | relative_url }}) takes up the shared-skeleton case.

## What runtime_checkable checks

A Protocol marked `@runtime_checkable` can be used with `isinstance`. The check is for names. `test_runtime_checkable_checks_names_only` passes a class whose `book` takes no consignment and returns an `int`, and a class where `book = 3`, and both satisfy `isinstance`. A data Protocol, one with a non-method member such as `code: str`, refuses `issubclass`: `test_a_data_protocol_refuses_issubclass` gets `TypeError` with `Protocols with non-method members don't support issubclass`, though `isinstance` on an instance works.

On 3.15 there is a deprecation. The [What's New in Python 3.15](https://docs.python.org/3.15/whatsnew/3.15.html) page says: "It is deprecated to call isinstance() and issubclass() checks on protocol classes that were not explicitly decorated with runtime_checkable() but that inherit from a runtime-checkable protocol class." The page adds that the call will raise `TypeError` in 3.20. `test_an_undecorated_subprotocol_warns_on_isinstance` defines a sub-protocol without the decorator and catches a `DeprecationWarning` whose message says it isn't explicitly decorated. Put the decorator on each Protocol that is meant for `isinstance`. The example's own Protocols aren't runtime-checkable, because `mypy --strict` already compares them at every call.

## When not to use it

A Protocol with one implementation and no substitute is ceremony: the class is the contract. An ABC hierarchy for classes that share no code adds a base nobody uses. A `| None` threaded through ten signatures costs ten branches where one guard at the boundary would do, as `book_with` does for the lookup. A sentinel where `None` already means "absent" adds a name and a third branch for no distinction.

<blockquote class="ai-sidebar" markdown="1">
**Specifying an interface.** "Write the carrier interface" leaves open what a missing gateway returns, how a class satisfies the Protocol and what an `isinstance` check can tell. Paste a prompt that states the form:

> Return `CarrierGateway | None` from `find_gateway` and narrow it once, at the boundary, with an explicit branch, because `assert` vanishes under `-O`. Satisfy `CarrierGateway` by shape, with no Protocol in the bases. Keep a do-nothing object only where doing nothing is correct, as `no_discount` is. Use a `sentinel` when `None` is a valid argument. Mark callback Protocol parameters positional-only with `/`. Leave signature checks to `mypy --strict`, not `@runtime_checkable`.

If a stand-in returns an empty reference, ask what the caller learns when a booking is lost.
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
collecting ... collected 40 items

tests/test_absence.py::test_find_gateway_returns_none_for_an_unknown_code PASSED [  2%]
tests/test_absence.py::test_book_with_turns_absence_into_a_booking_error PASSED [  5%]
tests/test_absence.py::test_a_null_gateway_hides_a_lost_booking PASSED   [  7%]
tests/test_absence.py::test_no_discount_is_a_null_object_that_loses_nothing PASSED [ 10%]
tests/test_absence.py::test_a_sentinel_separates_not_given_from_none PASSED [ 12%]
tests/test_absence.py::test_the_registry_is_a_frozendict PASSED          [ 15%]
tests/test_disambiguate.py::test_abc_refuses_an_incomplete_subclass_at_construction PASSED [ 17%]
tests/test_disambiguate.py::test_both_carriers_satisfy_the_protocol_one_by_inheritance PASSED [ 20%]
tests/test_disambiguate.py::test_airco_marks_its_book_as_an_override PASSED [ 22%]
tests/test_disambiguate.py::test_explicit_protocol_subclass_is_nominal_and_still_instantiable PASSED [ 25%]
tests/test_domain.py::test_weight_must_be_positive_and_finite[0.0] PASSED [ 27%]
tests/test_domain.py::test_weight_must_be_positive_and_finite[-1.0] PASSED [ 30%]
tests/test_domain.py::test_weight_must_be_positive_and_finite[inf] PASSED [ 32%]
tests/test_domain.py::test_weight_must_be_positive_and_finite[nan] PASSED [ 35%]
tests/test_domain.py::test_money_addition_needs_one_currency PASSED      [ 37%]
tests/test_generics.py::test_a_general_quoter_serves_hazmat_consignments PASSED [ 40%]
tests/test_generics.py::test_a_hazmat_quoter_fails_on_a_general_consignment_at_runtime PASSED [ 42%]
tests/test_generics.py::test_hazmat_quoter_surcharge_follows_the_un_number PASSED [ 45%]
tests/test_generics.py::test_hazmat_consignment_validates_its_un_number[UN12] PASSED [ 47%]
tests/test_generics.py::test_hazmat_consignment_validates_its_un_number[1203] PASSED [ 50%]
tests/test_generics.py::test_hazmat_consignment_validates_its_un_number[un1203] PASSED [ 52%]
tests/test_generics.py::test_hazmat_consignment_validates_its_un_number[UN12034] PASSED [ 55%]
tests/test_generics.py::test_callback_protocol_accepts_any_parameter_name PASSED [ 57%]
tests/test_runtime_checkable.py::test_runtime_checkable_checks_names_only PASSED [ 60%]
tests/test_runtime_checkable.py::test_a_data_protocol_refuses_issubclass PASSED [ 62%]
tests/test_runtime_checkable.py::test_an_undecorated_subprotocol_warns_on_isinstance PASSED [ 65%]
tests/test_static.py::test_mypy_requires_a_branch_for_absence[unguarded] PASSED [ 67%]
tests/test_static.py::test_mypy_requires_a_branch_for_absence[walrus] PASSED [ 70%]
tests/test_static.py::test_mypy_requires_a_branch_for_absence[match] PASSED [ 72%]
tests/test_static.py::test_mypy_requires_a_branch_for_absence[early-return] PASSED [ 75%]
tests/test_static.py::test_mypy_requires_a_branch_for_absence[assert] PASSED [ 77%]
tests/test_static.py::test_mypy_requires_a_branch_for_the_sentinel PASSED [ 80%]
tests/test_static.py::test_mypy_infers_quoter_variance PASSED            [ 82%]
tests/test_static.py::test_mypy_matches_callback_parameter_names_without_slash PASSED [ 85%]
tests/test_static.py::test_mypy_checks_protocols_at_use_and_abcs_at_construction[protocol-use] PASSED [ 87%]
tests/test_static.py::test_mypy_checks_protocols_at_use_and_abcs_at_construction[abc-construction] PASSED [ 90%]
tests/test_static.py::test_mypy_checks_protocols_at_use_and_abcs_at_construction[declared-protocol] PASSED [ 92%]
tests/test_static.py::test_mypy_checks_protocols_at_use_and_abcs_at_construction[override-typo] PASSED [ 95%]
tests/test_static.py::test_mypy_explains_a_conflicting_member_but_not_a_wholly_absent_one PASSED [ 97%]
tests/test_static.py::test_mypy_accepts_a_null_gateway PASSED            [100%]

============================== 40 passed in 8.06s ==============================
```

```text
Success: no issues found in 11 source files
```

The suite has 27 test functions and 40 cases, because the static module parametrises two of its seven functions and two other tests run four values each.

**Experiment one: delete the guard in `book_with`.** In a scratch copy, remove the `if gateway is None:` branch and its `raise`, so the function returns `gateway.book(consignment)` directly. `uv run mypy --strict src tests` reports:

```text
src/structural_typing/carriers.py:61: error: Item "None" of "CarrierGateway | None" has no attribute "book"  [union-attr]
Found 1 error in 1 file (checked 11 source files)
```

Filtering `uv run pytest -q` with `grep -E '^(E  |FAILED|[0-9]+ (passed|failed))'` gives:

```text
E       AttributeError: 'NoneType' object has no attribute 'book'
FAILED tests/test_absence.py::test_book_with_turns_absence_into_a_booking_error
1 failed, 39 passed in 8.34s
```

Both layers catch it: the checker before the program runs, and the test with the `AttributeError` that the guard exists to prevent. Restore the guard.

**Experiment two: delete the `/` from `PricingRule.__call__`.** Change the signature to `def __call__(self, consignment: Consignment) -> Money: ...` and run the same commands. mypy reports three errors, each followed by the note that `"PricingRule.__call__" has type "def __call__(self, consignment: Consignment) -> Money"`:

```text
src/structural_typing/pricing.py:36: error: Incompatible default for parameter "discount" (default has type "Callable[[Consignment], Money]", parameter has type "PricingRule")  [assignment]
tests/test_generics.py:58: error: List item 1 has incompatible type "Callable[[Consignment], Money]"; expected "PricingRule"  [list-item]
tests/test_absence.py:48: error: Argument 3 to "quote" has incompatible type "Callable[[Consignment], Money]"; expected "PricingRule"  [arg-type]
Found 3 errors in 3 files (checked 11 source files)
```

The rejected functions are `no_discount`, which has a positional-only parameter, `per_kg`, whose parameter has another name, and the local `ten_euro_off`. The pytest run is not green either:

```text
E       assert 1 == 0
FAILED tests/test_static.py::test_mypy_matches_callback_parameter_names_without_slash
1 failed, 39 passed in 8.22s
```

The failing assertion is the clean-run check on the `PricingRule` snippet, which now exits 1. The runtime behaviour is unchanged, because the functions still run; the change is in what the checker accepts. Restore the `/`.

## What you can do now

- Say what mypy compares: `test_mypy_checks_protocols_at_use_and_abcs_at_construction[protocol-use]` shows the assignment error on the line that passes the value.
- Replace a do-nothing stand-in: `find_gateway` returns `CarrierGateway | None`, `test_mypy_requires_a_branch_for_absence` covers the walrus, `match`, early return and `assert` narrowings, and `no_discount` is the case where the stand-in is still right.
- Use a `sentinel`: `carriers_to_ask` takes one as its default, which separates "not given" from `None`.
- Read a variance error and write a callback Protocol: `test_mypy_infers_quoter_variance` rejects a `HazmatQuoter` where a general quoter is wanted, and `PricingRule.__call__` takes its parameter with `/`, so `per_kg` qualifies.
- Choose Protocol or ABC: `CarrierBase` shares code and `CarrierGateway` compares shape, and `test_runtime_checkable_checks_names_only` shows what `runtime_checkable` checks.

## For deeper coverage

Bobby Woolf's "Null Object", in *Pattern Languages of Program Design 3* (Addison-Wesley, 1998), is the source for the pattern, and it's on the [bibliography page]({{ '/bibliography/' | relative_url }}).

The sources for the language features are [PEP 544](https://peps.python.org/pep-0544/) for Protocols, the [typing specification](https://typing.python.org/en/latest/spec/protocol.html) and the [mypy protocols documentation](https://mypy.readthedocs.io/en/stable/protocols.html) for the rules, [PEP 695](https://peps.python.org/pep-0695/) for variance inference, [PEP 698](https://peps.python.org/pep-0698/) for `override`, [PEP 661](https://peps.python.org/pep-0661/) for `sentinel`, [PEP 814](https://peps.python.org/pep-0814/) for `frozendict`, and [What's New in Python 3.15](https://docs.python.org/3.15/whatsnew/3.15.html) for the `runtime_checkable` deprecation.

Luciano Ramalho's *Fluent Python*, second edition, and Brett Slatkin's *Effective Python*, third edition, both treat typing and protocols, and both are in the bibliography.
