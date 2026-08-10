#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"
source "${ROOT}/scripts/_env.bash"

OUT_DIR="${ROOT}/dist/python"

usage() {
    cat <<'EOF'
Usage: bash scripts/build-wheel.bash [--out-dir DIRECTORY]

Build the desktop frontend, package it into ParaDev, create a reproducible
Python wheel, and verify that the wheel contains exactly the current GUI assets.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --out-dir)
            if [[ $# -lt 2 || "$2" == --* ]]; then
                echo "error: --out-dir requires a value" >&2
                exit 1
            fi
            if [[ "$2" == /* ]]; then
                OUT_DIR="$2"
            else
                OUT_DIR="${ROOT}/$2"
            fi
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "error: unknown argument: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if [[ -z "${SOURCE_DATE_EPOCH:-}" ]]; then
    SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
fi
if [[ ! "${SOURCE_DATE_EPOCH}" =~ ^[0-9]+$ ]]; then
    echo "error: SOURCE_DATE_EPOCH must be an integer Unix timestamp" >&2
    exit 1
fi
export SOURCE_DATE_EPOCH

npm --prefix apps/desktop run build

# setuptools may otherwise reuse build/lib and retain obsolete hashed assets.
BUILD_DIR="${ROOT}/build"
if [[ "${BUILD_DIR}" != "${ROOT}/build" ]]; then
    echo "error: refusing to clean unexpected build directory: ${BUILD_DIR}" >&2
    exit 1
fi
rm -rf -- "${BUILD_DIR}"

resolve_uv
TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/paradev-wheel.XXXXXX")"
trap 'rm -rf -- "${TEMP_DIR}"' EXIT
"${UV_BIN}" build --wheel --out-dir "${TEMP_DIR}"

WHEEL="$(find "${TEMP_DIR}" -maxdepth 1 -type f -name 'paradev-*.whl' -print -quit)"
if [[ -z "${WHEEL}" ]]; then
    echo "error: uv did not produce a ParaDev wheel" >&2
    exit 1
fi

run_python scripts/verify_wheel_inventory.py \
    --wheel "${WHEEL}" \
    --gui-root "${ROOT}/src/paradev/resources/gui" \
    --host-root "${ROOT}/apps/desktop/host" \
    --host-icon "${ROOT}/apps/desktop/host/icon.icns"

mkdir -p "${OUT_DIR}"
cp -- "${WHEEL}" "${OUT_DIR}/$(basename -- "${WHEEL}")"
echo "[build-wheel] wrote ${OUT_DIR}/$(basename -- "${WHEEL}")"
