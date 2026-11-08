// deck-301.js: "Design Patterns with Python", 301: Testing, legacy code and AI.
// Build from presentation/ with: node deck-301.js
// The slide helpers live in deck-lib.js; code slides are read from the shipped
// examples by path and line range and anchor-asserted there.

"use strict";

const H = require("./deck-helpers.js");
const { createDeck } = require("./deck-lib.js");
const { COLOR, FONT, W, ASSETS, newDeck, addContentTitle } = H;

const OUT = "design-patterns-with-python-301-testing-legacy-and-ai.pptx";

const pres = newDeck();
pres.title = "Design Patterns with Python: 301, Testing, legacy code and AI";
pres.subject = "Companion deck to Design Patterns with Python";
pres.author = "PatternCatalyst";
pres.company = "PatternCatalyst";
pres.lastModifiedBy = "PatternCatalyst";

const { S, divider, bullets, bulletSlide, tableSlide, codeSlide, figSlide, notes, bump, finish } = createDeck(pres);

const EX = "examples";
const E11 = `${EX}/11-testing-with-pytest-pytest-mock-and-mypy`;
const E33 = `${EX}/33-seams-in-python`;
const E34 = `${EX}/34-dependency-breaking-techniques`;
const E35 = `${EX}/35-fowler-vs-feathers`;
const E36 = `${EX}/36-refactor-or-rewrite`;
const E39 = `${EX}/39-final-project`;
const E40 = `${EX}/40-working-with-ai-and-llm-tools`;
const E42 = `${EX}/42-appendix-b-pytest`;
const E43 = `${EX}/43-appendix-c-mocking`;

// ===========================================================================
// Cover
// ===========================================================================
{
  const s = pres.addSlide();
  bump();
  s.background = { color: COLOR.white };
  s.addImage({ path: `${ASSETS}/cover-panel.png`, x: 0, y: 0, w: W, h: 7.5 });
  s.addText("DESIGN PATTERNS WITH PYTHON", {
    x: 6.00, y: 1.98, w: 6.90, h: 0.34,
    fontFace: FONT.title, fontSize: 14, bold: true, color: COLOR.red, charSpacing: 6,
    align: "left", valign: "middle",
  });
  s.addText([
    { text: "Design Patterns", options: { breakLine: true } },
    { text: "with Python" },
  ], {
    x: 5.95, y: 2.42, w: 6.95, h: 2.00,
    fontFace: FONT.title, fontSize: 48, bold: true, color: COLOR.ink,
    align: "left", valign: "top",
  });
  s.addText("301: Testing, legacy code and AI", {
    x: 6.00, y: 4.65, w: 6.70, h: 0.90,
    fontFace: FONT.body, fontSize: 18, italic: true, color: COLOR.caption,
    align: "left", valign: "top",
  });
  s.addImage({ path: `${ASSETS}/logo-candidate-2.png`, x: 11.10, y: 6.80, w: 1.55, h: 0.37 });
  notes(s, `This is the third deck in a series on the Gang of Four patterns in Python. It covers proving that code works, changing code somebody else wrote, and holding an assistant's reply to a set of gates. The listings are read from tested examples at build time, and the examples are set in one shipping domain of consignments, carriers, rate quotes and tracking. Where a test witnesses a claim, its name is given, so the claim can be re-run. What to show: the title and the subtitle. Fallback: the subtitle names the three subjects.`, 45, "cover");
}

// ===========================================================================
// Themes
// ===========================================================================
{
  const s = S();
  addContentTitle(s, "SECTIONS", "Eight sections");
  const left = [
    ["Proving it works:", " a test named as a claim, and a check seen failing."],
    ["Fixtures and test doubles:", " settings that refuse silence, and what each double records."],
    ["Seams in Python:", " a global name is a seam, and a patch has to land where the name is looked up."],
    ["Breaking dependencies:", " change the structure, keep the behaviour, record the behaviour first."],
  ];
  const right = [
    ["Refactor or rewrite:", " intent rows, golden quotes and a rewrite held to parity."],
    ["The final project:", " one booking through its steps, undone on a refusal."],
    ["Working with AI tools:", " a reply trusted as far as the gates it has passed."],
    ["Reference:", " sources, books and where the code lives."],
  ];
  bullets(s, left, { w: 5.95, fontSize: 18, gap: 14 });
  bullets(s, right, { x: 6.85, w: 5.86, fontSize: 18, gap: 14 });
  notes(s, `Eight sections make up Testing, legacy code and AI. Proving it works covers a test named as a claim and a check that has been seen to fail. Fixtures and test doubles covers the pytest settings that refuse silence and what each kind of double records. Seams in Python shows that a global name is a seam. Breaking dependencies changes structure while the behaviour is recorded first. Refactor or rewrite separates intent rows from golden values. The final project undoes a booking on a refusal, and working with AI tools holds a reply to three gates. The reference section lists the sources, the books and where the code lives. What to show: nothing runs here. Fallback: each bullet names a section and its subject.`, 90, "themes");
}

// ===========================================================================
// Section: Proving it works
// ===========================================================================
divider("01", "Proving it works", "A claim, its witness and a failing run",
  `A test is named for the claim it witnesses, so a failure reads as a broken sentence. A check that was never seen to fail is a guess, and each check is deleted in a scratch copy to see it fail. The cases are the winner's reference asserted before the calls, what each kind of double refuses, what mypy accepts of a mock, and a clock and an environment that leave nothing to patch. What to show: the section name. Fallback: the subtitle states the method.`);

