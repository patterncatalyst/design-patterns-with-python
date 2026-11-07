// deck-101.js: "Design Patterns with Python", 101: Patterns and SOLID in Python.
// Build from presentation/ with: node deck-101.js
// Code slides are read from the shipped examples by path and line range at
// build time and the first line of each range is asserted, so a listing is
// byte-exact with its source or the build fails.

"use strict";

const fs = require("fs");
const path = require("path");
const H = require("./deck-helpers.js");
const {
  COLOR, FONT, W, ASSETS, PNG,
  newDeck, addFooter, addContentTitle, addCaption, addCodeSlide, addDiagramSlide, addNotes,
} = H;

const ROOT = path.resolve(__dirname, "..");
const OUT = "design-patterns-with-python-101-patterns-and-solid.pptx";

const pres = newDeck();
pres.title = "Design Patterns with Python: 101, Patterns and SOLID";
pres.subject = "Companion deck to Design Patterns with Python";
pres.author = "PatternCatalyst";
pres.company = "PatternCatalyst";
pres.lastModifiedBy = "PatternCatalyst";

let pageNum = 0;
const floors = []; // [slide number, words, floor, label]

function words(text) {
  return text.trim().split(/\s+/).length;
}

function notes(slide, text, floor, label) {
  const n = words(text);
  floors.push([pageNum, n, floor, label]);
  addNotes(slide, text);
}

// A content slide: footer and logo come with it.
function S() {
  const s = pres.addSlide();
  pageNum += 1;
  addFooter(s, pageNum);
  return s;
}

// Section divider. The AB0000 background is what the deck check keys on.
function divider(code, title, subtitle, text) {
  const s = pres.addSlide();
  pageNum += 1;
  s.background = { color: COLOR.redDark };
  s.addImage({ path: `${ASSETS}/section-panel.png`, x: 0, y: 0, w: W, h: 7.5 });
  s.addText(code, {
    x: 6.27, y: 2.32, w: 6.40, h: 0.50,
    fontFace: FONT.title, fontSize: 22, bold: true, color: COLOR.white, charSpacing: 6,
    align: "left", valign: "middle",
  });
  s.addText(title, {
    x: 6.24, y: 2.84, w: 6.70, h: 1.60,
    fontFace: FONT.title, fontSize: title.length > 18 ? 36 : 44, bold: true, color: COLOR.white,
    align: "left", valign: "top",
  });
  s.addText(subtitle, {
    x: 6.27, y: 4.55, w: 6.60, h: 0.80,
    fontFace: FONT.body, fontSize: 16, italic: true, color: "FFD9D9",
    align: "left", valign: "top",
  });
  s.addImage({ path: `${ASSETS}/redhat-logo-white.png`, x: 11.42, y: 6.88, w: 1.33, h: 0.31 });
  notes(s, text, 45, "divider");
}

// Bullets with a bold subject. Each item is [subject, rest]; rest carries its own
// leading space or punctuation.
function runsFor(items, gap) {
  const runs = [];
  for (const [subject, rest] of items) {
    runs.push({
      text: subject,
      options: { bold: true, color: COLOR.ink, bullet: { code: "25CF" }, paraSpaceAfter: gap },
    });
    runs.push({ text: rest, options: { breakLine: true } });
  }
  return runs;
}

function bullets(s, items, o = {}) {
  s.addText(runsFor(items, o.gap ?? 12), {
    x: o.x ?? 0.62, y: o.y ?? 1.85, w: o.w ?? 12.09, h: o.h ?? 4.7,
    fontFace: FONT.body, fontSize: o.fontSize ?? 18, color: COLOR.body,
    align: "left", valign: "top", lineSpacingMultiple: 1.15,
  });
}

function bulletSlide(eyebrow, title, items, text, o = {}) {
  const s = S();
  addContentTitle(s, eyebrow, title);
  bullets(s, items, o);
  notes(s, text, 90, "bullets");
}

// A table slide. Rows are arrays of strings; the first column is set in bold.
function tableSlide(eyebrow, title, header, rows, colW, text, o = {}) {
  const s = S();
  addContentTitle(s, eyebrow, title);
  const fs = o.fontSize ?? 12;
  const head = header.map((h) => ({
    text: h,
    options: { bold: true, color: COLOR.white, fill: { color: COLOR.ink }, fontFace: FONT.body, fontSize: fs, valign: "middle" },
  }));
  const body = rows.map((r, ri) =>
    r.map((c, ci) => ({
      text: c,
      options: {
        bold: ci === 0,
        color: ci === 0 ? COLOR.ink : COLOR.body,
        fontFace: FONT.body,
        fontSize: fs,
        valign: "middle",
        fill: { color: ri % 2 ? COLOR.panel : COLOR.white },
      },
    })),
  );
  s.addTable([head, ...body], {
    x: 0.62, y: o.y ?? 1.55, w: 12.09, colW, rowH: o.rowH ?? 0.34,
    border: { type: "solid", color: COLOR.grid, pt: 0.5 },
  });
  notes(s, text, 90, "table");
}

// A code slide whose listing is read from the source file.
function codeSlide(eyebrow, title, file, first, last, anchor, caption, text) {
  const full = path.join(ROOT, file);
  const all = fs.readFileSync(full, "utf8").split("\n");
  const lines = all.slice(first - 1, last);
  if (lines[0] !== anchor) {
    throw new Error(`anchor mismatch in ${file}:${first}\n  want: ${JSON.stringify(anchor)}\n  have: ${JSON.stringify(lines[0])}`);
  }
  if (lines.length !== last - first + 1) throw new Error(`short range in ${file}`);
  const longest = Math.max(...lines.map((l) => l.length));
  const byWidth = Math.floor((1370 / longest) * 2) / 2;
  const byHeight = Math.floor(((4.2 * 72) / (lines.length * 1.4)) * 2) / 2;
  const fontSize = Math.min(18, byWidth, byHeight);
  const h = Math.min(4.55, Math.max(1.0, (lines.length * fontSize * 1.4) / 72 + 0.45));
  const s = S();
  addCodeSlide(s, eyebrow, title, "PYTHON", lines, caption, { fontSize, h });
  notes(s, text, 90, "code");
  return { file, first, last, longest, fontSize };
}

// A figure on its own slide, full width.
function figSlide(eyebrow, title, png, caption, text) {
  const s = S();
  addDiagramSlide(s, eyebrow, title, png, caption, { x: 0.62, y: 1.45, w: 12.09, h: 4.95 });
  notes(s, text, 90, "figure");
}

// ===========================================================================
// 1 Cover
// ===========================================================================
{
  const s = pres.addSlide();
  pageNum += 1;
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
  s.addText("101: Patterns and SOLID in Python", {
    x: 6.00, y: 4.65, w: 6.70, h: 0.90,
    fontFace: FONT.body, fontSize: 18, italic: true, color: COLOR.caption,
    align: "left", valign: "top",
  });
  s.addImage({ path: `${ASSETS}/logo-candidate-2.png`, x: 11.10, y: 6.80, w: 1.55, h: 0.37 });
  notes(s, `This is the opening companion to a book that sorts the Gang of Four patterns by what Python 3.15 does to them: some dissolve into a language feature, some survive as design, and some share a name with something else. It's written for engineers who already write Python and have met the catalogue by name. The code shown is read from tested examples, and the examples are set in one shipping domain, with consignments, carriers, rate quotes, tracking and billing. It starts from the decision a pattern represents and then takes the patterns by what they do.`, 45, "cover");
}

// ===========================================================================
// 2 Route
// ===========================================================================
{
  const s = S();
  addContentTitle(s, "ROUTE", "The route");
  const left = [
    ["Why patterns:", " a pattern as a decision made under forces."],
    ["What 1994 assumed:", " the sort into dissolves, survives and shares a name."],
    ["SOLID in Python:", " five principles, met with functions, Protocols and modules."],
    ["Selecting and varying behaviour:", " Strategy, Template Method, State, Command."],
    ["Creating objects under control:", " factories, Builder, Singleton."],
  ];
  const right = [
    ["Composing and adapting structure:", " Adapter, Facade, Bridge, the two Decorators, Proxy, Composite, Flyweight."],
    ["Coordinating and traversing:", " Observer, Mediator, Chain of Responsibility, Iterator, Visitor, Memento, Interpreter."],
    ["Choosing well:", " when to skip a pattern, patterns by force, prompting."],
    ["Reference:", " the toolchain, sources and further reading."],
  ];
  bullets(s, left, { w: 5.95, fontSize: 16, gap: 10 });
  bullets(s, right, { x: 6.85, w: 5.86, fontSize: 16, gap: 10 });
  notes(s, `The deck runs in nine sections. The first two set up the question: what a pattern is, and what changed between 1994 and Python 3.15. SOLID follows, because the principles are the forces the later patterns answer. The four middle sections walk the catalogue by what a pattern does: selecting behaviour, creating objects, composing structure, coordinating and traversing. Choosing well turns the catalogue back into a judgement about when to leave a pattern out, and the reference section closes with versions and reading. What to show: nothing needs running here. Fallback: the section names on the dividers carry the same route.`, 90, "route");
}

