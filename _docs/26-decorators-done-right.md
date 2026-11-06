---
title: "Decorators done right"
order: 26
layout: tutorial
sectionid: docs
part: "idiomatic-python"
description: "The @ syntax is given, but getting a decorator right isn't: what wraps copies, what ParamSpec keeps for mypy, bare use of a factory, stacking order and class decorators."
---

## Learning objectives

By the end of this chapter you can:

- Keep a decorated function's name, docstring and signature for runtime tools with `functools.wraps`, and say what it copies and where it misleads.
- Type a decorator for mypy with `ParamSpec`, including one that supplies an argument with `Concatenate`.
- Write a decorator factory that refuses bare use when the module loads.
- Build a cache with an injected clock and choose where a timer sits in the stack.
- Place a class decorator above `@dataclass(slots=True)`, and decorate a method without keeping its instances alive.

## Why this matters

A booking portal renders bills of lading, caches each rendering for five minutes and times the work. Each of those is a decorator over one function, `render_bill`. The `@` that applies them is the language's part: it rebinds a name when the function is defined. What stays design is the discipline around it, so the bucket is survives, as [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) sorts it. Three things go wrong in the obvious versions.

A renderer reports itself as `wrapper` and has no docstring, so a log line or a help page names a function nobody wrote.

A cache factory takes its window as a positional argument and never checks it, and someone writes `@cached_for` with no call. Nothing fails. The name is bound to the factory's inner function, and calling it returns a function where text was expected.

A document class is registered by a decorator and then wrapped by `@dataclass(slots=True)` above it. The registry holds a class that the code never uses.

Each one is a rule about how decorators compose, and each has a test.

{% include excalidraw.html name="26-decorators-done-right" caption="Figure 26.1: The order of a stack decides whether a timer sees a cache hit. functools.wraps keeps a renderer's identity for runtime tools, ParamSpec keeps its signature for mypy, and a class decorator belongs above a slotted dataclass." %}

Read the figure from the top down. `render_bill`, "the function both stacks wrap", has an arrow to each stack. On the left `timed_render` is outer and `cached_for` inner, with the note "timer outside: every call timed" beneath. On the right `cached_for` is outer and `timed_render` inner, with "timer inside: only misses timed" beneath. Lower down, `functools.wraps` ("copies name, doc, dict; adds __wrapped__") leads to `inspect.signature` ("follows __wrapped__"), and `ParamSpec` ("keeps the signature") leads to `mypy` ("sees the original parameters"). Between them a dashed, muted box reads "a decorator that supplies an argument: the signature misleads; use partial". At the bottom `document_kind` ("above: registers the class the name holds") leads to `dataclass(slots=True)` ("returns a new class").

## What wraps copies

A decorator replaces a function with another one, and everything that reads the function afterwards reads the replacement: a log line, a help page, a debugger, a signature check. `functools.wraps` makes the replacement look like the original. The rebinding itself, and the factories that sit around it, are in [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}).

```python
def timed_render[**P, R](
    sink: TimingSink, *, clock: Clock = time.perf_counter
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Report the function's name and the elapsed clock time to ``sink`` after every call."""

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started = clock()
            try:
                return func(*args, **kwargs)
            finally:
                sink(func.__name__, clock() - started)

        return wrapper

    return decorate
```

