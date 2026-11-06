"""Issuing shipping documents through a read-only table of callables."""

from collections.abc import Callable, Mapping
from enum import Enum
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class DocumentKind(Enum):
    BILL_OF_LADING = "bill of lading"
    MANIFEST = "manifest"
    CUSTOMS_DECLARATION = "customs declaration"


class UnsupportedDocumentError(LookupError):
    """A document kind that has no issuer, or text that names no document kind."""


type DocumentIssuer = Callable[[ConsignmentId], str]


def issue_bill_of_lading(consignment_id: ConsignmentId) -> str:
    return f"BL-{consignment_id}"


def issue_manifest(consignment_id: ConsignmentId) -> str:
    return f"MF-{consignment_id}"


def issue_customs_declaration(consignment_id: ConsignmentId) -> str:
    return f"CD-{consignment_id}"


# mypy checks every entry's signature and the key type, but not that every DocumentKind has an
# entry: a table that misses a kind type-checks. A test walks the enum instead.
ISSUERS: Mapping[DocumentKind, DocumentIssuer] = frozendict(
    {
        DocumentKind.BILL_OF_LADING: issue_bill_of_lading,
        DocumentKind.MANIFEST: issue_manifest,
        DocumentKind.CUSTOMS_DECLARATION: issue_customs_declaration,
    }
)


def issue(
    kind: DocumentKind,
    consignment_id: ConsignmentId,
    /,
    *,
    issuers: Mapping[DocumentKind, DocumentIssuer] = ISSUERS,
) -> str:
    """Issue the document of ``kind`` for ``consignment_id``.

    Only the lookup sits inside the ``try``. The issuer is called after it, so a ``KeyError``
    raised by the issuer itself is not reported as an unsupported kind.
    """
    try:
        issuer = issuers[kind]
    except KeyError:
        raise UnsupportedDocumentError(f"no issuer for {kind.value!r}") from None
    return issuer(consignment_id)


def parse_kind(raw: str) -> DocumentKind:
    """Read a document kind from its text value."""
    try:
        return DocumentKind(raw)
    except ValueError:
        raise UnsupportedDocumentError(f"unknown document kind {raw!r}") from None
