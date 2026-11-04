from dataclasses import dataclass
from decimal import Decimal

import pytest
from value_semantics.booking import BookingRequest, Consignment
from value_semantics.stowage import StowagePlan
from value_semantics.values import ConsignmentId, Money, SlotId, Weight


@dataclass(frozen=True, slots=True, order=True)
class _OrderedMoney:
    """Negative fixture: Money with order=True, which compares across currencies."""

    amount: Decimal
    currency: str


def test_order_true_sorts_by_field_order() -> None:
    unsorted = [SlotId(2, 0, 1), SlotId(1, 3, 1), SlotId(1, 0, 2), SlotId(1, 0, 1)]
    assert sorted(unsorted) == [SlotId(1, 0, 1), SlotId(1, 0, 2), SlotId(1, 3, 1), SlotId(2, 0, 1)]
    assert max(Weight(3.0), Weight(12.5), Weight(7.0)) == Weight(12.5)


def test_order_true_would_compare_money_across_currencies() -> None:
    assert _OrderedMoney(Decimal("3"), "EUR") < _OrderedMoney(Decimal("5"), "USD")
    with pytest.raises(TypeError):
        Money.of("3", "EUR") < Money.of("5", "USD")  # type: ignore[operator]  # noqa: B015


def test_order_true_refuses_a_hand_written_lt() -> None:
    with pytest.raises(TypeError, match="Cannot overwrite attribute __lt__"):

        @dataclass(order=True)
        class _HandWritten:
            kilograms: float

            def __lt__(self, other: _HandWritten) -> bool:  # type: ignore[misc]
                return self.kilograms < other.kilograms


def test_compare_false_keeps_remarks_out_of_equality(consignment: Consignment) -> None:
    first = BookingRequest(consignment=consignment, remarks="call driver")
    retry = BookingRequest(consignment=consignment, remarks="gate code 4411")
    assert first == retry
    assert hash(first) == hash(retry)
    assert len({first: 1, retry: 2}) == 1
    assert "call driver" in repr(first)
    assert "gate code 4411" in repr(retry)


def test_kw_only_rejects_positional_arguments() -> None:
    with pytest.raises(TypeError, match="positional argument"):
        Consignment(ConsignmentId("CN-00000009"), Weight(1.0), "SGSIN")  # type: ignore[call-arg]


def test_money_validates_and_of_normalises() -> None:
    assert Money.of("12.505", "EUR").amount == Decimal("12.51")
    with pytest.raises(ValueError, match="amount must be whole cents"):
        Money(Decimal("12.505"), "EUR")
    with pytest.raises(ValueError, match="currency must be three capital letters"):
        Money(Decimal("1.00"), "eur")


def test_slot_id_validates_each_coordinate() -> None:
    with pytest.raises(ValueError, match="bay must be at least 1"):
        SlotId(0, 0, 1)
    with pytest.raises(ValueError, match="row must be at least 0"):
        SlotId(1, -1, 1)
    with pytest.raises(ValueError, match="tier must be at least 1"):
        SlotId(1, 0, 0)


def test_money_addition_needs_one_currency() -> None:
    assert Money.of("1.50", "EUR") + Money.of("2.25", "EUR") == Money.of("3.75", "EUR")
    with pytest.raises(ValueError, match="cannot add USD to EUR"):
        Money.of("1.00", "EUR") + Money.of("1.00", "USD")
    with pytest.raises(TypeError):
        Money.of("1.00", "EUR") + 1


def test_stowage_plan_is_an_entity(slots: tuple[SlotId, SlotId, SlotId]) -> None:
    first, second, third = slots
    plan_a = StowagePlan("SAILING-1")
    plan_b = StowagePlan("SAILING-1")
    assert plan_a != plan_b
    assert plan_a == plan_a
    assert len({plan_a, plan_b}) == 2

    plan_a.reserve(third, ConsignmentId("CN-00000003"))
    plan_a.reserve(first, ConsignmentId("CN-00000001"))
    plan_a.reserve(second, ConsignmentId("CN-00000002"))
    with pytest.raises(ValueError, match="already holds"):
        plan_a.reserve(first, ConsignmentId("CN-00000004"))
    assert plan_b.reservations == {}
    assert plan_a.occupied() == [first, second, third]


def test_mutable_default_is_refused_at_class_creation() -> None:
    with pytest.raises(ValueError, match="use default_factory"):

        @dataclass(eq=False, slots=True)
        class _SharedDefault:
            reservations: dict[SlotId, ConsignmentId] = {}  # noqa: RUF008
