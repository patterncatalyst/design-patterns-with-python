from typing import Protocol

import pytest
from mediator_chain.domain import (
    ConsignmentId,
    CustomsDeclaration,
    DocumentKind,
    HandlingEvent,
    HandlingKind,
    TrackingHistory,
)
from mediator_chain.mediator import (
    ClearanceError,
    ClearanceMediator,
    ClearanceMessage,
    Inspection,
    Settlement,
)


class DeclarationFactory(Protocol):
    def __call__(
        self,
        *,
        restricted: bool = False,
        documents: frozenset[DocumentKind] = ...,
        duty_paid: bool = True,
    ) -> CustomsDeclaration: ...


class _Coordination(Protocol):
    history: TrackingHistory

    def settle(self) -> None: ...

    def inspect(self, passed: bool, /) -> None: ...


CN1 = ConsignmentId("CN-1")


def _mediate(declaration: CustomsDeclaration) -> tuple[ClearanceMediator, TrackingHistory]:
    history = TrackingHistory()
    return ClearanceMediator(declaration, release=history.record), history


def _kinds(history: TrackingHistory) -> list[HandlingKind]:
    return [event.kind for event in history.events]


def test_release_follows_inspection_then_settlement(coordination_form: _Coordination) -> None:
    coordination_form.inspect(True)
    coordination_form.settle()

    assert [e.kind for e in coordination_form.history.events] == [HandlingKind.CLEARED]


@pytest.mark.parametrize(
    "inspection_first", [True, False], ids=["inspection-first", "settlement-first"]
)
def test_the_mediator_releases_in_either_order(
    inspection_first: bool, declaration: DeclarationFactory
) -> None:
    mediator, history = _mediate(declaration(restricted=True, duty_paid=False))
    messages: list[ClearanceMessage] = [Inspection(CN1, True), Settlement(CN1)]
    first, second = messages if inspection_first else messages[::-1]

    mediator.receive(first)
    assert _kinds(history) == []
    mediator.receive(second)

    assert _kinds(history) == [HandlingKind.CLEARED]


def test_a_choreography_loses_a_settlement_that_arrives_before_inspection(
    choreography: _Coordination,
) -> None:
    choreography.settle()
    choreography.inspect(True)

    assert choreography.history.events == ()


def test_a_duplicate_settlement_releases_once(declaration: DeclarationFactory) -> None:
    mediator, history = _mediate(declaration(restricted=True, duty_paid=False))

    mediator.receive(Settlement(CN1))
    mediator.receive(Inspection(CN1, True))
    mediator.receive(Settlement(CN1))

    assert len(history.events) == 1


def test_a_failed_inspection_holds_the_consignment(declaration: DeclarationFactory) -> None:
    mediator, history = _mediate(declaration(restricted=True, duty_paid=False))

    mediator.receive(Settlement(CN1))
    mediator.receive(Inspection(CN1, False))

    assert history.events == ()


def test_a_declaration_with_nothing_outstanding_is_released_at_once(
    declaration: DeclarationFactory,
) -> None:
    _mediator, history = _mediate(declaration())

    assert len(history.events) == 1


@pytest.mark.parametrize(
    ("restricted", "duty_paid", "report"),
    [
        (False, False, Settlement(CN1)),
        (True, True, Inspection(CN1, True)),
    ],
    ids=["duty-only", "inspection-only"],
)
def test_a_declaration_that_owes_one_report_is_released_on_that_report(
    declaration: DeclarationFactory,
    restricted: bool,
    duty_paid: bool,
    report: ClearanceMessage,
) -> None:
    mediator, history = _mediate(declaration(restricted=restricted, duty_paid=duty_paid))
    assert _kinds(history) == []

    mediator.receive(report)

    assert _kinds(history) == [HandlingKind.CLEARED]


def test_a_message_for_another_consignment_is_refused(declaration: DeclarationFactory) -> None:
    mediator, history = _mediate(declaration(restricted=True, duty_paid=False))

    with pytest.raises(ClearanceError, match="CN-2"):
        mediator.receive(Settlement(ConsignmentId("CN-2")))
    mediator.receive(Inspection(CN1, True))

    assert history.events == ()


def test_release_records_a_cleared_handling_event_at_the_port(
    declaration: DeclarationFactory,
) -> None:
    _mediator, history = _mediate(declaration())

    assert history.events == (HandlingEvent(CN1, HandlingKind.CLEARED, "NLRTM"),)
