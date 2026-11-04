from collections.abc import Callable
from decimal import Decimal
from typing import override

import pytest
from template_method.declarer import CustomsDeclarer, GermanyDeclarer, NetherlandsDeclarer
from template_method.domain import (
    Consignment,
    CustomsDeclaration,
    CustomsError,
    DeclarationLine,
    Money,
)
from template_method.hooks import EU_CLASSIFICATION, EU_SCHEDULE, NETHERLANDS, declare_customs


class _OpenDeclarer:
    """A template whose invariant lives in an overridable step."""

    def check(self, consignment: Consignment) -> None:
        if not consignment.commodities:
            raise CustomsError("no commodities to declare")

    def declare(self, consignment: Consignment) -> CustomsDeclaration:
        self.check(consignment)
        lines = tuple(
            DeclarationLine(commodity.description, "0000.00", commodity.value)
            for commodity in consignment.commodities
        )
        zero = Money(Decimal("0.00"), "EUR")
        return CustomsDeclaration(consignment.id, "NL", lines, zero, zero, ("commercial invoice",))


class _ForgetfulDeclarer(_OpenDeclarer):
    @override
    def check(self, consignment: Consignment) -> None:
        return None


class _OverridingDeclarer(NetherlandsDeclarer):
    @override  # type: ignore[misc]
    def declare(self, consignment: Consignment) -> CustomsDeclaration:
        return CustomsDeclaration(
            consignment.id,
            "XX",
            (),
            Money(Decimal("0.00"), "EUR"),
            Money(Decimal("0.00"), "EUR"),
            (),
        )


class _NoDocumentsDeclarer(CustomsDeclarer):
    country = "XX"


def test_the_template_and_the_hooks_give_the_same_declaration(consignment: Consignment) -> None:
    by_hooks = declare_customs(consignment, hooks=NETHERLANDS)
    by_template = NetherlandsDeclarer(
        classification=EU_CLASSIFICATION, schedule=EU_SCHEDULE
    ).declare(consignment)
    assert by_template == by_hooks
    assert by_template.duty == Money(Decimal("96.00"), "EUR")


def test_a_declarer_without_its_documents_cannot_be_built() -> None:
    with pytest.raises(TypeError, match="abstract method 'extra_documents'"):
        _NoDocumentsDeclarer(  # type: ignore[abstract]
            classification=EU_CLASSIFICATION, schedule=EU_SCHEDULE
        )


def test_final_marks_the_template_without_enforcing_it(consignment: Consignment) -> None:
    assert getattr(CustomsDeclarer.declare, "__final__", False) is True
    overriding = _OverridingDeclarer(classification=EU_CLASSIFICATION, schedule=EU_SCHEDULE)
    assert overriding.declare(consignment).country == "XX"


def test_a_subclass_that_skips_the_base_check_declares_nothing(
    make_consignment: Callable[..., Consignment],
) -> None:
    empty = make_consignment()
    assert _ForgetfulDeclarer().declare(empty).lines == ()
    with pytest.raises(CustomsError, match="no commodities to declare"):
        _OpenDeclarer().declare(empty)
    declarer = NetherlandsDeclarer(classification=EU_CLASSIFICATION, schedule=EU_SCHEDULE)
    with pytest.raises(CustomsError, match="has no commodities to declare"):
        declarer.declare(empty)


def test_two_destinations_share_the_schedule_and_differ_in_documents(
    consignment: Consignment,
) -> None:
    netherlands = NetherlandsDeclarer(classification=EU_CLASSIFICATION, schedule=EU_SCHEDULE)
    germany = GermanyDeclarer(classification=EU_CLASSIFICATION, schedule=EU_SCHEDULE)
    nl = netherlands.declare(consignment)
    de = germany.declare(consignment)
    assert nl.duty == de.duty
    assert nl.lines == de.lines
    assert nl.documents != de.documents
    assert (nl.country, de.country) == ("NL", "DE")
    assert de.documents == ("commercial invoice", "Intrastat declaration")
    assert netherlands.classification is germany.classification
