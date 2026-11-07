# Building the companion decks

This directory holds the companion slide decks for *Design Patterns with Python*,
built with the `lgtm-presentation` skill's pptxgenjs engine. The builders
(`deck-101.js` and its siblings) read code slides from the shipped examples by
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
./render-png.sh                                       # the figure PNGs
node deck-101.js
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

## Figures

`render-png.sh` renders `diagrams/<NN>-*.svg` to `png/` at width 1600. Run
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
