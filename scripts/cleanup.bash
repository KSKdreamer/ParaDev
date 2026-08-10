#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"

REMOVE_ENV=0

usage() {
    cat <<'EOF'
Usage: bash scripts/cleanup.bash [OPTIONS]

Remove local caches, build artifacts, Finder metadata, and temporary demo data.

Options:
  --env       Also remove the uv virtual environment at .venv.
  -h, --help  Show this help message.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --env)
            REMOVE_ENV=1
            shift
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

rm -rf ./.pytest_cache
rm -rf ./.coverage
rm -rf ./.ruff_cache
rm -rf ./.mypy_cache
rm -rf ./coverage
rm -rf ./htmlcov
rm -rf ./build
rm -rf ./dist
rm -rf ./apps/desktop/dist
rm -rf ./.temp
rm -rf ./tmp
rm -rf ./temp
rm -rf ./__temp__
find . -type d -name __pycache__ -prune -exec rm -rf {} +
find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
find . \
    \( -path ./.git -o -path ./.venv -o -path ./node_modules -o -path ./apps/desktop/node_modules -o -path ./projects \) -prune \
    -o -type f -name .DS_Store -delete

if [[ -d demos/.temp ]]; then
    find demos/.temp -mindepth 1 ! -name .gitignore -exec rm -rf {} +
fi

if [[ "${REMOVE_ENV}" -eq 1 ]]; then
    rm -rf ./.venv
fi

echo "[cleanup] done"
