---
title: "ISP, DIP, and dependency injection without a framework"
order: 6
layout: tutorial
sectionid: docs
part: "principles"
description: "A consumer names the smallest Protocol it uses, policy owns that abstraction, and one plain function wires the adapters, shown on a booking service whose tests witness each claim."
---

## Learning objectives

By the end of this chapter you can:

- Split a wide gateway into the small Protocols its consumers each use, and say why a fake should implement only what its consumer calls.
- State both clauses of the dependency inversion principle and show, with an import check, that policy names the abstraction and the adapter names neither.
- Inject a collaborator as a dataclass field or through `functools.partial` without a container.
- Write a composition root as a plain function that is the one place that chooses an adapter.
- Say what mypy checks in a fake, a `partial` and an autospec, and where a mock bypasses the check.

## Why this matters

A booking service that constructs its own carrier client can't run in a test suite that has no carrier. The usual repair is a fake, and the repair goes wrong in a predictable way: the carrier interface has grown to offer booking, cancellation and tracking, so every fake must implement all three even when the test exercises one. Each unused method is code to maintain that no assertion reads, and each new method on the interface breaks the fakes that predate it.

Two principles name the pressure. Robert C. Martin's interface segregation principle says a client should not be forced to depend on methods it does not use. His dependency inversion principle says high-level policy should not depend on low-level detail, and that both should depend on abstractions. In a language where an interface is a base class, honouring them costs a hierarchy. In Python 3.15 both forces remain and the mechanism is smaller: a `Protocol` the consumer declares, an adapter that satisfies it without importing it, and a function that hands the adapter over. The example for this chapter is one booking service and one tracking function, with tests that witness each claim.

{% include excalidraw.html name="06-isp-dip-and-di-without-a-framework" caption="Figure 6.1: Dependency injection without a framework. The composition root builds one carrier adapter and passes it to each consumer, which names only the small Protocol it needs; the adapter satisfies both Protocols structurally and imports neither." %}

Read the figure from the top. The root builds one adapter, and the two arrows out of the adapter show that same object reaching both consumers. Each consumer names only the Protocol below it, and the dashed arrows show that the adapter satisfies both Protocols structurally and imports neither.

## A gateway with three methods and consumers that use one

A carrier can book a consignment, cancel a booking and report the handling events recorded for a consignment. A single gateway with those three methods is the natural first design, and it's correct for the code that wires a whole carrier together. It's the wrong thing for a consumer to depend on. Booking calls `book` and `cancel`. Tracking calls `track`. Neither calls the other's methods.

The wiring code does need a name for the whole carrier, and the example gives it one in the composition root:

```python
class CarrierGateway(BookingGateway, TrackingGateway, Protocol):
    """A whole carrier: everything booking and tracking each need, named once for the wiring."""
```

The class has no body of its own. It combines two smaller Protocols, and it lives in `app.py`, not in a policy module. That placement is the design decision. The wide name exists for the one function that builds a whole carrier, and no consumer imports it.

The interface segregation principle is about what a client depends on, not about how many methods an adapter has. `FastlineGateway` still has three methods. What changes is that nothing in the booking or tracking policy is typed against all three.

## Segregation with Protocols the consumer owns

Each policy module declares the Protocol it needs. Booking asks for two methods:

```python
class BookingGateway(Protocol):
    """What booking needs from a carrier: accept a request, withdraw a reference."""

    def book(self, request: BookingRequest, /) -> str: ...

    def cancel(self, reference: str, /) -> None: ...
```

Tracking asks for one, `track(self, consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]`, in `TrackingGateway`. The positional-only `/` matters: without it the parameter name is part of the member's signature, because a caller may pass it by keyword, and the typing specification then requires an implementer to use the same name. mypy 2.4.1 doesn't enforce that for a method member, so the `/` states the intent where the checker would not.

