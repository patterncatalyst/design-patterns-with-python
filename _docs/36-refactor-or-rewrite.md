---
title: "Refactor or rewrite"
order: 36
layout: tutorial
sectionid: docs
part: "changing-inherited-code"
description: "Decide between reworking an inherited engine and replacing it from the forces in front of you, prove a rewrite matches the old quotes before it takes traffic, and route one zone at a time."
---

## Learning objectives

By the end of this chapter you can:

- Name the forces that decide between refactoring and rewriting, and the check that measures each.
- Write a parity table that runs the legacy engine and a rewrite on the same consignments and lists every difference.
- Record accepted differences so the parity check fails on a new one and on a stale one.
- Route consignments between the two engines with a strangler-style router, and run the rewrite in shadow.
- Say what the router costs and when it can be deleted.

## Why this matters

A band tariff written as an `if`/`elif` chain invites a rewrite. The limits and prices are data, and a `Tariff` that holds them, with a bisection to find the band, looks like the better program. The temptation is to write it, run its own tests and swap it in.

A first draft of that rewrite can pass its own tests and still quote a 5 kg consignment from the next band's price, because `bisect_left` and `bisect_right` put a band limit in different bands. Martin Fowler's [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) page names the trap: "Replacements seem easy to specify, but often it's hard to figure out the details of existing behavior." The details here are whether a limit belongs to the band below it, and what happens to a zone nobody listed.

{% include excalidraw.html name="36-refactor-or-rewrite" described="true" caption="Figure 36.1: A router serves migrated zones from the rewrite and the rest from the legacy engine, and can run the rewrite in shadow. A parity table holds the two to the same quotes, and a first draft with exclusive band limits fails it." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-36-refactor-or-rewrite" markdown="1">
From the top. A `Consignment` ("zone and weight") has one arrow down to a wide accent box, `Router` ("zone in migrated?"). Two arrows leave it. The left one, labelled "yes", goes to `rating.quote` ("Tariff; bisect_left keeps limits inclusive"). The right one, labelled "no", goes to `legacy.RateEngine.quote` ("served"). A dashed arrow runs from the legacy box to a dashed box, "rewrite in shadow", which says that when `report` is set the result is compared, never served, and a `Mismatch` is reported on a difference. Both engine boxes have an arrow down to a bar, "parity table" ("the rows that differ must equal ACCEPTED_DIFFERENCES"). A dashed box at the lower right, "first draft with bisect_right" ("differs at the band limits"), has a dashed arrow to that bar.
</div>
</details>

The figure shows the router splitting traffic by zone, with the parity table holding both engines to the same quotes.

## The forces

Michael Feathers's *Working Effectively with Legacy Code* opens with "Changing Software", which breaks the risk of a change into three questions: what has to change, how you'll know it changed correctly, and how you'll know nothing else broke. A rewrite is a large change, so the same questions apply at a larger scale. Four forces turn them into a decision:

| Force | What it asks | Witness |
| --- | --- | --- |
| How much existing behaviour can be named | Can you list the inputs and outputs that must survive? Then a replacement has an oracle. | `PARITY_ROWS`, run through both engines |
| Which behaviour should change | Which of the legacy behaviour did somebody want, and which did nobody choose? | `ACCEPTED_DIFFERENCES` |
| Whether a seam exists to route by | Is there a place to split the traffic one slice at a time? | `Router`, split by zone |
| What the transitional code costs | What exists only for the move, and when can it go? | `Router` and `legacy.py`, deleted together |

[Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}) sets out forces as the frame for a design choice. The refactoring route, small steps under tests that pin behaviour, is [Fowler vs Feathers, contrasted and combined]({{ '/docs/35-fowler-vs-feathers/' | relative_url }}), and getting inherited code under test is [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}).

## A legacy engine and its rewrite

The legacy engine prices a consignment by weight band. Each band includes its upper limit, and a fallback nobody removed prices other zones:

<!-- fmt:off -->
```python
        kg = consignment.weight.kilograms
        if consignment.zone == "ASIA":
            if kg <= 5:
                price = Decimal("30.00")
            elif kg <= 20:
                price = Decimal("55.00")
            elif kg <= 50:
                price = Decimal("98.00")
            else:
                raise RatingError(f"no band for {kg} kg")
```
<!-- fmt:on -->

The `else` below the ASIA branch prices every other zone from the EU price list, so AFRICA at 5 kg quotes 13.20, the same as EU at 5 kg. The fallback stays as found, because the legacy engine is what the rewrite is measured against.

The rewrite holds the bands as data and finds the band by bisection:

