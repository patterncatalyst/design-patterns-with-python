from decimal import Decimal

import pytest
from structural_typing.domain import Consignment, ConsignmentId, HazmatConsignment, Money, Weight
from structural_typing.pricing import (
    GeneralQuoter,
    HazmatQuoter,
    PricingRule,
    flat_rate,
    per_kg,
    price_all,
    price_hazmat,
)


def test_a_general_quoter_serves_hazmat_consignments(
    consignment: Consignment, hazmat: HazmatConsignment
) -> None:
    assert price_hazmat(GeneralQuoter(), [hazmat]) == (Money(Decimal("60.00"), "EUR"),)
    assert price_all(GeneralQuoter(), [consignment, hazmat]) == (
        Money(Decimal("120.00"), "EUR"),
        Money(Decimal("60.00"), "EUR"),
    )


def test_a_hazmat_quoter_fails_on_a_general_consignment_at_runtime(
    consignment: Consignment,
) -> None:
    with pytest.raises(AttributeError, match="un_number"):
        price_all(HazmatQuoter(), [consignment])  # type: ignore[arg-type]


def test_hazmat_quoter_surcharge_follows_the_un_number(hazmat: HazmatConsignment) -> None:
    other = HazmatConsignment(
        id=ConsignmentId("CN-00000003"),
        weight=Weight(50.0),
        destination="NLRTM",
        un_number="UN3480",
    )
    assert price_hazmat(HazmatQuoter(), [hazmat, other]) == (
        Money(Decimal("100.00"), "EUR"),
        Money(Decimal("85.00"), "EUR"),
    )


@pytest.mark.parametrize("un_number", ["UN12", "1203", "un1203", "UN12034"])
def test_hazmat_consignment_validates_its_un_number(un_number: str) -> None:
    with pytest.raises(ValueError, match="un_number must look like UN1203"):
        HazmatConsignment(
            id=ConsignmentId("CN-00000004"),
            weight=Weight(1.0),
            destination="NLRTM",
            un_number=un_number,
        )


def test_callback_protocol_accepts_any_parameter_name(consignment: Consignment) -> None:
    rules: list[PricingRule] = [flat_rate, per_kg]
    assert [rule(consignment) for rule in rules] == [
        Money(Decimal("25.00"), "EUR"),
        Money(Decimal("120.00"), "EUR"),
    ]
