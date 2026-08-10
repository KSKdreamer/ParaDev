#!/usr/bin/env python3
"""Scan Python files for stdlib imports banned by heaven-style util rule."""

from __future__ import annotations

import argparse
import ast
import sys

from heavenbase.utils import enum_files, exists_dir, exists_file, get_file_ext, load_txt, pj

BANNED = {
    "json": "heavenbase.utils serialization helpers",
    "yaml": "heavenbase.utils serialization helpers",
    "pickle": "heavenbase.utils serialization helpers",
    "pathlib": "heavenbase.utils pj / CM_HVNB.pj",
    "subprocess": "heavenbase.utils cmd",
    "shutil": "heavenbase.utils file helpers",
    "hashlib": "heavenbase.utils hash helpers",
}


def _parts(path: str) -> set[str]:
    """Return lowercase normalized path parts."""
    return {part.lower() for part in pj(path, abs=True).replace("\\", "/").split("/")}


def _skip_file(path: str) -> bool:
    """Return whether a path is outside scanner scope."""
    parts = _parts(path)
    return bool(parts & {".venv", "__pycache__"}) or "heavenbase-reference" in parts


def _tree_imports(tree: ast.AST) -> list[tuple[int, str, str]]:
    """Return absolute imports from a parsed module."""
    out: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend((node.lineno, alias.name.split(".")[0], alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.append((node.lineno, node.module.split(".")[0], node.module))
    return out


def _os_attr_chain(node: ast.Attribute) -> str | None:
    """Return an os.* attribute chain when node roots at the os module."""
    parts: list[str] = []
    cur: ast.AST = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name) and cur.id == "os":
        return ".".join(reversed(parts))
    return None


def _os_import_ok(tree: ast.AST) -> bool:
    """Return whether os is used only for environment variable reads."""
    attrs = {chain for node in ast.walk(tree) if isinstance(node, ast.Attribute) and (chain := _os_attr_chain(node))}
    if not attrs:
        return True
    return all(attr == "environ" or attr.startswith("environ.") for attr in attrs)


def scan_file(path: str, *, allow_utils: bool) -> list[str]:
    """Return banned import issues for one Python file."""
    if "utils" in _parts(path) and allow_utils:
        return []
    issues: list[str] = []
    try:
        tree = ast.parse(load_txt(path), filename=path)
        imports = _tree_imports(tree)
        os_lines = [lineno for lineno, top, _full in imports if top == "os"]
        for lineno, top, full in imports:
            if top in BANNED:
                issues.append(f"{path}:{lineno}: import {full} -> use {BANNED[top]}")
        if os_lines and "utils" not in _parts(path) and not _os_import_ok(tree):
            issues.append(f"{path}:{os_lines[0]}: import os -> prefer heavenbase.utils / CM_HVNB.pj")
    except SyntaxError as error:
        issues.append(f"{path}: syntax error: {error}")
    return issues


def _scan_targets(paths: list[str]) -> list[str]:
    """Expand input files and directories into Python files."""
    files: list[str] = []
    for raw in paths:
        path = pj(raw, abs=True)
        if exists_file(path) and get_file_ext(path) == "py":
            files.append(path)
        elif exists_dir(path):
            files.extend(enum_files(path, ext="py", abs=True))
    return sorted(files, key=str.lower)


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Files or directories to scan")
    parser.add_argument("--no-utils-skip", action="store_true", help="Also scan heavenbase/utils")
    args = parser.parse_args()
    allow_utils = not args.no_utils_skip
    issues: list[str] = []
    scanned = 0
    for file in _scan_targets(args.paths):
        if _skip_file(file):
            continue
        scanned += 1
        issues.extend(scan_file(file, allow_utils=allow_utils))
    if issues:
        print("\n".join(issues))
        return 1
    print(f"OK: {scanned} file(s) - no banned imports")
    return 0


if __name__ == "__main__":
    sys.exit(main())
