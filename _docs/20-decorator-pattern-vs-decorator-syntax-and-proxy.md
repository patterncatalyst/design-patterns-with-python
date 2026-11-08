---
title: "Decorator the pattern vs @decorator the syntax, and Proxy"
order: 20
layout: tutorial
sectionid: docs
part: "composing-adapting-structure"
description: "The Decorator pattern composes wrapper objects while the program runs, the @decorator syntax rebinds a name once at definition time, and a proxy keeps the interface to control access."
---

## Learning objectives

By the end of this chapter you can:

- Say which of two unrelated mechanisms a use of the word "decorator" names: wrapper objects composed while the program runs, or a name rebound once when a module loads.
- Build a stack of layers as a value, chosen per consignment, and say which layers make its order matter: a fixed fee moves the price, and two percentages move it by a cent once rounding is involved.
- Say what a proxy keeps from the Decorator pattern and what it changes, and why an explicit class is the proxy mypy can check.
- Name the four costs of a `__getattr__` forwarding proxy.

## Why this matters

Python gives one word to two things, and mixing them up fails three ways:

- A 600 kg consignment to Rotterdam is priced with the destination tax applied before the heavy-goods fee. The quote is 886.20 where the rules give 889.35, 3.15 short, because the fee escaped the tax.
- A carrier call is wrapped for audit and for retry, with the audit beneath the retry. One quote that needed three attempts produces three audit records. Both are `@` lines above a `def`, and swapping them swaps the answer.
- A gateway proxy forwards unknown attributes to the client it wraps. `proxy.trakc(...)` passes the type checker, because the forwarding method returns `Any`, and fails when it runs.

The first is the Decorator pattern, the second the `@decorator` syntax and the third a proxy. They look alike and fail differently.

