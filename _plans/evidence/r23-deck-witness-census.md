---
title: "Evidence: Deck 201 witness census (r23, Z1b)"
output: false
render_with_liquid: false
---

# Deck 201 witness census

Recorded 2026-11-07 for r23, step Z1b, on Python 3.15.2 and pytest 9.2.0, at commit `0de82cd` on `release/r23` (after Z1c, so every line, anchor and figure below is read from the fixed tree; the working tree then held the five new Deck 201 PNGs and this file). Paths are repo-relative; `<scratchpad>` stands for the session scratch directory.

## Method

- Each slide of the plan's 45-slide inventory is recorded with its claim, the chapter's exact front-matter title, and the chapter sentences it rests on. A sentence is a fragment re-found with `grep -nF -- <fragment> <chapter file>`. A fragment is accepted only when it hits exactly one line, so the line number cannot drift between two copies of a phrase. Credits (URLs and attributions) may hit two lines, the body and the chapter's "For deeper coverage" paragraph, and show every hit.
- A witness test is cited by exact name. Each was searched with `^\s*(async )?def <name>\(` under `examples/*/tests/**/*.py` and has exactly one definition, none inside a class, so a node id is `<file>::<name>`. A test in the "Witness" column of the inventory is a witness; a test only named in the notes column is a notes witness. Both kinds are run.
- A code slide gives the source path, the 1-based range, the anchor (the exact first line, with its indentation) and the fence it is a contiguous run of. The check compares the range, line for line, with every fenced block of the chapter; a match means the excerpt is byte-exact with what the chapter quotes. The builder reads the range from the file and asserts the anchor, so the slide is byte-exact with the source by construction.
- A figure slide names the figure, its committed PNG and the arrow census re-run against the code now (section "Figure census").
- Every witness test was run by node id in a fresh scratch copy (section "Witness test runs").
- Line numbers moved with Z1c's edits to chapters 7 to 11, 26 to 32 and 37 to 38; every line below is current. The plan's quoted sentences were re-found; where a sentence or range differs, Corrections says so.

## Summary

45 slides. 41 kept as the plan has them, 4 reworded (slides 16, 22, 27, 28), none cut. Every content, code, figure and table slide has at least one witness test or a recorded chapter sentence, and no claim is stretched beyond them. The slide-kind counts are 2 cover and route, 8 dividers, 5 figures, 22 code, 5 bullets (including the closing slide), 3 tables.

| # | Section | Title | Kind | Disposition | Reason |
| --- | --- | --- | --- | --- | --- |
| 1 | Cover | Design Patterns with Python | cover | kept | structural slide |
| 2 | Cover | The route | route | kept | structural slide; standalone wording below |
| 3 | The data model | divider | divider | kept | structural slide |
| 4 | The data model | One hashing contract | code | kept | claim, witnesses and range confirmed |
| 5 | The data model | The reflected operand | figure | kept | figure 07 passes the census after F1; ordering tests are notes-only witnesses |
| 6 | The data model | Value Object as declaration | code | kept | range unchanged at 15 to 23 after P4, but its longest line is now 92 characters (plan: 81), which sets the font size; the bucket word is glossed in the standalone wording |
| 7 | The data model | Frozen, not sealed | bullets | kept | claim and all seven witnesses confirmed |
| 8 | Contracts and cleanup | divider | divider | kept | structural slide |
| 9 | Contracts and cleanup | Absence in the type | code | kept | claim, witnesses and range confirmed |
| 10 | Contracts and cleanup | A silent null object | code | kept | range is a test fixture (`_NullGateway`); the notes must say so |
| 11 | Contracts and cleanup | The carrier lookup | figure | kept | figure 09 passes the census after F2 |
| 12 | Contracts and cleanup | Exits from a block | figure | kept | figure 10 passes the census after F3 |
| 13 | Contracts and cleanup | Commit or discard | code | kept | claim, witnesses and range confirmed (range is lines 8 to 21 of a 21-line fence) |
| 14 | Contracts and cleanup | Try in the generator form | code | kept | claim, witnesses and range confirmed; the stack contract is worded as P1 narrowed it (a failed open discards the partials; each writer commits on its own on success) |
| 15 | Decorators done right | divider | divider | kept | structural slide |
| 16 | Decorators done right | What wraps copies | code | reworded | two `partial` witnesses named in the census (the plan said 'two tests'); range is a contiguous run of a 17-line fence |
| 17 | Decorators done right | Factories refusing bare use | code | kept | claim, witnesses and range confirmed |
| 18 | Decorators done right | Where the timer sits | bullets | kept | claim and witnesses confirmed |
| 19 | Attribute access | divider | divider | kept | structural slide |
| 20 | Attribute access | One validator, many fields | code | kept | claim, witnesses and range confirmed; see Corrections for an unrelated message observation in the excerpt |
| 21 | Attribute access | Costs of cached_property | code | kept | claim, witnesses and range confirmed |
| 22 | Attribute access | A self-loading history | code | reworded | the plan's claim uses the book's bucket vocabulary ('where Proxy is disambiguated'); standalone wording below. Range confirmed |
| 23 | Attribute access | The recursion trap | code | kept | claim, witnesses and range confirmed; range is a test-local class |
| 24 | Dispatch and registries | divider | divider | kept | structural slide |
| 25 | Dispatch and registries | Dispatch by registered type | code | kept | claim, witnesses and range confirmed |
| 26 | Dispatch and registries | Registration from another module | code | kept | claim, witnesses and range confirmed |
| 27 | Dispatch and registries | Registration by class keyword | code | reworded | range widened from lines 44 to 52 to lines 44 to 58, so the slide shows the registration the claim is about; the plan's range stops before it |
| 28 | Dispatch and registries | Metaclass costs | table | reworded | the chapter's 'four places' need `test_mypy_refuses_self_in_a_metaclass_new`, which the plan omitted; the table has four cost rows and one row for what a metaclass buys |
| 29 | Dispatch and registries | A narrow try | code | kept | claim, witnesses and range confirmed |
| 30 | Dispatch and registries | Dispatch tables and EAFP | figure | kept | figure 31 passes the census after F7; its look-first box restates a claim Deck 101 makes (see the boundary check), so the notes lead with the EAFP read |
| 31 | Pattern misuse | divider | divider | kept | structural slide |
| 32 | Pattern misuse | A quote as a function | code | kept | claim, witnesses and range confirmed |
| 33 | Pattern misuse | A misplaced Visitor | bullets | kept | claim and witnesses confirmed |
| 34 | Pattern misuse | A located dependency | code | kept | claim, witnesses and range confirmed; range is a test-local class |
| 35 | Concurrency and the patterns | divider | divider | kept | structural slide |
| 36 | Concurrency and the patterns | Build and GIL state | code | kept | claim, witnesses and range confirmed; both builds are tested in CI |
| 37 | Concurrency and the patterns | Locks over read and write | figure | kept | figure 37 passes the census after F9; the lost-update counts are now sourced (P12 landed) |
| 38 | Concurrency and the patterns | What a pool shares | code | kept | claim, witnesses and range confirmed |
| 39 | Concurrency and the patterns | A coroutine as a value | bullets | kept | claim and witnesses confirmed |
| 40 | Concurrency and the patterns | Closing a feed early | code | kept | the claim sentence is the Iterator row of the chapter's table (line 50); range confirmed |
| 41 | Concurrency and the patterns | Task groups and subscribers | code | kept | claim, witnesses and range confirmed |
| 42 | Reference | divider | divider | kept | structural slide; standalone wording below (do not point to the closing slide) |
| 43 | Reference | Sources credited | table | kept | built from the credit census below |
| 44 | Reference | Reading further | table | kept | eight books, each confirmed in the bibliography page and a chapter |
| 45 | Reference | Site and repository | bullets | kept | both URLs return 200 now; re-checked at the QA step |

## Per-slide census

Every chapter sentence below is a `grep -nF` fragment that hit exactly one line of the named chapter at this commit. Every test name was found once under `examples/*/tests`. A slide with a figure or code range names the figure or the source file and lines.

### Slide 1: Design Patterns with Python (Cover)

- Claim: 201: Idiomatic Python.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 2: The route (Cover)

- Claim: the eight themes of the deck.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide; standalone wording below.

### Slide 3: divider (The data model)

- Claim: -
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 4: One hashing contract (The data model)

- Claim: equal values must hash alike, and a set test catches a broken hash.
- Chapter: 07, "The data model: dunder methods as the substrate" (`_docs/07-the-data-model.md`).
- `07-the-data-model.md:53`: `grep -nF -- 'equal values must hash alike' _docs/07-the-data-model.md`
- `07-the-data-model.md:81`: `grep -nF -- 'A set test catches this and a reading of the class doesn'"'"'t.' _docs/07-the-data-model.md`
- `07-the-data-model.md:47`: `grep -nF -- 'The lookup is on the type.' _docs/07-the-data-model.md`
- Witness tests, each defined once:
  - `test_a_turned_carton_is_one_set_element` (`examples/07-the-data-model/tests/test_equality.py:82`, 1 definition)
  - `test_defining_eq_alone_makes_a_class_unhashable` (`examples/07-the-data-model/tests/test_equality.py:75`, 1 definition)
  - `test_custom_eq_in_a_frozen_dataclass_keeps_a_field_hash` (`examples/07-the-data-model/tests/test_equality.py:94`, 1 definition)
  - `test_mypy_cannot_see_a_broken_hash_contract` (`examples/07-the-data-model/tests/test_static.py:150`, 1 definition)
  - `test_special_methods_are_looked_up_on_the_type` (`examples/07-the-data-model/tests/test_equality.py:60`, 1 definition)
- Code: `examples/07-the-data-model/src/data_model/cargo.py` lines 32 to 41 (10 lines, longest 77 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 32, exact, 4 leading spaces): `def _extents(self) -> tuple[int, ...]:`
  - Last line (41): `return hash(self._extents())`
  - Contiguous run of the fence opening at `07-the-data-model.md:58` (block lines 1 to 10 of 10); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 5: The reflected operand (The data model)

