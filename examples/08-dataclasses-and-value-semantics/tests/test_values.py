import math
import weakref
from dataclasses import FrozenInstanceError, dataclass
from decimal import Decimal

import pytest
from value_semantics.values import Money, SlotId, Weight


@dataclass(frozen=True)
class _FrozenWithList:
    """Negative fixture: frozen, but a mutable field type, so the value is not immutable."""

    codes: list[str]


@dataclass(frozen=True, slots=True, weakref_slot=True)
class _WeakrefWeight:
    """Negative fixture: slots with the weak-reference slot put back."""

    kilograms: float


def test_equal_values_are_interchangeable() -> None:
    pairs: list[tuple[object, object]] = [
        (Weight(2.5), Weight(2.5)),
        (Money(Decimal("9.99"), "EUR"), Money(Decimal("9.99"), "EUR")),
        (SlotId(1, 2, 3), SlotId(1, 2, 3)),
    ]
    for left, right in pairs:
        assert left == right
        assert left is not right
        assert hash(left) == hash(right)
        assert {left: "held"}[right] == "held"


@pytest.mark.parametrize("kilograms", [0.0, -1.0, math.inf, -math.inf, math.nan])
def test_weight_must_be_positive_and_finite(kilograms: float) -> None:
    with pytest.raises(ValueError, match="kilograms must be positive"):
        Weight(kilograms)


def test_a_frozen_value_refuses_assignment() -> None:
    w = Weight(1.0)
    with pytest.raises(FrozenInstanceError, match="cannot assign to field 'kilograms'"):
        w.kilograms = 2.0  # type: ignore[misc]
    assert w.kilograms == 1.0


def test_frozen_is_a_setattr_guard_not_a_seal() -> None:
    w = Weight(1.0)
    object.__setattr__(w, "kilograms", -5.0)
    assert w.kilograms == -5.0


def test_frozen_is_shallow() -> None:
    value = _FrozenWithList(["SGSIN"])
    value.codes.append("NLRTM")
    assert value.codes == ["SGSIN", "NLRTM"]
    with pytest.raises(TypeError, match="unhashable type: 'list'"):
        hash(value)


def test_slots_remove_dict_and_weakref_until_asked() -> None:
    w = Weight(1.0)
    assert not hasattr(w, "__dict__")
    with pytest.raises(TypeError, match="cannot create weak reference to 'Weight'"):
        weakref.ref(w)
    kept = _WeakrefWeight(1.0)
    assert weakref.ref(kept)() is kept