The adapters name none of this. `FastlineGateway` and `AircoGateway` are plain classes with `book`, `track` and `cancel`, no base class and no import of either policy module. The test `test_adapters_satisfy_every_role_without_naming_one` assigns each adapter to a variable annotated `BookingGateway`, one annotated `TrackingGateway` and one annotated `CarrierGateway`, and checks that none of those Protocols appears in the adapter's method resolution order. The annotated assignments are the static witness: pytest executes them but doesn't check the annotations, and the member's `mypy --strict` run does, so a green pytest run alone doesn't cover that half of the claim. A Protocol is structural, so an adapter satisfies it by having the right members, as [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) develops.

Splitting a Protocol therefore costs implementers nothing. An adapter that already satisfied one wide Protocol satisfies its halves, and a new consumer can declare a third small Protocol without touching an adapter.

The benefit appears in the fakes. Pass a class that implements only `track` where `CarrierGateway` is required, and mypy refuses it. The snippet in `test_a_fat_protocol_forces_fakes_to_stub_unused_methods`, run through `mypy --strict`, prints:

```text
<string>:18: error: Argument 1 to "needs_a_whole_carrier" has incompatible type "TrackOnly"; expected "CarrierGateway"  [arg-type]
<string>:18: note: "TrackOnly" is missing following "CarrierGateway" protocol members:
<string>:18: note:     book, cancel
```

The same class passed to `tracking_history`, which asks only for a `TrackingGateway`, type-checks cleanly. The test `test_a_fat_protocol_forces_fakes_to_stub_unused_methods` asserts both outcomes: exit status 1 with exactly the `arg-type` code and the names `book, cancel` for the wide parameter, and exit status 0 with no output for the narrow one. `FakeTracker`, defined in that test module, has one method because its consumer calls one.

## Dependency inversion: the policy names the abstraction

Martin states the dependency inversion principle in two clauses. High-level modules should not depend on low-level modules, and both should depend on abstractions. Abstractions should not depend on details, and details should depend on abstractions. The second clause is the one a Protocol makes cheap. The abstraction is declared by the policy that needs it, in the same module, so the adapter depends on the policy's abstraction, and in Python it does so without an import, because structural typing needs none.

`BookingService` is the policy. It is a frozen dataclass with two collaborators, and it knows no carrier:

```python
@dataclass(frozen=True, slots=True)
class BookingService:
    """Books and cancels through whichever gateway it is given, and audits each outcome."""

    gateway: BookingGateway
    audit: AuditSink

    def book(self, request: BookingRequest) -> str:
        reference = self.gateway.book(request)
        self.audit(f"booked {reference}")
        return reference

    def cancel(self, reference: str) -> None:
        self.gateway.cancel(reference)
        self.audit(f"cancelled {reference}")
```

`AuditSink` is a type alias for `Callable[[str], None]`, so the service asks for a function and any function with that shape is a sink. The test passes `records.append`.

Three tests witness the inversion. `test_booking_service_runs_against_an_injected_fake` builds the service around `FakeBooker`, books, and checks that the reference, the recorded request and the audit record all came from the fake and the service, with no adapter built. `test_policy_modules_do_not_import_the_adapters` parses the source of `booking` and `tracking` with `ast` and asserts that neither imports `isp_dip_di.carriers` or `isp_dip_di.app`. `test_adapters_import_neither_policy_nor_protocols` parses `carriers` and asserts that it imports none of `booking`, `tracking` or `app`. Both import directions are checked, so the check is symmetric: policy doesn't reach down to the adapter, and the adapter doesn't reach up to the policy.

Reading imports with `ast` finds names written as import statements. It would miss a module loaded by a string passed to `importlib`, and the example uses none. It also checks direct imports only, which is enough here because `domain` imports nothing from the package.

## Injection without a container

The word "injection" for handing a collaborator to the code that uses it comes from Martin Fowler's January 2004 article on inversion of control containers and the dependency injection pattern. Strip away the container and the idea is plain. Something other than the consumer decides which collaborator it gets.

