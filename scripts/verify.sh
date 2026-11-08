#!/usr/bin/env bash
# Usage: scripts/verify.sh
# Full local gate: lint, format, strict typing per member, scripts typing, tests.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

step() { printf '\n==> %s\n' "$*"; }

step "Sync (locked, all packages)"
uv sync --locked --all-packages

step "ruff check"
uv run ruff check .

step "ruff format --check"
uv run ruff format --check .

step "mypy --strict per member"
for d in examples/*/ spikes/*/; do
    [ -f "$d/pyproject.toml" ] || continue
    echo "-- $d"
    (cd "$d" && uv run mypy --strict src tests)
done

step "mypy --strict repo scripts"
uv run mypy --strict scripts/validate.py scripts/render_diagrams.py

step "pytest"
uv run pytest

printf '\nverify: all steps passed\n'
