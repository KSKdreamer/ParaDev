#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"

WHEEL=""
EVIDENCE=""
PYTHON_BIN="${PARADEV_SMOKE_PYTHON:-python3}"
KEEP=0
BUNDLE_ID="top.ahvn.paradev"
FOREIGN_PORT=4817

usage() {
    cat <<'EOF'
Usage: bash scripts/smoke-macos-installed-app.bash --wheel PATH [OPTIONS]

Install a wheel into an isolated runtime and exercise its Finder-launchable
macOS ParaDev.app, loopback health endpoint, packaged frontend, and shutdown.

Options:
  --wheel PATH      ParaDev wheel to install. Required.
  --python PATH     Python 3.10+ used to create the isolated runtime.
  --evidence PATH   Optional JSON evidence output outside the temporary home.
  --keep            Keep the isolated runtime and home for debugging.
  -h, --help        Show this help message.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --wheel)
            WHEEL="${2:-}"
            shift 2
            ;;
        --evidence)
            EVIDENCE="${2:-}"
            shift 2
            ;;
        --python)
            PYTHON_BIN="${2:-}"
            shift 2
            ;;
        --keep)
            KEEP=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "error: unsupported option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "error: the installed macOS app smoke requires macOS" >&2
    exit 1
fi
if [[ -z "${WHEEL}" || ! -f "${WHEEL}" ]]; then
    echo "error: --wheel must name an existing ParaDev wheel" >&2
    exit 2
fi
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "error: --python must name an available Python 3.10+ executable" >&2
    exit 2
fi
if ! "${PYTHON_BIN}" -c 'import sys; raise SystemExit(0 if (3, 10) <= sys.version_info < (3, 14) else 1)'; then
    echo "error: --python must use a ParaDev-supported Python version (3.10 through 3.13)" >&2
    exit 2
fi
WHEEL="$(cd -- "$(dirname -- "${WHEEL}")" && pwd -P)/$(basename -- "${WHEEL}")"
if [[ -n "${EVIDENCE}" ]]; then
    EVIDENCE="$(cd -- "$(dirname -- "${EVIDENCE}")" && pwd -P)/$(basename -- "${EVIDENCE}")"
fi

WORK="$(mktemp -d "${TMPDIR:-/tmp}/paradev-macos-app-smoke.XXXXXX")"
WORK="$(cd -- "${WORK}" && pwd -P)"
SMOKE_HOME="${WORK}/home"
RUNTIME="${WORK}/runtime"
APP="${SMOKE_HOME}/Applications/ParaDev.app"
APP_PID=""
SERVER_PID=""
SERVER_PORT=""
FOREIGN_PID=""

cleanup() {
    /usr/bin/osascript -e "tell application id \"${BUNDLE_ID}\" to quit" >/dev/null 2>&1 || true
    if [[ -n "${APP_PID}" ]] && kill -0 "${APP_PID}" >/dev/null 2>&1; then
        kill "${APP_PID}" >/dev/null 2>&1 || true
    fi
    if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
        kill "${SERVER_PID}" >/dev/null 2>&1 || true
    fi
    if [[ -n "${FOREIGN_PID}" ]] && kill -0 "${FOREIGN_PID}" >/dev/null 2>&1; then
        kill "${FOREIGN_PID}" >/dev/null 2>&1 || true
    fi
    if [[ "${KEEP}" -eq 1 ]]; then
        echo "[macos-app-smoke] kept ${WORK}"
    else
        rm -rf -- "${WORK}"
    fi
}
trap cleanup EXIT

mkdir -p "${SMOKE_HOME}"
"${PYTHON_BIN}" -m venv "${RUNTIME}"
"${RUNTIME}/bin/python" -m pip install --quiet --upgrade pip
"${RUNTIME}/bin/python" -m pip install --quiet "${WHEEL}"

HOME="${SMOKE_HOME}" "${RUNTIME}/bin/paradev" dashboard --install-app --yes
test -x "${APP}/Contents/MacOS/applet"
test -f "${APP}/Contents/Resources/Scripts/main.scpt"
test -f "${APP}/Contents/Resources/ParaDev.icns"
/usr/bin/codesign --verify --deep --strict "${APP}"

"${RUNTIME}/bin/python" - "${APP}/Contents/Info.plist" "${RUNTIME}/bin/python" <<'PY'
from pathlib import Path
import plistlib
import sys

with Path(sys.argv[1]).open("rb") as stream:
    info = plistlib.load(stream)
assert info["CFBundleIdentifier"] == "top.ahvn.paradev"
assert Path(info["ParaDevPythonExecutable"]).samefile(Path(sys.argv[2]))
assert info["ParaDevPythonModule"] == "paradev.gui_macos"
assert info["OSAAppletStayOpen"] is True
PY

"${RUNTIME}/bin/python" -m http.server "${FOREIGN_PORT}" --bind 127.0.0.1 >"${WORK}/foreign-server.log" 2>&1 &
FOREIGN_PID=$!
FOREIGN_READY=0
for _attempt in $(seq 1 50); do
    if /usr/bin/curl --silent --fail --max-time 1 "http://127.0.0.1:${FOREIGN_PORT}/" >/dev/null; then
        FOREIGN_READY=1
        break
    fi
    sleep 0.1