codeSlide("PROVING IT WORKS", "Tests named as claims",
  `${E11}/tests/test_doubles.py`, 19, 34,
  "def test_book_best_books_only_the_winner(",
  "The winner's reference is asserted first; then the calls show the loser was never booked.",
  `The engine books only the winner, and the test name says so, so a failure reads as a broken sentence. It also asserts the return value, the winner's reference, ahead of the asserts on the calls, because an assertion that a method was called doesn't say the customer got the right reference (test_book_best_books_only_the_winner, test_book_best_books_the_winner_and_returns_its_reference). The winner is an autospec of the carrier gateway that has quote and book. A check that was never seen to fail is a guess, so each check is deleted in a scratch copy. With the engine's booking method changed to book every gateway, two tests fail, the two named here, 32 pass, and mypy still exits 0. What to show: the two asserts, then the experiment. Fallback: the test name carries the claim.`);

tableSlide("PROVING IT WORKS", "Doubles and refusals",
  ["Double", "Unknown name", "Wrong call", "mypy"], [
    ["FakeGateway", "AttributeError; mypy attr-defined", "TypeError; mypy call-arg", "rejects a missing member"],
    ["Mock()", "accepted", "accepted", "accepted"],
    ["Mock(spec=CarrierGateway)", "AttributeError", "accepted", "accepted"],
    ["create_autospec(CarrierGateway, instance=True)", "AttributeError", "TypeError", "accepted"],
  ], [3.9, 3.4, 2.6, 2.19],
  `Each kind of double refuses something different. The table hands each one a name that doesn't exist and a call with the wrong shape. The hand-written fake refuses both, and mypy checks it too (test_a_fake_rejects_unknown_names_and_wrong_signatures). A plain mock refuses nothing (test_a_plain_mock_passes_an_assertion_on_a_misspelled_method), and a spec closes the first gap and not the second (test_spec_rejects_unknown_names_but_not_wrong_signatures). An autospec refuses both at run time (test_autospec_rejects_names_and_signatures). The CarrierGateway here is the one with quote and book. That inline plain mock plays the negative case for the engine's claim: it passes a misspelt assertion. Credits: Martin Fowler's Mocks Aren't Stubs for the vocabulary of doubles. What to show: the Mock row, then the autospec row. Fallback: the table states each refusal.`, { rowH: 0.8, fontSize: 14, y: 1.7 });

codeSlide("PROVING IT WORKS", "Autospec and signatures",
  `${E11}/tests/test_doubles.py`, 59, 66,
  "def test_autospec_rejects_names_and_signatures(mocker: MockerFixture) -> None:",
  "create_autospec copies the signatures, so a misspelt name and a call with no consignment both raise.",
  `create_autospec copies the signatures of its target, so a misspelt name raises AttributeError and a call with no consignment raises TypeError (test_autospec_rejects_names_and_signatures). The mypy side is different: mypy accepts every one of the mocks where a carrier gateway is expected (test_mypy_accepts_every_mock_where_a_gateway_is_expected). typeshed declares the mock classes as subclasses of Any, and its comment reads 'We subclass with "Any" because mocks are explicitly designed to stand in for other types, something that can't be expressed with our static type system.' A hand-written fake gets a static check, and mypy rejects one that misses a member (test_mypy_checks_a_hand_written_fake). The side_effect argument drives a branch the happy path never reaches (test_side_effect_drives_the_timeout_branch). Credits: the unittest.mock documentation on autospeccing, and typeshed's mock stub. What to show: the two raises. Fallback: the caption.`);

codeSlide("PROVING IT WORKS", "Clock and environment",
  `${E11}/tests/test_environment.py`, 8, 20,
  "def test_validity_reads_the_environment_and_the_context_restores_it(",
  "The one test that touches the real environment sets and removes the variable inside monkeypatch.context().",
  `The engine takes its clock as an argument, so a test that passes clock=lambda: fixed_now has nothing to patch and nothing to wait for (test_quote_validity_comes_from_the_injected_clock). Carriers are asked in sorted code order, and a tie is broken by the carrier code (test_carriers_are_asked_in_code_order, test_a_tie_is_broken_by_the_carrier_code_in_the_quote). The environment comes in as a mapping, and the listing is the one test that touches the real one. It captures the value before, whatever the shell left there, and compares after the with block (test_validity_reads_the_environment_and_the_context_restores_it). This engine takes its gateways, a clock and a validity. The slide shows the test that touches the real environment and the assert that proves it was restored. Credits: the pytest fixtures and monkeypatch how-to guides. What to show: the with block and the last assert. Fallback: the caption.`);

// ===========================================================================
// Section: Fixtures and test doubles
// ===========================================================================
divider("02", "Fixtures and test doubles", "Settings, collisions and records",
  `The pytest settings decide what a run is willing to pass over: an unregistered marker, a passing xfail and a warning can all leave a green run unless a setting refuses them. Two test files that share a basename collide under one import mode and not under the other. A mock records its calls, and assert_has_calls checks a stricter thing than its name suggests. The mock libraries and the xUnit literature use stub and spy for different things. What to show: the section name. Fallback: the subtitle names the three subjects.`);

bulletSlide("FIXTURES AND TEST DOUBLES", "Settings that refuse silence", [
  ["Strict markers", " fail collection on a marker nobody registered."],
  ["Strict xfail", " fails the run when a test marked as expected to fail passes."],
  ["Strict config", " fails the run on an option pytest doesn't know."],
  ["A warning filter set to error", " turns a deprecation into a failure."],
  ["One configuration file", " applies to a run: a subdirectory's table replaces the root's, with no merge."],
], `Under pytest's defaults, an unregistered marker, an xfail test that passes and a deprecation in the end-of-run summary all leave a green run. Four settings refuse what those defaults let through. Each is tested by an inner session run with and without the setting; three assert the exact outcome counts of both runs, and the strict-config run is asserted by its usage-error exit status and message (test_an_unregistered_marker_fails_collection_under_strict_markers, test_a_passing_xfail_fails_the_run_under_strict_xfail, test_an_unknown_option_fails_under_strict_config, test_filterwarnings_error_turns_a_warning_into_a_failure). One configuration file applies to a run: the first one found wins and the files aren't merged (test_the_first_config_file_wins_and_is_not_merged). A test builds a subdirectory table and the header names that table's own file (test_a_member_table_replaces_the_root_filter_and_names_its_own_file). Credits: the pytest reference, configuration and capture-warnings pages, and Brian Okken's Python Testing with pytest. What to show: the first two tests. Fallback: the bullets.`);

