---
title: "Evidence: Deck 101 witness census (r22, Y1b)"
output: false
render_with_liquid: false
---

# Deck 101 witness census

Recorded 2026-11-07 for r22, step Y1b, on Python 3.15.2 and pytest 9.2.0, at commit `668526f` on `release/r22` (the working tree then held only this file, the extended `presentation/render-png.sh` and five new PNGs). Paths are repo-relative; `<scratchpad>` stands for the session scratch directory.

## Method

- Each slide of the plan's 62-slide inventory is recorded with its claim, the chapter's exact front-matter title, and the chapter sentences it rests on. A sentence is a fragment re-found with the `grep -nF -- <fragment> <chapter file>` command shown beside it. A fragment is accepted only when it hits exactly one line, so the line number cannot drift between two copies of a phrase. Credits (URLs and attributions) may hit two lines, the body and the chapter's "For deeper coverage" paragraph, and show both.
- A witness test is cited by exact name. Each was searched with `^\s*(async )?def <name>\(` under `examples/*/tests/**/*.py` and has exactly one definition (equivalent to `grep -rc 'def <name>(' examples/*/tests` summing to 1). None is a method inside a class, so a node id is `<file>::<name>`.
- A code slide gives the source path, the 1-based line range and the anchor, which is the exact first line including its indentation. The deck builder reads the range from the file at build time and asserts the anchor, so the excerpt is byte-exact with the source by construction. Where the chapter quotes the same lines as a contiguous run of one fenced block, that is recorded too.
- A figure slide names the figure and its committed PNG.
- The `render-png.sh` default list was checked and extended; see "Figure census".
- Every witness test was run by node id in a fresh scratch copy; see "Witness test runs".

## Summary

62 slides. 59 kept as the plan has them (some with a recorded range or witness fix), 3 reworded (slide 22 and slide 61 settled; slide 62 proposed), none cut. Every content, code and table slide has a witness test or a recorded chapter sentence; no slide's claim is stretched beyond them. The slide-kind counts in the inventory are 2 cover and route, 9 dividers, 6 figures, 26 code, 9 tables and 10 bullet slides (see Corrections).

| # | Section | Title | Kind | Disposition | Reason |
| --- | --- | --- | --- | --- | --- |
| 1 | Cover | Design Patterns with Python | cover | kept | structural slide |
| 2 | Cover | The deck's route | route | kept | structural slide |
| 3 | Why patterns | divider | divider | kept | structural slide |
| 4 | Why patterns | Decisions under forces | bullets | kept | prose only: three chapter sentences confirmed; chapter 1 has no example, so the slide claims nothing a test would have to show |
| 5 | Why patterns | Proof that runs | code | kept | range fixed at 36 to 43: a contiguous run of the chapter's fence (the chapter elides `__post_init__` and `reweigh` is not on the slide, so `test_reweigh...` is witnessed in the notes only) |
| 6 | What 1994 assumed | divider | divider | kept | structural slide |
| 7 | What 1994 assumed | The 1994 assumptions | bullets | kept | five assumptions from the chapter's own sentences, with five split tests as witnesses chosen by section (the chapter names none) |
| 8 | What 1994 assumed | Three ways out | bullets | kept | claim, witness and excerpt confirmed |
| 9 | What 1994 assumed | What dissolves | table | kept | ten of the eleven rows have a `test_dissolve` witness; the If-chain dispatch row is witnessed by a chapter 31 test, named in the row table |
| 10 | What 1994 assumed | What survives | table | kept | only Command has a witness in the split's own tests; every other row is witnessed in its own chapter's example, named in the row table |
| 11 | What 1994 assumed | One name, two meanings | table | kept | claim, witness and excerpt confirmed |
| 12 | What 1994 assumed | Dissolved in code | code | kept | claim, witness and excerpt confirmed |
| 13 | What 1994 assumed | Names for assistants | bullets | kept | prose only: four chapter sentences confirmed; chapter 4 has no example |
| 14 | SOLID in Python | divider | divider | kept | structural slide |
| 15 | SOLID in Python | One reason to change | bullets | kept | claim, witness and excerpt confirmed |
| 16 | SOLID in Python | How a quote flows | figure | kept | figure confirmed: every arrow composed by code, PNG equals a fresh render |
| 17 | SOLID in Python | Open to a new tax | code | kept | claim, witness and excerpt confirmed |
| 18 | SOLID in Python | The rate contract | code | kept | claim, witness and excerpt confirmed |
| 19 | SOLID in Python | Narrow roles | code | kept | claim, witness and excerpt confirmed |
| 20 | SOLID in Python | The composition root | code | kept | claim, witness and excerpt confirmed |
| 21 | SOLID in Python | Wiring the application | figure | kept | figure confirmed: every arrow composed by code, PNG equals a fresh render |
| 22 | SOLID in Python | Principles beyond SOLID | table | reworded | Appendix F's table at 46.md:34-38 is SOLID only, and slides 15 to 20 already carry it. The principles beyond SOLID have no table in the chapter, so the slide table is built from the chapter's own sections (eight rows, one witness each), and the claim reads "the principles Appendix F tests beyond SOLID". |
| 23 | SOLID in Python | Ask the shipment | code | kept | claim, witness and excerpt confirmed |
| 24 | Selecting and varying behaviour | divider | divider | kept | structural slide |
| 25 | Selecting and varying behaviour | Strategy as a callable | code | kept | package path fixed: `examples/12-strategy-the-callable/src/strategy_callable/rules.py` |
| 26 | Selecting and varying behaviour | Rules in a registry | figure | kept | figure confirmed: every arrow composed by code, PNG equals a fresh render |
| 27 | Selecting and varying behaviour | Hooks, not subclasses | code | kept | claim, witness and excerpt confirmed |
| 28 | Selecting and varying behaviour | State as a table | code | kept | claim, witness and excerpt confirmed |
| 29 | Selecting and varying behaviour | Command with undo | code | kept | claim, witness and excerpt confirmed |
| 30 | Creating objects under control | divider | divider | kept | structural slide |
| 31 | Creating objects under control | Factories in a dict | code | kept | claim, witness and excerpt confirmed |
| 32 | Creating objects under control | A family of gateways | code | kept | claim, witness and excerpt confirmed |
| 33 | Creating objects under control | Builder as a dataclass | code | kept | claim, witness and excerpt confirmed |
| 34 | Creating objects under control | Singleton as a module | code | kept | claim, witness and excerpt confirmed |
| 35 | Composing and adapting structure | divider | divider | kept | structural slide |
| 36 | Composing and adapting structure | Adapter, Facade and Bridge | bullets | kept | claim, witness and excerpt confirmed |
| 37 | Composing and adapting structure | A bridge over a Protocol | code | kept | claim, witness and excerpt confirmed |
| 38 | Composing and adapting structure | One call, two axes | figure | kept | figure confirmed: every arrow composed by code, PNG equals a fresh render |
| 39 | Composing and adapting structure | Two things called Decorator | bullets | kept | claim, witness and excerpt confirmed |
| 40 | Composing and adapting structure | Wrapper objects at run time | code | kept | claim, witness and excerpt confirmed |
| 41 | Composing and adapting structure | A name rebound once | code | kept | claim, witness and excerpt confirmed |
| 42 | Composing and adapting structure | A proxy keeps the interface | bullets | kept | claim, witness and excerpt confirmed |
| 43 | Composing and adapting structure | One weight question | code | kept | claim, witness and excerpt confirmed |
| 44 | Composing and adapting structure | Shared commodities | figure | kept | figure confirmed: every arrow composed by code, PNG equals a fresh render |
| 45 | Coordinating and traversing | divider | divider | kept | structural slide |
| 46 | Coordinating and traversing | What a signal decides | code | kept | claim, witness and excerpt confirmed |
| 47 | Coordinating and traversing | A chain of stages | code | kept | claim, witness and excerpt confirmed |
| 48 | Coordinating and traversing | One release rule | code | kept | claim, witness and excerpt confirmed |
| 49 | Coordinating and traversing | Generators as iterators | code | kept | claim, witness and excerpt confirmed |
| 50 | Coordinating and traversing | Visitor as a match | code | kept | claim, witness and excerpt confirmed |
| 51 | Coordinating and traversing | Snapshot and rollback | code | kept | claim, witness and excerpt confirmed |
| 52 | Coordinating and traversing | A tariff, two readings | code | kept | claim, witness and excerpt confirmed |
| 53 | Coordinating and traversing | Match, snapshot, tariff tree | figure | kept | figure confirmed: every arrow composed by code, PNG equals a fresh render |
| 54 | Choosing well | divider | divider | kept | structural slide |
| 55 | Choosing well | When not to | table | kept | prose only: six sentences, each in its chapter's When-not section; the chapters give no test for them, and the notes say so |
| 56 | Choosing well | Pattern to force | table | kept | ten rows chosen (the plan allows at most twelve) |
| 57 | Choosing well | Prompting for a pattern | bullets | kept | prose only: the sidebar's heading, nested prompt and review line are each found once; the sidebar states no test of its own |
| 58 | Reference | divider | divider | kept | structural slide |
| 59 | Reference | The toolchain | table | kept | six versions confirmed in chapter 0's table, root pyproject.toml and uv --version, and Appendix A |
| 60 | Reference | Sources credited | table | kept | sources grouped as the chapters link them; text-only credits named |
| 61 | Reference | Reading further | table | reworded | No 101 chapter cites Domain-Driven Design or Patterns of Enterprise Application Architecture (only chapters 8 and 30 do), so the two rows leave the list; ten books remain. |
| 62 | Reference | Take it with you | bullets | reworded (proposed) | site and repository URLs only; the hub URL is a cross-reference to a sibling site that CLAUDE.md bars from decks, and no reader-facing file names it. The owner decides |


## Per-slide census

Every chapter sentence below is a `grep -nF` fragment that hit exactly one line of the named chapter at this commit. Every test name was found once under `examples/*/tests` by the regular expression `^\s*(async )?def <name>\(` (the same count as `grep -rc 'def <name>(' examples/*/tests`). A slide with a figure or code range names the figure or the source file and lines.

### Slide 1: Design Patterns with Python (Cover)

- Claim: 101: Patterns and SOLID in Python.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 2: The deck's route (Cover)

- Claim: the nine sections in order.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 3: divider (Why patterns)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 4: Decisions under forces (Why patterns)

- Claim: a pattern is a decision a force asks for, with consequences.
- Chapter: 01, "Patterns as decisions under forces" (`_docs/01-patterns-as-decisions-under-forces.md`).
- `01-patterns-as-decisions-under-forces.md:25`: `grep -nF -- 'A pattern is a solution to a problem in a context, and the problem is a set of forces pulling against each other.' _docs/01-patterns-as-decisions-under-forces.md`
- `01-patterns-as-decisions-under-forces.md:37`: `grep -nF -- 'Consequences is the ledger.' _docs/01-patterns-as-decisions-under-forces.md`
- `01-patterns-as-decisions-under-forces.md:39`: `grep -nF -- 'every pattern has a price, paid whether or not the benefit turns up.' _docs/01-patterns-as-decisions-under-forces.md`
- Witness: prose only (prose only: chapter 1 has no example); no test is claimed.
- Disposition: **kept**. prose only: three chapter sentences confirmed; chapter 1 has no example, so the slide claims nothing a test would have to show.

### Slide 5: Proof that runs (Why patterns)

- Claim: every claim runs under the toolchain; the consignment is a frozen value.
- Chapter: 00, "Prerequisites and the toolchain" (`_docs/00-prerequisites.md`).
- `00-prerequisites.md:23`: `grep -nF -- 'Every example in this book is a small Python package with its own tests, and every chapter ends by running it.' _docs/00-prerequisites.md`
- `00-prerequisites.md:78`: `grep -nF -- 'Every example must pass four checks, in this order:' _docs/00-prerequisites.md`
- `00-prerequisites.md:95`: `grep -nF -- 'Identifiers and weights are value objects, written as frozen, slotted dataclasses that validate themselves on construction.' _docs/00-prerequisites.md`
- `00-prerequisites.md:109`: `grep -nF -- '`frozen=True` makes assignment to a field raise `FrozenInstanceError`' _docs/00-prerequisites.md`
- Witness tests, each defined once:
  - `test_equal_values_compare_equal` (`examples/00-prerequisites/tests/test_consignment.py:16`, 1 definition)
  - `test_reweigh_returns_new_consignment_and_leaves_original_unchanged` (`examples/00-prerequisites/tests/test_consignment.py:28`, 1 definition)
  - `test_instance_rejects_assignment` (`examples/00-prerequisites/tests/test_consignment.py:45`, 1 definition)
- Code: `examples/00-prerequisites/src/consignments/consignment.py` lines 36 to 43 (8 lines, longest 63 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 36, exact): `@dataclass(frozen=True, slots=True, kw_only=True)`
  - Last line (43): `    weight: Weight`
  - Byte-exact with the source by construction (read with `sed -n '36,43p' examples/00-prerequisites/src/consignments/consignment.py`); quoted byte-exact in `00-prerequisites.md` fence opening at line 113 (block lines 1 to 8).
- Disposition: **kept**. range fixed at 36 to 43: a contiguous run of the chapter's fence (the chapter elides `__post_init__` and `reweigh` is not on the slide, so `test_reweigh...` is witnessed in the notes only).

### Slide 6: divider (What 1994 assumed)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 7: The 1994 assumptions (What 1994 assumed)

- Claim: the catalogue assumed objects of declared classes, no first-class behaviour, no structural types.
- Chapter: 02, "What 1994 assumed, and what Python dissolves" (`_docs/02-what-1994-assumed-and-python-dissolves.md`).
- `02-what-1994-assumed-and-python-dissolves.md:32`: `grep -nF -- 'The catalogue'"'"'s central working assumption is that a unit of behaviour reaches a call site wrapped in an object whose class you declared in advance.' _docs/02-what-1994-assumed-and-python-dissolves.md`
- `02-what-1994-assumed-and-python-dissolves.md:36`: `grep -nF -- 'Python 3.15 differs on each count.' _docs/02-what-1994-assumed-and-python-dissolves.md`
- `02-what-1994-assumed-and-python-dissolves.md:179`: `grep -nF -- 'Did the force move, or only the mechanism?' _docs/02-what-1994-assumed-and-python-dissolves.md`
- Witness tests, each defined once:
  - `test_strategy_slot_accepts_def_lambda_and_partial` (`examples/03-three-way-split/tests/test_dissolve.py:47`, 1 definition)
  - `test_iterator_is_a_lazy_generator` (`examples/03-three-way-split/tests/test_dissolve.py:76`, 1 definition)
  - `test_protocol_is_structural_and_abc_is_nominal` (`examples/03-three-way-split/tests/test_disambiguate.py:183`, 1 definition)
  - `test_module_is_one_instance_for_every_importer` (`examples/03-three-way-split/tests/test_disambiguate.py:125`, 1 definition)
  - `test_null_object_is_an_optional_checked_by_mypy` (`examples/03-three-way-split/tests/test_dissolve.py:226`, 1 definition)
- Disposition: **kept**. five assumptions from the chapter's own sentences, with five split tests as witnesses chosen by section (the chapter names none).

### Slide 8: Three ways out (What 1994 assumed)

- Claim: each pattern dissolves, survives or needs disambiguating.
- Chapter: 03, "The three-way split: dissolve, survive, disambiguate" (`_docs/03-the-three-way-split.md`).
- `03-the-three-way-split.md:33`: `grep -nF -- 'The first question is about the name.' _docs/03-the-three-way-split.md`
- `03-the-three-way-split.md:35`: `grep -nF -- 'The second question is about the force.' _docs/03-the-three-way-split.md`
- `03-the-three-way-split.md:37`: `grep -nF -- 'And "dissolves" never means "forget it": the force remains' _docs/03-the-three-way-split.md`
- Witness tests, each defined once:
  - `test_strategy_slot_accepts_def_lambda_and_partial` (`examples/03-three-way-split/tests/test_dissolve.py:47`, 1 definition)
  - `test_undo_needs_a_command_object` (`examples/03-three-way-split/tests/test_survive.py:24`, 1 definition)
  - `test_the_two_decorators_are_independent` (`examples/03-three-way-split/tests/test_disambiguate.py:111`, 1 definition)
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 9: What dissolves (What 1994 assumed)