done
if [[ "${FOREIGN_READY}" -ne 1 ]]; then
    echo "error: could not establish the foreign loopback listener on ${FOREIGN_PORT}" >&2
    exit 1
fi

HOME="${SMOKE_HOME}" /usr/bin/open -n "${APP}"
READY=0
for _attempt in $(seq 1 450); do
    APP_PID="$(/usr/bin/pgrep -f "${APP}/Contents/MacOS/applet" | head -n 1 || true)"
    SERVER_PID="$(/usr/bin/pgrep -f "paradev.gui_macos --serve --host 127.0.0.1 --port 0 --ready-json" | head -n 1 || true)"
    if [[ -n "${SERVER_PID}" ]]; then
        SERVER_PORT="$(/usr/sbin/lsof -nP -a -p "${SERVER_PID}" -iTCP -sTCP:LISTEN -Fn 2>/dev/null | sed -n 's/^n127\.0\.0\.1:\([0-9][0-9]*\)$/\1/p' | head -n 1 || true)"
    fi
    if [[ -n "${SERVER_PORT}" ]] && /usr/bin/curl --silent --fail --max-time 1 "http://127.0.0.1:${SERVER_PORT}/health" >"${WORK}/health.json"; then
        READY=1
        break
    fi
    sleep 0.1
done
if [[ "${READY}" -ne 1 ]]; then
    echo "error: installed ParaDev.app did not expose /health" >&2
    exit 1
fi
if [[ -z "${APP_PID}" ]]; then
    echo "error: installed ParaDev.app exited before its server became ready" >&2
    exit 1
fi
if [[ "${SERVER_PORT}" == "${FOREIGN_PORT}" ]]; then
    echo "error: installed ParaDev.app attached to the foreign listener on ${FOREIGN_PORT}" >&2
    exit 1
fi

/usr/bin/curl --silent --fail --max-time 3 "http://127.0.0.1:${SERVER_PORT}/" >"${WORK}/index.html"
/usr/bin/curl --silent --fail --max-time 3 \
    "http://127.0.0.1:${SERVER_PORT}/paradev-runtime-config.js" >"${WORK}/paradev-runtime-config.js"
ASSET_PATH="$("${RUNTIME}/bin/python" - "${WORK}/index.html" <<'PY'
from pathlib import Path
import re
import sys

html = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(r'(?:src|href)="(/assets/[^"]+\.(?:js|css))"', html)
if match is None:
    raise SystemExit("packaged index does not reference a JavaScript or CSS asset")
print(match.group(1))
PY
)"
/usr/bin/curl --silent --fail --max-time 3 "http://127.0.0.1:${SERVER_PORT}${ASSET_PATH}" >"${WORK}/asset"

/usr/bin/osascript -e "tell application id \"${BUNDLE_ID}\" to quit" >"${WORK}/quit.log" 2>&1 || true
STOPPED=0
for _attempt in $(seq 1 100); do
    if ! kill -0 "${APP_PID}" >/dev/null 2>&1 && ! kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
        STOPPED=1
        break
    fi
    sleep 0.1
done
if [[ "${STOPPED}" -ne 1 ]]; then
    echo "error: installed ParaDev.app or its child server remained running after quit" >&2
    exit 1
fi
if /usr/bin/curl --silent --fail --max-time 1 "http://127.0.0.1:${SERVER_PORT}/health" >/dev/null 2>&1; then
    echo "error: installed ParaDev.app still serves /health after quit" >&2
    exit 1
fi
if ! kill -0 "${FOREIGN_PID}" >/dev/null 2>&1 || ! /usr/bin/curl --silent --fail --max-time 1 "http://127.0.0.1:${FOREIGN_PORT}/" >/dev/null; then
    echo "error: installed ParaDev.app disturbed the foreign loopback listener" >&2
    exit 1
fi

RESULT="$("${RUNTIME}/bin/python" - "${WHEEL}" "${ASSET_PATH}" "${SERVER_PID}" "${SERVER_PORT}" <<'PY'
from hashlib import sha256
from pathlib import Path
import json
import sys

wheel = Path(sys.argv[1])
print(json.dumps({
    "schema": "paradev.macos-installed-app-smoke.v1",
    "ok": True,
    "wheel": {
        "name": wheel.name,
        "bytes": wheel.stat().st_size,
        "sha256": sha256(wheel.read_bytes()).hexdigest(),
    },
    "app": {
        "bundle_id": "top.ahvn.paradev",
        "code_signature": "valid-adhoc",
        "installer_command": "paradev dashboard --install-app --yes",
        "runtime_binding": "isolated-venv",
        "app_exited_after_quit": True,
    },
    "runtime": {
        "isolated_home": True,
        "health": True,
        "same_origin_bootstrap": True,
        "probed_asset": sys.argv[2],
        "server_pid": int(sys.argv[3]),
        "dynamic_server_port": int(sys.argv[4]),
        "server_exited_after_quit": True,
        "foreign_listener_survived": True,
    },
}, indent=2, sort_keys=True))
PY
)"
printf '%s\n' "${RESULT}"
if [[ -n "${EVIDENCE}" ]]; then
    printf '%s\n' "${RESULT}" >"${EVIDENCE}"
    echo "[macos-app-smoke] wrote ${EVIDENCE}"
fi