codeSlide("FIXTURES AND TEST DOUBLES", "Same-name test files",
  `${E42}/tests/test_import_modes.py`, 15, 28,
  "def _two_files_with_one_basename(pytester: pytest.Pytester) -> None:",
  "Two test files share one basename; under prepend the run has one collection error, an import file mismatch.",
  `The helper writes two test files with one basename into an inner session. Under the prepend import mode pytest reports an import file mismatch, and the run has one collection error (test_same_basename_test_files_collide_under_prepend). Under importlib each file gets a unique module name, so the collision goes away (test_importlib_mode_gives_each_test_file_a_unique_name). The cost sits on the same page of the pytest documentation: test modules can't import each other, and a test that runs from conftest import LIMIT errors at collection with ModuleNotFoundError (test_importlib_mode_cannot_import_conftest_by_name). Shared values reach tests through fixtures, which pytest discovers without an import, and a test module imports a type from conftest.py under TYPE_CHECKING, so nothing is imported at run time. Credits: the pytest page on import mechanisms. What to show: run the listing's test and read the one collection error. Fallback: the caption.`);

codeSlide("FIXTURES AND TEST DOUBLES", "Ordered call records",
  `${E43}/tests/test_calls.py`, 81, 91,
  "def test_assert_has_calls_checks_a_contiguous_ordered_run(mocker: MockerFixture) -> None:",
  "assert_has_calls accepts a contiguous ordered run; a gap and a reversal raise, and any_order=True accepts both.",
  `assert_has_calls is stricter than its name suggests, and looser than comparing mock_calls with a list. Three bookings are made, and a contiguous ordered run passes. A gap raises, and so does a reversal. Passing any_order=True drops both conditions and so is the weaker check (test_assert_has_calls_checks_a_contiguous_ordered_run). To say the calls were exactly these, compare mock_calls with a list (test_mock_calls_records_calls_in_order_with_call_objects). Two related facts: spec_set refuses setting a name the spec lacks (test_spec_set_refuses_setting_a_name_the_spec_lacks), and an assertion typo raises instead of passing (test_an_assertion_typo_raises_instead_of_passing). A mock bypasses the static check. A stub keeps its call count after resetall (test_resetall_resets_patches_spies_and_autospecs_but_not_stubs). Credits: the unittest.mock page and the pytest-mock usage page. What to show: the gap and the reversal. Fallback: the caption.`);

tableSlide("FIXTURES AND TEST DOUBLES", "Two vocabularies",
  ["Word", "pytest-mock meaning", "Meszaros meaning"], [
    ["Stub", "mocker.stub(): a mock that accepts any call, for testing callbacks.", "A Test Stub, a double that feeds indirect inputs to the code under test."],
    ["Spy", "mocker.spy records a call the test made on a wrapped real object.", "A Test Spy, a double that captures the indirect outputs of the code under test for later verification."],
  ], [1.6, 5.2, 5.29],
  `Two names in the mock libraries collide with Meszaros's. pytest-mock's stub is a callback recorder (test_stub_records_a_callback), where a Test Stub feeds indirect inputs to the code under test. mocker.spy keeps the real behaviour and records the returns (test_spy_keeps_the_real_behaviour_and_records_returns), so it records a call the test made, where a Test Spy records an indirect output. When a test says stub or spy, ask which vocabulary it is in. Dummy Object is qualified: book_cheapest calls the stub with the booking reference, and the test never reads it (test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first). Credits: Gerard Meszaros's xUnit Test Patterns and xunitpatterns.com, the pytest-mock usage page, and Martin Fowler's Mocks Aren't Stubs on state against behaviour verification. What to show: the two rows. Fallback: the two rows.`, { rowH: 1.1, fontSize: 14, y: 1.7 });

// ===========================================================================
// Section: Seams in Python
// ===========================================================================
divider("03", "Seams in Python", "A global name is looked up at call time",
  `Python looks a global name up when the call runs, so a global that inherited code reads is a seam. A test can change what the code calls without touching its source. The work is in choosing where the patch lands: the name the engine looks up, which is not necessarily the module that defines it. Defaults captured at definition and reloaded modules defeat a patch, and mypy sees none of this. A parameter is the way out. What to show: the section name. Fallback: the subtitle states the mechanism.`);

codeSlide("SEAMS IN PYTHON", "An engine kept as found",
  `${E33}/src/seams/legacy.py`, 17, 31,
  "class RateEngine:",
  "The inherited engine holds its own binding of the FASTLINE function and reads the AIRCO module by attribute.",
  `Test code can still change what the calls do, because Python looks a global name up when the call runs. This is the inherited engine, before any parameter. request_quote is a function imported by name, so the legacy module holds its own binding of it. The AIRCO call goes through the module's attribute. A test of the engine reaches the real carrier (test_the_legacy_engine_calls_the_real_carrier), and the stand-in SDKs do no I/O: where a real one would open a connection, each raises the error a timeout would. Feathers's seam, a place where behaviour can be changed from outside the code, and its enabling point, the spot where the change is made, are credited to Working Effectively with Legacy Code, under "The Seam Model". What to show: the two lookups in quote. Fallback: the caption.`);

