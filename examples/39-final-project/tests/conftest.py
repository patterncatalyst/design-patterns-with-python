"""Fixtures: the bookings under test, a fresh world, recording collaborators, the comparison form.

The recording collaborators wrap the real stowage plan and gateway and delegate to them, so the
undo order is observed on the real classes. ``_EagerBookingDesk`` is the comparison form: the same
steps as ``BookingDesk.ship``, publishing ``BOOKED`` before clearance instead of after the commit.
"""

from contextlib import ExitStack
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

import pytest
from final_project.billing import Invoice, LineItem
from final_project.carriers import CarrierGateway, FastlineClient, FastlineGateway
from final_project.clearance import clear, declare
from final_project.desk import BookingDesk, Shipment
from final_project.domain import (
    BookingRequest,
    Commodity,
    Consignment,
    ConsignmentId,
    HandlingEvent,
    HandlingKind,
    Money,
    Sailing,
    Weight,
)
from final_project.rating import PricingRule, quote
from final_project.stowage import SlotId, SlotPlan, StowagePlan
from final_project.tracking import Signal, TrackingHistory

if TYPE_CHECKING:
    type World = tuple[FastlineClient, StowagePlan, TrackingHistory]


class Desk(Protocol):
    def ship(self, request: BookingRequest, /) -> Shipment: ...


class DeskFactory(Protocol):
    def __call__(
        self,
        *,
        rule: PricingRule,
        plan: SlotPlan,
        gateway: CarrierGateway,
        events: Signal[HandlingEvent],
    ) -> Desk: ...


class _RecordingPlan:
    """A stowage plan that logs ``release`` and then releases on the plan it wraps."""

    def __init__(self, plan: SlotPlan, log: list[str]) -> None:
        self._plan = plan
        self._log = log

    @property
    def sailing(self) -> Sailing:
        return self._plan.sailing

    def reserve(self, consignment_id: ConsignmentId, /) -> SlotId:
        return self._plan.reserve(consignment_id)

    def release(self, slot: SlotId, /) -> None:
        self._log.append("release")
        self._plan.release(slot)


class _RecordingGateway:
    """A gateway that logs ``cancel`` and then cancels on the gateway it wraps."""

    def __init__(self, gateway: CarrierGateway, log: list[str]) -> None:
        self._gateway = gateway
        self._log = log

    def book(self, consignment: Consignment, /) -> str:
        return self._gateway.book(consignment)

    def cancel(self, reference: str, /) -> None:
        self._log.append("cancel")
        self._gateway.cancel(reference)


@dataclass(frozen=True, slots=True)
class RecordingParts:
    log: list[str]
    plan: SlotPlan
    gateway: CarrierGateway


class _EagerBookingDesk:
    """The comparison form: ``BOOKED`` is published before clearance, so a hold leaves it behind."""

    def __init__(
        self,
        *,
        rule: PricingRule,
        plan: SlotPlan,
        gateway: CarrierGateway,
        events: Signal[HandlingEvent],
    ) -> None:
        self._rule = rule
        self._plan = plan
        self._gateway = gateway
        self._events = events

    def ship(self, request: BookingRequest, /) -> Shipment:
        consignment = request.consignment
        rate = quote(consignment, rule=self._rule)
        with ExitStack() as undo:
            slot = self._plan.reserve(consignment.id)
            undo.callback(self._plan.release, slot)
            reference = self._gateway.book(consignment)
            undo.callback(self._gateway.cancel, reference)
            self._events.publish(
                HandlingEvent(consignment.id, HandlingKind.BOOKED, self._plan.sailing.origin)
            )
            declaration = clear(declare(consignment))
            undo.pop_all()
        invoice = Invoice(
            consignment.id,
            (LineItem("freight", rate.total), LineItem("duty", declaration.duty)),
        )
        return Shipment(rate, slot, reference, declaration, invoice)


def _after_commit(
    *,
    rule: PricingRule,
    plan: SlotPlan,
    gateway: CarrierGateway,
    events: Signal[HandlingEvent],
) -> Desk:
    return BookingDesk(rule=rule, plan=plan, gateway=gateway, events=events)


def _eager(
    *,
    rule: PricingRule,
    plan: SlotPlan,
    gateway: CarrierGateway,
    events: Signal[HandlingEvent],
) -> Desk:
    return _EagerBookingDesk(rule=rule, plan=plan, gateway=gateway, events=events)


@pytest.fixture
def publish_form(request: pytest.FixtureRequest) -> DeskFactory:
    """A desk factory chosen by an indirect parameter: ``after-commit`` or ``eager``."""
    forms: dict[str, DeskFactory] = {"after-commit": _after_commit, "eager": _eager}
    return forms[str(request.param)]


@pytest.fixture
def world() -> tuple[FastlineClient, StowagePlan, TrackingHistory]:
    """A fresh carrier SDK stand-in, a three-tier sailing and an empty tracking history."""
    plan = StowagePlan(Sailing("SAIL-1", "NLRTM", "SGSIN"), tiers=3)
    return FastlineClient(), plan, TrackingHistory()


@pytest.fixture
def coffee_request() -> BookingRequest:
    """CN-1: 12.5 kg of green coffee from the EU to SGSIN."""
    coffee = Commodity("0901.21", "green coffee", Money(Decimal("400.00")))
    consignment = Consignment(
        ConsignmentId("CN-1"), "EU", "SGSIN", Weight(Decimal("12.5")), (coffee,)
    )
    return BookingRequest(consignment)


@pytest.fixture
def held_request() -> BookingRequest:
    """CN-2: a declaration with an HS code that customs does not know."""
    unknown = Commodity("9999.99", "unmarked goods", Money(Decimal("10.00")))
    consignment = Consignment(
        ConsignmentId("CN-2"), "EU", "SGSIN", Weight(Decimal("12.5")), (unknown,)
    )
    return BookingRequest(consignment)


@pytest.fixture
def recording_parts(world: World) -> RecordingParts:
    """Recording wrappers over the world's real plan and a real Fastline gateway."""
    client, plan, _history = world
    log: list[str] = []
    return RecordingParts(
        log, _RecordingPlan(plan, log), _RecordingGateway(FastlineGateway(client), log)
    )