For a class, constructor injection is a dataclass field. `BookingService(gateway, audit)` is the whole mechanism, and a frozen dataclass fixes the wiring: neither field can be reassigned after construction.

For a function, the collaborator can be bound ahead of time with `functools.partial`. The tracking policy is a function whose signature is `def tracking_history(consignment_id: ConsignmentId, *, gateway: TrackingGateway) -> TrackingHistory:`, and the root binds the gateway:

```python
    return App(BookingService(gateway, audit), partial(tracking_history, gateway=gateway))
```

The result is a callable that takes only a consignment id. A closure over `gateway` does the same job and reads equally well. The `partial` is the one the tests can inspect: `test_partial_injects_a_collaborator_into_a_function` checks that `app.track.func` is `tracking_history` and that the bound keyword reaches the function, so the tracking function shows the booking made through the service.

There is a gap in what mypy checks here, and it is a limitation of mypy 2.4.1, not a rule of the language. mypy checks the argument bound into the `partial` and the call through it. `partial(tracking_history, gateway=42)` is an `[arg-type]` error, and so is calling the result with an `int`. mypy doesn't check the assignment of a `partial` to a mismatched `Callable` annotation: `wrong: Callable[[int], TrackingHistory] = partial(tracking_history, gateway=gateway)` type-checks with no output. The test `test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment` records all three results, and it will start to fail if a later mypy closes the gap, which is the signal to revise this paragraph. A closure's signature is fully checked, so if the annotation at the assignment matters, the closure is the safer spelling.

## The composition root

Somewhere, a concrete adapter has to be named. The composition root is that place, and it is as close to the program's entry point as it can be. Mark Seemann describes the pattern in his post "Composition Root": application code relies on injection and is never composed itself, and the object graph is built once at the entry point. In this example the root is an ordinary function in `app.py`:

```python
def build_app(
    carrier: str,
    *,
    audit: AuditSink,
    gateways: Mapping[str, Callable[[], CarrierGateway]] = GATEWAYS,
) -> App:
    """Build one gateway for the named carrier and hand it to each consumer."""
    try:
        factory = gateways[carrier]
    except KeyError:
        known = sorted(gateways)
        raise ValueError(f"unknown carrier {carrier!r}, expected one of {known}") from None
    gateway = factory()
    return App(BookingService(gateway, audit), partial(tracking_history, gateway=gateway))
```

`app` is the one module in the source tree that imports `carriers`, and `test_build_app_shares_one_gateway_between_booking_and_tracking` checks that both consumers get the same gateway object. Choosing a carrier is an argument to `build_app`, and `test_swapping_the_carrier_changes_no_consumer` shows that `FASTLINE` and `AIRCO` produce references prefixed with their code through the same `BookingService` and the same `tracking_history`.

An unknown code fails at start-up, where the mistake is cheap to find. `build_app("NOSUCH", ...)` raises `ValueError: unknown carrier 'NOSUCH', expected one of ['AIRCO', 'FASTLINE']`, and `test_unknown_carrier_fails_at_the_composition_root` matches on the code. Tests that need a different adapter pass a substitute `gateways=` mapping. `test_composition_root_accepts_a_substitute_without_patching` wires `FakeCarrier` that way and checks that `GATEWAYS` is unchanged afterwards, so no test needs to patch module state.

## Fakes, autospec, and what mypy checks

A hand-written fake is ordinary typed code. `FakeBooker` in `tests/test_dip.py` has `book` and `cancel`, records the requests it receives, and is checked structurally against `BookingGateway` at the point it is passed in. Interface segregation keeps it small: it needs two methods because booking uses two. `FakeTracker` needs one, and `FakeCarrier` in `tests/test_composition_root.py` has all three because the root's mapping promises a `CarrierGateway`.

