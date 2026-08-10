#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
APP_DIR="${ROOT}/apps/desktop"
source "${ROOT}/scripts/_env.bash"

MODE="--native-web"
HOST="${PARADEV_HOST:-127.0.0.1}"
REQUESTED_PORT="${PARADEV_PORT:-5173}"
BRIDGE_HOST="${PARADEV_NATIVE_BRIDGE_HOST:-127.0.0.1}"
REQUESTED_BRIDGE_PORT="${PARADEV_NATIVE_BRIDGE_PORT:-8765}"
EXTRA_ARGS=()
BRIDGE_PID=""

usage() {
    cat <<'EOF'
Usage: bash scripts/run.bash [--native-web|--web] [OPTIONS] [-- MODE_ARGS...]

Run the ParaDev desktop prototype.

Modes:
  --native-web  Run Vite with a loopback native REST bridge for local files,
                builds, open-path actions, and game launch actions. This is the default.
  --web         Run only the Vite web preview for browser-only frontend checks.

Options:
  --host HOST         Development host. Defaults to 127.0.0.1.
  --port PORT         Preferred ParaDev development port. Defaults to 5173.
  --bridge-port PORT  Preferred native bridge port. Defaults to 8765.
  -h, --help          Show this help message.

The script uses the preferred port when possible. If it is busy, it tries to stop
local listeners on that port first, then falls back to the next available port and
wires Vite to the selected local origin.
The native bridge is always loopback-bound unless PARADEV_NATIVE_BRIDGE_HOST is
set explicitly.
Packaged builds do not use this dev server; they load the bundled frontend.

Examples:
  bash scripts/run.bash
  bash scripts/run.bash --web
  bash scripts/run.bash --native-web
  bash scripts/run.bash --web --port 5180
EOF
}

