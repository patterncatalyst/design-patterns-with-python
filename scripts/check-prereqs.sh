#!/usr/bin/env bash
# Usage: scripts/check-prereqs.sh
#
# Verify the local toolchain the examples build with: uv, CPython 3.14, git,
# and the locked dev tools (ruff, mypy, pytest). Prints a table and exits
# non-zero if anything is missing. Installs nothing.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

missing=()
rows=()

record() { # name, ok(0/1), detail
    local name=$1 ok=$2 detail=$3
    if [ "$ok" -eq 0 ]; then
        rows+=("$(printf '%-8s %-6s %s' "$name" "OK" "$detail")")
    else
        rows+=("$(printf '%-8s %-6s %s' "$name" "FAIL" "$detail")")
        missing+=("$name")
    fi
}

have() { command -v "$1" >/dev/null 2>&1; }

if have uv; then
    record uv 0 "$(uv --version)"
    uv_ok=1
else
    record uv 1 "not found on PATH"
    uv_ok=0
fi

if [ "$uv_ok" -eq 1 ]; then
    if py="$(uv python find 3.14 2>/dev/null)" && [ -n "$py" ]; then
        record python 0 "$("$py" --version 2>&1) ($py)"
    else
        record python 1 "no Python 3.14 found (uv python install 3.14)"
    fi
else
    record python 1 "needs uv"
fi

if have git; then
    record git 0 "$(git --version)"
else
    record git 1 "not found on PATH"
fi

for tool in ruff mypy pytest; do
    if [ "$uv_ok" -eq 1 ] && out="$(uv run --all-packages --quiet "$tool" --version 2>/dev/null)"; then
        record "$tool" 0 "$out"
    else
        record "$tool" 1 "does not resolve (run: uv sync --locked --all-packages)"
    fi
done

echo "Checking local toolchain for Design Patterns with Python"
echo
printf '%-8s %-6s %s\n' TOOL STATUS DETAIL
printf '%s\n' "${rows[@]}"
echo

if [ "${#missing[@]}" -eq 0 ]; then
    echo "All prerequisites found."
else
    echo "Missing or failing: ${missing[*]}"
    echo "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh   (or: sudo dnf install uv)"
fi
echo "Teardown: rm -rf .venv && uv cache clean"

[ "${#missing[@]}" -eq 0 ]