// ===========================================================================
// Section: Why patterns
// ===========================================================================
divider("01", "Why patterns", "A decision made under forces",
  `A pattern is easier to judge once it is seen as a decision. A problem arrives with competing forces, a shape resolves them, and the shape has a cost that is paid whether or not the benefit turns up. The code in the deck was held to a standard before it reached a slide: it ran under a linter, a formatter, a strict type checker and a test suite.`);

bulletSlide("WHY PATTERNS", "Decisions under forces", [
  ["A pattern", " answers a problem in a context, and the problem is a set of forces pulling against each other."],
  ["The shape", " is what is left after those forces are traded off, so the useful question is which forces are present in your system."],
  ["Consequences", " are the ledger: what the pattern buys, and what it costs in indirection and extra objects."],
  ["A pattern has a price,", " paid whether or not the benefit turns up. A hook for variation that never varies buys nothing."],
], `The catalogue's own framing isn't a menu of diagrams. A pattern is a solution to a problem in a context, and the problem is a set of forces. Gamma, Helm, Johnson and Vlissides, in Design Patterns, give their patterns a Consequences section that lists what it buys and what it costs, and that section is the ledger used throughout the catalogue sections. A pattern whose consequences you can't state has a cost nobody has counted. No code appears here: the claim rests on that reading of the catalogue, and no test backs it. What to show: pick a pattern from the catalogue sections and ask which force is present and what the ledger says. Fallback: the Consequences idea is stated in four bullets and needs no demonstration.`);

codeSlide("WHY PATTERNS", "Proof that runs",
  "examples/00-prerequisites/src/consignments/consignment.py", 36, 43,
  "@dataclass(frozen=True, slots=True, kw_only=True)",
  "A consignment is a frozen, slotted value: assignment to a field raises, and equal values compare equal.",
  `The smallest piece of the shipping domain: a consignment with an identifier, two ports and a weight. It's a frozen, slotted dataclass, so assigning to a field raises FrozenInstanceError and the equality the dataclass generates is consistent with its hash. The same example stands for the bar the listings met. The code passes ruff check, ruff format, mypy in strict mode and pytest, in that order, with pinned versions of those tools. Three tests witness the claim: equal values compare equal, re-weighing returns a new consignment and leaves the original unchanged, and an instance rejects assignment. What to show: run the pytest suite for the consignment example and watch those three pass. Fallback: the test names are written as sentences and state the behaviour.`);

// ===========================================================================
// Section: What 1994 assumed
// ===========================================================================
divider("02", "What 1994 assumed", "The catalogue's tools, and what Python changed",
  `The catalogue was written for languages in which a behaviour reached a call site inside an object of a class declared in advance. Python 3.15 differs on functions, loops, types and modules. Two questions sort the patterns that follow: does the name mean one thing, and does a language feature resolve the force without the structure. Three tables hold the result, and one short listing shows a dissolved pattern at its smallest.`);

bulletSlide("WHAT 1994 ASSUMED", "The 1994 assumptions", [
  ["Behaviour", " reached a call site wrapped in an object whose class you declared in advance, so naming it meant declaring a class."],
  ["Functions", " couldn't be passed around. In Python they're objects: stored, passed and returned."],
  ["Loops", " couldn't suspend; a Python function containing yield can."],
  ["Types", " were matched by declared name. A Protocol lets the checker match by shape."],
  ["Modules", " had no identity at run time. A Python module is an object, created once on first import."],
], `The catalogue's working assumption is that a unit of behaviour travels in an object whose class was declared in advance, so naming a behaviour meant declaring a class and promising one meant declaring an interface. For a language whose functions can't be passed, whose loops can't suspend, whose types are matched by declared name and whose files have no identity at run time, that is a sound description of the tools. Python 3.15 differs on functions, loops, types and modules, and X | None adds a type the checker follows through its branches. Five tests from the sorting example witness these: the strategy slot taking a def, lambda or partial; the lazy generator; Protocol against ABC; a module being one instance across importers; and Null Object as an optional. What to show: run that example's test files. Fallback: the five bullets state the assumptions and the features that replaced them.`);

bulletSlide("WHAT 1994 ASSUMED", "Three ways out", [
  ["The first question", " is about the name: does the word mean one thing, or does Python attach a second meaning? A shared name sends the pattern to the third bucket."],
  ["The second question", " is about the force: does a language feature resolve it without the pattern's structure? If one does, the pattern dissolves. If none does, it survives as design."],
  ["Dissolves", " never means forget it: the force remains, and the name stays useful in a design conversation."],
  ["A feature", " resolves a force when it resolves the whole force; a partial fix leaves the pattern in place."],
], `Two questions sort the catalogue's patterns into three buckets. The name question comes first, because Decorator is the clearest case of a word that Python attaches to two things. The force question comes second, and it is strict: a feature counts when it resolves the whole force. What dissolves is the class structure the catalogue drew around the force; the force remains. Three tests witness the three buckets: a strategy slot that accepts a def, a lambda and a partial; undo that still needs a command object; and the two meanings of Decorator being independent. What to show: those three tests in the sorting example. Fallback: the bullets give the two questions and the two precautions that keep the second one strict.`);

tableSlide("WHAT 1994 ASSUMED", "Dissolved patterns",
  ["Pattern", "What Python gives you"], [
    ["Strategy", "A callable or functools.partial"],
    ["Iterator", "A generator or __iter__"],
    ["Factory Method", "A class or function in a dict"],
    ["Template Method", "A function taking hook callables; an ABC hook only where steps share state"],
    ["Builder", "A keyword-only dataclass"],
    ["Prototype", "dataclasses.replace or copy"],
    ["Visitor", "singledispatch for an open set, match with assert_never for a closed set"],
    ["Null Object", "X | None checked by mypy"],
    ["Value Object", "A frozen dataclass"],
    ["Metaclass registry", "__init_subclass__"],
    ["If-chain dispatch", "A dict of callables, with EAFP"],
  ], [3.0, 9.09],
  `Eleven rows where a Python feature resolves the force without the structure the catalogue drew. A strategy becomes a callable and a builder becomes a keyword-only dataclass; the other nine rows read the same way. Ten of the rows have a test of their own in the sorting example, such as the lazy generator test and the test that a keyword-only dataclass is a builder. The eleventh, dict dispatch with EAFP, is witnessed by a test that document kinds have issuers. The force remains after a dissolve, so the rows still name a decision. What to show: run the sorting example's dissolve tests. Fallback: the table is the claim, and the test names state the rows.`, { rowH: 0.40 });

tableSlide("WHAT 1994 ASSUMED", "Surviving patterns",
  ["Pattern", "What Python gives you"], [
    ["State", "Enums, match and small classes help; the transition table remains design"],
    ["Command", "A functools.partial for the plain deferred call; undo and queues remain"],
    ["Abstract Factory", "A family of related factories stays a design decision"],
    ["Adapter", "Duck typing removes it only when the shapes already match"],
    ["Facade", "A module or class that narrows a subsystem"],
    ["Bridge", "Two hierarchies varying independently, joined by a Protocol"],
    ["Composite", "A uniform interface over a tree"],
    ["Flyweight", "Shared immutable state; __slots__ and interning help"],
    ["Observer", "Callbacks, but delivery order, failure isolation and subscriber lifetime remain"],
    ["Mediator", "Coordination in one place"],
    ["Chain of Responsibility", "Ordered handlers with a pass-along rule"],
    ["Memento", "A frozen dataclass snapshot; what to capture remains"],
    ["Interpreter", "A grammar and its evaluator remain design"],
    ["Resource acquisition", "The with statement and context managers"],
  ], [3.0, 9.09],
  `Fourteen rows where the language helps but the decision remains. State survives as a transition table, Command survives because undo and queues need an object with an identity, and Observer survives because callbacks don't decide order, failure or lifetime. In these rows the second column says what Python offers and what stays design. Command has a witness in the sorting example, a test that undo needs a command object. The other rows are witnessed in the example that develops the pattern, for instance the read-only transition table for State, the weak pool for Flyweight, the audit trail kept on rollback for Memento, and the with statement closing a writer on an exception. What to show: any one of those tests. Fallback: later sections return to these patterns with code.`, { fontSize: 11.5, rowH: 0.31 });

