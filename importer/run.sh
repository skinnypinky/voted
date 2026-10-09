#!/usr/bin/env bash
set -euo pipefail

# Find project root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Load environment variables
if [[ ! -f .env ]]; then
    echo "Error: .env file not found."
    echo "Create it using: cp .env.example .env"
    exit 1
fi

set -a
source .env
set +a

echo "Starting database..."
docker compose up -d
"$ROOT_DIR/database/migrate.sh"

echo "Importing voting data..."
.venv/bin/python importer/parser.py

echo "Validating imported data..."
.venv/bin/python importer/validate.py

echo "Import and validation completed successfully."
