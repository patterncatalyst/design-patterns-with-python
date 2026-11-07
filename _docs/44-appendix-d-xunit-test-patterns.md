---
title: "xUnit test patterns (Meszaros)"
order: 44
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "D"
description: "Gerard Meszaros's xUnit test patterns for fixtures, test doubles, verification and dependency injection, mapped onto tests the book already contains, with the two places where pytest-mock's names mean something else."
---

## Learning objectives

By the end of this appendix you can:

- Name the four phases of a test and find them in a pytest test.
- Give the Meszaros name for a fixture's lifetime, setup and teardown.
- Name the double a test uses, including when pytest-mock's name says otherwise.
- Say whether a test verifies state or behaviour, and what a helper does for the test that calls it.
- Recognise dependency injection in a test's constructor call.

## Why this matters

A name for what a test is doing lets a reviewer say it in a word. "This fixture is shared" and "this double records" are claims about how long a test's world lives and how tightly the test is coupled to its collaborators. Gerard Meszaros gives such claims names in *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007). The book's tests already follow many of those patterns under pytest's vocabulary, and the sections below say which test shows which pattern.

The pattern pages quoted here live on Meszaros's site, [xunitpatterns.com](http://xunitpatterns.com/). Each of the pages linked here carries a note that the book has since been published and that the chapter's content has likely changed, so the site is the pre-publication text and the printed book is the reference. The quotations are the one-sentence summary at the head of a page, and the page is linked by its address in the first column of a table. The reasons given for each row are this book's own reading of its own tests.

A test is named for a pattern when it meets the page's definition, and a row that meets it only in part says so. The site's catalogue is larger than this one. The chapter titled [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) holds the refusals a double makes, and [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}) holds the mock API. Neither is repeated here.

## Four-phase test