tableSlide("WHAT 1994 ASSUMED", "One name, two meanings",
  ["Name", "What Python gives you"], [
    ["Decorator pattern vs @decorator syntax", "Wrapper objects composed at runtime vs a function rebinding at definition time"],
    ["Singleton", "A module built at import time by default; Borg and metaclass as variants"],
    ["Proxy", "A surrogate object vs attribute interception with __getattr__, property and cached_property"],
    ["\"Interface\"", "Protocol (structural) vs an ABC (nominal)"],
  ], [3.9, 8.19],
  `Four names mean two things in Python, and confusing the two meanings produces wrong designs. Decorator comes first: the pattern is a wrapper object composed at run time, and the at-sign form is a function rebinding a name once at definition time. Singleton is a module by default. Proxy covers a surrogate object and attribute interception, which are different tools. Interface covers a Protocol, matched by shape, and an abstract base class, matched by declared name. Four tests from the sorting example witness the rows: the two decorators being independent, a module being one instance across importers, a proxy forwarding only the missing attributes, and a Protocol being structural while an ABC is nominal. What to show: those four tests. Fallback: the table is the claim.`, { rowH: 0.62, fontSize: 14, y: 1.7 });

codeSlide("WHAT 1994 ASSUMED", "Dissolved in code",
  "examples/03-three-way-split/src/three_way_split/dissolve.py", 35, 48,
  "def flat_rate(consignment: Consignment) -> Money:",
  "quote takes a def, a lambda or a partial in the same slot, and no RateStrategy interface exists.",
  `A pricing rule is a Callable from Consignment to Money, so quote accepts a def, a lambda or a functools.partial in the same slot. The listing shows the dissolved patterns at their smallest: two plain functions as rules, and a quote function that applies whichever rule it is handed. There's no abstract class and no subclass per rule. The force is still there, since a caller must choose behaviour at run time, and the language resolves it without the classes. One test witnesses the claim: the strategy slot accepts a def, a lambda and a partial. What to show: run that test, then pass a lambda to quote in a REPL. Fallback: the listing and the test name together carry the claim.`);

bulletSlide("WHAT 1994 ASSUMED", "Names for assistants", [
  ["A pattern name", " is a compact design review comment: \"this should be a Strategy\" asserts interchangeable rules and a caller that selects one."],
  ["Names are compressed claims.", " A reviewer who finds one implementation behind a RateStrategy has found a mismatch without reading anything else."],
  ["A prompt", " that says \"use the Strategy pattern\" leaves the mechanism open. Naming the role and the mechanism gives a result to compare line by line."],
  ["State the bucket:", " \"this is a dissolved pattern, no base class\" turns a preference into a testable constraint."],
], `A pattern name does work in a team and in a prompt for the same reason: it compresses claims that can be checked. Calling something a RateStrategy asserts several interchangeable rate computations, a caller that selects one, and a narrow shared surface. A reviewer can check those assertions against the code. In a prompt, naming the pattern alone leaves the mechanism open, so the reply may be a class hierarchy where a function was wanted. Naming the role and the mechanism, a callable type alias and a plain function that fits it, produces a result that can be compared with the instruction. Stating the bucket does the same in one sentence. No test backs this slide; it rests on prose. What to show: a prompt written both ways. Fallback: the four bullets give the contrast.`);

// ===========================================================================
// Section: SOLID in Python
// ===========================================================================
divider("03", "SOLID in Python", "Five principles, met with functions, Protocols and modules",
  `SOLID names five forces that keep code cheap to change: one reason to change, extension without editing, substitutability, narrow roles and dependence on abstractions. Python meets them with light tools. A function and a read-only mapping carry the first two, a docstring and a contract suite carry the third, a Protocol per role carries the fourth, and one composition function carries the fifth. Principles beyond SOLID follow, tested by the same examples.`);

bulletSlide("SOLID IN PYTHON", "One reason to change", [
  ["Pricing, tax and audit", " change for different reasons and under different tests, so they're separate pieces."],
  ["A change", " moves the fields it feeds: a new tariff changes net and tax, the SG tax rule changes tax, and the audit sink changes none."],
  ["Pricing and tax", " run alone: the test builds a base rate and a percent rule with no sink and no rule table."],
  ["The audit sink", " receives the quote that was returned."],
], `Robert Martin states the single responsibility principle as a class having only one reason to change, in Agile Software Development. The example applies it to a quote: a base rate prices, a percent rule taxes, and an audit callable records. A change request that arrives has its own author and moves its own test, which is the practical check for a separate reason to change. Three tests back the claim: a change moves the fields it feeds, pricing and tax run alone, and the audit receives exactly the quote returned. What to show: run the pricing example's single responsibility tests and read the third assertion. Fallback: the bullets list the three replacements and what those replacements move.`);

figSlide("SOLID IN PYTHON", "The quote flow", "05-srp-ocp-lsp",
  "Pricing sits behind a Protocol and hands its net to tax rules keyed by destination country; the finished quote goes to an audit callable.",
  `The figure draws one quote with three responsibilities. A rate calculator sits behind the RateCalculator Protocol and produces a net amount. Tax rules, keyed by destination country, take that net and add tax. The finished quote goes to an audit callable. The arrows are the data flow that the quote function coordinates in the code. The boxes change for separate reasons, and one contract suite checks the calculators. The figure is the shape behind the listings that follow. What to show: the figure at full width, following the arrows from rate to tax to audit. Fallback: the caption states the same flow in one sentence.`);

codeSlide("SOLID IN PYTHON", "Extension by table entry",
  "examples/05-srp-ocp-lsp/src/srp_ocp_lsp/tax.py", 23, 28,
  "TAX_RULES: Mapping[str, TaxRule] = MappingProxyType(",
  "A new tax rule arrives as a new entry in a read-only table; quote isn't edited and nothing can add to the table by assignment.",
  `The open-closed principle, in Bertrand Meyer's formulation in Object-Oriented Software Construction, asks for extension without editing what already works. Here a new rule arrives as data: another entry in a mapping from destination country to a percent rule. TAX_RULES is a read-only view over a dict, so no module can add to it by assignment, and the extension point stays visible. Two tests witness the claim: a new tax rule is added without editing quote, and the default tax table is read-only. What to show: run the open-closed tests, then try assigning to the table and read the TypeError. Fallback: the two test names state the behaviour and the listing shows the table.`);

codeSlide("SOLID IN PYTHON", "The rate contract",
  "examples/05-srp-ocp-lsp/src/srp_ocp_lsp/pricing.py", 16, 27,
  "class RateCalculator(Protocol):",
  "The contract lives in the docstring and the tests; mypy can see the signature but not a behavioural violation.",
  `Liskov substitution says a subtype must be usable wherever its base is. Barbara Liskov introduced the idea in her OOPSLA 1987 keynote, and Liskov and Wing gave the behavioural definition in A Behavioral Notion of Subtyping. Half of the rule is a type signature, and mypy checks that half. The other half is the contract in the docstring: accepted zones, a non-negative result in cents, a heavier consignment never cheaper, a refusal for an unknown zone. The claim rests on three tests: a calculator honours the contract, the contract suite catches a strengthened precondition, and mypy exits clean on a behavioural violation. What to show: the contract tests and the mypy test. Fallback: the docstring is in the listing, and the mypy test states the limit.`);

