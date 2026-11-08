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
- Name the four measured costs of a `__getattr__` forwarding proxy.

## Why this matters

Python gives one word to two things, and three failures follow from mixing them up.

A 600 kg consignment to Rotterdam is priced with the destination tax applied before the heavy-goods fee. The quote is 886.20 where the rules give 889.35, 3.15 short, because the fee escaped the tax.

A carrier call is wrapped for audit and for retry, and the audit sits beneath the retry. One quote that needed three attempts produces three audit records. Both are `@` lines above a `def`, and swapping them swaps the answer.

A gateway proxy forwards unknown attributes to the carrier client it wraps. A call to `proxy.trakc(...)` passes the type checker, because the forwarding method returns `Any`, and fails when it runs.

The first is the Decorator pattern, the second the `@decorator` syntax and the third a proxy. They look alike and fail differently.

{% include excalidraw.html name="20-decorator-pattern-vs-decorator-syntax-and-proxy" caption="Figure 20.1: Two things called Decorator, and a proxy. Layers are chosen per consignment and stacked as a value while the program runs; the @ form rebinds a name once at definition; the proxy keeps the interface and controls access." %}

On the left, "Decorator pattern: while the program runs": `layers_for(consignment)` leads to `compose(base, layers)`, then to nested frames, `Tax` around `Surcharge` around `BaseRate`, "a value: chosen per consignment". On the right, "@decorator syntax: at definition time": `@retry(attempts=..., on=...)` leads to `def quote_carrier`, then to `quote_carrier`. A dashed note between them reads "same word, unrelated mechanisms". At the bottom, `CarrierGatewayProxy` ("Proxy: same interface, controls access (caches quote)") sits beside a muted dashed box, "forwarding with __getattr__" and "mypy sees Any".

## Two things called Decorator

The pattern builds a value: `Tax(Surcharge(BaseRate(...), fee), percent)`. The syntax rebinds a name: `quote_carrier = retry(...)(quote_carrier)`, which the `@` line above a `def` spells in one step.

*Design Patterns*, by Gamma, Helm, Johnson and Vlissides, gives the name Decorator to a wrapper object that holds another object and presents the same interface, with behaviour added around the calls it passes on. Because a wrapper looks like the thing it wraps, wrappers nest, and the nesting can differ from one request to the next. Brandon Rhodes's page "The Decorator Pattern" at python-patterns.guide separates the pattern from the `@` syntax and warns about the clash of names.

PEP 318, which introduced the `@` form, records the mismatch in its own text. Among the complaints about the name, it says: "The major one is that the name is not consistent with its use in the GoF book." The sorting question from [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) gives this pair its bucket. The syntax is a language feature. A stack chosen per request is still a design. The two halves share a name and almost nothing else, so they need disambiguating.

In this chapter, "Decorator" alone is the pattern. The syntax is "the `@decorator` syntax" or "the `@` form". The naming rule is set out in [Naming patterns for teams and AI assistants]({{ '/docs/04-naming-patterns-for-teams-and-ai/' | relative_url }}).

## The pattern: a stack of layers

Adjustments chosen per consignment need wrappers that nest. A rate calculator is anything with a `price` method, and each layer is a frozen dataclass that holds another calculator and satisfies the same Protocol. One layer, the type of a layer, and the function that composes a stack:

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

`test_a_layer_wraps_a_calculator_and_leaves_it_unchanged` shows that `layered.inner` is the base object, that the base still prices 120.00 for 100 kg at 1.20 per kilogram, and that it still equals a freshly built `BaseRate`. `test_compose_wraps_the_last_layer_outermost` composes a surcharge, a tax and a discount and reads the types from the outside in: `Discount`, `Tax`, `Surcharge`, `BaseRate`. Rates and fees here are illustrative.

Order matters once a layer adds a fixed amount. For 100 kg at 1.20, with a 15.00 fee, `test_layer_order_changes_the_price_when_a_fee_is_added` has four stacks and four prices. Tax outside the fee gives 163.35, and the fee outside the tax gives 160.20. A 10 percent discount outside the fee gives 121.50, and the fee outside the discount gives 123.00. The fee isn't a scale, so moving it changes what the percentages apply to.

