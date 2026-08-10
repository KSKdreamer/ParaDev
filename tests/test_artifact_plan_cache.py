from __future__ import annotations

import gzip
import json
import logging
from pathlib import Path

import pytest

from paradev.build import (
    Artifact,
    BuildRegistry,
    BuildResult,
    Diagnostic,
    LocalizationEntry,
    Module,
    PDXTextWriter,
    SpriteGFXWriter,
    SpriteType,
)
from paradev.build import artifact_cache
import paradev.build.plan as build_plan
from paradev.pdx import PDXBlock
from paradev.sdk import Project


def _write_project(root: Path) -> Project:
    module_root = root / "src/modules/focus/TEST_FOCUS"
    module_root.mkdir(parents=True)
    (module_root / "def.txt").write_text(
        "focus = { id = TEST_FOCUS x = 1 }\n",
        encoding="utf-8",
    )
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: artifact_cache_project",
                "title: Artifact Cache Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return Project.load(root)


def _cache_result() -> BuildResult:
    module = Module(
        module_id="focus/TEST_FOCUS",
        family="focus",
        root="/project/src/modules/focus/TEST_FOCUS",
        metadata={"title": "Test Focus"},
    )
    return BuildResult.plan(
        "cache_test",
        profile="hoi4",
        modules=(module,),
        artifacts=(
            Artifact(
                path="common/test.txt",
                artifact_type="pdx",
                owner="module:focus/TEST_FOCUS",
                payload=PDXBlock.from_str("focus = { id = TEST_FOCUS }"),
            ),
            Artifact(
                path="localisation/test.yml",
                artifact_type="project_loc",
                owner="project:cache_test",
                payload=b'l_english:\n TEST_FOCUS:0 "Test"\n',
            ),
            Artifact(
                path="interface/test.gfx",
                artifact_type="sprite_gfx",
                owner="module:focus/TEST_FOCUS",
                payload=(
                    SpriteType(
                        name="GFX_TEST_FOCUS",
                        texturefile="gfx/interface/test.dds",
                        properties={"noOfFrames": 1},
                    ),
                ),
            ),
            Artifact(
                path="localisation/raw.yml",
                artifact_type="loc",
                owner="module:focus/TEST_FOCUS",
                payload=(
                    LocalizationEntry(
                        key="TEST_FOCUS",
                        language="l_english",
                        text="Test",
                        source_path="main.loc",
                        module_id="focus/TEST_FOCUS",
                    ),
                ),
            ),
        ),
        diagnostics=(
            Diagnostic(
                code="cache.notice",
                message="Cache fixture diagnostic.",
                severity="warning",
            ),
        ),
    )


def _cache_call(
    tmp_path: Path,
    *,
    builder,
    read: bool = True,
    write: bool = True,
) -> artifact_cache.CachedArtifactPlan:
    return artifact_cache.cached_artifact_plan(
        tmp_path / "artifact-plans",
        project_id="cache_test",
        project_root=tmp_path,
        profile="hoi4",
        emit_artifacts=True,
        signature="a" * 64,
        source_modules=_cache_result().modules,
        source_collections=_cache_result().collections,
        read=read,
        write=write,
        builder=builder,
    )


def test_artifact_plan_cache_round_trips_supported_writer_payloads(
    tmp_path: Path,
) -> None:
    result = _cache_result()
    cold = _cache_call(tmp_path, builder=lambda: result)

    def reject_rebuild() -> BuildResult:
        raise AssertionError("cache hit rebuilt the artifact plan")

    warm = _cache_call(tmp_path, builder=reject_rebuild)

    assert cold.status == "miss"
    assert warm.status == "hit"
    assert cold.signature == "a" * 64
    assert warm.signature == "a" * 64
    assert warm.result.to_dict() == result.to_dict()
    assert warm.result.artifacts[0].payload == result.artifacts[0].payload.to_str()
    assert warm.result.artifacts[1].payload == result.artifacts[1].payload
    assert warm.result.artifacts[2].payload == result.artifacts[2].payload
    assert warm.result.artifacts[3].payload == result.artifacts[3].payload