codeSlide("SOLID IN PYTHON", "Narrow roles",
  "examples/06-isp-dip-and-di-without-a-framework/src/isp_dip_di/booking.py", 12, 17,
  "class BookingGateway(Protocol):",
  "A narrow Protocol names what booking needs from a carrier; adapters satisfy it without naming it.",
  `Interface segregation asks that a consumer depend on what it uses. In Python the consumer's module declares the Protocol it needs, and an adapter satisfies it by shape without importing it. BookingGateway has two methods because booking needs two: accept a request and withdraw a reference. Two tests witness the claim. The adapters satisfy the roles without naming one, which is structural typing. The second shows what a fat Protocol costs: fakes have to stub methods their consumer never calls, and that's the sign the Protocol should be narrower. What to show: the second test, then the narrow fake beside it. Fallback: the listing is the whole role.`);

codeSlide("SOLID IN PYTHON", "The composition root",
  "examples/06-isp-dip-and-di-without-a-framework/src/isp_dip_di/app.py", 32, 45,
  "def build_app(",
  "One function names the concrete carrier, builds one gateway and hands it to the booking and tracking consumers.",
  `Somewhere a concrete adapter has to be named, and the composition root is that place, as close to the program's entry point as it can be. Mark Seemann describes the pattern in his post Composition Root, and the word injection for handing a collaborator to the code that uses it comes from Martin Fowler's January 2004 article on inversion of control containers and the dependency injection pattern. build_app looks up a factory by carrier name, raises an error naming the known carriers for an unknown carrier, builds one gateway and passes it to the booking service and the tracking function. Three tests witness it: one gateway is shared between booking and tracking, the root accepts a substitute without patching, and the policy modules don't import the adapters. What to show: the substitute test. Fallback: the listing is the wiring.`);

figSlide("SOLID IN PYTHON", "Wiring the application", "06-isp-dip-and-di-without-a-framework",
  "The composition root builds one carrier adapter and passes it to the booking and tracking consumers, which name the small Protocol they need.",
  `The figure shows dependency injection without a framework. The composition root builds one carrier adapter and passes it to two consumers, booking and tracking. The consumers name the small Protocol they need, and the adapter satisfies both Protocols structurally and imports neither. That's the inversion: the policy code points at an abstraction it owns, and the concrete adapter is named in one place. The arrows match the arguments in build_app, so the figure and the build_app listing describe the same call. What to show: the figure beside the build_app listing. Fallback: the caption gives the direction of the dependencies in words.`);

tableSlide("SOLID IN PYTHON", "Principles beyond SOLID",
  ["Principle", "What its test shows"], [
    ["Composition over inheritance", "A class adapter still exposes the client's own methods"],
    ["DRY", "The fuel surcharge lives in one definition of the function"],
    ["YAGNI", "The engine needs more classes, functions and lines than the function"],
    ["Simple design", "One engine quote makes more Python calls than the function"],
    ["Orthogonality", "A new booking kind needs no gateway change"],
    ["Fail fast", "An unknown carrier fails at the composition root"],
    ["EAFP", "A look-first read raises when another thread evicts between check and read"],
    ["The Law of Demeter", "Each reader names the attributes it depends on"],
  ], [3.4, 8.69],
  `Eight further principles, with a test that shows the effect of each. Brandon Rhodes's page on composition over inheritance frames the first. The Pragmatic Programmer is the source for DRY, Martin Fowler's site for YAGNI and for Beck's design rules, and Jim Shore's paper for fail fast. Orthogonality shows in the bridge: a new booking kind needs no gateway change. EAFP is shown by its failure case, where a look-first read races with another thread and raises. The Python glossary defines the style. The Demeter row gets a listing of its own. The tests come from several examples, because the principles show up in the pattern examples that exercise them. What to show: the DRY and YAGNI tests together. Fallback: the right column states the results.`, { rowH: 0.52, fontSize: 14 });

codeSlide("SOLID IN PYTHON", "Asking the shipment",
  "examples/46-appendix-f-programming-principles/src/principles_reviewed/billing.py", 40, 44,
  "    def amount_due(self) -> Money:",
  "The reader asks the shipment for the amount due; a credit reaches only the reader that asks the shipment.",
  `The Law of Demeter, hosted by the Demeter project at Northeastern University, puts one question to the code: who answers for the amount due? The reader shown here asks the shipment, which holds its invoice and its credits and returns the total less the credits. A second reader reaches through the shipment to the invoice and the credits itself, and so depends on their attributes. Two tests witness the difference: both readers give the same line while there are no credits, and a credit reaches only the reader that asks the shipment. That's why the dependence matters: the reaching-through reader drifts when the shipment changes. What to show: the credit test. Fallback: the listing and the caption carry the claim.`);

// ===========================================================================
// Section: Selecting and varying behaviour
// ===========================================================================
divider("04", "Selecting and varying behaviour", "Strategy, Template Method, State and Command",
  `These four patterns decide which behaviour runs and how it varies. Strategy dissolves into a callable. Template Method straddles two buckets: a function that takes hooks covers most cases, and an abstract base class stays where steps share state. State survives, with the transition table as the design. Command survives for undo and queues, while its deferred call dissolves into a partial.`);

codeSlide("SELECTING AND VARYING BEHAVIOUR", "Strategy as a callable",
  "examples/12-strategy-the-callable/src/strategy_callable/rules.py", 50, 56,
  "RATE_RULES: Mapping[str, PricingRule] = frozendict(",
  "A registry maps a name to a callable: a function, a partial and a frozen callable class share one slot.",
  `Strategy dissolves, because a feature resolves the force without the pattern's structure. The force is that a caller must choose among several ways of computing one result without depending on which one it holds. A callable type resolves it. The registry here holds a plain function, a functools.partial with a rate bound and a frozen dataclass with a call method, and quote treats them alike. Two tests witness the claim: a class per strategy passes the same behaviour table, and the class design declares four strategy classes where the rules declare one. The skip condition: a single rule called from one place is a function, with no registry. What to show: the table-driven test. Fallback: the listing is the registry.`);

figSlide("SELECTING AND VARYING BEHAVIOUR", "Rules in a registry", "12-strategy-the-callable",
  "The caller names a rule, the read-only RATE_RULES registry returns a callable, and quote records the name with the price.",
  `The figure follows one quote through the registry. The caller names a rule, the read-only RATE_RULES mapping returns a callable, and quote prices the consignment with it and records the rule's name next to the price. Whether the callable is a function, a partial or a frozen dataclass makes no difference to the call, which is the point of the slot. The arrows correspond to lines in the code, so the figure is a reading aid for the registry listing. What to show: the figure at full width, tracing a name to a callable to a price. Fallback: the caption says the same in one sentence, and the registry listing has it.`);

codeSlide("SELECTING AND VARYING BEHAVIOUR", "Hooks, not subclasses",
  "examples/13-template-method-and-the-function-alternative/src/template_method/hooks.py", 28, 35,
  "@dataclass(frozen=True, slots=True, kw_only=True)",
  "Customs steps are hooks on a frozen dataclass: classify and duty are required, extra_documents takes a default when left out.",
  `Template Method straddles two buckets. The fixed sequence, refuse an empty consignment, classify, total, assess duty, assemble documents, is a function that takes hooks. The varying steps are fields on a frozen dataclass, and the ones a destination must supply, classify and duty, have no default. An abstract base class stays the right tool where the steps share state. Three tests cover it: the function runs its steps in order, a hook left out takes its default, and a required hook can't be left out. The skip condition is the plain one: write a function when there is one variant. What to show: the required-hook test, which fails at construction. Fallback: the listing shows which hooks have defaults.`);

codeSlide("SELECTING AND VARYING BEHAVIOUR", "State as a table",
  "examples/14-state-and-finite-state-machines/src/state_machines/table.py", 7, 14,
  "TRANSITIONS: Mapping[tuple[ConsignmentStatus, HandlingKind], ConsignmentStatus] = frozendict(",
  "The legal transitions are one read-only mapping from a status and an event to the next status.",
  `State survives, and the transition table is the design. For State the force doesn't move: the legal transitions are a business rule that has to be written in one place and checked. The table is a frozendict from a status and a handling event to the next status, and a pair that isn't in the table is refused. Three tests witness the claim: state objects pass the same lifecycle table, an illegal event is a transition error, and the table is read-only. The skip condition: a two-state flag is a bool. What to show: the illegal-event test, which names the status and the event. Fallback: the four rows in the listing are the whole lifecycle from booking to delivery.`);

