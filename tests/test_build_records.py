from __future__ import annotations

from pathlib import Path

import pytest

import paradev.build.records as build_records
from paradev.build import Artifact, BuildResult, Collection, Diagnostic, LocalizationEntry, Module, ModuleSourceBundle


def test_build_records_have_stable_json_views() -> None:
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root=Path("modules/focus/GER_sample"),
        source_slots={"def": ["def.pdx"], "loc": ["main.loc"]},
        collection_id="GER_main",
        metadata={
            "type": "focus",
            "priority": 10,
            "requires": ["idea:GER_industrial_spirit"],
            "after": ["focus:GER_rhineland"],
        },
    )
    collection = Collection(collection_id="GER_main", family="focus_tree", module_ids=("focus/GER_sample",))
    artifact = Artifact(
        path="common/national_focus/GER_main.txt",
        artifact_type="pdx",
        owner="collection:GER_main",
        inputs=("modules/focus/GER_sample/def.pdx",),
    )
    result = BuildResult.plan(project_id="minimal_hoi4", modules=(module,), collections=(collection,), artifacts=(artifact,))

    assert module.to_dict()["source_slots"] == {"def": ["def.pdx"], "loc": ["main.loc"]}
    assert collection.to_dict()["module_ids"] == ["focus/GER_sample"]
    assert artifact.to_dict()["type"] == "pdx"
    assert artifact.to_dict()["target_root"] == "output"
    assert result.to_dict()["summary"] == {
        "module_count": 1,
        "collection_count": 1,
        "dependency_count": 2,
        "artifact_count": 1,
        "diagnostic_count": 0,
        "error_count": 0,
        "blocked": False,
    }
    assert result.to_dict()["dependencies"] == [
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


def test_build_result_records_selected_profile_when_supplied() -> None:
    result = BuildResult.plan(project_id="minimal_hoi4", profile="hoi4")

    assert result.to_dict()["profile"] == "hoi4"


def test_build_result_reports_duplicate_artifact_paths_as_blocking_diagnostics() -> None:
    first = Artifact(path="common/national_focus/GER_main.txt", artifact_type="pdx", owner="collection:GER_main", inputs=("a/def.pdx",))
    second = Artifact(path="common/national_focus/GER_main.txt", artifact_type="pdx", owner="collection:GER_alt", inputs=("b/def.pdx",))

    result = BuildResult.plan(project_id="minimal_hoi4", artifacts=(first, second))

    assert result.blocked is True
    assert result.diagnostics[0].to_dict() == {
        "code": "build.artifact_path_collision",
        "message": "Artifact path common/national_focus/GER_main.txt under output root is produced by collection:GER_main and collection:GER_alt.",
        "severity": "error",
        "artifact_path": "common/national_focus/GER_main.txt",
        "target_root": "output",
        "owners": ["collection:GER_main", "collection:GER_alt"],
    }
    assert result.to_dict()["summary"]["error_count"] == 1


def test_build_result_blocks_casefolded_artifact_paths_with_identical_content() -> None:
    first = Artifact(
        path="common/ideas/GER_Shared.txt",
        artifact_type="pdx",
        owner="module:idea/GER_first",
        target_root="build",
        payload="ideas = { GER_shared = {} }",
    )
    second = Artifact(
        path="common/ideas/ger_shared.txt",
        artifact_type="pdx",
        owner="module:idea/GER_second",
        target_root="build",
        payload="ideas = { GER_shared = {} }",
    )

    result = BuildResult.plan(project_id="minimal_hoi4", artifacts=(first, second))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="build.artifact_path_collision",
            message=(
                "Artifact paths 'common/ideas/GER_Shared.txt' from module:idea/GER_first and "
                "'common/ideas/ger_shared.txt' from module:idea/GER_second under build root "
                "collide after Unicode NFC normalization and case folding."
            ),
            severity="error",
            artifact_path="common/ideas/ger_shared.txt",
            target_root="build",
            owners=("module:idea/GER_first", "module:idea/GER_second"),
        ),
    )


def test_build_result_blocks_casefolded_artifact_paths_with_different_content() -> None:
    first = Artifact(
        path="common/ideas/Shared.txt",
        artifact_type="pdx",
        owner="module:idea/GER_first",
        payload="ideas = { GER_first = {} }",
    )
    second = Artifact(
        path="common/ideas/shared.txt",
        artifact_type="pdx",
        owner="module:idea/GER_second",
        payload="ideas = { GER_second = {} }",
    )

    result = BuildResult.plan(project_id="minimal_hoi4", artifacts=(first, second))

    assert result.blocked is True
    assert result.diagnostics[0].code == "build.artifact_path_collision"
    assert result.diagnostics[0].owners == ("module:idea/GER_first", "module:idea/GER_second")
    assert "'common/ideas/Shared.txt' from module:idea/GER_first" in result.diagnostics[0].message
    assert "'common/ideas/shared.txt' from module:idea/GER_second" in result.diagnostics[0].message


