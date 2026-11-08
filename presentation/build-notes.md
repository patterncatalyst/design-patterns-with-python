# Building the companion decks

This directory holds the companion slide decks for *Design Patterns with Python*,
built with the `lgtm-presentation` skill's pptxgenjs engine. The builders
(`deck-101.js` and `deck-201.js`) read code slides from the shipped examples by
path and line range, so a slide is byte-exact with its source.

## Pins

| Item | Version | Notes |
| --- | --- | --- |
| pptxgenjs | 4.0.1, exact | npm `latest`; the `beta` tag is a pre-release and is not used |
| image-size | 2.1.0, `overrides` only | clears two advisories against 1.2.1 that pptxgenjs pulls in; pptxgenjs never loads it |
| cairosvg | 2.9.1 | run through `uv run --no-project`; never added to the uv workspace |
| Node.js, npm | 22, 10 | host tools, not installed by this repo |

`package-lock.json` is committed (lockfileVersion 3). `npm audit` reports 0
vulnerabilities.

## Install and build

From this directory, and only here:

```bash
npm ci
node -e "console.log(require.resolve('pptxgenjs'))"   # must point under ./node_modules
./render-png.sh                                       # the figure PNGs, both decks
node deck-101.js
node deck-201.js
```

Never `npm install -g`, never set `NODE_PATH`. The deck must load the copy in
`node_modules/` that the lockfile pins.

## The helper

`deck-helpers.js` is the skill's `scripts/deck-helpers.js` (md5
`abedd5abb9a98c475b1d050febc25ca7`) with one local delta: its eight em-dash
lines are reworded, so the repo-wide voice gate passes without an exclusion.
No code changed. The new md5 is `47af3889bef56eba4736bb1565e17054`.

| Line | What changed |
| --- | --- |
| 1 | header comment: the dash after the file name became a colon |
| 65 | default `pres.title`: the dash before "Python" became a colon |
| 79 | logo comment: the dash became a comma |
| 136 | two-column comment: dash to colon |
| 177 | status-table comment: dash to colon |
| 233 | perf sidebar comment: dash to colon |
| 304 | code text comment: dash to colon |
| 334 | background comment: dash to colon |

The deck builder overrides `pres.title`, `pres.author`, `pres.company` and
`pres.subject` after `newDeck()`, so the helper's default title never ships.

## The shared module

`deck-lib.js` holds the slide helpers that both builders use. A builder creates
its presentation with `newDeck()`, sets the metadata, and calls
`createDeck(pres)`, which returns the helpers bound to that presentation:

| Export | Purpose |
| --- | --- |
| `S()` | a content slide with footer and page number |
| `divider(code, title, subtitle, text)` | section divider; the `AB0000` background is what the deck check keys on |
| `bullets`, `bulletSlide` | bold-subject bullets, alone or on a titled slide |
| `tableSlide` | header row plus striped body rows, first column bold |
| `codeSlide` | listing read byte-exact from a source file by line range, first line asserted, font sized to fit, caption under the box |
| `figSlide` | figure PNG fitted by its own aspect, never stretched |
| `notes(slide, text, floor, label)`, `words` | speaker notes with a word-count floor |
| `bump()` | count a slide the builder adds itself, such as the cover |
| `finish(out)` | assert the notes floors and the notes count, then write the file |

The slide counter and the floors live inside the closure, so two decks never
share state. `deck-helpers.js` is not touched by the module.

### Identity proof for Deck 101

Moving the helpers out of `deck-101.js` must not change Deck 101. The proof:

```bash
node deck-101.js                       # rebuild in place
unzip -q -d new design-patterns-with-python-101-patterns-and-solid.pptx
git show HEAD:presentation/design-patterns-with-python-101-patterns-and-solid.pptx > old.pptx
unzip -q -d old old.pptx
diff -rq old new                       # only docProps/core.xml may differ
```

Run the commands from `presentation/`; the unzip targets can sit in any scratch directory. Both trees hold 342 parts;
`docProps/core.xml` differs only in its `created` and `modified` timestamps.
After the proof, `git checkout` restores the committed `.pptx`, so its bytes do
not change and a refactor commit holds only code. Re-run the proof whenever
`deck-lib.js` or `deck-helpers.js` changes.

## Figures

`render-png.sh` renders `diagrams/<NN>-*.svg` to `png/` at width 1600. With no
arguments it renders both decks' lists (101: eleven figures; 201: five);
`--deck 101` or `--deck 201` selects one list, and figure numbers on the
command line override both. Run
`./render-png.sh --check` to render into a temporary directory and compare each
committed PNG with a fresh render; the render is deterministic, so any
difference means the SVG changed or the PNG is stale. A figure that is wrong is
fixed in its spec under `diagrams/specs/`, never redrawn for the deck.

## Quality checks

`qa/` and `*.pdf` are ignored scratch output.

```bash
soffice -env:UserInstallation=file://$TMPDIR/lo-qa --headless \
  --convert-to pdf --outdir qa <deck>.pptx
pdffonts qa/<deck>.pdf
pdftoppm -jpeg -r 110 qa/<deck>.pdf qa/p
python3 notes.py <deck>.pptx > qa/notes.txt
python3 notes.py --slides <deck>.pptx > qa/slides.txt
```

`notes.py` extracts the text because pptxgenjs writes a notes slide for every
slide, empty or not, so counting notes files proves nothing.
