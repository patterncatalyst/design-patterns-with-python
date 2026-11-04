from decimal import Decimal

import pytest
from strategy_callable.domain import Consignment, Money, RatingError
from strategy_callable.rules import RATE_RULES, quote


@pytest.mark.parametrize("name", ["flat", "per-kg", "zone"])
def test_a_quote_records_the_rule_that_priced_it(consignment: Consignment, name: str) -> None:
    result = quote(consignment, name)
    assert result.rule == name
    assert result.consignment_id == consignment.id
    assert result.price == RATE_RULES[name](consignment)
    assert quote(consignment, "zone").price == Money(Decimal("5.00"), "EUR")


def test_an_unknown_rule_name_is_a_rating_error(consignment: Consignment) -> None:
    with pytest.raises(RatingError, match="no pricing rule named 'express'") as raised:
        quote(consignment, "express")
    assert raised.value.__cause__ is None
    assert raised.value.__suppress_context__


def test_the_rule_registry_is_read_only() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        RATE_RULES["express"] = RATE_RULES["flat"]  # type: ignore[index]
    assert not isinstance(RATE_RULES, dict)
    assert sorted(RATE_RULES) == ["flat", "per-kg", "zone"]
