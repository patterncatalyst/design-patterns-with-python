import pytest
from structural_typing.carriers import (
    AircoGateway,
    CarrierBase,
    CarrierGateway,
    FastlineGateway,
)
from structural_typing.domain import Consignment


class _HalfCarrier(CarrierBase):
    """Negative fixture: an ABC subclass that forgets the abstract method."""

    code = "HALF"


class _DeclaredGateway(CarrierGateway):
    """Negative fixture: explicitly subclassing a Protocol makes the class nominal."""


def test_abc_refuses_an_incomplete_subclass_at_construction() -> None:
    with pytest.raises(TypeError, match="without an implementation for abstract method 'book'"):
        _HalfCarrier()  # type: ignore[abstract]


def test_both_carriers_satisfy_the_protocol_one_by_inheritance(consignment: Consignment) -> None:
    gateways: list[CarrierGateway] = [FastlineGateway(), AircoGateway()]
    assert [gateway.book(consignment) for gateway in gateways] == [
        "FASTLINE:CN-00000001",
        "AIRCO:CN-00000001",
    ]
    assert isinstance(gateways[1], CarrierBase)
    assert not isinstance(gateways[0], CarrierBase)
    assert AircoGateway().reference(consignment) == "AIRCO:CN-00000001"


def test_airco_marks_its_book_as_an_override() -> None:
    assert getattr(AircoGateway.book, "__override__", False) is True


def test_explicit_protocol_subclass_is_nominal_and_still_instantiable(
    consignment: Consignment,
) -> None:
    declared = _DeclaredGateway()  # type: ignore[abstract]
    assert declared.book(consignment) is None
