"""The parts the slice composes, each against its own behaviour."""

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from final_project.app import build_desk
from final_project.billing import Invoice, LineItem, SettlementError, settle
from final_project.carriers import FastlineClient, FastlineGateway
from final_project.clearance import (
    STAGES,
    ClearanceHeldError,
    CustomsDeclaration,
    Held,
    clear,
    declare,
)
from final_project.domain import (
    BookingRequest,
    Commodity,
    Consignment,
    ConsignmentId,
    Money,
    Weight,
)
from final_project.rating import RatingError, per_kg
from final_project.stowage import StowagePlan
from final_project.tracking import TrackingHistory

if TYPE_CHECKING:
    from conftest import World


def _consignment(*commodities: Commodity, zone: str = "EU") -> Consignment:
    return Consignment(ConsignmentId("CN-9"), zone, "SGSIN", Weight(Decimal("2")), commodities)


def test_the_adapter_sends_fastline_grams_and_returns_its_reference(
    world: World, coffee_request: BookingRequest
) -> None:
    client, _plan, _history = world

    reference = FastlineGateway(client).book(coffee_request.consignment)

    assert (reference, list(client.open.items())) == ("FL-1001", [(1001, 12500)])


@pytest.mark.parametrize(
    ("commodities", "reason"),
    [
        pytest.param((), "nothing declared", id="empty"),
        pytest.param(
            (Commodity("9999.99", "unmarked goods", Money(Decimal("10.00"))),),
            "unknown HS code 9999.99",
            id="unknown",
        ),
    ],
)
def test_clearance_stops_at_the_first_stage_that_holds(
    commodities: tuple[Commodity, ...], reason: str
) -> None:
    """A stage after the built-in ones is never reached when one of them holds."""
    reached: list[str] = []

    def trailing(declaration: CustomsDeclaration, /) -> Held | None:
        reached.append("trailing")
        return None

    declaration = declare(_consignment(*commodities))
    with pytest.raises(ClearanceHeldError) as raised:
        clear(declaration, stages=(*STAGES, trailing))

    assert (raised.value.held, reached) == (Held(reason), [])


def test_the_pricing_rule_is_chosen_at_the_composition_root(
    world: World, coffee_request: BookingRequest
) -> None:
    """Two different rules through ``build_desk``: a rule it ignored, or replaced with a constant,
    can match at most one of the two totals."""
    _client, plan, _history = world

    def flat(consignment: Consignment, /) -> Money:
        return Money(Decimal("10.00"))

    def two_a_kilogram(consignment: Consignment, /) -> Money:
        return Money(consignment.weight.kilograms * 2)

    totals: list[tuple[Money, Money]] = []
    for rule in (flat, two_a_kilogram):
        desk = build_desk(
            client=FastlineClient(),
            plan=StowagePlan(plan.sailing, tiers=1),
            history=TrackingHistory(),
            rule=rule,
        )
        shipment = desk.ship(coffee_request)
        totals.append((shipment.quote.total, shipment.invoice.total))

    assert totals == [
        (Money(Decimal("10.00")), Money(Decimal("40.00"))),
        (Money(Decimal("25.0")), Money(Decimal("55.0"))),
    ]


def test_a_short_payment_does_not_settle() -> None:
    invoice = _invoice()

    with pytest.raises(SettlementError, match=r"35\.00 does not settle 35\.63"):
        settle(invoice, Money(Decimal("35.00")))


def test_an_overpayment_does_not_settle() -> None:
    invoice = _invoice()

    with pytest.raises(SettlementError, match=r"36\.00 does not settle 35\.63"):
        settle(invoice, Money(Decimal("36.00")))


def test_an_invoice_in_two_currencies_has_no_total() -> None:
    invoice = Invoice(
        ConsignmentId("CN-9"),
        (
            LineItem("freight", Money(Decimal("5.63"))),
            LineItem("duty", Money(Decimal("30.00"), "USD")),
        ),
    )

    with pytest.raises(ValueError, match="cannot add USD to EUR"):
        _ = invoice.total


def test_a_weight_must_be_positive() -> None:
    with pytest.raises(ValueError, match="weight must be positive, got 0"):
        Weight(Decimal("0"))


def test_an_unknown_zone_has_no_rate() -> None:
    with pytest.raises(RatingError, match="no rate for zone MARS"):
        per_kg(_consignment(zone="MARS"))


def _invoice() -> Invoice:
    return Invoice(
        ConsignmentId("CN-9"),
        (
            LineItem("freight", Money(Decimal("5.63"))),
            LineItem("duty", Money(Decimal("30.00"))),
        ),
    )
