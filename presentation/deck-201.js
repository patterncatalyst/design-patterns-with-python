// deck-201.js: "Design Patterns with Python", 201: Idiomatic Python.
// Build from presentation/ with: node deck-201.js
// The slide helpers live in deck-lib.js; code slides are read from the shipped
// examples by path and line range and anchor-asserted there.

"use strict";

const H = require("./deck-helpers.js");
const { createDeck } = require("./deck-lib.js");
const { COLOR, FONT, W, ASSETS, newDeck, addContentTitle } = H;

const OUT = "design-patterns-with-python-201-idiomatic-python.pptx";

const pres = newDeck();
pres.title = "Design Patterns with Python: 201, Idiomatic Python";
pres.subject = "Companion deck to Design Patterns with Python";
pres.author = "PatternCatalyst";
pres.company = "PatternCatalyst";
pres.lastModifiedBy = "PatternCatalyst";

const { S, divider, bullets, bulletSlide, tableSlide, codeSlide, figSlide, notes, bump, finish } = createDeck(pres);

const EX = "examples";

// ===========================================================================
// 1 Cover
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
  s.addText("201: Idiomatic Python", {
    x: 6.00, y: 4.65, w: 6.70, h: 0.90,
    fontFace: FONT.body, fontSize: 18, italic: true, color: COLOR.caption,
    align: "left", valign: "top",
  });
  s.addImage({ path: `${ASSETS}/logo-candidate-2.png`, x: 11.10, y: 6.80, w: 1.55, h: 0.37 });
  notes(s, `This is the second deck in a series on the Gang of Four patterns in Python 3.15. It covers what the language gives you so that you don't write the pattern: the data model, context managers, decorators, descriptors, dispatch, and the concurrency model. The listings are read from tested examples at build time, and the examples are set in one shipping domain of consignments, carriers, rate quotes and tracking. Tests stand behind the claims, and the speaker notes name them, so a claim can be re-run when it matters.`, 45, "cover");
}

// ===========================================================================
// 2 Route
// ===========================================================================
{
  const s = S();
  addContentTitle(s, "ROUTE", "The route");
  const left = [
    ["The data model:", " equality, hashing, operators and value types declared, not hand-written."],
    ["Contracts and cleanup:", " absence in the type, shape at the point of use, release on both exits."],
    ["Decorators done right:", " the at-sign syntax written well and kept apart from the Decorator pattern."],
    ["Attribute access:", " descriptors, properties and the lookup hooks the language owns."],
  ];
  const right = [
    ["Dispatch and registries:", " choosing behaviour by type, by class creation and by value."],
    ["Pattern misuse:", " structure that stays after the forces that justified it have gone."],
    ["Concurrency and the patterns:", " what the GIL protects, and what coroutines change."],
    ["Reference:", " the sources and books behind the code."],
  ];
  bullets(s, left, { w: 5.95, fontSize: 16, gap: 10 });
  bullets(s, right, { x: 6.85, w: 5.86, fontSize: 16, gap: 10 });
  notes(s, `Eight themes make up Idiomatic Python. The data model covers special methods and value types. Contracts and cleanup covers absence, Protocols and context managers. Decorators done right and attribute access cover the two syntaxes that rewrite a name or a lookup. Dispatch and registries covers choosing behaviour by type, by class creation and by value. Pattern misuse looks at structure kept once its forces have left, and concurrency asks what the GIL protects and what an await changes. The reference theme credits the sources. What to show: nothing runs here. Fallback: each theme has a divider of its own that names it again.`, 90, "route");
}

// ===========================================================================
// Section: The data model
// ===========================================================================
divider("01", "The data model", "Syntax is a call on the type",
  `Python syntax is a set of calls on the type. A comparison calls __eq__, a set insertion calls __hash__, and an operator calls a method on the left operand and then the mirror method on the right one. Value types are declared with a dataclass instead of written by hand: the constructor, equality, hash and an assignment guard come from one decorator. The hashing contract, reflected operands, the Value Object pattern as a declaration and the limits of frozen all belong to this theme.`);

codeSlide("THE DATA MODEL", "One hashing contract",
  `${EX}/07-the-data-model/src/data_model/cargo.py`, 32, 41,
  "    def _extents(self) -> tuple[int, ...]:",
  "Equality and hash read the same sorted extents, so a carton turned on its side is one set element.",
  `Equal values must hash alike. The listing sorts a carton's three extents once and uses that tuple for both __eq__ and __hash__. __eq__ returns NotImplemented for a foreign type, so Python can try the other operand. A carton turned on its side is the same carton and one set element (test_a_turned_carton_is_one_set_element). Defining __eq__ alone leaves the class unhashable (test_defining_eq_alone_makes_a_class_unhashable). A custom __eq__ inside a frozen dataclass keeps a hash built from the fields, so two equal cartons both stay in a set (test_custom_eq_in_a_frozen_dataclass_keeps_a_field_hash). mypy can't see the broken contract: a set test catches it and a reading of the class doesn't (test_mypy_cannot_see_a_broken_hash_contract). Special methods are looked up on the type (test_special_methods_are_looked_up_on_the_type). This Dimensions is the carton's, with whole-centimetre extents and order-insensitive equality, which tells it apart from the container's Dimensions in the descriptor example. Credits: the Python Language Reference on the data model, and Ramalho's Fluent Python. What to show: run the equality tests. Fallback: the test names state the contract in sentences.`);

figSlide("THE DATA MODEL", "The reflected operand", "07-the-data-model",
  "The left operand's type asks first and declines a Money, so Money's reflected method answers; a float factor is declined twice.",
  `The figure traces factor times price, where price is a Money. Python calls the left operand's type first. Decimal declines a Money by returning NotImplemented, which is a value and not an exception, so Python calls Money.__rmul__, and that returns a Money. With a float factor the reflected method declines as well, and the expression raises TypeError (test_a_factor_times_money_uses_the_reflected_method). The built-in sum starts from the integer zero, which Money declines, so start= says what the zero is (test_sum_needs_a_money_start). Ordering within one currency works the same way: total_ordering derives the other comparisons from one (test_total_ordering_derives_the_other_comparisons), and quotes sort by total but not by themselves (test_quotes_sort_by_total_but_not_by_themselves). Credits: PEP 207, by Guido van Rossum and David Ascher; the NotImplemented entry in the built-ins documentation; the functools documentation. What to show: the figure at full width, then the first test. Fallback: the caption gives the path in one sentence.`);

