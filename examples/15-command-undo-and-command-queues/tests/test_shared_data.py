from dataclasses import dataclass, field, make_dataclass, replace

import pytest
from command_undo.amendments import SetInstructions
from command_undo.domain import BookingRequest, Consignment


@dataclass(frozen=True, slots=True)
class _LooseRequest:
    consignment: Consignment
    instructions: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class _LooseSetInstructions:
    instructions: dict[str, str]


def _loose_apply(
    request: _LooseRequest, command: _LooseSetInstructions
) -> tuple[_LooseRequest, _LooseSetInstructions]:
    return (
        replace(request, instructions=command.instructions),
        _LooseSetInstructions(request.instructions),
    )


def test_commands_sharing_a_mutable_mapping_undo_to_the_wrong_state(
    booking_request: BookingRequest,
) -> None:
    request = _LooseRequest(booking_request.consignment)
    notes = {"handling": "keep dry"}
    request, _first_inverse = _loose_apply(request, _LooseSetInstructions(notes))
    notes["handling"] = "fragile"  # the caller keeps editing the mapping it handed over
    request, second_inverse = _loose_apply(request, _LooseSetInstructions(notes))
    request, _redo = _loose_apply(request, second_inverse)
    assert request.instructions == {"handling": "fragile"}  # "keep dry" expected


def test_instructions_cannot_be_changed_after_queueing(booking_request: BookingRequest) -> None:
    command = SetInstructions(frozendict({"handling": "keep dry"}))
    with pytest.raises(TypeError, match="does not support item assignment"):
        command.instructions["handling"] = "fragile"  # type: ignore[index]
    assert command.instructions == {"handling": "keep dry"}
    with pytest.raises(TypeError, match="does not support item assignment"):
        booking_request.instructions["handling"] = "fragile"  # type: ignore[index]


def test_a_frozen_mapping_default_needs_no_factory(booking_request: BookingRequest) -> None:
    other = BookingRequest(consignment=booking_request.consignment)
    assert booking_request.instructions is other.instructions
    with pytest.raises(ValueError, match="use default_factory"):
        make_dataclass("_Loose", [("instructions", dict[str, str], {})])
