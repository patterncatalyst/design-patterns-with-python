# r21 pattern-to-force census (evidence E, step X1b)

Dated 2026-11-07, at HEAD bbe9b9b on release/r21, run from the repository root. This is the witness file for Appendix E. Each row below is one pattern in one developing chapter. Each Bucket, Force and When not to use it cell is a clause copied byte for byte from that chapter, with the file and line where it occurs and the `grep -nF` command that finds it. Every command was run and prints exactly one line, and a substring count over the whole file gives 1 for every clause.

## How to read this file

- A clause is a contiguous substring of one line of the chapter. Nothing is reworded, joined or elided. A clause never contains a link or Liquid markup, so no link-text substitution was needed.
- Run the commands from the repository root. The line number is at HEAD above and moves if a chapter is edited, so the check is on the text (plan, Risks, "E line drift").
- A clause may begin or end mid-sentence where the sentence continues into a link or a second clause. Where a clause is a lowercase noun phrase, the chapter states the force in that phrase and not in a sentence of its own.
- Rows follow the plan: 5 creational, 9 structural, 12 behavioural, 7 beyond the catalogue, 33 in all. Proxy has three rows, Visitor two. Decorator has one row here because the plan's table names ch20 for the pattern and ch26 for the discipline, which has its own row in the last table.

## Row counts

| Table | Rows |
| --- | --- |
| Creational | 5 |
| Structural | 9 |
| Behavioural | 12 |
| Beyond the catalogue | 7 |
| Closing list (no bucket) | 9 items (5 techniques, 1 definition, 3 anti-patterns) |

## Gaps: cells with no verbatim clause

