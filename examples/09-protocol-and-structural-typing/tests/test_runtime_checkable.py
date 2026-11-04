from typing import Protocol, runtime_checkable

import pytest
from structural_typing.carriers import FastlineGateway
from structural_typing.domain import Consignment


@runtime_checkable
class _CheckedGateway(Protocol):
    def book(self, consignment: Consignment, /) -> str: ...


class _WrongSignature:
    """Negative fixture: a book that takes no consignment and returns an int."""

    def book(self) -> int:
        return 0


class _BookAttribute:
    """Negative fixture: book is a number, not a callable."""

    book = 3


@runtime_checkable
class _HasCode(Protocol):
    code: str


class _Coded:
    code = "FASTLINE"


class _UndecoratedTracking(_CheckedGateway, Protocol):
    """Negative fixture: inherits a runtime-checkable Protocol without its own decorator."""

    def track(self, reference: str, /) -> str: ...


def _satisfies_checked(value: object) -> bool:
    return isinstance(value, _CheckedGateway)


def test_runtime_checkable_checks_names_only() -> None:
    assert _satisfies_checked(FastlineGateway())
    assert _satisfies_checked(_WrongSignature())
    assert _satisfies_checked(_BookAttribute())
    assert not _satisfies_checked(object())


def test_a_data_protocol_refuses_issubclass() -> None:
    assert isinstance(_Coded(), _HasCode)
    with pytest.raises(
        TypeError, match="Protocols with non-method members don't support issubclass"
    ):
        issubclass(_Coded, _HasCode)  # type: ignore[misc]


def test_an_undecorated_subprotocol_warns_on_isinstance() -> None:
    value: object = FastlineGateway()
    with pytest.warns(DeprecationWarning, match="isn't explicitly decorated"):
        isinstance(value, _UndecoratedTracking)  # type: ignore[misc]
