import os
import re
from pathlib import Path

import mypy.api
import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"


def _run(snippet: str, tmp_path: Path) -> tuple[str, int]:
    """Type-check a snippet strictly, finding the package through the member's src directory."""
    config = tmp_path / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {_SRC}\n")
    stdout, _stderr, status = mypy.api.run(
        [
            "--strict",
            "--config-file",
            str(config),
            "--cache-dir",
            os.devnull,
            "--no-error-summary",
            "-c",
            snippet,
        ]
    )
    return stdout, status


def _codes(stdout: str) -> set[str]:
    return set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE))


_DECORATED_AS_A_CALCULATOR = """
from decimal import Decimal

from decorator_proxy.domain import Consignment, Money
from decorator_proxy.layers import RateCalculator
from decorator_proxy.syntax import audited


@audited(print)
def price(consignment: Consignment) -> Money:
    return Money(Decimal(0), "EUR")


calculator: RateCalculator = price
"""

_LAYER_STACKS = {
    "missing-price": """
from decorator_proxy.domain import Money
from decorator_proxy.layers import Layer, RateCalculator


class Broken:
    def __init__(self, inner: RateCalculator) -> None:
        self.inner = inner


layers: tuple[Layer, ...] = (Broken,)
""",
    "wrong-keyword": """
from decimal import Decimal
from functools import partial

from decorator_proxy.domain import Money
from decorator_proxy.layers import Layer, Surcharge

layers: tuple[Layer, ...] = (partial(Surcharge, fees=Money(Decimal(15), "EUR")),)
""",
}

_SIGNATURE_KEPT = {
    "arg-type": """
from decorator_proxy.domain import Consignment
from decorator_proxy.proxy import CarrierGateway
from decorator_proxy.syntax import quote_carrier


def ask(gateway: CarrierGateway, consignment: Consignment) -> None:
    quote_carrier(gateway, 5)
""",
    "call-arg": """
from decorator_proxy.domain import Consignment
from decorator_proxy.proxy import CarrierGateway
from decorator_proxy.syntax import quote_carrier


def ask(gateway: CarrierGateway, consignment: Consignment) -> None:
    quote_carrier(gateway, consignment, retries=2)
""",
}

_EXPLICIT_PROXY_AS_A_GATEWAY = """
from decorator_proxy.proxy import CarrierGateway, CarrierGatewayProxy


def wrap(inner: CarrierGateway) -> CarrierGateway:
    return CarrierGatewayProxy(inner)
"""

_EXPLICIT_PROXY_TYPO = """
from decorator_proxy.domain import Consignment
from decorator_proxy.proxy import CarrierGateway, CarrierGatewayProxy


def ask(inner: CarrierGateway, consignment: Consignment) -> None:
    CarrierGatewayProxy(inner).quoet(consignment)
"""

# A reduced model: the proxy without `book`, over the same two-member Protocol.
_PROXY_WITHOUT_BOOK = """
from decorator_proxy.domain import CarrierQuote, Consignment
from decorator_proxy.proxy import CarrierGateway


class QuoteOnlyProxy:
    def __init__(self, inner: CarrierGateway) -> None:
        self._inner = inner

    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        return self._inner.quote(consignment)


def wrap(inner: CarrierGateway) -> None:
    gateway: CarrierGateway = QuoteOnlyProxy(inner)
"""

# Reduced models of the forwarding form: a Protocol with two members, and a proxy that defines one.
_FORWARDING_HEAD = """
from typing import Any, Protocol


class Gateway(Protocol):
    def book(self, consignment_id: str, /) -> str: ...

    def track(self, consignment_id: str, /) -> tuple[str, ...]: ...


class Inner:
    def book(self, consignment_id: str, /) -> str:
        return consignment_id

    def track(self, consignment_id: str, /) -> tuple[str, ...]:
        return (consignment_id,)


class ForwardingProxy:
    def __init__(self, inner: Inner) -> None:
        self._inner = inner

    def book(self, consignment_id: str, /) -> str:
        return self._inner.book(consignment_id)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


proxy = ForwardingProxy(Inner())
gateway: Gateway = proxy
"""

_FORWARDING_TAILS = {
    "any-typo": 'proxy.trakc("CN-1")\n',
    "any-wrong-type": 'count: int = proxy.track("CN-1")\n',
}

_FORWARDING_RETURNS_OBJECT = """
from typing import Protocol


class Gateway(Protocol):
    def book(self, consignment_id: str, /) -> str: ...

    def track(self, consignment_id: str, /) -> tuple[str, ...]: ...


class ForwardingProxy:
    def __init__(self, inner: object) -> None:
        self._inner = inner

    def book(self, consignment_id: str, /) -> str:
        return consignment_id

    def __getattr__(self, name: str) -> object:
        return getattr(self._inner, name)


gateway: Gateway = ForwardingProxy(object())
"""


def test_mypy_rejects_a_decorated_function_where_a_calculator_belongs(tmp_path: Path) -> None:
    stdout, status = _run(_DECORATED_AS_A_CALCULATOR, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert 'variable has type "RateCalculator"' in stdout


@pytest.mark.parametrize(
    ("name", "needle"),
    [("missing-price", "tuple[type[Broken]]"), ("wrong-keyword", 'did you mean "fee"?')],
    ids=["missing-price", "wrong-keyword"],
)
def test_mypy_checks_each_layer_in_a_stack(name: str, needle: str, tmp_path: Path) -> None:
    stdout, status = _run(_LAYER_STACKS[name], tmp_path)

    assert status == 1
    assert _codes(stdout) == {"assignment" if name == "missing-price" else "call-arg"}
    assert needle in stdout


@pytest.mark.parametrize(
    ("name", "code", "needle"),
    [
        ("arg-type", "arg-type", 'expected "Consignment"'),
        ("call-arg", "call-arg", 'Unexpected keyword argument "retries"'),
    ],
    ids=["arg-type", "call-arg"],
)
def test_mypy_keeps_the_call_signature_through_retry(
    name: str, code: str, needle: str, tmp_path: Path
) -> None:
    stdout, status = _run(_SIGNATURE_KEPT[name], tmp_path)

    assert status == 1
    assert _codes(stdout) == {code}
    assert needle in stdout


def test_mypy_accepts_the_explicit_proxy_as_a_gateway(tmp_path: Path) -> None:
    stdout, status = _run(_EXPLICIT_PROXY_AS_A_GATEWAY, tmp_path)

    assert status == 0
    assert stdout == ""


def test_mypy_reports_a_typo_on_the_explicit_proxy(tmp_path: Path) -> None:
    stdout, status = _run(_EXPLICIT_PROXY_TYPO, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"attr-defined"}
    assert '"CarrierGatewayProxy" has no attribute "quoet"' in stdout


def test_mypy_reports_a_member_missing_from_an_explicit_proxy(tmp_path: Path) -> None:
    stdout, status = _run(_PROXY_WITHOUT_BOOK, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert "protocol member" in stdout


@pytest.mark.parametrize("name", ["any-typo", "any-wrong-type"])
def test_mypy_accepts_a_typo_through_a_forwarding_proxy(name: str, tmp_path: Path) -> None:
    stdout, status = _run(_FORWARDING_HEAD + _FORWARDING_TAILS[name], tmp_path)

    assert status == 0
    assert stdout == ""


def test_mypy_rejects_a_forwarding_proxy_that_returns_object(tmp_path: Path) -> None:
    stdout, status = _run(_FORWARDING_RETURNS_OBJECT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert 'got "object"' in stdout
