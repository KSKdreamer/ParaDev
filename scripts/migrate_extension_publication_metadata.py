"""Move extension publication migration state into hidden Registry metadata."""

from __future__ import annotations

import argparse
from pathlib import Path

from heavenbase.utils import dumps_json

from paradev.build._extension_metadata import (
    migrate_extension_publication_metadata,
)


def main() -> int:
    """Run the extension publication-metadata migration."""

    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply exact descriptor rewrites; the default is a dry plan.",
    )
    args = parser.parse_args()
    root = args.project_root.expanduser().resolve()
    drafts = migrate_extension_publication_metadata(
        root,
        write=args.write,
    )
    payload = {
        "schema": "paradev.extension-publication-metadata-migration.v1",
        "status": "applied" if args.write else "planned",
        "count": len(drafts),
        "drafts": [draft.to_view(root) for draft in drafts],
    }
    print(dumps_json(payload, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
