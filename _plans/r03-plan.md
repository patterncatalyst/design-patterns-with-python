---
title: "r03 plan: chapters 5-6 (Part 3, SOLID)"
order: 3
output: false
render_with_liquid: false
---

# r03: chapters 5-6

Opus-planned 2026-11-03. Branch `release/r03`. Source of truth for r03 scope, criteria and
status. Executors never edit this file; the orchestrator updates the status board.

Planning evidence (read-only `mypy 2.4.1 --strict --cache-dir /dev/null -c`, Python 3.14.10):

- `Weight` rejects `<= 0`, so the domain model's old ch5 demo ("a subclass that raises on zero
  `Weight`") cannot be built; replaced below.
- An override narrowing the argument type prints `note: This violates the Liskov substitution
  principle`; a widened return or an extra required parameter gives `[override]` without the note.
- mypy accepts an override that widens the argument (`Consignment | None`): the static form of
  "a weaker precondition is allowed".
- mypy checks the argument bound into a `functools.partial` and calls through it, but not the
  partial's assignment to a mismatched `Callable[...]` annotation (exit 0): a mypy limitation.
- `create_autospec(TrackingGateway, instance=True)` passed where a `BookingGateway` is expected:
  mypy exit 0; at runtime `.book` raises `AttributeError: Mock object has no attribute 'book'`,
  `.track()` raises `TypeError: missing a required argument: 'consignment_id'`.
- The reconciliation plan has no claims for chapters 5-6; rows 29-36 are added.
- `validate.py` requires `Learning objectives`, `Why this matters`, `Build, run, observe`, `For
  deeper coverage` for `kind = "hands-on"` and checks the ai-sidebar only for `kind == "pattern"`.
  The stubs' `## How it works` heading is a placeholder and is replaced.

## User decisions (2026-11-03)

1. **ai-sidebar: one per chapter** (user chose series parity over the recommendation). Exactly
   one `<blockquote class="ai-sidebar" markdown="1">` ... `</blockquote>` per chapter, placed in
   `## When the principle costs more than it buys`, framed as review practice: what to check when
   an assistant proposes a split, an extension point or a Protocol (ch5: an interface per class,
   a subclass that narrows the contract; ch6: a DI container or a fat gateway Protocol for one
   consumer). No empirical claims about LLM behaviour ("may", review checklist wording).
2. **LSP violators as negative fixtures in `tests/`: accepted.**
3. **Bibliography: add Meyer.** Add *Object-Oriented Software Construction*, Bertrand Meyer,
   2nd ed. (Prentice Hall, 1997, ISBN 9780136291558) as a row in `bibliography.html`, matching the
   existing rows' markup, topic "Open-closed principle, Design by Contract". Prose says the
   principle first appeared in the 1988 first edition. Papers and articles (Liskov 1987/1988,
   Liskov and Wing 1994, Fowler 2004, Seemann 2011) stay inline in "For deeper coverage". The ch5
   prose agent owns the `bibliography.html` edit.

## Approach

- **Principles are not catalogue patterns: no three-way bucket.** Every principle's force stands;
  the chapters say where a Python feature changes the mechanism used to honour it (a `Protocol`
  instead of an interface hierarchy; a callable or mapping of callables as the extension point;
  `functools.partial` and constructor arguments instead of a container; a plain function as the
  composition root). Wording: "the force remains; a feature resolves it without the structure".
  Never "SRP dissolves". Domain-model rows for ch5/ch6 change bucket to `n.a. (principle)`.
- **No contrast code.** The overloaded calculator (pricing, destination tax and audit in one
  `price`) is described in prose. Code shows only the split design; witnesses prove each
  responsibility changes only its own output, an extension arrives as data, and one contract
  suite catches substitution failures.
- **LSP violators are negative test fixtures** in `tests/test_lsp.py`, never reader model code;
  the prose says so in one sentence.
- **One uv member per chapter:** `examples/05-srp-ocp-lsp` (package `srp_ocp_lsp`) and
  `examples/06-isp-dip-and-di-without-a-framework` (package `isp_dip_di`), standalone, each
  re-declaring small `Money`, `Weight`, `Consignment`, `ConsignmentId` in the ch3 shapes.