figSlide("SEAMS IN PYTHON", "The patch target", "33-seams-in-python",
  "The test patches the name in the legacy namespace, which the engine reads twice; the two dashed boxes are notes with no arrow.",
  `A patch replaces a name where the engine looks it up. The figure runs from the test, which calls monkeypatch.setattr on the legacy namespace, to the engine that reads request_quote there and airco.price on the AIRCO module (test_patching_the_name_where_it_is_looked_up_replaces_the_carrier, test_a_module_attribute_is_patched_on_the_module_it_belongs_to). The two dashed boxes are notes and reach nothing. A patch aimed at the module that defines the function leaves the engine calling the real carrier (test_patching_where_a_from_import_was_defined_leaves_the_engine_calling_the_real_carrier), and unittest.mock's patch applies the same rule (test_unittest_mock_patch_follows_the_same_lookup_rule). With the patch aimed at the defining module, one test fails and 20 pass, and mypy exits 0. The import form decides the target. "Mock the carrier in this test" leaves the target open. Credits: the unittest.mock page, Where to patch. What to show: the arrows, then the two dashed notes. Fallback: the caption.`);

codeSlide("SEAMS IN PYTHON", "A default captured early",
  `${E33}/tests/test_seams.py`, 64, 78,
  "def test_patching_a_module_constant_misses_a_default_captured_at_definition(",
  "Patching the margin constant leaves the quote at 27.50; passing margin= gives 50.00.",
  `A default argument is a value captured at definition, so a patch to the global it was copied from can't change it. The listing patches the margin constant and still gets 27.50, while passing margin= to the constructor gives 50.00 (test_patching_a_module_constant_misses_a_default_captured_at_definition). A reload has the opposite trouble: it re-runs the module body into the same dictionary, which overwrites a live patch and keeps old bindings (test_reload_discards_a_patch_and_keeps_old_bindings). Both monkeypatch and mock.patch refuse a missing name by default, and each has a switch that turns the refusal into a silent miss (test_monkeypatch_with_raising_false_creates_a_name_nothing_reads, test_patch_refuses_a_name_the_module_does_not_have). Credits: the importlib documentation for reload. What to show: the two asserts. Fallback: the caption.`);

bulletSlide("SEAMS IN PYTHON", "Patches and mypy", [
  ["A replacement of the wrong shape", " passes mypy: mypy exits 0 and the test fails at run time."],
  ["A misspelt target string", " passes mypy as well, because the target is only a string."],
  ["A direct assignment", " to a module name is checked and reported."],
  ["A fake passed to a Protocol parameter", " is checked, and a fake of the wrong shape is rejected before the test runs."],
], `mypy exits 0 with no errors on a monkeypatched replacement of the wrong shape, and the test then raises TypeError at run time (test_mypy_does_not_check_a_monkeypatched_replacement). It also accepts a misspelt target string (test_mypy_accepts_a_misspelt_monkeypatch_target_string). A direct assignment is checked: mypy reports an assignment error and an attr-defined error for the module name (test_mypy_checks_a_direct_assignment_to_a_module_name). A parameter is checked by mypy, and a fake of the wrong shape is rejected before the test runs, with an arg-type error (test_mypy_checks_a_fake_passed_to_a_protocol_parameter). A patch is the way to get the first test around code that can't change yet, and a parameter replaces it once the code can change. What to show: the exit code of the patched replacement. Fallback: the bullets state each check.`);

// ===========================================================================
// Section: Breaking dependencies
// ===========================================================================
divider("04", "Breaking dependencies", "Change the structure, keep the behaviour",
  `A dependency-breaking step changes structure and leaves behaviour alone, and the evidence is a record taken before the step. A characterisation table records what the code does, so that a change can be told apart from a fix. The same table then runs against five forms of the engine: the legacy engine, carriers as parameters, a wrapper that fits the quoter shape, the engine as a function, and a subclass that overrides a method name. mypy checks the steps that use parameters and says nothing about a patch. What to show: the section name. Fallback: the subtitle states the rule.`);

codeSlide("BREAKING DEPENDENCIES", "A characterisation table",
  `${E34}/tests/test_characterisation.py`, 67, 76,
  "    Row(",
  "A row that pins a 0.0006 kg weight: converted to grams it truncates to zero, and AIRCO quotes a cent.",
  `A characterisation test records what code does, so that a change can be told apart from a fix. The row converts 0.0006 kg to zero grams because int truncates, so AIRCO is asked about a weightless parcel and the quote is a cent. A reviewer might call that wrong, and the table pins it anyway, and runs it against five forms of the engine (test_every_step_matches_the_characterisation_table). A table that can't fail proves nothing (test_the_table_catches_a_step_that_changes_behaviour). A carrier timeout fails the quote in every form (test_every_step_lets_a_carrier_timeout_fail_the_quote). With a timeout-swallowing change added to the engine with carrier parameters, two tests fail and 40 pass, the 25 table cases pass, and mypy exits 0: the record of behaviour catches it. Credits: Feathers, in Working Effectively with Legacy Code, under "I Need to Make a Change, but I Don't Know What Tests to Write". What to show: the row's weight and its quote. Fallback: the caption.`);

codeSlide("BREAKING DEPENDENCIES", "Carriers as parameters",
  `${E34}/src/dependency_breaking/parameterised.py`, 27, 36,
  "    def __init__(",
  "The constructor takes the carriers as keyword parameters, defaulting to the real calls.",
  `A constructor that takes the carriers as parameters gives the test a seam it can use without a patch, and existing callers don't have to change if each parameter defaults to the real call (test_a_parameterised_engine_keeps_the_real_carriers_as_defaults). This is the engine with carrier parameters. AircoPrice is a callback Protocol because the AIRCO SDK takes keyword-only arguments, and mypy now checks the fake (test_mypy_checks_a_fake_passed_as_a_constructor_argument). The defaults have a cost: a test that passes a FASTLINE fake and forgets AIRCO reaches the real SDK and fails with an error saying AIRCO did not answer. Credits: the typing documentation on annotating callable objects. What to show: the three defaults. Fallback: the caption.`);

