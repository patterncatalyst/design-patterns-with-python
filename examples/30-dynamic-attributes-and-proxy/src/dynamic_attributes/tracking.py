"""A tracking history that loads its own fields on first read."""

import warnings
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class HandlingKind(Enum):
    BOOKED = "booked"
    LOADED = "loaded"
    DEPARTED = "departed"
    CLEARED = "cleared"
    DELIVERED = "delivered"


class ConsignmentStatus(Enum):
    BOOKED = "booked"
    LOADED = "loaded"
    IN_TRANSIT = "in transit"
    CLEARED = "cleared"
    DELIVERED = "delivered"


_STATUS_AFTER: Mapping[HandlingKind, ConsignmentStatus] = {
    HandlingKind.BOOKED: ConsignmentStatus.BOOKED,
    HandlingKind.LOADED: ConsignmentStatus.LOADED,
    HandlingKind.DEPARTED: ConsignmentStatus.IN_TRANSIT,
    HandlingKind.CLEARED: ConsignmentStatus.CLEARED,
    HandlingKind.DELIVERED: ConsignmentStatus.DELIVERED,
}


@dataclass(frozen=True, slots=True)
class HandlingEvent:
    consignment_id: ConsignmentId
    kind: HandlingKind
    port: str


# The only names ``__getattr__`` may load. Every other name is a missing attribute.
_LAZY = frozenset({"events", "status", "last_port"})


class TrackingHistory:
    """The handling events of one consignment, read from a slow feed on first access.

    The three fields are declared as annotations and hold no value until a read reaches
    ``__getattr__``. That one read loads them all and stores them in the instance dictionary, so
    later reads find them by ordinary lookup. ``hasattr`` on a lazy name is a read, and it loads.
    """

    events: tuple[HandlingEvent, ...]
    status: ConsignmentStatus | None
    last_port: str | None

    def __init__(
        self,
        consignment_id: ConsignmentId,
        load: Callable[[ConsignmentId], Iterable[HandlingEvent]],
    ) -> None:
        self.consignment_id = consignment_id
        self._load = load

    def __getattr__(self, name: str) -> object:
        """Load the lazy fields once.

        The allow-list comes first because this method reads ``self._load``: on an instance whose
        ``__init__`` never ran (``copy`` and ``pickle`` build one), that read would reach this
        method again for a name it does not own. Refusing every name outside ``_LAZY`` ends it.
        """
        if name not in _LAZY:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        events = tuple(self._load(self.consignment_id))
        # Write around __setattr__, which refuses the lazy names.
        vars(self).update(
            events=events,
            status=_STATUS_AFTER[events[-1].kind] if events else None,
            last_port=events[-1].port if events else None,
        )
        return vars(self)[name]

    def __setattr__(self, name: str, value: object) -> None:
        if name in _LAZY:
            raise AttributeError(f"{name!r} is loaded, not assigned")
        object.__setattr__(self, name, value)

    def __dir__(self) -> list[str]:
        return sorted({*object.__dir__(self), *_LAZY})

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self.events)


def __getattr__(name: str) -> type[TrackingHistory]:
    """The module's old name for the history, which warns and returns the new one."""
    if name == "LazyTrackingHistory":
        warnings.warn(
            "LazyTrackingHistory is deprecated; use TrackingHistory",
            DeprecationWarning,
            stacklevel=2,
        )
        return TrackingHistory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*globals(), "LazyTrackingHistory"})
