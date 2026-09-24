#!/usr/bin/env bash
# Start the FastAPI application locally
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "ERROR: .env not found. Copy .env.example to .env and set DATABASE_URL."
  exit 1
fi

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "Starting Azure DevOps Employee API..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
