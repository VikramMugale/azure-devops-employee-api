#!/usr/bin/env bash
# Run lint, tests, and coverage
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "=== Ruff (lint) ==="
ruff check app tests

echo ""
echo "=== Pytest + coverage ==="
pytest --cov=app --cov-report=term-missing --cov-report=xml

echo ""
echo "All checks passed."