{% include excalidraw.html name="20-decorator-pattern-vs-decorator-syntax-and-proxy" described="true" caption="Figure 20.1: Two things called Decorator, and a proxy. Layers are chosen per consignment and stacked as a value while the program runs; the @ form rebinds a name once at definition; the proxy keeps the interface and controls access." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-20-decorator-pattern-vs-decorator-syntax-and-proxy" markdown="1">
On the left, "Decorator pattern: while the program runs": `layers_for(consignment)` leads to `compose(base, layers)`, then to nested frames, `Tax` around `Surcharge` around `BaseRate`, "a value: chosen per consignment". On the right, "@decorator syntax: at definition time": `@retry(attempts=..., on=...)` leads to `def quote_carrier`, then to `quote_carrier`. A dashed note between them reads "same word, unrelated mechanisms". At the bottom, `CarrierGatewayProxy` ("Proxy: same interface, controls access (caches quote)") sits beside a muted dashed box, "forwarding with __getattr__" and "mypy sees Any".
</div>
</details>

The figure sets the pattern and the syntax side by side, with the proxy below.

## Pattern: Decorator

### The problem

A price has adjustments: a heavy-goods fee, a dangerous-goods fee, a destination tax. Which ones apply depends on the consignment, and the order they wrap in changes the total. Adjustments chosen per consignment need wrappers that nest.

### The solution

A **Decorator** is a wrapper object that holds another object, presents the same interface, and adds behaviour around the calls it passes on.

**Bucket: needs disambiguating.** The `@` syntax is a language feature, and a stack chosen per request is still a design. The two halves share a name and almost nothing else, so they need disambiguating.

That's the definition in *Design Patterns* by Gamma, Helm, Johnson and Vlissides. Because a wrapper looks like the thing it wraps, wrappers nest, and the nesting can differ per request. Brandon Rhodes's [The Decorator Pattern](https://python-patterns.guide/gang-of-four/decorator-pattern/) separates the pattern from the `@` syntax. PEP 318, which introduced the `@` form, records the clash itself: "The major one is that the name is not consistent with its use in the GoF book."

| | Decorator pattern | `@decorator` syntax |
| --- | --- | --- |
| What it builds | a value: `Tax(Surcharge(BaseRate(...), fee), percent)` | a rebinding: `quote_carrier = retry(...)(quote_carrier)` |
| When | while the program runs, per consignment | once, when the `def` runs |
| Equality | stacks compare by value | two wrappers of one function are unequal |
| Marker | has `price` | has `__wrapped__` |

Here "Decorator" alone is the pattern, and the syntax is "the `@decorator` syntax" or "the `@` form", following [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}). [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) gives the bucket.

### How Python models it

A rate calculator is anything with a `price` method. Each layer is a frozen dataclass that holds another calculator and satisfies the same Protocol:

<!-- fmt:off -->
```python
@dataclass(frozen=True, slots=True)
class Surcharge:
    """Adds a fixed fee to whatever the wrapped calculator prices."""

    inner: RateCalculator
    fee: Money

    def price(self, consignment: Consignment, /) -> Money:
        return self.inner.price(consignment) + self.fee


type Layer = Callable[[RateCalculator], RateCalculator]


def compose(base: RateCalculator, layers: Sequence[Layer]) -> RateCalculator:
    """Wrap the base in each layer in turn, so the last layer is outermost."""
    calculator = base
    for layer in layers:
        calculator = layer(calculator)
    return calculator
```
<!-- fmt:on -->

A layer leaves its base unchanged: `layered.inner` is the base object, which still prices 120.00 for 100 kg at 1.20 per kilogram. A stack of a surcharge, a tax and a discount reads from the outside in as `Discount`, `Tax`, `Surcharge`, `BaseRate`. Rates and fees are illustrative.

The stack is a value, and `layers_for` chooses it:

```python
def layers_for(consignment: Consignment) -> tuple[Layer, ...]:
    """Choose the layers for this consignment: surcharges first, destination tax last."""
    layers: list[Layer] = []
    if consignment.weight.kilograms > HEAVY_OVER.kilograms:
        layers.append(surcharge(HEAVY_FEE))
    if consignment.dangerous_goods:
        layers.append(surcharge(DANGEROUS_GOODS_FEE))
    country = consignment.destination[:2]
    try:
        layers.append(tax(TAX_RATES[country]))
    except KeyError:
        raise RatingError(f"no tax rate for country {country!r}") from None
    return tuple(layers)
```

A light consignment to Singapore, a heavy one and a dangerous-goods one get one, two and two layers, priced 13.08, 889.35 and 44.77. An unknown country is a `RatingError`, not a silent zero tax. Two stacks built the same way are equal with equal hashes, and a 9 percent tax makes a third unequal. A fee in another currency is refused when it adds, not when it's built.

mypy checks each layer: a class with no `price` where a `Layer` belongs is `[assignment]`, and a misspelt keyword to `Surcharge` through `partial` is `[call-arg]` with `did you mean "fee"?`. A function rebound by `@` has no `price`, so mypy refuses it where a `RateCalculator` belongs.

### When order matters

For 100 kg at 1.20 with a 15.00 fee:

| Stack | Price |
| --- | --- |
| tax outside the fee | 163.35 |
| fee outside the tax | 160.20 |
| 10 percent discount outside the fee | 121.50 |
| fee outside the discount | 123.00 |

The fee isn't a scale, so moving it changes what the percentages apply to. Two percentage layers multiply by constants, so in exact arithmetic either order gives the same price: a 120.00 base gives 130.68 both ways. Rounding to cents after each layer can split them. At 0.05 per kilogram for one kilogram, discount then tax gives 0.06 and tax then discount gives 0.05. A recorded sweep of every per-kilogram price from 0.01 to 200.00 at one kilogram found "6940 of 20000 differ", every one by exactly one cent. 20,000 seeded draws with weights from 1 to 1000 kg gave 6,726, again by one cent: each layer rounds its own total once, so weight doesn't widen the gap.

### The `@` syntax: a rebinding at definition time

PEP 318 gives `@dec2` over `@dec1` over `def func` as equivalent to `func = dec2(dec1(func))`, "without the intermediate assignment to the variable func", and says the `@` lines "are obviously executed at the time the function is defined." PEP 3129 extends the syntax to classes. `retry` and `audited` are factories: `retry(attempts=3, on=...)` returns the function the `@` line applies.

```python
@retry(attempts=3, on=(CarrierTimeoutError,))
def quote_carrier(gateway: CarrierGateway, consignment: Consignment) -> CarrierQuote:
    """Ask a carrier for a price, trying again after a timeout."""
    return gateway.quote(consignment)
```

An `@` function runs once, when the `def` finishes, and not again on calls; the name is bound to the wrapper, whose `__wrapped__` is the original.

- **`retry`** calls again after an error in its `on` tuple and stops after the last attempt: a gateway that times out twice gets three calls and a quote, one that times out three times gets three calls and the error. Other errors pass straight through, and fewer than one attempt is a `ValueError`.
- **`audited(sink)`** reports each call's function name to a sink it's given, so the module holds no log. `src` applies only `@retry`.
- **Stacking order** is fixed when the module loads. Over a gateway that times out twice, `@audited` above `@retry` writes one record, and `@retry` above `@audited` writes three.

The overlap case is a factory that returns something other than a function: `functools.cache` returns an object with `cache_info` that fails `inspect.isfunction`. That's still the `@` syntax. Both factories use [`functools.wraps`](https://docs.python.org/3/library/functools.html#functools.wraps), without which "the name of the example function would have been 'wrapper'", and a PEP 695 `ParamSpec`, so mypy keeps `quote_carrier`'s signature: a `5` for the consignment is `[arg-type]` and `retries=2` is `[call-arg]`. [Decorators done right]({{ '/docs/26-decorators-done-right/' | relative_url }}) covers how both work.

## Pattern: Proxy

### The problem

Asking a carrier for a quote is slow and can time out, so each consignment's quote should be asked for once. Bookings must still reach the carrier every time, and callers shouldn't know they're talking to anything but a gateway.

### The solution

A **Proxy** is a stand-in that sits in front of another object and decides whether, when and how the real one is reached.

**Bucket: survives.** A proxy keeps the interface and returns what the subject returns, which is the design choice an explicit class makes checkable.

A Decorator layer changes what its wrapped object returns, and a proxy doesn't: the caching proxy's quote equals the gateway's, and a `Tax` over the same figure doesn't. Where an Adapter changes the interface, a proxy keeps it; see [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}).

