"""Move generated project extension descriptors behind `.paradev/`."""

from __future__ import annotations

import argparse
from pathlib import Path

from heavenbase.utils import dumps_json

from paradev.build._extension_metadata import hide_project_extension_metadata


def main() -> int:
    """Run the hidden extension-descriptor migration."""

    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply the byte-preserving moves; the default is a dry plan.",
    )
    args = parser.parse_args()
    root = args.project_root.expanduser().resolve()
    moves = hide_project_extension_metadata(root, write=args.write)
    payload = {
        "schema": "paradev.project-extension-metadata-migration.v1",
        "status": "applied" if args.write else "planned",
        "count": len(moves),
        "moves": [move.to_view(root) for move in moves],
    }
    print(dumps_json(payload, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
