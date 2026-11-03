#!/usr/bin/env bash
# Usage: scripts/check-prereqs.sh
#
# Verify the local toolchain the examples build with: uv, CPython 3.14, git,
# and the locked dev tools (ruff, mypy, pytest). Prints a table and exits
# non-zero if anything is missing. A uv or CPython version that differs from
# the pins prints WARN (uv older than the pin is FAIL). Installs nothing.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

missing=()
rows=()

record() { # name, ok(0/1), detail
    local name=$1 ok=$2 detail=$3
    if [ "$ok" -eq 0 ]; then
        rows+=("$(printf '%-8s %-6s %s' "$name" "OK" "$detail")")
    elif [ "$ok" -eq 2 ]; then
        rows+=("$(printf '%-8s %-6s %s' "$name" "WARN" "$detail")")
    else
        rows+=("$(printf '%-8s %-6s %s' "$name" "FAIL" "$detail")")
        missing+=("$name")
    fi
}

# Pins: the interpreter from .python-version, uv from the setup-uv step in CI.
py_pin="$(tr -d '[:space:]' < .python-version)"
uv_pin="$(grep -A4 'astral-sh/setup-uv' .github/workflows/ci.yml | sed -n 's/.*version: *"\{0,1\}\([0-9][0-9.]*\).*/\1/p' | head -n1)"

have() { command -v "$1" >/dev/null 2>&1; }

if have uv; then
    uv_now="$(uv --version | awk '{print $2}')"
    if [ -z "$uv_pin" ] || [ "$uv_now" = "$uv_pin" ]; then
        record uv 0 "$(uv --version)"
    elif [ "$(printf '%s\n%s\n' "$uv_now" "$uv_pin" | sort -V | head -n1)" = "$uv_now" ]; then
        record uv 1 "$uv_now is older than the pinned $uv_pin (uv self update)"
    else
        record uv 2 "$uv_now is newer than the pinned $uv_pin"
    fi
    uv_ok=1
else
    record uv 1 "not found on PATH"
    uv_ok=0
fi

if [ "$uv_ok" -eq 1 ]; then
    if py="$(uv python find "${py_pin%.*}" 2>/dev/null)" && [ -n "$py" ]; then
        py_now="$("$py" --version 2>&1)"
        if [ -z "$py_pin" ] || [ "$py_now" = "Python $py_pin" ]; then
            record python 0 "$py_now ($py)"
        else
            record python 2 "$py_now, .python-version pins $py_pin (uv python install $py_pin)"
        fi
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
