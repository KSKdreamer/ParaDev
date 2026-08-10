from __future__ import annotations

import json
from pathlib import Path

from paradev.build import (
    Artifact,
    BuildContext,
    BuildRegistry,
    BuildResult,
    Collection,
    CopySource,
    Diagnostic,
    LocalizationEntry,
    Module,
    ModuleSourceBundle,
    PDXBlockSource,
    SpriteType,
    manifest_payloads,
    plan_build,
    write_manifests,
)
from paradev.pdx import PDXBlock


class FocusFamily:
    family = "focus"

    def emit(self, ctx: BuildContext, modules: tuple[Module, ...], collections: tuple[Collection, ...]) -> tuple[Artifact, ...]:
        assert ctx.project_id == "minimal_hoi4"
        assert ctx.dry_run is True
        assert collections[0].collection_id == "GER_main"
        return (
            Artifact(
                path="common/national_focus/GER_main.txt",
                artifact_type="pdx",
                owner="collection:GER_main",
                inputs=(Path(modules[0].root) / "def.pdx",),
                metadata={"module_ids": ["focus/GER_sample"]},
            ),
            Artifact(
                path="localisation/english/GER_sample_l_english.yml",
                artifact_type="loc",
                owner="module:focus/GER_sample",
                inputs=(Path(modules[0].root) / "main.loc",),
            ),
        )


class PDXTextWriter:
    artifact_type = "pdx"


class MissingWriterTargetRootsFamily:
    family = "focus"

    def emit(self, ctx: BuildContext, modules: tuple[Module, ...], collections: tuple[Collection, ...]) -> tuple[Artifact, ...]:
        return (
            Artifact(
                path="localisation/english/GER_sample_l_english.yml",
                artifact_type="loc",
                owner="module:focus/GER_sample",
            ),
            Artifact(
                path="debug/localisation/GER_sample_l_english.yml",
                artifact_type="loc",
                owner="module:focus/GER_sample",
                target_root="build",
            ),
        )


class ModuleOrderFamily:
    family = "focus"

    def emit(self, ctx: BuildContext, modules: tuple[Module, ...], collections: tuple[Collection, ...]) -> tuple[Artifact, ...]:
        return tuple(
            Artifact(
                path=f"order/{index}_{module.module_id.replace('/', '_')}.txt",
                artifact_type="pdx",
                owner=f"module:{module.module_id}",
            )
            for index, module in enumerate(modules)
        )


def test_registered_family_can_emit_dry_run_artifact_without_writes(tmp_path: Path) -> None:
    registry = BuildRegistry().add(FocusFamily()).add(PDXTextWriter())
    module = Module(module_id="focus/GER_sample", family="focus", root=tmp_path / "modules/focus/GER_sample")
    collection = Collection(collection_id="GER_main", family="focus_tree", module_ids=(module.module_id,))

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,), collections=(collection,))

    assert registry.family("focus").family == "focus"
    assert registry.writer("pdx").artifact_type == "pdx"
    assert result.dry_run is True
    assert result.artifacts[0].path == "common/national_focus/GER_main.txt"
    assert not (tmp_path / "common").exists()


def test_plan_build_reports_missing_artifact_writers_before_emission(tmp_path: Path) -> None:
    registry = BuildRegistry().add(FocusFamily()).add(PDXTextWriter())
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root=tmp_path / "modules/focus/GER_sample",
        source_slots={"def": ("def.pdx",), "loc": ("main.loc",)},
    )
    collection = Collection(collection_id="GER_main", family="focus_tree", module_ids=(module.module_id,))

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,), collections=(collection,))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="build.missing_artifact_writer",
            message="Artifact type 'loc' is planned but no artifact writer is registered.",
            severity="error",
            artifact_path="localisation/english/GER_sample_l_english.yml",
            target_root="output",
        ),
    )


def test_plan_build_reports_missing_artifact_writers_per_target_root(tmp_path: Path) -> None:
    registry = BuildRegistry().add(MissingWriterTargetRootsFamily()).add(PDXTextWriter())
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root=tmp_path / "modules/focus/GER_sample",
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="build.missing_artifact_writer",
            message="Artifact type 'loc' is planned but no artifact writer is registered.",
            severity="error",
            artifact_path="debug/localisation/GER_sample_l_english.yml",
            target_root="build",
        ),
        Diagnostic(
            code="build.missing_artifact_writer",
            message="Artifact type 'loc' is planned but no artifact writer is registered.",
            severity="error",
            artifact_path="localisation/english/GER_sample_l_english.yml",
            target_root="output",
        ),
    )