codeSlide("THE DATA MODEL", "Value Object as declaration",
  `${EX}/08-dataclasses-and-value-semantics/src/value_semantics/values.py`, 15, 23,
  "@dataclass(frozen=True, slots=True, order=True)",
  "One declaration supplies the constructor, equality, hash, ordering and the assignment guard; the invariant is the part left to write.",
  `A frozen, slotted dataclass supplies what the Value Object pattern wrote by hand: the constructor, equality, a hash and a guard on assignment. What remains is the part no decorator can supply, the invariant, which sits in __post_init__ and refuses a weight that isn't positive and finite. Equal values are interchangeable, even as dictionary keys (test_equal_values_are_interchangeable). Assignment raises (test_a_frozen_value_refuses_assignment), mypy checks the generated methods (test_mypy_checks_the_generated_methods), and slots remove the per-instance dictionary and the weak-reference slot until they are asked for (test_slots_remove_dict_and_weakref_until_asked). An entity is the contrast: a stowage plan has a lifecycle and an identity, so two plans with equal contents are still two plans (test_stowage_plan_is_an_entity), and a mutable default is refused when the class is created (test_mutable_default_is_refused_at_class_creation). Credits: Fowler's Patterns of Enterprise Application Architecture for the definition, Evans's Domain-Driven Design, PEP 557, the dataclasses documentation and Slatkin's Effective Python. What to show: run the value tests. Fallback: the listing and the first test name carry the claim.`);

bulletSlide("THE DATA MODEL", "Frozen, not sealed", [
  ["Frozen", " guards attribute assignment and doesn't seal the object: object.__setattr__ still writes past the invariant."],
  ["Shallow:", " a frozen value that holds a list lets the list change, and a value holding a list can't be hashed."],
  ["A mutable dataclass", " isn't a dict key, and one consignment shared by two bookings changes in both."],
  ["An amendment", " is a new value: the other booking keeps the old one, and replace runs __post_init__ again."],
  ["Validation", " reads and raises in __post_init__; it doesn't repair the value."],
], `Frozen is a guard on assignment, nothing more. A call to object.__setattr__ writes a negative weight straight past the invariant (test_frozen_is_a_setattr_guard_not_a_seal). It is shallow: a list inside a frozen value can still grow, and the value then can't be hashed (test_frozen_is_shallow). A mutable dataclass sets its hash to None and can't be a dictionary key (test_a_mutable_dataclass_is_not_a_dict_key), and two bookings that share a mutable consignment change together (test_a_mutable_consignment_aliased_between_bookings_changes_both). An amendment builds a new value, so the other booking keeps the old one (test_an_amendment_is_a_new_value_and_the_other_booking_keeps_the_old), and replace re-runs the check (test_replace_runs_post_init). mypy can't see these mistakes (test_mypy_cannot_see_value_semantics_mistakes). Normalising belongs before construction (test_money_validates_and_of_normalises). Credits: the dataclasses documentation, PEP 557, Slatkin's Effective Python. What to show: the first two tests. Fallback: the bullets state each limit.`);

// ===========================================================================
// Section: Contracts and cleanup
// ===========================================================================
divider("02", "Contracts and cleanup", "Absence, shape and release",
  `Three contracts hold a caller to what it promised. The return type says whether a value may be absent, and mypy refuses the call until the caller handles that case. A Protocol states the shape a collaborator needs, compared where the value is used. A context manager states what release means, so a resource is closed and a half-written file is discarded without a try and finally at the call site. Absence in the type, a silent null object, two meanings of interface, and both exits from a manifest write belong to this theme.`);

codeSlide("CONTRACTS AND CLEANUP", "Absence in the type",
  `${EX}/09-protocol-and-structural-typing/src/structural_typing/carriers.py`, 52, 63,
  "def find_gateway(code: str) -> CarrierGateway | None:",
  "The return type says a carrier may be absent, so mypy requires the branch before the gateway is used.",
  `The force: a caller that asks for a collaborator that may not exist must not go on as though it did. The return type says "or nothing", and mypy refuses the call on the result until the caller handles that case. Here book_with turns an unknown carrier code into a booking error, an explicit branch where the check must stay. The Null Object stand-in isn't needed for this. A lookup of an unknown code returns None (test_find_gateway_returns_none_for_an_unknown_code), the branch raises a booking error (test_book_with_turns_absence_into_a_booking_error), and mypy requires the branch (test_mypy_requires_a_branch_for_absence). A sentinel separates "not given" from None where None is itself a valid answer (test_a_sentinel_separates_not_given_from_none). Credits: Bobby Woolf's Null Object, in Pattern Languages of Program Design 3; PEP 661, by Tal Einat and Jelle Zijlstra. What to show: run the three tests. Fallback: the listing shows the optional return and its branch.`);

codeSlide("CONTRACTS AND CLEANUP", "A silent null object",
  `${EX}/09-protocol-and-structural-typing/tests/test_absence.py`, 18, 22,
  "class _NullGateway:",
  "A test fixture: a gateway that does nothing and reports success, so a lost booking looks like a booked one.",
  `A null object turns "no carrier" into a success that carries no information. The listing is a negative fixture from the tests and not production code: a gateway that accepts a consignment and returns an empty reference. A caller that books through it sees success, and a lost booking leaves no trace (test_a_null_gateway_hides_a_lost_booking). mypy accepts it, because the shape fits the Protocol (test_mypy_accepts_a_null_gateway). A null object is right where doing nothing is the correct answer, and the discount is that case: no discount is a null object that loses nothing (test_no_discount_is_a_null_object_that_loses_nothing). The question for any stand-in is what the caller needs to know that the stand-in hides. Credits: Bobby Woolf's Null Object, in Pattern Languages of Program Design 3. What to show: run the first test and read the empty reference. Fallback: the fixture is five lines and states the hazard.`);

figSlide("CONTRACTS AND CLEANUP", "The carrier lookup", "09-protocol-and-structural-typing",
  "One booking call, three checks: an optional return is narrowed, a Protocol is compared where used, an ABC is checked at construction.",
  `Two mechanisms share the word interface. A Protocol is compared where a value is used, at the call that passes it. An abstract base class is checked when a subclass is built, so an incomplete subclass refuses to instantiate (test_mypy_checks_protocols_at_use_and_abcs_at_construction, test_abc_refuses_an_incomplete_subclass_at_construction). Both carriers satisfy the Protocol, one by shape and one by inheritance (test_both_carriers_satisfy_the_protocol_one_by_inheritance). The CarrierBase here is the reference-sharing one, which reuses a reference() method. Subclassing a Protocol explicitly makes the class nominal: mypy reports it abstract while the runtime still builds it (test_explicit_protocol_subclass_is_nominal_and_still_instantiable). runtime_checkable checks names only (test_runtime_checkable_checks_names_only). Choose by who owns the need: a consumer states a Protocol, and a family that shares a skeleton uses an ABC. Credits: PEP 544, by Ivan Levkivskyi, Jukka Lehtosalo and Łukasz Langa; the mypy protocols documentation; the abc documentation. What to show: the three lanes of the figure. Fallback: the caption states them.`);

