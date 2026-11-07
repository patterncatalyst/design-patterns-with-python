---
title: "r21 evidence: Appendix F principle witnesses (X1c)"
order: 21
output: false
render_with_liquid: false
---

# r21 X1c: principle witnesses for Appendix F

Dated 2026-11-07. Repo commit at the run: bbe9b9b (branch `release/r21`, working tree clean for tracked files). The Law of Demeter member (X1d) does not exist yet, so this file records the Demeter sources and the final project's chain lines only.

## Method

- **Scratch copy.** Built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <dir>`, then `rm -rf .venv .venv-ft` and `uv sync --locked --all-packages`. `srp_ocp_lsp.__file__`, `final_project.__file__` and `fowler_feathers.__file__` all pointed into `<scratch>/examples/...` (confirmed). Interpreter `Python 3.15.2`. The copy was deleted afterwards. No sync ran in the real repo.
- **Run.** The 29 node ids below, from the copy's root with `--import-mode=importlib -q`, three times forward and once in reverse id order: `52 passed in 2.76s`, `52 passed in 2.64s`, `52 passed in 2.69s`, and reversed `52 passed in 2.68s`. 52 is the parametrised case count of the 29 functions (`test_every_booking_kind_works_with_every_carrier` 8, `test_every_cache_form_reads_loads_and_evicts_the_same_way` 6, `test_every_rating_form_quotes_the_same_table` 4, `test_each_change_moves_only_the_fields_it_feeds` 3, `test_mypy_rejects_an_incompatible_override` 3, and 2 each for `test_adapters_satisfy_every_role_without_naming_one`, `test_a_new_booking_kind_needs_no_gateway_change`, `test_calculator_honours_the_rate_contract`, `test_policy_modules_do_not_import_the_adapters`; 1 for the other 20).
- **Names.** Each of the 29 names is defined exactly once across `examples/*/tests` (grep `def <name>\b`, one hit each).
- **Sources.** Fetched 2026-11-07 with `curl -s -L`; HTTP 200 for all eight. "Raw" below means the quoted sentence is found byte-for-byte in the raw HTML; "collapsed" means it matches only after collapsing the source's line wraps and double spaces, so a reader-facing quote must be the collapsed text. Neither martinfowler.com page carries a `draft-notice` (`grep -c draft-notice` is 0 for both, and "draft" occurs once in Yagni's raw HTML, in unrelated body text).

Node ids (all under `examples/`):

```
05-srp-ocp-lsp/tests/test_srp.py::test_each_change_moves_only_the_fields_it_feeds
05-srp-ocp-lsp/tests/test_srp.py::test_pricing_and_tax_run_alone
05-srp-ocp-lsp/tests/test_ocp.py::test_a_new_tax_rule_is_added_without_editing_quote
05-srp-ocp-lsp/tests/test_lsp.py::test_calculator_honours_the_rate_contract
05-srp-ocp-lsp/tests/test_lsp.py::test_contract_catches_a_strengthened_precondition
05-srp-ocp-lsp/tests/test_lsp.py::test_contract_catches_a_weakened_postcondition
05-srp-ocp-lsp/tests/test_lsp.py::test_mypy_rejects_an_incompatible_override
05-srp-ocp-lsp/tests/test_lsp.py::test_mypy_cannot_see_a_behavioural_violation
06-isp-dip-and-di-without-a-framework/tests/test_isp.py::test_a_fat_protocol_forces_fakes_to_stub_unused_methods
06-isp-dip-and-di-without-a-framework/tests/test_isp.py::test_adapters_satisfy_every_role_without_naming_one
06-isp-dip-and-di-without-a-framework/tests/test_dip.py::test_policy_modules_do_not_import_the_adapters
06-isp-dip-and-di-without-a-framework/tests/test_dip.py::test_adapters_import_neither_policy_nor_protocols
06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py::test_swapping_the_carrier_changes_no_consumer
06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py::test_unknown_carrier_fails_at_the_composition_root
39-final-project/tests/test_structure.py::test_only_the_composition_root_names_a_concrete_carrier
19-adapter-facade-bridge/tests/test_adapter.py::test_a_class_adapter_still_exposes_the_clients_own_methods
19-adapter-facade-bridge/tests/test_bridge.py::test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier
19-adapter-facade-bridge/tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier
19-adapter-facade-bridge/tests/test_bridge.py::test_a_new_booking_kind_needs_no_gateway_change
32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_the_fuel_surcharge_lives_in_one_definition_of_the_function
32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_the_engine_needs_more_classes_functions_and_lines_than_the_function
32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time
32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_one_engine_quote_makes_more_python_calls_than_the_function
32-anti-patterns-and-pattern-misuse/tests/test_forms.py::test_every_rating_form_quotes_the_same_table
32-anti-patterns-and-pattern-misuse/tests/test_misuse.py::test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered
31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read
31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_an_eafp_read_reloads_when_another_thread_evicts_first
31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_two_eafp_readers_that_both_miss_both_load
31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_every_cache_form_reads_loads_and_evicts_the_same_way
```

In the entries below, a bare test name lives in the file of its principle's chapter member as listed in the node ids above.

## Kept principles

### SRP

- **Verdict:** keep.
- **Chapter:** "SRP, OCP, and LSP in Python" (`_docs/05-srp-ocp-lsp.md`, line 36: Martin states it as "a class should have only one reason to change" in *Agile Software Development: Principles, Patterns, and Practices* (2002)).
- **Source:** book only (Martin, bibliography). Nothing fetched, so F quotes the chapter's attribution and no further text of the book.
- **Witnesses:**
  - `test_each_change_moves_only_the_fields_it_feeds` (`05-srp-ocp-lsp/tests/test_srp.py`, 3 cases): replacing the tariff, the tax rule or the audit sink moves exactly the quote fields that component feeds (`{net, tax}`, `{tax}`, `set()`), so each concern has its own reason to change.
  - `test_pricing_and_tax_run_alone` (`test_srp.py`): pricing and the tax rule each produce their result with no `quote`, audit or other collaborator, so the concerns are separable units.
- **Result:** passes (summary above).

### OCP

- **Verdict:** keep.
- **Chapter:** "SRP, OCP, and LSP in Python" (line 85: Meyer's 1988 inheritance version and Martin's abstraction restatement; the test line quoted in the plan is "...without reopening code that is tested and in service.").
- **Source:** books only (Meyer, Martin; bibliography). Nothing fetched.
- **Witness:** `test_a_new_tax_rule_is_added_without_editing_quote` (`05-srp-ocp-lsp/tests/test_ocp.py`): a Hong Kong exempt rule is passed in as data (`{**TAX_RULES, "HK": exempt}`) and `quote` prices it, while `"HK" not in TAX_RULES` shows the shipped table and `quote` were not edited. Extension without modification.
- **Result:** passes.

### LSP with Design by Contract

- **Verdict:** keep (the strongest block).
- **Chapter:** "SRP, OCP, and LSP in Python" (line 117, Liskov's OOPSLA '87 keynote and Liskov and Wing, TOPLAS 16(6), 1994; line 245, Meyer for Design by Contract).
- **Source:** books and the two papers as ch05 cites them; no URL fetched, so F attributes by citation only and quotes ch05's own sentence ("a subtype may accept more than its supertype and promise more, and it may not accept less or promise less.", line 117 per the plan).
- **Witnesses:**
  - `test_calculator_honours_the_rate_contract` (`test_lsp.py`, 2 cases `BaseRate`, `FlatRate`): one contract suite (`assert_rate_contract`) passes for both real subtypes, so each is substitutable for the supertype's promises.
  - `test_contract_catches_a_strengthened_precondition` (`test_lsp.py`): `AsiaOnlyRate` rejects zone EU and the suite fails with `rejected zone EU`, a subtype that accepts less.
  - `test_contract_catches_a_weakened_postcondition` (`test_lsp.py`): `DollarRate` fails with `priced in USD`, a subtype that promises less.
  - `test_mypy_rejects_an_incompatible_override` (`test_lsp.py`, 3 cases): mypy `--strict` exit 1 with the Liskov message for a narrowed argument, `Return type "Money | None"` for a widened return, and the misspelt override.
  - `test_mypy_cannot_see_a_behavioural_violation` (`test_lsp.py`): the behavioural violation gets mypy exit 0 and empty output, which is the other half the contract suite catches.
- **Note:** `test_contract_catches_an_accepted_unknown_zone` (same file) is a third contract-suite negative case; the plan's table omits it, so F may cite it or leave it out. Not run here.
- **Result:** passes.

### ISP

- **Verdict:** keep.
- **Chapter:** "ISP, DIP, and dependency injection without a framework" (`_docs/06-...md`, line 24: "Robert C. Martin's interface segregation principle says a client should not be forced to depend on methods it does not use.").
- **Source:** Martin (bibliography). Nothing fetched.
- **Witnesses:**
  - `test_a_fat_protocol_forces_fakes_to_stub_unused_methods` (`06-.../tests/test_isp.py`): mypy rejects a `TrackOnly` fake against the fat `CarrierGateway` (`is missing following "CarrierGateway" protocol members`, `book, cancel`) and accepts it against the narrow tracking Protocol (exit 0, empty output), then the narrow fake runs `tracking_history`. A client forced onto unused methods versus one that depends on what it uses.
  - `test_adapters_satisfy_every_role_without_naming_one` (`test_isp.py`, 2 cases): each adapter satisfies the booking, tracking and carrier roles with none of the three Protocols in its `__mro__`, so the narrow roles cost the adapter nothing.
- **Result:** passes.

### DIP

- **Verdict:** keep.
- **Chapter:** "ISP, DIP, and dependency injection without a framework" (line 76: "High-level modules should not depend on low-level modules, and both should depend on abstractions." and the second clause).
- **Source:** Martin (bibliography); ch06 also cites Fowler's injection article, https://martinfowler.com/articles/injection.html (cited in the bibliography, not re-fetched here).
- **Witnesses:**
  - `test_policy_modules_do_not_import_the_adapters` (`06-.../tests/test_dip.py`, 2 cases `booking`, `tracking`): an AST import collector shows neither policy module imports `carriers` or `app`, so the policy does not depend on the detail.
  - `test_adapters_import_neither_policy_nor_protocols` (`test_dip.py`): the adapters import only `domain`, so the detail does not depend on the policy or the Protocols (the second clause).
  - `test_swapping_the_carrier_changes_no_consumer` (`06-.../tests/test_composition_root.py`): both carriers yield a `BookingService` and the same `tracking_history` partial, with only the reference differing.
  - `test_only_the_composition_root_names_a_concrete_carrier` (`39-final-project/tests/test_structure.py`): across the package only `app.py` names `FastlineGateway` or `FastlineClient` (`carriers.py` excluded), the composition root at project scale.
- **Result:** passes.

### Composition over inheritance

- **Verdict:** keep.
- **Chapter:** "Adapter, Facade, and Bridge" (`_docs/19-...md`, line 166: Rhodes quotes the Gang of Four principle "Favor object composition over class inheritance."; line 132 for the class adapter leak).
- **Source:** https://python-patterns.guide/gang-of-four/composition-over-inheritance/ (HTTP 200). "Favor object composition over class inheritance." found raw, once. Crediting Brandon Rhodes by page title.
- **Witnesses:**
  - `test_a_class_adapter_still_exposes_the_clients_own_methods` (`19-.../tests/test_adapter.py`): the inheriting adapter has `submit_shipment` and the composing `FastlineGateway` does not, so inheritance leaks the client's interface.
  - `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier` (`19-.../tests/test_bridge.py`): AST count, the bridge declares `["InsuredBooking", "StandardBooking"]` while class-per-pair declares five (`_CarrierBooking` plus four pairs); N plus M against N times M.
  - `test_every_booking_kind_works_with_every_carrier` (`test_bridge.py`, 8 cases = 2 carriers x 2 kinds x {bridge, class-per-pair}): both designs pass one table, so the class count is the only difference. Supporting witness, not stand-alone: on its own it shows behaviour, not composition. Cite only together with the class-count test.
- **Result:** passes.

### DRY

- **Verdict:** keep, qualified (weakest of the kept rows; see Flags).
- **Chapter:** "Anti-patterns and pattern misuse" (`_docs/32-...md`, line 68: "The second measure is where one rule lives. The fuel surcharge is one decision, and the test finds every definition whose own name or own statements mention `fuel`."; line 68 of the plan's note: "Changing how the surcharge is applied means reading five places to find the one that decides."). The book never uses the word DRY.
- **Source:** https://pragprog.com/tips/ (HTTP 200). Raw, once: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." (The tip's title holds an em dash and an entity and is not quoted.)
- **Witness:** `test_the_fuel_surcharge_lives_in_one_definition_of_the_function` (`32-.../tests/test_measure.py`): the AST search for definitions whose own name or statements say `fuel` finds `["quote"]` in the function and five in the engine (`_ChargeVisitor.visit_fuel`, `_FlatFeeStrategy.charges`, `_FuelSurcharge`, `_FuelSurcharge.accept`, `_NetTotalVisitor.visit_fuel`): one authoritative place against five.
- **Flag:** the fee value itself is not duplicated (`tariff.fuel_fee` is a single field in `rating.py` that the engine reads, `conftest.py` line 80); what the test counts is the rule's treatment scattered over five definitions, a name-match count. That matches "single, authoritative representation" of how the rule applies, not repeated copies of one fact. F must say "where the rule lives" and not "duplicated code". If the owner prefers a clean DRY case, cut the row rather than stretch it.
- **Result:** passes.

### YAGNI

- **Verdict:** keep.
- **Chapter:** "Anti-patterns and pattern misuse" (line 139, the sidebar prompt: "Add a class or a Protocol only when it holds state, offers several operations or has a second implementation today, and name the change it makes cheaper."); a second pointer is "ISP, DIP, and dependency injection without a framework" line 155 ("A Protocol with one implementation and no test double adds a name without adding a seam.").
- **Source:** https://martinfowler.com/bliki/Yagni.html (HTTP 200, no `draft-notice`). The defining sentence in the raw HTML, wrapped over lines 212 and 213 with curly quotes: "It's a statement that some capability we presume our software needs in the future should not be built now because “you aren't gonna need it”." The raw line break makes the full sentence match only after collapsing whitespace; the clause "should not be built now" (one raw line, count 1) is exact. Line 212 begins mid-sentence with `statement that some capability we presume...`, so quote from "some capability".
- **Witnesses:**
  - `test_the_engine_needs_more_classes_functions_and_lines_than_the_function` (`test_measure.py`): the function measures `(0, 1, 8)` classes, functions, lines; the engine `(9, 17, 57)`. Capability built beyond the one decision it serves.
  - `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time` (`test_measure.py`): the speculative extension point (visitor) fails on the first real extension with `AttributeError: ... no attribute 'visit_remote_area'`, so the generality bought is not what it was built for.
- **Result:** passes.

### Simple design (Beck's rules)

- **Verdict:** keep.
- **Chapter:** "Anti-patterns and pattern misuse" (the same rating-engine pair), with "Patterns as decisions under forces" line 85 ("Martin's warning about needless complexity points the same way...").
- **Source:** https://martinfowler.com/bliki/BeckDesignRules.html (HTTP 200, no `draft-notice`). Raw, one per line: "Passes the tests", "Reveals intention", "No duplication", "Fewest elements" (lines 245 to 251, a `<li>` list), followed by "The rules are in priority order, so “passes the tests” takes priority over “reveals intention”" (after tag and whitespace collapse). Page `<title>` is "Beck Design Rules".
- **Witnesses:**
  - `test_every_rating_form_quotes_the_same_table` (`32-.../tests/test_forms.py`, 4 cases = 2 zones x 2 forms): the function and the engine both pass one table of totals (`35.70`, `78.05`), so "passes the tests" holds for both and the comparison is on size alone.
  - `test_one_engine_quote_makes_more_python_calls_than_the_function` (`test_measure.py`): one `quote` is 1 Python call in the function and 11 in the engine, "fewest elements" measured at run time.
  - The class, function and line counts of `test_the_engine_needs_more_classes_functions_and_lines_than_the_function` (above) serve "fewest elements" statically; listed under YAGNI, may be cited here as well.
- **Flag:** the tests witness "passes the tests" and "fewest elements" only. "Reveals intention" and "no duplication" have no test of their own here (the fuel test is the DRY row). F should say which rules the tests show and not claim all four.
- **Result:** passes.

### Orthogonality

- **Verdict:** keep.
- **Chapter:** "Adapter, Facade, and Bridge" (line 166: two things that vary "so each can change without disturbing the other").
- **Source:** https://pragprog.com/tips/ (HTTP 200). Raw, once: "Design components that are self-contained, independent, and have a single, well-defined purpose."
- **Witnesses:**
  - `test_a_new_booking_kind_needs_no_gateway_change` (`19-.../tests/test_bridge.py`, 2 cases): a booking kind defined in the test module (`_ExpressBooking`, test_bridge.py:86) runs on either carrier through the two existing gateway primitives, so the kind axis and the carrier axis vary independently.
  - `test_each_change_moves_only_the_fields_it_feeds` (`05-.../tests/test_srp.py`, 3 cases): the same test cited for SRP; for orthogonality the point is that three components change independently with no effect on the fields they do not feed.
- **Flag:** the second witness is shared with SRP. It is a fair instance of both but F must not present it as two independent proofs; the Bridge test is the primary one.
- **Result:** passes.

### Fail fast

- **Verdict:** keep.
- **Chapter:** "ISP, DIP, and dependency injection without a framework" (line 143: "An unknown code fails at start-up, where the mistake is cheap to find."); contrast in "Anti-patterns and pattern misuse".
- **Source:** Jim Shore, https://martinfowler.com/ieeeSoftware/failFast.pdf (HTTP 200, PDF; text via `pdftotext`). The sentence is found once after joining the PDF's line breaks: "A system that fails fast does exactly the opposite: when a problem occurs, it fails immediately and visibly." (PDF text, not HTML, so there is no raw HTML form.)
- **Witnesses:**
  - `test_unknown_carrier_fails_at_the_composition_root` (`06-.../tests/test_composition_root.py`): `build_app("NOSUCH", ...)` raises `ValueError` matching `NOSUCH` at construction, before any booking exists.
  - Contrast: `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered` (`32-.../tests/test_misuse.py`): the service-locator engine builds fine and raises `KeyError: 'tariff'` only at the first `quote`, late and at use.
- **Result:** passes.

### EAFP

- **Verdict:** keep.
- **Chapter:** "Shortcut patterns: dict dispatch, function tables, and EAFP" (`_docs/31-...md`, line 75, the glossary quote).
- **Source:** https://docs.python.org/3/glossary.html (HTTP 200), term `EAFP`. Raw HTML has the sentence wrapped across three lines and two spaces after the first full stop (`permission.  This`), so it matches only after collapsing whitespace: "Easier to ask for forgiveness than permission. This common Python coding style assumes the existence of valid keys or attributes and catches exceptions if the assumption proves false." (as ch31 quotes it). The next sentence of the entry is "This clean and fast style is characterized by the presence of many try and except statements" (inside tags).
- **Witnesses:**
  - `test_every_cache_form_reads_loads_and_evicts_the_same_way` (`31-.../tests/test_eafp.py`, 6 cases): look-first and EAFP forms agree on one table, so the choice is style and race behaviour, not result.
  - `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`: a forced interleaving makes the test-then-read form raise `KeyError: '0901.21'` with no load.
  - `test_an_eafp_read_reloads_when_another_thread_evicts_first`: the same interleaving makes the EAFP form reload and return `8.0`.
  - `test_two_eafp_readers_that_both_miss_both_load`: the cost, two readers that both miss both load (`codes == [CODE, CODE]`). This witnesses EAFP's trade-off, not the principle's definition; F can cite it as the stated cost.
- **Result:** passes.

## Law of Demeter (sources and chain lines only)

The member (`examples/46-appendix-f-programming-principles`) is built by X1d and its tests are not run or recorded here. HTTP 200 for both pages, fetched 2026-11-07. Neither page is dated or versioned; `LawOfDemeter.html` returned 404 at planning. Credit by page title (the Demeter project at Northeastern University).

**general-formulation.html** (https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html):

- Raw exact: `"Only talk to your immediate friends" is the motto.` (straight double quotes in the raw HTML; count 1).
- Raw lines 17 and 18, exact after collapsing the line break: `Each unit should have only limited knowledge about other units: only units "closely" related to the current unit.`
- Raw lines 12 and 13, exact after collapsing the line break: `The style rule was discovered at Northeastern University in the fall of 1987 by Ian Holland.`
- Neither quote holds a dash.

**object-formulation.html** (https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html):

- Raw exact, count 1: `Within a method, messages can only be sent to the following objects:` followed by the list, which after tag collapse reads: 1 A parameter of the method, including the enclosing object (this or self); 1.1 For pragmatic reasons: a global object; 2 An immediate part object (computed or stored); 2.1 An object that a method called on the enclosing object returns, including attributes of the enclosing object; 2.2 An element of a collection which is an attribute of the enclosing object; 3 An object created within the method. The page's heading is `"Do not talk to strangers".`
- Plan difference: item 2.1 says the immediate part includes "an object that a method called on the enclosing object returns, including attributes of the enclosing object". F's paraphrase of the list must keep that, because it bears on whether `self._plan.sailing` (an attribute) and `.origin` count.

**Final project chain lines**, checked at bbe9b9b (exact line text, leading indent kept as in the file):

- `examples/39-final-project/tests/test_acceptance.py:40`: `    if shipment.invoice.total != Money(Decimal("35.63")):`
- `examples/39-final-project/tests/test_acceptance.py:41`: `        failures.append(f"invoice {shipment.invoice.total.amount}")`
- both are in `acceptance_failures` (defined at line 31); the helper's lines 36 to 39 also read `shipment.quote.total`, `shipment.quote.total.amount`, `shipment.declaration.duty` and `shipment.declaration.duty.amount`, the same shape as the invoice chain.
- `examples/39-final-project/tests/test_parts.py:98`: `        totals.append((shipment.quote.total, shipment.invoice.total))` (contains `shipment.invoice.total`; the line also reads `shipment.quote.total`).
- `examples/39-final-project/src/final_project/desk.py:58`: `            HandlingEvent(consignment.id, HandlingKind.BOOKED, self._plan.sailing.origin)`
- Also found, not in the plan: `examples/39-final-project/tests/conftest.py:118` holds the same `self._plan.sailing.origin` expression in the comparison desk `_EagerBookingDesk`.
- `examples/39-final-project/src/final_project/billing.py:39`: `        raise SettlementError(f"{payment.amount} does not settle {invoice.total.amount}")`, with the check on line 38 `    if payment != invoice.total:`. `invoice` is a parameter and `.total` its part, so line 39 reads one step past an immediate part (`invoice.total.amount`); line 38 reads only the part.

## Cut list

Each cut has no prose in `_docs/` (grep, recorded in the plan's evidence F) or no code that a test could witness. Reason recorded, no stretch attempted.

- **KISS** as a name: no fetched source defines the acronym; the chapter's words are Martin's "needless complexity" and Beck's rules (kept as simple design).
- **Tell, Don't Ask:** no prose in the book and no test framed by it; the Fowler page was fetched at planning but nothing in the repo witnesses it separately from the Demeter member.
- **Zen of Python:** no chapter quotes PEP 20 (no hit for "PEP 20", "explicit is better", "obvious way").
- **Rule of Three:** no prose, no test.
- **Hollywood principle:** no prose, no test.
- **Separation of concerns:** folded into SRP by the chapter's own sentence; a separate row would repeat the SRP tests.
- **Do one thing** and **Boy Scout Rule:** no prose, no test; the Clean Code bibliography row is corrected to the meaningful-names use (decision 6).
- **Brooks's Law** and **tracer bullets:** project and process claims that no code can witness; Brooks's Law is an outcome claim.

## Flags and differences from the plan

- No mapping failed. Two are weak enough to call out for the owner: **DRY** (the test counts where a rule's logic lives by name match, not repeated copies; keep only with the "where the rule lives" wording or cut) and **Beck's rules** (the tests show two of the four rules, "passes the tests" and "fewest elements"; F must not claim the other two).
- **Supporting-only witnesses**, cite beside a primary test and not alone: `test_every_booking_kind_works_with_every_carrier` (composition), `test_two_eafp_readers_that_both_miss_both_load` (EAFP's cost), the shared `test_each_change_moves_only_the_fields_it_feeds` (orthogonality).
- **No fetched source** for SRP, OCP, LSP, ISP, DIP; they rest on the bibliography books and, for LSP, the two papers as ch05 cites them. F quotes only ch05 and ch06's own sentences for these.
- The Yagni defining sentence and the EAFP glossary entry are exact only after whitespace collapse (not byte-exact in the raw HTML); the Fail Fast sentence is from PDF text. The BeckDesignRules four rules are raw one per `<li>`.
- Differences in the Demeter chain lines from the plan: the helper `acceptance_failures` also chains `shipment.quote.total` and `shipment.declaration.duty` (lines 36 to 39); `conftest.py:118` repeats the `self._plan.sailing.origin` expression; `billing.py:39` was already listed in the plan's evidence V.
- `test_contract_catches_an_accepted_unknown_zone` exists in `test_lsp.py` and is not in the plan's LSP list.
