---
title: "Programming principles reviewed in code"
order: 46
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "F"
description: "Reference to the programming principles the code shows, with the chapter that states each one, what it measures and, where one was fetched, the page it comes from, plus a runnable example of the Law of Demeter."
---

## Learning objectives

By the end of this appendix you can:

- State a principle in one sentence and say what in the code shows it.
- Read a before/after pair as a measured comparison on one table of cases.
- Say which principle a design change serves, and what would notice if it broke.
- Say why a principle with nothing to measure isn't listed.

## Why this matters

A principle is a reason for a shape, and a measurement is where the reason shows. "A class should have one job" is easy to nod at; replacing the tariff and counting the quote fields that move is harder to ignore. A principle is listed here only where the code shows it.

A comparison is fair when both forms pass one table of cases, so what differs is the property the principle names: the number of classes, the places a rule lives, the call that fails. Where a principle is set against its absence, the weaker form sits in the tests' `conftest.py`, beside the form taught.

## SOLID

[SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}) and [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}) teach these five. The statements are those chapters' sentences; Martin's *Agile Software Development: Principles, Patterns, and Practices* and Meyer's *Object-Oriented Software Construction* are on the bibliography page, and no page of either was fetched.

| Principle | Statement | What shows it |
| --- | --- | --- |
| Single responsibility | Martin's wording: "a class should have only one reason to change" | Replacing the tariff moves `net` and `tax`, a tax rule moves `tax`, the audit sink moves nothing; pricing and a tax rule run with no sink and no rule table |
| Open-closed | A change already seen is taken "without reopening code that is tested and in service" | A Hong Kong tax rule is passed in as data; `quote` prices with zero tax and the shipped `TAX_RULES` gains no `HK` entry |
| Liskov substitution, with Design by Contract | "a subtype may accept more than its supertype and promise more, and it may not accept less or promise less" | One contract suite passes `BaseRate` and `FlatRate`, fails `AsiaOnlyRate` (`rejected zone EU`, accepts less) and `DollarRate` (`priced in USD`, promises less) |
| Interface segregation | "a client should not be forced to depend on methods it does not use" | mypy rejects a tracking-only fake against the fat `CarrierGateway` for missing `book` and `cancel`, and accepts it against the narrow tracking Protocol |
| Dependency inversion | "High-level modules should not depend on low-level modules, and both should depend on abstractions." | An `ast` scan of imports: policy modules import neither `carriers` nor `app`; adapters import `domain` only; the final project names a concrete carrier only in `app.py` |

Liskov substitution splits between two checkers. mypy takes the signature half, refusing a narrowed argument, a widened return and a misspelt override; for a behavioural violation it exits 0 with empty output, and only the contract suite catches it. Interface segregation costs the adapter nothing: it satisfies the booking, tracking and carrier roles with none of the three Protocols in its `__mro__`.

## Composition over inheritance

A class that inherits from its collaborator takes on the collaborator's public methods; a class that holds it as a field doesn't. Brandon Rhodes's [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/) quotes the Gang of Four: "Favor object composition over class inheritance." The comparison form from [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}):

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

| Measure | Composition | Inheritance |
| --- | --- | --- |
| `submit_shipment` on the adapter | absent from `FastlineGateway` | present, so a caller can skip the translation |
| Booking classes for two kinds and two carriers | 2 (`InsuredBooking`, `StandardBooking`) | 5 (`_CarrierBooking` and four pairs) |
| Behaviour over two carriers by two kinds | same | same |

## Duplication, speculation and size

[Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) prices a consignment two ways, and both give the same totals over two zones. The function:

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

The comparison is a rating engine built from a factory, a strategy and a visitor, kept in the tests. One of its charge classes:

<!-- fmt:off -->
```python
class _FuelSurcharge(_Charge):
    def __init__(self, amount: Decimal) -> None:
        self.amount = amount

    def accept(self, visitor: _ChargeVisitor) -> None:
        visitor.visit_fuel(self)
```
<!-- fmt:on -->

