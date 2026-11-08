---
title: "ISP, DIP, and dependency injection without a framework"
order: 6
layout: tutorial
sectionid: docs
part: "principles"
description: "A consumer names the smallest Protocol it uses, policy owns that abstraction, and one plain function wires the adapters, shown on a runnable booking service."
---

## Learning objectives

By the end of this chapter you can:

- Split a wide gateway into the small Protocols its consumers each use, and say why a fake should implement only what its consumer calls.
- State both clauses of the dependency inversion principle and show, with an import check, that policy names the abstraction and the adapter names neither.
- Inject a collaborator as a dataclass field or through `functools.partial` without a container.
- Write a composition root as a plain function that is the one place that chooses an adapter.
- Say what mypy checks in a fake, a `partial` and an autospec, and where a mock bypasses the check.

## Why this matters

A booking service that constructs its own carrier client can't run in a test without a carrier. The usual repair is a fake, and it goes wrong predictably: the carrier interface offers booking, cancellation and tracking, so every fake implements all three even when a test uses one. Each unused method is code no assertion reads, and each new method on the interface breaks the fakes that predate it.

Robert C. Martin's interface segregation principle says a client shouldn't be forced to depend on methods it doesn't use. His dependency inversion principle says high-level policy shouldn't depend on low-level detail, and both should depend on abstractions. Where an interface is a base class, honouring them costs a hierarchy. In Python the mechanism is smaller: a `Protocol` the consumer declares, an adapter that satisfies it without importing it, and a function that hands the adapter over.

