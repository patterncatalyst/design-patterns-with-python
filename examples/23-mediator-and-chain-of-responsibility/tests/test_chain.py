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
    describe,
    inspect_goods,
    release,
)
from mediator_chain.domain import CustomsDeclaration, DocumentKind

type Chain = Callable[[CustomsDeclaration], Decision | None]


class DeclarationFactory(Protocol):
    def __call__(
        self,
        *,
        restricted: bool = False,
        documents: frozenset[DocumentKind] = ...,
        duty_paid: bool = True,
    ) -> CustomsDeclaration: ...


def test_a_restricted_commodity_is_held_for_inspection(
    chain_form: Chain, declaration: DeclarationFactory
) -> None:
    assert chain_form(declaration(restricted=True)) == Held("inspection required")


@pytest.mark.parametrize(
    ("restricted", "documents", "reason"),
    [
        pytest.param(False, frozenset(), "missing commercial invoice", id="commercial-invoice"),
        pytest.param(
            True,
            frozenset({DocumentKind.COMMERCIAL_INVOICE}),
            "missing dangerous goods declaration",
            id="dangerous-goods",
        ),
    ],
)
def test_a_declaration_missing_a_document_is_held(
    chain_form: Chain,
    declaration: DeclarationFactory,
    restricted: bool,
    documents: frozenset[DocumentKind],
    reason: str,
) -> None:
    held = declaration(restricted=restricted, documents=documents)

    assert chain_form(held) == Held(reason)


def test_an_unpaid_declaration_is_held_for_duty(
    chain_form: Chain, declaration: DeclarationFactory
) -> None:
    assert chain_form(declaration(duty_paid=False)) == Held("duty unpaid")


def test_the_first_stage_that_decides_wins(
    chain_form: Chain, declaration: DeclarationFactory
) -> None:
    both = declaration(documents=frozenset(), duty_paid=False)

    assert chain_form(both) == Held("missing commercial invoice")


def test_a_clean_declaration_is_released(declaration: DeclarationFactory) -> None:
    assert clear(declaration(), CLEARANCE_STAGES) == Released()


def test_a_linked_chain_with_no_terminal_returns_none(
    linked_chain: Chain, declaration: DeclarationFactory
) -> None:
    assert linked_chain(declaration()) is None


def test_stages_after_a_decision_are_not_called(declaration: DeclarationFactory) -> None:
    called: list[str] = []

    def passing(declaration: CustomsDeclaration, /) -> Decision | None:
        called.append("passing")
        return None

    def holding(declaration: CustomsDeclaration, /) -> Decision | None:
        called.append("holding")
        return Held("stop")

    def never(declaration: CustomsDeclaration, /) -> Decision | None:
        called.append("never")
        return Held("too late")

    def final(declaration: CustomsDeclaration, /) -> Decision:
        called.append("final")
        return Released()

    assert clear(declaration(), (passing, holding, never), final=final) == Held("stop")
    assert called == ["passing", "holding"]


def test_a_stage_added_after_release_clears_a_restricted_commodity(
    declaration: DeclarationFactory,
) -> None:
    misordered: list[ClearanceStage] = [check_documents, assess_duty, release]
    misordered.append(inspect_goods)

    assert clear(declaration(restricted=True), misordered) == Released()


def test_a_stage_added_to_the_chain_runs_before_the_final_stage(
    declaration: DeclarationFactory,
) -> None:
    def hold_all(declaration: CustomsDeclaration, /) -> Decision | None:
        return Held("hold everything")

    stages = (*CLEARANCE_STAGES, hold_all)

    assert clear(declaration(), stages) == Held("hold everything")


@pytest.mark.parametrize("final", ["release", "hold"])
def test_an_empty_chain_leaves_the_decision_to_the_final_stage(
    final: str, declaration: DeclarationFactory
) -> None:
    def hold(declaration: CustomsDeclaration, /) -> Decision:
        return Held("final holds")

    expected = Released() if final == "release" else Held("final holds")
    stage = release if final == "release" else hold

    assert clear(declaration(restricted=True), (), final=stage) == expected


@pytest.mark.parametrize(
    ("decision", "text"),
    [
        pytest.param(Released(), "released", id="released"),
        pytest.param(Held("duty unpaid"), "held: duty unpaid", id="held"),
    ],
)
def test_describe_names_every_decision(decision: Decision, text: str) -> None:
    assert describe(decision) == text
