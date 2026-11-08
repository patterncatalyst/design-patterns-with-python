from dataclasses import dataclass, replace

import pytest
from value_semantics.booking import BookingRequest, Consignment
from value_semantics.values import ConsignmentId, SlotId, Weight


@dataclass
class _MutableConsignment:
    """Negative fixture: the same consignment as a plain mutable dataclass."""

    id: ConsignmentId
    weight: Weight
    destination: str


@dataclass
class _MutableBooking:
    """Negative fixture: a booking holding a reference to a mutable consignment."""

    consignment: _MutableConsignment


@dataclass
class _MutableSlotId:
    """Negative fixture: eq without frozen sets __hash__ to None."""

    bay: int
    row: int
    tier: int


def test_a_mutable_consignment_aliased_between_bookings_changes_both() -> None:
    shared = _MutableConsignment(ConsignmentId("CN-00000001"), Weight(100.0), "SGSIN")
    booking_a = _MutableBooking(shared)
    booking_b = _MutableBooking(shared)
    booking_a.consignment.weight = Weight(250.0)
    assert booking_b.consignment.weight == Weight(250.0)


def test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old(
    consignment: Consignment,
) -> None:
    request_a = BookingRequest(consignment=consignment)
    request_b = BookingRequest(consignment=consignment)
    amended = replace(request_a.consignment, weight=Weight(250.0))
    request_a = replace(request_a, consignment=amended)
    assert amended is not consignment
    assert request_a.consignment.weight == Weight(250.0)
    assert request_b.consignment.weight == Weight(100.0)
    assert consignment.weight == Weight(100.0)
    assert request_b.consignment is consignment


def test_replace_runs_post_init() -> None:
    with pytest.raises(ValueError, match="kilograms must be positive and finite"):
        replace(Weight(1.0), kilograms=-1.0)
    with pytest.raises(ValueError, match="bay must be at least 1"):
        replace(SlotId(1, 0, 1), bay=0)


def test_a_mutable_dataclass_is_not_a_dict_key() -> None:
    slot = _MutableSlotId(1, 0, 1)
    hash_slot: object = slot.__hash__
    assert hash_slot is None
    with pytest.raises(TypeError, match="unhashable type: '_MutableSlotId'"):
        {slot: "held"}  # noqa: B018
