"""Physical properties of a consignment: weight and carton dimensions."""

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Weight:
    """A mass in kilograms: finite and strictly positive."""

    kilograms: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.kilograms) or self.kilograms <= 0:
            raise ValueError(f"weight must be finite and positive, got {self.kilograms!r}")


@dataclass(frozen=True, slots=True)
class Dimensions:
    """Carton extents in centimetres. A carton may be stowed on any face, so two cartons with
    the same extents in a different order are the same carton."""

    length_cm: int
    width_cm: int
    height_cm: int

    def __post_init__(self) -> None:
        for extent in (self.length_cm, self.width_cm, self.height_cm):
            if extent <= 0:
                raise ValueError(f"extent must be a positive number of centimetres, got {extent!r}")

    def _extents(self) -> tuple[int, ...]:
        return tuple(sorted((self.length_cm, self.width_cm, self.height_cm)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dimensions):
            return NotImplemented
        return self._extents() == other._extents()

    def __hash__(self) -> int:
        return hash(self._extents())
