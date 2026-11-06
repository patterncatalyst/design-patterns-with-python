from collections.abc import Callable
from decimal import Decimal
from unittest import mock

import pytest
from pytest_mock import MockerFixture
from seams import airco, fastline, legacy
from seams.domain import CarrierTimeoutError, Consignment

type FastlineFake = Callable[[str, Decimal], Decimal]
type AircoFake = Callable[..., int]


def _looked_up(name: str) -> object:
    """What ``seams.legacy`` holds under a name. ``vars`` reads it without the re-export check."""
    return vars(legacy)[name]


def _answer(consignment: Consignment) -> tuple[str, str]:
    quote = legacy.RateEngine().quote(consignment)
    return quote.carrier, str(quote.total.amount)


def test_the_legacy_engine_calls_the_real_carrier(consignment: Consignment) -> None:
    with pytest.raises(CarrierTimeoutError, match="FASTLINE did not answer for 'EU'"):
        legacy.RateEngine().quote(consignment)


def test_patching_the_name_where_it_is_looked_up_replaces_the_carrier(
    monkeypatch: pytest.MonkeyPatch,
    consignment: Consignment,
    fastline_fake: FastlineFake,
    airco_fake: AircoFake,
    airco_grams: list[int],
) -> None:
    monkeypatch.setattr("seams.legacy.request_quote", fastline_fake)
    monkeypatch.setattr(airco, "price", airco_fake)

    assert _answer(consignment) == ("FASTLINE", "27.50")
    assert airco_grams == [12500]


def test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier(
    monkeypatch: pytest.MonkeyPatch,
    consignment: Consignment,
    fastline_fake: FastlineFake,
    airco_fake: AircoFake,
) -> None:
    monkeypatch.setattr("seams.fastline.request_quote", fastline_fake)
    monkeypatch.setattr(airco, "price", airco_fake)

    with pytest.raises(CarrierTimeoutError, match="FASTLINE did not answer"):
        legacy.RateEngine().quote(consignment)


def test_a_module_attribute_is_patched_on_the_module_it_belongs_to(
    monkeypatch: pytest.MonkeyPatch,
    consignment: Consignment,
    fastline_fake: FastlineFake,
) -> None:
    def cheaper_airco(*, destination: str, grams: int) -> int:
        return 2000

    assert _looked_up("airco") is airco
    monkeypatch.setattr("seams.legacy.request_quote", fastline_fake)
    monkeypatch.setattr("seams.airco.price", cheaper_airco)

    assert _answer(consignment) == ("AIRCO", "22.00")


@pytest.mark.parametrize(
    ("target", "outcome"),
    [
        pytest.param("seams.legacy.request_quote", "FASTLINE 27.50", id="using-module"),
        pytest.param("seams.fastline.request_quote", "CarrierTimeoutError", id="defining-module"),
    ],
)
def test_unittest_mock_patch_follows_the_same_lookup_rule(
    monkeypatch: pytest.MonkeyPatch,
    consignment: Consignment,
    fastline_fake: FastlineFake,
    airco_fake: AircoFake,
    target: str,
    outcome: str,
) -> None:
    monkeypatch.setattr(airco, "price", airco_fake)

    with mock.patch(target, fastline_fake):
        try:
            carrier, total = _answer(consignment)
            result = f"{carrier} {total}"
        except CarrierTimeoutError:
            result = "CarrierTimeoutError"

    assert result == outcome


def test_monkeypatch_refuses_a_misspelt_name(
    monkeypatch: pytest.MonkeyPatch, fastline_fake: FastlineFake
) -> None:
    with pytest.raises(AttributeError, match="has no attribute 'request_qoute'"):
        monkeypatch.setattr("seams.legacy.request_qoute", fastline_fake)


def test_monkeypatch_with_raising_false_creates_a_name_nothing_reads(
    monkeypatch: pytest.MonkeyPatch,
    consignment: Consignment,
    fastline_fake: FastlineFake,
    airco_fake: AircoFake,
) -> None:
    monkeypatch.setattr("seams.legacy.request_qoute", fastline_fake, raising=False)
    monkeypatch.setattr(airco, "price", airco_fake)

    assert hasattr(legacy, "request_qoute")
    with pytest.raises(CarrierTimeoutError, match="FASTLINE did not answer"):
        legacy.RateEngine().quote(consignment)


def test_patch_refuses_a_name_the_module_does_not_have(
    mocker: MockerFixture, consignment: Consignment
) -> None:
    with pytest.raises(AttributeError, match="does not have the attribute 'price'"):
        mocker.patch("seams.legacy.price")

    mocker.patch("seams.legacy.price", create=True)
    with pytest.raises(CarrierTimeoutError, match="FASTLINE did not answer"):
        legacy.RateEngine().quote(consignment)


@pytest.mark.parametrize(
    ("autospec", "outcome"),
    [
        pytest.param(True, "TypeError: missing a required argument: 'weight_kg'", id="autospec"),
        pytest.param(False, "accepted", id="plain"),
    ],
)
def test_autospec_refuses_a_call_with_the_wrong_signature(
    mocker: MockerFixture, autospec: bool, outcome: str
) -> None:
    mocker.patch("seams.legacy.request_quote", autospec=autospec)
    call = _looked_up("request_quote")
    assert callable(call)

    try:
        call("EU")
        result = "accepted"
    except TypeError as error:
        result = f"TypeError: {error}"

    assert result == outcome


def test_monkeypatch_undoes_its_changes_when_the_context_ends(
    monkeypatch: pytest.MonkeyPatch,
    fastline_fake: FastlineFake,
    airco_fake: AircoFake,
) -> None:
    with monkeypatch.context() as patch:
        patch.setattr("seams.legacy.request_quote", fastline_fake)
        patch.setattr(airco, "price", airco_fake)
        assert _looked_up("request_quote") is fastline_fake
        assert airco.price is airco_fake

    assert _looked_up("request_quote") is fastline.request_quote
    assert airco.price is not airco_fake
    assert _looked_up("airco") is airco
