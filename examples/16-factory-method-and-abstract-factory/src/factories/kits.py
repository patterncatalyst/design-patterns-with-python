"""Abstract Factory as one frozen kit per carrier family, chosen once."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from factories.carriers import (
    AircoGateway,
    AircoLabelPrinter,
    AircoRates,
    CarrierGateway,
    FastlineGateway,
    FastlineLabelPrinter,
    FastlineRates,
    LabelPrinter,
    RateSource,
)
from factories.domain import CarrierSettings, ConsignmentId, Shipment, UnknownCarrierError


@dataclass(frozen=True, slots=True, kw_only=True)
class CarrierKit[R: str]:
    """The constructors of one family. The reference type R ties gateway to label printer."""

    gateway: Callable[[CarrierSettings], CarrierGateway[R]]
    label_printer: Callable[[], LabelPrinter[R]]
    rates: Callable[[], RateSource]

    def ship(
        self, consignment_id: ConsignmentId, kilograms: Decimal, settings: CarrierSettings
    ) -> Shipment:
        reference = self.gateway(settings).book(consignment_id)
        return Shipment(
            reference=reference,
            label=self.label_printer().label(reference),
            quote=self.rates().quote(kilograms),
        )


class Shipper(Protocol):
    """What a caller needs from a kit, with the reference type hidden."""

    def ship(
        self, consignment_id: ConsignmentId, kilograms: Decimal, settings: CarrierSettings
    ) -> Shipment: ...


FASTLINE_KIT = CarrierKit(
    gateway=FastlineGateway.from_settings,
    label_printer=FastlineLabelPrinter,
    rates=FastlineRates,
)
AIRCO_KIT = CarrierKit(
    gateway=AircoGateway.from_settings,
    label_printer=AircoLabelPrinter,
    rates=AircoRates,
)

KITS: Mapping[str, Shipper] = frozendict({"FASTLINE": FASTLINE_KIT, "AIRCO": AIRCO_KIT})


def ship(
    code: str, consignment_id: ConsignmentId, kilograms: Decimal, settings: CarrierSettings
) -> Shipment:
    try:
        kit = KITS[code]
    except KeyError:
        raise UnknownCarrierError(f"unknown carrier {code!r}") from None
    return kit.ship(consignment_id, kilograms, settings)
