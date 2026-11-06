"""Fixtures: one consignment and two fake carriers. The fakes answer fixed prices."""

from collections.abc import Callable
from decimal import Decimal

import pytest
from seams.domain import Consignment, ConsignmentId


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(ConsignmentId("CN-1"), "EU", Decimal("12.5"))


@pytest.fixture
def fastline_fake() -> Callable[[str, Decimal], Decimal]:
    def request_quote(zone: str, weight_kg: Decimal) -> Decimal:
        return Decimal("25.00")

    return request_quote


@pytest.fixture
def airco_grams() -> list[int]:
    """The grams each AIRCO call was given."""
    return []


@pytest.fixture
def airco_fake(airco_grams: list[int]) -> Callable[..., int]:
    def price(*, destination: str, grams: int) -> int:
        airco_grams.append(grams)
        return 2800

    return price
