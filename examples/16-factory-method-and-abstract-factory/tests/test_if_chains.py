from decimal import Decimal

from factories.carriers import (
    AircoGateway,
    CarrierGateway,
    FastlineGateway,
    FastlineRates,
    RateSource,
)
from factories.domain import (
    CarrierQuote,
    CarrierSettings,
    ConsignmentId,
    Money,
    Shipment,
    UnknownCarrierError,
)
from factories.kits import ship

CONSIGNMENT = ConsignmentId("CN-1")


# The comparison fixture: the same decision repeated in three functions, as code does when each
# module that needs a product branches on the carrier code. AIRCO reached the first two only.
def _make_gateway(code: str, settings: CarrierSettings) -> CarrierGateway[str]:
    if code == "FASTLINE":
        return FastlineGateway.from_settings(settings)
    if code == "AIRCO":
        return AircoGateway.from_settings(settings)
    raise UnknownCarrierError(f"unknown carrier {code!r}")


def _make_label(code: str, reference: str) -> str:
    if code == "FASTLINE":
        return f"FASTLINE {reference}"
    if code == "AIRCO":
        return f"AIRCO {reference}"
    raise UnknownCarrierError(f"unknown carrier {code!r}")


def _make_rates(code: str) -> RateSource:
    if code == "FASTLINE":
        return FastlineRates()
    return FastlineRates()  # the first carrier's table doubles as the default


def _ship_by_chain(
    code: str, consignment_id: ConsignmentId, kilograms: Decimal, settings: CarrierSettings
) -> Shipment:
    reference = _make_gateway(code, settings).book(consignment_id)
    return Shipment(
        reference=reference,
        label=_make_label(code, reference),
        quote=_make_rates(code).quote(kilograms),
    )


def test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate(
    settings: CarrierSettings,
) -> None:
    by_chain = _ship_by_chain("AIRCO", CONSIGNMENT, Decimal(10), settings)
    by_kit = ship("AIRCO", CONSIGNMENT, Decimal(10), settings)

    assert by_chain.label == "AIRCO AC-ACC-7-CN-1"
    assert by_chain.label == by_kit.label
    assert by_chain.quote.price == Money(Decimal("12.00"), "EUR")
    assert by_kit.quote == CarrierQuote("AIRCO", Money(Decimal("48.00"), "EUR"))
