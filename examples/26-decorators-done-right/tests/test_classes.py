from collections.abc import Callable
from dataclasses import dataclass

import pytest
from decorators_done_right.domain import (
    DOCUMENT_TYPES,
    BillOfLading,
    DocumentKind,
    DocumentKindError,
    Manifest,
    document_kind,
)


def test_document_kind_registers_the_class_at_definition() -> None:
    # The one test that reads the import-time registration in the shared registry.
    assert DOCUMENT_TYPES[DocumentKind.BILL_OF_LADING] is BillOfLading
    assert DOCUMENT_TYPES[DocumentKind.MANIFEST] is Manifest
    assert DocumentKind.CUSTOMS_DECLARATION not in DOCUMENT_TYPES


def test_document_kind_refuses_a_second_class_for_a_kind() -> None:
    registry: dict[DocumentKind, type] = {}

    @document_kind(DocumentKind.MANIFEST, registry=registry)
    class First:
        pass

    with pytest.raises(DocumentKindError, match=r"MANIFEST is already registered to .*First"):

        @document_kind(DocumentKind.MANIFEST, registry=registry)
        class Second:
            pass

    assert registry == {DocumentKind.MANIFEST: First}


def test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class() -> None:
    registry: dict[DocumentKind, type] = {}

    @dataclass(frozen=True, slots=True)
    @document_kind(DocumentKind.BILL_OF_LADING, registry=registry)
    class Beneath:
        number: str

    registered = registry[DocumentKind.BILL_OF_LADING]
    assert registered is not Beneath
    assert "__slots__" in vars(Beneath)
    assert "__slots__" not in vars(registered)

    @document_kind(DocumentKind.MANIFEST, registry=registry)
    @dataclass(frozen=True, slots=True)
    class Above:
        number: str

    assert registry[DocumentKind.MANIFEST] is Above


def _register_without_returning[C: type](
    kind: DocumentKind, registry: dict[DocumentKind, type]
) -> Callable[[C], C]:
    """``document_kind`` with its ``return cls`` forgotten."""

    def register(cls: C) -> C:  # type: ignore[return]
        registry[kind] = cls

    return register


def test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none() -> None:
    registry: dict[DocumentKind, type] = {}

    @_register_without_returning(DocumentKind.MANIFEST, registry)
    class Forgotten:
        pass

    bound: object = Forgotten
    assert bound is None
    assert registry[DocumentKind.MANIFEST].__name__ == "Forgotten"