codeSlide("BREAKING DEPENDENCIES", "The engine as a function",
  `${E34}/src/dependency_breaking/rating.py`, 21, 34,
  "def quote(",
  "The quoters have no default, so leaving them out is an error for mypy and a TypeError at run time.",
  `This is the quote that takes quoters. The engine with carrier parameters kept defaults so existing callers still worked, and the cost was the forgotten fake. The function form drops them (test_the_function_form_needs_its_quoters, test_mypy_reports_a_missing_quoters_argument). quote_standard is the one binding the root needs, and a test checks that it wraps quote with the standard quoters (test_quote_standard_binds_the_standard_quoters). The truncation stays, because a step doesn't fix behaviour, and the grams-truncated row still passes through airco_quote (test_airco_quote_converts_kilograms_and_cents). Credits: the functools documentation, for partial. What to show: the signature, with no defaults on quoters. Fallback: the caption.`);

bulletSlide("BREAKING DEPENDENCIES", "A misspelt override", [
  ["The seam", " in subclass and override is a method name."],
  ["Without @override,", " nothing checks the name before the quote runs: a misspelt override falls through to the real carrier."],
  ["@override from typing", " closes the gap: mypy reports the name that has no base method."],
  ["The parameter forms", " are the Python ones, and subclass and override stays as the comparison."],
], `In subclass and override the seam is a method name, and without @override nothing checks the name before the quote runs. A misspelt override doesn't replace the method, so the engine reaches the real carrier (test_a_misspelt_override_falls_through_to_the_real_carrier). @override from typing closes the gap (test_mypy_reports_a_misspelt_override_only_with_the_override_decorator). With the override renamed, five tests fail and 37 pass, and mypy exits 1 with one misc error that says the method is marked as an override but has no base method. The parameter forms are the Python ones, and this form stays as the comparison. Credits: Feathers, in Working Effectively with Legacy Code, under "Dependency Breaking Techniques", where the techniques are set out in full. What to show: the renamed method and mypy's one error. Fallback: the bullets.`);

// ===========================================================================
// Section: Refactor or rewrite
// ===========================================================================
divider("05", "Refactor or rewrite", "Intent, golden values and parity",
  `Refactoring changes structure and keeps behaviour, and the tests that decide whether it did are of two kinds. Intent rows come from the requirement and ask whether an answer is right. Golden quotes record what the code did and ask whether anything changed. A rewrite is a third case: it's held to parity with the old engine, with a short list of accepted differences, and it is switched in zone by zone behind a router. What to show: the section name. Fallback: the subtitle names the three tools.`);

bulletSlide("REFACTOR OR REWRITE", "Intent rows and golden quotes", [
  ["Five intent rows", " written from the requirement pass a refactor that still changes 18 of 120 recorded quotes."],
  ["The rows pass", " because the carrier prices in them are whole cents and no margined price sits on a half cent."],
  ["A golden quote", " asks whether anything changed."],
  ["Characterise first,", " then refactor in named steps."],
], `One way of making carrier prices Money passes all five intent rows and still changes 18 of 120 recorded quotes (test_the_intent_rows_pass_every_engine_and_both_rounding_refactors, test_the_golden_quotes_catch_a_refactor_that_changes_rounding). The rows pass the refactors that move totals because the carrier prices in them are already whole cents, so the two roundings agree. The golden file asks "did this change" (test_the_golden_file_records_the_legacy_engine). With each carrier price rounded half up before Money, two golden tests fail and 28 pass, the intent cases pass, and mypy exits 0. Credits: Martin Fowler's Definition Of Refactoring and Self Testing Code, refactoring.com, Fowler's Refactoring, and Feathers's "Changing Software" in Working Effectively with Legacy Code. What to show: the 18 of 120 count. Fallback: the bullets.`);

codeSlide("REFACTOR OR REWRITE", "A golden comparison",
  `${E35}/tests/test_golden.py`, 66, 79,
  "def _mismatches(observed: list[tuple[str, str]], golden: Mapping[str, str]) -> list[str]:",
  "The comparison returns a list of lines in grid order, so a failure reads the same from run to run.",
  `A golden value pins whatever the code did, including behaviour you would call wrong. The comparison returns a list of lines in grid order, so a failure reads the same from run to run and the first changed row sits at the top. These mismatches are golden mismatch lines, each holding the row, the golden quote and the quote now. A refactor that rounds before the margin gives a first line of EU-11: golden FASTLINE 14.84, now FASTLINE 14.85 (test_the_golden_quotes_catch_a_refactor_that_changes_rounding, test_the_refactored_engine_matches_the_golden_quotes). Regenerate the golden file in a commit of its own. round(x, 2) on a Decimal rounds half to even in the default context (test_round_with_two_digits_rounds_half_to_even_in_the_default_context): with it in place of the half-up rule, three golden tests fail and 27 pass, and mypy exits 0. Credits: the decimal documentation. What to show: the first mismatch line. Fallback: the caption.`);

codeSlide("REFACTOR OR REWRITE", "The rewrite's quote",
  `${E36}/src/refactor_or_rewrite/rating.py`, 30, 42,
  "def quote(consignment: Consignment, /, *, tariff: Tariff = STANDARD_TARIFF) -> RateQuote:",
  "bisect_left keeps each band limit inclusive, so a weight equal to a limit stays in its band.",
  `This is the quote that takes a tariff, and it finds the band by bisection. A first draft of a rewrite can pass its own tests and still quote a 5 kg consignment from the next band's price, because the difference between bisect_left and bisect_right moves each band limit from one band to the other (test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries). Both engines put a weight equal to a limit in the lower band (test_band_limits_include_the_boundary_weight). With bisect_right in its place, four tests fail and 15 pass, and mypy exits 0. Martin Fowler's Strangler Fig page names the trap: "Replacements seem easy to specify, but often it's hard to figure out the details of existing behavior." Credits: Fowler's Strangler Fig, and the bisect documentation. What to show: the bisect_left line and its comment. Fallback: the caption.`);

