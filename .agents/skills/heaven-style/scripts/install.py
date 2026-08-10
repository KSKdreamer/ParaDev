#!/usr/bin/env python3
"""Install heaven-style globally, mirror optional checkouts, and refresh assets."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
import re
import sys

from heavenbase.utils import (
    cmd,
    copy_dir,
    copy_file,
    copy_path,
    delete_path,
    exists_dir,
    exists_file,
    exists_path,
    get_file_basename,
    get_file_dir,
    load_json,
    list_paths,
    load_txt,
    dump_json,
    pj,
    touch_dir,
)

SKILL_ROOT = get_file_dir(get_file_dir(__file__, abs=True))
SKILL_NAME = "heaven-style"
CLAUDE_MARKETPLACE = "heaven-style-local"
VERSION_RE = re.compile(r"^metadata:\s*\n(?:[ \t].*\n)*?[ \t]+version:\s*(\S+)", re.M)
NAME_RE = re.compile(r"^name:\s*(\S+)", re.M)
DESCRIPTION_RE = re.compile(r"^description:\s*(.+)", re.M)
ASSET_FILES = ("REFERENCE.md", "default-glossary.md", ".gitignore")
SKIP_NAMES = {"__pycache__", "heavenbase-reference"}


def read_skill_version(skill_root: str) -> str:
    """Return metadata.version from SKILL.md."""
    text = load_txt(pj(skill_root, "SKILL.md"))
    match = VERSION_RE.search(text)
    if match:
        return match.group(1)
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("version:"):
            return stripped.split(":", 1)[1].strip()
    raise ValueError(f"missing metadata.version in {pj(skill_root, 'SKILL.md')}")


def read_skill_name(skill_root: str) -> str | None:
    """Return SKILL.md name when present."""
    skill_file = pj(skill_root, "SKILL.md")
    if not exists_file(skill_file):
        return None
    match = NAME_RE.search(load_txt(skill_file))
    return match.group(1).strip("'\"") if match else None


def read_skill_description(skill_root: str) -> str:
    """Return the SKILL.md description."""
    text = load_txt(pj(skill_root, "SKILL.md"))
    match = DESCRIPTION_RE.search(text)
    if match:
        return match.group(1).strip()
    return "Heaven-style code and architecture guide for Python-first repos in the HeavenBase lineage."


def is_heaven_style_skill(path: str) -> bool:
    """Return whether path is a verified heaven-style skill."""
    return exists_dir(path) and read_skill_name(path) == SKILL_NAME


def agents_root() -> str:
    """Return the user-level Agent Skills root."""
    override = os.environ.get("HEAVEN_STYLE_AGENTS_ROOT")
    if override:
        return pj(override, abs=True)
    return pj("~", ".agents", "skills", abs=True)


def agents_base() -> str:
    """Return the parent directory for user-level Agent Skills roots."""
    return get_file_dir(agents_root())


def global_agents_skill_dir(skill_root: str) -> str:
    """Return the standard user-level install path under ~/.agents/skills."""
    return pj(agents_root(), read_skill_name(skill_root) or SKILL_NAME, abs=True)


def claude_root(config_dir: str | None = None) -> str:
    """Return the Claude Code config root."""
    if config_dir:
        return pj(config_dir, abs=True)
    override = os.environ.get("HEAVEN_STYLE_CLAUDE_ROOT") or os.environ.get("CLAUDE_CONFIG_DIR")
    if override:
        return pj(override, abs=True)
    return pj("~", ".claude", abs=True)


def claude_plain_skill_dir(config_dir: str | None = None) -> str:
    """Return the duplicate-prone plain Claude skill path."""
    return pj(claude_root(config_dir), "skills", SKILL_NAME, abs=True)


def claude_marketplace_root(path: str | None = None) -> str:
    """Return the local Claude plugin marketplace root."""
    if path:
        return pj(path, abs=True)
    override = os.environ.get("HEAVEN_STYLE_CLAUDE_MARKETPLACE_ROOT")
    if override:
        return pj(override, abs=True)
    return pj(agents_base(), "heaven-style-claude-marketplace", abs=True)


def embedded_heavenbase_root(skill_root: str) -> str | None:
    """Return the HeavenBase repo root when this skill is checked in there."""
    current = pj(skill_root, abs=True)
    for _ in range(8):
        if exists_file(pj(current, "src", "heavenbase", "version.py")):
            return current
        parent = get_file_dir(current)
        if parent == current:
            break
        current = parent
    return None


def run(args: list[str], *, cwd: str | None = None) -> None:
    """Run a child command."""
    print("+", " ".join(args))
    cmd(args, check=True, cwd=cwd or SKILL_ROOT, encoding="utf-8", errors="replace")


def copy_skill_tree(source: str, target: str) -> None:
    """Copy skill files to target, excluding the reference clone."""
    touch_dir(target)
    for path in list_paths(source, abs=True):
        name = get_file_basename(path)
        if name in SKIP_NAMES or name.startswith("."):
            continue
        dest = pj(target, name, abs=True)
        if name == "assets" and exists_dir(path):
            touch_dir(dest)
            for asset in ASSET_FILES:
                asset_path = pj(path, asset)
                if exists_file(asset_path):
                    copy_file(asset_path, pj(dest, asset))
            continue
        if exists_dir(path):
            copy_dir(path, dest)
        else:
            copy_file(path, dest)


def require_replaceable_skill(path: str, label: str) -> None:
    """Fail unless an existing path is a verified heaven-style skill."""
    if not exists_path(path):
        return
    if not is_heaven_style_skill(path):
        raise RuntimeError(f"refusing to replace {label} at {path}; it is not a verified {SKILL_NAME} skill")
    delete_path(path)


def remove_legacy_global_installs() -> list[str]:
    """Remove verified legacy versioned heaven-style installs."""
    root = agents_root()
    if not exists_dir(root):
        return []

    removed: list[str] = []
    prefix = f"{SKILL_NAME}-"
    for path in list_paths(root, abs=True):
        name = get_file_basename(path)
        if not name.startswith(prefix):
            continue
        if is_heaven_style_skill(path):
            delete_path(path)
            removed.append(path)
        else:
            print(f"[heaven-style] skipped unverified legacy install {path}", file=sys.stderr)
    return removed


def sync_and_index(
    skill_root: str,
    *,
    skip_sync: bool,
    local: str | None,
) -> bool:
    """Refresh reference assets and index.yaml for a skill checkout."""
    embedded_root = embedded_heavenbase_root(skill_root)
    did_sync = not skip_sync
    if embedded_root is not None:
        if not skip_sync:
            print(
                f"Skipping reference sync for embedded HeavenBase skill ({embedded_root}); " f"use {global_agents_skill_dir(SKILL_ROOT)}",
                file=sys.stderr,
            )
        did_sync = False
    elif did_sync:
        sync = [sys.executable, pj(skill_root, "scripts", "sync.py")]
        if local is not None:
            sync.extend(["--local", local])
        run(sync, cwd=skill_root)

    run([sys.executable, pj(skill_root, "scripts", "index.py")], cwd=skill_root)
    return did_sync


def install_global(*, skip_sync: bool, local: str | None) -> str:
    """Install the standard global heaven-style checkout."""
    target = global_agents_skill_dir(SKILL_ROOT)
    require_replaceable_skill(target, "global skill install")
    removed = remove_legacy_global_installs()
    for path in removed:
        print(f"[heaven-style] removed stale install {path}")
    copy_skill_tree(SKILL_ROOT, target)
    sync_and_index(target, skip_sync=skip_sync, local=local)
    print(f"[heaven-style] installed global copy at {target}")
    return target


def backup_claude_plain_skill(config_dir: str | None) -> str | None:
    """Back up a verified plain Claude skill that would duplicate discovery."""
    path = claude_plain_skill_dir(config_dir)
    if not exists_path(path):
        return None
    if not is_heaven_style_skill(path):
        raise RuntimeError(f"refusing to move {path}; it is not a verified {SKILL_NAME} skill")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = pj(get_file_dir(path), f"{SKILL_NAME}.backup-{stamp}", abs=True)
    copy_path(path, backup)
    delete_path(path)
    return backup


def guard_claude_plain_skill(*, config_dir: str | None, backup: bool) -> None:
    """Prevent duplicate discovery through ~/.claude/skills."""
    path = claude_plain_skill_dir(config_dir)
    if not exists_path(path):
        return
    if backup:
        target = backup_claude_plain_skill(config_dir)
        print(f"[heaven-style] backed up duplicate-prone Claude skill to {target}")
        return
    raise RuntimeError(
        f"Plain Claude skill found at {path}. Cursor, OpenCode, and Kilo may also scan this location, "
        f"so installing the Claude plugin would duplicate {SKILL_NAME}. Remove it or rerun with --backup-claude-skill."
    )


def read_claude_plugin_name(plugin_root: str) -> str | None:
    """Return a Claude plugin name when present."""
    manifest = pj(plugin_root, ".claude-plugin", "plugin.json")
    if not exists_file(manifest):
        return None
    data = load_json(manifest)
    return data.get("name") if isinstance(data, dict) else None


def require_replaceable_claude_plugin(plugin_root: str) -> None:
    """Fail unless an existing Claude plugin path is managed by heaven-style."""
    if not exists_path(plugin_root):
        return
    if read_claude_plugin_name(plugin_root) != SKILL_NAME:
        raise RuntimeError(f"refusing to replace Claude plugin source at {plugin_root}; it is not {SKILL_NAME}")
    delete_path(plugin_root)


def write_claude_marketplace(market_root: str, plugin_root: str, version: str, description: str) -> None:
    """Write Claude plugin marketplace manifests."""
    author = {"name": "Magolor", "email": "magolorcz@gmail.com"}
    plugin = {
        "name": SKILL_NAME,
        "description": description,
        "version": version,
        "author": author,
        "homepage": "https://github.com/Magolor/Blueprint",
        "repository": "https://github.com/Magolor/Blueprint",
        "license": "MIT",
        "keywords": ["skills", "python", "heavenbase", "codex", "claude-code"],
    }
    marketplace_plugin = dict(plugin)
    marketplace_plugin["source"] = f"./{get_file_basename(plugin_root)}"
    touch_dir(pj(market_root, ".claude-plugin"))
    touch_dir(pj(plugin_root, ".claude-plugin"))
    dump_json(plugin, pj(plugin_root, ".claude-plugin", "plugin.json"), indent=2)
    dump_json(
        {
            "name": CLAUDE_MARKETPLACE,
            "metadata": {"description": "Local marketplace for the Heaven-style skill."},
            "owner": author,
            "plugins": [marketplace_plugin],
        },
        pj(market_root, ".claude-plugin", "marketplace.json"),
        indent=2,
    )


def run_with_claude_config(args: list[str], config_dir: str | None) -> None:
    """Run Claude with an optional isolated config dir."""
    if not config_dir:
        run(args)
        return
    old = os.environ.get("CLAUDE_CONFIG_DIR")
    os.environ["CLAUDE_CONFIG_DIR"] = pj(config_dir, abs=True)
    try:
        run(args)
    finally:
        if old is None:
            del os.environ["CLAUDE_CONFIG_DIR"]
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = old


def install_claude_plugin(
    *,
    skip_sync: bool,
    local: str | None,
    config_dir: str | None,
    marketplace_root: str | None,
    backup_plain_skill: bool,
    scope: str,
) -> str:
    """Install heaven-style as a Claude Code plugin without plain skill duplication."""
    guard_claude_plain_skill(config_dir=config_dir, backup=backup_plain_skill)
    market_root = claude_marketplace_root(marketplace_root)
    plugin_root = pj(market_root, SKILL_NAME, abs=True)
    plugin_skill_root = pj(plugin_root, "skills", SKILL_NAME, abs=True)
    require_replaceable_claude_plugin(plugin_root)
    copy_skill_tree(SKILL_ROOT, plugin_skill_root)
    sync_and_index(plugin_skill_root, skip_sync=skip_sync, local=local)
    write_claude_marketplace(market_root, plugin_root, read_skill_version(SKILL_ROOT), read_skill_description(SKILL_ROOT))
    run_with_claude_config(["claude", "plugin", "validate", market_root], config_dir)
    run_with_claude_config(["claude", "plugin", "marketplace", "add", market_root], config_dir)
    run_with_claude_config(["claude", "plugin", "install", "--scope", scope, f"{SKILL_NAME}@{CLAUDE_MARKETPLACE}"], config_dir)
    print(f"[heaven-style] installed Claude plugin from {market_root}")
    return market_root


def mirror_skill(target: str) -> None:
    """Mirror the skill tree to another checkout without touching global installs."""
    mirror_root = pj(target, abs=True)
    copy_skill_tree(SKILL_ROOT, mirror_root)
    run([sys.executable, pj(mirror_root, "scripts", "index.py")], cwd=mirror_root)
    print(f"[heaven-style] mirrored skill to {mirror_root}")


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-sync", action="store_true", help="Do not refresh the HeavenBase reference asset")
    parser.add_argument("--local", default=None, help="Refresh the reference asset from a local repo path")
    parser.add_argument(
        "--print-global-dir",
        action="store_true",
        help="Print the standard ~/.agents/skills install directory for this skill",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Sync and index only at the current skill root; do not install globally",
    )
    parser.add_argument(
        "--mirror",
        metavar="PATH",
        default=None,
        help="Mirror the skill tree to PATH (for example a HeavenBase in-repo copy)",
    )
    parser.add_argument(
        "--skip-global",
        action="store_true",
        help="Skip the standard ~/.agents/skills install",
    )
    parser.add_argument(
        "--all-harnesses",
        action="store_true",
        help="Install the common Agent Skill and the Claude Code plugin bridge",
    )
    parser.add_argument(
        "--claude-plugin",
        action="store_true",
        help="Install the Claude Code plugin bridge without writing ~/.claude/skills",
    )
    parser.add_argument(
        "--backup-claude-skill",
        action="store_true",
        help="Back up an existing verified ~/.claude/skills/heaven-style before installing the Claude plugin",
    )
    parser.add_argument(
        "--claude-config-dir",
        default=None,
        help="Use a Claude Code config directory for plugin commands (defaults to Claude's normal config)",
    )
    parser.add_argument(
        "--claude-marketplace-root",
        default=None,
        help="Write the local Claude plugin marketplace at PATH",
    )
    parser.add_argument(
        "--claude-scope",
        default="user",
        choices=("user", "project", "local"),
        help="Claude plugin install scope",
    )
    args = parser.parse_args()

    if args.print_global_dir:
        print(global_agents_skill_dir(SKILL_ROOT))
        return 0

    embedded_root = embedded_heavenbase_root(SKILL_ROOT)
    local = args.local
    if embedded_root is not None and local is not None and pj(local, abs=True) == embedded_root:
        print(
            f"Ignoring --local for embedded HeavenBase skill; use {global_agents_skill_dir(SKILL_ROOT)} " "for reference assets",
            file=sys.stderr,
        )
        local = None

    if args.mirror is not None:
        mirror_skill(args.mirror)

    if args.in_place:
        did_sync = sync_and_index(SKILL_ROOT, skip_sync=args.skip_sync, local=local)
        print("heaven-style is synced and indexed" if did_sync else "heaven-style index is current; sync skipped")
        return 0

    if not args.skip_global:
        install_global(skip_sync=args.skip_sync, local=local)
    if args.all_harnesses or args.claude_plugin:
        install_claude_plugin(
            skip_sync=args.skip_sync,
            local=local,
            config_dir=args.claude_config_dir,
            marketplace_root=args.claude_marketplace_root,
            backup_plain_skill=args.backup_claude_skill,
            scope=args.claude_scope,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