{% include excalidraw.html name="06-isp-dip-and-di-without-a-framework" described="true" caption="Figure 6.1: Dependency injection without a framework. The composition root builds one carrier adapter and passes it to each consumer, which names only the small Protocol it needs; the adapter satisfies both Protocols structurally and imports neither." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-06-isp-dip-and-di-without-a-framework" markdown="1">
From the top: `build_app(carrier)`, the composition root, builds one adapter, `FastlineGateway` or `AircoGateway`, with no base class. Two arrows take that same object to both consumers: `BookingService(gateway, audit)` and `partial(tracking_history, gateway=...)`, each injected by the root. Below each consumer is the only Protocol it names: `BookingGateway` (`book`, `cancel`) and `TrackingGateway` (`track`). Dashed arrows from the adapter to both Protocols show that it satisfies them structurally and imports neither.
</div>
</details>

One adapter object reaches both consumers, and each consumer names only its own Protocol.

## A gateway with three methods and consumers that use one

A carrier can book a consignment, cancel a booking and report handling events. A gateway with those three methods is right for the code that wires a whole carrier together and wrong for a consumer to depend on: booking calls `book` and `cancel`, and tracking calls `track`.

The wiring code still needs a name for the whole carrier, so the composition root declares one:

```python
class CarrierGateway(BookingGateway, TrackingGateway, Protocol):
    """A whole carrier: everything booking and tracking each need, named once for the wiring."""
```

It combines two smaller Protocols and lives in `app.py`, not in a policy module. The wide name exists for the one function that builds a carrier, and no consumer imports it. Segregation is about what a client depends on, not how many methods an adapter has: `FastlineGateway` still has three, but nothing in booking or tracking is typed against all three.

## Segregation with Protocols the consumer owns

Each policy module declares the Protocol it needs. Booking asks for two methods:

```python
class BookingGateway(Protocol):
    """What booking needs from a carrier: accept a request, withdraw a reference."""

    def book(self, request: BookingRequest, /) -> str: ...

    def cancel(self, reference: str, /) -> None: ...
```

Tracking asks for one, `track(self, consignment_id: ConsignmentId, /) -> tuple[HandlingEvent, ...]`, in `TrackingGateway`. The positional-only `/` matters: without it a caller may pass the argument by keyword, so the typing specification requires an implementer to use the same parameter name.

`FastlineGateway` and `AircoGateway` are plain classes with `book`, `track` and `cancel`, no base class and no import of either policy module. Each type-checks as a `BookingGateway`, a `TrackingGateway` and a `CarrierGateway`, and none of those appears in its method resolution order. That half of the claim is static: `mypy --strict` checks the annotated assignments, and pytest alone doesn't. [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) develops structural matching.

Splitting a Protocol costs implementers nothing: an adapter that satisfied the wide Protocol satisfies its halves, and a new consumer can declare a third without touching an adapter.

The benefit is in the fakes. A class with only `track`, passed where `CarrierGateway` is required:

```text
<string>:18: error: Argument 1 to "needs_a_whole_carrier" has incompatible type "TrackOnly"; expected "CarrierGateway"  [arg-type]
<string>:18: note: "TrackOnly" is missing following "CarrierGateway" protocol members:
<string>:18: note:     book, cancel
```

The same class passed to `tracking_history`, which asks only for a `TrackingGateway`, type-checks with no output. `FakeTracker` has one method because its consumer calls one.

## Dependency inversion: the policy names the abstraction

Martin's two clauses:

1. High-level modules shouldn't depend on low-level modules; both should depend on abstractions.
2. Abstractions shouldn't depend on details; details should depend on abstractions.

A Protocol makes the second clause cheap. The policy declares the abstraction in its own module, and the adapter conforms to it without an import, because structural typing needs none. `BookingService` is the policy, a frozen dataclass that knows no carrier:

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

`AuditSink` is `Callable[[str], None]`, so `records.append` is a sink. Around `FakeBooker`, the service books with no adapter built, and the reference, the recorded request and the audit line all come from the fake and the service.

The import direction is checked both ways by parsing source with `ast`:

| Module | Must not import |
| --- | --- |
| `booking`, `tracking` | `isp_dip_di.carriers`, `isp_dip_di.app` |
| `carriers` | `booking`, `tracking`, `app` |

Reading imports with `ast` finds import statements. It would miss a module loaded by a string passed to `importlib`, which the booking code doesn't use, and it checks direct imports only, which is enough because `domain` imports nothing from the package.

## Injection without a container

The word "injection" comes from Martin Fowler's January 2004 article on inversion of control containers. Without the container, the idea is that something other than the consumer decides which collaborator it gets.

- **A class** takes it as a dataclass field. `BookingService(gateway, audit)` is the whole mechanism, and `frozen=True` stops either field being reassigned.
- **A function** gets it bound ahead of time. `tracking_history(consignment_id, *, gateway)` is bound by the root:

```python
    return App(BookingService(gateway, audit), partial(tracking_history, gateway=gateway))
```

The result takes only a consignment id. A closure over `gateway` does the same job. The `partial` is inspectable: `app.track.func` is `tracking_history`, and a booking made through the service shows up in its history.

mypy 2.4.1 checks a `partial` in two places and not the third:

| Code | mypy |
| --- | --- |
| `partial(tracking_history, gateway=42)` | `[arg-type]` |
| Calling the bound `partial` with an `int` | `[arg-type]` |
| `wrong: Callable[[int], TrackingHistory] = partial(tracking_history, gateway=gateway)` | No output |

That's a limitation of mypy, not a rule of the language, and a later mypy may close it. A closure's signature is fully checked, so prefer it when the annotation at the assignment matters.

## The composition root

Somewhere a concrete adapter has to be named, as close to the entry point as possible. Mark Seemann's "Composition Root" describes it: application code relies on injection and is never composed itself, and the object graph is built once at the entry point. Here the root is an ordinary function in `app.py`:

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

- `app` imports `carriers`; neither policy module does.
- Both consumers get the same gateway object.
- `FASTLINE` and `AIRCO` produce references prefixed with their code through the same `BookingService` and `tracking_history`.
- An unknown code fails at start-up, where it's cheap: `build_app("NOSUCH", ...)` raises `ValueError: unknown carrier 'NOSUCH', expected one of ['AIRCO', 'FASTLINE']`.
- A test passes a substitute `gateways=` mapping holding `FakeCarrier`, and `GATEWAYS` is unchanged afterwards, so no test patches module state.

## Fakes, autospec, and what mypy checks

A hand-written fake is ordinary typed code, checked structurally where it's passed in. Segregation keeps it small:

| Fake | Methods | Because |
| --- | --- | --- |
| `FakeBooker` | `book`, `cancel` | Booking uses two |
| `FakeTracker` | `track` | Tracking uses one |
| `FakeCarrier` | All three | The root's mapping promises a `CarrierGateway` |

When a test asserts on interactions, `mocker.create_autospec` from pytest-mock copies the signatures of a real class. A mock is assignable to every type, though, so mypy checks nothing at the call site: `create_autospec(TrackingGateway, instance=True)` passed as the booking gateway type-checks with no output.

The autospec enforces the shape at run time instead. That wrong autospec raises `AttributeError` when `BookingService.cancel` reaches the missing method, and `wrong.track()` raises `TypeError` for the missing argument. With an autospec of `BookingGateway`, `service.cancel("FASTLINE:CN-1")` records the call for `assert_called_once_with`. A fake gets a static check; an autospec gets a run-time one. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) covers the mock tools in full.

