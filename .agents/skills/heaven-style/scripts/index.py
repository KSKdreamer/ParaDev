#!/usr/bin/env python3
"""Regenerate references/index.yaml from skill metadata and bundled resources."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone

from heavenbase.utils import (
    dump_yaml,
    enum_files,
    exists_dir,
    exists_file,
    get_file_basename,
    get_file_dir,
    list_paths,
    load_txt,
    load_yaml,
    loads_yaml,
    pj,
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SKILL_ROOT = get_file_dir(get_file_dir(__file__, abs=True))
REFERENCES = pj(SKILL_ROOT, "references")
ASSETS = pj(SKILL_ROOT, "assets")
SCRIPTS = pj(SKILL_ROOT, "scripts")


def rel(path: str) -> str:
    """Return a stable skill-root-relative POSIX path."""
    root = SKILL_ROOT.replace("\\", "/").rstrip("/")
    value = pj(path, abs=True).replace("\\", "/")
    return value[len(root) + 1 :] if value.startswith(f"{root}/") else value


def parse_frontmatter(path: str) -> dict[str, object]:
    """Return YAML frontmatter for a reference file."""
    text = load_txt(path)
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {"path": rel(path), "parse_error": "missing frontmatter"}
    meta = loads_yaml(match.group(1)) or {}
    if not isinstance(meta, dict):
        return {"path": rel(path), "parse_error": "frontmatter not a mapping"}
    meta.setdefault("path", rel(path))
    return meta


def _rule_category(path: str) -> str | None:
    value = rel(path)
    if "/rules/code/" in f"/{value}":
        return "code-quality"
    if "/rules/project/" in f"/{value}":
        return "project"
    if value == "references/rules/overview.md":
        return "overview"
    return None


def collect_md(root: str) -> list[dict[str, object]]:
    """Collect reference markdown frontmatter recursively."""
    if not exists_dir(root):
        return []
    items: list[dict[str, object]] = []
    for path in enum_files(root, ext="md", abs=True):
        if get_file_basename(path).startswith("_"):
            continue
        entry = parse_frontmatter(path)
        entry["path"] = rel(path)
        if get_file_basename(root) == "rules" and "category" not in entry:
            category = _rule_category(path)
            if category:
                entry["category"] = category
        items.append(entry)
    return sorted(items, key=lambda item: (item.get("order", 9999), item.get("path", "")))


def _script_desc(path: str) -> str:
    text = load_txt(path)
    return text.split('"""', 2)[1].strip().split("\n")[0] if '"""' in text[:500] else ""


def collect_scripts() -> list[dict[str, str]]:
    """Collect script names and docstring summaries."""
    return [
        {"path": rel(path), "name": get_file_basename(path, ext=False), "description": _script_desc(path)}
        for path in sorted(enum_files(SCRIPTS, ext="py", abs=True))
        if not get_file_basename(path).startswith("_")
    ]


def collect_assets() -> list[dict[str, str]]:
    """Collect direct assets and reference clone metadata."""
    if not exists_dir(ASSETS):
        return []
    out: list[dict[str, str]] = []
    for path in list_paths(ASSETS, abs=True):
        if get_file_basename(path).startswith("."):
            continue
        entry = {"path": rel(path), "kind": "dir" if exists_dir(path) else "file"}
        head = pj(path, ".git", "HEAD")
        if exists_dir(path) and exists_file(head):
            entry["git_head"] = load_txt(head).strip()
        out.append(entry)
    return out


def skill_meta() -> dict[str, object]:
    """Return selected SKILL.md frontmatter fields."""
    meta = parse_frontmatter(pj(SKILL_ROOT, "SKILL.md"))
    out = {key: meta[key] for key in ["name", "description"] if key in meta}
    metadata = meta.get("metadata")
    version = metadata.get("version") if isinstance(metadata, dict) else meta.get("version")
    if version is not None:
        out["version"] = version
    return out


def build_index() -> dict[str, object]:
    """Build the full generated index."""
    meta = skill_meta()
    return {
        "skill": meta.get("name", "heaven-style"),
        "version": meta.get("version"),
        "description": meta.get("description"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": rel(__file__),
        "references": {
            "rules": collect_md(pj(REFERENCES, "rules")),
            "workflows": collect_md(pj(REFERENCES, "workflows")),
            "tasks": collect_md(pj(REFERENCES, "tasks")),
            "failures": collect_md(pj(REFERENCES, "failures")),
        },
        "scripts": collect_scripts(),
        "assets": collect_assets(),
    }


def comparable(index: dict[str, object]) -> dict[str, object]:
    """Return index with volatile fields normalized."""
    out = dict(index)
    out["generated_at"] = "<ignored>"
    return out


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit 1 if index.yaml would change")
    args = parser.parse_args()
    index_path = pj(REFERENCES, "index.yaml")
    new_index = build_index()
    if args.check:
        old_index = load_yaml(index_path) if exists_file(index_path) else {}
        if not isinstance(old_index, dict) or comparable(old_index) != comparable(new_index):
            print(f"index.yaml is stale; run: python {rel(__file__)}", file=sys.stderr)
            return 1
        print("index.yaml is up to date")
        return 0
    dump_yaml(new_index, index_path, sort_keys=False, allow_unicode=True)
    print(f"Wrote {rel(index_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