codeSlide("SELECTING AND VARYING BEHAVIOUR", "Command with undo",
  "examples/15-command-undo-and-command-queues/src/command_undo/booking.py", 25, 34,
  "    def amend(self, amendment: Amendment) -> None:",
  "amend applies an amendment and stacks its inverse; undo pops the inverse and stacks the redo.",
  `Command survives, with the deferred call dissolving. A deferred call is a functools.partial. What survives is the force that a change needs an identity of its own: something to undo, redo and queue. amend applies an amendment, which returns the amendment that reverses it, and pushes that inverse on the undo stack. undo applies the inverse and pushes the redo. Harry Percival and Bob Gregory's Architecture Patterns with Python treats commands as messages with one handler, is the credit for that idea. Three tests back it: apply returns the reversing amendment, a failing batch leaves the booking unchanged, and amendments compare by value where partials don't. What to show: the batch test. Fallback: call the function when a change is never undone or queued.`);

// ===========================================================================
// Section: Creating objects under control
// ===========================================================================
divider("05", "Creating objects under control", "Factories, Builder and Singleton",
  `Creational patterns decide who builds an object and how many exist. Factory Method dissolves into a value in a dict, while Abstract Factory survives as a kit of products that have to match. Builder dissolves into a keyword-only dataclass, and Prototype into dataclasses.replace. Singleton is a name that needs disambiguating, and the default answer is a module. The listings are short because the language does most of the work.`);

codeSlide("CREATING OBJECTS UNDER CONTROL", "Factories in a dict",
  "examples/16-factory-method-and-abstract-factory/src/factories/factories.py", 8, 15,
  "type GatewayFactory = Callable[[CarrierSettings], CarrierGateway[str]]",
  "The creator subclass becomes a value in a slot: a mapping from carrier code to a constructor.",
  `Factory Method dissolves. The force is present: the caller wants a gateway for a carrier and shouldn't know which gateway class that is. A mapping from carrier code to a constructor resolves it, and the type alias GatewayFactory, written with the type statement, names what the values are. Three tests witness the claim: a registered constructor builds the carrier gateways, the creator design declares three classes where the registry declares none, and an unknown carrier code is an unknown-carrier error. Brandon Rhodes's page on the Factory Method pattern is the source for reading the catalogue this way. What to show: the class-count test. Fallback: the listing is the entire registry.`);

codeSlide("CREATING OBJECTS UNDER CONTROL", "A family of gateways",
  "examples/16-factory-method-and-abstract-factory/src/factories/kits.py", 49, 60,
  "FASTLINE_KIT = CarrierKit(",
  "A kit bundles a carrier's gateway, label printer and rates, so the products come from one family.",
  `Abstract Factory survives. The force is that products must come from the same family, and a language that stores callables doesn't choose the family. A kit holds a gateway constructor, a label printer and a rates source for one carrier, and KITS maps a carrier code to its kit. The claim rests on three tests: a kit ships with its own carrier's products, a kit is a frozen value, and mypy rejects a kit that mixes reference types. Rhodes's page on the Abstract Factory pattern gives the Python reading. The skip condition: if the products don't have to match, pass them separately. What to show: the mypy rejection test, which is the family constraint enforced before the code runs. Fallback: the two kits on the slide differ in the carrier.`);

codeSlide("CREATING OBJECTS UNDER CONTROL", "Builder as a dataclass",
  "examples/17-builder-dataclasses-and-prototype/src/builder_prototype/booking.py", 14, 23,
  "@dataclass(frozen=True, slots=True, kw_only=True)",
  "Named, keyword-only fields with defaults do a builder's work, and dataclasses.replace makes a variant.",
  `Builder dissolves. A keyword-only frozen dataclass takes named arguments, supplies defaults and validates once in its post-init, which is what a builder was for. Prototype dissolves too: a template request and dataclasses.replace give a new request. Three tests witness the claim: both constructors pass the booking table, a positional constructor accepts a swapped origin and destination, and a template and replace give a new request. The second test is the reason for keyword-only fields. Rhodes's pages on Builder and on Prototype are the credit for reading both patterns this way. The skip condition: a value with three fields doesn't need this treatment. What to show: the swapped-argument test. Fallback: the listing shows the defaults.`);

codeSlide("CREATING OBJECTS UNDER CONTROL", "Singleton as a module",
  "examples/18-singleton-module-borg-metaclass/src/singleton/quoting.py", 3, 16,
  "from decimal import Decimal",
  "lazy from imports the tariff module on first use, so callers share one table and a test can pass its own.",
  `Singleton needs disambiguating, and the default answer to the force, load this once and let everyone read it, is the first meaning: a module. The listing shows two forms. A tariff module is built once, and the lazy from import, new in Python 3.15, defers building it to first use. The quote function takes the table as a parameter, so a test or a tenant can pass its own. Two tests witness the claim: the forms give callers the same rates, and a load-once helper runs the loader once when two threads pass the first check. Rhodes's Singleton and module-globals pages are credited. What to show: the threads test. Fallback: pass a parameter when state differs per test, tenant or request.`);

// ===========================================================================
// Section: Composing and adapting structure
// ===========================================================================
divider("06", "Composing and adapting structure", "Adapter, Facade, Bridge, the Decorators, Proxy, Composite and Flyweight",
  `Structural patterns join parts that were written apart. Adapter, Facade and Bridge all survive: duck typing removes an adapter only where shapes already match, a facade narrows a subsystem, and a bridge keeps two axes of variation independent. The name Decorator needs the most care here, because the pattern and the at-sign syntax are different things. Proxy covers a surrogate object and attribute interception. Composite and Flyweight close the section with a tree and a pool.`);

bulletSlide("COMPOSING AND ADAPTING STRUCTURE", "Adapter, Facade and Bridge", [
  ["All three survive.", " Duck typing removes an adapter where the shapes already match, and the type checker says where they don't."],
  ["Facade", " is for a subsystem with many parts and a caller that wants a few operations: one ship call books a carrier."],
  ["Bridge", " is for a design with two things that vary, joined by a narrow Protocol."],
  ["A rejected booking", " crosses the facade as a carrier error, not as the carrier's own failure type."],
  ["Skip the layer", " when there is one carrier and its SDK already fits."],
], `Adapter, Facade and Bridge all survive. An adapter translates between two parts that disagree about shape, and duck typing removes it only where the shapes already match; mypy reports where they don't. Gamma, Helm, Johnson and Vlissides give Facade to a subsystem with many parts and a caller that wants a few operations, and Bridge to a design with two things that vary. Brandon Rhodes's page on composition over inheritance is credited for the Bridge reading. Four tests witness the claim: a client whose shape matches needs no adapter, mypy rejects a client with a different shape, ship books a carrier through one call, and a carrier rejection becomes a carrier error. What to show: the mypy rejection test. Fallback: call the client when there is one carrier and the SDK fits.`);

codeSlide("COMPOSING AND ADAPTING STRUCTURE", "A bridge over a Protocol",
  "examples/19-adapter-facade-bridge/src/adapter_facade_bridge/bookings.py", 9, 17,
  "@dataclass(frozen=True, slots=True)",
  "A booking kind holds a gateway through a Protocol, so N kinds and M carriers need N plus M classes, not N times M.",
  `The bridge keeps two axes apart. Booking kinds sit on one side, and carrier gateways on the other, joined by the narrow gateway Protocol. A standard booking holds a gateway and books through it, and a kind written later works with the existing carriers. That's N times M classes against N plus M. The cost sits on the implementor, which has to satisfy the Protocol, and the benefit sits on the abstraction. Three tests cover it: every booking kind works with every carrier, the class-per-pair design needs a class per kind and carrier pair, and a new booking kind needs no gateway change. What to show: the class-per-pair test next to the bridge test. Fallback: the arithmetic in the caption is the claim.`);

figSlide("COMPOSING AND ADAPTING STRUCTURE", "One call, two axes", "19-adapter-facade-bridge",
  "The facade picks a gateway and a booking kind; the kinds work through the narrow gateway Protocol, and one client reaches it through an adapter.",
  `The figure combines the three patterns in one call. The facade picks a gateway and a booking kind. The booking kinds work through the narrow gateway Protocol, which is the bridge. One carrier client already satisfies the Protocol, and the other reaches it through an adapter that converts units, which is why a dashed arrow marks the unit read from the consignment's weight. The arrows correspond to calls in the code, including the registration of the facade's collaborators. What to show: the figure at full width, then follow a single ship call from the facade to a carrier. Fallback: the caption gives the flow, and the bridge listing shows the booking kind.`);