`wraps` applies `functools.update_wrapper`, which the [functools documentation](https://docs.python.org/3/library/functools.html) sums up as "Update a wrapper function to look like the wrapped function." The same page says the function "automatically adds a __wrapped__ attribute to the wrapper that refers to the function being wrapped".

The comparison is a fixture, `wrapper_form`, with two parameters: `timed_render` and a copy of the same timer with `wraps` left out. Both render the same text for two bills (`test_both_wrapper_forms_render_the_same_text`), so the difference is only in what a tool reads off them. With `wraps` the wrapper keeps the name, qualified name, docstring and module (`test_wraps_keeps_the_name_qualname_doc_and_module`). Without it the name is `wrapper`, the qualified name ends in `<locals>.wrapper`, the docstring is `None` and there's no `__wrapped__` (`test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring`).

Attributes set on the function travel too. `wraps` copies the function's `__dict__` into the wrapper's and adds `__wrapped__` beside them (`test_wraps_copies_the_function_dict_and_adds_wrapped`). `__wrapped__` points one level down: with a timer over a cache over `render_bill`, the timer's `__wrapped__` is the cache wrapper, and the cache wrapper's is `render_bill`. The [inspect documentation](https://docs.python.org/3/library/inspect.html) describes `inspect.unwrap` as one that "follows the chain of __wrapped__ attributes returning the last object in the chain", and `test_wrapped_points_one_level_down_and_unwrap_reaches_the_original` checks both steps.

`inspect.signature` follows `__wrapped__` as well, so the wrapped renderer reports `(bill: decorators_done_right.domain.BillOfLading, /, *, width: int = 72) -> str`, and the bare one reports `(*args: P.args, **kwargs: P.kwargs) -> R` (`test_inspect_signature_follows_wrapped_to_the_original_parameters`).

One attribute changed under it. PEP 749, by Jelle Zijlstra, says: "functools.update_wrapper() (and therefore functools.wraps()) will copy only the __annotate__ attribute from the wrapped object to the wrapper." That holds since Python 3.14, when annotations became evaluated on demand. On 3.15.2 `functools.WRAPPER_ASSIGNMENTS` contains `__annotate__` and not `__annotations__`, and the wrapper's `__annotations__` still equals the original's (`test_wraps_copies_annotate_rather_than_annotations`). The functools page for 3.15.2 still lists `__annotations__` among the attributes it assigns, so the constant is the one to read.

## What mypy reads

mypy doesn't read `__wrapped__`. It reads the wrapper's declared type, and `ParamSpec` is what carries the wrapped function's parameters through that type. [PEP 612](https://peps.python.org/pep-0612/), by Mark Mendoza, says: "This PEP proposes typing.ParamSpec and typing.Concatenate to support expressing these kinds of relationships." The two tools therefore read different things: `wraps` serves runtime tools, `ParamSpec` serves mypy, and a wrapper can have either without the other.

Two reduced models, snippets inside the tests that stand for code and aren't part of the example, show the split. A `ParamSpec` timer with no `wraps` still lets mypy see `render_bill(bill, /, *, width: int = 72)`: calling it with `width="30"` is `[arg-type]`, `Argument "width" to "render_bill" has incompatible type "str"; expected "int"` (`test_mypy_keeps_the_signature_through_a_wrapper_without_wraps`). The same timer with no annotations erases the signature instead, and mypy reports `[untyped-decorator]`, `Untyped decorator makes function "render_bill" untyped`, together with `[no-untyped-def]` on the decorator (`test_mypy_reports_an_untyped_decorator`).

`Concatenate` is for a decorator that supplies an argument. The [typing documentation](https://docs.python.org/3/library/typing.html) says it "can be used in conjunction with Callable and ParamSpec to annotate a higher-order callable which adds, removes, or transforms parameters of another callable". A reduced model takes a function `render(width, bill, /)` and supplies `width`. mypy sees the decorated function as taking the bill alone, and a call that repeats the width is refused with `[call-arg]` and `[arg-type]` (`test_mypy_types_a_decorator_that_supplies_an_argument`).

Runtime tools disagree, and here `wraps` is the cause. A test-local decorator, `supplying`, fixes the clock argument of `issued_at(clock, number)` and uses `wraps`. `stamp("BL-1")` returns `BL-1 issued at 1000`, yet `inspect.signature(stamp)` lists `clock` and `number`, and `signature.bind("BL-1")` raises `TypeError` with "missing a required argument" (`test_a_decorator_that_supplies_an_argument_reports_the_original_parameters`). `functools.partial(issued_at, clock)` reports `number` alone, and its `bind` accepts the call (`test_partial_reports_the_parameters_that_remain`). `wraps` assumes the wrapper takes the wrapped function's arguments; when it supplies one, use `partial`.

## Factories that refuse to be used bare

A decorator with parameters is a function that returns a decorator, so `@cached_for(seconds=300)` has a call after the name. The [compound statements reference](https://docs.python.org/3/reference/compound_stmts.html) says "Decorator expressions are evaluated when the function is defined, in the scope that contains the function definition." The call runs at definition, and so does any mistake in it. The comparison is a fixture in `tests/conftest.py`, a factory that takes its window positionally:

```python
def _cached_for_positional[**P, R](
    seconds: float,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """The comparison: the window is a positional argument, so a bare ``@`` use is not refused."""

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)

        return wrapper

    return decorate
```

Used bare, as `@positional_factory` with no call, it fails without an error:

<!-- fmt:off -->
```python
    @positional_factory  # type: ignore[arg-type]
    def render(bill: BillOfLading, /) -> str:
        return render_bill(bill)

    result = render(bill)  # type: ignore[arg-type]

    assert render.__name__ == "decorate"
    assert callable(result)
    assert not isinstance(result, str)
    assert result.__name__ == "wrapper"
```
<!-- fmt:on -->

`render` is now the factory's inner `decorate`, and calling it with a bill returns the wrapper (`test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator`). mypy refuses the bare use on a reduced model (`[arg-type]`, `test_mypy_refuses_a_positional_factory_used_bare`), but only where mypy runs.

The factory in the example puts a `*` before `seconds`. Bare `@cached_for` then raises `TypeError` with "takes 0 positional arguments" when the module loads (`test_a_keyword_only_factory_used_bare_fails_at_definition`), and mypy reports `[call-arg]` and `[arg-type]` (`test_mypy_refuses_a_keyword_only_factory_used_bare`). Without the `*` the bare use still fails at the `def`, as experiment two shows, but only because the window check compares a function with `0`.

## A cache with a clock, and the order of the stack

A cache over rendered text has to expire, and a test can't wait for it to. `cached_for` takes the clock as an argument, so a test advances time by hand. The `[**P, R]` after the name is the type-parameter syntax of PEP 695, by Eric Traut, with `ParamSpec` from PEP 612.

```python
def cached_for[**P, R](
    *, seconds: float, clock: Clock = time.monotonic
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Serve a result again for ``seconds`` of clock time, one entry per distinct arguments.

    Single-threaded, and every argument must be hashable.
    """
    if seconds <= 0:
        raise ValueError(f"seconds must be positive, got {seconds}")

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        entries: dict[Hashable, tuple[float, R]] = {}

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = (args, frozenset(kwargs.items()))
            now = clock()
            entry = entries.get(key)
            if entry is not None and now - entry[0] < seconds:
                return entry[1]
            result = func(*args, **kwargs)
            entries[key] = (now, result)
            return result

        return wrapper

    return decorate
```

Two calls inside the window render once (`test_cached_for_returns_the_cached_text_within_the_window`). The entry is stamped when the call starts, so the render's own two seconds of clock time count against the window: a call exactly one window later, and one past it, render again (`test_cached_for_renders_again_once_the_window_has_passed`). Each distinct argument has its own entry, including a keyword argument such as `width=30` (`test_cached_for_keeps_one_entry_per_argument`). A list passed positionally fails with `TypeError` and the message "cannot use 'tuple' as a dict key (unhashable type: 'list')" on 3.15.2 (`test_cached_for_refuses_an_unhashable_argument`). A window of zero or less is a `ValueError` (`test_cached_for_refuses_a_window_that_is_not_positive`). The cache is single-threaded, as its docstring says. `timed_render` reports the elapsed clock time, `2.0` in the tests, whether the render returns or raises (`test_timed_render_reports_the_elapsed_clock_time`).

Stacking decides what the timer sees. The compound statements reference says "Multiple decorators are applied in nested fashion", and its example reads `@f1(arg)` over `@f2` as `f1(arg)(f2(func))`: the decorator nearest the `def` applies first. These two orders are written as calls in the test:

<!-- fmt:off -->
```python
    stacked = timer(cache(render)) if timer_outside else cache(timer(render))
```
<!-- fmt:on -->

Called twice with the same bill, both orders render once. With the timer outside, the sink receives `("render", 2.0)` and then `("render", 0.0)`, the hit counted as a call that took no clock time. With the timer inside, it receives only `("render", 2.0)`, because a hit never reaches it (`test_stacking_order_decides_whether_a_cache_hit_is_timed`). The inside order measures the renderer. The outside order measures what the caller waited, hits included. A dashboard of renderer cost wants the timer inside, and one of response time wants it outside.

## Class decorators

A registry of document classes shouldn't depend on someone remembering to call `register(BillOfLading)`. `document_kind` is a class decorator that registers at definition:

```python
def document_kind[C: type](
    kind: DocumentKind, *, registry: dict[DocumentKind, type] = DOCUMENT_TYPES
) -> Callable[[C], C]:
    """Register the decorated class for ``kind`` and return it unchanged.

    Put it above ``@dataclass(slots=True)``: that decorator returns a new class, and a
    decorator beneath it would register the class that is thrown away.
    """

    def register(cls: C) -> C:
        if kind in registry:
            raise DocumentKindError(
                f"{kind.name} is already registered to {registry[kind].__qualname__}"
            )
        registry[kind] = cls
        return cls

    return register


@document_kind(DocumentKind.BILL_OF_LADING)
@dataclass(frozen=True, slots=True)
class BillOfLading:
    number: str
    consignment_id: ConsignmentId
    port_of_loading: str
    port_of_discharge: str
```

Importing the module fills `DOCUMENT_TYPES` with `BillOfLading` and `Manifest` (`test_document_kind_registers_the_class_at_definition`), and a second class for the same kind raises `DocumentKindError` (`test_document_kind_refuses_a_second_class_for_a_kind`). The signature says the class comes back unchanged. mypy doesn't apply a class decorator's return type, though: a decorated class keeps its own type whatever the decorator declares, so `BillOfLading.number` is a `str` either way (`test_mypy_keeps_the_class_type_through_document_kind`, beside a reduced model declared to return `int`). The mechanism is [PEP 3129](https://peps.python.org/pep-3129/), by Collin Winter, which extended the `@` form to classes.

The order against `@dataclass(slots=True)` matters. The [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) says of `slots`: "If true (the default is False), __slots__ attribute will be generated and new class will be returned instead of the original one." `test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class` puts `document_kind` beneath it on a class `Beneath`: the registry holds a class without `__slots__`, and the name holds the slotted one. Put above, as on `BillOfLading` and `Manifest`, `document_kind` registers the class the name ends up holding, and the same test checks that order too.

A class decorator that doesn't return the class binds the name to `None`. A test-local one that registers and falls off the end leaves `Forgotten` as `None` (`test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none`), and a reduced model shows mypy reporting `[return]`, `Missing return statement` (`test_mypy_reports_a_class_decorator_that_forgets_to_return`). Registering classes by other means is the business of [Metaclasses, __init_subclass__, and registries]({{ '/docs/29-metaclasses-init-subclass-and-registries/' | relative_url }}).

## Decorating methods

A function wrapper works on a method unchanged. The [descriptor guide](https://docs.python.org/3/howto/descriptor.html) says "To support automatic creation of methods, functions include the __get__() method for binding methods during attribute access." The wrapper `timed_render` returns is a function, so `Renderer().render("BL-1")` binds `self` and the timer records the call (`test_a_function_wrapper_binds_self_on_a_method`). A class-based wrapper with `__call__` and no `__get__` has nothing to bind with: the instance is never passed, `"BL-1"` fills `self`, and the call fails with "missing 1 required positional argument" (`test_a_class_based_wrapper_does_not_bind_self`). Writing `__get__` and `cached_property` belong to [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}).

`functools.cache` on a method has a different cost. The functools page says "If a method is cached, the self instance argument is included in the cache." The [programming FAQ](https://docs.python.org/3/faq/programming.html) puts the consequence this way: "The disadvantage is that instances are kept alive until they age out of the cache or until the cache is cleared". In the test a `weakref` to the instance still resolves after `del` and `gc.collect()`, and stops resolving after `Renderer.render.cache_clear()` (`test_functools_cache_on_a_method_keeps_the_instance_alive`). Ruff's [B019 rule](https://docs.astral.sh/ruff/rules/cached-instance-method/) flags it: "Using the functools.lru_cache and functools.cache decorators on methods can lead to memory leaks, as the global cache will retain a reference to the instance, preventing it from being garbage collected." The repository's ruff configuration selects `B`, so the test carries `# noqa: B019`.

## When not to use it

When behaviour has to vary per object while the program runs, a decorator can't help, because it fixes the wrapping when the function is defined; wrapper objects that share an interface, composed at run time, can. Where a decorator would supply an argument, `functools.partial` reports the signature that's left. A cache over data that must be fresh serves the wrong answer for a window, and one over unhashable arguments raises. And a registry that nobody reads is a dictionary to keep in step.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a decorator.** "A caching decorator" doesn't say how the wrapper keeps its identity, how the window is passed or where the timer sits, so the reply decides each one for you. State them in the prompt:

> Write `cached_for` as a PEP 695 `[**P, R]` factory with keyword-only `seconds` and an injected `clock`, its wrapper decorated with `functools.wraps(func)` and typed `Callable[P, R]`. Put `timed_render` inside the cache so only misses are timed. Where a decorator would supply an argument, use `functools.partial`. Put `document_kind` above `@dataclass(slots=True)`, and never put `functools.cache` on a method.

If the reply drops `wraps` or the `*`, ask for the test that fails.
</blockquote>

## Build, run, observe

The run shows each rule failing in the form that breaks it and passing in the form that keeps it: the wrapper with and without `wraps` on one rendering table, the factory used bare in both forms, and both stacking orders against one clock. From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/26-decorators-done-right
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
collecting ... collected 40 items

tests/test_classes.py::test_document_kind_registers_the_class_at_definition PASSED [  2%]
tests/test_classes.py::test_document_kind_refuses_a_second_class_for_a_kind PASSED [  5%]
tests/test_classes.py::test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class PASSED [  7%]
tests/test_classes.py::test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none PASSED [ 10%]
tests/test_factories.py::test_cached_for_returns_the_cached_text_within_the_window PASSED [ 12%]
tests/test_factories.py::test_cached_for_renders_again_once_the_window_has_passed[at-the-limit] PASSED [ 15%]
tests/test_factories.py::test_cached_for_renders_again_once_the_window_has_passed[past-it] PASSED [ 17%]
tests/test_factories.py::test_cached_for_keeps_one_entry_per_argument PASSED [ 20%]
tests/test_factories.py::test_cached_for_refuses_an_unhashable_argument PASSED [ 22%]
tests/test_factories.py::test_cached_for_refuses_a_window_that_is_not_positive[zero] PASSED [ 25%]
tests/test_factories.py::test_cached_for_refuses_a_window_that_is_not_positive[negative] PASSED [ 27%]
tests/test_factories.py::test_timed_render_reports_the_elapsed_clock_time[rendered] PASSED [ 30%]
tests/test_factories.py::test_timed_render_reports_the_elapsed_clock_time[raised] PASSED [ 32%]
tests/test_factories.py::test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator PASSED [ 35%]
tests/test_factories.py::test_a_keyword_only_factory_used_bare_fails_at_definition PASSED [ 37%]
tests/test_factories.py::test_stacking_order_decides_whether_a_cache_hit_is_timed[timer-outside-2] PASSED [ 40%]
tests/test_factories.py::test_stacking_order_decides_whether_a_cache_hit_is_timed[timer-inside-1] PASSED [ 42%]
tests/test_methods.py::test_a_function_wrapper_binds_self_on_a_method PASSED [ 45%]
tests/test_methods.py::test_a_class_based_wrapper_does_not_bind_self PASSED [ 47%]
tests/test_methods.py::test_functools_cache_on_a_method_keeps_the_instance_alive PASSED [ 50%]
tests/test_static.py::test_mypy_keeps_the_signature_through_a_wrapper_without_wraps PASSED [ 52%]
tests/test_static.py::test_mypy_reports_an_untyped_decorator PASSED      [ 55%]
tests/test_static.py::test_mypy_refuses_a_positional_factory_used_bare PASSED [ 57%]
tests/test_static.py::test_mypy_refuses_a_keyword_only_factory_used_bare PASSED [ 60%]
tests/test_static.py::test_mypy_types_a_decorator_that_supplies_an_argument PASSED [ 62%]
tests/test_static.py::test_mypy_reports_a_class_decorator_that_forgets_to_return PASSED [ 65%]
tests/test_static.py::test_mypy_keeps_the_class_type_through_document_kind PASSED [ 67%]
tests/test_wraps.py::test_both_wrapper_forms_render_the_same_text[wraps-first-bill] PASSED [ 70%]
tests/test_wraps.py::test_both_wrapper_forms_render_the_same_text[wraps-second-bill] PASSED [ 72%]
tests/test_wraps.py::test_both_wrapper_forms_render_the_same_text[bare-first-bill] PASSED [ 75%]
tests/test_wraps.py::test_both_wrapper_forms_render_the_same_text[bare-second-bill] PASSED [ 77%]
tests/test_wraps.py::test_render_bill_shortens_the_line_to_the_width PASSED [ 80%]
tests/test_wraps.py::test_wraps_keeps_the_name_qualname_doc_and_module PASSED [ 82%]
tests/test_wraps.py::test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring PASSED [ 85%]
tests/test_wraps.py::test_inspect_signature_follows_wrapped_to_the_original_parameters PASSED [ 87%]
tests/test_wraps.py::test_wraps_copies_the_function_dict_and_adds_wrapped PASSED [ 90%]
tests/test_wraps.py::test_wrapped_points_one_level_down_and_unwrap_reaches_the_original PASSED [ 92%]
tests/test_wraps.py::test_wraps_copies_annotate_rather_than_annotations PASSED [ 95%]
tests/test_wraps.py::test_a_decorator_that_supplies_an_argument_reports_the_original_parameters PASSED [ 97%]
tests/test_wraps.py::test_partial_reports_the_parameters_that_remain PASSED [100%]

============================== 40 passed in 3.24s ==============================
Success: no issues found in 9 source files
```

The suite has 33 test functions and 40 cases. For how the mypy tests are built, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

- `tests/test_wraps.py` holds the `wrapper_form` table and the metadata tests. They show that `wraps` is what a runtime tool reads, and that it misleads when the wrapper supplies an argument.
- `tests/test_factories.py` holds the cache, the timer, the two bare-use tests and the stacking test, on a fake clock that no test waits for.
- `tests/test_classes.py` and `tests/test_methods.py` hold the registration, the order against the dataclass, and the two ways a method is wrapped.
- `tests/test_static.py` holds the mypy witnesses: the reduced models and the two that import the example.

**Experiment one: remove `wraps` from the timer.** In a fresh scratch copy, delete the `@wraps(func)` line from `timed_render`'s wrapper. Running `uv run pytest -q 2>&1 | grep -E '^(FAILED|E {7}[^ ]|tests/.*Error$|[0-9]+ (passed|failed))' | sed -E 's/[0-9a-f]{12}>/ADDR>/g'` and then `uv run mypy --strict src tests` prints:

```text
E       AssertionError: assert 'wrapper' == 'render_bill'
tests/test_wraps.py:50: AssertionError
E       AssertionError: assert '(*args: P.ar....kwargs) -> R' == '(bill: decor... = 72) -> str'
tests/test_wraps.py:72: AssertionError
E       AssertionError: assert {} == {'kind': 'BIL...ADDR>}
tests/test_wraps.py:85: AssertionError
E       AttributeError: 'function' object has no attribute '__wrapped__'
tests/test_wraps.py:94: AttributeError
E       AssertionError: assert {'args': P.ar..., 'return': R} == {'bill': <cla...<class 'str'>}
tests/test_wraps.py:106: AssertionError
FAILED tests/test_wraps.py::test_wraps_keeps_the_name_qualname_doc_and_module
FAILED tests/test_wraps.py::test_inspect_signature_follows_wrapped_to_the_original_parameters
FAILED tests/test_wraps.py::test_wraps_copies_the_function_dict_and_adds_wrapped
FAILED tests/test_wraps.py::test_wrapped_points_one_level_down_and_unwrap_reaches_the_original
FAILED tests/test_wraps.py::test_wraps_copies_annotate_rather_than_annotations
5 failed, 35 passed in 3.23s
Success: no issues found in 9 source files
```

The sed masks an object address the pytest message carries. Five metadata tests fail: the name, the signature, the copied dictionary, `__wrapped__` and the annotations. The table that compares rendered text still passes, because the timer returns the same string, and mypy exits 0, because `ParamSpec` still carries the signature.

**Experiment two: make `seconds` positional.** In a fresh scratch copy, delete the `*,` from `cached_for`'s parameters. The same filter, then mypy, prints:

```text
E       AssertionError: Regex pattern did not match.
tests/test_factories.py:121: AssertionError
E       AssertionError: assert {'arg-type'} == {'arg-type', 'call-arg'}
tests/test_static.py:185: AssertionError
FAILED tests/test_factories.py::test_a_keyword_only_factory_used_bare_fails_at_definition
FAILED tests/test_static.py::test_mypy_refuses_a_keyword_only_factory_used_bare
2 failed, 38 passed in 3.16s
tests/test_factories.py:123: error: Unused "type: ignore[call-arg]" comment  [unused-ignore]
Found 1 error in 1 file (checked 9 source files)
```

The bare `@cached_for` no longer fails at the `def`. It reaches `if seconds <= 0` with a function in place of a number, and the pytest report gives the actual message as "'<=' not supported between instances of 'function' and 'int'", which doesn't match "takes 0 positional arguments". mypy now reports only `[arg-type]`, so the code set changes, and the `# type: ignore[call-arg, arg-type]` on the decorator is half unused: member mypy exits 1 with `[unused-ignore]`.

## What you can do now

- Keep identity and signature: `timed_render` with `functools.wraps`, and the `wrapper_form` table where `test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring` shows what the bare form loses and experiment one shows the five tests that notice.
- Type a decorator for mypy: `ParamSpec` in `timed_render`, and `Concatenate` for one that supplies an argument, where `test_a_decorator_that_supplies_an_argument_reports_the_original_parameters` shows `wraps` misleading `inspect.signature` and `functools.partial` as the answer.
- Refuse bare use: the keyword-only `cached_for`, witnessed by `test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator` for the silent form and `test_a_keyword_only_factory_used_bare_fails_at_definition` for the refusal.
- Build and stack a cache: `cached_for` on an injected clock, with `test_stacking_order_decides_whether_a_cache_hit_is_timed` showing what a timer outside and inside each record.
- Place a class decorator and wrap a method: `document_kind` above `@dataclass(slots=True)`, witnessed by `test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class`, and no `functools.cache` on a method, as `test_functools_cache_on_a_method_keeps_the_instance_alive` shows.

## For deeper coverage

[PEP 318](https://peps.python.org/pep-0318/), by Kevin D. Smith, Jim J. Jewett, Skip Montanaro and Anthony Baxter, introduced decorators for functions and methods, and [PEP 3129](https://peps.python.org/pep-3129/) extended them to classes. [PEP 612](https://peps.python.org/pep-0612/) specifies `ParamSpec` and `Concatenate`, [PEP 695](https://peps.python.org/pep-0695/) the type-parameter syntax the factories use, and [PEP 749](https://peps.python.org/pep-0749/) the `__annotate__` change. The [functools](https://docs.python.org/3/library/functools.html), [inspect](https://docs.python.org/3/library/inspect.html), [typing](https://docs.python.org/3/library/typing.html) and [dataclasses](https://docs.python.org/3/library/dataclasses.html) documentation cover the functions used here, the [compound statements reference](https://docs.python.org/3/reference/compound_stmts.html) covers decorator evaluation, and the [descriptor guide](https://docs.python.org/3/howto/descriptor.html) covers why functions bind. The [programming FAQ](https://docs.python.org/3/faq/programming.html) and ruff's [B019 page](https://docs.astral.sh/ruff/rules/cached-instance-method/) cover caching methods. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books, and the hub carries the same list.