When a test asserts on interactions, `mocker.create_autospec` from pytest-mock builds a mock that copies the signatures of a real class. It's a convenient tool with one property to keep in view: a mock is assignable to every type, so mypy checks nothing at the call site. An autospec of the wrong Protocol type-checks where a gateway is expected. `test_autospec_bypasses_mypy` passes `create_autospec(TrackingGateway, instance=True)` as the booking gateway and gets exit status 0 and empty output.

The autospec still enforces the shape at runtime, only later. `test_autospec_enforces_the_protocol_shape_at_runtime` shows the wrong autospec reaching the missing method through `BookingService.cancel`, which raises `AttributeError`, and `wrong.track()` raises `TypeError` for the missing argument. With an autospec of `BookingGateway`, `service.cancel("FASTLINE:CN-1")` records the call and `assert_called_once_with` confirms it. The practical rule is that a hand-written fake gets a static check and an autospec gets a runtime one. The testing chapter, [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}), covers the fixtures and the mock tools in full.

## When the principle costs more than it buys

A Protocol with one implementation and no test double adds a name without adding a seam. If nothing substitutes for the adapter and nothing is likely to, the class itself is the contract and the extra declaration is reading cost. The same holds for a split: two Protocols for a consumer that needs both methods describe a boundary that doesn't exist.

Don't inject the standard library. A function that needs the current directory can call `pathlib.Path.cwd()`. Wrapping `json` or `os` behind a Protocol adds indirection around something a test can already use directly. Inject what varies between environments or what a test must control: a carrier, a clock the test must fix, a message sink.

Hand wiring stops being short at some size. When dozens of services have lifetimes, scopes and ordered start-up, writing the root as a function becomes the problem, and a container library is a reasonable tool for that problem. The signal is the size of the wiring, not the presence of injection.

<blockquote class="ai-sidebar" markdown="1">
**Reviewing assistant-proposed seams.** Asked to make booking testable, an assistant may reach for a container library, a base class per adapter, or one wide gateway Protocol every consumer shares. Paste a prompt that states the form:

> Have each policy module declare a Protocol with only the methods it calls: `BookingGateway` with `book` and `cancel`, `TrackingGateway` with `track`, parameters positional-only. Adapters inherit nothing and import no policy module. Inject through a frozen dataclass field or `functools.partial`. Choose the adapter in one `build_app` function, in the only module that imports `carriers`. No container library for wiring this small. Add an `ast` test that policy modules don't import adapters.

If a fake has to stub a method its consumer never calls, ask for the narrower Protocol.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then from the example directory:

```bash
uv run pytest -v
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 17 items

tests/test_composition_root.py::test_build_app_shares_one_gateway_between_booking_and_tracking PASSED [  5%]
tests/test_composition_root.py::test_partial_injects_a_collaborator_into_a_function PASSED [ 11%]
tests/test_composition_root.py::test_swapping_the_carrier_changes_no_consumer PASSED [ 17%]
tests/test_composition_root.py::test_composition_root_accepts_a_substitute_without_patching PASSED [ 23%]
tests/test_composition_root.py::test_unknown_carrier_fails_at_the_composition_root PASSED [ 29%]
tests/test_dip.py::test_booking_service_runs_against_an_injected_fake PASSED [ 35%]
tests/test_dip.py::test_policy_modules_do_not_import_the_adapters[booking] PASSED [ 41%]
tests/test_dip.py::test_policy_modules_do_not_import_the_adapters[tracking] PASSED [ 47%]
tests/test_dip.py::test_adapters_import_neither_policy_nor_protocols PASSED [ 52%]
tests/test_dip.py::test_autospec_bypasses_mypy PASSED                    [ 58%]
tests/test_dip.py::test_autospec_enforces_the_protocol_shape_at_runtime PASSED [ 64%]
tests/test_dip.py::test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment[binding] PASSED [ 70%]
tests/test_dip.py::test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment[call] PASSED [ 76%]
tests/test_dip.py::test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment[assignment] PASSED [ 82%]
tests/test_isp.py::test_adapters_satisfy_every_role_without_naming_one[FASTLINE] PASSED [ 88%]
tests/test_isp.py::test_adapters_satisfy_every_role_without_naming_one[AIRCO] PASSED [ 94%]
tests/test_isp.py::test_a_fat_protocol_forces_fakes_to_stub_unused_methods PASSED [100%]

============================== 17 passed in 3.42s ==============================
```

