---
title: "Programming principles reviewed in code"
order: 46
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "F"
description: "Reference to the programming principles the book's code shows, with the chapter that states it, the tests that witness it and, where one was fetched, the page it comes from, plus a runnable example of the Law of Demeter."
---

## Learning objectives

By the end of this appendix you can:

- State a principle in one sentence and name the test that shows it in this book.
- Read a before/after pair as a measured comparison on one table of cases.
- Say which principle a design change serves, and which test would notice.
- Say why a principle with no test isn't listed.

## Why this matters

A principle is a reason for a shape, and a test is where the reason shows. "A class should have one job" is easy to nod at; a test that replaces the tariff and counts the quote fields that moved is harder to ignore. This appendix lists a principle where the book's code shows it, and the entries name the tests that do.

The chapters titled [SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}) and [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) teach five of these principles, and this appendix doesn't repeat them. It points back, then adds the ones the book's other chapters show.

A comparison is fair when both forms pass one table of cases, so what differs is the property the principle names: the number of classes, the places a rule lives, the call that fails. Where a principle is set against its absence, the weaker form sits in the tests' `conftest.py`, beside the form the chapter teaches.

## SOLID, by its tests

The statements below are the chapters' own sentences. Martin's *Agile Software Development: Principles, Patterns, and Practices* and Meyer's *Object-Oriented Software Construction* are on the bibliography page, and no page of either was fetched, so nothing here is their text.

| Principle | The chapter's statement | Tests | Chapter |
| --- | --- | --- | --- |
| Single responsibility | Martin's wording, as the chapter quotes it: "a class should have only one reason to change" | `test_each_change_moves_only_the_fields_it_feeds`, `test_pricing_and_tax_run_alone` | SRP, OCP, and LSP in Python |
| Open-closed | A change you have already seen is taken "without reopening code that is tested and in service" | `test_a_new_tax_rule_is_added_without_editing_quote` | SRP, OCP, and LSP in Python |
| Liskov substitution, with Design by Contract | "a subtype may accept more than its supertype and promise more, and it may not accept less or promise less" | `test_calculator_honours_the_rate_contract`, `test_contract_catches_a_strengthened_precondition`, `test_contract_catches_a_weakened_postcondition`, `test_mypy_rejects_an_incompatible_override`, `test_mypy_cannot_see_a_behavioural_violation` | SRP, OCP, and LSP in Python |
| Interface segregation | "a client should not be forced to depend on methods it does not use" | `test_a_fat_protocol_forces_fakes_to_stub_unused_methods`, `test_adapters_satisfy_every_role_without_naming_one` | ISP, DIP, and dependency injection without a framework |
| Dependency inversion | "High-level modules should not depend on low-level modules, and both should depend on abstractions." | `test_policy_modules_do_not_import_the_adapters`, `test_adapters_import_neither_policy_nor_protocols`, `test_swapping_the_carrier_changes_no_consumer`, `test_only_the_composition_root_names_a_concrete_carrier` | ISP, DIP, and dependency injection without a framework |

For the single responsibility principle, `test_each_change_moves_only_the_fields_it_feeds` replaces the tariff, a tax rule and the audit sink in three cases. The quote fields that change are `net` and `tax`, `tax`, and none. `test_pricing_and_tax_run_alone` builds pricing and a tax rule with no sink and no rule table.

For the open-closed principle, `test_a_new_tax_rule_is_added_without_editing_quote` passes a Hong Kong rule in as data. `quote` prices the consignment with zero tax, and the shipped `TAX_RULES` has no `HK` entry afterwards.

For Liskov substitution, a contract suite and mypy check different things. `test_calculator_honours_the_rate_contract` runs one suite against `BaseRate` and `FlatRate`. `test_contract_catches_a_strengthened_precondition` makes `AsiaOnlyRate` fail it with `rejected zone EU`, a subtype that accepts less, and `test_contract_catches_a_weakened_postcondition` makes `DollarRate` fail with `priced in USD`, a subtype that promises less. mypy takes the signature half: `test_mypy_rejects_an_incompatible_override` covers a narrowed argument, a widened return and a misspelt override. `test_mypy_cannot_see_a_behavioural_violation` gets exit 0 and empty output from mypy for a behavioural violation.

For interface segregation, `test_a_fat_protocol_forces_fakes_to_stub_unused_methods` shows mypy rejecting a tracking-only fake against the fat `CarrierGateway` for missing `book` and `cancel`, and accepting it against the narrow tracking Protocol. `test_adapters_satisfy_every_role_without_naming_one` checks that an adapter satisfies the booking, tracking and carrier roles with none of the three Protocols in its `__mro__`, so the narrow roles cost the adapter nothing.

