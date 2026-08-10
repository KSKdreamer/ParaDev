#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"
source "${ROOT}/scripts/_env.bash"

CHECK=0
SOURCE="README.en.md"
TRANSLATION="README.zh.md"
TARGETS=(README.md "src/paradev/resources/README.md")

usage() {
    cat <<'EOF'
Usage: bash scripts/sync-readme.bash [OPTIONS]

Copy README.en.md to README.md, src/paradev/resources/README.md, and optional extra targets.
README.en.md is the canonical README source. README.zh.md is its line-aligned translation.

Options:
  --check                  Verify targets match README.en.md without writing.
  --target PATH            Also sync/check README.en.md to PATH.
  --resource-target IMPORT Also sync/check src/IMPORT/resources/README.md.
  -h, --help               Show this help message.

Examples:
  rtk bash scripts/sync-readme.bash
  rtk bash scripts/sync-readme.bash --check --resource-target heavenbase
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)
            CHECK=1
            shift
            ;;
        --target)
            if [[ $# -lt 2 ]]; then
                echo "error: --target requires a value" >&2
                exit 1
            fi
            TARGETS+=("$2")
            shift 2
            ;;
        --resource-target)
            if [[ $# -lt 2 ]]; then
                echo "error: --resource-target requires a value" >&2
                exit 1
            fi
            TARGETS+=("src/$2/resources/README.md")
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

if [[ ! -f "${SOURCE}" ]]; then
    echo "error: ${SOURCE} not found" >&2
    exit 1
fi
if [[ ! -f "${TRANSLATION}" ]]; then
    echo "error: ${TRANSLATION} not found" >&2
    exit 1
fi

run_python - "${SOURCE}" "${TRANSLATION}" <<'PY'
from pathlib import Path
import re
import sys

source = Path(sys.argv[1])
translation = Path(sys.argv[2])
source_text = source.read_text(encoding="utf-8")
translation_text = translation.read_text(encoding="utf-8")
source_lines = source_text.splitlines()
translation_lines = translation_text.splitlines()
if len(source_lines) != len(translation_lines):
    print(
        f"error: {translation} has {len(translation_lines)} lines; "
        f"expected {len(source_lines)} to match {source}",
        file=sys.stderr,
    )
    sys.exit(1)

def heading_shape(lines):
    return [
        (index, len(line) - len(line.lstrip("#")))
        for index, line in enumerate(lines, start=1)
        if line.startswith("#")
    ]


if heading_shape(source_lines) != heading_shape(translation_lines):
    print(f"error: {translation} headings are not line-aligned with {source}", file=sys.stderr)
    sys.exit(1)

block_pattern = re.compile(r"```([^\n]*)\n(.*?)```", re.DOTALL)
source_blocks = block_pattern.findall(source_text)
translation_blocks = block_pattern.findall(translation_text)
if source_blocks != translation_blocks:
    print(f"error: {translation} code blocks differ from {source}", file=sys.stderr)
    sys.exit(1)

print(
    f"[readme] bilingual pair aligned "
    f"({len(source_lines)} lines, {len(source_blocks)} code block(s))"
)
PY

if [[ "${CHECK}" -eq 1 ]]; then
    run_python - "${SOURCE}" "${TARGETS[@]}" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
targets = [Path(item) for item in sys.argv[2:]]
source_bytes = source.read_bytes()
outdated = [str(target) for target in targets if not target.exists() or target.read_bytes() != source_bytes]
if outdated:
    for target in outdated:
        print(f"error: {target} is out of date; run rtk bash scripts/sync-readme.bash", file=sys.stderr)
    sys.exit(1)
PY
    echo "[readme] ${#TARGETS[@]} target(s) current"
    exit 0
fi

run_python - "${SOURCE}" "${TARGETS[@]}" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
targets = [Path(item) for item in sys.argv[2:]]
source_bytes = source.read_bytes()
for target in targets:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source_bytes)
PY
echo "[readme] copied ${SOURCE} to ${#TARGETS[@]} target(s)"