figSlide("CONTRACTS AND CLEANUP", "Exits from a block", "10-context-managers",
  "After __enter__ opens the partial file, __exit__ replaces it with the manifest on success, or unlinks it and lets the exception propagate.",
  `A manifest write has two exits, and neither may leak or lie. The first failure is a leak: without a with block an exception leaves the handle open (test_without_with_an_exception_leaves_the_handle_open). The second is a lie: a half-written file left in place reads as a finished manifest. The figure shows the writer's answer. __enter__ opens a partial file. On success __exit__ closes it and replaces the manifest with it (test_writer_commits_only_on_success). On an exception __exit__ closes and discards the partial, then returns nothing so the exception continues (test_writer_closes_and_discards_on_an_exception). The Manifest here lists the consignments loaded on one sailing, bound for a port, which tells it from the manifest document in the decorator example. Credits: PEP 343, by Guido van Rossum and Alyssa Coghlan, and Kircher and Jain's Pattern-Oriented Software Architecture, Volume 3, on resource management. What to show: the two outgoing branches of the figure. Fallback: the caption states both exits.`);

codeSlide("CONTRACTS AND CLEANUP", "Commit or discard",
  `${EX}/10-context-managers/src/context_managers/manifest.py`, 61, 74,
  "    def __exit__(",
  "On success the partial file replaces the manifest; on an exception it is closed and removed, and nothing is returned.",
  `The language removes the try and finally from the call site. What release means, commit or discard, stays a decision of the writer. The writer commits only on success and discards on an exception, and it returns nothing, which is the decision to let the failure be seen. A writer is single-use (test_writer_is_single_use). A truthy return from __exit__ swallows the exception and the program carries on, with nothing in the output to say an error occurred (test_a_truthy_exit_swallows_the_exception). Where swallowing is intended, contextlib.suppress states it narrowly: it swallows only the named exception (test_suppress_swallows_only_the_named_exception). mypy reads the return type of __exit__ to decide whether code after the block is reachable (test_mypy_reads_exit_return_type_for_reachability). Credits: the Python Language Reference on with statement context managers, and the contextlib documentation. What to show: raise inside the with block and list the directory. Fallback: the listing shows both branches.`);

codeSlide("CONTRACTS AND CLEANUP", "Try in the generator form",
  `${EX}/10-context-managers/src/context_managers/manifest.py`, 77, 90,
  "@contextmanager",
  "The generator form of the same contract: without the try, an exception raised in the block never reaches the cleanup.",
  `In the generator form try isn't optional. An exception raised inside the with block arrives at the yield, and code after a bare yield is skipped. The type checker has nothing to say about a missing try, so a test that raises mid-write is the only guard (test_the_generator_form_needs_try, test_mypy_cannot_see_a_missing_try). An ExitStack extends the contract over several writers. A failed open discards the partials of every writer entered, and the writers unwind in reverse order (test_exit_stack_unwinds_entered_writers_in_reverse_order). On success each writer commits on its own as the stack unwinds, so the contract says nothing about a failure at commit time. Python 3.15 changed one more thing: a context manager used as a decorator on a generator function now holds the context across the iteration (test_a_context_manager_decorating_a_generator_spans_iteration). Credits: the contextlib documentation and What's New in Python 3.15. What to show: run the generator-form test with the try removed. Fallback: the test name states the failure.`);

// ===========================================================================
// Section: Decorators done right
// ===========================================================================
divider("03", "Decorators done right", "The at-sign syntax, written well",
  `The at-sign syntax rebinds a name once, at definition time. That is a different thing from the Decorator pattern, which composes wrapper objects at run time, and the two names stay apart here. Writing the syntax well means three things: the wrapper keeps the original's identity, a decorator with arguments refuses a mistake at definition, and the stacking order is chosen for what it measures. Class decorators and methods complete the picture.`);

codeSlide("DECORATORS DONE RIGHT", "What wraps copies",
  `${EX}/26-decorators-done-right/src/decorators_done_right/rendering.py`, 28, 37,
  "    def decorate(func: Callable[P, R]) -> Callable[P, R]:",
  "wraps copies the name, docstring and module for runtime tools; ParamSpec carries the parameters through for mypy.",
  `functools.wraps makes the replacement look like the original. It copies the name, qualified name, docstring and module (test_wraps_keeps_the_name_qualname_doc_and_module); without it the wrapper reports its own name and no docstring (test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring). inspect.signature reads __wrapped__ back to the original parameters (test_inspect_signature_follows_wrapped_to_the_original_parameters), and unwrap reaches the original (test_wrapped_points_one_level_down_and_unwrap_reaches_the_original). mypy doesn't read __wrapped__; it reads the declared type, and ParamSpec carries the parameters through it, so a wrapper can have either without the other (test_mypy_keeps_the_signature_through_a_wrapper_without_wraps). When a decorator supplies an argument, wraps misreports the signature and functools.partial reports the parameters that remain (test_a_decorator_that_supplies_an_argument_reports_the_original_parameters, test_partial_reports_the_parameters_that_remain). Credits: the functools documentation and PEP 612, by Mark Mendoza. What to show: inspect.signature on a wrapped function. Fallback: the caption separates the runtime and static halves.`);

codeSlide("DECORATORS DONE RIGHT", "Factories refusing bare use",
  `${EX}/26-decorators-done-right/src/decorators_done_right/rendering.py`, 42, 50,
  "def cached_for[**P, R](",
  "The keyword-only parameter makes a bare @cached_for fail where it is written, and the check on seconds runs at definition.",
  `A decorator with parameters is a function that returns a decorator, so the call runs at definition, and so does any mistake in it. Decorator expressions are evaluated when the function is defined. The keyword-only star in the signature makes a bare @cached_for fail at that line with a TypeError (test_a_keyword_only_factory_used_bare_fails_at_definition) and makes mypy refuse it (test_mypy_refuses_a_keyword_only_factory_used_bare). A factory that takes its window positionally accepts the bare form silently and binds the name to its inner decorator, which fails at the call site (test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator). The signature also shows the PEP 695 syntax for type parameters, including a ParamSpec. Credits: the compound statements reference in the Python Language Reference, and PEP 695, by Eric Traut. What to show: apply the decorator with no call. Fallback: the two test names state both outcomes.`);

