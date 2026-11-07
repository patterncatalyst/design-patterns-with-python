---
layout: example
order: 39
title: "Final project"
description: One booking request shipped through rating, stowage, the carrier, customs, billing and tracking, with its undo steps held on an ExitStack and one composition root.
github_path: examples/39-final-project
card_eyebrow: "Putting it together · Final project"
card_blurb: "A booking that customs holds releases its slot and cancels the carrier booking in reverse order. The tracking event waits for the commit, and one function chooses the concrete parts."
card_title: "One booking, seven areas"
---

One shipping domain witnesses the argument. A `BookingRequest` goes through a `PricingRule`, a
`StowagePlan`, a `CarrierGateway`, a chain of clearance stages, an `Invoice` and a `Signal` that
feeds a `TrackingHistory`. The carrier is an in-memory stand-in.

## Undo in reverse

Each step registers its inverse on an `ExitStack` with `callback`. A held declaration runs them in
reverse order, so the carrier booking is cancelled and then the slot is released. `pop_all()` hands
the callbacks away once clearance has passed, and the booking stands.

## Publish after the commit

`BookingDesk.ship` publishes `BOOKED` after `pop_all()`. An eager desk in the test fixtures
publishes it before clearance, and a held booking then leaves a tracking event in the history.

## One composition root

`build_desk` is the only module that names `FastlineGateway` and `FastlineClient`, and it takes the
pricing rule as a parameter. The acceptance helper lists what is missing when the rating, the
carrier, the clearance or the tracking is left out. mypy refuses a gateway without `cancel`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/39-final-project
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