- Claim: the left operand's type asks first and the reflected method answers; `NotImplemented` is a value, and `start=` says what the zero is.
- Chapter: 07, "The data model: dunder methods as the substrate" (`_docs/07-the-data-model.md`).
- `07-the-data-model.md:85`: `grep -nF -- '`NotImplemented` isn'"'"'t an exception.' _docs/07-the-data-model.md`
- `07-the-data-model.md:114`: `grep -nF -- '`start=` says what the zero is' _docs/07-the-data-model.md`
- `07-the-data-model.md:131`: `grep -nF -- 'Ordering stops where the domain stops.' _docs/07-the-data-model.md`
- Witness tests, each defined once:
  - `test_a_factor_times_money_uses_the_reflected_method` (`examples/07-the-data-model/tests/test_arithmetic.py:17`, 1 definition)
  - `test_sum_needs_a_money_start` (`examples/07-the-data-model/tests/test_arithmetic.py:32`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_total_ordering_derives_the_other_comparisons` (`examples/07-the-data-model/tests/test_ordering.py:18`, 1 definition)
  - `test_quotes_sort_by_total_but_not_by_themselves` (`examples/07-the-data-model/tests/test_ordering.py:43`, 1 definition)
- Figure: `diagrams/07-the-data-model.svg`, PNG `presentation/png/07-the-data-model.png` (see Figure census).
- Disposition: **kept**. figure 07 passes the census after F1; ordering tests are notes-only witnesses.

### Slide 6: Value Object as declaration (The data model)

- Claim: one frozen, slotted dataclass declaration supplies what the Value Object pattern wrote by hand.
- Chapter: 08, "Dataclasses and value semantics" (`_docs/08-dataclasses-and-value-semantics.md`).
- `08-dataclasses-and-value-semantics.md:38`: `grep -nF -- 'This pattern dissolves.' _docs/08-dataclasses-and-value-semantics.md`
- `08-dataclasses-and-value-semantics.md:38`: `grep -nF -- 'What remains is the part no decorator can supply.' _docs/08-dataclasses-and-value-semantics.md`
- `08-dataclasses-and-value-semantics.md:34`: `grep -nF -- 'The force is four needs at once.' _docs/08-dataclasses-and-value-semantics.md`
- `08-dataclasses-and-value-semantics.md:32`: `grep -nF -- 'whose equality isn'"'"'t based on identity' _docs/08-dataclasses-and-value-semantics.md`
- `08-dataclasses-and-value-semantics.md:163`: `grep -nF -- 'A type with a lifecycle and an identity isn'"'"'t a value.' _docs/08-dataclasses-and-value-semantics.md`
- Witness tests, each defined once:
  - `test_equal_values_are_interchangeable` (`examples/08-dataclasses-and-value-semantics/tests/test_values.py:24`, 1 definition)
  - `test_a_frozen_value_refuses_assignment` (`examples/08-dataclasses-and-value-semantics/tests/test_values.py:43`, 1 definition)
  - `test_mypy_checks_the_generated_methods` (`examples/08-dataclasses-and-value-semantics/tests/test_static.py:111`, 1 definition)
  - `test_slots_remove_dict_and_weakref_until_asked` (`examples/08-dataclasses-and-value-semantics/tests/test_values.py:64`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_stowage_plan_is_an_entity` (`examples/08-dataclasses-and-value-semantics/tests/test_generated.py:83`, 1 definition)
  - `test_mutable_default_is_refused_at_class_creation` (`examples/08-dataclasses-and-value-semantics/tests/test_generated.py:107`, 1 definition)
- Code: `examples/08-dataclasses-and-value-semantics/src/value_semantics/values.py` lines 15 to 23 (9 lines, longest 92 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 15, exact, 0 leading spaces): `@dataclass(frozen=True, slots=True, order=True)`
  - Last line (23): `raise ValueError(f"kilograms must be positive and finite, got {self.kilograms}")`
  - Contiguous run of the fence opening at `08-dataclasses-and-value-semantics.md:44` (block lines 1 to 9 of 9); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. range unchanged at 15 to 23 after P4, but its longest line is now 92 characters (plan: 81), which sets the font size; the bucket word is glossed in the standalone wording.

### Slide 7: Frozen, not sealed (The data model)

- Claim: frozen guards assignment only, is shallow, and an amendment is a new value.
- Chapter: 08, "Dataclasses and value semantics" (`_docs/08-dataclasses-and-value-semantics.md`).
- `08-dataclasses-and-value-semantics.md:65`: `grep -nF -- 'Frozen guards attribute assignment; it doesn'"'"'t seal the object.' _docs/08-dataclasses-and-value-semantics.md`
- `08-dataclasses-and-value-semantics.md:75`: `grep -nF -- 'Frozen is also shallow.' _docs/08-dataclasses-and-value-semantics.md`
- `08-dataclasses-and-value-semantics.md:81`: `grep -nF -- 'An amendment isn'"'"'t an edit.' _docs/08-dataclasses-and-value-semantics.md`
- `08-dataclasses-and-value-semantics.md:157`: `grep -nF -- '`__post_init__` reads and raises. It doesn'"'"'t repair.' _docs/08-dataclasses-and-value-semantics.md`
- Witness tests, each defined once:
  - `test_frozen_is_a_setattr_guard_not_a_seal` (`examples/08-dataclasses-and-value-semantics/tests/test_values.py:50`, 1 definition)
  - `test_frozen_is_shallow` (`examples/08-dataclasses-and-value-semantics/tests/test_values.py:56`, 1 definition)
  - `test_a_mutable_dataclass_is_not_a_dict_key` (`examples/08-dataclasses-and-value-semantics/tests/test_aliasing.py:62`, 1 definition)
  - `test_a_mutable_consignment_aliased_between_bookings_changes_both` (`examples/08-dataclasses-and-value-semantics/tests/test_aliasing.py:33`, 1 definition)
  - `test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old` (`examples/08-dataclasses-and-value-semantics/tests/test_aliasing.py:41`, 1 definition)
  - `test_replace_runs_post_init` (`examples/08-dataclasses-and-value-semantics/tests/test_aliasing.py:55`, 1 definition)
  - `test_mypy_cannot_see_value_semantics_mistakes` (`examples/08-dataclasses-and-value-semantics/tests/test_static.py:125`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_money_validates_and_of_normalises` (`examples/08-dataclasses-and-value-semantics/tests/test_generated.py:58`, 1 definition)
- Code: none; a bullet slide whose claims are the sentences and tests above.
- Disposition: **kept**. claim and all seven witnesses confirmed.

### Slide 8: divider (Contracts and cleanup)

- Claim: -
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 9: Absence in the type (Contracts and cleanup)

- Claim: an optional return makes absence a branch mypy requires.
- Chapter: 09, "Protocol, duck typing, and structural typing with mypy" (`_docs/09-protocol-and-structural-typing.md`).
- `09-protocol-and-structural-typing.md:62`: `grep -nF -- 'This pattern dissolves.' _docs/09-protocol-and-structural-typing.md`
- `09-protocol-and-structural-typing.md:79`: `grep -nF -- 'Use an explicit branch where the check must survive.' _docs/09-protocol-and-structural-typing.md`
- `09-protocol-and-structural-typing.md:60`: `grep -nF -- 'The force: a caller that asks for a collaborator that may not exist must not go on as though it did.' _docs/09-protocol-and-structural-typing.md`
- Witness tests, each defined once:
  - `test_find_gateway_returns_none_for_an_unknown_code` (`examples/09-protocol-and-structural-typing/tests/test_absence.py:25`, 1 definition)
  - `test_book_with_turns_absence_into_a_booking_error` (`examples/09-protocol-and-structural-typing/tests/test_absence.py:30`, 1 definition)
  - `test_mypy_requires_a_branch_for_absence` (`examples/09-protocol-and-structural-typing/tests/test_static.py:102`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_a_sentinel_separates_not_given_from_none` (`examples/09-protocol-and-structural-typing/tests/test_absence.py:51`, 1 definition)
- Code: `examples/09-protocol-and-structural-typing/src/structural_typing/carriers.py` lines 52 to 63 (12 lines, longest 79 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 52, exact, 0 leading spaces): `def find_gateway(code: str) -> CarrierGateway | None:`
  - Last line (63): `return gateway.book(consignment)`
  - Contiguous run of the fence opening at `09-protocol-and-structural-typing.md:64` (block lines 1 to 12 of 12); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 10: A silent null object (Contracts and cleanup)

- Claim: a null object turns a missing carrier into a success that carries no information.
- Chapter: 09, "Protocol, duck typing, and structural typing with mypy" (`_docs/09-protocol-and-structural-typing.md`).
- `09-protocol-and-structural-typing.md:93`: `grep -nF -- 'A null object turns "no carrier" into a success that carries no information.' _docs/09-protocol-and-structural-typing.md`
- `09-protocol-and-structural-typing.md:95`: `grep -nF -- 'A null object is right where doing nothing is the correct answer.' _docs/09-protocol-and-structural-typing.md`
- Witness tests, each defined once:
  - `test_a_null_gateway_hides_a_lost_booking` (`examples/09-protocol-and-structural-typing/tests/test_absence.py:36`, 1 definition)
  - `test_mypy_accepts_a_null_gateway` (`examples/09-protocol-and-structural-typing/tests/test_static.py:314`, 1 definition)
  - `test_no_discount_is_a_null_object_that_loses_nothing` (`examples/09-protocol-and-structural-typing/tests/test_absence.py:42`, 1 definition)
- Code: `examples/09-protocol-and-structural-typing/tests/test_absence.py` lines 18 to 22 (5 lines, longest 80 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 18, exact, 0 leading spaces): `class _NullGateway:`
  - Last line (22): `return ""`
  - Contiguous run of the fence opening at `09-protocol-and-structural-typing.md:85` (block lines 1 to 5 of 5); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. range is a test fixture (`_NullGateway`); the notes must say so.

### Slide 11: The carrier lookup (Contracts and cleanup)

- Claim: a Protocol is compared where a value is used and an ABC where a subclass is built.
- Chapter: 09, "Protocol, duck typing, and structural typing with mypy" (`_docs/09-protocol-and-structural-typing.md`).
- `09-protocol-and-structural-typing.md:162`: `grep -nF -- '"Interface" needs disambiguating' _docs/09-protocol-and-structural-typing.md`
- `09-protocol-and-structural-typing.md:32`: `grep -nF -- 'The comparison happens where the value is used' _docs/09-protocol-and-structural-typing.md`
- `09-protocol-and-structural-typing.md:191`: `grep -nF -- 'Subclassing a Protocol explicitly is a third thing.' _docs/09-protocol-and-structural-typing.md`
- `09-protocol-and-structural-typing.md:195`: `grep -nF -- 'Choose by who owns the need' _docs/09-protocol-and-structural-typing.md`
- `09-protocol-and-structural-typing.md:123`: `grep -nF -- '`test_a_sentinel_separates_not_given_from_none` checks the branches' _docs/09-protocol-and-structural-typing.md`
- Witness tests, each defined once:
  - `test_mypy_checks_protocols_at_use_and_abcs_at_construction` (`examples/09-protocol-and-structural-typing/tests/test_static.py:266`, 1 definition)
  - `test_abc_refuses_an_incomplete_subclass_at_construction` (`examples/09-protocol-and-structural-typing/tests/test_disambiguate.py:21`, 1 definition)
  - `test_both_carriers_satisfy_the_protocol_one_by_inheritance` (`examples/09-protocol-and-structural-typing/tests/test_disambiguate.py:26`, 1 definition)
  - `test_explicit_protocol_subclass_is_nominal_and_still_instantiable` (`examples/09-protocol-and-structural-typing/tests/test_disambiguate.py:41`, 1 definition)
  - `test_runtime_checkable_checks_names_only` (`examples/09-protocol-and-structural-typing/tests/test_runtime_checkable.py:45`, 1 definition)
- Figure: `diagrams/09-protocol-and-structural-typing.svg`, PNG `presentation/png/09-protocol-and-structural-typing.png` (see Figure census).
- Disposition: **kept**. figure 09 passes the census after F2.

### Slide 12: Exits from a block (Contracts and cleanup)

- Claim: a manifest write has two exits and neither may leak or lie.
- Chapter: 10, "Context managers: deterministic cleanup" (`_docs/10-context-managers.md`).
- `10-context-managers.md:24`: `grep -nF -- 'The first failure is a leak and the second is a lie.' _docs/10-context-managers.md`
- Witness tests, each defined once:
  - `test_without_with_an_exception_leaves_the_handle_open` (`examples/10-context-managers/tests/test_writer.py:52`, 1 definition)
  - `test_writer_commits_only_on_success` (`examples/10-context-managers/tests/test_writer.py:80`, 1 definition)
  - `test_writer_closes_and_discards_on_an_exception` (`examples/10-context-managers/tests/test_writer.py:66`, 1 definition)
- Figure: `diagrams/10-context-managers.svg`, PNG `presentation/png/10-context-managers.png` (see Figure census).
- Disposition: **kept**. figure 10 passes the census after F3.

### Slide 13: Commit or discard (Contracts and cleanup)

- Claim: `__exit__` commits on success and discards on an exception; returning nothing lets the failure be seen.
- Chapter: 10, "Context managers: deterministic cleanup" (`_docs/10-context-managers.md`).
- `10-context-managers.md:36`: `grep -nF -- 'This pattern survives.' _docs/10-context-managers.md`
- `10-context-managers.md:74`: `grep -nF -- 'Returning nothing is the decision to let the failure be seen.' _docs/10-context-managers.md`
- `10-context-managers.md:151`: `grep -nF -- 'A truthy `__exit__` return swallows the exception' _docs/10-context-managers.md`
- `10-context-managers.md:153`: `grep -nF -- '`contextlib.suppress` states it narrowly.' _docs/10-context-managers.md`
- Witness tests, each defined once:
  - `test_writer_is_single_use` (`examples/10-context-managers/tests/test_writer.py:95`, 1 definition)
  - `test_a_truthy_exit_swallows_the_exception` (`examples/10-context-managers/tests/test_semantics.py:24`, 1 definition)
  - `test_suppress_swallows_only_the_named_exception` (`examples/10-context-managers/tests/test_semantics.py:32`, 1 definition)
  - `test_mypy_reads_exit_return_type_for_reachability` (`examples/10-context-managers/tests/test_static.py:80`, 1 definition)
- Code: `examples/10-context-managers/src/context_managers/manifest.py` lines 61 to 74 (14 lines, longest 64 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 61, exact, 4 leading spaces): `def __exit__(`
  - Last line (74): `self._partial.unlink(missing_ok=True)`
  - Contiguous run of the fence opening at `10-context-managers.md:47` (block lines 8 to 21 of 21); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed (range is lines 8 to 21 of a 21-line fence).

### Slide 14: Try in the generator form (Contracts and cleanup)

- Claim: in the generator form `try` is not optional, and only a test that raises mid-write guards it.
- Chapter: 10, "Context managers: deterministic cleanup" (`_docs/10-context-managers.md`).
- `10-context-managers.md:120`: `grep -nF -- 'That'"'"'s why `try` isn'"'"'t optional.' _docs/10-context-managers.md`
- `10-context-managers.md:120`: `grep -nF -- 'The type checker has nothing to say, so a test that raises mid-write is the only guard.' _docs/10-context-managers.md`
- `10-context-managers.md:145`: `grep -nF -- 'maintains a stack of registered callbacks' _docs/10-context-managers.md`
- `10-context-managers.md:147`: `grep -nF -- 'the contract says nothing about a failure at commit time' _docs/10-context-managers.md`
- Witness tests, each defined once:
  - `test_the_generator_form_needs_try` (`examples/10-context-managers/tests/test_writer.py:110`, 1 definition)
  - `test_mypy_cannot_see_a_missing_try` (`examples/10-context-managers/tests/test_static.py:161`, 1 definition)
  - `test_exit_stack_unwinds_entered_writers_in_reverse_order` (`examples/10-context-managers/tests/test_stack.py:12`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_a_context_manager_decorating_a_generator_spans_iteration` (`examples/10-context-managers/tests/test_semantics.py:39`, 1 definition)
- Code: `examples/10-context-managers/src/context_managers/manifest.py` lines 77 to 90 (14 lines, longest 81 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 77, exact, 0 leading spaces): `@contextmanager`
  - Last line (90): `partial.replace(path)`
  - Contiguous run of the fence opening at `10-context-managers.md:102` (block lines 1 to 14 of 14); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed; the stack contract is worded as P1 narrowed it (a failed open discards the partials; each writer commits on its own on success).

### Slide 15: divider (Decorators done right)

- Claim: -
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 16: What wraps copies (Decorators done right)

- Claim: `functools.wraps` makes the replacement look like the original; mypy reads the declared type, not `__wrapped__`.
- Chapter: 26, "Decorators done right" (`_docs/26-decorators-done-right.md`).
- `26-decorators-done-right.md:38`: `grep -nF -- '`functools.wraps` makes the replacement look like the original.' _docs/26-decorators-done-right.md`
- `26-decorators-done-right.md:72`: `grep -nF -- 'mypy doesn'"'"'t read `__wrapped__`.' _docs/26-decorators-done-right.md`
- `26-decorators-done-right.md:78`: `grep -nF -- 'Runtime tools disagree, and here `wraps` is the cause.' _docs/26-decorators-done-right.md`
- Witness tests, each defined once:
  - `test_wraps_keeps_the_name_qualname_doc_and_module` (`examples/26-decorators-done-right/tests/test_wraps.py:47`, 1 definition)
  - `test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring` (`examples/26-decorators-done-right/tests/test_wraps.py:57`, 1 definition)
  - `test_inspect_signature_follows_wrapped_to_the_original_parameters` (`examples/26-decorators-done-right/tests/test_wraps.py:69`, 1 definition)
  - `test_wrapped_points_one_level_down_and_unwrap_reaches_the_original` (`examples/26-decorators-done-right/tests/test_wraps.py:88`, 1 definition)
  - `test_mypy_keeps_the_signature_through_a_wrapper_without_wraps` (`examples/26-decorators-done-right/tests/test_static.py:156`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_a_decorator_that_supplies_an_argument_reports_the_original_parameters` (`examples/26-decorators-done-right/tests/test_wraps.py:129`, 1 definition)
  - `test_partial_reports_the_parameters_that_remain` (`examples/26-decorators-done-right/tests/test_wraps.py:141`, 1 definition)
- Code: `examples/26-decorators-done-right/src/decorators_done_right/rendering.py` lines 28 to 37 (10 lines, longest 60 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 28, exact, 4 leading spaces): `def decorate(func: Callable[P, R]) -> Callable[P, R]:`
  - Last line (37): `return wrapper`
  - Contiguous run of the fence opening at `26-decorators-done-right.md:40` (block lines 6 to 15 of 17); identical line for line, so byte-exact with the chapter.
- Disposition: **reworded**. two `partial` witnesses named in the census (the plan said 'two tests'); range is a contiguous run of a 17-line fence.

### Slide 17: Factories refusing bare use (Decorators done right)

- Claim: a decorator factory's call runs at definition, and so does any mistake in it.
- Chapter: 26, "Decorators done right" (`_docs/26-decorators-done-right.md`).
- `26-decorators-done-right.md:82`: `grep -nF -- 'The call runs at definition, and so does any mistake in it.' _docs/26-decorators-done-right.md`
- Witness tests, each defined once:
  - `test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator` (`examples/26-decorators-done-right/tests/test_factories.py:107`, 1 definition)
  - `test_a_keyword_only_factory_used_bare_fails_at_definition` (`examples/26-decorators-done-right/tests/test_factories.py:122`, 1 definition)
  - `test_mypy_refuses_a_keyword_only_factory_used_bare` (`examples/26-decorators-done-right/tests/test_static.py:181`, 1 definition)
- Code: `examples/26-decorators-done-right/src/decorators_done_right/rendering.py` lines 42 to 50 (9 lines, longest 92 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 42, exact, 0 leading spaces): `def cached_for[**P, R](`
  - Last line (50): `raise ValueError(f"seconds must be positive, got {seconds}")`
  - Contiguous run of the fence opening at `26-decorators-done-right.md:125` (block lines 1 to 9 of 27); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 18: Where the timer sits (Decorators done right)

- Claim: stacking order decides whether a cache hit is timed.
- Chapter: 26, "Decorators done right" (`_docs/26-decorators-done-right.md`).
- `26-decorators-done-right.md:165`: `grep -nF -- 'The inside order measures the renderer. The outside order measures what the caller waited, hits included.' _docs/26-decorators-done-right.md`
- `26-decorators-done-right.md:205`: `grep -nF -- 'A class decorator that doesn'"'"'t return the class binds the name to `None`.' _docs/26-decorators-done-right.md`
- `26-decorators-done-right.md:209`: `grep -nF -- 'A function wrapper works on a method unchanged.' _docs/26-decorators-done-right.md`
- Witness tests, each defined once:
  - `test_stacking_order_decides_whether_a_cache_hit_is_timed` (`examples/26-decorators-done-right/tests/test_factories.py:135`, 1 definition)
  - `test_cached_for_renders_again_once_the_window_has_passed` (`examples/26-decorators-done-right/tests/test_factories.py:42`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class` (`examples/26-decorators-done-right/tests/test_classes.py:38`, 1 definition)
  - `test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none` (`examples/26-decorators-done-right/tests/test_classes.py:70`, 1 definition)
  - `test_functools_cache_on_a_method_keeps_the_instance_alive` (`examples/26-decorators-done-right/tests/test_methods.py:49`, 1 definition)
- Code: none; a bullet slide whose claims are the sentences and tests above.
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 19: divider (Attribute access)

- Claim: -
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 20: One validator, many fields (Attribute access)

- Claim: a descriptor puts a rule in one place for any number of fields.
- Chapter: 27, "Descriptors and properties" (`_docs/27-descriptors-and-properties.md`).
- `27-descriptors-and-properties.md:79`: `grep -nF -- 'A descriptor puts the rule in one place and lets any number of fields use it.' _docs/27-descriptors-and-properties.md`
- `27-descriptors-and-properties.md:75`: `grep -nF -- 'The trouble is the third copy.' _docs/27-descriptors-and-properties.md`
- `27-descriptors-and-properties.md:201`: `grep -nF -- 'Skip the descriptor when one field in one class needs a rule' _docs/27-descriptors-and-properties.md`
- Witness tests, each defined once:
  - `test_every_field_form_validates_the_same_extents` (`examples/27-descriptors-and-properties/tests/test_fields.py:33`, 1 definition)
  - `test_a_copy_pasted_property_validator_drifts` (`examples/27-descriptors-and-properties/tests/test_fields.py:126`, 1 definition)
  - `test_one_descriptor_class_validates_every_field` (`examples/27-descriptors-and-properties/tests/test_fields.py:95`, 1 definition)
  - `test_set_name_gives_each_field_its_own_storage` (`examples/27-descriptors-and-properties/tests/test_fields.py:87`, 1 definition)
- Code: `examples/27-descriptors-and-properties/src/descriptors_properties/fields.py` lines 29 to 38 (10 lines, longest 81 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 29, exact, 4 leading spaces): `def __get__(self, instance: object | None, owner: type) -> Decimal:`
  - Last line (38): `vars(instance)[self.private_name] = value`
  - Contiguous run of the fence opening at `27-descriptors-and-properties.md:82` (block lines 14 to 23 of 23); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed; see Corrections for an unrelated message observation in the excerpt.

### Slide 21: Costs of cached_property (Attribute access)

- Claim: the cache lives in the instance dictionary and has four costs.
- Chapter: 27, "Descriptors and properties" (`_docs/27-descriptors-and-properties.md`).
- `27-descriptors-and-properties.md:190`: `grep -nF -- 'The cache lives in the instance dictionary, and it has four costs.' _docs/27-descriptors-and-properties.md`
- `27-descriptors-and-properties.md:194`: `grep -nF -- 'Over mutable state it goes stale.' _docs/27-descriptors-and-properties.md`
- `27-descriptors-and-properties.md:131`: `grep -nF -- 'The descriptor wins (`test_a_data_descriptor_takes_precedence_over_the_instance_dict`)' _docs/27-descriptors-and-properties.md`
- Witness tests, each defined once:
  - `test_chargeable_weight_is_computed_on_first_access_and_stored` (`examples/27-descriptors-and-properties/tests/test_cached.py:18`, 1 definition)
  - `test_cached_property_needs_an_instance_dict` (`examples/27-descriptors-and-properties/tests/test_cached.py:49`, 1 definition)
  - `test_a_frozen_dataclass_cannot_clear_a_cached_property` (`examples/27-descriptors-and-properties/tests/test_cached.py:54`, 1 definition)
  - `test_a_cached_property_over_mutable_state_goes_stale` (`examples/27-descriptors-and-properties/tests/test_cached.py:81`, 1 definition)
  - `test_a_cached_property_getter_can_run_twice_under_threads` (`examples/27-descriptors-and-properties/tests/test_cached.py:110`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_a_data_descriptor_takes_precedence_over_the_instance_dict` (`examples/27-descriptors-and-properties/tests/test_lookup.py:11`, 1 definition)
  - `test_an_instance_dict_entry_takes_precedence_over_cached_property` (`examples/27-descriptors-and-properties/tests/test_lookup.py:21`, 1 definition)
- Code: `examples/27-descriptors-and-properties/src/descriptors_properties/cargo.py` lines 50 to 53 (4 lines, longest 84 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 50, exact, 4 leading spaces): `@cached_property`
  - Last line (53): `return max(self.kilograms, self.dimensions.volume_m3 * VOLUMETRIC_KG_PER_M3)`
  - Contiguous run of the fence opening at `27-descriptors-and-properties.md:180` (block lines 1 to 4 of 4); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 22: A self-loading history (Attribute access)

- Claim: a history can load itself on first read through `__getattr__` and an allow-list, with no stand-in object.
- Chapter: 30, "Dynamic attributes: __getattr__ and Proxy as a feature" (`_docs/30-dynamic-attributes-and-proxy.md`).
- `30-dynamic-attributes-and-proxy.md:22`: `grep -nF -- 'That'"'"'s interception with no surrogate' _docs/30-dynamic-attributes-and-proxy.md`
- `30-dynamic-attributes-and-proxy.md:24`: `grep -nF -- 'What stays design is which names may load' _docs/30-dynamic-attributes-and-proxy.md`
- `30-dynamic-attributes-and-proxy.md:124`: `grep -nF -- 'The set is also the defence against the opposite mistake.' _docs/30-dynamic-attributes-and-proxy.md`
- Witness tests, each defined once:
  - `test_every_history_form_loads_once_for_every_field` (`examples/30-dynamic-attributes-and-proxy/tests/test_history.py:50`, 1 definition)
  - `test_nothing_is_loaded_until_a_field_is_read` (`examples/30-dynamic-attributes-and-proxy/tests/test_history.py:78`, 1 definition)
  - `test_a_loaded_history_reads_its_fields_from_the_instance_dict` (`examples/30-dynamic-attributes-and-proxy/tests/test_history.py:84`, 1 definition)
  - `test_getattr_runs_only_when_normal_lookup_fails` (`examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py:87`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_a_misspelt_field_suggests_the_declared_name_through_dir` (`examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py:209`, 1 definition)
- Code: `examples/30-dynamic-attributes-and-proxy/src/dynamic_attributes/tracking.py` lines 75 to 84 (10 lines, longest 93 characters, tabs 0, trailing whitespace 0, common indent 8).
  - Anchor (line 75, exact, 8 leading spaces): `if name not in _LAZY:`
  - Last line (84): `return vars(self)[name]`
  - Contiguous run of the fence opening at `30-dynamic-attributes-and-proxy.md:39` (block lines 16 to 25 of 25); identical line for line, so byte-exact with the chapter.
- Disposition: **reworded**. the plan's claim uses the book's bucket vocabulary ('where Proxy is disambiguated'); standalone wording below. Range confirmed.

### Slide 23: The recursion trap (Attribute access)

- Claim: `copy` builds an instance without running `__init__`, and a careless `__getattr__` then recurses.
- Chapter: 30, "Dynamic attributes: __getattr__ and Proxy as a feature" (`_docs/30-dynamic-attributes-and-proxy.md`).
- `30-dynamic-attributes-and-proxy.md:120`: `grep -nF -- '`copy` builds such an instance.' _docs/30-dynamic-attributes-and-proxy.md`
- `30-dynamic-attributes-and-proxy.md:147`: `grep -nF -- 'Special methods are looked up on the type.' _docs/30-dynamic-attributes-and-proxy.md`
- `30-dynamic-attributes-and-proxy.md:149`: `grep -nF -- '`hasattr(history, "status")` is a read' _docs/30-dynamic-attributes-and-proxy.md`
- Witness tests, each defined once:
  - `test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute` (`examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py:134`, 1 definition)
  - `test_each_fix_keeps_getattr_out_of_recursion` (`examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py:159`, 1 definition)
  - `test_copy_keeps_a_history_before_and_after_loading` (`examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py:142`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_hasattr_loads_the_history` (`examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py:223`, 1 definition)
  - `test_implicit_special_method_lookup_bypasses_getattr` (`examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py:174`, 1 definition)
- Code: `examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py` lines 35 to 44 (10 lines, longest 94 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 35, exact, 0 leading spaces): `class _SelfHealing:`
  - Last line (44): `return value`
  - Contiguous run of the fence opening at `30-dynamic-attributes-and-proxy.md:104` (block lines 1 to 10 of 10); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed; range is a test-local class.

### Slide 24: divider (Dispatch and registries)

- Claim: -
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 25: Dispatch by registered type (Dispatch and registries)

- Claim: for an open set of kinds, one generic function replaces the Visitor, and the fallback is a design decision.
- Chapter: 28, "singledispatch: the Visitor the language gives you" (`_docs/28-singledispatch.md`).
- `28-singledispatch.md:22`: `grep -nF -- 'For an open set of kinds like this one it dissolves into a single generic function' _docs/28-singledispatch.md`
- `28-singledispatch.md:56`: `grep -nF -- 'The registrations carry no class argument because the annotation supplies it.' _docs/28-singledispatch.md`
- `28-singledispatch.md:66`: `grep -nF -- 'An unregistered kind reaches the `object` implementation' _docs/28-singledispatch.md`
- Witness tests, each defined once:
  - `test_every_fallback_form_gives_registered_commodities_their_codes` (`examples/28-singledispatch/tests/test_tariff.py:27`, 1 definition)
  - `test_the_most_specific_registration_wins` (`examples/28-singledispatch/tests/test_tariff.py:44`, 1 definition)
  - `test_an_unregistered_subclass_gets_its_base_class_code` (`examples/28-singledispatch/tests/test_tariff.py:51`, 1 definition)
  - `test_a_raising_fallback_names_an_unregistered_kind` (`examples/28-singledispatch/tests/test_tariff.py:33`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently` (`examples/28-singledispatch/tests/test_tariff.py:38`, 1 definition)
- Code: `examples/28-singledispatch/src/singledispatch_visitor/tariff.py` lines 17 to 31 (15 lines, longest 75 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 17, exact, 0 leading spaces): `@singledispatch`
  - Last line (31): `return "2101.11"`
  - Contiguous run of the fence opening at `28-singledispatch.md:38` (block lines 1 to 15 of 15); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 26: Registration from another module (Dispatch and registries)

- Claim: another module extends the set when it is imported, and a union fallback closes it for mypy.
- Chapter: 28, "singledispatch: the Visitor the language gives you" (`_docs/28-singledispatch.md`).
- `28-singledispatch.md:121`: `grep -nF -- 'The design question is who imports the extension' _docs/28-singledispatch.md`
- `28-singledispatch.md:103`: `grep -nF -- 'A union fallback is what closes the set.' _docs/28-singledispatch.md`
- `28-singledispatch.md:121`: `grep -nF -- 'PEP 443, by' _docs/28-singledispatch.md`
- Witness tests, each defined once:
  - `test_another_module_extends_the_set_when_it_is_imported` (`examples/28-singledispatch/tests/test_registration.py:103`, 1 definition)
  - `test_the_registry_is_read_only` (`examples/28-singledispatch/tests/test_tariff.py:70`, 1 definition)
  - `test_mypy_refuses_a_kind_outside_a_union_fallback` (`examples/28-singledispatch/tests/test_static.py:144`, 1 definition)
  - `test_mypy_checks_calls_and_registrations_against_the_fallback` (`examples/28-singledispatch/tests/test_static.py:135`, 1 definition)
- Code: `examples/28-singledispatch/src/singledispatch_visitor/dangerous_goods.py` lines 8 to 14 (7 lines, longest 64 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 8, exact, 0 leading spaces): `from singledispatch_visitor.commodities import LithiumIonBattery`
  - Last line (14): `return "8507.60"`
  - Contiguous run of the fence opening at `28-singledispatch.md:111` (block lines 1 to 7 of 7); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 27: Registration by class keyword (Dispatch and registries)

- Claim: a class keyword registers a subclass at definition and refuses a bad one before the registry is touched.
- Chapter: 29, "Metaclasses, __init_subclass__, and registries" (`_docs/29-metaclasses-init-subclass-and-registries.md`).
- `29-metaclasses-init-subclass-and-registries.md:22`: `grep -nF -- 'so the pattern dissolves' _docs/29-metaclasses-init-subclass-and-registries.md`
- `29-metaclasses-init-subclass-and-registries.md:89`: `grep -nF -- 'The hook runs before the registry is touched' _docs/29-metaclasses-init-subclass-and-registries.md`
- `29-metaclasses-init-subclass-and-registries.md:99`: `grep -nF -- 'imports no carrier module' _docs/29-metaclasses-init-subclass-and-registries.md`
- Witness tests, each defined once:
  - `test_every_registry_form_books_through_the_registered_carrier` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py:119`, 1 definition)
  - `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py:130`, 1 definition)
  - `test_the_carrier_registry_is_a_read_only_view` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py:162`, 1 definition)
  - `test_isabstract_sees_abstractness_inside_init_subclass` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py:189`, 1 definition)
  - `test_mypy_reports_a_misspelt_class_keyword` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py:170`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_a_carrier_module_registers_only_when_it_is_imported` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py:251`, 1 definition)
- Code: `examples/29-metaclasses-init-subclass-and-registries/src/carrier_registry/carriers.py` lines 44 to 58 (15 lines, longest 92 characters, tabs 0, trailing whitespace 0, common indent 8).
  - Anchor (line 44, exact, 8 leading spaces): `super().__init_subclass__()`
  - Last line (58): `_CARRIERS[code] = cls`
  - Contiguous run of the fence opening at `29-metaclasses-init-subclass-and-registries.md:38` (block lines 18 to 32 of 32); identical line for line, so byte-exact with the chapter.
- Disposition: **reworded**. range widened from lines 44 to 52 to lines 44 to 58, so the slide shows the registration the claim is about; the plan's range stops before it.

### Slide 28: Metaclass costs (Dispatch and registries)

- Claim: a metaclass costs a conflict and three things mypy does not follow, and pays only for operators on the class.
- Chapter: 29, "Metaclasses, __init_subclass__, and registries" (`_docs/29-metaclasses-init-subclass-and-registries.md`).
- `29-metaclasses-init-subclass-and-registries.md:149`: `grep -nF -- 'What the metaclass costs shows in four places.' _docs/29-metaclasses-init-subclass-and-registries.md`
- `29-metaclasses-init-subclass-and-registries.md:151`: `grep -nF -- 'The other three are mypy'"'"'s' _docs/29-metaclasses-init-subclass-and-registries.md`
- `29-metaclasses-init-subclass-and-registries.md:155`: `grep -nF -- 'The one case where the metaclass earns its cost is an operator on the class object.' _docs/29-metaclasses-init-subclass-and-registries.md`
- `29-metaclasses-init-subclass-and-registries.md:168`: `grep -nF -- 'EnumType is the metaclass for enum enumerations.' _docs/29-metaclasses-init-subclass-and-registries.md`
- `29-metaclasses-init-subclass-and-registries.md:174`: `grep -nF -- 'A metaclass is the wrong tool' _docs/29-metaclasses-init-subclass-and-registries.md`
- Witness tests, each defined once:
  - `test_a_second_metaclass_conflicts_with_the_bases_metaclass` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py:25`, 1 definition)
  - `test_a_metaclass_derived_from_abcmeta_resolves_the_conflict` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py:31`, 1 definition)
  - `test_mypy_does_not_check_metaclass_class_keywords` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py:178`, 1 definition)
  - `test_mypy_types_a_class_called_from_a_metaclass_registry_as_any` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py:212`, 1 definition)
  - `test_only_a_metaclass_gives_the_class_object_operators` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py:37`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_mypy_refuses_self_in_a_metaclass_new` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py:201`, 1 definition)
