"""Fixtures. The comparison forms live here as fixture parameters so that they run the same
journey table, the same restore table and the same pricing table as the idiomatic code: a
singledispatch visitor and the GoF accept form, a shallow and a deep memento, and closure rules."""

import copy
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from decimal import Decimal
from functools import singledispatch
from typing import Protocol

import pytest
from visitor_memento_interpreter.domain import (
    Consignment,
    ConsignmentId,
    DocumentKind,
    Money,
    Weight,
)
from visitor_memento_interpreter.events import (
    Booked,
    Cleared,
    Delivered,
    Departed,
    HandlingEvent,
    Loaded,
    describe,
)
from visitor_memento_interpreter.memento import Booking, BookingRequest, rollback
from visitor_memento_interpreter.tariff import STANDARD_TARIFF, evaluate

CN1 = ConsignmentId("CN-1")

JOURNEY: tuple[HandlingEvent, ...] = (
    Booked(CN1, "NLRTM"),
    Loaded(CN1, "NLRTM"),
    Departed(CN1, "NLRTM"),
    Cleared(CN1, "SGSIN"),
    Delivered(CN1, "SGSIN"),
)

# ---------------------------------------------------------------------------------------------
# Visitor forms


class EventVisitor[T](Protocol):
    """The GoF visitor: one visit method per element class."""

    def visit_booked(self, event: Booked, /) -> T: ...
    def visit_loaded(self, event: Loaded, /) -> T: ...
    def visit_departed(self, event: Departed, /) -> T: ...
    def visit_cleared(self, event: Cleared, /) -> T: ...
    def visit_delivered(self, event: Delivered, /) -> T: ...


@dataclass(frozen=True, slots=True)
class _AcceptingBooked(Booked):
    def accept[T](self, visitor: EventVisitor[T], /) -> T:
        return visitor.visit_booked(self)


@dataclass(frozen=True, slots=True)
class _AcceptingLoaded(Loaded):
    def accept[T](self, visitor: EventVisitor[T], /) -> T:
        return visitor.visit_loaded(self)


@dataclass(frozen=True, slots=True)
class _AcceptingDeparted(Departed):
    def accept[T](self, visitor: EventVisitor[T], /) -> T:
        return visitor.visit_departed(self)


@dataclass(frozen=True, slots=True)
class _AcceptingCleared(Cleared):
    def accept[T](self, visitor: EventVisitor[T], /) -> T:
        return visitor.visit_cleared(self)


@dataclass(frozen=True, slots=True)
class _AcceptingDelivered(Delivered):
    def accept[T](self, visitor: EventVisitor[T], /) -> T:
        return visitor.visit_delivered(self)


class _Describer:
    def visit_booked(self, event: Booked, /) -> str:
        return f"{event.consignment_id} booked at {event.port}"

    def visit_loaded(self, event: Loaded, /) -> str:
        return f"{event.consignment_id} loaded at {event.port}"

    def visit_departed(self, event: Departed, /) -> str:
        return f"{event.consignment_id} departed {event.port}"

    def visit_cleared(self, event: Cleared, /) -> str:
        return f"{event.consignment_id} cleared customs at {event.port}"

    def visit_delivered(self, event: Delivered, /) -> str:
        return f"{event.consignment_id} delivered at {event.port}"


ACCEPTING_TWINS = (
    _AcceptingBooked(CN1, "NLRTM"),
    _AcceptingLoaded(CN1, "NLRTM"),
    _AcceptingDeparted(CN1, "NLRTM"),
    _AcceptingCleared(CN1, "SGSIN"),
    _AcceptingDelivered(CN1, "SGSIN"),
)


def _describe_by_accept(event: HandlingEvent, /) -> str:
    if isinstance(
        event,
        _AcceptingBooked
        | _AcceptingLoaded
        | _AcceptingDeparted
        | _AcceptingCleared
        | _AcceptingDelivered,
    ):
        return event.accept(_Describer())
    raise TypeError(f"{event!r} has no accept method")


def _singledispatch_describe() -> Callable[[HandlingEvent], str]:
    @singledispatch
    def describe_event(event: object, /) -> str:
        return "unrecognised event"

    @describe_event.register
    def _(event: Booked, /) -> str:
        return f"{event.consignment_id} booked at {event.port}"

    @describe_event.register
    def _(event: Loaded, /) -> str:
        return f"{event.consignment_id} loaded at {event.port}"

    @describe_event.register
    def _(event: Departed, /) -> str:
        return f"{event.consignment_id} departed {event.port}"

    @describe_event.register
    def _(event: Cleared, /) -> str:
        return f"{event.consignment_id} cleared customs at {event.port}"

    @describe_event.register
    def _(event: Delivered, /) -> str:
        return f"{event.consignment_id} delivered at {event.port}"

    return describe_event