bulletSlide("DECORATORS DONE RIGHT", "Where the timer sits", [
  ["A timer inside the cache", " measures the renderer: a hit never reaches it."],
  ["A timer outside the cache", " measures what the caller waited, with a hit counted as a call that took no clock time."],
  ["A class decorator", " that doesn't return the class binds the name to None, and one placed beneath a slotted dataclass registers a class that is then discarded."],
  ["A function wrapper", " works on a method unchanged, because a function binds self; functools.cache on a method keeps the instance alive."],
], `Called twice with the same bill, both stacking orders render once. With the timer outside the cache the sink receives a two-second render and then a zero, with the hit counted as a call that took no clock time. With the timer inside, it receives the render alone, because a hit never reaches it (test_stacking_order_decides_whether_a_cache_hit_is_timed). The inside order measures the renderer and the outside order measures what the caller waited, hits included. A dashboard of renderer cost wants the first, and one of response time wants the second. The cache window expires with the clock (test_cached_for_renders_again_once_the_window_has_passed). Class decorators have their own traps (test_a_class_decorator_beneath_a_slotted_dataclass_registers_a_discarded_class, test_a_class_decorator_that_forgets_to_return_binds_the_name_to_none), and functools.cache on a method keeps the instance alive (test_functools_cache_on_a_method_keeps_the_instance_alive; ruff rule B019 flags it). Credits: PEP 3129, by Collin Winter, and the Descriptor Guide. What to show: the two stacking orders with a recording sink. Fallback: the bullets state both readings.`);

// ===========================================================================
// Section: Attribute access
// ===========================================================================
divider("04", "Attribute access", "The language owns the lookup",
  `Attribute lookup is a language mechanism with a fixed order, and three hooks sit in it. A descriptor puts a rule on a class attribute once and lets any number of fields use it. A property is a descriptor written inline, and cached_property is one that stores its result in the instance dictionary. A __getattr__ hook runs only when normal lookup fails, which makes lazy loading possible without a stand-in object. The traps in the hooks are the substance of this theme.`);

codeSlide("ATTRIBUTE ACCESS", "One validator, many fields",
  `${EX}/27-descriptors-and-properties/src/descriptors_properties/fields.py`, 29, 38,
  "    def __get__(self, instance: object | None, owner: type) -> Decimal:",
  "A descriptor stores a validated value per instance, so the rule lives in one place for any number of fields.",
  `A descriptor puts the rule in one place and lets any number of fields use it. The trouble with a property is the third copy: pasted validators drift, and a pasted property accepts an infinite height where the shared rule refuses it (test_a_copy_pasted_property_validator_drifts). The descriptor's __set__ checks the value and stores it under a private name in the instance dictionary, and __set_name__ gives each field its own storage (test_set_name_gives_each_field_its_own_storage). One descriptor class validates every field form (test_one_descriptor_class_validates_every_field), and the field forms agree on the extents they accept (test_every_field_form_validates_the_same_extents). This Dimensions is the container's, with Decimal extents; the carton's Dimensions in the data model example is a different class. Skip the descriptor when one field in one class needs a rule: a property pair is shorter. Credits: the Descriptor Guide and PEP 487, by Martin Teichmann. What to show: assign an infinite value through the field forms. Fallback: the listing and the drift test.`);

codeSlide("ATTRIBUTE ACCESS", "Costs of cached_property",
  `${EX}/27-descriptors-and-properties/src/descriptors_properties/cargo.py`, 50, 53,
  "    @cached_property",
  "The first read computes the value and stores it in the instance dictionary; that storage is where the costs come from.",
  `The cache lives in the instance dictionary, and it has four costs. It needs the dictionary, so a slotted class without one raises on the read (test_cached_property_needs_an_instance_dict). A frozen class can't clear the cache by deleting the attribute (test_a_frozen_dataclass_cannot_clear_a_cached_property). Over mutable state it goes stale (test_a_cached_property_over_mutable_state_goes_stale). And two threads can both run the getter (test_a_cached_property_getter_can_run_twice_under_threads). The benefit is real: the value is computed on first access and stored (test_chargeable_weight_is_computed_on_first_access_and_stored). Lookup precedence explains the storage trick. A data descriptor beats the instance dictionary (test_a_data_descriptor_takes_precedence_over_the_instance_dict), and cached_property isn't one, so its dictionary entry wins when the attribute is read again (test_an_instance_dict_entry_takes_precedence_over_cached_property). Credits: the functools documentation, What's New in Python 3.12 for the lock removal, and Brandon Rhodes's page on the Factory Method pattern. What to show: read the attribute twice. Fallback: the four tests state the costs.`);

codeSlide("ATTRIBUTE ACCESS", "A self-loading history",
  `${EX}/30-dynamic-attributes-and-proxy/src/dynamic_attributes/tracking.py`, 75, 84,
  "        if name not in _LAZY:",
  "A tracking history loads on the first read of a lazy field, through __getattr__ and an allow-list, with no stand-in object.",
  `A history can load itself on first read: when normal attribute lookup fails, Python calls the object's own __getattr__. There is no stand-in object, so this is interception, not a surrogate. Nothing loads until a field is read (test_nothing_is_loaded_until_a_field_is_read), the load runs once for every field (test_every_history_form_loads_once_for_every_field), and once loaded the fields come from the instance dictionary (test_a_loaded_history_reads_its_fields_from_the_instance_dict). The hook runs only when normal lookup fails (test_getattr_runs_only_when_normal_lookup_fails). What stays design is which names may load. The allow-list refuses a misspelt field, and __dir__ lets Python suggest the declared name (test_a_misspelt_field_suggests_the_declared_name_through_dir). This TrackingHistory is the lazy one, which tells it apart from the eager history in the data model example. Credits: Fowler's Patterns of Enterprise Application Architecture for Lazy Load, and the Design Patterns catalogue, which lists the idea under Proxy. What to show: read a field and watch the feed once. Fallback: the two guard lines.`);

codeSlide("ATTRIBUTE ACCESS", "The recursion trap",
  `${EX}/30-dynamic-attributes-and-proxy/tests/test_lookup.py`, 35, 44,
  "class _SelfHealing:",
  "__getattr__ reads self._load, which copy never sets: the missing attribute calls __getattr__ again, without end.",
  `copy builds an instance without running __init__, so the instance has no _load. The first read of _load fails normal lookup, which calls __getattr__, which reads _load again, and the recursion runs until RecursionError. The test runs copy.copy, copy.deepcopy and a pickle round trip over this test-local class, and each raises (test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute). Each fix keeps the hook out of the recursion (test_each_fix_keeps_getattr_out_of_recursion), and a copy of the real history keeps its state before and after loading (test_copy_keeps_a_history_before_and_after_loading). Two related facts: hasattr is a read, so checking for a lazy field loads the history (test_hasattr_loads_the_history), and special methods are looked up on the type, so a hook can't forward them (test_implicit_special_method_lookup_bypasses_getattr). Credits: the copy and pickle documentation. What to show: run the recursion test and read the error. Fallback: the class is ten lines.`);