Two percentage layers are different. In exact arithmetic a 10 percent discount and a 21 percent tax both multiply by a constant, so either order gives the same price. With rounding to cents after each layer they can split. `test_two_percentage_layers_agree_before_rounding_and_can_split_by_a_cent` prices a 120.00 base both ways and gets 130.68 each time. At 0.05 per kilogram for one kilogram, discount then tax gives 0.06 and tax then discount gives 0.05. A recorded sweep covers every per-kilogram price from 0.01 to 200.00 at one kilogram: "6940 of 20000 differ", every one by exactly one cent. A second run of 20,000 seeded draws, with weights from 1 to 1000 kg, gave 6,726 differing, again by one cent. A heavier consignment doesn't widen the gap, because each layer rounds its own total once.

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

`test_the_layers_for_a_consignment_are_chosen_while_the_program_runs` runs a light consignment to Singapore, a heavy one and a dangerous-goods one, and gets one, two and two layers and the prices 13.08, 889.35 and 44.77. An unknown country is a `RatingError` and not a silent zero tax. The layers are data, so they compare by value: `test_layer_stacks_compare_by_value` builds two stacks the same way and finds them equal with equal hashes, and a 9 percent tax makes a third unequal. A layer in another currency is refused when it adds, not when it's built (`test_a_layer_refuses_a_fee_in_another_currency`).

mypy checks each layer. A class with no `price` where a `Layer` belongs is `[assignment]`, and a misspelt keyword passed to `Surcharge` through `partial` is `[call-arg]` with the suggestion `did you mean "fee"?`. It also refuses a rebound function where a calculator belongs: `test_mypy_rejects_a_decorated_function_where_a_calculator_belongs` assigns one to a `RateCalculator` and gets `[assignment]`. A function has no `price` member (`test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped`), so it doesn't satisfy the Protocol.

## The syntax: a rebinding at definition time

The `@` form is a statement about a name. PEP 318 gives it as two lines, `@dec2` over `@dec1` over a `def func`, and says: "This is equivalent to:" a plain `def func`, then `func = dec2(dec1(func))`, "without the intermediate assignment to the variable func." Its section "Decorator Location" says the `@` lines live outside the method body and "are obviously executed at the time the function is defined." PEP 3129 extends the same syntax to classes: "This PEP proposes class decorators, an extension to the function and method decorators introduced in PEP 318."

`retry` and `audited` are factories: calling `retry(attempts=3, on=...)` returns the function that the `@` line applies.

```python
@retry(attempts=3, on=(CarrierTimeoutError,))
def quote_carrier(gateway: CarrierGateway, consignment: Consignment) -> CarrierQuote:
    """Ask a carrier for a price, trying again after a timeout."""
    return gateway.quote(consignment)
```

`test_the_at_sign_rebinds_the_name_once_at_definition_time` uses an `@` function of its own that records each function it's applied to. It has run once when the `def` finishes, and it hasn't run again after two calls. The name `quote` is bound to the wrapper, and its `__wrapped__` is a different object. The same check on `quote_carrier` gives the same result.

`retry` calls again after an error in its `on` tuple and stops after the last attempt: with a gateway that times out twice, `quote_carrier` makes three calls and returns the quote, and with one that times out three times it makes three calls and raises (`test_retry_calls_again_on_a_listed_error_and_gives_up_after_the_last_attempt`). An error outside the tuple goes straight through after one call, and fewer than one attempt is a `ValueError`. `audited(sink)` reports each call's function name to a sink it's given, so the module holds no log, and `src` applies only `@retry`.

Stacking order is fixed when the module loads. `test_syntax_stacking_order_decides_whether_each_attempt_is_audited` defines two functions over a gateway that times out twice. With `@audited` above `@retry`, the sink has one record. With `@retry` above `@audited`, it has three. Rebound functions don't compare by value: two calls of `retry(...)` on the same function give two unequal wrappers (`test_rebound_functions_do_not_compare_by_value`), where two layer stacks built the same way are equal.

A rebound function has no `price`, and a layer has no `__wrapped__`. The overlap case is a factory that returns an object that isn't a function. `functools.cache` does, and the returned value has `cache_info` and fails `inspect.isfunction` (`test_a_decorator_may_return_an_object_that_is_not_a_function`). That use is still `@decorator` syntax, rebound at definition. Both factories use [`functools.wraps`](https://docs.python.org/3.15/library/functools.html#functools.wraps), without which, its documentation says, "the name of the example function would have been 'wrapper'", and a PEP 695 `ParamSpec`. The witness here is that mypy keeps `quote_carrier`'s signature through `retry`: a `5` for the consignment is `[arg-type]` and `retries=2` is `[call-arg]` (`test_mypy_keeps_the_call_signature_through_retry`). How both work is the subject of [Decorators done right]({{ '/docs/26-decorators-done-right/' | relative_url }}).

