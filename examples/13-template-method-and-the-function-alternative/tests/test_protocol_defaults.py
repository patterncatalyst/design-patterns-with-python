from typing import Protocol, override

import pytest
from template_method.domain import Commodity, Consignment


class _DocumentHooks(Protocol):
    def classify(self, commodity: Commodity, /) -> str: ...

    def extra_documents(self, consignment: Consignment, /) -> tuple[str, ...]:
        return ()


class _ExplicitHooks(_DocumentHooks):
    @override
    def classify(self, commodity: Commodity, /) -> str:
        return "0000.00"


class _StructuralHooks:
    def classify(self, commodity: Commodity, /) -> str:
        return "0000.00"


def _documents_of(hooks: _DocumentHooks, consignment: Consignment) -> tuple[str, ...]:
    return hooks.extra_documents(consignment)


def test_protocol_defaults_reach_only_explicit_subclasses(consignment: Consignment) -> None:
    assert _documents_of(_ExplicitHooks(), consignment) == ()
    with pytest.raises(AttributeError, match="has no attribute 'extra_documents'"):
        _documents_of(_StructuralHooks(), consignment)  # type: ignore[arg-type]
