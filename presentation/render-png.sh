#!/usr/bin/env bash
# Render figure PNGs from the committed diagrams/*.svg with cairosvg 2.9.1.
#
#   ./render-png.sh 05 06 12 19 21 25   render those figures into png/
#   ./render-png.sh --check 05 06 ...   render into a temp dir and fail if any
#                                       committed PNG differs from a fresh render
#   ./render-png.sh --deck 101|201|301  use that deck's figure list (add --check
#                                       to compare instead of write)
#
# With no figure numbers it uses all three decks' lists together: the eleven
# figures of Deck 101, the five of Deck 201 and the two of Deck 301 (eighteen in
# all).
# cairosvg runs through `uv run --no-project`: it is never added to the
# workspace, and nothing is installed globally.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
diagrams="$here/../diagrams"
CAIROSVG="2.9.1"
WIDTH=1600

# Per-deck figure lists. Keep each in step with the figures its builder uses.
figs_101=(05 06 12 13 14 16 19 21 22 23 25)
figs_201=(07 09 10 31 37)
figs_301=(33 40)

check=0
deck=""
while [[ "${1:-}" == --* ]]; do
  case "$1" in
    --check) check=1; shift ;;
    --deck)  deck="${2:?render-png: --deck needs 101, 201 or 301}"; shift 2 ;;
    *) echo "render-png: unknown option $1" >&2; exit 2 ;;
  esac
done
figs=("$@")
if [[ ${#figs[@]} -eq 0 ]]; then
  case "$deck" in
    101) figs=("${figs_101[@]}") ;;
    201) figs=("${figs_201[@]}") ;;
    301) figs=("${figs_301[@]}") ;;
    "")  figs=("${figs_101[@]}" "${figs_201[@]}" "${figs_301[@]}") ;;
    *) echo "render-png: unknown deck $deck" >&2; exit 2 ;;
  esac
fi

out="$here/png"
if [[ $check -eq 1 ]]; then
  out="$(mktemp -d)"
  trap 'rm -rf "$out"' EXIT
fi
mkdir -p "$out"

render_py="$(mktemp --suffix=.py)"
trap 'rm -f "$render_py"; [[ $check -eq 1 ]] && rm -rf "$out"' EXIT
cat >"$render_py" <<'PY'
import sys
import cairosvg

src, dst, width = sys.argv[1], sys.argv[2], int(sys.argv[3])
cairosvg.svg2png(url=src, write_to=dst, output_width=width)
PY

for n in "${figs[@]}"; do
  svg=("$diagrams/$n"-*.svg)
  if [[ ${#svg[@]} -ne 1 || ! -f "${svg[0]}" ]]; then
    echo "render-png: no unique diagrams/$n-*.svg" >&2
    exit 1
  fi
  name="$(basename "${svg[0]}" .svg)"
  uv run --no-project --python 3.15 --with "cairosvg==$CAIROSVG" \
    python -I "$render_py" "${svg[0]}" "$out/$name.png" "$WIDTH"
  if [[ $check -eq 1 ]]; then
    if cmp -s "$out/$name.png" "$here/png/$name.png"; then
      echo "same   png/$name.png"
    else
      echo "DIFFER png/$name.png" >&2
      status=1
    fi
  else
    echo "wrote  png/$name.png"
  fi
done
exit "${status:-0}"