- **Proxy (surrogate), Bucket** (`_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`). The chapter sorts the Decorator pair (line 41) and the Proxy section (lines 123 to 196) never says dissolves, survives or needs disambiguating about the surrogate. `grep -nE 'dissolve|surviv|disambiguat|straddl|bucket' ` over the chapter finds line 41 (the pair) and nothing in the Proxy section. Proposed cut: leave the Bucket cell of this row empty with a dash, and let the one-line row note say that the chapter states no bucket for the surrogate and that the map files Proxy under needs disambiguating (the map's own line, quoted below, is the only source). The other two Proxy rows keep their chapters' own words. Rejected alternative: borrow ch27:22 or ch30:22, which are other chapters' words about other rows.

## Verbatim, but the chapter does not use the word force

Every Force cell below is verbatim. These are the rows where the chapter states the pressure in a plain sentence or phrase and does not write "the force": Adapter, Facade, Bridge, Decorator, Proxy (all three), Composite, Flyweight, Template Method (the chapter says "The force is the one above" on line 34 and the clause is the sentence the phrase points back to, from line 34 itself), Observer, Chain of Responsibility, Mediator, Iterator, Visitor (both), Memento, Interpreter, Singleton, "Interface", the `@decorator` discipline, Metaclass registry. Where a chapter does write "The force is ..." or "The force: ...", the clause keeps it: Factory Method, Abstract Factory, Builder, Prototype, Strategy, State, Command, Value Object, Null Object, Resource acquisition, If-chain dispatch. For the first group the prose of E should read the cell as the chapter's statement of the pressure; it must not add the word.

Two cells are long or borrowed and the cut is cheap if the table is too wide:

- **Value Object, Force** is five contiguous sentences (the chapter's list of four needs). A one-sentence cut, `The force is four needs at once.`, is also verbatim but loses the needs.
- **Singleton, Force** is `load this once and let everyone read it`, the chapter's quoted statement of the default answer to the force (ch18:41). The chapter has no sentence that begins "The force".

## Conflicts with the three-way split's map

The map is `_docs/03-the-three-way-split.md`. Link cells are omitted from the quoted rows below (they hold only links), and links inside quoted prose are reduced to their text with the omission marked.

### 1. Template Method: the map says Dissolves, the chapter says straddles

- `_docs/03-the-three-way-split.md:48`: > | Template Method | Dissolves | A function taking hook callables; an ABC hook only where steps share state | (link to the chapter) |
- `_docs/03-the-three-way-split.md:18`: > Explain why Command, Template Method and Visitor straddle two buckets.
- `_docs/03-the-three-way-split.md:157`: > ## Patterns that straddle two buckets
- `_docs/03-the-three-way-split.md:163`: > Template Method fixes the order of steps and lets variants supply some of them. The example's `declare_customs` is a function that takes hooks: it classifies, assesses duty and certifies in that order, and a `CustomsHooks` value supplies the varying parts per destination. That dissolves the inheritance structure. Where the steps share state and code that every hook would otherwise have to carry, an object with overridable methods remains the right shape, and the Template Method chapter says where that line falls.
- `_docs/13-template-method-and-the-function-alternative.md:36`: > The pattern straddles two buckets. The hook structure dissolves: a function that takes the varying steps as arguments fixes the order as well as a base class does, with nothing to inherit from. The inheritance form survives where a family of variants shares state and code across several steps. (the sentence continues with a link to the map: "Where that line falls is the question [The three-way split: dissolve, survive, disambiguate] left open for this pattern, and the sections below answer it." Link reduced to its text.)

Handling: the row follows ch13 (straddles). The map's own prose (ch03:18 and ch03:163) already says Template Method straddles; only its table row (ch03:48) files it under Dissolves. ch03:18 also lists Command and Visitor as straddling while the table files Command under Survives (ch03:57) and Visitor under Dissolves (ch03:51); ch15:42 says "So the bucket is survives, with the deferred call dissolving." and ch25:36 says "The bucket is dissolves", so those two rows agree with the map's table and the E prose need not note them.

### 2. "Decorators done right": the chapter attributes its bucket to the map, which does not sort it (decision 7)

- `_docs/26-decorators-done-right.md:22`: > What stays design is the discipline around it, so the bucket is survives, as [The three-way split: dissolve, survive, disambiguate] sorts it. (link reduced to its text; the sentence is `What stays design is the discipline around it, so the bucket is survives, as` followed by the link and `sorts it.`)
- `_docs/03-the-three-way-split.md:70`: > | Decorator pattern vs `@decorator` syntax | Needs disambiguating | Wrapper objects composed at runtime vs a function rebinding at definition time | (links to ch20 and ch26) |
- `_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md:41`: > The syntax is a language feature. A stack chosen per request is still a design. The two halves share a name and almost nothing else, so they need disambiguating.

Handling: ch26's own verdict is survives (the discipline around the `@` syntax). The map's row sorts the pair, pattern and syntax, as needs disambiguating, and links ch26 from that row. The two answer different questions, the shared name and the discipline, so the row follows ch26 and a note says the map files the pair under needs disambiguating. X4b rewrites ch26:22, so the Bucket clause recorded for that row (`so the bucket is survives`) must be re-checked after X4b; the Force clause on the same line (`What stays design is the discipline around it`) survives the rewrite only if X4b keeps it.

### 3. Proxy: the map files it under needs disambiguating, the surrogate's chapter files nothing

- `_docs/03-the-three-way-split.md:72`: > | Proxy | Needs disambiguating | A surrogate object vs attribute interception with `__getattr__`, `property` and `cached_property` | (links to ch30 and ch27) |
- `_docs/03-the-three-way-split.md:135`: > **Proxy.** The catalogue's proxy is a surrogate object standing in for another. Python adds a second sense: intercepting attribute access with `__getattr__`, `property` or `cached_property`. They are different tools. `CarrierGatewayProxy` is the surrogate
- `_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md:125`: > *Design Patterns* gives Proxy to a stand-in that sits in front of another object and decides whether, when and how the real one is reached.
- `_docs/27-descriptors-and-properties.md:22`: > and `cached_property` is where the Proxy name needs disambiguating (ch27:177 repeats the phrase)
- `_docs/30-dynamic-attributes-and-proxy.md:22`: > That's interception with no surrogate, which is where Proxy is disambiguated

Handling: three rows. Interception (ch30) and `cached_property` (ch27) say needs disambiguating in their own words, so they agree with the map. The surrogate (ch20) states no bucket, so its Bucket cell is empty (see Gaps) and the E prose says the map files Proxy under needs disambiguating, as one sentence about the pair of senses, without attributing it to ch20.

## Differences from the plan

- **Proxy (surrogate) has no Bucket clause.** The plan's evidence E says "none stated in ch20; ch03 line 72 and ch30 line 22", and the spec lists a row for it. The row exists with an empty Bucket cell and a proposed cut (Gaps).
- **Composite and Chain of Responsibility cite different lines from the plan.** The plan has 21:23 for both Composite and Flyweight and 23:30 for both Mediator and Chain of Responsibility. The census gives Composite its own sentence (21:39, `so the bucket is survives`) and Chain of Responsibility its own (23:38, `The bucket is survives`), and keeps the shared sentences (21:23, 23:30) for Flyweight and Mediator. Adapter, Facade and Bridge share 19:36 as in the plan.
- **Decorator has one row in the structural table.** The plan's E spec lists "Decorator (the pattern, ch20)" there and the `@decorator` discipline (ch26) in the beyond table, as here. Decision 8 says "Decorator in two" chapters, which is these two rows.
- **Closing list has 9 items, not 7.** Decision 8 names Seam, Monitor Object, Active Object, Strangler Fig and the three anti-patterns. The spec's item 7 also names the characterisation test, so it is recorded, marked as such. Drop it if decision 8 governs. The anti-patterns also get a definition line (ch32:22) that is not one of the three, for the closing sentence of E.
- **Strangler Fig has no sentence beginning with its name in ch36's section.** The plan cites "the heading `A strangler-style router`". The heading (ch36:112) does not contain the words Strangler Fig, so the defining clause is Fowler's description in ch36:114, which names the approach by the link text of ch36:24 (`Strangler Fig`). The heading is `## A strangler-style router` for a title-only citation.
- **Resource acquisition.** ch10:32 says the label is "descriptive, not a catalogue name", as the plan notes; the row keeps the chapter's words and E may add the note.
- **Line numbers.** Every bucket line the plan lists was re-checked and matches the plan except where the two items above say otherwise. "No `_docs` file contains an em or en dash" and the curly-apostrophe list in the plan were not re-audited; no clause below contains a curly apostrophe (they were matched with straight ones).

# Census

## Creational patterns (5 rows)

### Factory Method

- Chapter: "Factory Method and Abstract Factory" (`_docs/16-factory-method-and-abstract-factory.md`)

- Bucket: `16:34`
  - clause: `## Factory Method dissolves`
  - check: `grep -nF '## Factory Method dissolves' _docs/16-factory-method-and-abstract-factory.md`

- Force: `16:36`
  - clause: `The force is real: the caller wants a gateway for a carrier and shouldn't know which gateway class that is.`
  - check: `grep -nF 'The force is real: the caller wants a gateway for a carrier and shouldn'"'"'t know which gateway class that is.' _docs/16-factory-method-and-abstract-factory.md`

- When not to use it: `16:189`
  - clause: `With one carrier, call the class.`
  - check: `grep -nF 'With one carrier, call the class.' _docs/16-factory-method-and-abstract-factory.md`

### Abstract Factory

- Chapter: "Factory Method and Abstract Factory" (`_docs/16-factory-method-and-abstract-factory.md`)

- Bucket: `16:130`
  - clause: `The bucket is survives.`
  - check: `grep -nF 'The bucket is survives.' _docs/16-factory-method-and-abstract-factory.md`

- Force: `16:130`
  - clause: `The force is that products must come from the same family, and a language that stores callables doesn't choose the family.`
  - check: `grep -nF 'The force is that products must come from the same family, and a language that stores callables doesn'"'"'t choose the family.' _docs/16-factory-method-and-abstract-factory.md`

- When not to use it: `16:189`
  - clause: `If the products don't have to match, pass them separately.`
  - check: `grep -nF 'If the products don'"'"'t have to match, pass them separately.' _docs/16-factory-method-and-abstract-factory.md`

### Builder

- Chapter: "Builder, dataclasses, and Prototype" (`_docs/17-builder-dataclasses-and-prototype.md`)

- Bucket: `17:36`
  - clause: `so the bucket is dissolves`
  - check: `grep -nF 'so the bucket is dissolves' _docs/17-builder-dataclasses-and-prototype.md`

- Force: `17:36`
  - clause: `The force that remains is an object with many parts, several of them optional, that has to be complete and valid before anyone uses it.`
  - check: `grep -nF 'The force that remains is an object with many parts, several of them optional, that has to be complete and valid before anyone uses it.' _docs/17-builder-dataclasses-and-prototype.md`

- When not to use it: `17:199`
  - clause: `A builder kept only for a fluent style gives up the type checker's missing-argument report in exchange for a chain of method calls.`
  - check: `grep -nF 'A builder kept only for a fluent style gives up the type checker'"'"'s missing-argument report in exchange for a chain of method calls.' _docs/17-builder-dataclasses-and-prototype.md`

### Prototype

- Chapter: "Builder, dataclasses, and Prototype" (`_docs/17-builder-dataclasses-and-prototype.md`)

- Bucket: `17:130`
  - clause: `That dissolves too.`
  - check: `grep -nF 'That dissolves too.' _docs/17-builder-dataclasses-and-prototype.md`

- Force: `17:130`
  - clause: `The force that remains is a new object that starts as a copy of a configured one`
  - check: `grep -nF 'The force that remains is a new object that starts as a copy of a configured one' _docs/17-builder-dataclasses-and-prototype.md`

- When not to use it: `17:199`
  - clause: `Don't deep-copy a lock; build another.`
  - check: `grep -nF 'Don'"'"'t deep-copy a lock; build another.' _docs/17-builder-dataclasses-and-prototype.md`

### Singleton

- Chapter: "Singleton: module, Borg, and metaclass" (`_docs/18-singleton-module-borg-metaclass.md`)

- Bucket: `18:41`
  - clause: `The bucket is needs disambiguating`
  - check: `grep -nF 'The bucket is needs disambiguating' _docs/18-singleton-module-borg-metaclass.md`

- Force: `18:41`
  - clause: `load this once and let everyone read it`
  - check: `grep -nF 'load this once and let everyone read it' _docs/18-singleton-module-borg-metaclass.md`

- When not to use it: `18:193`
  - clause: `A class whose only reason to exist is to be single is a module.`
  - check: `grep -nF 'A class whose only reason to exist is to be single is a module.' _docs/18-singleton-module-borg-metaclass.md`

## Structural patterns (9 rows)

### Adapter

- Chapter: "Adapter, Facade, and Bridge" (`_docs/19-adapter-facade-bridge.md`)
- Note: Bucket sentence is shared by Adapter, Facade and Bridge.

- Bucket: `19:36`
  - clause: `All three patterns in this chapter survive.`
  - check: `grep -nF 'All three patterns in this chapter survive.' _docs/19-adapter-facade-bridge.md`

- Force: `19:38`
  - clause: `two parts that disagree about shape: one calls, the other supplies, and an object between them translates`
  - check: `grep -nF 'two parts that disagree about shape: one calls, the other supplies, and an object between them translates' _docs/19-adapter-facade-bridge.md`

- When not to use it: `19:221`
  - clause: `An adapter that only renames parameters isn't needed, because the Protocol's parameters are positional-only.`
  - check: `grep -nF 'An adapter that only renames parameters isn'"'"'t needed, because the Protocol'"'"'s parameters are positional-only.' _docs/19-adapter-facade-bridge.md`

### Facade

- Chapter: "Adapter, Facade, and Bridge" (`_docs/19-adapter-facade-bridge.md`)
- Note: Bucket sentence is shared by Adapter, Facade and Bridge.

- Bucket: `19:36`
  - clause: `All three patterns in this chapter survive.`
  - check: `grep -nF 'All three patterns in this chapter survive.' _docs/19-adapter-facade-bridge.md`

- Force: `19:136`
  - clause: `a subsystem with many parts and a caller that wants a few operations`
  - check: `grep -nF 'a subsystem with many parts and a caller that wants a few operations' _docs/19-adapter-facade-bridge.md`

- When not to use it: `19:221`
  - clause: `A facade over a subsystem with one caller can be inlined.`
  - check: `grep -nF 'A facade over a subsystem with one caller can be inlined.' _docs/19-adapter-facade-bridge.md`

### Bridge

- Chapter: "Adapter, Facade, and Bridge" (`_docs/19-adapter-facade-bridge.md`)
- Note: Bucket sentence is shared by Adapter, Facade and Bridge.

- Bucket: `19:36`
  - clause: `All three patterns in this chapter survive.`
  - check: `grep -nF 'All three patterns in this chapter survive.' _docs/19-adapter-facade-bridge.md`

- Force: `19:166`
  - clause: `a design with two things that vary, such as what an operation means and how it's carried out, so each can change without disturbing the other`
  - check: `grep -nF 'a design with two things that vary, such as what an operation means and how it'"'"'s carried out, so each can change without disturbing the other' _docs/19-adapter-facade-bridge.md`

- When not to use it: `19:221`
  - clause: `A bridge where one axis doesn't vary is a parameter, and the second hierarchy is a cost with no return.`
  - check: `grep -nF 'A bridge where one axis doesn'"'"'t vary is a parameter, and the second hierarchy is a cost with no return.' _docs/19-adapter-facade-bridge.md`

### Decorator (the pattern, with the `@decorator` syntax)

- Chapter: "Decorator the pattern vs @decorator the syntax, and Proxy" (`_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`)
- Note: The bucket is for the pair, pattern and syntax.

- Bucket: `20:41`
  - clause: `The two halves share a name and almost nothing else, so they need disambiguating.`
  - check: `grep -nF 'The two halves share a name and almost nothing else, so they need disambiguating.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`

- Force: `20:47`
  - clause: `Adjustments chosen per consignment need wrappers that nest.`
  - check: `grep -nF 'Adjustments chosen per consignment need wrappers that nest.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`

- When not to use it: `20:200`
  - clause: `Skip it when the layers don't vary per consignment, because one calculator reads better.`
  - check: `grep -nF 'Skip it when the layers don'"'"'t vary per consignment, because one calculator reads better.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`

### Proxy (surrogate)

- Chapter: "Decorator the pattern vs @decorator the syntax, and Proxy" (`_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`)
- Note: Chapter states no bucket for the surrogate.

- Bucket: **NO VERBATIM CLAUSE** in `_docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md` (see Gaps)

- Force: `20:125`
  - clause: `a stand-in that sits in front of another object and decides whether, when and how the real one is reached`
  - check: `grep -nF 'a stand-in that sits in front of another object and decides whether, when and how the real one is reached' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`

- When not to use it: `20:200`
  - clause: `Don't put a caching proxy over data that must be fresh, and write the proxy explicitly where a forwarding one would do.`
  - check: `grep -nF 'Don'"'"'t put a caching proxy over data that must be fresh, and write the proxy explicitly where a forwarding one would do.' _docs/20-decorator-pattern-vs-decorator-syntax-and-proxy.md`

### Proxy (`cached_property`)

- Chapter: "Descriptors and properties" (`_docs/27-descriptors-and-properties.md`)

- Bucket: `27:22`
  - clause: ``and `cached_property` is where the Proxy name needs disambiguating``
  - check: `grep -nF 'and `cached_property` is where the Proxy name needs disambiguating' _docs/27-descriptors-and-properties.md`

- Force: `27:177`
  - clause: `The lazy-initialisation use of Proxy is a stand-in object that builds the real one on first use.`
  - check: `grep -nF 'The lazy-initialisation use of Proxy is a stand-in object that builds the real one on first use.' _docs/27-descriptors-and-properties.md`

- When not to use it: `27:201`
  - clause: ``A value derived from state that changes belongs to a `property`, not `cached_property`.``
  - check: `grep -nF 'A value derived from state that changes belongs to a `property`, not `cached_property`.' _docs/27-descriptors-and-properties.md`

### Proxy (interception)

- Chapter: "Dynamic attributes: __getattr__ and Proxy as a feature" (`_docs/30-dynamic-attributes-and-proxy.md`)

- Bucket: `30:22`
  - clause: `That's interception with no surrogate, which is where Proxy is disambiguated`
  - check: `grep -nF 'That'"'"'s interception with no surrogate, which is where Proxy is disambiguated' _docs/30-dynamic-attributes-and-proxy.md`

- Force: `30:22`
  - clause: `A tracking history comes from a carrier feed that is slow to read, and most callers want only the consignment id.`
  - check: `grep -nF 'A tracking history comes from a carrier feed that is slow to read, and most callers want only the consignment id.' _docs/30-dynamic-attributes-and-proxy.md`

- When not to use it: `30:190`
  - clause: `Fields that aren't known when the class is written belong in a mapping, not in attributes.`
  - check: `grep -nF 'Fields that aren'"'"'t known when the class is written belong in a mapping, not in attributes.' _docs/30-dynamic-attributes-and-proxy.md`

### Composite

- Chapter: "Composite and Flyweight" (`_docs/21-composite-and-flyweight.md`)

- Bucket: `21:39`
  - clause: `so the bucket is survives`
  - check: `grep -nF 'so the bucket is survives' _docs/21-composite-and-flyweight.md`

- Force: `21:39`
  - clause: `Composite is for the caller who holds something and asks one question without caring whether it's a single item or a bundle of them.`
  - check: `grep -nF 'Composite is for the caller who holds something and asks one question without caring whether it'"'"'s a single item or a bundle of them.' _docs/21-composite-and-flyweight.md`

- When not to use it: `21:230`
  - clause: ``A flat list of consignments with no nesting needs a tuple and `sum`, not a union.``
  - check: `grep -nF 'A flat list of consignments with no nesting needs a tuple and `sum`, not a union.' _docs/21-composite-and-flyweight.md`

### Flyweight

- Chapter: "Composite and Flyweight" (`_docs/21-composite-and-flyweight.md`)

- Bucket: `21:23`
  - clause: `Both patterns survive in Python`
  - check: `grep -nF 'Both patterns survive in Python' _docs/21-composite-and-flyweight.md`

- Force: `21:23`
  - clause: `the same few commodities can repeat across many consignments, and each repetition costs an object`
  - check: `grep -nF 'the same few commodities can repeat across many consignments, and each repetition costs an object' _docs/21-composite-and-flyweight.md`

- When not to use it: `21:232`
  - clause: `A handful of commodities doesn't need a pool.`
  - check: `grep -nF 'A handful of commodities doesn'"'"'t need a pool.' _docs/21-composite-and-flyweight.md`

## Behavioural patterns (12 rows)

### Strategy

- Chapter: "Strategy: the callable" (`_docs/12-strategy-the-callable.md`)

- Bucket: `12:34`
  - clause: `This pattern dissolves, because a feature resolves the force without the pattern's structure.`
  - check: `grep -nF 'This pattern dissolves, because a feature resolves the force without the pattern'"'"'s structure.' _docs/12-strategy-the-callable.md`

- Force: `12:34`
  - clause: `The force is intact and the structure is what goes.`
  - check: `grep -nF 'The force is intact and the structure is what goes.' _docs/12-strategy-the-callable.md`

- When not to use it: `12:184`
  - clause: `A single rule called from one place is a function, with no registry.`
  - check: `grep -nF 'A single rule called from one place is a function, with no registry.' _docs/12-strategy-the-callable.md`

### Template Method

- Chapter: "Template Method and the function alternative" (`_docs/13-template-method-and-the-function-alternative.md`)
- Note: Conflict 1 with the map.

- Bucket: `13:36`
  - clause: `The pattern straddles two buckets.`
  - check: `grep -nF 'The pattern straddles two buckets.' _docs/13-template-method-and-the-function-alternative.md`

- Force: `13:34`
  - clause: `a sequence that has to hold across variants that differ in a few steps`
  - check: `grep -nF 'a sequence that has to hold across variants that differ in a few steps' _docs/13-template-method-and-the-function-alternative.md`

- When not to use it: `13:214`
  - clause: `Write a function when there is one variant.`
  - check: `grep -nF 'Write a function when there is one variant.' _docs/13-template-method-and-the-function-alternative.md`

### State

- Chapter: "State and finite state machines" (`_docs/14-state-and-finite-state-machines.md`)

- Bucket: `14:34`
  - clause: `The pattern survives, and the transition table is the design.`
  - check: `grep -nF 'The pattern survives, and the transition table is the design.' _docs/14-state-and-finite-state-machines.md`

- Force: `14:34`
  - clause: `The force is that the legal transitions are a business rule that has to be written in one place and checked.`
  - check: `grep -nF 'The force is that the legal transitions are a business rule that has to be written in one place and checked.' _docs/14-state-and-finite-state-machines.md`

- When not to use it: `14:200`
  - clause: ``A two-state flag is a `bool`.``
  - check: `grep -nF 'A two-state flag is a `bool`.' _docs/14-state-and-finite-state-machines.md`

### Command

- Chapter: "Command, undo, and command queues" (`_docs/15-command-undo-and-command-queues.md`)

- Bucket: `15:42`
  - clause: `So the bucket is survives, with the deferred call dissolving.`
  - check: `grep -nF 'So the bucket is survives, with the deferred call dissolving.' _docs/15-command-undo-and-command-queues.md`

- Force: `15:36`
  - clause: `The force is that a change needs an identity of its own.`
  - check: `grep -nF 'The force is that a change needs an identity of its own.' _docs/15-command-undo-and-command-queues.md`

- When not to use it: `15:220`
  - clause: `Call the function when a change is never undone or queued.`
  - check: `grep -nF 'Call the function when a change is never undone or queued.' _docs/15-command-undo-and-command-queues.md`

### Observer

- Chapter: "Observer" (`_docs/22-observer.md`)

- Bucket: `22:58`
  - clause: `The bucket is survives`
  - check: `grep -nF 'The bucket is survives' _docs/22-observer.md`

- Force: `22:22`
  - clause: `The handling code shouldn't name any of them, and a new party shouldn't mean an edit to it.`
  - check: `grep -nF 'The handling code shouldn'"'"'t name any of them, and a new party shouldn'"'"'t mean an edit to it.' _docs/22-observer.md`

- When not to use it: `22:217`
  - clause: `Call the parties directly when the set is fixed at the time the subject is built.`
  - check: `grep -nF 'Call the parties directly when the set is fixed at the time the subject is built.' _docs/22-observer.md`

### Chain of Responsibility

- Chapter: "Mediator and Chain of Responsibility" (`_docs/23-mediator-and-chain-of-responsibility.md`)

- Bucket: `23:38`
  - clause: `The bucket is survives`
  - check: `grep -nF 'The bucket is survives' _docs/23-mediator-and-chain-of-responsibility.md`

- Force: `23:22`
  - clause: `The code that submits a declaration shouldn't know which check stops it, and a new check shouldn't mean an edit at every call site.`
  - check: `grep -nF 'The code that submits a declaration shouldn'"'"'t know which check stops it, and a new check shouldn'"'"'t mean an edit at every call site.' _docs/23-mediator-and-chain-of-responsibility.md`

- When not to use it: `23:182`
  - clause: `With one check, call the function.`
  - check: `grep -nF 'With one check, call the function.' _docs/23-mediator-and-chain-of-responsibility.md`

### Mediator

- Chapter: "Mediator and Chain of Responsibility" (`_docs/23-mediator-and-chain-of-responsibility.md`)
- Note: Bucket sentence covers both patterns of the chapter.

- Bucket: `23:30`
  - clause: `both patterns survive because Python's syntax doesn't make those decisions for you`
  - check: `grep -nF 'both patterns survive because Python'"'"'s syntax doesn'"'"'t make those decisions for you' _docs/23-mediator-and-chain-of-responsibility.md`

- Force: `23:22`
  - clause: `something has to decide when both have reported`
  - check: `grep -nF 'something has to decide when both have reported' _docs/23-mediator-and-chain-of-responsibility.md`

- When not to use it: `23:182`
  - clause: `if a mediator starts to make a decision that belongs to one colleague, move that rule back to the colleague`
  - check: `grep -nF 'if a mediator starts to make a decision that belongs to one colleague, move that rule back to the colleague' _docs/23-mediator-and-chain-of-responsibility.md`

### Iterator

- Chapter: "Iterator: generators and the iterator protocol" (`_docs/24-iterator-generators-and-the-iterator-protocol.md`)

- Bucket: `24:47`
  - clause: `The bucket is dissolves`
  - check: `grep -nF 'The bucket is dissolves' _docs/24-iterator-generators-and-the-iterator-protocol.md`

- Force: `24:22`
  - clause: `Both want the events one at a time and neither should care how the history stores them.`
  - check: `grep -nF 'Both want the events one at a time and neither should care how the history stores them.' _docs/24-iterator-generators-and-the-iterator-protocol.md`

- When not to use it: `24:151`
  - clause: `Pass the tuple when the data is already in a list that callers index or measure.`
  - check: `grep -nF 'Pass the tuple when the data is already in a list that callers index or measure.' _docs/24-iterator-generators-and-the-iterator-protocol.md`

### Visitor (closed set)

- Chapter: "Visitor, Memento, and Interpreter" (`_docs/25-visitor-memento-interpreter.md`)

- Bucket: `25:36`
  - clause: `The bucket is dissolves`
  - check: `grep -nF 'The bucket is dissolves' _docs/25-visitor-memento-interpreter.md`

- Force: `25:36`
  - clause: `Visitor is for a fixed family of kinds that gets new operations over time.`
  - check: `grep -nF 'Visitor is for a fixed family of kinds that gets new operations over time.' _docs/25-visitor-memento-interpreter.md`

- When not to use it: `25:218`
  - clause: ``With one operation over the kinds, write the `match` where it's needed.``
  - check: `grep -nF 'With one operation over the kinds, write the `match` where it'"'"'s needed.' _docs/25-visitor-memento-interpreter.md`

### Visitor (open set)

- Chapter: "singledispatch: the Visitor the language gives you" (`_docs/28-singledispatch.md`)

- Bucket: `28:22`
  - clause: `For an open set of kinds like this one it dissolves into a single generic function`
  - check: `grep -nF 'For an open set of kinds like this one it dissolves into a single generic function' _docs/28-singledispatch.md`

- Force: `28:22`
  - clause: `The customs team owns most of the kinds, and the dangerous goods team adds others that the customs team doesn't own, such as a lithium-ion battery.`
  - check: `grep -nF 'The customs team owns most of the kinds, and the dangerous goods team adds others that the customs team doesn'"'"'t own, such as a lithium-ion battery.' _docs/28-singledispatch.md`

- When not to use it: `28:149`
  - clause: ``A closed set that one team owns wants a `match` with `assert_never`, because mypy then reports a missing kind and a registry can't.``
  - check: `grep -nF 'A closed set that one team owns wants a `match` with `assert_never`, because mypy then reports a missing kind and a registry can'"'"'t.' _docs/28-singledispatch.md`

### Memento

- Chapter: "Visitor, Memento, and Interpreter" (`_docs/25-visitor-memento-interpreter.md`)

- Bucket: `25:105`
  - clause: `The bucket is survives, because two decisions stay with you: what to capture, and what must not roll back.`
  - check: `grep -nF 'The bucket is survives, because two decisions stay with you: what to capture, and what must not roll back.' _docs/25-visitor-memento-interpreter.md`

- Force: `25:105`
  - clause: `Memento is for putting an object back the way it was after a change fails, when the code that asks for the undo shouldn't reach into the object's fields.`
  - check: `grep -nF 'Memento is for putting an object back the way it was after a change fails, when the code that asks for the undo shouldn'"'"'t reach into the object'"'"'s fields.' _docs/25-visitor-memento-interpreter.md`

- When not to use it: `25:218`
  - clause: `With a booking whose originator is frozen, keep the old value and skip the snapshot class.`
  - check: `grep -nF 'With a booking whose originator is frozen, keep the old value and skip the snapshot class.' _docs/25-visitor-memento-interpreter.md`

### Interpreter

- Chapter: "Visitor, Memento, and Interpreter" (`_docs/25-visitor-memento-interpreter.md`)

- Bucket: `25:153`
  - clause: `The bucket is survives, because the grammar and its readings are still design.`
  - check: `grep -nF 'The bucket is survives, because the grammar and its readings are still design.' _docs/25-visitor-memento-interpreter.md`

- Force: `25:153`
  - clause: `Interpreter is for rules that people write down and the program must apply.`
  - check: `grep -nF 'Interpreter is for rules that people write down and the program must apply.' _docs/25-visitor-memento-interpreter.md`

- When not to use it: `25:218`
  - clause: `With a rule set that doesn't change and that nobody reads back, a plain function is enough.`
  - check: `grep -nF 'With a rule set that doesn'"'"'t change and that nobody reads back, a plain function is enough.' _docs/25-visitor-memento-interpreter.md`

## Beyond the catalogue (7 rows)

### Value Object

- Chapter: "Dataclasses and value semantics" (`_docs/08-dataclasses-and-value-semantics.md`)

- Bucket: `08:38`
  - clause: `This pattern dissolves.`
  - check: `grep -nF 'This pattern dissolves.' _docs/08-dataclasses-and-value-semantics.md`

- Force: `08:34`
  - clause: `The force is four needs at once. Two values with the same content should be equal. A value should be shareable without defensive copies. It should work as a dictionary key or set member. An invariant, such as a positive weight, should hold for as long as the value exists.`
  - check: `grep -nF 'The force is four needs at once. Two values with the same content should be equal. A value should be shareable without defensive copies. It should work as a dictionary key or set member. An invariant, such as a positive weight, should hold for as long as the value exists.' _docs/08-dataclasses-and-value-semantics.md`

- When not to use it: `08:163`
  - clause: `A type with a lifecycle and an identity isn't a value.`
  - check: `grep -nF 'A type with a lifecycle and an identity isn'"'"'t a value.' _docs/08-dataclasses-and-value-semantics.md`

### Null Object

- Chapter: "Protocol, duck typing, and structural typing with mypy" (`_docs/09-protocol-and-structural-typing.md`)

- Bucket: `09:62`
  - clause: `This pattern dissolves.`
  - check: `grep -nF 'This pattern dissolves.' _docs/09-protocol-and-structural-typing.md`

- Force: `09:60`
  - clause: `The force: a caller that asks for a collaborator that may not exist must not go on as though it did.`
  - check: `grep -nF 'The force: a caller that asks for a collaborator that may not exist must not go on as though it did.' _docs/09-protocol-and-structural-typing.md`

- When not to use it: `09:205`
  - clause: ``A `| None` threaded through ten signatures costs ten branches where one guard at the boundary would do``
  - check: `grep -nF 'A `| None` threaded through ten signatures costs ten branches where one guard at the boundary would do' _docs/09-protocol-and-structural-typing.md`

### "Interface"

- Chapter: "Protocol, duck typing, and structural typing with mypy" (`_docs/09-protocol-and-structural-typing.md`)

- Bucket: `09:162`
  - clause: `"Interface" needs disambiguating: the word covers two mechanisms, and they check at different times.`
  - check: `grep -nF '"Interface" needs disambiguating: the word covers two mechanisms, and they check at different times.' _docs/09-protocol-and-structural-typing.md`

- Force: `09:24`
  - clause: `Each is a question about what a caller may assume about a collaborator: whether it exists, and whether its shape and its construction are right.`
  - check: `grep -nF 'Each is a question about what a caller may assume about a collaborator: whether it exists, and whether its shape and its construction are right.' _docs/09-protocol-and-structural-typing.md`

- When not to use it: `09:205`
  - clause: `A Protocol with one implementation and no substitute is ceremony: the class is the contract.`
  - check: `grep -nF 'A Protocol with one implementation and no substitute is ceremony: the class is the contract.' _docs/09-protocol-and-structural-typing.md`

### Resource acquisition

- Chapter: "Context managers: deterministic cleanup" (`_docs/10-context-managers.md`)
- Note: Chapter 10:32 says the label is descriptive, not a catalogue name.

- Bucket: `10:36`
  - clause: `This pattern survives.`
  - check: `grep -nF 'This pattern survives.' _docs/10-context-managers.md`

- Force: `10:32`
  - clause: `The force: a resource obtained in one place must be released on every path out of the code that uses it, and what release means is a decision.`
  - check: `grep -nF 'The force: a resource obtained in one place must be released on every path out of the code that uses it, and what release means is a decision.' _docs/10-context-managers.md`

- When not to use it: `10:183`
  - clause: `A resource with no release step doesn't need a manager.`
  - check: `grep -nF 'A resource with no release step doesn'"'"'t need a manager.' _docs/10-context-managers.md`

### The `@decorator` discipline

- Chapter: "Decorators done right" (`_docs/26-decorators-done-right.md`)
- Note: Conflict 2. The bucket clause is the one X4b rewrites.

- Bucket: `26:22`
  - clause: `so the bucket is survives`
  - check: `grep -nF 'so the bucket is survives' _docs/26-decorators-done-right.md`

- Force: `26:22`
  - clause: `What stays design is the discipline around it`
  - check: `grep -nF 'What stays design is the discipline around it' _docs/26-decorators-done-right.md`

- When not to use it: `26:215`
  - clause: `When behaviour has to vary per object while the program runs, a decorator can't help, because it fixes the wrapping when the function is defined`
  - check: `grep -nF 'When behaviour has to vary per object while the program runs, a decorator can'"'"'t help, because it fixes the wrapping when the function is defined' _docs/26-decorators-done-right.md`

### Metaclass registry

- Chapter: "Metaclasses, __init_subclass__, and registries" (`_docs/29-metaclasses-init-subclass-and-registries.md`)

- Bucket: `29:22`
  - clause: `the pattern dissolves`
  - check: `grep -nF 'the pattern dissolves' _docs/29-metaclasses-init-subclass-and-registries.md`

- Force: `29:22`
  - clause: `A registry that fills as each carrier class is created spares the booking code from knowing the list, and it's the job a metaclass registry used to do.`
  - check: `grep -nF 'A registry that fills as each carrier class is created spares the booking code from knowing the list, and it'"'"'s the job a metaclass registry used to do.' _docs/29-metaclasses-init-subclass-and-registries.md`

- When not to use it: `29:174`
  - clause: ``A metaclass is the wrong tool for anything `__init_subclass__`, a class decorator or a descriptor does.``
  - check: `grep -nF 'A metaclass is the wrong tool for anything `__init_subclass__`, a class decorator or a descriptor does.' _docs/29-metaclasses-init-subclass-and-registries.md`

### If-chain dispatch

- Chapter: "Shortcut patterns: dict dispatch, function tables, and EAFP" (`_docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`)

- Bucket: `31:36`
  - clause: `What dissolves is the structure built around it`
  - check: `grep -nF 'What dissolves is the structure built around it' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`

- Force: `31:36`
  - clause: `The force, picking behaviour by data, is still there.`
  - check: `grep -nF 'The force, picking behaviour by data, is still there.' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`

- When not to use it: `31:153`
  - clause: `Keep the branch when the cases need different arguments, or when they must run in a fixed order`
  - check: `grep -nF 'Keep the branch when the cases need different arguments, or when they must run in a fixed order' _docs/31-shortcut-patterns-dict-dispatch-and-eafp.md`

## Closing list: named elsewhere, without a bucket (9 items)

### Seam (and enabling point)

- Chapter: "Seams in Python: monkeypatch, injection, and duck typing" (`_docs/33-seams-in-python.md`)
- `33:32`
  - clause: `A seam is a place where that change can be made from outside.`
  - check: `grep -nF 'A seam is a place where that change can be made from outside.' _docs/33-seams-in-python.md`

### Characterisation test (spec item 7 lists it; decision 8 does not)

- Chapter: "Dependency-breaking techniques for modern Python" (`_docs/34-dependency-breaking-techniques.md`)
- `34:32`
  - clause: `A characterisation test records what code does, so that a change can be told apart from a fix.`
  - check: `grep -nF 'A characterisation test records what code does, so that a change can be told apart from a fix.' _docs/34-dependency-breaking-techniques.md`

### Strangler Fig

- Chapter: "Refactor or rewrite" (`_docs/36-refactor-or-rewrite.md`)
- `36:114`
  - clause: `Fowler's description of the approach is to "move bits of behavior from the legacy system into the new code base."`
  - check: `grep -nF 'Fowler'"'"'s description of the approach is to "move bits of behavior from the legacy system into the new code base."' _docs/36-refactor-or-rewrite.md`

### Monitor Object (with Scoped Locking)

- Chapter: "The GIL and performance" (`_docs/37-the-gil-and-performance.md`)
- `37:78`
  - clause: `so the class is a Monitor Object in the vocabulary of *Pattern-Oriented Software Architecture, Volume 2*`
  - check: `grep -nF 'so the class is a Monitor Object in the vocabulary of *Pattern-Oriented Software Architecture, Volume 2*' _docs/37-the-gil-and-performance.md`

### Active Object

- Chapter: "asyncio and the patterns" (`_docs/38-asyncio-and-the-patterns.md`)
- `38:170`
  - clause: `The worker and its queue have the shape that *Pattern-Oriented Software Architecture, Volume 2* names Active Object.`
  - check: `grep -nF 'The worker and its queue have the shape that *Pattern-Oriented Software Architecture, Volume 2* names Active Object.' _docs/38-asyncio-and-the-patterns.md`

### Anti-pattern (definition)

- Chapter: "Anti-patterns and pattern misuse" (`_docs/32-anti-patterns-and-pattern-misuse.md`)
- `32:22`
  - clause: `a recurring structure whose costs outweigh its benefits in the context it sits in`
  - check: `grep -nF 'a recurring structure whose costs outweigh its benefits in the context it sits in' _docs/32-anti-patterns-and-pattern-misuse.md`

### Anti-pattern 1: the overbuilt rating engine

- Chapter: "Anti-patterns and pattern misuse" (`_docs/32-anti-patterns-and-pattern-misuse.md`)
- `32:32`
  - clause: `## The rating function and its overbuilt twin`
  - check: `grep -nF '## The rating function and its overbuilt twin' _docs/32-anti-patterns-and-pattern-misuse.md`

### Anti-pattern 2: getters and setters

- Chapter: "Anti-patterns and pattern misuse" (`_docs/32-anti-patterns-and-pattern-misuse.md`)
- `32:84`
  - clause: `A getter and setter pair is a promise that the field might need behaviour later.`
  - check: `grep -nF 'A getter and setter pair is a promise that the field might need behaviour later.' _docs/32-anti-patterns-and-pattern-misuse.md`

### Anti-pattern 3: the service locator

- Chapter: "Anti-patterns and pattern misuse" (`_docs/32-anti-patterns-and-pattern-misuse.md`)
- `32:113`
  - clause: `A service locator is a registry that a class asks for its collaborators, by name, when it needs them.`
  - check: `grep -nF 'A service locator is a registry that a class asks for its collaborators, by name, when it needs them.' _docs/32-anti-patterns-and-pattern-misuse.md`