// ===========================================================================
// Section: Dispatch and registries
// ===========================================================================
divider("05", "Dispatch and registries", "Behaviour chosen by type, class creation or value",
  `Three mechanisms choose behaviour without an if-chain. functools.singledispatch picks an implementation by the type of the first argument, and a registration can live in another module. A class keyword with __init_subclass__ registers a subclass the moment its class statement runs, and refuses a bad one. A dictionary of callables picks by value, and a narrow try around its lookup keeps a bug from reading as a missing key. The fallback, or the failure mode, is the design decision in each mechanism.`);

codeSlide("DISPATCH AND REGISTRIES", "Dispatch by registered type",
  `${EX}/28-singledispatch/src/singledispatch_visitor/tariff.py`, 17, 31,
  "@singledispatch",
  "One generic function, one registration per commodity; the annotation names the class, and the fallback raises.",
  `For an open set of kinds like this one, the Visitor from Design Patterns becomes a single generic function. The registrations carry no class argument because the annotation supplies it. The most specific registration wins (test_the_most_specific_registration_wins), and an unregistered subclass gets its base class's code (test_an_unregistered_subclass_gets_its_base_class_code). Registered commodities get their codes whichever fallback form is used (test_every_fallback_form_gives_registered_commodities_their_codes). An unregistered kind reaches the object implementation, so what that function does is a design choice. Here it raises and names the kind (test_a_raising_fallback_names_an_unregistered_kind); for a customs declaration that is right, because a declaration without a heading shouldn't be filed. A fallback that answers gives an unknown kind a code silently (test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently). Credits: the functools documentation and the Design Patterns catalogue. What to show: dispatch on an unregistered commodity. Fallback: the raising function in the listing.`);

codeSlide("DISPATCH AND REGISTRIES", "Registration from another module",
  `${EX}/28-singledispatch/src/singledispatch_visitor/dangerous_goods.py`, 8, 14,
  "from singledispatch_visitor.commodities import LithiumIonBattery",
  "The tariff module imports nothing from this one; the registration exists once something imports it.",
  `The design question is who imports the extension. The tariff module imports nothing from this one, so a battery raises a tariff error until something imports the module, and gets its code afterwards (test_another_module_extends_the_set_when_it_is_imported). The registry that records this is a read-only view (test_the_registry_is_read_only). PEP 443 expects most registrations beside the function or the type, and calls this module-away case infrequent, so start-up has to import the extension. The price of an open set is what mypy can check. With an object fallback it can't report a missing kind. A union fallback closes the set: mypy then refuses a registration or a call for a kind outside the union (test_mypy_refuses_a_kind_outside_a_union_fallback, test_mypy_checks_calls_and_registrations_against_the_fallback). Credits: PEP 443, by Łukasz Langa. What to show: dispatch a battery before and after the import. Fallback: the listing is seven lines.`);

codeSlide("DISPATCH AND REGISTRIES", "Registration by class keyword",
  `${EX}/29-metaclasses-init-subclass-and-registries/src/carrier_registry/carriers.py`, 44, 58,
  "        super().__init_subclass__()",
  "A class keyword registers a carrier at definition and refuses a bad class before the registry is touched.",
  `A class keyword registers a subclass at the moment its class statement runs, so the metaclass registry is not needed. The hook runs ahead of the registry, so it can refuse a class and leave the registry as it was (test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry). An abstract class with a code is refused, a concrete class without one is refused, and a duplicate code raises. Registered carriers book through the registry (test_every_registry_form_books_through_the_registered_carrier), and the registry is exposed as a read-only view (test_the_carrier_registry_is_a_read_only_view). Abstractness is visible inside the hook (test_isabstract_sees_abstractness_inside_init_subclass). mypy reports a misspelt class keyword (test_mypy_reports_a_misspelt_class_keyword). Imports decide the registry: a carrier registers when its module is imported (test_a_carrier_module_registers_only_when_it_is_imported). This CarrierBase is the registering one, which tells it apart from the reference-sharing base. Credits: PEP 487, by Martin Teichmann, and Brandon Rhodes's The Global Object Pattern. What to show: define a subclass with a code. Fallback: the four refusals in the listing.`);

tableSlide("DISPATCH AND REGISTRIES", "Metaclass costs",
  ["Cost", "What the test shows"], [
    ["A second metaclass", "It conflicts with the base's metaclass and raises TypeError; deriving from ABCMeta resolves it."],
    ["Class keywords", "mypy doesn't check them: code=1 exits 0, and the run registers an int key."],
    ["Self in __new__", "mypy refuses Self in a metaclass __new__ although the class builds."],
    ["A registry of classes", "A class called from a metaclass registry is typed Any, so a misspelt method passes mypy."],
    ["What it buys", "Operators on the class object itself: in, iteration and len."],
  ], [3.0, 9.09],
  `A metaclass shows its cost in four places: a conflict at class creation and three things mypy doesn't track. A second metaclass conflicts with the base's metaclass and raises TypeError, and a metaclass derived from ABCMeta resolves it (test_a_second_metaclass_conflicts_with_the_bases_metaclass, test_a_metaclass_derived_from_abcmeta_resolves_the_conflict). mypy doesn't check metaclass class keywords (test_mypy_does_not_check_metaclass_class_keywords), refuses Self in a metaclass __new__ (test_mypy_refuses_self_in_a_metaclass_new), and types a class called from a metaclass registry as Any (test_mypy_types_a_class_called_from_a_metaclass_registry_as_any). The one case where it pays is an operator on the class object (test_only_a_metaclass_gives_the_class_object_operators); enum does this with EnumType. Otherwise a metaclass is the wrong tool. Credits: the mypy documentation on metaclasses, the abc and enum documentation, and the data model reference. What to show: the conflict test. Fallback: the table states each cost.`, { rowH: 0.62, fontSize: 14, y: 1.7 });