- Disposition: **reworded**. the chapter's 'four places' need `test_mypy_refuses_self_in_a_metaclass_new`, which the plan omitted; the table has four cost rows and one row for what a metaclass buys.

### Slide 29: A narrow try (Dispatch and registries)

- Claim: the `try` holds the lookup and nothing else.
- Chapter: 31, "Shortcut patterns: dict dispatch, function tables, and EAFP" (`_docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`).
- `31-shortcut-patterns-dict-dispatch-and-eafp.md:36`: `grep -nF -- 'What dissolves is the structure built around' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`
- `31-shortcut-patterns-dict-dispatch-and-eafp.md:87`: `grep -nF -- 'The `try` holds the lookup and nothing else.' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`
- `31-shortcut-patterns-dict-dispatch-and-eafp.md:104`: `grep -nF -- 'A handler that'"'"'s too broad turns a bug into a missing value.' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`
- `31-shortcut-patterns-dict-dispatch-and-eafp.md:52`: `grep -nF -- 'What mypy 2.4.1 checks is the shape of the table.' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`
- Witness tests, each defined once:
  - `test_an_issuers_own_key_error_passes_through_issue` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py:80`, 1 definition)
  - `test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py:86`, 1 definition)
  - `test_an_unsupported_kind_raises_unsupported_document_error` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py:66`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_mypy_accepts_a_table_that_misses_a_kind` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_static.py:248`, 1 definition)
  - `test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py:136`, 1 definition)
  - `test_suppress_skips_the_rest_of_its_block_after_the_first_exception` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py:144`, 1 definition)
- Code: `examples/31-shortcut-patterns-dict-dispatch-and-eafp/src/shortcut_patterns/documents.py` lines 58 to 62 (5 lines, longest 81 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 58, exact, 4 leading spaces): `try:`
  - Last line (62): `return issuer(consignment_id)`
  - Contiguous run of the fence opening at `31-shortcut-patterns-dict-dispatch-and-eafp.md:78` (block lines 1 to 5 of 5); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 30: Dispatch tables and EAFP (Dispatch and registries)

- Claim: a table wins when the set is data, and the guarantee of asking forgiveness is one gap.
- Chapter: 31, "Shortcut patterns: dict dispatch, function tables, and EAFP" (`_docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`).
- `31-shortcut-patterns-dict-dispatch-and-eafp.md:65`: `grep -nF -- 'A table wins when the set is data.' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`
- `31-shortcut-patterns-dict-dispatch-and-eafp.md:147`: `grep -nF -- 'The scope of the guarantee is one gap.' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`
- `31-shortcut-patterns-dict-dispatch-and-eafp.md:149`: `grep -nF -- 'On a recorded run on Python 3.15.2 (best of five repeats of one million calls, 2026-11-06)' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`
- Witness tests, each defined once:
  - `test_an_eafp_read_reloads_when_another_thread_evicts_first` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py:82`, 1 definition)
  - `test_two_eafp_readers_that_both_miss_both_load` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py:90`, 1 definition)
  - `test_every_cache_form_reads_loads_and_evicts_the_same_way` (`examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py:58`, 1 definition)
- Figure: `diagrams/31-shortcut-patterns-dict-dispatch-and-eafp.svg`, PNG `presentation/png/31-shortcut-patterns-dict-dispatch-and-eafp.png` (see Figure census).
- Disposition: **kept**. figure 31 passes the census after F7; its look-first box restates a claim Deck 101 makes (see the boundary check), so the notes lead with the EAFP read.

### Slide 31: divider (Pattern misuse)

- Claim: -
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 32: A quote as a function (Pattern misuse)

- Claim: two forms quote one table, so what differs is the cost of the structure.
- Chapter: 32, "Anti-patterns and pattern misuse" (`_docs/32-anti-patterns-and-pattern-misuse.md`).
- `32-anti-patterns-and-pattern-misuse.md:62`: `grep -nF -- 'The behaviour is identical, so what differs is the cost of the structure.' _docs/32-anti-patterns-and-pattern-misuse.md`
- `32-anti-patterns-and-pattern-misuse.md:22`: `grep -nF -- 'When the forces leave and the structure stays, the price is still paid on each change.' _docs/32-anti-patterns-and-pattern-misuse.md`
- `32-anti-patterns-and-pattern-misuse.md:84`: `grep -nF -- 'A getter and setter pair is a promise that the field might need behaviour later.' _docs/32-anti-patterns-and-pattern-misuse.md`
- `32-anti-patterns-and-pattern-misuse.md:109`: `grep -nF -- 'The error is `FrozenInstanceError`' _docs/32-anti-patterns-and-pattern-misuse.md`
- Witness tests, each defined once:
  - `test_every_rating_form_quotes_the_same_table` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_forms.py:18`, 1 definition)
  - `test_every_rating_form_refuses_an_unknown_zone` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_forms.py:26`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_an_accessor_consignment_has_no_value_equality` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py:20`, 1 definition)
  - `test_a_setter_lets_a_quoted_consignment_change_its_quote` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py:28`, 1 definition)
  - `test_a_frozen_consignment_refuses_assignment` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py:38`, 1 definition)
- Code: `examples/32-anti-patterns-and-pattern-misuse/src/pattern_misuse/rating.py` lines 49 to 57 (9 lines, longest 95 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 49, exact, 0 leading spaces): `def quote(consignment: Consignment, tariff: Tariff) -> RateQuote:`
  - Last line (57): `return RateQuote(consignment.id, Money(net + tax, tariff.currency))`
  - Contiguous run of the fence opening at `32-anti-patterns-and-pattern-misuse.md:36` (block lines 1 to 9 of 9); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 33: A misplaced Visitor (Pattern misuse)

- Claim: a Visitor over a growing set breaks at run time on a new charge, and declaring the method moves the failure.
- Chapter: 32, "Anti-patterns and pattern misuse" (`_docs/32-anti-patterns-and-pattern-misuse.md`).
- `32-anti-patterns-and-pattern-misuse.md:78`: `grep -nF -- 'Declaring the method on the visitor base is the fix, and it moves the failure.' _docs/32-anti-patterns-and-pattern-misuse.md`
- `32-anti-patterns-and-pattern-misuse.md:78`: `grep -nF -- 'A Visitor suits a fixed set of kinds that gains operations.' _docs/32-anti-patterns-and-pattern-misuse.md`
- Witness tests, each defined once:
  - `test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py:157`, 1 definition)
  - `test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py:165`, 1 definition)
  - `test_mypy_reports_a_visitor_missing_a_new_visit_method` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_static.py:157`, 1 definition)
