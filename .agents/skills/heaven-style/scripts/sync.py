#!/usr/bin/env python3
"""Clone or refresh the HeavenBase reference tree under assets/."""

from __future__ import annotations

import argparse
import sys

from heavenbase.utils import cmd, exists_dir, get_file_dir, pj, touch_dir

SKILL_ROOT = get_file_dir(get_file_dir(__file__, abs=True))
DEFAULT_TARGET = pj(SKILL_ROOT, "assets", "heavenbase-reference")
DEFAULT_URL = "https://github.com/Magolor/HeavenBase.git"


def run(args: list[str], cwd: str | None = None) -> None:
    """Run a command through HeavenBase command utilities."""
    print("+", " ".join(args))
    cmd(args, check=True, cwd=cwd)


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--local", default=None, help="Local repo path; cloned directly when set")
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--depth", type=int, default=1)
    args = parser.parse_args()
    target = pj(args.target, abs=True)
    url = args.url
    if args.local is not None:
        local = pj(args.local, abs=True)
        if not exists_dir(pj(local, ".git")):
            print(f"Not a git repo: {local}", file=sys.stderr)
            return 1
        url = local
    if exists_dir(pj(target, ".git")):
        run(["git", "fetch", "--depth", str(args.depth), url], cwd=target)
        # Force: the reference clone is disposable and autocrlf noise must not block refresh.
        run(["git", "checkout", "--force", "--detach", "FETCH_HEAD"], cwd=target)
    else:
        touch_dir(get_file_dir(target))
        run(["git", "clone", "--depth", str(args.depth), url, target])
    print(f"Reference repo ready at {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
