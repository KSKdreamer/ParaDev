#!/usr/bin/env python3
"""Verify that a ParaDev wheel contains the canonical GUI and host assets."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile


def verify_wheel_inventory(
    wheel: Path,
    gui_root: Path,
    host_root: Path,
    host_icon: Path,
) -> tuple[int, int]:
    """Verify exact wheel GUI and host inventories against repository assets.

    Args:
        wheel: Wheel archive to inspect.
        gui_root: Canonical packaged frontend directory.
        host_root: Directory containing the system-WebView host scripts.
        host_icon: Canonical installed-application icon.

    Returns:
        Frontend and host file counts.

    Raises:
        ValueError: If an input is missing or the wheel inventory differs.
        OSError: If an input cannot be read.
    """

    if not wheel.is_file() or wheel.is_symlink():
        raise ValueError(f"wheel must be a regular file: {wheel}")
    if not gui_root.is_dir() or gui_root.is_symlink():
        raise ValueError(f"GUI root must be a real directory: {gui_root}")
    if not host_root.is_dir() or host_root.is_symlink():
        raise ValueError(f"host root must be a real directory: {host_root}")
    if not host_icon.is_file() or host_icon.is_symlink():
        raise ValueError(f"host icon must be a regular file: {host_icon}")

    prefix = "paradev/resources/gui/"
    expected = {prefix + path.relative_to(gui_root).as_posix() for path in gui_root.rglob("*") if path.is_file()}
    host_expected = {path.name: path.read_bytes() for path in sorted(host_root.glob("*.js"))}
    host_expected[host_icon.name] = host_icon.read_bytes()
    package_root = gui_root.parents[1]
    owned_sources = (
        package_root / "__main__.py",
        package_root / "resources" / "release" / "project-packages.json",
        *sorted((package_root / "api").glob("*.pyi")),
    )
    owned_expected = {"paradev/" + path.relative_to(package_root).as_posix(): path.read_bytes() for path in owned_sources if path.is_file()}

    with ZipFile(wheel) as archive:
        names = set(archive.namelist())
        actual = {name for name in names if name.startswith(prefix) and not name.endswith("/")}
        missing = sorted(expected - actual)
        stale = sorted(actual - expected)
        if missing or stale:
            details = []
            if missing:
                details.append("missing: " + ", ".join(missing))
            if stale:
                details.append("stale: " + ", ".join(stale))
            raise ValueError("wheel GUI inventory mismatch; " + "; ".join(details))

        host_entries = {Path(name).name: name for name in names if ".data/data/share/paradev/gui/host/" in name and not name.endswith("/")}
        if set(host_entries) != set(host_expected):
            raise ValueError(f"wheel GUI host inventory mismatch; expected {sorted(host_expected)!r}, found {sorted(host_entries)!r}")
        changed = [name for name, content in host_expected.items() if archive.read(host_entries[name]) != content]
        if changed:
            raise ValueError(f"wheel GUI host bytes differ from source: {changed!r}")
        missing_owned = sorted(set(owned_expected) - names)
        if missing_owned:
            raise ValueError(f"wheel is missing owned package resources: {missing_owned!r}")
        changed_owned = [name for name, content in owned_expected.items() if archive.read(name) != content]
        if changed_owned:
            raise ValueError(f"wheel owned package resources differ from source: {changed_owned!r}")
    return len(actual), len(host_entries)


def main() -> int:
    """Run the wheel inventory verifier from the command line.

    Returns:
        Process-style exit code.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument("--gui-root", required=True, type=Path)
    parser.add_argument("--host-root", required=True, type=Path)
    parser.add_argument("--host-icon", required=True, type=Path)
    args = parser.parse_args()
    try:
        gui_count, host_count = verify_wheel_inventory(args.wheel, args.gui_root, args.host_root, args.host_icon)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"[wheel-inventory] verified {gui_count} packaged GUI files and {host_count} host files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
