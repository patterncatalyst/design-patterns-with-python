import dataclasses
from collections.abc import Callable
from decimal import Decimal

import pytest
from srp_ocp_lsp.audit import AuditSink
from srp_ocp_lsp.domain import Consignment, Money, RateQuote, Tariff
from srp_ocp_lsp.pricing import FLAT_BY_ZONE, TARIFF, BaseRate
from srp_ocp_lsp.rating import quote
from srp_ocp_lsp.tax import TAX_RULES, TaxRule, percent


def _changed_fields(before: RateQuote, after: RateQuote) -> set[str]:
    return {
        field.name
        for field in dataclasses.fields(RateQuote)
        if getattr(before, field.name) != getattr(after, field.name)
    }


def _double_tariff() -> Tariff:
    return Tariff(
        {
            zone: Money(rate.amount * 2, rate.currency)
            for zone, rate in TARIFF.per_kg_by_zone.items()
        }
    )


@pytest.mark.parametrize("replaced", ["tariff", "tax-rule", "audit-sink"])
def test_each_change_moves_only_the_fields_it_feeds(
    replaced: str, asia_consignment: Consignment, records: list[RateQuote]
) -> None:
    baseline = quote(
        asia_consignment, calculator=BaseRate(TARIFF), tax_rules=TAX_RULES, audit=records.append
    )
    records.clear()

    calculator = BaseRate(TARIFF)
    tax_rules: dict[str, TaxRule] = dict(TAX_RULES)
    other_records: list[RateQuote] = []
    sink: AuditSink = records.append
    match replaced:
        case "tariff":
            calculator = BaseRate(_double_tariff())
        case "tax-rule":
            tax_rules["SG"] = percent(Decimal("12"))
        case _:
            sink = other_records.append

    changed = quote(asia_consignment, calculator=calculator, tax_rules=tax_rules, audit=sink)

    # The tax is a percentage of the net, so a new tariff moves the tax that follows from it.
    expected = {"tariff": {"net", "tax"}, "tax-rule": {"tax"}, "audit-sink": set()}[replaced]
    assert _changed_fields(baseline, changed) == expected
    if replaced == "audit-sink":
        assert other_records == [changed]
        assert records == []
    else:
        assert records == [changed]


def test_audit_receives_exactly_the_quote_returned(
    eu_consignment: Consignment, records: list[RateQuote]
) -> None:
    result = quote(
        eu_consignment,
        calculator=BaseRate(TARIFF),
        tax_rules={"NL": percent(Decimal("21"))},
        audit=records.append,
    )

    assert records == [result]
    assert records[0] is result


def test_pricing_and_tax_run_alone(asia_consignment: Consignment) -> None:
    net = BaseRate(TARIFF).price(asia_consignment)
    tax_rule: Callable[[Money], Money] = percent(Decimal("9"))

    assert net == Money(Decimal("408.00"), "EUR")
    assert tax_rule(Money(Decimal("408.00"), "EUR")) == Money(Decimal("36.72"), "EUR")
    assert FLAT_BY_ZONE["ASIA"] == Money(Decimal("60.00"), "EUR")