- Code: none; a bullet slide whose claims are the sentences and tests above.
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 34: A located dependency (Pattern misuse)

- Claim: passing the tariff as a parameter turns the unseen failure into the seen one.
- Chapter: 32, "Anti-patterns and pattern misuse" (`_docs/32-anti-patterns-and-pattern-misuse.md`).
- `32-anti-patterns-and-pattern-misuse.md:129`: `grep -nF -- 'Passing the tariff as a parameter turns the unseen failure into the seen one.' _docs/32-anti-patterns-and-pattern-misuse.md`
- `32-anti-patterns-and-pattern-misuse.md:133`: `grep -nF -- 'The function wins on the forces in the one-carrier case' _docs/32-anti-patterns-and-pattern-misuse.md`
- Witness tests, each defined once:
  - `test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py:43`, 1 definition)
  - `test_a_located_engine_quotes_once_its_tariff_is_registered` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py:50`, 1 definition)
  - `test_mypy_does_not_see_a_missing_registration` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_static.py:143`, 1 definition)
  - `test_mypy_reports_a_missing_tariff_argument` (`examples/32-anti-patterns-and-pattern-misuse/tests/test_static.py:150`, 1 definition)
- Code: `examples/32-anti-patterns-and-pattern-misuse/tests/conftest.py` lines 175 to 179 (5 lines, longest 78 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 175, exact, 4 leading spaces): `def quote(self, consignment: Consignment) -> RateQuote:`
  - Last line (179): `return quote(consignment, tariff)`
  - Contiguous run of the fence opening at `32-anti-patterns-and-pattern-misuse.md:118` (block lines 1 to 5 of 5); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed; range is a test-local class.

### Slide 35: divider (Concurrency and the patterns)

- Claim: -
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide.

### Slide 36: Build and GIL state (Concurrency and the patterns)

- Claim: two functions are needed because the build and the running state can differ.
- Chapter: 37, "The GIL and performance" (`_docs/37-the-gil-and-performance.md`).
- `37-the-gil-and-performance.md:48`: `grep -nF -- 'Two functions are needed because the build and the running state can differ.' _docs/37-the-gil-and-performance.md`
- Witness tests, each defined once:
  - `test_the_build_flag_and_the_runtime_gil_state_agree` (`examples/37-the-gil-and-performance/tests/test_build.py:11`, 1 definition)
  - `test_sys_version_names_the_free_threading_build_only_on_that_build` (`examples/37-the-gil-and-performance/tests/test_build.py:16`, 1 definition)
  - `test_mypy_types_the_build_flag_as_any` (`examples/37-the-gil-and-performance/tests/test_static.py:46`, 1 definition)
- Code: `examples/37-the-gil-and-performance/src/gil_and_performance/build.py` lines 11 to 19 (9 lines, longest 87 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 11, exact, 0 leading spaces): `def gil_disabled_build() -> bool:`
  - Last line (19): `return sys._is_gil_enabled()`
  - Contiguous run of the fence opening at `37-the-gil-and-performance.md:35` (block lines 1 to 9 of 9); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed; both builds are tested in CI.

### Slide 37: Locks over read and write (Concurrency and the patterns)

- Claim: the GIL never promised that read and write run together; a lock over both fixes it.
- Chapter: 37, "The GIL and performance" (`_docs/37-the-gil-and-performance.md`).
- `37-the-gil-and-performance.md:91`: `grep -nF -- 'because it never promised that the steps run together' _docs/37-the-gil-and-performance.md`
- `37-the-gil-and-performance.md:93`: `grep -nF -- 'The fix is a lock that covers the read as well as the write.' _docs/37-the-gil-and-performance.md`
- `37-the-gil-and-performance.md:24`: `grep -nF -- 'lost an update in none on the default build' _docs/37-the-gil-and-performance.md`
- Witness tests, each defined once:
  - `test_two_threads_parked_between_read_and_write_take_the_same_slot` (`examples/37-the-gil-and-performance/tests/test_stowage.py:28`, 1 definition)
  - `test_a_lock_across_read_and_write_gives_each_thread_its_own_slot` (`examples/37-the-gil-and-performance/tests/test_stowage.py:46`, 1 definition)
  - `test_an_attribute_increment_is_a_separate_load_add_and_store` (`examples/37-the-gil-and-performance/tests/test_stowage.py:39`, 1 definition)
- Figure: `diagrams/37-the-gil-and-performance.svg`, PNG `presentation/png/37-the-gil-and-performance.png` (see Figure census).
- Disposition: **kept**. figure 37 passes the census after F9; the lost-update counts are now sourced (P12 landed).

### Slide 38: What a pool shares (Concurrency and the patterns)

- Claim: pools return the serial loop's answers; what differs is what the workers can see.
- Chapter: 37, "The GIL and performance" (`_docs/37-the-gil-and-performance.md`).
- `37-the-gil-and-performance.md:122`: `grep -nF -- 'What differs is what the workers can see.' _docs/37-the-gil-and-performance.md`
- `37-the-gil-and-performance.md:197`: `grep -nF -- 'Two loops on one build moved in opposite directions, so measure your loop.' _docs/37-the-gil-and-performance.md`
- Witness tests, each defined once:
  - `test_every_pool_rates_the_batch_as_the_serial_loop_does` (`examples/37-the-gil-and-performance/tests/test_pools.py:22`, 1 definition)
  - `test_threads_share_the_argument_and_processes_and_interpreters_copy_it` (`examples/37-the-gil-and-performance/tests/test_pools.py:32`, 1 definition)
  - `test_a_process_pool_cannot_send_a_lambda` (`examples/37-the-gil-and-performance/tests/test_pools.py:45`, 1 definition)
- Code: `examples/37-the-gil-and-performance/src/gil_and_performance/pools.py` lines 18 to 33 (16 lines, longest 85 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 18, exact, 0 leading spaces): `# A class cannot stand in here: mypy rejects calling type[Executor] with max_workers.`
  - Last line (33): `return list(executor.map(quote, batch))`
  - Contiguous run of the fence opening at `37-the-gil-and-performance.md:102` (block lines 1 to 16 of 16); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 39: A coroutine as a value (Concurrency and the patterns)

- Claim: a quote that is assigned and never awaited does not fail where it was written.
- Chapter: 38, "asyncio and the patterns" (`_docs/38-asyncio-and-the-patterns.md`).
- `38-asyncio-and-the-patterns.md:25`: `grep -nF -- 'A quote that is assigned and never awaited doesn'"'"'t fail where it was written.' _docs/38-asyncio-and-the-patterns.md`
- `38-asyncio-and-the-patterns.md:40`: `grep -nF -- 'A call whose result is dropped gets `[unused-coroutine]`' _docs/38-asyncio-and-the-patterns.md`
- `38-asyncio-and-the-patterns.md:44`: `grep -nF -- 'The second edge is the switch point.' _docs/38-asyncio-and-the-patterns.md`
- Witness tests, each defined once:
  - `test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote` (`examples/38-asyncio-and-the-patterns/tests/test_await.py:16`, 1 definition)
  - `test_a_quote_that_is_never_awaited_warns_when_it_is_collected` (`examples/38-asyncio-and-the-patterns/tests/test_await.py:27`, 1 definition)
  - `test_mypy_reports_a_quote_returned_without_await` (`examples/38-asyncio-and-the-patterns/tests/test_static.py:90`, 1 definition)
  - `test_mypy_accepts_a_coroutine_bound_to_underscore` (`examples/38-asyncio-and-the-patterns/tests/test_static.py:121`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_an_await_between_read_and_write_double_books_a_slot` (`examples/38-asyncio-and-the-patterns/tests/test_stowage.py:17`, 1 definition)
  - `test_an_asyncio_lock_gives_each_task_its_own_slot` (`examples/38-asyncio-and-the-patterns/tests/test_stowage.py:31`, 1 definition)
- Code: none; a bullet slide whose claims are the sentences and tests above.
- Disposition: **kept**. claim and witnesses confirmed.

### Slide 40: Closing a feed early (Concurrency and the patterns)

- Claim: leaving `async for` early does not close an async generator; `aclosing` does.
- Chapter: 38, "asyncio and the patterns" (`_docs/38-asyncio-and-the-patterns.md`).
- `38-asyncio-and-the-patterns.md:50`: `grep -nF -- 'Leaving `async for` early doesn'"'"'t close it; `aclosing` does' _docs/38-asyncio-and-the-patterns.md`
- `38-asyncio-and-the-patterns.md:50`: `grep -nF -- 'Dissolves into an async generator' _docs/38-asyncio-and-the-patterns.md`
- Witness tests, each defined once:
  - `test_breaking_out_of_async_for_leaves_the_feed_open` (`examples/38-asyncio-and-the-patterns/tests/test_feed.py:35`, 1 definition)
  - `test_first_departure_closes_the_feed_when_it_stops_early` (`examples/38-asyncio-and-the-patterns/tests/test_feed.py:49`, 1 definition)
  - `test_the_session_closes_the_feed_when_its_task_is_cancelled` (`examples/38-asyncio-and-the-patterns/tests/test_feed.py:72`, 1 definition)
- Code: `examples/38-asyncio-and-the-patterns/src/asyncio_patterns/feed.py` lines 54 to 60 (7 lines, longest 88 characters, tabs 0, trailing whitespace 0, common indent 0).
  - Anchor (line 54, exact, 0 leading spaces): `async def first_departure(feed: CarrierFeed) -> HandlingEvent | None:`
  - Last line (60): `return None`
  - Contiguous run of the fence opening at `38-asyncio-and-the-patterns.md:62` (block lines 8 to 14 of 14); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. the claim sentence is the Iterator row of the chapter's table (line 50); range confirmed.

### Slide 41: Task groups and subscribers (Concurrency and the patterns)

- Claim: a task group is right for quotes and wrong for notifications.
- Chapter: 38, "asyncio and the patterns" (`_docs/38-asyncio-and-the-patterns.md`).
- `38-asyncio-and-the-patterns.md:166`: `grep -nF -- 'A task group is right for quotes, where one failure makes the rest worthless, and wrong for notifications' _docs/38-asyncio-and-the-patterns.md`
- `38-asyncio-and-the-patterns.md:189`: `grep -nF -- 'A worker that waits on `get()` needs a way to be told to stop.' _docs/38-asyncio-and-the-patterns.md`
- Witness tests, each defined once:
  - `test_a_failing_subscriber_does_not_stop_the_others` (`examples/38-asyncio-and-the-patterns/tests/test_signal.py:45`, 1 definition)
  - `test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails` (`examples/38-asyncio-and-the-patterns/tests/test_signal.py:68`, 1 definition)
  - `test_a_failing_carrier_cancels_the_other_quote` (`examples/38-asyncio-and-the-patterns/tests/test_quoting.py:57`, 1 definition)
  - `test_the_first_answer_cancels_the_rest_of_the_group` (`examples/38-asyncio-and-the-patterns/tests/test_quoting.py:75`, 1 definition)
- Notes-only witnesses, each defined once:
  - `test_shutdown_lets_the_worker_drain_the_queue_then_stop` (`examples/38-asyncio-and-the-patterns/tests/test_commands.py:48`, 1 definition)
- Code: `examples/38-asyncio-and-the-patterns/src/asyncio_patterns/signal.py` lines 25 to 31 (7 lines, longest 92 characters, tabs 0, trailing whitespace 0, common indent 4).
  - Anchor (line 25, exact, 4 leading spaces): `async def publish(self, event: E, /) -> None:`
  - Last line (31): `raise BaseExceptionGroup(f"{len(failures)} subscriber(s) failed", failures)`
  - Contiguous run of the fence opening at `38-asyncio-and-the-patterns.md:141` (block lines 1 to 7 of 7); identical line for line, so byte-exact with the chapter.
- Disposition: **kept**. claim, witnesses and range confirmed.

### Slide 42: divider (Reference)

- Claim: -
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. structural slide; standalone wording below (do not point to the closing slide).

### Slide 43: Sources credited (Reference)

- Claim: the online sources the slides use.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. built from the credit census below.

### Slide 44: Reading further (Reference)

- Claim: the books the 201 chapters cite.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. eight books, each confirmed in the bibliography page and a chapter.

### Slide 45: Site and repository (Reference)

- Claim: the site and repository URLs.
- Witness: none needed; a structural slide with no claim about the code.
- Disposition: **kept**. both URLs return 200 now; re-checked at the QA step.

## Table cells (slides 28, 43 and 44)

### Slide 28: Metaclass costs

Columns: Cost, What the test shows. The chapter says "What the metaclass costs shows in four places." (a conflict and three mypy limits) and then names the one case where it pays. The plan's witness list left out the `Self` cost, so the table has four cost rows and one row for what a metaclass buys. Each cell below is a `grep -F` fragment of the chapter at the stated line; every test is defined once.

| Cost | What the test shows | Chapter fragment (`29-metaclasses-init-subclass-and-registries.md`) | Test |
| --- | --- | --- | --- |
| A second metaclass | It conflicts with the base's metaclass and raises TypeError; deriving from ABCMeta resolves it | `29-metaclasses-init-subclass-and-registries.md:149`: `grep -nF -- 'raises `TypeError` with "metaclass conflict"'` hit 1 line | `test_a_second_metaclass_conflicts_with_the_bases_metaclass` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py:25`, 1 definition); `test_a_metaclass_derived_from_abcmeta_resolves_the_conflict` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py:31`, 1 definition) |
| Class keywords | mypy does not check them: code=1 exits 0 and the run registers an int key | `29-metaclasses-init-subclass-and-registries.md:151`: `grep -nF -- '`class Fastline(MetaBase, code=1)` exits 0 with no output'` hit 1 line | `test_mypy_does_not_check_metaclass_class_keywords` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py:178`, 1 definition) |
| Self in __new__ | mypy refuses Self in a metaclass __new__ although the class builds | `29-metaclasses-init-subclass-and-registries.md:151`: `grep -nF -- '"Self type cannot be used in a metaclass"'` hit 1 line | `test_mypy_refuses_self_in_a_metaclass_new` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py:201`, 1 definition) |
| A registry of classes | A class called from a metaclass registry is typed Any, so a misspelt method passes mypy | `29-metaclasses-init-subclass-and-registries.md:151`: `grep -nF -- 'a misspelt method `bok` passes mypy and fails with `AttributeError` at run time'` hit 1 line | `test_mypy_types_a_class_called_from_a_metaclass_registry_as_any` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py:212`, 1 definition) |
| What it buys | Only a metaclass gives the class object operators: in, iteration and len | `29-metaclasses-init-subclass-and-registries.md:155`: `grep -nF -- 'so the class itself behaves as a collection of codes'` hit 1 line | `test_only_a_metaclass_gives_the_class_object_operators` (`examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py:37`, 1 definition) |

