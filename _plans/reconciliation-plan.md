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
| 9 | 28 | singledispatch registers on type annotations and works on 3.14 (including union types) | Spike 012 on the pinned interpreter | open |
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
| 29 | 5 | Replacing one collaborator changes only its own output | `test_each_change_moves_only_its_own_field` | open |
| 30 | 5 | A new tax rule arrives from outside the package without editing `quote`; the default is read-only | `test_a_new_tax_rule_is_added_without_editing_quote`, `test_default_tax_table_is_read_only` | open |
| 31 | 5 | mypy checks override signatures (narrowed argument with the LSP note, widened return, `@override` misspelling) and Protocol conformance at the use site; accepts a widened argument | ch5 tests 10-12 | open |
| 32 | 5 | mypy cannot see a strengthened precondition or weakened postcondition; the contract suite catches both | ch5 tests 8, 9, 13 | open |
| 33 | 6 | A track-only fake satisfies the narrow Protocol and fails the fat one under mypy | ch6 test 2 | open |
| 34 | 6 | Policy modules import no adapters; adapters import neither policy nor Protocols | ch6 tests 4-5 | open |
| 35 | 6 | An autospec mock is `Any` to mypy even for the wrong Protocol, but enforces the shape at runtime | ch6 tests 6-7 | open |
| 36 | 6 | mypy 2.4.1 checks a partial's bound argument and calls, not its assignment to a `Callable` annotation | ch6 test 8 | open |

## Process

1. Pick the claim, write the experiment under `spikes/feature-spikes` or the chapter
   example, run it 3 times.
2. Record the outcome in the Status column and in `_plans/spikes.md` if a spike.
3. If the claim fails, adjust the chapter's thesis before drafting, never after.