- Claim: the eleven Dissolves rows of the map.
- Chapter: 03, "The three-way split: dissolve, survive, disambiguate" (`_docs/03-the-three-way-split.md`).
- `03-the-three-way-split.md:41`: `grep -nF -- 'The first eleven rows of the table are the ones where a Python feature resolves the force without the structure.' _docs/03-the-three-way-split.md`
- Witness tests, each defined once:
  - `test_strategy_slot_accepts_def_lambda_and_partial` (`examples/03-three-way-split/tests/test_dissolve.py:47`, 1 definition)
  - `test_iterator_is_a_lazy_generator` (`examples/03-three-way-split/tests/test_dissolve.py:76`, 1 definition)
  - `test_a_class_is_already_a_factory_method` (`examples/03-three-way-split/tests/test_dissolve.py:68`, 1 definition)
  - `test_template_method_is_a_function_taking_hooks` (`examples/03-three-way-split/tests/test_dissolve.py:105`, 1 definition)
  - `test_builder_is_a_keyword_only_dataclass` (`examples/03-three-way-split/tests/test_dissolve.py:153`, 1 definition)
  - `test_prototype_is_replace` (`examples/03-three-way-split/tests/test_dissolve.py:166`, 1 definition)
  - `test_visitor_is_singledispatch_without_accept` (`examples/03-three-way-split/tests/test_dissolve.py:176`, 1 definition)
  - `test_null_object_is_an_optional_checked_by_mypy` (`examples/03-three-way-split/tests/test_dissolve.py:226`, 1 definition)
  - `test_value_object_is_a_frozen_dataclass` (`examples/03-three-way-split/tests/test_dissolve.py:242`, 1 definition)
  - `test_registry_is_init_subclass` (`examples/03-three-way-split/tests/test_dissolve.py:256`, 1 definition)
  - `test_every_document_kind_has_an_issuer` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py:57`, 1 definition)
- Disposition: **kept**. ten of the eleven rows have a `test_dissolve` witness; the If-chain dispatch row is witnessed by a chapter 31 test, named in the row table.

### Slide 10: What survives (What 1994 assumed)

- Claim: the fourteen Survives rows of the map.
- Chapter: 03, "The three-way split: dissolve, survive, disambiguate" (`_docs/03-the-three-way-split.md`).
- `03-the-three-way-split.md:79`: `grep -nF -- 'Patterns that survive' _docs/03-the-three-way-split.md`
- Witness tests, each defined once:
  - `test_the_transition_table_is_read_only` (`examples/14-state-and-finite-state-machines/tests/test_lifecycle.py:100`, 1 definition)
  - `test_undo_needs_a_command_object` (`examples/03-three-way-split/tests/test_survive.py:24`, 1 definition)
  - `test_mypy_rejects_a_kit_that_mixes_reference_types` (`examples/16-factory-method-and-abstract-factory/tests/test_static.py:176`, 1 definition)
  - `test_a_client_whose_shape_matches_needs_no_adapter` (`examples/19-adapter-facade-bridge/tests/test_adapter.py:17`, 1 definition)
  - `test_ship_books_each_carrier_through_one_call` (`examples/19-adapter-facade-bridge/tests/test_facade.py:13`, 1 definition)
  - `test_every_booking_kind_works_with_every_carrier` (`examples/19-adapter-facade-bridge/tests/test_bridge.py:15`, 1 definition)
  - `test_a_consignment_and_a_consolidation_answer_weight_the_same_way` (`examples/21-composite-and-flyweight/tests/test_composite.py:46`, 1 definition)
  - `test_the_weak_pool_drops_a_commodity_nobody_holds` (`examples/21-composite-and-flyweight/tests/test_flyweight.py:34`, 1 definition)
  - `test_one_failing_subscriber_does_not_stop_the_rest` (`examples/22-observer/tests/test_delivery.py:70`, 1 definition)
  - `test_the_mediator_releases_in_either_order` (`examples/23-mediator-and-chain-of-responsibility/tests/test_mediator.py:61`, 1 definition)
  - `test_the_first_stage_that_decides_wins` (`examples/23-mediator-and-chain-of-responsibility/tests/test_chain.py:69`, 1 definition)
  - `test_rollback_keeps_the_audit_trail` (`examples/25-visitor-memento-interpreter/tests/test_memento.py:50`, 1 definition)
  - `test_explain_writes_the_tariff_as_text` (`examples/25-visitor-memento-interpreter/tests/test_tariff.py:44`, 1 definition)
  - `test_writer_closes_and_discards_on_an_exception` (`examples/10-context-managers/tests/test_writer.py:66`, 1 definition)
- Disposition: **kept**. only Command has a witness in the split's own tests; every other row is witnessed in its own chapter's example, named in the row table.

### Slide 11: One name, two meanings (What 1994 assumed)

- Claim: the four Needs disambiguating rows of the map.
- Chapter: 03, "The three-way split: dissolve, survive, disambiguate" (`_docs/03-the-three-way-split.md`).
- `03-the-three-way-split.md:91`: `grep -nF -- 'Four names mean two things in Python.' _docs/03-the-three-way-split.md`
- Witness tests, each defined once:
  - `test_the_two_decorators_are_independent` (`examples/03-three-way-split/tests/test_disambiguate.py:111`, 1 definition)
  - `test_module_is_one_instance_for_every_importer` (`examples/03-three-way-split/tests/test_disambiguate.py:125`, 1 definition)
  - `test_proxy_forwards_only_missing_attributes` (`examples/03-three-way-split/tests/test_disambiguate.py:156`, 1 definition)
  - `test_protocol_is_structural_and_abc_is_nominal` (`examples/03-three-way-split/tests/test_disambiguate.py:183`, 1 definition)
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 12: Dissolved in code (What 1994 assumed)

- Claim: a rule is a Callable[[Consignment], Money] and quote takes any.
- Chapter: 03, "The three-way split: dissolve, survive, disambiguate" (`_docs/03-the-three-way-split.md`).
- `03-the-three-way-split.md:75`: `grep -nF -- 'The example shows the dissolved rows at their smallest. A pricing rule is a `Callable[[Consignment], Money]`, so `quote(consignment, rule)` accepts a `def`, a lambda or a `functools.partial` in the same slot and no `RateStrategy` interface exists.' _docs/03-the-three-way-split.md`
- Witness tests, each defined once:
  - `test_strategy_slot_accepts_def_lambda_and_partial` (`examples/03-three-way-split/tests/test_dissolve.py:47`, 1 definition)
- Code: `examples/03-three-way-split/src/three_way_split/dissolve.py` lines 35 to 48 (14 lines, longest 80 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 35, exact): `def flat_rate(consignment: Consignment) -> Money:`
  - Last line (48): `    return RateQuote(consignment.id, rule(consignment))`
  - Byte-exact with the source by construction (read with `sed -n '35,48p' examples/03-three-way-split/src/three_way_split/dissolve.py`); quoted byte-exact in `02-what-1994-assumed-and-python-dissolves.md` fence opening at line 44 (block lines 6 to 19).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 13: Names for assistants (What 1994 assumed)

- Claim: a pattern name tells a team and an assistant which decision was made.
- Chapter: 04, "Naming patterns for teams and AI assistants" (`_docs/04-naming-patterns-for-teams-and-ai.md`).
- `04-naming-patterns-for-teams-and-ai.md:24`: `grep -nF -- 'A pattern name is the shortest design review comment there is.' _docs/04-naming-patterns-for-teams-and-ai.md`
- `04-naming-patterns-for-teams-and-ai.md:36`: `grep -nF -- 'Pattern names are compressed claims.' _docs/04-naming-patterns-for-teams-and-ai.md`
- `04-naming-patterns-for-teams-and-ai.md:90`: `grep -nF -- 'State the bucket.' _docs/04-naming-patterns-for-teams-and-ai.md`
- `04-naming-patterns-for-teams-and-ai.md:86`: `grep -nF -- 'Telling an assistant to "use the Strategy pattern" leaves the mechanism open' _docs/04-naming-patterns-for-teams-and-ai.md`
- Witness: prose only (prose only: chapter 4 has no example); no test is claimed.
- Disposition: **kept**. prose only: four chapter sentences confirmed; chapter 4 has no example.

### Slide 14: divider (SOLID in Python)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 15: One reason to change (SOLID in Python)

- Claim: each change moves only the fields it feeds.
- Chapter: 05, "SRP, OCP, and LSP in Python" (`_docs/05-srp-ocp-lsp.md`).
- `05-srp-ocp-lsp.md:34`: `grep -nF -- 'Each request has a different author and a different test that ought to move.' _docs/05-srp-ocp-lsp.md`
- `05-srp-ocp-lsp.md:79`: `grep -nF -- 'Replacing the tariff changes `net` and `tax`. Replacing the `"SG"` tax rule changes `tax` alone. Replacing the audit sink changes no field' _docs/05-srp-ocp-lsp.md`
- `05-srp-ocp-lsp.md:81`: `grep -nF -- '`test_pricing_and_tax_run_alone` builds a `BaseRate` and a `percent` rule with no sink and no rule table' _docs/05-srp-ocp-lsp.md`
- Witness tests, each defined once:
  - `test_each_change_moves_only_the_fields_it_feeds` (`examples/05-srp-ocp-lsp/tests/test_srp.py:31`, 1 definition)
  - `test_pricing_and_tax_run_alone` (`examples/05-srp-ocp-lsp/tests/test_srp.py:77`, 1 definition)
  - `test_audit_receives_exactly_the_quote_returned` (`examples/05-srp-ocp-lsp/tests/test_srp.py:63`, 1 definition)
- Credits (each re-found in the chapter that makes them):
  - `05-srp-ocp-lsp.md:36`: `grep -nF -- 'Robert C. Martin states it as "a class should have only one reason to change" in *Agile Software Development: Principles, Patterns, and Practices* (2002)' _docs/05-srp-ocp-lsp.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 16: How a quote flows (SOLID in Python)

- Claim: figure 05.
- Chapter: 05, "SRP, OCP, and LSP in Python" (`_docs/05-srp-ocp-lsp.md`).
- Figure: `05-srp-ocp-lsp` (`diagrams/05-srp-ocp-lsp.svg`, PNG `presentation/png/05-srp-ocp-lsp.png` at width 1600). Included by `05-srp-ocp-lsp.md:26`.
  - Registry caption: "One quote, three responsibilities. Pricing sits behind the RateCalculator Protocol and hands its net to tax rules keyed by destination country; the finished quote goes to an audit callable. Each changes for its own reason, and one contract suite checks every calculator."
  - Arrow census: every arrow composed by code (planning census R). The SVG, spec and chapter are unchanged since the plan's base (`git diff --stat db8f3ce HEAD -- diagrams/05-* diagrams/specs/05-*` is empty); committed PNG equals a fresh render (`render-png.sh --check`: same).
- Disposition: **kept**. figure confirmed: every arrow composed by code, PNG equals a fresh render.

### Slide 17: Open to a new tax (SOLID in Python)

- Claim: a tax rule is added without editing quote.
- Chapter: 05, "SRP, OCP, and LSP in Python" (`_docs/05-srp-ocp-lsp.md`).
- `05-srp-ocp-lsp.md:111`: `grep -nF -- 'A new rule arrives as data.' _docs/05-srp-ocp-lsp.md`
- `05-srp-ocp-lsp.md:109`: `grep -nF -- '`TAX_RULES` is a read-only view over a dict, so no module can add to it by assignment.' _docs/05-srp-ocp-lsp.md`
- Witness tests, each defined once:
  - `test_a_new_tax_rule_is_added_without_editing_quote` (`examples/05-srp-ocp-lsp/tests/test_ocp.py:14`, 1 definition)
  - `test_default_tax_table_is_read_only` (`examples/05-srp-ocp-lsp/tests/test_ocp.py:31`, 1 definition)
- Code: `examples/05-srp-ocp-lsp/src/srp_ocp_lsp/tax.py` lines 23 to 28 (6 lines, longest 52 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 23, exact): `TAX_RULES: Mapping[str, TaxRule] = MappingProxyType(`
  - Last line (28): `)`
  - Byte-exact with the source by construction (read with `sed -n '23,28p' examples/05-srp-ocp-lsp/src/srp_ocp_lsp/tax.py`); quoted byte-exact in `05-srp-ocp-lsp.md` fence opening at line 89 (block lines 12 to 17).
- Credits (each re-found in the chapter that makes them):
  - `05-srp-ocp-lsp.md:85`: `grep -nF -- 'Bertrand Meyer introduced the open-closed principle in *Object-Oriented Software Construction*' _docs/05-srp-ocp-lsp.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 18: The rate contract (SOLID in Python)

- Claim: the contract is the docstring plus tests; mypy can't see a behavioural violation.
- Chapter: 05, "SRP, OCP, and LSP in Python" (`_docs/05-srp-ocp-lsp.md`).
- `05-srp-ocp-lsp.md:170`: `grep -nF -- 'With one calculator, the contract is a docstring and the calculator'"'"'s own tests.' _docs/05-srp-ocp-lsp.md`
- `05-srp-ocp-lsp.md:119`: `grep -nF -- 'Half of that rule is a type signature, and mypy checks it.' _docs/05-srp-ocp-lsp.md`
- `05-srp-ocp-lsp.md:154`: `grep -nF -- '`test_mypy_cannot_see_a_behavioural_violation` passes copies of both to `quote` and gets exit status 0 with empty output.' _docs/05-srp-ocp-lsp.md`
- Witness tests, each defined once:
  - `test_calculator_honours_the_rate_contract` (`examples/05-srp-ocp-lsp/tests/test_lsp.py:73`, 1 definition)
  - `test_contract_catches_a_strengthened_precondition` (`examples/05-srp-ocp-lsp/tests/test_lsp.py:77`, 1 definition)
  - `test_mypy_cannot_see_a_behavioural_violation` (`examples/05-srp-ocp-lsp/tests/test_lsp.py:254`, 1 definition)
- Code: `examples/05-srp-ocp-lsp/src/srp_ocp_lsp/pricing.py` lines 16 to 27 (12 lines, longest 87 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 16, exact): `class RateCalculator(Protocol):`
  - Last line (27): `    def price(self, consignment: Consignment, /) -> Money: ...`
  - Byte-exact with the source by construction (read with `sed -n '16,27p' examples/05-srp-ocp-lsp/src/srp_ocp_lsp/pricing.py`); quoted byte-exact in `05-srp-ocp-lsp.md` fence opening at line 42 (block lines 1 to 12).
- Credits (each re-found in the chapter that makes them):
  - `05-srp-ocp-lsp.md:117`: `grep -nF -- 'Barbara Liskov introduced the idea in her OOPSLA '"'"'87 keynote' _docs/05-srp-ocp-lsp.md`
  - `05-srp-ocp-lsp.md:117`: `grep -nF -- 'Liskov and Wing gave the behavioural definition in "A Behavioral Notion of Subtyping"' _docs/05-srp-ocp-lsp.md`
  - `05-srp-ocp-lsp.md:85`: `grep -nF -- 'Bertrand Meyer introduced the open-closed principle in *Object-Oriented Software Construction*' _docs/05-srp-ocp-lsp.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 19: Narrow roles (SOLID in Python)

- Claim: a narrow Protocol per role.
- Chapter: 06, "ISP, DIP, and dependency injection without a framework" (`_docs/06-isp-dip-and-di-without-a-framework.md`).
- `06-isp-dip-and-di-without-a-framework.md:47`: `grep -nF -- 'Each policy module declares the Protocol it needs.' _docs/06-isp-dip-and-di-without-a-framework.md`
- `06-isp-dip-and-di-without-a-framework.md:166`: `grep -nF -- 'If a fake has to stub a method its consumer never calls, ask for the narrower Protocol.' _docs/06-isp-dip-and-di-without-a-framework.md`
- Witness tests, each defined once:
  - `test_adapters_satisfy_every_role_without_naming_one` (`examples/06-isp-dip-and-di-without-a-framework/tests/test_isp.py:50`, 1 definition)
  - `test_a_fat_protocol_forces_fakes_to_stub_unused_methods` (`examples/06-isp-dip-and-di-without-a-framework/tests/test_isp.py:86`, 1 definition)
- Code: `examples/06-isp-dip-and-di-without-a-framework/src/isp_dip_di/booking.py` lines 12 to 17 (6 lines, longest 84 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 12, exact): `class BookingGateway(Protocol):`
  - Last line (17): `    def cancel(self, reference: str, /) -> None: ...`
  - Byte-exact with the source by construction (read with `sed -n '12,17p' examples/06-isp-dip-and-di-without-a-framework/src/isp_dip_di/booking.py`); quoted byte-exact in `06-isp-dip-and-di-without-a-framework.md` fence opening at line 49 (block lines 1 to 6).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 20: The composition root (SOLID in Python)

- Claim: one function wires the application.
- Chapter: 06, "ISP, DIP, and dependency injection without a framework" (`_docs/06-isp-dip-and-di-without-a-framework.md`).
- `06-isp-dip-and-di-without-a-framework.md:122`: `grep -nF -- 'Somewhere, a concrete adapter has to be named. The composition root is that place, and it is as close to the program'"'"'s entry point as it can be.' _docs/06-isp-dip-and-di-without-a-framework.md`
- `06-isp-dip-and-di-without-a-framework.md:122`: `grep -nF -- 'Mark Seemann describes the pattern in his post "Composition Root"' _docs/06-isp-dip-and-di-without-a-framework.md`
- `06-isp-dip-and-di-without-a-framework.md:106`: `grep -nF -- 'The word "injection" for handing a collaborator to the code that uses it comes from Martin Fowler'"'"'s January 2004 article' _docs/06-isp-dip-and-di-without-a-framework.md`
- Witness tests, each defined once:
  - `test_build_app_shares_one_gateway_between_booking_and_tracking` (`examples/06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py:32`, 1 definition)
  - `test_composition_root_accepts_a_substitute_without_patching` (`examples/06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py:71`, 1 definition)
  - `test_policy_modules_do_not_import_the_adapters` (`examples/06-isp-dip-and-di-without-a-framework/tests/test_dip.py:87`, 1 definition)
- Code: `examples/06-isp-dip-and-di-without-a-framework/src/isp_dip_di/app.py` lines 32 to 45 (14 lines, longest 91 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 32, exact): `def build_app(`
  - Last line (45): `    return App(BookingService(gateway, audit), partial(tracking_history, gateway=gateway))`
  - Byte-exact with the source by construction (read with `sed -n '32,45p' examples/06-isp-dip-and-di-without-a-framework/src/isp_dip_di/app.py`); quoted byte-exact in `06-isp-dip-and-di-without-a-framework.md` fence opening at line 124 (block lines 1 to 14).