codeSlide("DISPATCH AND REGISTRIES", "A narrow try",
  `${EX}/31-shortcut-patterns-dict-dispatch-and-eafp/src/shortcut_patterns/documents.py`, 58, 62,
  "    try:",
  "The try holds the lookup and nothing else, so a KeyError raised inside an issuer travels out as itself.",
  `What goes is the structure built around an if-chain; the dictionary of callables stays. The try holds the lookup and nothing else. The call to the issuer sits outside the try, so a KeyError raised inside an issuer travels out of issue as itself (test_an_issuers_own_key_error_passes_through_issue). The same call inside the try reports that bug as "no issuer" for the kind (test_a_try_around_the_call_reports_an_issuers_bug_as_an_unsupported_kind). An unsupported kind raises the named error (test_an_unsupported_kind_raises_unsupported_document_error). A handler that's too broad turns a bug into a missing value, and two idioms do it by design: getattr with a default hides an AttributeError raised inside a property (test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property), and suppress ends its block at the first exception it swallows (test_suppress_skips_the_rest_of_its_block_after_the_first_exception). mypy checks the shape of the table but not totality (test_mypy_accepts_a_table_that_misses_a_kind). Credits: the Python glossary entry for EAFP, PEP 814 on frozendict by Victor Stinner and Donghee Na, and the contextlib documentation. What to show: raise a KeyError inside an issuer. Fallback: the five lines of the listing.`);

figSlide("DISPATCH AND REGISTRIES", "Dispatch tables and EAFP", "31-shortcut-patterns-dict-dispatch-and-eafp",
  "A document kind is looked up in a read-only table and its issuer called outside the try; a duty rate is read once and loaded on KeyError.",
  `The figure shows a cache read that asks forgiveness: read once, and on KeyError load and store the rate. If another thread evicts the entry first, the read reloads instead of raising (test_an_eafp_read_reloads_when_another_thread_evicts_first). A table wins when the set is data: a caller can supply its own, and a kind that arrives as text is looked up like any other key. The scope of the guarantee is one gap: two readers that both miss both load, so EAFP doesn't make a load happen once (test_two_eafp_readers_that_both_miss_both_load). The cache forms read, load and evict the same way (test_every_cache_form_reads_loads_and_evicts_the_same_way). The ghost-styled look-first form is the comparison, where a check and a read leave a gap. Recorded figures, labelled: on Python 3.15.2, best of five repeats of one million calls, 2026-11-06, a present key cost 42.7 ns for EAFP against 50.4 ns look-first, and an absent key cost 141.5 ns against 45.0 ns. On a miss EAFP was about three times dearer. No test asserts a time. Credits: the Python glossary entry for EAFP. What to show: the figure. Fallback: the caption.`);

// ===========================================================================
// Section: Pattern misuse
// ===========================================================================
divider("06", "Pattern misuse", "Structure that outlives its forces",
  `A pattern is a structure with a reason. When the forces leave and the structure stays, the price is still paid on each change. A rate quote written as a function and as an engine of strategies, charges and visitors gives the same answers, so what differs is the cost of the structure. A Visitor over a growing set breaks on a new kind, and a service locator moves a failure from the signature to the first call.`);

codeSlide("PATTERN MISUSE", "A quote as a function",
  `${EX}/32-anti-patterns-and-pattern-misuse/src/pattern_misuse/rating.py`, 49, 57,
  "def quote(consignment: Consignment, tariff: Tariff) -> RateQuote:",
  "A flat fee by zone, a fuel fee, then tax rounded to the cent; an unknown zone raises a rating error.",
  `Two forms quote one table, and the table is the test. The EU zone quotes 35.70 and the Asia zone 78.05 through each form (test_every_rating_form_quotes_the_same_table), and an unknown zone raises the same rating error with the same message (test_every_rating_form_refuses_an_unknown_zone). The behaviour is identical, so what differs is the cost of the structure. Here the quote is one function taking a tariff as an argument, and the alternative spreads the same arithmetic across an engine, strategies, charges and a visitor. Related misuse sits in accessors. A getter and setter pair promises behaviour the field may never need, and the promise has costs: an accessor consignment has no value equality (test_an_accessor_consignment_has_no_value_equality), a setter lets a quoted consignment change its quote (test_a_setter_lets_a_quoted_consignment_change_its_quote), and a frozen consignment refuses assignment (test_a_frozen_consignment_refuses_assignment). Credits: PEP 8, by Guido van Rossum, Barry Warsaw and Alyssa Coghlan, which says to expose the attribute name and use properties if behaviour arrives. What to show: the shared table. Fallback: the listing.`);

bulletSlide("PATTERN MISUSE", "A misplaced Visitor", [
  ["A new charge kind", " breaks the engine's Visitor at run time, because no visit method exists for it."],
  ["Declaring the method", " on the visitor base is the fix, and it moves the failure: concrete visitors turn abstract until they implement it, and mypy reports the gap."],
  ["A Visitor suits", " a fixed set of kinds that gains operations. Here the change that arrives is a new kind."],
], `A Visitor suits a fixed set of kinds that gains operations. In the rating engine the change that arrives is a new charge kind, which is the edit this structure makes expensive. Adding the kind breaks the engine's visitor at run time (test_a_new_charge_kind_breaks_the_engines_visitor_at_run_time). Declaring the method on the visitor base is the fix, and it moves the failure: building a concrete visitor then raises a TypeError until it implements the method (test_declaring_a_new_visit_method_makes_every_concrete_visitor_abstract), and mypy reports a visitor that misses the new method (test_mypy_reports_a_visitor_missing_a_new_visit_method). So the failure becomes an error mypy reports before the program runs, at the price of editing the visitors. Where the set of kinds is open, the singledispatch form avoids the edit. Credits: the Design Patterns catalogue is the source for Visitor. What to show: add a charge kind to the engine and run the quote. Fallback: the three bullets state the cost.`);

codeSlide("PATTERN MISUSE", "A located dependency",
  `${EX}/32-anti-patterns-and-pattern-misuse/tests/conftest.py`, 175, 179,
  "    def quote(self, consignment: Consignment) -> RateQuote:",
  "A test fixture: the engine asks a locator for its tariff by name, so a missing registration appears only at the first quote.",
  `A service locator is a registry that a class asks for its collaborators by name. It answers a real need, since a collaborator is found without being passed down the signature, and it has a cost. The engine in the listing is a test fixture. It fails at the first quote when nothing is registered (test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered) and quotes normally once the tariff is registered (test_a_located_engine_quotes_once_its_tariff_is_registered). mypy doesn't see the missing registration (test_mypy_does_not_see_a_missing_registration). Passing the tariff as an argument turns the unseen failure into the seen one: mypy then reports the missing argument (test_mypy_reports_a_missing_tariff_argument). The function wins on the forces in the one-carrier case, where there is one owner and one tariff schedule. A Protocol or ABC with one implementation adds a name and no seam. Credits: Martin Fowler's article on Inversion of Control containers and dependency injection, and Mark Seemann's Service Locator is an Anti-Pattern. What to show: build the engine with an empty locator. Fallback: the four lines of the listing.`);