| Principle | Source | Function | Engine |
| --- | --- | --- | --- |
| DRY | "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." ([tips](https://pragprog.com/tips/)) | 1 definition mentions `fuel` | 5 definitions mention `fuel` |
| YAGNI | "some capability we presume our software needs in the future should not be built now" ([Yagni](https://martinfowler.com/bliki/Yagni.html)) | 0 classes, 1 function, 8 lines | 9 classes, 17 functions, 57 lines |
| Simple design, "Fewest elements" | [Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html) | 1 Python call per quote | 11 Python calls per quote |

- **DRY is about knowledge, not copied text.** The fee isn't repeated; the engine reads `tariff.fuel_fee`. The five definitions are where the rule for applying it lives: `_ChargeVisitor.visit_fuel`, `_FlatFeeStrategy.charges`, `_FuelSurcharge`, `_FuelSurcharge.accept` and `_NetTotalVisitor.visit_fuel`. The count is a name match, so it measures how many places a reader opens.
- **YAGNI: the extension point didn't extend.** The visitor exists for new charge kinds, and the first new one fails with `AttributeError` (`has no attribute 'visit_remote_area'`) at the first quote.
- **Simple design: two of four rules are measured.** Beck's rules in priority order are "Passes the tests", "Reveals intention", "No duplication" and "Fewest elements". Both forms pass the shared table, and the counts above measure the last. Nothing here judges the middle two, so neither is claimed.

## Other principles

| Principle | Source | What shows it |
| --- | --- | --- |
| Orthogonality | Tip 17, "Eliminate Effects Between Unrelated Things": "Design components that are self-contained, independent, and have a single, well-defined purpose." ([tips](https://pragprog.com/tips/)) | A new booking kind runs on either carrier through the gateway's existing `book` and `insure`; swapping the audit sink moves no quote field |
| Fail fast | "A system that fails fast does exactly the opposite: when a problem occurs, it fails immediately and visibly." ([Shore, Fail Fast](https://martinfowler.com/ieeeSoftware/failFast.pdf)) | An unknown carrier code `NOSUCH` raises `ValueError` at the composition root, before a booking exists; a service-locator engine builds fine and fails with `KeyError: 'tariff'` at the first quote |
| EAFP | "Easier to ask for forgiveness than permission. This common Python coding style assumes the existence of valid keys or attributes and catches exceptions if the assumption proves false." ([glossary](https://docs.python.org/3/glossary.html)) | See below |

EAFP is a trade, shown by forcing an eviction between check and read; [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}) owns the race mechanics.

| Case | Look-first | EAFP |
| --- | --- | --- |
| No contention | same answers on one table | same answers on one table |
| Another thread evicts between check and read | `KeyError: '0901.21'`, no load | reloads and returns `8.0` |
| Two readers both miss | - | both load, the cost of EAFP |

## The Law of Demeter

The Demeter project at Northeastern University hosts the rule. Its [general formulation](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html) gives the motto "Only talk to your immediate friends" and the aim "Each unit should have only limited knowledge about other units". Its [object formulation](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html) says "Within a method, messages can only be sent to the following objects". In paraphrase:

| Allowed receiver | Note |
| --- | --- |
| The method's parameters | including the enclosing object itself |
| A global object | for pragmatic reasons |
| An immediate part of the enclosing object | stored or computed; item 2.1 adds what a method called on the enclosing object returns, attributes included; item 2.2 adds an element of a collection attribute |
| An object the method creates | |

Item 2.1 is the one that matters: inside a `Shipment` method, `self.invoice` is allowed; an invoice read as an attribute of a parameter isn't.

`examples/46-appendix-f-programming-principles` asks who answers for the amount due. A `Shipment` holds an `Invoice` and the credits granted against it. The shipped reader asks the shipment:

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

The comparison reader, kept in the tests' `conftest.py`, reaches through the shipment to its invoice:

<!-- fmt:off -->
```python
def _chained_remittance(shipment: Shipment, /) -> str:
    # The comparison form: it reaches through the shipment to its invoice.
    return f"{shipment.consignment_id} {shipment.invoice.total}"
```
<!-- fmt:on -->

| | `remittance_line` | `_chained_remittance` |
| --- | --- | --- |
| Attribute names in its source | `amount_due`, `consignment_id` | `consignment_id`, `invoice`, `total` |
| No credits, two invoices | `CN-1 30.00 EUR`, `CN-2 35.63 EUR` | the same |
| 10.63 EUR credit on 35.63 EUR | `CN-3 25.00 EUR` | `CN-3 35.63 EUR` |

The comparison reader is coupled to where the total lives, so a credit applied through the shipment never reaches it.

### The final project's chains

The final project's code has the comparison reader's shape in five places.

| Place | Expression | What it reaches |
| --- | --- | --- |
| `test_acceptance.py:36-41`, in the helper `acceptance_failures` | `shipment.quote.total`, `shipment.declaration.duty` and `shipment.invoice.total`, and the same three with `.amount` | parts of the parameter `shipment`, and what those parts hold |
| `test_parts.py:98` | `shipment.quote.total, shipment.invoice.total` | parts of the parameter `shipment`, and what those parts hold |
| `conftest.py:118`, in the comparison desk `_EagerBookingDesk` | `self._plan.sailing.origin` | the plan's `sailing`, and what it holds |
| `desk.py:58` | `self._plan.sailing.origin` | the plan's `sailing`, and what it holds |
| `billing.py:39`, in `settle` | `invoice.total.amount` | the amount of a total that the parameter `invoice` returned |

A message to `shipment`, `invoice` or `self._plan` is allowed; an attribute read on what they return (the `total` of a quote, the `origin` of a sailing) isn't. Read to the letter, the list also excludes operators and formatting on a returned `Money`, such as the `-` in `amount_due`; counting attribute names doesn't see those.

Two facts limit what the chains cost. Past the first step, every object read is a frozen dataclass (`RateQuote`, `CustomsDeclaration`, `Invoice`, `Money`, `Sailing`). And the final project grants no credits: `grep -rni credit` over its `src` prints nothing, and its `Shipment` has no `amount_due`. The chains are counter-examples to the form of the rule, not defects, and they stay.

### Running the member

From the repository root, run `uv sync --locked --all-packages` once. Then:

```bash
cd examples/46-appendix-f-programming-principles
uv run pytest -q
uv run mypy --strict src tests
```

All 18 cases pass and mypy is clean.

## For deeper coverage

The books are on the [bibliography page]({{ '/bibliography/' | relative_url }}): Robert C. Martin's *Agile Software Development: Principles, Patterns, and Practices*, Bertrand Meyer's *Object-Oriented Software Construction*, *The Pragmatic Programmer*, and the Gang of Four's *Design Patterns*. The pages quoted above are the primary sources for the rest: Rhodes's [composition page](https://python-patterns.guide/gang-of-four/composition-over-inheritance/), the Pragmatic Programmer [tips](https://pragprog.com/tips/), Fowler's [Yagni](https://martinfowler.com/bliki/Yagni.html) and [Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html), Shore's [Fail Fast](https://martinfowler.com/ieeeSoftware/failFast.pdf), the Python [glossary](https://docs.python.org/3/glossary.html) and the Demeter project's [general](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html) and [object](https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html) formulations.

The comparisons come from [SRP, OCP, and LSP in Python]({{ '/docs/05-srp-ocp-lsp/' | relative_url }}), [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}), [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}), [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}), [Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) and [Final project]({{ '/docs/39-final-project/' | relative_url }}).
