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

- Name the forces that decide between refactoring and rewriting, and the test that measures each.
- Write a parity table that runs the legacy engine and a rewrite on the same consignments and lists every difference.
- Record deliberate differences so the parity test fails on a new one and on a stale one.
- Route consignments between the two engines with a strangler-style router, and run the rewrite in shadow.
- Say what the router costs and when it can be deleted.

## Why this matters

A band tariff written as an `if`/`elif` chain invites a rewrite. The limits and prices are data, and a `Tariff` that holds them, with a bisection to find the band, looks like the better program. The temptation is to write it, run its own tests and swap it in.

A first draft of that rewrite can pass its own tests and still quote a 5 kg consignment from the next band's price, because the difference between `bisect_left` and `bisect_right` moves each band limit from one band to the other (`test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries`). Martin Fowler's [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) page names the trap: "Replacements seem easy to specify, but often it's hard to figure out the details of existing behavior." The details here are whether a limit belongs to the band below it, and what happens to a zone nobody listed.

{% include excalidraw.html name="36-refactor-or-rewrite" caption="Figure 36.1: A router serves migrated zones from the rewrite and the rest from the legacy engine, and can run the rewrite in shadow. A parity table holds the two to the same quotes, and a first draft with exclusive band limits fails it." %}

Read the figure from the top. A `Consignment` ("zone and weight") has one arrow down to a wide accent box, `Router` ("zone in migrated?"). Two arrows leave it. The left one, labelled "yes", goes to `rating.quote` ("Tariff; bisect_left keeps limits inclusive"). The right one, labelled "no", goes to `legacy.RateEngine.quote` ("served"). A dashed arrow runs from the legacy box to a dashed box, "rewrite in shadow", which says that when `report` is set the result is compared, never served, and a `Mismatch` is reported on a difference. Both engine boxes have an arrow down to a bar, "parity table" ("the rows that differ must equal ACCEPTED_DIFFERENCES"). A dashed box at the lower right, "first draft with bisect_right" ("differs at the band limits"), has a dashed arrow to that bar.

## The forces

Michael Feathers's *Working Effectively with Legacy Code* opens with "Changing Software", which breaks the risk of a change into three questions: what has to change, how you will know it changed correctly, and how you will know nothing else broke. A rewrite is a large change, so the same questions apply to it at a larger scale. Four forces turn them into a decision, and each has a witness in the example.

**How much existing behaviour can be named.** If you can list the inputs and outputs that must survive, a replacement has an oracle. The witness is the parity table in `PARITY_ROWS`, which prices the same consignments through both engines and lists the rows where they disagree.

**Which behaviour should change.** A legacy engine holds behaviour somebody wanted and behaviour nobody chose. The witness is `ACCEPTED_DIFFERENCES`, the written list of rows where the rewrite is meant to differ.

**Whether a seam exists to route by.** A rewrite that takes one slice at a time needs a place to split the traffic. Here the zone is that place, and `Router` is the code that uses it.

**What the transitional code costs.** Running two engines needs code that exists only for the move. In the example that is the router and `legacy.py`, and `test_with_every_zone_migrated_the_legacy_engine_is_never_called` shows the point at which both can go.

[Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}) sets out forces as the frame for a design choice. The refactoring route, small steps under tests that pin behaviour, has its own chapter: [Fowler vs Feathers, contrasted and combined]({{ '/docs/35-fowler-vs-feathers/' | relative_url }}). Getting inherited code under test in the first place is the subject of [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}).

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

The `else` below the ASIA branch prices every other zone from the EU price list, so an unknown zone gets a quote. AFRICA at 5 kg quotes 13.20, the same as EU at 5 kg (`test_the_legacy_engine_prices_an_unknown_zone_as_eu`). The module keeps the fallback as found, because the engine is the thing the rewrite is measured against.

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

