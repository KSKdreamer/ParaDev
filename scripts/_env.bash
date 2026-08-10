#!/usr/bin/env bash

# macOS /bin/bash 3.2 + set -u treats "${name[@]}" on a zero-length array as unbound.
array_len() {
    eval "printf '%s' \"\${#$1[@]}\""
}

array_copy() {
    local _dst="$1" _src="$2"
    if [[ $(array_len "${_src}") -gt 0 ]]; then
        eval "${_dst}=(\"\${${_src}[@]}\")"
    else
        eval "${_dst}=()"
    fi
}

run_with_array() {
    local array_name="$1"
    shift
    if [[ $(array_len "${array_name}") -gt 0 ]]; then
        eval "\"\$@\" \"\${${array_name}[@]}\""
    else
        "$@"
    fi
}

resolve_uv_optional() {
    if [[ -n "${UV_BIN:-}" ]]; then
        return 0
    fi
    if command -v uv >/dev/null 2>&1; then
        UV_BIN="uv"
        return 0
    fi
    if command -v uv.exe >/dev/null 2>&1; then
        UV_BIN="uv.exe"
        return 0
    fi
    return 1
}

resolve_uv() {
    if resolve_uv_optional; then
        return 0
    fi
    echo "error: uv or uv.exe is required but was not found on PATH" >&2
    exit 1
}

venv_python() {
    local venv="$1"
    local candidate
    for candidate in "${venv}/bin/python" "${venv}/Scripts/python.exe" "${venv}/Scripts/python"; do
        if [[ -x "${candidate}" || -f "${candidate}" ]]; then
            printf '%s\n' "${candidate}"
            return 0
        fi
    done
    return 1
}

resolve_python_preference() {
    if [[ -n "${REPO_PYTHON_PREFERENCE:-}" ]]; then
        printf '%s\n' "${REPO_PYTHON_PREFERENCE}"
        return 0
    fi
    if [[ -n "${HEAVENBASE_PYTHON_PREFERENCE:-}" ]]; then
        printf '%s\n' "${HEAVENBASE_PYTHON_PREFERENCE}"
        return 0
    fi
    if [[ -n "${BLUEPRINT_PYTHON_PREFERENCE:-}" ]]; then
        printf '%s\n' "${BLUEPRINT_PYTHON_PREFERENCE}"
        return 0
    fi
    printf '%s\n' "venv-first"
}

resolve_python() {
    if declare -p PYTHON_CMD >/dev/null 2>&1; then
        return 0
    fi

    local preference
    preference="$(resolve_python_preference)"
    local root="${ROOT:-$(pwd -P)}"
    local candidate

    if heavenbase_override_active && candidate="$(venv_python "${root}/.venv")"; then
        PYTHON_CMD=("${candidate}")
        return 0
    fi

    if [[ "${preference}" == "uv-first" ]] && resolve_uv_optional; then
        PYTHON_CMD=("${UV_BIN}" run python)
        return 0
    fi

    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        if candidate="$(venv_python "${VIRTUAL_ENV}")"; then
            PYTHON_CMD=("${candidate}")
            return 0
        fi
    fi

    if candidate="$(venv_python "${root}/.venv")"; then
        PYTHON_CMD=("${candidate}")
        return 0
    fi

    if resolve_uv_optional; then
        PYTHON_CMD=("${UV_BIN}" run python)
        return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD=("python3")
        return 0
    fi

    if command -v python >/dev/null 2>&1; then
        PYTHON_CMD=("python")
        return 0
    fi

    echo "error: Python was not found via active venv, .venv, uv/uv.exe, or system PATH" >&2
    exit 1
}

run_python() {
    resolve_python
    "${PYTHON_CMD[@]}" "$@"
}

heavenbase_override_marker() {
    local root="${ROOT:-$(pwd -P)}"
    printf '%s\n' "${root}/.venv/.paradev-heavenbase-source"
}

heavenbase_override_active() {
    local marker source python
    marker="$(heavenbase_override_marker)"
    [[ -f "${marker}" ]] || return 1
    IFS= read -r source <"${marker}" || return 1
    [[ -n "${source}" && -f "${source}/pyproject.toml" && -d "${source}/src/heavenbase" ]] || return 1
    python="$(venv_python "${ROOT:-$(pwd -P)}/.venv")" || return 1
    "${python}" -c \
        'from pathlib import Path; import heavenbase, sys; package = Path(heavenbase.__file__).resolve(); source = Path(sys.argv[1]).resolve() / "src" / "heavenbase"; raise SystemExit(0 if package == source or source in package.parents else 1)' \
        "${source}" >/dev/null 2>&1
}

enable_heavenbase_override() {
    if heavenbase_override_active; then
        export UV_NO_SYNC=1
    fi
}

uv_run() {
    resolve_uv
    if heavenbase_override_active; then
        UV_NO_SYNC=1 "${UV_BIN}" run "$@"
        return
    fi
    "${UV_BIN}" run "$@"
}

run_uv_python() {
    uv_run python "$@"
}

_discover_heavenbase_beside_ancestor() {
    local search_root="$1"
    local candidate parent
    while :; do
        parent="$(dirname -- "${search_root}")"
        candidate="${parent}/HeavenBase/HeavenBase"
        if [[ -f "${candidate}/pyproject.toml" && -d "${candidate}/src/heavenbase" ]]; then
            printf '%s\n' "${candidate}"
            return 0
        fi
        [[ "${parent}" == "${search_root}" ]] && return 1
        search_root="${parent}"
    done
}

discover_local_heavenbase_source() {
    local root="${1:-${ROOT:-$(pwd -P)}}"
    local common_dir checkout_root source
    if source="$(_discover_heavenbase_beside_ancestor "${root}")"; then
        printf '%s\n' "${source}"
        return 0
    fi
    if common_dir="$(git -C "${root}" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"; then
        checkout_root="$(dirname -- "${common_dir}")"
        if source="$(_discover_heavenbase_beside_ancestor "${checkout_root}")"; then
            printf '%s\n' "${source}"
            return 0
        fi
    fi
    return 1
}
