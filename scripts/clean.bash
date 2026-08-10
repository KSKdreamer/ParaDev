#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"

FRESH_GIT=0
YES=0
COMMIT_MESSAGE="Initialize project"

usage() {
    cat <<'EOF'
Usage: bash scripts/clean.bash [OPTIONS]

Run normal cleanup, or explicitly collapse Git history to one master commit.

Options:
  --fresh-git             Destructively replace local Git history with one master commit.
  --yes                   Required with --fresh-git.
  --message MESSAGE       Commit message for --fresh-git.
  -h, --help              Show this help message.

Examples:
  bash scripts/clean.bash
  bash scripts/clean.bash --fresh-git --yes --message "Initial commit"
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fresh-git)
            FRESH_GIT=1
            shift
            ;;
        --yes)
            YES=1
            shift
            ;;
        --message)
            if [[ $# -lt 2 ]]; then
                echo "error: --message requires a value" >&2
                exit 1
            fi
            COMMIT_MESSAGE="$2"
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

bash scripts/cleanup.bash

if [[ "${FRESH_GIT}" -eq 0 ]]; then
    exit 0
fi

if [[ "${YES}" -ne 1 ]]; then
    echo "error: --fresh-git is destructive and requires --yes" >&2
    exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "error: --fresh-git requires a Git repository" >&2
    exit 1
fi

tmp_branch="fresh-git-$(date +%s)"
git checkout --orphan "${tmp_branch}"
git rm -rf --cached . >/dev/null 2>&1 || true
git add -A
git commit -m "${COMMIT_MESSAGE}"

while IFS= read -r branch; do
    if [[ "${branch}" != "${tmp_branch}" ]]; then
        git branch -D "${branch}" >/dev/null 2>&1 || true
    fi
done < <(git for-each-ref --format='%(refname:short)' refs/heads/)

git branch -M master
git reflog expire --expire=now --all
git gc --prune=now --aggressive
echo "[clean] fresh Git history created on master"
