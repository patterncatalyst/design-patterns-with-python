from collections.abc import Callable, Sequence

import pytest
from state_machines.domain import (
    ConsignmentId,
    ConsignmentStatus,
    HandlingEvent,
    HandlingKind,
)
from state_machines.states import (
    Booked,
    Cleared,
    ConsignmentState,
    Delivered,
    InTransit,
    Loaded,
    apply_event,
    status_of,
)
from state_machines.table import next_status

type Fold = Callable[[Sequence[HandlingKind]], ConsignmentStatus]
type Legal = Sequence[tuple[Sequence[HandlingKind], ConsignmentStatus]]
type Illegal = Sequence[tuple[Sequence[HandlingKind], str]]

_CONSIGNMENT = ConsignmentId("CN-00000014")
_K = HandlingKind
_S = ConsignmentStatus

_SAMPLE_STATES: frozendict[ConsignmentStatus, ConsignmentState] = frozendict(
    {
        _S.BOOKED: Booked("NLRTM"),
        _S.LOADED: Loaded("NLRTM"),
        _S.IN_TRANSIT: InTransit("NLRTM"),
        _S.CLEARED: Cleared("SGSIN"),
        _S.DELIVERED: Delivered("SGSIN"),
    }
)


def _fold_table(kinds: Sequence[HandlingKind]) -> ConsignmentStatus:
    status = ConsignmentStatus.BOOKED
    for kind in kinds:
        status = next_status(status, kind)
    return status


def _fold_match(kinds: Sequence[HandlingKind]) -> ConsignmentStatus:
    state: ConsignmentState = Booked("NLRTM")
    for kind in kinds:
        state = apply_event(state, HandlingEvent(_CONSIGNMENT, kind, "NLRTM"))
    return status_of(state)


@pytest.fixture(params=["table", "match"])
def forms(request: pytest.FixtureRequest) -> Fold:
    """The same lifecycle, folded by the transition table and by the match over frozen states."""
    return _fold_table if request.param == "table" else _fold_match


@pytest.fixture
def sample_states() -> frozendict[ConsignmentStatus, ConsignmentState]:
    """One state per status."""
    return _SAMPLE_STATES


@pytest.fixture
def legal_histories() -> Legal:
    """Histories every form accepts, with the status each ends in."""
    return [
        ([], _S.BOOKED),
        ([_K.LOADED], _S.LOADED),
        ([_K.LOADED, _K.DEPARTED], _S.IN_TRANSIT),
        ([_K.LOADED, _K.DEPARTED, _K.CLEARED], _S.CLEARED),
        ([_K.LOADED, _K.DEPARTED, _K.CLEARED, _K.DELIVERED], _S.DELIVERED),
    ]


@pytest.fixture
def illegal_histories() -> Illegal:
    """Histories every form refuses, with the message the refusal carries."""
    return [
        ([_K.DEPARTED], "DEPARTED not allowed when BOOKED"),
        ([_K.BOOKED], "BOOKED not allowed when BOOKED"),
        ([_K.LOADED, _K.LOADED], "LOADED not allowed when LOADED"),
        ([_K.LOADED, _K.DEPARTED, _K.DELIVERED], "DELIVERED not allowed when IN_TRANSIT"),
        ([_K.LOADED, _K.DEPARTED, _K.CLEARED, _K.DEPARTED], "DEPARTED not allowed when CLEARED"),
    ]