```text
Success: no issues found in 10 source files
```

Two edits make the checks visible: one that breaks the import direction, and one that shrinks a fake.

**Experiment one: let policy import an adapter.** In a scratch copy, add `from isp_dip_di.carriers import FastlineGateway` to `src/isp_dip_di/booking.py`, just above the `domain` import, and run `uv run pytest`. The result is one failure and sixteen passes: `tests/test_dip.py::test_policy_modules_do_not_import_the_adapters[booking]` fails on the line `assert not imports & {"isp_dip_di.carriers", "isp_dip_di.app"}`, and the assertion message lists `isp_dip_di.carriers` and `isp_dip_di.carriers.FastlineGateway` among the collected imports. The `tracking` case still passes, and mypy stays clean. `ruff check` reports the new line as `F401`, an unused import, so a linter alone would catch this edit only because the name is unused. Had `booking.py` used `FastlineGateway`, the import test would still be the one to notice. Revert the line.

**Experiment two: shrink a fake past its Protocol.** In a scratch copy, delete the `cancel` method from `FakeBooker` in `tests/test_dip.py` and run both commands. All seventeen tests still pass, because no test calls `cancel` on that fake. mypy is the one that objects, with one error on the line that constructs the service:

```text
tests/test_dip.py:74: error: Argument 1 to "BookingService" has incompatible type "FakeBooker"; expected "BookingGateway"  [arg-type]
tests/test_dip.py:74: note: "FakeBooker" is missing following "BookingGateway" protocol member:
tests/test_dip.py:74: note:     cancel
```

A passing pytest run doesn't prove a fake still satisfies the Protocol it stands in for. Restore the method.

## What you can do now

- Split a wide gateway: `BookingGateway` and `TrackingGateway` replace `CarrierGateway` as the consumers' types, and `test_a_fat_protocol_forces_fakes_to_stub_unused_methods` shows a one-method fake refused by the wide one and accepted by the narrow one.
- Show the dependency direction: `test_policy_modules_do_not_import_the_adapters` and `test_adapters_import_neither_policy_nor_protocols` read the imports with `ast` in both directions.
- Inject without a container: `BookingService` takes its gateway as a field, and `functools.partial` binds it into `tracking_history`.
- Write a composition root: `build_app` is the one function that chooses an adapter, and `test_build_app_shares_one_gateway_between_booking_and_tracking` checks the result.
- Say what mypy checks: `test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment` marks the `partial` gap, and `test_autospec_bypasses_mypy` shows where a mock skips the check.

## For deeper coverage

Robert C. Martin's *Agile Software Development, Principles, Patterns, and Practices* is where the interface segregation and dependency inversion principles are stated and worked through; it is in the hub's list and on the [bibliography page]({{ '/bibliography/' | relative_url }}). Harry Percival and Bob Gregory's *Architecture Patterns with Python* applies dependency inversion in Python services and shows the same fake-versus-real split at application scale.

Martin Fowler's article [Inversion of Control Containers and the Dependency Injection pattern](https://martinfowler.com/articles/injection.html), first published in January 2004, names constructor, setter and interface injection and compares them with a service locator. Mark Seemann's post [Composition Root](https://blog.ploeh.dk/2011/07/28/CompositionRoot/) describes where to compose the object graph.

The language references are [PEP 544](https://peps.python.org/pep-0544/) on Protocols, the [functools documentation](https://docs.python.org/3.15/library/functools.html) for `partial`, and the [unittest.mock documentation on autospeccing](https://docs.python.org/3.15/library/unittest.mock.html#autospeccing) for `create_autospec`.
