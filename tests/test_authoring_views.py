from __future__ import annotations

from pathlib import Path

import pytest

from paradev.build import BuildRegistry, CollectionSourceFamily, SimpleSourceFamily, Slot, authoring_path_view, authoring_plan_view, authoring_view


def test_authoring_view_lists_source_roots_and_folder_templates(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    import_root = tmp_path / "imports"
    source_root.mkdir()
    import_root.mkdir()

    payload = authoring_view(tmp_path, (source_root, import_root))

    assert payload == {
        "source_roots": [
            {
                "path": str(source_root),
                "relative_path": "src",
                "default": True,
            },
            {
                "path": str(import_root),
                "relative_path": "imports",
                "default": False,
            },
        ],
        "module_path_template": "modules/{family}/{object_id}",
        "collection_path_template": "collections/{family}/{collection_id}",
    }


def test_authoring_path_view_resolves_module_and_collection_roots(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    import_root = tmp_path / "imports"
    source_root.mkdir()
    import_root.mkdir()

    module = authoring_path_view(
        project_id="starter",
        project_root=tmp_path,
        source_roots=(source_root, import_root),
        kind="module",
        family="idea",
        target_id="GER_industry_spirit",
        source_root="imports",
    )
    collection = authoring_path_view(
        project_id="starter",
        project_root=tmp_path,
        source_roots=(source_root, import_root),
        kind="collection",
        family="focus",
        target_id="GER_main",
    )

    assert module == {
        "schema": "paradev.sdk.authoring_path.v1",
        "project_id": "starter",
        "kind": "module",
        "family": "idea",
        "object_id": "GER_industry_spirit",
        "module_id": "idea/GER_industry_spirit",
        "source_root": str(import_root),
        "source_root_relative_path": "imports",
        "root": str(import_root / "modules/idea/GER_industry_spirit"),
        "relative_path": "imports/modules/idea/GER_industry_spirit",
        "template": "modules/{family}/{object_id}",
        "exists": False,
    }
    assert collection == {
        "schema": "paradev.sdk.authoring_path.v1",
        "project_id": "starter",
        "kind": "collection",
        "family": "focus",
        "collection_id": "GER_main",
        "source_root": str(source_root),
        "source_root_relative_path": "src",
        "root": str(source_root / "collections/focus/GER_main"),
        "relative_path": "src/collections/focus/GER_main",
        "template": "collections/{family}/{collection_id}",
        "exists": False,
    }


def test_authoring_path_view_resolves_relative_source_roots_from_project_root(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()

    payload = authoring_path_view(
        project_id="starter",
        project_root=tmp_path,
        source_roots=("src",),
        kind="module",
        family="idea",
        target_id="GER_industry_spirit",
    )

    assert payload["source_root"] == str(tmp_path / "src")
    assert payload["source_root_relative_path"] == "src"
    assert payload["root"] == str(tmp_path / "src/modules/idea/GER_industry_spirit")
    assert payload["relative_path"] == "src/modules/idea/GER_industry_spirit"


def test_authoring_path_view_rejects_unknown_source_root(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()

    with pytest.raises(ValueError, match="Unknown source root other\\. Available source roots: src\\."):
        authoring_path_view(
            project_id="starter",
            project_root=tmp_path,
            source_roots=(source_root,),
            kind="module",
            family="idea",
            target_id="GER_industry_spirit",
            source_root="other",
        )


def test_authoring_plan_view_returns_module_source_slot_contract(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="badge",
            pdx_path_template="common/badges/{object_id}.txt",
            copy_path_template="gfx/badges/{object_id}{source_suffix}",
            source_slots=(
                Slot("body", "body.txt", required=True, kind="pdx"),
                Slot("icon", r"^icon\.(png|dds)$", required=True, regex=True, kind="copy"),
            ),
        )
    )

    payload = authoring_plan_view(
        registry,
        project_id="starter",
        profile="hoi4",
        project_root=tmp_path,
        source_roots=(source_root,),
        kind="module",
        family="badge",
        target_id="GER_new_badge",
    )

    assert payload == {
        "schema": "paradev.sdk.authoring_plan.v1",
        "project_id": "starter",
        "profile": "hoi4",
        "authoring_path": {
            "schema": "paradev.sdk.authoring_path.v1",
            "project_id": "starter",
            "kind": "module",
            "family": "badge",
            "object_id": "GER_new_badge",
            "module_id": "badge/GER_new_badge",
            "source_root": str(source_root),
            "source_root_relative_path": "src",
            "root": str(source_root / "modules/badge/GER_new_badge"),
            "relative_path": "src/modules/badge/GER_new_badge",
            "template": "modules/{family}/{object_id}",
            "exists": False,
        },
        "source_slots": [
            {
                "owner_kind": "module",
                "module_id": "badge/GER_new_badge",
                "family": "badge",
                "root": str(source_root / "modules/badge/GER_new_badge"),
                "slot": "body",
                "match": "body.txt",
                "required": True,
                "many": False,
                "regex": False,
                "loader": "pdx",
                "status": "missing",
                "source_count": 0,
                "relative_paths": [],
                "paths": [],
                "diagnostic_codes": ["slot.missing_required"],
                "suggested_relative_paths": ["src/modules/badge/GER_new_badge/body.txt"],
                "suggested_paths": [str(source_root / "modules/badge/GER_new_badge/body.txt")],
            },
            {
                "owner_kind": "module",
                "module_id": "badge/GER_new_badge",
                "family": "badge",
                "root": str(source_root / "modules/badge/GER_new_badge"),
                "slot": "icon",
                "match": r"^icon\.(png|dds)$",
                "required": True,
                "many": False,
                "regex": True,
                "loader": "copy",
                "status": "missing",
                "source_count": 0,
                "relative_paths": [],
                "paths": [],
                "diagnostic_codes": ["slot.missing_required"],
            },
        ],
        "index": {
            "loader": {"copy": [1], "pdx": [0]},
            "slot": {"body": [0], "icon": [1]},
            "status": {"missing": [0, 1]},
        },
    }


def test_authoring_plan_view_reports_existing_module_slot_status(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    module_root = source_root / "modules/badge/GER_existing_badge"
    module_root.mkdir(parents=True)
    (module_root / "body.txt").write_text("badge = { id = GER_existing_badge }", encoding="utf-8")
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="badge",
            pdx_path_template="common/badges/{object_id}.txt",
            copy_path_template="gfx/badges/{object_id}{source_suffix}",
            source_slots=(
                Slot("body", "body.txt", required=True, kind="pdx"),
                Slot("icon", "icon.png", required=True, kind="copy"),
            ),
        )
    )

    payload = authoring_plan_view(
        registry,
        project_id="starter",
        profile="hoi4",
        project_root=tmp_path,
        source_roots=(source_root,),
        kind="module",
        family="badge",
        target_id="GER_existing_badge",
    )

    assert payload["authoring_path"]["exists"] is True
    assert payload["source_slots"] == [
        {
            "owner_kind": "module",
            "module_id": "badge/GER_existing_badge",
            "family": "badge",
            "root": str(module_root),
            "slot": "body",
            "match": "body.txt",
            "required": True,
            "many": False,
            "regex": False,
            "loader": "pdx",
            "status": "satisfied",
            "source_count": 1,
            "relative_paths": ["body.txt"],
            "paths": [str(module_root / "body.txt")],
            "suggested_relative_paths": ["src/modules/badge/GER_existing_badge/body.txt"],
            "suggested_paths": [str(module_root / "body.txt")],
        },
        {
            "owner_kind": "module",
            "module_id": "badge/GER_existing_badge",
            "family": "badge",
            "root": str(module_root),
            "slot": "icon",
            "match": "icon.png",
            "required": True,
            "many": False,
            "regex": False,
            "loader": "copy",
            "status": "missing",
            "source_count": 0,
            "relative_paths": [],
            "paths": [],
            "diagnostic_codes": ["slot.missing_required"],
            "suggested_relative_paths": ["src/modules/badge/GER_existing_badge/icon.png"],
            "suggested_paths": [str(module_root / "icon.png")],
        },
    ]
    assert payload["index"] == {
        "loader": {"copy": [1], "pdx": [0]},
        "slot": {"body": [0], "icon": [1]},
        "status": {"missing": [1], "satisfied": [0]},
    }


def test_authoring_plan_view_reports_diagnostic_slot_status(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    module_root = source_root / "modules/badge/GER_duplicate_icons"
    icon_root = module_root / "icons"
    icon_root.mkdir(parents=True)
    (icon_root / "a.png").write_bytes(b"icon-a")
    (icon_root / "b.png").write_bytes(b"icon-b")
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="badge",
            pdx_path_template="common/badges/{object_id}.txt",
            copy_path_template="gfx/badges/{object_id}{source_suffix}",
            source_slots=(Slot("icon", "icons/*.png", kind="copy"),),
        )
    )

    payload = authoring_plan_view(
        registry,
        project_id="starter",
        profile="hoi4",
        project_root=tmp_path,
        source_roots=(source_root,),
        kind="module",
        family="badge",
        target_id="GER_duplicate_icons",
    )

    assert payload["source_slots"] == [
        {
            "owner_kind": "module",
            "module_id": "badge/GER_duplicate_icons",
            "family": "badge",
            "root": str(module_root),
            "slot": "icon",
            "match": "icons/*.png",
            "required": False,
            "many": False,
            "regex": False,
            "loader": "copy",
            "status": "diagnostic",
            "source_count": 1,
            "relative_paths": ["icons/a.png"],
            "paths": [str(icon_root / "a.png")],
            "diagnostic_codes": ["slot.multiple_matches"],
        }
    ]
    assert payload["index"] == {
        "loader": {"copy": [0]},
        "slot": {"icon": [0]},
        "status": {"diagnostic": [0]},
    }


def test_authoring_plan_view_groups_collection_descriptor_slots(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    registry = BuildRegistry().add(
        CollectionSourceFamily(
            family="bulletin",
            pdx_path_template="events/{collection_id}.txt",
            source_slots=(Slot("body", "body.txt", kind="pdx"),),
            collection_source_slots=(
                Slot("strings", "strings.yml", many=True, kind="loc"),
                Slot("strings", "loc/*.yml", many=True, kind="loc"),
            ),
        )
    )

    payload = authoring_plan_view(
        registry,
        project_id="starter",
        profile="hoi4",
        project_root=tmp_path,
        source_roots=(source_root,),
        kind="collection",
        family="bulletin",
        target_id="germany",
    )

    assert payload["authoring_path"]["collection_id"] == "germany"
    assert payload["source_slots"] == [
        {
            "owner_kind": "collection",
            "collection_id": "germany",
            "family": "bulletin",
            "root": str(source_root / "collections/bulletin/germany"),
            "slot": "strings",
            "match": "strings.yml",
            "matches": ["strings.yml", "loc/*.yml"],
            "required": False,
            "many": True,
            "regex": False,
            "loader": "loc",
            "status": "empty",
            "source_count": 0,
            "relative_paths": [],
            "paths": [],
            "suggested_relative_paths": ["src/collections/bulletin/germany/strings.yml"],
            "suggested_paths": [str(source_root / "collections/bulletin/germany/strings.yml")],
        }
    ]
    assert payload["index"] == {
        "loader": {"loc": [0]},
        "slot": {"strings": [0]},
        "status": {"empty": [0]},
    }


def test_authoring_plan_view_rejects_unknown_family(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()

    with pytest.raises(ValueError, match="Unknown build family 'missing'\\."):
        authoring_plan_view(
            BuildRegistry(),
            project_id="starter",
            profile="hoi4",
            project_root=tmp_path,
            source_roots=(source_root,),
            kind="module",
            family="missing",
            target_id="GER_missing",
        )
