import dataclasses

import pytest
from consignments import Consignment, ConsignmentId, Weight


def make_consignment(kilograms: float = 120.5) -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00012345"),
        origin="NLRTM",
        destination="SGSIN",
        weight=Weight(kilograms),
    )


def test_equal_values_compare_equal() -> None:
    assert make_consignment() == make_consignment()
    assert make_consignment() != make_consignment(kilograms=99.0)


def test_consignment_is_usable_as_dict_key_and_set_member() -> None:
    first, second = make_consignment(), make_consignment()
    assert hash(first) == hash(second)
    assert {first, second} == {first}
    assert {first: "booked"}[second] == "booked"


def test_reweigh_returns_new_consignment_and_leaves_original_unchanged() -> None:
    original = make_consignment()
    amended = original.reweigh(Weight(130.0))
    assert amended.weight == Weight(130.0)
    assert original.weight == Weight(120.5)
    assert amended.id == original.id
    assert amended is not original


def test_dataclasses_replace_keeps_other_fields() -> None:
    original = make_consignment()
    moved = dataclasses.replace(original, destination="USNYC")
    assert moved.destination == "USNYC"
    assert moved.origin == original.origin
    assert original.destination == "SGSIN"


def test_instance_rejects_assignment() -> None:
    consignment = make_consignment()
    with pytest.raises(dataclasses.FrozenInstanceError):
        consignment.origin = "DEHAM"  # type: ignore[misc]


def test_consignment_id_renders_its_value() -> None:
    assert str(ConsignmentId("CN-00012345")) == "CN-00012345"


@pytest.mark.parametrize("raw", ["", "CN-1234567", "CN-123456789", "cn-12345678", "XX-12345678"])
def test_invalid_consignment_id_is_rejected(raw: str) -> None:
    with pytest.raises(ValueError, match="consignment id"):
        ConsignmentId(raw)


@pytest.mark.parametrize("kilograms", [0.0, -1.0, float("nan"), float("inf"), float("-inf")])
def test_invalid_weight_is_rejected(kilograms: float) -> None:
    with pytest.raises(ValueError, match="weight must be finite and positive"):
        Weight(kilograms)


@pytest.mark.parametrize("code", ["", "NLRT", "NLRTMX", "nlrtm", "NL1TM"])
@pytest.mark.parametrize("field", ["origin", "destination"])
def test_invalid_port_code_is_rejected(field: str, code: str) -> None:
    ports = {"origin": "NLRTM", "destination": "SGSIN", field: code}
    with pytest.raises(ValueError, match=f"{field} must be five uppercase letters"):
        Consignment(id=ConsignmentId("CN-00012345"), weight=Weight(1.0), **ports)
