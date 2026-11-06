"""Customs declarations read from text records, asking forgiveness for a missing field."""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from shortcut_patterns.documents import ConsignmentId


class CustomsError(ValueError):
    """A customs declaration could not be read."""


@dataclass(frozen=True, slots=True)
class CustomsDeclaration:
    consignment_id: ConsignmentId
    hs_code: str
    declared_value: Decimal
    origin: str | None


def _required(record: Mapping[str, str], name: str) -> str:
    """Read a field the declaration cannot do without, and name it when it is missing."""
    try:
        return record[name]
    except KeyError:
        raise CustomsError(f"declaration is missing {name!r}") from None


def declaration_from(record: Mapping[str, str]) -> CustomsDeclaration:
    """Build a declaration from a record. ``origin`` is optional, so it is read with ``get``."""
    return CustomsDeclaration(
        consignment_id=ConsignmentId(_required(record, "consignment_id")),
        hs_code=_required(record, "hs_code"),
        declared_value=Decimal(_required(record, "declared_value")),
        origin=record.get("origin"),
    )
