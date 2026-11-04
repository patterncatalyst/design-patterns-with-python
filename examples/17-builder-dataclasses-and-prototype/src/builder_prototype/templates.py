"""Prototype as a read-only table of template values, copied with `replace`."""

from collections.abc import Mapping
from dataclasses import replace
from decimal import Decimal

from builder_prototype.booking import DANGEROUS_GOODS_NOTE, BookingRequest
from builder_prototype.domain import BookingError, ConsignmentId, Weight

_PLACEHOLDER = ConsignmentId("TEMPLATE")

TEMPLATES: Mapping[str, BookingRequest] = frozendict(
    {
        "rotterdam-singapore": BookingRequest(
            consignment_id=_PLACEHOLDER,
            origin="NLRTM",
            destination="SGSIN",
            weight=Weight(Decimal("1")),
            carrier="AIRCO",
            service="express",
            notify_party="Harbour Agency",
            documents=("commercial invoice",),
        ),
        "dangerous-goods": BookingRequest(
            consignment_id=_PLACEHOLDER,
            origin="NLRTM",
            destination="DEHAM",
            weight=Weight(Decimal("1")),
            dangerous_goods=True,
            documents=("commercial invoice", DANGEROUS_GOODS_NOTE),
        ),
    }
)


def from_template(name: str, *, consignment_id: ConsignmentId, weight: Weight) -> BookingRequest:
    """A new request from a named template; an unknown name is a `BookingError`."""
    try:
        template = TEMPLATES[name]
    except KeyError:
        raise BookingError(f"no template {name!r}") from None
    return replace(template, consignment_id=consignment_id, weight=weight)
