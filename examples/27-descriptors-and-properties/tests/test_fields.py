from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from descriptors_properties.cargo import (
    Consignment,
    ConsignmentId,
    Container,
    ContainerError,
    Dimensions,
)
from descriptors_properties.fields import Positive

if TYPE_CHECKING:
    from conftest import ConsignmentFactory, ExtentsFactory


# (id, extents, name of the field that must be refused or None)
EXTENT_ROWS = [
    pytest.param((Decimal(120), Decimal(80), Decimal(100)), None, id="valid"),
    pytest.param((Decimal(0), Decimal(80), Decimal(100)), "length_cm", id="length-zero"),
    pytest.param((Decimal(120), Decimal(-2), Decimal(100)), "width_cm", id="width-negative"),
    pytest.param((Decimal(120), Decimal(80), Decimal("NaN")), "height_cm", id="height-nan"),
    pytest.param(
        (Decimal(120), Decimal(80), Decimal("Infinity")), "height_cm", id="height-infinity"
    ),
]


@pytest.mark.parametrize(("extents", "refused"), EXTENT_ROWS)
def test_every_field_form_validates_the_same_extents(
    field_form: ExtentsFactory, extents: tuple[Decimal, Decimal, Decimal], refused: str | None
) -> None:
    if refused is None:
        built = field_form(*extents)
        assert (built.length_cm, built.width_cm, built.height_cm) == extents
    else:
        with pytest.raises(ValueError, match=f"{refused} must be positive"):
            field_form(*extents)


def _consignment(kilograms: Decimal) -> object:
    return Consignment(
        id=ConsignmentId("CN-1"),
        kilograms=kilograms,
        dimensions=Dimensions(Decimal(1), Decimal(1), Decimal(1)),
    )


def _dimensions(height_cm: Decimal) -> object:
    return Dimensions(Decimal(1), Decimal(1), height_cm)


def _container_tare(tare_kg: Decimal) -> object:
    return Container("C-1", tare_kg, Decimal(28000))


def _container_max(max_payload_kg: Decimal) -> object:
    return Container("C-1", Decimal(2200), max_payload_kg)


@pytest.mark.parametrize(
    ("build", "name"),
    [
        pytest.param(_consignment, "kilograms", id="consignment-kilograms"),
        pytest.param(_dimensions, "height_cm", id="dimensions-height_cm"),
        pytest.param(_container_tare, "tare_kg", id="container-tare_kg"),
        pytest.param(_container_max, "max_payload_kg", id="container-max_payload_kg"),
    ],
)
def test_a_positive_field_refuses_a_bad_value_on_every_class(
    build: Callable[[Decimal], object], name: str
) -> None:
    with pytest.raises(ValueError, match=f"{name} must be positive, got -1"):
        build(Decimal(-1))


def test_assignment_to_a_container_field_is_validated(container: Container) -> None:
    with pytest.raises(ValueError, match="tare_kg must be positive"):
        container.tare_kg = Decimal(0)

    assert container.tare_kg == Decimal(2200)


def test_set_name_gives_each_field_its_own_storage(dimensions: Dimensions) -> None:
    assert vars(dimensions) == {
        "_length_cm": Decimal(120),
        "_width_cm": Decimal(80),
        "_height_cm": Decimal(100),
    }


def test_one_descriptor_class_validates_every_field() -> None:
    fields = [
        vars(Consignment)["kilograms"],
        vars(Dimensions)["length_cm"],
        vars(Dimensions)["width_cm"],
        vars(Dimensions)["height_cm"],
        vars(Container)["tare_kg"],
        vars(Container)["max_payload_kg"],
    ]

    assert {type(entry) for entry in fields} == {Positive}
    assert len({id(entry) for entry in fields}) == 6


class _DriftedDimensions:
    """A copy-pasted height setter that lost its finiteness check on the way."""

    def __init__(self, height_cm: Decimal) -> None:
        self.height_cm = height_cm

    @property
    def height_cm(self) -> Decimal:
        return self._height_cm

    @height_cm.setter
    def height_cm(self, value: Decimal) -> None:
        if value <= 0:
            raise ValueError(f"height_cm must be positive, got {value}")
        self._height_cm = value


def test_a_copy_pasted_property_validator_drifts() -> None:
    infinity = Decimal("Infinity")

    assert _DriftedDimensions(infinity).height_cm == infinity
    with pytest.raises(ValueError, match="height_cm must be positive"):
        Dimensions(Decimal(1), Decimal(1), infinity)


def test_a_property_without_a_setter_refuses_assignment(container: Container) -> None:
    with pytest.raises(AttributeError, match="has no setter"):
        container.payload_kg = Decimal(1)  # type: ignore[misc]


def test_payload_is_recomputed_after_each_load(
    container: Container, consignment: ConsignmentFactory
) -> None:
    container.load(consignment(100))
    first = container.payload_kg
    container.load(consignment(250))

    assert (first, container.payload_kg) == (Decimal(100), Decimal(350))


@pytest.mark.parametrize(
    ("kilograms", "accepted"), [(28000, True), (28050, False)], ids=["at-the-limit", "over"]
)
def test_load_refuses_a_consignment_over_the_max_payload(
    container: Container, consignment: ConsignmentFactory, kilograms: int, accepted: bool
) -> None:
    if accepted:
        container.load(consignment(kilograms))
        assert container.payload_kg == Decimal(28000)
    else:
        with pytest.raises(ContainerError, match="would exceed 28000 kg in C-1"):
            container.load(consignment(kilograms))
        assert container.consignments == []
