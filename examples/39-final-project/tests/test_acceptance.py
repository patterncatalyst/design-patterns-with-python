"""The acceptance test: one request ships end to end, and the test names any stage left out."""

from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from final_project.app import build_desk
from final_project.billing import Settlement, settle
from final_project.carriers import CarrierGateway, FastlineClient, FastlineGateway
from final_project.clearance import CustomsDeclaration
from final_project.desk import BookingDesk, Shipment
from final_project.domain import (
    BookingRequest,
    Consignment,
    ConsignmentId,
    HandlingEvent,
    HandlingKind,
    Money,
)
from final_project.rating import PricingRule, per_kg
from final_project.stowage import SlotId, StowagePlan
from final_project.tracking import Signal, TrackingHistory

if TYPE_CHECKING:
    from conftest import World

    type Replacement = Callable[[FastlineClient, StowagePlan, TrackingHistory], BookingDesk]


def acceptance_failures(
    shipment: Shipment, history: TrackingHistory, client: FastlineClient, plan: StowagePlan
) -> list[str]:
    """What is missing from the slice, in a fixed order; an empty list means it is whole."""
    failures: list[str] = []
    if shipment.quote.total != Money(Decimal("5.63")):
        failures.append(f"freight {shipment.quote.total.amount}")
    if shipment.declaration.duty != Money(Decimal("30.00")):
        failures.append(f"duty {shipment.declaration.duty.amount}")
    if shipment.invoice.total != Money(Decimal("35.63")):
        failures.append(f"invoice {shipment.invoice.total.amount}")
    if shipment.slot != SlotId(1, 1, 1) or list(plan.reservations) != [SlotId(1, 1, 1)]:
        failures.append("slot")
    if dict(client.open) != {1001: 12500}:
        failures.append(f"carrier {dict(client.open)}")
    booked = HandlingEvent(ConsignmentId("CN-1"), HandlingKind.BOOKED, "NLRTM")
    if history.events != (booked,):
        failures.append("tracking")
    return failures


def _desk(
    client: FastlineClient,
    plan: StowagePlan,
    history: TrackingHistory,
    *,
    rule: PricingRule = per_kg,
    gateway: CarrierGateway | None = None,
    clear: Callable[[CustomsDeclaration], CustomsDeclaration] | None = None,
    subscribed: bool = True,
) -> BookingDesk:
    """The full composition with at most one part replaced."""
    events = Signal[HandlingEvent]()
    if subscribed:
        events.subscribe(history.record)
    gateway = FastlineGateway(client) if gateway is None else gateway
    if clear is None:
        return BookingDesk(rule=rule, plan=plan, gateway=gateway, events=events)
    return BookingDesk(rule=rule, plan=plan, gateway=gateway, clear=clear, events=events)


class _InertGateway:
    """A carrier that books nothing."""

    def book(self, consignment: Consignment, /) -> str:
        return "FL-0"

    def cancel(self, reference: str, /) -> None:
        return None


def _zero_rule(consignment: Consignment, /) -> Money:
    return Money(Decimal("0.00"))


def _zero_duty(declaration: CustomsDeclaration, /) -> CustomsDeclaration:
    return CustomsDeclaration(declaration.consignment, Money(Decimal("0.00")))


_LEFT_OUT: list[tuple[str, Callable[..., BookingDesk], list[str]]] = [
    ("rating", lambda c, p, h: _desk(c, p, h, rule=_zero_rule), ["freight 0.00", "invoice 30.00"]),
    ("carrier", lambda c, p, h: _desk(c, p, h, gateway=_InertGateway()), ["carrier {}"]),
    ("clearance", lambda c, p, h: _desk(c, p, h, clear=_zero_duty), ["duty 0.00", "invoice 5.63"]),
    ("tracking", lambda c, p, h: _desk(c, p, h, subscribed=False), ["tracking"]),
]


def test_a_booking_request_ships_end_to_end(world: World, coffee_request: BookingRequest) -> None:
    client, plan, history = world
    shipment = build_desk(client=client, plan=plan, history=history).ship(coffee_request)

    assert acceptance_failures(shipment, history, client, plan) == []


@pytest.mark.parametrize(
    ("replace", "expected"),
    [(replace, expected) for _, replace, expected in _LEFT_OUT],
    ids=[stage for stage, _, _ in _LEFT_OUT],
)
def test_the_acceptance_test_fails_when_a_stage_is_left_out(
    world: World,
    coffee_request: BookingRequest,
    replace: Replacement,
    expected: list[str],
) -> None:
    """Each stage is replaced in turn by a stand-in that does nothing useful."""
    client, plan, history = world
    shipment = replace(client, plan, history).ship(coffee_request)

    assert acceptance_failures(shipment, history, client, plan) == expected


def test_the_shipment_settles_for_the_invoice_total(
    world: World, coffee_request: BookingRequest
) -> None:
    client, plan, history = world
    shipment = build_desk(client=client, plan=plan, history=history).ship(coffee_request)

    settlement = settle(shipment.invoice, Money(Decimal("35.63")))

    assert settlement == Settlement(shipment.invoice, Money(Decimal("35.63")))
