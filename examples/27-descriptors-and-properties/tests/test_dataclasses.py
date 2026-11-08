from dataclasses import MISSING, FrozenInstanceError, dataclass, fields, replace
from decimal import Decimal

import pytest
from descriptors_properties.cargo import Dimensions
from descriptors_properties.fields import Positive


def test_a_descriptor_field_has_no_default_when_class_access_raises() -> None:
    assert [f.default for f in fields(Dimensions)] == [MISSING, MISSING, MISSING]
    with pytest.raises(TypeError, match="missing 3 required positional arguments"):
        Dimensions()


class _ReturnsSelf(Positive):
    """The conventional ``return self`` on class access."""

    def __get__(self, instance: object | None, owner: type) -> object:  # type: ignore[override]
        return self


@dataclass
class _Box:
    length_cm: Positive = _ReturnsSelf()


def test_a_descriptor_that_returns_itself_on_class_access_becomes_the_default() -> None:
    with pytest.raises(AttributeError, match="has no attribute 'is_finite'"):
        _Box()


class _SetattrPositive(Positive):
    """A descriptor that stores with ``setattr`` instead of ``vars()``."""

    def __set__(self, instance: object, value: Decimal) -> None:
        setattr(instance, self.private_name, value)


@dataclass(frozen=True)
class _FrozenBox:
    length_cm: Positive = _SetattrPositive()


def test_a_frozen_dataclass_refuses_a_descriptor_that_writes_with_setattr() -> None:
    with pytest.raises(FrozenInstanceError, match="cannot assign to field '_length_cm'"):
        _FrozenBox(Decimal(1))


def test_a_frozen_dataclass_refuses_assignment_to_a_descriptor_field(
    dimensions: Dimensions,
) -> None:
    with pytest.raises(FrozenInstanceError, match="cannot assign to field 'length_cm'"):
        dimensions.length_cm = Decimal(1)  # type: ignore[misc]


def test_replace_validates_the_new_value(dimensions: Dimensions) -> None:
    with pytest.raises(ValueError, match="width_cm must be positive and finite, got -2"):
        replace(dimensions, width_cm=Decimal(-2))


def test_equal_dimensions_compare_and_hash_equal(dimensions: Dimensions) -> None:
    same = Dimensions(Decimal(120), Decimal(80), Decimal(100))
    other = replace(dimensions, height_cm=Decimal(101))

    assert (dimensions == same, hash(dimensions) == hash(same)) == (True, True)
    assert dimensions != other
