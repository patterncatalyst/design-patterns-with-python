---
layout: example
order: 40
title: "Working with AI and LLM tools"
description: Three hand-written drafts of pricing code reviewed through a static gate, a shape review and a behaviour oracle, with the model client behind a Protocol and a recorded fake.
github_path: examples/40-working-with-ai-and-llm-tools
card_eyebrow: "Putting it together · Working with AI and LLM tools"
card_blurb: "Three drafts written for the book fail different sets of gates: types and lint, the pattern shape rules and a behaviour oracle. A recorded fake stands in for the model client, and no test uses the network."
card_title: "Three drafts, three gates"
---

One shipping domain witnesses the argument. A `price` function over a `PricingRule` is the code
under review, and three drafts of it are text files in the example's tests. The drafts were written
for the book as data to review.

## Three gates

`mypy --strict` and ruff pass the typed class hierarchy and fail the untyped factory. The shape
review in `review_gate.shape` flags both class drafts and passes the callable one. The behaviour
oracle runs a draft over a generated grid of consignments and lists the three half-cent rows that
the two rounding drafts price differently from the recorded answers.

## A seam for the model client

`Assistant` is a Protocol with one method, `reply`. `RecordedAssistant` replays recorded replies and
refuses a prompt it has no reply for. `propose` gates each reply and sends the findings back in the
next prompt, stopping at the first accepted reply or after its attempts. The package imports no
network module, and mypy refuses an assistant without `reply`.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then change into the example directory:

```bash
cd examples/40-working-with-ai-and-llm-tools
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