- **Static vs behavioural LSP**, r02's mypy-API witness pattern:
  `mypy.api.run(["--strict","--cache-dir",os.devnull,"--no-error-summary","-c",SNIPPET])`;
  assert exit status and the exact code set (`set(re.findall(r"\[([a-z-]+)\]", stdout))`) plus
  one or two key substrings.
- **One ai-sidebar per chapter and no `## When not to use it`** (decision 1); each chapter has
  `## When the principle costs more than it buys`, which holds the sidebar.
- **No global-state mutation:** module tables are `types.MappingProxyType`; substitutes arrive as
  arguments; no `monkeypatch`, no `mock.patch`.

Rejected: one shared member (breaks one member per chapter); the overloaded `RateCalculator` as
code (contrast code); OCP via `Surcharge` wrappers (Decorator, owned by its chapter); OCP via
`__init_subclass__` (registries chapter owns it); violators only in snippet strings (behavioural
violations must run); a DI container library (title says without a framework); closure and
partial as equal mechanisms (partial leads, closure one sentence); bucket labels on SOLID.

## Per-chapter spec

### Chapter 5: SRP, OCP, and LSP in Python (hands-on, has_example = true)

Thesis: the three principles still name real forces in a rate quote. Pricing, tax and audit change
for different reasons on different schedules; new tax rules arrive without reopening the quoting
code; any calculator handed to the quote must keep the caller's contract. Python changes the
mechanism (one coordinating function over three collaborators; a mapping of callables as the
extension point; a `Protocol` mypy checks plus a contract suite for what no type expresses).

Sections (spine headings exact; about 2,200 prose words):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200): tariff schedules, tax law and audit rules change on different
   calendars; a quote that mixes them is retested for every change.
3. Figure include plus one paragraph reading it (~60).
4. `## Three reasons to change in one rate calculation` (~250): prose only. One `price` that looks
   up the tariff, applies destination tax and appends to an audit log; who asks for each change
   (carrier contract or tariff; destination tax rule; audit requirement). SRP with attribution.
5. `## Single responsibility: three collaborators and a coordinator` (~350): excerpts
   `RateCalculator` Protocol with its contract docstring, `type TaxRule`, `type AuditSink`,
   `quote`; what `test_each_change_moves_only_its_own_field` shows.
6. `## Open for extension: a new tax rule is data` (~300): excerpts `percent`, `TAX_RULES`.
   Meyer's original framing rested on inheritance; Martin restated it on abstraction. In Python
   the extension point is often a callable in a mapping passed in; the default table is
   read-only; a missing rule is a `RatingError`, not silent zero tax; the principle protects
   against a change you have seen, not every change imaginable.
7. `## Liskov substitution: the contract the type does not state` (~450): Liskov 1987 keynote;
   Liskov and Wing 1994 behavioural definition. Static half: fresh mypy output for the
   narrowed-argument snippet (with the LSP note), the widened-return `[override]`,
   `typing.override` catching a misspelling (`[misc]`), a widened argument accepted; on a
   Protocol the check moves to the place of use (`[arg-type]`). Behavioural half: the contract
   suite and two violators: rejecting a zone the base accepts strengthens a precondition; pricing
   in USD weakens a postcondition; both pass mypy, both fail the contract.
8. `## Where Python changes how the principles apply` (~200): structural typing means a
   substitutable implementation need not inherit, but must honour the contract; the narrowest
   abstraction is a callable; the principles stand, the scaffolding is not needed.
9. `## When the principle costs more than it buys` (~180): one tax rule that never varies needs no
   mapping; splitting before a second reason to change adds indirection; a contract suite pays off
   once two implementations exist.
10. `## Build, run, observe` (~250 plus output): commands as in the three-way split chapter; fresh
    `uv run pytest -v` and `uv run mypy --strict src tests` output filtered with
    `python3 scripts/host_ids.py filter` inside the repo (path reads `<repo>`). Two experiments,
    performed in a scratch copy and described exactly as observed:
    (a) make `FlatRate.price` return `"USD"`: expected
    `test_calculator_honours_the_rate_contract[FlatRate]` fails with the currency message while
    mypy reports success; revert.
    (b) widen `FlatRate.price`'s parameter to `Consignment | None`, raising `RatingError` on
    `None`: expected mypy and pytest stay green (weaker precondition allowed). Record the real
    result; if it differs, the claim is wrong: record and adjust before drafting.
