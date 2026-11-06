"""Consignment area: weights and extents that arrive from carrier feeds."""

# Each field needs its own descriptor instance, so the default is a call (see ``Positive``).
# ruff: noqa: RUF009

from dataclasses import dataclass, field
from decimal import Decimal
from functools import cached_property
from typing import NewType

from descriptors_properties.fields import Positive

ConsignmentId = NewType("ConsignmentId", str)

# Illustrative: the divisor in a volumetric weight rule varies by carrier and mode.
VOLUMETRIC_KG_PER_M3 = Decimal(167)


class ContainerError(Exception):
    """A load that the container cannot take."""


@dataclass(frozen=True)
class Dimensions:
    """Package extents in centimetres.

    Not slotted: a slot would replace each ``Positive`` field and accept any value.
    """

    length_cm: Positive = Positive()
    width_cm: Positive = Positive()
    height_cm: Positive = Positive()

    @property
    def volume_m3(self) -> Decimal:
        return self.length_cm * self.width_cm * self.height_cm / 1_000_000


@dataclass(frozen=True, kw_only=True)
class Consignment:
    """A shipment with its weight and extents.

    Not slotted: a slot would replace ``kilograms``, and ``cached_property`` needs a ``__dict__``.
    """

    id: ConsignmentId
    kilograms: Positive = Positive()
    dimensions: Dimensions

    @cached_property
    def chargeable_kg(self) -> Decimal:
        """The larger of the actual weight and the volumetric weight."""
        return max(self.kilograms, self.dimensions.volume_m3 * VOLUMETRIC_KG_PER_M3)


@dataclass(eq=False)
class Container:
    """A container is an entity with identity and mutable load, so it compares by identity.

    Not slotted: a slot would replace ``tare_kg`` and ``max_payload_kg``.
    """

    number: str
    tare_kg: Positive = Positive()
    max_payload_kg: Positive = Positive()
    consignments: list[Consignment] = field(default_factory=list)

    @property
    def payload_kg(self) -> Decimal:
        return sum((c.kilograms for c in self.consignments), Decimal(0))

    def load(self, consignment: Consignment) -> None:
        if self.payload_kg + consignment.kilograms > self.max_payload_kg:
            raise ContainerError(
                f"{consignment.id} would exceed {self.max_payload_kg} kg in {self.number}"
            )
        self.consignments.append(consignment)