- Credits (each re-found in the chapter that makes them):
  - `06-isp-dip-and-di-without-a-framework.md:240`: `grep -nF -- https://martinfowler.com/articles/injection.html _docs/06-isp-dip-and-di-without-a-framework.md`
  - `06-isp-dip-and-di-without-a-framework.md:240`: `grep -nF -- https://blog.ploeh.dk/2011/07/28/CompositionRoot/ _docs/06-isp-dip-and-di-without-a-framework.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 21: Wiring the application (SOLID in Python)

- Claim: figure 06.
- Chapter: 06, "ISP, DIP, and dependency injection without a framework" (`_docs/06-isp-dip-and-di-without-a-framework.md`).
- Figure: `06-isp-dip-and-di-without-a-framework` (`diagrams/06-isp-dip-and-di-without-a-framework.svg`, PNG `presentation/png/06-isp-dip-and-di-without-a-framework.png` at width 1600). Included by `06-isp-dip-and-di-without-a-framework.md:26`.
  - Registry caption: "Dependency injection without a framework. The composition root builds one carrier adapter and passes it to each consumer, which names only the small Protocol it needs; the adapter satisfies both Protocols structurally and imports neither."
  - Arrow census: every arrow composed by code (planning census R). The SVG, spec and chapter are unchanged since the plan's base (`git diff --stat db8f3ce HEAD -- diagrams/06-* diagrams/specs/06-*` is empty); committed PNG equals a fresh render (`render-png.sh --check`: same).
- Disposition: **kept**. figure confirmed: every arrow composed by code, PNG equals a fresh render.

### Slide 22: Principles beyond SOLID (SOLID in Python)

- Claim: Appendix F's principles and their witnesses.
- Chapter: 46, "Programming principles reviewed in code" (`_docs/46-appendix-f-programming-principles.md`).
- `46-appendix-f-programming-principles.md:52`: `grep -nF -- 'Brandon Rhodes'"'"'s [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:109`: `grep -nF -- '**DRY.** *The Pragmatic Programmer* is the source' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:111`: `grep -nF -- '**YAGNI.** Fowler'"'"'s [Yagni](https://martinfowler.com/bliki/Yagni.html)' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:113`: `grep -nF -- '**Simple design.** Fowler'"'"'s [Beck Design Rules]' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:117`: `grep -nF -- 'In the bridge, the booking kind and the carrier vary on separate axes.' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:121`: `grep -nF -- 'Jim Shore'"'"'s [Fail Fast](https://martinfowler.com/ieeeSoftware/failFast.pdf)' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:127`: `grep -nF -- 'The Python glossary defines the style:' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:136`: `grep -nF -- 'The Demeter project at Northeastern University hosts the rule.' _docs/46-appendix-f-programming-principles.md`
- Witness tests, each defined once:
  - `test_a_class_adapter_still_exposes_the_clients_own_methods` (`examples/19-adapter-facade-bridge/tests/test_adapter.py:41`, 1 definition)
  - `test_the_fuel_surcharge_lives_in_one_definition_of_the_function` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py:122`, 1 definition)
  - `test_the_engine_needs_more_classes_functions_and_lines_than_the_function` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py:115`, 1 definition)
  - `test_one_engine_quote_makes_more_python_calls_than_the_function` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py:135`, 1 definition)
  - `test_a_new_booking_kind_needs_no_gateway_change` (`examples/19-adapter-facade-bridge/tests/test_bridge.py:98`, 1 definition)
  - `test_unknown_carrier_fails_at_the_composition_root` (`examples/06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py:85`, 1 definition)
  - `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py:74`, 1 definition)
  - `test_each_reader_names_the_attributes_it_depends_on` (`examples/46-appendix-f-programming-principles/tests/test_demeter.py:59`, 1 definition)
- Credits (each re-found in the chapter that makes them):
  - `46-appendix-f-programming-principles.md:52, 206`: `grep -nF -- https://python-patterns.guide/gang-of-four/composition-over-inheritance/ _docs/46-appendix-f-programming-principles.md`
  - `46-appendix-f-programming-principles.md:109, 206`: `grep -nF -- https://pragprog.com/tips/ _docs/46-appendix-f-programming-principles.md`
  - `46-appendix-f-programming-principles.md:111, 206`: `grep -nF -- https://martinfowler.com/bliki/Yagni.html _docs/46-appendix-f-programming-principles.md`
  - `46-appendix-f-programming-principles.md:113, 206`: `grep -nF -- https://martinfowler.com/bliki/BeckDesignRules.html _docs/46-appendix-f-programming-principles.md`
  - `46-appendix-f-programming-principles.md:121, 206`: `grep -nF -- https://martinfowler.com/ieeeSoftware/failFast.pdf _docs/46-appendix-f-programming-principles.md`
  - `46-appendix-f-programming-principles.md:206`: `grep -nF -- https://docs.python.org/3/glossary.html _docs/46-appendix-f-programming-principles.md`
  - `46-appendix-f-programming-principles.md:136, 206`: `grep -nF -- https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html _docs/46-appendix-f-programming-principles.md`
- Disposition: **reworded**. Appendix F's table at 46.md:34-38 is SOLID only, and slides 15 to 20 already carry it. The principles beyond SOLID have no table in the chapter, so the slide table is built from the chapter's own sections (eight rows, one witness each), and the claim reads "the principles Appendix F tests beyond SOLID"..

### Slide 23: Ask the shipment (SOLID in Python)

- Claim: the reader asks the shipment for the amount due.
- Chapter: 46, "Programming principles reviewed in code" (`_docs/46-appendix-f-programming-principles.md`).
- `46-appendix-f-programming-principles.md:140`: `grep -nF -- 'The member `examples/46-appendix-f-programming-principles` puts one question to the rule: who answers for the amount due?' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:140`: `grep -nF -- 'The reader the package ships asks the shipment.' _docs/46-appendix-f-programming-principles.md`
- `46-appendix-f-programming-principles.md:169`: `grep -nF -- '`test_both_readers_give_the_same_line_without_credits` runs both readers' _docs/46-appendix-f-programming-principles.md`
- Witness tests, each defined once:
  - `test_a_credit_reaches_only_the_reader_that_asks_the_shipment` (`examples/46-appendix-f-programming-principles/tests/test_demeter.py:45`, 1 definition)
  - `test_both_readers_give_the_same_line_without_credits` (`examples/46-appendix-f-programming-principles/tests/test_demeter.py:31`, 1 definition)
- Code: `examples/46-appendix-f-programming-principles/src/principles_reviewed/billing.py` lines 40 to 44 (5 lines, longest 37 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 40, exact): `    def amount_due(self) -> Money:`
  - Last line (44): `        return due`
  - Byte-exact with the source by construction (read with `sed -n '40,44p' examples/46-appendix-f-programming-principles/src/principles_reviewed/billing.py`); quoted byte-exact in `46-appendix-f-programming-principles.md` fence opening at line 143 (block lines 1 to 5).
- Credits (each re-found in the chapter that makes them):
  - `46-appendix-f-programming-principles.md:136, 206`: `grep -nF -- https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html _docs/46-appendix-f-programming-principles.md`
  - `46-appendix-f-programming-principles.md:136, 206`: `grep -nF -- https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/object-formulation.html _docs/46-appendix-f-programming-principles.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 24: divider (Selecting and varying behaviour)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 25: Strategy as a callable (Selecting and varying behaviour)

- Claim: Strategy dissolves into a callable.
- Chapter: 12, "Strategy: the callable" (`_docs/12-strategy-the-callable.md`).
- `12-strategy-the-callable.md:34`: `grep -nF -- 'This pattern dissolves, because a feature resolves the force without the pattern'"'"'s structure.' _docs/12-strategy-the-callable.md`
- `12-strategy-the-callable.md:184`: `grep -nF -- 'A single rule called from one place is a function, with no registry.' _docs/12-strategy-the-callable.md`
- Witness tests, each defined once:
  - `test_a_class_per_strategy_passes_the_same_table` (`examples/12-strategy-the-callable/tests/test_behaviour_table.py:67`, 1 definition)
  - `test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one` (`examples/12-strategy-the-callable/tests/test_behaviour_table.py:86`, 1 definition)
- Code: `examples/12-strategy-the-callable/src/strategy_callable/rules.py` lines 50 to 56 (7 lines, longest 56 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 50, exact): `RATE_RULES: Mapping[str, PricingRule] = frozendict(`
  - Last line (56): `)`
  - Byte-exact with the source by construction (read with `sed -n '50,56p' examples/12-strategy-the-callable/src/strategy_callable/rules.py`); quoted byte-exact in `12-strategy-the-callable.md` fence opening at line 58 (block lines 1 to 7).
- Disposition: **kept**. package path fixed: `examples/12-strategy-the-callable/src/strategy_callable/rules.py`.

### Slide 26: Rules in a registry (Selecting and varying behaviour)

- Claim: figure 12.
- Chapter: 12, "Strategy: the callable" (`_docs/12-strategy-the-callable.md`).
- Figure: `12-strategy-the-callable` (`diagrams/12-strategy-the-callable.svg`, PNG `presentation/png/12-strategy-the-callable.png` at width 1600). Included by `12-strategy-the-callable.md:26`.
  - Registry caption: "One quote, three rules in a slot. The caller names a rule, the read-only RATE_RULES registry returns a callable, and quote records the name with the price, whether the rule is a function, a partial or a frozen dataclass."
  - Arrow census: every arrow composed by code (planning census R). The SVG, spec and chapter are unchanged since the plan's base (`git diff --stat db8f3ce HEAD -- diagrams/12-* diagrams/specs/12-*` is empty); committed PNG equals a fresh render (`render-png.sh --check`: same).
- Disposition: **kept**. figure confirmed: every arrow composed by code, PNG equals a fresh render.

### Slide 27: Hooks, not subclasses (Selecting and varying behaviour)

- Claim: Template Method straddles two buckets.
- Chapter: 13, "Template Method and the function alternative" (`_docs/13-template-method-and-the-function-alternative.md`).
- `13-template-method-and-the-function-alternative.md:36`: `grep -nF -- 'The pattern straddles two buckets.' _docs/13-template-method-and-the-function-alternative.md`
- `13-template-method-and-the-function-alternative.md:214`: `grep -nF -- 'Write a function when there is one variant.' _docs/13-template-method-and-the-function-alternative.md`
- Witness tests, each defined once:
  - `test_declare_customs_runs_its_steps_in_order` (`examples/13-template-method-and-the-function-alternative/tests/test_hooks.py:32`, 1 definition)
  - `test_a_hook_left_out_takes_its_default` (`examples/13-template-method-and-the-function-alternative/tests/test_hooks.py:54`, 1 definition)
  - `test_a_required_hook_cannot_be_left_out` (`examples/13-template-method-and-the-function-alternative/tests/test_hooks.py:84`, 1 definition)
- Code: `examples/13-template-method-and-the-function-alternative/src/template_method/hooks.py` lines 28 to 35 (8 lines, longest 83 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 28, exact): `@dataclass(frozen=True, slots=True, kw_only=True)`
  - Last line (35): `    extra_documents: DocumentRule = no_extra_documents`
  - Byte-exact with the source by construction (read with `sed -n '28,35p' examples/13-template-method-and-the-function-alternative/src/template_method/hooks.py`); quoted byte-exact in `13-template-method-and-the-function-alternative.md` fence opening at line 46 (block lines 1 to 8).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 28: State as a table (Selecting and varying behaviour)

- Claim: State survives and the transition table is the design.
- Chapter: 14, "State and finite state machines" (`_docs/14-state-and-finite-state-machines.md`).
- `14-state-and-finite-state-machines.md:34`: `grep -nF -- 'For State it doesn'"'"'t. The force is that the legal transitions are a business rule that has to be written in one place and checked.' _docs/14-state-and-finite-state-machines.md`
- `14-state-and-finite-state-machines.md:200`: `grep -nF -- 'A two-state flag is a `bool`.' _docs/14-state-and-finite-state-machines.md`
- Witness tests, each defined once:
  - `test_state_objects_pass_the_same_lifecycle_table` (`examples/14-state-and-finite-state-machines/tests/test_state_objects.py:91`, 1 definition)
  - `test_an_illegal_event_is_a_transition_error` (`examples/14-state-and-finite-state-machines/tests/test_lifecycle.py:46`, 1 definition)
  - `test_the_transition_table_is_read_only` (`examples/14-state-and-finite-state-machines/tests/test_lifecycle.py:100`, 1 definition)
- Code: `examples/14-state-and-finite-state-machines/src/state_machines/table.py` lines 7 to 14 (8 lines, longest 93 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 7, exact): `TRANSITIONS: Mapping[tuple[ConsignmentStatus, HandlingKind], ConsignmentStatus] = frozendict(`
  - Last line (14): `)`
  - Byte-exact with the source by construction (read with `sed -n '7,14p' examples/14-state-and-finite-state-machines/src/state_machines/table.py`); quoted byte-exact in `14-state-and-finite-state-machines.md` fence opening at line 44 (block lines 1 to 8).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 29: Command with undo (Selecting and varying behaviour)

- Claim: Command survives, with the deferred call dissolving.
- Chapter: 15, "Command, undo, and command queues" (`_docs/15-command-undo-and-command-queues.md`).
- `15-command-undo-and-command-queues.md:42`: `grep -nF -- 'So the bucket is survives, with the deferred call dissolving.' _docs/15-command-undo-and-command-queues.md`
- `15-command-undo-and-command-queues.md:36`: `grep -nF -- 'The force is that a change needs an identity of its own.' _docs/15-command-undo-and-command-queues.md`
- `15-command-undo-and-command-queues.md:220`: `grep -nF -- 'Call the function when a change is never undone or queued.' _docs/15-command-undo-and-command-queues.md`
- Witness tests, each defined once:
  - `test_apply_returns_the_amendment_that_reverses_it` (`examples/15-command-undo-and-command-queues/tests/test_commands.py:23`, 1 definition)
  - `test_a_failing_batch_leaves_the_booking_unchanged` (`examples/15-command-undo-and-command-queues/tests/test_queue.py:33`, 1 definition)
  - `test_amendments_compare_by_value_and_partials_do_not` (`examples/15-command-undo-and-command-queues/tests/test_commands.py:13`, 1 definition)
- Code: `examples/15-command-undo-and-command-queues/src/command_undo/booking.py` lines 25 to 34 (10 lines, longest 71 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 25, exact): `    def amend(self, amendment: Amendment) -> None:`
  - Last line (34): `        self.redo_stack.append(redo)`
  - Byte-exact with the source by construction (read with `sed -n '25,34p' examples/15-command-undo-and-command-queues/src/command_undo/booking.py`); quoted byte-exact in `15-command-undo-and-command-queues.md` fence opening at line 114 (block lines 16 to 25).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 30: divider (Creating objects under control)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 31: Factories in a dict (Creating objects under control)

- Claim: Factory Method dissolves into a registry.
- Chapter: 16, "Factory Method and Abstract Factory" (`_docs/16-factory-method-and-abstract-factory.md`).
- `16-factory-method-and-abstract-factory.md:38`: `grep -nF -- 'The creator subclass becomes a value in a slot.' _docs/16-factory-method-and-abstract-factory.md`
- `16-factory-method-and-abstract-factory.md:34`: `grep -nF -- '## Factory Method dissolves' _docs/16-factory-method-and-abstract-factory.md`
- Witness tests, each defined once:
  - `test_a_registered_constructor_builds_each_carrier_gateway` (`examples/16-factory-method-and-abstract-factory/tests/test_factory_method.py:57`, 1 definition)
  - `test_the_creator_design_declares_three_classes_where_the_registry_declares_none` (`examples/16-factory-method-and-abstract-factory/tests/test_factory_method.py:124`, 1 definition)
  - `test_an_unknown_carrier_code_is_an_unknown_carrier_error` (`examples/16-factory-method-and-abstract-factory/tests/test_factory_method.py:102`, 1 definition)
- Code: `examples/16-factory-method-and-abstract-factory/src/factories/factories.py` lines 8 to 15 (8 lines, longest 70 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 8, exact): `type GatewayFactory = Callable[[CarrierSettings], CarrierGateway[str]]`
  - Last line (15): `)`
  - Byte-exact with the source by construction (read with `sed -n '8,15p' examples/16-factory-method-and-abstract-factory/src/factories/factories.py`); quoted byte-exact in `16-factory-method-and-abstract-factory.md` fence opening at line 41 (block lines 1 to 8).
- Credits (each re-found in the chapter that makes them):
  - `16-factory-method-and-abstract-factory.md:38, 294`: `grep -nF -- https://python-patterns.guide/gang-of-four/factory-method/ _docs/16-factory-method-and-abstract-factory.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 32: A family of gateways (Creating objects under control)

- Claim: Abstract Factory survives as a kit.
- Chapter: 16, "Factory Method and Abstract Factory" (`_docs/16-factory-method-and-abstract-factory.md`).
- `16-factory-method-and-abstract-factory.md:130`: `grep -nF -- 'The bucket is survives.' _docs/16-factory-method-and-abstract-factory.md`
- `16-factory-method-and-abstract-factory.md:130`: `grep -nF -- 'The force is that products must come from the same family, and a language that stores callables doesn'"'"'t choose the family.' _docs/16-factory-method-and-abstract-factory.md`
- `16-factory-method-and-abstract-factory.md:189`: `grep -nF -- 'If the products don'"'"'t have to match, pass them separately.' _docs/16-factory-method-and-abstract-factory.md`
- Witness tests, each defined once:
  - `test_each_kit_ships_with_its_own_carriers_products` (`examples/16-factory-method-and-abstract-factory/tests/test_kits.py:16`, 1 definition)
  - `test_every_kit_is_a_frozen_value` (`examples/16-factory-method-and-abstract-factory/tests/test_kits.py:37`, 1 definition)
  - `test_mypy_rejects_a_kit_that_mixes_reference_types` (`examples/16-factory-method-and-abstract-factory/tests/test_static.py:176`, 1 definition)
