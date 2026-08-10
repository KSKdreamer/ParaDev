"""Deterministic ParaDev project archive packaging tests."""

# heaven-style-scan: standalone-control-plane

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "package_project.py"
PIHC3_ROOT = ROOT / "projects" / "PIHC3"


def _load_script() -> ModuleType:
    specification = importlib.util.spec_from_file_location("paradev_package_project", SCRIPT_PATH)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


PACKAGE_PROJECT = _load_script()


def _project(root: Path) -> Path:
    root.mkdir()
    (root / "paradev.yaml").write_text(
        "project_id: tiny_project\n"
        "title: Tiny Project\n"
        "game: hoi4\n"
        "source_roots:\n"
        "  - src\n"
        "build_root: .paradev/.cache/build\n"
        "mod_version: 1.2.3\n",
        encoding="utf-8",
    )
    (root / "src").mkdir()
    (root / "src" / "idea.txt").write_text("idea = { modifier = { political_power_gain = 0.02 } }\n", encoding="utf-8")
    (root / "tools").mkdir()
    script = root / "tools" / "compile.sh"
    script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    script.chmod(0o755)
    (root / "empty").mkdir()
    (root / ".gitignore").write_text(".paradev/\n", encoding="utf-8")
    return root


def _archive_payloads(archive: zipfile.ZipFile, folder: str) -> dict[str, bytes]:
    prefix = f"{folder}/"
    return {
        name[len(prefix) :]: archive.read(name)
        for name in archive.namelist()
        if name.startswith(prefix) and not name.endswith("/") and name != f"{prefix}{PACKAGE_PROJECT.ARCHIVE_MANIFEST_NAME}"
    }


@pytest.mark.unit
def test_project_archive_is_reproducible_sorted_and_self_verifying(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    first = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "first")
    for path in project.rglob("*"):
        if not path.is_symlink():
            os.utime(path, (1_900_000_000, 1_900_000_000))
    second = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "second")

    assert first.archive_path.name == "tiny_project-1.2.3-project.zip"
    assert first.top_level_folder == "tiny_project-1.2.3"
    assert first.archive_path.read_bytes() == second.archive_path.read_bytes()
    assert first.archive_sha256 == second.archive_sha256 == hashlib.sha256(first.archive_path.read_bytes()).hexdigest()
    assert first.max_windows_archive_member_path_length <= PACKAGE_PROJECT.WINDOWS_ARCHIVE_MEMBER_MAX_CODE_UNITS

    with zipfile.ZipFile(first.archive_path) as archive:
        names = archive.namelist()
        assert names == sorted(names)
        assert {name.split("/", 1)[0] for name in names} == {first.top_level_folder}
        assert max(PACKAGE_PROJECT._windows_path_length(name) for name in names) <= PACKAGE_PROJECT.WINDOWS_ARCHIVE_MEMBER_MAX_CODE_UNITS
        assert all(info.date_time == PACKAGE_PROJECT.FIXED_ZIP_TIMESTAMP for info in archive.infolist())
        assert all(info.extract_version >= 45 for info in archive.infolist() if not info.is_dir())

        payloads = _archive_payloads(archive, first.top_level_folder)
        manifest = archive.read(f"{first.top_level_folder}/{PACKAGE_PROJECT.ARCHIVE_MANIFEST_NAME}").decode("utf-8")
        expected_hashes = {name: digest for digest, name in (line.split("  ", 1) for line in manifest.splitlines())}
        assert expected_hashes == {name: hashlib.sha256(content).hexdigest() for name, content in payloads.items()}


