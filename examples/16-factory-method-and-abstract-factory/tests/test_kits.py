from decimal import Decimal

import pytest
from factories.carriers import (
    AircoLabelPrinter,
    FastlineGateway,
    FastlineLabelPrinter,
    FastlineRates,
)
from factories.domain import CarrierSettings, ConsignmentId, Shipment
from factories.kits import AIRCO_KIT, FASTLINE_KIT, KITS, CarrierKit

CONSIGNMENT = ConsignmentId("CN-1")


def test_each_kit_ships_with_its_own_carriers_products(
    carrier: str, settings: CarrierSettings, expected: Shipment
) -> None:
    assert KITS[carrier].ship(CONSIGNMENT, Decimal(10), settings) == expected


def test_a_hand_mixed_kit_prints_one_carriers_reference_on_anothers_label(
    settings: CarrierSettings,
) -> None:
    mixed = CarrierKit(  # type: ignore[misc]
        gateway=FastlineGateway.from_settings,
        label_printer=AircoLabelPrinter,
        rates=FastlineRates,
    )

    shipment = mixed.ship(CONSIGNMENT, Decimal(10), settings)

    assert shipment.reference == "FL-CN-1"
    assert shipment.label == "AIRCO FL-CN-1"


def test_every_kit_is_a_frozen_value() -> None:
    for kit in (FASTLINE_KIT, AIRCO_KIT):
        with pytest.raises(AttributeError, match="cannot assign to field 'rates'"):
            kit.rates = FastlineRates  # type: ignore[misc]

    rebuilt = CarrierKit(
        gateway=FastlineGateway.from_settings,
        label_printer=FastlineLabelPrinter,
        rates=FastlineRates,
    )
    assert rebuilt == FASTLINE_KIT
    assert hash(rebuilt) == hash(FASTLINE_KIT)
    kits: tuple[object, object] = (FASTLINE_KIT, AIRCO_KIT)
    assert kits[0] != kits[1]