## Proxy: the same interface, controlling access

*Design Patterns* gives Proxy to a stand-in that sits in front of another object and decides whether, when and how the real one is reached. A layer in the Decorator pattern adds behaviour to what its wrapped object returns, and a proxy returns what the subject returns. The tax layer changes a price. A proxy that caches a quote leaves it alone, and `test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price` sets the two side by side: the proxy's quote equals the gateway's, and a `Tax` over the same figure doesn't. Where an Adapter changes the interface, a proxy keeps it. For the Adapter, see [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}).

The proxy here guards the call to a carrier. `CarrierGateway` is a two-member Protocol, and the proxy implements both members itself:

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

The proxy asks the gateway once per consignment, and again for a different one (`test_the_proxy_asks_the_gateway_once_per_consignment`). Two bookings of the same consignment reach the gateway twice (`test_the_proxy_forwards_every_booking`). A quote that times out isn't stored, so the next call asks again and the one after that is answered from the cache (`test_a_timed_out_quote_is_not_cached`). The cache is a plain dict and the proxy is for one thread; what happens when two threads reach a cache together is in [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}).

mypy checks the class against the Protocol. A copy without `book`, in `test_mypy_reports_a_member_missing_from_an_explicit_proxy`, is a reduced model of the proxy over the same two-member Protocol. The test's own snippet, run through its own helper, printed:

```text
<string>:15: error: Incompatible types in assignment (expression has type "QuoteOnlyProxy", variable has type "CarrierGateway")  [assignment]
<string>:15: note: "QuoteOnlyProxy" is missing following "CarrierGateway" protocol member:
<string>:15: note:     book
```

The other way to write a proxy forwards whatever it doesn't define. The comparison form, in `tests/conftest.py`, defines `quote` and hands the rest to the wrapped gateway:

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

It's a parameter of the same fixture, so the three behaviour tests above run once per form and both forms pass. It's shorter, and it has four costs. The mypy ones come from reduced models in `test_static.py` with the same shape (a Protocol, an inner class and a forwarding proxy), not from this fixture.

- **mypy accepts typos.** `proxy.trakc("CN-1")` and `count: int = proxy.track("CN-1")` both exit 0 with no output (`test_mypy_accepts_a_typo_through_a_forwarding_proxy`), because the forwarded attribute is `Any`. The explicit proxy reports `"CarrierGatewayProxy" has no attribute "quoet"; maybe "quote"?` as `[attr-defined]` (`test_mypy_reports_a_typo_on_the_explicit_proxy`).
- **An `object` return fails the Protocol.** Annotate `__getattr__` as `-> object` and the proxy no longer satisfies it (`test_mypy_rejects_a_forwarding_proxy_that_returns_object`). mypy 2.4.1 printed:

```text
<string>:22: error: Incompatible types in assignment (expression has type "ForwardingProxy", variable has type "Gateway")  [assignment]
<string>:22: note: Following member(s) of "ForwardingProxy" have conflicts:
<string>:22: note:     track: expected "Callable[[str], tuple[str, ...]]", got "object"
```

- **`runtime_checkable` doesn't see forwarded members.** For the forwarding proxy `hasattr(proxy, "book")` is true and `isinstance(proxy, _Gateway)` is false, while the explicit proxy passes both (`test_runtime_checkable_does_not_see_attributes_forwarded_by_getattr`). The typing documentation says: "The internal implementation of isinstance() checks against runtime-checkable protocols now uses inspect.getattr_static() to look up attributes (previously, hasattr() was used)." The `inspect` documentation says `getattr_static` retrieves attributes "without triggering dynamic lookup via the descriptor protocol, `__getattr__()` or `__getattribute__()`".
- **A typo names the wrapped class.** `proxy.bok` raises an `AttributeError` that reads `'ScriptedGateway' object has no attribute 'bok'`, so the message points at the gateway and not at the proxy (`test_a_forwarded_typo_is_reported_against_the_wrapped_gateway`).

