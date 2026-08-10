"""Portable generated-artifact path policy contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from paradev.build import Artifact, BuildRegistry, BuildResult, PDXTextWriter, write_artifacts
from paradev.build import publication as build_publication


@pytest.mark.parametrize(
    ("artifact_path", "component"),
    (
        ("common/ideas/idea.txt.", "idea.txt."),
        ("common/ideas/idea.txt ", "idea.txt "),
        ("common/ideas/CON", "CON"),
        ("common/ideas/nul.txt", "nul.txt"),
        ("common/ideas/LPT1.backup", "LPT1.backup"),
        ("common/ideas/COM¹.txt", "COM¹.txt"),
        ("common/ideas/idea:alternate.txt", "idea:alternate.txt"),
        ("common/ideas/idea?.txt", "idea?.txt"),
        ("common/ideas/idea\x01.txt", "idea\x01.txt"),
        ("common/ideas/idea\x7f.txt", "idea\x7f.txt"),
    ),
)
def test_build_plan_blocks_windows_incompatible_artifact_components(
    artifact_path: str,
    component: str,
) -> None:
    artifact = Artifact(
        path=artifact_path,
        artifact_type="pdx",
        owner="module:idea/portable",
    )

    result = BuildResult.plan(project_id="portable", artifacts=(artifact,))

    assert result.blocked is True
    diagnostic = next(item for item in result.diagnostics if item.code == "build.invalid_artifact_path")
    assert diagnostic.artifact_path == artifact_path
    assert component in diagnostic.message
    assert "not portable to Windows" in diagnostic.message


@pytest.mark.parametrize(
    "artifact_path",
    (
        ".hidden/generated.txt",
        "common/ leading-space/idea+variant[1].txt",
        "common/ideas/COM10.txt",
        "common/ideas/LPT0.txt",
        "common/ideas/auxiliary.txt",
    ),
)
def test_build_plan_preserves_other_posix_artifact_names(artifact_path: str) -> None:
    artifact = Artifact(
        path=artifact_path,
        artifact_type="pdx",
        owner="module:idea/portable",
    )

    result = BuildResult.plan(project_id="portable", artifacts=(artifact,))

    assert not any(item.code == "build.invalid_artifact_path" for item in result.diagnostics)


@pytest.mark.parametrize(
    "artifact_path",
    (
        "common/ideas/PRN.txt",
        "common/ideas/alternate:name.txt",
        "common/ideas/name.",
    ),
)
def test_publication_rejects_windows_incompatible_paths_even_without_planning(
    artifact_path: str,
) -> None:
    result = BuildResult(
        project_id="portable",
        artifacts=(
            Artifact(
                path=artifact_path,
                artifact_type="pdx",
                owner="module:idea/portable",
            ),
        ),
    )

    with pytest.raises(ValueError, match="Windows-incompatible component"):
        build_publication.emitted_artifact_rows(result)


def test_publication_rejects_windows_incompatible_replacement_paths() -> None:
    result = BuildResult(
        project_id="portable",
        artifacts=(
            Artifact(
                path="common/ideas/current.txt",
                artifact_type="pdx",
                owner="module:idea/portable",
                metadata={
                    "publication_scope": "project",
                    "publication_replaces": ["common/ideas/NUL.txt"],
                },
            ),
        ),
    )

    with pytest.raises(ValueError, match="Windows-incompatible component"):
        build_publication.emitted_artifact_rows(result)


def test_direct_artifact_writer_rejects_windows_incompatible_path(
    tmp_path: Path,
) -> None:
    artifact = Artifact(
        path="common/ideas/idea:alternate.txt",
        artifact_type="pdx",
        owner="module:idea/portable",
        payload="ideas = {}",
    )
    result = BuildResult(project_id="portable", artifacts=(artifact,))
    registry = BuildRegistry().add(PDXTextWriter())

    with pytest.raises(ValueError, match="not portable to Windows"):
        write_artifacts(result, registry, tmp_path / "out")

    assert not (tmp_path / "out").exists()