def test_build_result_blocks_unicode_nfc_equivalent_artifact_paths() -> None:
    first = Artifact(path="gfx/interface/caf\u00e9.dds", artifact_type="copy", owner="module:idea/first")
    second = Artifact(path="gfx/interface/cafe\u0301.dds", artifact_type="copy", owner="module:idea/second")

    result = BuildResult.plan(project_id="minimal_hoi4", artifacts=(first, second))

    assert result.blocked is True
    assert result.diagnostics[0].code == "build.artifact_path_collision"
    assert "'gfx/interface/caf\u00e9.dds' from module:idea/first" in result.diagnostics[0].message
    assert "'gfx/interface/cafe\u0301.dds' from module:idea/second" in result.diagnostics[0].message


def test_build_result_allows_same_artifact_path_under_different_target_roots() -> None:
    output_artifact = Artifact(path="views/focus-tree/GER_main.json", artifact_type="view", owner="collection:GER_main")
    build_artifact = Artifact(
        path="views/focus-tree/GER_main.json",
        artifact_type="view",
        owner="collection:GER_main",
        target_root="build",
    )

    result = BuildResult.plan(project_id="minimal_hoi4", artifacts=(output_artifact, build_artifact))

    assert result.blocked is False
    assert [artifact.to_dict()["target_root"] for artifact in result.artifacts] == ["output", "build"]


def test_build_result_reports_invalid_artifact_target_roots() -> None:
    artifact = Artifact(path="debug/focus/GER_main.json", artifact_type="view", owner="collection:GER_main", target_root="cache")

    result = BuildResult.plan(project_id="minimal_hoi4", artifacts=(artifact,))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="build.invalid_artifact_target_root",
            message="Artifact debug/focus/GER_main.json target root 'cache' must be one of: build, output.",
            severity="error",
            artifact_path="debug/focus/GER_main.json",
            target_root="cache",
        ),
    )


def test_build_result_reports_invalid_artifact_paths() -> None:
    artifact = Artifact(path="../escaped.txt", artifact_type="pdx", owner="module:focus/GER_sample")

    result = BuildResult.plan(project_id="minimal_hoi4", artifacts=(artifact,))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="build.invalid_artifact_path",
            message="Artifact path ../escaped.txt must be relative and stay under its target root.",
            severity="error",
            artifact_path="../escaped.txt",
            target_root="output",
        ),
    )


def test_build_result_reports_untracked_artifact_inputs_as_warnings() -> None:
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root=Path("modules/focus/GER_sample"),
        source_slots={"def": ["def.pdx"]},
    )
    artifact = Artifact(
        path="common/national_focus/GER_main.txt",
        artifact_type="pdx",
        owner="collection:GER_main",
        inputs=("modules/focus/GER_sample/missing.pdx",),
        target_root="build",
    )

    result = BuildResult.plan(project_id="minimal_hoi4", modules=(module,), artifacts=(artifact,))

    assert result.blocked is False
    assert result.diagnostics == (
        Diagnostic(
            code="build.untracked_artifact_input",
            message="Artifact common/national_focus/GER_main.txt input modules/focus/GER_sample/missing.pdx does not match any discovered module source slot.",
            severity="warning",
            source_path="modules/focus/GER_sample/missing.pdx",
            artifact_path="common/national_focus/GER_main.txt",
            target_root="build",
        ),
    )


def test_build_result_reports_project_level_duplicate_localization_keys() -> None:
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
    first = Module(
        module_id="focus/GER_a",
        family="focus",
        root="modules/focus/GER_a",
        source_slots=first_bundle.source_slots,
        metadata=first_bundle.metadata,
        payload=first_bundle,
    )
    second = Module(
        module_id="focus/GER_b",
        family="focus",
        root="modules/focus/GER_b",
        source_slots=second_bundle.source_slots,
        metadata=second_bundle.metadata,
        payload=second_bundle,
    )
    expected_message = " ".join(
        (
            "Localization key 'GER_shared' for 'l_english' is declared by",
            "focus/GER_a main.loc and focus/GER_b main.loc.",
        )
    )

    result = BuildResult.plan(project_id="minimal_hoi4", modules=(first, second))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="loc.project_duplicate_key",
            message=expected_message,
            severity="error",
            module_id="focus/GER_b",
            slot="loc",
            source_path="main.loc",
        ),
    )