bulletSlide("COMPOSING AND ADAPTING STRUCTURE", "Two things called Decorator", [
  ["The pattern", " builds a value: a wrapper object that holds another and presents the same interface, composed while the program runs."],
  ["The at-sign form", " rebinds a name: one step above a def, taken once when the module loads."],
  ["The name", " is a known mismatch. PEP 318, which introduced the syntax, says the name isn't consistent with its use in the original catalogue."],
  ["A naming rule:", " Decorator alone means the pattern. The syntax is the at-sign form or decorator syntax."],
  ["They stay apart:", " a decorated function has no price, and a layer has no wrapped function."],
], `The pattern builds a value, a layer wrapped around a calculator. The syntax rebinds a name. PEP 318, which introduced the syntax, records the mismatch in its own text, in a complaint about the name being inconsistent with its use in the Gang of Four book. The sorting question gives the pair its bucket: the syntax is a language feature, a stack chosen per request is still a design, and the two share a name and little else. Four tests witness the claim: the layers for a consignment are chosen while the program runs, the at sign rebinds a name once at definition time, a decorated function has no price and a layer has no wrapped function, and mypy rejects a decorated function where a calculator belongs. What to show: the last test. Fallback: the five bullets state the split.`);

codeSlide("COMPOSING AND ADAPTING STRUCTURE", "Wrapper objects at run time",
  "examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/src/decorator_proxy/layers.py", 45, 53,
  "@dataclass(frozen=True, slots=True)",
  "A layer wraps a calculator and adds a fixed fee; the order of layers changes the price once a fee is added.",
  `The Decorator pattern gives the name to a wrapper object that holds another object and presents the same interface. This layer holds a calculator and adds a fixed fee to whatever it prices. Order matters once a layer adds a fixed amount, because a percentage and a fee don't commute the way two percentages do. Three tests witness the claim: a layer wraps a calculator and leaves it unchanged, layer order changes the price when a fee is added, and compose wraps the last layer outermost. Brandon Rhodes's page on the Decorator pattern is credited. The skip condition: skip the layer stack when the adjustment is one fixed step, since a function does it. What to show: the order test with a fee. Fallback: the arithmetic in that test is short.`);

codeSlide("COMPOSING AND ADAPTING STRUCTURE", "A name rebound once",
  "examples/20-decorator-pattern-vs-decorator-syntax-and-proxy/src/decorator_proxy/syntax.py", 46, 49,
  "@retry(attempts=3, on=(CarrierTimeoutError,))",
  "The at-sign line rebinds quote_carrier once, when the module loads, and stacking order is fixed then too.",
  `The at-sign form is a statement about a name. The line above the def means quote_carrier is the result of calling retry on the function, bound once when the module loads. Stacking order is fixed at that time as well. Three tests back it: the at sign rebinds the name once at definition time, syntax stacking order decides whether each attempt is audited, and rebound functions don't compare by value. The caution on the syntax is about safety: don't put a retry around an operation that isn't safe to repeat. PEP 318 is the credit for the form. The pattern and the syntax are different tools. What to show: the stacking-order test. Fallback: the four lines on the slide are the form.`);

bulletSlide("COMPOSING AND ADAPTING STRUCTURE", "Proxy as stand-in", [
  ["Proxy", " is a name that covers a surrogate object and attribute interception."],
  ["A proxy", " is a stand-in in front of another object, deciding whether, when and how the subject is reached. It returns what the subject returns."],
  ["A layer", " may change the price. A proxy returns what the gateway returns, and asks the gateway once per consignment."],
  ["An explicit proxy", " lets mypy report a typo. A proxy that forwards through __getattr__ accepts the same typo."],
], `Gamma, Helm, Johnson and Vlissides give Proxy to a stand-in that sits in front of another object and decides whether, when and how the subject is reached. In Python the name covers two tools: a surrogate object that keeps the interface, shown here, and attribute interception with __getattr__ and properties, which is a different design with different checking. Four tests witness the claim: the proxy asks the gateway once per consignment, a proxy returns what the gateway returns where a layer changes the price, mypy reports a typo on the explicit proxy, and mypy accepts a typo through a forwarding proxy. What to show: the last two tests together. Fallback: the bullets name the contrast between the explicit and the forwarding proxy.`);

codeSlide("COMPOSING AND ADAPTING STRUCTURE", "One weight question",
  "examples/21-composite-and-flyweight/src/composite_flyweight/consolidation.py", 8, 16,
  "def consignments(shipment: Shipment) -> tuple[Consignment, ...]:",
  "A consignment and a consolidation answer the same question; the match covers both kinds and assert_never flags a third.",
  `Composite is for the caller who holds something and asks one question without caring whether it is a single item or a bundle. Composite and Flyweight both survive. The listing flattens a shipment to its consignments, depth first, with a match that handles a consignment and a consolidated shipment and ends in assert_never. The tree's invariants are the part of Composite that no language feature supplies. Flyweight, drawn in the figure that follows, is for many references to equal values. Three Composite tests witness the claim: a consignment and a consolidation answer weight the same way, a flat sum misses nested consolidations, and mypy refuses adding to a frozen consolidation. Rhodes's Composite and Flyweight pages are credited. What to show: the flat-sum test. Fallback: the caption states the question.`);

figSlide("COMPOSING AND ADAPTING STRUCTURE", "Shared commodities", "21-composite-and-flyweight",
  "A consolidation sums its parts through nested groups, and consignments reach one frozen commodity per code from a pool.",
  `The figure draws a small tree. A consolidation answers weight as a consignment does, by summing its parts through nested groups, and consignments reach a single frozen commodity per code from a pool that lets go of commodities nobody holds. The tree it draws is smaller than the one the tests build, with two top-level parts against three and one commodity against two. Every arrow in it is still composed by code. Two Flyweight tests witness the pool: the weak pool drops a commodity nobody holds, and split port codes are equal but distinct objects. What to show: the weak-pool test. Fallback: the caption names both halves of the figure.`);

// ===========================================================================
// Section: Coordinating and traversing
// ===========================================================================
divider("07", "Coordinating and traversing", "Observer, Mediator, Chain, Iterator, Visitor, Memento and Interpreter",
  `The last catalogue section covers patterns that coordinate parties and walk structures. Observer, Mediator and Chain of Responsibility survive, for forces that callbacks and loops don't settle. Iterator dissolves into a generator, leaving three decisions about passes, reading and closing. Visitor dissolves into a match over a closed set. Memento survives as a snapshot with a choice of what to capture, and Interpreter survives as a small grammar with more than one reading.`);

codeSlide("COORDINATING AND TRAVERSING", "Signal delivery",
  "examples/22-observer/src/observer/signal.py", 66, 81,
  "        errors: list[Exception] = []",
  "Delivery runs in subscription order, a failing subscriber doesn't stop the rest, and the failures are raised together afterwards.",
  `Observer survives, as a Signal. A list of callables decides nothing about delivery order, failure, re-entry or lifetime, and Signal settles those four. The listing shows the delivery loop: it pops pending events, calls subscribers in subscription order, collects any exception from a failing subscriber and raises an ExceptionGroup after delivery. PEP 654 is the credit for exception groups. Five tests cover it: subscribers are called in subscription order, one failing subscriber doesn't stop the rest, every failure is reported after delivery, a bound-method subscriber is dropped when its owner goes, and an event published during delivery waits its turn. The skip condition: call the parties directly when the set is fixed when the subject is built. What to show: the failing-subscriber test. Fallback: the listing is the loop.`);

codeSlide("COORDINATING AND TRAVERSING", "A chain of stages",
  "examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/clearance.py", 65, 68,
  "    for stage in stages:",
  "A loop over a tuple of functions replaces the linked handler class; the first stage that decides wins.",
  `Chain of Responsibility survives, and the class that carries the successor link is the part Python removes. A stage is a function from a declaration to a decision or None, the order is a property of the tuple, and a loop passes the declaration along until one stage decides. What remains as design is the order of the stages and which stage may be last. Three tests witness the claim: the first stage that decides wins, stages after a decision aren't called, and mypy refuses a stage that can pass as the final stage. The skip condition: with one check, call the function. What to show: the final-stage test, which makes the last link total. Fallback: the four lines are the whole chain.`);

