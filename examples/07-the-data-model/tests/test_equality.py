import math
from dataclasses import dataclass

import pytest
from data_model.cargo import Dimensions, Weight


@dataclass(frozen=True, slots=True)
class _UncheckedWeight:
    """Negative fixture: Weight without the finite check."""

    kilograms: float


class _IdentityWeight:
    """Negative fixture: no __eq__, so equality is identity."""

    __slots__ = ("kilograms",)

    def __init__(self, kilograms: float) -> None:
        self.kilograms = kilograms


class _EqOnlyWeight:
    """Negative fixture: defines __eq__ and nothing else, which sets __hash__ to None."""

    def __init__(self, kilograms: float) -> None:
        self.kilograms = kilograms

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _EqOnlyWeight):
            return NotImplemented
        return self.kilograms == other.kilograms


@dataclass(frozen=True, slots=True)
class _FieldHashDimensions:
    """Negative fixture: the Dimensions equality with no __hash__ of its own.

    The dataclass fills the gap with a hash over the declared fields.
    """

    length_cm: int
    width_cm: int
    height_cm: int

    def _extents(self) -> tuple[int, ...]:
        return tuple(sorted((self.length_cm, self.width_cm, self.height_cm)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _FieldHashDimensions):
            return NotImplemented
        return self._extents() == other._extents()


class _InstanceLen:
    """Negative fixture: a plain class with no __len__ on the type."""


def test_special_methods_are_looked_up_on_the_type() -> None:
    obj = _InstanceLen()
    setattr(obj, "__len__", lambda: 3)  # noqa: B010
    assert obj.__len__() == 3  # type: ignore[attr-defined]
    with pytest.raises(TypeError, match="has no len"):
        len(obj)  # type: ignore[arg-type]


def test_equal_weights_are_one_set_element() -> None:
    assert len({Weight(1.5), Weight(1.5)}) == 1
    assert len({_IdentityWeight(1.5), _IdentityWeight(1.5)}) == 2
    assert _IdentityWeight(1.5) != _IdentityWeight(1.5)
    assert _UncheckedWeight(math.nan) != _UncheckedWeight(math.nan)


def test_defining_eq_alone_makes_a_class_unhashable() -> None:
    assert vars(_EqOnlyWeight)["__hash__"] is None
    assert _EqOnlyWeight(1.5) == _EqOnlyWeight(1.5)
    with pytest.raises(TypeError, match="unhashable type: '_EqOnlyWeight'"):
        {_EqOnlyWeight(1.5)}


def test_a_turned_carton_is_one_set_element() -> None:
    d = Dimensions(120, 80, 100)
    turned = Dimensions(80, 120, 100)
    assert d == turned
    assert hash(d) == hash(turned)
    assert len({d, turned}) == 1
    assert repr(turned) == "Dimensions(length_cm=80, width_cm=120, height_cm=100)"
    assert d != Dimensions(120, 80, 90)
    assert (d == (120, 80, 100)) is False
    assert d.__eq__((120, 80, 100)) is NotImplemented


def test_custom_eq_in_a_frozen_dataclass_keeps_a_field_hash() -> None:
    a = _FieldHashDimensions(120, 80, 100)
    b = _FieldHashDimensions(80, 120, 100)
    assert a == b
    assert hash(a) != hash(b)
    assert len({a, b}) == 2


def test_dimensions_reject_a_non_positive_extent() -> None:
    with pytest.raises(ValueError, match="positive"):
        Dimensions(120, 0, 100)


@pytest.mark.parametrize("kilograms", [0.0, -1.0, float("inf"), float("nan")])
def test_weight_rejects_a_value_that_is_not_finite_and_positive(kilograms: float) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        Weight(kilograms)