bulletSlide("REFACTOR OR REWRITE", "Parity and accepted differences", [
  ["The rewrite", " differs from the legacy engine only where an accepted list says it may."],
  ["The list", " records a decision, so a reviewer who sees it grow can ask who made that decision."],
  ["An unknown zone", " is priced as EU by the legacy engine and refused by the rewrite."],
  ["Rows on each limit,", " and just above 5 and 50 kg, make the boundaries visible."],
], `The legacy engine prices an unknown zone as EU (test_the_legacy_engine_prices_an_unknown_zone_as_eu), and the rewrite refuses it (test_the_rewrite_refuses_an_unknown_zone). The parity test runs both engines over one table of rows. It fails on a new difference and on a stale entry, so the rewrite differs only where the accepted list says (test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted). The list records a decision, so a reviewer who sees it grow can ask who made that decision. With an empty accepted list, one test fails and 18 pass, and mypy exits 0. These mismatches are parity row ids, not golden lines. Credits: Cartwright, Horn and Lewis, in Patterns of Legacy Displacement, for Feature Parity. Rows on each band limit, and just above 5 kg and 50 kg, make the boundaries visible. What to show: the accepted list and the unknown-zone row. Fallback: the bullets.`);

codeSlide("REFACTOR OR REWRITE", "A router with a shadow",
  `${E36}/src/refactor_or_rewrite/strangler.py`, 35, 46,
  "    legacy: RateQuoter",
  "A migrated zone is served by the rewrite; otherwise the legacy quote is served and, in shadow mode, compared.",
  `The router serves migrated zones from the rewrite and the rest from the legacy engine (test_the_router_serves_migrated_zones_from_the_rewrite). In shadow mode a difference becomes a Mismatch holding both amounts, and the caller still gets the legacy quote (test_shadow_mode_reports_a_mismatch_and_serves_the_legacy_quote). With every zone migrated, a legacy quoter that raises isn't reached, so the router and the legacy module can be deleted together (test_with_every_zone_migrated_the_legacy_engine_is_never_called). mypy holds the rewrite to the legacy call shape (test_mypy_requires_the_rewrite_to_take_a_consignment). Credits: Cartwright, Horn and Lewis for Transitional Architecture, and Martin Fowler's Dark Launching entry, which describes calling new behaviour without users seeing it. What to show: the shadow branch. Fallback: the caption.`);

// ===========================================================================
// Section: The final project
// ===========================================================================
divider("06", "The final project", "One booking, undone on a refusal",
  `The final project pulls a booking through rating, a slot, a carrier, customs clearance and tracking, behind one desk. It starts from an acceptance test that names the stage that's missing. A refusal undoes the completed steps newest first, and effects other parts can see are published only after the commit. One function chooses the carrier, the pricing rule and the subscriber. What to show: the section name. Fallback: the subtitle names the behaviour.`);

codeSlide("THE FINAL PROJECT", "An acceptance test first",
  `${E39}/tests/test_acceptance.py`, 35, 49,
  "    failures: list[str] = []",
  "The helper collects what is missing instead of stopping at the first miss, so a failing run names the stage.",
  `An acceptance test says when the slice is whole, and it comes first: it fixes one request and the shipment that request has to produce, and the parts are built until it passes. Because the helper returns a list in a fixed order, a failing run says which stage is absent, not only that something is (test_a_booking_request_ships_end_to_end). Four stage removals each replace one stage with a stand-in that does nothing useful, and the helper's list changes with each (test_the_acceptance_test_fails_when_a_stage_is_left_out). When the acceptance test goes red it says which stage; the part's own test says why. Credits: Harry Percival and Bob Gregory, in Architecture Patterns with Python, under "TDD in High Gear and Low Gear". What to show: the helper's failures list. Fallback: the caption.`);

codeSlide("THE FINAL PROJECT", "A stack of inverses",
  `${E39}/src/final_project/desk.py`, 43, 52,
  "    def ship(self, request: BookingRequest, /) -> Shipment:",
  "The slot and the booking register their inverses as they succeed; a refusal runs them newest first, and pop_all() is the commit.",
  `A step that succeeded has to be taken back when a step that runs afterwards refuses. The desk gets the means from an ExitStack: each step registers the function that reverses it as soon as it succeeds, and a refusal runs them newest first (test_the_undo_runs_in_reverse_order_of_the_steps). The slot was reserved first and the carrier booked second, so the carrier is cancelled first (test_a_held_declaration_releases_the_slot_and_cancels_the_carrier_booking, test_a_full_sailing_books_nothing_with_the_carrier). In ship, pop_all() is the commit. With that line deleted, five tests fail and 18 pass, because the booking is made and then undone; mypy exits 0, because removing the call is type-correct. This isn't a design for a restart, or for a step that can't be undone. Credits: the contextlib documentation, and Percival and Gregory's Unit of Work in Architecture Patterns with Python for the persistent form. What to show: the callback lines. Fallback: the caption.`);

codeSlide("THE FINAL PROJECT", "Events after the commit",
  `${E39}/src/final_project/desk.py`, 53, 60,
  "        invoice = Invoice(",
  "The booked event is published after the with block, so a held booking leaves no event behind.",
  `An event can't be taken back, so the rule is that effects other parts can see go after pop_all(). The listing is the end of ship: the invoice is built and the booked event published only once the with block has closed. A held booking publishes no tracking event (test_a_held_booking_publishes_no_tracking_event), and an eager publisher reports a booking that was rolled back (test_an_eager_publisher_reports_a_booking_that_was_rolled_back). With the publish moved into the with block, one test fails and 22 pass, and mypy exits 0 again, because publish order isn't a type. Billing makes a related refusal: an invoice in two currencies has no total (test_an_invoice_in_two_currencies_has_no_total). Credits: the contextlib documentation. What to show: the publish after the with block. Fallback: the caption.`);

