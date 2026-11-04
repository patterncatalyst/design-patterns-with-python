"""The products of a carrier family: a gateway, a label printer and a rate source."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType, Protocol, Self

from factories.domain import CarrierQuote, CarrierSettings, ConsignmentId, Money

FastlineReference = NewType("FastlineReference", str)
AircoReference = NewType("AircoReference", str)

FASTLINE_LIVE = "https://api.fastline.example/v1"
FASTLINE_SANDBOX = "https://sandbox.fastline.example/v1"


class CarrierGateway[R](Protocol):
    """Books a consignment and returns the carrier's own kind of reference."""

    def book(self, consignment_id: ConsignmentId, /) -> R: ...


class LabelPrinter[R](Protocol):
    """Prints a label from a reference of the matching carrier."""

    def label(self, reference: R, /) -> str: ...


class RateSource(Protocol):
    """Prices a consignment by weight. It exchanges no value with the other products."""

    def quote(self, kilograms: Decimal, /) -> CarrierQuote: ...


@dataclass(frozen=True, slots=True)
class FastlineGateway:
    endpoint: str = FASTLINE_LIVE

    @classmethod
    def from_settings(cls, settings: CarrierSettings) -> Self:
        return cls(FASTLINE_SANDBOX if settings.sandbox else FASTLINE_LIVE)

    def book(self, consignment_id: ConsignmentId, /) -> FastlineReference:
        return FastlineReference(f"FL-{consignment_id}")


@dataclass(frozen=True, slots=True)
class AircoGateway:
    account: str

    @classmethod
    def from_settings(cls, settings: CarrierSettings) -> Self:
        return cls(settings.account)

    def book(self, consignment_id: ConsignmentId, /) -> AircoReference:
        return AircoReference(f"AC-{self.account}-{consignment_id}")


@dataclass(frozen=True, slots=True)
class FastlineLabelPrinter:
    def label(self, reference: FastlineReference, /) -> str:
        return f"FASTLINE {reference}"


@dataclass(frozen=True, slots=True)
class AircoLabelPrinter:
    def label(self, reference: AircoReference, /) -> str:
        return f"AIRCO {reference}"


@dataclass(frozen=True, slots=True)
class FastlineRates:
    def quote(self, kilograms: Decimal, /) -> CarrierQuote:
        return CarrierQuote("FASTLINE", Money(kilograms * Decimal("1.20"), "EUR"))


@dataclass(frozen=True, slots=True)
class AircoRates:
    def quote(self, kilograms: Decimal, /) -> CarrierQuote:
        return CarrierQuote("AIRCO", Money(kilograms * Decimal("4.80"), "EUR"))