For dependency inversion, the two import tests read the modules' imports with `ast`: neither policy module imports `carriers` or `app`, and the adapters import `domain` and neither the policy nor the Protocols. `test_swapping_the_carrier_changes_no_consumer` builds a `BookingService` and a tracking function with either carrier, and the reference is what differs. In the final project, `test_only_the_composition_root_names_a_concrete_carrier` finds the concrete carrier named in `app.py` and, with `carriers.py` excluded, nowhere else in the package.

## Composition over inheritance

A class that inherits from its collaborator takes on the collaborator's public methods. A class that holds the collaborator as a field doesn't. Brandon Rhodes's [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/) quotes the Gang of Four principle: "Favor object composition over class inheritance."

The chapter titled [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) keeps a class adapter in its tests as the comparison form:

<!-- fmt:off -->
```python
# Comparison: a class adapter. Inheriting from the SDK client makes the client's own methods part
# of the adapter's public surface.
class _FastlineClassAdapter(FastlineClient):
    def book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str:
        payload = {
            "ref": consignment_id,
            "weight_lb": str(weight.pounds.quantize(_HUNDREDTH, rounding=ROUND_HALF_UP)),
        }
        return f"FL-{self.submit_shipment(payload).tracking_number}"

    def insure(self, reference: str, value: Money, /) -> None:
        cents = int(value.amount.scaleb(2))
        self.add_cover(int(reference.removeprefix("FL-")), cents, value.currency)
```
<!-- fmt:on -->

`test_a_class_adapter_still_exposes_the_clients_own_methods` finds `submit_shipment` on this adapter and not on the composing `FastlineGateway`, so a caller holding the class adapter can call the client's method and skip the translation. The cost of the other design shows in a count. `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier` reads the class definitions: the bridge declares two booking classes, `InsuredBooking` and `StandardBooking`, and the class-per-pair design declares five, `_CarrierBooking` and four pairs. `test_every_booking_kind_works_with_every_carrier` runs eight cases, two carriers by two kinds in both designs, so the two designs differ in class count and not in behaviour. That test shows behaviour, not structure, so it supports the count test and doesn't stand alone.

## Duplication, speculation and size

The chapter titled [Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) prices a consignment two ways. The function, from `src`:

<!-- fmt:off -->
```python
def quote(consignment: Consignment, tariff: Tariff) -> RateQuote:
    """Price a consignment: its zone's flat fee, the fuel fee, then tax rounded to the cent."""
    try:
        flat_fee = tariff.flat_fee_by_zone[consignment.zone]
    except KeyError:
        raise RatingError(f"no flat fee for zone {consignment.zone!r}") from None
    net = flat_fee + tariff.fuel_fee
    tax = (net * tariff.tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return RateQuote(consignment.id, Money(net + tax, tariff.currency))
```
<!-- fmt:on -->

The comparison form is a rating engine built from a factory, a strategy and a visitor, kept in the tests. One of its charge classes:

<!-- fmt:off -->
```python
class _FuelSurcharge(_Charge):
    def __init__(self, amount: Decimal) -> None:
        self.amount = amount

    def accept(self, visitor: _ChargeVisitor) -> None:
        visitor.visit_fuel(self)
```
<!-- fmt:on -->

`test_every_rating_form_quotes_the_same_table` runs four cases, two zones by two forms, and both forms give the same totals. The three principles below are measured on that pair.

