import dataclasses
import inspect
import os
from collections.abc import Callable, Generator, Iterator
from decimal import Decimal
from functools import partial
from types import FunctionType
from typing import Any

import mypy.api
import pytest
from three_way_split import dissolve
from three_way_split.dissolve import (
    GATEWAYS,
    AircoGateway,
    BookingRequest,
    CarrierBase,
    DuplicateCarrierError,
    FastlineGateway,
    PricingRule,
    declare_customs,
    describe,
    find_gateway,
    flat_rate,
    pages,
    per_kg,
    quote,
)
from three_way_split.domain import (
    Booked,
    Cleared,
    Consignment,
    ConsignmentId,
    CustomsHooks,
    Delivered,
    Departed,
    HandlingEvent,
    Loaded,
    Money,
    TrackingHistory,
    Weight,
)

CID = ConsignmentId("CN-00012345")


def test_strategy_slot_accepts_def_lambda_and_partial(consignment: Consignment) -> None:
    from_partial: PricingRule = partial(per_kg, rate=Decimal("2.00"))
    rules: dict[str, PricingRule] = {
        "def": flat_rate,
        "lambda": lambda c: Money(Decimal("9.99"), "EUR"),
        "partial": from_partial,
    }

    prices = {name: quote(consignment, rule).price for name, rule in rules.items()}

    assert prices == {
        "def": Money(Decimal("25.00"), "EUR"),
        "lambda": Money(Decimal("9.99"), "EUR"),
        "partial": Money(Decimal("240.00"), "EUR"),
    }
    assert type(rules["def"]) is FunctionType
    assert type(rules["lambda"]) is FunctionType
    assert isinstance(rules["partial"], partial)
    assert all(not isinstance(rule, type) and callable(rule) for rule in rules.values())


def test_a_class_is_already_a_factory_method() -> None:
    assert GATEWAYS["FASTLINE"] is FastlineGateway
    assert GATEWAYS["AIRCO"] is AircoGateway
    gateway = GATEWAYS["AIRCO"]()
    assert type(gateway) is AircoGateway
    assert GATEWAYS["AIRCO"]() is not gateway


def test_iterator_is_a_lazy_generator() -> None:
    class CountingSource:
        def __init__(self) -> None:
            self.pulled = 0

        def __iter__(self) -> Iterator[HandlingEvent]:
            for number in range(7):
                self.pulled += 1
                yield Booked(consignment_id=CID, location=f"STOP{number}")

    source = CountingSource()
    generator = pages(TrackingHistory(source), 3)

    assert inspect.isgeneratorfunction(pages)
    assert isinstance(generator, Generator)
    assert iter(generator) is generator
    assert source.pulled == 0

    first = next(generator)
    assert len(first) == 3
    assert source.pulled == 3

    assert [len(page) for page in generator] == [3, 1]
    assert source.pulled == 7
    assert list(generator) == []
    with pytest.raises(StopIteration):
        next(generator)


def test_template_method_is_a_function_taking_hooks(consignment: Consignment) -> None:
    steps: list[str] = []

    def classify(c: Consignment) -> str:
        steps.append("classify")
        return "8471.30"

    def assess_duty(c: Consignment, tariff_code: str) -> Money:
        steps.append(f"assess_duty:{tariff_code}")
        return Money(Decimal("12.50"), "EUR")

    def certify(c: Consignment) -> str:
        steps.append("certify")
        return f"CERT-{c.destination}"

    hooks = CustomsHooks(classify=classify, assess_duty=assess_duty, certify=certify)
    declaration = declare_customs(consignment, hooks=hooks)

    assert steps == ["classify", "assess_duty:8471.30", "certify"]
    assert declaration.tariff_code == "8471.30"
    assert declaration.certificate == "CERT-SGSIN"
    assert declaration.duty == Money(Decimal("12.50"), "EUR")
    assert CustomsHooks.__bases__ == (object,)

    steps.clear()

    def classify_medical(c: Consignment) -> str:
        steps.append("classify")
        return "9018.90"

    def assess_exempt(c: Consignment, tariff_code: str) -> Money:
        steps.append(f"assess_duty:{tariff_code}")
        return Money(Decimal("0"), "EUR")

    def certify_exempt(c: Consignment) -> str:
        steps.append("certify")
        return "EXEMPT"

    other = CustomsHooks(
        classify=classify_medical, assess_duty=assess_exempt, certify=certify_exempt
    )
    exempt = declare_customs(consignment, hooks=other)

    assert steps == ["classify", "assess_duty:9018.90", "certify"]
    assert exempt.certificate == "EXEMPT"
    assert exempt.duty == Money(Decimal("0"), "EUR")


