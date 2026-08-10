#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "${ROOT}"
source "${ROOT}/scripts/_env.bash"

REMOTE="origin"
MASTER_BRANCH="master"
RELEASE_BRANCH="release"
MESSAGE=""

usage() {
    cat <<'EOF'
Usage: bash scripts/release.bash [OPTIONS]

Create or reuse a [release] commit on master, fast-forward the release branch,
and push release to trigger the PyPI trusted-publishing workflow.

Options:
  --remote NAME       Git remote to push. Default: origin.
  --master BRANCH     Source branch. Default: master.
  --release BRANCH    Release branch. Default: release.
  --message TEXT      Release commit message. Default uses the package version.
  -h, --help          Show this help message.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --remote)
            if [[ $# -lt 2 || "$2" == --* ]]; then
                echo "error: --remote requires a value" >&2
                exit 1
            fi
            REMOTE="$2"
            shift 2
            ;;
        --master)
            if [[ $# -lt 2 || "$2" == --* ]]; then
                echo "error: --master requires a value" >&2
                exit 1
            fi
            MASTER_BRANCH="$2"
            shift 2
            ;;
        --release)
            if [[ $# -lt 2 || "$2" == --* ]]; then
                echo "error: --release requires a value" >&2
                exit 1
            fi
            RELEASE_BRANCH="$2"
            shift 2
            ;;
        --message)
            if [[ $# -lt 2 || "$2" == --* ]]; then
                echo "error: --message requires a value" >&2
                exit 1
            fi
            MESSAGE="$2"
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

git_output() {
    git "$@" | tr -d '\r'
}

ref_exists() {
    git rev-parse --verify --quiet "$1" >/dev/null
}

is_ancestor() {
    git merge-base --is-ancestor "$1" "$2" >/dev/null 2>&1
}

version="$(run_python - <<'PY'
from pathlib import Path

namespace = {}
exec(Path("src/paradev/version.py").read_text(encoding="utf-8"), namespace)
print(namespace["__version__"])
PY
)"

current_branch="$(git_output branch --show-current)"
if [[ "${current_branch}" != "${MASTER_BRANCH}" ]]; then
    echo "error: release must be run from ${MASTER_BRANCH}; current branch is ${current_branch}" >&2
    exit 1
fi

dirty="$(git_output status --porcelain)"
if [[ -n "${dirty}" ]]; then
    echo "error: release requires a clean worktree:" >&2
    printf '%s\n' "${dirty}" >&2
    exit 1
fi

git fetch "${REMOTE}" "${MASTER_BRANCH}:refs/remotes/${REMOTE}/${MASTER_BRANCH}"
git fetch "${REMOTE}" "${RELEASE_BRANCH}:refs/remotes/${REMOTE}/${RELEASE_BRANCH}" || true

remote_master="${REMOTE}/${MASTER_BRANCH}"
remote_release="${REMOTE}/${RELEASE_BRANCH}"

if ref_exists "${remote_master}" && ! is_ancestor "${remote_master}" "${MASTER_BRANCH}"; then
    echo "error: ${MASTER_BRANCH} is behind or diverged from ${remote_master}; pull or rebase before release" >&2
    exit 1
fi

if ! ref_exists "${RELEASE_BRANCH}" && ref_exists "${remote_release}"; then
    git branch "${RELEASE_BRANCH}" "${remote_release}"
fi

if ref_exists "${RELEASE_BRANCH}" && ref_exists "${remote_release}" && [[ "$(git_output rev-parse "${RELEASE_BRANCH}")" != "$(git_output rev-parse "${remote_release}")" ]]; then
    echo "error: local ${RELEASE_BRANCH} differs from ${remote_release}; update it before release" >&2
    exit 1
fi

head_message="$(git_output log -1 --pretty=%B "${MASTER_BRANCH}")"
if [[ "${head_message}" == *"[release]"* ]]; then
    echo "Reusing existing [release] head commit on ${MASTER_BRANCH}"
else
    if [[ -z "${MESSAGE}" ]]; then
        MESSAGE="[release] Publish ParaDev ${version}"
    fi
    echo "Creating release commit on ${MASTER_BRANCH}: ${MESSAGE}"
    git commit --allow-empty -m "${MESSAGE}"
fi

echo "Pushing ${MASTER_BRANCH} to ${REMOTE}"
git push "${REMOTE}" "${MASTER_BRANCH}"

echo "Fast-forwarding ${RELEASE_BRANCH} from ${MASTER_BRANCH}"
if ref_exists "${RELEASE_BRANCH}"; then
    git switch "${RELEASE_BRANCH}"
else
    git switch -c "${RELEASE_BRANCH}" "${MASTER_BRANCH}"
fi

trap 'git switch "${MASTER_BRANCH}" >/dev/null 2>&1 || true' EXIT
git merge --ff-only "${MASTER_BRANCH}"

echo "Pushing ${RELEASE_BRANCH} to ${REMOTE}; this triggers the PyPI release workflow"
git push "${REMOTE}" "${RELEASE_BRANCH}"
