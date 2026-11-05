---
layout: example
order: 6
title: "ISP, DIP and DI without a framework: consumer-owned Protocols and a composition root"
description: One booking service and one tracking function whose tests show small consumer-owned Protocols, policy that imports no adapter, and a plain composition root.
github_path: examples/06-isp-dip-and-di-without-a-framework
card_eyebrow: "Principles: SOLID · ISP, DIP, DI"
card_title: "Small Protocols owned by consumers and one plain wiring function"
card_blurb: "Booking and tracking each depend on the smallest Protocol they use, carrier adapters satisfy them without naming them, and one plain function wires the whole application."
---

One booking service and one tracking function witness two of the SOLID principles and the
wiring that joins them. Each test asserts the behaviour named in its title.

## Interface segregation

`BookingGateway` (`book`, `cancel`) and `TrackingGateway` (`track`) are declared by the modules
that consume them. The in-memory `FastlineGateway` and `AircoGateway` have no base class and
satisfy both. A fake that implements only `track` is rejected where the combined
`CarrierGateway` is required, and accepted by `tracking_history`.

## Dependency inversion

- `BookingService` runs against an injected fake with no carrier built.
- The policy modules import neither the adapters nor the composition root, and the adapters
  import neither policy module.
- An autospec of the wrong Protocol passes `mypy --strict` and fails at runtime.

## The composition root

`app.py`, home of `build_app`, is the only module that names a concrete adapter. It builds one gateway and gives
it to `BookingService` as a field and to `tracking_history` through `functools.partial`. mypy
checks the bound argument and the call through the partial, but not its assignment to a
`Callable` annotation. A substitute mapping replaces the adapters without patching, and an
unknown carrier code fails at start-up.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/06-isp-dip-and-di-without-a-framework
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
