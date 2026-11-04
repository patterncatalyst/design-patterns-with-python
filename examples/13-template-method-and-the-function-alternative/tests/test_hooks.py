import dataclasses
from collections.abc import Callable
from decimal import Decimal
from functools import partial
from typing import Any

import pytest
from template_method.declarer import NetherlandsDeclarer
from template_method.domain import (
    Commodity,
    Consignment,
    CustomsDeclaration,
    CustomsError,
    DeclarationLine,
    Money,
)
from template_method.hooks import (
    EU_SCHEDULE,
    NETHERLANDS,
    SINGAPORE,
    CustomsHooks,
    declare_customs,
    lookup_tariff_code,
    no_extra_documents,
    schedule_duty,
)

type Declare = Callable[[Consignment], CustomsDeclaration]
type MakeConsignment = Callable[..., Consignment]


def test_declare_customs_runs_its_steps_in_order(consignment: Consignment) -> None:
    calls: list[str] = []

    def classify(commodity: Commodity) -> str:
        calls.append(f"classify:{commodity.description}")
        return "0000.00"

    def duty(lines: tuple[DeclarationLine, ...]) -> Money:
        calls.append("duty")
        return Money(Decimal("0.00"), "EUR")

    def extra_documents(consignment: Consignment, /) -> tuple[str, ...]:
        calls.append("extra_documents")
        return ()

    hooks = CustomsHooks(
        country="NL", classify=classify, duty=duty, extra_documents=extra_documents
    )
    declare_customs(consignment, hooks=hooks)
    assert calls == ["classify:laptops", "classify:cotton t-shirts", "duty", "extra_documents"]


def test_a_hook_left_out_takes_its_default(consignment: Consignment) -> None:
    assert SINGAPORE.extra_documents is no_extra_documents
    declaration = declare_customs(consignment, hooks=SINGAPORE)
    assert declaration.documents == ("commercial invoice",)


def test_a_declaration_needs_at_least_one_commodity(
    declare: Declare, make_consignment: MakeConsignment
) -> None:
    with pytest.raises(CustomsError, match="has no commodities to declare"):
        declare(make_consignment())


def test_a_declaration_in_two_currencies_is_refused(
    declare: Declare, make_consignment: MakeConsignment
) -> None:
    mixed = make_consignment(
        Commodity("laptops", Money(Decimal("1200.00"), "EUR")),
        Commodity("cotton t-shirts", Money(Decimal("800.00"), "SGD")),
    )
    with pytest.raises(CustomsError, match="mixed currencies: EUR and SGD"):
        declare(mixed)


def test_the_commercial_invoice_is_always_first(declare: Declare, consignment: Consignment) -> None:
    documents = declare(consignment).documents
    assert documents[0] == "commercial invoice"
    assert documents == ("commercial invoice", "EUR.1 movement certificate")


def test_a_required_hook_cannot_be_left_out() -> None:
    duty = partial(schedule_duty, schedule=EU_SCHEDULE)
    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'classify'"):
        CustomsHooks(country="NL", duty=duty)  # type: ignore[call-arg]


def test_an_unclassified_commodity_is_refused(
    declare: Declare, make_consignment: MakeConsignment
) -> None:
    unknown = make_consignment(Commodity("antique harpsichord", Money(Decimal("900.00"), "EUR")))
    with pytest.raises(
        CustomsError, match="no tariff code for 'antique harpsichord' in NL"
    ) as info:
        declare(unknown)
    assert info.value.__suppress_context__


def test_duty_rounds_half_up_to_cents() -> None:
    # 28.50 at 5% is 1.425: half up gives 1.43, half even would give 1.42.
    line = DeclarationLine("cotton t-shirts", "6109.10", Money(Decimal("28.50"), "EUR"))
    duty = schedule_duty((line,), schedule={"6109.10": Decimal("0.05")})
    assert duty == Money(Decimal("1.43"), "EUR")


@pytest.mark.parametrize("form", ["hooks", "template"])
def test_a_tariff_code_without_a_duty_rate_is_refused(
    form: str, make_consignment: MakeConsignment
) -> None:
    classification = {"drones": "8806.21"}
    drones = make_consignment(Commodity("drones", Money(Decimal("500.00"), "EUR")))
    if form == "hooks":
        hooks = CustomsHooks(
            country="NL",
            classify=partial(lookup_tariff_code, classification, country="NL"),
            duty=partial(schedule_duty, schedule=EU_SCHEDULE),
        )
        declare: Declare = partial(declare_customs, hooks=hooks)
    else:
        declare = NetherlandsDeclarer(classification=classification, schedule=EU_SCHEDULE).declare
    with pytest.raises(CustomsError, match=r"no duty rate for 8806\.21") as info:
        declare(drones)
    assert info.value.__suppress_context__


def test_a_declaration_lists_a_line_per_commodity_and_totals_them(
    declare: Declare, consignment: Consignment
) -> None:
    declaration = declare(consignment)
    assert [(line.description, line.tariff_code) for line in declaration.lines] == [
        ("laptops", "8471.30"),
        ("cotton t-shirts", "6109.10"),
    ]
    assert declaration.country == "NL"
    assert declaration.declared_value == Money(Decimal("2000.00"), "EUR")
    assert declaration.duty == Money(Decimal("96.00"), "EUR")


def _assert_frozen(value: Any) -> None:
    name = dataclasses.fields(value)[0].name
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(value, name, None)


def test_every_value_in_the_model_is_frozen(consignment: Consignment) -> None:
    declaration = declare_customs(consignment, hooks=NETHERLANDS)
    for value in (
        declaration.duty,
        consignment,
        consignment.commodities[0],
        declaration,
        declaration.lines[0],
        NETHERLANDS,
    ):
        _assert_frozen(value)