- Code: `examples/16-factory-method-and-abstract-factory/src/factories/kits.py` lines 49 to 60 (12 lines, longest 88 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 49, exact): `FASTLINE_KIT = CarrierKit(`
  - Last line (60): `KITS: Mapping[str, Shipper] = frozendict({"FASTLINE": FASTLINE_KIT, "AIRCO": AIRCO_KIT})`
  - Byte-exact with the source by construction (read with `sed -n '49,60p' examples/16-factory-method-and-abstract-factory/src/factories/kits.py`); quoted byte-exact in `16-factory-method-and-abstract-factory.md` fence opening at line 153 (block lines 1 to 12).
- Credits (each re-found in the chapter that makes them):
  - `16-factory-method-and-abstract-factory.md:132, 294`: `grep -nF -- https://python-patterns.guide/gang-of-four/abstract-factory/ _docs/16-factory-method-and-abstract-factory.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 33: Builder as a dataclass (Creating objects under control)

- Claim: Builder dissolves into a keyword-only dataclass.
- Chapter: 17, "Builder, dataclasses, and Prototype" (`_docs/17-builder-dataclasses-and-prototype.md`).
- `17-builder-dataclasses-and-prototype.md:36`: `grep -nF -- 'so the bucket is dissolves' _docs/17-builder-dataclasses-and-prototype.md`
- `17-builder-dataclasses-and-prototype.md:130`: `grep -nF -- 'That dissolves too.' _docs/17-builder-dataclasses-and-prototype.md`
- `17-builder-dataclasses-and-prototype.md:199`: `grep -nF -- 'A value with three fields doesn'"'"'t need this treatment' _docs/17-builder-dataclasses-and-prototype.md`
- Witness tests, each defined once:
  - `test_both_constructors_pass_the_booking_table` (`examples/17-builder-dataclasses-and-prototype/tests/test_builder.py:29`, 1 definition)
  - `test_a_positional_constructor_accepts_a_swapped_origin_and_destination` (`examples/17-builder-dataclasses-and-prototype/tests/test_builder.py:17`, 1 definition)
  - `test_a_template_and_replace_give_a_new_request` (`examples/17-builder-dataclasses-and-prototype/tests/test_prototype.py:33`, 1 definition)
- Code: `examples/17-builder-dataclasses-and-prototype/src/builder_prototype/booking.py` lines 14 to 23 (10 lines, longest 78 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 14, exact): `@dataclass(frozen=True, slots=True, kw_only=True)`
  - Last line (23): `    service: ServiceLevel = "standard"`
  - Byte-exact with the source by construction (read with `sed -n '14,23p' examples/17-builder-dataclasses-and-prototype/src/builder_prototype/booking.py`); quoted byte-exact in `17-builder-dataclasses-and-prototype.md` fence opening at line 79 (block lines 1 to 10).
- Credits (each re-found in the chapter that makes them):
  - `17-builder-dataclasses-and-prototype.md:36, 321`: `grep -nF -- https://python-patterns.guide/gang-of-four/builder/ _docs/17-builder-dataclasses-and-prototype.md`
  - `17-builder-dataclasses-and-prototype.md:130, 321`: `grep -nF -- https://python-patterns.guide/gang-of-four/prototype/ _docs/17-builder-dataclasses-and-prototype.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 34: Singleton as a module (Creating objects under control)

- Claim: Singleton as a module.
- Chapter: 18, "Singleton: module, Borg, and metaclass" (`_docs/18-singleton-module-borg-metaclass.md`).
- `18-singleton-module-borg-metaclass.md:41`: `grep -nF -- 'The bucket is needs disambiguating, and the default answer to the force, "load this once and let everyone read it", is the first meaning: a module.' _docs/18-singleton-module-borg-metaclass.md`
- `18-singleton-module-borg-metaclass.md:193`: `grep -nF -- 'A class whose only reason to exist is to be single is a module.' _docs/18-singleton-module-borg-metaclass.md`
- Witness tests, each defined once:
  - `test_every_form_gives_each_caller_the_same_rates` (`examples/18-singleton-module-borg-metaclass/tests/test_variants.py:10`, 1 definition)
  - `test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check` (`examples/18-singleton-module-borg-metaclass/tests/test_once.py:95`, 1 definition)
- Code: `examples/18-singleton-module-borg-metaclass/src/singleton/quoting.py` lines 3 to 16 (14 lines, longest 76 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 3, exact): `from decimal import Decimal`
  - Last line (16): `    return quote(zone, kilograms, table=tariff_table.TARIFF)`
  - Byte-exact with the source by construction (read with `sed -n '3,16p' examples/18-singleton-module-borg-metaclass/src/singleton/quoting.py`); quoted byte-exact in `18-singleton-module-borg-metaclass.md` fence opening at line 51 (block lines 1 to 14).
- Credits (each re-found in the chapter that makes them):
  - `18-singleton-module-borg-metaclass.md:35, 293`: `grep -nF -- https://python-patterns.guide/gang-of-four/singleton/ _docs/18-singleton-module-borg-metaclass.md`
  - `18-singleton-module-borg-metaclass.md:37, 293`: `grep -nF -- https://python-patterns.guide/python/module-globals/ _docs/18-singleton-module-borg-metaclass.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 35: divider (Composing and adapting structure)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 36: Adapter, Facade and Bridge (Composing and adapting structure)

- Claim: Adapter, Facade and Bridge all survive.
- Chapter: 19, "Adapter, Facade, and Bridge" (`_docs/19-adapter-facade-bridge.md`).
- `19-adapter-facade-bridge.md:36`: `grep -nF -- 'All three patterns in this chapter survive.' _docs/19-adapter-facade-bridge.md`
- `19-adapter-facade-bridge.md:50`: `grep -nF -- 'So duck typing removes an adapter where the shapes already match, and the type checker says where they don'"'"'t.' _docs/19-adapter-facade-bridge.md`
- `19-adapter-facade-bridge.md:136`: `grep -nF -- 'The *Design Patterns* catalogue gives Facade to a subsystem with many parts and a caller that wants a few operations.' _docs/19-adapter-facade-bridge.md`
- `19-adapter-facade-bridge.md:166`: `grep -nF -- 'Gamma, Helm, Johnson and Vlissides give Bridge to a design with two things that vary' _docs/19-adapter-facade-bridge.md`
- `19-adapter-facade-bridge.md:221`: `grep -nF -- 'Call the client when there'"'"'s one carrier and the SDK already fits.' _docs/19-adapter-facade-bridge.md`
- Witness tests, each defined once:
  - `test_a_client_whose_shape_matches_needs_no_adapter` (`examples/19-adapter-facade-bridge/tests/test_adapter.py:17`, 1 definition)
  - `test_mypy_rejects_a_client_with_a_different_shape` (`examples/19-adapter-facade-bridge/tests/test_static.py:100`, 1 definition)
  - `test_ship_books_each_carrier_through_one_call` (`examples/19-adapter-facade-bridge/tests/test_facade.py:13`, 1 definition)
  - `test_a_carrier_rejection_becomes_a_carrier_error` (`examples/19-adapter-facade-bridge/tests/test_facade.py:49`, 1 definition)
- Credits (each re-found in the chapter that makes them):
  - `19-adapter-facade-bridge.md:166, 344`: `grep -nF -- https://python-patterns.guide/gang-of-four/composition-over-inheritance/ _docs/19-adapter-facade-bridge.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 37: A bridge over a Protocol (Composing and adapting structure)

- Claim: N+M against N×M.
- Chapter: 19, "Adapter, Facade, and Bridge" (`_docs/19-adapter-facade-bridge.md`).
- `19-adapter-facade-bridge.md:203`: `grep -nF -- 'That'"'"'s N×M against N+M.' _docs/19-adapter-facade-bridge.md`
- `19-adapter-facade-bridge.md:209`: `grep -nF -- 'The cost sits on the implementor, and the benefit sits on the abstraction.' _docs/19-adapter-facade-bridge.md`
- Witness tests, each defined once:
  - `test_every_booking_kind_works_with_every_carrier` (`examples/19-adapter-facade-bridge/tests/test_bridge.py:15`, 1 definition)
  - `test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier` (`examples/19-adapter-facade-bridge/tests/test_bridge.py:36`, 1 definition)
  - `test_a_new_booking_kind_needs_no_gateway_change` (`examples/19-adapter-facade-bridge/tests/test_bridge.py:98`, 1 definition)
- Code: `examples/19-adapter-facade-bridge/src/adapter_facade_bridge/bookings.py` lines 9 to 17 (9 lines, longest 73 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 9, exact): `@dataclass(frozen=True, slots=True)`
  - Last line (17): `        return Booking(carrier, reference)`
  - Byte-exact with the source by construction (read with `sed -n '9,17p' examples/19-adapter-facade-bridge/src/adapter_facade_bridge/bookings.py`); quoted byte-exact in `19-adapter-facade-bridge.md` fence opening at line 171 (block lines 1 to 9).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 38: One call, two axes (Composing and adapting structure)

- Claim: figure 19.
- Chapter: 19, "Adapter, Facade, and Bridge" (`_docs/19-adapter-facade-bridge.md`).
- Figure: `19-adapter-facade-bridge` (`diagrams/19-adapter-facade-bridge.svg`, PNG `presentation/png/19-adapter-facade-bridge.png` at width 1600). Included by `19-adapter-facade-bridge.md:30`.
  - Registry caption: "One call, two axes, one translation. The facade picks a gateway and a booking kind; each kind works through the narrow gateway Protocol, which one client already satisfies and the other reaches through an adapter that converts units."
  - Arrow census: every arrow composed by code (planning census R). The SVG, spec and chapter are unchanged since the plan's base (`git diff --stat db8f3ce HEAD -- diagrams/19-* diagrams/specs/19-*` is empty); committed PNG equals a fresh render (`render-png.sh --check`: same).
- Disposition: **kept**. figure confirmed: every arrow composed by code, PNG equals a fresh render.

### Slide 39: Two things called Decorator (Composing and adapting structure)

- Claim: the pattern and the syntax share a name.
- Chapter: 20, "Decorator the pattern vs @decorator the syntax, and Proxy" (`_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`).
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:37`: `grep -nF -- 'The pattern builds a value: `Tax(Surcharge(BaseRate(...), fee), percent)`. The syntax rebinds a name:' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:43`: `grep -nF -- 'In this chapter, "Decorator" alone is the pattern.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:41`: `grep -nF -- 'The major one is that the name is not consistent with its use in the GoF book.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- Witness tests, each defined once:
  - `test_the_layers_for_a_consignment_are_chosen_while_the_program_runs` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_layers.py:98`, 1 definition)
  - `test_the_at_sign_rebinds_the_name_once_at_definition_time` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py:16`, 1 definition)
  - `test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py:129`, 1 definition)
  - `test_mypy_rejects_a_decorated_function_where_a_calculator_belongs` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_static.py:194`, 1 definition)
- Credits (each re-found in the chapter that makes them):
  - `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:337`: `grep -nF -- https://peps.python.org/pep-0318/ _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 40: Wrapper objects at run time (Composing and adapting structure)

- Claim: layers wrap a calculator and the order matters.
- Chapter: 20, "Decorator the pattern vs @decorator the syntax, and Proxy" (`_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`).
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:39`: `grep -nF -- 'gives the name Decorator to a wrapper object that holds another object and presents the same interface' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:76`: `grep -nF -- 'Order matters once a layer adds a fixed amount.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:200`: `grep -nF -- 'Skip the layer stack when the adjustment is one fixed step: a function does it' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- Witness tests, each defined once:
  - `test_a_layer_wraps_a_calculator_and_leaves_it_unchanged` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_layers.py:31`, 1 definition)
  - `test_layer_order_changes_the_price_when_a_fee_is_added` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_layers.py:54`, 1 definition)
  - `test_compose_wraps_the_last_layer_outermost` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_layers.py:155`, 1 definition)
- Code: `examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/src/decorator_proxy/layers.py` lines 45 to 53 (9 lines, longest 69 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 45, exact): `@dataclass(frozen=True, slots=True)`
  - Last line (53): `        return self.inner.price(consignment) + self.fee`
  - Byte-exact with the source by construction (read with `sed -n '45,53p' examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/src/decorator_proxy/layers.py`); quoted byte-exact in `20-decorator-pattern-vs-decorator-syntax-and-proxy.md` fence opening at line 50 (block lines 1 to 9).
- Credits (each re-found in the chapter that makes them):
  - `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:337`: `grep -nF -- https://python-patterns.guide/gang-of-four/decorator-pattern/ _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 41: A name rebound once (Composing and adapting structure)

- Claim: the @ form rebinds a name at definition time.
- Chapter: 20, "Decorator the pattern vs @decorator the syntax, and Proxy" (`_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`).
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:104`: `grep -nF -- 'The `@` form is a statement about a name.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:119`: `grep -nF -- 'Stacking order is fixed when the module loads.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:200`: `grep -nF -- 'Don'"'"'t put `@retry` around an operation that isn'"'"'t safe to repeat' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- Witness tests, each defined once:
  - `test_the_at_sign_rebinds_the_name_once_at_definition_time` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py:16`, 1 definition)
  - `test_syntax_stacking_order_decides_whether_each_attempt_is_audited` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py:88`, 1 definition)
  - `test_rebound_functions_do_not_compare_by_value` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py:118`, 1 definition)
- Code: `examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/src/decorator_proxy/syntax.py` lines 46 to 49 (4 lines, longest 85 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 46, exact): `@retry(attempts=3, on=(CarrierTimeoutError,))`
  - Last line (49): `    return gateway.quote(consignment)`
  - Byte-exact with the source by construction (read with `sed -n '46,49p' examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/src/decorator_proxy/syntax.py`); quoted byte-exact in `20-decorator-pattern-vs-decorator-syntax-and-proxy.md` fence opening at line 108 (block lines 1 to 4).
- Credits (each re-found in the chapter that makes them):
  - `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:337`: `grep -nF -- https://peps.python.org/pep-0318/ _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 42: A proxy keeps the interface (Composing and adapting structure)

- Claim: a proxy returns what the subject returns.
- Chapter: 20, "Decorator the pattern vs @decorator the syntax, and Proxy" (`_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`).
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:125`: `grep -nF -- '*Design Patterns* gives Proxy to a stand-in that sits in front of another object and decides whether, when and how the real one is reached.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:125`: `grep -nF -- 'a proxy returns what the subject returns' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`
- `03-the-three-way-split.md:72`: `grep -nF -- '| Proxy | Needs disambiguating | A surrogate object vs attribute interception' _docs/03-the-three-way-split.md`
- Witness tests, each defined once:
  - `test_the_proxy_asks_the_gateway_once_per_consignment` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_proxy.py:13`, 1 definition)
  - `test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_proxy.py:60`, 1 definition)
  - `test_mypy_reports_a_typo_on_the_explicit_proxy` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_static.py:240`, 1 definition)
  - `test_mypy_accepts_a_typo_through_a_forwarding_proxy` (`examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_static.py:257`, 1 definition)
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 43: One weight question (Composing and adapting structure)

- Claim: Composite and Flyweight survive.
- Chapter: 21, "Composite and Flyweight" (`_docs/21-composite-and-flyweight.md`).
- `21-composite-and-flyweight.md:39`: `grep -nF -- 'Composite is for the caller who holds something and asks one question without caring whether it'"'"'s a single item or a bundle of them.' _docs/21-composite-and-flyweight.md`
- `21-composite-and-flyweight.md:103`: `grep -nF -- 'The tree'"'"'s invariants are the part of Composite that no language feature supplies.' _docs/21-composite-and-flyweight.md`
- `21-composite-and-flyweight.md:134`: `grep -nF -- 'Flyweight is for many references to equal values.' _docs/21-composite-and-flyweight.md`
- Witness tests, each defined once:
  - `test_a_consignment_and_a_consolidation_answer_weight_the_same_way` (`examples/21-composite-and-flyweight/tests/test_composite.py:46`, 1 definition)
  - `test_a_flat_sum_misses_nested_consolidations` (`examples/21-composite-and-flyweight/tests/test_composite.py:33`, 1 definition)
  - `test_mypy_refuses_adding_to_a_frozen_consolidation` (`examples/21-composite-and-flyweight/tests/test_static.py:148`, 1 definition)
  - `test_the_weak_pool_drops_a_commodity_nobody_holds` (`examples/21-composite-and-flyweight/tests/test_flyweight.py:34`, 1 definition)
  - `test_split_port_codes_are_equal_but_distinct_objects` (`examples/21-composite-and-flyweight/tests/test_flyweight.py:109`, 1 definition)
- Code: `examples/21-composite-and-flyweight/src/composite_flyweight/consolidation.py` lines 8 to 16 (9 lines, longest 82 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 8, exact): `def consignments(shipment: Shipment) -> tuple[Consignment, ...]:`
  - Last line (16): `            assert_never(unreachable)`
  - Byte-exact with the source by construction (read with `sed -n '8,16p' examples/21-composite-and-flyweight/src/composite_flyweight/consolidation.py`); quoted byte-exact in `21-composite-and-flyweight.md` fence opening at line 84 (block lines 1 to 9).