codeSlide("COORDINATING AND TRAVERSING", "One release rule",
  "examples/23-mediator-and-chain-of-responsibility/src/mediator_chain/mediator.py", 64, 74,
  "        match message:",
  "The mediator receives a message, updates what is outstanding and tries one release.",
  `Mediator is for a group of parties whose actions depend on one another. The listing shows the whole rule: a settlement clears the duty, a passed inspection clears the inspection, a failed inspection clears it and marks the clearance failed, and after a message the mediator tries one release. Arrival order therefore doesn't matter. The choreography is the other form, where a party reacts to the previous one, and the cost of a mediator is that it knows the messages its colleagues send and decides who acts next. The claim rests on three tests: the mediator releases in either order, a choreography loses a settlement that arrives before inspection, and a duplicate settlement releases once. What to show: the choreography test. Fallback: the match is on the slide.`);

codeSlide("COORDINATING AND TRAVERSING", "Generators as iterators",
  "examples/24-iterator-generators-and-the-iterator-protocol/src/iterator_protocol/domain.py", 42, 43,
  "    def __iter__(self) -> Iterator[HandlingEvent]:",
  "A generator method makes the history walkable again and again; the cursor class dissolves.",
  `The cursor class dissolves, and three decisions remain: one pass or many, how much to read, and who closes. A function with yield is a generator function, and calling it returns a generator iterator. Two lines make a tracking history iterable, and calling iter again starts a fresh walk. Four tests witness the claim: a tracking history can be walked twice, a self-iterating history is empty on the second pass, the first page reads only one page, and breaking out of a loop leaves a named reader open. Rhodes's page on the Iterator pattern and PEP 255 are credited. The skip condition: pass the tuple when the data is already in a list that callers index or measure. What to show: the walk-twice test. Fallback: the two lines are the method.`);

codeSlide("COORDINATING AND TRAVERSING", "Visitor as a match",
  "examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/events.py", 42, 56,
  "def describe(event: HandlingEvent, /) -> str:",
  "One function with a match is the whole operation; a kind left out of the match is a type error.",
  `Visitor is for a fixed family of kinds that gets new operations over time, and over a closed set it dissolves into one match per operation. The listing describes a handling event for a tracking feed. Each kind is a case, and the last case calls assert_never, so a kind left out is reported by mypy. An open set of kinds is a different tool and a different question. Three tests witness the claim: mypy reports an event left out of a match, a status-after function maps each event to a consignment status, and every visitor form describes a journey the same way. The skip condition: with one operation over the kinds, write the match where it is needed. What to show: the left-out-event test. Fallback: the listing and its last case.`);

codeSlide("COORDINATING AND TRAVERSING", "Snapshot and rollback",
  "examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/memento.py", 61, 70,
  "@contextmanager",
  "A context manager restores the snapshot on failure; the audit is left out, so the record of the refusal survives.",
  `Memento is for putting an object back the way it was after a change fails. What survives as design is the choice of what to capture. The snapshot here holds the request and the attached documents and leaves the audit out, because a record that an amendment was refused must survive the rollback. The context manager takes a snapshot, runs the block, and on an exception restores the snapshot, appends a rolled-back entry to the audit and re-raises. Three tests cover it: rollback keeps the audit trail, a deepcopy memento erases the audit trail on rollback, and rollback restores the attached documents. What to show: the deepcopy test, which is the failure the design avoids. Fallback: the listing and its comment.`);

codeSlide("COORDINATING AND TRAVERSING", "A tariff, two readings",
  "examples/25-visitor-memento-interpreter/src/visitor_memento_interpreter/tariff.py", 44, 59,
  "def evaluate(expr: Expr, consignment: Consignment, /) -> Money:",
  "One tree of frozen nodes: evaluate prices a consignment from it, and a second match explains it as text.",
  `Interpreter is for rules that people write down and the program must apply. The classes stay in Python, as a small grammar of frozen nodes under a type alias, and the operations over them are matches. The listing prices a consignment: a per-kilogram node, a flat amount, a sum, a maximum and an overweight branch. A second function explains the same tree as text. Three tests witness the claim: explain writes the tariff as text, every rule form prices the same consignments, and mypy reports a tariff node left out of evaluate. PEP 634 and PEP 636 are the credit for match. What to show: the explain test beside the evaluate listing. Fallback: the listing and the caption describe the two readings.`);

figSlide("COORDINATING AND TRAVERSING", "Match, snapshot, tariff tree", "25-visitor-memento-interpreter",
  "Operations over the event union are matches; a booking rolls back from a frozen snapshot; one tariff tree is priced and explained.",
  `The figure draws three columns from the same module. In the first, each operation over the closed event union is one match, and mypy reports a kind it leaves out. In the second, a booking rolls back from a frozen snapshot that leaves the audit alone. In the third, one tariff tree is both priced and explained. The arrows follow the code in the match, rollback and tariff listings. The figure has its own slide because its small labels need the full width. What to show: the figure at full width, one column at a time. Fallback: the caption lists the three columns, and the three listings before it hold the code.`);

// ===========================================================================
// Section: Choosing well
// ===========================================================================
divider("08", "Choosing well", "When to skip a pattern, and how to ask for one",
  `A catalogue is useful if it can say no. Skip conditions say when a pattern is the wrong answer, the force table reads the catalogue back by force rather than by name, and a sample prompt names the decision before it asks for code. The skip conditions come from the sentences that close the pattern discussions, and the force column comes from the book's pattern-to-force reference, quoted without change.`);

tableSlide("CHOOSING WELL", "Skip conditions",
  ["Pattern", "Skip it when"], [
    ["Strategy", "A single rule called from one place is a function, with no registry."],
    ["State", "A two-state flag is a bool."],
    ["Singleton", "Pass a parameter when state differs per test, per tenant or per request."],
    ["Adapter, Facade, Bridge", "Call the client when there's one carrier and the SDK already fits."],
    ["Observer", "Call the parties directly when the set is fixed at the time the subject is built."],
    ["Iterator", "Pass the tuple when the data is already in a list that callers index or measure."],
  ], [3.2, 8.89],
  `The rows are sentences that open or close a pattern's discussion of when to leave it out. The force that justified the pattern is missing in these cases: a single rule has nothing to select among, a two-state flag has no transition table worth keeping, a value that differs per test can't be shared, one carrier has nothing to adapt between, a fixed set of parties has no subscribers to manage, and data already in a list has nothing to stream. No test backs these rows. They rest on the book's reasoning, and the table claims what the sentences claim. What to show: pick one row and name the force that is absent. Fallback: the right column is the rule, in the book's own words.`, { rowH: 0.62, fontSize: 14, y: 1.7 });

tableSlide("CHOOSING WELL", "Pattern to force",
  ["Pattern", "The force it answers"], [
    ["Factory Method", "The force is real: the caller wants a gateway for a carrier and shouldn't know which gateway class that is."],
    ["Strategy", "a caller must choose among several ways of computing one result without depending on which one it holds"],
    ["Template Method", "a sequence that has to hold across variants that differ in a few steps"],
    ["State", "The force is that the legal transitions are a business rule that has to be written in one place and checked."],
    ["Command", "The force is that a change needs an identity of its own."],
    ["Adapter", "two parts that disagree about shape: one calls, the other supplies, and an object between them translates"],
    ["Facade", "a subsystem with many parts and a caller that wants a few operations"],
    ["Flyweight", "the same few commodities can repeat across many consignments, and each repetition costs an object"],
    ["Visitor (closed set)", "Visitor is for a fixed family of kinds that gets new operations over time."],
    ["Interpreter", "Interpreter is for rules that people write down and the program must apply."],
  ], [2.5, 9.59],
  `A pattern answers one force, and the quickest way into the catalogue is to start from the force you have. Ten rows are shown, with the book's own wording of the force. Start from a caller who must choose among several ways of computing one result, and the row says Strategy; start from legal transitions as a business rule, and it says State. The column is read from the force back to the pattern, which is the direction a design review travels. Brandon Rhodes's pattern pages and the Design Patterns catalogue are the starting points for the wording. What to show: cover the left column and name the pattern from the right. Fallback: read two rows and the direction of travel is clear.`, { rowH: 0.47, fontSize: 12, y: 1.5 });

