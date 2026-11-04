from decimal import Decimal

import pytest
from srp_ocp_lsp.domain import Consignment, ConsignmentId, Money, RateQuote, RatingError, Weight
from srp_ocp_lsp.pricing import TARIFF, BaseRate
from srp_ocp_lsp.rating import quote
from srp_ocp_lsp.tax import TAX_RULES


def exempt(net: Money) -> Money:
    return Money(Decimal("0.00"), net.currency)


def test_a_new_tax_rule_is_added_without_editing_quote(records: list[RateQuote]) -> None:
    hong_kong = Consignment(
        id=ConsignmentId("CN-00000003"), weight=Weight(50.0), zone="ASIA", destination="HKHKG"
    )

    result = quote(
        hong_kong,
        calculator=BaseRate(TARIFF),
        tax_rules={**TAX_RULES, "HK": exempt},
        audit=records.append,
    )

    assert result.net == Money(Decimal("170.00"), "EUR")
    assert result.tax == Money(Decimal("0.00"), "EUR")
    assert "HK" not in TAX_RULES


def test_default_tax_table_is_read_only() -> None:
    with pytest.raises(TypeError):
        TAX_RULES["HK"] = exempt  # type: ignore[index]


def test_missing_tax_rule_is_a_rating_error(records: list[RateQuote]) -> None:
    new_york = Consignment(
        id=ConsignmentId("CN-00000004"), weight=Weight(10.0), zone="AMERICAS", destination="USNYC"
    )

    with pytest.raises(RatingError, match="US"):
        quote(new_york, calculator=BaseRate(TARIFF), tax_rules=TAX_RULES, audit=records.append)

    assert records == []
