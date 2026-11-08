# Decorators done right

The `@` syntax rebinds a name when a function or class is defined, and that part is the language's.
Doing it right is the design that survives: what `functools.wraps` copies and what it gets wrong,
what `ParamSpec` keeps for mypy, a factory that refuses to be used bare, the order of a stack, a
class decorator placed above `@dataclass(slots=True)`, and decorated methods. The example decorates
the Documentation renderers: `render_bill`, a timer, a cache and a registry of document classes.
Port codes, consignment ids and numbers are illustrative.

## What it witnesses

Identity and signature.

- `render_bill(bill, /, *, width=72)` renders a `BillOfLading` as one line.
  `timed_render(sink, clock=...)` reports the function's name and the elapsed clock time to a
  `TimingSink`, also when the function raises.
- `wrapper_form` is `wraps` or `bare`, a `ParamSpec` timer with and without `functools.wraps`,
  and both render the same text for two bills. The bare form reports its own name, has no
  docstring and no `__wrapped__`, and `inspect.signature` gives
  `(*args: P.args, **kwargs: P.kwargs) -> R`.
- `wraps` copies the name, qualified name, docstring, module and `__dict__`, adds `__wrapped__`
  one level down (`inspect.unwrap` reaches the original) and copies `__annotate__`, not
  `__annotations__`.
- mypy keeps the signature through a wrapper without `wraps`, and reports an untyped decorator. A
  decorator that supplies an argument is typed with `Concatenate`, but `wraps` makes
  `inspect.signature` report the original parameters and `bind` refuse a working call.
  `functools.partial` reports what remains.

Factories and stacking.

- `cached_for(*, seconds, clock=...)` serves a result for the window, one entry per distinct
  arguments, with the clock injected, so no test sleeps. It refuses an unhashable argument and a
  window that isn't positive.
- The window is keyword-only, so `@cached_for` used bare is a `TypeError` at definition. The
  comparison `_cached_for_positional(seconds)` in `tests/conftest.py` takes it positionally, and
  used bare it binds the name to its inner decorator and returns a function where text was
  expected, with no error. mypy refuses both.
- With the timer outside the cache every call is timed, the hit as `0.0`. With the timer inside only
  the miss is timed.

Class decorators and methods.

- `document_kind(kind, *, registry=DOCUMENT_TYPES)` registers `BillOfLading` and `Manifest` at
  definition, refuses a second class for a kind with `DocumentKindError`, and mypy keeps the
  class's type, as it does through any class decorator. Beneath `@dataclass(slots=True)` it
  registers a class that is thrown away. Forgetting `return cls` binds the name to `None`, and
  mypy reports `[return]`.
- A function wrapper binds `self` on a method, because functions are descriptors. A class-based
  wrapper without `__get__` doesn't. `functools.cache` on a method keeps the instance alive
  until the cache is cleared (ruff B019).

## Layout

- `src/decorators_done_right/domain.py`: `ConsignmentId`, `DocumentKind`, `DocumentKindError`,
  `DOCUMENT_TYPES`, `document_kind`, `BillOfLading`, `Manifest`.
- `src/decorators_done_right/rendering.py`: `Clock`, `TimingSink`, `render_bill`, `timed_render`,
  `cached_for`.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
```

## What the tests verify

`tests/test_wraps.py`

- `test_both_wrapper_forms_render_the_same_text`: `wraps` and `bare`, two bills.
- `test_render_bill_shortens_the_line_to_the_width`: the width limit and its ellipsis.
- `test_wraps_keeps_the_name_qualname_doc_and_module`: the metadata copied.
- `test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring`: `wrapper`, no docstring.
- `test_inspect_signature_follows_wrapped_to_the_original_parameters`: against the bare signature.
- `test_wraps_copies_the_function_dict_and_adds_wrapped`: the `__dict__` of the wrapper.
- `test_wrapped_points_one_level_down_and_unwrap_reaches_the_original`: a two-layer stack.
- `test_wraps_copies_annotate_rather_than_annotations`: `functools.WRAPPER_ASSIGNMENTS`.
- `test_a_decorator_that_supplies_an_argument_reports_the_original_parameters`: `bind` refuses.
- `test_partial_reports_the_parameters_that_remain`: one parameter left.

`tests/test_factories.py`

- `test_cached_for_returns_the_cached_text_within_the_window`: one render for two calls.
- `test_cached_for_renders_again_once_the_window_has_passed`: at the limit and past it.
- `test_cached_for_keeps_one_entry_per_argument`: positional and keyword arguments.
- `test_cached_for_refuses_an_unhashable_argument`: `unhashable type`.
- `test_cached_for_refuses_a_window_that_is_not_positive`: zero and negative.
- `test_timed_render_reports_the_elapsed_clock_time`: rendered and raised, `2.0` both.
- `test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator`: no error.
- `test_a_keyword_only_factory_used_bare_fails_at_definition`: `TypeError`.
- `test_stacking_order_decides_whether_a_cache_hit_is_timed`: timer outside and inside.

`tests/test_classes.py`

- `test_document_kind_registers_the_class_at_definition`: the shared registry.
- `test_document_kind_refuses_a_second_class_for_a_kind`: a registry of its own.
- `test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class`: and above it.
- `test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none`: a test-local decorator.

`tests/test_methods.py`

- `test_a_function_wrapper_binds_self_on_a_method`: `timed_render` on a method.
- `test_a_class_based_wrapper_does_not_bind_self`: `TypeError`.
- `test_functools_cache_on_a_method_keeps_the_instance_alive`: a `weakref`, `gc.collect()` and
  `cache_clear()`.

`tests/test_static.py`

- `test_mypy_keeps_the_signature_through_a_wrapper_without_wraps`: `[arg-type]` (a reduced model).
- `test_mypy_reports_an_untyped_decorator`: `[untyped-decorator]` and `[no-untyped-def]` (a
  reduced model).
- `test_mypy_refuses_a_positional_factory_used_bare`: `[arg-type]` (a reduced model).
- `test_mypy_refuses_a_keyword_only_factory_used_bare`: `[call-arg]` and `[arg-type]`.
- `test_mypy_types_a_decorator_that_supplies_an_argument`: a repeated argument is refused (a reduced
  model).
- `test_mypy_reports_a_class_decorator_that_forgets_to_return`: `[return]` (a reduced model).
- `test_mypy_keeps_the_class_type_through_document_kind`: clean.

Classes and functions named with a leading underscore in the tests are fixtures and aren't part
of the model code.
