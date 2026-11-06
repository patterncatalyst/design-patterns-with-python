from collections.abc import Callable
from functools import singledispatch

import pytest
from visitor_memento_interpreter.domain import ConsignmentId, ConsignmentStatus
from visitor_memento_interpreter.events import (
    Booked,
    Cleared,
    Delivered,
    Departed,
    HandlingEvent,
    Loaded,
    describe,
    status_after,
)

CN1 = ConsignmentId("CN-1")

type VisitorForm = tuple[tuple[HandlingEvent, ...], Callable[[HandlingEvent], str]]

DESCRIPTIONS = (
    "CN-1 booked at NLRTM",
    "CN-1 loaded at NLRTM",
    "CN-1 departed NLRTM",
    "CN-1 cleared customs at SGSIN",
    "CN-1 delivered at SGSIN",
)


def test_every_visitor_form_describes_a_journey_the_same_way(visitor_form: VisitorForm) -> None:
    events, describe_event = visitor_form
    described = tuple(describe_event(event) for event in events)

    assert described == DESCRIPTIONS


@pytest.mark.parametrize(
    ("event", "status"),
    [
        pytest.param(Booked(CN1, "NLRTM"), ConsignmentStatus.BOOKED, id="booked"),
        pytest.param(Loaded(CN1, "NLRTM"), ConsignmentStatus.LOADED, id="loaded"),
        pytest.param(Departed(CN1, "NLRTM"), ConsignmentStatus.IN_TRANSIT, id="departed"),
        pytest.param(Cleared(CN1, "SGSIN"), ConsignmentStatus.CLEARED, id="cleared"),
        pytest.param(Delivered(CN1, "SGSIN"), ConsignmentStatus.DELIVERED, id="delivered"),
    ],
)
def test_status_after_maps_each_event_to_a_consignment_status(
    event: HandlingEvent, status: ConsignmentStatus
) -> None:
    assert status_after(event) is status


def test_a_singledispatch_visitor_gives_an_unregistered_event_its_fallback() -> None:
    @singledispatch
    def describe_event(event: object, /) -> str:
        return "unrecognised event"

    @describe_event.register
    def _(event: Booked, /) -> str:
        return "booked"

    @describe_event.register
    def _(event: Loaded, /) -> str:
        return "loaded"

    @describe_event.register
    def _(event: Departed, /) -> str:
        return "departed"

    @describe_event.register
    def _(event: Cleared, /) -> str:
        return "cleared"

    assert describe_event(Cleared(CN1, "SGSIN")) == "cleared"
    assert describe_event(Delivered(CN1, "SGSIN")) == "unrecognised event"


def test_describe_refuses_an_object_outside_the_union() -> None:
    with pytest.raises(AssertionError, match="Expected code to be unreachable"):
        describe("not an event")  # type: ignore[arg-type]


def test_singledispatch_dispatches_on_the_first_argument_only() -> None:
    @singledispatch
    def two(first: object, second: object, /) -> str:
        return "fallback"

    @two.register
    def _(first: Booked, second: object, /) -> str:
        return f"booked/{type(second).__name__}"

    booked = Booked(CN1, "NLRTM")

    assert two(booked, 1) == "booked/int"
    assert two(booked, "x") == "booked/str"
    assert two(1, booked) == "fallback"


def test_the_accept_form_puts_an_accept_method_on_every_event_class(
    accepting_twins: tuple[HandlingEvent, ...],
) -> None:
    src_classes = (Booked, Loaded, Departed, Cleared, Delivered)

    assert len(accepting_twins) == len(src_classes)
    assert all(callable(getattr(twin, "accept", None)) for twin in accepting_twins)
    assert not any(hasattr(cls, "accept") for cls in src_classes)
