---
layout: example
order: 14
title: "State and finite state machines"
description: A consignment lifecycle written as a read-only transition table and as frozen states matched with assert_never, with tests for what mypy checks, what it can't, and a seeded transit-delay model.
github_path: examples/14-state-and-finite-state-machines
card_eyebrow: "Selecting behaviour · State"
card_title: "A lifecycle in a table and in a match"
card_blurb: "Booked to delivered as a read-only frozendict and as frozen states under assert_never, one behaviour table for both forms, and a transit-delay model that is reproducible because its generator is injected."
---

One consignment lifecycle witnesses what State becomes in Python. Each test asserts the behaviour
named in its title.

## The table form

`TRANSITIONS` maps a status and an event kind to the next status in a read-only `frozendict`. An
absent pair is a `TransitionError`. Tests walk the table: every status is reachable from booked and
delivered is terminal. mypy checks each entry's types and not its legality.

## The match form

`apply_event` matches on a frozen state, guards each legal arm on the event kind, lists every state
in one illegal arm and ends in `assert_never`. A state added to the union is a mypy error until
every match handles it, and a wildcard arm hides it. One behaviour table runs both forms.

## The state-object form

The class-per-state form is a test fixture that passes the same table. Adding an operation fails at
each return site, and a state class that nothing returns is never checked.

## A probabilistic machine

`simulate_transit` draws each day's delay from an injected `random.Random`. The same seed gives the
same voyage, a shared generator gives a different second run, and the module generator is left
alone.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/14-state-and-finite-state-machines
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