// ===========================================================================
// Section: Concurrency and the patterns
// ===========================================================================
divider("07", "Concurrency and the patterns", "What the GIL protects and an await changes",
  `Concurrency changes where the patterns break. The global interpreter lock protects the interpreter's own structures, and a reservation that reads a count and then writes a slot is several steps of your code. Threads, processes and interpreters see data differently, and what a pool shares matters more than which pool is fastest. Under asyncio, a coroutine is a value, an await is a switch point, and a generator that is left early has to be closed.`);

codeSlide("CONCURRENCY AND THE PATTERNS", "Build and GIL state",
  `${EX}/37-the-gil-and-performance/src/gil_and_performance/build.py`, 11, 19,
  "def gil_disabled_build() -> bool:",
  "One function reads the build, the other the running state, because a free-threaded build can run with the GIL back on.",
  `Two functions are needed because the build and the running state can differ. A free-threaded build can run with the GIL enabled through an environment variable or a command-line option, so the build flag and the GIL state are separate questions. With neither override set the two answers are opposites, and the test asserts that the GIL is on exactly when the build isn't free-threaded (test_the_build_flag_and_the_runtime_gil_state_agree). The version banner names the free-threading build on that build alone (test_sys_version_names_the_free_threading_build_only_on_that_build). get_config_var is typed Any, so mypy needs the bool wrapper (test_mypy_types_the_build_flag_as_any). The free-threaded build is tested here and measured; this deck does not recommend it. The tests run on the default build and on the free-threaded one in CI. Credits: the free-threading how-to, PEP 703 (Making the Global Interpreter Lock Optional in CPython) and PEP 779. What to show: run the build tests on both builds. Fallback: the two functions are the whole listing.`);

figSlide("CONCURRENCY AND THE PATTERNS", "Locks over read and write", "37-the-gil-and-performance",
  "Two threads reserve a slot: parked between read and write they take the same one; a lock over both gives each its own.",
  `Two bookings reach the same sailing from two threads, and each reserves a slot. The GIL never promised that the steps run together. Parked between the read and the write, both threads take the same slot, and one reservation remains (test_two_threads_parked_between_read_and_write_take_the_same_slot). The fix is a lock that covers the read as well as the write, and then each thread gets its own slot (test_a_lock_across_read_and_write_gives_each_thread_its_own_slot). A Barrier forces the interleaving without a sleep. An attribute increment is a separate load, add and store (test_an_attribute_increment_is_a_separate_load_add_and_store). In recorded runs of the probe, 300 trials of four threads each adding 1 to a shared attribute 5,000 times lost an update in 0 of 300 on the default build and in 300 of 300 on the free-threaded build (Python 3.15.2, a 16-thread x86-64 CPU class, 2026-11-07). A race that doesn't fire on one build still exists. This is the threaded stowage plan. Credits: the Monitor Object pattern in Pattern-Oriented Software Architecture, Volume 2. What to show: the two lanes. Fallback: the caption.`);

codeSlide("CONCURRENCY AND THE PATTERNS", "What a pool shares",
  `${EX}/37-the-gil-and-performance/src/gil_and_performance/pools.py`, 18, 33,
  "# A class cannot stand in here: mypy rejects calling type[Executor] with max_workers.",
  "Three pool factories rate a batch through one function; the pools differ in what the workers can see.",
  `Every pool returns the serial loop's answers (test_every_pool_rates_the_batch_as_the_serial_loop_does). What differs is what the workers can see: threads share the argument, while processes and interpreters copy it (test_threads_share_the_argument_and_processes_and_interpreters_copy_it), and a process pool can't send a lambda (test_a_process_pool_cannot_send_a_lambda). This quote is the CPU-bound one, which tells it from the async quote. Recorded ratios, labelled: on Python 3.15.2, default and free-threading builds, 4 workers, best of 3, a 16-thread x86-64 CPU class, 2026-11-06, serial time over pool time. On the default build the thread pool ran at 1.0 times serial. On the free-threaded build the integer loop ran at 3.9 times in the thread pool and the Decimal loop at 0.5 times. Process and interpreter pools ran at about 3.4 to 3.7 times, warm, on both builds. A second run agreed within about 0.4. No test asserts a time. Two loops on one build moved in opposite directions, so measure your loop. Credits: the concurrent.futures and threading documentation. What to show: the pool table. Fallback: the listing.`);

bulletSlide("CONCURRENCY AND THE PATTERNS", "A coroutine as a value", [
  ["Calling a coroutine function", " gives a coroutine, not a RateQuote, until something awaits it."],
  ["A quote assigned and never awaited", " doesn't fail where it was written; the runtime warns when the coroutine is collected."],
  ["mypy reports", " a quote returned without await and a call whose result is dropped; a coroutine bound to an underscore passes, so the runtime warning is the check left."],
  ["An await", " is a switch point: a read and a write that span one can interleave with another task's."],
], `A quote that is assigned and never awaited doesn't fail where it was written. Calling a coroutine function gives a coroutine and not a RateQuote (test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote), and the runtime warns when the coroutine is collected (test_a_quote_that_is_never_awaited_warns_when_it_is_collected). mypy reports a quote returned without await (test_mypy_reports_a_quote_returned_without_await) and accepts a coroutine bound to an underscore (test_mypy_accepts_a_coroutine_bound_to_underscore). The second edge is the switch point. A read-modify-write that spans an await can interleave with another task's: with no lock, five tasks all read before any stores, and the stowage plan books one slot five times (test_an_await_between_read_and_write_double_books_a_slot), while an asyncio lock gives each task its own slot (test_an_asyncio_lock_gives_each_task_its_own_slot). This is the async stowage plan, not the threaded one. Credits: the Developing with asyncio page and ruff rule RUF006. What to show: drop an await and run the test. Fallback: the bullets.`);

codeSlide("CONCURRENCY AND THE PATTERNS", "Closing a feed early",
  `${EX}/38-asyncio-and-the-patterns/src/asyncio_patterns/feed.py`, 54, 60,
  "async def first_departure(feed: CarrierFeed) -> HandlingEvent | None:",
  "aclosing closes the async generator even though the loop returns early; a bare async for would leave it open.",
  `Leaving async for early doesn't close an async generator. contextlib.aclosing does. The iterator becomes an async generator, and the closing is the part that needs care. A plain break out of async for leaves the feed open (test_breaking_out_of_async_for_leaves_the_feed_open). Wrapping the generator in aclosing makes first_departure close the feed even though it returns early (test_first_departure_closes_the_feed_when_it_stops_early), and a session closes the feed when its task is cancelled (test_the_session_closes_the_feed_when_its_task_is_cancelled). The question to ask of an async generator is who closes it. Annotate it as an AsyncGenerator, since an AsyncIterator has no aclose to call. Credits: the contextlib documentation. What to show: break out of the loop and check whether the feed's cleanup ran. Fallback: the three test names state the cases.`);