### How Python models it

`CarrierGateway` is a two-member Protocol, and the proxy implements both:

<!-- fmt:off -->
```python
class CarrierGatewayProxy:
    """Asks the gateway for each consignment's quote once, and forwards every booking.

    The cache is a plain dict and is not safe to share between threads.
    """

    def __init__(self, inner: CarrierGateway) -> None:
        self._inner = inner
        self._quotes: dict[Consignment, CarrierQuote] = {}

    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        if consignment not in self._quotes:
            self._quotes[consignment] = self._inner.quote(consignment)
        return self._quotes[consignment]

    def book(self, consignment: Consignment, /) -> str:
        return self._inner.book(consignment)
```
<!-- fmt:on -->

- **Once per consignment.** The gateway is asked once for a consignment, and again for a different one.
- **Every booking.** Two bookings of the same consignment reach the gateway twice.
- **No cached failures.** A quote that times out isn't stored, so the next call asks again.
- **One thread.** The cache is a plain dict. [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) covers two threads reaching a cache together.

mypy checks the class against the Protocol. A copy without `book` gives:

```text
<string>:15: error: Incompatible types in assignment (expression has type "QuoteOnlyProxy", variable has type "CarrierGateway")  [assignment]
<string>:15: note: "QuoteOnlyProxy" is missing following "CarrierGateway" protocol member:
<string>:15: note:     book
```

### The cost of forwarding with `__getattr__`

The comparison form defines `quote` and forwards the rest:

<!-- fmt:off -->
```python
class _ForwardingGatewayProxy:
    def __init__(self, inner: CarrierGateway) -> None:
        self._inner = inner
        self._quotes: dict[Consignment, CarrierQuote] = {}

    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        if consignment not in self._quotes:
            self._quotes[consignment] = self._inner.quote(consignment)
        return self._quotes[consignment]

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._inner, name)
```
<!-- fmt:on -->

It passes the same behaviour cases and it's shorter. It has four costs, the mypy ones measured on reduced models of the same shape:

- **mypy accepts typos.** `proxy.trakc("CN-1")` and `count: int = proxy.track("CN-1")` both exit 0, because the forwarded attribute is `Any`. The explicit proxy reports `"CarrierGatewayProxy" has no attribute "quoet"; maybe "quote"?` as `[attr-defined]`.
- **An `object` return fails the Protocol.** Annotate `__getattr__` as `-> object` and mypy reports `track: expected "Callable[[str], tuple[str, ...]]", got "object"`.
- **`runtime_checkable` doesn't see forwarded members.** `hasattr(proxy, "book")` is true and `isinstance(proxy, _Gateway)` is false. The typing documentation says `isinstance()` against a runtime-checkable protocol "now uses inspect.getattr_static() to look up attributes", which works "without triggering dynamic lookup via the descriptor protocol, `__getattr__()` or `__getattribute__()`".
- **A typo names the wrapped class.** `proxy.bok` raises `'ScriptedGateway' object has no attribute 'bok'`, pointing at the gateway, not the proxy.