**DRY.** *The Pragmatic Programmer* is the source, and the tips page at [pragprog.com](https://pragprog.com/tips/) says: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." The test supports a narrower reading than copied code. The fee itself isn't repeated: the engine reads `tariff.fuel_fee`. What `test_the_fuel_surcharge_lives_in_one_definition_of_the_function` counts is where the rule for applying it lives. It searches for definitions whose own name or statements mention `fuel`, and finds `quote` in the function and five definitions in the engine: `_ChargeVisitor.visit_fuel`, `_FlatFeeStrategy.charges`, `_FuelSurcharge`, `_FuelSurcharge.accept` and `_NetTotalVisitor.visit_fuel`. The count is a name match, so it's a measure of how many places a reader opens, not of copied text.

**YAGNI.** Fowler's [Yagni](https://martinfowler.com/bliki/Yagni.html) page says that "some capability we presume our software needs in the future should not be built now", and ties the idea to the practice of Simple Design. `test_the_engine_needs_more_classes_functions_and_lines_than_the_function` measures classes, functions and lines as `(0, 1, 8)` for the function and `(9, 17, 57)` for the engine. The visitor is the engine's extension point, and `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time` shows what it did on the first new charge kind: `AttributeError` with `has no attribute 'visit_remote_area'`, raised at the first quote.

**Simple design.** Fowler's [Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html) page lists four rules in priority order: "Passes the tests", "Reveals intention", "No duplication" and "Fewest elements". The tests here speak to two of them. "Passes the tests" holds for both forms, by the shared table. "Fewest elements" is measured twice: by the sizes above, and by `test_one_engine_quote_makes_more_python_calls_than_the_function`, which records one Python call for the function and eleven for the engine. No test here judges the other two rules, so none is claimed.

## Orthogonality

The tips page gives Tip 17, "Eliminate Effects Between Unrelated Things", and says: "Design components that are self-contained, independent, and have a single, well-defined purpose." In the bridge, the booking kind and the carrier vary on separate axes. `test_a_new_booking_kind_needs_no_gateway_change` uses `_ExpressBooking`, a class defined in its test module, and it runs on either carrier through the gateway's existing `book` and `insure`. The single responsibility test is a second witness: when `test_each_change_moves_only_the_fields_it_feeds` swaps the audit sink, no quote field moves.

## Fail fast

Jim Shore's [Fail Fast](https://martinfowler.com/ieeeSoftware/failFast.pdf) describes working around a problem automatically, which fails slowly, as the alternative, and says: "A system that fails fast does exactly the opposite: when a problem occurs, it fails immediately and visibly."

`test_unknown_carrier_fails_at_the_composition_root` builds the application with an unknown code, `NOSUCH`, and gets a `ValueError` naming it at construction, before a booking exists. The contrast is in the anti-patterns chapter. `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered` builds a service-locator engine without complaint and gets `KeyError: 'tariff'` at the first quote.

## EAFP

The Python glossary defines the style: "Easier to ask for forgiveness than permission. This common Python coding style assumes the existence of valid keys or attributes and catches exceptions if the assumption proves false." The chapter titled [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}) owns the race mechanics. The tests that show the trade:

- `test_every_cache_form_reads_loads_and_evicts_the_same_way` runs six cases, and the look-first and EAFP forms agree on one table.
- `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read` forces an eviction between the check and the read, and the look-first form raises `KeyError: '0901.21'` with no load.
- `test_an_eafp_read_reloads_when_another_thread_evicts_first` forces the same interleaving, and the EAFP form reloads and returns `8.0`.
- `test_two_eafp_readers_that_both_miss_both_load` is the cost: both readers load.

## The Law of Demeter

The Demeter project at Northeastern University hosts the rule. Its [general formulation](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html) page gives the motto as "Only talk to your immediate friends", and the aim as "Each unit should have only limited knowledge about other units". Its [object formulation](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html) page says "Within a method, messages can only be sent to the following objects", and then lists them.

In paraphrase, the list names the method's parameters, which include the enclosing object itself; a global object, for pragmatic reasons; an immediate part of the enclosing object, stored or computed; and an object the method creates. Under the immediate part, item 2.1 adds an object that a method called on the enclosing object returns, attributes of the enclosing object included, and item 2.2 adds an element of a collection that is an attribute of the enclosing object. Item 2.1 matters here: inside a `Shipment` method `self.invoice` is within the list, and an invoice read as an attribute of a parameter is not.

The member `examples/46-appendix-f-programming-principles` puts one question to the rule: who answers for the amount due? It has 12 test functions and 18 cases. A `Shipment` holds an `Invoice` and the credits granted against it, and `amount_due()` is the invoice total less each credit. The reader the package ships asks the shipment. `billing.py` has the method `Shipment.amount_due` and the function `remittance_line`:

<!-- fmt:off -->
```python
    def amount_due(self) -> Money:
        due = self.invoice.total
        for credit in self.credits:
            due = due - credit.amount
        return due
```
<!-- fmt:on -->

<!-- fmt:off -->
```python
def remittance_line(shipment: Shipment, /) -> str:
    return f"{shipment.consignment_id} {shipment.amount_due()}"
```
<!-- fmt:on -->

The comparison reader, kept in the tests' `conftest.py` and not in the package, reaches through the shipment to its invoice:

