from __future__ import annotations

import hashlib
import os
import shutil
import stat
import zipfile
from pathlib import Path

import pytest
from heavenbase.utils import dumps_json

from paradev.desktop.project_packages import (
    PROJECT_PACKAGE_CATALOG_SCHEMA,
    PROJECT_PACKAGE_INSTALL_SCHEMA,
    PROJECT_PACKAGE_PROVENANCE_SCHEMA,
    ProjectPackageError,
    _install_project_package,
    _load_project_package_catalog,
    desktop_install_project_package,
    desktop_project_package_catalog,
)
from paradev.version import __version__


def _zip_info(name: str, *, directory: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED if directory else zipfile.ZIP_DEFLATED
    info.external_attr = ((stat.S_IFDIR | 0o755) if directory else (stat.S_IFREG | 0o644)) << 16
    if directory:
        info.external_attr |= 0x10
    return info


def _write_package(
    root: Path,
    *,
    extra_member: tuple[str, bytes] | None = None,
    manifest_override: bytes | None = None,
) -> tuple[Path, Path]:
    top = "SAMPLE-1.2.3"
    source_files = {
        "paradev.yaml": (
            b"project_id: SAMPLE\n"
            b"title: Sample project\n"
            b"game: hoi4\n"
            b"mod_version: 1.2.3\n"
            b"source_roots:\n"
            b"  - src\n"
            b"output_root: build/mod\n"
            b"build_root: .paradev/.cache/build\n"
        ),
        "src/readme.txt": b"publisher-verified project\n",
    }
    if extra_member is not None:
        source_files[extra_member[0]] = extra_member[1]
    manifest = manifest_override or "".join(f"{hashlib.sha256(content).hexdigest()}  {name}\n" for name, content in sorted(source_files.items())).encode(
        "utf-8"
    )
    archive_path = root / "SAMPLE-1.2.3-project.zip"
    with zipfile.ZipFile(archive_path, "w", allowZip64=True) as archive:
        archive.writestr(_zip_info(f"{top}/", directory=True), b"")
        archive.writestr(_zip_info(f"{top}/src/", directory=True), b"")
        for name, content in sorted(source_files.items()):
            archive.writestr(_zip_info(f"{top}/{name}"), content)
        archive.writestr(_zip_info(f"{top}/SHA256SUMS"), manifest)

    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        row = {
            "id": "sample-1.2.3",
            "label": "Sample 1.2.3",
            "game": "hoi4",
            "archive_name": archive_path.name,
            "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
            "archive_size": archive_path.stat().st_size,
            "project_id": "SAMPLE",
            "project_version": "1.2.3",
            "top_level_folder": top,
            "entry_count": len(infos),
            "file_count": sum(not info.is_dir() for info in infos),
            "directory_count": sum(info.is_dir() for info in infos),
            "uncompressed_size": sum(info.file_size for info in infos),
            "compressed_size": sum(info.compress_size for info in infos),
            "max_member_path_code_units": max(len(info.filename.encode("utf-16-le")) // 2 for info in infos),
        }
    catalog_path = root / "project-packages.json"
    catalog_path.write_text(
        dumps_json(
            {
                "schema": PROJECT_PACKAGE_CATALOG_SCHEMA,
                "paradev_version": __version__,
                "desktop_version": "0.1.0-0",
                "packages": [row],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return archive_path, catalog_path


def _install(archive: Path, destination: Path, catalog: Path) -> dict[str, object]:
    return _install_project_package(
        archive,
        destination,
        catalog=_load_project_package_catalog(catalog),
    )


def test_project_package_catalog_loads_bundled_pihc3_release() -> None:
    catalog = desktop_project_package_catalog()

    assert catalog["schema"] == PROJECT_PACKAGE_CATALOG_SCHEMA
    assert catalog["paradev_version"] == __version__
    assert catalog["desktop_version"] == "0.1.0-0"
    assert catalog["packages"] == [
        {
            "id": "pihc3-0.2.3",
            "label": "PIHC3 0.2.3",
            "game": "hoi4",
            "archive_name": "PIHC3-0.2.3-project.zip",
            "archive_sha256": "87c8f75834ca3b32bdf5124e924a3013d8948ebb189615eeba88ee42f65ef01d",
            "archive_size": 1844557429,
            "project_id": "PIHC3",
            "project_version": "0.2.3",
            "top_level_folder": "PIHC3-0.2.3",
            "entry_count": 137566,
            "file_count": 79690,
            "directory_count": 57876,
            "uncompressed_size": 2764159173,
            "compressed_size": 1807896455,
            "max_member_path_code_units": 199,
        }
    ]


def test_project_package_install_is_transactional_and_reopens_managed_project(tmp_path: Path) -> None:
    archive, catalog = _write_package(tmp_path)
    destination = tmp_path / "projects"

    installed = _install(archive, destination, catalog)

    project_root = destination / "SAMPLE-1.2.3"
    assert installed["schema"] == PROJECT_PACKAGE_INSTALL_SCHEMA
    assert installed["status"] == "installed"
    assert installed["installed"] is True
    assert installed["project_root"] == str(project_root.resolve())
    assert installed["project"]["project_id"] == "SAMPLE"
    assert installed["project"]["version"] == "1.2.3"
    assert installed["project"]["root"] == str(project_root.resolve())
    assert installed["project"]["manifest"] == str((project_root / "paradev.yaml").resolve())
    assert (project_root / "src/readme.txt").read_text(encoding="utf-8") == "publisher-verified project\n"
    provenance = (project_root / ".paradev/release-package.json").read_text(encoding="utf-8")
    assert PROJECT_PACKAGE_PROVENANCE_SCHEMA in provenance
    assert not list(destination.glob(".p-*"))

    (project_root / "src/user-edit.txt").write_text("preserve me\n", encoding="utf-8")
    reopened = _install(archive, destination, catalog)

    assert reopened["status"] == "existing"
    assert reopened["installed"] is False
    assert (project_root / "src/user-edit.txt").read_text(encoding="utf-8") == "preserve me\n"


def test_project_package_install_defaults_to_user_documents_projects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    archive, catalog_path = _write_package(tmp_path)
    catalog = _load_project_package_catalog(catalog_path)
    destination = tmp_path / "home/Documents/ParaDev/Projects"
    monkeypatch.setattr(
        "paradev.desktop.project_packages.desktop_project_package_catalog",
        lambda: catalog,
    )
    monkeypatch.setattr(
        "paradev.desktop.project_packages._default_project_package_destination_root",
        lambda: destination,
    )

    installed = desktop_install_project_package(archive)

    assert installed["project_root"] == str((destination / "SAMPLE-1.2.3").resolve())


def test_project_package_install_rejects_unknown_bytes_without_publishing(tmp_path: Path) -> None:
    archive, catalog = _write_package(tmp_path)
    archive.write_bytes(archive.read_bytes() + b"tampered")
    destination = tmp_path / "projects"

    with pytest.raises(ProjectPackageError, match="does not match the publisher checksum"):
        _install(archive, destination, catalog)

    assert not (destination / "SAMPLE-1.2.3").exists()


def test_project_package_install_rejects_path_escape_even_when_cataloged(tmp_path: Path) -> None:
    archive, catalog = _write_package(tmp_path, extra_member=("../escape.txt", b"escape\n"))
    destination = tmp_path / "projects"

    with pytest.raises(ProjectPackageError, match="unsafe path"):
        _install(archive, destination, catalog)

    assert not (tmp_path / "escape.txt").exists()
    assert not (destination / "SAMPLE-1.2.3").exists()


def test_project_package_install_rejects_content_manifest_mismatch(tmp_path: Path) -> None:
    archive, catalog = _write_package(
        tmp_path,
        manifest_override=f"{'0' * 64}  paradev.yaml\n".encode(),
    )

    with pytest.raises(ProjectPackageError, match="content manifest does not match"):
        _install(archive, tmp_path / "projects", catalog)


def test_project_package_install_never_overwrites_unmanaged_folder(tmp_path: Path) -> None:
    archive, catalog = _write_package(tmp_path)
    project_root = tmp_path / "projects/SAMPLE-1.2.3"
    project_root.mkdir(parents=True)
    marker = project_root / "keep.txt"
    marker.write_text("keep\n", encoding="utf-8")

    with pytest.raises(ProjectPackageError, match="cannot prove it came from this package"):
        _install(archive, tmp_path / "projects", catalog)

    assert marker.read_text(encoding="utf-8") == "keep\n"


def test_project_package_catalog_rejects_another_backend_version(tmp_path: Path) -> None:
    _, catalog = _write_package(tmp_path)
    catalog.write_text(catalog.read_text(encoding="utf-8").replace(__version__, "9.9.9"), encoding="utf-8")

    with pytest.raises(ProjectPackageError, match="targets ParaDev 9.9.9"):
        _load_project_package_catalog(catalog)


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable-mode assertion")
def test_project_package_install_preserves_publisher_file_mode(tmp_path: Path) -> None:
    archive, catalog = _write_package(tmp_path)

    _install(archive, tmp_path / "projects", catalog)

    mode = stat.S_IMODE((tmp_path / "projects/SAMPLE-1.2.3/src/readme.txt").stat().st_mode)
    assert mode == 0o644


def test_project_package_install_accepts_browser_renamed_verified_archive(tmp_path: Path) -> None:
    archive, catalog = _write_package(tmp_path)
    renamed = archive.with_name("SAMPLE-1.2.3-project (1).zip")
    archive.rename(renamed)

    installed = _install(renamed, tmp_path / "projects", catalog)

    assert installed["status"] == "installed"
    assert installed["package"]["archive_name"] == "SAMPLE-1.2.3-project.zip"


def test_project_package_install_rejects_windows_reserved_component(tmp_path: Path) -> None:
    archive, catalog = _write_package(tmp_path, extra_member=("CON.txt", b"not portable\n"))

    with pytest.raises(ProjectPackageError, match="Windows-reserved"):
        _install(archive, tmp_path / "projects", catalog)


def test_project_package_install_reports_insufficient_disk_space(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    archive, catalog = _write_package(tmp_path)
    usage = shutil.disk_usage(tmp_path)
    monkeypatch.setattr(
        "paradev.desktop.project_packages.shutil.disk_usage",
        lambda _path: usage._replace(free=0),
    )

    with pytest.raises(ProjectPackageError, match="Free disk space"):
        _install(archive, tmp_path / "projects", catalog)