The mypy documentation quote (`29-metaclasses-init-subclass-and-registries.md:151`): `grep -nF -- 'Mypy does not and cannot understand arbitrary metaclass code.' _docs/29-metaclasses-init-subclass-and-registries.md` hit 1 line. The enum quote (`:168`) and the "What the metaclass costs shows in four places." sentence (`:149`) each hit one line.

### Slide 43: Sources credited

Columns: Source, Used for. One row per source (a source used by more than one slide is one row). Every URL is a link in the named chapter at the stated lines; a URL shared by two links in one chapter, or cited in the body and in "For deeper coverage", shows every line.

| Source | Used for | URL | Slides | Chapter lines (`grep -nF -- <url> <chapter>`) |
| --- | --- | --- | --- | --- |
| Python Language Reference: the data model | special methods are looked up on the type | https://docs.python.org/3/reference/datamodel.html | 4, 28 | 07:282; 29:313 |
| Python built-ins: NotImplemented | a value a binary method returns to decline | https://docs.python.org/3/builtins/constants.html#NotImplemented | 5 | 07:282 |
| functools.total_ordering | one method derives the other comparisons | https://docs.python.org/3/library/functools.html#functools.total_ordering | 5 | 07:282 |
| PEP 207, rich comparisons | the comparison protocol | https://peps.python.org/pep-0207/ | 5 | 07:282 |
| dataclasses documentation | frozen, slots and replace | https://docs.python.org/3/library/dataclasses.html | 6, 7 | 08:38,283 |
| PEP 557, data classes | the dataclass decorator | https://peps.python.org/pep-0557/ | 6, 7 | 08:38,283 |
| PEP 661, sentinel values | a sentinel separates not given from None | https://peps.python.org/pep-0661/ | 9 | 09:99,333 |
| PEP 544, Protocols | structural subtyping | https://peps.python.org/pep-0544/ | 11 | 09:32,333 |
| mypy documentation on protocols | how mypy checks a Protocol | https://mypy.readthedocs.io/en/stable/protocols.html | 11 | 09:32,333 |
| abc module documentation | abstract base classes | https://docs.python.org/3/library/abc.html | 11, 28 | 09:162; 29:313 |
| PEP 343, the with statement | acquire and release without call-site boilerplate | https://peps.python.org/pep-0343/ | 12 | 10:34,278 |
| Python Language Reference: with statement context managers | what __exit__ may return | https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers | 13 | 10:34,278 |
| contextlib documentation | suppress, ExitStack and contextmanager | https://docs.python.org/3/library/contextlib.html | 13, 14, 29, 40 | 10:34,145,153,278; 31:108,216; 38:80,248 |
| What's New in Python 3.15 | a context manager used as a decorator spans iteration | https://docs.python.org/3.15/whatsnew/3.15.html | 14, 41 | 10:76,159,278; 38:134,248 |
| functools documentation | wraps and partial | https://docs.python.org/3/library/functools.html | 16, 25 | 26:60,348; 28:56,267 |
| PEP 612, ParamSpec | carrying parameters through a decorator | https://peps.python.org/pep-0612/ | 16 | 26:72,348 |
| PEP 695, type parameter syntax | generic functions | https://peps.python.org/pep-0695/ | 17 | 26:348 |
| Python Language Reference: compound statements | decorator expressions run at definition | https://docs.python.org/3/reference/compound_stmts.html | 17 | 26:82,348 |
| PEP 3129, class decorators | decorating a class | https://peps.python.org/pep-3129/ | 18 | 26:201,348 |
| ruff rule B019 | caching an instance method | https://docs.astral.sh/ruff/rules/cached-instance-method/ | 18 | 26:211,348 |
| Descriptor Guide | functions bind as methods | https://docs.python.org/3/howto/descriptor.html | 18, 20 | 26:209,348; 27:79,337 |
| PEP 487, class creation hooks | __set_name__ and __init_subclass__ | https://peps.python.org/pep-0487/ | 20, 27 | 27:109,337; 29:313 |
| What's New in Python 3.12 | the cached_property lock was removed | https://docs.python.org/3/whatsnew/3.12.html | 21 | 27:337 |
| Brandon Rhodes, The Factory Method Pattern | the instance attribute wins | https://python-patterns.guide/gang-of-four/factory-method/ | 21 | 27:135,337 |
| copy documentation | copy builds an instance without __init__ | https://docs.python.org/3/library/copy.html | 23 | 30:261 |
| pickle documentation | unpickling does not call __init__ | https://docs.python.org/3/library/pickle.html | 23 | 30:261 |
| PEP 443, single-dispatch generic functions | registration away from the function | https://peps.python.org/pep-0443/ | 26 | 28:267 |
| Brandon Rhodes, The Global Object Pattern | imports decide a registry | https://python-patterns.guide/python/module-globals/ | 27 | 29:313 |
| mypy documentation on metaclasses | what mypy cannot follow | https://mypy.readthedocs.io/en/stable/metaclasses.html | 28 | 29:313 |
| Python glossary: EAFP | asking forgiveness rather than permission | https://docs.python.org/3/glossary.html | 29, 30 | 31:75,216 |
| PEP 814, frozendict | a read-only mapping | https://peps.python.org/pep-0814/ | 29 | 31:48,216 |
| Python built-ins: types | dict.get never raises KeyError | https://docs.python.org/3/builtins/stdtypes.html | 29 | 31:100,216 |
| PEP 8, style guide | expose simple attributes without accessors | https://peps.python.org/pep-0008/ | 32 | 32:215 |
| Martin Fowler, Inversion of Control Containers and the Dependency Injection pattern | a service locator against injection | https://martinfowler.com/articles/injection.html | 34 | 32:215 |
| Mark Seemann, Service Locator is an Anti-Pattern | a located dependency fails at first use | https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/ | 34 | 32:215 |
| free-threading how-to | building and running with or without the GIL | https://docs.python.org/3/howto/free-threading-python.html | 36 | 37:48,308 |
| PEP 703, making the GIL optional | the free-threaded build | https://peps.python.org/pep-0703/ | 36 | 37:308 |
| PEP 779, supported free-threaded builds | the build's status | https://peps.python.org/pep-0779/ | 36 | 37:308 |
| concurrent.futures documentation | thread, process and interpreter pools | https://docs.python.org/3/library/concurrent.futures.html | 38 | 37:122,308 |
| threading documentation | the GIL and performance considerations | https://docs.python.org/3/library/threading.html | 38 | 37:308 |
| Developing with asyncio | a coroutine never awaited is reported | https://docs.python.org/3/library/asyncio-dev.html | 39 | 38:40,248 |
| ruff rule RUF006 | a dangling task | https://docs.astral.sh/ruff/rules/asyncio-dangling-task/ | 39 | 38:42,248 |
| coroutines and tasks documentation | task groups | https://docs.python.org/3/library/asyncio-task.html | 41 | 38:42,152,248 |

43 distinct rows. The slide cannot hold them all legibly in one table; the builder splits the list by theme, or drops the rows whose slide notes already carry the credit, and the census row counts here are the superset. Rows for a PEP name its authors in the notes as the chapter words them (`grep -nE 'PEP [0-9]+\]\([^)]*\), by ' <chapter>` prints each).

Text-only credits with no URL (named in notes, `grep -nF` hit counts):

- Bobby Woolf's "Null Object" (slide 9): `09-protocol-and-structural-typing.md:60`, `grep -nF -- 'Bobby Woolf'"'"'s "Null Object", in *Pattern Languages of Program Design 3*'` hit 2 line(s)
- Martin Fowler, Lazy Load, in Patterns of Enterprise Application Architecture (slide 22): `30-dynamic-attributes-and-proxy.md:261`, `grep -nF -- '*Patterns of Enterprise Application Architecture* for Lazy Load'` hit 1 line(s)
- Active Object in POSA2 (slide 41): `38-asyncio-and-the-patterns.md:170`, `grep -nF -- 'names Active Object'` hit 1 line(s)
- Monitor Object and Scoped Locking in POSA2 (slide 37): `37-the-gil-and-performance.md:78`, `grep -nF -- 'Monitor Object in the vocabulary of *Pattern-Oriented Software Architecture, Volume 2*'` hit 1 line(s)
- Kircher and Jain, POSA3 (slide 12): `10-context-managers.md:280`, `grep -nF -- 'Kircher and Jain'"'"'s *Pattern-Oriented Software Architecture, Volume 3'` hit 1 line(s)
- Design Patterns, Visitor (slides 25 and 33): `32-anti-patterns-and-pattern-misuse.md:215`, `grep -nF -- 'is the source for Visitor'` hit 1 line(s)
- Design Patterns, Visitor (slide 25): `28-singledispatch.md:22`, `grep -nF -- 'Visitor, in *Design Patterns*'` hit 1 line(s)
- Design Patterns, Proxy (slide 22): `30-dynamic-attributes-and-proxy.md:22`, `grep -nF -- 'lists it under Proxy'` hit 1 line(s)

### Slide 44: Reading further

Columns: Book, Authors, Year. Each row is cited by an in-scope chapter and listed in `bibliography.html`.

| Book | Authors | Year | Slides | Chapter line | Bibliography (`grep -c`) |
| --- | --- | --- | --- | --- | --- |
| Fluent Python | Luciano Ramalho | 2022 | 4, 5 | `07-the-data-model.md:284` | `grep -cF -- 'Fluent Python' bibliography.html` = 1 |
| Effective Python | Brett Slatkin | 2024 | 6, 7 | `08-dataclasses-and-value-semantics.md:281` | `grep -cF -- 'Effective Python: 125' bibliography.html` = 1 |
| Patterns of Enterprise Application Architecture | Martin Fowler | 2002 | 6 | `08-dataclasses-and-value-semantics.md:32,279` | `grep -cF -- 'Patterns of Enterprise Application Architecture' bibliography.html` = 1 |
| Domain-Driven Design | Eric Evans | 2003 | 6 | `08-dataclasses-and-value-semantics.md:32` | `grep -cF -- 'Domain-Driven Design: Tackling' bibliography.html` = 1 |
| Pattern Languages of Program Design 3 | Bobby Woolf (chapter) in an edited volume | 1998 | 9 | `09-protocol-and-structural-typing.md:60,331` | `grep -cF -- 'Pattern Languages of Program Design 3' bibliography.html` = 1 |
| Pattern-Oriented Software Architecture, Volume 2 | Schmidt, Stal, Rohnert, Buschmann | 2000 | 37, 41 | `37-the-gil-and-performance.md:78,308` | `grep -cF -- 'Patterns for Concurrent and Networked Objects' bibliography.html` = 1 |
| Pattern-Oriented Software Architecture, Volume 3 | Kircher, Jain | 2004 | 12 | `10-context-managers.md:280` | `grep -cF -- 'Patterns for Resource Management' bibliography.html` = 1 |
| Design Patterns | Gamma, Helm, Johnson, Vlissides | 1994 | 22, 25, 33 | `28-singledispatch.md:22` | `grep -cF -- 'Design Patterns: Elements' bibliography.html` = 1 |

Eight books, matching the plan's evidence S. The year and the authors are the bibliography page's. Fluent Python and Effective Python are cited in several in-scope chapters (07, 08, 09, 10, 30, 31 for the first; 08, 09 for the second); the table lists each once.

## Credits per slide

The credits each slide's notes name, from the two tables above (the superset for the reference slides).

- Slide 4: Python Language Reference: the data model; Fluent Python
- Slide 5: Python built-ins: NotImplemented; functools.total_ordering; PEP 207, rich comparisons; Fluent Python
- Slide 6: dataclasses documentation; PEP 557, data classes; Effective Python; Patterns of Enterprise Application Architecture; Domain-Driven Design
- Slide 7: dataclasses documentation; PEP 557, data classes; Effective Python
- Slide 9: PEP 661, sentinel values; Pattern Languages of Program Design 3
- Slide 11: PEP 544, Protocols; mypy documentation on protocols; abc module documentation
- Slide 12: PEP 343, the with statement; Pattern-Oriented Software Architecture, Volume 3
- Slide 13: Python Language Reference: with statement context managers; contextlib documentation
- Slide 14: contextlib documentation; What's New in Python 3.15
- Slide 16: functools documentation; PEP 612, ParamSpec
- Slide 17: PEP 695, type parameter syntax; Python Language Reference: compound statements
- Slide 18: PEP 3129, class decorators; ruff rule B019; Descriptor Guide
- Slide 20: Descriptor Guide; PEP 487, class creation hooks
- Slide 21: What's New in Python 3.12; Brandon Rhodes, The Factory Method Pattern
- Slide 22: Design Patterns
- Slide 23: copy documentation; pickle documentation
- Slide 25: functools documentation; Design Patterns
- Slide 26: PEP 443, single-dispatch generic functions
- Slide 27: PEP 487, class creation hooks; PEP 487, class creation hooks; Brandon Rhodes, The Global Object Pattern
- Slide 28: abc module documentation; mypy documentation on metaclasses; Python Language Reference: the data model
- Slide 29: Python glossary: EAFP; PEP 814, frozendict; contextlib documentation; Python built-ins: types
- Slide 30: Python glossary: EAFP
- Slide 32: PEP 8, style guide
- Slide 33: Design Patterns
- Slide 34: Martin Fowler, Inversion of Control Containers and the Dependency Injection pattern; Mark Seemann, Service Locator is an Anti-Pattern
- Slide 36: free-threading how-to; PEP 703, making the GIL optional; PEP 779, supported free-threaded builds
- Slide 37: Pattern-Oriented Software Architecture, Volume 2
- Slide 38: concurrent.futures documentation; threading documentation
- Slide 39: Developing with asyncio; ruff rule RUF006
- Slide 40: contextlib documentation
- Slide 41: What's New in Python 3.15; coroutines and tasks documentation; Pattern-Oriented Software Architecture, Volume 2

## Figure census

