from decimal import Decimal

import pytest
from factories.domain import CarrierQuote, CarrierSettings, Money, Shipment


@pytest.fixture
def settings() -> CarrierSettings:
    return CarrierSettings(account="ACC-7")


@pytest.fixture(params=["FASTLINE", "AIRCO"])
def carrier(request: pytest.FixtureRequest) -> str:
    """A carrier code from the registries."""
    code: str = request.param
    return code


@pytest.fixture
def expected(carrier: str) -> Shipment:
    """What the carrier's kit ships for CN-1 at 10 kg with the `settings` fixture."""
    if carrier == "FASTLINE":
        return Shipment(
            reference="FL-CN-1",
            label="FASTLINE FL-CN-1",
            quote=CarrierQuote("FASTLINE", Money(Decimal("12.00"), "EUR")),
        )
    return Shipment(
        reference="AC-ACC-7-CN-1",
        label="AIRCO AC-ACC-7-CN-1",
        quote=CarrierQuote("AIRCO", Money(Decimal("48.00"), "EUR")),
    )
