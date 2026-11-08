---
title: "Pattern-to-force quick reference"
order: 45
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "E"
description: "Four tables that give, for each pattern developed, its bucket, its force and its when-not rule in the words of the chapter that develops it, with a link to that chapter."
---

## Learning objectives

By the end of this appendix you can:

- Find a pattern's force and its when-not rule in one row, in the words of the chapter that weighs it.
- Tell from the bucket word whether Python removes the structure, keeps it or shares the name with something else.
- Jump from a row to the chapter that develops the pattern.

## Why this matters

A pattern is chosen by its force: "A pattern is a solution to a problem in a context, and the problem is a set of forces pulling against each other" ([Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }})). The force stays when a language feature removes the structure, so in review a lookup by force beats a lookup by class diagram. The bucket comes from [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}), which places each pattern "by asking about its force, the pressure that made the pattern worth having, and about its name."

How to read the rows:

- **Each row is one pattern as one chapter treats it.** The Bucket, Force and When-not cells are clauses copied from the chapter in the last column, in that chapter's voice. A clause may start or stop mid-sentence where the chapter's sentence runs on into a link.
- **A pattern treated in two or three chapters has a row for each**, and the rows can differ because each chapter asks a different question. The three Proxy rows are the clearest case.
- **A dash means the chapter states no bucket**, as for the Proxy surrogate. The three-way split files Proxy under needs disambiguating, because the name covers a surrogate object and attribute interception.
- **The `| None` pipe in the Null Object row is escaped** so the table renders; the chapter has it unescaped.

What Python gives for each pattern is in the three-way split, and the bucket for six patterns under asyncio is in [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## Creational patterns

Singleton's Force cell is the chapter's quoted default answer to the force, not a statement of the force.

| Pattern | Bucket | Force | When not to use it | Chapter |
| --- | --- | --- | --- | --- |
| Factory Method | Factory Method dissolves | The force is real: the caller wants a gateway for a carrier and shouldn't know which gateway class that is. | With one carrier, call the class. | [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) |
| Abstract Factory | Bucket: survives. | The force is that products must come from the same family, and a language that stores callables doesn't choose the family. | If the products don't have to match, pass them separately. | [Factory Method and Abstract Factory]({{ '/docs/16-factory-method-and-abstract-factory/' | relative_url }}) |
| Builder | Bucket: dissolves. | The force that remains is an object with many parts, several of them optional, that has to be complete and valid before anyone uses it. | A builder kept only for a fluent style gives up the type checker's missing-argument report in exchange for a chain of method calls. | [Builder, dataclasses, and Prototype]({{ '/docs/17-builder-dataclasses-and-prototype/' | relative_url }}) |
| Prototype | Bucket: dissolves. | The force that remains is a new object that starts as a copy of a configured one | Don't deep-copy a lock; build another. | [Builder, dataclasses, and Prototype]({{ '/docs/17-builder-dataclasses-and-prototype/' | relative_url }}) |
| Singleton | Bucket: needs disambiguating. | load this once and let everyone read it | A class whose only reason to exist is to be single is a module. | [Singleton: module, Borg, and metaclass]({{ '/docs/18-singleton-module-borg-metaclass/' | relative_url }}) |

## Structural patterns

The Decorator row covers the pair, the wrapper-object pattern and the `@` syntax that shares its name. The `@decorator` row under "Beyond the catalogue" asks what stays design around the syntax.

| Pattern | Bucket | Force | When not to use it | Chapter |
| --- | --- | --- | --- | --- |
| Adapter | Bucket: survives. | two parts that disagree about shape: one calls, the other supplies, and an object between them translates | An adapter that only renames parameters isn't needed, because the Protocol's parameters are positional-only. | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| Facade | Bucket: survives. | a subsystem with many parts and a caller that wants a few operations | A facade over a subsystem with one caller can be inlined. | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| Bridge | Bucket: survives. | a design with two things that vary, such as what an operation means and how it's carried out, so each can change without disturbing the other | A bridge where one axis doesn't vary is a parameter, and the second hierarchy is a cost with no return. | [Adapter, Facade, and Bridge]({{ '/docs/19-adapter-facade-bridge/' | relative_url }}) |
| Decorator (with the `@decorator` syntax) | The two halves share a name and almost nothing else, so they need disambiguating. | Adjustments chosen per consignment need wrappers that nest. | Skip it when the layers don't vary per consignment, because one calculator reads better. | [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) |
| Proxy (surrogate) | - | a stand-in that sits in front of another object and decides whether, when and how the real one is reached | Don't put a caching proxy over data that must be fresh, and write the proxy explicitly where a forwarding one would do. | [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) |
| Proxy (`cached_property`) | and `cached_property` is where the Proxy name needs disambiguating | The lazy-initialisation use of Proxy is a stand-in object that builds the real one on first use. | A value derived from state that changes belongs to a `property`, not `cached_property`. | [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}) |
| Proxy (interception) | That's interception with no surrogate, which is where Proxy is disambiguated | A tracking history comes from a carrier feed that is slow to read, and most callers want only the consignment id. | Fields that aren't known when the class is written belong in a mapping, not in attributes. | [Dynamic attributes: __getattr__ and Proxy as a feature]({{ '/docs/30-dynamic-attributes-and-proxy/' | relative_url }}) |
| Composite | Bucket: survives. | Composite is for the caller who holds something and asks one question without caring whether it's a single item or a bundle of them. | A flat list of consignments with no nesting needs a tuple and `sum`, not a union. | [Composite and Flyweight]({{ '/docs/21-composite-and-flyweight/' | relative_url }}) |
| Flyweight | Both patterns survive in Python | the same few commodities can repeat across many consignments, and each repetition costs an object | A handful of commodities doesn't need a pool. | [Composite and Flyweight]({{ '/docs/21-composite-and-flyweight/' | relative_url }}) |

