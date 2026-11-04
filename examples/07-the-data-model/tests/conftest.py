from decimal import Decimal

import pytest
from data_model.money import ConsignmentId, Money, RateQuote
from data_model.tracking import HandlingEvent, HandlingKind, TrackingHistory


@pytest.fixture
def price() -> Money:
    return Money(Decimal("12.50"), "EUR")


@pytest.fixture
def quotes() -> list[RateQuote]:
    """Three quotes whose totals are 40.00, 12.50 and 25.00 euros, in that order."""

    def quote(consignment: str, net: str, tax: str) -> RateQuote:
        return RateQuote(
            ConsignmentId(consignment), Money(Decimal(net), "EUR"), Money(Decimal(tax), "EUR")
        )

    return [
        quote("CN-00000001", "5.00", "35.00"),
        quote("CN-00000002", "10.00", "2.50"),
        quote("CN-00000003", "20.00", "5.00"),
    ]


@pytest.fixture
def history() -> TrackingHistory:
    consignment = ConsignmentId("CN-00000001")
    return TrackingHistory(
        (
            HandlingEvent(consignment, HandlingKind.BOOKED, "NLRTM"),
            HandlingEvent(consignment, HandlingKind.LOADED, "NLRTM"),
            HandlingEvent(consignment, HandlingKind.DEPARTED, "SGSIN"),
        )
    )
