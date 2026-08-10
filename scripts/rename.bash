#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"

OLD_PROJECT="ParaDev"
OLD_DIST="paradev"
OLD_IMPORT="paradev"
OLD_CLI="paradev"

PROJECT_NAME=""
DIST_NAME=""
IMPORT_NAME=""
CLI_NAME=""
YES=0

usage() {
    cat <<'EOF'
Usage: bash scripts/rename.bash --project-name NAME --dist-name NAME --import-name NAME --cli-name NAME [OPTIONS]

Rename this ParaDev template into a real project.

Options:
  --project-name NAME  Display name, e.g. "My Project".
  --dist-name NAME     Python distribution name, e.g. my-project.
  --import-name NAME   Python import package name, e.g. my_project.
  --cli-name NAME      Console command name, e.g. my-tool.
  --yes                Run without interactive confirmation.
  -h, --help           Show this help message.

Example:
  bash scripts/rename.bash --project-name "My Project" --dist-name my-project --import-name my_project --cli-name my-tool --yes
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-name)
            PROJECT_NAME="${2:-}"
            shift 2
            ;;
        --dist-name)
            DIST_NAME="${2:-}"
            shift 2
            ;;
        --import-name)
            IMPORT_NAME="${2:-}"
            shift 2
            ;;
        --cli-name)
            CLI_NAME="${2:-}"
            shift 2
            ;;
        --yes)
            YES=1
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

require_value() {
    local name="$1"
    local value="$2"
    if [[ -z "${value}" ]]; then
        echo "error: ${name} is required" >&2
        usage
        exit 1
    fi
}

require_value "--project-name" "${PROJECT_NAME}"
require_value "--dist-name" "${DIST_NAME}"
require_value "--import-name" "${IMPORT_NAME}"
require_value "--cli-name" "${CLI_NAME}"

if [[ ! "${DIST_NAME}" =~ ^[a-z0-9]([a-z0-9._-]*[a-z0-9])?$ ]]; then
    echo "error: --dist-name must be a valid lowercase Python distribution name" >&2
    exit 1
fi

if [[ ! "${IMPORT_NAME}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
    echo "error: --import-name must be a valid Python identifier" >&2
    exit 1
fi

if [[ ! "${CLI_NAME}" =~ ^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$ ]]; then
    echo "error: --cli-name must be a valid console command name" >&2
    exit 1
fi

if [[ "${YES}" -ne 1 ]]; then
    printf 'Rename ParaDev to %s (dist=%s, import=%s, cli=%s)? [y/N] ' "${PROJECT_NAME}" "${DIST_NAME}" "${IMPORT_NAME}" "${CLI_NAME}"
    read -r answer
    case "${answer}" in
        y|Y|yes|YES)
            ;;
        *)
            echo "rename cancelled"
            exit 1
            ;;
    esac
fi

if [[ "${IMPORT_NAME}" != "${OLD_IMPORT}" && -e "src/${IMPORT_NAME}" ]]; then
    echo "error: src/${IMPORT_NAME} already exists" >&2
    exit 1
fi

if [[ "${IMPORT_NAME}" != "${OLD_IMPORT}" && -d "src/${OLD_IMPORT}" ]]; then
    mv "src/${OLD_IMPORT}" "src/${IMPORT_NAME}"
fi

if [[ "${IMPORT_NAME}" != "${OLD_IMPORT}" && -d ".claude/skills/${OLD_IMPORT}" ]]; then
    if [[ -e ".claude/skills/${IMPORT_NAME}" ]]; then
        echo "error: .claude/skills/${IMPORT_NAME} already exists" >&2
        exit 1
    fi
    mv ".claude/skills/${OLD_IMPORT}" ".claude/skills/${IMPORT_NAME}"
fi

replace_text() {
    local old="$1"
    local new="$2"
    local file="$3"
    OLD_TEXT="${old}" NEW_TEXT="${new}" perl -0pi -e 's/\Q$ENV{OLD_TEXT}\E/$ENV{NEW_TEXT}/g' "${file}"
}

while IFS= read -r -d '' file; do
    case "${file}" in
        ./.git/*|./.venv/*|./dist/*|./build/*)
            continue
            ;;
    esac
    if grep -Iq . "${file}"; then
        replace_text "${OLD_PROJECT}" "${PROJECT_NAME}" "${file}"
        replace_text 'name = "paradev"' "name = \"${DIST_NAME}\"" "${file}"
        replace_text 'paradev = "paradev.cli:main"' "${CLI_NAME} = \"${IMPORT_NAME}.cli:main\"" "${file}"
        replace_text 'paradev-gui = "paradev.gui:main"' "${CLI_NAME}-gui = \"${IMPORT_NAME}.gui:main\"" "${file}"
        replace_text "${OLD_IMPORT}.version.__version__" "${IMPORT_NAME}.version.__version__" "${file}"
        replace_text "${OLD_IMPORT}.cli:main" "${IMPORT_NAME}.cli:main" "${file}"
        replace_text "${OLD_IMPORT}.gui:main" "${IMPORT_NAME}.gui:main" "${file}"
        replace_text "src/${OLD_IMPORT}" "src/${IMPORT_NAME}" "${file}"
        replace_text ".claude/skills/${OLD_IMPORT}" ".claude/skills/${IMPORT_NAME}" "${file}"
        replace_text "test_${OLD_IMPORT}_" "test_${IMPORT_NAME}_" "${file}"
        replace_text "uv run ${OLD_CLI}" "uv run ${CLI_NAME}" "${file}"
        replace_text "uv run ${OLD_CLI}-gui" "uv run ${CLI_NAME}-gui" "${file}"
        replace_text "bash scripts/${OLD_CLI}" "bash scripts/${CLI_NAME}" "${file}"
        replace_text "${OLD_DIST}" "${IMPORT_NAME}" "${file}"
    fi
done < <(find . -type f -print0)

while IFS= read -r -d '' path; do
    dir="$(dirname -- "${path}")"
    base="$(basename -- "${path}")"
    new_base="${base//${OLD_IMPORT}/${IMPORT_NAME}}"
    if [[ "${base}" != "${new_base}" ]]; then
        if [[ -e "${dir}/${new_base}" ]]; then
            echo "error: cannot rename ${path}; ${dir}/${new_base} already exists" >&2
            exit 1
        fi
        mv "${path}" "${dir}/${new_base}"
    fi
done < <(find . -depth -name "*${OLD_IMPORT}*" -not -path "./.git/*" -print0)

echo "[rename] renamed project to ${PROJECT_NAME} (dist=${DIST_NAME}, import=${IMPORT_NAME}, cli=${CLI_NAME})"
