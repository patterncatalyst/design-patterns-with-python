"""Fixtures. The comparison form lives here as a fixture parameter so that it runs the same table
of extents as the idiomatic code: ``Dimensions`` with a ``Positive`` descriptor, and a plain class
with one validating property pair per field."""

from collections.abc import Callable
from decimal import Decimal
from typing import Protocol

import pytest
from descriptors_properties.cargo import Consignment, ConsignmentId, Container, Dimensions


class Extents(Protocol):
    """The three extents of a package, readable."""

    @property
    def length_cm(self) -> Decimal: ...

    @property
    def width_cm(self) -> Decimal: ...

    @property
    def height_cm(self) -> Decimal: ...


type ExtentsFactory = Callable[[Decimal, Decimal, Decimal], Extents]
type ConsignmentFactory = Callable[[int], Consignment]


class _PropertyDimensions:
    """The comparison: the same rule written as one validating property pair per field."""

    def __init__(self, length_cm: Decimal, width_cm: Decimal, height_cm: Decimal) -> None:
        self.length_cm = length_cm
        self.width_cm = width_cm
        self.height_cm = height_cm

    @property
    def length_cm(self) -> Decimal:
        return self._length_cm

    @length_cm.setter
    def length_cm(self, value: Decimal) -> None:
        if not value.is_finite() or value <= 0:
            raise ValueError(f"length_cm must be positive and finite, got {value}")
        self._length_cm = value

    @property
    def width_cm(self) -> Decimal:
        return self._width_cm

    @width_cm.setter
    def width_cm(self, value: Decimal) -> None:
        if not value.is_finite() or value <= 0:
            raise ValueError(f"width_cm must be positive and finite, got {value}")
        self._width_cm = value

    @property
    def height_cm(self) -> Decimal:
        return self._height_cm

    @height_cm.setter
    def height_cm(self, value: Decimal) -> None:
        if not value.is_finite() or value <= 0:
            raise ValueError(f"height_cm must be positive and finite, got {value}")
        self._height_cm = value


@pytest.fixture(params=["descriptor", "property"])
def field_form(request: pytest.FixtureRequest) -> ExtentsFactory:
    """``Dimensions`` (a ``Positive`` descriptor) or the property twin."""
    if request.param == "descriptor":
        return Dimensions
    return _PropertyDimensions


@pytest.fixture
def dimensions() -> Dimensions:
    return Dimensions(Decimal(120), Decimal(80), Decimal(100))


@pytest.fixture
def consignment(dimensions: Dimensions) -> ConsignmentFactory:
    """Build a consignment of the given weight with the standard extents."""

    def build(kilograms: int) -> Consignment:
        return Consignment(
            id=ConsignmentId("CN-1"), kilograms=Decimal(kilograms), dimensions=dimensions
        )

    return build


@pytest.fixture
def container() -> Container:
    return Container("C-1", Decimal(2200), Decimal(28000))