codeSlide("CONCURRENCY AND THE PATTERNS", "Task groups and subscribers",
  `${EX}/38-asyncio-and-the-patterns/src/asyncio_patterns/signal.py`, 25, 31,
  "    async def publish(self, event: E, /) -> None:",
  "gather with return_exceptions lets the other subscribers finish, then raises the failures together as one group.",
  `A task group is right for quotes, where one failure makes the rest worthless, and wrong for notifications, where subscribers are independent. The listing shows the notification form: gather with return_exceptions lets the other subscribers finish, and the failures are raised afterwards as one exception group. A failing subscriber doesn't stop the others (test_a_failing_subscriber_does_not_stop_the_others). A task-group publisher cancels the other subscribers when one fails (test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails). For quotes the cancellation is the point: a failing carrier cancels the other quote (test_a_failing_carrier_cancels_the_other_quote), and the first answer cancels the rest of the group (test_the_first_answer_cancels_the_rest_of_the_group). A command queue can stop by shutdown, which lets the worker drain the queue and then stop (test_shutdown_lets_the_worker_drain_the_queue_then_stop), where a None sentinel adds a value the worker has to test for. Credits: What's New in Python 3.15 for TaskGroup.cancel, and the Active Object pattern in Pattern-Oriented Software Architecture, Volume 2. What to show: fail one subscriber in each form. Fallback: the caption.`);

// ===========================================================================
// Section: Reference
// ===========================================================================
divider("08", "Reference", "The sources and books behind the code",
  `The code in these slides rests on the Python documentation, the design record in the PEPs, a few articles on patterns, and a short list of books. Sources are credited where an idea leans on them. The wording and the examples are new, and the short quotations are attributed. A table of sources and a table of books come with the site and the repository that hold the examples.`);

tableSlide("REFERENCE", "Sources credited",
  ["Source", "Used for"], [
    ["Python Language Reference", "The data model, the with statement and decorator expressions"],
    ["Python library documentation", "functools, contextlib, dataclasses, abc, copy, concurrent.futures, asyncio and sys"],
    ["Descriptor Guide; free-threading how-to", "Attribute lookup order; building and running with or without the GIL"],
    ["mypy documentation", "How mypy checks Protocols and what it cannot check in a metaclass"],
    ["PEPs 207, 343, 443, 487, 544, 557, 612, 661, 695, 703, 779, 814 and 3129", "The design record behind each feature, with authors named in the notes"],
    ["What's New in Python 3.12 and 3.15", "The cached_property lock removal; contextlib and TaskGroup.cancel changes"],
    ["ruff rules B019 and RUF006", "Caching an instance method; a dangling task"],
    ["Brandon Rhodes, python-patterns.guide", "Lookup precedence and the cost of global registries"],
    ["Martin Fowler, Inversion of Control Containers and the Dependency Injection pattern", "A service locator against injection"],
    ["Mark Seemann, Service Locator is an Anti-Pattern", "A located dependency fails at first use"],
  ], [5.9, 6.19],
  `Each source is named with what it is used for, and the speaker notes of the slides that rely on it name it again. The Python Language Reference covers the data model, the with statement and decorator expressions. The library documentation covers the behaviour of the standard modules shown, and the Descriptor Guide gives the lookup order. The PEPs record why a feature exists: Guido van Rossum and David Ascher on rich comparisons, Guido van Rossum and Alyssa Coghlan on the with statement, Łukasz Langa on single-dispatch functions, Martin Teichmann on class creation hooks, Victor Stinner and Donghee Na on frozendict, and others named where they are used. Brandon Rhodes, Martin Fowler and Mark Seemann are credited for their articles. What to show: nothing; the table is the record. Fallback: the rows name each source and what it was used for.`, { rowH: 0.40, fontSize: 12, y: 1.55 });

tableSlide("REFERENCE", "Reading further",
  ["Book", "Authors", "Year"], [
    ["Fluent Python, second edition", "Ramalho", "2022"],
    ["Effective Python, third edition", "Slatkin", "2024"],
    ["Design Patterns: Elements of Reusable Object-Oriented Software", "Gamma, Helm, Johnson, Vlissides", "1994"],
    ["Patterns of Enterprise Application Architecture", "Fowler", "2002"],
    ["Domain-Driven Design", "Evans", "2003"],
    ["Pattern Languages of Program Design 3", "Edited volume; Woolf's Null Object", "1998"],
    ["Pattern-Oriented Software Architecture, Volume 2", "Schmidt, Stal, Rohnert, Buschmann", "2000"],
    ["Pattern-Oriented Software Architecture, Volume 3", "Kircher, Jain", "2004"],
  ], [7.0, 3.9, 1.19],
  `Eight books cover the ground the slides compress. Fluent Python by Luciano Ramalho and Effective Python by Brett Slatkin are the companions to the language features: the data model, dataclasses and decorators. Design Patterns by Gamma, Helm, Johnson and Vlissides is the catalogue itself. Fowler's Patterns of Enterprise Application Architecture defines Value Object and Lazy Load, and Evans's Domain-Driven Design uses the value-object term in modelling. Bobby Woolf's Null Object is in Pattern Languages of Program Design 3. The two Pattern-Oriented Software Architecture volumes give Monitor Object and Active Object, and resource management. What to show: nothing; the list is the reference. Fallback: titles, authors and years are enough to find them.`, { rowH: 0.50, fontSize: 14, y: 1.7 });

bulletSlide("REFERENCE", "Site and repository", [
  ["The site", " is at https://patterncatalyst.github.io/design-patterns-with-python/"],
  ["The repository", " holds the examples: https://github.com/patterncatalyst/design-patterns-with-python"],
  ["To run an example,", " sync the workspace once with uv sync --locked --all-packages, then run uv run pytest and uv run mypy --strict src tests inside an example directory."],
  ["Two further decks", " cover themes: patterns and SOLID in Python, and testing, inherited code and working with AI tools."],
], `The site holds the prose and the figures. The repository holds the examples that the listings were read from, with their tests, so a claim can be re-run. An example runs on its own: sync the workspace once from the root, then run pytest and mypy in strict mode from the example's directory, since both find the root configuration. The pinned versions are CPython 3.15.2, uv 0.13.7, pytest 9.2.0 and mypy 2.4.1. The two concurrency examples are also tested on the free-threaded build, 3.15.2t. The two further decks cover, by theme, patterns and SOLID in Python, and testing, changing inherited code and working with AI tools on pattern-heavy code. What to show: the site's home page and the repository's examples directory. Fallback: the two addresses are enough to find both.`, { fontSize: 17 });

// ===========================================================================
// Checks and write
// ===========================================================================
finish(OUT);