def test_build_result_derives_collections_from_module_metadata() -> None:
    earlier = Module(
        module_id="focus/GER_rhineland",
        family="focus",
        root=Path("modules/focus/GER_rhineland"),
        collection_id="GER_main",
        metadata={"object_id": "GER_rhineland"},
    )
    later = Module(
        module_id="focus/GER_sample",
        family="focus",
        root=Path("modules/focus/GER_sample"),
        collection_id="GER_main",
        metadata={"object_id": "GER_sample", "after": ["focus:GER_rhineland"]},
    )

    result = BuildResult.plan(project_id="minimal_hoi4", modules=(later, earlier))

    assert result.summary()["collection_count"] == 1
    assert result.collections == (
        Collection(
            collection_id="GER_main",
            family="focus",
            module_ids=("focus/GER_rhineland", "focus/GER_sample"),
        ),
    )


def test_explicit_collection_order_appends_new_self_declared_members() -> None:
    existing = Module(
        module_id="focus/GER_rhineland",
        family="focus",
        root=Path("modules/focus/GER_rhineland"),
        collection_id="GER_main",
    )
    copied = Module(
        module_id="focus/GER_new_focus",
        family="focus",
        root=Path("modules/focus/GER_new_focus"),
        collection_id="GER_main",
    )
    collection = Collection(
        collection_id="GER_main",
        family="focus",
        module_ids=("focus/GER_rhineland",),
    )

    result = BuildResult.plan(
        project_id="minimal_hoi4",
        modules=(copied, existing),
        collections=(collection,),
    )

    assert result.collections[0].module_ids == (
        "focus/GER_rhineland",
        "focus/GER_new_focus",
    )


def test_module_order_without_after_edges_skips_alias_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    modules = tuple(
        Module(
            module_id=f"idea/IDEA_{index:04d}",
            family="idea",
            root=Path(f"modules/idea/IDEA_{index:04d}"),
            metadata={"requires": ["external:dependency"]},
        )
        for index in reversed(range(256))
    )

    def unexpected_alias_graph(_modules: object) -> object:
        pytest.fail("dependency-free ordering should not build an alias graph")

    monkeypatch.setattr(build_records, "_module_aliases", unexpected_alias_graph)

    ordered, diagnostics = build_records._module_order(modules)

    assert [module.module_id for module in ordered] == sorted(module.module_id for module in modules)
    assert diagnostics == ()


def test_build_result_reports_invalid_module_dependencies_as_blocking_diagnostics() -> None:
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root=Path("modules/focus/GER_sample"),
        metadata={"requires": "idea:GER_industrial_spirit"},
    )

    result = BuildResult.plan(project_id="minimal_hoi4", modules=(module,))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="build.invalid_dependency_metadata",
            message="Module focus/GER_sample metadata field 'requires' must be a list of dependency targets.",
            severity="error",
            module_id="focus/GER_sample",
            source_path="meta.yaml",
        ),
    )


def test_build_result_reports_missing_project_local_dependency_targets() -> None:
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root=Path("modules/focus/GER_sample"),
        metadata={
            "object_id": "GER_sample",
            "requires": ["module:focus/GER_missing"],
            "after": ["focus/GER_late"],
        },
    )

    result = BuildResult.plan(project_id="minimal_hoi4", modules=(module,))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="build.missing_dependency_target",
            message="Module focus/GER_sample dependency 'module:focus/GER_missing' from metadata field 'requires' does not resolve to a project module.",
            severity="error",
            module_id="focus/GER_sample",
            source_path="meta.yaml",
        ),
        Diagnostic(
            code="build.missing_dependency_target",
            message="Module focus/GER_sample dependency 'focus/GER_late' from metadata field 'after' does not resolve to a project module.",
            severity="error",
            module_id="focus/GER_sample",
            source_path="meta.yaml",
        ),
    )


def test_build_result_keeps_reference_style_dependency_targets_as_graph_edges() -> None:
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root=Path("modules/focus/GER_sample"),
        metadata={
            "object_id": "GER_sample",
            "requires": ["idea:GER_industrial_spirit"],
            "after": ["focus:GER_rhineland"],
        },
    )

    result = BuildResult.plan(project_id="minimal_hoi4", modules=(module,))

    assert result.diagnostics == ()
    assert [dependency.to_dict() for dependency in result.dependencies] == [
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


def test_build_result_reports_module_after_cycles_as_blocking_diagnostics() -> None:
    first = Module(
        module_id="focus/GER_a",
        family="focus",
        root=Path("modules/focus/GER_a"),
        metadata={"object_id": "GER_a", "after": ["focus:GER_b"]},
    )
    second = Module(
        module_id="focus/GER_b",
        family="focus",
        root=Path("modules/focus/GER_b"),
        metadata={"object_id": "GER_b", "after": ["focus:GER_a"]},
    )

    result = BuildResult.plan(project_id="minimal_hoi4", modules=(first, second))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="build.dependency_cycle",
            message="Module after dependencies contain a cycle: focus/GER_a, focus/GER_b.",
            severity="error",
            module_id="focus/GER_a",
            source_path="meta.yaml",
        ),
    )
