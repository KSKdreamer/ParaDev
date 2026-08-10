#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"
source "${ROOT}/scripts/_env.bash"

CHECK=0
SYNC=1
UV_SYNC_ARGS=(--all-extras)
README_ARGS=()
INSTALL_HEAVENBASE=0
HEAVENBASE_REPO_URL="${HEAVENBASE_REPO_URL:-https://github.com/Magolor/HeavenBase.git}"
HEAVENBASE_CLONE_DIR="${HEAVENBASE_CLONE_DIR:-.temp/deps/HeavenBase}"

usage() {
    cat <<'EOF'
Usage: bash scripts/sync-env.bash [OPTIONS] [-- UV_SYNC_ARGS...]

Synchronize lockfiles and generated metadata from repository source files.

Edit requirements.txt and requirements-dev.txt first. pyproject.toml reads them
through setuptools dynamic metadata. Keep the product version only in
src/paradev/version.py. This script refreshes Python/frontend version metadata,
the release project-package catalog binding, uv.lock, poetry.lock, and
environment-dev.yml.

Options:
  --check       Verify uv.lock, poetry.lock, and generated files are current.
  --no-sync     Update lock/generated files without running uv sync.
  --heavenbase-source
                Install a temporary editable HeavenBase source override after uv sync.
  --no-heavenbase
                Do not install a temporary HeavenBase source override.
  --readme-target PATH
                Also sync/check README.en.md to PATH.
  --readme-resource-target IMPORT_NAME
                Also sync/check src/IMPORT_NAME/resources/README.md.
  -h, --help    Show this help message.

Examples:
  rtk bash scripts/sync-env.bash
  rtk bash scripts/sync-env.bash --check
  rtk bash scripts/sync-env.bash -- --extra dev
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)
            CHECK=1
            SYNC=0
            shift
            ;;
        --no-sync)
            SYNC=0
            shift
            ;;
        --heavenbase-source)
            INSTALL_HEAVENBASE=1
            shift
            ;;
        --no-heavenbase)
            INSTALL_HEAVENBASE=0
            shift
            ;;
        --readme-target)
            if [[ $# -lt 2 ]]; then
                echo "error: --readme-target requires a value" >&2
                exit 1
            fi
            README_ARGS+=(--target "$2")
            shift 2
            ;;
        --readme-resource-target)
            if [[ $# -lt 2 ]]; then
                echo "error: --readme-resource-target requires a value" >&2
                exit 1
            fi
            README_ARGS+=(--resource-target "$2")
            shift 2
            ;;
        --)
            shift
            UV_SYNC_ARGS+=("$@")
            break
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            UV_SYNC_ARGS+=("$1")
            shift
            ;;
    esac
done

resolve_uv

heavenbase_source() {
    local source
    if [[ -n "${HEAVENBASE_SOURCE:-}" ]]; then
        printf '%s\n' "${HEAVENBASE_SOURCE}"
        return
    fi
    if source="$(discover_local_heavenbase_source "${ROOT}")"; then
        printf '%s\n' "${source}"
        return
    fi
    if [[ ! -d "${HEAVENBASE_CLONE_DIR}/.git" ]]; then
        mkdir -p "$(dirname -- "${HEAVENBASE_CLONE_DIR}")"
        git clone --depth 1 --quiet "${HEAVENBASE_REPO_URL}" "${HEAVENBASE_CLONE_DIR}"
    else
        git -C "${HEAVENBASE_CLONE_DIR}" pull --ff-only --quiet
    fi
    printf '%s\n' "${HEAVENBASE_CLONE_DIR}"
}

install_heavenbase() {
    local marker python source
    [[ "${INSTALL_HEAVENBASE}" -eq 1 ]] || return 0
    source="$(heavenbase_source)"
    if ! python="$(venv_python "${ROOT}/.venv")"; then
        echo "error: repo .venv is missing after uv sync" >&2
        exit 1
    fi
    "${UV_BIN}" pip install --python "${python}" --reinstall --no-deps -e "${source}"
    marker="$(heavenbase_override_marker)"
    printf '%s\n' "$(cd -- "${source}" && pwd -P)" >"${marker}"
    echo "[sync-env] HeavenBase source override: $(<"${marker}")"
}

sync_poetry_lock() {
    uv_run --with poetry poetry lock
    echo "[sync-env] refreshed poetry.lock"
}

check_poetry_lock() {
    if [[ ! -f poetry.lock ]]; then
        echo "error: poetry.lock is missing; run rtk bash scripts/sync-env.bash" >&2
        exit 1
    fi
    uv_run --with poetry poetry check
    echo "[sync-env] poetry.lock is current"
}

if [[ "${CHECK}" -eq 1 ]]; then
    UV_BIN="${UV_BIN}" run_uv_python scripts/sync-env.py --check
    "${UV_BIN}" lock --check
    check_poetry_lock
    run_with_array README_ARGS bash scripts/sync-readme.bash --check
    echo "[sync-env] generated files are current"
    exit 0
fi

UV_BIN="${UV_BIN}" run_uv_python scripts/sync-env.py
"${UV_BIN}" lock
sync_poetry_lock
if [[ "${SYNC}" -eq 1 ]]; then
    rm -f "$(heavenbase_override_marker)"
    "${UV_BIN}" sync "${UV_SYNC_ARGS[@]}"
    install_heavenbase
fi
run_with_array README_ARGS bash scripts/sync-readme.bash