- Credits (each re-found in the chapter that makes them):
  - `21-composite-and-flyweight.md:39, 361`: `grep -nF -- https://python-patterns.guide/gang-of-four/composite/ _docs/21-composite-and-flyweight.md`
  - `21-composite-and-flyweight.md:136, 361`: `grep -nF -- https://python-patterns.guide/gang-of-four/flyweight/ _docs/21-composite-and-flyweight.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 44: Shared commodities (Composing and adapting structure)

- Claim: figure 21.
- Chapter: 21, "Composite and Flyweight" (`_docs/21-composite-and-flyweight.md`).
- Figure: `21-composite-and-flyweight` (`diagrams/21-composite-and-flyweight.svg`, PNG `presentation/png/21-composite-and-flyweight.png` at width 1600). Included by `21-composite-and-flyweight.md:33`.
  - Registry caption: "One weight question, one shared commodity. A consolidation answers weight as a consignment does, summing its parts through nested groups; consignments reach a single frozen commodity per code from a pool that lets go of commodities nobody holds."
  - Arrow census: every arrow composed by code (planning census R). The SVG, spec and chapter are unchanged since the plan's base (`git diff --stat db8f3ce HEAD -- diagrams/21-* diagrams/specs/21-*` is empty); committed PNG equals a fresh render (`render-png.sh --check`: same).
- Disposition: **kept**. figure confirmed: every arrow composed by code, PNG equals a fresh render.

### Slide 45: divider (Coordinating and traversing)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 46: What a signal decides (Coordinating and traversing)

- Claim: Observer survives; a signal decides order, failure, re-entry and lifetime.
- Chapter: 22, "Observer" (`_docs/22-observer.md`).
- `22-observer.md:58`: `grep -nF -- 'The bucket is survives, as' _docs/22-observer.md`
- `22-observer.md:58`: `grep -nF -- 'A list of callables decides nothing about delivery order, failure, re-entry or lifetime, and `Signal` decides each.' _docs/22-observer.md`
- `22-observer.md:217`: `grep -nF -- 'Call the parties directly when the set is fixed at the time the subject is built.' _docs/22-observer.md`
- Witness tests, each defined once:
  - `test_subscribers_are_called_in_subscription_order` (`examples/22-observer/tests/test_delivery.py:20`, 1 definition)
  - `test_one_failing_subscriber_does_not_stop_the_rest` (`examples/22-observer/tests/test_delivery.py:70`, 1 definition)
  - `test_every_failure_is_reported_after_delivery` (`examples/22-observer/tests/test_delivery.py:106`, 1 definition)
  - `test_a_bound_method_subscriber_is_dropped_when_its_owner_goes` (`examples/22-observer/tests/test_lifetime.py:47`, 1 definition)
  - `test_an_event_published_during_delivery_waits_its_turn` (`examples/22-observer/tests/test_reentrancy.py:96`, 1 definition)
- Code: `examples/22-observer/src/observer/signal.py` lines 66 to 81 (16 lines, longest 67 characters, tabs 0, trailing whitespace 0, common indent 8).
  - Anchor (line 66, exact): `        errors: list[Exception] = []`
  - Last line (81): `            raise ExceptionGroup("subscribers failed", errors)`
  - Byte-exact with the source by construction (read with `sed -n '66,81p' examples/22-observer/src/observer/signal.py`); quoted byte-exact in `22-observer.md` fence opening at line 86 (block lines 11 to 26).
- Credits (each re-found in the chapter that makes them):
  - `22-observer.md:116, 327`: `grep -nF -- https://peps.python.org/pep-0654/ _docs/22-observer.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 47: A chain of stages (Coordinating and traversing)

- Claim: Chain of Responsibility survives; the link class goes.
- Chapter: 23, "Mediator and Chain of Responsibility" (`_docs/23-mediator-and-chain-of-responsibility.md`).
- `23-mediator-and-chain-of-responsibility.md:38`: `grep -nF -- 'The class that carries the successor link is the part Python removes.' _docs/23-mediator-and-chain-of-responsibility.md`
- `23-mediator-and-chain-of-responsibility.md:30`: `grep -nF -- 'Each is a decision, and both patterns survive because Python'"'"'s syntax doesn'"'"'t make those decisions for you.' _docs/23-mediator-and-chain-of-responsibility.md`
- `23-mediator-and-chain-of-responsibility.md:182`: `grep -nF -- 'With one check, call the function.' _docs/23-mediator-and-chain-of-responsibility.md`
- Witness tests, each defined once:
  - `test_the_first_stage_that_decides_wins` (`examples/23-mediator-and-chain-of-responsibility/tests/test_chain.py:69`, 1 definition)
  - `test_stages_after_a_decision_are_not_called` (`examples/23-mediator-and-chain-of-responsibility/tests/test_chain.py:87`, 1 definition)
  - `test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage` (`examples/23-mediator-and-chain-of-responsibility/tests/test_static.py:143`, 1 definition)
- Code: `examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/clearance.py` lines 65 to 68 (4 lines, longest 56 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 65, exact): `    for stage in stages:`
  - Last line (68): `    return final(declaration)`
  - Byte-exact with the source by construction (read with `sed -n '65,68p' examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/clearance.py`); quoted byte-exact in `23-mediator-and-chain-of-responsibility.md` fence opening at line 50 (block lines 9 to 12).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 48: One release rule (Coordinating and traversing)

- Claim: a mediator owns the release rule.
- Chapter: 23, "Mediator and Chain of Responsibility" (`_docs/23-mediator-and-chain-of-responsibility.md`).
- `23-mediator-and-chain-of-responsibility.md:127`: `grep -nF -- 'Mediator is for a group of parties whose actions depend on one another.' _docs/23-mediator-and-chain-of-responsibility.md`
- `23-mediator-and-chain-of-responsibility.md:166`: `grep -nF -- 'The choreography is the other form.' _docs/23-mediator-and-chain-of-responsibility.md`
- `23-mediator-and-chain-of-responsibility.md:178`: `grep -nF -- 'A mediator knows the messages its colleagues send and decides who acts next' _docs/23-mediator-and-chain-of-responsibility.md`
- Witness tests, each defined once:
  - `test_the_mediator_releases_in_either_order` (`examples/23-mediator-and-chain-of-responsibility/tests/test_mediator.py:61`, 1 definition)
  - `test_a_choreography_loses_a_settlement_that_arrives_before_inspection` (`examples/23-mediator-and-chain-of-responsibility/tests/test_mediator.py:75`, 1 definition)
  - `test_a_duplicate_settlement_releases_once` (`examples/23-mediator-and-chain-of-responsibility/tests/test_mediator.py:84`, 1 definition)
- Code: `examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/mediator.py` lines 64 to 74 (11 lines, longest 55 characters, tabs 0, trailing whitespace 0, common indent 8).
  - Anchor (line 64, exact): `        match message:`
  - Last line (74): `        self._try_release()`
  - Byte-exact with the source by construction (read with `sed -n '64,74p' examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/mediator.py`); quoted byte-exact in `23-mediator-and-chain-of-responsibility.md` fence opening at line 132 (block lines 7 to 17).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 49: Generators as iterators (Coordinating and traversing)

- Claim: the cursor class dissolves; three decisions remain.
- Chapter: 24, "Iterator: generators and the iterator protocol" (`_docs/24-iterator-generators-and-the-iterator-protocol.md`).
- `24-iterator-generators-and-the-iterator-protocol.md:30`: `grep -nF -- 'The cursor class dissolves, and those three decisions remain.' _docs/24-iterator-generators-and-the-iterator-protocol.md`
- `24-iterator-generators-and-the-iterator-protocol.md:47`: `grep -nF -- 'A function with `yield` is a generator function, and calling it returns a generator iterator.' _docs/24-iterator-generators-and-the-iterator-protocol.md`
- `24-iterator-generators-and-the-iterator-protocol.md:151`: `grep -nF -- 'Pass the tuple when the data is already in a list that callers index or measure.' _docs/24-iterator-generators-and-the-iterator-protocol.md`
- Witness tests, each defined once:
  - `test_a_tracking_history_can_be_walked_twice` (`examples/24-iterator-generators-and-the-iterator-protocol/tests/test_protocol.py:22`, 1 definition)
  - `test_a_self_iterating_history_is_empty_on_the_second_pass` (`examples/24-iterator-generators-and-the-iterator-protocol/tests/test_protocol.py:27`, 1 definition)
  - `test_the_first_page_reads_only_one_page` (`examples/24-iterator-generators-and-the-iterator-protocol/tests/test_laziness.py:20`, 1 definition)
  - `test_breaking_out_of_a_loop_leaves_a_named_reader_open` (`examples/24-iterator-generators-and-the-iterator-protocol/tests/test_reading.py:98`, 1 definition)
- Code: `examples/24-iterator-generators-and-the-iterator-protocol/src/iterator_protocol/domain.py` lines 30 to 43 (14 lines, longest 85 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 30, exact): `class TrackingHistory:`
  - Last line (43): `        yield from self._events`
  - Byte-exact with the source by construction (read with `sed -n '30,43p' examples/24-iterator-generators-and-the-iterator-protocol/src/iterator_protocol/domain.py`); not quoted as one block by `24-iterator-generators-and-the-iterator-protocol.md` (6 of 14 lines appear in its fences); the slide reads the source range.
- Credits (each re-found in the chapter that makes them):
  - `24-iterator-generators-and-the-iterator-protocol.md:276`: `grep -nF -- https://python-patterns.guide/gang-of-four/iterator/ _docs/24-iterator-generators-and-the-iterator-protocol.md`
  - `24-iterator-generators-and-the-iterator-protocol.md:276`: `grep -nF -- https://peps.python.org/pep-0255/ _docs/24-iterator-generators-and-the-iterator-protocol.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 50: Visitor as a match (Coordinating and traversing)

- Claim: Visitor dissolves into a match over a closed set.
- Chapter: 25, "Visitor, Memento, and Interpreter" (`_docs/25-visitor-memento-interpreter.md`).
- `25-visitor-memento-interpreter.md:36`: `grep -nF -- 'Visitor is for a fixed family of kinds that gets new operations over time.' _docs/25-visitor-memento-interpreter.md`
- `25-visitor-memento-interpreter.md:218`: `grep -nF -- 'With one operation over the kinds, write the `match` where it'"'"'s needed.' _docs/25-visitor-memento-interpreter.md`
- Witness tests, each defined once:
  - `test_mypy_reports_an_event_left_out_of_a_match` (`examples/25-visitor-memento-interpreter/tests/test_static.py:162`, 1 definition)
  - `test_status_after_maps_each_event_to_a_consignment_status` (`examples/25-visitor-memento-interpreter/tests/test_visitor.py:47`, 1 definition)
  - `test_every_visitor_form_describes_a_journey_the_same_way` (`examples/25-visitor-memento-interpreter/tests/test_visitor.py:30`, 1 definition)
- Code: `examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/events.py` lines 42 to 56 (15 lines, longest 72 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 42, exact): `def describe(event: HandlingEvent, /) -> str:`
  - Last line (56): `            assert_never(event)`
  - Byte-exact with the source by construction (read with `sed -n '42,56p' examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/events.py`); quoted byte-exact in `25-visitor-memento-interpreter.md` fence opening at line 38 (block lines 4 to 18).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 51: Snapshot and rollback (Coordinating and traversing)

- Claim: Memento survives: what to capture and what must not roll back.
- Chapter: 25, "Visitor, Memento, and Interpreter" (`_docs/25-visitor-memento-interpreter.md`).
- `25-visitor-memento-interpreter.md:105`: `grep -nF -- 'Memento is for putting an object back the way it was after a change fails' _docs/25-visitor-memento-interpreter.md`
- `25-visitor-memento-interpreter.md:138`: `grep -nF -- 'It leaves the audit out, because a record that an amendment was refused' _docs/25-visitor-memento-interpreter.md`
- Witness tests, each defined once:
  - `test_rollback_keeps_the_audit_trail` (`examples/25-visitor-memento-interpreter/tests/test_memento.py:50`, 1 definition)
  - `test_a_deepcopy_memento_erases_the_audit_trail_on_rollback` (`examples/25-visitor-memento-interpreter/tests/test_memento.py:79`, 1 definition)
  - `test_rollback_restores_the_attached_documents` (`examples/25-visitor-memento-interpreter/tests/test_memento.py:31`, 1 definition)
- Code: `examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/memento.py` lines 61 to 70 (10 lines, longest 80 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 61, exact): `@contextmanager`
  - Last line (70): `        raise`
  - Byte-exact with the source by construction (read with `sed -n '61,70p' examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/memento.py`); quoted byte-exact in `25-visitor-memento-interpreter.md` fence opening at line 108 (block lines 17 to 26).
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 52: A tariff, two readings (Coordinating and traversing)

- Claim: Interpreter survives: a grammar and its readings.
- Chapter: 25, "Visitor, Memento, and Interpreter" (`_docs/25-visitor-memento-interpreter.md`).
- `25-visitor-memento-interpreter.md:153`: `grep -nF -- 'Interpreter is for rules that people write down and the program must apply.' _docs/25-visitor-memento-interpreter.md`
- `25-visitor-memento-interpreter.md:153`: `grep -nF -- 'The classes stay in Python, as a small grammar of frozen nodes.' _docs/25-visitor-memento-interpreter.md`
- Witness tests, each defined once:
  - `test_explain_writes_the_tariff_as_text` (`examples/25-visitor-memento-interpreter/tests/test_tariff.py:44`, 1 definition)
  - `test_every_rule_form_prices_the_same_consignments` (`examples/25-visitor-memento-interpreter/tests/test_tariff.py:35`, 1 definition)
  - `test_mypy_reports_a_tariff_node_left_out_of_evaluate` (`examples/25-visitor-memento-interpreter/tests/test_static.py:194`, 1 definition)
- Code: `examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/tariff.py` lines 44 to 59 (16 lines, longest 84 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 44, exact): `def evaluate(expr: Expr, consignment: Consignment, /) -> Money:`
  - Last line (59): `            assert_never(expr)`
  - Byte-exact with the source by construction (read with `sed -n '44,59p' examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/tariff.py`); quoted byte-exact in `25-visitor-memento-interpreter.md` fence opening at line 156 (block lines 19 to 34).
- Credits (each re-found in the chapter that makes them):
  - `25-visitor-memento-interpreter.md:101, 338`: `grep -nF -- https://peps.python.org/pep-0634/ _docs/25-visitor-memento-interpreter.md`
  - `25-visitor-memento-interpreter.md:338`: `grep -nF -- https://peps.python.org/pep-0636/ _docs/25-visitor-memento-interpreter.md`
- Disposition: **kept**. claim, witness and excerpt confirmed.

### Slide 53: Match, snapshot, tariff tree (Coordinating and traversing)

- Claim: figure 25.
- Chapter: 25, "Visitor, Memento, and Interpreter" (`_docs/25-visitor-memento-interpreter.md`).
- Figure: `25-visitor-memento-interpreter` (`diagrams/25-visitor-memento-interpreter.svg`, PNG `presentation/png/25-visitor-memento-interpreter.png` at width 1600). Included by `25-visitor-memento-interpreter.md:30`.
  - Registry caption: "Each operation over the closed event union is one match, and mypy reports a kind it leaves out. A booking rolls back from a frozen snapshot that leaves the audit alone, and one tariff tree is both priced and explained."
  - Arrow census: every arrow composed by code (planning census R). The SVG, spec and chapter are unchanged since the plan's base (`git diff --stat db8f3ce HEAD -- diagrams/25-* diagrams/specs/25-*` is empty); committed PNG equals a fresh render (`render-png.sh --check`: same).
- Disposition: **kept**. figure confirmed: every arrow composed by code, PNG equals a fresh render.

### Slide 54: divider (Choosing well)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 55: When not to (Choosing well)

- Claim: when-not sentences quoted from the catalogue chapters.
- Disposition: **kept**. prose only: six sentences, each in its chapter's When-not section; the chapters give no test for them, and the notes say so.

### Slide 56: Pattern to force (Choosing well)

- Claim: Appendix E rows mapping to the catalogue chapters.
- Chapter: 45, "Pattern-to-force quick reference" (`_docs/45-appendix-e-pattern-to-force-reference.md`).
- Disposition: **kept**. ten rows chosen (the plan allows at most twelve).

### Slide 57: Prompting for a pattern (Choosing well)

- Claim: a catalogue chapter's sidebar prompt and review line, quoted.
- Chapter: 25, "Visitor, Memento, and Interpreter" (`_docs/25-visitor-memento-interpreter.md`).
- `25-visitor-memento-interpreter.md:221`: `grep -nF -- '**Specifying a visitor, a memento and an interpreter.**' _docs/25-visitor-memento-interpreter.md`
- `25-visitor-memento-interpreter.md:223`: `grep -nF -- '> Over the closed `HandlingEvent` union, write each operation as one function using `match`' _docs/25-visitor-memento-interpreter.md`
- `25-visitor-memento-interpreter.md:225`: `grep -nF -- 'If the reply adds an `accept` method or snapshots with `copy.copy`, ask for the test that fails.' _docs/25-visitor-memento-interpreter.md`
- Witness: prose only (prose only: the sidebar states no test of its own); no test is claimed.
- Disposition: **kept**. prose only: the sidebar's heading, nested prompt and review line are each found once; the sidebar states no test of its own.

