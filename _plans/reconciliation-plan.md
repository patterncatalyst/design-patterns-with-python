---
title: "Reconciliation plan"
order: 9
output: false
---

# PDP-009: reconciliation plan

Internal planning file, excluded from the site. No C# reconciliation file exists to
mirror, so this follows the same log style as the spikes report. A claim in a 🔬
chapter is not asserted until a runnable experiment confirms it; the result is then
recorded here and the chapter quotes real, scrubbed output. Performance claims live in
a benchmark script with recorded output, never in test assertions. Free-threaded
Python is out of scope.

Status values: open, verified, adjusted, dropped.

| # | Ch | Claim | How to verify | Status |
| --- | --- | --- | --- | --- |
| 1 | 2 | Most Strategy, Command and Factory classes collapse to functions or dicts of callables in Python | Implement the ch12/15/16 cases both ways; the same behaviour table passes for both; count types and lines | **adjusted** (r02). Strategy and Factory Method are witnessed in the chapter 3 example; Command is split (the deferred call dissolves to a partial, undo survives); type and line counts move to the Strategy, Command and Factory chapters. Evidence: witnesses 1, 2, 11, 12 green (19/19, 3 runs, 2026-11-03) |
| 2 | 2 | First-class functions, duck typing and generators remove the need for scaffolding 1994 patterns assumed | Witness test per claim in `spikes/feature-spikes` | **verified** (r02). verified by the dissolve witnesses in `examples/03-three-way-split`. Evidence: witnesses 1-10 green (19/19, 3 runs, 2026-11-03) |
| 3 | 3 | Each pattern's dissolve/survive/disambiguate bucket is correct | One runnable witness per row; row stays only if the witness passes | **adjusted** (r02). Dissolve and disambiguate rows are witnessed in `examples/03-three-way-split`; survive rows are verified in their own chapters. Evidence: witnesses 1-19 green (19/19, 3 runs, 2026-11-03); no map row changed |
| 4 | 3 | "Disambiguate" patterns (Decorator, Singleton, Proxy) have two real meanings in Python | Paired examples: GoF object wrapping and `@decorator`; module singleton and class Singleton | **verified** (r02). verified by the disambiguate witnesses in `examples/03-three-way-split`. Evidence: witnesses 13-19 green (19/19, 3 runs, 2026-11-03) |
| 5 | 20 | Runtime decorator objects on a `RateCalculator` Protocol compose per instance and in a chosen order; `@retry`/`@audited` on `quote()` do not give per-instance composition | Spike 010: shipping types, both mechanisms, stacking-order witness | open |
| 6 | 20 | A `functools.wraps`-less wrapper loses `__name__` and signature | Spike 010 assertion on `__name__`, `inspect.signature` | open |
| 7 | 25 | singledispatch, `match` and classic double dispatch give the same Visitor result over `Document` kinds | Spike 012/014: one table of cases through three dispatchers | open |
| 8 | 25 | `assert_never` makes a missing `match` arm a type error | Spike 014: mypy strict run on a deliberately incomplete `match`, recorded output | open |
| 9 | 28 | singledispatch registers on type annotations and works on 3.15 (including union types) | Spike 012 on the pinned interpreter | open (2026-11-04, r05: spike tests re-run green on 3.15.2; the first run was on 3.14.10) |
| 10 | 28 | `singledispatchmethod` dispatches on the first non-self argument | Spike 012 | open |
| 11 | 30 | `__getattr__` is called only on failed normal lookup; `__getattribute__` on every access | Small experiment with a call counter | open |
| 12 | 30 | `__getattr__` proxy avoids infinite recursion only when it uses `object.__getattribute__`/`__dict__` | Experiment: failing recursion case, then the fixed one | open |
| 13 | 29 | `__init_subclass__` replaces most metaclass registries | Spike 013: same registry both ways, conflict case for metaclasses | open |
| 14 | 33 | A patch must target the namespace where the name is looked up, not where it is defined | Experiment with `unittest.mock.patch` on both targets | open |
| 15 | 33 | Python has seams that need no source change: module attributes, injected callables, `monkeypatch` | Legacy `RateEngine` fixture; each seam gets a test | open |
| 16 | 34 | Each dependency-breaking technique preserves behaviour | Characterisation tests before and after every step | open |
| 17 | 37 | Under the GIL, threads do not speed up CPU-bound work but do help I/O-bound work | Benchmark script, scrubbed recorded output; tests assert correctness only | open |
| 18 | 37 | Processes speed up CPU-bound work at a pickling and startup cost | Same benchmark script, three batch sizes | open |
| 19 | 37 | asyncio helps I/O-bound work and does not help CPU-bound work; a blocking call stalls the loop | Benchmark script; a deterministic test that a blocking callback delays an `Event`-gated task, ordering only | open |
| 20 | 38 | An async generator is the async form of the Iterator pattern (`async for`) | Spike 015: ordering asserted with `asyncio.Event` and `gather`, no sleep | open |
| 21 | 38 | `async with` is the async Context Manager; cancellation still runs `__aexit__` | Spike 015 cancellation test | open |
| 22 | 38 | A coroutine can be a Command (create, queue, await later) and a forgotten `await` is detectable | Spike 015 plus mypy/warning output | open |
| 23 | 38 | Deterministic async tests need no sleep | Run the suite 3 times consecutively; grep tests for `sleep` | open |
| 24 | 39 | The final project integrates all seven domain areas without a framework | End-to-end acceptance test; idiom scan | open |
| 25 | 40 | Typical LLM output for patterns is Java-in-Python and fails strict mypy or the idiom scan | Collect sample outputs, run the scan, record results | open |
| 26 | 14 | A probabilistic state machine is reproducible with an injected seeded RNG | Seeded run equality test | open |
| 27 | 9 | `Optional` plus mypy makes Null Object unnecessary in most cases | mypy strict run on missing-carrier code, recorded output | open |
| 28 | 31 | EAFP beats LBYL for shared mutable state and costs little when the key is present | Race-free witness test; speed note only in a benchmark script | open |
| 29 | 5 | Replacing one collaborator changes only the outputs it feeds (a tariff moves net and, through it, tax; a tax rule moves only tax; a sink moves nothing) | `test_each_change_moves_only_the_fields_it_feeds` | **verified** (r03). Evidence: examples/05-srp-ocp-lsp, 18/18 green, 3 runs, mypy 2.4.1 output matched the plan, 2026-11-03 |
| 30 | 5 | A new tax rule arrives from outside the package without editing `quote`; the default is read-only | `test_a_new_tax_rule_is_added_without_editing_quote`, `test_default_tax_table_is_read_only` | **verified** (r03). Evidence: examples/05-srp-ocp-lsp, 18/18 green, 3 runs, mypy 2.4.1 output matched the plan, 2026-11-03 |
| 31 | 5 | mypy checks override signatures (an argument narrowed to a subtype, with the LSP note, widened return, `@override` misspelling) and Protocol conformance at the use site; accepts a widened argument | ch5 tests 10-12 | **verified** (r03). Evidence: examples/05-srp-ocp-lsp, 18/18 green, 3 runs, mypy 2.4.1 output matched the plan, 2026-11-03 |
| 32 | 5 | mypy cannot see a strengthened precondition or weakened postcondition; the contract suite catches both | ch5 tests 8, 9, 13 | **verified** (r03). Evidence: examples/05-srp-ocp-lsp, 18/18 green, 3 runs, mypy 2.4.1 output matched the plan, 2026-11-03 |
| 33 | 6 | A track-only fake satisfies the narrow Protocol and fails the fat one under mypy | ch6 test 2 | **verified** (r03). Evidence: examples/06-isp-dip-and-di-without-a-framework, 17/17 green, 3 runs, mypy 2.4.1 output matched the plan, 2026-11-03 |
| 34 | 6 | Policy modules import no adapters; adapters import neither policy nor Protocols | ch6 tests 4-5 | **verified** (r03). Evidence: examples/06-isp-dip-and-di-without-a-framework, 17/17 green, 3 runs, mypy 2.4.1 output matched the plan, 2026-11-03 |
| 35 | 6 | An autospec mock is `Any` to mypy even for the wrong Protocol, but enforces the shape at runtime | ch6 tests 6-7 | **verified** (r03). Evidence: examples/06-isp-dip-and-di-without-a-framework, 17/17 green, 3 runs, mypy 2.4.1 output matched the plan, 2026-11-03 |
| 36 | 6 | mypy 2.4.1 checks a partial's bound argument and calls, not its assignment to a `Callable` annotation | ch6 test 8 | **verified** (r03). Evidence: examples/06-isp-dip-and-di-without-a-framework, 17/17 green, 3 runs, mypy 2.4.1 output matched the plan, 2026-11-03 |
| 37 | 7 | Operators and builtins call the special method on the type; an instance attribute named `__len__` is ignored | ch7 test 1 | **verified** (r04). Evidence: examples/07-the-data-model, 25/25 green, 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 38 | 7 | Equal values must hash equal: `__eq__` alone sets `__hash__` to None; a custom `__eq__` in a frozen dataclass keeps a field hash and breaks set membership; mypy is silent | ch7 tests 2-5, 19 | **verified** (r04). Evidence: examples/07-the-data-model, 25/25 green, 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 39 | 7 | Returning `NotImplemented` hands the operation to the other operand: `factor * price` reaches `Money.__rmul__`; foreign operands raise `TypeError`; `sum()` needs `start=`; mypy checks operand types when the parameter is typed with the class | ch7 tests 6-8, 17, 18 | **adjusted** (r04): `sum(prices)` without `start=` is `[arg-type]` under mypy 2.4.1, not `[list-item]`. Evidence: examples/07-the-data-model, 25/25 green, 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 40 | 7 | `total_ordering` derives `<=`, `>`, `>=`; with `__lt__` alone `>` works by reflection and `<=` fails; sorting quotes by total needs `Money.__lt__` at runtime and under mypy | ch7 tests 9-11, 18 | **verified** (r04). Evidence: examples/07-the-data-model, 25/25 green, 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 41 | 7 | `bool` falls back to `__len__` and `in` to `__iter__`; an iterable without `__len__` is truthy when empty; iterable isn't subscriptable | ch7 tests 12-14 | **verified** (r04). Evidence: examples/07-the-data-model, 25/25 green, 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 42 | 7 | mypy requires `__eq__` to accept `object`, reporting `[override]` with the LSP note | ch7 test 16 | **verified** (r04). Evidence: examples/07-the-data-model, 25/25 green, 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 43 | 8 | A frozen slotted dataclass supplies Value Object's equality, hash and immutability (dissolve); frozen is a `__setattr__` guard and is shallow; slots drop weak references until `weakref_slot` | ch8 tests 1-5 | **verified** (r04). Evidence: examples/08-dataclasses-and-value-semantics, 32/32 green (23 functions), 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 44 | 8 | A mutable consignment shared between bookings aliases; `replace` gives a new value and reruns `__post_init__`; a mutable eq dataclass is unhashable and mypy accepts it as a key | ch8 tests 6-9, 19 | **adjusted** (r04): the 3.14 unhashable message names the class's module-qualified name (unchanged on 3.15.2, re-run 2026-11-04) (for any class outside `__main__`); tests match `unhashable type: '<Name>'`. Evidence: examples/08-dataclasses-and-value-semantics, 32/32 green (23 functions), 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 45 | 8 | `order=True` orders by field tuple, would order `Money` across currencies, and refuses a hand-written `__lt__` | ch8 tests 10-12 | **adjusted** (r04): mypy also flags a hand-written `__lt__` under `order=True` with `[misc]` on the `def` (kept as a typed ignore witness). Evidence: examples/08-dataclasses-and-value-semantics, 32/32 green (23 functions), 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 46 | 8 | `compare=False`, `kw_only`, `eq=False` and `default_factory` behave as documented; mypy checks frozen assignment, kw_only, `replace` keywords and missing order, but not mutable defaults or weakrefs to slotted instances | ch8 tests 13-19 | **verified** (r04). Evidence: examples/08-dataclasses-and-value-semantics, 32/32 green (23 functions), 3 runs, mypy 2.4.1, deletion table clean, 2026-11-03 |
| 47 | 0-8 | Every quoted output and inline message in chapters 0-8 reproduces on 3.15.2 and mypy 2.4.1, or is re-quoted from a fresh run | `run: A4` | open |
| 48 | 9 | `X \| None` makes absence a branch: unguarded access is `[union-attr]`; walrus, match and early return narrow; `assert` narrows but is removed under `-O` | `test_mypy_requires_a_branch_for_absence`, `test_book_with_turns_absence_into_a_booking_error`, `source: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement` | open |
| 49 | 9 | A null gateway hides a lost booking and mypy accepts it; a null object is right where doing nothing is the answer | `test_a_null_gateway_hides_a_lost_booking`, `test_mypy_accepts_a_null_gateway`, `test_no_discount_is_a_null_object_that_loses_nothing` | open |
| 50 | 9 | A 3.15 `sentinel` separates not-given from `None`, is truthy, keeps identity under copy, and mypy narrows it with `is` | `test_a_sentinel_separates_not_given_from_none`, `test_mypy_requires_a_branch_for_the_sentinel`, `source: https://peps.python.org/pep-0661/` | open |
| 51 | 9 | PEP 695 Protocol variance is inferred: a general quoter serves the narrow type, the narrow quoter is rejected, and it fails at runtime | `test_mypy_infers_quoter_variance`, `test_a_general_quoter_serves_hazmat_consignments`, `test_a_hazmat_quoter_fails_on_a_general_consignment_at_runtime` | open |
| 52 | 9 | A callback Protocol with `/` ignores parameter names; without it, names must match | `test_callback_protocol_accepts_any_parameter_name`, `test_mypy_matches_callback_parameter_names_without_slash` | open |
| 53 | 9 | Protocol is checked at use, ABC at construction; an explicit Protocol subclass is abstract to mypy but instantiable; `override` catches a misspelling; an ABC subclass also satisfies the Protocol | `test_mypy_checks_protocols_at_use_and_abcs_at_construction`, `test_abc_refuses_an_incomplete_subclass_at_construction`, `test_explicit_protocol_subclass_is_nominal_and_still_instantiable`, `test_both_carriers_satisfy_the_protocol_one_by_inheritance`, `test_mypy_explains_a_conflicting_member_but_not_a_wholly_absent_one` | open |
| 54 | 9 | `runtime_checkable` checks names only; data protocols refuse `issubclass`; 3.15 warns on an undecorated sub-protocol | `test_runtime_checkable_checks_names_only`, `test_a_data_protocol_refuses_issubclass`, `test_an_undecorated_subprotocol_warns_on_isinstance` | open |
| 55 | 10 | Without `with`, an exception leaves the handle open; `ManifestWriter` and `manifest_file` close on every path and commit only on success | `test_without_with_an_exception_leaves_the_handle_open`, `test_writer_closes_and_discards_on_an_exception`, `test_writer_commits_only_on_success`, `test_writer_is_single_use` | open |
| 56 | 10 | The generator form needs `try`, and mypy can't see it missing | `test_the_generator_form_needs_try`, `test_mypy_cannot_see_a_missing_try` | open |
| 57 | 10 | `ExitStack` unwinds entered resources in reverse order when a later one fails | `test_exit_stack_unwinds_entered_writers_in_reverse_order`, `test_exit_stack_commits_every_manifest_on_success` | open |
| 58 | 10 | A truthy `__exit__` swallows; mypy's reachability follows `__exit__`'s return type | `test_a_truthy_exit_swallows_the_exception`, `test_mypy_reads_exit_return_type_for_reachability` | open |
| 59 | 10 | On 3.15 a context manager decorating a generator function spans iteration (before 3.15 it exited at creation) | `test_a_context_manager_decorating_a_generator_spans_iteration`, `source: https://docs.python.org/3.15/whatsnew/3.15.html`, run: _plans/evidence/contextlib-decorator-generator.md | open |
| 60 | 11 | A plain Mock passes an assertion on a misspelled method; spec rejects names only; autospec rejects names and signatures | `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method`, `test_spec_rejects_unknown_names_but_not_wrong_signatures`, `test_autospec_rejects_names_and_signatures`, `test_book_best_books_only_the_winner`, `test_a_fake_rejects_unknown_names_and_wrong_signatures` | open |
| 61 | 11 | Every mock is assignable to every type for mypy because typeshed subclasses mocks from `Any`; a hand-written fake is checked | `test_mypy_accepts_every_mock_where_a_gateway_is_expected`, `test_mypy_checks_a_hand_written_fake`, `source: https://github.com/python/typeshed/blob/main/stdlib/unittest/mock.pyi` | open |
| 62 | 11 | An injected clock and a code tie-break make quote tests deterministic; `monkeypatch.context` restores the environment | `test_quote_validity_comes_from_the_injected_clock`, `test_best_quote_picks_the_cheapest_carrier`, `test_validity_reads_the_environment_and_the_context_restores_it`, `test_a_tie_is_broken_by_the_carrier_code_in_the_quote`, `test_carriers_are_asked_in_code_order` | open |
| 63 | 11 | `assert_type` is a static assertion and a runtime no-op; a typed ignore is a static regression test | `test_assert_type_is_static_only`, `run: 1c` | open |
| 64 | 11 | `yield` fixture teardown runs on failure; strict markers, config and xfail refuse silence; `filterwarnings = error` fails on a deprecation | `run: 5`, `source: https://docs.pytest.org/en/stable/how-to/fixtures.html`, `source: https://docs.pytest.org/en/stable/reference/reference.html`, run: _plans/evidence/yield-fixture-teardown-on-failure.md | open |

2026-11-04 (r05): Python 3.15.2. Rows 47 to 64 are added at the move to 3.15.2 and start `open`; the r05 steps fill in their evidence. Rows 1 to 46 were verified on 3.14.10 and keep that evidence; row 47 covers the re-run of their quoted output on 3.15.2.

## Process

1. Pick the claim, write the experiment under `spikes/feature-spikes` or the chapter
   example, run it 3 times.
2. Record the outcome in the Status column and in `_plans/spikes.md` if a spike.
3. If the claim fails, adjust the chapter's thesis before drafting, never after.