Re-run now, arrow by arrow, against the specs in `diagrams/specs/` and the code. A figure passes when every arrow is composed by code (a call in `src`, a call the test makes, or interpreter dispatch the test witnesses) and no arrow is conceptual. Legibility is the smallest `font-size` in the SVG scaled into the 12.09 by 4.95 inch box by the contained fit (`min(12.09/w, 4.95/h)`), against the 6.3 pt floor. Every registry caption equals its include caption with the "Figure N.1: " prefix removed, and has 20 to 45 words.

| Fig | Slide | viewBox | Smallest label, pt | Edges | Caption words | Registry equals include | PNG | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 07 | 5 | 820x560 | 7.0 | 4 | 36 | yes | `presentation/png/07-the-data-model.png` | passes |
| 09 | 11 | 890x430 | 9.5 | 3 | 33 | yes | `presentation/png/09-protocol-and-structural-typing.png` | passes |
| 10 | 12 | 820x600 | 6.8 | 6 | 32 | yes | `presentation/png/10-context-managers.png` | passes |
| 31 | 30 | 1220x480 | 8.2 | 6 | 37 | yes | `presentation/png/31-shortcut-patterns-dict-dispatch-and-eafp.png` | passes |
| 37 | 37 | 860x560 | 7.3 | 4 | 34 | yes | `presentation/png/37-the-gil-and-performance.png` | passes |

`presentation/render-png.sh --deck 201` wrote the five PNGs and `./render-png.sh --check` printed `same` for all sixteen figures (the eleven of Deck 101 and these five). The frame the builder uses comes from the PNG's own aspect, so the slide frames are 7.25 by 4.95 (07), 10.25 by 4.95 (09), 6.77 by 4.95 (10), 12.09 by 4.76 (31) and 7.60 by 4.95 (37) inches.

### Figure 07 (slide 5)

Spec: `diagrams/specs/07-the-data-model.py`, four edges. F1 applied: the second box reads `type(factor).__mul__(factor, price)` and the dashed edge reads `NotImplemented again (float factor)`.

- `factor * price` to `type(factor).__mul__(factor, price)`: interpreter dispatch on the left operand's type, witnessed by `examples/07-the-data-model/tests/test_arithmetic.py:18` (`Decimal("2") * price`).
- That box to `Money.__rmul__(price, factor)`, labelled `NotImplemented`: `Decimal.__mul__` declines a `Money`, so the interpreter calls the reflected method (`money.py:33`); the same line 18 result is a `Money`, which only the reflected method can produce.
- `Money.__rmul__` to `Money`, labelled `returns`: `money.py:34` (`return self.__mul__(factor)`) and the equal result at `test_arithmetic.py:18-20`.
- Dashed edge from `Money.__rmul__` to `TypeError`: `money.py:29-30` returns `NotImplemented` for a factor that is not `Decimal | int`, and `test_arithmetic.py:22` and `:24` assert `TypeError` for `price * 1.5` and `1.5 * price`. This is the float case the label names; it cannot happen for a `Decimal`.
- Verdict: every arrow composed. Test: `test_a_factor_times_money_uses_the_reflected_method`.

### Figure 09 (slide 11)

Spec: `diagrams/specs/09-protocol-and-structural-typing.py`, three edges. F2 applied: the `_NullGateway (test fixture)` node has no edge, and the spec docstring says no code swaps it in.

- `book_with(code, consignment)` to the absence lane (`find_gateway(code)` returning `CarrierGateway | None`): `carriers.py:60` calls it, `:52` declares the optional return, and `:61-62` narrows before use. Witness: `test_mypy_requires_a_branch_for_absence`.
- `book_with` to the shape lane (`CarrierGateway`, `FastlineGateway`, no base class): `carriers.py:63` calls `gateway.book(consignment)` on a `CarrierGateway`, `:12` is the Protocol and `:18` the class with no base. Witness: `test_mypy_checks_protocols_at_use_and_abcs_at_construction`.
- `book_with` to the declaration lane (`CarrierBase`, `AircoGateway`): `carriers.py:47-49` maps `AIRCO` to `AircoGateway`, `:55` builds it, `:25` and `:37` declare the ABC and subclass. Witness: `test_abc_refuses_an_incomplete_subclass_at_construction`.
- The unconnected fixture node is `_NullGateway` (`tests/test_absence.py:18`), used directly at `test_absence.py:37`; no edge claims otherwise.
- Verdict: every arrow composed.

### Figure 10 (slide 12)

Spec: `diagrams/specs/10-context-managers.py`, six edges. F3 applied: the label reads `__exit__(exc_type, exc, traceback)`, the parameter names at `manifest.py:63-65`.

- `with ManifestWriter(path) as out:` to `__enter__`: the `with` line at `tests/test_static.py:42`; `__enter__` at `manifest.py:54`.
- `__enter__` to the body: `manifest.py:58` opens `path.partial` and returns the handle (`:59`).
- Body to the success exit and the failure exit (two edges): `__exit__` at `manifest.py:61`, branching on `exc_type is None` at `:69`.
- Success exit to `manifest committed`: `manifest.py:70-71` closes and replaces the partial. Witness: `test_writer_commits_only_on_success`.
- Failure exit to `exception propagates`: `manifest.py:73-74` closes and unlinks the partial, and the method returns `None`, so the exception continues. Witness: `test_writer_closes_and_discards_on_an_exception`.
- Verdict: every arrow composed.

### Figure 31 (slide 30)

Spec: `diagrams/specs/31-shortcut-patterns-dict-dispatch-and-eafp.py`, six edges. F7 applied: the look-first edge leaves its own node, `_LookFirstDutyRateCache.rate_for`, drawn in the ghost style as the comparison form.

- `issue(kind, consignment_id)` to `issuers[kind]`: `documents.py:46` and `:59`.
- `ISSUERS` to the lookup: the default argument at `documents.py:51` (`issuers=ISSUERS`), the table at `:37`.
- Lookup to `issuer(consignment_id)` outside the try: `documents.py:62`. Witness: `test_an_issuers_own_key_error_passes_through_issue`.
- `issuer(consignment_id)` to `reference`: the returned string, `documents.py:62`.
- `DutyRateCache.rate_for(hs_code)` to "ask forgiveness: read once, on KeyError, load and store the rate": `duties.py:26-32`. Witness: `test_an_eafp_read_reloads_when_another_thread_evicts_first` (`test_eafp.py:82`).
- `_LookFirstDutyRateCache.rate_for` to "look first: in, then read; an eviction in the gap raises KeyError": `tests/conftest.py:26-34`. Witness: `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read` (`test_eafp.py:74`).
- Verdict: every arrow composed. The last witness is also the test Deck 101's EAFP row uses (boundary check below).

### Figure 37 (slide 37)

Spec: `diagrams/specs/37-the-gil-and-performance.py`, four edges. F9 applied: the summary bar is an unconnected note; nothing leads into it.

- `StowagePlan.reserve` to the no-lock lane: `stowage.py:40` takes `with self._lock`, and `test_stowage.py:31` passes `lock=nullcontext()` with `gap=barrier_gap`.
- `StowagePlan.reserve` to the lock lane: `test_stowage.py:49` passes `recording_lock` and `recording_lock.wait_for_second_caller`; `stowage.py:30` is where the lock is stored.
- No-lock lane to "the two threads take the same SlotId" (the dashed edge): `test_stowage.py:33-34` asserts `[SlotId(1, 1, 1), SlotId(1, 1, 1)]` and one reservation. Witness: `test_two_threads_parked_between_read_and_write_take_the_same_slot`.
- Lock lane to "each thread gets its own SlotId": `test_stowage.py:51-55` asserts `SlotId(1, 1, 1)` and `SlotId(1, 1, 2)`, two reservations, and that the second caller arrived. Witness: `test_a_lock_across_read_and_write_gives_each_thread_its_own_slot`.
- Verdict: every arrow composed. The "on either build" in the box is witnessed by the same test passing on both builds in CI (`ci.yml`), and the tests here ran on the default build.

## Numbers in the notes

Decision 7 allows two recorded measurements in notes, each with its label, and says no test asserts a time. Slide text carries no timing. The lost-update counts are quoted because P12 landed.

### Ratio sentence (slide 30)

- Chapter: `31-shortcut-patterns-dict-dispatch-and-eafp.md:149`, `grep -nF -- 'On a recorded run on Python 3.15.2 (best of five repeats of one million calls, 2026-11-06)' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md` hit 1 line. The label is exactly that: Python 3.15.2, best of five repeats of one million calls, 2026-11-06.
  - `42.7 ns`: `_plans/evidence/eafp-lookup-cost.md:24` (the output block), chapter line 149
  - `50.4 ns`: `_plans/evidence/eafp-lookup-cost.md:25` (the output block), chapter line 149
  - `51.3 ns`: `_plans/evidence/eafp-lookup-cost.md:26` (the output block), chapter line 149
  - `141.5 ns`: `_plans/evidence/eafp-lookup-cost.md:27` (the output block), chapter line 149
  - `45.0 ns`: `_plans/evidence/eafp-lookup-cost.md:28` (the output block), chapter line 
  - `51.0 ns`: `_plans/evidence/eafp-lookup-cost.md:29` (the output block), chapter line 
- Source: `_plans/evidence/eafp-lookup-cost.md` (recorded 2026-11-06, r15, Python 3.15.2, run from `examples/31-shortcut-patterns-dict-dispatch-and-eafp` with `uv run python -I bench/lookup_cost.py`, five times, through `host_ids.py filter`). The script is `examples/31-shortcut-patterns-dict-dispatch-and-eafp/bench/lookup_cost.py`; the output block is kept in the evidence file, not in `bench/`. The output prints the version only (no build, no machine class).
- "About three times dearer" is the miss ratio: 141.5 over 45.0 is 3.14 and over 51.0 is 2.77. The chapter says "about three times", and the notes should too.

### Warm ratios (slide 38)

- Chapter: `37-the-gil-and-performance.md:197`; the bullets run from line 196. Label: Python 3.15.2, default and free-threading builds, workers 4, best of 3, a 16-thread x86-64 CPU class, 2026-11-06.
- `examples/37-the-gil-and-performance/bench/gil_bench.out.txt` (default build): header lines `Python 3.15.2, default build, GIL enabled: True`, `workers: 4, batch: 4 consignments, best of 3`, `date: 2026-11-06, machine: 16-thread x86-64 CPU`.
  - Chapter fence: lines 149 to 167 are line for line equal to the file (19 lines).
- `examples/37-the-gil-and-performance/bench/gil_bench.ft.out.txt` (free-threading build): header lines `Python 3.15.2, free-threading build, GIL enabled: False`, `workers: 4, batch: 4 consignments, best of 3`, `date: 2026-11-06, machine: 16-thread x86-64 CPU`.
  - Chapter fence: lines 173 to 191 are line for line equal to the file (19 lines).
  - `3.9x` (ft integer thread pool warm): in `bench/gil_bench.ft.out.txt`; chapter line 185
  - `0.5x` (ft Decimal thread pool warm): in `bench/gil_bench.ft.out.txt`; chapter line 179
  - `1.648 s` (ft Decimal thread pool): in `bench/gil_bench.ft.out.txt`; chapter line 179
  - `0.878 s` (ft Decimal serial): in `bench/gil_bench.ft.out.txt`; chapter line 178,197
  - `0.132 s` (default integer serial): in `bench/gil_bench.out.txt`; chapter line 160,161
  - `0.159 s` (ft integer serial): in `bench/gil_bench.ft.out.txt`; chapter line 184,198
  - `1.3x` (default cold interpreter integer): in `bench/gil_bench.out.txt`; chapter line 163
  - `0.8x` (ft cold interpreter integer): in `bench/gil_bench.ft.out.txt`; chapter line 187
- "Process and interpreter pools ran at about 3.4 to 3.7 times serial, warm, on both builds": the eight warm cells are default build Decimal process 3.6x and interpreter 3.4x, integer process 3.4x and interpreter 3.5x; free-threading Decimal process 3.4x and interpreter 3.7x, integer process 3.5x and interpreter 3.7x. The range 3.4 to 3.7 holds across all eight.
- A second run "agreed within about 0.4 on every ratio" (chapter line 194) is recorded in `_plans/evidence/r18-gil-benchmark.md:92` ("The two runs of each build agree within about 0.4x on every ratio."); the notes must say a figure is one recorded run.
- No test asserts a time. These are `bench/` outputs only.

### Lost-update counts (slide 37)

