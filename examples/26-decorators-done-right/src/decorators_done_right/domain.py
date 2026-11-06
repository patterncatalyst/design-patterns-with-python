"""Documentation values: kinds, the two documents and the class decorator that registers them."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class DocumentKind(Enum):
    BILL_OF_LADING = "bill of lading"
    MANIFEST = "manifest"
    CUSTOMS_DECLARATION = "customs declaration"


class DocumentKindError(ValueError):
    """A document kind that is registered twice."""


DOCUMENT_TYPES: dict[DocumentKind, type] = {}


def document_kind[C: type](
    kind: DocumentKind, *, registry: dict[DocumentKind, type] = DOCUMENT_TYPES
) -> Callable[[C], C]:
    """Register the decorated class for ``kind`` and return it unchanged.

    Put it above ``@dataclass(slots=True)``: that decorator returns a new class, and a
    decorator beneath it would register the class that is thrown away.
    """

    def register(cls: C) -> C:
        if kind in registry:
            raise DocumentKindError(
                f"{kind.name} is already registered to {registry[kind].__qualname__}"
            )
        registry[kind] = cls
        return cls

    return register


@document_kind(DocumentKind.BILL_OF_LADING)
@dataclass(frozen=True, slots=True)
class BillOfLading:
    number: str
    consignment_id: ConsignmentId
    port_of_loading: str
    port_of_discharge: str


@document_kind(DocumentKind.MANIFEST)
@dataclass(frozen=True, slots=True)
class Manifest:
    number: str
    consignment_ids: tuple[ConsignmentId, ...]
