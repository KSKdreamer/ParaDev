from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from paradev.build import BuildContext, BuildResult, write_artifacts
from paradev.sdk import Project

pytestmark = pytest.mark.integration

PIHC3_ROOT = Path("projects/PIHC3").resolve()
MIO_ROOT = PIHC3_ROOT / "src/modules/military_industrial_organization"
RETIRED_MIO_ROOT = PIHC3_ROOT / "src/modules/military_industrial_organization_component"
EXPECTED_MODULES = {
    "ai_bonus_weights": "AI加成权重",
    "air_policies": "空军政策",
    "c01_airship_organization": "C01飞艇军工组织",
    "debug_organization": "调试军工组织",
    "general_policies": "通用政策",
    "generic_organizations": "通用军工组织",
    "land_policies": "陆军政策",
}
EXPECTED_PDX_PATHS = {
    "common/military_industrial_organization/ai_bonus_weights/ai_bonus_weights.txt",
    "common/military_industrial_organization/organizations/00_DEBUG_organization.txt",
    "common/military_industrial_organization/organizations/00_generic_organization.txt",
    "common/military_industrial_organization/organizations/C01.txt",
    "common/military_industrial_organization/policies/_air_policies.txt",
    "common/military_industrial_organization/policies/_general_policies.txt",
    "common/military_industrial_organization/policies/_land_policies.txt",
}
EXPECTED_SOURCE_DIGEST = "b871483cb075db73e37a0ee427fafdaffaa9b03ab117acbcc0eb6383a2e2cc87"
EXPECTED_EMITTED_DIGEST = "9868945b24f7079f8993d5de7ec16f6e3e06f517d576382c69a844262c73d789"
EXPECTED_PUBLISHED_DIGEST = "9a3649eeb2b6091fadd673822b9a868088be2bafbe029e66995e3435e01ad062"


def _module_roots() -> list[Path]:
    return [path for path in sorted(MIO_ROOT.iterdir(), key=lambda candidate: candidate.name) if path.is_dir() and not path.name.startswith(".")]


def _digest_rows(rows: list[tuple[str, bytes]]) -> tuple[int, int, str]:
    digest = hashlib.sha256()
    total = 0
    for key, payload in sorted(rows):
        key_bytes = key.encode()
        digest.update(len(key_bytes).to_bytes(8, "big"))
        digest.update(key_bytes)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
        total += len(payload)
    return len(rows), total, digest.hexdigest()


def test_pihc3_mio_family_owns_exact_nested_sources() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    family = registry.family("military_industrial_organization")
    slots = {
        slot.name: slot
        for slot in registry.source_slots_for(
            "military_industrial_organization",
        )
    }

    assert tuple(slots) == ("pdx", "loc")
    assert slots["pdx"].kind == "pdx"
    assert slots["pdx"].many is True
    assert slots["pdx"].required is True
    assert slots["loc"].kind == "loc"
    assert slots["loc"].match == "localization/*.loc"
    assert slots["loc"].many is True
    assert family.pdx_path_template == "{source_path}"
    assert family.loc_path_template == ("localisation/{language_folder}/" "MILITARY_INDUSTRIAL_ORGANIZATION_" "{source_stem}_{language}.yml")
    assert registry.publication_replacements_for("military_industrial_organization") == ()
    assert not hasattr(family, "retired_families")
    with pytest.raises(ValueError, match="not registered"):
        registry.family("military_industrial_organization_component")


def test_pihc3_mio_modules_are_minimal_portable_single_sources_of_truth() -> None:
    roots = _module_roots()

    assert {path.name.split(" - ", 1)[0] for path in roots} == set(EXPECTED_MODULES)
    assert not RETIRED_MIO_ROOT.exists()

    pdx_rows: list[tuple[str, bytes]] = []
    discovered_paths: set[str] = set()
    for module_root in roots:
        object_id, folder_title = module_root.name.split(" - ", 1)

        assert folder_title == EXPECTED_MODULES[object_id]
        assert not (module_root / "meta.yaml").exists()
        assert not (module_root / ".paradev").exists()
        assert not (module_root / "legacy").exists()

        pdx_paths = [
            path
            for path in module_root.glob(
                "common/military_industrial_organization/**/*.txt",
            )
            if path.is_file()
        ]
        assert len(pdx_paths) == 1
        relative_path = pdx_paths[0].relative_to(module_root).as_posix()
        discovered_paths.add(relative_path)
        pdx_rows.append((relative_path, pdx_paths[0].read_bytes()))

        loc_paths = list(module_root.glob("localization/*.loc"))
        if object_id == "ai_bonus_weights":
            assert loc_paths == []
        else:
            assert len(loc_paths) == 1
        assert not any(path.is_symlink() for path in module_root.rglob("*"))

    assert discovered_paths == EXPECTED_PDX_PATHS
    assert _digest_rows(pdx_rows) == (
        7,
        290_900,
        EXPECTED_SOURCE_DIGEST,
    )


def test_pihc3_mio_family_emits_byte_exact_preconsolidation_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    discovery = project.discover_modules(
        profile=project.game,
        registry=registry,
        strict_metadata=True,
        family="military_industrial_organization",
    )
    artifacts = tuple(
        registry.family("military_industrial_organization").emit(
            BuildContext(project_id="PIHC3"),
            discovery.modules,
            (),
        )
    )
    result = BuildResult.plan(
        "PIHC3",
        profile=project.game,
        modules=discovery.modules,
        artifacts=artifacts,
    )
    output_root = tmp_path / "out"
    written = write_artifacts(result, registry, output_root)
    rows = [(relative_path, (output_root / relative_path).read_bytes()) for relative_path in written]

    assert discovery.diagnostics == ()
    assert result.summary() == {
        "module_count": 7,
        "collection_count": 0,
        "dependency_count": 0,
        "artifact_count": 67,
        "diagnostic_count": 0,
        "error_count": 0,
        "blocked": False,
    }
    assert sum(path.startswith("common/military_industrial_organization/") for path in written) == 7
    assert sum(path.startswith("localisation/") for path in written) == 60
    assert _digest_rows(rows) == (
        67,
        589_966,
        EXPECTED_EMITTED_DIGEST,
    )

    monkeypatch.setenv("PIHC3_HOI4_GAME_ROOT", str(output_root))
    postprocessor = next(postprocessor for postprocessor in registry.postprocessors if postprocessor.postprocessor_id == "pihc3.localisation")
    published_artifacts = postprocessor.process(
        BuildContext(project_id="PIHC3"),
        artifacts,
    )
    published_result = BuildResult.plan(
        "PIHC3",
        profile=project.game,
        modules=discovery.modules,
        artifacts=published_artifacts,
    )
    published_root = tmp_path / "published"
    published = write_artifacts(
        published_result,
        registry,
        published_root,
    )
    published_rows = [(relative_path, (published_root / relative_path).read_bytes()) for relative_path in published]

    assert len(published) == 67
    assert (
        sum(
            path.startswith(
                "localisation/replace/",
            )
            for path in published
        )
        == 60
    )
    assert _digest_rows(published_rows) == (
        67,
        589_966,
        EXPECTED_PUBLISHED_DIGEST,
    )
