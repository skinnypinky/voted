#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Waiting for PostgreSQL..."
until docker compose exec -T db pg_isready -U postgres -d voted >/dev/null 2>&1; do
    sleep 1
done

docker compose exec -T db psql -U postgres -d voted <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SQL

for migration in database/migrations/*.sql; do
    filename="$(basename "$migration")"

    already_applied=$(
        docker compose exec -T db psql \
            -U postgres \
            -d voted \
            -Atc "SELECT EXISTS (
                SELECT 1
                FROM schema_migrations
                WHERE filename = '$filename'
            );"
    )

    if [ "$already_applied" = "t" ]; then
        echo "Skipping $filename"
        continue
    fi

    echo "Running $filename"

    docker compose exec -T db psql \
        -v ON_ERROR_STOP=1 \
        -U postgres \
        -d voted < "$migration"

    docker compose exec -T db psql \
        -U postgres \
        -d voted \
        -c "INSERT INTO schema_migrations (filename) VALUES ('$filename');"
done