def test_builder_is_a_keyword_only_dataclass() -> None:
    build: Callable[..., BookingRequest] = BookingRequest
    with pytest.raises(TypeError, match="positional"):
        build(CID, "NLRTM", "SGSIN", Weight(10.0))

    request = BookingRequest(
        consignment_id=CID, origin="NLRTM", destination="SGSIN", weight=Weight(10.0)
    )
    assert request.carrier == "FASTLINE"
    assert request.insured is False
    assert all(field.kw_only for field in dataclasses.fields(BookingRequest))


def test_prototype_is_replace(consignment: Consignment) -> None:
    heavier = dataclasses.replace(consignment, weight=Weight(200.0))

    assert heavier is not consignment
    assert heavier.weight == Weight(200.0)
    assert consignment.weight == Weight(120.0)
    assert heavier.id == consignment.id
    assert dataclasses.replace(consignment) == consignment


def test_visitor_is_singledispatch_without_accept() -> None:
    events: list[HandlingEvent] = [
        Booked(consignment_id=CID, location="NLRTM"),
        Loaded(consignment_id=CID, location="NLRTM"),
        Departed(consignment_id=CID, location="NLRTM"),
        Cleared(consignment_id=CID, location="SGSIN"),
        Delivered(consignment_id=CID, location="SGSIN"),
    ]

    assert [describe(event) for event in events] == [
        "CN-00012345 booked at NLRTM",
        "CN-00012345 loaded at NLRTM",
        "CN-00012345 departed NLRTM",
        "CN-00012345 cleared customs at SGSIN",
        "CN-00012345 delivered at SGSIN",
    ]
    assert {type(event) for event in events} <= set(describe.registry)
    assert describe(object()) == "unrecognised event"
    assert not any(hasattr(type(event), "accept") for event in events)


_UNGUARDED = """
from three_way_split.dissolve import find_gateway
from three_way_split.domain import Consignment


def book_with(consignment: Consignment) -> str:
    return find_gateway("FASTLINE").book(consignment)
"""

_GUARDED = """
from three_way_split.dissolve import find_gateway
from three_way_split.domain import Consignment


def book_with(consignment: Consignment) -> str:
    gateway = find_gateway("FASTLINE")
    if gateway is None:
        return "unknown carrier"
    return gateway.book(consignment)
"""


def _check(snippet: str) -> tuple[str, int]:
    stdout, _stderr, status = mypy.api.run(
        ["--strict", "--cache-dir", os.devnull, "--no-error-summary", "-c", snippet]
    )
    return stdout, status


def test_null_object_is_an_optional_checked_by_mypy(consignment: Consignment) -> None:
    stdout, status = _check(_UNGUARDED)
    assert status == 1
    assert "[union-attr]" in stdout
    assert "<string>:" in stdout

    stdout, status = _check(_GUARDED)
    assert status == 0
    assert stdout == ""

    assert find_gateway("NOSUCH") is None
    gateway = find_gateway("AIRCO")
    assert gateway is not None
    assert gateway.book(consignment) == "AIRCO:CN-00012345"


def test_value_object_is_a_frozen_dataclass() -> None:
    price = Money(Decimal("10.00"), "EUR")

    assert price == Money(Decimal("10.00"), "EUR")
    assert hash(price) == hash(Money(Decimal("10.00"), "EUR"))
    assert {price: "x"}[Money(Decimal("10.00"), "EUR")] == "x"
    with pytest.raises(dataclasses.FrozenInstanceError):
        price.amount = Decimal("1")  # type: ignore[misc]
    assert not hasattr(price, "__dict__")
    assert price + price == Money(Decimal("20.00"), "EUR")
    with pytest.raises(ValueError, match="cannot add USD to EUR"):
        price + Money(Decimal("1.00"), "USD")


def test_registry_is_init_subclass(monkeypatch: pytest.MonkeyPatch) -> None:
    registry: dict[str, Any] = {}
    monkeypatch.setattr(dissolve, "CARRIERS", registry)

    class Fastline(CarrierBase, code="FASTLINE"):
        def book(self, consignment: Consignment, /) -> str:
            return "booked"

    assert registry == {"FASTLINE": Fastline}

    with pytest.raises(DuplicateCarrierError, match="FASTLINE"):

        class Again(CarrierBase, code="FASTLINE"):
            def book(self, consignment: Consignment, /) -> str:
                return "booked"

    assert registry == {"FASTLINE": Fastline}