## When the principle costs more than it buys

- **A Protocol with one implementation and no test double** adds a name without a seam. If nothing substitutes for the adapter, the class is the contract. Two Protocols for a consumer that needs both methods describe a boundary that doesn't exist.
- **Don't inject the standard library.** A function that needs the current directory can call `pathlib.Path.cwd()`. Inject what varies between environments or what a test must control: a carrier, a clock a test must fix, a message sink.
- **Hand wiring has a size limit.** With dozens of services, lifetimes, scopes and ordered start-up, the root function becomes the problem, and a container library is a reasonable tool. The signal is the size of the wiring, not the presence of injection.

<blockquote class="ai-sidebar" markdown="1">
**Specifying seams.** "Make booking testable" leaves open what the seam is, who owns it and where the adapter is chosen. Paste a prompt that states the form:

> Have each policy module declare a Protocol with only the methods it calls: `BookingGateway` with `book` and `cancel`, `TrackingGateway` with `track`, parameters positional-only. Adapters inherit nothing and import no policy module. Inject through a frozen dataclass field or `functools.partial`. Choose the adapter in one `build_app` function, in the only module that imports `carriers`. No container library for wiring this small. Add an `ast` test that policy modules don't import adapters.

If a fake has to stub a method its consumer never calls, ask for the narrower Protocol.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/06-isp-dip-and-di-without-a-framework
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 17 cases pass, and mypy reports no issues in 10 source files. Make each experiment in a scratch copy:

- **Let policy import an adapter.** Add `from isp_dip_di.carriers import FastlineGateway` to `src/isp_dip_di/booking.py`, above the `domain` import. One case fails, the import check for `booking`, listing `isp_dip_di.carriers` among the collected imports; `tracking` still passes and mypy stays clean. `ruff check` flags the line as `F401` only because the name is unused; if `booking.py` used it, the import check would be the only one to notice.
- **Shrink a fake past its Protocol.** Delete `cancel` from `FakeBooker` in `tests/test_dip.py`. All 17 cases still pass, because none calls `cancel` on that fake. mypy objects where the service is built:

```text
tests/test_dip.py:74: error: Argument 1 to "BookingService" has incompatible type "FakeBooker"; expected "BookingGateway"  [arg-type]
tests/test_dip.py:74: note: "FakeBooker" is missing following "BookingGateway" protocol member:
tests/test_dip.py:74: note:     cancel
```

A green pytest run doesn't prove a fake still satisfies the Protocol it stands in for.

## What you can do now

- Split a wide gateway into `BookingGateway` and `TrackingGateway`, and keep `CarrierGateway` for the wiring, so a one-method fake fits its consumer.
- Show the dependency direction by reading imports with `ast`: policy never imports `carriers`, and `carriers` never imports policy.
- Inject without a container: `BookingService` takes its gateway as a field, and `functools.partial` binds it into `tracking_history`.
- Write a composition root: `build_app` is the one function that chooses an adapter, and both consumers share what it builds.
- Say what mypy checks: the `partial` assignment gap, the static check on a fake, and the autospec that skips it.

## For deeper coverage

Robert C. Martin's *Agile Software Development, Principles, Patterns, and Practices* is where the interface segregation and dependency inversion principles are stated and worked through; it is on the [bibliography page]({{ '/bibliography/' | relative_url }}). Harry Percival and Bob Gregory's *Architecture Patterns with Python* applies dependency inversion in Python services and shows the same fake-versus-real split at application scale.

Martin Fowler's article [Inversion of Control Containers and the Dependency Injection pattern](https://martinfowler.com/articles/injection.html), first published in January 2004, names constructor, setter and interface injection and compares them with a service locator. Mark Seemann's post [Composition Root](https://blog.ploeh.dk/2011/07/28/CompositionRoot/) describes where to compose the object graph.

The language references are [PEP 544](https://peps.python.org/pep-0544/) on Protocols, the [functools documentation](https://docs.python.org/3/library/functools.html) for `partial`, and the [unittest.mock documentation on autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing) for `create_autospec`.
