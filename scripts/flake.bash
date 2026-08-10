#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"
source "${ROOT}/scripts/_env.bash"

PATHS=(src tests scripts demos .agents/skills/heaven-style/scripts)
LINE_LENGTH=160
FLAKE8_IGNORE="F401,F403,F405,F821,E203,E402,E501,W503,E701,E704,E741"
MODE="flake"

usage() {
    cat <<'EOF'
Usage: bash scripts/flake.bash [OPTIONS]

Run Black and/or Flake8 through uv.

Options:
  --black              Run Black formatter only.
  --check              Run Black check only.
  --flake              Run Flake8 only.
  --all, -a             Run Black formatter, then Flake8.
  --ci                 Run Black check, then Flake8.
  --paths PATH...      Override target paths. Consumes values until the next option.
  --line-length N      Override line length.
  --ignore CODES       Override Flake8 ignore list.
  -h, --help           Show this help message.

Examples:
  rtk bash scripts/flake.bash --ci
  rtk bash scripts/flake.bash --all --paths src tests
  rtk bash scripts/flake.bash --flake --ignore E501,W503
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --black)
            MODE="black"
            shift
            ;;
        --check)
            MODE="check"
            shift
            ;;
        --flake)
            MODE="flake"
            shift
            ;;
        --all|-a)
            MODE="all"
            shift
            ;;
        --ci)
            MODE="ci"
            shift
            ;;
        --paths)
            PATHS=()
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                PATHS+=("$1")
                shift
            done
            if [[ "${#PATHS[@]}" -eq 0 ]]; then
                echo "error: --paths requires at least one path" >&2
                exit 1
            fi
            ;;
        --line-length)
            if [[ $# -lt 2 ]]; then
                echo "error: --line-length requires a value" >&2
                exit 1
            fi
            LINE_LENGTH="$2"
            shift 2
            ;;
        --ignore)
            if [[ $# -lt 2 ]]; then
                echo "error: --ignore requires a value" >&2
                exit 1
            fi
            FLAKE8_IGNORE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "error: unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

filter_existing_paths() {
    local path
    local out=()
    for path in "${PATHS[@]}"; do
        if [[ -e "${path}" ]]; then
            out+=("${path}")
        fi
    done
    array_copy PATHS out
    if [[ "${#PATHS[@]}" -eq 0 ]]; then
        echo "[flake] no target paths found"
        exit 0
    fi
}

filter_existing_paths
resolve_uv

run_black_format() {
    uv_run black "${PATHS[@]}" --line-length "${LINE_LENGTH}"
}

run_black_check() {
    uv_run black "${PATHS[@]}" --line-length "${LINE_LENGTH}" --check --diff
}

run_flake8() {
    uv_run flake8 "${PATHS[@]}" --max-line-length "${LINE_LENGTH}" --ignore "${FLAKE8_IGNORE}" --exclude ".temp,.venv,__pycache__,*.egg-info"
}

case "${MODE}" in
    black)
        run_black_format
        ;;
    check)
        run_black_check
        ;;
    flake)
        run_flake8
        ;;
    all)
        run_black_format
        run_flake8
        ;;
    ci)
        run_black_check
        run_flake8
        ;;
esac