The data model documents when `__getattr__` runs: it's "Called when the default attribute access fails with an AttributeError". It adds that `__getattribute__` "may still be bypassed when looking up special methods as the result of implicit invocation via language syntax or built-in functions", so a built-in such as `len()` or `iter()` looks the special method up on the proxy's type, as the reference's "Special method lookup" section shows for `len()`, not through `__getattr__`. Rhodes makes the same point about `iter()`. The mechanics of `__getattr__`, `__getattribute__` and recursion are the business of [Dynamic attributes: __getattr__ and Proxy as a feature]({{ '/docs/30-dynamic-attributes-and-proxy/' | relative_url }}). A proxy that caches a computed value on an object belongs with `property` and `cached_property`, in [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}).

## When not to use it

Skip the layer stack when the adjustment is one fixed step: a function does it, as in [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}). Skip it when the layers don't vary per consignment, because one calculator reads better. Don't put `@retry` around an operation that isn't safe to repeat, such as a booking without an idempotency key, since a repeat can book twice. Don't put a caching proxy over data that must be fresh, and write the proxy explicitly where a forwarding one would do.

<blockquote class="ai-sidebar" markdown="1">
**Specifying wrappers and proxies.** "A decorator" leaves open whether the behaviour is a stack chosen per consignment or a function rebound at definition, which one is called "Decorator", and which wrapper sits outside. Paste a prompt that states the form:

> For price adjustments, write frozen layers that hold a `RateCalculator` and satisfy the same Protocol, composed per consignment by `layers_for`, with fixed fees inside the tax layer. For call behaviour, write `@` factories with `functools.wraps` and a `ParamSpec`, `@audited` above `@retry`. Write the proxy as a class that defines every member of `CarrierGateway`, with no `__getattr__` forwarding. Say "Decorator" only for the layer stack.

If the proxy forwards through `__getattr__`, ask what mypy reports for a typo.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/20-decorator-pattern-vs-decorator-syntax-and-proxy
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
collecting ... collected 50 items

