"""HOI4 keyword dataset helpers for editor services."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from heavenbase.utils import load_txt

from paradev.config import CM_PARADEV
from paradev.pdx import PDXBlock, PDXParseError

HOI4_KEYWORD_DATASET_SCHEMA = "paradev.hoi4.keyword-dataset.v1"
HOI4_DEFAULT_GAME_ROOT = Path.home() / "Library/Application Support/Steam/steamapps/common/Hearts of Iron IV"
HOI4_KEYWORD_KINDS = ("modifier", "effect", "trigger")

_COMPLETION_KIND_FUNCTION = 3
_COMPLETION_KIND_PROPERTY = 10
_DOC_SOURCES = {
    "modifier": "modifiers_documentation.md",
    "effect": "effects_documentation.md",
    "trigger": "triggers_documentation.md",
}
_SCRIPTED_SOURCES = {
    "effect": ("common/scripted_effects", "scripted_effect"),
    "trigger": ("common/scripted_triggers", "scripted_trigger"),
}
_SCOPE_HEADING_RE = re.compile(r"^##\s+(Modifiers|Effects|Triggers)\s+for scope\s+(.+?)\s*$", re.IGNORECASE)
_MARKDOWN_LINK_RE = re.compile(r"^\*\s+\[([A-Za-z_][A-Za-z0-9_.:@-]*)\]\(#[^)]+\)")
_KEYWORD_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:@-]*$")
_SEED_KEYWORDS = (
    ("modifier", "stability_factor", "country"),
    ("modifier", "war_support_factor", "country"),
    ("modifier", "political_power_factor", "country"),
    ("modifier", "consumer_goods_factor", "country"),
    ("modifier", "production_speed_buildings_factor", "country"),
    ("modifier", "army_attack_factor", "army"),
    ("modifier", "army_defence_factor", "army"),
    ("modifier", "research_speed_factor", "country"),
    ("effect", "add_political_power", "country"),
    ("effect", "add_stability", "country"),
    ("effect", "add_war_support", "country"),
    ("effect", "add_ideas", "country"),
    ("effect", "country_event", "country"),
    ("trigger", "always", "any"),
    ("trigger", "has_idea", "country"),
    ("trigger", "has_country_flag", "country"),
    ("trigger", "has_completed_focus", "country"),
    ("trigger", "is_ai", "country"),
)


def hoi4_keyword_dataset(game_root: str | Path | None = None) -> dict[str, object]:
    """Return the cached HOI4 keyword dataset used by editor completion.

    Args:
        game_root: Optional Hearts of Iron IV install path. When omitted,
            `paradev.hoi4.game_root` is used before the default macOS Steam
            install location.

    Returns:
        JSON-safe dataset with modifier, effect, and trigger keyword rows.
    """

    root_text = _normalized_game_root(game_root)
    root = Path(root_text).expanduser() if root_text is not None else None
    rows = _keyword_rows(root_text)
    return {
        "schema": HOI4_KEYWORD_DATASET_SCHEMA,
        "game": "hoi4",
        "game_root": str(root) if root is not None else None,
        "game_root_exists": bool(root and root.exists()),
        "metadata": _game_metadata(root),
        "kinds": list(HOI4_KEYWORD_KINDS),
        "count": len(rows),
        "counts": {kind: sum(1 for row in rows if row["kind"] == kind) for kind in HOI4_KEYWORD_KINDS},
        "rows": [dict(row) for row in rows],
    }


def hoi4_keyword_completion_items(
    *,
    kind: str,
    prefix: str = "",
    game_root: str | Path | None = None,
    limit: int | None = None,
) -> list[dict[str, object]]:
    """Return LSP completion items for one HOI4 keyword kind.

    Args:
        kind: Keyword kind: `modifier`, `effect`, or `trigger`.
        prefix: Optional case-insensitive label prefix filter.
        game_root: Optional Hearts of Iron IV install path.
        limit: Optional maximum number of completion rows.

    Returns:
        JSON-safe LSP `CompletionItem` rows.

    Raises:
        ValueError: If `kind` or `limit` is unsupported.
    """

    if kind not in HOI4_KEYWORD_KINDS:
        raise ValueError(f"Unsupported HOI4 keyword kind: {kind}")
    if limit is not None and limit < 1:
        raise ValueError("HOI4 keyword completion limit must be a positive integer.")

    normalized_prefix = prefix.lower()
    items: list[dict[str, object]] = []
    for row in _keyword_rows(_normalized_game_root(game_root)):
        if row["kind"] != kind:
            continue
        label = str(row["name"])
        if normalized_prefix and not label.lower().startswith(normalized_prefix):
            continue
        items.append(_completion_item(row))
        if limit is not None and len(items) >= limit:
            break
    return items


def _completion_item(row: dict[str, object]) -> dict[str, object]:
    name = str(row["name"])
    kind = str(row["kind"])
    scopes = list(row["scopes"]) if isinstance(row.get("scopes"), list) else []
    scope_text = ", ".join(str(scope) for scope in scopes[:4])
    detail = f"HOI4 {kind}" + (f" ({scope_text})" if scope_text else "")
    completion_kind = _COMPLETION_KIND_PROPERTY if kind == "modifier" else _COMPLETION_KIND_FUNCTION
    return {
        "label": name,
        "kind": completion_kind,
        "detail": detail,
        "insertText": name,
        "sortText": f"0_{kind}_{name}",
        "documentation": {"kind": "markdown", "value": detail},
        "data": {
            "source": "hoi4-keyword",
            "kind": kind,
            "scopes": scopes,
            "source_kinds": list(row["source_kinds"]) if isinstance(row.get("source_kinds"), list) else [],
        },
    }


def resolve_hoi4_game_root(game_root: str | Path | None = None) -> Path | None:
    """Resolve the shared HOI4 install root used by local ParaDev surfaces.

    An explicit nonblank value wins over ``paradev.hoi4.game_root``. The
    platform default is used only when it exists.

    Args:
        game_root: Optional explicit Hearts of Iron IV install path.

    Returns:
        Expanded configured/default path, or ``None`` when no root is
        available.
    """

    if game_root is not None:
        explicit_root = str(game_root).strip()
        return Path(explicit_root).expanduser() if explicit_root else None
    configured_root = str(CM_PARADEV.get("paradev.hoi4.game_root", default="") or "").strip()
    if configured_root:
        return Path(configured_root).expanduser()
    return HOI4_DEFAULT_GAME_ROOT if HOI4_DEFAULT_GAME_ROOT.exists() else None


def _normalized_game_root(game_root: str | Path | None) -> str | None:
    root = resolve_hoi4_game_root(game_root)
    return str(root) if root is not None else None


@lru_cache(maxsize=8)
def _keyword_rows(game_root_text: str | None) -> tuple[dict[str, object], ...]:
    root = Path(game_root_text).expanduser() if game_root_text is not None else None
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for kind, name, scope in _SEED_KEYWORDS:
        _add_keyword(rows, kind=kind, name=name, scope=scope, source_kind="seed", source_path=None)
    if root is not None and root.exists():
        for kind, filename in _DOC_SOURCES.items():
            _add_documentation_keywords(rows, root=root, kind=kind, path=root / "documentation" / filename)
        for kind, (folder, source_kind) in _SCRIPTED_SOURCES.items():
            _add_scripted_keywords(rows, root=root, kind=kind, folder=root / folder, source_kind=source_kind)
    return tuple(_finalize_row(row) for row in sorted(rows.values(), key=lambda row: (row["kind"], row["name"])))


def _add_documentation_keywords(rows: dict[tuple[str, str], dict[str, Any]], *, root: Path, kind: str, path: Path) -> None:
    if not path.exists():
        return
    try:
        text = load_txt(str(path), encoding="utf-8")
    except OSError:
        return

    scope: str | None = None
    for line in text.splitlines():
        heading_match = _SCOPE_HEADING_RE.match(line.strip())
        if heading_match:
            scope = heading_match.group(2).strip().lower()
            continue
        if line.startswith("## "):
            scope = None
            continue
        if scope is None:
            continue
        link_match = _MARKDOWN_LINK_RE.match(line.strip())
        if link_match:
            _add_keyword(rows, kind=kind, name=link_match.group(1), scope=scope, source_kind="game_documentation", source_path=_relative_path(root, path))


def _add_scripted_keywords(rows: dict[tuple[str, str], dict[str, Any]], *, root: Path, kind: str, folder: Path, source_kind: str) -> None:
    if not folder.exists():
        return
    for path in sorted(folder.glob("*.txt")):
        try:
            block = PDXBlock.from_str(load_txt(str(path), encoding="utf-8"))
        except (OSError, PDXParseError, ValueError):
            continue
        for entry in block.entries:
            if entry.key is None:
                continue
            name = str(entry.key.val)
            if _KEYWORD_RE.match(name):
                _add_keyword(rows, kind=kind, name=name, scope="scripted", source_kind=source_kind, source_path=_relative_path(root, path))


def _add_keyword(
    rows: dict[tuple[str, str], dict[str, Any]],
    *,
    kind: str,
    name: str,
    scope: str | None,
    source_kind: str,
    source_path: str | None,
) -> None:
    if kind not in HOI4_KEYWORD_KINDS or not _KEYWORD_RE.match(name):
        return
    row = rows.setdefault(
        (kind, name),
        {
            "name": name,
            "kind": kind,
            "scopes": set(),
            "source_kinds": set(),
            "source_paths": set(),
        },
    )
    if scope:
        row["scopes"].add(scope)
    row["source_kinds"].add(source_kind)
    if source_path:
        row["source_paths"].add(source_path)


def _finalize_row(row: dict[str, Any]) -> dict[str, object]:
    return {
        "name": str(row["name"]),
        "kind": str(row["kind"]),
        "scopes": sorted(str(scope) for scope in row["scopes"]),
        "source_kinds": sorted(str(source_kind) for source_kind in row["source_kinds"]),
        "source_paths": sorted(str(source_path) for source_path in row["source_paths"]),
    }


def _game_metadata(root: Path | None) -> dict[str, object]:
    if root is None or not root.exists():
        return {"source": "seed"}
    return {
        "source": "local-game-files",
        "hoi4_branch": _optional_text(root / "hoi4_branch.txt"),
        "hoi4_rev": _optional_text(root / "hoi4_rev.txt"),
        "documentation": {kind: str(root / "documentation" / filename) for kind, filename in _DOC_SOURCES.items()},
    }


def _optional_text(path: Path) -> str | None:
    try:
        value = load_txt(str(path), encoding="utf-8").strip()
    except OSError:
        return None
    return value or None


def _relative_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