@pytest.mark.unit
def test_project_archive_derives_deterministic_version_bound_catalog(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    result = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")

    catalog = PACKAGE_PROJECT.derive_project_package_catalog(
        result.archive_path,
        paradev_version="0.1.0.000dev",
        desktop_version="0.1.0-0",
    )

    with zipfile.ZipFile(result.archive_path) as archive:
        infos = archive.infolist()
    assert catalog == {
        "schema": PACKAGE_PROJECT.PROJECT_PACKAGE_CATALOG_SCHEMA,
        "paradev_version": "0.1.0.000dev",
        "desktop_version": "0.1.0-0",
        "packages": [
            {
                "id": "tiny_project-1.2.3",
                "label": "tiny_project 1.2.3",
                "game": "hoi4",
                "archive_name": result.archive_path.name,
                "archive_sha256": hashlib.sha256(result.archive_path.read_bytes()).hexdigest(),
                "archive_size": result.archive_path.stat().st_size,
                "project_id": "tiny_project",
                "project_version": "1.2.3",
                "top_level_folder": result.top_level_folder,
                "entry_count": len(infos),
                "file_count": sum(not info.is_dir() for info in infos),
                "directory_count": sum(info.is_dir() for info in infos),
                "uncompressed_size": sum(info.file_size for info in infos),
                "compressed_size": sum(info.compress_size for info in infos),
                "max_member_path_code_units": max(PACKAGE_PROJECT._windows_path_length(info.filename) for info in infos),
            }
        ],
    }


@pytest.mark.unit
def test_project_archive_catalog_check_is_non_mutating_and_allows_other_packages(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    result = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")
    catalog = PACKAGE_PROJECT.derive_project_package_catalog(
        result.archive_path,
        paradev_version="0.1.0.000dev",
        desktop_version="0.1.0-0",
    )
    other = dict(catalog["packages"][0])
    other.update(
        {
            "id": "other-9.9.9",
            "label": "Other 9.9.9",
            "archive_name": "Other-9.9.9-project.zip",
            "project_id": "Other",
            "project_version": "9.9.9",
            "top_level_folder": "Other-9.9.9",
        }
    )
    catalog["packages"].append(other)
    catalog_path = PACKAGE_PROJECT._write_project_package_catalog(catalog, tmp_path / "project-packages.json")
    second_catalog_path = PACKAGE_PROJECT._write_project_package_catalog(catalog, tmp_path / "project-packages-copy.json")
    assert second_catalog_path.read_bytes() == catalog_path.read_bytes()
    archive_before = result.archive_path.read_bytes()
    catalog_before = catalog_path.read_bytes()
    archive_mtime = result.archive_path.stat().st_mtime_ns
    catalog_mtime = catalog_path.stat().st_mtime_ns

    row = PACKAGE_PROJECT.check_project_package_catalog(
        result.archive_path,
        catalog_path,
        paradev_version="0.1.0.000dev",
        desktop_version="0.1.0-0",
    )

    assert row == catalog["packages"][0]
    assert result.archive_path.read_bytes() == archive_before
    assert catalog_path.read_bytes() == catalog_before
    assert result.archive_path.stat().st_mtime_ns == archive_mtime
    assert catalog_path.stat().st_mtime_ns == catalog_mtime


@pytest.mark.unit
def test_project_archive_catalog_check_reports_exact_row_drift(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    result = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")
    catalog = PACKAGE_PROJECT.derive_project_package_catalog(
        result.archive_path,
        paradev_version="0.1.0.000dev",
        desktop_version="0.1.0-0",
    )
    catalog["packages"][0]["archive_sha256"] = "0" * 64
    catalog_path = PACKAGE_PROJECT._write_project_package_catalog(catalog, tmp_path / "project-packages.json")

    with pytest.raises(
        PACKAGE_PROJECT.ProjectArchiveError,
        match="archive_sha256 expected .* found",
    ):
        PACKAGE_PROJECT.check_project_package_catalog(
            result.archive_path,
            catalog_path,
            paradev_version="0.1.0.000dev",
            desktop_version="0.1.0-0",
        )


@pytest.mark.unit
def test_project_archive_excludes_generated_metadata_and_tool_caches(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    excluded = {
        ".git/config": "git",
        ".paradev/.cache/build/state.json": "{}",
        ".pytest_cache/state": "pytest",
        ".mypy_cache/state": "mypy",
        "__pycache__/module.pyc": "bytecode",
        "src/ignored.pyc": "bytecode",
        ".DS_Store": "mac",
        "._thumbnail.png": "mac",
        "Thumbs.db": "windows",
        ".coverage": "coverage",
        ".venv/bin/python": "venv",
        "node_modules/package/index.js": "node",
    }
    for relative_path, content in excluded.items():
        path = project / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    result = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")

    with zipfile.ZipFile(result.archive_path) as archive:
        relative_names = {name.split("/", 1)[1] for name in archive.namelist()}
        assert ".gitignore" in relative_names
        assert not any(name == ".paradev/" or name.startswith(".paradev/") for name in relative_names)
        for excluded_path in excluded:
            assert excluded_path not in relative_names


@pytest.mark.unit
def test_project_archive_normalizes_file_and_directory_permissions(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")

    result = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")

    with zipfile.ZipFile(result.archive_path) as archive:
        folder = result.top_level_folder
        assert archive.getinfo(f"{folder}/").external_attr >> 16 & 0o777 == 0o755
        assert archive.getinfo(f"{folder}/empty/").external_attr >> 16 & 0o777 == 0o755
        assert archive.getinfo(f"{folder}/tools/compile.sh").external_attr >> 16 & 0o777 == 0o755
        assert archive.getinfo(f"{folder}/src/idea.txt").external_attr >> 16 & 0o777 == 0o644


@pytest.mark.unit
def test_project_archive_normalizes_only_legacy_module_title_suffixes(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    legacy_module = project / "src" / "modules" / "reward" / "REWARD_ID - 唔..."
    legacy_module.mkdir(parents=True)
    (legacy_module / "meta.yaml").write_text("type: reward\n", encoding="utf-8")

    result = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")

    assert result.normalized_directory_count == 1
    assert legacy_module.is_dir()
    with zipfile.ZipFile(result.archive_path) as archive:
        names = archive.namelist()
        portable_path = f"{result.top_level_folder}/src/modules/reward/REWARD_ID - 唔/meta.yaml"
        assert portable_path in names
        assert not any("REWARD_ID - 唔..." in name for name in names)
        manifest = archive.read(f"{result.top_level_folder}/{PACKAGE_PROJECT.ARCHIVE_MANIFEST_NAME}").decode("utf-8")
        assert "src/modules/reward/REWARD_ID - 唔/meta.yaml" in manifest


@pytest.mark.unit
def test_project_archive_rejects_module_title_normalization_collisions(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    family = project / "src" / "modules" / "reward"
    (family / "REWARD_ID - duplicate...").mkdir(parents=True)
    (family / "REWARD_ID - duplicate").mkdir()

    with pytest.raises(PACKAGE_PROJECT.ProjectArchiveError, match="collide.*after normalization"):
        PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")


@pytest.mark.unit
def test_project_archive_rejects_symlinks(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    try:
        (project / "linked.txt").symlink_to(project / "src" / "idea.txt")
    except OSError as exc:
        pytest.skip(f"symlinks are unavailable on this test host: {exc}")

    with pytest.raises(PACKAGE_PROJECT.ProjectArchiveError, match="unsupported symlink"):
        PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")

    assert not (tmp_path / "dist").exists()


@pytest.mark.unit
def test_project_archive_requires_manifest_and_portable_paths(tmp_path: Path) -> None:
    missing_manifest = tmp_path / "missing"
    missing_manifest.mkdir()
    with pytest.raises(PACKAGE_PROJECT.ProjectArchiveError, match="regular paradev.yaml"):
        PACKAGE_PROJECT.package_project(missing_manifest, output_dir=tmp_path / "dist")

    project = _project(tmp_path / "source")
    (project / "src" / "bad:name.txt").write_text("bad", encoding="utf-8")
    with pytest.raises(PACKAGE_PROJECT.ProjectArchiveError, match="not portable to Windows"):
        PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")


@pytest.mark.unit
def test_project_archive_rejects_members_over_documented_windows_path_budget(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    oversized_directory = project / "src" / ("x" * 220)
    oversized_directory.mkdir()
    (oversized_directory / "entry.txt").write_text("too deep", encoding="utf-8")

    with pytest.raises(
        PACKAGE_PROJECT.ProjectArchiveError,
        match="200-code-unit Windows portability budget",
    ):
        PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")

    assert not (tmp_path / "dist").exists()


@pytest.mark.integration
def test_pihc3_project_tree_fits_documented_windows_path_budget() -> None:
    identity = PACKAGE_PROJECT._project_identity(PIHC3_ROOT / "paradev.yaml")
    tree = PACKAGE_PROJECT._scan_project(PIHC3_ROOT)

    maximum_length = PACKAGE_PROJECT._validate_windows_path_budget(identity, tree)

    assert maximum_length <= PACKAGE_PROJECT.WINDOWS_ARCHIVE_MEMBER_MAX_CODE_UNITS
    assert not any(
        "SCRIPTED_LOCALISATION_COMPONENT_SCRIPTED_LOCALISATION_INVENTORY_ITEMS_4EP_C02_RABID_RHODODENDRONS_NEUTRALIZER" in item.relative_path.as_posix()
        for item in tree.files
    )
    assert any("SCRIPTED_LOC_C02_RHODODENDRONS_SWITCH" in item.relative_path.as_posix() for item in tree.files)


@pytest.mark.unit
def test_project_archive_help_declares_release_defaults() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "projects/PIHC3" in result.stdout
    assert "dist/projects" in result.stdout
    assert "--catalog-output" in result.stdout
    assert "--check-catalog [PATH]" in result.stdout
    assert "src/paradev/resources/release/project-packages.json" in result.stdout


@pytest.mark.unit
def test_project_archive_cli_packages_a_selected_project(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    output = tmp_path / "dist"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(project), "--output-dir", str(output)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    archive = output / "tiny_project-1.2.3-project.zip"
    assert result.returncode == 0
    assert f"archive: {archive}" in result.stdout
    assert "sha256: " in result.stdout
    assert "portable folder normalizations: 0" in result.stdout
    assert "Windows archive member path budget:" in result.stdout
    assert "58 code units reserved for the extraction destination" in result.stdout
    assert archive.is_file()


@pytest.mark.unit
def test_project_archive_cli_generates_and_checks_catalog_without_repackaging(tmp_path: Path) -> None:
    project = _project(tmp_path / "source")
    packaged = PACKAGE_PROJECT.package_project(project, output_dir=tmp_path / "dist")
    catalog_path = tmp_path / "project-packages.json"

    generated = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--archive",
            str(packaged.archive_path),
            "--catalog-output",
            str(catalog_path),
            "--paradev-version",
            "0.1.0.000dev",
            "--desktop-version",
            "0.1.0-0",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert generated.returncode == 0
    assert f"catalog: {catalog_path}" in generated.stdout
    assert PACKAGE_PROJECT.loads_json(catalog_path.read_text(encoding="utf-8")) == PACKAGE_PROJECT.derive_project_package_catalog(
        packaged.archive_path,
        paradev_version="0.1.0.000dev",
        desktop_version="0.1.0-0",
    )
    archive_before = packaged.archive_path.read_bytes()
    catalog_before = catalog_path.read_bytes()
    archive_mtime = packaged.archive_path.stat().st_mtime_ns
    catalog_mtime = catalog_path.stat().st_mtime_ns

    checked = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--archive",
            str(packaged.archive_path),
            "--check-catalog",
            str(catalog_path),
            "--paradev-version",
            "0.1.0.000dev",
            "--desktop-version",
            "0.1.0-0",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert checked.returncode == 0
    assert f"catalog check: {catalog_path}" in checked.stdout
    assert "package: tiny_project-1.2.3" in checked.stdout
    assert packaged.archive_path.read_bytes() == archive_before
    assert catalog_path.read_bytes() == catalog_before
    assert packaged.archive_path.stat().st_mtime_ns == archive_mtime
    assert catalog_path.stat().st_mtime_ns == catalog_mtime