A test with four visible parts can be read in one pass: put the world in order, do the one thing under test, check the result, and clean up. [Four-Phase Test](http://xunitpatterns.com/Four%20Phase%20Test.html) says "Structure each test with four distinct parts executed in sequence". Here is the pattern in a test of the rate engine:

<!-- fmt:off -->
```python
def test_quote_validity_comes_from_the_injected_clock(
    consignment: Consignment, fixed_now: datetime, make_fake: FakeFactory, quote_log: Path
) -> None:
    engine = _engine({"fastline": make_fake("fastline", _usd("10.00"))}, fixed_now, minutes=45)

    quote = engine.best_quote(consignment)

    assert_type(quote.total, Money)
    assert quote.total == _usd("10.00")
    assert quote.consignment_id == consignment.id
    assert quote.valid_until == fixed_now + timedelta(minutes=45)
    with quote_log.open("a", encoding="utf-8") as handle:
        handle.write(f"valid_until={quote.valid_until.isoformat()}\n")
```
<!-- fmt:on -->

The fixtures `consignment`, `fixed_now`, `make_fake` and `quote_log`, with the `_engine(...)` call, are the setup. `engine.best_quote(consignment)` is the exercise, the `assert` lines verify, and the code after the `yield` in `quote_log` is the teardown, which the test never calls. The chapter titled "Proving it works: pytest, pytest-mock, and mypy" makes a test fail and shows the teardown line written before pytest prints the failure report.

## Fixtures: lifetime, setup and teardown

A fixture pattern answers two questions: how long the test's world lives, and who builds it. The first column links the page; the last says what pytest calls the same thing.

| Pattern | The page's summary | Test | In pytest |
| --- | --- | --- | --- |
| [Fresh Fixture](http://xunitpatterns.com/Fresh%20Fixture.html) | "Each test constructs its own brand-new test fixture for its own private use." | `test_tmp_path_is_a_fresh_directory_per_test`, `test_a_factory_fixture_builds_a_fresh_object_per_call` | a fixture at function scope |
| [Shared Fixture](http://xunitpatterns.com/Shared%20Fixture.html) | "We reuse the same instance of the test fixture across many tests." | `test_a_module_scoped_fixture_is_set_up_once_for_the_module` | `scope="module"` or wider |
| [Standard Fixture](http://xunitpatterns.com/Standard%20Fixture.html) | "The same design of test fixture is used in several tests." | `test_book_best_books_only_the_winner`, `test_side_effect_drives_the_timeout_branch` | conftest fixtures that several tests take |
| [Implicit Setup](http://xunitpatterns.com/Implicit%20Setup.html) | "Build the test fixture common to several tests in the setUp method." | `test_an_autouse_fixture_runs_without_being_named` | `autouse=True` |
| [Inline Setup](http://xunitpatterns.com/Inline%20Setup.html) | "Each Test Method creates" its own Fresh Fixture by calling constructors in the test | `test_an_unrecorded_prompt_is_refused` | constructor calls in the test body |
| [Delegated Setup](http://xunitpatterns.com/Delegated%20Setup.html) | "Each test creates its own Fresh Fixture by calling Creation Methods from within the Test Methods." | `test_a_quote_rounds_half_up_to_the_cent`, `test_a_clean_batch_returns_its_quotes_in_order` | a call to a factory in the test body |
| [Creation Method](http://xunitpatterns.com/Creation%20Method.html) | "Set up the test fixture by calling methods that hide the mechanics of building ready-to-use objects behind Intent Revealing Names." | `test_a_factory_fixture_builds_a_fresh_object_per_call` | a factory fixture |
| [Implicit Teardown](http://xunitpatterns.com/Implicit%20Teardown.html) | "The Test Automation Framework calls our clean up logic in the tearDown method after every Test Method." | `test_yield_fixtures_tear_down_in_reverse_order_of_setup`, `test_quote_validity_comes_from_the_injected_clock` | code after `yield` |
| [Automated Teardown](http://xunitpatterns.com/Automated%20Teardown.html) | "We keep track of all resources that are created in a test and automatically destroy/free them during teardown." | `test_validity_reads_the_environment_and_the_context_restores_it`, `test_monkeypatch_undoes_its_changes_when_the_context_ends` | `monkeypatch` |

Function scope gives a fresh object per test. `test_a_module_scoped_fixture_is_set_up_once_for_the_module` runs a generated module in which a module-scoped `shared` fixture is set up once for two tests and a function-scoped `fresh` fixture is set up twice, so the scope is the thing the test asserts. How pytest orders the teardown of fixtures at different scopes is in [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}).

A Standard Fixture is the weakest row. The two named tests take the conftest's `consignment` and `fixed_now`, and so does `test_quote_validity_comes_from_the_injected_clock`, so the fixture design is the same across them.

The three setup patterns differ in who calls the builder. An `autouse` fixture is Implicit Setup because the framework runs it before the test without the test naming it; a fixture named in the signature is explicit, so it isn't. In `test_an_unrecorded_prompt_is_refused` the test builds `RecordedAssistant({_PROMPT: ["reply"]})` itself, which is Inline Setup. Delegated Setup hands that work to a Creation Method, and the book's Creation Method is a factory fixture, with parameters:

<!-- fmt:off -->
```python
@pytest.fixture
def make_consignment() -> MakeConsignment:
    """A factory fixture: the test decides how many consignments to build, and with what."""

    def make(
        consignment_id: str = "CN-1", /, *, zone: str = "EU", kilograms: str = "10"
    ) -> Consignment:
        return Consignment(ConsignmentId(consignment_id), zone, Weight(Decimal(kilograms)))

    return make
```
<!-- fmt:on -->

The factory hides `Consignment(ConsignmentId(...), zone, Weight(Decimal(...)))` behind defaults and the keyword `kilograms=`, so `make_consignment(kilograms="3.3")` in a test says what matters about the consignment and nothing else.

Teardown has two rows. Code after a `yield` is Implicit Teardown: the framework runs it, and `test_yield_fixtures_tear_down_in_reverse_order_of_setup` asserts the order. The second test in that row relies on the teardown of `quote_log` without asserting it; the experiment in the chapter titled "Proving it works: pytest, pytest-mock, and mypy" is what shows that teardown running when a test fails.

Automated Teardown carries a qualification. Both tests use `with monkeypatch.context()`, which undoes its changes at the end of the `with` block, and the page says "during teardown". The first test records three changes (`setenv`, `delenv`, `setenv`) and asserts the environment is back as it was; the second records two `setattr` changes and asserts the originals are back. No test in the book asserts the restore of `monkeypatch` used as a plain fixture, so the row rests on the context form.

## Test doubles

A test double replaces a collaborator so that the test controls what the code under test receives or sees what it sends. The kind of double decides which of those the test can claim. [Test Double](http://xunitpatterns.com/Test%20Double.html) is the umbrella: "We replace a component on which the SUT depends" with a test-specific equivalent, where the SUT is the system under test. The rows below are its kinds.

| Pattern | The page's summary | The book's double | Test |
| --- | --- | --- | --- |
| [Dummy Object](http://xunitpatterns.com/Dummy%20Object.html) | "We pass an object that has no implementation as an argument of a method called on the SUT." | `notify=mocker.stub()`, passed and never read | `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` |
| [Test Stub](http://xunitpatterns.com/Test%20Stub.html) | "We replace a real object with a test-specific object that feeds the desired indirect inputs into the system under test." | `slow.quote.side_effect = CarrierTimeoutError(...)` on an autospec | `test_side_effect_drives_the_timeout_branch`, `test_a_carrier_that_times_out_is_skipped` |
| [Test Spy](http://xunitpatterns.com/Test%20Spy.html) | "Use a Test Double to capture the indirect output calls made to another component by the system under test (SUT) for later verification by the test." | `FakeGateway.booked`; `RecordedAssistant.prompts`; a `mocker.stub()` callback; an autospec asserted afterwards | `test_book_best_books_the_winner_and_returns_its_reference`, `test_a_rejected_reply_is_sent_back_with_its_findings`, `test_stub_records_a_callback`, `test_book_best_books_only_the_winner` |
| [Configurable Test Double](http://xunitpatterns.com/Configurable%20Test%20Double.html) | "Configure a reusable Test Double with the values to be returned or verified during the fixture setup phase of a test." | `FakeGateway` built by `make_fake("fastline", ...)`; an autospec with `return_value` set | `test_best_quote_picks_the_cheapest_carrier`, `test_book_best_books_only_the_winner` |
| [Hard-Coded Test Double](http://xunitpatterns.com/Hard-Coded%20Test%20Double.html) | "Build the Test Double by hard-coding the return values and/or expected calls." | `airco_fake`, a closure that always returns `2800`; `_InertGateway`, `_zero_rule`, `_zero_duty` | `test_airco_quote_converts_kilograms_and_cents`, `test_the_acceptance_test_fails_when_a_stage_is_left_out` |
| [Test-Specific Subclass](http://xunitpatterns.com/Test-Specific%20Subclass.html) | "Add methods that expose the state or behavior needed by the test to a subclass of the SUT." | `_FakeCarrierRateEngine`; `Misspelt` | `test_every_step_matches_the_characterisation_table`, `test_a_misspelt_override_falls_through_to_the_real_carrier` |
| [Mock Object](http://xunitpatterns.com/Mock%20Object.html) | "Replace an object the system under test (SUT) depends on with a test-specific object that verifies it is being used correctly by the SUT." | none: the contrast | none |

The difference between a Configurable and a Hard-Coded Test Double is where the answer is written. `make_fake("fastline", _usd(fastline))` passes the carrier name and amount in at setup, in three parametrised cases of `test_best_quote_picks_the_cheapest_carrier`. `airco_fake` has `2800` inside its body, and `_InertGateway` returns the constant `"FL-0"` and books nothing.

`FakeGateway` carries the word fake in its name. In Meszaros's terms it is a Configurable Test Double used as a stub and a spy: it's built with its `amount` and `times_out`, which feed the engine's inputs, and it appends to `booked`, which records an output. The [Fake Object](http://xunitpatterns.com/Fake%20Object.html) page says a fake differs from a Test Stub in that a stub is "a control point to inject indirect inputs into the SUT" and a fake isn't one. A double configured with its answers is that control point, so the class keeps its name `FakeGateway` and isn't given a Fake Object row.

Mock Object is the contrast: none of the book's mocks is one. The page defines a double that checks, as the code under test calls it, that it is being used correctly. In `test_book_best_books_only_the_winner` the mocks are asserted after the exercise step:

<!-- fmt:off -->
```python
def test_book_best_books_only_the_winner(
    mocker: MockerFixture, consignment: Consignment, fixed_now: datetime
) -> None:
    winner = mocker.create_autospec(CarrierGateway, instance=True)
    loser = mocker.create_autospec(CarrierGateway, instance=True)
    winner.quote.return_value = CarrierQuote("airco", _usd("10.00"))
    loser.quote.return_value = CarrierQuote("fastline", _usd("12.00"))
    winner.book.return_value = "AIRCO:CN-00000001"
    engine = RateEngine(
        {"airco": winner, "fastline": loser}, clock=lambda: fixed_now, validity=timedelta(hours=1)
    )

    assert engine.book_best(consignment) == "AIRCO:CN-00000001"

    winner.book.assert_called_once_with(consignment)
    loser.book.assert_not_called()
```
<!-- fmt:on -->

`winner.book.assert_called_once_with(consignment)` runs after `engine.book_best(...)` has returned, which is the Test Spy's style. The [Test Spy](http://xunitpatterns.com/Test%20Spy.html) page contrasts the two: "Because a Test Spy does not fail the test at the first deviation from the expected behavior like a Mock Object". No `Mock` in the book is given expectations before the exercise and left to fail the test, so the row stays a contrast. The chapter titled "Proving it works: pytest, pytest-mock, and mypy" says that a mock, in Meszaros's sense, is an object that checks the calls it receives. The `Mock` class in this test is used in the spy style instead.

A Test-Specific Subclass lives in the tests and changes nothing in `src`. `_FakeCarrierRateEngine` overrides the engine's `_fastline_quote` and `_airco_price` to reach fakes, and `Misspelt`, written inside one test, shows what a misspelt override does. The page lists exposing state and modifying behaviour under one name, and the book's subclasses modify behaviour. The chapter titled [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) builds the engine forms that these subclasses extend.

## Two vocabularies

Two names in the mock libraries collide with Meszaros's. pytest-mock's [usage page](https://pytest-mock.readthedocs.io/en/stable/usage.html) says "The stub is a mock object that accepts any arguments and is useful to test callbacks." That is a callback recorder. Meszaros's Test Stub is a double that feeds indirect inputs to the code under test. Neither of the book's `mocker.stub()` tests cited here uses it that way: `test_stub_records_a_callback` asserts the calls the stub received, which makes it a Test Spy by role, and `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first` passes one that is never read, which makes it a Dummy Object. The Test Stub rows in the table are the autospecs with `side_effect` set.

`mocker.spy` is the second collision. In `test_spy_keeps_the_real_behaviour_and_records_returns` the test calls `fastline.quote(...)` on the wrapped real object itself and then reads `spy_return`. It records a call the test made, where a Test Spy records an indirect output of a system under test, so it isn't a Test Spy in the page's sense.

When a test says "stub" or "spy", ask which vocabulary it is in. The sentence in "Mocking reference: unittest.mock and pytest-mock" that defines a stub says "in pytest-mock's sense" for this reason, and the role of a double is the one its test gives it.

## Verifying results

Verification patterns say what a test looks at once the exercise has run.

| Pattern | The page's summary | Test | In the book |
| --- | --- | --- | --- |
| [State Verification](http://xunitpatterns.com/State%20Verification.html) | "We inspect the state of the system under test (SUT) after it has been exercised and compare it to the expected state." | `test_a_clean_batch_returns_its_quotes_in_order`, `test_best_quote_picks_the_cheapest_carrier` | asserts on the returned quotes |
| [Behavior Verification](http://xunitpatterns.com/Behavior%20Verification.html) | "We capture the indirect outputs of the SUT as they occur and compare them to the expected behavior." | `test_book_best_books_only_the_winner` | `assert_called_once_with`, `assert_not_called` |
| [Guard Assertion](http://xunitpatterns.com/Guard%20Assertion.html) | "Replace an if statement in a test with an assertion that fails the test if not satisfied." | `test_null_object_is_an_optional_checked_by_mypy` | `assert gateway is not None` |
| [Custom Assertion](http://xunitpatterns.com/Custom%20Assertion.html) | "Create a purpose-built Assertion Method that compares only those attributes of the object that define test-specific equality." | `test_a_booking_request_ships_end_to_end`, `test_the_acceptance_test_fails_when_a_stage_is_left_out` | `acceptance_failures`, qualified |
| [Test Utility Method](http://xunitpatterns.com/Test%20Utility%20Method.html) | "We encapsulate the test logic we want to reuse behind a suitably named utility method." | `test_the_refactored_engine_matches_the_golden_quotes` | `_observed` and `_mismatches` |
| [Parameterized Test](http://xunitpatterns.com/Parameterized%20Test.html) | "We pass the information needed to do fixture setup and result verification to a utility method that implements the entire test lifecycle." | `test_every_step_matches_the_characterisation_table` | `parametrize`, qualified |

State Verification and Behavior Verification are the choice between asking what came back and asking what was called. `test_a_clean_batch_returns_its_quotes_in_order` asserts on the returned quotes; the excerpt of `test_book_best_books_only_the_winner` above asserts on calls to the collaborators. Martin Fowler's [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html), which "Mocking reference: unittest.mock and pytest-mock" also cites, sets the two against each other. In `test_null_object_is_an_optional_checked_by_mypy` the `assert gateway is not None` stands where an `if gateway is not None:` would otherwise wrap the call, and it fails the test if the lookup returned `None`.

Custom Assertion is qualified. `acceptance_failures` takes what it needs as parameters, has no side effects and makes six checks, but it returns a list of failure strings and the test compares that list with `[]`. It doesn't fail the test itself, which the page's Assertion Method does.

<!-- fmt:off -->
```python
def acceptance_failures(
    shipment: Shipment, history: TrackingHistory, client: FastlineClient, plan: StowagePlan
) -> list[str]:
    """What is missing from the slice, in a fixed order; an empty list means it is whole."""
    failures: list[str] = []
    if shipment.quote.total != Money(Decimal("5.63")):
        failures.append(f"freight {shipment.quote.total.amount}")
    if shipment.declaration.duty != Money(Decimal("30.00")):
        failures.append(f"duty {shipment.declaration.duty.amount}")
    if shipment.invoice.total != Money(Decimal("35.63")):
        failures.append(f"invoice {shipment.invoice.total.amount}")
    if shipment.slot != SlotId(1, 1, 1) or list(plan.reservations) != [SlotId(1, 1, 1)]:
        failures.append("slot")
    if dict(client.open) != {1001: 12500}:
        failures.append(f"carrier {dict(client.open)}")
    booked = HandlingEvent(ConsignmentId("CN-1"), HandlingKind.BOOKED, "NLRTM")
    if history.events != (booked,):
        failures.append("tracking")
    return failures
```
<!-- fmt:on -->

`test_a_booking_request_ships_end_to_end` asserts the list equals `[]`, and `test_the_acceptance_test_fails_when_a_stage_is_left_out` asserts it equals the failures expected for the stage left out. The helper is a Custom Assertion in intent and a report builder in form.

A Test Utility Method holds logic that several tests reuse behind names that say what they do. `_observed` is called by four tests in `test_golden.py`, and `_mismatches` by three. Parameterized Test is also qualified. In `test_every_step_matches_the_characterisation_table`, `_observed(step, carrier_answers, row)`, a different helper with the same name, takes the row, builds the engine form and exercises it, but the comparison stays in the test body, and `pytest.mark.parametrize` generates the cases from the table of rows. The page's test calls a utility method that implements the whole lifecycle, including verification; pytest's way is to multiply a test over data.

## Dependency injection in tests

[Dependency Injection](http://xunitpatterns.com/Dependency%20Injection.html) gives a double its way in: "The client provides the depended-on object to the SUT". Three of the book's tests show it. `test_booking_service_runs_against_an_injected_fake` builds `BookingService(fake, records.append)`, so both dependencies arrive through the constructor. `test_a_parameterised_engine_keeps_the_real_carriers_as_defaults` passes one dependency by keyword, `parameterised.RateEngine(fastline_quote=fastline_fake)`, and leaves the other at its production default. In `test_two_threads_parked_between_read_and_write_take_the_same_slot`, `StowagePlan("SAILING-1", lock=nullcontext(), gap=barrier_gap)` injects a lock and a callable through the constructor; `gap` is a parameter, so it counts as injection. The design reasons are in [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}).

## For deeper coverage

Gerard Meszaros's *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007) is the reference for every pattern in this appendix, and it's on the [bibliography page]({{ '/bibliography/' | relative_url }}). The pattern pages linked in the tables are the pre-publication text on [xunitpatterns.com](http://xunitpatterns.com/), where the site's other patterns are also listed. Martin Fowler's [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) covers the choice between state and behaviour verification. For the pytest side, read "pytest reference" for fixtures and scopes and "Mocking reference: unittest.mock and pytest-mock" for the doubles' API.
