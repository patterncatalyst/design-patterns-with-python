"""Customs clearance as a chain of stages. `None` passes the declaration on."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import assert_never

from mediator_chain.domain import CustomsDeclaration, DocumentKind


@dataclass(frozen=True, slots=True)
class Released:
    """The consignment may move."""


@dataclass(frozen=True, slots=True)
class Held:
    """The consignment is stopped, with the reason."""

    reason: str


type Decision = Released | Held
type ClearanceStage = Callable[[CustomsDeclaration], Decision | None]
type FinalStage = Callable[[CustomsDeclaration], Decision]


def check_documents(declaration: CustomsDeclaration, /) -> Decision | None:
    if DocumentKind.COMMERCIAL_INVOICE not in declaration.documents:
        return Held("missing commercial invoice")
    if (
        declaration.commodity.restricted
        and DocumentKind.DANGEROUS_GOODS_DECLARATION not in declaration.documents
    ):
        return Held("missing dangerous goods declaration")
    return None


def assess_duty(declaration: CustomsDeclaration, /) -> Decision | None:
    if not declaration.duty_paid:
        return Held("duty unpaid")
    return None


def inspect_goods(declaration: CustomsDeclaration, /) -> Decision | None:
    if declaration.commodity.restricted:
        return Held("inspection required")
    return None


def release(declaration: CustomsDeclaration, /) -> Decision:
    return Released()


CLEARANCE_STAGES: tuple[ClearanceStage, ...] = (check_documents, assess_duty, inspect_goods)


def clear(
    declaration: CustomsDeclaration,
    stages: Iterable[ClearanceStage],
    /,
    *,
    final: FinalStage = release,
) -> Decision:
    """Return the first decision a stage makes, else the final stage's. Later stages don't run."""
    for stage in stages:
        if (decision := stage(declaration)) is not None:
            return decision
    return final(declaration)


def describe(decision: Decision, /) -> str:
    match decision:
        case Released():
            return "released"
        case Held(reason=reason):
            return f"held: {reason}"
        case _:
            assert_never(decision)
