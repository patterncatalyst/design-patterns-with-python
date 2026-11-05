from collections.abc import Callable
from decimal import Decimal

import pytest
from decorator_proxy.domain import Consignment, ConsignmentId, Money, RatingError, Weight
from decorator_proxy.layers import (
    DANGEROUS_GOODS_FEE,
    HEAVY_FEE,
    HEAVY_OVER,
    TAX_RATES,
    BaseRate,
    Discount,
    RateCalculator,
    Surcharge,
    Tax,
    compose,
    discount,
    layers_for,
    surcharge,
    tax,
)

_PER_KG = Money(Decimal("1.20"), "EUR")
_FEE = Money(Decimal("15.00"), "EUR")


def _hundred_kilograms() -> Consignment:
    return Consignment(id=ConsignmentId("CN-9"), weight=Weight(Decimal(100)), destination="NLRTM")


def test_a_layer_wraps_a_calculator_and_leaves_it_unchanged() -> None:
    base = BaseRate(_PER_KG)
    consignment = _hundred_kilograms()
    before = base.price(consignment)

    layered = Surcharge(base, _FEE)

    assert layered.inner is base
    assert layered.price(consignment) == Money(Decimal("135.00"), "EUR")
    assert base.price(consignment) == before == Money(Decimal("120.00"), "EUR")
    assert base == BaseRate(_PER_KG)


@pytest.mark.parametrize(
    ("stack", "expected"),
    [
        (lambda base: Tax(Surcharge(base, _FEE), Decimal(21)), "163.35"),
        (lambda base: Surcharge(Tax(base, Decimal(21)), _FEE), "160.20"),
        (lambda base: Discount(Surcharge(base, _FEE), Decimal(10)), "121.50"),
        (lambda base: Surcharge(Discount(base, Decimal(10)), _FEE), "123.00"),
    ],
    ids=["tax-outside", "surcharge-outside", "discount-outside", "surcharge-outside-discount"],
)
def test_layer_order_changes_the_price_when_a_fee_is_added(
    stack: Callable[[RateCalculator], RateCalculator], expected: str
) -> None:
    calculator = stack(BaseRate(_PER_KG))

    price = calculator.price(_hundred_kilograms())

    assert str(price.amount) == expected
    assert price.currency == "EUR"


def test_two_percentage_layers_agree_before_rounding_and_can_split_by_a_cent() -> None:
    def both_ways(per_kg: str, kilograms: int) -> tuple[Money, Money]:
        base = BaseRate(Money(Decimal(per_kg), "EUR"))
        consignment = Consignment(
            id=ConsignmentId("CN-9"), weight=Weight(Decimal(kilograms)), destination="NLRTM"
        )
        discount_then_tax = Tax(Discount(base, Decimal(10)), Decimal(21))
        tax_then_discount = Discount(Tax(base, Decimal(21)), Decimal(10))
        return discount_then_tax.price(consignment), tax_then_discount.price(consignment)

    agree = both_ways("1.20", 100)
    split = both_ways("0.05", 1)

    assert agree[0] == agree[1] == Money(Decimal("130.68"), "EUR")
    assert split == (Money(Decimal("0.06"), "EUR"), Money(Decimal("0.05"), "EUR"))


_LIGHT = Consignment(id=ConsignmentId("L"), weight=Weight(Decimal(10)), destination="SGSIN")
_HEAVY = Consignment(id=ConsignmentId("H"), weight=Weight(Decimal(600)), destination="NLRTM")
_DANGEROUS = Consignment(
    id=ConsignmentId("D"), weight=Weight(Decimal(10)), destination="NLRTM", dangerous_goods=True
)


@pytest.mark.parametrize(
    ("consignment", "layer_count", "base_price", "price"),
    [
        (_LIGHT, 1, "12.00", "13.08"),
        (_HEAVY, 2, "720.00", "889.35"),
        (_DANGEROUS, 2, "12.00", "44.77"),
    ],
    ids=["light", "heavy", "dangerous-goods"],
)
def test_the_layers_for_a_consignment_are_chosen_while_the_program_runs(
    consignment: Consignment, layer_count: int, base_price: str, price: str
) -> None:
    base = BaseRate(_PER_KG)

    layers = layers_for(consignment)
    stack = compose(base, layers)

    assert len(layers) == layer_count
    assert str(stack.price(consignment).amount) == price
    assert str(base.price(consignment).amount) == base_price


def test_the_heavy_threshold_is_exclusive() -> None:
    at_the_limit = Consignment(id=ConsignmentId("T"), weight=HEAVY_OVER, destination="NLRTM")
    over = Consignment(
        id=ConsignmentId("T"), weight=Weight(HEAVY_OVER.kilograms + 1), destination="NLRTM"
    )

    assert len(layers_for(at_the_limit)) == 1
    assert len(layers_for(over)) == 2


def test_the_fees_are_in_the_order_the_rules_say() -> None:
    both = Consignment(
        id=ConsignmentId("B"),
        weight=Weight(Decimal(600)),
        destination="NLRTM",
        dangerous_goods=True,
    )

    stack = compose(BaseRate(_PER_KG), layers_for(both))

    assert isinstance(stack, Tax)
    assert isinstance(stack.inner, Surcharge)
    assert stack.inner.fee == DANGEROUS_GOODS_FEE
    assert isinstance(stack.inner.inner, Surcharge)
    assert stack.inner.inner.fee == HEAVY_FEE


def test_an_unknown_destination_country_is_a_rating_error() -> None:
    nowhere = Consignment(id=ConsignmentId("X"), weight=Weight(Decimal(10)), destination="XXAAA")

    with pytest.raises(RatingError, match="no tax rate for country 'XX'"):
        layers_for(nowhere)


def test_layer_stacks_compare_by_value() -> None:
    def stack(percent: int) -> object:
        return compose(BaseRate(_PER_KG), [surcharge(_FEE), tax(Decimal(percent))])

    assert stack(21) == stack(21)
    assert hash(stack(21)) == hash(stack(21))
    assert stack(21) != stack(9)
    assert repr(stack(21)).startswith("Tax(inner=Surcharge(inner=BaseRate(")


def test_compose_wraps_the_last_layer_outermost() -> None:
    stack = compose(BaseRate(_PER_KG), [surcharge(_FEE), tax(Decimal(21)), discount(Decimal(5))])

    assert type(stack) is Discount
    assert type(stack.inner) is Tax
    assert type(stack.inner.inner) is Surcharge
    assert type(stack.inner.inner.inner) is BaseRate


def test_a_layer_refuses_a_fee_in_another_currency() -> None:
    stack = compose(BaseRate(_PER_KG), [surcharge(Money(Decimal("15.00"), "USD"))])

    with pytest.raises(RatingError, match="cannot add USD to EUR"):
        stack.price(_hundred_kilograms())


@pytest.mark.parametrize("kilograms", [Decimal(0), Decimal(-1), Decimal("NaN")])
def test_a_weight_that_is_not_positive_and_finite_is_refused(kilograms: Decimal) -> None:
    with pytest.raises(ValueError, match="weight must be positive and finite"):
        Weight(kilograms)


def test_the_tax_rates_are_read_only() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        TAX_RATES["NL"] = Decimal(0)  # type: ignore[index]
    assert not isinstance(TAX_RATES, dict)