codeSlide("THE FINAL PROJECT", "One composition root",
  `${E39}/src/final_project/app.py`, 11, 21,
  "def build_desk(",
  "One function chooses the carrier, the pricing rule and the subscriber, then hands the desk its parts.",
  `One function chooses the pricing rule as well as the carrier and the subscriber, and the desk takes its parts as keyword parameters, so it never decides which carrier or which pricing rule it has (test_the_pricing_rule_is_chosen_at_the_composition_root). The gateway has book and cancel, and mypy refuses one without cancel with an arg-type error that names the CarrierGateway Protocol (test_mypy_refuses_a_gateway_without_cancel). A structure test parses each module with ast and finds that only app.py names a concrete carrier (test_only_the_composition_root_names_a_concrete_carrier). This gateway is the one with book and cancel, which tells it from the quote-and-book gateway used with the engines. Credits: Percival and Gregory, in Architecture Patterns with Python, under "Dependency Injection (and Bootstrapping)". What to show: the three choices in the body. Fallback: the caption.`);

// ===========================================================================
// Section: Working with AI tools
// ===========================================================================
divider("07", "Working with AI tools", "A reply trusted as far as its gates",
  `A reply from an assistant reaches a repository the way any other change does, and the stance is the same: trust it as far as the checks it has passed. Three hand-written drafts stand in for replies, and three gates check them: a static gate, a shape review and a behaviour oracle. The gates answer different questions, so a draft one gate accepts another can stop. A recorded fake puts the assistant behind a seam. What to show: the section name. Fallback: the subtitle states the stance.`);

tableSlide("WORKING WITH AI TOOLS", "Three drafts, three gates",
  ["Draft", "Static gate", "Shape review", "Behaviour oracle"], [
    ["untyped_factory", "fails", "fails", "fails"],
    ["typed_hierarchy", "passes", "fails", "passes"],
    ["rounded_callable", "passes", "passes", "fails"],
    ["the idiomatic module", "passes", "passes", "passes"],
  ], [3.9, 2.6, 2.8, 2.79],
  `The three drafts were written by hand as stand-ins for replies, so the results describe these drafts and make no claim about what any assistant writes. Each gate alone accepts at least one draft that another gate stops: the static gate accepts the second and third, the shape review accepts the third, and the oracle accepts the second. Of these four modules, only the idiomatic one passes all three (test_each_draft_fails_exactly_the_gates_in_the_table, test_the_idiomatic_module_passes_every_gate). The drafts' shapes are the class-per-strategy shape, a factory class with only static methods, a getter and a setter, and a factory that stores its instance, which the four shape rules look for. Credits: OWASP's LLM05:2025 entry, Improper Output Handling: "Treat the model as any other user, adopting a zero-trust approach, and apply proper input validation on responses coming from the model to backend functions." What to show: the third row. Fallback: the table.`, { rowH: 0.8, fontSize: 15, y: 1.7 });

figSlide("WORKING WITH AI TOOLS", "Gates in parallel", "40-working-with-ai-and-llm-tools",
  "A draft goes to three gates in parallel; a gate that reports a draft names it, and a rejected reply's findings go back in the next prompt.",
  `The gates answer different questions, and no code orders them. The figure shows a draft's text going to the static gate, the shape review and the behaviour oracle, and the three outcome arrows reaching "accepted" only when no gate reports the draft (test_each_draft_fails_exactly_the_gates_in_the_table, test_the_idiomatic_module_passes_every_gate). The typed hierarchy passes mypy and ruff (test_mypy_and_ruff_pass_the_typed_hierarchy). The static gate reports the untyped draft by rule and line: no-untyped-def and no-untyped-call from mypy, UP037 and UP045 from ruff (test_the_static_gate_reports_the_untyped_draft). The oracle lists the three half-cent rows (test_the_oracle_lists_the_half_cent_rows). With round() in place of quantize in the idiomatic module, one test fails and 25 pass, and mypy exits 0. The amber arrow is the loop that sends every gate's findings back. Credits: the mypy command-line page and the Ruff rules, UP045. What to show: the three boxes and the amber arrow. Fallback: the caption.`);

codeSlide("WORKING WITH AI TOOLS", "A seam for the model",
  `${E40}/src/review_gate/assistant.py`, 42, 56,
  "def propose(",
  "propose asks, gates the reply and, if it is rejected, asks again with the findings appended.",
  `Code that asks an assistant for a reply has a dependency like any other: a dependency on a model client goes behind a Protocol with a recorded fake. The loop asks, gates the reply and, if it is rejected, asks again with the findings appended (test_a_rejected_reply_is_sent_back_with_its_findings). It stops at the first accepted reply and gives up once its attempts run out (test_the_loop_stops_at_the_first_accepted_reply, test_the_loop_gives_up_after_its_attempts). An unrecorded prompt raises LookupError, so a test can't pass on a prompt nobody recorded (test_an_unrecorded_prompt_is_refused). The package imports no network module (test_the_package_imports_no_network_module), and mypy refuses an assistant without a reply method (test_mypy_refuses_an_assistant_without_reply). The tests run mypy in-process and ruff as a local process. With one shape rule removed, four tests fail and 22 pass, and mypy exits 0. What to show: the retry line. Fallback: the caption.`);

