import dataclasses
from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from builder_prototype.booking import BookingRequest
from builder_prototype.domain import BookingError, ConsignmentId, Weight

if TYPE_CHECKING:
    from conftest import BookingCase, BookingInput, _BookingRequestBuilder, _LegacyBookingRequest

CN = ConsignmentId("CN-1")
WEIGHT = Weight(Decimal("120"))


def test_a_positional_constructor_accepts_a_swapped_origin_and_destination(
    legacy_request: type[_LegacyBookingRequest],
) -> None:
    origin, destination = "NLRTM", "SGSIN"

    swapped = legacy_request(
        CN, destination, origin, WEIGHT, "FASTLINE", "standard", False, None, False, None, None, ()
    )

    assert (swapped.origin, swapped.destination) == ("SGSIN", "NLRTM")


def test_both_constructors_pass_the_booking_table(
    build: Callable[[BookingInput], object],
    booking_case: BookingCase,
    view: Callable[[object], dict[str, object]],
) -> None:
    if booking_case.error is not None:
        with pytest.raises(BookingError, match=booking_case.error) as raised:
            build(booking_case.fields)
        assert isinstance(raised.value, ValueError)
        return

    assert view(build(booking_case.fields)) == dataclasses.asdict(booking_case.fields) | {
        "weight": WEIGHT
    }


def test_the_request_has_twelve_fields_and_four_are_required() -> None:
    fields = dataclasses.fields(BookingRequest)
    required = {f.name for f in fields if f.default is dataclasses.MISSING}
    defaults = {f.name: f.default for f in fields if f.default is not dataclasses.MISSING}

    assert len(fields) == 12
    assert required == {"consignment_id", "origin", "destination", "weight"}
    assert all(f.kw_only for f in fields)
    assert defaults == {
        "carrier": "FASTLINE",
        "service": "standard",
        "insured": False,
        "declared_value": None,
        "dangerous_goods": False,
        "reference": None,
        "notify_party": None,
        "documents": (),
    }


def test_a_builder_with_a_step_left_out_fails_only_at_build(
    new_builder: type[_BookingRequestBuilder],
) -> None:
    builder = new_builder().consignment(CN).origin("NLRTM").weight(WEIGHT)

    with pytest.raises(ValueError, match="missing: destination") as raised:
        builder.build()

    assert type(raised.value) is ValueError


def test_a_booking_request_and_a_weight_are_frozen() -> None:
    request = BookingRequest(consignment_id=CN, origin="NLRTM", destination="SGSIN", weight=WEIGHT)

    with pytest.raises(dataclasses.FrozenInstanceError):
        request.origin = "DEHAM"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        WEIGHT.kilograms = Decimal("1")  # type: ignore[misc]


def test_a_booking_request_has_no_instance_dict() -> None:
    request = BookingRequest(consignment_id=CN, origin="NLRTM", destination="SGSIN", weight=WEIGHT)

    assert not hasattr(request, "__dict__")


@pytest.mark.parametrize("kilograms", ["0", "-1", "NaN"], ids=["zero", "negative", "nan"])
def test_a_requested_weight_must_be_positive_and_finite(kilograms: str) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        Weight(Decimal(kilograms))