tests/test_layers.py::test_a_layer_wraps_a_calculator_and_leaves_it_unchanged PASSED [  2%]
tests/test_layers.py::test_layer_order_changes_the_price_when_a_fee_is_added[tax-outside] PASSED [  4%]
tests/test_layers.py::test_layer_order_changes_the_price_when_a_fee_is_added[surcharge-outside] PASSED [  6%]
tests/test_layers.py::test_layer_order_changes_the_price_when_a_fee_is_added[discount-outside] PASSED [  8%]
tests/test_layers.py::test_layer_order_changes_the_price_when_a_fee_is_added[surcharge-outside-discount] PASSED [ 10%]
tests/test_layers.py::test_two_percentage_layers_agree_before_rounding_and_can_split_by_a_cent PASSED [ 12%]
tests/test_layers.py::test_the_layers_for_a_consignment_are_chosen_while_the_program_runs[light] PASSED [ 14%]
tests/test_layers.py::test_the_layers_for_a_consignment_are_chosen_while_the_program_runs[heavy] PASSED [ 16%]
tests/test_layers.py::test_the_layers_for_a_consignment_are_chosen_while_the_program_runs[dangerous-goods] PASSED [ 18%]
tests/test_layers.py::test_the_heavy_threshold_is_exclusive PASSED       [ 20%]
tests/test_layers.py::test_the_fees_are_in_the_order_the_rules_say PASSED [ 22%]
tests/test_layers.py::test_an_unknown_destination_country_is_a_rating_error PASSED [ 24%]
tests/test_layers.py::test_layer_stacks_compare_by_value PASSED          [ 26%]
tests/test_layers.py::test_compose_wraps_the_last_layer_outermost PASSED [ 28%]
tests/test_layers.py::test_a_layer_refuses_a_fee_in_another_currency PASSED [ 30%]
tests/test_layers.py::test_a_weight_that_is_not_positive_and_finite_is_refused[zero] PASSED [ 32%]
tests/test_layers.py::test_a_weight_that_is_not_positive_and_finite_is_refused[negative] PASSED [ 34%]
tests/test_layers.py::test_a_weight_that_is_not_positive_and_finite_is_refused[nan] PASSED [ 36%]
tests/test_layers.py::test_the_tax_rates_are_read_only PASSED            [ 38%]
tests/test_proxy.py::test_the_proxy_asks_the_gateway_once_per_consignment[explicit] PASSED [ 40%]
tests/test_proxy.py::test_the_proxy_asks_the_gateway_once_per_consignment[forwarding] PASSED [ 42%]
tests/test_proxy.py::test_the_proxy_forwards_every_booking[explicit] PASSED [ 44%]
tests/test_proxy.py::test_the_proxy_forwards_every_booking[forwarding] PASSED [ 46%]
tests/test_proxy.py::test_a_timed_out_quote_is_not_cached[explicit] PASSED [ 48%]
tests/test_proxy.py::test_a_timed_out_quote_is_not_cached[forwarding] PASSED [ 50%]
tests/test_proxy.py::test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price PASSED [ 52%]
tests/test_proxy.py::test_runtime_checkable_does_not_see_attributes_forwarded_by_getattr PASSED [ 54%]
tests/test_proxy.py::test_a_forwarded_typo_is_reported_against_the_wrapped_gateway PASSED [ 56%]
tests/test_static.py::test_mypy_rejects_a_decorated_function_where_a_calculator_belongs PASSED [ 58%]
tests/test_static.py::test_mypy_checks_each_layer_in_a_stack[missing-price] PASSED [ 60%]
tests/test_static.py::test_mypy_checks_each_layer_in_a_stack[wrong-keyword] PASSED [ 62%]
tests/test_static.py::test_mypy_keeps_the_call_signature_through_retry[arg-type] PASSED [ 64%]
tests/test_static.py::test_mypy_keeps_the_call_signature_through_retry[call-arg] PASSED [ 66%]
tests/test_static.py::test_mypy_accepts_the_explicit_proxy_as_a_gateway PASSED [ 68%]
tests/test_static.py::test_mypy_reports_a_typo_on_the_explicit_proxy PASSED [ 70%]
tests/test_static.py::test_mypy_reports_a_member_missing_from_an_explicit_proxy PASSED [ 72%]
tests/test_static.py::test_mypy_accepts_a_typo_through_a_forwarding_proxy[any-typo] PASSED [ 74%]
tests/test_static.py::test_mypy_accepts_a_typo_through_a_forwarding_proxy[any-wrong-type] PASSED [ 76%]
tests/test_static.py::test_mypy_rejects_a_forwarding_proxy_that_returns_object PASSED [ 78%]
tests/test_syntax.py::test_the_at_sign_rebinds_the_name_once_at_definition_time PASSED [ 80%]
tests/test_syntax.py::test_retry_calls_again_on_a_listed_error_and_gives_up_after_the_last_attempt PASSED [ 82%]
tests/test_syntax.py::test_retry_lets_an_unlisted_error_through PASSED   [ 84%]
tests/test_syntax.py::test_retry_refuses_fewer_than_one_attempt[0] PASSED [ 86%]
tests/test_syntax.py::test_retry_refuses_fewer_than_one_attempt[-1] PASSED [ 88%]
tests/test_syntax.py::test_audited_reports_each_call_to_the_injected_sink PASSED [ 90%]
tests/test_syntax.py::test_syntax_stacking_order_decides_whether_each_attempt_is_audited[audit-outside-1] PASSED [ 92%]
tests/test_syntax.py::test_syntax_stacking_order_decides_whether_each_attempt_is_audited[retry-outside-3] PASSED [ 94%]
tests/test_syntax.py::test_rebound_functions_do_not_compare_by_value PASSED [ 96%]
tests/test_syntax.py::test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped PASSED [ 98%]
tests/test_syntax.py::test_a_decorator_may_return_an_object_that_is_not_a_function PASSED [100%]

============================== 50 passed in 5.04s ==============================
Success: no issues found in 10 source files
```

The suite has 35 test functions and 50 cases. The tests for the three halves are in `test_layers.py`, `test_syntax.py` and `test_proxy.py`, with the type-checker witnesses in `test_static.py`. For how the tests and the mypy witnesses are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

**Experiment one: tax before the fees.** In a fresh scratch copy, move the `country = ...` line and its `try` block in `layers_for` to just after `layers: list[Layer] = []`, so the tax layer is added first. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))'` and then `uv run mypy --strict src tests` gives:

```text
E       AssertionError: assert '886.20' == '889.35'
tests/test_layers.py:107: AssertionError
E       AssertionError: assert '39.52' == '44.77'
tests/test_layers.py:107: AssertionError
E       AssertionError: assert False
tests/test_layers.py:131: AssertionError
FAILED tests/test_layers.py::test_the_layers_for_a_consignment_are_chosen_while_the_program_runs[heavy]
FAILED tests/test_layers.py::test_the_layers_for_a_consignment_are_chosen_while_the_program_runs[dangerous-goods]
FAILED tests/test_layers.py::test_the_fees_are_in_the_order_the_rules_say - A...
3 failed, 47 passed in 5.46s
Success: no issues found in 10 source files
```

The heavy consignment is 3.15 short, and the dangerous-goods one is 5.25 short. The third failure is the test that reads the stack's shape. mypy stays green, because a tax layer under a fee layer is a well-typed stack. Nothing in a type says which layer goes outside.

**Experiment two: delete `book` from the proxy.** In a fresh scratch copy, delete the `book` method from `CarrierGatewayProxy`. The same filtered run, then mypy, gives:

```text
E       AttributeError: 'CarrierGatewayProxy' object has no attribute 'book'
tests/test_proxy.py:39: AttributeError
E       assert False
tests/test_proxy.py:84: AssertionError
E       assert 1 == 0
tests/test_static.py:236: AssertionError
FAILED tests/test_proxy.py::test_the_proxy_forwards_every_booking[explicit]
FAILED tests/test_proxy.py::test_runtime_checkable_does_not_see_attributes_forwarded_by_getattr
FAILED tests/test_static.py::test_mypy_accepts_the_explicit_proxy_as_a_gateway
3 failed, 47 passed in 5.38s
tests/conftest.py:86: error: Incompatible return value type (got "type[CarrierGatewayProxy]", expected "Callable[[CarrierGateway], CarrierGateway]")  [return-value]
tests/conftest.py:92: error: Incompatible return value type (got "CarrierGatewayProxy", expected "CarrierGateway")  [return-value]
tests/conftest.py:92: note: "CarrierGatewayProxy" is missing following "CarrierGateway" protocol member:
tests/conftest.py:92: note:     book
Found 2 errors in 1 file (checked 10 source files)
```

The explicit proxy fails at run time with `AttributeError`, and `test_the_proxy_forwards_every_booking[forwarding]` still passes, because the forwarding form hands the missing call to the gateway. mypy reports the missing member wherever the proxy is typed as a `CarrierGateway`, here in the fixtures. The other two failures are the runtime check on the explicit proxy and the witness that expects a clean assignment.

## What you can do now

- Say which mechanism "decorator" names: a layer stack built while the program runs, or a name rebound at definition, the mismatch PEP 318 records.
- Build a stack of layers as a value: `layers_for` chooses it, `compose(base, layers)` wraps it, and the fee-order and rounding tests show which orders matter.
- Say what a proxy keeps and changes: `CarrierGatewayProxy` returns the gateway's quote where `Tax` changes the price, and the explicit-proxy mypy report names the missing `book`.
- Name the four costs of a `__getattr__` forwarding proxy: accepted typos, an `object` return, `runtime_checkable` and the wrong class in the error.

## For deeper coverage

*Design Patterns* (Gamma, Helm, Johnson and Vlissides) is the source for Decorator and Proxy. Brandon Rhodes's [The Decorator Pattern](https://python-patterns.guide/gang-of-four/decorator-pattern/) separates the pattern from the syntax. [PEP 318](https://peps.python.org/pep-0318/) introduced the `@` form and [PEP 3129](https://peps.python.org/pep-3129/) extended it to classes. [PEP 612](https://peps.python.org/pep-0612/) specifies `ParamSpec` and [PEP 695](https://peps.python.org/pep-0695/) the generic syntax the factories use. The [`typing` documentation](https://docs.python.org/3.15/library/typing.html) covers `runtime_checkable`, the [`inspect` documentation](https://docs.python.org/3.15/library/inspect.html) covers `getattr_static`, and the [data model reference](https://docs.python.org/3.15/reference/datamodel.html) covers `__getattr__` and special method lookup. Luciano Ramalho's *Fluent Python* and Brett Slatkin's *Effective Python* treat the `@decorator` syntax and closures in depth. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
