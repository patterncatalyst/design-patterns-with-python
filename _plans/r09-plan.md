---
title: "r09 plan: chapters 19-20 (Part 7, composing and adapting structure)"
order: 9
output: false
render_with_liquid: false
---

# r09: chapters 19-20, Adapter, Facade and Bridge; the Decorator pattern, the `@decorator` syntax, and Proxy

Opus-planned 2026-11-04. Branch `release/r09` (from main at bfd0b4c, r08.x). This file is the source of truth for r09 scope, criteria and status. Executors never edit it; the orchestrator updates the status board. No toolchain work this iteration: Python 3.15.2, mypy 2.4.1, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.3 and uv 0.13.7 are unchanged. `uv.lock` changes only because two members are added.

## User decisions (proposed 2026-11-04, for the owner to confirm)

Each decision carries a recommendation. Nothing below is built until the owner answers.

Standing, not a decision: step ids are `J*`. `validate.py --claims` resolves `run: <id>` against the steps table of every `_plans/r*-plan.md` (`scripts/validate.py` globs `r[0-9]*-plan.md`, and the row regex needs `| <id> | ... | done |`). `grep -nE "^\| J[0-9]" _plans/*.md` matched nothing before this file.

1. **Bridge stays "survives", shown as booking kinds against carrier gateways.**
   - The abstraction side is two booking kinds, `StandardBooking` and `InsuredBooking`: frozen dataclasses that each hold a `gateway: CarrierGateway` and build their operation from its two primitives, `book` and `insure`.
   - The implementor side is the gateways that ch19's Adapter section produces. Without the split you'd need a class per pair (`_FastlineStandardBooking`, `_AircoInsuredBooking`, ...). That hierarchy is a test-only comparison fixture, run on the same booking table and counted with `ast`.
   - What survives is the decision: which axis is the abstraction, and which narrow set of primitives the implementor promises. The mechanism, a Protocol-typed field, belongs to "ISP, DIP, and dependency injection without a framework", and ch19 points there by title.
   - The measured cost (planning evidence C): widening the implementor Protocol breaks every implementor under mypy. Adding a booking kind costs nothing.

   **Recommend: yes.** Alternatives:
   - (b) Say Bridge dissolves into a Protocol parameter. That contradicts the r02 canonical map and the ch3 table row ("Two hierarchies varying independently, joined by a Protocol"), so both would have to be edited.
   - (c) Documentation kinds against output formats. That collides with ch26 (renderers, the `DocumentKind` class decorator) and ch31 (document dispatch tables).

2. **Proxy is an explicit Protocol wrapper in `src`, with `__getattr__` forwarding as a test-only comparison fixture.**
   - `CarrierGatewayProxy` caches `quote` per consignment and forwards `book` explicitly. mypy checks every Protocol member on it: a missing member is `[assignment]` with `is missing following "CarrierGateway" protocol member` (planning evidence C).
   - `_ForwardingGatewayProxy`, with `__getattr__(self, name) -> Any`, runs the same proxy table (`[explicit|forwarding]`). Its measured costs:
     - mypy accepts a typo and a wrongly typed use (evidence B, exit 0);
     - typing it `-> object` makes it fail the Protocol (evidence A);
     - a `runtime_checkable` `isinstance` is `False`, because 3.12+ uses `inspect.getattr_static` (evidence D, typing docs quoted);
     - a typo's `AttributeError` names the wrapped class;
     - dunders bypass it (`len()` raises `TypeError`).
   - `__getattr__` mechanics (`__getattribute__`, recursion, `__setattr__`) stay in "Dynamic attributes: __getattr__ and Proxy as a feature". `property` and `cached_property` stay in "Descriptors and properties". ch20 points to both by title. This follows the domain-model ch20/ch30 non-overlap rule and reconciliation rows 11-12, which stay with ch30.

   **Recommend: yes.** Alternative (b): a `__getattr__` forwarding proxy in `src` as the lesson. "The three-way split" already shows that form, and the probes show mypy is blind through it.

3. **Facade gets its own short section (about 280 words), as a module function with a narrow public surface.**
   - `desk.ship(consignment, carrier, *, gateways, declared_value=None) -> Booking` is the one call. It picks the gateway from a read-only registry, chooses the booking kind, and turns an unknown code into a domain error. `desk.__all__` and its type hints name no SDK type (a test reads them).
   - The section's point is that in Python a module already is the facade object. What survives is choosing the few calls, and translating units, shapes and errors behind them.
   - The test-only `_book_by_branching` caller is the "calling code branches on carrier code" failure from domain row 19. It sends kilograms to the pounds API.

   **Recommend: yes.** Alternative (b): fold Facade into the Adapter section as one paragraph. The chapter title names three patterns, and a two-sentence Facade would read as an omission.

4. **Two carrier SDK stand-ins, not three; domain row 19 is amended.** Domain row 19 says "Three carrier APIs behind one CarrierGateway", but the rules allow only `FASTLINE` and `AIRCO`.
   - (a) Two stand-ins in `sdks.py` with deliberately different shapes:
     - `AircoClient`, whose `book` and `insure` already match the Protocol, so it's used with no adapter (the duck-typing case, evidence E1);
     - `FastlineClient`, whose `submit_shipment(payload)` takes pounds and returns a numeric receipt, and whose `add_cover` takes cents. It needs `FastlineGateway`, an object adapter that translates shape, units and errors (E2, E4).
   - A class adapter (`_FastlineClassAdapter(FastlineClient)`) is a test-only comparison fixture on the same adapter table. It leaks `submit_shipment` to callers.
   - Row 19 becomes "Two carrier SDKs of deliberately different shapes behind one `CarrierGateway`".

   **Recommend: (a).** Alternative (b): a third stand-in, a legacy Fastline API in pounds, selected by a setting. That needs a configuration path the chapter doesn't otherwise use, and it adds words to the tightest chapter in the iteration.

5. **The ch20 split, and who owns `functools.wraps`.**
   - ch20's member holds all three halves named in domain row 20:
     - the Decorator pattern: `RateCalculator`, `BaseRate`, `Discount`, `Surcharge`, `Tax`, `compose`, `Layer`, `layers_for`;
     - the `@decorator` syntax: `retry` and `audited` as PEP 695 `[**P, R]` factories, and `quote_carrier`;
     - the caching proxy: `CarrierGatewayProxy`.
     ch19's member holds nothing from ch20.
   - `functools.wraps` and `ParamSpec` are **used** in `retry` and `audited`, not taught. The domain-model non-overlap rule says "the syntax-specific teaching (`functools.wraps`, `ParamSpec`) stays in ch26". So reconciliation row 6 ("A `functools.wraps`-less wrapper loses `__name__` and signature") moves to ch26: its Ch cell becomes 26, with the note "moved from ch20 (r09 decision 5)".
   - ch20 keeps one static witness, that `ParamSpec` keeps `quote_carrier`'s signature for mypy (evidence F). The prose gives it one sentence and points to "Decorators done right".
   - Row 5 is resolved by ch20 (rows 101-103).
   - ch20 also owns one syntax stacking-order witness (`@audited` over `@retry` reports once per call; the reverse reports once per attempt), because that order is fixed at definition time, which is the disambiguation. Stacking order for caches stays in ch26.

   **Recommend: yes.** Alternative (b): ch20 teaches `wraps` and `ParamSpec` (`inspect.signature` against `reveal_type`, evidence F) and resolves row 6 itself. That makes ch26 re-teach or skip its own core, and it breaks the written non-overlap rule.

Also proposed for the owner (no decision needed unless declined):
- No new books. Every book cited is already in `bibliography.html`. Bracketed items below are dropped if the prose agents can't verify them.
- The spike finding "Pure percentage layers commute" is refined (evidence G): it holds in exact arithmetic, but per-layer rounding to cents splits two percentage layers by a cent on 6,940 of 20,000 sampled prices. The orchestrator adds a dated r09 note to `_plans/spikes.md` at J2. CLAUDE.md's wording is the owner's to change; the plan doesn't touch it.

## Planning evidence

All probes were read-only. Because this planning run is read-only, no scratch directory or file was created, so `.../scratchpad/plan9` doesn't exist. Every probe ran as inline code from the session scratchpad as the working directory, outside the repo, so the root config didn't apply:
- Runtime: `uv run --project <repo> python -I -c CODE` (3.15.2).
- mypy: `uv run --project <repo> python -m mypy --strict --warn-unreachable --cache-dir /dev/null --no-error-summary -c SNIPPET` (mypy 2.4.1).

Snippets are reduced models. Line numbers will differ and are never asserted. Every output is a prediction for the member until the build quotes it as observed.

**A. A `__getattr__ -> object` forwarding proxy against a two-member Protocol** (the proxy defines `book` only):
```
<string>:13: error: Incompatible types in assignment (expression has type "ForwardingProxy", variable has type "CarrierGateway")  [assignment]
<string>:13: note: Following member(s) of "ForwardingProxy" have conflicts:
<string>:13: note:     track: expected "Callable[[str], tuple[str, ...]]", got "object"
```

**B. The same proxy with `__getattr__ -> Any`:** exit 0. `reveal_type(p.track)` is `Revealed type is "Any"`. `p.trakc("CN-1")` and `n: int = p.track("CN-1")` are both accepted silently.

**C. An explicit wrapper missing a Protocol member:**
```
<string>:12: error: Incompatible types in assignment (expression has type "CachingGateway", variable has type "CarrierGateway")  [assignment]
<string>:12: note: "CachingGateway" is missing following "CarrierGateway" protocol member:
<string>:12: note:     track
```

