from dataclasses import dataclass
from decimal import Decimal

import pytest
from feature_spikes.decorator_vs_syntax import (
    BaseRate,
    CarrierTimeout,
    Consignment,
    FuelSurcharge,
    Layer,
    RateCalculator,
    Vat,
    VolumeDiscount,
    audited,
    compose,
    retry,
)

D = Decimal
CONSIGNMENT = Consignment("C-1", weight_kg=D(100), parcels=12)
BASE = BaseRate(per_kg=D(2))  # 200


def discount() -> Layer:
    return lambda inner: VolumeDiscount(inner, min_parcels=10, rate=D("0.1"))


def vat() -> Layer:
    return lambda inner: Vat(inner, rate=D("0.2"))


def fuel() -> Layer:
    return lambda inner: FuelSurcharge(inner, rate=D("0.05"))


def test_wrapped_object_still_satisfies_protocol() -> None:
    calculator: RateCalculator = compose(BASE, [fuel(), discount(), vat()])
    assert calculator.quote(CONSIGNMENT) == D(200) * D("1.05") * D("0.9") * D("1.2")


@dataclass(frozen=True, slots=True)
class HandlingFee:
    """A non-multiplicative layer: an additive fee, so position in the stack matters."""

    inner: RateCalculator
    fee: Decimal

    def quote(self, c: Consignment) -> Decimal:
        return self.inner.quote(c) + self.fee


def handling() -> Layer:
    return lambda inner: HandlingFee(inner, D(10))


def test_stacking_order_changes_result() -> None:
    discount_then_vat = compose(BASE, [discount(), handling(), vat()])
    vat_then_discount = compose(BASE, [vat(), handling(), discount()])
    assert discount_then_vat.quote(CONSIGNMENT) == (D(200) * D("0.9") + 10) * D("1.2")
    assert vat_then_discount.quote(CONSIGNMENT) == (D(200) * D("1.2") + 10) * D("0.9")
    assert discount_then_vat.quote(CONSIGNMENT) != vat_then_discount.quote(CONSIGNMENT)


def test_purely_multiplicative_layers_commute() -> None:
    # Caveat for the chapter: discount-then-VAT equals VAT-then-discount unless a layer is
    # additive, capped or rounded. Choose a non-commuting example when order is the point.
    assert compose(BASE, [discount(), vat()]).quote(CONSIGNMENT) == compose(
        BASE, [vat(), discount()]
    ).quote(CONSIGNMENT)


def test_rounding_layer_makes_order_matter() -> None:
    @dataclass(frozen=True, slots=True)
    class Round:
        inner: RateCalculator

        def quote(self, c: Consignment) -> Decimal:
            return self.inner.quote(c).quantize(D("1"))

    odd = Consignment("C-2", weight_kg=D("33.3"), parcels=12)
    assert compose(BASE, [Round, vat()]).quote(odd) != compose(BASE, [vat(), Round]).quote(odd)


def test_layers_are_added_and_removed_at_runtime_per_consignment() -> None:
    small = Consignment("C-3", weight_kg=D(10), parcels=1)
    config: dict[str, list[Layer]] = {"C-1": [discount(), vat()], "C-3": []}
    assert compose(BASE, config["C-1"]).quote(CONSIGNMENT) == D(200) * D("0.9") * D("1.2")
    assert compose(BASE, config["C-3"]).quote(small) == D(20)
    config["C-3"].append(vat())
    assert compose(BASE, config["C-3"]).quote(small) == D(20) * D("1.2")
    config["C-3"].clear()
    assert compose(BASE, config["C-3"]).quote(small) == D(20)


def test_same_base_instance_is_reused_not_modified() -> None:
    wrapped = Vat(BASE, rate=D("0.2"))
    assert wrapped.inner is BASE
    assert BASE.quote(CONSIGNMENT) == D(200)


def test_retry_reinvokes_on_listed_exception_then_succeeds() -> None:
    calls: list[str] = []

    @retry(attempts=3, on=(CarrierTimeout,))
    def quote_carrier(carrier: str, c: Consignment) -> Decimal:
        calls.append(carrier)
        if len(calls) < 3:
            raise CarrierTimeout(carrier)
        return D(5)

    assert quote_carrier("ACME", CONSIGNMENT) == D(5)
    assert calls == ["ACME"] * 3


def test_retry_gives_up_after_n_attempts() -> None:
    calls = 0

    @retry(attempts=3, on=(CarrierTimeout,))
    def quote_carrier(carrier: str) -> Decimal:
        nonlocal calls
        calls += 1
        raise CarrierTimeout(carrier)

    with pytest.raises(CarrierTimeout):
        quote_carrier("ACME")
    assert calls == 3


def test_retry_does_not_catch_unlisted_exceptions() -> None:
    calls = 0

    @retry(attempts=3, on=(CarrierTimeout,))
    def quote_carrier() -> Decimal:
        nonlocal calls
        calls += 1
        raise ValueError

    with pytest.raises(ValueError):  # noqa: PT011 - the type is the whole assertion
        quote_carrier()
    assert calls == 1


def test_audited_records_calls_to_injected_sink() -> None:
    records: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    @audited(lambda name, args, kwargs: records.append((name, args, kwargs)))
    def quote_carrier(carrier: str, *, express: bool = False) -> Decimal:
        return D(7) if express else D(5)

    assert quote_carrier("ACME", express=True) == D(7)
    assert quote_carrier("ZED") == D(5)
    assert records == [
        ("quote_carrier", ("ACME",), {"express": True}),
        ("quote_carrier", ("ZED",), {}),
    ]


def test_decorators_preserve_name_doc_and_wrapped() -> None:
    def quote_carrier(carrier: str) -> Decimal:
        """Ask a carrier."""
        return D(1)

    original = quote_carrier
    wrapped = retry(attempts=2, on=(CarrierTimeout,))(audited(lambda *_: None)(quote_carrier))
    assert wrapped.__name__ == "quote_carrier"
    assert wrapped.__doc__ == "Ask a carrier."
    assert wrapped.__wrapped__.__wrapped__ is original  # type: ignore[attr-defined]


def test_decorator_syntax_replaces_the_function_object_at_definition_time() -> None:
    def plain(carrier: str) -> Decimal:
        return D(1)

    before = plain

    @retry(attempts=2, on=(CarrierTimeout,))
    def decorated(carrier: str) -> Decimal:
        return D(1)

    assert plain is before  # no decorator: name still bound to the original
    assert decorated is not decorated.__wrapped__  # type: ignore[attr-defined]
    assert decorated.__wrapped__.__name__ == "decorated"  # type: ignore[attr-defined]
    # '@' is only sugar: the manual spelling produces the same kind of replacement
    manual = retry(attempts=2, on=(CarrierTimeout,))(plain)
    assert manual is not plain
    assert manual.__wrapped__ is plain  # type: ignore[attr-defined]


def test_gof_decorators_wrap_instances_and_leave_classes_alone() -> None:
    before = BaseRate.quote
    stacked = compose(BASE, [vat()])
    assert BaseRate.quote is before  # the class and the inner instance are untouched
    assert stacked is not BASE
    assert BASE.quote(CONSIGNMENT) == D(200)


def test_decorator_syntax_is_not_needed_for_gof_decorator() -> None:
    # No '@' anywhere in the GoF composition; and '@' wrappers never implement RateCalculator.
    @audited(lambda *_: None)
    def quote_carrier(c: Consignment) -> Decimal:
        return D(1)

    assert not hasattr(quote_carrier, "quote")
