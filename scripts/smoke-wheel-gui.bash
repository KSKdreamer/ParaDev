#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"
source "${ROOT}/scripts/_env.bash"

resolve_uv
run_python "${ROOT}/scripts/wheel_smoke.py" --uv "${UV_BIN}" "$@"