```python
def quote(consignment: Consignment, /, *, tariff: Tariff = STANDARD_TARIFF) -> RateQuote:
    """Price a consignment from the tariff. An unknown zone is refused."""
    try:
        band_prices = tariff.prices[consignment.zone]
    except KeyError:
        raise RatingError(f"no tariff for zone {consignment.zone!r}") from None
    kg = consignment.weight.kilograms
    # bisect_left keeps each limit inclusive: a weight equal to a limit stays in its band.
    band = bisect_left(tariff.upper_kg, kg)
    if band == len(tariff.upper_kg):
        raise RatingError(f"no band for {kg} kg")
    total = (band_prices[band] * MARGIN).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return RateQuote(consignment.id, Money(total))
```

The rewrite refuses AFRICA with a `RatingError` that names the zone. Both engines put a weight equal to a limit in the lower band: 5 kg quotes 13.20 and 5.001 kg quotes 27.50 in each. The [bisect documentation](https://docs.python.org/3/library/bisect.html) says of `bisect_left`: "If x is already present in a, the insertion point will be before (to the left of) any existing entries." A limit equal to the weight gives that band's own index, and `bisect_right` gives the next one.

## The parity table

A parity table is a list of consignments run through both engines, comparing the outcome of each (an amount or a refusal) and collecting the ids of the rows that differ. Ian Cartwright, Rob Horn and James Lewis, in "Patterns of Legacy Displacement", define [Feature Parity](https://martinfowler.com/articles/patterns-legacy-displacement/feature-parity.html) as: "Replicate existing functionality of a legacy system using a new technology stack." The table asks for parity, with the exceptions written down.

```python
# Weights sit on every limit (5, 20, 50 kg), just above 5 and 50 kg, and well above the last band.
_WEIGHTS = ("0.5", "5", "5.001", "20", "20.5", "50", "50.001", "60")
PARITY_ROWS = [(zone, kg) for zone in ("EU", "ASIA") for kg in _WEIGHTS] + [("AFRICA", "5")]

# The rewrite refuses an unknown zone; the legacy engine prices it as EU. That was decided.
ACCEPTED_DIFFERENCES = ["AFRICA-5"]
```

The rows sit on each limit, just above 5 and 50 kg, and past the last band, for EU and ASIA, plus one unknown zone. Without the 50.001 rows, moving the last limit from 50 to 51 would pass the rewrite's parity check.

The list of differing ids must equal `ACCEPTED_DIFFERENCES`, in table order, so it fails both ways:

- **A new divergence** adds an id the list doesn't hold.
- **A stale entry** fails too: make the legacy engine refuse AFRICA with the rewrite's message, `no tariff for zone 'AFRICA'`, and the check fails with `Right contains one more item: 'AFRICA-5'`.

The list records a decision, so a reviewer who sees it grow can ask who made it.

The first draft lives in the fixtures, as the mistake the table exists to catch. Its band line is the whole difference from `rating.quote`:

<!-- fmt:off -->
```python
    band = bisect_right(tariff.upper_kg, kg)
```
<!-- fmt:on -->

The bisect page says `bisect_right` "returns an insertion point which comes after (to the right of) any existing entries of x in a." The draft agrees with the legacy engine on ten rows and differs on seven: `EU-5`, `EU-20`, `EU-50`, `ASIA-5`, `ASIA-20`, `ASIA-50` and `AFRICA-5`. The comparison builds a list, so the failure reads in table order every run; a dictionary comparison under pytest 9.2.0 prints differing keys in set order, which changes from run to run.

## A strangler-style router

Parity says the rewrite is ready for a zone. Taking the zone over needs a place in the code where the decision is made. Fowler's description of the approach is to "move bits of behavior from the legacy system into the new code base." `Router` is that place:

<!-- fmt:off -->
```python
    legacy: RateQuoter
    rewrite: RateQuoter
    migrated: Container[str]
    report: Callable[[Mismatch], None] | None = None

    def __call__(self, consignment: Consignment) -> RateQuote:
        if consignment.zone in self.migrated:
            return self.rewrite(consignment)
        served = self.legacy(consignment)
        if self.report is not None:
            self._compare(consignment, served, self.report)
        return served
```
<!-- fmt:on -->

The router routes calls and converts no interface, so it isn't the Adapter pattern; [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) covers that one. It's a seam in the sense of [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}), with `migrated` as its enabling point.

The router is transitional. Cartwright, Horn and Lewis define [Transitional Architecture](https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html) as: "Software elements installed to ease the displacement of a legacy system that we intend to remove when the displacement is complete." With EU and ASIA both in `migrated`, a legacy quoter that raises is never reached and both zones still quote, so the router and `legacy.py` can be deleted together. The module-level binding, `quote_routed`, migrates ASIA only.

With `report` set, the router also runs the rewrite on the zones it hasn't taken over and compares the result without serving it. Fowler's [Dark Launching](https://martinfowler.com/bliki/DarkLaunching.html) entry names this use: "The old and new code can both be called and their results checked to see if there are changes with the new algorithm, but only one answer returned to the interface."

| Shadow outcome | Reported | Served |
| --- | --- | --- |
| Engines agree | nothing | legacy quote |
| Amounts differ | a `Mismatch` holding both amounts | legacy quote |
| Rewrite refuses | a `Mismatch` with text beginning `RatingError` | legacy quote |

mypy holds the rewrite to the legacy call shape. A rewrite that takes a zone and a weight is rejected where it's passed to `Router`:

```text
<string>:13: error: Argument 2 to "Router" has incompatible type "Callable[[str, Weight], RateQuote]"; expected "Callable[[Consignment], RateQuote]"  [arg-type]
```

`quote` itself is accepted. Annotating `RateQuoter` as `Callable[..., RateQuote]` removes the check, so it comes from the alias on `Router`'s fields.

## Refactor or rewrite: the decision

- **Refactor** while the structure can reach the target shape in behaviour-preserving steps under a characterisation table.
- **Rewrite a slice** when the target changes behaviour by decision. Here the data-driven `Tariff` also refuses a zone the chain priced as EU, and `ACCEPTED_DIFFERENCES` records that change.

A rewrite needs a parity table, an accepted-differences list and a seam to route by before it takes traffic. Without them it has no oracle, and its tests restate what its author expected. The four forces give the questions:

- If the table of behaviour can't be written, you can't say what parity means.
- If differences are accepted without a name against them, the list isn't recording decisions.
- If no seam exists, a rewrite is all or nothing.
- If the transitional code would cost more than the structure it replaces, refactor.

<blockquote class="ai-sidebar" markdown="1">

**Rewriting behind a router.** A request to "rewrite the rating engine" names no oracle, so nothing says the new quotes must match the old ones at a band limit. Keep both engines running:

> Write `rating.quote` beside the legacy `RateEngine`, not in place of it. Add a parity table with every zone, a weight on each band limit and one just above it, and one above the last band, and assert that the list of rows where the two engines differ equals `ACCEPTED_DIFFERENCES`. Route consignments through `Router`: send only the zones in `migrated` to the rewrite, and run it in shadow for the rest.

If `ACCEPTED_DIFFERENCES` grew in the diff, ask who decided that quote should change.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/36-refactor-or-rewrite
uv run pytest -q
uv run mypy --strict src tests
```

All 19 cases pass and mypy is clean. Run each experiment in a scratch copy of the repository with its own `.venv`:

- **Use `bisect_right` in the rewrite.** In `src/refactor_or_rewrite/rating.py`, replace `bisect_left` with `bisect_right` in the import and the call. Four cases fail: the parity check lists the six boundary ids beyond `AFRICA-5`, the rewrite quotes 27.50 at 5 kg, and the router quotes ASIA at 5 kg as 60.50 where 33.00 is expected. The shadow cases still pass, because none drives a limit through the real rewrite; the parity table is what pins the limits. mypy exits 0, since the change moves a value and not a type.
- **Empty the accepted list.** Restore `rating.py` and set `ACCEPTED_DIFFERENCES: list[str] = []` in `tests/test_parity.py`. One case fails, naming `AFRICA-5`, the one difference the rewrite is meant to make. mypy exits 0.

## What you can do now

- Name the forces and their witnesses: `PARITY_ROWS`, `ACCEPTED_DIFFERENCES`, `Router`, and the point where the router and `legacy.py` go.
- Write a parity table: `PARITY_ROWS` runs both engines on 17 rows and finds seven differences in a first draft.
- Record accepted differences: `ACCEPTED_DIFFERENCES` fails on a new divergence and on a stale entry.
- Route and run in shadow: `Router` serves by zone and reports a `Mismatch` while the caller keeps the legacy quote.
- Say what the router costs: it goes with `legacy.py` once every zone is in `migrated`, and `quote_routed` shows the state in between, with ASIA only.

## For deeper coverage

Martin Fowler's [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) page and Ian Cartwright, Rob Horn and James Lewis's "Patterns of Legacy Displacement" ([Feature Parity](https://martinfowler.com/articles/patterns-legacy-displacement/feature-parity.html) and [Transitional Architecture](https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html)) cover the approach, and Fowler's [Dark Launching](https://martinfowler.com/bliki/DarkLaunching.html) entry covers running new behaviour unseen, including old and new code side by side. Michael Feathers's *Working Effectively with Legacy Code* (2004) has the chapters "Changing Software" and "How Do I Know That I'm Not Breaking Anything?". Martin Fowler's *Refactoring* (second edition) is the catalogue of behaviour-preserving changes. The [bisect documentation](https://docs.python.org/3/library/bisect.html) defines both insertion points. The books are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
