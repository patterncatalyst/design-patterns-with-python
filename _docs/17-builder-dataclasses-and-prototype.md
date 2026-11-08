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

- Say why Builder and Prototype dissolve in Python, and which force each one leaves behind.
- Write a booking as a frozen keyword-only dataclass whose cross-field rules run once, in `__post_init__`.
- Say what mypy checks on that call (a `Literal` value, a missing field, a misspelt keyword) and what it can't (two `str` arguments swapped).
- Keep Prototype as a read-only table of template values copied with `replace` or `copy.replace`.
- Choose a field type so that a shallow copy can't share state, and measure the alternative with `copy.deepcopy`.

## Why this matters

A booking request has twelve fields. Four are required and eight have a sensible default, and three rules tie fields together: an insured booking needs a declared value, dangerous goods need a dangerous goods note among the documents, and the origin can't equal the destination. Three things go wrong in the obvious versions.

A twelve-argument constructor takes its arguments by position. A caller swaps origin and destination, and the booking runs from Singapore to Rotterdam where Rotterdam to Singapore was meant. Both are strings, so mypy accepts the call, and the rules pass because the two ports still differ.

A fluent builder replaces the constructor with a chain of steps. A caller leaves out `.destination(...)`, the chain still type-checks, and the mistake appears when `build()` runs.

A team keeps a template booking and copies it for each new consignment. The template has a list of documents, the copy shares that list, and adding the dangerous goods note to one customer's copy adds it to the template.

{% include excalidraw.html name="17-builder-dataclasses-and-prototype" caption="Figure 17.1: Building and copying a booking request. A template is copied into a frozen keyword-only request whose checks rerun on every replace, and only an immutable field type keeps two copies from sharing one list." %}

Read the figure from the top down. `TEMPLATES`, "read-only: name to template request", feeds `from_template`, "replace(template, ...)", which feeds `BookingRequest(...)`, "keyword-only, frozen". An arrow runs on to `__post_init__`, "cross-field checks: insured, dangerous goods, ports". Two dashed arrows leave that box. One runs right to a dashed box, "both replace functions rerun it: replace, copy.replace". The other runs down to the accent box at the bottom, "a list field is shared by copy and replace; a tuple field cannot be".

## The construction problem

