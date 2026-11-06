from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from descriptors_properties.cargo import Container

if TYPE_CHECKING:
    from conftest import ConsignmentFactory


def test_a_data_descriptor_takes_precedence_over_the_instance_dict(
    consignment: ConsignmentFactory,
) -> None:
    shipment = consignment(100)

    vars(shipment)["kilograms"] = Decimal(999)

    assert shipment.kilograms == Decimal(100)


def test_an_instance_dict_entry_takes_precedence_over_cached_property(
    consignment: ConsignmentFactory,
) -> None:
    shipment = consignment(100)

    vars(shipment)["chargeable_kg"] = Decimal(1)

    assert shipment.chargeable_kg == Decimal(1)


def test_class_access_to_a_positive_field_raises_attribute_error() -> None:
    with pytest.raises(AttributeError, match="tare_kg"):
        _ = Container.tare_kg
