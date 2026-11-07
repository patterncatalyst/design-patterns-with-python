"""A mediator that releases a held declaration once the reports it is still owed have arrived."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, assert_never

from mediator_chain.domain import (
    ConsignmentId,
    CustomsDeclaration,
    HandlingEvent,
    HandlingKind,
)


@dataclass(frozen=True, slots=True)
class Settlement:
    """Billing reports that duty is paid in full."""

    consignment_id: ConsignmentId


@dataclass(frozen=True, slots=True)
class Inspection:
    """The inspection party reports a result."""

    consignment_id: ConsignmentId
    passed: bool


type ClearanceMessage = Settlement | Inspection
type Report = Literal["duty", "inspection"]


class ClearanceError(ValueError):
    """A message was sent to the wrong mediator."""


class ClearanceMediator:
    """Owns the rule for releasing one declaration. Single-threaded."""

    def __init__(
        self,
        declaration: CustomsDeclaration,
        *,
        release: Callable[[HandlingEvent], None],
    ) -> None:
        self._declaration = declaration
        self._release = release
        self._outstanding: set[Report] = set()
        if not declaration.duty_paid:
            self._outstanding.add("duty")
        if declaration.commodity.restricted:
            self._outstanding.add("inspection")
        self._failed = False
        self._released = False
        self._try_release()

    def receive(self, message: ClearanceMessage, /) -> None:
        own = self._declaration.consignment_id
        if message.consignment_id != own:
            raise ClearanceError(
                f"message for {message.consignment_id!r} sent to the mediator for {own!r}"
            )
        match message:
            case Settlement():
                self._outstanding.discard("duty")
            case Inspection(passed=True):
                self._outstanding.discard("inspection")
            case Inspection():
                self._outstanding.discard("inspection")
                self._failed = True
            case _:
                assert_never(message)
        self._try_release()

    def _try_release(self) -> None:
        if self._outstanding or self._failed or self._released:
            return
        self._released = True
        declaration = self._declaration
        self._release(
            HandlingEvent(declaration.consignment_id, HandlingKind.CLEARED, declaration.port)
        )
