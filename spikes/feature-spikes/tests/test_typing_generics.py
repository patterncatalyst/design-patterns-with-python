from decimal import Decimal
from unittest.mock import Mock, create_autospec

import pytest
from feature_spikes.decorator_vs_syntax import Consignment
from feature_spikes.typing_generics import (
    Describable,
    FlatQuoter,
    HazmatConsignment,
    HazmatQuoter,
    Quoter,
    cheapest,
    price_all,
    price_with,
)
from pytest_mock import MockerFixture

D = Decimal
C = Consignment("C-1", weight_kg=D(10))
H = HazmatConsignment("H-1", weight_kg=D(10))


def total(quoter: Quoter[Consignment]) -> Decimal:
    return quoter.quote(C)


def test_structural_conformance_without_base_class() -> None:
    assert total(FlatQuoter(D(5))) == D(5)
    with pytest.raises(TypeError, match="runtime_checkable"):
        isinstance(FlatQuoter(D(5)), Quoter)  # type: ignore[misc]


def test_contravariance_is_inferred_for_pep695_protocol() -> None:
    # A Quoter[Consignment] works where a Quoter[HazmatConsignment] is expected.
    assert price_all(FlatQuoter(D(3)), [H, H]) == [D(3), D(3)]


def test_explicit_protocol_subclass_with_override() -> None:
    assert HazmatQuoter(D(9)).quote(H) == D(9)
    assert HazmatQuoter.quote.__override__ is True  # type: ignore[attr-defined]


def test_cheapest_generic() -> None:
    options = {"ACME": D(9), "ZED": D(4)}
    assert cheapest(options, key=options.__getitem__) == "ZED"
    assert cheapest([FlatQuoter(D(7)), FlatQuoter(D(2))], key=lambda q: q.quote(C)) == FlatQuoter(
        D(2)
    )


def test_plain_function_and_lambda_satisfy_callback_protocol() -> None:
    def by_weight(c: Consignment, /) -> Decimal:
        return c.weight_kg * 2

    assert price_with(by_weight, C) == D(20)
    assert price_with(lambda c: c.weight_kg, C) == D(10)
    assert price_with(FlatQuoter(D(1)).quote, C) == D(1)


def test_mock_for_protocol_parameter() -> None:
    mock = Mock(spec=FlatQuoter)
    mock.quote.return_value = D(1)
    assert total(mock) == D(1)
    mock.quote.assert_called_once_with(C)


def test_create_autospec_for_protocol_parameter() -> None:
    spec = create_autospec(FlatQuoter, instance=True)
    spec.quote.return_value = D(2)
    assert total(spec) == D(2)


def test_pytest_mock_for_protocol_parameter(mocker: MockerFixture) -> None:
    m = mocker.Mock(spec=FlatQuoter)
    m.quote.return_value = D(3)
    assert total(m) == D(3)
    typed = mocker.create_autospec(FlatQuoter, instance=True)
    typed.quote.return_value = D(4)
    assert total(typed) == D(4)


def test_autospec_enforces_signature_unlike_bare_mock() -> None:
    spec = create_autospec(FlatQuoter, instance=True)
    with pytest.raises(TypeError, match="missing a required argument"):
        spec.quote()
    Mock().quote()  # a bare Mock accepts anything


def test_runtime_checkable_checks_method_presence_only() -> None:
    class Wrong:
        def describe(self, a: int, b: int, c: int) -> int:  # wrong signature and return type
            return a

    class Missing:
        pass

    assert isinstance(Wrong(), Describable)
    assert not isinstance(Missing(), Describable)

    # A non-callable attribute with the right name also passes for a method protocol member.
    class Attr:
        describe = 3

    assert isinstance(Attr(), Describable)
