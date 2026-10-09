#!/usr/bin/env bash
set -euo pipefail

# Find project root regardless of where the script is called from
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Starting database..."
docker compose up -d
"$ROOT_DIR/database/migrate.sh"

echo "Importing voting data..."
.venv/bin/python importer/parser.py

echo "Validating imported data..."
.venv/bin/python importer/validate.py

echo "Import and validation completed successfully."