The rewrite refuses AFRICA with a `RatingError` that names the zone (`test_the_rewrite_refuses_an_unknown_zone`). Both engines put a weight equal to a limit in the lower band: 5 kg quotes 13.20 and 5.001 kg quotes 27.50 in each (`test_band_limits_include_the_boundary_weight`). In the rewrite that is the job of `bisect_left`. The [bisect documentation](https://docs.python.org/3/library/bisect.html) says of it: "If x is already present in a, the insertion point will be before (to the left of) any existing entries." A limit equal to the weight gives that band's own index, and `bisect_right` gives the next one.

## The parity table

A parity table is a list of consignments run through both engines. The test compares the outcome of each, an amount or a refusal, and collects the ids of the rows that differ. Ian Cartwright, Rob Horn and James Lewis describe the aim in "Patterns of Legacy Displacement", where [Feature Parity](https://martinfowler.com/articles/patterns-legacy-displacement/feature-parity.html) is defined as: "Replicate existing functionality of a legacy system using a new technology stack." The table is how this example asks for parity, with the exceptions written down.

```python
# Weights sit on every limit (5, 20, 50 kg), just above 5 and 50 kg, and well above the last band.
_WEIGHTS = ("0.5", "5", "5.001", "20", "20.5", "50", "50.001", "60")
PARITY_ROWS = [(zone, kg) for zone in ("EU", "ASIA") for kg in _WEIGHTS] + [("AFRICA", "5")]

# The rewrite refuses an unknown zone; the legacy engine prices it as EU. That was decided.
ACCEPTED_DIFFERENCES = ["AFRICA-5"]
```

The rows sit on each limit, just above 5 and 50 kg, and past the last band, for EU and ASIA, plus one unknown zone. That choice makes the boundary visible. The first draft agrees with the legacy engine at 0.5, 20.5 and 60 kg, and at 5.001 and 50.001 kg. Without the 50.001 rows, moving the last limit from 50 to 51 fails only the first-draft test, which shares the tariff; with them, the rewrite's own parity test fails too.

`test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted` asserts that the list of differing ids equals `ACCEPTED_DIFFERENCES`, in table order. A new divergence adds an id the list doesn't hold. A stale entry fails too: make the legacy engine refuse AFRICA with the rewrite's message, `no tariff for zone 'AFRICA'`, and the same test fails with `Right contains one more item: 'AFRICA-5'`. The list records a decision, so a reviewer who sees it grow can ask who made that decision.

The first draft lives in the test fixtures, because it is the mistake the table exists to catch. Its band line is the whole difference from `rating.quote`:

<!-- fmt:off -->
```python
    band = bisect_right(tariff.upper_kg, kg)
```
<!-- fmt:on -->

`test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries` runs it through the same comparison and asserts the exact list: `EU-5`, `EU-20`, `EU-50`, `ASIA-5`, `ASIA-20`, `ASIA-50` and `AFRICA-5`. The bisect page says that `bisect_right` "returns an insertion point which comes after (to the right of) any existing entries of x in a." The draft agrees with the legacy engine on the other ten rows, and the table finds the seven it doesn't. The failure reads as a list of ids in table order because the comparison builds a list. A dictionary comparison would print differing keys in set order under pytest 9.2.0, which changes from run to run.

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

A migrated zone goes to the rewrite and any other zone is served by the legacy engine (`test_the_router_serves_migrated_zones_from_the_rewrite`, `test_the_router_serves_other_zones_from_the_legacy_engine`). The router routes calls and converts no interface, so it isn't the Adapter pattern; [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) covers that one. The router is a seam in the sense of [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}), `migrated` is its enabling point, and the zone is what it routes by.

The router is transitional. [Transitional Architecture](https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html), another pattern from Cartwright, Horn and Lewis, is defined as: "Software elements installed to ease the displacement of a legacy system that we intend to remove when the displacement is complete." That fits. With EU and ASIA both in `migrated`, a legacy quoter that raises isn't reached and both zones still quote (`test_with_every_zone_migrated_the_legacy_engine_is_never_called`), so the router and `legacy.py` can be deleted together. The module-level binding, `quote_routed`, migrates ASIA only (`test_the_standard_router_migrates_asia_only`).

With `report` set, the router also runs the rewrite on the zones it hasn't taken over, and compares the result without serving it. Martin Fowler's [Dark Launching](https://martinfowler.com/bliki/DarkLaunching.html) entry describes calling new behaviour without users seeing it: "It's done to assess the additional load and performance impacts upon the system before making a public announcement of the new capability." The aim differs here, because the router compares quotes and doesn't assess performance. A difference becomes a `Mismatch` holding both amounts, and the caller still gets the legacy quote (`test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote`). A refusal from the rewrite is reported as a mismatch too, as text beginning `RatingError` (`test_shadow_mode_reports_a_refusal_as_a_mismatch`), and agreement reports nothing (`test_shadow_mode_is_silent_when_the_engines_agree`).

mypy holds the rewrite to the legacy call shape. A rewrite that takes a zone and a weight, where the legacy engine takes a consignment, is rejected where it is passed to `Router`. The test runs a snippet through `mypy.api` with `--strict`, and checks the exit status, the error code and a fragment of the message. The snippet's output is:

```text
<string>:13: error: Argument 2 to "Router" has incompatible type "Callable[[str, Weight], RateQuote]"; expected "Callable[[Consignment], RateQuote]"  [arg-type]
```

A second snippet passes `quote` itself and is accepted (`test_mypy_requires_the_rewrite_to_take_a_consignment`). Annotating `RateQuoter` as `Callable[..., RateQuote]` makes that test fail, so the check comes from the alias on `Router`'s fields.

## Refactor or rewrite: the decision

Refactor while the structure can reach the target shape in behaviour-preserving steps under a characterisation table. Rewrite a slice when the target changes behaviour by decision, as here, where the data-driven `Tariff` also refuses a zone the chain priced as EU and `ACCEPTED_DIFFERENCES` records that change. A rewrite needs three things before it takes traffic: a parity table, an accepted-differences list and a seam to route by. Without them the rewrite has no oracle, and its tests restate what its author expected.

The four forces give the questions to ask. If the table of behaviour can't be written, you can't say what parity means. If differences are accepted without a name against them, the list isn't recording decisions. If no seam exists, a rewrite is all or nothing. If the transitional code would cost more than the structure it replaces, refactor.

<blockquote class="ai-sidebar" markdown="1">

**Rewriting behind a router.** A request to "rewrite the rating engine" names no oracle, so nothing says the new quotes must match the old ones at a band limit. Paste a prompt that keeps both engines running:

> Write `rating.quote` beside the legacy `RateEngine`, not in place of it. Add a parity table with every zone, a weight on each band limit and one just above it, and one above the last band, and assert that the list of rows where the two engines differ equals `ACCEPTED_DIFFERENCES`. Route consignments through `Router`: send only the zones in `migrated` to the rewrite, and run it in shadow for the rest.

If `ACCEPTED_DIFFERENCES` grew in the diff, ask who decided that quote should change.

</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then, from the example directory, `uv run pytest` runs 15 test functions as 19 cases, and `uv run mypy --strict src tests` checks the example. Each experiment below changes a scratch copy and nothing else, after deleting the copy's `.venv` and running `uv sync --locked --all-packages` again. The first changes the rewrite's band search: in `src/refactor_or_rewrite/rating.py`, replace `bisect_left` with `bisect_right` in the import and in the call. Then:

```bash
uv run pytest -q 2>&1 | grep -E '^(FAILED|ERROR|E {3}[^ ]|E {7}[^ ]|E {9}[^ ]|E {11}[^ ]|(tests|src)/.*Error$|[0-9]+ (passed|failed|errors?))'
uv run mypy --strict src tests
```

```text
E       AssertionError: assert ['EU-5', 'EU-...ASIA-50', ...] == ['AFRICA-5']
E         At index 0 diff: 'EU-5' != 'AFRICA-5'
E         Left contains 6 more items, first extra item: 'EU-20'
E         Use -v to get more diff
tests/test_parity.py:43: AssertionError
E       AssertionError: assert ['27.50', '27.50'] == ['13.20', '27.50']
E         At index 0 diff: '27.50' != '13.20'
E         Use -v to get more diff
tests/test_parity.py:75: AssertionError
E       AssertionError: assert '60.50' == '33.00'
E         - 33.00
E         + 60.50
tests/test_strangler.py:21: AssertionError
E       AssertionError: assert ['27.50', '60.50'] == ['13.20', '33.00']
E         At index 0 diff: '27.50' != '13.20'
E         Use -v to get more diff
tests/test_strangler.py:70: AssertionError
FAILED tests/test_parity.py::test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted
FAILED tests/test_parity.py::test_band_limits_include_the_boundary_weight[rewrite]
FAILED tests/test_strangler.py::test_the_router_serves_migrated_zones_from_the_rewrite
FAILED tests/test_strangler.py::test_with_every_zone_migrated_the_legacy_engine_is_never_called
4 failed, 15 passed in 0.95s
Success: no issues found in 9 source files
```

Four tests fail. The parity test lists the six boundary ids that the table holds beyond `AFRICA-5`. The rewrite case of the limit test quotes 27.50 at 5 kg. Two router tests fail as well: ASIA at 5 kg quotes 60.50 where 33.00 is expected. mypy exits 0, since the change moves a value and not a type. The three shadow tests still pass. They drive the router with a weight of 0.5 kg, with the first draft, and with an unknown zone, and none of those reaches a limit through the real rewrite. The parity table is what pins the limits.

The second experiment restores `rating.py` and, in `tests/test_parity.py`, replaces the `ACCEPTED_DIFFERENCES` line with `ACCEPTED_DIFFERENCES: list[str] = []`. The same two commands print:

```text
E       AssertionError: assert ['AFRICA-5'] == []
E         Left contains one more item: 'AFRICA-5'
E         Use -v to get more diff
tests/test_parity.py:43: AssertionError
FAILED tests/test_parity.py::test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted
1 failed, 18 passed in 0.93s
Success: no issues found in 9 source files
```

One test fails, and it names the one difference the rewrite is meant to make. mypy exits 0 again.

## What you can do now

- Name the forces and their tests: the named behaviour is `PARITY_ROWS`, the behaviour that should change is `ACCEPTED_DIFFERENCES`, the seam is the zone that `Router` reads, and the transitional cost ends in `test_with_every_zone_migrated_the_legacy_engine_is_never_called`.
- Write a parity table: `PARITY_ROWS` runs both engines on 17 rows, and `test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries` shows it finding seven differences in a first draft.
- Record deliberate differences: `test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted` compares against `ACCEPTED_DIFFERENCES`, and the second experiment shows it failing when the entry goes.
- Route and run in shadow: `Router` serves by zone, and `test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote` reports a `Mismatch` while the caller keeps the legacy quote.
- Say what the router costs: it goes with `legacy.py` once every zone is in `migrated`, and `quote_routed` shows the state in between, with ASIA only.

## For deeper coverage

Martin Fowler's [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) page and Ian Cartwright, Rob Horn and James Lewis's "Patterns of Legacy Displacement" ([Feature Parity](https://martinfowler.com/articles/patterns-legacy-displacement/feature-parity.html) and [Transitional Architecture](https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html)) cover the approach, and Fowler's [Dark Launching](https://martinfowler.com/bliki/DarkLaunching.html) entry covers running new behaviour unseen. Michael Feathers's *Working Effectively with Legacy Code* (2004) has the chapters "Changing Software" and "How Do I Know That I'm Not Breaking Anything?". Martin Fowler's *Refactoring* (second edition) is the catalogue of behaviour-preserving changes. The [bisect documentation](https://docs.python.org/3/library/bisect.html) defines both insertion points. The books are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
