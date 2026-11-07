"""Patching through mocker: replace a name for the length of the test, then undo it."""

import os
from decimal import Decimal

import pytest
from mocking_reference.carriers import CarrierQuote, ConsignmentId, FastlineGateway
from pytest_mock import MockerFixture, PytestMockWarning

CN1 = ConsignmentId("CN-1")
TEN = Decimal("10")


def test_patch_object_replaces_an_attribute_for_the_test(mocker: MockerFixture) -> None:
    canned = CarrierQuote("PATCHED", Decimal("9.00"))
    patched = mocker.patch.object(FastlineGateway, "quote", autospec=True, return_value=canned)
    gateway = FastlineGateway()

    assert gateway.quote(CN1, TEN) == canned
    patched.assert_called_once_with(gateway, CN1, TEN)
    with pytest.raises(TypeError, match="missing a required argument"):
        gateway.quote()  # type: ignore[call-arg]

    mocker.stopall()
    assert gateway.quote(CN1, TEN) == CarrierQuote("FASTLINE", Decimal("4.50"))


@pytest.mark.parametrize("before", [None, "ASIA"], ids=["absent", "present"])
def test_patch_dict_restores_the_mapping_after_the_test(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, before: str | None
) -> None:
    if before is None:
        monkeypatch.delenv("CARRIER_REGION", raising=False)
    else:
        monkeypatch.setenv("CARRIER_REGION", before)

    mocker.patch.dict(os.environ, {"CARRIER_REGION": "EU"})
    inside = os.environ["CARRIER_REGION"]
    mocker.stopall()

    assert (inside, os.environ.get("CARRIER_REGION")) == ("EU", before)


def test_mocker_stop_undoes_one_patch(mocker: MockerFixture) -> None:
    patched_book = mocker.patch.object(FastlineGateway, "book", return_value="PATCHED")
    canned = CarrierQuote("PATCHED", Decimal("9.00"))
    mocker.patch.object(FastlineGateway, "quote", return_value=canned)
    gateway = FastlineGateway()

    mocker.stop(patched_book)

    assert gateway.book(CN1) == "FASTLINE:CN-1"
    assert gateway.quote(CN1, TEN) == canned


def test_mocker_patch_used_as_a_context_manager_fails_under_the_warning_filter(
    mocker: MockerFixture,
) -> None:
    with (
        pytest.raises(PytestMockWarning, match="do not need to be used as context managers"),
        mocker.patch.object(FastlineGateway, "book"),
    ):
        pass
