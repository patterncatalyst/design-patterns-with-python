#!/usr/bin/env bash
# Render figure PNGs from the committed diagrams/*.svg with cairosvg 2.9.1.
#
#   ./render-png.sh 05 06 12 19 21 25   render those figures into png/
#   ./render-png.sh --check 05 06 ...   render into a temp dir and fail if any
#                                       committed PNG differs from a fresh render
#
# With no figure numbers it uses the eleven figures that pass the arrow census.
# cairosvg runs through `uv run --no-project`: it is never added to the
# workspace, and nothing is installed globally.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
diagrams="$here/../diagrams"
CAIROSVG="2.9.1"
WIDTH=1600

check=0
if [[ "${1:-}" == "--check" ]]; then
  check=1
  shift
fi
figs=("$@")
if [[ ${#figs[@]} -eq 0 ]]; then
  figs=(05 06 12 13 14 16 19 21 22 23 25)
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