cleanup() {
    if [[ -n "${BRIDGE_PID}" ]]; then
        kill "${BRIDGE_PID}" 2>/dev/null || true
        wait "${BRIDGE_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

require_command() {
    local name="$1"
    if ! command -v "${name}" >/dev/null 2>&1; then
        echo "error: ${name} is required" >&2
        exit 1
    fi
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --web|--native-web)
                MODE="$1"
                shift
                ;;
            --host)
                if [[ $# -lt 2 ]]; then
                    echo "error: --host requires a value" >&2
                    exit 1
                fi
                HOST="$2"
                shift 2
                ;;
            --port)
                if [[ $# -lt 2 ]]; then
                    echo "error: --port requires a value" >&2
                    exit 1
                fi
                REQUESTED_PORT="$2"
                shift 2
                ;;
            --bridge-port)
                if [[ $# -lt 2 ]]; then
                    echo "error: --bridge-port requires a value" >&2
                    exit 1
                fi
                REQUESTED_BRIDGE_PORT="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            --)
                shift
                EXTRA_ARGS+=("$@")
                break
                ;;
            *)
                EXTRA_ARGS+=("$1")
                shift
                ;;
        esac
    done
}

validate_port() {
    local port="$1"
    if [[ ! "${port}" =~ ^[0-9]+$ || "${port}" -lt 1 || "${port}" -gt 65535 ]]; then
        echo "error: invalid port: ${port}" >&2
        exit 1
    fi
}

port_available() {
    local host="$1"
    local port="$2"
    PARADEV_CHECK_HOST="${host}" PARADEV_CHECK_PORT="${port}" node <<'NODE'
const net = require("node:net");
const host = process.env.PARADEV_CHECK_HOST;
const port = Number(process.env.PARADEV_CHECK_PORT);
const server = net.createServer();

server.once("error", () => process.exit(1));
server.once("listening", () => server.close(() => process.exit(0)));
server.listen(port, host);
NODE
}

port_listener_pids() {
    local port="$1"

    if command -v lsof >/dev/null 2>&1; then
        lsof -nP -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null || true
        return 0
    fi

    if command -v fuser >/dev/null 2>&1; then
        fuser -n tcp "${port}" 2>/dev/null | tr -s ' ' '\n' | grep -E '^[0-9]+$' || true
        return 0
    fi

    echo "error: cannot inspect port ${port}; install lsof or fuser" >&2
    return 1
}

free_port() {
    local port="$1"
    local pids pid attempt

    pids="$(port_listener_pids "${port}")"
    if [[ -z "${pids}" ]]; then
        return 0
    fi

    echo "[paradev] port ${port} is busy; stopping listener pids: $(tr '\n' ' ' <<<"${pids}")" >&2
    while IFS= read -r pid; do
        [[ -n "${pid}" ]] || continue
        kill "${pid}" 2>/dev/null || true
    done <<<"${pids}"

    for attempt in 1 2 3 4 5; do
        if port_available "${HOST}" "${port}"; then
            return 0
        fi

        pids="$(port_listener_pids "${port}")"
        if [[ -z "${pids}" ]]; then
            continue
        fi

        while IFS= read -r pid; do
            [[ -n "${pid}" ]] || continue
            kill -9 "${pid}" 2>/dev/null || true
        done <<<"${pids}"
        sleep 0.2
    done

    port_available "${HOST}" "${port}"
}

find_available_port() {
    local host="$1"
    local port="$2"
    local limit=$((port + 100))

    while [[ "${port}" -lt "${limit}" && "${port}" -le 65535 ]]; do
        if port_available "${host}" "${port}"; then
            echo "${port}"
            return 0
        fi
        port=$((port + 1))
    done

    echo "error: no available port found from ${REQUESTED_PORT} to $((limit - 1))" >&2
    exit 1
}

ensure_dev_port() {
    local host="$1"
    local port="$2"

    if port_available "${host}" "${port}"; then
        echo "${port}"
        return 0
    fi

    if free_port "${port}"; then
        echo "${port}"
        return 0
    fi

    echo "[paradev] could not free port ${port}; searching for the next available port" >&2
    find_available_port "${host}" "${port}"
}

ensure_node_modules() {
    if [[ -d node_modules ]]; then
        return
    fi

    if [[ -f package-lock.json ]]; then
        npm ci
    else
        npm install
    fi
}

start_native_bridge() {
    local port="$1"
    local url="http://${BRIDGE_HOST}:${port}"

    echo "[paradev] native web bridge: ${url}"
    (
        cd "${ROOT}"
        uv_run python -m uvicorn paradev.api:build_app --factory --host "${BRIDGE_HOST}" --port "${port}"
    ) &
    BRIDGE_PID="$!"
}

parse_args "$@"
validate_port "${REQUESTED_PORT}"
validate_port "${REQUESTED_BRIDGE_PORT}"
enable_heavenbase_override

require_command node
require_command npm

cd "${APP_DIR}"
ensure_node_modules

PORT="$(ensure_dev_port "${HOST}" "${REQUESTED_PORT}")"
DEV_URL="http://${HOST}:${PORT}"
BRIDGE_PORT=""
BRIDGE_URL=""

if [[ "${PORT}" != "${REQUESTED_PORT}" ]]; then
    echo "[paradev] using alternate port ${PORT} instead of ${REQUESTED_PORT}"
fi

case "${MODE}" in
    --web)
        echo "[paradev] web dev server: ${DEV_URL}"
        PARADEV_HOST="${HOST}" PARADEV_PORT="${PORT}" npm run dev -- --host "${HOST}" --port "${PORT}" --strictPort ${EXTRA_ARGS+"${EXTRA_ARGS[@]}"}
        ;;
    --native-web)
        resolve_uv
        BRIDGE_PORT="$(find_available_port "${BRIDGE_HOST}" "${REQUESTED_BRIDGE_PORT}")"
        BRIDGE_URL="http://${BRIDGE_HOST}:${BRIDGE_PORT}"
        if [[ "${BRIDGE_PORT}" != "${REQUESTED_BRIDGE_PORT}" ]]; then
            echo "[paradev] using alternate native bridge port ${BRIDGE_PORT} instead of ${REQUESTED_BRIDGE_PORT}"
        fi
        start_native_bridge "${BRIDGE_PORT}"
        echo "[paradev] web dev server: ${DEV_URL}"
        PARADEV_HOST="${HOST}" PARADEV_PORT="${PORT}" VITE_PARADEV_NATIVE_BRIDGE_URL="${BRIDGE_URL}" npm run dev -- --host "${HOST}" --port "${PORT}" --strictPort ${EXTRA_ARGS+"${EXTRA_ARGS[@]}"}
        ;;
    *)
        echo "error: unknown mode: ${MODE}" >&2
        usage
        exit 1
        ;;
esac
