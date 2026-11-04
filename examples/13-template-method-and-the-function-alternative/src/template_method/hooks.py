"""The function form of Template Method: fixed steps in declare_customs, hooks for the rest."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from functools import partial

from template_method.domain import (
    Commodity,
    Consignment,
    CustomsDeclaration,
    CustomsError,
    DeclarationLine,
    Money,
)

_CENT = Decimal("0.01")

type Classifier = Callable[[Commodity], str]
type DutyRule = Callable[[tuple[DeclarationLine, ...]], Money]
type DocumentRule = Callable[[Consignment], tuple[str, ...]]


def no_extra_documents(consignment: Consignment, /) -> tuple[str, ...]:
    return ()


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomsHooks:
    """The steps that vary by destination. Classification and duty are required."""

    country: str
    classify: Classifier
    duty: DutyRule
    extra_documents: DocumentRule = no_extra_documents


def lookup_tariff_code(table: Mapping[str, str], commodity: Commodity, country: str) -> str:
    """Classify a commodity by description, or refuse when the table has no code for it."""
    try:
        return table[commodity.description]
    except KeyError:
        raise CustomsError(f"no tariff code for {commodity.description!r} in {country}") from None


def schedule_duty(lines: tuple[DeclarationLine, ...], *, schedule: Mapping[str, Decimal]) -> Money:
    """Sum a percentage duty per line, rounded half up to the cent."""
    total = Decimal(0)
    for line in lines:
        try:
            rate = schedule[line.tariff_code]
        except KeyError:
            raise CustomsError(f"no duty rate for {line.tariff_code}") from None
        total += line.value.amount * rate
    return Money(total.quantize(_CENT, rounding=ROUND_HALF_UP), lines[0].value.currency)


def declare_customs(consignment: Consignment, *, hooks: CustomsHooks) -> CustomsDeclaration:
    """Issue a declaration. The order and the invariant steps are fixed; hooks fill the rest."""
    if not consignment.commodities:
        raise CustomsError(f"consignment {consignment.id} has no commodities to declare")
    lines = tuple(
        DeclarationLine(commodity.description, hooks.classify(commodity), commodity.value)
        for commodity in consignment.commodities
    )
    values = [line.value for line in lines]
    declared_value = sum(values[1:], values[0])
    duty = hooks.duty(lines)
    documents = ("commercial invoice", *hooks.extra_documents(consignment))
    return CustomsDeclaration(consignment.id, hooks.country, lines, declared_value, duty, documents)


EU_CLASSIFICATION: Mapping[str, str] = frozendict(
    {"laptops": "8471.30", "cotton t-shirts": "6109.10"}
)
EU_SCHEDULE: Mapping[str, Decimal] = frozendict(
    {"8471.30": Decimal("0.00"), "6109.10": Decimal("0.12")}
)
SG_CLASSIFICATION: Mapping[str, str] = frozendict(
    {"laptops": "8471.30", "cotton t-shirts": "6109.10"}
)


def _no_import_duty(lines: tuple[DeclarationLine, ...]) -> Money:
    return Money(Decimal("0.00"), lines[0].value.currency)


SINGAPORE = CustomsHooks(
    country="SG",
    classify=partial(lookup_tariff_code, SG_CLASSIFICATION, country="SG"),
    duty=_no_import_duty,
)

NETHERLANDS = CustomsHooks(
    country="NL",
    classify=partial(lookup_tariff_code, EU_CLASSIFICATION, country="NL"),
    duty=partial(schedule_duty, schedule=EU_SCHEDULE),
    extra_documents=lambda consignment: ("EUR.1 movement certificate",),
)
