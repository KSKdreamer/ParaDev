from __future__ import annotations

import logging
from pathlib import Path

import pytest
from heavenbase.utils import loads_json

import paradev.build._fs as build_fs
import paradev.build.manifest as build_manifest
import paradev.build.views as build_views
from paradev.build import (
    Artifact,
    BuildResult,
    Diagnostic,
    Module,
    ModuleSourceBundle,
    PDXBlockSource,
    artifacts_view,
    diagnostics_view,
    manifests_view,
    sources_view,
    summary_view,
    write_manifests,
)
from paradev.pdx import PDXBlock


def test_summary_view_returns_build_summary_manifest_payload() -> None:
    result = BuildResult.plan(
        project_id="view_project",
        profile="hoi4",
        modules=(Module(module_id="focus/GER_sample", family="focus", root="modules/focus/GER_sample"),),
        artifacts=(Artifact(path="common/national_focus/GER_sample.txt", artifact_type="pdx", owner="module:focus/GER_sample"),),
    )

    payload = summary_view(result)

    assert payload == {
        "schema": "paradev.build.summary.v1",
        "project_id": "view_project",
        "profile": "hoi4",
        "summary": {
            "module_count": 1,
            "collection_count": 0,
            "dependency_count": 0,
            "artifact_count": 1,
            "diagnostic_count": 0,
            "error_count": 0,
            "blocked": False,
        },
    }


def test_summary_view_does_not_materialize_unrelated_manifests(monkeypatch: pytest.MonkeyPatch) -> None:
    result = BuildResult.plan(project_id="view_project", profile="hoi4")

    def unexpected_manifests(_result: BuildResult) -> dict[str, dict[str, object]]:
        raise AssertionError("summary_view must build only summary.json")

    monkeypatch.setattr(build_views, "manifest_payloads", unexpected_manifests)

    assert summary_view(result)["schema"] == "paradev.build.summary.v1"