- Chapter: `37-the-gil-and-performance.md:24`, `grep -nF -- 'lost an update in none on the default build and in all 300 on the free-threaded build' _docs/37-the-gil-and-performance.md` hit 1 line.
- `examples/37-the-gil-and-performance/bench/lost_update_probe.out.txt` (default build):
```text
Python 3.15.2, default build, GIL enabled: True
date: 2026-11-07, machine: 16-thread x86-64 CPU
switch interval: 0.005 s
threads: 4, additions per thread: 5000, trials: 300
trials with a lost update: 0 of 300
```
- `examples/37-the-gil-and-performance/bench/lost_update_probe.ft.out.txt` (free-threading build):
```text
Python 3.15.2, free-threading build, GIL enabled: False
date: 2026-11-07, machine: 16-thread x86-64 CPU
switch interval: 0.005 s
threads: 4, additions per thread: 5000, trials: 300
trials with a lost update: 300 of 300
```
- 300 trials of four threads, each adding 1 to a shared attribute 5,000 times: `threads: 4, additions per thread: 5000, trials: 300`. Default build 0 of 300, free-threading build 300 of 300. Both outputs are dated 2026-11-07 (the plan's other 37 ratios are 2026-11-06), run by Z1c on the same machine class.
- The switch interval "0.005" (chapter line 52) is the probe's `switch interval: 0.005 s` line in both files.
- The notes may quote the counts with the label "recorded runs of the probe" and the build, and must say a race that does not fire on one build still exists (chapter line 24).

### Pinned versions (slide 45 notes)

| Version | Source |
| --- | --- |
| CPython 3.15.2 | `.python-version` (`3.15.2`); `_docs/41-appendix-a-build-and-toolchain.md:32` (`uv python install 3.15.2`); `_docs/00-prerequisites.md` version table |
| uv 0.13.7 | `uv --version` prints `uv 0.13.7`; `_docs/00-prerequisites.md:34` |
| pytest 9.2.0 | `pyproject.toml:18` (`pytest==9.2.0`); `_docs/00-prerequisites.md:35` |
| mypy 2.4.1 | `pyproject.toml:21` (`mypy==2.4.1`); `_docs/00-prerequisites.md:38` |

### URLs (slide 45)

`curl -s -o /dev/null -w '%{http_code}'` on `https://patterncatalyst.github.io/design-patterns-with-python/` and on `https://github.com/patterncatalyst/design-patterns-with-python` printed `200` and `200` on 2026-11-07. The QA step repeats the check.

## Boundary check against Deck 101

Run now over `presentation/deck-101.js` (the refactored builder; its line numbers moved when Z1a factored out `deck-lib.js`, so the plan's `js:NNN` references are stale and the lines below are current).

- Test names: all 147 witness and notes-witness names of Deck 201 were searched with `grep -c <name> presentation/deck-101.js`; the total is 0. Deck 101 names its tests in words (the table rows at the lines below), never by identifier, so no 201 slide reuses a 101 test by name. The three words-only overlaps are in the table.
- Code ranges: Deck 101 has 26 `codeSlide` calls; none reads from `examples/07` to `examples/10` or `examples/26` to `examples/38`. No 201 code range is a 101 range.
- Titles: no Deck 201 slide title equals a Deck 101 content-slide title, and none is within 0.8 string similarity of one, except the three reference slides ("Sources credited", "Reading further", "Site and repository"), which carry different rows by design. The four titles the plan says to avoid ("Proxy as stand-in", "Builder as a dataclass", "Snapshot and rollback", "Generators as iterators") are not used.

| Deck 101 has (current line) | 201 slides | Result |
| --- | --- | --- |
| "Null Object" row `X \| None checked by mypy` (126) | 9, 10 | angle differs: the branch mypy requires, and a null object that hides a lost booking. Distinct tests (example 09, not example 03). Clear. |
| "Value Object" row `A frozen dataclass` (127); chapter 0's consignment listing (line 90) | 6, 7 | `Weight` is a different listing; slides teach declaration, the setattr guard, shallowness and amendment. Clear. |
| "Interface" row (157), "Narrow roles" (203) | 11 | checked at use against checked at construction, `runtime_checkable` names only; not a Protocol per role. Clear. |
| "Resource acquisition" row (148), the `with` statement (148), "Snapshot and rollback" (399) | 12, 13, 14 | commit or discard on each exit path, the generator form's `try`, narrow swallowing. Clear. |
| "A name rebound once" (340) | 16, 17, 18 | what `wraps` copies, a factory refusing bare use, what each stacking order measures. Clear; the title is not reused. |
| `__getattr__`, property and `cached_property` (156) and the proxy-typo bullet (350) | 20, 21, 22, 23 | one descriptor for many fields, the four costs, lazy load by allow-list, the recursion trap. No 201 slide uses the typo point or `30.md:157`. Clear. |
| singledispatch row (125) | 25, 26 | the fallback as the decision, registration from another module, the union fallback; no match contrast. Clear. The title "Visitor as a match" (393) is not reused. |
| "Metaclass registry" row `__init_subclass__` (128) | 27, 28 | a class keyword that registers and refuses at definition; metaclass costs. Chapter 3's forwarding `CarrierBase` is not used. Clear. |
| "If-chain dispatch" row (129), `RATE_RULES` (246), the EAFP row (227) | 29, 30 | the narrow `try` and one gap. **Partial overlap**: figure 31's look-first box depicts the same fact as 101's EAFP row ("A look-first read raises when another thread evicts between check and read"), and its only witness is `test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read`. Slide 30's witness column does not list it (only the EAFP-side tests), so it is not a headline witness; the notes must lead with the EAFP read and mention the look-first branch as the comparison. Allowed on that condition. |
| YAGNI, DRY and simple-design rows (223) | 32, 33, 34 | two forms passing one table, a Visitor that breaks on a new charge, a located dependency mypy cannot see. **Near repeat**: 101's YAGNI row states that the engine needs more classes, functions and lines than the function. No 201 witness counts classes, but the claim at slide 32 ("what differs is the cost of the structure") is the same idea, so the notes must lead with the shared table and the zone refusal, and mention the structure's cost without class and line counts. Allowed on that condition. |

Verdict: no 201 slide reuses a 101 code range, a 101 test by name, a 101 title (apart from the three reference titles) or a 101 headline claim. Two near repeats (slides 30 and 32) are allowed on the stated conditions. No slide is cut or narrowed for the boundary.

## Sentences no slide may quote

The surveys named phrases that point to the book or use a workspace term. Re-found now:

- "the label this book uses": `10-context-managers.md:32` (`grep -nF -- 'is the label this book uses' _docs/10-context-managers.md` hit 1 line)
- "the book this chapter leans on": `07-the-data-model.md:284` (`grep -nF -- 'is the book this chapter leans on most' _docs/07-the-data-model.md` hit 1 line)
- "Nothing in this member shares a consignment": `27-descriptors-and-properties.md:195` (`grep -nF -- 'Nothing in this member shares a consignment' _docs/27-descriptors-and-properties.md` hit 1 line)
- the proxy-typo sentence: `30-dynamic-attributes-and-proxy.md:157` (`grep -nF -- '`cached_property` form has no `__getattr__`, so mypy names the typo' _docs/30-dynamic-attributes-and-proxy.md` hit 1 line)

## Witness test runs

Date 2026-11-07. The 147 distinct test names above (215 cases once parametrised cases expand) were run by node id in a fresh copy built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <scratchpad>/z1b` (the copy then held the five new PNGs). In the copy: `rm -rf .venv .venv-ft`, then `uv sync --locked --all-packages`. The sync used the locked set and installed the thirteen in-scope members editable from the copy. The names are the 143 of the plan's inventory plus four the census added (`test_mypy_refuses_self_in_a_metaclass_new`, `test_a_decorator_that_supplies_an_argument_reports_the_original_parameters`, `test_partial_reports_the_parameters_that_remain`, `test_money_validates_and_of_normalises`). The reverse run passes the same node ids in reverse order.

Each member imports from the copy, not from the repository (`__file__`, scrubbed):

```text
data_model <scratchpad>/z1b/examples/07-the-data-model/src/data_model/__init__.py
value_semantics <scratchpad>/z1b/examples/08-dataclasses-and-value-semantics/src/value_semantics/__init__.py
structural_typing <scratchpad>/z1b/examples/09-protocol-and-structural-typing/src/structural_typing/__init__.py
context_managers <scratchpad>/z1b/examples/10-context-managers/src/context_managers/__init__.py
decorators_done_right <scratchpad>/z1b/examples/26-decorators-done-right/src/decorators_done_right/__init__.py
descriptors_properties <scratchpad>/z1b/examples/27-descriptors-and-properties/src/descriptors_properties/__init__.py
singledispatch_visitor <scratchpad>/z1b/examples/28-singledispatch/src/singledispatch_visitor/__init__.py
carrier_registry <scratchpad>/z1b/examples/29-metaclasses-init-subclass-and-registries/src/carrier_registry/__init__.py
dynamic_attributes <scratchpad>/z1b/examples/30-dynamic-attributes-and-proxy/src/dynamic_attributes/__init__.py
shortcut_patterns <scratchpad>/z1b/examples/31-shortcut-patterns-dict-dispatch-and-eafp/src/shortcut_patterns/__init__.py
pattern_misuse <scratchpad>/z1b/examples/32-anti-patterns-and-pattern-misuse/src/pattern_misuse/__init__.py
gil_and_performance <scratchpad>/z1b/examples/37-the-gil-and-performance/src/gil_and_performance/__init__.py
asyncio_patterns <scratchpad>/z1b/examples/38-asyncio-and-the-patterns/src/asyncio_patterns/__init__.py
3.15.2
```

```text
$ uv run pytest --version
pytest 9.2.0
$ uv run pytest -q --collect-only <147 node ids>
215 tests collected
```

Command: `uv run pytest -q -p no:cacheprovider $(cat <ids>)` from the copy's root (the root `pyproject.toml` supplies `--import-mode=importlib`, `--strict-markers`, `--strict-config` and `filterwarnings = ["error"]`).

| Run | Order | Summary line | Date |
| --- | --- | --- | --- |
| forward 1 | inventory order | `215 passed in 20.83s` | 2026-11-07 |
| forward 2 | inventory order | `215 passed in 20.51s` | 2026-11-07 |
| forward 3 | inventory order | `215 passed in 20.64s` | 2026-11-07 |
| reverse | reverse of the inventory order | `215 passed in 19.82s` | 2026-11-07 |

No test skipped, none warned (`filterwarnings = ["error"]` would have failed it), and the four counts agree: 215 cases. The scratch copy was deleted afterwards and no process was left running.

Node ids run (repo-relative, in inventory order):

```text
examples/07-the-data-model/tests/test_equality.py::test_a_turned_carton_is_one_set_element
examples/07-the-data-model/tests/test_equality.py::test_defining_eq_alone_makes_a_class_unhashable
examples/07-the-data-model/tests/test_equality.py::test_custom_eq_in_a_frozen_dataclass_keeps_a_field_hash
examples/07-the-data-model/tests/test_static.py::test_mypy_cannot_see_a_broken_hash_contract
examples/07-the-data-model/tests/test_equality.py::test_special_methods_are_looked_up_on_the_type
examples/07-the-data-model/tests/test_arithmetic.py::test_a_factor_times_money_uses_the_reflected_method
examples/07-the-data-model/tests/test_arithmetic.py::test_sum_needs_a_money_start
examples/07-the-data-model/tests/test_ordering.py::test_total_ordering_derives_the_other_comparisons
examples/07-the-data-model/tests/test_ordering.py::test_quotes_sort_by_total_but_not_by_themselves
examples/08-dataclasses-and-value-semantics/tests/test_values.py::test_equal_values_are_interchangeable
examples/08-dataclasses-and-value-semantics/tests/test_values.py::test_a_frozen_value_refuses_assignment
examples/08-dataclasses-and-value-semantics/tests/test_static.py::test_mypy_checks_the_generated_methods
examples/08-dataclasses-and-value-semantics/tests/test_values.py::test_slots_remove_dict_and_weakref_until_asked
examples/08-dataclasses-and-value-semantics/tests/test_generated.py::test_stowage_plan_is_an_entity
examples/08-dataclasses-and-value-semantics/tests/test_generated.py::test_mutable_default_is_refused_at_class_creation
examples/08-dataclasses-and-value-semantics/tests/test_values.py::test_frozen_is_a_setattr_guard_not_a_seal
examples/08-dataclasses-and-value-semantics/tests/test_values.py::test_frozen_is_shallow
examples/08-dataclasses-and-value-semantics/tests/test_aliasing.py::test_a_mutable_dataclass_is_not_a_dict_key
examples/08-dataclasses-and-value-semantics/tests/test_aliasing.py::test_a_mutable_consignment_aliased_between_bookings_changes_both
examples/08-dataclasses-and-value-semantics/tests/test_aliasing.py::test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old
examples/08-dataclasses-and-value-semantics/tests/test_aliasing.py::test_replace_runs_post_init
examples/08-dataclasses-and-value-semantics/tests/test_static.py::test_mypy_cannot_see_value_semantics_mistakes
examples/09-protocol-and-structural-typing/tests/test_absence.py::test_find_gateway_returns_none_for_an_unknown_code
examples/09-protocol-and-structural-typing/tests/test_absence.py::test_book_with_turns_absence_into_a_booking_error
examples/09-protocol-and-structural-typing/tests/test_static.py::test_mypy_requires_a_branch_for_absence
examples/09-protocol-and-structural-typing/tests/test_absence.py::test_a_sentinel_separates_not_given_from_none
examples/09-protocol-and-structural-typing/tests/test_absence.py::test_a_null_gateway_hides_a_lost_booking
examples/09-protocol-and-structural-typing/tests/test_static.py::test_mypy_accepts_a_null_gateway
examples/09-protocol-and-structural-typing/tests/test_absence.py::test_no_discount_is_a_null_object_that_loses_nothing
examples/09-protocol-and-structural-typing/tests/test_static.py::test_mypy_checks_protocols_at_use_and_abcs_at_construction
examples/09-protocol-and-structural-typing/tests/test_disambiguate.py::test_abc_refuses_an_incomplete_subclass_at_construction
examples/09-protocol-and-structural-typing/tests/test_disambiguate.py::test_both_carriers_satisfy_the_protocol_one_by_inheritance
examples/09-protocol-and-structural-typing/tests/test_disambiguate.py::test_explicit_protocol_subclass_is_nominal_and_still_instantiable
examples/09-protocol-and-structural-typing/tests/test_runtime_checkable.py::test_runtime_checkable_checks_names_only
examples/10-context-managers/tests/test_writer.py::test_without_with_an_exception_leaves_the_handle_open
examples/10-context-managers/tests/test_writer.py::test_writer_commits_only_on_success
examples/10-context-managers/tests/test_writer.py::test_writer_closes_and_discards_on_an_exception
examples/10-context-managers/tests/test_writer.py::test_writer_is_single_use
examples/10-context-managers/tests/test_semantics.py::test_a_truthy_exit_swallows_the_exception
examples/10-context-managers/tests/test_semantics.py::test_suppress_swallows_only_the_named_exception
examples/10-context-managers/tests/test_static.py::test_mypy_reads_exit_return_type_for_reachability
examples/10-context-managers/tests/test_writer.py::test_the_generator_form_needs_try
examples/10-context-managers/tests/test_static.py::test_mypy_cannot_see_a_missing_try
examples/10-context-managers/tests/test_stack.py::test_exit_stack_unwinds_entered_writers_in_reverse_order
examples/10-context-managers/tests/test_semantics.py::test_a_context_manager_decorating_a_generator_spans_iteration
examples/26-decorators-done-right/tests/test_wraps.py::test_wraps_keeps_the_name_qualname_doc_and_module
examples/26-decorators-done-right/tests/test_wraps.py::test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring
examples/26-decorators-done-right/tests/test_wraps.py::test_inspect_signature_follows_wrapped_to_the_original_parameters
examples/26-decorators-done-right/tests/test_wraps.py::test_wrapped_points_one_level_down_and_unwrap_reaches_the_original
examples/26-decorators-done-right/tests/test_static.py::test_mypy_keeps_the_signature_through_a_wrapper_without_wraps
examples/26-decorators-done-right/tests/test_factories.py::test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator
examples/26-decorators-done-right/tests/test_factories.py::test_a_keyword_only_factory_used_bare_fails_at_definition
examples/26-decorators-done-right/tests/test_static.py::test_mypy_refuses_a_keyword_only_factory_used_bare
examples/26-decorators-done-right/tests/test_factories.py::test_stacking_order_decides_whether_a_cache_hit_is_timed
examples/26-decorators-done-right/tests/test_factories.py::test_cached_for_renders_again_once_the_window_has_passed
examples/26-decorators-done-right/tests/test_classes.py::test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class
examples/26-decorators-done-right/tests/test_classes.py::test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none
examples/26-decorators-done-right/tests/test_methods.py::test_functools_cache_on_a_method_keeps_the_instance_alive
examples/27-descriptors-and-properties/tests/test_fields.py::test_every_field_form_validates_the_same_extents
examples/27-descriptors-and-properties/tests/test_fields.py::test_a_copy_pasted_property_validator_drifts
examples/27-descriptors-and-properties/tests/test_fields.py::test_one_descriptor_class_validates_every_field
examples/27-descriptors-and-properties/tests/test_fields.py::test_set_name_gives_each_field_its_own_storage
examples/27-descriptors-and-properties/tests/test_cached.py::test_chargeable_weight_is_computed_on_first_access_and_stored
examples/27-descriptors-and-properties/tests/test_cached.py::test_cached_property_needs_an_instance_dict
examples/27-descriptors-and-properties/tests/test_cached.py::test_a_frozen_dataclass_cannot_clear_a_cached_property
examples/27-descriptors-and-properties/tests/test_cached.py::test_a_cached_property_over_mutable_state_goes_stale
examples/27-descriptors-and-properties/tests/test_cached.py::test_a_cached_property_getter_can_run_twice_under_threads
examples/27-descriptors-and-properties/tests/test_lookup.py::test_a_data_descriptor_takes_precedence_over_the_instance_dict
examples/27-descriptors-and-properties/tests/test_lookup.py::test_an_instance_dict_entry_takes_precedence_over_cached_property
examples/30-dynamic-attributes-and-proxy/tests/test_history.py::test_every_history_form_loads_once_for_every_field
examples/30-dynamic-attributes-and-proxy/tests/test_history.py::test_nothing_is_loaded_until_a_field_is_read
examples/30-dynamic-attributes-and-proxy/tests/test_history.py::test_a_loaded_history_reads_its_fields_from_the_instance_dict
examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py::test_getattr_runs_only_when_normal_lookup_fails
examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py::test_a_misspelt_field_suggests_the_declared_name_through_dir
examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py::test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute
examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py::test_each_fix_keeps_getattr_out_of_recursion
examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py::test_copy_keeps_a_history_before_and_after_loading
examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py::test_hasattr_loads_the_history
examples/30-dynamic-attributes-and-proxy/tests/test_lookup.py::test_implicit_special_method_lookup_bypasses_getattr
examples/28-singledispatch/tests/test_tariff.py::test_every_fallback_form_gives_registered_commodities_their_codes
examples/28-singledispatch/tests/test_tariff.py::test_the_most_specific_registration_wins
examples/28-singledispatch/tests/test_tariff.py::test_an_unregistered_subclass_gets_its_base_class_code
examples/28-singledispatch/tests/test_tariff.py::test_a_raising_fallback_names_an_unregistered_kind
examples/28-singledispatch/tests/test_tariff.py::test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently
examples/28-singledispatch/tests/test_registration.py::test_another_module_extends_the_set_when_it_is_imported
examples/28-singledispatch/tests/test_tariff.py::test_the_registry_is_read_only
examples/28-singledispatch/tests/test_static.py::test_mypy_refuses_a_kind_outside_a_union_fallback
examples/28-singledispatch/tests/test_static.py::test_mypy_checks_calls_and_registrations_against_the_fallback
examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py::test_every_registry_form_books_through_the_registered_carrier
examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py::test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry
examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py::test_the_carrier_registry_is_a_read_only_view
examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py::test_isabstract_sees_abstractness_inside_init_subclass
examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py::test_mypy_reports_a_misspelt_class_keyword
examples/29-metaclasses-init-subclass-and-registries/tests/test_registry.py::test_a_carrier_module_registers_only_when_it_is_imported
examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py::test_a_second_metaclass_conflicts_with_the_bases_metaclass
examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py::test_a_metaclass_derived_from_abcmeta_resolves_the_conflict
examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py::test_mypy_does_not_check_metaclass_class_keywords
examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py::test_mypy_types_a_class_called_from_a_metaclass_registry_as_any
examples/29-metaclasses-init-subclass-and-registries/tests/test_metaclass.py::test_only_a_metaclass_gives_the_class_object_operators
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py::test_an_issuers_own_key_error_passes_through_issue
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py::test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_dispatch.py::test_an_unsupported_kind_raises_unsupported_document_error
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_static.py::test_mypy_accepts_a_table_that_misses_a_kind
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_suppress_skips_the_rest_of_its_block_after_the_first_exception
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_an_eafp_read_reloads_when_another_thread_evicts_first
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_two_eafp_readers_that_both_miss_both_load
examples/31-shortcut-patterns-dict-dispatch-and-eafp/tests/test_eafp.py::test_every_cache_form_reads_loads_and_evicts_the_same_way
examples/32-anti-patterns-and-pattern-misuse/tests/test_forms.py::test_every_rating_form_quotes_the_same_table
examples/32-anti-patterns-and-pattern-misuse/tests/test_forms.py::test_every_rating_form_refuses_an_unknown_zone
examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py::test_an_accessor_consignment_has_no_value_equality
examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py::test_a_setter_lets_a_quoted_consignment_change_its_quote
examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py::test_a_frozen_consignment_refuses_assignment
examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time
examples/32-anti-patterns-and-pattern-misuse/tests/test_measure.py::test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract
examples/32-anti-patterns-and-pattern-misuse/tests/test_static.py::test_mypy_reports_a_visitor_missing_a_new_visit_method
examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py::test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered
examples/32-anti-patterns-and-pattern-misuse/tests/test_misuse.py::test_a_located_engine_quotes_once_its_tariff_is_registered
examples/32-anti-patterns-and-pattern-misuse/tests/test_static.py::test_mypy_does_not_see_a_missing_registration
examples/32-anti-patterns-and-pattern-misuse/tests/test_static.py::test_mypy_reports_a_missing_tariff_argument
examples/37-the-gil-and-performance/tests/test_build.py::test_the_build_flag_and_the_runtime_gil_state_agree
examples/37-the-gil-and-performance/tests/test_build.py::test_sys_version_names_the_free_threading_build_only_on_that_build
examples/37-the-gil-and-performance/tests/test_static.py::test_mypy_types_the_build_flag_as_any
examples/37-the-gil-and-performance/tests/test_stowage.py::test_two_threads_parked_between_read_and_write_take_the_same_slot
examples/37-the-gil-and-performance/tests/test_stowage.py::test_a_lock_across_read_and_write_gives_each_thread_its_own_slot
examples/37-the-gil-and-performance/tests/test_stowage.py::test_an_attribute_increment_is_a_separate_load_add_and_store
examples/37-the-gil-and-performance/tests/test_pools.py::test_every_pool_rates_the_batch_as_the_serial_loop_does
examples/37-the-gil-and-performance/tests/test_pools.py::test_threads_share_the_argument_and_processes_and_interpreters_copy_it
examples/37-the-gil-and-performance/tests/test_pools.py::test_a_process_pool_cannot_send_a_lambda
examples/38-asyncio-and-the-patterns/tests/test_await.py::test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote
examples/38-asyncio-and-the-patterns/tests/test_await.py::test_a_quote_that_is_never_awaited_warns_when_it_is_collected
examples/38-asyncio-and-the-patterns/tests/test_static.py::test_mypy_reports_a_quote_returned_without_await
examples/38-asyncio-and-the-patterns/tests/test_static.py::test_mypy_accepts_a_coroutine_bound_to_underscore
examples/38-asyncio-and-the-patterns/tests/test_stowage.py::test_an_await_between_read_and_write_double_books_a_slot
examples/38-asyncio-and-the-patterns/tests/test_stowage.py::test_an_asyncio_lock_gives_each_task_its_own_slot
examples/38-asyncio-and-the-patterns/tests/test_feed.py::test_breaking_out_of_async_for_leaves_the_feed_open
examples/38-asyncio-and-the-patterns/tests/test_feed.py::test_first_departure_closes_the_feed_when_it_stops_early
examples/38-asyncio-and-the-patterns/tests/test_feed.py::test_the_session_closes_the_feed_when_its_task_is_cancelled
examples/38-asyncio-and-the-patterns/tests/test_signal.py::test_a_failing_subscriber_does_not_stop_the_others
examples/38-asyncio-and-the-patterns/tests/test_signal.py::test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails
examples/38-asyncio-and-the-patterns/tests/test_quoting.py::test_a_failing_carrier_cancels_the_other_quote
examples/38-asyncio-and-the-patterns/tests/test_quoting.py::test_the_first_answer_cancels_the_rest_of_the_group
examples/38-asyncio-and-the-patterns/tests/test_commands.py::test_shutdown_lets_the_worker_drain_the_queue_then_stop
examples/29-metaclasses-init-subclass-and-registries/tests/test_static.py::test_mypy_refuses_self_in_a_metaclass_new
examples/26-decorators-done-right/tests/test_wraps.py::test_a_decorator_that_supplies_an_argument_reports_the_original_parameters
examples/26-decorators-done-right/tests/test_wraps.py::test_partial_reports_the_parameters_that_remain
examples/08-dataclasses-and-value-semantics/tests/test_generated.py::test_money_validates_and_of_normalises
```

## Corrections to the plan

1. Line numbers moved. Z1c edited chapters 7 to 11, 26 to 32, 37 and 38, so every `NN.md:line` in the plan's inventory is stale; the census lines above are current. The plan's quoted sentences were all re-found and hit exactly one line, with the exact wording the plan gives (straight apostrophes in the chapters' own prose, curly ones only inside quoted documentation).
2. Slide 6: the range `values.py:15-23` is unchanged by P4, but its longest line is now 92 characters (the P4 message `kilograms must be positive and finite, got ...`), not 81. The builder's per-call font size must be set from the real longest line (about 14 pt at 92 to 95).
3. Slide 16: the plan says "`partial` when the decorator supplies an argument (26.md:78, two tests)" without names. They are `test_a_decorator_that_supplies_an_argument_reports_the_original_parameters` and `test_partial_reports_the_parameters_that_remain`, both defined once in `examples/26-decorators-done-right/tests/test_wraps.py`.
4. Slide 7: the notes cover "validation without repair (08.md:157)" and the chapter names `test_money_validates_and_of_normalises`; the plan lists no test for it. Added as a notes witness (defined once, `test_generated.py:58`).
5. Slide 22: the claim `30.md:22` "That's interception with no surrogate, which is where Proxy is disambiguated" uses the book's bucket vocabulary, which the deck does not teach. The census keeps the sentence as the source and rewords the slide's claim (standalone wording below).
6. Slide 27: the plan's range `carriers.py:44-52` stops at the second refusal and shows nothing of the registration the claim is about. The census widens it to lines 44 to 58 (15 lines, longest 92 characters), still a contiguous run of the chapter's 32-line fence (block lines 18 to 32). Anchor: `super().__init_subclass__()`, 8 leading spaces.
7. Slide 28: the chapter says "What the metaclass costs shows in four places." The four are a metaclass conflict and three mypy limits (class keywords unchecked, `Self` refused in a metaclass `__new__`, a class from a metaclass registry typed `Any`). The plan's witness list omits the `Self` limit, so the table would have shown three costs under a sentence that says four. The census adds `test_mypy_refuses_self_in_a_metaclass_new` (defined once, `test_static.py:201`) and gives the table four cost rows and one row for what a metaclass buys (operators on the class, `test_only_a_metaclass_gives_the_class_object_operators`).
8. Slide 40: the plan leaves the claim line to the census. It is the Iterator row of the bucket table, `38.md:50`: "Leaving `async for` early doesn't close it; `aclosing` does". The table spans lines 48 to 55 as planned.
9. Slide 40 and slide 38 and slide 30 numbers: the plan's Decision 7 holds. The ratio sentence is `31.md:149`, and the warm ratios are `37.md:196-198`; both are line for line equal to their recorded sources (see Numbers in the notes). The lost-update outputs are dated 2026-11-07, one day after the other chapter 37 measurements.
10. Figure 09: the smallest label is 9.5 pt at the contained fit, not the 9.1 pt the plan's table gives (the F2 edit removed the edge and the label sizes in the spec are unchanged: 11.5 at 890 by 430). All five figures are at or above 6.8 pt.
11. Boundary section of the plan: Deck 101's `js:NNN` line references (270 to 300, 366 to 368, 371, 390, 484 to 494) are stale since the Z1a refactor, and the current builder names no test by identifier; the 101 slides state the claims in words. The conclusion is unchanged. Two near repeats (slides 30 and 32) carry conditions on the notes.
12. Count of tests: the plan names 143 distinct tests across the inventory; the census runs 147 (the four additions above). All 147 are defined exactly once.
13. Observation, not fixed here (Z1c's scope was fixed at P4 for chapters 8, 9 and 11): slide 20's excerpt, `descriptors_properties/fields.py:29-38`, shows `Positive.__set__` testing `not value.is_finite() or value <= 0` and raising `"{name} must be positive, got {value}"`, the same message-wider-than-condition pattern as P4's `Weight`. The tests match `must be positive` (`test_fields.py:40`, `:76`, `:81`), so the message is tested as it stands. The slide's claim does not depend on it. If the owner wants the P4 treatment applied to chapter 27, the message becomes `must be finite and positive` with the three `match=` strings changed together; the census range and anchor do not move because the message is on line 37 of an unchanged-length block. The census records it for a decision at the validation step.
14. Reconciliation rows: the plan's row 389 cites the census for the metaclass-cost, sources and books tables. The census holds all three (section "Table cells"); the metaclass table has five rows, not the four the plan's witnesses imply.

## Standalone wording (owner rule O4: the deck stands alone)

The rule: no slide text or note points to a chapter, an appendix or "the book's" text, and none points to another slide by number or position. A grep of the inventory's title, claim and notes columns for the QA step 8 terms (`follow`, `next`, `previous`, `earlier`, `later`, `above`, `below`, `the book`, `this book`, `chapter`, `appendix`, `member`, `slide N`) plus the plan's internal codes found the items below. No title contains a pointer; the pointers are in claim and notes text, and most are the plan's own evidence shorthand (a chapter line, a step id, a decision number) that must not reach the builder's strings. Each item gives the planned wording and the standalone wording to use.

| # | Slide | Planned wording | Problem | Standalone wording |
| --- | --- | --- | --- | --- |
| 1 | 2 | "the eight sections in order" | "in order" invites a sequence pointer, and each bullet must not say first, then or next | Eight bullets, one per theme, no ordinals: "The data model", "Contracts and cleanup", "Decorators done right", "Attribute access", "Dispatch and registries", "Pattern misuse", "Concurrency and the patterns", "Reference". Each names its subject, e.g. "Dispatch and registries: choosing behaviour by type, by class creation and by value". |
| 2 | 6 | "08.md:38 'This pattern dissolves.'" | "dissolves" is the book's bucket label; the deck defines no buckets | Say it directly: "A frozen, slotted dataclass supplies what the Value Object pattern wrote by hand: constructor, equality, hash and an assignment guard. What remains is the part no decorator can supply: the invariant." |
| 3 | 9 | "09.md:62 bucket" | same bucket label | "The return type says 'or nothing', and mypy refuses the call until the caller handles that case. The Null Object stand-in is not needed." |
| 4 | 11 | "09.md:162 bucket" ('Interface' needs disambiguating) | "disambiguating" is the bucket label | "Two mechanisms share the word interface. A Protocol is compared where a value is used. An ABC is checked when a subclass is built." |
| 5 | 13 | "10.md:36 bucket survives" | bucket label | "The language removes the try and finally from every call site. What release means, commit or discard, stays a decision of the writer." |
| 6 | 14 | "stated within P1's narrowed wording" | internal step code (P1) | State what the tests show: "A failed open discards the partials of every writer entered. On success each writer commits on its own as the stack unwinds, so the contract says nothing about a failure at commit time." |
| 7 | 22 | "30.md:22 ... which is where Proxy is disambiguated" | book vocabulary, and a pointer to a framework the deck does not teach | "A history can load itself on first read: attribute lookup that fails calls the object's own hook. There is no stand-in object, so this is interception, not a surrogate." |
| 8 | 25, 27, 29 | "dissolves into a single generic function"; "so the pattern dissolves"; "31.md:36 bucket" | the verb is the book's bucket label when it stands alone | Keep the chapters' own sentences where they explain the feature ("For an open set of kinds like this one it dissolves into a single generic function" reads as plain English) and never introduce "dissolves", "survives" or "disambiguates" as three named buckets. |
| 9 | 28 | "rows worded from 29.md:149-155, census" | chapter and census pointers in the plan | The table cells are stated as facts: "A second metaclass conflicts with the base's metaclass (TypeError)." and so on, with no source line. |
| 10 | 30, 38 | "the measured ratio as decision 7 labels it" | internal decision number | Label each number where it stands: "On Python 3.15.2, best of five repeats of one million calls, a present key cost 42.7 ns for the EAFP form against 50.4 ns look-first; an absent key cost 141.5 ns against 45.0 ns. No test asserts a time." Likewise "best of 3, workers 4, a 16-thread x86-64 CPU class" for slide 38. |
| 11 | 31 | "32.md:22 when the forces leave and the structure stays" | chapter pointer in the divider's notes column | "A pattern is a structure with a reason. When the forces leave and the structure stays, the price is still paid on each change." |
| 12 | 34 | "the boundary wording"; "Fowler's article and Seemann's ... credited" | "boundary" is a plan term for the other deck; the credits are fine as credits | Use the plan's three phrases: "an error mypy reports before the program runs", "a Protocol or ABC with one implementation", "pass the tariff as an argument". Name the Fowler article and the Seemann post only in the credit line. |
| 13 | 36 | "the free-threaded build not promoted" | would read as a position taken by "the book" | "The free-threaded build is tested here and measured; this deck does not recommend it." |
| 14 | 37 | "the lost-update counts only after P12" | internal step code | P12 has landed: "In recorded runs of the probe, 300 trials of four threads each adding 1 to a shared attribute 5,000 times lost an update in none on the default build and in all 300 on the free-threaded build. A race that does not fire on one build still exists." |
| 15 | 40 | "38.md:48-55 ... (census picks the line)" | chapter and census pointers | "Leaving async for early does not close an async generator. contextlib.aclosing does." |
| 16 | 42 | "sources, books, where the examples live" | "where the examples live" points at the closing slide; only that slide may name the site and repository | "The sources and books behind the code". |
| 17 | 43 | "the online sources the slides use (evidence S)"; notes "each, as the chapters word them" | evidence code, and a pointer to the chapters | Title "Sources credited"; notes: "Each source is named with its authors and what the slide uses it for." |
| 18 | 44 | "the books the 201 chapters cite (evidence S)" | evidence code, "201 chapters" | Title "Reading further"; notes: "These books cover the ground the slides compress." |
| 19 | 45 | "the site and repository URLs (evidence Q)"; "the other two decks by theme" | evidence code; the closing slide may name the site and repository and the other decks | Fine on this slide only: the site URL, the repository URL, how to run an example, the pinned versions, and the two further decks by theme. |
| 20 | all | a quoted chapter sentence that starts "in the example", "this chapter" or "this member" | these phrases point at the book | Quote only the sentences the census lists; phrases the census marks in "Sentences no slide may quote" never appear. |

No title needs a change. The Boundary table's own "(slides 9, 10)" style references and every `NN.md:line` stay in the plan and the evidence and never reach the builder's text.

## Cuts and narrowings

None. Every claim has a witness test or a recorded chapter sentence, and no chapter now contradicts one. Slides 22, 27 and 28 are reworded or widened as recorded above; no claim is stretched.

2026-11-07 (Z5 repair 1): Corrections item 13 is out of date. `Positive.__set__` and the property setters in `conftest.py` now raise "must be positive and finite"; the sign-only test-local setter in `test_fields.py` keeps "must be positive". Slide 18 also cites `test_a_function_wrapper_binds_self_on_a_method`, and slide 39 also cites `test_mypy_reports_a_quote_call_whose_result_is_never_used`. Both are defined once and pass.