### Slide 58: divider (Reference)

- Claim: -.
- Witness: none needed; a structural slide with no claim about the code. Notes cover what the inventory lists.
- Disposition: **kept**. structural slide.

### Slide 59: The toolchain (Reference)

- Claim: Appendix A and chapter 0 versions.
- Chapter: 00, "Prerequisites and the toolchain" (`_docs/00-prerequisites.md`).
- `00-prerequisites.md:33`: `grep -nF -- '| CPython | 3.15.2 | Interpreter, installed by uv |' _docs/00-prerequisites.md`
- `00-prerequisites.md:34`: `grep -nF -- '| uv | 0.13.7 | Interpreter, environment, lockfile |' _docs/00-prerequisites.md`
- `00-prerequisites.md:35`: `grep -nF -- '| pytest | 9.2.0 | Test runner |' _docs/00-prerequisites.md`
- `00-prerequisites.md:36`: `grep -nF -- '| pytest-mock | 3.17.0 |' _docs/00-prerequisites.md`
- `00-prerequisites.md:37`: `grep -nF -- '| ruff | 0.17.4 | Lint and format |' _docs/00-prerequisites.md`
- `00-prerequisites.md:38`: `grep -nF -- '| mypy | 2.4.1 | Static types, run with `--strict` |' _docs/00-prerequisites.md`
- Disposition: **kept**. six versions confirmed in chapter 0's table, root pyproject.toml and uv --version, and Appendix A.

### Slide 60: Sources credited (Reference)

- Claim: the online sources the 101 chapters cite.
- Disposition: **kept**. sources grouped as the chapters link them; text-only credits named.

### Slide 61: Reading further (Reference)

- Claim: the books the 101 chapters cite.
- Disposition: **reworded**. No 101 chapter cites Domain-Driven Design or Patterns of Enterprise Application Architecture (only chapters 8 and 30 do), so the two rows leave the list; ten books remain..

### Slide 62: Take it with you (Reference)

- Claim: the site, repository and hub URLs.
- Disposition: **reworded (proposed)**. site and repository URLs only; the hub URL is a cross-reference to a sibling site that CLAUDE.md bars from decks, and no reader-facing file names it. The owner decides.

## Map tables (slides 9, 10 and 11)

The map in `03-the-three-way-split.md` is one table, `| Pattern | Bucket | What Python gives you | Developed in |`, at lines 45 to 73. Cells are copied from the chapter with the link markup reduced to its text; a literal pipe inside a code span (the Null Object row) is kept. The deck table takes the Pattern and What Python gives you columns verbatim.

### Slide 9, what dissolves: 11 rows

| Line | Pattern | What Python gives you | Witness test |
| --- | --- | --- | --- |
| 03-the-three-way-split.md:45 | Strategy | A callable or `functools.partial` | `test_strategy_slot_accepts_def_lambda_and_partial` (`examples/03-three-way-split/tests/test_dissolve.py:47`, 1 definition) |
| 03-the-three-way-split.md:46 | Iterator | A generator or `__iter__` | `test_iterator_is_a_lazy_generator` (`examples/03-three-way-split/tests/test_dissolve.py:76`, 1 definition) |
| 03-the-three-way-split.md:47 | Factory Method | A class or function in a dict | `test_a_class_is_already_a_factory_method` (`examples/03-three-way-split/tests/test_dissolve.py:68`, 1 definition) |
| 03-the-three-way-split.md:48 | Template Method | A function taking hook callables; an ABC hook only where steps share state | `test_template_method_is_a_function_taking_hooks` (`examples/03-three-way-split/tests/test_dissolve.py:105`, 1 definition) |
| 03-the-three-way-split.md:49 | Builder | A keyword-only dataclass | `test_builder_is_a_keyword_only_dataclass` (`examples/03-three-way-split/tests/test_dissolve.py:153`, 1 definition) |
| 03-the-three-way-split.md:50 | Prototype | `dataclasses.replace` or `copy` | `test_prototype_is_replace` (`examples/03-three-way-split/tests/test_dissolve.py:166`, 1 definition) |
| 03-the-three-way-split.md:51 | Visitor | `singledispatch` for an open set, `match` with `assert_never` for a closed set | `test_visitor_is_singledispatch_without_accept` (`examples/03-three-way-split/tests/test_dissolve.py:176`, 1 definition) |
| 03-the-three-way-split.md:52 | Null Object | `X &#124; None` checked by mypy | `test_null_object_is_an_optional_checked_by_mypy` (`examples/03-three-way-split/tests/test_dissolve.py:226`, 1 definition) |
| 03-the-three-way-split.md:53 | Value Object | A frozen dataclass | `test_value_object_is_a_frozen_dataclass` (`examples/03-three-way-split/tests/test_dissolve.py:242`, 1 definition) |
| 03-the-three-way-split.md:54 | Metaclass registry | `__init_subclass__` | `test_registry_is_init_subclass` (`examples/03-three-way-split/tests/test_dissolve.py:256`, 1 definition) |
| 03-the-three-way-split.md:55 | If-chain dispatch | A dict of callables, with EAFP | `test_every_document_kind_has_an_issuer` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py:57`, 1 definition) |

### Slide 10, what survives: 14 rows

| Line | Pattern | What Python gives you | Witness test |
| --- | --- | --- | --- |
| 03-the-three-way-split.md:56 | State | Enums, `match` and small classes help; the transition table remains design | `test_the_transition_table_is_read_only` (`examples/14-state-and-finite-state-machines/tests/test_lifecycle.py:100`, 1 definition) |
| 03-the-three-way-split.md:57 | Command | A `functools.partial` for the plain deferred call; undo and queues remain | `test_undo_needs_a_command_object` (`examples/03-three-way-split/tests/test_survive.py:24`, 1 definition) |
| 03-the-three-way-split.md:58 | Abstract Factory | A family of related factories stays a design decision | `test_mypy_rejects_a_kit_that_mixes_reference_types` (`examples/16-factory-method-and-abstract-factory/tests/test_static.py:176`, 1 definition) |
| 03-the-three-way-split.md:59 | Adapter | Duck typing removes it only when the shapes already match | `test_a_client_whose_shape_matches_needs_no_adapter` (`examples/19-adapter-facade-bridge/tests/test_adapter.py:17`, 1 definition) |
| 03-the-three-way-split.md:60 | Facade | A module or class that narrows a subsystem | `test_ship_books_each_carrier_through_one_call` (`examples/19-adapter-facade-bridge/tests/test_facade.py:13`, 1 definition) |
| 03-the-three-way-split.md:61 | Bridge | Two hierarchies varying independently, joined by a Protocol | `test_every_booking_kind_works_with_every_carrier` (`examples/19-adapter-facade-bridge/tests/test_bridge.py:15`, 1 definition) |
| 03-the-three-way-split.md:62 | Composite | A uniform interface over a tree | `test_a_consignment_and_a_consolidation_answer_weight_the_same_way` (`examples/21-composite-and-flyweight/tests/test_composite.py:46`, 1 definition) |
| 03-the-three-way-split.md:63 | Flyweight | Shared immutable state; `__slots__` and interning help | `test_the_weak_pool_drops_a_commodity_nobody_holds` (`examples/21-composite-and-flyweight/tests/test_flyweight.py:34`, 1 definition) |
| 03-the-three-way-split.md:64 | Observer | Callbacks, but delivery order, failure isolation and subscriber lifetime remain | `test_one_failing_subscriber_does_not_stop_the_rest` (`examples/22-observer/tests/test_delivery.py:70`, 1 definition) |
| 03-the-three-way-split.md:65 | Mediator | Coordination in one place | `test_the_mediator_releases_in_either_order` (`examples/23-mediator-and-chain-of-responsibility/tests/test_mediator.py:61`, 1 definition) |
| 03-the-three-way-split.md:66 | Chain of Responsibility | Ordered handlers with a pass-along rule | `test_the_first_stage_that_decides_wins` (`examples/23-mediator-and-chain-of-responsibility/tests/test_chain.py:69`, 1 definition) |
| 03-the-three-way-split.md:67 | Memento | A frozen dataclass snapshot; what to capture remains | `test_rollback_keeps_the_audit_trail` (`examples/25-visitor-memento-interpreter/tests/test_memento.py:50`, 1 definition) |
| 03-the-three-way-split.md:68 | Interpreter | A grammar and its evaluator remain design | `test_explain_writes_the_tariff_as_text` (`examples/25-visitor-memento-interpreter/tests/test_tariff.py:44`, 1 definition) |
| 03-the-three-way-split.md:69 | Resource acquisition | The `with` statement and context managers | `test_writer_closes_and_discards_on_an_exception` (`examples/10-context-managers/tests/test_writer.py:66`, 1 definition) |

### Slide 11, one name, two meanings: 4 rows

| Line | Pattern | What Python gives you | Witness test |
| --- | --- | --- | --- |
| 03-the-three-way-split.md:70 | Decorator pattern vs `@decorator` syntax | Wrapper objects composed at runtime vs a function rebinding at definition time | `test_the_two_decorators_are_independent` (`examples/03-three-way-split/tests/test_disambiguate.py:111`, 1 definition) |
| 03-the-three-way-split.md:71 | Singleton | A module built at import time by default; Borg and metaclass as variants | `test_module_is_one_instance_for_every_importer` (`examples/03-three-way-split/tests/test_disambiguate.py:125`, 1 definition) |
| 03-the-three-way-split.md:72 | Proxy | A surrogate object vs attribute interception with `__getattr__`, `property` and `cached_property` | `test_proxy_forwards_only_missing_attributes` (`examples/03-three-way-split/tests/test_disambiguate.py:156`, 1 definition) |
| 03-the-three-way-split.md:73 | "Interface" | `Protocol` (structural) vs an ABC (nominal) | `test_protocol_is_structural_and_abc_is_nominal` (`examples/03-three-way-split/tests/test_disambiguate.py:183`, 1 definition) |

Row counts: 11 Dissolves, 14 Survives, 4 Needs disambiguating, 29 in all.

### Chapter 2 excerpts against the three-way split sources

`02-what-1994-assumed-and-python-dissolves.md` has 7 fenced blocks. Of their 46 non-blank lines, 44 appear verbatim in the three-way split example's `src` or `tests` files. Chapter 2 names no test; slide 7's five tests are chosen by section (functions, generators, structural typing, modules, absence in the type).

## Slide 22, principles beyond SOLID

`46-appendix-f-programming-principles.md` has no table for these; its sections each give one witness. The deck table (Principle, Witness) takes one row per section:

| Principle (section) | Witness test | Chapter line naming the test |
| --- | --- | --- |
| Composition over inheritance | `test_a_class_adapter_still_exposes_the_clients_own_methods` (`examples/19-adapter-facade-bridge/tests/test_adapter.py:41`, 1 definition) | `46-appendix-f-programming-principles.md:74` under "Composition over inheritance" |
| DRY | `test_the_fuel_surcharge_lives_in_one_definition_of_the_function` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py:122`, 1 definition) | `46-appendix-f-programming-principles.md:109` under "Duplication, speculation and size" |
| YAGNI | `test_the_engine_needs_more_classes_functions_and_lines_than_the_function` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py:115`, 1 definition) | `46-appendix-f-programming-principles.md:111` under "Duplication, speculation and size" |
| Simple design | `test_one_engine_quote_makes_more_python_calls_than_the_function` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py:135`, 1 definition) | `46-appendix-f-programming-principles.md:113` under "Duplication, speculation and size" |
| Orthogonality | `test_a_new_booking_kind_needs_no_gateway_change` (`examples/19-adapter-facade-bridge/tests/test_bridge.py:98`, 1 definition) | `46-appendix-f-programming-principles.md:117` under "Orthogonality" |
| Fail fast | `test_unknown_carrier_fails_at_the_composition_root` (`examples/06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py:85`, 1 definition) | `46-appendix-f-programming-principles.md:123` under "Fail fast" |
| EAFP | `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py:74`, 1 definition) | `46-appendix-f-programming-principles.md:130` under "EAFP" |
| The Law of Demeter | `test_each_reader_names_the_attributes_it_depends_on` (`examples/46-appendix-f-programming-principles/tests/test_demeter.py:59`, 1 definition) | `46-appendix-f-programming-principles.md:169, 183` under "The Law of Demeter" |

## Slide 55, when not to

Each sentence is the opening sentence of a catalogue chapter's "When not to use it" section, or a sentence in its first paragraph. The chapters give no test for these, so the slide rests on the sentence alone and the notes say so.

| Pattern | Chapter line (grep -nF) | In the chapter's When-not section | Same sentence in Appendix E |
| --- | --- | --- | --- |
| Strategy | `12-strategy-the-callable.md:184`: `grep -nF -- 'A single rule called from one place is a function, with no registry.' _docs/12-strategy-the-callable.md` | yes, section heading at line 182 | `45-appendix-e-pattern-to-force-reference.md:63` |
| State | `14-state-and-finite-state-machines.md:200`: `grep -nF -- 'A two-state flag is a `bool`.' _docs/14-state-and-finite-state-machines.md` | yes, section heading at line 198 | `45-appendix-e-pattern-to-force-reference.md:65` |
| Singleton | `18-singleton-module-borg-metaclass.md:193`: `grep -nF -- 'Pass a parameter when state differs per test, per tenant or per request.' _docs/18-singleton-module-borg-metaclass.md` | yes, section heading at line 191 | not an Appendix E cell |
| Adapter, Facade, Bridge | `19-adapter-facade-bridge.md:221`: `grep -nF -- 'Call the client when there'"'"'s one carrier and the SDK already fits.' _docs/19-adapter-facade-bridge.md` | yes, section heading at line 219 | not an Appendix E cell |
| Observer | `22-observer.md:217`: `grep -nF -- 'Call the parties directly when the set is fixed at the time the subject is built.' _docs/22-observer.md` | yes, section heading at line 215 | `45-appendix-e-pattern-to-force-reference.md:67` |
| Iterator | `24-iterator-generators-and-the-iterator-protocol.md:151`: `grep -nF -- 'Pass the tuple when the data is already in a list that callers index or measure.' _docs/24-iterator-generators-and-the-iterator-protocol.md` | yes, section heading at line 149 | `45-appendix-e-pattern-to-force-reference.md:70` |

## Slide 56, Appendix E rows

The reference's tables are at `45-appendix-e-pattern-to-force-reference.md` lines 33 to 88 (four tables). Ten rows are used; the cell shown is the Force column, verbatim, and its second check is that the developing chapter holds the same words.

| Pattern | Appendix E line | Force cell (verbatim) | `grep -cF` in Appendix E | Developing chapter and line |
| --- | --- | --- | --- | --- |
| Factory Method | 35 | The force is real: the caller wants a gateway for a carrier and shouldn't know which gateway class that is. | 1 | `16-factory-method-and-abstract-factory.md:36` |
| Strategy | 63 | a caller must choose among several ways of computing one result without depending on which one it holds | 1 | `12-strategy-the-callable.md:32` |
| Template Method | 64 | a sequence that has to hold across variants that differ in a few steps | 1 | `13-template-method-and-the-function-alternative.md:34` |
| State | 65 | The force is that the legal transitions are a business rule that has to be written in one place and checked. | 1 | `14-state-and-finite-state-machines.md:34` |
| Command | 66 | The force is that a change needs an identity of its own. | 1 | `15-command-undo-and-command-queues.md:36` |
| Adapter | 47 | two parts that disagree about shape: one calls, the other supplies, and an object between them translates | 1 | `19-adapter-facade-bridge.md:38` |
| Facade | 48 | a subsystem with many parts and a caller that wants a few operations | 1 | `19-adapter-facade-bridge.md:136` |
| Flyweight | 55 | the same few commodities can repeat across many consignments, and each repetition costs an object | 1 | `21-composite-and-flyweight.md:23` |
| Visitor (closed set) | 71 | Visitor is for a fixed family of kinds that gets new operations over time. | 1 | `25-visitor-memento-interpreter.md:36` |
| Interpreter | 74 | Interpreter is for rules that people write down and the program must apply. | 1 | `25-visitor-memento-interpreter.md:153` |

## Slide 59, the toolchain

| Tool | Version | Chapter 0 line | Other statement |
| --- | --- | --- | --- |
| CPython | 3.15.2 | `00-prerequisites.md:33` | .python-version holds 3.15.2; `uv run --no-sync python --version` prints Python 3.15.2 |
| uv | 0.13.7 | `00-prerequisites.md:34` | `uv --version` prints uv 0.13.7 |
| pytest | 9.2.0 | `00-prerequisites.md:35` | root pyproject.toml line 18: `pytest==9.2.0` |
| pytest-mock | 3.17.0 | `00-prerequisites.md:36` | root pyproject.toml line 19: `pytest-mock==3.17.0` |
| ruff | 0.17.4 | `00-prerequisites.md:37` | root pyproject.toml line 20; Appendix A mentions `ruff==0.17.4` |
| mypy | 2.4.1 | `00-prerequisites.md:38` | root pyproject.toml line 21; Appendix A: "On 2.4.1, `mypy --help` lists thirteen" |
| Appendix A | `uv python install 3.15.2` | `41-appendix-a-build-and-toolchain.md:32, 33, 88, 96` | |
| Appendix A | `ruff==0.17.4` | `41-appendix-a-build-and-toolchain.md:47` | |
| Appendix A | `uv_build>=0.13.7,<0.14` | `41-appendix-a-build-and-toolchain.md:63, 74` | |
| Appendix A | `On 2.4.1, `mypy --help` lists thirteen.` | `41-appendix-a-build-and-toolchain.md:156` | |