def test_plan_build_orders_family_modules_from_after_dependencies() -> None:
    registry = BuildRegistry().add(ModuleOrderFamily())
    later = Module(
        module_id="focus/GER_sample",
        family="focus",
        root="modules/focus/GER_sample",
        metadata={"object_id": "GER_sample", "after": ["focus:GER_rhineland"]},
    )
    earlier = Module(
        module_id="focus/GER_rhineland",
        family="focus",
        root="modules/focus/GER_rhineland",
        metadata={"object_id": "GER_rhineland"},
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(later, earlier))

    assert [module.module_id for module in result.modules] == ["focus/GER_rhineland", "focus/GER_sample"]
    assert [artifact.owner for artifact in result.artifacts] == ["module:focus/GER_rhineland", "module:focus/GER_sample"]


def test_plan_build_derives_collections_before_family_emit() -> None:
    registry = BuildRegistry().add(FocusFamily())
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root="modules/focus/GER_sample",
        collection_id="GER_main",
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,))

    assert result.collections == (
        Collection(
            collection_id="GER_main",
            family="focus",
            module_ids=("focus/GER_sample",),
        ),
    )
    assert result.artifacts[0].owner == "collection:GER_main"


def test_manifest_payloads_and_writes_include_source_map_and_summary(tmp_path: Path) -> None:
    registry = BuildRegistry().add(FocusFamily())
    bundle = ModuleSourceBundle(
        root="modules/focus/GER_sample",
        source_slots={"def": ("def.pdx",), "loc": ("main.loc",)},
        metadata={"requires": ["idea:GER_industrial_spirit"], "after": ["focus:GER_rhineland"]},
        pdx_sources=(PDXBlockSource(slot="def", path="def.pdx", block=PDXBlock.from_str("focus = { id = GER_sample }")),),
        loc_entries=(LocalizationEntry(key="GER_sample", language="l_english", text="Sample Focus", source_path="main.loc"),),
    )
    module = bundle.to_module(family="focus", collection_id="GER_main")
    collection = Collection(collection_id="GER_main", family="focus_tree", module_ids=(module.module_id,))
    diagnostic = Diagnostic(
        code="focus.test_warning",
        message="Focus warning with source context.",
        severity="warning",
        module_id="focus/GER_sample",
        source_path="def.pdx",
        span={"line": 2, "column": 7},
    )
    result = plan_build(project_id="minimal_hoi4", profile="hoi4", registry=registry, modules=(module,), collections=(collection,), diagnostics=(diagnostic,))

    payloads = manifest_payloads(result)
    written = write_manifests(result, tmp_path / ".paradev/.cache/build")

    assert set(payloads) == {
        "modules.json",
        "collections.json",
        "dependencies.json",
        "artifacts.json",
        "assets.json",
        "diagnostics.json",
        "localization.json",
        "sources.json",
        "source-map.json",
        "sprites.json",
        "summary.json",
    }
    assert payloads["modules.json"]["index"] == {
        "collection": {"GER_main": [0]},
        "family": {"focus": [0]},
        "id": {"focus/GER_sample": [0]},
        "slot": {"def": [0], "loc": [0]},
    }
    assert payloads["collections.json"]["index"] == {
        "family": {"focus_tree": [0]},
        "id": {"GER_main": [0]},
        "module": {"focus/GER_sample": [0]},
    }
    assert payloads["artifacts.json"]["index"] == {
        "collection": {"GER_main": [0]},
        "mode": {"plan": [0, 1]},
        "module": {"focus/GER_sample": [0, 1]},
        "owner": {"collection:GER_main": [0], "module:focus/GER_sample": [1]},
        "path": {"common/national_focus/GER_main.txt": [0], "localisation/english/GER_sample_l_english.yml": [1]},
        "target_root": {"output": [0, 1]},
        "type": {"loc": [1], "pdx": [0]},
    }
    assert payloads["dependencies.json"]["dependencies"] == [
        {
            "source": "module:focus/GER_sample",
            "target": "idea:GER_industrial_spirit",
            "kind": "requires",
        },
        {
            "source": "module:focus/GER_sample",
            "target": "focus:GER_rhineland",
            "kind": "after",
        },
    ]
    assert payloads["dependencies.json"]["index"] == {"module:focus/GER_sample": {"after": [1], "requires": [0]}}
    assert payloads["source-map.json"]["source_map"] == [
        {
            "artifact_path": "common/national_focus/GER_main.txt",
            "type": "pdx",
            "target_root": "output",
            "owner": "collection:GER_main",
            "inputs": ["modules/focus/GER_sample/def.pdx"],
            "sources": [
                {
                    "path": "modules/focus/GER_sample/def.pdx",
                    "module_id": "focus/GER_sample",
                    "family": "focus",
                    "slot": "def",
                }
            ],
        },
        {
            "artifact_path": "localisation/english/GER_sample_l_english.yml",
            "type": "loc",
            "target_root": "output",
            "owner": "module:focus/GER_sample",
            "inputs": ["modules/focus/GER_sample/main.loc"],
            "sources": [
                {
                    "path": "modules/focus/GER_sample/main.loc",
                    "module_id": "focus/GER_sample",
                    "family": "focus",
                    "slot": "loc",
                }
            ],
        },
    ]
    assert payloads["source-map.json"]["index"] == {"focus/GER_sample": {"def": [0], "loc": [1]}}
    assert payloads["sources.json"]["sources"] == [
        {
            "owner_kind": "module",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "root": "modules/focus/GER_sample",
            "slot": "def",
            "path": "modules/focus/GER_sample/def.pdx",
            "relative_path": "def.pdx",
            "loader": "pdx",
            "status": "loaded",
            "entry_count": 1,
            "diagnostic_codes": ["focus.test_warning"],
        },
        {
            "owner_kind": "module",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "root": "modules/focus/GER_sample",
            "slot": "loc",
            "path": "modules/focus/GER_sample/main.loc",
            "relative_path": "main.loc",
            "loader": "loc",
            "status": "loaded",
            "localization_count": 1,
            "languages": ["l_english"],
        },
    ]
    assert payloads["sources.json"]["index"] == {"focus/GER_sample": {"def": [0], "loc": [1]}}
    assert payloads["sprites.json"]["sprites"] == []
    assert payloads["sprites.json"]["index"] == {}
    assert payloads["diagnostics.json"]["diagnostics"] == [
        {
            "code": "focus.test_warning",
            "message": "Focus warning with source context.",
            "severity": "warning",
            "module_id": "focus/GER_sample",
            "source_path": "def.pdx",
            "span": {"line": 2, "column": 7},
            "source": {
                "path": "modules/focus/GER_sample/def.pdx",
                "module_id": "focus/GER_sample",
                "family": "focus",
                "slot": "def",
            },
        }
    ]
    assert payloads["diagnostics.json"]["index"] == {"warning": {"focus.test_warning": [0]}}
    assert payloads["diagnostics.json"]["family_index"] == {"focus": {"warning": {"focus.test_warning": [0]}}}
    assert payloads["modules.json"]["profile"] == "hoi4"
    assert payloads["source-map.json"]["profile"] == "hoi4"
    assert payloads["summary.json"]["summary"]["artifact_count"] == 2
    assert set(written) == set(payloads)
    assert json.loads((tmp_path / ".paradev/.cache/build/summary.json").read_text(encoding="utf-8")) == payloads["summary.json"]


