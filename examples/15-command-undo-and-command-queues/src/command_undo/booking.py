"""A booking with undo and redo stacks and a queue of pending amendments."""

from collections import deque
from dataclasses import dataclass, field

from command_undo.amendments import Amendment, apply
from command_undo.domain import AmendmentError, BookingRequest


@dataclass(slots=True, eq=False)
class Booking:
    """An entity: its request changes over time, and its history says how to go back."""

    request: BookingRequest
    history_limit: int = 20
    undo_stack: deque[Amendment] = field(init=False)
    redo_stack: deque[Amendment] = field(init=False)
    pending: deque[Amendment] = field(init=False)

    def __post_init__(self) -> None:
        self.undo_stack = deque(maxlen=self.history_limit)
        self.redo_stack = deque()
        self.pending = deque()

    def amend(self, amendment: Amendment) -> None:
        self.request, inverse = apply(self.request, amendment)
        self.undo_stack.append(inverse)
        self.redo_stack.clear()

    def undo(self) -> None:
        if not self.undo_stack:
            raise AmendmentError("nothing to undo")
        self.request, redo = apply(self.request, self.undo_stack.pop())
        self.redo_stack.append(redo)

    def redo(self) -> None:
        if not self.redo_stack:
            raise AmendmentError("nothing to redo")
        self.request, undo = apply(self.request, self.redo_stack.pop())
        self.undo_stack.append(undo)

    def submit(self, amendment: Amendment) -> None:
        self.pending.append(amendment)

    def apply_pending(self) -> None:
        """Apply the queue first in, first out, all or nothing."""
        queue = deque(self.pending)
        request = self.request
        inverses: list[Amendment] = []
        while queue:
            request, inverse = apply(request, queue.popleft())
            inverses.append(inverse)
        self.request = request
        self.undo_stack.extend(inverses)
        self.pending.clear()
        self.redo_stack.clear()
