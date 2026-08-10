from __future__ import annotations

import paradev.build.source_slots as source_slots_module

from paradev.build import (
    BuildRegistry,
    BuildResult,
    CollectionSourceBundle,
    CollectionSourceFamily,
    Diagnostic,
    LocalizationEntry,
    ModuleSourceBundle,
    PDXBlockSource,
    SimpleSourceFamily,
    Slot,
    source_slot_status,
)
from paradev.pdx import PDXBlock


def test_source_slot_status_only_materializes_the_sources_manifest(monkeypatch) -> None:
    calls: list[str] = []
    original_manifest_rows = source_slots_module.manifest_rows

    def capture_manifest_rows(result: BuildResult, manifest_name: str) -> list[dict[str, object]]:
        calls.append(manifest_name)
        return original_manifest_rows(result, manifest_name)

    monkeypatch.setattr(source_slots_module, "manifest_rows", capture_manifest_rows)

    source_slot_status(BuildResult.plan(project_id="source_rows_only", profile="hoi4"), BuildRegistry())

    assert calls == ["sources.json"]


def test_source_slot_status_reports_module_contract_state() -> None:
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
    bundle = ModuleSourceBundle(
        root="src/modules/badge/GER_missing_icon",
        source_slots={"body": ("body.txt",)},
        metadata={"object_id": "GER_missing_icon"},
        pdx_sources=(PDXBlockSource(slot="body", path="body.txt", block=PDXBlock.from_str("badge = { id = GER_missing_icon }")),),
        module_id="badge/GER_missing_icon",
    )
    result = BuildResult.plan(
        project_id="required_slot_project",
        profile="hoi4",
        modules=(bundle.to_module(family="badge"),),
        diagnostics=(
            Diagnostic(
                code="slot.missing_required",
                message="Required slot 'icon' did not match 'icon.png'.",
                module_id="badge/GER_missing_icon",
                slot="icon",
            ),
        ),
    )

    payload = source_slot_status(result, registry, family="badge")

    assert payload == {
        "schema": "paradev.build.source-slots.v1",
        "project_id": "required_slot_project",
        "profile": "hoi4",
        "source_slots": [
            {
                "owner_kind": "module",
                "module_id": "badge/GER_missing_icon",
                "family": "badge",
                "root": "src/modules/badge/GER_missing_icon",
                "slot": "body",
                "match": "body.txt",
                "required": True,
                "many": False,
                "regex": False,
                "loader": "pdx",
                "status": "satisfied",
                "source_count": 1,
                "relative_paths": ["body.txt"],
                "paths": ["src/modules/badge/GER_missing_icon/body.txt"],
                "suggested_relative_paths": ["body.txt"],
                "suggested_paths": ["src/modules/badge/GER_missing_icon/body.txt"],
                "source_statuses": ["loaded"],
            },
            {
                "owner_kind": "module",
                "module_id": "badge/GER_missing_icon",
                "family": "badge",
                "root": "src/modules/badge/GER_missing_icon",
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
                "suggested_relative_paths": ["icon.png"],
                "suggested_paths": ["src/modules/badge/GER_missing_icon/icon.png"],
                "diagnostic_codes": ["slot.missing_required"],
            },
        ],
        "index": {
            "owner": {"module:badge/GER_missing_icon": {"body": [0], "icon": [1]}},
            "family": {"badge": [0, 1]},
            "slot": {"body": [0], "icon": [1]},
            "status": {"missing": [1], "satisfied": [0]},
        },
    }


def test_source_slot_status_reports_collection_descriptor_and_repeated_slots() -> None:
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
    bundle = CollectionSourceBundle(
        root="src/collections/bulletin/germany",
        metadata={"object_id": "germany"},
        source_slots={"strings": ("strings.yml", "loc/extra.yml")},
        loc_entries=(
            LocalizationEntry(key="germany", language="l_english", text="Germany", source_path="strings.yml"),
            LocalizationEntry(key="germany_desc", language="l_english", text="Germany extra.", source_path="loc/extra.yml"),
        ),
        collection_id="germany",
        family="bulletin",
    )
    result = BuildResult.plan(
        project_id="collection_slot_project",
        profile="hoi4",
        collections=(bundle.to_collection(),),
    )

    payload = source_slot_status(result, registry, collection_id="germany")

    assert payload["index"] == {
        "owner": {"collection:germany": {"strings": [0]}},
        "family": {"bulletin": [0]},
        "slot": {"strings": [0]},
        "status": {"satisfied": [0]},
    }
    assert payload["source_slots"] == [
        {
            "owner_kind": "collection",
            "collection_id": "germany",
            "family": "bulletin",
            "root": "src/collections/bulletin/germany",
            "slot": "strings",
            "match": "strings.yml",
            "matches": ["strings.yml", "loc/*.yml"],
            "required": False,
            "many": True,
            "regex": False,
            "loader": "loc",
            "status": "satisfied",
            "source_count": 2,
            "relative_paths": ["loc/extra.yml", "strings.yml"],
            "paths": [
                "src/collections/bulletin/germany/loc/extra.yml",
                "src/collections/bulletin/germany/strings.yml",
            ],
            "suggested_relative_paths": ["strings.yml"],
            "suggested_paths": ["src/collections/bulletin/germany/strings.yml"],
            "source_statuses": ["loaded"],
        }
    ]
