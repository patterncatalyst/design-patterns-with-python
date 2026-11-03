from consignments import Consignment


def test_consignment_keeps_reference() -> None:
    assert Consignment("C-1").reference == "C-1"
