import dataclasses
from collections.abc import Callable
from decimal import Decimal

import pytest
from composite_flyweight.consolidation import carries_dangerous_goods, consignments
from composite_flyweight.domain import (
    Consignment,
    ConsolidatedShipment,
    ConsolidationError,
    Shipment,
    Weight,
)

LITHIUM = "850760"


def _weight_of(shipment: Shipment) -> Weight:
    """One function for both kinds: no `isinstance`, no `match`."""
    return shipment.weight


def test_the_total_weight_includes_nested_consolidations(
    tree_form: Callable[[], Decimal],
) -> None:
    assert tree_form() == Decimal("23.75")


def test_a_flat_sum_misses_nested_consolidations(
    nested: ConsolidatedShipment, flat_weight: Callable[[ConsolidatedShipment], Decimal]
) -> None:
    assert flat_weight(nested) == Decimal("17.25")
    assert nested.weight == Weight(Decimal("23.75"))
    assert flat_weight(nested) != nested.weight.kilograms


@pytest.mark.parametrize(
    ("kind", "expected"),
    [("consignment", "10"), ("consolidation", "23.75")],
    ids=["consignment", "consolidation"],
)
def test_a_consignment_and_a_consolidation_answer_weight_the_same_way(
    kind: str, expected: str, nested: ConsolidatedShipment
) -> None:
    shipment: Shipment = nested.parts[0] if kind == "consignment" else nested

    assert isinstance(shipment, Consignment) == (kind == "consignment")
    assert _weight_of(shipment) == Weight(Decimal(expected))


def test_consignments_lists_every_leaf_in_order(nested: ConsolidatedShipment) -> None:
    assert [c.id for c in consignments(nested)] == ["CN-1", "CN-3", "CN-4", "CN-2"]
    assert all(isinstance(c, Consignment) for c in consignments(nested))


@pytest.mark.parametrize("where", ["top-level", "nested", "none"])
def test_a_consolidation_with_dangerous_goods_anywhere_is_flagged(
    where: str,
    nested: ConsolidatedShipment,
    make_consignment: Callable[..., Consignment],
) -> None:
    shipments: dict[str, Shipment] = {
        "top-level": ConsolidatedShipment(
            "CS-2", (make_consignment("CN-8", "1"), make_consignment("CN-9", "1", LITHIUM))
        ),
        "nested": nested,
        "none": ConsolidatedShipment(
            "CS-3", (make_consignment("CN-8", "1"), make_consignment("CN-9", "2"))
        ),
    }

    assert carries_dangerous_goods(shipments[where]) == (where != "none")


def test_a_consolidation_must_have_parts() -> None:
    with pytest.raises(ConsolidationError, match="needs at least one part"):
        ConsolidatedShipment("CS-0", ())


@pytest.mark.parametrize("placement", ["same-level", "nested"])
def test_a_consignment_may_appear_only_once_in_a_consolidation(
    placement: str, make_consignment: Callable[..., Consignment]
) -> None:
    once = make_consignment("CN-1", "1")
    other = make_consignment("CN-2", "1")
    parts: tuple[Shipment, ...] = (
        (once, once)
        if placement == "same-level"
        else (once, ConsolidatedShipment("CS-INNER", (once, other)))
    )

    with pytest.raises(ConsolidationError, match="CN-1 appears twice"):
        ConsolidatedShipment("CS-2", parts)


def test_a_frozen_consolidation_cannot_be_rewired(nested: ConsolidatedShipment) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError, match="cannot assign to field 'parts'"):
        nested.parts = ()  # type: ignore[misc]

    assert isinstance(nested.parts, tuple)
    assert len(nested.parts) == 3


def test_a_component_leaf_refuses_add_only_when_the_program_runs(
    add_to_a_component_leaf: Callable[[], None],
) -> None:
    with pytest.raises(TypeError, match="cannot hold components"):
        add_to_a_component_leaf()


@pytest.mark.usefixtures("recursion_limit")
def test_a_mutable_component_group_can_contain_itself(
    self_containing_weight: Callable[[], Decimal],
) -> None:
    with pytest.raises(RecursionError):
        self_containing_weight()


def test_consolidations_compare_by_value(
    make_consignment: Callable[..., Consignment],
) -> None:
    def build() -> ConsolidatedShipment:
        inner = ConsolidatedShipment(
            "CS-INNER", (make_consignment("CN-3", "2.5"), make_consignment("CN-4", "4"))
        )
        return ConsolidatedShipment("CS-1", (make_consignment("CN-1", "10"), inner))

    first, second = build(), build()

    assert first is not second
    assert first == second
    assert hash(first) == hash(second)
    assert first != ConsolidatedShipment("CS-1", (make_consignment("CN-1", "10"),))


@pytest.mark.usefixtures("recursion_limit")
def test_a_pathologically_deep_consolidation_hits_the_recursion_limit(
    make_consignment: Callable[..., Consignment],
) -> None:
    """Validation recurses too, so the deep tree is assembled without running it."""
    shipment: Shipment = make_consignment("CN-1", "1")
    for level in range(5_000):
        group = object.__new__(ConsolidatedShipment)
        object.__setattr__(group, "id", f"CS-{level}")
        object.__setattr__(group, "parts", (shipment,))
        shipment = group

    with pytest.raises(RecursionError):
        shipment.weight  # noqa: B018


@pytest.mark.parametrize(
    "kilograms",
    [Decimal(0), Decimal(-1), Decimal("NaN"), Decimal("Infinity")],
    ids=["zero", "negative", "nan", "infinity"],
)
def test_weight_refuses_zero_negative_and_non_finite_values(kilograms: Decimal) -> None:
    with pytest.raises(ValueError, match="positive and finite"):
        Weight(kilograms)
