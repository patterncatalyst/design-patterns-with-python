import dataclasses
from collections import Counter
from collections.abc import Callable
from decimal import Decimal
from typing import Any, Protocol, runtime_checkable

import pytest
from decorator_proxy.domain import CarrierQuote, CarrierTimeoutError, Consignment, ConsignmentId
from decorator_proxy.layers import BaseRate, Tax
from decorator_proxy.proxy import CarrierGateway


def test_the_proxy_asks_the_gateway_once_per_consignment(
    make_proxy: Callable[[CarrierGateway], CarrierGateway],
    make_gateway: Callable[[int], CarrierGateway],
    consignment: Consignment,
    quoted: CarrierQuote,
    calls: Counter[str],
) -> None:
    proxy = make_proxy(make_gateway(0))

    assert proxy.quote(consignment) == quoted
    assert proxy.quote(consignment) == quoted
    assert calls["quote"] == 1

    other = dataclasses.replace(consignment, id=ConsignmentId("CN-2"))
    proxy.quote(other)
    assert calls["quote"] == 2


def test_the_proxy_forwards_every_booking(
    make_proxy: Callable[[CarrierGateway], CarrierGateway],
    make_gateway: Callable[[int], CarrierGateway],
    consignment: Consignment,
    calls: Counter[str],
) -> None:
    proxy = make_proxy(make_gateway(0))

    assert proxy.book(consignment) == "AC-CN-1"
    assert proxy.book(consignment) == "AC-CN-1"
    assert calls["book"] == 2


def test_a_timed_out_quote_is_not_cached(
    make_proxy: Callable[[CarrierGateway], CarrierGateway],
    make_gateway: Callable[[int], CarrierGateway],
    consignment: Consignment,
    quoted: CarrierQuote,
    calls: Counter[str],
) -> None:
    proxy = make_proxy(make_gateway(1))

    with pytest.raises(CarrierTimeoutError):
        proxy.quote(consignment)
    assert proxy.quote(consignment) == quoted
    assert proxy.quote(consignment) == quoted
    assert calls["quote"] == 2


def test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price(
    make_gateway: Callable[[int], CarrierGateway],
    explicit_proxy: CarrierGateway,
    consignment: Consignment,
    quoted: CarrierQuote,
) -> None:
    base = BaseRate(quoted.price)
    layered = Tax(base, Decimal(21))

    assert explicit_proxy.quote(consignment) == make_gateway(0).quote(consignment)
    assert layered.price(consignment) != base.price(consignment)
    assert explicit_proxy.quote(consignment).price == quoted.price


@runtime_checkable
class _Gateway(Protocol):
    def quote(self, consignment: Consignment, /) -> CarrierQuote: ...

    def book(self, consignment: Consignment, /) -> str: ...


def test_runtime_checkable_does_not_see_attributes_forwarded_by_getattr(
    explicit_proxy: CarrierGateway, forwarding_proxy: Any
) -> None:
    assert isinstance(explicit_proxy, _Gateway)
    assert hasattr(forwarding_proxy, "book")
    assert not isinstance(forwarding_proxy, _Gateway)


def test_a_forwarded_typo_is_reported_against_the_wrapped_gateway(forwarding_proxy: Any) -> None:
    with pytest.raises(AttributeError, match="'ScriptedGateway' object has no attribute 'bok'"):
        _ = forwarding_proxy.bok
