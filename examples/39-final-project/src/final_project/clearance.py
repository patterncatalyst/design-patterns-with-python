"""Documentation: customs clears a declaration through a chain of stages."""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from final_project.domain import Consignment, Money
from final_project.rating import CENT

HS_RATES = frozendict({"0901.21": Decimal("0.075"), "6109.10": Decimal("0.12")})


@dataclass(frozen=True, slots=True)
class CustomsDeclaration:
    consignment: Consignment
    duty: Money


@dataclass(frozen=True, slots=True)
class Held:
    reason: str


class ClearanceHeldError(Exception):
    """A stage held the declaration."""

    def __init__(self, held: Held) -> None:
        super().__init__(held.reason)
        self.held = held


type ClearanceStage = Callable[[CustomsDeclaration], Held | None]


def declare(consignment: Consignment, /) -> CustomsDeclaration:
    """Duty is each commodity's value times its HS rate; an unknown code carries none."""
    duty = Money(Decimal("0.00"))
    for commodity in consignment.commodities:
        rate = HS_RATES.get(commodity.hs_code, Decimal(0))
        amount = (commodity.value.amount * rate).quantize(CENT, rounding=ROUND_HALF_UP)
        duty = duty + Money(amount, commodity.value.currency)
    return CustomsDeclaration(consignment, duty)


def has_commodities(declaration: CustomsDeclaration, /) -> Held | None:
    if not declaration.consignment.commodities:
        return Held("nothing declared")
    return None


def known_codes(declaration: CustomsDeclaration, /) -> Held | None:
    for commodity in declaration.consignment.commodities:
        if commodity.hs_code not in HS_RATES:
            return Held(f"unknown HS code {commodity.hs_code}")
    return None


STAGES: tuple[ClearanceStage, ...] = (has_commodities, known_codes)


def clear(
    declaration: CustomsDeclaration, /, *, stages: tuple[ClearanceStage, ...] = STAGES
) -> CustomsDeclaration:
    """Run the stages in order; the first that holds stops the chain and raises."""
    for stage in stages:
        held = stage(declaration)
        if held is not None:
            raise ClearanceHeldError(held)
    return declaration