def test_sources_manifest_does_not_attach_unanchored_owner_diagnostics() -> None:
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root="modules/focus/GER_sample",
        source_slots={"def": ("def.pdx",), "loc": ("main.loc",)},
    )
    result = BuildResult.plan(
        project_id="minimal_hoi4",
        modules=(module,),
        diagnostics=(
            Diagnostic(
                code="family.emit_failed",
                message="Family emit failed.",
                module_id="focus/GER_sample",
            ),
        ),
    )

    payload = manifest_payloads(result)["sources.json"]

    assert payload["sources"] == [
        {
            "owner_kind": "module",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "root": "modules/focus/GER_sample",
            "slot": "def",
            "path": "modules/focus/GER_sample/def.pdx",
            "relative_path": "def.pdx",
            "loader": "pdx",
            "status": "matched",
        },
        {
            "owner_kind": "module",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "root": "modules/focus/GER_sample",
            "slot": "loc",
            "path": "modules/focus/GER_sample/main.loc",
            "relative_path": "main.loc",
            "loader": "loc",
            "status": "matched",
        },
    ]


def test_manifest_payloads_include_copy_asset_catalog() -> None:
    source = CopySource(
        slot="icon",
        path="icon.png",
        output_path="icon.png",
        sha256="asset-sha",
        size=24,
        media_type="image/png",
        format="png",
        width=40,
        height=30,
    )
    bundle = ModuleSourceBundle(
        root="modules/idea/GER_idea",
        source_slots={"icon": ("icon.png",)},
        metadata={"object_id": "GER_idea"},
        copy_sources=(source,),
        module_id="idea/GER_idea",
    )
    module = Module(
        module_id="idea/GER_idea",
        family="idea",
        root="modules/idea/GER_idea",
        source_slots=bundle.source_slots,
        metadata=bundle.metadata,
        payload=bundle,
    )
    result = BuildResult.plan(
        project_id="minimal_hoi4",
        modules=(module,),
        artifacts=(
            Artifact(
                path="gfx/interface/ideas/idea_GER_idea.png",
                artifact_type="copy",
                owner="module:idea/GER_idea",
                inputs=("modules/idea/GER_idea/icon.png",),
                metadata=source.to_dict(),
            ),
        ),
    )

    payload = manifest_payloads(result)["assets.json"]

    assert payload == {
        "schema": "paradev.build.assets.v1",
        "project_id": "minimal_hoi4",
        "assets": [
            {
                "module_id": "idea/GER_idea",
                "family": "idea",
                "slot": "icon",
                "source_path": "icon.png",
                "artifact_path": "gfx/interface/ideas/idea_GER_idea.png",
                "owner": "module:idea/GER_idea",
                "target_root": "output",
                "sha256": "asset-sha",
                "size": 24,
                "media_type": "image/png",
                "format": "png",
                "width": 40,
                "height": 30,
                "source": {
                    "path": "modules/idea/GER_idea/icon.png",
                    "module_id": "idea/GER_idea",
                    "family": "idea",
                    "slot": "icon",
                },
            }
        ],
        "index": {"idea/GER_idea": {"icon": [0]}},
    }