def test_write_manifests_skips_byte_identical_replacements(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = BuildResult.plan(project_id="stable_manifests", profile="hoi4")
    write_manifests(result, tmp_path)
    modules_text = (tmp_path / "modules.json").read_text(encoding="utf-8")
    assert "\n" not in modules_text
    assert loads_json(modules_text)["schema"] == "paradev.build.modules.v1"
    original_write_bytes = build_fs.AnchoredDirectory.write_bytes
    replaced: list[str] = []

    def track_write(self, relative_path, payload, *, replace=True):
        replaced.append(str(relative_path))
        return original_write_bytes(self, relative_path, payload, replace=replace)

    monkeypatch.setattr(build_fs.AnchoredDirectory, "write_bytes", track_write)

    written = write_manifests(result, tmp_path)

    assert replaced == []
    assert set(written) == {
        "artifacts.json",
        "assets.json",
        "collections.json",
        "dependencies.json",
        "diagnostics.json",
        "localization.json",
        "modules.json",
        "source-map.json",
        "sources.json",
        "sprites.json",
        "summary.json",
    }
    assert all(path == tmp_path / name for name, path in written.items())


def test_manifest_publication_cache_skips_exact_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = BuildResult.plan(project_id="cached_manifests", profile="hoi4")
    build_root = tmp_path / "build"
    cache_path = tmp_path / "cache/receipt.json"
    with build_fs.open_anchored_directory(build_root) as publication_root:
        build_manifest._write_manifests_anchored(
            result,
            publication_root,
            cache_path=cache_path,
            plan_signature="a" * 64,
        )

    def reject_projection(_result: BuildResult) -> dict[str, dict[str, object]]:
        raise AssertionError("exact published manifests were projected again")

    monkeypatch.setattr(build_manifest, "manifest_payloads", reject_projection)
    with build_fs.open_anchored_directory(build_root) as publication_root:
        written = build_manifest._write_manifests_anchored(
            result,
            publication_root,
            cache_path=cache_path,
            plan_signature="a" * 64,
        )

    assert set(written) == set(build_manifest.MANIFEST_SCHEMAS)


def test_manifest_publication_cache_repairs_changed_output(
    tmp_path: Path,
) -> None:
    result = BuildResult.plan(project_id="repaired_manifests", profile="hoi4")
    build_root = tmp_path / "build"
    cache_path = tmp_path / "cache/receipt.json"
    with build_fs.open_anchored_directory(build_root) as publication_root:
        build_manifest._write_manifests_anchored(
            result,
            publication_root,
            cache_path=cache_path,
            plan_signature="b" * 64,
        )
    expected = (build_root / "modules.json").read_bytes()
    (build_root / "modules.json").write_text('{"user":"changed"}', encoding="utf-8")

    with build_fs.open_anchored_directory(build_root) as publication_root:
        build_manifest._write_manifests_anchored(
            result,
            publication_root,
            cache_path=cache_path,
            plan_signature="b" * 64,
        )

    assert (build_root / "modules.json").read_bytes() == expected


def test_manifest_publication_cache_reprojects_for_a_changed_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = BuildResult.plan(project_id="changed_manifest_plan", profile="hoi4")
    build_root = tmp_path / "build"
    cache_path = tmp_path / "cache/receipt.json"
    with build_fs.open_anchored_directory(build_root) as publication_root:
        build_manifest._write_manifests_anchored(
            result,
            publication_root,
            cache_path=cache_path,
            plan_signature="e" * 64,
        )
    original_projection = build_manifest.manifest_payloads
    projections = 0

    def count_projection(value: BuildResult) -> dict[str, dict[str, object]]:
        nonlocal projections
        projections += 1
        return original_projection(value)

    monkeypatch.setattr(build_manifest, "manifest_payloads", count_projection)
    with build_fs.open_anchored_directory(build_root) as publication_root:
        build_manifest._write_manifests_anchored(
            result,
            publication_root,
            cache_path=cache_path,
            plan_signature="f" * 64,
        )

    assert projections == 1


def test_manifest_publication_cache_recovers_from_corruption(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    result = BuildResult.plan(project_id="corrupt_manifest_cache", profile="hoi4")
    build_root = tmp_path / "build"
    cache_path = tmp_path / "cache/receipt.json"
    with build_fs.open_anchored_directory(build_root) as publication_root:
        build_manifest._write_manifests_anchored(
            result,
            publication_root,
            cache_path=cache_path,
            plan_signature="c" * 64,
        )
    cache_path.write_text('{"schema":"broken"}', encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger=build_manifest.__name__):
        with build_fs.open_anchored_directory(build_root) as publication_root:
            build_manifest._write_manifests_anchored(
                result,
                publication_root,
                cache_path=cache_path,
                plan_signature="c" * 64,
            )

    assert "Ignoring invalid manifest publication cache" in caplog.text
    assert loads_json(cache_path.read_text(encoding="utf-8"))["schema"] == build_manifest.MANIFEST_PUBLICATION_CACHE_SCHEMA


def test_manifest_publication_cache_write_failure_is_non_blocking_and_observable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    result = BuildResult.plan(project_id="unwritable_manifest_cache", profile="hoi4")
    build_root = tmp_path / "build"

    def fail_write(*_args: object, **_kwargs: object) -> None:
        raise OSError("synthetic disk full")

    monkeypatch.setattr(build_manifest, "_write_manifest_publication_cache", fail_write)
    with caplog.at_level(logging.WARNING, logger=build_manifest.__name__):
        with build_fs.open_anchored_directory(build_root) as publication_root:
            written = build_manifest._write_manifests_anchored(
                result,
                publication_root,
                cache_path=tmp_path / "cache/receipt.json",
                plan_signature="d" * 64,
            )

    assert set(written) == set(build_manifest.MANIFEST_SCHEMAS)
    assert "Could not write manifest publication cache" in caplog.text
    assert "synthetic disk full" in caplog.text


def test_manifests_view_wraps_all_manifest_payloads() -> None:
    result = BuildResult.plan(project_id="view_project", profile="hoi4")

    payload = manifests_view(result)

    assert payload["schema"] == "paradev.build.manifests.v1"
    assert payload["project_id"] == "view_project"
    assert payload["profile"] == "hoi4"
    assert sorted(payload["manifests"]) == [
        "artifacts.json",
        "assets.json",
        "collections.json",
        "dependencies.json",
        "diagnostics.json",
        "localization.json",
        "modules.json",
        "source-map.json",
        "sources.json",
        "sprites.json",
        "summary.json",
    ]
    assert payload["manifests"]["summary.json"] == summary_view(result)
    assert all(manifest["project_id"] == "view_project" for manifest in payload["manifests"].values())


def test_sources_view_filters_source_inventory_and_rebuilds_index() -> None:
    bundle = ModuleSourceBundle(
        root="modules/idea/GER_industry_spirit",
        source_slots={"def": ("def.pdx",), "loc": ("main.loc",)},
        metadata={"object_id": "GER_industry_spirit"},
        pdx_sources=(
            PDXBlockSource(
                slot="def",
                path="def.pdx",
                block=PDXBlock.from_str("ideas = { GER_industry_spirit = { picture = GER_industry_spirit } }"),
            ),
        ),
        module_id="idea/GER_industry_spirit",
    )
    result = BuildResult.plan(project_id="view_project", profile="hoi4", modules=(bundle.to_module(family="idea"),))

    payload = sources_view(result, family="idea", slot="def", loader="pdx", status="loaded")

    assert payload == {
        "schema": "paradev.build.sources.v1",
        "project_id": "view_project",
        "profile": "hoi4",
        "sources": [
            {
                "owner_kind": "module",
                "module_id": "idea/GER_industry_spirit",
                "family": "idea",
                "root": "modules/idea/GER_industry_spirit",
                "slot": "def",
                "path": "modules/idea/GER_industry_spirit/def.pdx",
                "relative_path": "def.pdx",
                "loader": "pdx",
                "status": "loaded",
                "entry_count": 1,
            }
        ],
        "index": {"idea/GER_industry_spirit": {"def": [0]}},
    }


def test_artifacts_view_filters_by_contributing_module_and_collection() -> None:
    module = Module(
        module_id="event/GER_news",
        family="event",
        root="modules/event/GER_news",
        source_slots={"def": ("def.pdx",)},
        collection_id="germany",
    )
    result = BuildResult.plan(
        project_id="view_project",
        profile="hoi4",
        modules=(module,),
        artifacts=(
            Artifact(
                path="events/germany.txt",
                artifact_type="pdx",
                owner="collection:germany",
                inputs=("modules/event/GER_news/def.pdx",),
                metadata={"module_ids": ["event/GER_news"], "collection_id": "germany"},
            ),
            Artifact(
                path="descriptor.mod",
                artifact_type="mod_descriptor",
                owner="project:view_project",
            ),
        ),
    )

    payload = artifacts_view(result, artifact_type="pdx", module_id="event/GER_news", collection_id="germany")

    assert payload == {
        "schema": "paradev.build.artifacts.v1",
        "project_id": "view_project",
        "profile": "hoi4",
        "artifacts": [
            {
                "path": "events/germany.txt",
                "type": "pdx",
                "owner": "collection:germany",
                "inputs": ["modules/event/GER_news/def.pdx"],
                "mode": "plan",
                "target_root": "output",
                "metadata": {"module_ids": ["event/GER_news"], "collection_id": "germany"},
            }
        ],
        "index": {
            "path": {"events/germany.txt": [0]},
            "type": {"pdx": [0]},
            "owner": {"collection:germany": [0]},
            "target_root": {"output": [0]},
            "mode": {"plan": [0]},
            "module": {"event/GER_news": [0]},
            "collection": {"germany": [0]},
        },
    }


def test_diagnostics_view_matches_resolved_source_context() -> None:
    module = Module(
        module_id="focus/GER_sample",
        family="focus",
        root="modules/focus/GER_sample",
        source_slots={"loc": ("main.loc",)},
    )
    result = BuildResult.plan(
        project_id="view_project",
        profile="hoi4",
        modules=(module,),
        diagnostics=(
            Diagnostic(
                code="focus.missing_localization",
                message="Focus GER_sample missing localization key 'GER_sample_desc' for l_english.",
                module_id="focus/GER_sample",
                slot="loc",
                source_path="main.loc",
            ),
        ),
    )

    payload = diagnostics_view(
        result,
        family="focus",
        source_path="modules/focus/GER_sample/main.loc",
        slot="loc",
    )

    assert payload == {
        "schema": "paradev.build.diagnostics.v1",
        "project_id": "view_project",
        "profile": "hoi4",
        "diagnostics": [
            {
                "code": "focus.missing_localization",
                "message": "Focus GER_sample missing localization key 'GER_sample_desc' for l_english.",
                "severity": "error",
                "module_id": "focus/GER_sample",
                "slot": "loc",
                "source_path": "main.loc",
                "source": {
                    "path": "modules/focus/GER_sample/main.loc",
                    "module_id": "focus/GER_sample",
                    "family": "focus",
                    "slot": "loc",
                },
            }
        ],
        "index": {"error": {"focus.missing_localization": [0]}},
        "family_index": {"focus": {"error": {"focus.missing_localization": [0]}}},
    }