11. `## For deeper coverage` (~150).

Figure `05-srp-ocp-lsp` (vertical): top accent box `quote(consignment, calculator, tax_rules,
audit)`; three boxes under it: "`RateCalculator`: `BaseRate`, `FlatRate`" / "pricing: changes with
the tariff"; "`TAX_RULES`: `percent(...)` by destination country" / "tax: changes with tax law";
"`AuditSink`: `records.append`" / "audit: changes with compliance"; arrows converge on
`RateQuote(net, tax)`; side box off `RateCalculator`: "rate contract suite: every calculator".
Caption draft (39 words): "One quote, three responsibilities. Pricing sits behind the
RateCalculator Protocol, tax rules are callables keyed by destination country, and the audit sink
is a callable, so each changes for its own reason while one contract suite checks every
calculator."

Citations (verify each before writing; bracketed fallback if not verifiable):
- SRP: Martin, *Agile Software Development: Principles, Patterns, and Practices* (Prentice Hall,
  2002), "a class should have only one reason to change". Martin's credit to DeMarco and
  Page-Jones cohesion work only if verified [else omit]; the *Clean Architecture* (2017) "one
  actor" restatement only if verified [else omit].
- OCP: Meyer, *Object-Oriented Software Construction* (Prentice Hall, 1988) names the principle;
  Martin (2002) restates it on abstraction. Do not attribute "open for extension, closed for
  modification" verbatim to Meyer unless verified [else "Meyer introduced the principle; Martin's
  formulation..."].
- LSP: Liskov, "Data Abstraction and Hierarchy", OOPSLA '87 keynote, *SIGPLAN Notices* 23(5),
  1988; Liskov and Wing, "A Behavioral Notion of Subtyping", *ACM TOPLAS* 16(6), 1994. The name
  as one of the five comes from Martin. Pre/postcondition rule credited to Meyer's Design by
  Contract only if verified [else unattributed].
- Do not name who coined SOLID.
- PEP 544, PEP 698, the typing spec's Protocols chapter, mypy docs "Incompatible overrides";
  Lott & Phillips 5th ed by topic; `{{ '/bibliography/' | relative_url }}`.

ai-sidebar: one, inside `## When the principle costs more than it buys` (decision 1).

### Chapter 6: ISP, DIP, and dependency injection without a framework (hands-on, has_example = true)

Thesis: a consumer depends on the smallest Protocol it uses; high-level policy names that
abstraction, not a carrier adapter. In Python both cost almost nothing: the consumer declares and
owns a small `Protocol`; adapters satisfy it structurally without importing it; collaborators
arrive as dataclass fields or `functools.partial` arguments; one plain function, the composition
root, is the only place that names a concrete adapter. No container until wiring itself is the
problem.

Sections (about 2,200 prose words):
1. `## Learning objectives` (~90).
2. `## Why this matters` (~200): a booking test that needs a live carrier cannot run in CI; a fake
   implementing methods its consumer never calls is maintenance with no benefit.
3. Figure plus one paragraph (~60).
4. `## A gateway with three methods and consumers that use one` (~250): prose and the composite
   `CarrierGateway` excerpt; booking uses `book` and `cancel`, tracking uses `track`; ISP with
   attribution.
