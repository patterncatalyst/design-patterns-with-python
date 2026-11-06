---
layout: example
order: 25
title: "Visitor, Memento, and Interpreter"
description: Tracking events as a closed union with one match per operation, a booking that rolls back from a frozen snapshot while its audit trail survives, and a tariff as a tree that is both priced and explained, with singledispatch and accept visitors, shallow and deep mementos and closure rules as comparisons.
github_path: examples/25-visitor-memento-interpreter
card_eyebrow: "Coordination · Visitor, Memento and Interpreter"
card_blurb: "Each operation over the event union is one match that mypy checks for every kind. A rollback restores a frozen snapshot and leaves the audit alone, and one tariff tree is both priced and explained."
card_title: "Closed or open, what to capture, and a grammar with two readings"
---

One shipping domain witnesses all three patterns. A tracking feed has five event kinds, a booking
batch can fail midway, and a pricing team writes tariff rules. Each test asserts the behaviour
named in its title.

## The visitor

`describe` and `status_after` are each one `match` over `HandlingEvent`, ending in `assert_never`,
so mypy reports an event left out and the run time refuses an object outside the union. A
singledispatch visitor and the accept form describe the same journey as comparisons. The
singledispatch form gives an unregistered event its fallback's answer without an error, and mypy accepts
it. The accept form puts a method on every event class.

## The memento

`rollback(booking)` restores a frozen `BookingSnapshot` when a block raises an `Exception`, appends a record and
re-raises. The audit isn't captured, so a refused amendment survives. A shallow copy shares the
document set and keeps a document attached inside the failed block. A deep copy restores the audit
and erases the refused attempt.

## The interpreter

`Expr` is a tree of frozen nodes. `evaluate` prices a consignment and `explain` writes the rule
back as a sentence. Equal trees compare and hash equal, closures built the same way don't, and
currencies don't mix. mypy reports a node left out of `evaluate`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/25-visitor-memento-interpreter
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