`__getattr__` is "Called when the default attribute access fails with an AttributeError", and special methods bypass it: `len()` or `iter()` looks the method up on the proxy's type, as the data model's "Special method lookup" section shows. Rhodes makes the same point about `iter()`. [Dynamic attributes: __getattr__ and Proxy as a feature]({{ '/docs/30-dynamic-attributes-and-proxy/' | relative_url }}) covers `__getattr__`, `__getattribute__` and recursion, and [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) covers caching a computed value with `cached_property`.

## When not to use it

- **Decorator.** Skip the layer stack when the adjustment is one fixed step: a function does it, as in [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}). Skip it when the layers don't vary per consignment, because one calculator reads better.
- **`@decorator` syntax.** Don't put `@retry` around an operation that isn't safe to repeat, such as a booking without an idempotency key, since a repeat can book twice.
- **Proxy.** Don't put a caching proxy over data that must be fresh, and write the proxy explicitly where a forwarding one would do.

<blockquote class="ai-sidebar" markdown="1">
**Specifying wrappers and proxies.** "A decorator" leaves open whether the behaviour is a stack chosen per consignment or a function rebound at definition, which one is called "Decorator", and which wrapper sits outside. Paste a prompt that states the form:

> For price adjustments, write frozen layers that hold a `RateCalculator` and satisfy the same Protocol, composed per consignment by `layers_for`, with fixed fees inside the tax layer. For call behaviour, write `@` factories with `functools.wraps` and a `ParamSpec`, `@audited` above `@retry`. Write the proxy as a class that defines every member of `CarrierGateway`, with no `__getattr__` forwarding. Say "Decorator" only for the layer stack.

If the proxy forwards through `__getattr__`, ask what mypy reports for a typo.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/20-decorator-pattern-vs-decorator-syntax-and-proxy
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 50 cases pass and mypy is clean. [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) covers how the mypy checks are built. Two experiments, each in a fresh scratch copy:

- **Tax before the fees.** In `layers_for`, move the `country = ...` line and its `try` block to just after `layers: list[Layer] = []`. The heavy consignment is 3.15 short at 886.20, the dangerous-goods one is 5.25 short at 39.52, and the stack-shape check fails. mypy is clean: nothing in a type says which layer goes outside.
- **Delete `book` from the proxy.** The explicit proxy raises `AttributeError` on a booking while the forwarding form still passes, because it hands the call to the gateway. mypy reports the missing `book` wherever the proxy is typed as a `CarrierGateway`, here in the fixtures.

## What you can do now

- Say which mechanism "decorator" names: a layer stack built while the program runs, or a name rebound at definition, the mismatch PEP 318 records.
- Build a stack with `layers_for` and `compose(base, layers)`, with fixed fees inside the tax.
- Order `@audited` above `@retry` so each call is audited once.
- Write `CarrierGatewayProxy` as an explicit class that returns the gateway's quote and that mypy checks against the Protocol.
- Name the four costs of a `__getattr__` forwarding proxy: accepted typos, an `object` return, `runtime_checkable` and the wrong class in the error.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Decorator and Proxy. Brandon Rhodes's [The Decorator Pattern](https://python-patterns.guide/gang-of-four/decorator-pattern/) separates the pattern from the syntax. [PEP 318](https://peps.python.org/pep-0318/) introduced the `@` form and [PEP 3129](https://peps.python.org/pep-3129/) extended it to classes. [PEP 612](https://peps.python.org/pep-0612/) specifies `ParamSpec` and [PEP 695](https://peps.python.org/pep-0695/) the generic syntax the factories use. The [`typing` documentation](https://docs.python.org/3/library/typing.html) covers `runtime_checkable`, the [`inspect` documentation](https://docs.python.org/3/library/inspect.html) covers `getattr_static`, and the [data model reference](https://docs.python.org/3/reference/datamodel.html) covers `__getattr__` and special method lookup. Luciano Ramalho's *Fluent Python* and Brett Slatkin's *Effective Python* treat the `@decorator` syntax and closures in depth. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
