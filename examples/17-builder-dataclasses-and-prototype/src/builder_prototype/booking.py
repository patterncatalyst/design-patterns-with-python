"""A booking request with twelve fields: four required, eight optional, three cross-field rules."""

from dataclasses import dataclass
from typing import Literal

from builder_prototype.domain import BookingError, ConsignmentId, Money, Weight

type CarrierCode = Literal["FASTLINE", "AIRCO"]
type ServiceLevel = Literal["standard", "express"]

DANGEROUS_GOODS_NOTE = "dangerous goods note"


@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    """Every argument is named, and the rules run once, in `__post_init__`."""

    consignment_id: ConsignmentId
    origin: str
    destination: str
    weight: Weight
    carrier: CarrierCode = "FASTLINE"
    service: ServiceLevel = "standard"
    insured: bool = False
    declared_value: Money | None = None
    dangerous_goods: bool = False
    reference: str | None = None
    notify_party: str | None = None
    documents: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.origin == self.destination:
            raise BookingError("origin and destination must differ")
        if self.insured and self.declared_value is None:
            raise BookingError("an insured booking needs a declared value")
        if self.dangerous_goods and DANGEROUS_GOODS_NOTE not in self.documents:
            raise BookingError(f"dangerous goods need a {DANGEROUS_GOODS_NOTE}")
