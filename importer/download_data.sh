#!/usr/bin/env bash
set -euo pipefail

# Expected location: <project-root>/scripts/download_data.sh
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$ROOT_DIR/importer/data"
mkdir -p "$DATA_DIR"

# Use the project's Python when possible; otherwise use an installed Python 3.
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    PYTHON="$ROOT_DIR/.venv/bin/python"
elif [[ -x "$ROOT_DIR/.venv/Scripts/python.exe" ]]; then
    PYTHON="$ROOT_DIR/.venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
else
    echo "ERROR: Python 3 is required to validate ZIP archives." >&2
    exit 1
fi

# Check archive integrity and count its JSON entries without extracting it.
zip_json_count() {
    "$PYTHON" - "$1" <<'PY'
import sys
import zipfile

with zipfile.ZipFile(sys.argv[1]) as z:
    bad = z.testzip()
    if bad is not None:
        raise RuntimeError(f"Corrupted ZIP entry: {bad}")
    print(sum(name.lower().endswith('.json') for name in z.namelist()))
PY
}

staging=""
backup=""
part=""
year_dir=""

cleanup() {
    if [[ -n "$staging" && -d "$staging" ]]; then
        rm -rf -- "$staging"
    fi
    if [[ -n "$part" && -f "$part" ]]; then
        rm -f -- "$part"
    fi
    if [[ -n "$backup" && -e "$backup" ]]; then
        if [[ -n "$year_dir" && ! -e "$year_dir" ]]; then
            echo "Restoring previous data from $backup" >&2
            mv -- "$backup" "$year_dir" || true
        else
            echo "Previous data backup retained at $backup" >&2
        fi
    fi
}
trap cleanup EXIT

for year in 202223 202324 202425 202526; do
    archive="$DATA_DIR/votering-$year.json.zip"
    year_dir="$DATA_DIR/$year"

    # Minimum counts for the validated 2026-10 dataset snapshot.
    # Newer archives can contain additional records.
    case "$year" in
        202223) baseline=564 ;;
        202324) baseline=594 ;;
        202425) baseline=656 ;;
        202526) baseline=798 ;;
    esac

    existing=0
    if [[ -d "$year_dir" ]]; then
        existing=$(find "$year_dir" -maxdepth 1 -type f -name '*.json' | wc -l | tr -d '[:space:]')
    fi

    cached_count=""
    if [[ -f "$archive" ]]; then
        if cached_count=$(zip_json_count "$archive" 2>/dev/null); then
            if (( cached_count < baseline )); then
                echo "$year: Cached ZIP is older/incomplete ($cached_count < $baseline)." >&2
                cached_count=""
            fi
        else
            echo "$year: Cached ZIP failed integrity check; it will be redownloaded." >&2
            cached_count=""
        fi
    fi

    expected="${cached_count:-$baseline}"
    if (( existing == expected )); then
        echo "$year: $existing/$expected files already exist. Skipping."
        continue
    fi

    echo "$year: Incomplete local dataset ($existing/$expected)."

    if [[ -z "$cached_count" ]]; then
        echo "$year: Downloading archive..."
        part="$archive.part"
        rm -f -- "$part"
        curl -fL --retry 3 --output "$part" \
            "https://data.riksdagen.se/dataset/votering/votering-$year.json.zip"

        expected=$(zip_json_count "$part")
        if (( expected < baseline )); then
            echo "ERROR: $year archive has only $expected JSON entries (minimum $baseline)." >&2
            exit 1
        fi
        mv -- "$part" "$archive"
        part=""
    else
        echo "$year: Reusing verified cached ZIP."
    fi

    # Place staging on the same filesystem as final data for safe renaming.
    staging=$(mktemp -d "$DATA_DIR/.extract-${year}.XXXXXX")
    echo "$year: Extracting..."

    case "$(uname -s)" in
        Darwin)
            ditto -x -k "$archive" "$staging"
            ;;
        Linux)
            unzip -oq "$archive" -d "$staging"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            # Intended for Git Bash on Windows, using native PowerShell extraction.
            if command -v pwsh >/dev/null 2>&1; then
                powershell=pwsh
            elif command -v powershell.exe >/dev/null 2>&1; then
                powershell=powershell.exe
            else
                echo "ERROR: PowerShell not found on Windows." >&2
                exit 1
            fi
            (
                cd "$DATA_DIR"
                ARCHIVE="$(basename "$archive")" DEST="$(basename "$staging")" \
                    "$powershell" -NoProfile -NonInteractive -Command \
                    '$ErrorActionPreference = "Stop"; Expand-Archive -LiteralPath $env:ARCHIVE -DestinationPath $env:DEST -Force'
            )
            ;;
        *)
            echo "ERROR: Unsupported OS: $(uname -s)" >&2
            exit 1
            ;;
    esac

    actual=$(find "$staging" -maxdepth 1 -type f -name '*.json' | wc -l | tr -d '[:space:]')
    if (( actual != expected )); then
        echo "ERROR: $year expected $expected JSON files, found $actual." >&2
        exit 1
    fi

    # Keep the previous directory available until the new one is in place.
    if [[ -e "$year_dir" ]]; then
        backup=$(mktemp -d "$DATA_DIR/.backup-${year}.XXXXXX")
        rmdir "$backup"
        mv -- "$year_dir" "$backup"
    fi

    if ! mv -- "$staging" "$year_dir"; then
        echo "ERROR: Could not install verified data for $year." >&2
        exit 1
    fi
    staging=""

    if [[ -n "$backup" ]]; then
        rm -rf -- "$backup"
        backup=""
    fi

    echo "$year: $actual/$expected JSON files verified."
done

echo "All datasets downloaded and verified successfully."