Gamma, Helm, Johnson and Vlissides, in *Design Patterns* (1994), give Builder to a product too involved to produce in one call. A director walks through the steps, and interchangeable builders decide what the finished product turns out to be. Brandon Rhodes, in [The Builder Pattern](https://python-patterns.guide/gang-of-four/builder/), observes that Python programs reach for builders for convenience, a short series of calls that hides a tangle of construction, and rarely for the original aim of one process producing several representations. The force that remains is an object with many parts, several of them optional, that has to be complete and valid before anyone uses it. Python resolves that force with a class declaration, so the bucket is dissolves.

The shape that signals the problem is a long positional signature. This fixture, in the example's `conftest.py`, stands for a constructor a team inherits:

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

It's a comparison fixture and not model code. Its body holds the same three checks as the dataclass below, so every form in this chapter runs the same booking table. `test_a_positional_constructor_accepts_a_swapped_origin_and_destination` passes the two ports in the wrong order and finds a booking from `SGSIN` to `NLRTM` with nothing raised.

mypy splits these swaps by type. The test `test_mypy_cannot_see_two_same_typed_arguments_swapped` swaps the ports, then the carrier and service, then the two flags on a reduced copy of the signature. The run exits 0 and prints nothing. `test_mypy_reports_swapped_arguments_of_different_types` swaps the weight and the declared value in the same reduced model, and the test's own run prints:

```text
<string>:37: error: Argument 4 to "LegacyBookingRequest" has incompatible type "Money"; expected "Weight"  [arg-type]
<string>:37: error: Argument 8 to "LegacyBookingRequest" has incompatible type "Weight"; expected "Money | None"  [arg-type]
```

So a type system finds the swaps that cross types, and two arguments of one type pass whatever their order. [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) shows how `kw_only` makes a positional call a `TypeError`.

## A keyword-only dataclass is the builder

The model, with its three rules:

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

`test_the_request_has_twelve_fields_and_four_are_required` reads the field table: twelve fields, `consignment_id`, `origin`, `destination` and `weight` without a default, all keyword-only, and the eight defaults as written. The class is frozen and slotted, so `test_a_booking_request_and_a_weight_are_frozen` sees `FrozenInstanceError` on assignment and `test_a_booking_request_has_no_instance_dict` finds no `__dict__`. `Weight` has its own rule, checked in `test_a_requested_weight_must_be_positive_and_finite` for zero, a negative and NaN.

The carrier and the service level are `Literal` types, `CarrierCode` and `ServiceLevel`, and mypy checks them. `test_mypy_checks_literal_fields_and_keyword_names` runs three calls through the test's own helper, against the real package. Swapping the two `Literal` arguments prints:

```text
<string>:12: error: Argument "carrier" to "BookingRequest" has incompatible type "Literal['standard']"; expected "Literal['FASTLINE', 'AIRCO']"  [arg-type]
<string>:12: error: Argument "service" to "BookingRequest" has incompatible type "Literal['FASTLINE']"; expected "Literal['standard', 'express']"  [arg-type]
```

Leaving out `destination` prints `<string>:10: error: Missing named argument "destination" for "BookingRequest"  [call-arg]`, and a misspelt `servce=` prints `<string>:10: error: Unexpected keyword argument "servce" for "BookingRequest"; did you mean "service"?  [call-arg]`. The same swap of origin and destination, written with keywords, still type-checks, because both fields are `str`. What changed is that the call site says which is which, so a reviewer can read it. The check stays a human one.

The cross-field rules run in `__post_init__` once, at construction, so a request that exists is a request that passed them. `test_both_constructors_pass_the_booking_table` runs four cases (a minimal request, an insured one without a declared value, dangerous goods without the note, and equal ports) through three forms: the dataclass by keyword, the positional constructor and a fluent builder. All twelve combinations produce the expected fields or the expected `BookingError` message. The checks are the same in all three, so the difference is where the mistakes show up.

## What a builder costs

The fluent form is the fixture `_BookingRequestBuilder`: one method per field, each returning `self`, and a `build()` that checks the four required parts and hands everything to the positional constructor. `test_a_builder_with_a_step_left_out_fails_only_at_build` leaves out the destination and gets a plain `ValueError` with the message "builder is missing: destination", raised by `build()`. `test_mypy_accepts_a_builder_with_a_step_left_out` runs a reduced copy with the same shape and finds exit status 0 and no output. The builder moved the required-field check from the type checker, where the dataclass has it, to run time.

A dataclass call has the other properties a builder is praised for. Optional values take defaults, and the product is complete the moment it exists. What a builder adds is an intermediate object that is incomplete and mutable, and the checks you write to cope with that.

A builder keeps a real job where the value is assembled in stages from parts that arrive over time, and the parts aren't all in hand at one call site. Then the incomplete state is the point. For the dataclass side, Luciano Ramalho's *Fluent Python* has material on dataclasses, and Brett Slatkin's *Effective Python* has advice on keyword-only arguments. Both are in the [bibliography]({{ '/bibliography/' | relative_url }}).

## Prototype: templates and replace

The *Design Patterns* catalogue gives Prototype to a system that must create objects without naming their classes: it asks an existing, configured object to produce another like it. Rhodes's page, [The Prototype Pattern](https://python-patterns.guide/gang-of-four/prototype/), makes the Python case. Classes and functions are ordinary values, so a table of them and their arguments does the work, with no `clone` method on every product. The force that remains is a new object that starts as a copy of a configured one, and in this example a copy is a request with a few fields changed. That dissolves too.

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

`test_a_template_and_replace_give_a_new_request` runs both templates: the new request has the new id and weight, is a different object, and replacing the two fields back gives a value equal to the template, which still carries its placeholder id. `test_an_unknown_template_is_a_booking_error` asks for `'air-freight'` and gets `BookingError` with the message "no template 'air-freight'", the original `KeyError` suppressed. `test_the_template_registry_is_read_only` assigns into `TEMPLATES` and gets a `TypeError` about item assignment, so a caller can't add a template by accident. A read-only module-level table is a small case of the shared state that [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) takes up. Which class to construct, by name, is the question of [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}). Here every template is the same class.

`replace` is Prototype's `clone`, a point [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) makes. `dataclasses.replace` builds the copy by calling `__init__`, and the [dataclasses documentation](https://docs.python.org/3.15/library/dataclasses.html) says that this "ensures that `__post_init__()`, if present, is also called." The `copy` module gained a generic form. The [copy documentation](https://docs.python.org/3.15/library/copy.html) describes `copy.replace(obj, /, **changes)` as: "Creates a new object of the same type as obj, replacing fields with values from changes." It's marked "Added in version 3.13." A class opts in with `__replace__`, described there as: "This method should create a new object of the same type, replacing fields with values from changes." The dataclasses page adds: "Dataclass instances are also supported by generic function `copy.replace()`."

`test_replace_reruns_the_cross_field_checks` runs both functions on a template with `insured=True` and gets `BookingError` from each, matching "declared value", with the template unchanged. A replace can't build an invalid request. `test_copy_replace_works_on_dataclasses_and_refuses_a_plain_class` calls `copy.replace(template, service="standard")` on the express template and gets a standard request, with the template unchanged. A plain class without `__replace__` gets `TypeError: replace() does not support Plain objects` from a run of `copy.replace`.

mypy checks `copy.replace` the way it checks `dataclasses.replace`. `test_mypy_checks_copy_replace_like_dataclasses_replace` runs four calls, and the test's own run prints this for `copy.replace(request, wieght=weight)`, the misspelt keyword:

```text
<string>:14: error: Unexpected keyword argument "wieght" for "replace"; did you mean "weight"?  [call-arg]
<string>:14: note: "replace" defined in "copy"
```

The same misspelling through `dataclasses.replace` prints `Unexpected keyword argument "wieght" for "replace" of "BookingRequest"; did you mean "weight"?`. A wrong type, `origin=1`, is `Argument "origin" to "replace" has incompatible type "int"; expected "str"  [arg-type]`. A plain class is refused at the call with `expected "_SupportsReplace[[str], Never]"`. This is mypy 2.4.1, and the tests pin it. [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) uses `replace` to build each amended request.

## Shallow copies share

`replace` and `copy.copy` are shallow. The copy documentation defines the two kinds: "A shallow copy constructs a new compound object and then (to the extent possible) inserts references into it to the objects found in the original." And: "A deep copy constructs a new compound object and then, recursively, inserts copies into it of the objects found in the original."

The fixture for it is `_LooseRequest`, a mutable slotted dataclass whose `documents` field is `list[str] = field(default_factory=list)`. The model's request can't be used here, because its documents are a tuple.

`test_a_shallow_copy_shares_the_documents_list` makes a template with one document, copies it with `copy.copy` and again with `replace`, and appends a dangerous goods note through the copy. In both cases the template reads `["commercial invoice", "dangerous goods note"]`, and `clone.documents is template.documents` holds. `default_factory` runs only "when a default value is needed for this field", in the words of the [dataclasses documentation](https://docs.python.org/3.15/library/dataclasses.html). A copy isn't built that way, and takes whatever list the original holds. `test_mypy_cannot_see_a_shallow_copy_sharing_a_list` checks a reduced copy of the same code: exit 0 and no output.

`copy.deepcopy` separates the lists. `test_a_deep_copy_separates_the_documents_list` appends through a deep copy and finds the template unchanged and the two lists distinct objects. That works, and the documentation states its price: "Because deep copy copies everything it may copy too much, such as data which is intended to be shared between copies." A lock is a poor fit for it: on Python 3.15.2, `copy.deepcopy(threading.Lock())` raises `TypeError: cannot pickle '_thread.lock' object`. Build such an object again.

The better answer is the field type. In the model, `documents` is `tuple[str, ...]`. A tuple has no `append`, so a copy that wants a longer list of documents builds a new tuple. `test_a_tuple_field_makes_the_template_safe_to_share` copies a template with `copy.copy`, makes a longer request with `replace(clone, documents=(*clone.documents, "packing list"))`, and checks that the template still holds `("commercial invoice",)`. The copy equals its template and is a different object. Nothing is shared that can change. That frozen is shallow is covered in [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}), and a field type chosen for immutability is its remedy here as it is there.

## When not to use it

A value with three fields doesn't need this treatment: a plain frozen dataclass or an ordinary constructor is clear. An object whose construction is a process, such as opening a connection or calling a service, is a function. A request that holds no resources is the case `replace` and the copy functions fit. Don't deep-copy a lock; build another. A builder kept only for a fluent style gives up the type checker's missing-argument report in exchange for a chain of method calls.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a builder.** "A builder" leaves open where the cross-field rules run, how a template is copied and whether a class is needed at all. Paste a prompt that states the form:

> Write `BookingRequest` as `@dataclass(frozen=True, slots=True, kw_only=True)` with the cross-field rules in `__post_init__`, closed choices as `Literal` types and `documents` as a `tuple`. Keep templates in a read-only `frozendict` and copy them with `dataclasses.replace` or `copy.replace`, which rerun `__post_init__`. No builder class and no `clone` method.

If a template field is a `list`, ask for the test that appends through a copy.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/17-builder-dataclasses-and-prototype
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
collecting ... collected 42 items

tests/test_builder.py::test_a_positional_constructor_accepts_a_swapped_origin_and_destination PASSED [  2%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[keyword-minimal] PASSED [  4%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[keyword-insured-without-value] PASSED [  7%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[keyword-dangerous-without-note] PASSED [  9%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[keyword-same-ports] PASSED [ 11%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[positional-minimal] PASSED [ 14%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[positional-insured-without-value] PASSED [ 16%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[positional-dangerous-without-note] PASSED [ 19%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[positional-same-ports] PASSED [ 21%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[builder-minimal] PASSED [ 23%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[builder-insured-without-value] PASSED [ 26%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[builder-dangerous-without-note] PASSED [ 28%]
tests/test_builder.py::test_both_constructors_pass_the_booking_table[builder-same-ports] PASSED [ 30%]
tests/test_builder.py::test_the_request_has_twelve_fields_and_four_are_required PASSED [ 33%]
tests/test_builder.py::test_a_builder_with_a_step_left_out_fails_only_at_build PASSED [ 35%]
tests/test_builder.py::test_a_booking_request_and_a_weight_are_frozen PASSED [ 38%]
tests/test_builder.py::test_a_booking_request_has_no_instance_dict PASSED [ 40%]
tests/test_builder.py::test_a_requested_weight_must_be_positive_and_finite[zero] PASSED [ 42%]
tests/test_builder.py::test_a_requested_weight_must_be_positive_and_finite[negative] PASSED [ 45%]
tests/test_builder.py::test_a_requested_weight_must_be_positive_and_finite[nan] PASSED [ 47%]
tests/test_prototype.py::test_a_template_and_replace_give_a_new_request[rotterdam-singapore] PASSED [ 50%]
tests/test_prototype.py::test_a_template_and_replace_give_a_new_request[dangerous-goods] PASSED [ 52%]
tests/test_prototype.py::test_replace_reruns_the_cross_field_checks[replace] PASSED [ 54%]
tests/test_prototype.py::test_replace_reruns_the_cross_field_checks[copy-replace] PASSED [ 57%]
tests/test_prototype.py::test_a_deep_copy_separates_the_documents_list PASSED [ 59%]
tests/test_prototype.py::test_a_shallow_copy_shares_the_documents_list[copy] PASSED [ 61%]
tests/test_prototype.py::test_a_shallow_copy_shares_the_documents_list[replace] PASSED [ 64%]
tests/test_prototype.py::test_a_tuple_field_makes_the_template_safe_to_share PASSED [ 66%]
tests/test_prototype.py::test_copy_replace_works_on_dataclasses_and_refuses_a_plain_class PASSED [ 69%]
tests/test_prototype.py::test_an_unknown_template_is_a_booking_error PASSED [ 71%]
tests/test_prototype.py::test_the_template_registry_is_read_only PASSED  [ 73%]
tests/test_static.py::test_mypy_cannot_see_two_same_typed_arguments_swapped PASSED [ 76%]
tests/test_static.py::test_mypy_reports_swapped_arguments_of_different_types PASSED [ 78%]
tests/test_static.py::test_mypy_checks_literal_fields_and_keyword_names[literal-swap] PASSED [ 80%]
tests/test_static.py::test_mypy_checks_literal_fields_and_keyword_names[missing-field] PASSED [ 83%]
tests/test_static.py::test_mypy_checks_literal_fields_and_keyword_names[misspelt-keyword] PASSED [ 85%]
tests/test_static.py::test_mypy_accepts_a_builder_with_a_step_left_out PASSED [ 88%]
tests/test_static.py::test_mypy_checks_copy_replace_like_dataclasses_replace[dataclasses-name] PASSED [ 90%]
tests/test_static.py::test_mypy_checks_copy_replace_like_dataclasses_replace[copy-name] PASSED [ 92%]
tests/test_static.py::test_mypy_checks_copy_replace_like_dataclasses_replace[copy-type] PASSED [ 95%]
tests/test_static.py::test_mypy_checks_copy_replace_like_dataclasses_replace[plain-class] PASSED [ 97%]
tests/test_static.py::test_mypy_cannot_see_a_shallow_copy_sharing_a_list PASSED [100%]

============================== 42 passed in 4.77s ==============================
Success: no issues found in 8 source files
```

The suite has 21 test functions and 42 cases: 7 functions in `test_builder.py`, 8 in `test_prototype.py` and 6 in `test_static.py`. For how the tests and the mypy witnesses are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: delete a rule.** In a fresh scratch copy, delete the two lines in `BookingRequest.__post_init__` that raise for an insured booking without a declared value. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests | tail -1` prints:

```text
E       Failed: DID NOT RAISE BookingError
E       Failed: DID NOT RAISE BookingError
FAILED tests/test_builder.py::test_both_constructors_pass_the_booking_table[keyword-insured-without-value]
FAILED tests/test_prototype.py::test_replace_reruns_the_cross_field_checks[replace]
FAILED tests/test_prototype.py::test_replace_reruns_the_cross_field_checks[copy-replace]
3 failed, 39 passed in 4.98s
Success: no issues found in 8 source files
```

The keyword case of the booking table fails for the insured request, and so do both cases of `test_replace_reruns_the_cross_field_checks`. The positional and builder cases still pass, because the positional fixture holds its own copy of the check and the builder hands its values to that fixture. mypy finds nothing wrong: a rule that's missing is valid code.

**Experiment two: make the field a list.** In a fresh scratch copy, import `field` and change `documents` in `BookingRequest` to `list[str] = field(default_factory=list)`. The same filtered pytest run, then `uv run mypy --strict --no-incremental src tests | grep -v "^ "`, prints (`--no-incremental` fixes the order of the list, which otherwise depends on what mypy cached from an earlier run):

```text
E       AssertionError: assert {'consignment...in', 'weight'} == {'consignment...in', 'weight'}
tests/test_builder.py:51: AssertionError
FAILED tests/test_builder.py::test_the_request_has_twelve_fields_and_four_are_required
1 failed, 41 passed in 5.07s
src/builder_prototype/templates.py:22: error: Argument "documents" to "BookingRequest" has incompatible type "tuple[str]"; expected "list[str]"  [arg-type]
src/builder_prototype/templates.py:30: error: Argument "documents" to "BookingRequest" has incompatible type "tuple[str, str]"; expected "list[str]"  [arg-type]
tests/test_prototype.py:91: error: Argument "documents" to "replace" of "BookingRequest" has incompatible type "tuple[str, ...]"; expected "list[str]"  [arg-type]
tests/test_prototype.py:93: error: Non-overlapping equality check (left operand type: "list[str]", right operand type: "tuple[str]")  [comparison-overlap]
tests/test_prototype.py:94: error: Statement is unreachable  [unreachable]
tests/conftest.py:202: error: Argument "documents" to "BookingRequest" has incompatible type "tuple[str, ...]"; expected "list[str]"  [arg-type]
Found 6 errors in 3 files (checked 8 source files)
```

One test fails, `test_the_request_has_twelve_fields_and_four_are_required`, which reads the field defaults. The template-sharing tests pass, because the templates in `src` still hand over tuples at run time. mypy is the check that notices: it reports six errors, including the two literals in `templates.py` that pass tuples where a list is now declared.

## What you can do now

- Say why Builder and Prototype dissolve: the twelve-argument positional fixture shows the force a builder answers, and the dataclass answers it with a declaration.
- Write a booking as a frozen keyword-only dataclass: the field-table test reads twelve fields, and `__post_init__` runs the three rules once.
- Know what mypy checks on the call: `test_mypy_checks_literal_fields_and_keyword_names` rejects a swapped `Literal` and a misspelt keyword, and the same-type swap still passes.
- Keep Prototype as a table: `TEMPLATES` is read-only, and `from_template` copies with `replace`.
- Choose the field type: the tuple field is safe to share, and `copy.deepcopy` is the measured alternative.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Builder and Prototype. Brandon Rhodes's [The Builder Pattern](https://python-patterns.guide/gang-of-four/builder/) and [The Prototype Pattern](https://python-patterns.guide/gang-of-four/prototype/) give the Python view. The [`dataclasses` documentation](https://docs.python.org/3.15/library/dataclasses.html) covers `kw_only`, `replace` and `__post_init__`, and the [`copy` documentation](https://docs.python.org/3.15/library/copy.html) covers `copy.replace`, `__replace__` and deep copies. [PEP 557](https://peps.python.org/pep-0557/) specifies dataclasses. Luciano Ramalho's *Fluent Python* and Brett Slatkin's *Effective Python* are in the [bibliography page]({{ '/bibliography/' | relative_url }}).