**D. The forwarding proxy at run time** (a `@runtime_checkable` Protocol with `book` and `track`; the inner class has `__len__`):
```
isinstance: False
track: ('BOOKED',)
hasattr __len__: True
len: TypeError("object of type 'ForwardingProxy' has no len()")
typo: AttributeError("'Fastline' object has no attribute 'trakc'")
dir has track: False
```
`isinstance` is `False` although `hasattr` finds the forwarded members. The typing docs (fetched 2026-11-04, 3.15.2) say: "Changed in version 3.12: The internal implementation of `isinstance()` checks against runtime-checkable protocols now uses `inspect.getattr_static()` to look up attributes (previously, `hasattr()` was used)."

**E. When duck typing suffices and when an adapter is needed** (Protocol `book(self, consignment_id: str, weight: Weight, /) -> str`, used through `ship(gateway: CarrierGateway)`):
- E1, same shape and named, non-positional-only parameters: exit 0 (the Protocol's `/` makes the names irrelevant).
- E2, a client with `submit_shipment(payload: dict[str, str]) -> int`: `<string>:16: error: Argument 1 to "ship" has incompatible type "FastlineClient"; expected "CarrierGateway"  [arg-type]`. **No missing-member note was printed** (it was in C). Recorded as observed; tests don't assert the note.
- E3, the same shape with units in a `float`: a Protocol `book(self, consignment_id: str, kilograms: float, /)` and a client `book(self, consignment_id: str, pounds: float, /)`: exit 0. The unit mix-up passes silently.
- E4, the same client against the `Weight`-typed Protocol:
  ```
  <string>:16: error: Argument 1 to "ship" has incompatible type "LegacyClient"; expected "CarrierGateway"  [arg-type]
  <string>:16: note: Following member(s) of "LegacyClient" have conflicts:
  <string>:16: note:     Expected:
  <string>:16: note:         def book(self, str, Weight, /) -> str
  <string>:16: note:     Got:
  <string>:16: note:         def book(self, str, float, /) -> str
  ```
- Units: `Decimal(10) * Decimal("0.45359237")` is `4.53592370` (a 10 kg figure read as pounds books 4.54 kg). `Decimal(10) / Decimal("0.45359237")` is `22.04622621848775807229738013`. The executor fixes the pound factor's source (the 1959 international pound, exact) and quotes it in the README.

**F. `ParamSpec` and `functools.wraps`** (`retry[**P, R]` with `@wraps`; `bare[**P, R]` without `wraps`; an untyped decorator with `@wraps`). Runtime `inspect.signature`, `__doc__` and `__wrapped__`:
```
quote_carrier (carrier: str, kilograms: decimal.Decimal) -> decimal.Decimal 'Ask a carrier for a price.' True
wrapper (*args: P.args, **kwargs: P.kwargs) -> R None False
quote_untyped (carrier: str, kilograms: decimal.Decimal) -> decimal.Decimal None True
```
mypy:
```
<string>:43: error: Untyped decorator makes function "quote_untyped" untyped  [untyped-decorator]
<string>:51: note: Revealed type is "def (carrier: str, kilograms: decimal.Decimal) -> decimal.Decimal"
<string>:52: note: Revealed type is "def (carrier: str, kilograms: decimal.Decimal) -> decimal.Decimal"
<string>:53: note: Revealed type is "Any"
<string>:54: error: Argument 2 to "quote_carrier" has incompatible type "int"; expected "Decimal"  [arg-type]
<string>:55: error: Unexpected keyword argument "kilos" for "quote_carrier"  [call-arg]
```
- Surprise: `ParamSpec` keeps the static signature **without** `wraps`, and `wraps` keeps the runtime one even for an untyped decorator. The two tools read different things, and ch26 owns that lesson (decision 5).
- `[untyped-decorator]` is the mypy 2.4.1 code; don't assume `[misc]`. Not a ch20 claim.

**G. Layer order** (per-kg base, each layer rounding half-up to cents, 100 kg at 1.20, fee 15.00, tax 21 %, discount 10 %):
```
base 120.00
Tax(Discount) 130.68 Discount(Tax) 130.68
Tax(Surcharge) 163.35 Surcharge(Tax) 160.20
Discount(Surcharge) 121.50 Surcharge(Discount) 123.00
percent pairs differing under per-layer rounding: 6940 of 20000; first (Decimal('0.05'), Decimal('0.06'), Decimal('0.05'))
```
The additive fee makes order matter on every value. Two percentages agree at 120.00 but split by a cent at 0.05 per kg for 1 kg. The sweep covers per-kg prices 0.01 to 200.00 at 1 kg, Discount 10 then Tax 21 against the reverse.

**H. Stacks are values, rebound functions are not:**
```
stack eq: True hash eq: True
repr: Surcharge(inner=BaseRate(per_kg=Decimal('1.20')), fee=Decimal('15.00'))
rebound eq: False
unwrap is original: True one level: False
repr: <function quote_carrier at 0x...>
```
(The address was masked in the probe.)

**I. Layer slots under mypy** (`type Layer = Callable[[RateCalculator], RateCalculator]`, `compose(base, layers)`):
- `partial(Surcharge, fee=...)` and `partial(Tax, percent=...)` in a `tuple[Layer, ...]`: exit 0.
- A misspelt keyword: `Unexpected keyword argument "fees" for "Surcharge"; did you mean "fee"?  [call-arg]`.
- **`partial(Surcharge)` binding nothing: exit 0.** This is the known Strategy-chapter gap, so `src` uses small layer constructors (`surcharge(fee) -> Layer` returning a lambda), which mypy checks fully.
- A wrapper class without `price` in the slot: `Incompatible types in assignment (expression has type "tuple[type[Broken]]", variable has type "tuple[Callable[[RateCalculator], RateCalculator], ...]")  [assignment]`.
- An `@`-decorated function in a layer slot or a `RateCalculator` variable: two `[assignment]` errors, the second `expression has type "Callable[[Decimal], Decimal]", variable has type "RateCalculator"`.

Sources fetched 2026-11-04. The fetch tool paraphrases punctuation, so prose agents re-fetch and the page text wins.
- PEP 318 (https://peps.python.org/pep-0318/), Status Final, Python-Version 2.4. "On the name 'Decorator'": "There’s been a number of complaints about the choice of the name ‘decorator’ for this feature." "The major one is that the name is not consistent with its use in the GoF book." "The name ‘decorator’ probably owes more to its use in the compiler area – a syntax tree is walked and annotated." The equivalence block is `func = dec2(dec1(func))`, "without the intermediate assignment to the variable `func`". The location section has "they are obviously executed at the time the function is defined."
- PEP 3129 (https://peps.python.org/pep-3129/), Status Final, Python-Version 3.0. Abstract: "This PEP proposes class decorators, an extension to the function and method decorators introduced in PEP 318." "The following two snippets are semantically identical:" with `A = foo(bar(A))`.
- functools docs (https://docs.python.org/3/library/functools.html, banner 3.15.2): the `update_wrapper` and `wraps` entries were read in full. Quotable for ch20's single sentence: "Without the use of this decorator factory, the name of the example function would have been `'wrapper'`, and the docstring of the original `example()` would have been lost."
- Data model (https://docs.python.org/3/reference/datamodel.html, 3.15.2): `object.__getattr__`: "Called when the default attribute access fails with an `AttributeError` ..." and "Note that if the attribute is found through the normal mechanism, `__getattr__()` is not called." Special method lookup: "For custom classes, implicit invocations of special methods are only guaranteed to work correctly if defined on an object’s type, not in the object’s instance dictionary."
- typing docs (`runtime_checkable`, the 3.12 `getattr_static` note above).
- python-patterns.guide index (https://python-patterns.guide/): **no Adapter, Facade, Bridge or Proxy page.** The relevant pages are:
  - "The Composition Over Inheritance Principle" (https://python-patterns.guide/gang-of-four/composition-over-inheritance/). Its sections include "Solution #1: The Adapter Pattern", "Solution #2: The Bridge Pattern" and "Solution #3: The Decorator Pattern". Its example domain is logging (filters and outputs), so ch19 credits it for the framing only.
  - "The Decorator Pattern" (https://python-patterns.guide/gang-of-four/decorator-pattern/). Its sections are "Implementing: Static wrapper", "Tactical wrapper", "Dynamic wrapper" and "Caveat: Wrapping doesn't actually work". It says the `@decorator` feature is unrelated to the pattern, and it covers dunder lookup bypassing `__getattr__`.
  - Paraphrase only. No sentence is planned as a quote unless the prose agent re-fetches it.
- O'Reilly MCP: *Fluent Python* 2nd ed. (Ramalho, 2022) and *Effective Python* 3rd ed. (Slatkin, 2024) are listed; chapter and item titles were not visible. Bracketed.
- GoF: not quotable (r06 finding). Bracketed items, used only if a prose agent verifies them in the book; otherwise the idea is described without attribution:
  - [GoF describes a class adapter (by inheritance) and an object adapter (by composition)];
  - [GoF gives Wrapper as another name for Adapter and for Decorator];
  - [GoF notes that a Facade doesn't stop clients using subsystem classes directly];
  - [GoF lists remote, virtual and protection proxies and smart references];
  - [GoF contrasts Decorator, which adds responsibilities, with Proxy, which controls access through the same interface].

Repo facts:
- **Chapter status.** ch19-20 are `kind = "pattern"`, `has_example = true`, `status = "stub"`, part 7 (`composing-adapting-structure`). The stubs carry `## How it works` and "Draft pending" descriptions. "Composite and Flyweight" is ch21 (r10), also part 7, and isn't touched.
- **Reconciliation.** Rows run 1-96, so r09 adds 97-106. Open rows 5 (ch20) and 6 (ch20, moved to ch26 by decision 5) are updated. Rows 11-12 (ch30) are untouched. `CLAIMS_FIRST_ENFORCED = 47`.
- **Figures.** `_data/diagrams.yml` has 19 entries; r09 makes 21.
- **Already taught, so not repeated** (each gets a pointer by title and at most one sentence):
  - `Surcharge` over `BaseRate`, `calculator_for`, `@audited(sink)` on `quote_carrier`, the independence test, `CarrierGatewayProxy` with `__getattr__`, `cached_property` laziness: "The three-way split: dissolve, survive, disambiguate". ch20 excerpts none of that member's code, and its new ground is order, stacks as data, the syntax's definition-time order, and the measured Proxy forms.
  - "Duck typing removes the adapter only when the shapes already match" and `submit_shipment(payload)`: "What 1994 assumed, and what Python dissolves". ch19 measures it (E1-E4).
  - In-memory `FastlineGateway`/`AircoGateway`, the composition root, narrow Protocols: "ISP, DIP, and dependency injection without a framework".
  - Positional-only `/` in Protocols, `runtime_checkable` checking names only: "Protocol, duck typing, and structural typing with mypy". ch20 adds only the `getattr_static` consequence for a forwarding proxy.
  - `RateCalculator` and LSP: "SRP, OCP, and LSP in Python".
  - `partial` binding nothing in a typed slot: "Strategy: the callable".
  - A registry of constructors, `CarrierKit`: "Factory Method and Abstract Factory".
  - `functools.cache` not call-once under threads (the proxy's cache is single-threaded): "Singleton: module, Borg, and metaclass".
  - Negative fixtures, the mypy-API helper and deletion tables: "Proving it works: pytest, pytest-mock, and mypy".
- **Later chapters whose ground must not be taken:**
  - "Decorators done right" (`wraps`, `ParamSpec`, `inspect.signature`, a parametrised decorator used bare, stacking order on caches, class decorators);
  - "Descriptors and properties" (`property`, `cached_property`, `__set_name__`);
  - "Dynamic attributes: __getattr__ and Proxy as a feature" (`__getattr__`/`__getattribute__`/`__setattr__`, recursion, the lazy `TrackingHistory`; no gateway there);
  - "Composite and Flyweight" (consolidated shipments);
  - "Metaclasses, __init_subclass__, and registries" (auto-registered adapters);
  - "Seams in Python: monkeypatch, injection, and duck typing";
  - "Refactor or rewrite" (the strangler-style adapter);
  - "The GIL and performance".
- **Test names.** Every name below was checked against `grep -rhoE "def test_\w+" examples spikes --include='*.py'` (403 names): no collision. Names avoided because they exist: `test_an_unknown_carrier_code_is_an_unknown_carrier_error`, `test_the_carrier_registries_are_read_only`, `test_weight_must_be_positive_and_finite`, `test_proxy_forwards_only_missing_attributes`, `test_stacking_order_changes_result` (spike), `test_layers_are_added_and_removed_at_runtime_per_consignment` (spike), `test_retry_gives_up_after_n_attempts` (spike).
- r08-plan shows I6 and I7 as `todo` although r08 merged. No r09 token depends on them; the orchestrator may close them separately.

## What is new in each chapter

**ch19 (Adapter, Facade and Bridge survive).** Two earlier chapters argue that duck typing removes an adapter only when shapes match, and show in-memory adapters behind a composition root. This chapter adds:
- **The line, measured**: a client whose shape matches is used as is (E1). A different shape is `[arg-type]` (E2). A shape that matches with the wrong units passes silently while the unit is a `float` (E3), and is caught once the parameter is `Weight` (E4).
- **The adapter's real job**: translating call shape, units (kilograms to pounds in one place, `Weight.from_pounds`) and errors (an SDK rejection becomes `CarrierError`). An object adapter against a class adapter that leaks the SDK's own methods.
- **A Facade as a module function** whose public surface names no SDK type, against a caller that branches on the carrier code and sends kilograms to a pounds API.
- **Bridge as two axes**: booking kinds against carrier gateways, a class-per-pair fixture counted, and the cost of widening the implementor Protocol.

**ch20 (Decorator needs disambiguating; Proxy needs disambiguating).** "The three-way split" shows one `Surcharge`, one `@audited` and a `__getattr__` proxy. This chapter adds:
- **Order matters only with something non-commuting**: an additive fee changes the price with its position. Two percentages agree before rounding and split by a cent after it (evidence G, recorded).
- **The stack is data**: `layers_for(consignment)` chooses layers per consignment while the program runs, `compose` wraps them, and the stack compares by value. Rebound functions don't.
- **The syntax is a definition-time rebinding** (PEP 318's equivalence quoted). Its stacking order is fixed when the module loads: `@audited` over `@retry` reports once per call, and the reverse reports once per attempt. mypy refuses an `@`-decorated function where a `RateCalculator` belongs.
- **Proxy against Decorator**: the same interface. A proxy returns what the gateway returns and controls access (a cache); a layer changes the price. The explicit proxy against the forwarding form, measured on one table.

## Approach

- **Thesis wording.**
  - ch19 says Adapter, Facade and Bridge survive. Duck typing dissolves the adapter only where shapes and units already agree. A module is a facade's container, but choosing the narrow surface is still design. Bridge's mechanism is a Protocol field, and the split along two axes is the decision.
  - ch20 says the Decorator pattern and the `@decorator` syntax need disambiguating: wrapper objects composed while the program runs, stacks as data, against a function rebinding at definition time. They share a word and nothing else. Proxy needs disambiguating too: a surrogate object here, attribute interception in the later chapters. Never blur the names. In prose, "Decorator" alone means the pattern, and the syntax is "the `@decorator` syntax" or "the `@` form" (the naming chapter's rule).
- **Credit.**
  - GoF where each pattern is introduced, in plain paraphrase that doesn't track the Intent wording.
  - Rhodes: "The Composition Over Inheritance Principle" in ch19; "The Decorator Pattern" in ch20 (its point that the syntax is unrelated, and that dunders bypass `__getattr__`).
  - PEP 318, PEP 3129, the functools docs and the `__getattr__` and typing docs, quoted exactly from fetched pages.
- **Domain names** come from `_plans/shipping-domain-model.md` plus the supporting names below, recorded in domain rows 19-20 at J0. No new domain area and no new carrier codes. Port codes are UN/LOCODEs (`NLRTM`, `SGSIN`). Rates, fees, tax percentages and SDK shapes are illustrative, and each chapter says so once.
  - ch19 (Carrier, Consignment): `Weight` (with `from_pounds`, `pounds`), `POUND_IN_KILOGRAMS`, `Consignment`, `Booking`, `Money`, `CarrierGateway`, `AircoClient`, `FastlineClient`, `FastlineReceipt`, `FastlineRejectedError`, `FastlineGateway`, `StandardBooking`, `InsuredBooking`, `ship`, `default_gateways`, `BookingError`, `CarrierError`, `UnknownCarrierError`.
  - ch20 (Rating, Carrier): `RateCalculator`, `BaseRate`, `Discount`, `Surcharge`, `Tax`, `Layer`, `discount`, `surcharge`, `tax`, `compose`, `layers_for`, `TAX_RATES`, `HEAVY_FEE`, `DANGEROUS_GOODS_FEE`, `retry`, `audited`, `quote_carrier`, `CarrierGateway`, `CarrierQuote`, `CarrierGatewayProxy`, `CarrierTimeoutError`, `RatingError`, `Money`, `Consignment`, `Weight`.
- **One uv member per chapter.** Each is standalone, re-declares its small domain module and imports no other member:
  - `examples/19-adapter-facade-bridge` (project `adapter-facade-bridge`, package `adapter_facade_bridge`);
  - `examples/20-decorator-pattern-vs-decorator-syntax-and-proxy` (project `decorator-proxy`, package `decorator_proxy`).
- **mypy witnesses** copy the r08 `_run`/`_codes` helper with the **anchored** regex `re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)` (r08 correction: the unanchored form matched `[str]` inside generics). Each asserts exit status, an exact `_codes()` set and one or two stable substrings, never line numbers or notes whose presence varies (E2 printed no note). Wherever possible a snippet imports the real `src` names, so deleting a check in `src` changes the snippet's result. Reduced models are named as such in the prose (criterion 23).
- **Comparison code** (the owner's 2026-11-04 rule). Every comparison form is real, tested on the same behaviour table **as a conftest fixture param** (the r08 lesson: "on the same table" means a fixture param), and shown in at most one excerpt per chapter, with the idiomatic code as the lesson.
  - ch19: `_FastlineClassAdapter` (`gateway_form` param `object-adapter|class-adapter`), the class-per-pair bookings (`booking_form` param `bridge|class-per-pair`), and `_book_by_branching` (its own failing test, because it fails the table on purpose).
  - ch20: `_ForwardingGatewayProxy` (`proxy_form` param `explicit|forwarding`).
  - All of them live in `tests/conftest.py` behind fixtures, because sibling test imports are blocked under `--import-mode=importlib` (r08 I1b correction).
- **Negative witness rule.** Every check in `src` has a test that fails when the check is deleted. The deletion tables (J1a, J1b) name the test and say why it sees the deletion. A row whose witness was predicted, not run, is marked "executor check".
- **Global state and determinism.**
  - No `mock`, `mocker`, `monkeypatch`, `print(`, `sleep` or wall clock.
  - Every registry is a `frozendict` typed as `Mapping`. SDK stand-ins record calls in instance attributes. ch20's `audited` sink is injected; `src` applies `@retry` only, and `audited(sink)(quote_carrier)` is applied where a sink exists (a test or a composition function). There's no module-level log.
  - Retry and timeout tests use a scripted fake gateway that raises `CarrierTimeoutError` a set number of times, so no clock or backoff is involved. `retry` has no delay parameter (one sentence: backoff is out of scope).
  - The proxy's cache is a plain `dict` per instance; the prose says it's single-threaded and points to "Singleton: module, Borg, and metaclass" for the thread trap.
  - `filterwarnings = ["error"]` stays active. Test-local `runtime_checkable` Protocols are decorated directly (the 3.15 deprecation).
- **Counts** of test functions and cases come from the code, and the pytest summary line wins (r07 and r08 misadded).

Rejected:
- `abc.ABC` adapter bases or booking-kind hierarchies in `src` (decisions 1, 4).
- A `__getattr__` proxy in `src` (decision 2).
- Teaching `wraps`, `ParamSpec`, `inspect.signature` or bare-versus-called decorator factories in ch20 (decision 5).
- `partial(Surcharge, ...)` as the layer constructor in `src` (evidence I's unbound-partial gap).
- A time-based cache expiry or retry backoff (non-deterministic, and out of scope).
- A third carrier code; a real carrier SDK or HTTP client; any UI.
- `typing.cast` or `Any` in `src`: the `Any` return lives only in the forwarding fixture.

## Per-chapter spec

### ch19: Adapter, Facade, and Bridge (pattern, has_example = true, bucket: survives)

Thesis: Adapter's force is two parts that disagree on shape. Structural typing removes the adapter only when the shapes, and the units inside them, already agree. Otherwise you write the translation, once, in one class. A Facade narrows a subsystem to the few calls a caller needs, and in Python it's usually a module function. Bridge separates two axes of variation, joined by a narrow Protocol. All three survive as design, and each is lighter than in 1994.

Sections (about 2,400 prose words, max 2,500; at most six excerpts, at most one of them from a comparison fixture):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - a 10 kg consignment booked through a pounds API as 10 lb, by a caller that branches on the carrier code (test 5);
   - a client whose units differ behind a `float` parameter, which mypy accepts (test 17);
   - booking kinds multiplied by carriers into a class per pair (test 12).
3. Figure plus one paragraph (~60).
4. `## When no adapter is needed` (~300):
   - GoF credited for Adapter in paraphrase. Bucket: survives. One sentence pointing to "What 1994 assumed, and what Python dissolves".
   - `AircoClient` sits in the registry unwrapped (tests 1, 15); a different shape is `[arg-type]` (test 16). Fresh output.
   - Positional-only `/` makes parameter names irrelevant: one sentence pointing to "Protocol, duck typing, and structural typing with mypy".
5. `## An adapter translates shape, units and errors` (~450). Excerpt `FastlineGateway` and `Weight.from_pounds`:
   - The payload the SDK receives (test 2), exact pound conversion (test 4), a rejection turned into `CarrierError` (test 10), cover converted to cents (test 13 through the Fastline gateway).
   - Same-shape units in a `float` pass mypy (test 17); a `Weight` parameter catches them (test 18).
   - [GoF's class and object adapters if verified]: the class-adapter fixture passes the same table and leaks `submit_shipment` (test 3). At most one short excerpt of its header.
6. `## A Facade is a function with a narrow surface` (~280). Excerpt `ship`:
   - One call books each carrier (test 8). An unknown code is refused (test 6), and the registry is read-only (test 7). The public surface names no SDK type (test 9).
   - The branching caller (test 5) described, not excerpted. One sentence pointing to "ISP, DIP, and dependency injection without a framework" for the composition root.
7. `## Bridge: two axes, one narrow Protocol` (~420). Excerpt `StandardBooking` and `InsuredBooking`:
   - Every kind works with every carrier (test 11, both forms). The class-per-pair fixture needs N×M classes where the bridge needs N+M (test 12).
   - An insured booking records the declared value (test 13) and refuses a missing or non-positive one (test 14).
   - The cost sits on the implementor: a gateway missing a primitive is a mypy error (test 19). Keep the primitive set small. Credit Rhodes's "The Composition Over Inheritance Principle" for this framing.
8. `## When not to use it` (~180): one carrier and no SDK mismatch (call the client); a facade over a subsystem with one caller (inline it); a bridge with one axis that actually varies (a parameter is enough); an adapter that only renames (structural typing already covers it). Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written adapters.** An assistant asked to "integrate a carrier" may write an `AbstractCarrierAdapter` base class, an adapter for a client whose shape already matches, a `float` weight passed straight through to an API that expects pounds, a facade that returns the SDK's own receipt type, or one subclass per booking kind and carrier. Check: does the client already satisfy the Protocol; are units converted in one place through a value type; are SDK errors translated; does the facade's signature name only domain types; is each axis of variation one parameter rather than a subclass per pair.</blockquote>

   Each check maps to tests 1 and 15, 4 and 18, 10, 9, 11-12.
9. `## Build, run, observe` (~220 plus output). Experiments, each in a fresh scratch copy (delete the copy's `.venv`, re-sync, and confirm `adapter_facade_bridge.__file__` points into the copy), one change, reverted. Run `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'`, then `uv run mypy --strict src tests`, three times:
   - (a) In `FastlineGateway.book`, send `weight.kilograms` instead of `weight.pounds`. Expected: test 2 (both forms, or object-adapter only if the class adapter overrides independently; executor check) and test 8[FASTLINE] fail on the payload weight; mypy exits 0. Quote as observed.
   - (b) Add `def cancel(self, reference: str, /) -> None: ...` to `CarrierGateway`. Expected: mypy reports `AircoClient` and `FastlineGateway` (codes as observed, likely `[dict-item]` at the registry and `[arg-type]` at the booking kinds); pytest still passes. That's the cost of widening the implementor. Quote as observed.
10. `## For deeper coverage` (~130): GoF (Adapter, Facade, Bridge); Rhodes, "The Composition Over Inheritance Principle"; PEP 544; the typing docs (Protocols); [Percival and Gregory, *Architecture Patterns with Python*, on adapters at a boundary, only if a prose agent verifies the chapter]; the bibliography link.

Figure `19-adapter-facade-bridge` (vertical):
- Top accent box `ship(consignment, carrier, ...)`, "Facade: one call, domain types only".
- Then two boxes side by side, `StandardBooking` and `InsuredBooking`, "Bridge: each kind holds a gateway".
- Then `CarrierGateway`, "book, insure: the narrow Protocol".
- It forks to `AircoClient`, "shape already matches: no adapter", and `FastlineGateway`, "Adapter: shape, pounds, errors", with an arrow down to a muted `FastlineClient`, "carrier SDK".
- A side note on `FastlineGateway`: `Weight.from_pounds`, "units converted in one place".
- No numbers in the SVG.

Caption draft (41 words with prefix): "Figure 19.1: One call, two axes, one translation. The facade picks a gateway and a booking kind; each kind works through the narrow gateway Protocol, which one client already satisfies and the other reaches through an adapter that converts units."

### ch20: Decorator the pattern vs @decorator the syntax, and Proxy (pattern, has_example = true, bucket: needs disambiguating)

Thesis: "Decorator" names two unrelated things in Python. The pattern is a wrapper object with the wrapped object's interface, composed while the program runs, so a stack is data: chosen per consignment, compared by value, and never mutating what it wraps. The `@decorator` syntax rebinds a function name once, at definition time, and PEP 318 itself records that the name doesn't match the GoF book. Proxy shares the pattern's shape and differs in intent: it controls access and returns what the subject returns. In Python the honest proxy is an explicit class that mypy can check. Open with the two one-liners: `Tax(Surcharge(BaseRate(...), fee), percent)` against `quote_carrier = retry(...)(quote_carrier)`.

Sections (about 2,450 prose words, max 2,500; at most six excerpts, at most one from the forwarding fixture):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200). Three failures:
   - a heavy consignment's tax computed before the surcharge, which under-charges by 3.15 (test 2);
   - an audit placed under `@retry`, which reports three calls for one quote (test 12);
   - a forwarding proxy with a typo that mypy accepts (test 26).
3. Figure plus one paragraph (~60).
4. `## Two things called Decorator` (~250):
   - The two one-liners. GoF credited for Decorator in paraphrase; Rhodes's "The Decorator Pattern" on the unrelated feature; PEP 318's "On the name 'Decorator'" sentence quoted. Bucket: needs disambiguating.
   - One sentence pointing to "The three-way split: dissolve, survive, disambiguate" for the first witness, and one to "Naming patterns for teams and AI assistants" for the naming rule.
5. `## The pattern: a stack of layers` (~480). Excerpt `Surcharge`, `Layer`, `compose` and `layers_for`:
   - A layer wraps and leaves the inner calculator unchanged (test 1). `compose` puts the last layer outermost (test 6).
   - Order matters with an additive fee (test 2's table, fresh values). Two percentages agree at 120.00 and split by a cent after rounding (test 3, `run:` evidence file).
   - `layers_for` chooses the layers per consignment while the program runs (test 4). Stacks compare and hash by value (test 5). Mixed currencies are refused (test 27).
   - mypy checks each layer in a stack (test 23) and refuses an `@`-decorated function where a calculator belongs (test 22).
6. `## The syntax: a rebinding at definition time` (~430). Excerpt `retry` (the factory and the `@retry(...)` line on `quote_carrier`):
   - PEP 318's equivalence `func = dec2(dec1(func))` quoted; PEP 3129 credited for class decorators (one sentence).
   - The name is rebound once (test 8). `retry` re-invokes on listed errors and gives up after the last attempt (test 9), and lets others through (test 10). `audited(sink)` reports to an injected sink (test 11).
   - Stacking order is fixed when the module loads (test 12), and rebound functions don't compare by value (test 13).
   - `ParamSpec` keeps the call signature for mypy (test 24). One sentence, quoting the functools docs on `wraps`, pointing to "Decorators done right" for both. Neither mechanism has the other's attributes (test 14).
   - The overlap case, one paragraph: a `@` factory may return an object, as `functools.cache` does (test 15). It's still the syntax, because the rebinding happened at definition time.
7. `## Proxy: the same interface, controlling access` (~420). Excerpt `CarrierGatewayProxy`:
   - GoF credited for Proxy in paraphrase; [kinds of proxy and the Decorator contrast if verified].
   - The proxy asks the gateway once per consignment (test 16), forwards every booking (test 17), and doesn't cache a timeout (test 18). It returns what the gateway returns where a layer changes the price (test 19).
   - mypy reports a member missing from the explicit proxy (test 25).
   - The forwarding form passes the same table. Its costs: mypy accepts typos and wrong types through `Any` (test 26), `-> object` fails the Protocol (test 27b), a runtime-checkable `isinstance` is false (test 20, typing docs quoted), and a typo names the wrapped class (test 21). The data-model sentence on `__getattr__` and the special-method-lookup sentence are quoted.
   - Pointers by title to "Dynamic attributes: __getattr__ and Proxy as a feature" and "Descriptors and properties".
8. `## When not to use it` (~180): a single fixed adjustment (a function); layers that never vary per consignment (one calculator); a retry around an operation that isn't safe to repeat, such as a booking without an idempotency key; a caching proxy over data that must be fresh; a forwarding proxy where an explicit one would do. Then the sidebar:

   <blockquote class="ai-sidebar" markdown="1"> **Reviewing assistant-written decorators and proxies.** Asked for "a decorator", an assistant may write an `@` function where a runtime stack was needed, or a wrapper class where a definition-time `@retry` would do, and call either one "the Decorator pattern". It may also put an audit under a retry, or write a proxy with `__getattr__` returning `Any`. Check: is the choice made per consignment at run time (a layer stack) or once at definition (the `@` form); does the stack order put fixed fees and taxes where the rules say; is the audit above the retry; does the proxy define every Protocol member it promises; does the description use "Decorator" only for the pattern.</blockquote>

   Each check maps to tests 4-5, 2, 12, 25-26, 14 and 22.
9. `## Build, run, observe` (~220 plus output). Same scratch-copy rules and the same filter, then mypy, three times:
   - (a) In `layers_for`, put the tax layer before the heavy surcharge. Expected: test 4[heavy] and test 4[dangerous-goods] fail with the reordered price; mypy exits 0. Quote as observed.
   - (b) Delete `book` from `CarrierGatewayProxy`. Expected: member mypy reports the missing Protocol member wherever the proxy is typed as a `CarrierGateway` (code as observed); test 17[explicit] fails with `AttributeError`, and 17[forwarding] still passes. Quote as observed.
10. `## For deeper coverage` (~130): GoF (Decorator, Proxy); Rhodes, "The Decorator Pattern"; PEP 318; PEP 3129; PEP 612 (`ParamSpec`); PEP 695; the functools docs; the data model on `__getattr__`; [Ramalho, *Fluent Python* 2nd ed., on decorators and closures, and Slatkin, *Effective Python* 3rd ed., on `functools.wraps`, chapter and item titles only if verified]; the bibliography link.

Figure `20-decorator-pattern-vs-decorator-syntax-and-proxy` (two vertical columns):
- Left column, "Decorator pattern: while the program runs": `layers_for(consignment)`, then `compose(base, layers)`, then a nested-box stack `Tax`, `Surcharge`, `BaseRate`, with the note "a value: chosen per consignment".
- Right column, "@decorator syntax: at definition time": `@retry(attempts=3, on=...)`, then `def quote_carrier`, then "name rebound once".
- A dashed divider, "same word, unrelated mechanisms".
- Bottom accent box `CarrierGatewayProxy`, "Proxy: same interface, controls access (caches quote)", with a muted side box "forwarding with __getattr__: mypy sees Any".
- No numbers in the SVG.

Caption draft (40 words with prefix): "Figure 20.1: Two things called Decorator, and a proxy. Layers are chosen per consignment and stacked as a value while the program runs; the @ form rebinds a name once at definition; the proxy keeps the interface and controls access."

Citations, both chapters: verify each before writing; apply the bracketed fallbacks; quote no sentence unless it was checked on a fetched page; no comparison between languages.

## Example spec

### `examples/19-adapter-facade-bridge` (project `adapter-facade-bridge`, package `adapter_facade_bridge`)

`pyproject.toml` in the r08 shape (`requires-python = ">=3.15"`, no `[tool.*]`).

- `domain.py`:
  - `ConsignmentId = NewType`.
  - `POUND_IN_KILOGRAMS: Final = Decimal("0.45359237")`.
  - `Weight(kilograms: Decimal)`, frozen slotted: finite and positive, else `ValueError`; `from_pounds(cls, pounds: Decimal) -> Self`; a `pounds` property.
  - `Money(amount: Decimal, currency: str)`, frozen slotted.
  - `Consignment(id, weight, origin, destination)`, frozen slotted kw_only.
  - `Booking(carrier: str, reference: str, insured_for: Money | None = None)`, frozen slotted.
  - `BookingError(ValueError)`, `CarrierError(RuntimeError)`, `UnknownCarrierError(LookupError)`.
- `sdks.py` (stand-ins, "deliberately different shapes"; each records calls on the instance):
  - `AircoClient` with `book(self, consignment_id: str, weight: Weight) -> str` (returns `AC-<id>`) and `insure(self, reference: str, value: Money) -> None`.
  - `FastlineReceipt(tracking_number: int)`.
  - `FastlineRejectedError(Exception)`.
  - `FastlineClient` with `submit_shipment(self, payload: Mapping[str, str]) -> FastlineReceipt` (keys `ref`, `weight_lb`; raises `FastlineRejectedError` above an illustrative limit) and `add_cover(self, tracking_number: int, amount_cents: int, currency: str) -> None`.
- `gateways.py`:
  - `CarrierGateway` Protocol: `book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str` and `insure(self, reference: str, value: Money, /) -> None`.
  - `FastlineGateway(client: FastlineClient)`, an object adapter:
    - pounds quantised to 0.01 as a string in the payload;
    - reference `FL-<n>`;
    - `FastlineRejectedError` becomes `CarrierError` (`from` the original);
    - cover in integer cents from `Money`.
- `bookings.py`:
  - `StandardBooking(gateway)` and `InsuredBooking(gateway, declared_value: Money)`, frozen slotted. Each has `place(self, consignment, carrier: str) -> Booking`.
  - `InsuredBooking.__post_init__` raises `BookingError` for a non-positive value.
- `desk.py`:
  - `__all__ = ["ship", "default_gateways"]`.
  - `default_gateways() -> Mapping[str, CarrierGateway]` returns `frozendict({"AIRCO": AircoClient(), "FASTLINE": FastlineGateway(FastlineClient())})`.
  - `ship(consignment, carrier, *, gateways, declared_value: Money | None = None) -> Booking` chooses the booking kind. An unknown code raises `UnknownCarrierError(f"unknown carrier {carrier!r}")` from None.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `consignment` (`CN-1`, 10 kg, `NLRTM` to `SGSIN`).
- `carrier` params `FASTLINE|AIRCO`, each with the expected reference prefix.
- `gateway_form` params `object-adapter|class-adapter`, giving a Fastline gateway built over a fresh recording client, plus fixture `_FastlineClassAdapter(FastlineClient)`.
- `booking_form` params `bridge|class-per-pair`, plus the fixture classes `_CarrierBooking(ABC)`, `_FastlineStandardBooking`, `_FastlineInsuredBooking`, `_AircoStandardBooking`, `_AircoInsuredBooking`.
- `booking_kind` params `standard|insured`.
- `_book_by_branching(consignment, carrier, clients)`, the branching caller that passes `weight.kilograms` as `weight_lb`.

`test_adapter.py`:
1. `test_a_client_whose_shape_matches_needs_no_adapter`: `type(default_gateways()["AIRCO"]) is AircoClient`; a booking succeeds.
2. `test_the_fastline_adapter_translates_the_booking_call` x `gateway_form` (2): the recorded payload is `{"ref": "CN-1", "weight_lb": "22.05"}` (the executor confirms the quantised value) and the reference is `FL-...`.
3. `test_a_class_adapter_still_exposes_the_clients_own_methods`: `hasattr(class_adapter, "submit_shipment")`, and not on `FastlineGateway`.
4. `test_weight_converts_between_kilograms_and_pounds_exactly`: `Weight.from_pounds(Decimal(1)).kilograms == POUND_IN_KILOGRAMS`; 10 kg reads `22.05` lb after quantising.
5. `test_a_pounds_api_called_with_kilograms_books_the_wrong_weight`: the branching caller records `weight_lb == "10"` for a 10 kg consignment, which `Weight.from_pounds` reads as 4.54 kg.
6. `test_an_unknown_carrier_is_refused_at_the_desk`: `"NOSUCH"`, matching `unknown carrier 'NOSUCH'`.
7. `test_the_desk_registry_is_read_only`: `# type: ignore[index]`; `TypeError` matching `does not support item assignment`; `not isinstance(..., dict)`.
20. `test_a_consignment_weight_must_be_positive_and_finite[zero|negative|nan]`.

`test_facade.py`:
8. `test_ship_books_each_carrier_through_one_call` x `carrier` (2).
9. `test_the_desk_names_no_sdk_type_in_its_public_surface`: `desk.__all__`; every value of `typing.get_type_hints(ship)` has a `__module__` other than `adapter_facade_bridge.sdks`.
10. `test_a_carrier_rejection_becomes_a_carrier_error`: over the illustrative limit; `CarrierError`, with `__cause__` a `FastlineRejectedError`.

`test_bridge.py`:
11. `test_every_booking_kind_works_with_every_carrier` x `booking_form` x `booking_kind` x `carrier` (8).
12. `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier`: `ast` over `bookings.py` (2 `ClassDef`) and over conftest's fixture classes (5: one base plus four pairs). The docstring states N×M against N+M.
13. `test_an_insured_booking_records_the_declared_value_with_the_carrier` x `carrier` (2): Airco's `insure` record and Fastline's `add_cover` in cents.
14. `test_an_insured_booking_without_a_declared_value_is_a_booking_error[zero|negative]`.

`test_static.py`:
15. `test_mypy_accepts_a_client_whose_shape_matches_the_protocol`: imports `src`; `g: CarrierGateway = AircoClient()`; exit 0, empty.
16. `test_mypy_rejects_a_client_with_a_different_shape`: imports `src`; `{"assignment"}` with `"FastlineClient"` (the executor adjusts to `{"arg-type"}` if the snippet passes it to a function; assert only the code observed).
17. `test_mypy_cannot_see_pounds_passed_as_kilograms_through_a_float`: reduced model (E3); exit 0, empty.
18. `test_mypy_rejects_a_float_where_a_weight_belongs`: imports `src`; a pounds-`float` client typed as `CarrierGateway`; the single code observed, with `"Weight"` in the output.
19. `test_mypy_reports_an_implementor_missing_a_primitive`: imports `src`; a test-local class with `book` only; `{"assignment"}` with `protocol member`.

Numbers are spec ids, not file order. 20 test functions, 33 cases:
- `test_adapter.py` 11 (1: 1; 2: 2; 3: 1; 4: 1; 5: 1; 6: 1; 7: 1; 20: 3);
- `test_facade.py` 4 (8: 2; 9: 1; 10: 1);
- `test_bridge.py` 13 (11: 8; 12: 1; 13: 2; 14: 2);
- `test_static.py` 5.

The executor counts from the pytest summary line and reports that number.

Also `README.md` and the card `_examples/19-adapter-facade-bridge.md` (`order: 19`, eyebrow "Structure · Adapter, Facade, Bridge"). No `mock`, `monkeypatch`, `print(`, `Optional`, `abc`/`ABC`, `Any`, `cast` or `float` in `src/` (weights and money are `Decimal`).

Deletion table (J1a). Each row: the check, how it's deleted, the failing test, and why that test sees the deletion.

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `Weight` finite and positive | `__post_init__` removed | 20[all] | no `ValueError` |
| pounds in `FastlineGateway.book` | `weight.kilograms` sent | 2[object-adapter], 8[FASTLINE] | payload `weight_lb` is the kilogram figure |
| `POUND_IN_KILOGRAMS` exact | rounded to `0.4536` | 4 | `from_pounds(1)` no longer equals the exact factor |
| error translation in `FastlineGateway` | `try`/`except` removed | 10 | `FastlineRejectedError` escapes |
| cents in `insure` | `int(value.amount)` | 13[FASTLINE] | `add_cover` records whole units |
| `UnknownCarrierError` in `ship` | plain index | 6 | `KeyError`, not the domain error |
| `frozendict` registry | `dict` | 7 | assignment succeeds; `isinstance(..., dict)` |
| `InsuredBooking` value check | removed | 14[all] | no `BookingError` |
| `InsuredBooking` calls `insure` | call removed | 13[all], 11[bridge-insured-*] | no cover recorded |
| `Weight` in the Protocol | `kilograms: Decimal` | 18, member mypy | the pounds client type-checks (executor check: the adapter's own signature changes too) |
| `ship` returns `Booking` | returns the SDK receipt for Fastline | 9, member mypy | a hint names an `sdks` type; mypy `[return-value]` |

### `examples/20-decorator-pattern-vs-decorator-syntax-and-proxy` (project `decorator-proxy`, package `decorator_proxy`)

- `domain.py`:
  - `ConsignmentId`.
  - `Weight(kilograms: Decimal)`, positive and finite.
  - `Money(amount, currency)`, frozen slotted: `__add__` refuses another currency with `RatingError`; `scaled(self, factor: Decimal) -> Money` rounds half-up to cents.
  - `Consignment(id, weight, destination, dangerous_goods: bool = False)`, frozen slotted kw_only.
  - `CarrierQuote(carrier, price: Money)`.
  - `RatingError(ValueError)`, `CarrierTimeoutError(Exception)`.
- `layers.py` (the Decorator pattern):
  - `RateCalculator` Protocol, `price(self, consignment: Consignment, /) -> Money`.
  - `BaseRate(per_kg: Money)`, `Discount(inner, percent: Decimal)`, `Surcharge(inner, fee: Money)` and `Tax(inner, percent: Decimal)`: frozen slotted, no base class, each rounding through `Money.scaled`.
  - `type Layer = Callable[[RateCalculator], RateCalculator]`; `discount(percent) -> Layer`, `surcharge(fee) -> Layer`, `tax(percent) -> Layer`.
  - `compose(base, layers: Sequence[Layer]) -> RateCalculator`, last outermost.
  - `HEAVY_FEE`, `DANGEROUS_GOODS_FEE`, `HEAVY_OVER = Weight(Decimal(500))`, `TAX_RATES: Mapping[str, Decimal] = frozendict({"NL": 21, "SG": 9})` by UN/LOCODE country prefix (illustrative).
  - `layers_for(consignment) -> tuple[Layer, ...]`: heavy and dangerous-goods surcharges first, destination tax last. An unknown country is a `RatingError`.
- `syntax.py` (the `@decorator` syntax):
  - `retry[**P, R](*, attempts: int, on: tuple[type[BaseException], ...])`; `attempts < 1` raises `ValueError` at decoration.
  - `audited[**P, R](sink: Callable[[str], None])`. Both use `functools.wraps`.
  - `@retry(attempts=3, on=(CarrierTimeoutError,))` on `quote_carrier(gateway: CarrierGateway, consignment: Consignment) -> CarrierQuote`.
- `proxy.py`:
  - `CarrierGateway` Protocol: `quote(self, consignment: Consignment, /) -> CarrierQuote` and `book(self, consignment: Consignment, /) -> str`.
  - `CarrierGatewayProxy(inner: CarrierGateway)`: `quote` cached in a per-instance `dict[Consignment, CarrierQuote]`, an exception isn't stored, and `book` always forwards.
- `py.typed`, `__init__.py`.

`tests/conftest.py`:
- `heavy`, `light` and `dangerous` consignments.
- `ScriptedGateway`, which counts `quote` and `book` calls and raises `CarrierTimeoutError` for the first *n* quotes.
- `proxy_form` params `explicit|forwarding`, with fixture `_ForwardingGatewayProxy` (`__getattr__(self, name: str) -> Any`, leading-underscore names raise `AttributeError`; it caches `quote` like the explicit form so the table is shared).

`test_layers.py`:
1. `test_a_layer_wraps_a_calculator_and_leaves_it_unchanged`.
2. `test_layer_order_changes_the_price_when_a_fee_is_added[tax-outside|surcharge-outside|discount-outside|surcharge-outside-discount]`: 163.35, 160.20, 121.50, 123.00 EUR for 100 kg at 1.20 (as observed).
3. `test_two_percentage_layers_agree_before_rounding_and_can_split_by_a_cent`: 130.68 both ways at 120.00; 0.06 against 0.05 at 0.05 per kg for 1 kg.
4. `test_the_layers_for_a_consignment_are_chosen_while_the_program_runs[light|heavy|dangerous-goods]`: the layer count and the price, with the base calculator unchanged.
5. `test_layer_stacks_compare_by_value`: equal and equal hashes.
6. `test_compose_wraps_the_last_layer_outermost`: `type(stack) is Tax` and `type(stack.inner) is Surcharge`.
27. `test_a_layer_refuses_a_fee_in_another_currency`.

`test_syntax.py`:
8. `test_the_at_sign_rebinds_the_name_once_at_definition_time`: a test-local counting factory runs once at `def` and not per call; `quote_carrier.__wrapped__` (one `# type: ignore[attr-defined]`) `is not quote_carrier`.
9. `test_retry_calls_again_on_a_listed_error_and_gives_up_after_the_last_attempt`: two timeouts then success gives three calls; three timeouts raise after three calls.
10. `test_retry_lets_an_unlisted_error_through`: one call.
11. `test_audited_reports_each_call_to_the_injected_sink`.
12. `test_syntax_stacking_order_decides_whether_each_attempt_is_audited[audit-outside|retry-outside]`: sink lengths 1 and 3 for two timeouts then success.
13. `test_rebound_functions_do_not_compare_by_value`.
14. `test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped`.
15. `test_a_decorator_may_return_an_object_that_is_not_a_function`: `functools.cache` returns an object with `cache_info`, and `inspect.isfunction` is false.

`test_proxy.py`:
16. `test_the_proxy_asks_the_gateway_once_per_consignment` x `proxy_form` (2).
17. `test_the_proxy_forwards_every_booking` x `proxy_form` (2): two `book` calls reach the gateway.
18. `test_a_timed_out_quote_is_not_cached` x `proxy_form` (2): the first call raises, the second reaches the gateway and is then cached.
19. `test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price`.
20. `test_runtime_checkable_does_not_see_attributes_forwarded_by_getattr`: a test-local `@runtime_checkable` Protocol; the explicit proxy is `True`, the forwarding one `False`.
21. `test_a_forwarded_typo_is_reported_against_the_wrapped_gateway`: `AttributeError` matching `'ScriptedGateway' object has no attribute`.

`test_static.py`:
22. `test_mypy_rejects_a_decorated_function_where_a_calculator_belongs`: imports `src`; `{"assignment"}`, `variable has type "RateCalculator"`.
23. `test_mypy_checks_each_layer_in_a_stack[missing-price|wrong-keyword]`: `{"assignment"}`; `{"call-arg"}` with `did you mean "fee"?` (imports `src`).
24. `test_mypy_keeps_the_call_signature_through_retry[arg-type|call-arg]`: imports `src`; a wrong argument type; an unknown keyword.
25. `test_mypy_reports_a_member_missing_from_an_explicit_proxy`: a reduced copy of the proxy without `book`; `{"assignment"}`, `protocol member`.
26. `test_mypy_accepts_a_typo_through_a_forwarding_proxy[any-typo|any-wrong-type]`: reduced model (evidence B); exit 0, empty.
28. `test_mypy_rejects_a_forwarding_proxy_that_returns_object`: reduced model (evidence A); `{"assignment"}`, `got "object"`.

Spec ids 7 and 27 are reused across files only where listed; the executor renumbers freely. 27 test functions, 40 cases:
- `test_layers.py` 12 (1: 1; 2: 4; 3: 1; 4: 3; 5: 1; 6: 1; 27: 1);
- `test_syntax.py` 9 (8-11: 4; 12: 2; 13-15: 3);
- `test_proxy.py` 9 (16-18: 6; 19-21: 3);
- `test_static.py` 10 (22: 1; 23: 2; 24: 2; 25: 1; 26: 2; 28: 1).

The executor counts from the pytest summary line.

J1b also writes `_plans/evidence/percentage-layer-rounding.md`: the evidence-G sweep re-run against the member's real `Discount`, `Tax` and `Money.scaled` (count, range and first example), scrubbed, with Python and mypy versions.

Also `README.md` and the card (`order: 20`, eyebrow "Structure · Decorator and Proxy"). No `mock`, `monkeypatch`, `print(`, `Optional`, `__getattr__`, `Any`, `cast`, `partial` or `sleep` in `src/`.

Deletion table (J1b):

| Check | Deleted as | Failing test | Why it sees the deletion |
| --- | --- | --- | --- |
| `Money.__add__` currency check | removed | 27 | no `RatingError` |
| rounding in `Money.scaled` | unquantised | 3, 2 (executor check) | the cent split disappears; prices gain digits |
| `layers_for` order (surcharges before tax) | reversed | 4[heavy], 4[dangerous-goods] | the price changes (experiment a) |
| heavy threshold | `>=` against `>` or removed | 4[light] or 4[heavy] (executor names which) | layer count changes |
| unknown country in `layers_for` | `TAX_RATES.get(..., 0)` | executor adds `test_an_unknown_destination_country_is_a_rating_error` | no error |
| `compose` order | `reversed(layers)` | 6, 4 | the outermost type changes |
| `retry` re-raises after the last attempt | returns `None` | 9, member mypy | no exception; mypy `[return-value]` |
| `retry` catches only `on` | `except Exception` | 10 | the unlisted error is retried |
| `attempts < 1` refused | removed | executor adds `test_retry_refuses_fewer_than_one_attempt` | no `ValueError` |
| `audited` calls the sink | removed | 11, 12 | the sink is empty |
| proxy cache | always forwards | 16[explicit] | two gateway calls |
| proxy doesn't cache failures | exception stored | 18[explicit] | the second call re-raises without asking |
| proxy `book` forwards | cached like `quote` | 17[explicit] | one gateway booking |
| proxy defines `book` | deleted | 17[explicit], member mypy | `AttributeError`; missing protocol member (experiment b) |

## Steps and status

Step ids are `J*` (see User decisions).

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| J0 | This plan file. PDP-119a-c and 120a-c `active` in `iteration-plan.md` (dated note). Reconciliation rows 97-106 `open`; row 5 notes "witnessed by rows 101-103 (r09)"; row 6 moves to ch26 (decision 5). Domain rows 19-20 updated (decisions 1-5 and the supporting names), with the ch20/ch26 non-overlap sentence extended to the syntax stacking-order witness. ch19-20 stub `description` lines written. Decisions recorded | - | todo |
| J1a | ch19 member, card, README; one `uv lock`; three green runs; the deletion table, each row in a fresh scratch copy with its `.venv` removed and re-synced (confirm `__file__`) | J0 | todo |
| J1b | ch20 member, card, README; one `uv lock` after J1a (sequenced); three green runs; deletion table; `_plans/evidence/percentage-layer-rounding.md` | J1a | todo |
| J2 | Witness results into rows 97-106 (the claims audit resolves). A failed witness changes the thesis before prose. Any message differing from Planning evidence goes in "Corrections after the build". The dated spikes.md note on percentage layers | J1b | todo |
| J3 | Two figures, specs `diagrams/specs/19-*.py` and `20-*.py`, `_data/diagrams.yml` (single owner; `section: "Ch. 19"` and `"Ch. 20"`); figures 00-18 unchanged | J2 | todo |
| J4 | ch19-20 `status = "drafted"` (`kind` stays `pattern`) | J3 | todo |
| J5 | Two prose agents in parallel. Each re-fetches its sources and quotes exactly, runs its two experiments in scratch copies, quotes fresh output filtered by `python3 scripts/host_ids.py filter`, and hands back the sources checked plus a per-paragraph claims table (claim, then test, run or source URL) | J3, J4 | todo |
| J6 | Opus validation; up to two repair rounds | J5 | todo |
| J7 | PR, `ci-ok` green, ask the user before merge; tag r09.x; notes-only release | J6 | todo |

Reconciliation rows (step J0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 97 | 19 | A client whose shape matches the Protocol needs no adapter; a different shape is a mypy error; an object adapter and a class adapter pass the same table, and the class adapter leaks the client's methods | `test_a_client_whose_shape_matches_needs_no_adapter`, `test_mypy_accepts_a_client_whose_shape_matches_the_protocol`, `test_mypy_rejects_a_client_with_a_different_shape`, `test_the_fastline_adapter_translates_the_booking_call`, `test_a_class_adapter_still_exposes_the_clients_own_methods` |
| 98 | 19 | Units hidden in a `float` pass mypy and book the wrong weight; a `Weight` parameter is checked; the pound converts exactly; the adapter translates SDK errors | `test_mypy_cannot_see_pounds_passed_as_kilograms_through_a_float`, `test_mypy_rejects_a_float_where_a_weight_belongs`, `test_a_pounds_api_called_with_kilograms_books_the_wrong_weight`, `test_weight_converts_between_kilograms_and_pounds_exactly`, `test_a_carrier_rejection_becomes_a_carrier_error`, `test_a_consignment_weight_must_be_positive_and_finite` |
| 99 | 19 | One facade call books each carrier, refuses an unknown code, keeps a read-only registry and names no SDK type | `test_ship_books_each_carrier_through_one_call`, `test_an_unknown_carrier_is_refused_at_the_desk`, `test_the_desk_registry_is_read_only`, `test_the_desk_names_no_sdk_type_in_its_public_surface` |
| 100 | 19 | Booking kinds and gateways vary independently: both designs pass the table, the class-per-pair design needs N×M classes against N+M, insurance goes through the implementor, and a missing primitive is a mypy error | `test_every_booking_kind_works_with_every_carrier`, `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier`, `test_an_insured_booking_records_the_declared_value_with_the_carrier`, `test_an_insured_booking_without_a_declared_value_is_a_booking_error`, `test_mypy_reports_an_implementor_missing_a_primitive` |
| 101 | 20 | Layers wrap without mutating; an additive fee makes order matter; two percentages agree before rounding and can split by a cent after it; `compose` puts the last layer outermost; currencies don't mix | `test_a_layer_wraps_a_calculator_and_leaves_it_unchanged`, `test_layer_order_changes_the_price_when_a_fee_is_added`, `test_two_percentage_layers_agree_before_rounding_and_can_split_by_a_cent`, `test_compose_wraps_the_last_layer_outermost`, `test_a_layer_refuses_a_fee_in_another_currency`, `run: _plans/evidence/percentage-layer-rounding.md` |
| 102 | 20 | The stack is data: layers are chosen per consignment while the program runs and compare by value; rebound functions don't; mypy checks each layer and refuses an `@`-decorated function as a calculator | `test_the_layers_for_a_consignment_are_chosen_while_the_program_runs`, `test_layer_stacks_compare_by_value`, `test_rebound_functions_do_not_compare_by_value`, `test_mypy_checks_each_layer_in_a_stack`, `test_mypy_rejects_a_decorated_function_where_a_calculator_belongs` |
| 103 | 20 | `@` rebinds a name once at definition time (PEP 318); `retry` and `audited` behave as stated; syntax stacking order is fixed at definition; `ParamSpec` keeps the signature for mypy; neither mechanism has the other's attributes; a `@` factory may return an object | `test_the_at_sign_rebinds_the_name_once_at_definition_time`, `test_retry_calls_again_on_a_listed_error_and_gives_up_after_the_last_attempt`, `test_retry_lets_an_unlisted_error_through`, `test_audited_reports_each_call_to_the_injected_sink`, `test_syntax_stacking_order_decides_whether_each_attempt_is_audited`, `test_mypy_keeps_the_call_signature_through_retry`, `test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped`, `test_a_decorator_may_return_an_object_that_is_not_a_function`, `source: https://peps.python.org/pep-0318/` |
| 104 | 20 | A caching proxy asks once per consignment, forwards bookings, doesn't cache timeouts and returns what the gateway returns; mypy reports a member missing from an explicit proxy | `test_the_proxy_asks_the_gateway_once_per_consignment`, `test_the_proxy_forwards_every_booking`, `test_a_timed_out_quote_is_not_cached`, `test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price`, `test_mypy_reports_a_member_missing_from_an_explicit_proxy` |
| 105 | 20 | A `__getattr__` forwarding proxy passes the same table but mypy accepts typos through `Any`, an `object` return fails the Protocol, `runtime_checkable` doesn't see forwarded members, and a typo names the wrapped class | `test_mypy_accepts_a_typo_through_a_forwarding_proxy`, `test_mypy_rejects_a_forwarding_proxy_that_returns_object`, `test_runtime_checkable_does_not_see_attributes_forwarded_by_getattr`, `test_a_forwarded_typo_is_reported_against_the_wrapped_gateway`, `source: https://docs.python.org/3/library/typing.html`, `source: https://docs.python.org/3/reference/datamodel.html` |
| 106 | 19-20 | The "Build, run, observe" experiments behave as quoted | `run: J5` |

Row 5 status note at J2: "witnessed by rows 101-103 (r09)". Row 6: Ch cell 26, "moved from ch20 (r09 decision 5)", stays `open`.

## Corrections after the build

(Empty. The orchestrator records here every message, count or value that differs from Planning evidence or this spec, with the step that found it.)

## Acceptance criteria

1. `bash scripts/verify.sh` prints `verify: all steps passed`. `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member: `uv run pytest` and `uv run mypy --strict src tests` exit 0 on three consecutive runs.
   - `grep -rnE "time\.sleep|perf_counter|time\.time\(|datetime\.now|mock|monkeypatch|print\("` over both members prints nothing.
   - `grep -rnE "^\s*(from abc|import abc)|\bABC\b|\bAny\b|cast\(|\bfloat\b" examples/19-*/src` prints nothing.
   - `grep -rnE "__getattr__|\bAny\b|cast\(|partial" examples/20-*/src` prints nothing.
3. Every test name cited in rows 97-106 is defined exactly once across `examples/*/tests` (`grep -rhoE "def test_\w+" examples/*/tests | sort | uniq -d` lists none of them).
4. Every mypy-API test asserts exit status and an exact code set (`grep -c "_codes("` at least 4 in each `test_static.py`), uses the anchored `_codes` regex, and asserts no line number or optional note. Every `# type: ignore[...]` names a code.
5. Deletion tables (J1a, J1b): every row, deleted in a fresh scratch copy whose imports are confirmed to come from the copy, makes the named test fail for the stated reason. The handback quotes the failing line. No row reads "nothing failed"; executor-check rows are resolved or moved to Corrections with the orchestrator's agreement.
6. ch19-20 drafted, one figure each, captions 20-45 words including `Figure N.1:`, 1,900-2,500 prose words each (validate.py).
7. `grep -c '<blockquote class="ai-sidebar"'` is 1 in each, and `{: .ai-sidebar}` appears nowhere. `grep -c "^## When not to use it"` is 1 in each, and `grep -c "^## How it works"` is 0. `validate.py` passes the `pattern` spine.
8. Thesis:
   - ch19 says all three patterns survive (`surviv` at least 1) and that duck typing removes an adapter only when shapes match.
   - ch20 says both names need disambiguating (`disambiguat` at least 1). In prose, every bare "Decorator" or "decorator" refers to the pattern, and the syntax is always "`@decorator` syntax", "the `@` form" or a named function. The prose agent lists every occurrence in its handback, and the validator reads each.
9. Non-overlap:
   - ch19 doesn't re-teach the composition root, positional-only Protocols or factory registries, and points to "What 1994 assumed, and what Python dissolves", "ISP, DIP, and dependency injection without a framework" and "Protocol, duck typing, and structural typing with mypy" by title.
   - ch20 excerpts no code from the three-way-split member, doesn't teach `wraps`/`ParamSpec` beyond one sentence each, teaches no `__getattr__` mechanics beyond the fixture's measured costs, and points to "The three-way split: dissolve, survive, disambiguate", "Decorators done right", "Dynamic attributes: __getattr__ and Proxy as a feature", "Descriptors and properties" and "Singleton: module, Borg, and metaclass" by title.
   - Neither chapter re-teaches the evidence method, which is pointed to "Proving it works: pytest, pytest-mock, and mypy".
10. Voice:
    - `scan.sh --tier ban --fail` exits 0 over both chapters, READMEs, cards and SVGs, with `--stats` reviewed against the house-voice rubric.
    - Contractions are used: uncontracted `does not|do not|is not|are not|did not|cannot` at most 3 per chapter outside code, output and exact quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ)"` over prose (the front matter `part:` slug, quotations and code excluded) prints nothing.
11. `grep -c $'-'` is 0 over every file touched in r09, including this plan.
12. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|Smalltalk|capstone|PDP-|\br0[0-9]\b|spike|[Cc]hapter [0-9]|magic method"` over `_docs/19-*.md`, `_docs/20-*.md`, the new READMEs and cards prints nothing.
13. Idiomatic scan: 0 ban-tier in both members.
14. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs piped through `host_ids.py filter`, never hand-edited.
15. Every excerpt matches its source byte for byte. Every quoted pytest or mypy output comes from a fresh run, apart from scrubbing and duration. Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`, and `ruff format --check .` is clean. Excerpts containing `{{` are wrapped in `{% raw %}`.
16. Each experiment is performed in a fresh scratch copy (its `.venv` removed and re-synced, `__file__` confirmed) and changes one thing. The run uses exactly `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests`, three times. The prose quotes the observed result, and the handback includes the raw filtered output and states where it differs from the prediction.
17. Attribution (credit every source a chapter leans on, by author and work, where the idea is used; nothing copied; a missing credit is blocking):
    - ch19 credits GoF (Adapter, Facade, Bridge) in plain paraphrase and Rhodes's "The Composition Over Inheritance Principle".
    - ch20 credits GoF (Decorator, Proxy) and Rhodes's "The Decorator Pattern", and quotes PEP 318, the functools `wraps` entry, the data-model `__getattr__` entry and the typing `runtime_checkable` note exactly; it credits PEP 3129.
    - GoF claims appear only if verified, with the bracketed fallbacks applied, and no GoF sentence tracks the Intent wording. Each prose agent lists the sources it checked. Every book cited is already in `bibliography.html`; anything else is flagged to the owner, not added.
18. Claims:
    - Every factual sentence in ch19-20 maps to a named test, a recorded run (`run: J5` or a file under `_plans/evidence/`) or a fetched source URL linked in that chapter, in the prose agent's claims table.
    - `validate.py`, `--self-test` and `--claims` exit 0. The claims table lists rows 1-106, with 97-106 resolved, and each `source:` URL appears in its chapter.
    - No `run: G*`, `H*` or `I*` token appears in rows 97-106.
19. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 21 entries, and `diagrams/0*-*` and `diagrams/1[0-8]-*` are unchanged.
20. Reconciliation rows 97-106 are `verified` or `adjusted` with evidence; row 5 carries the r09 note; row 6 is reassigned to ch26.
21. Deterministic: no test depends on wall time, the environment, memory addresses, test order or iteration order it didn't create. Retries are driven by a scripted fake, not by timing. `filterwarnings = ["error"]` is still in the root config. Every fixture builds fresh SDK stand-ins and proxies per test.
22. CI `ci-ok` is green on the PR. Merge happens only after the user's explicit approval.
23. Every self-contained mypy snippet that stands for code (ch19 test 17; ch20 tests 25, 26, 28) is either checked against its source by an `ast` test or named in the prose as a reduced model. Snippets that import `src` need neither.
24. Test counts in prose and handbacks come from the pytest summary line of a fresh run, never from this plan's arithmetic.
25. Every comparison form said to share a table is a conftest fixture param (`gateway_form`, `booking_form`, `proxy_form`), and each chapter shows at most one comparison excerpt.

## Risks

- **Predicted messages.** r05 to r08 each mispredicted something. Evidence E2 already showed a note missing where a similar case printed one. Expect the `[assignment]` against `[arg-type]` choice in ch19 tests 16 and 18 to depend on how the snippet uses the client, the quantised pound value in test 2, and the ch20 experiment (b) code to differ. Tests match codes and stable substrings only; differences go in Corrections.
- **mypy findings can age.** `__getattr__ -> Any` silence, the `[untyped-decorator]` code and the `ParamSpec` reveal are mypy 2.4.1 behaviour. The `getattr_static` result is runtime behaviour since 3.12. The prose says "mypy 2.4.1 reports", and the tests pin it.
- **The headline disambiguation is easy to blur in prose.** ch20 discusses three wrapper-shaped things (layer, `@` wrapper, proxy). Criterion 8's occurrence list is the guard, and the naming chapter's rule is applied word by word.
- **ch20 word budget.** Three halves within 2,500 words. If it overruns, the overlap paragraph and the `ParamSpec` sentence shrink first; their tests stay.
- **ch26 overlap.** The syntax stacking-order witness touches ch26's "stacking order" ground. ch20 keeps it to the audit/retry pair and one paragraph; ch26 owns caches and renderers. Domain row 20's non-overlap sentence is extended at J0.
- **The percentage-layer refinement** contradicts a CLAUDE.md sentence read literally. The chapter states both halves (commute exactly, split after rounding) with the evidence file, and the owner decides whether CLAUDE.md changes.
- **Bridge may read as dependency injection again.** The section leads with the two-axis count and the implementor-widening cost, and gives the mechanism one sentence plus a pointer.
- **SDK stand-ins look like invented domain.** They stay inside the Carrier area ("carrier SDK types are small stand-in classes with deliberately different shapes", domain row Carrier), and use only `FASTLINE` and `AIRCO`.
- **`get_type_hints` on deferred annotations** (3.15) in ch19 test 9: the executor confirms that it resolves the `desk` module's names under `--import-mode=importlib`, and otherwise reads `inspect.get_annotations(ship, eval_str=True)`.
- **ruff.** N818 holds (`CarrierError`, `BookingError`, `RatingError`, `CarrierTimeoutError`, `FastlineRejectedError`, `UnknownCarrierError`). B-rules may flag a `lambda` assigned in a layer constructor; the constructors return the lambda directly.
- **Liquid.** f-strings with `{{` in excerpts need `{% raw %}`; validate.py checks.
- **`uv.lock` race.** J1a and J1b are sequenced, and project names normalise to the package names.
- **r08 bookkeeping.** r08-plan's I6 and I7 still read `todo`. That's harmless to r09's tokens, but the orchestrator should close them before J7 so the status board is truthful.
