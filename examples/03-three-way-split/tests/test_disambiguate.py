import dataclasses
import importlib
from collections.abc import Iterator
from decimal import Decimal
from typing import Final

import pytest
from three_way_split import dissolve
from three_way_split.disambiguate import (
    BaseRate,
    CarrierGatewayProxy,
    LazyTrackingHistory,
    RateCalculator,
    Surcharge,
    audit_trail,
    audited,
    calculator_for,
    quote_carrier,
)
from three_way_split.dissolve import (
    AircoGateway,
    CarrierBase,
    CarrierGateway,
    FastlineGateway,
    per_kg,
)
from three_way_split.domain import (
    Booked,
    Consignment,
    ConsignmentId,
    HandlingEvent,
    Money,
    Tariff,
    Weight,
)
from three_way_split.loads import LOAD_LOG

HEAVY_FEE: Final = Money(Decimal("15.00"), "EUR")


@pytest.fixture(autouse=True)
def clean_audit_trail() -> Iterator[None]:
    audit_trail.clear()
    yield
    audit_trail.clear()


def test_gof_decorator_wraps_an_instance_at_runtime(consignment: Consignment) -> None:
    base = BaseRate(per_kg)
    light = dataclasses.replace(consignment, weight=Weight(100.0))
    heavy = dataclasses.replace(consignment, weight=Weight(600.0))

    def stack(c: Consignment) -> RateCalculator:
        return calculator_for(c, base, heavy_over=Weight(500.0), heavy_fee=HEAVY_FEE)

    assert stack(light) is base
    wrapped = stack(heavy)
    assert isinstance(wrapped, Surcharge)
    assert wrapped.inner is base
    assert wrapped.price(heavy) == Money(Decimal("720.00"), "EUR") + HEAVY_FEE
    assert base.price(heavy) == Money(Decimal("720.00"), "EUR")
    assert Surcharge.__bases__ == (object,)
    assert isinstance(wrapped, RateCalculator)
    assert isinstance(base, RateCalculator)
    with pytest.raises(dataclasses.FrozenInstanceError):
        wrapped.fee = Money(Decimal("0"), "EUR")  # type: ignore[misc]


def test_decorator_syntax_rebinds_the_name_at_definition_time(consignment: Consignment) -> None:
    sink: list[str] = []

    def quote_plain(c: Consignment, carrier: str) -> Money:
        return Money(Decimal("1.00"), "EUR")

    rebound = audited(sink.append)(quote_plain)

    assert rebound is not quote_plain
    assert rebound.__wrapped__ is quote_plain  # type: ignore[attr-defined]
    assert rebound.__name__ == "quote_plain"
    assert sink == []
    assert rebound(consignment, "AIRCO") == Money(Decimal("1.00"), "EUR")
    assert sink == ["quote_plain"]

    assert quote_carrier.__wrapped__ is not quote_carrier  # type: ignore[attr-defined]
    assert quote_carrier.__name__ == "quote_carrier"
    assert quote_carrier(consignment, "FASTLINE") == Money(Decimal("180.00"), "EUR")
    assert audit_trail == ["quote_carrier"]


def test_the_two_decorators_are_independent(consignment: Consignment) -> None:
    calculator = Surcharge(BaseRate(lambda c: quote_carrier(c, "AIRCO")), HEAVY_FEE)

    assert calculator.price(consignment) == Money(Decimal("360.00"), "EUR") + HEAVY_FEE
    assert audit_trail == ["quote_carrier"]

    assert hasattr(quote_carrier, "__wrapped__")
    assert not hasattr(calculator, "__wrapped__")
    assert not hasattr(quote_carrier, "price")
    assert not hasattr(quote_carrier, "inner")
    assert calculator.inner.price(consignment) == Money(Decimal("360.00"), "EUR")
    assert audit_trail == ["quote_carrier", "quote_carrier"]


def test_module_is_one_instance_for_every_importer() -> None:
    first = importlib.import_module("three_way_split.tariff_table")
    second = importlib.import_module("three_way_split.tariff_table")

    assert first is second
    assert first.TARIFF is second.TARIFF
    assert isinstance(first.TARIFF, Tariff)
    assert first.TARIFF.rate_for("ASIA") == Money(Decimal("2.40"), "EUR")
    assert LOAD_LOG.count("tariff_table") == 1


def test_cached_property_is_lazy_initialisation_without_a_proxy() -> None:
    loads: list[int] = []
    event = Booked(consignment_id=ConsignmentId("CN-00012345"), location="NLRTM")

    def loader() -> list[HandlingEvent]:
        loads.append(1)
        return [event]

    history = LazyTrackingHistory(loader)
    assert loads == []
    assert "events" not in vars(history)

    assert history.events == (event,)
    assert loads == [1]
    assert "events" in vars(history)

    assert history.events is history.events
    assert loads == [1]


def test_proxy_forwards_only_missing_attributes(consignment: Consignment) -> None:
    class CountingGateway:
        code = "FASTLINE"

        def __init__(self) -> None:
            self.calls = 0

        def book(self, consignment: Consignment, /) -> str:
            self.calls += 1
            return f"REF-{self.calls}"

    inner = CountingGateway()
    proxy = CarrierGatewayProxy(inner)

    assert "book" in vars(CarrierGatewayProxy)
    assert "code" not in vars(CarrierGatewayProxy)
    assert proxy.code == "FASTLINE"
    assert proxy.book(consignment) == "REF-1"
    assert proxy.book(consignment) == "REF-1"
    assert inner.calls == 1

    with pytest.raises(AttributeError):
        proxy.missing  # noqa: B018
    with pytest.raises(AttributeError):
        proxy._missing  # noqa: B018


def test_protocol_is_structural_and_abc_is_nominal(consignment: Consignment) -> None:
    fastline: CarrierGateway = FastlineGateway()

    assert CarrierGateway not in FastlineGateway.__mro__
    assert isinstance(fastline, CarrierGateway)
    assert isinstance(AircoGateway(), CarrierGateway)
    assert not isinstance(fastline, CarrierBase)

    class Unrelated:
        def book(self, consignment: Consignment, /) -> str:
            return "unrelated"

    assert isinstance(Unrelated(), CarrierGateway)
    assert not isinstance(Unrelated(), CarrierBase)

    class Incomplete(CarrierBase, code="INCOMPLETE-WITNESS"):
        pass

    try:
        with pytest.raises(TypeError, match="abstract"):
            Incomplete()  # type: ignore[abstract]
    finally:
        dissolve.CARRIERS.pop("INCOMPLETE-WITNESS")