def test_artifact_plan_cache_recovers_from_unknown_payload_kind(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    result = _cache_result()
    _cache_call(tmp_path, builder=lambda: result)
    cache_file = next((tmp_path / "artifact-plans").glob("*.json.gz"))
    document = json.loads(gzip.decompress(cache_file.read_bytes()))
    document["payload"]["artifacts"][0]["payload"]["kind"] = "unknown"
    document["payload_sha256"] = artifact_cache._json_digest(document["payload"])
    cache_file.write_bytes(
        gzip.compress(
            json.dumps(document, separators=(",", ":")).encode("utf-8"),
            compresslevel=1,
            mtime=0,
        )
    )
    builds = 0

    def rebuild() -> BuildResult:
        nonlocal builds
        builds += 1
        return result

    with caplog.at_level(logging.WARNING, logger=artifact_cache.__name__):
        recovered = _cache_call(tmp_path, builder=rebuild)

    assert recovered.status == "refresh"
    assert builds == 1
    assert "Ignoring invalid artifact plan cache" in caplog.text
    assert "ValueError" in caplog.text


def test_artifact_plan_cache_write_failure_is_non_blocking_and_observable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    result = _cache_result()

    def fail_write(_path: Path, _document: object) -> None:
        raise OSError("synthetic disk full")

    monkeypatch.setattr(artifact_cache, "_write_cache", fail_write)
    with caplog.at_level(logging.WARNING, logger=artifact_cache.__name__):
        cached = _cache_call(tmp_path, builder=lambda: result)

    assert cached.result is result
    assert cached.status == "miss"
    assert "Could not write artifact plan cache" in caplog.text
    assert "synthetic disk full" in caplog.text


def test_artifact_plan_signature_tracks_registry_component_code(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    component = tmp_path / "component.py"
    component.write_text("VERSION = 1\n", encoding="utf-8")
    registry = BuildRegistry().add(PDXTextWriter()).add(SpriteGFXWriter())
    monkeypatch.setattr(artifact_cache, "getsourcefile", lambda _item: str(component))
    artifact_cache._cache_engine_fingerprint.cache_clear()
    try:
        first = artifact_cache.artifact_plan_signature(
            project_id="cache_test",
            profile="hoi4",
            metadata={"emit_artifacts": True},
            module_cache_signature="a" * 64,
            collection_cache_signature="b" * 64,
            copy_artifacts=(),
            copy_diagnostics=(),
            registry=registry,
        )
        component.write_text("VERSION = 2\n", encoding="utf-8")
        second = artifact_cache.artifact_plan_signature(
            project_id="cache_test",
            profile="hoi4",
            metadata={"emit_artifacts": True},
            module_cache_signature="a" * 64,
            collection_cache_signature="b" * 64,
            copy_artifacts=(),
            copy_diagnostics=(),
            registry=registry,
        )
    finally:
        artifact_cache._cache_engine_fingerprint.cache_clear()

    assert first != second


def test_artifact_plan_signature_requires_postprocessor_external_input_key(
    tmp_path: Path,
) -> None:
    class Postprocessor:
        postprocessor_id = "external"

        def process(
            self,
            _ctx: object,
            artifacts: tuple[Artifact, ...],
        ) -> tuple[Artifact, ...]:
            return artifacts

    registry = BuildRegistry().add(PDXTextWriter()).add(Postprocessor())

    signature = artifact_cache.artifact_plan_signature(
        project_id="cache_test",
        profile="hoi4",
        metadata={"root": str(tmp_path)},
        module_cache_signature="a" * 64,
        collection_cache_signature="b" * 64,
        copy_artifacts=(),
        copy_diagnostics=(),
        registry=registry,
    )

    assert signature is None


def test_artifact_plan_cache_replans_once_when_external_signature_changes(
    tmp_path: Path,
) -> None:
    signatures = iter(("a" * 64, "b" * 64, "b" * 64))
    builds = 0

    def signature() -> str:
        return next(signatures)

    def build() -> BuildResult:
        nonlocal builds
        builds += 1
        return _cache_result()

    cached = artifact_cache.cached_artifact_plan(
        tmp_path / "artifact-plans",
        project_id="cache_test",
        project_root=tmp_path,
        profile="hoi4",
        emit_artifacts=True,
        signature=signature,
        source_modules=_cache_result().modules,
        source_collections=(),
        read=True,
        write=True,
        builder=build,
    )

    assert cached.status == "refresh"
    assert cached.signature == "b" * 64
    assert builds == 2


def test_artifact_plan_cache_rejects_repeated_external_input_changes(
    tmp_path: Path,
) -> None:
    signatures = iter(("a" * 64, "b" * 64, "c" * 64))
    builds = 0

    def signature() -> str:
        return next(signatures)

    def build() -> BuildResult:
        nonlocal builds
        builds += 1
        return _cache_result()

    with pytest.raises(RuntimeError, match="changed repeatedly while planning"):
        artifact_cache.cached_artifact_plan(
            tmp_path / "artifact-plans",
            project_id="cache_test",
            project_root=tmp_path,
            profile="hoi4",
            emit_artifacts=True,
            signature=signature,
            source_modules=_cache_result().modules,
            source_collections=(),
            read=True,
            write=True,
            builder=build,
        )

    assert builds == 2


def test_project_cached_build_reuses_validated_artifact_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    cold = project.build()

    def reject_plan(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("artifact plan cache hit replanned build families")

    monkeypatch.setattr(build_plan, "_plan_build_draft", reject_plan)
    events: list[dict[str, object]] = []
    warm = Project.load(tmp_path).build(progress=events.append)

    assert warm.to_dict() == cold.to_dict()
    cached_event = next(event for event in events if event["phase"] == "artifact_generation")
    assert cached_event["counts"] == {
        "artifact_plan_cache_hits": 1,
        "artifacts": len(warm.artifacts),
    }


def test_project_cached_build_reuses_exact_published_manifests(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import paradev.build.manifest as build_manifest

    project = _write_project(tmp_path)
    project.build(
        emit_artifacts=True,
        emit_manifests=True,
        sync_launcher_descriptor=False,
    )

    def reject_projection(_result: BuildResult) -> dict[str, dict[str, object]]:
        raise AssertionError("exact cached manifests were projected again")

    monkeypatch.setattr(build_manifest, "manifest_payloads", reject_projection)
    warm = Project.load(tmp_path).build(
        emit_artifacts=True,
        emit_manifests=True,
        sync_launcher_descriptor=False,
    )

    assert warm.blocked is False


def test_project_artifact_plan_cache_refreshes_after_source_edit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    project.build()
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    source.write_text(
        "focus = { id = TEST_FOCUS x = 2 }\n",
        encoding="utf-8",
    )
    original = build_plan._plan_build_draft
    calls = 0

    def record_plan(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(build_plan, "_plan_build_draft", record_plan)
    refreshed = Project.load(tmp_path).build()

    assert calls == 1
    artifact = next(item for item in refreshed.artifacts if str(item.path).endswith("TEST_FOCUS.txt"))
    assert "x = 2" in artifact.payload.to_str()


def test_project_full_build_bypasses_artifact_plan_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    project.build()
    original = build_plan._plan_build_draft
    calls = 0

    def record_plan(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(build_plan, "_plan_build_draft", record_plan)
    rebuilt = Project.load(tmp_path).build(full_rebuild=True)

    assert calls == 1
    assert rebuilt.blocked is False


def test_project_cached_artifact_plan_publishes_byte_identical_pdx(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    cold = project.build(
        emit_artifacts=True,
        sync_launcher_descriptor=False,
    )
    output = project.output_root / "common/national_focus/TEST_FOCUS.txt"
    cold_bytes = output.read_bytes()

    def reject_plan(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("cached emitted build replanned families")

    monkeypatch.setattr(build_plan, "_plan_build_draft", reject_plan)
    warm = Project.load(tmp_path).build(
        emit_artifacts=True,
        sync_launcher_descriptor=False,
    )

    assert cold.blocked is False
    assert warm.blocked is False
    assert output.read_bytes() == cold_bytes
