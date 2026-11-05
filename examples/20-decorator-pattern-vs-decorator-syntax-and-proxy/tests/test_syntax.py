import inspect
from collections import Counter
from collections.abc import Callable
from decimal import Decimal
from functools import cache, wraps

import pytest
from decorator_proxy.domain import CarrierQuote, CarrierTimeoutError, Consignment, Money
from decorator_proxy.layers import BaseRate, Surcharge
from decorator_proxy.proxy import CarrierGateway
from decorator_proxy.syntax import audited, quote_carrier, retry

_FEE = Money(Decimal("15.00"), "EUR")


def test_the_at_sign_rebinds_the_name_once_at_definition_time(
    consignment: Consignment, make_gateway: Callable[[int], CarrierGateway]
) -> None:
    applied: list[str] = []

    def counting[**P, R](func: Callable[P, R]) -> Callable[P, R]:
        applied.append(func.__name__)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)

        return wrapper

    @counting
    def quote(gateway: CarrierGateway, consignment: Consignment) -> CarrierQuote:
        return gateway.quote(consignment)

    assert applied == ["quote"]
    quote(make_gateway(0), consignment)
    quote(make_gateway(0), consignment)
    assert applied == ["quote"]
    assert quote.__wrapped__ is not quote  # type: ignore[attr-defined]
    assert quote_carrier.__wrapped__ is not quote_carrier  # type: ignore[attr-defined]


def test_retry_calls_again_on_a_listed_error_and_gives_up_after_the_last_attempt(
    consignment: Consignment, make_gateway: Callable[[int], CarrierGateway], calls: Counter[str]
) -> None:
    assert quote_carrier(make_gateway(2), consignment).carrier == "AIRCO"
    assert calls["quote"] == 3

    calls.clear()
    with pytest.raises(CarrierTimeoutError, match="no answer for CN-1"):
        quote_carrier(make_gateway(3), consignment)
    assert calls["quote"] == 3


def test_retry_lets_an_unlisted_error_through() -> None:
    attempts: list[int] = []

    @retry(attempts=3, on=(CarrierTimeoutError,))
    def refuse() -> None:
        attempts.append(1)
        raise ValueError("not a timeout")

    with pytest.raises(ValueError, match="not a timeout"):
        refuse()
    assert attempts == [1]


@pytest.mark.parametrize("attempts", [0, -1])
def test_retry_refuses_fewer_than_one_attempt(attempts: int) -> None:
    with pytest.raises(ValueError, match="attempts must be at least 1"):
        retry(attempts=attempts, on=(CarrierTimeoutError,))


def test_audited_reports_each_call_to_the_injected_sink() -> None:
    sink: list[str] = []

    @audited(sink.append)
    def quote_nothing() -> None: ...

    quote_nothing()
    quote_nothing()

    assert sink == ["quote_nothing", "quote_nothing"]


@pytest.mark.parametrize(
    ("order", "reports"), [("audit-outside", 1), ("retry-outside", 3)], ids=lambda value: str(value)
)
def test_syntax_stacking_order_decides_whether_each_attempt_is_audited(
    order: str,
    reports: int,
    consignment: Consignment,
    make_gateway: Callable[[int], CarrierGateway],
) -> None:
    sink: list[str] = []
    quote: Callable[[CarrierGateway, Consignment], CarrierQuote]
    if order == "audit-outside":

        @audited(sink.append)
        @retry(attempts=3, on=(CarrierTimeoutError,))
        def audit_outside(gateway: CarrierGateway, consignment: Consignment) -> CarrierQuote:
            return gateway.quote(consignment)

        quote = audit_outside
    else:

        @retry(attempts=3, on=(CarrierTimeoutError,))
        @audited(sink.append)
        def retry_outside(gateway: CarrierGateway, consignment: Consignment) -> CarrierQuote:
            return gateway.quote(consignment)

        quote = retry_outside

    quote(make_gateway(2), consignment)

    assert len(sink) == reports


def test_rebound_functions_do_not_compare_by_value() -> None:
    def quote() -> None: ...

    first = retry(attempts=3, on=(CarrierTimeoutError,))(quote)
    second = retry(attempts=3, on=(CarrierTimeoutError,))(quote)
    base = BaseRate(Money(Decimal("1.20"), "EUR"))

    assert first != second
    assert Surcharge(base, _FEE) == Surcharge(base, _FEE)


def test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped() -> None:
    layer = Surcharge(BaseRate(Money(Decimal("1.20"), "EUR")), _FEE)

    assert not hasattr(quote_carrier, "price")
    assert not hasattr(layer, "__wrapped__")
    assert hasattr(layer, "price")


def test_a_decorator_may_return_an_object_that_is_not_a_function() -> None:
    @cache
    def lookup(code: str) -> str:
        return code

    returned: object = lookup
    assert hasattr(returned, "cache_info")
    assert not inspect.isfunction(returned)
    assert inspect.isfunction(quote_carrier)