Y0 re-checked every pin against upstream on 2026-11-07 (see the plan's Y0 correction). The root `pyproject.toml`, `.python-version` and `uv --version` agree with the table at this commit.

## Slide 60, sources credited

Online sources the 101 chapters (0 to 6, 12 to 25, and Appendices A, E and F) link, grouped by source. "Used for" is the sentence the chapter attaches to the link, not new text. Chapter numbers are internal and do not appear on the slide.

| Source | Links | Chapters (internal numbers) |
| --- | --- | --- |
| Archived ActiveState recipe (Borg) | 1 | 18 |
| Astral, uv and ruff documentation | 8 | 0, 41 |
| Brandon Rhodes, python-patterns.guide | 12 | 2, 3, 16, 17, 18, 19, 20, 21, 24, 46 |
| Mark Seemann, Composition Root | 1 | 6 |
| Martin Fowler's site and papers it hosts | 4 | 6, 46 |
| Percival and Gregory, Architecture Patterns with Python (preface) | 1 | 15 |
| Python Enhancement Proposals | 21 | 0, 2, 3, 4, 5, 6, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25 |
| The Demeter project at Northeastern University | 2 | 46 |
| The Pragmatic Programmer tips page | 1 | 46 |
| The Python documentation | 26 | 0, 2, 3, 4, 6, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 46 |
| The mypy documentation | 4 | 0, 5, 41 |
| The pytest documentation | 1 | 0 |
| The typing documentation | 1 | 14 |

83 distinct URLs. Sources the chapters cite without a link: Liskov and Wing, "A Behavioral Notion of Subtyping" (ACM TOPLAS 16(6), 1994) and Liskov's OOPSLA '87 keynote (chapter 5), Meyer, Martin and Alexander as the chapters word them. The slide names the linked groups above and these three text-only credits.

## Slide 61, reading further

A book is listed when a 101 chapter cites it by title (italic title, grep `*<Title>`). Year and author are the bibliography page's.

| Book | Author(s) | Year | In bibliography.html | Cited by (chapter:line) |
| --- | --- | --- | --- | --- |
| Design Patterns: Elements of Reusable Object-Oriented Software | Gamma, Helm, Johnson, Vlissides | 1994 | yes | 1:35, 1:98, 2:199, 3:231, 4:128, 12:32 and more (42 lines) |
| Fluent Python | Ramalho | 2022 | yes | 0:235, 2:200, 3:231, 12:32, 12:299, 13:329 and more (11 lines) |
| Effective Python | Slatkin | 2024 | yes | 0:235, 2:201, 3:231, 12:299, 13:329, 17:126 and more (8 lines) |
| Architecture Patterns with Python | Percival, Gregory | 2020 | yes | 6:238, 15:216, 15:325 (3 lines) |
| Python Object-Oriented Programming | Lott, Phillips | 2025 | yes | 3:231, 5:245 (2 lines) |
| Agile Software Development | Martin | 2002 | yes | 1:98, 5:36, 5:245, 6:238, 46:30, 46:206 (6 lines) |
| Object-Oriented Software Construction | Meyer | 1997 | yes | 5:85, 5:245, 46:30, 46:206 (4 lines) |
| The Pragmatic Programmer | Thomas, Hunt | 2019 | yes | 46:109, 46:206 (2 lines) |
| Clean Code | Martin | 2008 | yes | 4:34, 4:128 (2 lines) |
| Refactoring | Fowler | 2018 | yes | 4:34, 4:72, 4:128 (3 lines) |
| (not used) Domain-Driven Design | | | yes | 0 lines in the 101 chapters; chapters 8 and 30 cite it |
| (not used) Patterns of Enterprise Application Architecture | | | yes | 0 lines in the 101 chapters; chapters 8 and 30 cite it |

## Slide 62, URLs

| URL | HTTP status at census | Where the repository names it |
| --- | --- | --- |
| https://patterncatalyst.github.io/design-patterns-with-python/ | 200 | `README.md:9` |
| https://github.com/patterncatalyst/design-patterns-with-python | 200 | `_docs/00-prerequisites.md:61` (as the `.git` clone URL), `_config.yml:14-15` |
| https://patterncatalyst.github.io/patterncatalyst-workshops-tutorials-list/ | 200 | nowhere in a reader-facing file; only the plan names it |

The hub row is a flag for the slide's author: CLAUDE.md bars cross-references to sibling sites in chapters and decks and keeps the series line in the README and site chrome, and no reader-facing file names the hub. The slide is proposed **reworded**: site and repository URLs only, with the hub dropped, unless the owner says the hub is not a sibling site.


## Figure census

The arrow census of figures 13, 14, 16, 22 and 23 was re-run against the code after the Y1d edits: for each, the spec in `diagrams/specs/` was read arrow by arrow and each arrow was matched to a line of `src` (or, where stated, a test that composes it). Figures 05, 06, 12, 19, 21 and 25 were censused at planning (their arrows are the plan's census R); their SVGs, specs and chapters are unchanged since the plan's base commit (`git diff --stat db8f3ce HEAD -- diagrams _docs` lists only 13, 14, 16, 22, 23 and chapter 25's one line).

### Figure 13, the customs skeleton (`diagrams/specs/13-template-method-and-the-function-alternative.py`)

| Arrow | Composed at |
| --- | --- |
| `CustomsHooks` to `declare_customs` | `examples/13-template-method-and-the-function-alternative/src/template_method/hooks.py:58` (`hooks: CustomsHooks`), and `SINGAPORE = CustomsHooks(...)` at :88 |
| `CustomsDeclarer` to `declare_customs`, "bound methods become hooks" | `declarer.py:40-46`: `declare` builds `CustomsHooks(classify=self.classify, duty=self.duty, extra_documents=self.extra_documents)` and calls `declare_customs` |
| `NetherlandsDeclarer` and `GermanyDeclarer` to `CustomsDeclarer` | `declarer.py:49` and `:57` (subclasses) |
| `declare_customs` to the first step, step to step, last step to `CustomsDeclaration` | `hooks.py:60-70`: refuse an empty consignment (:60-61, invariant), classify (:62-65, hook), total in one currency (:66-67, invariant; `Money.__add__` raises on mixed currencies, `domain.py:21-23`), assess duty (:68, hook), commercial invoice first then extra documents (:69, invariant), declaration (:70) |
| `extra_documents` to the last step, "default: none" | `hooks.py:69` and the default `no_extra_documents` at :24 and :35 |

Result: every arrow composed. The Y1d wording "refuse an empty consignment" matches `hooks.py:60-61`. **Passes.**

### Figure 14, the lifecycle (`diagrams/specs/14-state-and-finite-state-machines.py`)

| Arrow | Composed at |
| --- | --- |
| `TRANSITIONS` to the status column | `examples/14-state-and-finite-state-machines/src/state_machines/table.py:7-14`, read by `next_status` at :20 |
| `apply_event` to the status column | `states.py:63-77` |
| "each day: delay" box to `InTransit` | `transit.py:9-13` (`sail_one_day(state: InTransit, ...)`) |
| Downward arrows labelled `LOADED`, `DEPARTED`, `CLEARED`, `DELIVERED` | `table.py:9-12` and `states.py:66-73` |
| Dashed arrows to the refusal box from `Booked`, `Loaded`, `Cleared` and `Delivered` | `table.py:21-22` (`KeyError` becomes `TransitionError`) and `states.py:74-75` (any status with any other event) |

Result: every arrow drawn is composed. **Passes**, with one discrepancy against the Y1d note: the spec draws four refusal arrows (`Booked`, `Loaded`, `Cleared`, `Delivered`) and none from `InTransit`, not five. `TRANSITIONS[IN_TRANSIT, LOADED]` is refused by the same code (`states.py:74-75`), so the figure omits a true arrow and draws no false one. The caption says "any other pair is refused". Adding `{"x1": COL_X, "y1": 308, "x2": 270, "y2": 370, "dashed": True}` to the spec and regenerating would complete it; that is a Y1d-scope edit and is not made here.

### Figure 16, carrier kits (`diagrams/specs/16-factory-method-and-abstract-factory.py`)

| Arrow | Composed at |
| --- | --- |
| `ship(code, ...)` to `KITS` | `examples/16-factory-method-and-abstract-factory/src/factories/kits.py:63-67` |
| `KITS` to `FASTLINE_KIT` and `AIRCO_KIT` | `kits.py:60` |
| kit to its gateway | `kits.py:33` (`self.gateway(settings).book(...)`), `:50` and `:55` |
| gateway to label printer, labelled `FastlineReference` and `AircoReference` | `kits.py:33` and `:36` (the reference from `book` goes to `label`); `carriers.py:9-10`, `:42`, `:54`, `:60`, `:66` |

`GATEWAYS` (`factories.py:10-15`), the mypy note and the "not tied" rate sources are drawn as unconnected annotations, as Y1d left them. Result: **passes.**

### Figure 22, the signal (`diagrams/specs/22-observer.py`)

| Arrow | Composed at |
| --- | --- |
| `Signal.publish` to `subscribers` | `examples/22-observer/src/observer/signal.py:62` and `:70` (a snapshot of the subscribers, in order) |
| `subscribers` to `TrackingHistory.record`, held through `WeakMethod` | `signal.py:39-41`; the test `tests/test_delivery.py:60` subscribes `history.record` |
| `subscribers` to `lambda`, held strongly | `signal.py:44-45` and `_strong` at :17-23 |
| `subscribers` to "a failing subscriber" | `signal.py:74-77` (the `try` around each call) |
| "a failing subscriber" to `ExceptionGroup` | `signal.py:76-77` and :80-81; no edge from the other two |

The "plain list" box is unconnected. Result: **passes.**

### Figure 23, clearance (`diagrams/specs/23-mediator-and-chain-of-responsibility.py`)

| Arrow | Composed at |
| --- | --- |
| `CustomsDeclaration` to `clear`, `clear` to `check_documents` | `examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/clearance.py:57-67` |
| stage to next stage, "None: pass it on", and `inspect_goods` to `release` | `clearance.py:35`, `:41`, `:47` (return `None`), `:54` (the tuple), `:65-68` (`return final(declaration)`) |
| each of the three stages to `Held` | `clearance.py:29`, `:34`, `:40`, `:46` |
| `Settlement` and `Inspection` to `ClearanceMediator` | `mediator.py:58-74` (`receive` matches on both) |
| `ClearanceMediator` to `TrackingHistory.record`, labelled `CLEARED` | `mediator.py:81-83` builds the `CLEARED` event and calls `release`; `release=history.record` is passed at `tests/test_mediator.py:44` and `tests/conftest.py:148` |

The Held-to-mediator arrow is gone, as Y1d recorded. The "linked chain" box is unconnected. The last arrow is composed by the tests (and the example's README, line 32, describes the keyword), not by a module in `src`, because `release` is an injected callable. Result: **passes**, with that note.

### PNGs

All five were rendered with `presentation/render-png.sh 13 14 16 22 23` (cairosvg 2.9.1, width 1600): `presentation/png/13-template-method-and-the-function-alternative.png`, `14-state-and-finite-state-machines.png`, `16-factory-method-and-abstract-factory.png`, `22-observer.png` and `23-mediator-and-chain-of-responsibility.png`. Figure 14's PNG was viewed.

### The script's default list

Before Y1b, `render-png.sh` with no arguments rendered `05 06 12 19 21 25`, the six figures the deck embeds. Its default is now the eleven that pass the arrow census, `05 06 12 13 14 16 19 21 22 23 25`, and the header comment says so. `./render-png.sh --check` with no arguments then printed `same` for all eleven:

```text
same   png/05-srp-ocp-lsp.png
same   png/06-isp-dip-and-di-without-a-framework.png
same   png/12-strategy-the-callable.png
same   png/13-template-method-and-the-function-alternative.png
same   png/14-state-and-finite-state-machines.png
same   png/16-factory-method-and-abstract-factory.png
same   png/19-adapter-facade-bridge.png
same   png/21-composite-and-flyweight.png
same   png/22-observer.png
same   png/23-mediator-and-chain-of-responsibility.png
same   png/25-visitor-memento-interpreter.png
```

The deck's inventory embeds only the six figures it always did; 13, 14, 16, 22 and 23 are eligible but no slide uses them, so Y3 adds no slide for them unless the owner asks.

## Witness test runs

Date 2026-11-07. The 113 distinct test names above (191 cases once parametrised cases expand) were run by node id in a fresh copy built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <scratchpad>/y1b`, then `rm -rf .venv .venv-ft` and `uv sync --locked --all-packages`. Every example package's `__file__` points into the copy, for instance:

```text
consignments <scratchpad>/y1b/examples/00-prerequisites/src/consignments/__init__.py
three_way_split <scratchpad>/y1b/examples/03-three-way-split/src/three_way_split/__init__.py
srp_ocp_lsp <scratchpad>/y1b/examples/05-srp-ocp-lsp/src/srp_ocp_lsp/__init__.py
isp_dip_di <scratchpad>/y1b/examples/06-isp-dip-and-di-without-a-framework/src/isp_dip_di/__init__.py
strategy_callable <scratchpad>/y1b/examples/12-strategy-the-callable/src/strategy_callable/__init__.py
template_method <scratchpad>/y1b/examples/13-template-method-and-the-function-alternative/src/template_method/__init__.py
state_machines <scratchpad>/y1b/examples/14-state-and-finite-state-machines/src/state_machines/__init__.py
command_undo <scratchpad>/y1b/examples/15-command-undo-and-command-queues/src/command_undo/__init__.py
factories <scratchpad>/y1b/examples/16-factory-method-and-abstract-factory/src/factories/__init__.py
builder_prototype <scratchpad>/y1b/examples/17-builder-dataclasses-and-prototype/src/builder_prototype/__init__.py
singleton <scratchpad>/y1b/examples/18-singleton-module-borg-metaclass/src/singleton/__init__.py
adapter_facade_bridge <scratchpad>/y1b/examples/19-adapter-facade-bridge/src/adapter_facade_bridge/__init__.py
decorator_proxy <scratchpad>/y1b/examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/src/decorator_proxy/__init__.py
composite_flyweight <scratchpad>/y1b/examples/21-composite-and-flyweight/src/composite_flyweight/__init__.py
observer <scratchpad>/y1b/examples/22-observer/src/observer/__init__.py
mediator_chain <scratchpad>/y1b/examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/__init__.py
iterator_protocol <scratchpad>/y1b/examples/24-iterator-generators-and-the-iterator-protocol/src/iterator_protocol/__init__.py
visitor_memento_interpreter <scratchpad>/y1b/examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/__init__.py
principles_reviewed <scratchpad>/y1b/examples/46-appendix-f-programming-principles/src/principles_reviewed/__init__.py
context_managers <scratchpad>/y1b/examples/10-context-managers/src/context_managers/__init__.py
shortcut_patterns <scratchpad>/y1b/examples/31-shortcut-patterns-dict-dispatch-and-eafp/src/shortcut_patterns/__init__.py
pattern_misuse <scratchpad>/y1b/examples/32-anti-patterns-and-pattern-misuse/src/pattern_misuse/__init__.py
```

| Run | Order | Summary line |
| --- | --- | --- |
| 1 | forward | `191 passed in 9.83s` |
| 2 | forward | `191 passed in 9.61s` |
| 3 | forward | `191 passed in 9.56s` |
| 4 | reverse | `191 passed in 9.50s` |

The reverse run lists the node ids reversed (`-p no:randomly` is not needed; pytest-randomly is not installed). The copy was deleted afterwards. No sync ran in the real repository.

The node ids, in slide order:

```text
examples/00-prerequisites/tests/test_consignment.py::test_equal_values_compare_equal
examples/00-prerequisites/tests/test_consignment.py::test_reweigh_returns_new_consignment_and_leaves_original_unchanged
examples/00-prerequisites/tests/test_consignment.py::test_instance_rejects_assignment
examples/03-three-way-split/tests/test_dissolve.py::test_strategy_slot_accepts_def_lambda_and_partial
examples/03-three-way-split/tests/test_dissolve.py::test_iterator_is_a_lazy_generator
examples/03-three-way-split/tests/test_disambiguate.py::test_protocol_is_structural_and_abc_is_nominal
examples/03-three-way-split/tests/test_disambiguate.py::test_module_is_one_instance_for_every_importer
examples/03-three-way-split/tests/test_dissolve.py::test_null_object_is_an_optional_checked_by_mypy
examples/03-three-way-split/tests/test_survive.py::test_undo_needs_a_command_object
examples/03-three-way-split/tests/test_disambiguate.py::test_the_two_decorators_are_independent
examples/03-three-way-split/tests/test_dissolve.py::test_a_class_is_already_a_factory_method
examples/03-three-way-split/tests/test_dissolve.py::test_template_method_is_a_function_taking_hooks
examples/03-three-way-split/tests/test_dissolve.py::test_builder_is_a_keyword_only_dataclass
examples/03-three-way-split/tests/test_dissolve.py::test_prototype_is_replace
examples/03-three-way-split/tests/test_dissolve.py::test_visitor_is_singledispatch_without_accept
examples/03-three-way-split/tests/test_dissolve.py::test_value_object_is_a_frozen_dataclass
examples/03-three-way-split/tests/test_dissolve.py::test_registry_is_init_subclass
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py::test_every_document_kind_has_an_issuer
examples/14-state-and-finite-state-machines/tests/test_lifecycle.py::test_the_transition_table_is_read_only
examples/16-factory-method-and-abstract-factory/tests/test_static.py::test_mypy_rejects_a_kit_that_mixes_reference_types
examples/19-adapter-facade-bridge/tests/test_adapter.py::test_a_client_whose_shape_matches_needs_no_adapter
examples/19-adapter-facade-bridge/tests/test_facade.py::test_ship_books_each_carrier_through_one_call
examples/19-adapter-facade-bridge/tests/test_bridge.py::test_every_booking_kind_works_with_every_carrier
examples/21-composite-and-flyweight/tests/test_composite.py::test_a_consignment_and_a_consolidation_answer_weight_the_same_way
examples/21-composite-and-flyweight/tests/test_flyweight.py::test_the_weak_pool_drops_a_commodity_nobody_holds
examples/22-observer/tests/test_delivery.py::test_one_failing_subscriber_does_not_stop_the_rest
examples/23-mediator-and-chain-of-responsibility/tests/test_mediator.py::test_the_mediator_releases_in_either_order
examples/23-mediator-and-chain-of-responsibility/tests/test_chain.py::test_the_first_stage_that_decides_wins
examples/25-visitor-memento-interpreter/tests/test_memento.py::test_rollback_keeps_the_audit_trail
examples/25-visitor-memento-interpreter/tests/test_tariff.py::test_explain_writes_the_tariff_as_text
examples/10-context-managers/tests/test_writer.py::test_writer_closes_and_discards_on_an_exception
examples/03-three-way-split/tests/test_disambiguate.py::test_proxy_forwards_only_missing_attributes
examples/05-srp-ocp-lsp/tests/test_srp.py::test_each_change_moves_only_the_fields_it_feeds
examples/05-srp-ocp-lsp/tests/test_srp.py::test_pricing_and_tax_run_alone
examples/05-srp-ocp-lsp/tests/test_srp.py::test_audit_receives_exactly_the_quote_returned
examples/05-srp-ocp-lsp/tests/test_ocp.py::test_a_new_tax_rule_is_added_without_editing_quote
examples/05-srp-ocp-lsp/tests/test_ocp.py::test_default_tax_table_is_read_only
examples/05-srp-ocp-lsp/tests/test_lsp.py::test_calculator_honours_the_rate_contract
examples/05-srp-ocp-lsp/tests/test_lsp.py::test_contract_catches_a_strengthened_precondition
examples/05-srp-ocp-lsp/tests/test_lsp.py::test_mypy_cannot_see_a_behavioural_violation
examples/06-isp-dip-and-di-without-a-framework/tests/test_isp.py::test_adapters_satisfy_every_role_without_naming_one
examples/06-isp-dip-and-di-without-a-framework/tests/test_isp.py::test_a_fat_protocol_forces_fakes_to_stub_unused_methods
examples/06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py::test_build_app_shares_one_gateway_between_booking_and_tracking
examples/06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py::test_composition_root_accepts_a_substitute_without_patching
examples/06-isp-dip-and-di-without-a-framework/tests/test_dip.py::test_policy_modules_do_not_import_the_adapters
examples/19-adapter-facade-bridge/tests/test_adapter.py::test_a_class_adapter_still_exposes_the_clients_own_methods
examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_the_fuel_surcharge_lives_in_one_definition_of_the_function
examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_the_engine_needs_more_classes_functions_and_lines_than_the_function
examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_one_engine_quote_makes_more_python_calls_than_the_function
examples/19-adapter-facade-bridge/tests/test_bridge.py::test_a_new_booking_kind_needs_no_gateway_change
examples/06-isp-dip-and-di-without-a-framework/tests/test_composition_root.py::test_unknown_carrier_fails_at_the_composition_root
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read
examples/46-appendix-f-programming-principles/tests/test_demeter.py::test_each_reader_names_the_attributes_it_depends_on
examples/46-appendix-f-programming-principles/tests/test_demeter.py::test_a_credit_reaches_only_the_reader_that_asks_the_shipment
examples/46-appendix-f-programming-principles/tests/test_demeter.py::test_both_readers_give_the_same_line_without_credits
examples/12-strategy-the-callable/tests/test_behaviour_table.py::test_a_class_per_strategy_passes_the_same_table
examples/12-strategy-the-callable/tests/test_behaviour_table.py::test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one
examples/13-template-method-and-the-function-alternative/tests/test_hooks.py::test_declare_customs_runs_its_steps_in_order
examples/13-template-method-and-the-function-alternative/tests/test_hooks.py::test_a_hook_left_out_takes_its_default
examples/13-template-method-and-the-function-alternative/tests/test_hooks.py::test_a_required_hook_cannot_be_left_out
examples/14-state-and-finite-state-machines/tests/test_state_objects.py::test_state_objects_pass_the_same_lifecycle_table
examples/14-state-and-finite-state-machines/tests/test_lifecycle.py::test_an_illegal_event_is_a_transition_error
examples/15-command-undo-and-command-queues/tests/test_commands.py::test_apply_returns_the_amendment_that_reverses_it
examples/15-command-undo-and-command-queues/tests/test_queue.py::test_a_failing_batch_leaves_the_booking_unchanged
examples/15-command-undo-and-command-queues/tests/test_commands.py::test_amendments_compare_by_value_and_partials_do_not
examples/16-factory-method-and-abstract-factory/tests/test_factory_method.py::test_a_registered_constructor_builds_each_carrier_gateway
examples/16-factory-method-and-abstract-factory/tests/test_factory_method.py::test_the_creator_design_declares_three_classes_where_the_registry_declares_none
examples/16-factory-method-and-abstract-factory/tests/test_factory_method.py::test_an_unknown_carrier_code_is_an_unknown_carrier_error
examples/16-factory-method-and-abstract-factory/tests/test_kits.py::test_each_kit_ships_with_its_own_carriers_products
examples/16-factory-method-and-abstract-factory/tests/test_kits.py::test_every_kit_is_a_frozen_value
examples/17-builder-dataclasses-and-prototype/tests/test_builder.py::test_both_constructors_pass_the_booking_table
examples/17-builder-dataclasses-and-prototype/tests/test_builder.py::test_a_positional_constructor_accepts_a_swapped_origin_and_destination
examples/17-builder-dataclasses-and-prototype/tests/test_prototype.py::test_a_template_and_replace_give_a_new_request
examples/18-singleton-module-borg-metaclass/tests/test_variants.py::test_every_form_gives_each_caller_the_same_rates
examples/18-singleton-module-borg-metaclass/tests/test_once.py::test_load_once_runs_the_loader_once_when_two_threads_pass_the_first_check
examples/19-adapter-facade-bridge/tests/test_static.py::test_mypy_rejects_a_client_with_a_different_shape
examples/19-adapter-facade-bridge/tests/test_facade.py::test_a_carrier_rejection_becomes_a_carrier_error
examples/19-adapter-facade-bridge/tests/test_bridge.py::test_the_class_per_pair_design_needs_a_class_for_every_kind_and_carrier
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_layers.py::test_the_layers_for_a_consignment_are_chosen_while_the_program_runs
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py::test_the_at_sign_rebinds_the_name_once_at_definition_time
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py::test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_static.py::test_mypy_rejects_a_decorated_function_where_a_calculator_belongs
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_layers.py::test_a_layer_wraps_a_calculator_and_leaves_it_unchanged
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_layers.py::test_layer_order_changes_the_price_when_a_fee_is_added
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_layers.py::test_compose_wraps_the_last_layer_outermost
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py::test_syntax_stacking_order_decides_whether_each_attempt_is_audited
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_syntax.py::test_rebound_functions_do_not_compare_by_value
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_proxy.py::test_the_proxy_asks_the_gateway_once_per_consignment
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_proxy.py::test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_static.py::test_mypy_reports_a_typo_on_the_explicit_proxy
examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/tests/test_static.py::test_mypy_accepts_a_typo_through_a_forwarding_proxy
examples/21-composite-and-flyweight/tests/test_composite.py::test_a_flat_sum_misses_nested_consolidations
examples/21-composite-and-flyweight/tests/test_static.py::test_mypy_refuses_adding_to_a_frozen_consolidation
examples/21-composite-and-flyweight/tests/test_flyweight.py::test_split_port_codes_are_equal_but_distinct_objects
examples/22-observer/tests/test_delivery.py::test_subscribers_are_called_in_subscription_order
examples/22-observer/tests/test_delivery.py::test_every_failure_is_reported_after_delivery
examples/22-observer/tests/test_lifetime.py::test_a_bound_method_subscriber_is_dropped_when_its_owner_goes
examples/22-observer/tests/test_reentrancy.py::test_an_event_published_during_delivery_waits_its_turn
examples/23-mediator-and-chain-of-responsibility/tests/test_chain.py::test_stages_after_a_decision_are_not_called
examples/23-mediator-and-chain-of-responsibility/tests/test_static.py::test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage
examples/23-mediator-and-chain-of-responsibility/tests/test_mediator.py::test_a_choreography_loses_a_settlement_that_arrives_before_inspection
examples/23-mediator-and-chain-of-responsibility/tests/test_mediator.py::test_a_duplicate_settlement_releases_once
examples/24-iterator-generators-and-the-iterator-protocol/tests/test_protocol.py::test_a_tracking_history_can_be_walked_twice
examples/24-iterator-generators-and-the-iterator-protocol/tests/test_protocol.py::test_a_self_iterating_history_is_empty_on_the_second_pass
examples/24-iterator-generators-and-the-iterator-protocol/tests/test_laziness.py::test_the_first_page_reads_only_one_page
examples/24-iterator-generators-and-the-iterator-protocol/tests/test_reading.py::test_breaking_out_of_a_loop_leaves_a_named_reader_open
examples/25-visitor-memento-interpreter/tests/test_static.py::test_mypy_reports_an_event_left_out_of_a_match
examples/25-visitor-memento-interpreter/tests/test_visitor.py::test_status_after_maps_each_event_to_a_consignment_status
examples/25-visitor-memento-interpreter/tests/test_visitor.py::test_every_visitor_form_describes_a_journey_the_same_way
examples/25-visitor-memento-interpreter/tests/test_memento.py::test_a_deepcopy_memento_erases_the_audit_trail_on_rollback
examples/25-visitor-memento-interpreter/tests/test_memento.py::test_rollback_restores_the_attached_documents
examples/25-visitor-memento-interpreter/tests/test_tariff.py::test_every_rule_form_prices_the_same_consignments
examples/25-visitor-memento-interpreter/tests/test_static.py::test_mypy_reports_a_tariff_node_left_out_of_evaluate
```

## Corrections to the plan

- **Line drift.** One inventory line moved: the `@` form sentence is at `20-decorator-pattern-vs-decorator-syntax-and-proxy.md:104`, not 102. Every other chapter line the inventory cites (checked one by one, including the six when-not sentences and the chapters Y1d edited) still holds.
- **Slide 5.** The range is fixed at `examples/00-prerequisites/src/consignments/consignment.py` lines 36 to 43. It is a contiguous run of the chapter's second fenced block (the chapter elides `__post_init__` and the slide stops before `reweigh`), so `test_reweigh_returns_new_consignment_and_leaves_original_unchanged` is witnessed in the notes, not on the code.
- **Slide 12.** `dissolve.py` lines 35 to 48 are quoted byte-exact by chapter 2 (the fence opening at line 44, block lines 6 to 19), not by chapter 3, which quotes only `quote_carrier`. The sentence the slide rests on is chapter 3's (line 75); both chapters draw on the same example.
- **Slide 49.** Of the 26 code slides, 25 are quoted byte-exact as a contiguous run of a chapter fence. Slide 49 is the exception: `iterator_protocol/domain.py` lines 30 to 43 are read from the source, and chapter 24 quotes only lines 42 and 43 (`__iter__` and its `yield from`). The class header, docstring, `__init__` and `record` (lines 30 to 41) are in no chapter fence. The excerpt is exact with the source, which is the acceptance test; if the owner wants decision 11's "only ranges the chapter quotes", narrow the slide to lines 42 to 43 with the anchor `    def __iter__(self) -> Iterator[HandlingEvent]:`.
- **Slide 25.** The package path is `examples/12-strategy-the-callable/src/strategy_callable/rules.py`; "Y1b fixes the package path" needs no change beyond writing it in full.
- **Slides 9 and 10.** The plan's "the split's `test_dissolve` tests" covers ten of the eleven Dissolves rows. If-chain dispatch is witnessed by chapter 31's `test_every_document_kind_has_an_issuer`. Only Command of the fourteen Survives rows has a witness in the split's own tests; each other row is witnessed in its own chapter's example (Resource acquisition in chapter 10), named in the row table. The deck notes say which chapter develops which row, by concept.
- **Slide 22.** Appendix F's table at `46-appendix-f-programming-principles.md:34-38` is the five SOLID principles, already carried by slides 15 to 20. The principles beyond SOLID have no table; the slide table is built from the chapter's eight sections (composition over inheritance, DRY, YAGNI, simple design, orthogonality, fail fast, EAFP, the Law of Demeter), each with one named witness. Of these only the Demeter row's test lives in Appendix F's own member; the others live in the chapters 6, 19, 31 and 32 examples. The plan's "F member tests" is wrong for seven of the eight rows.
- **Slide 61.** The plan's evidence U lists *Domain-Driven Design* and *Patterns of Enterprise Application Architecture*. No 101 chapter cites either (chapters 8 and 30 do), so the two rows leave the slide. Ten books remain; years and authors are the bibliography page's, and *Refactoring* is the second edition (2018).
- **Slide 62.** The hub URL is named in no reader-facing file, and CLAUDE.md bars cross-references to sibling sites in decks. Proposed: site and repository URLs only. All three URLs return 200.
- **Decision 9 counts.** The inventory has 9 table slides (9, 10, 11, 22, 55, 56, 59, 60, 61) and 10 bullet slides (4, 7, 8, 13, 15, 36, 39, 42, 57, 62), not "4 table slides". The total stays 62: 2 cover and route, 9 dividers, 6 figures, 26 code, 9 tables, 10 bullets.
- **Chapter 2.** It names no test. Of its 46 non-blank fence lines, 44 appear verbatim in the three-way split example, so the slide 7 witnesses are the five split tests that match its five sections, not tests the chapter cites.
- **Figure 14.** The spec draws four refusal arrows, not five as the Y1d note says; see "Figure 14". The census passes.
- **Figure 23.** The mediator-to-record arrow is composed by tests (`release=history.record`), not by `src`; it passes on that ground.
- **render-png.sh.** The default list moved from six figures to eleven.
- **Row 348.** Applied as the Y1d note words it: "the delivery sentence, the module-docstring sentence, the tuple sentence (not a default), the mediator docstring".

## Standalone wording (owner rule: no chapter references in slides or notes)

The decks carry no chapter numbers, no chapter or appendix titles used as pointers, and no phrases such as "the X chapter" or "see the chapter on", in slide text or notes. This census stays internal. These inventory slides depend on such a pointer, with standalone wording that states the idea itself:

| Slide | Dependency in the inventory | Standalone wording |
| --- | --- | --- |
| 5 | "the range chapter 0 quotes" | Notes name the toolchain and the three tests, not where the book says it. |
| 7 | "ch2, census lines" | Title and notes state the five assumptions: behaviour inside objects of declared classes, functions that cannot be passed, loops that cannot suspend, types matched by declared name, no module identity. |
| 8, 9, 10, 11 | "the three-way split", "the chapter's rows verbatim" | Call it "the sort" (does a feature resolve the force without the structure; does the name mean one thing). Tables are headed by the bucket, not by where the book maps them. |
| 12 | notes: "the three-way split" | "Dissolved patterns at their smallest". |
| 13 | notes: "the deck's prompt sidebars build on it" | State the idea: a pattern name tells a reviewer and an assistant which decision was made. |
| 20 | notes: Fowler and Seemann "as chapter 6 credits them" | Credit the two authors by name and title only. |
| 22 | claim: "Appendix F's principles", "as F states it" | Title "Principles beyond SOLID"; claim "each principle has a test that shows its effect". |
| 23 | notes: "as F credits them" | Credit the Demeter project by name. |
| 36, 40, 43, 49 | notes: "Rhodes's page, credited" | Name the author and the page title as a credit, with no pointer to a chapter. |
| 41, 50 | notes: "the 201 deck writes decorators well", "open set in the 201 deck" | Drop the deck pointers; say the open-set form is a different tool, by concept. |
| 42 | "the three-way split's map row" | "Proxy is a name that covers a surrogate object and attribute interception." |
| 55 | "when-not sentences quoted from the catalogue chapters" | "Skip it when" table headed by the absent force; no source named on the slide. |
| 56 | "Appendix E rows", "how to read the reference by force" | Title "Pattern to force"; claim "each pattern answers one force". |
| 57 | "a catalogue chapter's sidebar prompt" | "A prompt that names the decision, then asks for the failing test". |
| 59 | "Appendix A and chapter 0 versions" | "The pinned toolchain". |
| 60 | "as the chapters word them" | "Sources credited", each named by author and title. |
| 61 | "Reading further" listing what each book adds | Books by title, author and year only, with no chapter or appendix pointers. |
| 62 | "the next two decks by theme" | Keep by theme; no chapter numbers. |

Every "NN.md:line" in the inventory's notes column is internal and must not reach a slide or notes.