5. `## Segregation with Protocols the consumer owns` (~350): excerpts `BookingGateway`,
   `TrackingGateway`, `CarrierGateway(BookingGateway, TrackingGateway, Protocol)`;
   `FastlineGateway` has no base class; fresh mypy output for a track-only fake passed where
   `CarrierGateway` is required (`[arg-type]`, "missing following ... protocol members: book,
   cancel"); splitting a Protocol costs implementers nothing.
6. `## Dependency inversion: the policy names the abstraction` (~350): excerpt `BookingService`
   (frozen dataclass; `gateway: BookingGateway`, `audit: AuditSink`); DIP's two clauses with
   attribution; the abstraction lives with the policy; the adapter module imports neither policy
   nor Protocols; the import-direction witnesses show it.
7. `## Injection without a container` (~350): constructor injection is a dataclass field; function
   injection is `partial(tracking_history, gateway=...)`; one closure sentence; the mypy caveat
   (mypy 2.4.1 checks the bound `gateway=` argument and calls through the partial, not its
   assignment to a `Callable` annotation; a closure's signature is fully checked); "dependency
   injection" is Fowler, 2004.
8. `## The composition root` (~250): excerpt `build_app`, the only module importing `carriers`; an
   unknown carrier fails at start-up; tests pass a substitute `gateways=` mapping; "composition
   root" credited to Seemann if verified [else uncredited].
9. `## Fakes, autospec, and what mypy checks` (~250): hand-written fakes are typed and checked
   structurally, ISP keeps them small; `mocker.create_autospec` when the test asserts interactions;
   a mock is `Any` to mypy: an autospec of the wrong Protocol passes the type check and fails only
   at runtime. Point to "Proving it works: pytest, pytest-mock, and mypy" by title.
10. `## When the principle costs more than it buys` (~180): a Protocol with one implementation and
    no double adds a name, not a seam; don't inject the standard library; when wiring dozens of
    services with lifetimes is the problem, a container library is a reasonable tool (neutral).
11. `## Build, run, observe` (~200 plus output). Two experiments performed and described exactly:
    (a) add `from isp_dip_di.carriers import FastlineGateway` to `src/isp_dip_di/booking.py`:
    expected `test_policy_modules_do_not_import_the_adapters` fails naming the module (report ruff
    F401 if run); revert. (b) delete `cancel` from `FakeBooker` in `tests/test_dip.py`: record what
    mypy reports (expected `[arg-type]` naming `cancel`) and whether any pytest test fails; revert.
12. `## For deeper coverage` (~150).

Figure `06-isp-dip-and-di-without-a-framework` (vertical): top accent `build_app(carrier)` /
"composition root"; below `FastlineGateway` / `AircoGateway` ("no base class"), built by the root;
two consumers injected by the root: `BookingService(gateway, audit)` and
`partial(tracking_history, gateway=...)`; under each the Protocol it owns: `BookingGateway: book,
cancel` and `TrackingGateway: track`; dashed arrows adapter to both Protocols, "satisfies
structurally, imports neither". Caption draft (35 words): "Dependency injection without a
framework. The composition root builds one carrier adapter and passes it to each consumer, which
names only the small Protocol it needs; the adapter satisfies both Protocols structurally and
imports neither."

Citations: Martin (2002) for ISP and DIP (client-owned interface wording only if verified);
Fowler, "Inversion of Control Containers and the Dependency Injection pattern" (martinfowler.com,
January 2004); Seemann, "Composition Root" (blog.ploeh.dk, 2011) if the URL verifies, else omit;
Percival & Gregory, *Architecture Patterns with Python* by topic; PEP 544, `functools.partial`
docs, `unittest.mock` autospeccing docs; bibliography link. No platform-specific titles, no
cross-language comparison.

ai-sidebar: one, inside `## When the principle costs more than it buys` (decision 1).

## Example spec

### `examples/05-srp-ocp-lsp` (project `srp-ocp-lsp`, package `srp_ocp_lsp`)

`pyproject.toml` in the ch3 shape, no `[tool.*]` tables; the project name must normalise to the
package name.

- `domain.py`: `ConsignmentId = NewType(...)`; `Weight` (frozen slotted, finite, positive);
  `Money(amount: Decimal, currency: str)` (frozen slotted; `__add__` same currency only, else
  `ValueError`); `Consignment(id, weight, zone, destination)` (frozen slotted kw_only; destination a
  UN/LOCODE such as `"SGSIN"`); `RateQuote(consignment_id, net: Money, tax: Money)` with `total`;
  `RatingError(Exception)`; `Tariff(per_kg_by_zone: Mapping[str, Money])` with `rate_for(zone)`
  raising `RatingError` for an unknown zone.
- `pricing.py`: `class RateCalculator(Protocol): def price(self, consignment: Consignment, /) ->
  Money`, docstring stating the contract (accepts every consignment whose zone is in `ZONES`;
  returns `Money` in the tariff currency, non-negative, quantised to cents; heavier in the same
  zone is never cheaper; unknown zone raises `RatingError`). `ZONES = ("EU", "ASIA",
  "AMERICAS")`, `TARIFF`, `BaseRate(tariff)` (per kg by zone, `ROUND_HALF_UP` to cents),
  `FlatRate(by_zone: Mapping[str, Money])`, default `FLAT_BY_ZONE`. All EUR.
- `tax.py`: `type TaxRule = Callable[[Money], Money]`; `percent(rate: Decimal) -> TaxRule`
  (closure); `TAX_RULES: Mapping[str, TaxRule] = MappingProxyType({"SG": percent(Decimal("9")),
  "NL": percent(Decimal("21"))})`. Illustrative rates; prose never presents them as statutory.
- `audit.py`: `type AuditSink = Callable[[RateQuote], None]`.
- `rating.py`: `quote(consignment, *, calculator: RateCalculator, tax_rules: Mapping[str,
  TaxRule], audit: AuditSink) -> RateQuote`: tax rule by `consignment.destination[:2]`,
  `RatingError` naming the country if missing, build the quote, `audit(quote)` once, return it.
- `py.typed`, `__init__.py`.

`tests/conftest.py`: an `"EU"`/`"NLRTM"` and an `"ASIA"`/`"SGSIN"` consignment; a
`records: list[RateQuote]` sink.

`test_srp.py`:
1. `test_each_change_moves_only_its_own_field[tariff|tax-rule|audit-sink]`: baseline quote, then
   replace one collaborator (a different `Tariff`; a different `"SG"` rule; a different sink);
   changed `dataclasses.fields(RateQuote)` set is exactly `{"net"}`, `{"tax"}`, `set()`; in the
   sink case the new sink got the quote and the old did not.
2. `test_audit_receives_exactly_the_quote_returned`: `records == [q]`, `records[0] is q`.
3. `test_pricing_and_tax_run_alone`: `BaseRate(TARIFF).price(c)` and
   `percent(Decimal("9"))(Money(...))` give exact amounts with no sink or rules built.

`test_ocp.py`:
4. `test_a_new_tax_rule_is_added_without_editing_quote`: test-module `exempt` rule passed as
   `{**TAX_RULES, "HK": exempt}`; an `"HKHKG"` quote has tax `0.00`; `"HK" not in TAX_RULES` after.
5. `test_default_tax_table_is_read_only`: `TAX_RULES["HK"] = ...` raises `TypeError`.
6. `test_missing_tax_rule_is_a_rating_error`: `"USNYC"` raises `RatingError` matching `"US"`.

`test_lsp.py` (contract helper `assert_rate_contract(calculator, *, currency="EUR")` here: a
`RatingError` for a zone in `ZONES` re-raised as `AssertionError(f"rejected zone {zone} that the
contract accepts")`; wrong currency raises `AssertionError(f"priced in {currency_seen}, contract
requires EUR")`; every zone at 0.5 kg and 1200 kg. Negative fixtures `AsiaOnlyRate(BaseRate)`
raising unless zone `"ASIA"`, structural `DollarRate` returning USD):
7. `test_calculator_honours_the_rate_contract[BaseRate|FlatRate]`.
8. `test_contract_catches_a_strengthened_precondition`: `pytest.raises(AssertionError,
   match="rejected zone EU")` on `AsiaOnlyRate`.
9. `test_contract_catches_a_weakened_postcondition`: `match="priced in USD"` on `DollarRate`.
10. `test_mypy_rejects_an_incompatible_override[narrowed-argument|widened-return|misspelled-override]`
    (snippets subclass `BaseRate` with `@override`): narrowed `def price(self, consignment_id:
    ConsignmentId, /) -> Money`: exit 1, `{"override"}`, contains `This violates the Liskov
    substitution principle`; widened `-> Money | None`: exit 1, `{"override"}`, contains
    `Return type "Money | None"`; misspelled `prcie` with `@override`: exit 1, `{"misc"}`,
    contains `marked as an override, but no base method was found`.
11. `test_mypy_accepts_an_override_that_widens_the_argument`: `consignment: Consignment | None`:
    exit 0, empty stdout.
12. `test_mypy_checks_a_structural_calculator_where_it_is_used`: a class with `price(...) ->
    Decimal` passed as `calculator=`: exit 1, `{"arg-type"}`, contains `Following member(s)`.
13. `test_mypy_cannot_see_a_behavioural_violation`: `AsiaOnlyRate` and `DollarRate` passed to
    `quote`: exit 0, empty stdout.

Snippet bodies type-check apart from the intended error (return `Money(Decimal("0.00"), "EUR")`,
never `...`, which gives `[empty-body]`). Assert exact code sets. Also `README.md` ("What it
witnesses", ch3 style) and card `_examples/05-srp-ocp-lsp.md` (`order: 5`, eyebrow "Principles:
SOLID · SRP, OCP, LSP"). No `Surcharge`, no `@runtime_checkable`, no `monkeypatch`.

### `examples/06-isp-dip-and-di-without-a-framework` (project `isp-dip-di`, package `isp_dip_di`)

- `domain.py`: `ConsignmentId`, `Weight`, `Consignment(id, weight, origin, destination)`;
  `BookingRequest` (frozen kw_only: `consignment`, `insured: bool = False`); `HandlingKind` enum
  (BOOKED, LOADED, DEPARTED, CLEARED, DELIVERED); `HandlingEvent(consignment_id, kind, location)`
  (single class plus enum; the README says why); `TrackingHistory(events: tuple[HandlingEvent,
  ...])`, frozen, iterable.
- `booking.py` (policy; imports only `domain`): `BookingGateway(Protocol)` with `book(self,
  request: BookingRequest, /) -> str`, `cancel(self, reference: str, /) -> None`; `type AuditSink
  = Callable[[str], None]`; frozen slotted `BookingService(gateway: BookingGateway, audit:
  AuditSink)`: `book` returns the reference and audits `"booked <ref>"`; `cancel` delegates and
  audits `"cancelled <ref>"`.
- `tracking.py` (policy; imports only `domain`): `TrackingGateway(Protocol)` with `track(self,
  consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]`; `tracking_history(
  consignment_id, *, gateway: TrackingGateway) -> TrackingHistory`.
- `carriers.py` (adapters; imports only `domain`): in-memory `FastlineGateway`, `AircoGateway`
  with `book`, `track`, `cancel`; `book` returns `"FASTLINE:<id>"` / `"AIRCO:<id>"` and records a
  BOOKED event at the origin. No base class.
- `app.py` (composition root; only importer of `carriers`): `class CarrierGateway(BookingGateway,
  TrackingGateway, Protocol): pass`; `GATEWAYS: Mapping[str, Callable[[], CarrierGateway]] =
  MappingProxyType({"FASTLINE": FastlineGateway, "AIRCO": AircoGateway})`; frozen slotted
  `App(booking: BookingService, track: Callable[[ConsignmentId], TrackingHistory])`;
  `build_app(carrier, *, audit, gateways=GATEWAYS) -> App`: `ValueError` naming an unknown code;
  one gateway; `App(BookingService(gateway, audit), partial(tracking_history, gateway=gateway))`.

`tests/conftest.py`: consignment fixture; `FakeBooker` (records requests; `book`, `cancel`);
`FakeTracker` (`track` only); `FakeCarrier` (all three).

`test_isp.py`:
1. `test_adapters_satisfy_every_role_without_naming_one`: typed assignments to `BookingGateway`,
   `TrackingGateway`, `CarrierGateway` (static half verified by the member's mypy run); runtime: no
   Protocol in `type(gw).__mro__`; book then track returns the BOOKED event.
2. `test_a_fat_protocol_forces_fakes_to_stub_unused_methods`: snippet passing a track-only class
   to a `CarrierGateway` parameter: exit 1, `{"arg-type"}`, contains `is missing following
   "CarrierGateway" protocol members` and `book, cancel`; the same class to `tracking_history`:
   exit 0; runtime `tracking_history(id, gateway=FakeTracker())` returns the fake's events.

`test_dip.py`:
3. `test_booking_service_runs_against_an_injected_fake`: reference is the fake's,
   `fake.requests == [request]`, `records == ["booked <ref>"]`; no adapter built.
4. `test_policy_modules_do_not_import_the_adapters[booking|tracking]`: imports collected with
   `ast.parse(inspect.getsource(module))` exclude `isp_dip_di.carriers` and `isp_dip_di.app`.
5. `test_adapters_import_neither_policy_nor_protocols`: `carriers` imports exclude
   `isp_dip_di.booking`, `isp_dip_di.tracking`, `isp_dip_di.app`.
6. `test_autospec_bypasses_mypy`: snippet passing `create_autospec(TrackingGateway,
   instance=True)` as `gateway=` to `BookingService`: exit 0, empty stdout.
7. `test_autospec_enforces_the_protocol_shape_at_runtime`: `.book` raises `AttributeError`;
   `.track()` raises `TypeError` matching `missing a required argument`; with a `BookingGateway`
   autospec, `service.cancel("FASTLINE:CN-1")` then `gateway.cancel.assert_called_once_with(...)`.
8. `test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment`: binding a non-gateway:
   exit 1, `{"arg-type"}`; calling with an `int`: exit 1, `{"arg-type"}`; assigning to
   `Callable[[int], TrackingHistory]`: exit 0 (records a mypy 2.4.1 limitation; if it flips,
   revise the prose).

`test_composition_root.py`:
9. `test_build_app_shares_one_gateway_between_booking_and_tracking`:
   `app.booking.gateway is app.track.keywords["gateway"]`.
10. `test_partial_injects_a_collaborator_into_a_function`: `isinstance(app.track, partial)`,
    `app.track.func is tracking_history`; after a booking `list(app.track(id))` is the BOOKED event.
11. `test_swapping_the_carrier_changes_no_consumer`: FASTLINE vs AIRCO references prefixed by code;
    `type(app.booking) is BookingService` both; same `tracking_history`.
12. `test_composition_root_accepts_a_substitute_without_patching`: `gateways={"FASTLINE":
    FakeCarrier}` wires `FakeCarrier`; `GATEWAYS` unchanged.
13. `test_unknown_carrier_fails_at_the_composition_root`: `pytest.raises(ValueError,
    match="NOSUCH")`.

Also `README.md` and card `_examples/06-isp-dip-and-di-without-a-framework.md` (`order: 6`). No
`monkeypatch`, `mock.patch`, `@runtime_checkable`, or `print(` in source.

## Steps and status

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| 0 | Plan file; PDP-105a..c and 106a..c active; domain-model ch5/ch6 rows (bucket `n.a. (principle)`, new ch5 failure demo, ch5 names drop `Surcharge` and add `BaseRate`, `FlatRate`, `TAX_RULES`, `percent`, `TaxRule`, `AuditSink`, `RatingError`; ch6 adds `BookingGateway`, `TrackingGateway`, `BookingService`, `tracking_history`, `App`, `HandlingKind`); reconciliation rows 29-36 `open` | - | in progress |
| 1a | ch5 member, card, README; gates; handback with test names and scrubbed output | 0 | todo |
| 1b | ch6 member, card, README; one `uv lock` after both exist (sequenced after 1a); gates; handback | 1a | todo |
| 2 | Witness results into reconciliation rows 29-36; a failed witness changes the thesis before prose | 1b | todo |
| 3 | Two figures, specs, `_data/diagrams.yml` (single owner); figures 00-04 unchanged | 1b | todo |
| 4 | ch5 and ch6 `status = "drafted"` | 3 | todo |
| 5 | Two prose agents in parallel; verify attributions; run experiments in a scratch copy; quote fresh filtered output | 3,4 | todo |
| 6 | Opus validation; up to two repair rounds | 5 | todo |
| 7 | PR, `ci-ok` green, ask the user before merge; tag r03.x; notes-only release; PRD build log | 6 | todo |

Reconciliation rows (step 0):

| # | Ch | Claim | Verified by |
| --- | --- | --- | --- |
| 29 | 5 | Replacing one collaborator changes only its own output | `test_each_change_moves_only_its_own_field` |
| 30 | 5 | A new tax rule arrives from outside the package without editing `quote`; the default is read-only | `test_a_new_tax_rule_is_added_without_editing_quote`, `test_default_tax_table_is_read_only` |
| 31 | 5 | mypy checks override signatures (narrowed argument with the LSP note, widened return, `@override` misspelling) and Protocol conformance at the use site; accepts a widened argument | tests 10-12 |
| 32 | 5 | mypy cannot see a strengthened precondition or weakened postcondition; the contract suite catches both | tests 8, 9, 13 |
| 33 | 6 | A track-only fake satisfies the narrow Protocol and fails the fat one under mypy | ch6 test 2 |
| 34 | 6 | Policy modules import no adapters; adapters import neither policy nor Protocols | ch6 tests 4-5 |
| 35 | 6 | An autospec mock is `Any` to mypy even for the wrong Protocol, but enforces the shape at runtime | ch6 tests 6-7 |
| 36 | 6 | mypy 2.4.1 checks a partial's bound argument and calls, not its assignment to a `Callable` annotation | ch6 test 8 |

## Acceptance criteria

1. `bash scripts/verify.sh` prints `verify: all steps passed`.
2. Each new member: `uv run pytest` and `uv run mypy --strict src tests` exit 0 on three
   consecutive runs; `grep -rnE "time\.sleep|perf_counter|time\.time\(|monkeypatch|mock\.patch|runtime_checkable"`
   over both members prints nothing.
3. Every mypy-API test asserts exit status and an exact code set: `grep -c "_codes("` at least 4
   in ch5 `tests/test_lsp.py`, at least 3 across ch6 `test_isp.py` and `test_dip.py`.
4. `validate.py` and `--self-test` exit 0; ch5 and ch6 drafted, one figure each, captions 20-45
   words, 1,900-2,500 prose words (target about 2,200).
5. `grep -c '<blockquote class="ai-sidebar"'` is 1 for ch5 and ch6 (decision 1), and the
   kramdown form `{: .ai-sidebar}` appears nowhere;
   `grep -c "^## When the principle costs more than it buys"` is 1 each; `^## How it works` is 0.
6. Voice `scan.sh --tier ban --fail` exits 0 over ch5, ch6, both READMEs, both cards and both
   SVGs; `--stats` reviewed; `only`, `never`, `always`, `every` checked against the code.
7. Idiomatic scan 0 ban-tier in both members.
8. `python3 scripts/host_ids.py check` exits 0; quoted output shows `<repo>`.
9. `grep -nE "unlike (Java|C#|C\+\+)|in Java|in C#|\.NET|capstone|PDP-|\br0[0-9]\b|spike|SRP dissolves|dissolves? (SRP|OCP|LSP|ISP|DIP)" _docs/0[56]-*.md`
   prints nothing.
10. Every code excerpt matches its source byte for byte; every quoted run matches a fresh run
    apart from scrubbing and duration.
11. `bibliography.html` has the Meyer row (decision 3). Attribution: ch5 names Meyer for OCP's origin, Liskov (1987/1988) and Liskov and Wing (1994)
    for LSP, credits Martin with the formulations; ch6 credits Fowler (2004) for "dependency
    injection"; no SOLID coiner named; bracketed fallbacks applied where unverified (prose agent
    lists checked sources).
12. Each experiment performed in a scratch copy; prose quotes the observed failing test id and
    message; handback includes raw filtered output.
13. `scripts/site-build.sh` succeeds and `git status` is clean after; both figures and example
    pages render; `_data/diagrams.yml` has seven entries; `diagrams/0[0-4]-*` unchanged.
14. Reconciliation rows 29-36 `verified` or `adjusted`, with evidence.
15. CI `ci-ok` green on the PR; merge only after the user's explicit approval.

## Risks

- Impossible witness inherited from the domain model (zero `Weight`): fixed in step 0.
- mypy message drift: assert code sets and short substrings; re-run on every mypy pin bump; ch6
  test 8 flips if mypy improves partial checking (then revise the prose).
- Snippets with accidental extra errors (`[empty-body]`, `[no-untyped-def]`): exact code sets.
- Static witnesses pytest does not exercise (ch6 test 1 typed assignments) rely on the per-member
  mypy run; the prose says so.
- Import-direction witness reads `ast`; misses `importlib.import_module` strings (none used).
- Project names must normalise to the package names or `uv sync` fails.
- `uv.lock` race: 1a and 1b are sequenced.
- Illustrative tax rates read as law: prose calls them illustrative.
- Attribution errors: Meyer vs Martin for the OCP sentence; Liskov 1987 keynote vs 1988
  publication; Design by Contract credit; composition-root source. Fallbacks and criterion 11.
- Overlap with the Protocol chapter, the testing chapter, Appendix C and the Decorator chapter:
  one-sentence pointers by title; no `Surcharge` in ch5.
- Thesis wording slip ("SOLID dissolves"): criterion 9 grep; validation reads every "dissolve".
- Violators read as contrast code: they live in `tests/`, named as negative fixtures.
- Word budget: at most five excerpts per chapter; watch ch5's LSP section against 2,500.
- Liquid: nested dict literals with `{{` need `{% raw %}`.
- Never "chapter N" in prose.
- Re-rendering all specs could alter figures 00-04: criterion 13 diffs them.
