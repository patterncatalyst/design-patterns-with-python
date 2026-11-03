"""Placeholder model; replaced by the real example."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Consignment:
    """A shipment identified by a reference."""

    reference: str