## Behavioural patterns

Template Method straddles two buckets; the three-way split files it under dissolves, with an ABC hook kept "only where steps share state". Visitor has two rows: a closed set of kinds, which dissolves, and an open set that two teams extend, which dissolves into a single generic function.

| Pattern | Bucket | Force | When not to use it | Chapter |
| --- | --- | --- | --- | --- |
| Strategy | Bucket: dissolves. | a caller must choose among several ways of computing one result without depending on which one it holds | A single rule called from one place is a function, with no registry. | [Strategy: the callable]({{ '/docs/12-strategy-the-callable/' | relative_url }}) |
| Template Method | Bucket: dissolves. | a sequence that has to hold across variants that differ in a few steps | Write a function when there is one variant. | [Template Method and the function alternative]({{ '/docs/13-template-method-and-the-function-alternative/' | relative_url }}) |
| State | Bucket: survives. | The force is that the legal transitions are a business rule that has to be written in one place and checked. | A two-state flag is a `bool`. | [State and finite state machines]({{ '/docs/14-state-and-finite-state-machines/' | relative_url }}) |
| Command | Bucket: survives. | The force is that a change needs an identity of its own. | Call the function when a change is never undone or queued. | [Command, undo, and command queues]({{ '/docs/15-command-undo-and-command-queues/' | relative_url }}) |
| Observer | Bucket: survives. | The handling code shouldn't name any of them, and a new party shouldn't mean an edit to it. | Call the parties directly when the set is fixed at the time the subject is built. | [Observer]({{ '/docs/22-observer/' | relative_url }}) |
| Chain of Responsibility | Bucket: survives. | The code that submits a declaration shouldn't know which check stops it, and a new check shouldn't mean an edit at every call site. | With one check, call the function. | [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}) |
| Mediator | Bucket: survives. | Something has to decide when the reports it is owed have arrived. | If a mediator starts to make a choice that belongs to one colleague, move that rule back to the colleague. | [Mediator and Chain of Responsibility]({{ '/docs/23-mediator-and-chain-of-responsibility/' | relative_url }}) |
| Iterator | Bucket: dissolves. | Both want the events one at a time and neither should care how the history stores them. | Pass the tuple when the data is already in a list that callers index or measure. | [Iterator: generators and the iterator protocol]({{ '/docs/24-iterator-generators-and-the-iterator-protocol/' | relative_url }}) |
| Visitor (closed set) | Bucket: dissolves. | Visitor is for a fixed family of kinds that gets new operations over time. | With one operation over the kinds, write the `match` where it's needed. | [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) |
| Visitor (open set) | For an open set of kinds like this one it dissolves into a single generic function | The customs team owns most of the kinds, and the dangerous goods team adds others that the customs team doesn't own, such as a lithium-ion battery. | A closed set that one team owns wants a `match` with `assert_never`, because mypy then reports a missing kind and a registry can't. | [singledispatch: the Visitor the language gives you]({{ '/docs/28-singledispatch/' | relative_url }}) |
| Memento | Bucket: survives. | Memento is for putting an object back the way it was after a change fails, when the code that asks for the undo shouldn't reach into the object's fields. | With a booking that is itself an immutable value, keep the old value and skip the snapshot class. | [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) |
| Interpreter | Bucket: survives. | Interpreter is for rules that people write down and the program must apply. | With a rule set that doesn't change and that nobody reads back, a plain function is enough. | [Visitor, Memento, and Interpreter]({{ '/docs/25-visitor-memento-interpreter/' | relative_url }}) |

## Beyond the catalogue

