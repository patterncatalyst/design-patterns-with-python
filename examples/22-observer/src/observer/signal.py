"""A signal: one event source, an open set of subscribers, and a written-down delivery contract.

A `Signal` is single-threaded. It decides four things a bare list of callables leaves open:
subscribers run in subscription order, a failing subscriber does not stop the rest, a subscriber
may subscribe, unsubscribe or publish during delivery, and a bound method is held weakly.
"""

import inspect
import weakref
from collections import deque
from collections.abc import Callable

type Subscriber[E] = Callable[[E], None]
type Unsubscribe = Callable[[], None]


def _strong[E](subscriber: Subscriber[E]) -> Callable[[], Subscriber[E] | None]:
    """A getter that holds the subscriber for as long as the getter lives."""

    def get() -> Subscriber[E] | None:
        return subscriber

    return get


class Signal[E]:
    def __init__(self) -> None:
        self._subscribers: dict[object, Callable[[], Subscriber[E] | None]] = {}
        self._pending: deque[E] = deque()
        self._delivering = False

    def subscribe(self, subscriber: Subscriber[E], /) -> Unsubscribe:
        """Add a subscriber and return the call that removes it.

        A bound method is held through `weakref.WeakMethod`, so the signal does not keep its
        owner alive. Every other callable is held strongly. A duplicate is ignored.
        """
        key: object
        if inspect.ismethod(subscriber):
            method = weakref.WeakMethod(subscriber, self._forget)
            key = method
            reference: Callable[[], Subscriber[E] | None] = method
        else:
            key = subscriber
            reference = _strong(subscriber)
        self._subscribers.setdefault(key, reference)

        def unsubscribe() -> None:
            self._forget(key)

        return unsubscribe

    def _forget(self, key: object) -> None:
        self._subscribers.pop(key, None)

    def publish(self, event: E, /) -> None:
        """Deliver the event to every subscriber, then raise one group for the failures.

        An event published during delivery waits in a queue, so every subscriber sees events in
        publication order. Each event goes to a snapshot of the subscribers.
        """
        self._pending.append(event)
        if self._delivering:
            return
        self._delivering = True
        errors: list[Exception] = []
        try:
            while self._pending:
                current = self._pending.popleft()
                for reference in tuple(self._subscribers.values()):
                    subscriber = reference()
                    if subscriber is None:
                        continue
                    try:
                        subscriber(current)
                    except Exception as error:
                        errors.append(error)
        finally:
            self._delivering = False
        if errors:
            raise ExceptionGroup("subscribers failed", errors)

    def __len__(self) -> int:
        """The number of registered subscribers. A dead bound method has already been removed."""
        return len(self._subscribers)