def test_manifest_payloads_include_sprite_declaration_catalog() -> None:
    bundle = ModuleSourceBundle(
        root="modules/idea/GER_idea",
        source_slots={"icon": ("icon.dds",)},
        metadata={"object_id": "GER_idea"},
        module_id="idea/GER_idea",
    )
    module = Module(
        module_id="idea/GER_idea",
        family="idea",
        root="modules/idea/GER_idea",
        source_slots=bundle.source_slots,
        metadata=bundle.metadata,
        payload=bundle,
    )
    result = BuildResult.plan(
        project_id="minimal_hoi4",
        modules=(module,),
        artifacts=(
            Artifact(
                path="interface/paradev_idea.gfx",
                artifact_type="sprite_gfx",
                owner="project:minimal_hoi4",
                inputs=("modules/idea/GER_idea/icon.dds",),
                metadata={"family": "idea", "sprite_count": 1},
                payload=(SpriteType(name="GFX_idea_GER_idea", texturefile="gfx/interface/ideas/idea_GER_idea.dds"),),
            ),
        ),
    )

    payload = manifest_payloads(result)["sprites.json"]

    assert payload == {
        "schema": "paradev.build.sprites.v1",
        "project_id": "minimal_hoi4",
        "sprites": [
            {
                "name": "GFX_idea_GER_idea",
                "texturefile": "gfx/interface/ideas/idea_GER_idea.dds",
                "artifact_path": "interface/paradev_idea.gfx",
                "owner": "project:minimal_hoi4",
                "target_root": "output",
                "family": "idea",
                "module_id": "idea/GER_idea",
                "slot": "icon",
                "source_path": "modules/idea/GER_idea/icon.dds",
                "source": {
                    "path": "modules/idea/GER_idea/icon.dds",
                    "module_id": "idea/GER_idea",
                    "family": "idea",
                    "slot": "icon",
                },
            }
        ],
        "index": {"idea/GER_idea": {"icon": [0]}},
    }


