import copy
import dataclasses
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal

import pytest
from builder_prototype.booking import BookingRequest
from builder_prototype.domain import BookingError, ConsignmentId, Weight
from builder_prototype.templates import TEMPLATES, from_template

NEW_ID = ConsignmentId("CN-42")
NEW_WEIGHT = Weight(Decimal("640"))


@dataclass(slots=True, kw_only=True)
class _LooseRequest:
    """A mutable request with a list field: the case where copies can share state."""

    consignment_id: str
    documents: list[str] = field(default_factory=list)


def _copy(request: _LooseRequest) -> _LooseRequest:
    return copy.copy(request)


def _replace(request: _LooseRequest) -> _LooseRequest:
    return dataclasses.replace(request, consignment_id="CN-2")


@pytest.mark.parametrize("name", ["rotterdam-singapore", "dangerous-goods"])
def test_a_template_and_replace_give_a_new_request(name: str) -> None:
    template = TEMPLATES[name]

    request = from_template(name, consignment_id=NEW_ID, weight=NEW_WEIGHT)

    assert request is not template
    assert (request.consignment_id, request.weight) == (NEW_ID, NEW_WEIGHT)
    assert template.consignment_id == ConsignmentId("TEMPLATE")
    assert (
        dataclasses.replace(request, consignment_id=template.consignment_id, weight=template.weight)
        == template
    )


@pytest.mark.parametrize(
    "amend",
    [dataclasses.replace, copy.replace],
    ids=["replace", "copy-replace"],
)
def test_replace_reruns_the_cross_field_checks(
    amend: Callable[..., BookingRequest],
) -> None:
    template = TEMPLATES["rotterdam-singapore"]

    with pytest.raises(BookingError, match="declared value"):
        amend(template, insured=True)

    assert template.insured is False


def test_a_deep_copy_separates_the_documents_list() -> None:
    template = _LooseRequest(consignment_id="TEMPLATE", documents=["commercial invoice"])

    clone = copy.deepcopy(template)
    clone.documents.append("dangerous goods note")

    assert template.documents == ["commercial invoice"]
    assert clone.documents is not template.documents


@pytest.mark.parametrize("make_copy", [_copy, _replace], ids=["copy", "replace"])
def test_a_shallow_copy_shares_the_documents_list(
    make_copy: Callable[[_LooseRequest], _LooseRequest],
) -> None:
    template = _LooseRequest(consignment_id="TEMPLATE", documents=["commercial invoice"])

    clone = make_copy(template)
    clone.documents.append("dangerous goods note")

    assert template.documents == ["commercial invoice", "dangerous goods note"]
    assert clone.documents is template.documents


def test_a_tuple_field_makes_the_template_safe_to_share() -> None:
    template = TEMPLATES["rotterdam-singapore"]
    before = template.documents

    clone = copy.copy(template)
    longer = dataclasses.replace(clone, documents=(*clone.documents, "packing list"))

    assert template.documents == before == ("commercial invoice",)
    assert longer.documents == ("commercial invoice", "packing list")
    assert clone == template
    assert clone is not template


def test_copy_replace_works_on_dataclasses_and_refuses_a_plain_class() -> None:
    class Plain:
        service = "standard"

    express = copy.replace(TEMPLATES["rotterdam-singapore"], service="express")

    assert express.service == "express"
    with pytest.raises(TypeError, match="does not support"):
        copy.replace(Plain(), service="express")  # type: ignore[arg-type]


def test_an_unknown_template_is_a_booking_error() -> None:
    with pytest.raises(BookingError, match="no template 'air-freight'") as raised:
        from_template("air-freight", consignment_id=NEW_ID, weight=NEW_WEIGHT)

    assert raised.value.__cause__ is None
    assert raised.value.__suppress_context__


def test_the_template_registry_is_read_only() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        TEMPLATES["rush"] = TEMPLATES["dangerous-goods"]  # type: ignore[index]

    assert not isinstance(TEMPLATES, dict)
