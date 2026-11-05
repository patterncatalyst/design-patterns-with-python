"""Fixtures. The comparison forms live here as fixture parameters so that they run the same hold
table and the same release table as the idiomatic code: a GoF linked chain, one `match`, and
colleagues that call each other."""

from collections.abc import Callable
from typing import Protocol

import pytest
from mediator_chain.clearance import (
    CLEARANCE_STAGES,
    ClearanceStage,
    Decision,
    Held,
    Released,
    assess_duty,
    check_documents,
    clear,
    inspect_goods,
)
from mediator_chain.domain import (
    Commodity,
    ConsignmentId,
    CustomsDeclaration,
    DocumentKind,
    HandlingEvent,
    HandlingKind,
    TrackingHistory,
)
from mediator_chain.mediator import ClearanceMediator, Inspection, Settlement

# Harmonised-system codes are illustrative.
BATTERIES = Commodity("850760", "lithium-ion batteries", restricted=True)
COFFEE = Commodity("090111", "coffee, not roasted", restricted=False)
ALL_DOCUMENTS = frozenset(DocumentKind)

type Chain = Callable[[CustomsDeclaration], Decision | None]


class DeclarationFactory(Protocol):
    def __call__(
        self,
        *,
        restricted: bool = False,
        documents: frozenset[DocumentKind] = ALL_DOCUMENTS,
        duty_paid: bool = True,
        consignment_id: str = "CN-1",
    ) -> CustomsDeclaration: ...


@pytest.fixture
def declaration() -> DeclarationFactory:
    """Build a declaration at Rotterdam. The default is paid coffee with every document."""

    def make(
        *,
        restricted: bool = False,
        documents: frozenset[DocumentKind] = ALL_DOCUMENTS,
        duty_paid: bool = True,
        consignment_id: str = "CN-1",
    ) -> CustomsDeclaration:
        return CustomsDeclaration(
            consignment_id=ConsignmentId(consignment_id),
            port="NLRTM",
            commodity=BATTERIES if restricted else COFFEE,
            documents=documents,
            duty_paid=duty_paid,
        )

    return make


class _Handler:
    """The GoF linked chain: each handler holds the next one. Off the end it returns None."""

    def __init__(self, stage: ClearanceStage, next_handler: _Handler | None = None) -> None:
        self._stage = stage
        self._next = next_handler

    def handle(self, declaration: CustomsDeclaration, /) -> Decision | None:
        if (decision := self._stage(declaration)) is not None:
            return decision
        return self._next.handle(declaration) if self._next is not None else None


def _clear_by_match(declaration: CustomsDeclaration, /) -> Decision | None:
    """One `match` over the declaration with a default: the rules are closed and fixed."""
    match declaration:
        case CustomsDeclaration(documents=documents) if (
            DocumentKind.COMMERCIAL_INVOICE not in documents
        ):
            return Held("missing commercial invoice")
        case CustomsDeclaration(commodity=Commodity(restricted=True), documents=documents) if (
            DocumentKind.DANGEROUS_GOODS_DECLARATION not in documents
        ):
            return Held("missing dangerous goods declaration")
        case CustomsDeclaration(duty_paid=False):
            return Held("duty unpaid")
        case CustomsDeclaration(commodity=Commodity(restricted=True)):
            return Held("inspection required")
        case _:
            return Released()


def _clear_stages(declaration: CustomsDeclaration, /) -> Decision | None:
    return clear(declaration, CLEARANCE_STAGES)


def _linked_chain() -> _Handler:
    return _Handler(check_documents, _Handler(assess_duty, _Handler(inspect_goods)))


def _clear_linked(declaration: CustomsDeclaration, /) -> Decision | None:
    return _linked_chain().handle(declaration)


@pytest.fixture
def linked_chain() -> Chain:
    """The linked chain with no terminal stage."""
    return _linked_chain().handle


@pytest.fixture(params=["stages", "linked", "match"])
def chain_form(request: pytest.FixtureRequest) -> Chain:
    """The same chain written three ways."""
    forms: dict[str, Chain] = {
        "stages": _clear_stages,
        "linked": _clear_linked,
        "match": _clear_by_match,
    }
    form: Chain = forms[request.param]
    return form


class Coordination(Protocol):
    """What the release table needs from either form."""

    history: TrackingHistory

    def settle(self) -> None: ...

    def inspect(self, passed: bool, /) -> None: ...


class _Mediated:
    def __init__(self, declaration: CustomsDeclaration) -> None:
        self.history = TrackingHistory()
        self._id = declaration.consignment_id
        self._mediator = ClearanceMediator(declaration, release=self.history.record)

    def settle(self) -> None:
        self._mediator.receive(Settlement(self._id))

    def inspect(self, passed: bool, /) -> None:
        self._mediator.receive(Inspection(self._id, passed))


class _Choreography:
    """Colleagues that call each other: inspection tells billing, and billing releases.

    Billing only acts on a settlement once it has been told the inspection passed.
    """

    def __init__(self, declaration: CustomsDeclaration) -> None:
        self.history = TrackingHistory()
        inspected = False

        def release_consignment() -> None:
            self.history.record(
                HandlingEvent(declaration.consignment_id, HandlingKind.CLEARED, declaration.port)
            )

        def billing_told_inspected() -> None:
            nonlocal inspected
            inspected = True

        def billing_settled() -> None:
            if inspected:
                release_consignment()

        def inspection_reported(passed: bool, /) -> None:
            if passed:
                billing_told_inspected()

        self._settled = billing_settled
        self._inspected = inspection_reported

    def settle(self) -> None:
        self._settled()

    def inspect(self, passed: bool, /) -> None:
        self._inspected(passed)


@pytest.fixture
def choreography(declaration: DeclarationFactory) -> Coordination:
    """Colleagues that call each other, for the tests that show where they fail."""
    return _Choreography(declaration(restricted=True, duty_paid=False))


@pytest.fixture(params=["mediator", "choreography"])
def coordination_form(
    request: pytest.FixtureRequest, declaration: DeclarationFactory
) -> Coordination:
    """Held batteries (duty unpaid), coordinated by a mediator or by colleagues."""
    held = declaration(restricted=True, duty_paid=False)
    form: Coordination = _Mediated(held) if request.param == "mediator" else _Choreography(held)
    return form
