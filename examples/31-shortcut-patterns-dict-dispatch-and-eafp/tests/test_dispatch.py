from collections.abc import Mapping
from functools import singledispatch

import pytest
from shortcut_patterns.documents import (
    ISSUERS,
    ConsignmentId,
    DocumentIssuer,
    DocumentKind,
    UnsupportedDocumentError,
    issue,
    issue_bill_of_lading,
    issue_manifest,
    parse_kind,
)

CN_1 = ConsignmentId("CN-1")

# (kind, reference)
ISSUED = [
    (DocumentKind.BILL_OF_LADING, "BL-CN-1"),
    (DocumentKind.MANIFEST, "MF-CN-1"),
    (DocumentKind.CUSTOMS_DECLARATION, "CD-CN-1"),
]

_TWO_ISSUERS: dict[DocumentKind, DocumentIssuer] = {
    DocumentKind.BILL_OF_LADING: issue_bill_of_lading,
    DocumentKind.MANIFEST: issue_manifest,
}


def _raises_key_error(consignment_id: ConsignmentId) -> str:
    raise KeyError("port")


def _issue_broadly(
    kind: DocumentKind,
    consignment_id: ConsignmentId,
    issuers: Mapping[DocumentKind, DocumentIssuer],
) -> str:
    """The comparison: the whole call sits inside the ``try``."""
    try:
        return issuers[kind](consignment_id)
    except KeyError:
        raise UnsupportedDocumentError(f"no issuer for {kind.value!r}") from None


def _issue_by_chain(kind: DocumentKind, consignment_id: ConsignmentId) -> str:
    """An if-chain written before the customs declaration existed."""
    if kind is DocumentKind.BILL_OF_LADING:
        return issue_bill_of_lading(consignment_id)
    if kind is DocumentKind.MANIFEST:
        return issue_manifest(consignment_id)
    raise ValueError(kind)


def test_every_document_kind_has_an_issuer() -> None:
    assert [kind.name for kind in DocumentKind if kind not in ISSUERS] == []


@pytest.mark.parametrize(("kind", "reference"), ISSUED, ids=[kind.name for kind, _ in ISSUED])
def test_issue_gives_each_kind_its_reference(kind: DocumentKind, reference: str) -> None:
    assert issue(kind, CN_1) == reference


def test_an_unsupported_kind_raises_unsupported_document_error() -> None:
    with pytest.raises(
        UnsupportedDocumentError, match="no issuer for 'customs declaration'"
    ) as info:
        issue(DocumentKind.CUSTOMS_DECLARATION, CN_1, issuers=_TWO_ISSUERS)
    assert info.value.__suppress_context__ is True


def test_the_issuer_table_is_read_only() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        ISSUERS[DocumentKind.MANIFEST] = issue_bill_of_lading  # type: ignore[index]
    assert not isinstance(ISSUERS, dict)


def test_an_issuers_own_key_error_passes_through_issue() -> None:
    table = {DocumentKind.MANIFEST: _raises_key_error}
    with pytest.raises(KeyError, match="port"):
        issue(DocumentKind.MANIFEST, CN_1, issuers=table)


def test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind() -> None:
    table = {DocumentKind.MANIFEST: _raises_key_error}
    with pytest.raises(UnsupportedDocumentError, match="no issuer for 'manifest'"):
        _issue_broadly(DocumentKind.MANIFEST, CN_1, table)


def test_a_table_passed_by_the_caller_replaces_the_default() -> None:
    table = {DocumentKind.MANIFEST: issue_bill_of_lading}
    assert issue(DocumentKind.MANIFEST, CN_1, issuers=table) == "BL-CN-1"
    assert issue(DocumentKind.MANIFEST, CN_1) == "MF-CN-1"


def test_an_if_chain_whose_else_raises_misses_a_new_kind() -> None:
    assert _issue_by_chain(DocumentKind.MANIFEST, CN_1) == "MF-CN-1"
    with pytest.raises(ValueError, match="CUSTOMS_DECLARATION"):
        _issue_by_chain(DocumentKind.CUSTOMS_DECLARATION, CN_1)


def test_singledispatch_sends_every_document_kind_to_one_implementation() -> None:
    @singledispatch
    def describe(kind: object) -> str:
        return "fallback"

    @describe.register
    def _(kind: DocumentKind) -> str:
        return "one implementation"

    assert [describe(kind) for kind in DocumentKind] == ["one implementation"] * 3
    assert sorted(cls.__name__ for cls in describe.registry) == ["DocumentKind", "object"]


@pytest.mark.parametrize("kind", list(DocumentKind), ids=[kind.name for kind in DocumentKind])
def test_parse_kind_reads_a_document_kind_from_its_value(kind: DocumentKind) -> None:
    assert parse_kind(kind.value) is kind


def test_parse_kind_refuses_an_unknown_value() -> None:
    with pytest.raises(UnsupportedDocumentError, match="unknown document kind 'nope'") as info:
        parse_kind("nope")
    assert info.value.__suppress_context__ is True
