---
title: "Evidence: xUnit test patterns mapped onto existing tests (r21, X1a)"
output: false
render_with_liquid: false
---

# Appendix D witness file: Meszaros test patterns and the book's tests

Recorded 2026-11-07 for r21, step X1a, on Python 3.15.2 and pytest 9.2.0, at commit `bbe9b9b` on `release/r21` (the working tree also held uncommitted edits to `_plans/iteration-plan.md`, `_plans/shipping-domain-model.md`, `bibliography.html` and `scripts/chapters.toml`; no test, source or `uv.lock` file differed from the commit). Nothing here edits a test.

## Method

- The pages were fetched with `curl -s` over `http://` on 2026-11-07 (`https://xunitpatterns.com/` timed out at planning). Every one of the 26 returned HTTP 200. The summary is the page's `summary-statement` span with the tags removed, the entities decoded and the whitespace collapsed (runs of spaces, tabs and newlines become one space); nothing else is changed. All 26 strings equal the sentences in the plan's evidence D table. Each page opens with the site's note "The book has now been published and the content of this chapter has likely changed substanstially." (the site's spelling), so every summary is the pre-publication text.
- The tests were run in a fresh scratch copy built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <dir>`, then `rm -rf .venv .venv-ft` and `uv sync --locked --all-packages`. `testing_baseline.__file__`, `mocking_reference.__file__` and `pytest_reference.__file__` each pointed into `<scratch>/examples/...`. The copy was deleted afterwards. No sync ran in the real repo.
- A node id below is `<path>::<test name>`; for a parametrised test the id names the function and pytest runs every case. Each name is defined exactly once across `examples/*/tests` (grep `def <name>(`).
- Vocabulary (decision 4): pytest-mock's `stub` is "a mock object that accepts any arguments and is useful to test callbacks" (usage page, `https://pytest-mock.readthedocs.io/en/stable/usage.html`, HTTP 200) and is never a Meszaros Test Stub. A `Mock` or autospec asserted after the exercise step is the Test Spy style.

## Run results

31 distinct test names (29 kept-row tests, plus `test_spy_keeps_the_real_behaviour_and_records_returns` for the vocabulary section and the cut Fake Object test), 60 cases. The `-p no:randomly` flag is not needed (pytest-randomly is not installed); reverse order lists the node ids reversed.

| Run | Order | Summary line |
| --- | --- | --- |
| 1 | forward | `60 passed in 1.15s` |
| 2 | forward | `60 passed in 1.07s` |
| 3 | forward | `60 passed in 1.06s` |
| 4 | reverse | `60 passed in 1.08s` |

The multi-case tests: `test_every_step_matches_the_characterisation_table` 25 cases, `test_the_acceptance_test_fails_when_a_stage_is_left_out` 4, `test_best_quote_picks_the_cheapest_carrier` 3; the other 28 names are one case each (31 names, 60 cases).

## Summary: pattern, page, verdict

| Pattern | Page | Verdict | Cited tests |
| --- | --- | --- | --- |
| Four-Phase Test | HTTP 200 | keep | `test_quote_validity_comes_from_the_injected_clock` |
| Test Double | HTTP 200 | keep (umbrella) | `test_side_effect_drives_the_timeout_branch`, `test_best_quote_picks_the_cheapest_carrier` |
| Dummy Object | HTTP 200 | keep | `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` |
| Test Stub | HTTP 200 | keep | `test_side_effect_drives_the_timeout_branch`, `test_a_carrier_that_times_out_is_skipped` |
| Test Spy | HTTP 200 | keep | `test_book_best_books_the_winner_and_returns_its_reference`, `test_stub_records_a_callback`, `test_a_rejected_reply_is_sent_back_with_its_findings`, `test_book_best_books_only_the_winner` |
| Mock Object | HTTP 200 | contrast only (no instance) | none |
| Fake Object | HTTP 200 | CUT | `test_the_feed_yields_events_in_order_and_closes_at_the_end` |
| Configurable Test Double | HTTP 200 | keep | `test_best_quote_picks_the_cheapest_carrier`, `test_book_best_books_only_the_winner` |
| Hard-Coded Test Double | HTTP 200 | keep | `test_airco_quote_converts_kilograms_and_cents`, `test_the_acceptance_test_fails_when_a_stage_is_left_out` |
| Test-Specific Subclass | HTTP 200 | keep | `test_every_step_matches_the_characterisation_table`, `test_a_misspelt_override_falls_through_to_the_real_carrier` |
| Fresh Fixture | HTTP 200 | keep | `test_tmp_path_is_a_fresh_directory_per_test`, `test_a_factory_fixture_builds_a_fresh_object_per_call` |
| Shared Fixture | HTTP 200 | keep | `test_a_module_scoped_fixture_is_set_up_once_for_the_module`, `test_yield_fixtures_tear_down_in_reverse_order_of_setup` |
| Standard Fixture | HTTP 200 | keep | `test_book_best_books_only_the_winner`, `test_side_effect_drives_the_timeout_branch` |
| Implicit Setup | HTTP 200 | keep | `test_an_autouse_fixture_runs_without_being_named` |
| Inline Setup | HTTP 200 | keep | `test_an_unrecorded_prompt_is_refused` |
| Delegated Setup | HTTP 200 | keep | `test_a_quote_rounds_half_up_to_the_cent`, `test_a_clean_batch_returns_its_quotes_in_order` |
| Creation Method | HTTP 200 | keep | `test_a_factory_fixture_builds_a_fresh_object_per_call` |
| Implicit Teardown | HTTP 200 | keep | `test_yield_fixtures_tear_down_in_reverse_order_of_setup`, `test_quote_validity_comes_from_the_injected_clock` |
| Automated Teardown | HTTP 200 | keep (qualified) | `test_validity_reads_the_environment_and_the_context_restores_it`, `test_monkeypatch_undoes_its_changes_when_the_context_ends` |
| State Verification | HTTP 200 | keep | `test_a_clean_batch_returns_its_quotes_in_order`, `test_best_quote_picks_the_cheapest_carrier` |
| Behavior Verification | HTTP 200 | keep | `test_book_best_books_only_the_winner` |
| Guard Assertion | HTTP 200 | keep | `test_null_object_is_an_optional_checked_by_mypy` |
| Custom Assertion | HTTP 200 | keep (qualified) | `test_a_booking_request_ships_end_to_end`, `test_the_acceptance_test_fails_when_a_stage_is_left_out` |
| Test Utility Method | HTTP 200 | keep | `test_the_refactored_engine_matches_the_golden_quotes` |
| Parameterized Test | HTTP 200 | keep (qualified) | `test_every_step_matches_the_characterisation_table` |
| Dependency Injection | HTTP 200 | keep | `test_booking_service_runs_against_an_injected_fake`, `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`, `test_two_threads_parked_between_read_and_write_take_the_same_slot` |

Tally of the 26 pages: 24 have at least one instance (Automated Teardown, Custom Assertion and Parameterized Test with a qualification; Test Double as the umbrella), Mock Object is the contrast with no instance, Fake Object is cut.

## Patterns

### Four-Phase Test

- Page: `http://xunitpatterns.com/Four%20Phase%20Test.html`
- Summary (exact, whitespace collapsed): "Structure each test with four distinct parts executed in sequence."
- Verdict: **keep**
- Tests:
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_quote_validity_comes_from_the_injected_clock`
    Reason: the fixtures `consignment`, `fixed_now`, `make_fake`, `quote_log` and `_engine(...)` are the setup, `engine.best_quote(...)` is the single exercise, the asserts verify, and the `quote_log` fixture tears down after its `yield`.

### Test Double

- Page: `http://xunitpatterns.com/Test%20Double.html`
- Summary (exact, whitespace collapsed): "We replace a component on which the SUT depends with a "test-specific equivalent.""
- Verdict: **keep (umbrella)**
- Tests:
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_side_effect_drives_the_timeout_branch`
    Reason: two `create_autospec` gateways replace the real `CarrierGateway` objects the `RateEngine` depends on, and the engine cannot tell.
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_best_quote_picks_the_cheapest_carrier`
    Reason: the hand-written `FakeGateway` replaces each real carrier gateway.
- Note: The umbrella; the kinds are the rows below.

### Dummy Object

- Page: `http://xunitpatterns.com/Dummy%20Object.html`
- Summary (exact, whitespace collapsed): "We pass an object that has no implementation as an argument of a method called on the SUT."
- Verdict: **keep**
- Tests:
  - `examples/43-appendix-c-mocking/tests/test_booking.py::test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first`
    Reason: `notify=mocker.stub()` is passed to `book_cheapest` because the signature needs a callback, and nothing ever reads or asserts it.
- Note: The pytest-mock `stub` is used here as a Dummy Object, which is not Meszaros's Test Stub.

### Test Stub

- Page: `http://xunitpatterns.com/Test%20Stub.html`
- Summary (exact, whitespace collapsed): "We replace a real object with a test-specific object that feeds the desired indirect inputs into the system under test."
- Verdict: **keep**
- Tests:
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_side_effect_drives_the_timeout_branch`
    Reason: `slow.quote.side_effect = CarrierTimeoutError(...)` and `quick.quote.return_value = ...` feed indirect inputs to the engine, which is what the page describes (the last line, `slow.quote.assert_called_once_with(...)`, is a spy-style check on top).
  - `examples/43-appendix-c-mocking/tests/test_booking.py::test_a_carrier_that_times_out_is_skipped`
    Reason: `slow.quote.side_effect = CarrierTimeoutError("slow")` feeds the timeout to `book_cheapest` as an indirect input.
- Note: These are the Test Stubs of the book. pytest-mock's `stub` is never one.

### Test Spy

- Page: `http://xunitpatterns.com/Test%20Spy.html`
- Summary (exact, whitespace collapsed): "Use a Test Double to capture the indirect output calls made to another component by the system under test (SUT) for later verification by the test."
- Verdict: **keep**
- Tests:
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_book_best_books_the_winner_and_returns_its_reference`
    Reason: `FakeGateway.book` appends to `booked` while the engine runs, and the test asserts `winner.booked == [consignment]` and `loser.booked == []` after the exercise step.
  - `examples/43-appendix-c-mocking/tests/test_spies.py::test_stub_records_a_callback`
    Reason: the `mocker.stub(name="notify")` object captures the call `book_cheapest` makes to it, and the test asserts `assert_called_once_with` afterwards.
  - `examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py::test_a_rejected_reply_is_sent_back_with_its_findings`
    Reason: `RecordedAssistant.reply` appends every prompt it receives to `prompts`, and the test compares `assistant.prompts` after `propose(...)` returns (it also replays recorded replies, so it is a stub as well).
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_book_best_books_only_the_winner`
    Reason: added by X1a: a `create_autospec` mock whose `assert_called_once_with` and `assert_not_called` run after the exercise step; that is the Test Spy style, decision 4.
- Note: A `Mock` asserted afterwards is spy style, not Mock Object style. The fourth test is an addition to the plan (see Differences).

### Mock Object

- Page: `http://xunitpatterns.com/Mock%20Object.html`
- Summary (exact, whitespace collapsed): "Replace an object the system under test (SUT) depends on with a test-specific object that verifies it is being used correctly by the SUT."
- Verdict: **contrast only (no instance)**
- Tests: none.
- Note: The page defines an object that "verifies it is being used correctly" as calls arrive and fails the test itself. No existing test sets expectations on a double before the exercise step and lets the double fail the test; every `Mock` in the repo is asserted afterwards. The row has no witness and is kept as the contrast the appendix needs (decision 4), not as a pattern the book instantiates.

### Fake Object

- Page: `http://xunitpatterns.com/Fake%20Object.html`
- Summary (exact, whitespace collapsed): "Replace a component that the system under test (SUT) depends on with a much lighter-weight implementation."
- Verdict: **CUT**
- Tests:
  - `examples/38-asyncio-and-the-patterns/tests/test_feed.py::test_the_feed_yields_events_in_order_and_closes_at_the_end`
    Reason: REJECTED: `InMemoryFeed` has no I/O and records `closed`, but `feed_of(*KINDS)` hands it the events the test wants the code under test to read. That is the test injecting indirect inputs (a control point, so a Test Stub or Configurable Test Double), and the Fake Object page says "while a Test Stub acts as a control point to inject indirect inputs into the SUT the Fake Object does not"; the `closed` flag is a Test Spy. The repo has no double that holds self-consistent state across calls (the `Recording*` and `Fake*` classes in `examples/*/tests` and `src` were listed and each is configured with its answers or only records calls).
- Note: Cut. The Fake Object row leaves D, and `FakeGateway` stays a Configurable Test Double (decision 4).

### Configurable Test Double

- Page: `http://xunitpatterns.com/Configurable%20Test%20Double.html`
- Summary (exact, whitespace collapsed): "Configure a reusable Test Double with the values to be returned or verified during the fixture setup phase of a test."
- Verdict: **keep**
- Tests:
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_best_quote_picks_the_cheapest_carrier`
    Reason: `make_fake("fastline", _usd(fastline))` builds a `FakeGateway` configured with its carrier name and amount in the test's setup, three parametrised cases.
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_book_best_books_only_the_winner`
    Reason: `create_autospec(CarrierGateway, instance=True)` plus `winner.quote.return_value = ...` is configured with the values to return before the exercise (the page's generated-double variation).

### Hard-Coded Test Double

- Page: `http://xunitpatterns.com/Hard-Coded%20Test%20Double.html`
- Summary (exact, whitespace collapsed): "Build the Test Double by hard-coding the return values and/or expected calls."
- Verdict: **keep**
- Tests:
  - `examples/34-dependency-breaking-techniques/tests/test_steps.py::test_airco_quote_converts_kilograms_and_cents`
    Reason: `airco_fake` is a closure that always returns `2800`; the answer is written into the double, not configured.
  - `examples/39-final-project/tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out`
    Reason: `_InertGateway` returns the constant `"FL-0"` and books nothing, `_zero_rule` always returns `0.00`, and `_zero_duty` always returns a zero duty.

### Test-Specific Subclass

- Page: `http://xunitpatterns.com/Test-Specific%20Subclass.html`
- Summary (exact, whitespace collapsed): "Add methods that expose the state or behavior needed by the test to a subclass of the SUT."
- Verdict: **keep**
- Tests:
  - `examples/34-dependency-breaking-techniques/tests/test_characterisation.py::test_every_step_matches_the_characterisation_table`
    Reason: its `subclass` case (25 cases in all, 5 of them `subclass`) runs `_FakeCarrierRateEngine`, a subclass of the engine (`_ExtractedCallsRateEngine`) that overrides `_fastline_quote` and `_airco_price` to reach fakes; the subclass lives in the tests and changes nothing in `src`.
  - `examples/34-dependency-breaking-techniques/tests/test_steps.py::test_a_misspelt_override_falls_through_to_the_real_carrier`
    Reason: the test defines `Misspelt`, a subclass of the engine written inside the test to override the extracted calls, and shows what a misspelt override does.
- Note: The page's Behavior-Modifying use (overriding the calls) rather than State Exposing; the page lists both under one name.

### Fresh Fixture

- Page: `http://xunitpatterns.com/Fresh%20Fixture.html`
- Summary (exact, whitespace collapsed): "Each test constructs its own brand-new test fixture for its own private use."
- Verdict: **keep**
- Tests:
  - `examples/42-appendix-b-pytest/tests/test_builtin_fixtures.py::test_tmp_path_is_a_fresh_directory_per_test`
    Reason: the generated tests assert that each starts with an empty `tmp_path`, a new directory per test.
  - `examples/42-appendix-b-pytest/tests/test_fixtures.py::test_a_factory_fixture_builds_a_fresh_object_per_call`
    Reason: `first == second` and `first is not second`: each call builds a new object.
- Note: Both tests are about pytest's behaviour; the first one asserts on tests it generates with `pytester`.

### Shared Fixture

- Page: `http://xunitpatterns.com/Shared%20Fixture.html`
- Summary (exact, whitespace collapsed): "We reuse the same instance of the test fixture across many tests."
- Verdict: **keep**
- Tests:
  - `examples/42-appendix-b-pytest/tests/test_fixtures.py::test_a_module_scoped_fixture_is_set_up_once_for_the_module`
    Reason: the generated module's `scope="module"` fixture `shared` is set up once for two tests while the function-scoped `fresh` is set up twice (`setup shared` once, `setup fresh` twice), so the scope is shared.
  - `examples/42-appendix-b-pytest/tests/test_fixtures.py::test_yield_fixtures_tear_down_in_reverse_order_of_setup`
    Reason: the module-scoped `outer` is set up once and torn down after both tests, the function-scoped `inner` around each.
- Note: The test asserts the scope, which the instance rule asks for.

### Standard Fixture

- Page: `http://xunitpatterns.com/Standard%20Fixture.html`
- Summary (exact, whitespace collapsed): "The same design of test fixture is used in several tests."
- Verdict: **keep**
- Tests:
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_book_best_books_only_the_winner`
    Reason: takes the conftest `consignment` and `fixed_now` fixtures, the same fixture design as the engine tests.
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_side_effect_drives_the_timeout_branch`
    Reason: takes the same `consignment` and `fixed_now` fixtures.
- Note: Weakest of the fixture rows: the same two fixtures serve most tests in the member; two are cited.

### Implicit Setup

- Page: `http://xunitpatterns.com/Implicit%20Setup.html`
- Summary (exact, whitespace collapsed): "Build the test fixture common to several tests in the setUp method."
- Verdict: **keep**
- Tests:
  - `examples/42-appendix-b-pytest/tests/test_fixtures.py::test_an_autouse_fixture_runs_without_being_named`
    Reason: `note_autouse` is `autouse=True` in the conftest, so the framework runs it before the test without the test asking: `ran == ["autouse"]`.
- Note: The page says `setUp`; pytest's `autouse` is the same idea, a framework-run setup. Not every fixture is Implicit Setup: a fixture named in the signature is explicit.

### Inline Setup

- Page: `http://xunitpatterns.com/Inline%20Setup.html`
- Summary (exact, whitespace collapsed): "Each Test Method creates it's own Fresh Fixture by calling the appropriate constructor methods to build exactly the test fixture it requires."
- Verdict: **keep**
- Tests:
  - `examples/40-working-with-ai-and-llm-tools/tests/test_assistant.py::test_an_unrecorded_prompt_is_refused`
    Reason: the test builds `RecordedAssistant({_PROMPT: ["reply"]})` itself, in its own body, with no fixture.
- Note: The page's summary has the misspelling "it's"; a quote stops before it or paraphrases.

### Delegated Setup

- Page: `http://xunitpatterns.com/Delegated%20Setup.html`
- Summary (exact, whitespace collapsed): "Each test creates its own Fresh Fixture by calling Creation Methods from within the Test Methods."
- Verdict: **keep**
- Tests:
  - `examples/42-appendix-b-pytest/tests/test_rating.py::test_a_quote_rounds_half_up_to_the_cent`
    Reason: the test builds its fixture with `make_consignment(kilograms="3.3")` inside its own body.
  - `examples/42-appendix-b-pytest/tests/test_rating.py::test_a_clean_batch_returns_its_quotes_in_order`
    Reason: builds a two-consignment batch with two `make_consignment(...)` calls.

### Creation Method

- Page: `http://xunitpatterns.com/Creation%20Method.html`
- Summary (exact, whitespace collapsed): "Set up the test fixture by calling methods that hide the mechanics of building ready-to-use objects behind Intent Revealing Names."
- Verdict: **keep**
- Tests:
  - `examples/42-appendix-b-pytest/tests/test_fixtures.py::test_a_factory_fixture_builds_a_fresh_object_per_call`
    Reason: `make_consignment` hides `Consignment(ConsignmentId(...), zone, Weight(Decimal(...)))` behind defaults and the intent-revealing keyword `kilograms=`.
- Note: The page's Parameterized Creation Method variation, delivered as a pytest factory fixture.

### Implicit Teardown

- Page: `http://xunitpatterns.com/Implicit%20Teardown.html`
- Summary (exact, whitespace collapsed): "The Test Automation Framework calls our clean up logic in the tearDown method after every Test Method."
- Verdict: **keep**
- Tests:
  - `examples/42-appendix-b-pytest/tests/test_fixtures.py::test_yield_fixtures_tear_down_in_reverse_order_of_setup`
    Reason: the code after `yield` in `outer` and `inner` runs after the tests with no call from them, and the test asserts the order.
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_quote_validity_comes_from_the_injected_clock`
    Reason: the `quote_log` fixture writes `teardown` after its `yield`; the test itself does not assert that, `_plans/evidence/yield-fixture-teardown-on-failure.md` records it (and that it runs on failure).
- Note: The second row is supported by a recorded file, not by an assertion in the test.

### Automated Teardown

- Page: `http://xunitpatterns.com/Automated%20Teardown.html`
- Summary (exact, whitespace collapsed): "We keep track of all resources that are created in a test and automatically destroy/free them during teardown."
- Verdict: **keep (qualified)**
- Tests:
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_environment.py::test_validity_reads_the_environment_and_the_context_restores_it`
    Reason: `monkeypatch.context()` records three changes (`setenv`, `delenv`, `setenv`) and the test asserts that all of them are undone together.
  - `examples/33-seams-in-python/tests/test_patching.py::test_monkeypatch_undoes_its_changes_when_the_context_ends`
    Reason: two `setattr` changes are recorded and undone together at the end of the context, and the originals are asserted back.
- Note: QUALIFIED. Both tests use the explicit `with monkeypatch.context()` form, which undoes at the end of the `with` block. The page says "during teardown". The fixture form undoes at teardown by the same mechanism, but no test asserts that (the fixture form appears in `test_registry_is_init_subclass` and `examples/34-dependency-breaking-techniques/tests/conftest.py`, where nothing checks the restore). D must say "at the end of the context, or at teardown for the fixture itself". If the owner wants no qualification, cut this row.

### State Verification

- Page: `http://xunitpatterns.com/State%20Verification.html`
- Summary (exact, whitespace collapsed): "We inspect the state of the system under test (SUT) after it has been exercised and compare it to the expected state."
- Verdict: **keep**
- Tests:
  - `examples/42-appendix-b-pytest/tests/test_rating.py::test_a_clean_batch_returns_its_quotes_in_order`
    Reason: asserts only on the returned quotes.
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_engine.py::test_best_quote_picks_the_cheapest_carrier`
    Reason: asserts only on the returned quote's carrier.

### Behavior Verification

- Page: `http://xunitpatterns.com/Behavior%20Verification.html`
- Summary (exact, whitespace collapsed): "We capture the indirect outputs of the SUT as they occur and compare them to the expected behavior."
- Verdict: **keep**
- Tests:
  - `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_book_best_books_only_the_winner`
    Reason: `winner.book.assert_called_once_with(consignment)` and `loser.book.assert_not_called()` check the calls the engine made to its collaborators.

### Guard Assertion

- Page: `http://xunitpatterns.com/Guard%20Assertion.html`
- Summary (exact, whitespace collapsed): "Replace an if statement in a test with an assertion that fails the test if not satisfied."
- Verdict: **keep**
- Tests:
  - `examples/03-three-way-split/tests/test_dissolve.py::test_null_object_is_an_optional_checked_by_mypy`
    Reason: `assert gateway is not None` stands where an `if gateway is not None:` would otherwise wrap the call, and it narrows the type for mypy.

### Custom Assertion

- Page: `http://xunitpatterns.com/Custom%20Assertion.html`
- Summary (exact, whitespace collapsed): "Create a purpose-built Assertion Method that compares only those attributes of the object that define test-specific equality."
- Verdict: **keep (qualified)**
- Tests:
  - `examples/39-final-project/tests/test_acceptance.py::test_a_booking_request_ships_end_to_end`
    Reason: `acceptance_failures(shipment, history, client, plan)` takes everything it needs as parameters, has no side effects and makes six checks, each on only the attributes that define the slice's acceptance.
  - `examples/39-final-project/tests/test_acceptance.py::test_the_acceptance_test_fails_when_a_stage_is_left_out`
    Reason: the same helper, with the expected failure list per left-out stage.
- Note: QUALIFIED. The helper returns a list of failure strings and the test asserts `== []`; it does not itself fail the test, which the page's Assertion Method does. D must say that (the plan says so). The page's "Verification Method" mention covers helpers that interact with the SUT, which this one does not.

### Test Utility Method

- Page: `http://xunitpatterns.com/Test%20Utility%20Method.html`
- Summary (exact, whitespace collapsed): "We encapsulate the test logic we want to reuse behind a suitably named utility method."
- Verdict: **keep**
- Tests:
  - `examples/35-fowler-vs-feathers/tests/test_golden.py::test_the_refactored_engine_matches_the_golden_quotes`
    Reason: `_observed(...)` and `_mismatches(...)` hold logic reused by five tests behind names that say what they do.

### Parameterized Test

- Page: `http://xunitpatterns.com/Parameterized%20Test.html`
- Summary (exact, whitespace collapsed): "We pass the information needed to do fixture setup and result verification to a utility method that implements the entire test lifecycle."
- Verdict: **keep (qualified)**
- Tests:
  - `examples/34-dependency-breaking-techniques/tests/test_characterisation.py::test_every_step_matches_the_characterisation_table`
    Reason: one test method per row passes the row (inputs and expected result) to `_observed(...)`, which builds the engine form, exercises it and returns what to compare; the whole method is a single exercise and a single assert.
- Note: QUALIFIED. `_observed` covers setup and exercise, and the verification stays in the test method; `pytest.mark.parametrize` generates the test cases from the rows instead of the test calling a utility method. D says the pytest difference (plan). 25 cases from 5 forms x 5 rows.

### Dependency Injection

- Page: `http://xunitpatterns.com/Dependency%20Injection.html`
- Summary (exact, whitespace collapsed): "The client provides the depended-on object to the SUT."
- Verdict: **keep**
- Tests:
  - `examples/06-isp-dip-and-di-without-a-framework/tests/test_dip.py::test_booking_service_runs_against_an_injected_fake`
    Reason: `BookingService(fake, records.append)` passes the dependencies through the constructor.
  - `examples/34-dependency-breaking-techniques/tests/test_steps.py::test_a_parameterised_engine_keeps_the_real_carriers_as_defaults`
    Reason: `parameterised.RateEngine(fastline_quote=fastline_fake)` injects one dependency by keyword and the default stays for the other.
  - `examples/37-the-gil-and-performance/tests/test_stowage.py::test_two_threads_parked_between_read_and_write_take_the_same_slot`
    Reason: `StowagePlan("SAILING-1", lock=nullcontext(), gap=barrier_gap)` injects the lock and the gap callable through the constructor; `gap` is a parameter, not a Test Hook.
- Note: Constructor-injection variation; the page also names method arguments and settable attributes.

## Vocabulary witnesses (decision 4)

These are not D patterns; they support the "Two vocabularies" section. All three were run in the same four runs above.

- pytest-mock `stub` used as a spy: `examples/43-appendix-c-mocking/tests/test_spies.py::test_stub_records_a_callback` (the stub records the callback call and the test asserts it afterwards; Test Spy by role).
- pytest-mock `stub` used as a dummy: `examples/43-appendix-c-mocking/tests/test_booking.py::test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` (passed, never read; Dummy Object by role).
- pytest-mock `spy`: `examples/43-appendix-c-mocking/tests/test_spies.py::test_spy_keeps_the_real_behaviour_and_records_returns` calls `fastline.quote(...)` itself on the wrapped real object and then reads `spy_return`; it records a call the test made, not an indirect output of a system under test, so it is not a Test Spy in the page's sense.
- `Mock` asserted afterwards is spy style: `examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py::test_book_best_books_only_the_winner`. The Test Spy page: "Because a Test Spy does not fail the test at the first deviation from the expected behavior like a Mock Object," (the sentence runs on; D quotes to the comma or paraphrases).
- `FakeGateway` (`examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/conftest.py`) is configured with `amount` and `times_out` and records `booked`: a Configurable Test Double used as stub and spy, not a Fake Object.

## Conditional Test Logic instances for r25 (decision 13)

Recorded only; no test was edited. Whether each is a smell is the r25 QA sweep's judgement.

1. `examples/43-appendix-c-mocking/tests/test_patching.py`, `test_patch_dict_restores_the_mapping_after_the_test`, line 32: `if before is None: monkeypatch.delenv(...) else: monkeypatch.setenv(...)`, a branch on the parameter in the fixture-setup phase.
2. `examples/35-fowler-vs-feathers/tests/test_golden.py`, `test_the_golden_file_records_the_legacy_engine`, line 97: `if request.config.getoption("--update-golden"):` writes the file and skips, otherwise asserts.
3. `examples/05-srp-ocp-lsp/tests/test_srp.py`, `test_each_change_moves_only_the_fields_it_feeds`, lines 43 and 56: a `match replaced:` in the setup and an `if replaced == "audit-sink":` in the verification.

Related wording, also recorded only: `examples/37-the-gil-and-performance/src/gil_and_performance/stowage.py` line 18, the `StowagePlan` docstring, calls `gap` "a test seam" (the page for Test Hook is cut; `gap` is a parameter taking a callable, so it is Dependency Injection).

## Cut list

- **Fake Object** (this step): rejected, reason under its heading.
- Cut at planning and unchanged: Persistent Fresh Fixture and Mystery Guest (404 at planning, not fetched again here), Delta Assertion, Data-Driven Test, Test Hook, Dependency Lookup, Humble Object, Back Door Manipulation, Minimal Fixture, Testcase Class per Fixture, Test Helper, Chained Tests, Inline Teardown, Garbage-Collected Teardown, Lazy Setup, Setup Decorator, SuiteFixture Setup, Assertion Message and the smells. This step did not re-fetch or re-judge them.
- Not cut but weak, for X5's one-in-three re-read: Standard Fixture (two tests that share two fixtures), Inline Setup (one test), Implicit Setup (one test).

## Differences from the plan

1. Fake Object is cut (the plan left it to X1a).
2. Test Spy gains a fourth test, `test_book_best_books_only_the_winner`, because decision 4 names that style.
3. Automated Teardown, Custom Assertion and Parameterized Test are kept with the qualifications recorded under their headings; Automated Teardown is the one most likely to be cut if the owner wants every row to match the page without a rider.
4. Test Double (umbrella) cites two tests where the plan said "the rows below".
5. Standard Fixture cites `test_side_effect_drives_the_timeout_branch` and `test_book_best_books_only_the_winner` as in the plan, but both are in `test_doubles.py` of chapter 11 (the plan's evidence lists them under ch11 without the file).
6. The run was at `bbe9b9b` (the branch head), not at the planning commit `97207d4`; the scratch copy included the working-tree edits listed in the first paragraph.
7. The plan says 25 patterns have instances; with Fake Object cut and Mock Object a contrast, 24 of the 26 pages have instances.