<!-- fmt:off -->
```python
def _chained_remittance(shipment: Shipment, /) -> str:
    # The comparison form: it reaches through the shipment to its invoice.
    return f"{shipment.consignment_id} {shipment.invoice.total}"
```
<!-- fmt:on -->

`test_each_reader_names_the_attributes_it_depends_on` reads both readers' own source: the shipped reader names `amount_due` and `consignment_id`, and the comparison names `consignment_id`, `invoice` and `total`. It counts attribute names, not the calls made inside them. `test_both_readers_give_the_same_line_without_credits` runs both readers on two invoices and gets `CN-1 30.00 EUR` and `CN-2 35.63 EUR` from both readers. After a credit of 10.63 EUR against an invoice of 35.63 EUR, `test_a_credit_reaches_only_the_reader_that_asks_the_shipment` gets `CN-3 25.00 EUR` from the shipped reader and `CN-3 35.63 EUR` from the comparison. The comparison reader is coupled to where the total lives, so a credit applied through the shipment never reaches it.

### The final project's chains

The final project's code has the comparison reader's shape in five places.

| Place | Expression | What it reaches |
| --- | --- | --- |
| `test_acceptance.py:36-41`, in the helper `acceptance_failures` | `shipment.quote.total`, `shipment.declaration.duty` and `shipment.invoice.total`, and the same three with `.amount` | parts of the parameter `shipment`, and what those parts hold |
| `test_parts.py:98` | `shipment.quote.total, shipment.invoice.total` | parts of the parameter `shipment`, and what those parts hold |
| `conftest.py:118`, in the comparison desk `_EagerBookingDesk` | `self._plan.sailing.origin` | the plan's `sailing`, and what it holds |
| `desk.py:58` | `self._plan.sailing.origin` | the plan's `sailing`, and what it holds |
| `billing.py:39`, in `settle` | `invoice.total.amount` | the amount of a total that the parameter `invoice` returned |

Under the object form, a message to the parameter `shipment` or `invoice` is within the list, and so is a message to `self._plan`, an immediate part. An attribute read on what they return is not: the `total` of a quote, the `duty` of a declaration, the `origin` of a sailing. Read to the letter, the list also leaves out the operators and formatting applied to a returned `Money`, such as the `-` in `amount_due` and the f-string in each reader; `test_each_reader_names_the_attributes_it_depends_on` lists the attribute names a reader's source uses, so it sees the names a chain reads and not those operations. The chains couple their readers to the shape behind the first step. The helper depends on a shipment's invoice having a `total` that has an `amount`, and the desk on a plan carrying a sailing that has an origin.

Two facts limit what these lines show. Past the first step, the objects the chains read are frozen dataclasses: the `RateQuote`, `CustomsDeclaration` and `Invoice` that a frozen `Shipment` holds or `settle` is given, the `Money` each of them holds or returns, and `Sailing`. The desk's first step, its stowage plan, is a plain class, but the chain reads only its `sailing`, a frozen `Sailing`. And the final project grants no credits: `grep -rni credit` over its `src` prints nothing, and its `Shipment` has no `amount_due`, so there's no credit for these reads to miss. The lines are counter-examples to the form of the rule, not defects any test found, and they stay as written.

### Running the member

From the repository root, run `uv sync --locked --all-packages` once. Then:

```bash
cd examples/46-appendix-f-programming-principles
uv run pytest -q
uv run mypy --strict src tests
```

The last line of each command, from a fresh run on Python 3.15.2, with the duration left out:

```text
18 passed
Success: no issues found in 6 source files
```

## For deeper coverage

The books are on the [bibliography page]({{ '/bibliography/' | relative_url }}): Robert C. Martin's *Agile Software Development: Principles, Patterns, and Practices*, Bertrand Meyer's *Object-Oriented Software Construction*, *The Pragmatic Programmer*, and the Gang of Four's *Design Patterns*. The pages quoted above are the primary sources for the rest: Rhodes's [composition page](https://python-patterns.guide/gang-of-four/composition-over-inheritance/), the Pragmatic Programmer [tips](https://pragprog.com/tips/), Fowler's [Yagni](https://martinfowler.com/bliki/Yagni.html) and [Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html), Shore's [Fail Fast](https://martinfowler.com/ieeeSoftware/failFast.pdf), the Python [glossary](https://docs.python.org/3.15/glossary.html) and the Demeter project's [general](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html) and [object](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html) formulations.

The tests live in the chapters titled [SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}), [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}), [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}), [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}), [Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) and [Final project]({{ '/docs/39-final-project/' | relative_url }}).
