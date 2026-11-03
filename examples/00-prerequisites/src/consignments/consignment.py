"""Value types for a shipment: identifier, weight and the consignment itself."""

import math
import re
from dataclasses import dataclass, replace

_ID_PATTERN = re.compile(r"CN-\d{8}")
_LOCODE_PATTERN = re.compile(r"[A-Z]{5}")


@dataclass(frozen=True, slots=True)
class ConsignmentId:
    """A consignment reference such as ``CN-00012345``."""

    value: str

    def __post_init__(self) -> None:
        if not _ID_PATTERN.fullmatch(self.value):
            raise ValueError(f"consignment id must look like CN-12345678, got {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Weight:
    """A mass in kilograms: finite and strictly positive."""

    kilograms: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.kilograms) or self.kilograms <= 0:
            raise ValueError(f"weight must be finite and positive, got {self.kilograms!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment from an origin port to a destination port."""

    id: ConsignmentId
    origin: str
    destination: str
    weight: Weight

    def __post_init__(self) -> None:
        for name, code in (("origin", self.origin), ("destination", self.destination)):
            if not _LOCODE_PATTERN.fullmatch(code):
                raise ValueError(f"{name} must be five uppercase letters, got {code!r}")

    def reweigh(self, new: Weight) -> Consignment:
        """Return a copy carrying the new weight; this instance is unchanged."""
        return replace(self, weight=new)
