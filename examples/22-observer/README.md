# Observer

A subject that tells an open set of parties about handling events without knowing them. The
chapter's thesis is that Observer survives: Python removes the Observer interface, because a
subscriber is any callable that takes the event, and the contract remains. It decides in what order
subscribers run, whether one failure stops the rest, what happens when a subscriber subscribes,
unsubscribes or publishes during delivery, and how long the signal keeps a subscriber alive. Port
codes and consignment ids are illustrative. `Signal` is documented as single-threaded, and the
example has no thread or async test.

## What it witnesses

Delivery.

- `Signal[E]` holds subscribers in a dict, in subscription order. `subscribe` returns an
  `Unsubscribe` callable, and a duplicate is ignored. `type Subscriber[E] = Callable[[E], None]`
  replaces an Observer interface, and mypy checks both the subscriber's event type and the
  published event.
- `publish` delivers to every subscriber and then raises one `ExceptionGroup`
  ("subscribers failed") holding the failures in order. A plain list of callables stops at the first
  failure. The signal recovers after a failed delivery, and also after a subscriber raises
  something that isn't an `Exception`, because `_delivering` is reset in a `finally`.
- The comparison form `_ListSignal` is a fixture in `tests/conftest.py`: a list of callables
  iterated live, with no `try`. It is the `plain-list` parameter of `signal_form`, so it runs the same
  order and unsubscribe tables as `Signal`. Its hazards have their own tests, because they fail on
  purpose.

Lifetime.

- A bound method is held through `weakref.WeakMethod`, whose callback removes the entry. A
  `TrackingHistory` the application dropped is gone, and the signal no longer calls it. A plain list
  keeps it alive and still calls it.
- The trade-offs are tested: a subscriber nobody else holds is dropped, a lambda is held strongly, a
  lambda that closes over its owner keeps the owner alive, an owner with slots and no weak-reference
  slot is refused at `subscribe` with `TypeError`, and a reference cycle holds a subscriber until the
  collector runs. Unsubscribing after the owner has gone is harmless.
- Every lifetime test builds its subscriber in a helper or deletes its names, then calls
  `gc.collect()` before asserting. The cycle test pauses the collector with the `collector_paused`
  fixture and restores its state.

Re-entrancy.

- Delivery iterates a snapshot. A subscriber added during delivery gets the next event, and an
  unsubscribe during delivery skips no one, where the plain list skips one.
- An event published during delivery is queued and delivered after the current event, so every
  subscriber sees events in publication order. Immediate nested delivery in the plain list reverses
  them.

Static checks.

- mypy refuses a subscriber typed for another event and publishing a wrong event. It accepts a
  typo in a string-topic bus with `Any` payloads (a reduced model in `test_static.py`, not part of the
  example), and it accepts a slotted subscriber that fails at run time.

## Layout

- `src/observer/domain.py`: `ConsignmentId`, `HandlingKind`, `HandlingEvent`.
- `src/observer/signal.py`: `Subscriber`, `Unsubscribe`, `Signal`.
- `src/observer/tracking.py`: `TrackingHistory`.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
```

## What the tests verify

`tests/test_delivery.py`

- `test_subscribers_are_called_in_subscription_order`: both forms.
- `test_an_unsubscribed_subscriber_gets_no_more_events`: both forms.
- `test_subscribing_twice_delivers_once`: a function and a bound method.
- `test_one_failing_subscriber_does_not_stop_the_rest`: one `ExceptionGroup` with the `RuntimeError`.
- `test_a_plain_list_stops_at_the_first_failing_subscriber`: the later subscriber is not called.
- `test_every_failure_is_reported_after_delivery`: one and two failures, in order.
- `test_tracking_history_records_events_in_order`: booked, loaded, departed.
- `test_the_signal_accepts_new_events_after_a_failed_delivery`: the next event is delivered.
- `test_the_signal_accepts_new_events_after_an_interrupted_delivery`: a `BaseException` from a subscriber.

`tests/test_lifetime.py`

- `test_a_plain_list_keeps_an_abandoned_subscriber_alive`: alive after `del` and `gc.collect()`, and still called.
- `test_a_bound_method_subscriber_is_dropped_when_its_owner_goes`: gone, and `len` is 0.
- `test_a_subscriber_that_dies_during_delivery_is_skipped`: an earlier subscriber drops the owner of a later one.
- `test_a_subscriber_nobody_else_holds_is_dropped`: `TrackingHistory().record`.
- `test_a_lambda_subscriber_is_held_strongly`: still called after `gc.collect()`.
- `test_a_lambda_that_closes_over_its_owner_keeps_it_alive`: the history survives.
- `test_a_slotted_subscriber_without_a_weakref_slot_is_refused`: `TypeError` at `subscribe`.
- `test_a_subscriber_in_a_reference_cycle_stays_until_the_collector_runs`: alive until `gc.collect()`.
- `test_unsubscribe_is_safe_after_the_owner_has_gone`: twice, without error.

`tests/test_reentrancy.py`

- `test_a_subscriber_added_during_delivery_gets_the_next_event`: not the current one.
- `test_unsubscribing_during_delivery_does_not_skip_another_subscriber`: remover, a, b.
- `test_a_plain_list_skips_a_subscriber_when_one_unsubscribes_during_delivery`: remover, b.
- `test_an_event_published_during_delivery_waits_its_turn`: cleared, then delivered.
- `test_an_immediately_delivered_nested_event_arrives_out_of_order`: delivered, then cleared.

`tests/test_static.py`

- `test_mypy_refuses_a_subscriber_for_another_event_type`: `[arg-type]`.
- `test_mypy_refuses_publishing_the_wrong_event`: `[arg-type]`.
- `test_mypy_accepts_a_typo_in_a_string_topic_bus`: clean, for a typo and a wrong payload (a reduced model).
- `test_mypy_cannot_see_a_subscriber_that_refuses_weak_references`: clean.

Classes and functions named with a leading underscore in `tests/conftest.py` are test fixtures and
aren't part of the model code.