bulletSlide("WORKING WITH AI TOOLS", "Limits of the gates", [
  ["The gates", " verify what they list, and a draft that passes all three has been checked on those rows and in those shapes."],
  ["A diff that edits the expected rows", " moves the answer the oracle holds every draft to."],
  ["A prompt", " can name the gates before any reply exists, so the reply is measured against them."],
  ["The review line", " asks who decided the answer should change."],
], `The gates verify what they list. The oracle's grid is ten rows, so it says nothing about a weight it doesn't list, and the shape review looks for four shapes; a draft that passes all three has been checked on those rows and in those shapes (test_the_oracle_lists_the_half_cent_rows, test_mypy_and_ruff_pass_the_typed_hierarchy). A diff that edits EXPECTED_ROWS moves the answer the oracle holds every draft to. A prompt that lists the gates says what the reply will be measured against, and the review line for such a diff asks who decided the answer should change. OWASP's LLM09:2025 entry, Misinformation, names the failure: "Overreliance occurs when users place excessive trust in LLM-generated content, failing to verify its accuracy." The oracle verifies accuracy at the rows it lists. What to show: the expected rows. Fallback: the bullets.`);

// ===========================================================================
// Section: Reference
// ===========================================================================
divider("08", "Reference", "Sources, books and where the code lives",
  `The code rests on the pytest and Python documentation, a few articles on refactoring and legacy displacement, the xUnit pattern pages and two OWASP entries. Short quotations are attributed. Two tables list the sources and the books, and the site and the repository that hold the examples are given too. What to show: the section name. Fallback: the subtitle names the three parts.`);

tableSlide("REFERENCE", "Sources credited",
  ["Source", "Used for"], [
    ["pytest documentation", "Fixture teardown, monkeypatch scoping, strict options, one configuration file and import modes"],
    ["pytest-mock documentation: usage", "stub, spy and resetall"],
    ["Python documentation: unittest.mock", "assert_has_calls, spec_set, autospeccing and where to patch"],
    ["typeshed: unittest/mock.pyi", "Why mypy accepts a mock where a Protocol is expected"],
    ["Python documentation: importlib, typing, functools, decimal, bisect, contextlib", "reload, callback Protocols, partial, half-even rounding, bisection and ExitStack"],
    ["Martin Fowler, bliki and articles", "Mocks Aren't Stubs, Definition Of Refactoring, Self Testing Code, Strangler Fig and Dark Launching"],
    ["refactoring.com", "The catalogue of small behaviour-preserving steps"],
    ["Cartwright, Horn and Lewis", "Patterns of Legacy Displacement: Feature Parity and Transitional Architecture"],
    ["Gerard Meszaros, xunitpatterns.com", "Test Stub, Test Spy and Dummy Object"],
    ["OWASP; mypy; Ruff", "Two LLM Top 10 entries; the command line and the UP045 rule"],
  ], [5.9, 6.19],
  `The table pairs sources with their use. The pytest documentation covers fixture teardown, monkeypatch scoping, the strict options, one configuration file and import modes. pytest-mock's usage page covers stub, spy and resetall. The Python library documentation covers unittest.mock with its autospeccing and where-to-patch sections, importlib.reload, typing's callable objects, functools.partial, decimal, bisect and contextlib. typeshed's mock stub explains why mypy accepts a mock. Martin Fowler's pieces and refactoring.com cover the vocabulary of doubles, refactoring and the strangler fig. Ian Cartwright, Rob Horn and James Lewis wrote Patterns of Legacy Displacement. Gerard Meszaros's pattern pages define the doubles, OWASP's LLM05:2025 and LLM09:2025 entries supply the two quotations, and the mypy and Ruff pages describe the gates. What to show: nothing; the table is the record. Fallback: the rows pair source and use.`, { rowH: 0.40, fontSize: 12, y: 1.55 });

tableSlide("REFERENCE", "Reading further",
  ["Book", "Authors", "Year"], [
    ["Working Effectively with Legacy Code", "Michael Feathers", "2004"],
    ["Refactoring: Improving the Design of Existing Code, second edition", "Martin Fowler", "2018"],
    ["xUnit Test Patterns: Refactoring Test Code", "Gerard Meszaros", "2007"],
    ["Python Testing with pytest, second edition", "Brian Okken", "2022"],
    ["Architecture Patterns with Python", "Harry Percival and Bob Gregory", "2020"],
    ["Effective Python, third edition", "Brett Slatkin", "2024"],
  ], [7.0, 3.9, 1.19],
  `Six books are credited. Michael Feathers's Working Effectively with Legacy Code is the source of the seam, the characterisation test and the dependency-breaking catalogue. Martin Fowler's Refactoring gives the catalogue of behaviour-preserving steps. Gerard Meszaros's xUnit Test Patterns is the vocabulary behind the doubles. Brian Okken's Python Testing with pytest is a full-length treatment of fixtures, markers and configuration. Harry Percival and Bob Gregory's Architecture Patterns with Python covers tests at different levels, the bootstrap script and the Unit of Work. Brett Slatkin's Effective Python is on the list as further reading. What to show: nothing; the list is the reference. Fallback: titles, authors and years are enough to find them.`, { rowH: 0.62, fontSize: 14, y: 1.7 });

bulletSlide("REFERENCE", "Site and repository", [
  ["The site", " is at https://patterncatalyst.github.io/design-patterns-with-python/"],
  ["The repository", " holds the examples: https://github.com/patterncatalyst/design-patterns-with-python"],
  ["To set up,", " run uv sync --locked --all-packages once at the root."],
  ["In an example directory,", " run uv run pytest, then uv run mypy --strict src tests."],
  ["Two further decks", " cover themes: patterns and SOLID in Python, and idiomatic Python."],
], `The site holds the prose and the figures. The repository holds the examples that the listings were read from, with their tests, so a claim can be re-run. An example runs on its own: sync the workspace once from the root, then run pytest and mypy in strict mode from the example's directory, since both find the root configuration. The pinned versions are CPython 3.15.2, uv 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, ruff 0.17.4 and mypy 2.4.1. The two further decks cover, by theme, patterns and SOLID in Python, and idiomatic Python: what the language gives you so that you don't write the pattern. What to show: the site's home page and the repository's examples directory. Fallback: the two addresses are enough to find both.`, { fontSize: 17 });

// ===========================================================================
// Checks and write
// ===========================================================================
finish(OUT);
