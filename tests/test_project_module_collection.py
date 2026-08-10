from __future__ import annotations

from pathlib import Path

import pytest

from paradev.sdk import Project


def _write_project(root: Path, *, duplicate_root: bool = False) -> Project:
    source_roots = "[src, extra]" if duplicate_root else "[src]"
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: module_collection",
                "title: Module Collection",
                "game: hoi4",
                f"source_roots: {source_roots}",
                "output_root: output",
                "build_root: build",
                "families:",
                "  bulletin:",
                "    kind: collection_source",
                "    source_slots:",
                "      - name: body",
                "        match: body.txt",
                "        kind: pdx",
                "    collection_source_slots:",
                "      - name: category",
                "        match: category.txt",
                "        kind: pdx",
                "    templates:",
                "      pdx: events/{collection_id}.txt",
                "",
            )
        ),
        encoding="utf-8",
    )
    module_root = root / "src/modules/bulletin/NEWS"
    module_root.mkdir(parents=True)
    (module_root / "body.txt").write_text("news = {}\n", encoding="utf-8")
    for source_root, collection_id in (("src", "alpha"), ("src", "beta")):
        collection_root = root / source_root / "collections/bulletin" / collection_id
        collection_root.mkdir(parents=True)
        (collection_root / "category.txt").write_text(
            f"add_namespace = {collection_id}\n",
            encoding="utf-8",
        )
    if duplicate_root:
        collection_root = root / "extra/collections/bulletin/remote"
        collection_root.mkdir(parents=True)
        (collection_root / "category.txt").write_text(
            "add_namespace = remote\n",
            encoding="utf-8",
        )
    return Project.load(root)


def test_module_collection_update_plans_and_applies_hidden_membership(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    hidden_path = tmp_path / "src/modules/bulletin/NEWS/.paradev/meta.yaml"

    plan = project.set_module_collection("bulletin/NEWS", "alpha")
    repeated = project.set_module_collection("bulletin/NEWS", "alpha")

    assert plan["schema"] == "paradev.sdk.module_collection_update.v1"
    assert plan["previous_collection_id"] is None
    assert plan["collection_id"] == "alpha"
    assert plan["changed"] is True
    assert plan["blocked"] is False
    assert plan["files"] == [
        {
            "path": str(hidden_path),
            "relative_path": "src/modules/bulletin/NEWS/.paradev/meta.yaml",
            "layer": "hidden",
            "action": "create",
            "before_sha256": None,
            "after_sha256": plan["files"][0]["after_sha256"],
        }
    ]
    assert plan["plan_hash"] == repeated["plan_hash"]
    assert not hidden_path.exists()

    result = project.set_module_collection(
        "bulletin/NEWS",
        "alpha",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "updated"
    assert result["written"] is True
    assert hidden_path.read_text(encoding="utf-8") == "collection: alpha\n"
    module = Project.load(tmp_path).discover_modules(module_id="bulletin/NEWS").modules[0]
    assert module.collection_id == "alpha"


def test_module_collection_update_preserves_hidden_settings_and_clears_file(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    hidden_path = tmp_path / "src/modules/bulletin/NEWS/.paradev/meta.yaml"
    hidden_path.parent.mkdir()
    hidden_path.write_text(
        "collection: alpha\nsettings:\n  display: compact\n",
        encoding="utf-8",
    )
    project = Project.load(tmp_path)

    move = project.set_module_collection("bulletin/NEWS", "beta")
    project.set_module_collection(
        "bulletin/NEWS",
        "beta",
        write=True,
        plan_hash=str(move["plan_hash"]),
    )
    assert hidden_path.read_text(encoding="utf-8") == ("collection: beta\nsettings:\n  display: compact\n")

    clear = Project.load(tmp_path).set_module_collection("bulletin/NEWS", None)
    result = Project.load(tmp_path).set_module_collection(
        "bulletin/NEWS",
        None,
        write=True,
        plan_hash=str(clear["plan_hash"]),
    )

    assert result["module"].get("collection_id") is None
    assert hidden_path.read_text(encoding="utf-8") == ("settings:\n  display: compact\n")


def test_module_collection_update_removes_empty_hidden_metadata_directory(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    hidden_path = tmp_path / "src/modules/bulletin/NEWS/.paradev/meta.yaml"
    hidden_path.parent.mkdir()
    hidden_path.write_text("collection: alpha\n", encoding="utf-8")
    project = Project.load(tmp_path)

    plan = project.set_module_collection("bulletin/NEWS", None)
    result = project.set_module_collection(
        "bulletin/NEWS",
        None,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "updated"
    assert not hidden_path.exists()
    assert not hidden_path.parent.exists()


def test_module_collection_update_migrates_visible_membership_atomically(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    module_root = tmp_path / "src/modules/bulletin/NEWS"
    visible_path = module_root / "meta.yaml"
    hidden_path = module_root / ".paradev/meta.yaml"
    visible_path.write_text(
        "title: Daily News\ncollection: alpha\n",
        encoding="utf-8",
    )
    project = Project.load(tmp_path)

    plan = project.set_module_collection("bulletin/NEWS", "beta")
    assert [(row["layer"], row["action"]) for row in plan["files"]] == [
        ("visible", "update"),
        ("hidden", "create"),
    ]
    result = project.set_module_collection(
        "bulletin/NEWS",
        "beta",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["module"]["collection_id"] == "beta"
    assert visible_path.read_text(encoding="utf-8") == "title: Daily News\n"
    assert hidden_path.read_text(encoding="utf-8") == "collection: beta\n"


def test_module_collection_update_rejects_stale_and_cross_root_targets(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path, duplicate_root=True)
    plan = project.set_module_collection("bulletin/NEWS", "alpha")
    module_root = tmp_path / "src/modules/bulletin/NEWS"
    (module_root / "meta.yaml").write_text("title: Changed\n", encoding="utf-8")

    stale = project.set_module_collection(
        "bulletin/NEWS",
        "alpha",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert stale["status"] == "blocked"
    assert stale["diagnostics"][0]["code"] == ("module_collection_update.plan_hash_mismatch")
    assert not (module_root / ".paradev/meta.yaml").exists()
    with pytest.raises(ValueError, match="Unknown collection"):
        project.set_module_collection("bulletin/NEWS", "remote")
