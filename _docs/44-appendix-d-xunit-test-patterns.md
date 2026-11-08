---
title: "xUnit test patterns (Meszaros)"
order: 44
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "D"
description: "Gerard Meszaros's xUnit test patterns for fixtures, test doubles, verification and dependency injection, mapped onto pytest and pytest-mock, with the two places where pytest-mock's names mean something else."
---

## Learning objectives

By the end of this appendix you can:

- Name the four phases of a test and find them in a pytest test.
- Give the Meszaros name for a fixture's lifetime, setup and teardown.
- Name the double a test uses, including when pytest-mock's name says otherwise.
- Say whether a test verifies state or behaviour, and what a helper does for the test that calls it.
- Recognise dependency injection in a test's constructor call.

## Why this matters

A name for what a test does lets a reviewer say it in a word. "This fixture is shared" and "this double records" are claims about how long a test's world lives and how tightly the test is coupled to its collaborators. Gerard Meszaros names them in *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007), and pytest has its own word for most of them.

The quotations are the one-sentence summaries from [xunitpatterns.com](http://xunitpatterns.com/), linked from the first column of each table. Each page notes that the printed book has since been published, so the site is the pre-publication text and the print edition is the reference. A row that meets a page's definition only in part says so. The refusals a double makes are in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}), and the mock API is in [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}).

## Four-phase test

[Four-Phase Test](http://xunitpatterns.com/Four%20Phase%20Test.html): "Structure each test with four distinct parts executed in sequence". Setup, exercise, verify, teardown:

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

| Phase | Where it is |
| --- | --- |
| Setup | the fixtures in the signature and the `_engine(...)` call |
| Exercise | `engine.best_quote(consignment)` |
| Verify | the `assert` lines |
| Teardown | the code after `yield` in the `quote_log` fixture, which the test never calls; it runs even when the test fails |

## Fixtures: lifetime, setup and teardown

A fixture pattern answers two questions: how long the test's world lives, and who builds it.

| Pattern | The page's summary | In pytest |
| --- | --- | --- |
| [Fresh Fixture](http://xunitpatterns.com/Fresh%20Fixture.html) | "Each test constructs its own brand-new test fixture for its own private use." | a function-scoped fixture; `tmp_path` |
| [Shared Fixture](http://xunitpatterns.com/Shared%20Fixture.html) | "We reuse the same instance of the test fixture across many tests." | `@pytest.fixture(scope="module")` or wider |
| [Standard Fixture](http://xunitpatterns.com/Standard%20Fixture.html) | "The same design of test fixture is used in several tests." | `conftest.py` fixtures such as `consignment` and `fixed_now` that several tests take |
| [Implicit Setup](http://xunitpatterns.com/Implicit%20Setup.html) | "Build the test fixture common to several tests in the setUp method." | `@pytest.fixture(autouse=True)` |
| [Inline Setup](http://xunitpatterns.com/Inline%20Setup.html) | "Each Test Method creates" its own Fresh Fixture by calling constructors in the test | `RecordedAssistant({_PROMPT: ["reply"]})` in the test body |
| [Delegated Setup](http://xunitpatterns.com/Delegated%20Setup.html) | "Each test creates its own Fresh Fixture by calling Creation Methods from within the Test Methods." | `make_consignment(kilograms="3.3")` in the test body |
| [Creation Method](http://xunitpatterns.com/Creation%20Method.html) | "Set up the test fixture by calling methods that hide the mechanics of building ready-to-use objects behind Intent Revealing Names." | a factory fixture |
| [Implicit Teardown](http://xunitpatterns.com/Implicit%20Teardown.html) | "The Test Automation Framework calls our clean up logic in the tearDown method after every Test Method." | code after `yield`, run in reverse order of setup |
| [Automated Teardown](http://xunitpatterns.com/Automated%20Teardown.html) | "We keep track of all resources that are created in a test and automatically destroy/free them during teardown." | `monkeypatch`, qualified |

The setup patterns differ in who calls the builder. An `autouse` fixture is Implicit Setup because the framework runs it without the test naming it; a fixture named in the signature is explicit. A Creation Method in pytest is a factory fixture with parameters:

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

It hides `Consignment(ConsignmentId(...), zone, Weight(Decimal(...)))` behind defaults, so `make_consignment(kilograms="3.3")` says what matters about the consignment and nothing else.

Automated Teardown is qualified. `with monkeypatch.context()` undoes `setenv`, `delenv` and `setattr` changes at the end of the `with` block, where the page says "during teardown". Fixture scopes and teardown order are in [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}).

## Test doubles

[Test Double](http://xunitpatterns.com/Test%20Double.html) is the umbrella: "We replace a component on which the SUT depends" with a test-specific equivalent, where the SUT is the system under test. The kind decides whether the test controls what the SUT receives or sees what it sends.

| Pattern | The page's summary | In Python |
| --- | --- | --- |
| [Dummy Object](http://xunitpatterns.com/Dummy%20Object.html) | "We pass an object that has no implementation as an argument of a method called on the SUT." | `notify=mocker.stub()` passed and never read (qualified) |
| [Test Stub](http://xunitpatterns.com/Test%20Stub.html) | "We replace a real object with a test-specific object that feeds the desired indirect inputs into the system under test." | `slow.quote.side_effect = CarrierTimeoutError(...)` on an autospec |
| [Test Spy](http://xunitpatterns.com/Test%20Spy.html) | "Use a Test Double to capture the indirect output calls made to another component by the system under test (SUT) for later verification by the test." | a fake with a `booked` list; `RecordedAssistant.prompts`; a `mocker.stub()` callback asserted afterwards; an autospec asserted afterwards |
| [Configurable Test Double](http://xunitpatterns.com/Configurable%20Test%20Double.html) | "Configure a reusable Test Double with the values to be returned or verified during the fixture setup phase of a test." | `make_fake("fastline", _usd("10.00"))`; an autospec with `return_value` set |
| [Hard-Coded Test Double](http://xunitpatterns.com/Hard-Coded%20Test%20Double.html) | "Build the Test Double by hard-coding the return values and/or expected calls." | a closure that always returns `2800`; a gateway that returns the constant `"FL-0"` |
| [Test-Specific Subclass](http://xunitpatterns.com/Test-Specific%20Subclass.html) | "Add methods that expose the state or behavior needed by the test to a subclass of the SUT." | a test subclass that overrides `_fastline_quote` and `_airco_price` to reach fakes |
| [Mock Object](http://xunitpatterns.com/Mock%20Object.html) | "Replace an object the system under test (SUT) depends on with a test-specific object that verifies it is being used correctly by the SUT." | none; see below |

**Dummy Object is qualified.** The page's Dummy has "no implementation", and its values "are not used by the SUT". `mocker.stub()` accepts any call, and `book_cheapest` calls it with the booking reference, so the stub is used. What holds is that the test passes it only to fill the parameter and never reads it.

**Configurable or Hard-Coded** is a question of where the answer is written: passed in at setup, or inside the double's body.

**A class named `FakeGateway` isn't a Fake Object.** It's built with its `amount` and `times_out`, which feed the engine's inputs, and it appends to `booked`, which records an output: a Configurable Test Double used as a stub and a spy. The [Fake Object](http://xunitpatterns.com/Fake%20Object.html) page says a stub is "a control point to inject indirect inputs into the SUT" and a fake isn't one, and a double configured with its answers is that control point.

**A Test-Specific Subclass lives in the tests** and changes nothing in `src`. The page covers exposing state and modifying behaviour; overriding a protected method modifies behaviour. [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}) builds the engine these subclasses extend.

**Mock Object is the contrast.** The page's mock checks, as the SUT calls it, that it's used correctly, and fails at the first deviation. A `Mock` asserted after the exercise step is used in the Test Spy's style:

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

The [Test Spy](http://xunitpatterns.com/Test%20Spy.html) page draws the line: "Because a Test Spy does not fail the test at the first deviation from the expected behavior like a Mock Object". Python's `unittest.mock` records calls and checks them afterwards, so its `Mock` class plays the spy.

## Two vocabularies

Two names in the mock libraries collide with Meszaros's.

| Name | pytest-mock means | Meszaros means | Role in practice |
| --- | --- | --- | --- |
| `mocker.stub()` | "a mock object that accepts any arguments and is useful to test callbacks" ([usage](https://pytest-mock.readthedocs.io/en/stable/usage.html)) | Test Stub: a double that feeds indirect inputs | a Test Spy when its calls are asserted; a qualified Dummy when never read |
| `mocker.spy(obj, "method")` | a wrapper that records calls on a real object | Test Spy: records the SUT's indirect outputs | records calls the test itself made, so not a Test Spy |

When a test says "stub" or "spy", ask which vocabulary it's in. The role of a double is the one its test gives it, and the Test Stub in pytest-mock terms is an autospec with `side_effect` set.

## Verifying results

| Pattern | The page's summary | In pytest |
| --- | --- | --- |
| [State Verification](http://xunitpatterns.com/State%20Verification.html) | "We inspect the state of the system under test (SUT) after it has been exercised and compare it to the expected state." | `assert` on the returned quotes |
| [Behavior Verification](http://xunitpatterns.com/Behavior%20Verification.html) | "We capture the indirect outputs of the SUT as they occur and compare them to the expected behavior." | `assert_called_once_with`, `assert_not_called` |
| [Guard Assertion](http://xunitpatterns.com/Guard%20Assertion.html) | "Replace an if statement in a test with an assertion that fails the test if not satisfied." | `assert gateway is not None` before the call |
| [Custom Assertion](http://xunitpatterns.com/Custom%20Assertion.html) | "Create a purpose-built Assertion Method that compares only those attributes of the object that define test-specific equality." | a helper returning a list of failure strings, compared with `[]` (qualified) |
| [Test Utility Method](http://xunitpatterns.com/Test%20Utility%20Method.html) | "We encapsulate the test logic we want to reuse behind a suitably named utility method." | a module-level `_observed` helper shared by several tests |
| [Parameterized Test](http://xunitpatterns.com/Parameterized%20Test.html) | "We pass the information needed to do fixture setup and result verification to a utility method that implements the entire test lifecycle." | `@pytest.mark.parametrize` over a table of rows (qualified) |

State and Behavior Verification are the choice between asking what came back and asking what was called. Martin Fowler's [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) sets the two against each other. A Guard Assertion stands where `if gateway is not None:` would otherwise wrap the call, and it also narrows the type for mypy.

**Custom Assertion is qualified.** `acceptance_failures(shipment, history, client, plan)` makes six checks of an end-to-end shipment (freight, duty, invoice, slot, carrier, tracking) and returns the failures in a fixed order. The test asserts the list equals `[]`, or the failures expected for a stage left out. It doesn't fail the test itself, as the page's Assertion Method does, so it's a Custom Assertion in intent and a report builder in form.

**Parameterized Test is qualified.** The page's test calls a utility method that runs the whole lifecycle, verification included. pytest multiplies one test over data, and the comparison stays in the test body.

## Dependency injection in tests

[Dependency Injection](http://xunitpatterns.com/Dependency%20Injection.html) gives a double its way in: "The client provides the depended-on object to the SUT".

| Form | Example |
| --- | --- |
| Constructor, all dependencies | `BookingService(fake, records.append)` |
| Keyword, one dependency, the rest at production defaults | `parameterised.RateEngine(fastline_quote=fastline_fake)` |
| Constructor, a lock and a hook | `StowagePlan("SAILING-1", lock=nullcontext(), gap=barrier_gap)` |

The design reasons are in [ISP, DIP, and dependency injection without a framework]({{ '/docs/06-isp-dip-and-di-without-a-framework/' | relative_url }}).

## For deeper coverage

Gerard Meszaros's *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley, 2007) is the reference for every pattern in this appendix, and it's on the [bibliography page]({{ '/bibliography/' | relative_url }}). The pattern pages linked in the tables are the pre-publication text on [xunitpatterns.com](http://xunitpatterns.com/), where the site's other patterns are also listed. Martin Fowler's [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) covers the choice between state and behaviour verification. For the pytest side, read [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}) for fixtures and scopes and [Mocking reference: unittest.mock and pytest-mock]({{ '/docs/43-appendix-c-mocking/' | relative_url }}) for the doubles' API.
