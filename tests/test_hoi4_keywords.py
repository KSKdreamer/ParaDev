from __future__ import annotations

import json
from pathlib import Path

from paradev.config import CM_PARADEV
from paradev.games.hoi4.keywords import (
    hoi4_keyword_completion_items,
    hoi4_keyword_dataset,
    resolve_hoi4_game_root,
)


def _write_keyword_documentation(game_root: Path, *, kind: str, keyword: str, scope: str = "country") -> None:
    documentation = game_root / "documentation"
    documentation.mkdir(parents=True, exist_ok=True)
    filenames = {
        "modifier": "modifiers_documentation.md",
        "effect": "effects_documentation.md",
        "trigger": "triggers_documentation.md",
    }
    headings = {
        "modifier": "Modifiers",
        "effect": "Effects",
        "trigger": "Triggers",
    }
    (documentation / filenames[kind]).write_text(
        f"# {headings[kind]}\n\n" f"## {headings[kind]} for scope {scope}\n\n" f"* [{keyword}](#{keyword})\n",
        encoding="utf-8",
    )


def test_hoi4_keyword_dataset_reads_game_documentation_and_scripted_helpers(tmp_path: Path) -> None:
    documentation = tmp_path / "documentation"
    documentation.mkdir()
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [stability_factor](#stability_factor)\n" "* [war_support_factor](#war_support_factor)\n",
        encoding="utf-8",
    )
    (documentation / "effects_documentation.md").write_text(
        "# Effects\n\n" "## Effects for scope COUNTRY\n\n" "* [add_stability](#add_stability)\n",
        encoding="utf-8",
    )
    (documentation / "triggers_documentation.md").write_text(
        "# Triggers\n\n" "## Triggers for scope COUNTRY\n\n" "* [has_stability](#has_stability)\n",
        encoding="utf-8",
    )
    scripted_effects = tmp_path / "common/scripted_effects"
    scripted_triggers = tmp_path / "common/scripted_triggers"
    scripted_effects.mkdir(parents=True)
    scripted_triggers.mkdir(parents=True)
    (scripted_effects / "sample.txt").write_text("PARADEV_effect = { add_stability = 0.1 }\n", encoding="utf-8")
    (scripted_triggers / "sample.txt").write_text("PARADEV_trigger = { always = yes }\n", encoding="utf-8")

    payload = hoi4_keyword_dataset(tmp_path)

    assert payload["schema"] == "paradev.hoi4.keyword-dataset.v1"
    rows = {(row["kind"], row["name"]): row for row in payload["rows"]}
    assert rows[("modifier", "stability_factor")]["scopes"] == ["country"]
    assert rows[("effect", "PARADEV_effect")]["source_kinds"] == ["scripted_effect"]
    assert rows[("trigger", "PARADEV_trigger")]["source_kinds"] == ["scripted_trigger"]
    json.dumps(payload)


def test_hoi4_keyword_completion_items_filter_prefix_and_shape_lsp_rows(tmp_path: Path) -> None:
    documentation = tmp_path / "documentation"
    documentation.mkdir()
    (documentation / "modifiers_documentation.md").write_text(
        "# Modifiers\n\n" "## Modifiers for scope country\n\n" "* [stability_factor](#stability_factor)\n" "* [war_support_factor](#war_support_factor)\n",
        encoding="utf-8",
    )

    items = hoi4_keyword_completion_items(kind="modifier", prefix="sta", game_root=tmp_path)

    assert [item["label"] for item in items] == ["stability_factor"]
    assert items[0]["kind"] == 10
    assert items[0]["data"]["source"] == "hoi4-keyword"


def test_hoi4_keyword_dataset_uses_configured_game_root_when_omitted(tmp_path: Path, cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "configured-game"
    _write_keyword_documentation(game_root, kind="modifier", keyword="cfg_modifier_factor")

    try:
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")

        payload = hoi4_keyword_dataset()

        modifier_names = [row["name"] for row in payload["rows"] if row["kind"] == "modifier"]
        assert payload["game_root"] == str(game_root)
        assert payload["game_root_exists"] is True
        assert "cfg_modifier_factor" in modifier_names
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_hoi4_keyword_completion_items_use_configured_game_root_when_omitted(tmp_path: Path, cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "configured-game"
    _write_keyword_documentation(game_root, kind="modifier", keyword="cfg_completion_factor")

    try:
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")

        items = hoi4_keyword_completion_items(kind="modifier", prefix="cfg")

        assert [item["label"] for item in items] == ["cfg_completion_factor"]
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_resolve_hoi4_game_root_prefers_explicit_path_over_shared_config(
    tmp_path: Path,
    cm_paradev_lock,
) -> None:
    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    configured_root = tmp_path / "configured-game"
    explicit_root = tmp_path / "explicit-game"
    try:
        CM_PARADEV.set("paradev.hoi4.game_root", str(configured_root))

        assert resolve_hoi4_game_root() == configured_root
        assert resolve_hoi4_game_root(explicit_root) == explicit_root
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)
