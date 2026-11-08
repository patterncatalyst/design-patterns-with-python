import dataclasses
from collections.abc import Callable
from decimal import Decimal

import pytest
from srp_ocp_lsp.audit import AuditSink
from srp_ocp_lsp.domain import Consignment, Money, RateQuote, Tariff
from srp_ocp_lsp.pricing import TARIFF, BaseRate
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


@pytest.mark.parametrize(
    ("replaced", "expected_fields", "sink_counts"),
    [
        # The tax is a percentage of the net, so a new tariff moves the tax that follows from it.
        ("tariff", {"net", "tax"}, (1, 0)),
        ("tax-rule", {"tax"}, (1, 0)),
        ("audit-sink", set(), (0, 1)),
    ],
    ids=["tariff", "tax-rule", "audit-sink"],
)
def test_each_change_moves_only_the_fields_it_feeds(
    replaced: str,
    expected_fields: set[str],
    sink_counts: tuple[int, int],
    asia_consignment: Consignment,
    records: list[RateQuote],
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

    assert _changed_fields(baseline, changed) == expected_fields
    assert (len(records), len(other_records)) == sink_counts
    assert records + other_records == [changed]


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
