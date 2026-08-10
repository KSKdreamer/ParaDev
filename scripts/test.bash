#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"
source "${ROOT}/scripts/_env.bash"

PYTEST_ARGS=()
PARALLEL=0
SERIAL=0
MODE="fast"
EXPLICIT_PYTEST_ARGS=0
DEFAULT_SUITE=0

usage() {
    cat <<'EOF'
Usage: bash scripts/test.bash [OPTIONS] [PYTEST_ARGS...]

Run pytest through the repository environment.

Options:
  --parallel             Run with pytest-xdist using -n auto.
  --serial               Disable the default no-argument xdist run.
  --fast                 Run the standard fast suite, excluding slow tests. Default when no pytest args are provided.
  --full                 Run all tests, including slow migration/integration contracts.
  --slow                 Run only tests marked slow.
  --asyncio-mode MODE    Forward pytest asyncio mode, e.g. auto or strict.
  -h, --help             Show this help message.

Examples:
  rtk bash scripts/test.bash
  rtk bash scripts/test.bash --full
  rtk bash scripts/test.bash --slow --parallel
  rtk bash scripts/test.bash --parallel
  rtk bash scripts/test.bash --serial
  rtk bash scripts/test.bash tests/test_scripts.py -q
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --parallel)
            PARALLEL=1
            shift
            ;;
        --serial)
            SERIAL=1
            PARALLEL=0
            shift
            ;;
        --fast)
            MODE="fast"
            shift
            ;;
        --full)
            MODE="full"
            shift
            ;;
        --slow)
            MODE="slow"
            shift
            ;;
        --asyncio-mode)
            if [[ $# -lt 2 ]]; then
                echo "error: --asyncio-mode requires a value" >&2
                exit 1
            fi
            PYTEST_ARGS+=(-o "asyncio_mode=$2")
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            PYTEST_ARGS+=("$1")
            EXPLICIT_PYTEST_ARGS=1
            shift
            ;;
    esac
done

if [[ "${#PYTEST_ARGS[@]}" -eq 0 ]]; then
    if [[ ! -d tests ]] || ! find tests -type f -name 'test_*.py' -print -quit | grep -q .; then
        echo "[test] no tests found"
        exit 0
    fi
    PYTEST_ARGS=(tests -q)
    DEFAULT_SUITE=1
fi

case "${MODE}" in
    fast)
        if [[ "${EXPLICIT_PYTEST_ARGS}" -eq 0 ]]; then
            PYTEST_ARGS+=(-m "not slow")
        fi
        ;;
    full)
        PYTEST_ARGS=(--durations=25 -o "faulthandler_timeout=300" "${PYTEST_ARGS[@]}")
        ;;
    slow)
        PYTEST_ARGS+=(-m slow)
        ;;
    *)
        echo "error: unknown test mode: ${MODE}" >&2
        exit 1
        ;;
esac

if [[ "${DEFAULT_SUITE}" -eq 1 && "${SERIAL}" -eq 0 ]]; then
    PARALLEL=1
fi

if [[ "${PARALLEL}" -eq 1 ]]; then
    if [[ $(array_len PYTEST_ARGS) -gt 0 ]]; then
        PYTEST_ARGS=(-n auto --dist=loadgroup "${PYTEST_ARGS[@]}")
    else
        PYTEST_ARGS=(-n auto --dist=loadgroup)
    fi
fi

uv_run pytest "${PYTEST_ARGS[@]}"