type VisitorForm = tuple[tuple[HandlingEvent, ...], Callable[[HandlingEvent], str]]
"""A journey and the function that describes one of its events."""

_VISITOR_FORMS: dict[str, VisitorForm] = {
    "match": (JOURNEY, describe),
    "singledispatch": (JOURNEY, _singledispatch_describe()),
    "accept": (ACCEPTING_TWINS, _describe_by_accept),
}


@pytest.fixture
def accepting_twins() -> tuple[HandlingEvent, ...]:
    return ACCEPTING_TWINS


@pytest.fixture(params=list(_VISITOR_FORMS))
def visitor_form(request: pytest.FixtureRequest) -> VisitorForm:
    return _VISITOR_FORMS[request.param]


# ---------------------------------------------------------------------------------------------
# Memento forms

type MementoForm = Callable[[Booking], AbstractContextManager[None]]


@contextmanager
def _shallow_rollback(booking: Booking) -> Iterator[None]:
    """Keep a shallow copy: the document set is shared with the live booking."""
    saved = copy.copy(booking)
    try:
        yield
    except Exception:
        booking.request = saved.request
        booking.documents = saved.documents
        booking.audit.append("rolled back")
        raise


@contextmanager
def _deep_rollback(booking: Booking) -> Iterator[None]:
    """Keep a deep copy: the audit is copied too, so restoring it erases the refused attempt."""
    saved = copy.deepcopy(booking)
    try:
        yield
    except Exception:
        booking.request = saved.request
        booking.documents = saved.documents
        booking.audit = saved.audit
        booking.audit.append("rolled back")
        raise


_MEMENTO_FORMS: dict[str, MementoForm] = {
    "snapshot": rollback,
    "shallow": _shallow_rollback,
    "deepcopy": _deep_rollback,
}


@pytest.fixture(params=list(_MEMENTO_FORMS))
def memento_form(request: pytest.FixtureRequest) -> MementoForm:
    return _MEMENTO_FORMS[request.param]


@pytest.fixture
def shallow_memento() -> MementoForm:
    return _MEMENTO_FORMS["shallow"]


@pytest.fixture
def deep_memento() -> MementoForm:
    return _MEMENTO_FORMS["deepcopy"]


@pytest.fixture
def booking() -> Booking:
    """A booking of 100 kg to Singapore with its commercial invoice attached."""
    return Booking(
        BookingRequest(consignment_id=CN1, kilograms=Decimal(100), destination="SGSIN"),
        {DocumentKind.COMMERCIAL_INVOICE},
    )


# ---------------------------------------------------------------------------------------------
# Rule forms

type PricingRule = Callable[[Consignment], Money]


def _per_kg(rate: Money) -> PricingRule:
    def price(consignment: Consignment, /) -> Money:
        return rate.times(consignment.weight.kilograms)

    return price


def _flat(amount: Money) -> PricingRule:
    def price(consignment: Consignment, /) -> Money:
        return amount

    return price


def _add(left: PricingRule, right: PricingRule) -> PricingRule:
    def price(consignment: Consignment, /) -> Money:
        return left(consignment) + right(consignment)

    return price


def _max(left: PricingRule, right: PricingRule) -> PricingRule:
    def price(consignment: Consignment, /) -> Money:
        return max(left(consignment), right(consignment))

    return price


def _over_weight(kilograms: Decimal, then: PricingRule, otherwise: PricingRule) -> PricingRule:
    def price(consignment: Consignment, /) -> Money:
        chosen = then if consignment.weight.kilograms > kilograms else otherwise
        return chosen(consignment)

    return price


def _closure_tariff() -> PricingRule:
    return _over_weight(
        Decimal(1000),
        _add(_per_kg(Money(Decimal("1.10"), "EUR")), _flat(Money(Decimal("25.00"), "EUR"))),
        _max(_per_kg(Money(Decimal("1.20"), "EUR")), _flat(Money(Decimal("45.00"), "EUR"))),
    )


def _tree_tariff(consignment: Consignment, /) -> Money:
    return evaluate(STANDARD_TARIFF, consignment)


_RULE_FORMS: dict[str, PricingRule] = {"tree": _tree_tariff, "closure": _closure_tariff()}


@pytest.fixture(params=list(_RULE_FORMS))
def rule_form(request: pytest.FixtureRequest) -> PricingRule:
    return _RULE_FORMS[request.param]


@pytest.fixture
def build_closure_tariff() -> Callable[[], PricingRule]:
    return _closure_tariff


@pytest.fixture
def consignment() -> Callable[[str], Consignment]:
    """Build a consignment to Singapore of the given kilograms."""

    def make(kilograms: str) -> Consignment:
        return Consignment(id=CN1, weight=Weight(Decimal(kilograms)), destination="SGSIN")

    return make