{
  const s = S();
  addContentTitle(s, "CHOOSING WELL", "Prompting for a pattern");
  bullets(s, [
    ["A request", " for \"a visitor\" or \"a memento\" names a 1994 shape and leaves open whether the kinds are closed, what a snapshot captures and what it must leave alone."],
    ["State those", " in the prompt:"],
  ], { h: 1.55, fontSize: 17, gap: 8 });
  s.addShape("rect", { x: 0.62, y: 3.35, w: 0.06, h: 2.35, fill: { color: COLOR.red }, line: { color: COLOR.red, width: 0 } });
  s.addShape("rect", { x: 0.68, y: 3.35, w: 12.03, h: 2.35, fill: { color: COLOR.panel }, line: { color: COLOR.panel, width: 0 } });
  s.addText("Over the closed HandlingEvent union, write each operation as one function using match that ends in case _: assert_never(event). Snapshot a Booking into a frozen BookingSnapshot holding the request and a frozenset of documents, leave the audit out, and restore it in a rollback context manager that re-raises. Write tariff rules as frozen node dataclasses under type Expr, with evaluate and explain each a single match.", {
    x: 0.85, y: 3.42, w: 11.7, h: 2.2, fontFace: FONT.body, fontSize: 15, italic: true, color: COLOR.body, align: "left", valign: "middle",
  });
  bullets(s, [
    ["Review line:", " if the reply adds an accept method or snapshots with copy.copy, ask for the test that fails."],
  ], { y: 5.85, h: 0.9, fontSize: 17 });
  notes(s, `A request for a visitor or a memento names a 1994 shape and leaves open the decisions that matter, so the prompt states them: the closed set of event kinds, a match per operation that ends in assert_never, a frozen snapshot that leaves the audit out, a rollback context manager that re-raises, and tariff rules as frozen nodes. The review line is a check on the reply. An accept method means the Visitor shape came back, and copy.copy means the snapshot may share state with the booking; in either case ask for the test that fails. No test backs this slide; the prompt and the review line stand as written. What to show: the prompt beside the visitor, memento and tariff listings it describes. Fallback: the prompt reads as a checklist on its own.`, 90, "bullets");
}

// ===========================================================================
// Section: Reference
// ===========================================================================
divider("09", "Reference", "Versions, sources and further reading",
  `The pinned versions the examples were built and checked with come first, then the online sources and the books behind the catalogue and the principles. The listings passed under those versions. The closing slide gives the address of the book's site and of the repository that holds the examples.`);

tableSlide("REFERENCE", "The toolchain",
  ["Tool", "Version", "Role"], [
    ["CPython", "3.15.2", "Interpreter, installed by uv"],
    ["uv", "0.13.7", "Interpreter, environment, lockfile"],
    ["pytest", "9.2.0", "Test runner"],
    ["pytest-mock", "3.17.0", "mocker fixture over unittest.mock"],
    ["ruff", "0.17.4", "Lint and format"],
    ["mypy", "2.4.1", "Static types, run with --strict"],
  ], [2.6, 1.9, 7.59],
  `The listings passed under these exact versions: CPython 3.15.2 as the interpreter, uv 0.13.7 for the environment and lockfile, pytest 9.2.0 and pytest-mock 3.17.0 for the tests, ruff 0.17.4 for lint and format, and mypy 2.4.1 in strict mode. A pin that moves is a claim that has to be re-run, so the pins are exact and a build script runs the whole sequence of checks on the repository, from the locked sync to the type check of the scripts and the tests. The uv and ruff documentation from Astral, the mypy and pytest documentation, and the Python documentation are credited as sources. What to show: uv --version and python --version in a terminal. Fallback: the table is the record.`, { rowH: 0.5, fontSize: 15, y: 1.8 });

tableSlide("REFERENCE", "Sources credited",
  ["Source", "Used for"], [
    ["Brandon Rhodes, python-patterns.guide", "Readings of the catalogue patterns as Python writes them"],
    ["Python Enhancement Proposals", "The design record behind decorators, generators, match and exception groups"],
    ["The Python, mypy, pytest, typing, uv and ruff documentation", "Language, library and tool behaviour"],
    ["Martin Fowler, articles and bliki", "Dependency injection, YAGNI, Beck's design rules"],
    ["Mark Seemann, Composition Root", "Where the object graph is composed"],
    ["Jim Shore, Fail Fast", "Failing at the first sign of a fault"],
    ["Harry Percival and Bob Gregory, cosmicpython.com", "Commands as messages with one handler"],
    ["The Demeter project, Northeastern University", "The Law of Demeter"],
    ["The Pragmatic Programmer, tips page", "DRY"],
    ["Liskov and Wing, A Behavioral Notion of Subtyping (1994)", "The behavioural definition of substitutability"],
    ["Bertrand Meyer, Object-Oriented Software Construction", "The open-closed principle"],
  ], [5.6, 6.49],
  `Sources are credited where an idea leans on them. The wording and the examples are new, and the short quotations are attributed. Brandon Rhodes's guide supplies the readings of Composite, Decorator, Factory Method, Iterator and Singleton as Python writes them. The PEPs record why a feature exists. Fowler and Seemann supply the vocabulary of injection and the composition root. Percival and Gregory's free book describes commands as messages with one handler. Liskov and Wing, and Meyer, are credited for the principles they introduced. An archived ActiveState recipe is credited for the Borg variant of Singleton. What to show: nothing; the table is the record. Fallback: the rows name the source and what it was used for.`, { rowH: 0.40, fontSize: 12, y: 1.55 });

tableSlide("REFERENCE", "Reading further",
  ["Book", "Authors", "Year"], [
    ["Design Patterns: Elements of Reusable Object-Oriented Software", "Gamma, Helm, Johnson, Vlissides", "1994"],
    ["Fluent Python", "Ramalho", "2022"],
    ["Effective Python, third edition", "Slatkin", "2024"],
    ["Architecture Patterns with Python", "Percival, Gregory", "2020"],
    ["Python Object-Oriented Programming, fifth edition", "Lott, Phillips", "2025"],
    ["Agile Software Development: Principles, Patterns, and Practices", "Martin", "2002"],
    ["Object-Oriented Software Construction", "Meyer", "1997"],
    ["The Pragmatic Programmer", "Thomas, Hunt", "2019"],
    ["Clean Code", "Martin", "2008"],
    ["Refactoring, second edition", "Fowler", "2018"],
  ], [7.0, 3.9, 1.19],
  `Ten books stand behind the discussion. Design Patterns is the catalogue itself. Fluent Python and Effective Python, both by Python practitioners, are companions to the language features that dissolve patterns. Python Object-Oriented Programming covers the class machinery. Percival and Gregory take patterns into application architecture. Martin's Agile Software Development states the single responsibility principle and its neighbours, and Meyer's Object-Oriented Software Construction states the open-closed principle. The Pragmatic Programmer is the source for DRY; Clean Code and Refactoring are cited for naming and for review. What to show: nothing; the list is the reference. Fallback: titles, authors and years are enough to find them.`, { rowH: 0.45, fontSize: 14, y: 1.7 });

bulletSlide("REFERENCE", "Site and repository", [
  ["The book", " is at https://patterncatalyst.github.io/design-patterns-with-python/"],
  ["The repository", " holds the examples: https://github.com/patterncatalyst/design-patterns-with-python"],
  ["To run an example,", " sync the workspace once with uv sync --locked --all-packages, then run uv run pytest and uv run mypy --strict src tests inside an example directory."],
  ["Two further decks", " follow by theme: what the language gives you so you don't write the pattern, and testing, inherited code and working with AI tools."],
], `The book's site holds the prose and the figures. The repository holds the examples that the listings were read from, with their tests, so a claim can be re-run. An example runs on its own: sync the workspace once from the root, then run pytest and mypy in strict mode from the example's directory, since both discover the root configuration. The two further decks cover, by theme, what Python gives you so that you don't write a pattern, and testing, changing inherited code and working with AI tools on pattern-heavy code. What to show: the site's home page and the repository's examples directory. Fallback: the two addresses on the slide are enough to find both.`, { fontSize: 17 });

// ===========================================================================
// Checks and write
// ===========================================================================
const short = floors.filter(([, n, floor]) => n < floor);
if (short.length) {
  throw new Error("notes under floor: " + short.map(([p, n, f, l]) => `slide ${p} ${l} ${n}<${f}`).join(", "));
}
if (floors.length !== pageNum) throw new Error(`notes ${floors.length} != slides ${pageNum}`);

pres
  .writeFile({ fileName: OUT })
  .then((p) => console.log("WROTE", p, "slides:", pageNum, "min notes words:", Math.min(...floors.map((f) => f[1]))))
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });
