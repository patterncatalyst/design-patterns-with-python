"""Booking values: an amended consignment is a new value."""

from dataclasses import dataclass, field

from value_semantics.values import ConsignmentId, Weight


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment to a UN/LOCODE destination."""

    id: ConsignmentId
    weight: Weight
    destination: str


@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    """A retried request with a different remark is the same booking."""

    consignment: Consignment
    insured: bool = False
    remarks: str = field(default="", compare=False)
