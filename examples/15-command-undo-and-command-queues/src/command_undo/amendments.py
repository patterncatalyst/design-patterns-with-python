"""Amendments as frozen values, and the one function that applies them."""

import re
from dataclasses import dataclass, replace
from typing import assert_never

from command_undo.domain import AmendmentError, BookingRequest, Weight

_PORT_CODE = re.compile(r"[A-Z]{5}")


@dataclass(frozen=True, slots=True)
class Reweigh:
    """Change the declared weight."""

    weight: Weight


@dataclass(frozen=True, slots=True)
class Redirect:
    """Change the destination to another UN/LOCODE port."""

    destination: str


@dataclass(frozen=True, slots=True)
class SetInstructions:
    """Replace the handling instructions as a whole."""

    instructions: frozendict[str, str]


type Amendment = Reweigh | Redirect | SetInstructions


def apply(request: BookingRequest, amendment: Amendment) -> tuple[BookingRequest, Amendment]:
    """Return the amended request and the amendment that reverses it.

    The inverse is read from the request being amended, at the moment of the change.
    """
    match amendment:
        case Reweigh(weight):
            amended = replace(request, consignment=replace(request.consignment, weight=weight))
            return amended, Reweigh(request.consignment.weight)
        case Redirect(destination):
            if not _PORT_CODE.fullmatch(destination):
                raise AmendmentError(f"not a port code: {destination!r}")
            amended = replace(
                request, consignment=replace(request.consignment, destination=destination)
            )
            return amended, Redirect(request.consignment.destination)
        case SetInstructions(instructions):
            return replace(request, instructions=instructions), SetInstructions(
                request.instructions
            )
        case _:
            assert_never(amendment)
