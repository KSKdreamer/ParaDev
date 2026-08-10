from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
pytestmark = pytest.mark.integration

PIHC3_ROOT = Path(os.environ.get("PARADEV_PIHC3_ROOT", "projects/PIHC3")).expanduser().resolve()


def test_pihc3_intelligence_agency_family_owns_definition_preview_and_assets() -> None:
    from paradev.sdk import Project

    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    slots = registry.source_slots_for("intelligence_agency")
    by_name = {slot.name: slot for slot in slots}
    compiled_assets = [slot for slot in slots if slot.name == "compiled_assets"]
    family = registry.family("intelligence_agency")

    assert tuple(by_name) == ("def", "loc", "preview", "compiled_assets")
    assert by_name["def"].kind == "pdx"
    assert by_name["def"].match == "def.txt"
    assert by_name["def"].required is True
    assert by_name["loc"].kind == "loc"
    assert by_name["loc"].match == "**/*.loc"
    assert by_name["loc"].many is True
    assert by_name["preview"].kind is None
    assert by_name["preview"].match == r"^icon\.(png|dds|tga)$"
    assert len(compiled_assets) == 2
    assert all(slot.kind == "copy" for slot in compiled_assets)
    assert all(slot.many is True for slot in compiled_assets)
    assert all(slot.required is False for slot in compiled_assets)
    assert {slot.match for slot in compiled_assets} == {
        r"^interface/intelligence_agencies/.*\.gfx$",
        r"^gfx/interface/intelligence_agencies/.*\.dds$",
    }
    assert {slot.authoring_path for slot in compiled_assets} == {
        "interface/intelligence_agencies/{filename}",
        "gfx/interface/intelligence_agencies/{filename}",
    }
    assert family.pdx_path_template == "common/intelligence_agencies/{object_id}.txt"
    assert family.copy_path_template == "{source_path}"

    with pytest.raises(ValueError, match="is not registered"):
        registry.family("intelligence_agency_component")
    with pytest.raises(ValueError, match="is not registered"):
        registry.family("intelligence_agency_asset_component")


def test_pihc3_intelligence_agency_modules_are_single_source_of_truth() -> None:
    modules_root = PIHC3_ROOT / "src/modules/intelligence_agency"
    expected_previews = {
        "INTEL_AGENCY_BOC": False,
        "INTEL_AGENCY_CECIA": True,
        "INTEL_AGENCY_DDDPPPWWWHHH": True,
        "INTEL_AGENCY_DEFAULT": False,
        "INTEL_AGENCY_EEMO": True,
        "INTEL_AGENCY_EOF": True,
        "INTEL_AGENCY_LFCC": True,
        "INTEL_AGENCY_MNS": True,
        "INTEL_AGENCY_SEPAL": True,
    }
    module_roots = sorted(path for path in modules_root.iterdir() if path.is_dir())
    owned_assets: set[str] = set()

    assert len(module_roots) == 9
    assert {path.name.split(" - ", 1)[0] for path in module_roots} == set(expected_previews)
    for module_root in module_roots:
        object_id, folder_title = module_root.name.split(" - ", 1)
        expected_assets = [
            f"interface/intelligence_agencies/{object_id}.gfx",
            f"gfx/interface/intelligence_agencies/{object_id}.dds",
        ]

        assert folder_title
        assert not (module_root / "meta.yaml").exists()
        assert not (module_root / ".paradev").exists()
        assert not (module_root / "legacy").exists()
        assert (module_root / "icon.png").is_file() is expected_previews[object_id]
        for relative_path in expected_assets:
            assert relative_path not in owned_assets
            owned_assets.add(relative_path)
            assert (module_root / relative_path).is_file()

    assert len(owned_assets) == 18
    assert not (PIHC3_ROOT / "src/modules/intelligence_agency_component").exists()
    assert not (PIHC3_ROOT / "src/modules/intelligence_agency_asset_component").exists()


def test_pihc3_intelligence_agency_sources_match_reviewed_digest() -> None:
    modules_root = PIHC3_ROOT / "src/modules/intelligence_agency"
    rows: list[str] = []
    for module_root in sorted(modules_root.iterdir()):
        for path in sorted(candidate for candidate in module_root.rglob("*") if candidate.is_file()):
            rows.append(f"{module_root.name}\0" f"{path.relative_to(module_root).as_posix()}\0" f"{hashlib.sha256(path.read_bytes()).hexdigest()}")

    assert len(rows) == 43
    assert hashlib.sha256("\n".join(rows).encode()).hexdigest() == "7849fa8dd589438f52507878d9df063d1af01afe6dc7e69080b76ef1c796ce21"
    boc_dds = modules_root / "INTEL_AGENCY_BOC - 水晶之锋" / "gfx/interface/intelligence_agencies/INTEL_AGENCY_BOC.dds"
    assert hashlib.sha256(boc_dds.read_bytes()).hexdigest() == "ea173fa6ec92c03a5a5856835bc0c7d8547d50fe3c9cb739039bdf3b9ac5ccff"


@pytest.mark.slow
def test_pihc3_intelligence_agency_family_owns_exact_runtime_footprint() -> None:
    from paradev.sdk import Project

    project = Project.load(PIHC3_ROOT)
    result = project.build(family="intelligence_agency", strict_metadata=True)
    artifacts = [artifact for artifact in result.artifacts if artifact.owner.startswith("module:intelligence_agency/")]
    paths = {str(artifact.path) for artifact in artifacts}

    assert len(artifacts) == 45
    assert len(paths) == 45
    assert "common/intelligence_agencies/00_intelligence_agencies.txt" not in paths
    assert not any(path.startswith("gfx/interface/intelligence_agencies/") and path.endswith(".png") for path in paths)
    for object_id in (
        "INTEL_AGENCY_BOC",
        "INTEL_AGENCY_CECIA",
        "INTEL_AGENCY_DDDPPPWWWHHH",
        "INTEL_AGENCY_DEFAULT",
        "INTEL_AGENCY_EEMO",
        "INTEL_AGENCY_EOF",
        "INTEL_AGENCY_LFCC",
        "INTEL_AGENCY_MNS",
        "INTEL_AGENCY_SEPAL",
    ):
        owner = f"module:intelligence_agency/{object_id}"
        assert {str(artifact.path) for artifact in artifacts if artifact.owner == owner} == {
            f"common/intelligence_agencies/{object_id}.txt",
            f"localisation/english/{object_id}_l_english.yml",
            f"localisation/simp_chinese/{object_id}_l_simp_chinese.yml",
            f"interface/intelligence_agencies/{object_id}.gfx",
            f"gfx/interface/intelligence_agencies/{object_id}.dds",
        }
    assert not result.diagnostics