def test_manifest_payloads_include_localization_scan_rows_with_duplicate_state() -> None:
    bundle = ModuleSourceBundle(
        root="modules/focus/GER_sample",
        source_slots={"loc": ("extra.loc", "main.loc")},
        metadata={"object_id": "GER_sample"},
        loc_entries=(
            LocalizationEntry(
                key="GER_sample",
                language="l_english",
                text="Duplicate Focus",
                source_path="extra.loc",
                module_id="focus/GER_sample",
            ),
            LocalizationEntry(
                key="GER_sample",
                language="l_english",
                text="Sample Focus",
                source_path="main.loc",
                module_id="focus/GER_sample",
            ),
            LocalizationEntry(
                key="GER_sample_desc",
                language="l_english",
                text="Sample description",
                source_path="main.loc",
                module_id="focus/GER_sample",
            ),
        ),
        module_id="focus/GER_sample",
    )
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root="modules/focus/GER_sample",
        source_slots=bundle.source_slots,
        metadata=bundle.metadata,
        payload=bundle,
    )
    result = BuildResult.plan(project_id="minimal_hoi4", modules=(module,))

    payload = manifest_payloads(result)["localization.json"]

    assert payload == {
        "schema": "paradev.build.localization.v1",
        "project_id": "minimal_hoi4",
        "localization": [
            {
                "module_id": "focus/GER_sample",
                "family": "focus",
                "language": "l_english",
                "key": "GER_sample",
                "text": "Duplicate Focus",
                "source_path": "extra.loc",
                "duplicate": True,
                "source": {
                    "path": "modules/focus/GER_sample/extra.loc",
                    "module_id": "focus/GER_sample",
                    "family": "focus",
                    "slot": "loc",
                },
            },
            {
                "module_id": "focus/GER_sample",
                "family": "focus",
                "language": "l_english",
                "key": "GER_sample",
                "text": "Sample Focus",
                "source_path": "main.loc",
                "duplicate": True,
                "source": {
                    "path": "modules/focus/GER_sample/main.loc",
                    "module_id": "focus/GER_sample",
                    "family": "focus",
                    "slot": "loc",
                },
            },
            {
                "module_id": "focus/GER_sample",
                "family": "focus",
                "language": "l_english",
                "key": "GER_sample_desc",
                "text": "Sample description",
                "source_path": "main.loc",
                "duplicate": False,
                "source": {
                    "path": "modules/focus/GER_sample/main.loc",
                    "module_id": "focus/GER_sample",
                    "family": "focus",
                    "slot": "loc",
                },
            },
        ],
        "index": {
            "l_english": {
                "GER_sample": {"duplicate": True, "rows": [0, 1]},
                "GER_sample_desc": {"duplicate": False, "rows": [2]},
            }
        },
    }


def test_manifest_payloads_mark_project_level_duplicate_localization_rows() -> None:
    first_bundle = ModuleSourceBundle(
        root="modules/focus/GER_a",
        source_slots={"loc": ("main.loc",)},
        metadata={"object_id": "GER_a"},
        loc_entries=(LocalizationEntry(key="GER_shared", language="l_english", text="First", source_path="main.loc", module_id="focus/GER_a"),),
        module_id="focus/GER_a",
    )
    second_bundle = ModuleSourceBundle(
        root="modules/focus/GER_b",
        source_slots={"loc": ("main.loc",)},
        metadata={"object_id": "GER_b"},
        loc_entries=(LocalizationEntry(key="GER_shared", language="l_english", text="Second", source_path="main.loc", module_id="focus/GER_b"),),
        module_id="focus/GER_b",
    )
    result = BuildResult.plan(
        project_id="minimal_hoi4",
        modules=(
            Module(
                module_id="focus/GER_a",
                family="focus",
                root="modules/focus/GER_a",
                source_slots=first_bundle.source_slots,
                metadata=first_bundle.metadata,
                payload=first_bundle,
            ),
            Module(
                module_id="focus/GER_b",
                family="focus",
                root="modules/focus/GER_b",
                source_slots=second_bundle.source_slots,
                metadata=second_bundle.metadata,
                payload=second_bundle,
            ),
        ),
    )

    rows = manifest_payloads(result)["localization.json"]["localization"]
    index = manifest_payloads(result)["localization.json"]["index"]

    assert [(row["module_id"], row["duplicate"]) for row in rows] == [
        ("focus/GER_a", True),
        ("focus/GER_b", True),
    ]
    assert index == {"l_english": {"GER_shared": {"duplicate": True, "rows": [0, 1]}}}