Ideas developed without a catalogue entry, or that a catalogue name covers only in part. "Resource acquisition" is a descriptive label, not a catalogue name. The `@decorator` row gives its chapter's verdict, survives; the three-way split files the shared name, not the discipline, under needs disambiguating.

| Pattern | Bucket | Force | When not to use it | Chapter |
| --- | --- | --- | --- | --- |
| Value Object | This pattern dissolves. | The force is four needs at once. Two values with the same content should be equal. A value should be shareable without defensive copies. It should work as a dictionary key or set member. An invariant, such as a positive weight, should hold for as long as the value exists. | A type with a lifecycle and an identity isn't a value. | [Dataclasses and value semantics]({{ '/docs/08-dataclasses-and-value-semantics/' | relative_url }}) |
| Null Object | This pattern dissolves. | The force: a caller that asks for a collaborator that may not exist must not go on as though it did. | A `\| None` threaded through ten signatures costs ten branches where one guard at the boundary would do | [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) |
| "Interface" | "Interface" needs disambiguating: the word covers two mechanisms, and they check at different times. | Each is a question about what a caller may assume about a collaborator: whether it exists, and whether its shape and its construction are right. | A Protocol with one implementation and no substitute is ceremony: the class is the contract. | [Protocol, duck typing, and structural typing with mypy]({{ '/docs/09-protocol-and-structural-typing/' | relative_url }}) |
| Resource acquisition | This pattern survives. | The force: a resource obtained in one place must be released on every path out of the code that uses it, and what release means is a decision. | A resource with no release step doesn't need a manager. | [Context managers: deterministic cleanup]({{ '/docs/10-context-managers/' | relative_url }}) |
| The `@decorator` discipline | so the bucket is survives | What stays design is the discipline around it | When behaviour has to vary per object while the program runs, a decorator can't help, because it fixes the wrapping when the function is defined | [Decorators done right]({{ '/docs/26-decorators-done-right/' | relative_url }}) |
| Metaclass registry | the pattern dissolves | A registry that fills as each carrier class is created spares the booking code from knowing the list, and it's the job a metaclass registry used to do. | A metaclass is the wrong tool for anything `__init_subclass__`, a class decorator or a descriptor does. | [Metaclasses, __init_subclass__, and registries]({{ '/docs/29-metaclasses-init-subclass-and-registries/' | relative_url }}) |
| If-chain dispatch | What dissolves is the structure built around it | The force, picking behaviour by data, is still there. | Keep the branch when the cases need different arguments, or when they must run in a fixed order | [Shortcut patterns: dict dispatch, function tables, and EAFP]({{ '/docs/31-shortcut-patterns-dict-dispatch-and-eafp/' | relative_url }}) |

## Named elsewhere, without a bucket

These techniques and anti-patterns are named, with no bucket. Each line gives the chapter and a clause from it.

- Seam, in [Seams in Python: monkeypatch, injection, and duck typing]({{ '/docs/33-seams-in-python/' | relative_url }}): "A seam is a place where that change can be made from outside."
- Characterisation test, in [Dependency-breaking techniques for modern Python]({{ '/docs/34-dependency-breaking-techniques/' | relative_url }}): "A characterisation test records what code does, so that a change can be told apart from a fix."
- Strangler Fig, in [Refactor or rewrite]({{ '/docs/36-refactor-or-rewrite/' | relative_url }}): Fowler's description of the approach is to "move bits of behavior from the legacy system into the new code base."
- Monitor Object, in [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}): "so the class is a Monitor Object in the vocabulary of *Pattern-Oriented Software Architecture, Volume 2*"
- Active Object, in [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}): "The worker and its queue have the shape that *Pattern-Oriented Software Architecture, Volume 2* names Active Object."

[Anti-patterns and pattern misuse]({{ '/docs/32-anti-patterns-and-pattern-misuse/' | relative_url }}) defines an anti-pattern as "a recurring structure whose costs outweigh its benefits in the context it sits in". Three are developed there:

- The overbuilt rating engine, in the section "The rating function and its overbuilt twin".
- Getters and setters: "A getter and setter pair is a promise that the field might need behaviour later."
- The service locator: "A service locator is a registry that a class asks for its collaborators, by name, when it needs them."

## For deeper coverage

The method behind the rows is in [Patterns as decisions under forces]({{ '/docs/01-patterns-as-decisions-under-forces/' | relative_url }}), and the placement of each pattern is in [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}). The pattern names come from *Design Patterns: Elements of Reusable Object-Oriented Software* by Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides (Addison-Wesley, 1994): its Introduction defines the pattern template, its Motivation and Applicability sections describe the forces, and its Consequences sections list what each pattern buys and costs. Christopher Alexander, from whom it took the idea of forces, is credited in Patterns as decisions under forces. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
