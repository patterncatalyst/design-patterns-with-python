from typing import TYPE_CHECKING

import pytest
from dynamic_attributes.tracking import (
    ConsignmentId,
    ConsignmentStatus,
    HandlingKind,
    TrackingHistory,
)

if TYPE_CHECKING:
    from conftest import HistoryForm, RecordingLoad

# (id, consignment, event count, status, last port)
HISTORY_ROWS = [
    ("in-transit", "CN-1", 3, ConsignmentStatus.IN_TRANSIT, "SGSIN"),
    ("booked", "CN-2", 1, ConsignmentStatus.BOOKED, "NLRTM"),
    ("delivered", "CN-3", 5, ConsignmentStatus.DELIVERED, "SGSIN"),
    ("empty", "CN-4", 0, None, None),
]


def _assign(target: object, name: str, value: object) -> None:
    setattr(target, name, value)


def _read(target: object, name: str) -> object:
    return getattr(target, name)


@pytest.mark.parametrize(
    ("consignment", "count", "status", "last_port"),
    [row[1:] for row in HISTORY_ROWS],
    ids=[row[0] for row in HISTORY_ROWS],
)
def test_every_history_form_reads_the_loaded_fields(
    history_form: HistoryForm,
    recording_load: RecordingLoad,
    consignment: str,
    count: int,
    status: ConsignmentStatus | None,
    last_port: str | None,
) -> None:
    history = history_form(ConsignmentId(consignment), recording_load)
    assert len(history.events) == count
    assert history.status is status
    assert history.last_port == last_port


def test_every_history_form_loads_once_for_every_field(
    history_form: HistoryForm, recording_load: RecordingLoad
) -> None:
    history = history_form(ConsignmentId("CN-1"), recording_load)
    for _ in range(2):
        assert history.status is ConsignmentStatus.IN_TRANSIT
        assert history.last_port == "SGSIN"
        assert len(history.events) == 3
    assert recording_load.calls == ["CN-1"]


def test_every_history_form_refuses_assignment_to_a_loaded_field(
    history_form: HistoryForm, recording_load: RecordingLoad
) -> None:
    history = history_form(ConsignmentId("CN-1"), recording_load)
    with pytest.raises(AttributeError):
        _assign(history, "status", ConsignmentStatus.BOOKED)
    assert history.status is ConsignmentStatus.IN_TRANSIT


def test_every_history_form_raises_attribute_error_for_a_misspelt_field(
    history_form: HistoryForm, recording_load: RecordingLoad
) -> None:
    history = history_form(ConsignmentId("CN-1"), recording_load)
    with pytest.raises(AttributeError, match="stauts"):
        _read(history, "stauts")


def test_nothing_is_loaded_until_a_field_is_read(recording_load: RecordingLoad) -> None:
    history = TrackingHistory(ConsignmentId("CN-1"), recording_load)
    assert sorted(vars(history)) == ["_load", "consignment_id"]
    assert recording_load.calls == []


def test_a_loaded_history_reads_its_fields_from_the_instance_dict(
    recording_load: RecordingLoad,
) -> None:
    history = TrackingHistory(ConsignmentId("CN-1"), recording_load)
    assert history.last_port == "SGSIN"
    assert {"events", "last_port", "status"} <= set(vars(history))
    assert vars(history)["status"] is ConsignmentStatus.IN_TRANSIT


def test_iterating_a_history_loads_it(recording_load: RecordingLoad) -> None:
    history = TrackingHistory(ConsignmentId("CN-1"), recording_load)
    assert [event.kind for event in history] == [
        HandlingKind.BOOKED,
        HandlingKind.LOADED,
        HandlingKind.DEPARTED,
    ]
    assert recording_load.calls == ["CN-1"]
