---
title: "r01 feature spikes: findings"
order: 6
output: false
---

# r01 feature spikes

Evidence for chapters that depend on language features. Code lives in
`spikes/feature-spikes` (package `feature_spikes`); spikes are retired in the iteration
whose example covers the claim. Recorded 2026-11-03, Python 3.14.10, mypy 2.4.1,
pytest 9.2.0. Workspace layout decisions (S4a) are in `spikes/S4a-findings.md`.

| PDP | Spike | Verdict |
| --- | --- | --- |
| 010 | Decorator pattern vs `@decorator` | **go** (framing adjusted) |
| 011 | Protocol, ParamSpec, PEP 695 generics | **go** |
| 012 | singledispatch on 3.14 | pending |
| 013 | `__init_subclass__` vs metaclass registry | pending |
| 014 | `match` + `assert_never` | pending |
| 015 | GIL and asyncio determinism | pending |

## PDP-010 Decorator pattern vs `@decorator`: go

Files: `decorator_vs_syntax.py`, `test_decorator_vs_syntax.py` (3 consecutive green runs).

Proven:
- GoF stack (`FuelSurcharge`, `VolumeDiscount`, `Vat`, `HandlingFee` frozen dataclasses,
  no base class) still satisfies the `RateCalculator` Protocol (mypy).
- Stacks are data: `compose(base, layers)` with `type Layer = Callable[[RateCalculator], RateCalculator]`.
- Layers added and removed per consignment at runtime; the inner object is wrapped, never mutated.
- `@retry(attempts=, on=)` re-invokes on listed exceptions, gives up after N, ignores
  unlisted ones; `@audited(sink)` records to an injected sink; `__name__`, `__doc__`,
  `__wrapped__` preserved through two stacked decorators.
- `@` replaces the function object at definition time (`f is not f.__wrapped__`;
  `retry(...)(plain)` is the same rebinding without `@`); GoF wrappers leave classes untouched.
- Independence: the composition uses no `@`; an `@`-wrapped function has no `quote`.
- PEP 695 `def retry[**P, R](...)` accepted by mypy 2.4.1; signatures preserved
  (`reveal_type` gives `def (carrier: str, n: int =) -> decimal.Decimal`; bad calls are `[arg-type]` errors).

Adjustments for the chapter:
- **Pure percentage layers commute** (discount then VAT == VAT then discount). The
  "order matters" demo must use an additive fee, a cap, or rounding.
- `@audited` must be a factory, `@audited(sink)`; a bare form needs global state.
- `__wrapped__` is not on `Callable`; reading it needs `# type: ignore[attr-defined]` (one sentence).
- Exception names: ruff N818 wants an `Error` suffix; name it `CarrierTimeoutError` in reader code.
- Overlap case (a decorator function returning a wrapper object) gets one paragraph, not a section.
- Open with the two one-liners: `Vat(FuelSurcharge(BaseRate(...)))` vs
  `quote_carrier = retry(...)(quote_carrier)`. Teach `functools.wraps` + `ParamSpec` as the syntax-specific part.

## PDP-011 Protocol, ParamSpec, PEP 695: go

Files: `typing_generics.py`, `test_typing_generics.py`.

Proven:
- Structural conformance without a base class; PEP 695 `Quoter[T: Consignment]` infers
  contravariance (no `contravariant=True`); a narrower `HazmatQuoter` is rejected as `Quoter[Consignment]`.
- `typing.override` sets `__override__`; mypy rejects a misspelled override
  (`Method "qoute" is marked as an override, but no base method was found with this name [misc]`).
- `cheapest[T](options, key)` infers T correctly.
- Callback Protocol `RateStrategy.__call__(self, c, /)` accepts def, lambda and bound
  method; **use positional-only `/`** or parameter names must match.
- `@runtime_checkable` checks name presence only: wrong signature and even a
  non-callable attribute pass `isinstance`.
- Non-runtime Protocol in `isinstance`: static `[misc]` error, runtime `TypeError`.

Key surprise for the Protocol and testing chapters:
- **mypy gives no protection when a mock stands in for a Protocol parameter.** `Mock()`,
  `Mock(spec=...)`, `MagicMock(spec=...)` and `create_autospec(..., instance=True)` are all
  accepted because typeshed types them as `Any`, not because the spec is checked.
  `create_autospec` does enforce the call signature at runtime (`TypeError: missing a
  required argument`); a bare `Mock` accepts anything. Recommend autospec and say plainly
  that mocks bypass the static check.
