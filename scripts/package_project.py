#!/usr/bin/env python3
"""Create a deterministic, portable ParaDev project archive."""

# heaven-style-scan: standalone-control-plane

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import tempfile
import unicodedata
import zipfile
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import chain
from pathlib import Path, PurePosixPath
from typing import BinaryIO, TypedDict

from heavenbase.utils import dumps_json, loads_json, loads_yaml
from yaml import YAMLError

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT_ROOT = ROOT / "projects" / "PIHC3"
DEFAULT_OUTPUT_DIR = ROOT / "dist" / "projects"
DEFAULT_PROJECT_PACKAGE_CATALOG = ROOT / "src" / "paradev" / "resources" / "release" / "project-packages.json"

ARCHIVE_MANIFEST_NAME = "SHA256SUMS"
PROJECT_PACKAGE_CATALOG_SCHEMA = "paradev.release.project-package-catalog.v1"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
READ_CHUNK_SIZE = 1024 * 1024
PROJECT_MANIFEST_MAX_BYTES = 32 * 1024 * 1024
WINDOWS_MAX_PATH_CODE_UNITS = 260
WINDOWS_ARCHIVE_MEMBER_MAX_CODE_UNITS = 200
WINDOWS_EXTRACTION_PREFIX_HEADROOM = WINDOWS_MAX_PATH_CODE_UNITS - 1 - 1 - WINDOWS_ARCHIVE_MEMBER_MAX_CODE_UNITS

_EXCLUDED_DIRECTORY_NAMES = frozenset(
    {
        ".cache",
        ".eggs",
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".nox",
        ".paradev",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__macosx",
        "__pycache__",
        "htmlcov",
        "node_modules",
    }
)
_EXCLUDED_FILE_NAMES = frozenset({".coverage", ".ds_store", "desktop.ini", "thumbs.db"})
_EXCLUDED_FILE_SUFFIXES = frozenset({".pyc", ".pyo"})
_WINDOWS_INVALID_CHARACTERS = frozenset('<>:"/\\|?*')
_WINDOWS_RESERVED_NAMES = frozenset(
    {
        "AUX",
        "CON",
        "NUL",
        "PRN",
        *(f"COM{number}" for number in range(1, 10)),
        *(f"LPT{number}" for number in range(1, 10)),
    }
)


class ProjectArchiveError(ValueError):
    """Raised when a project archive or release catalog is invalid."""


class ProjectPackageCatalogRow(TypedDict):
    """One deterministic project-package release row."""

    id: str
    label: str
    game: str
    archive_name: str
    archive_sha256: str
    archive_size: int
    project_id: str
    project_version: str
    top_level_folder: str
    entry_count: int
    file_count: int
    directory_count: int
    uncompressed_size: int
    compressed_size: int
    max_member_path_code_units: int


class ProjectPackageCatalog(TypedDict):
    """Version-bound project-package catalog emitted for one archive."""

    schema: str
    paradev_version: str
    desktop_version: str
    packages: list[ProjectPackageCatalogRow]


@dataclass(frozen=True)
class ProjectIdentity:
    """Names that identify one packaged project release."""

    project_id: str
    version: str
    folder_name: str
    archive_name: str


@dataclass(frozen=True)
class ProjectArchiveObservation:
    """Immutable release facts observed from one completed project archive."""

    archive_path: Path
    archive_sha256: str
    archive_size: int
    identity: ProjectIdentity
    game: str
    entry_count: int
    file_count: int
    directory_count: int
    uncompressed_size: int
    compressed_size: int
    max_member_path_code_units: int


@dataclass(frozen=True)
class SourceFile:
    """One immutable source-file observation used by the archive pass."""

    path: Path
    source_relative_path: PurePosixPath
    relative_path: PurePosixPath
    size: int
    executable: bool
    sha256: str
    stat_identity: tuple[int, int, int, int, int]


@dataclass(frozen=True)
class SourcePath:
    """One source file selected by the portable project-tree scan."""

    path: Path
    source_relative_path: PurePosixPath
    relative_path: PurePosixPath


@dataclass(frozen=True)
class SourceDirectory:
    """One source directory and its normalized archive path."""

    source_relative_path: PurePosixPath
    relative_path: PurePosixPath


@dataclass(frozen=True)
class ProjectTree:
    """The lightweight portable project-tree selection."""

    directories: tuple[SourceDirectory, ...]
    files: tuple[SourcePath, ...]


@dataclass(frozen=True)
class ProjectInventory:
    """The deterministic directories and files selected from a project."""

    directories: tuple[SourceDirectory, ...]
    files: tuple[SourceFile, ...]


@dataclass(frozen=True)
class ProjectArchive:
    """Result of packaging one ParaDev project."""

    archive_path: Path
    archive_sha256: str
    project_id: str
    version: str
    top_level_folder: str
    file_count: int
    normalized_directory_count: int
    max_windows_archive_member_path_length: int


def _portable_label(value: str, *, field: str) -> str:
    normalized = unicodedata.normalize("NFC", value.strip())
    parts: list[str] = []
    separator_pending = False
    for character in normalized:
        if character.isalnum() or character in "._-":
            if separator_pending and parts and parts[-1] != "-":
                parts.append("-")
            parts.append(character)
            separator_pending = False
        else:
            separator_pending = True
    label = "".join(parts).strip(" .-_")
    if not label:
        raise ProjectArchiveError(f"paradev.yaml {field!r} cannot form a portable archive name")
    if len(label.encode("utf-8")) > 100:
        raise ProjectArchiveError(f"paradev.yaml {field!r} is too long for a portable archive name")
    if label.split(".", 1)[0].upper() in _WINDOWS_RESERVED_NAMES:
        label = f"project-{label}"
    return label


def _project_identity(manifest_path: Path) -> ProjectIdentity:
    try:
        manifest = loads_yaml(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, YAMLError) as exc:
        raise ProjectArchiveError(f"could not read {manifest_path}: {exc}") from exc
    return _project_identity_from_manifest(manifest, manifest_path)


def _project_identity_from_manifest(manifest: object, source: object) -> ProjectIdentity:
    if not isinstance(manifest, Mapping):
        raise ProjectArchiveError(f"{source} must contain a YAML mapping")

    project_id = manifest.get("project_id")
    if not isinstance(project_id, str) or not project_id.strip():
        raise ProjectArchiveError(f"{source} must define a non-empty string project_id")
    raw_version = manifest.get("mod_version")
    if isinstance(raw_version, (Mapping, list, tuple, set, bool)):
        raise ProjectArchiveError(f"{source} mod_version must be a scalar value")
    version = "unversioned" if raw_version is None else str(raw_version).strip()
    if not version:
        raise ProjectArchiveError(f"{source} mod_version cannot be empty")

    project_label = _portable_label(project_id, field="project_id")
    version_label = _portable_label(version, field="mod_version")
    folder_name = f"{project_label}-{version_label}"
    return ProjectIdentity(
        project_id=project_id.strip(),
        version=version,
        folder_name=folder_name,
        archive_name=f"{folder_name}-project.zip",
    )


def _is_excluded(name: str, *, directory: bool) -> bool:
    folded = name.casefold()
    if directory and (folded in _EXCLUDED_DIRECTORY_NAMES or folded.endswith(".egg-info")):
        return True
    if not directory:
        if folded in _EXCLUDED_FILE_NAMES or folded.startswith("._"):
            return True
        if Path(folded).suffix in _EXCLUDED_FILE_SUFFIXES:
            return True
        if folded in {".git", ".paradev"}:
            return True
    return False


def _validate_member_component(name: str, relative_path: PurePosixPath) -> None:
    if not name or name in {".", ".."}:
        raise ProjectArchiveError(f"project contains an unsafe path component: {relative_path}")
    if name[0] == " " or name[-1] in {" ", "."}:
        raise ProjectArchiveError(f"project path is not portable to Windows: {relative_path}")
    if any(
        character in _WINDOWS_INVALID_CHARACTERS
        or ord(character) < 32
        or unicodedata.category(character).startswith("C")
        or unicodedata.category(character) in {"Zl", "Zp"}
        for character in name
    ):
        raise ProjectArchiveError(f"project path is not portable to Windows: {relative_path}")
    if len(name.encode("utf-8")) > 255:
        raise ProjectArchiveError(f"project path component exceeds the portable 255-byte limit: {relative_path}")
    if name.split(".", 1)[0].upper() in _WINDOWS_RESERVED_NAMES:
        raise ProjectArchiveError(f"project path uses a Windows-reserved name: {relative_path}")


def _portable_path_key(relative_path: PurePosixPath) -> str:
    return "/".join(unicodedata.normalize("NFD", part).casefold() for part in relative_path.parts)


def _archive_directory_name(name: str, source_relative_path: PurePosixPath) -> str:
    try:
        _validate_member_component(name, source_relative_path)
    except ProjectArchiveError:
        parts = source_relative_path.parts
        module_folder = len(parts) == 4 and parts[:2] == ("src", "modules")
        if not module_folder or not name.endswith((".", " ")) or " - " not in name:
            raise
        logical_id, title = name.split(" - ", 1)
        portable_title = title.rstrip(" .")
        if not logical_id or not portable_title or logical_id != logical_id.strip() or title != title.lstrip():
            raise
        candidate = f"{logical_id} - {portable_title}"
        _validate_member_component(candidate, PurePosixPath(*parts[:-1], candidate))
        return candidate
    return name


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        stat.S_IMODE(value.st_mode),
    )


def _read_source(
    path: Path,
    *,
    sink: BinaryIO | None = None,
    expected: SourceFile | None = None,
) -> tuple[str, int, bool, tuple[int, int, int, int, int]]:
    before = path.lstat()
    if stat.S_ISLNK(before.st_mode):
        raise ProjectArchiveError(f"project contains an unsupported symlink: {path}")
    if not stat.S_ISREG(before.st_mode):
        raise ProjectArchiveError(f"project contains an unsupported special file: {path}")

    digest = hashlib.sha256()
    with path.open("rb") as source:
        opened = os.fstat(source.fileno())
        if _stat_identity(opened) != _stat_identity(before):
            raise ProjectArchiveError(f"project file changed while being opened: {path}")
        while chunk := source.read(READ_CHUNK_SIZE):
            digest.update(chunk)
            if sink is not None:
                sink.write(chunk)
        after = os.fstat(source.fileno())
    current = path.lstat()
    identity = _stat_identity(before)
    if _stat_identity(after) != identity or _stat_identity(current) != identity:
        raise ProjectArchiveError(f"project file changed while being packaged: {path}")

    sha256 = digest.hexdigest()
    executable = bool(stat.S_IMODE(before.st_mode) & 0o111)
    if expected is not None and (
        identity != expected.stat_identity or sha256 != expected.sha256 or before.st_size != expected.size or executable != expected.executable
    ):
        raise ProjectArchiveError(f"project file changed between archive passes: {path}")
    return sha256, before.st_size, executable, identity


def _scan_project(project_root: Path) -> ProjectTree:
    directories: list[SourceDirectory] = []
    files: list[SourcePath] = []
    portable_paths: dict[str, PurePosixPath] = {}

    def visit(directory: Path, source_relative_directory: PurePosixPath, archive_relative_directory: PurePosixPath) -> None:
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda item: item.name)
        except OSError as exc:
            raise ProjectArchiveError(f"could not inspect project directory {directory}: {exc}") from exc
        for entry in entries:
            source_relative_path = source_relative_directory / entry.name
            if entry.is_symlink():
                raise ProjectArchiveError(f"project contains an unsupported symlink: {entry.path}")
            try:
                is_directory = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError as exc:
                raise ProjectArchiveError(f"could not inspect project path {entry.path}: {exc}") from exc
            if _is_excluded(entry.name, directory=is_directory):
                continue
            if is_directory:
                archive_name = _archive_directory_name(entry.name, source_relative_path)
            else:
                _validate_member_component(entry.name, source_relative_path)
                archive_name = entry.name
            archive_relative_path = archive_relative_directory / archive_name
            portable_key = _portable_path_key(archive_relative_path)
            collision = portable_paths.get(portable_key)
            if collision is not None and collision != source_relative_path:
                raise ProjectArchiveError(f"project paths collide on Windows or macOS after normalization: {collision} and {source_relative_path}")
            portable_paths[portable_key] = source_relative_path
            if is_directory:
                directories.append(SourceDirectory(source_relative_path=source_relative_path, relative_path=archive_relative_path))
                visit(Path(entry.path), source_relative_path, archive_relative_path)
            elif is_file:
                files.append(
                    SourcePath(
                        path=Path(entry.path),
                        source_relative_path=source_relative_path,
                        relative_path=archive_relative_path,
                    )
                )
            else:
                raise ProjectArchiveError(f"project contains an unsupported special file: {entry.path}")

    visit(project_root, PurePosixPath(), PurePosixPath())
    files.sort(key=lambda item: item.relative_path.as_posix())
    directories.sort(key=lambda item: item.relative_path.as_posix())
    manifest_key = _portable_path_key(PurePosixPath(ARCHIVE_MANIFEST_NAME))
    if any(_portable_path_key(item.relative_path) == manifest_key for item in directories) or any(
        _portable_path_key(item.relative_path) == manifest_key for item in files
    ):
        raise ProjectArchiveError(f"project root reserves {ARCHIVE_MANIFEST_NAME} for the archive content manifest")
    return ProjectTree(directories=tuple(directories), files=tuple(files))


def _inventory_project(tree: ProjectTree) -> ProjectInventory:
    files: list[SourceFile] = []
    for source in tree.files:
        sha256, size, executable, identity = _read_source(source.path)
        files.append(
            SourceFile(
                path=source.path,
                source_relative_path=source.source_relative_path,
                relative_path=source.relative_path,
                size=size,
                executable=executable,
                sha256=sha256,
                stat_identity=identity,
            )
        )
    return ProjectInventory(directories=tree.directories, files=tuple(files))


def _windows_path_length(path: str | PurePosixPath) -> int:
    return len(str(path).encode("utf-16-le")) // 2


def _validate_windows_path_budget(identity: ProjectIdentity, tree: ProjectTree) -> int:
    members = chain(
        (f"{identity.folder_name}/",),
        (f"{identity.folder_name}/{item.relative_path.as_posix()}/" for item in tree.directories),
        (f"{identity.folder_name}/{item.relative_path.as_posix()}" for item in tree.files),
        (f"{identity.folder_name}/{ARCHIVE_MANIFEST_NAME}",),
    )
    maximum_length, longest_member = max(((_windows_path_length(member), member) for member in members), key=lambda item: item[0])
    if maximum_length > WINDOWS_ARCHIVE_MEMBER_MAX_CODE_UNITS:
        raise ProjectArchiveError(
            f"project archive member exceeds the {WINDOWS_ARCHIVE_MEMBER_MAX_CODE_UNITS}-code-unit Windows portability budget "
            f"({maximum_length} UTF-16 code units): {longest_member}"
        )
    return maximum_length


def _zip_info(name: str, *, directory: bool, executable: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIMESTAMP)
    info.create_system = 3
    info.create_version = max(info.create_version, 45)
    info.extract_version = max(info.extract_version, 45)
    info.flag_bits |= 0x800
    info.compress_type = zipfile.ZIP_STORED if directory else zipfile.ZIP_DEFLATED
    if directory:
        info.external_attr = (stat.S_IFDIR | 0o755) << 16 | 0x10
    else:
        permissions = 0o755 if executable else 0o644
        info.external_attr = (stat.S_IFREG | permissions) << 16
    return info


def _content_manifest(files: tuple[SourceFile, ...]) -> bytes:
    return "".join(f"{item.sha256}  {item.relative_path.as_posix()}\n" for item in files).encode("utf-8")


def _write_archive(path: Path, identity: ProjectIdentity, inventory: ProjectInventory) -> None:
    manifest_content = _content_manifest(inventory.files)
    source_files = {item.relative_path.as_posix(): item for item in inventory.files}
    entry_names = [f"{identity.folder_name}/"]
    entry_names.extend(f"{identity.folder_name}/{item.relative_path.as_posix()}/" for item in inventory.directories)
    entry_names.extend(f"{identity.folder_name}/{item.relative_path.as_posix()}" for item in inventory.files)
    entry_names.append(f"{identity.folder_name}/{ARCHIVE_MANIFEST_NAME}")

    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=True, strict_timestamps=True) as archive:
        for name in sorted(entry_names):
            relative_name = name[len(identity.folder_name) + 1 :]
            if name.endswith("/"):
                archive.writestr(_zip_info(name, directory=True), b"")
            elif relative_name == ARCHIVE_MANIFEST_NAME:
                with archive.open(_zip_info(name, directory=False), mode="w", force_zip64=True) as target:
                    target.write(manifest_content)
            else:
                source = source_files[relative_name]
                with archive.open(_zip_info(name, directory=False, executable=source.executable), mode="w", force_zip64=True) as target:
                    _read_source(source.path, sink=target, expected=source)


def _inventory_paths(inventory: ProjectInventory) -> tuple[tuple[tuple[str, str], ...], tuple[tuple[str, str], ...]]:
    return (
        tuple((item.source_relative_path.as_posix(), item.relative_path.as_posix()) for item in inventory.directories),
        tuple((item.source_relative_path.as_posix(), item.relative_path.as_posix()) for item in inventory.files),
    )


def _tree_paths(tree: ProjectTree) -> tuple[tuple[tuple[str, str], ...], tuple[tuple[str, str], ...]]:
    return (
        tuple((item.source_relative_path.as_posix(), item.relative_path.as_posix()) for item in tree.directories),
        tuple((item.source_relative_path.as_posix(), item.relative_path.as_posix()) for item in tree.files),
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(READ_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def derive_project_package_catalog(
    archive_path: Path,
    *,
    paradev_version: str,
    desktop_version: str,
) -> ProjectPackageCatalog:
    """Derive a deterministic release catalog from one completed archive.

    Args:
        archive_path (Path): Canonically named project ZIP produced by
            `package_project`.
        paradev_version (str): Exact Python/backend version accepting the
            archive.
        desktop_version (str): Exact desktop release version paired with the
            archive.

    Returns:
        ProjectPackageCatalog: Strict one-row catalog containing archive
        identity, digest, size, inventory, and portability facts.

    Raises:
        ProjectArchiveError: If release metadata is empty or the archive is
            missing, unsafe, malformed, noncanonical, or changes while read.
        OSError: If the archive cannot be read.
    """

    release_version = _required_release_text(paradev_version, "ParaDev version")
    desktop_release_version = _required_release_text(desktop_version, "desktop version")
    observation = _observe_project_archive(archive_path)
    identity = observation.identity
    row: ProjectPackageCatalogRow = {
        "id": identity.folder_name.casefold(),
        "label": f"{identity.project_id} {identity.version}",
        "game": observation.game,
        "archive_name": observation.archive_path.name,
        "archive_sha256": observation.archive_sha256,
        "archive_size": observation.archive_size,
        "project_id": identity.project_id,
        "project_version": identity.version,
        "top_level_folder": identity.folder_name,
        "entry_count": observation.entry_count,
        "file_count": observation.file_count,
        "directory_count": observation.directory_count,
        "uncompressed_size": observation.uncompressed_size,
        "compressed_size": observation.compressed_size,
        "max_member_path_code_units": observation.max_member_path_code_units,
    }
    return {
        "schema": PROJECT_PACKAGE_CATALOG_SCHEMA,
        "paradev_version": release_version,
        "desktop_version": desktop_release_version,
        "packages": [row],
    }


def check_project_package_catalog(
    archive_path: Path,
    catalog_path: Path = DEFAULT_PROJECT_PACKAGE_CATALOG,
    *,
    paradev_version: str,
    desktop_version: str,
) -> ProjectPackageCatalogRow:
    """Check an archive against its exact row in an existing catalog.

    The check reads the archive and catalog without writing either file.
    Additional package rows are allowed so one generic catalog can bind
    several independently checked project archives.

    Args:
        archive_path (Path): Canonically named project ZIP to observe.
        catalog_path (Path): Existing catalog JSON to check without mutation.
        paradev_version (str): Expected Python/backend release version.
        desktop_version (str): Expected desktop release version.

    Returns:
        ProjectPackageCatalogRow: Freshly derived row that exactly matches the
        selected catalog entry.

    Raises:
        ProjectArchiveError: If the catalog is malformed, targets other
            release metadata, omits or duplicates the package id, or its row
            differs from the archive.
        OSError: If the archive or catalog cannot be read.
    """

    expected_catalog = derive_project_package_catalog(
        archive_path,
        paradev_version=paradev_version,
        desktop_version=desktop_version,
    )
    expected_row = expected_catalog["packages"][0]
    catalog = _read_project_package_catalog(catalog_path)
    _check_catalog_release_metadata(catalog, expected_catalog)
    packages = catalog.get("packages")
    if not isinstance(packages, list):
        raise ProjectArchiveError(f"{catalog_path} packages must be a JSON array")
    matches = [row for row in packages if isinstance(row, Mapping) and row.get("id") == expected_row["id"]]
    if not matches:
        raise ProjectArchiveError(f"{catalog_path} is missing project package {expected_row['id']!r}")
    if len(matches) != 1:
        raise ProjectArchiveError(f"{catalog_path} contains duplicate project package id {expected_row['id']!r}")
    differences = _catalog_row_differences(expected_row, matches[0])
    if differences:
        raise ProjectArchiveError(f"{catalog_path} package {expected_row['id']!r} differs from the archive: {'; '.join(differences)}")
    return expected_row


def _observe_project_archive(archive_path: Path) -> ProjectArchiveObservation:
    unresolved = archive_path.expanduser()
    try:
        before = unresolved.lstat()
    except OSError as exc:
        raise ProjectArchiveError(f"project archive does not exist or cannot be read: {unresolved}") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise ProjectArchiveError(f"project archive must be a regular local ZIP file: {unresolved}")
    resolved = unresolved.resolve(strict=True)

    digest = hashlib.sha256()
    with resolved.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if _stat_identity(opened) != _stat_identity(before):
            raise ProjectArchiveError(f"project archive changed while being opened: {resolved}")
        while chunk := stream.read(READ_CHUNK_SIZE):
            digest.update(chunk)
        stream.seek(0)
        try:
            with zipfile.ZipFile(stream) as archive:
                infos = tuple(archive.infolist())
                identity, game = _archive_release_identity(archive, infos, resolved)
        except (NotImplementedError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            raise ProjectArchiveError(f"project archive is not a supported ZIP file: {resolved}: {exc}") from exc
        after = os.fstat(stream.fileno())
    current = resolved.lstat()
    if _stat_identity(after) != _stat_identity(before) or _stat_identity(current) != _stat_identity(before):
        raise ProjectArchiveError(f"project archive changed while release metadata was derived: {resolved}")

    file_count = sum(not info.is_dir() for info in infos)
    directory_count = len(infos) - file_count
    return ProjectArchiveObservation(
        archive_path=resolved,
        archive_sha256=digest.hexdigest(),
        archive_size=before.st_size,
        identity=identity,
        game=game,
        entry_count=len(infos),
        file_count=file_count,
        directory_count=directory_count,
        uncompressed_size=sum(info.file_size for info in infos),
        compressed_size=sum(info.compress_size for info in infos),
        max_member_path_code_units=max((_windows_path_length(info.filename) for info in infos), default=0),
    )


def _archive_release_identity(
    archive: zipfile.ZipFile,
    infos: tuple[zipfile.ZipInfo, ...],
    archive_path: Path,
) -> tuple[ProjectIdentity, str]:
    names = [info.filename for info in infos]
    if not names:
        raise ProjectArchiveError(f"project archive is empty: {archive_path}")
    if len(names) != len(set(names)):
        raise ProjectArchiveError(f"project archive contains duplicate members: {archive_path}")
    manifest_infos = [
        info for info in infos if not info.is_dir() and len(PurePosixPath(info.filename).parts) == 2 and PurePosixPath(info.filename).name == "paradev.yaml"
    ]
    if len(manifest_infos) != 1:
        raise ProjectArchiveError(f"project archive must contain exactly one top-level paradev.yaml: {archive_path}")
    manifest_info = manifest_infos[0]
    top_level_folder = PurePosixPath(manifest_info.filename).parts[0]
    root_name = f"{top_level_folder}/"
    if not any(info.filename == root_name and info.is_dir() for info in infos):
        raise ProjectArchiveError(f"project archive is missing its top-level directory entry: {root_name}")
    if any(not info.filename.startswith(root_name) for info in infos):
        raise ProjectArchiveError(f"project archive contains a member outside {root_name}")
    if manifest_info.file_size > PROJECT_MANIFEST_MAX_BYTES:
        raise ProjectArchiveError(f"{manifest_info.filename} exceeds the {PROJECT_MANIFEST_MAX_BYTES}-byte release metadata limit")
    try:
        manifest = loads_yaml(archive.read(manifest_info).decode("utf-8"))
    except (UnicodeError, YAMLError) as exc:
        raise ProjectArchiveError(f"could not read {manifest_info.filename}: {exc}") from exc
    if not isinstance(manifest, Mapping):
        raise ProjectArchiveError(f"{manifest_info.filename} must contain a YAML mapping")
    identity = _project_identity_from_manifest(manifest, manifest_info.filename)
    if top_level_folder != identity.folder_name:
        raise ProjectArchiveError(f"project archive folder is {top_level_folder!r}, but paradev.yaml requires {identity.folder_name!r}")
    if archive_path.name != identity.archive_name:
        raise ProjectArchiveError(f"project archive name is {archive_path.name!r}, but paradev.yaml requires {identity.archive_name!r}")
    game = manifest.get("game")
    if not isinstance(game, str) or not game.strip():
        raise ProjectArchiveError(f"{manifest_info.filename} must define a non-empty string game")
    content_manifest_name = f"{top_level_folder}/{ARCHIVE_MANIFEST_NAME}"
    content_manifests = [info for info in infos if info.filename == content_manifest_name and not info.is_dir()]
    if len(content_manifests) != 1:
        raise ProjectArchiveError(f"project archive must contain exactly one {content_manifest_name}")
    return identity, game.strip()


def _required_release_text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectArchiveError(f"{label} must be a non-empty string")
    return value.strip()


def _read_project_package_catalog(catalog_path: Path) -> Mapping[object, object]:
    path = catalog_path.expanduser()
    try:
        encoded = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ProjectArchiveError(f"could not read project package catalog {path}: {exc}") from exc
    try:
        value = loads_json(encoded)
    except (TypeError, ValueError) as exc:
        raise ProjectArchiveError(f"project package catalog is not valid JSON: {path}: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ProjectArchiveError(f"project package catalog must be a JSON object: {path}")
    fields = set(value)
    expected_fields = {"schema", "paradev_version", "desktop_version", "packages"}
    if fields != expected_fields:
        missing = sorted(str(field) for field in expected_fields - fields)
        unknown = sorted(str(field) for field in fields - expected_fields)
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if unknown:
            details.append(f"unsupported fields: {', '.join(unknown)}")
        raise ProjectArchiveError(f"project package catalog has an invalid shape: {'; '.join(details)}")
    return value


def _check_catalog_release_metadata(
    catalog: Mapping[object, object],
    expected: ProjectPackageCatalog,
) -> None:
    expected_values = (
        ("schema", expected["schema"]),
        ("paradev_version", expected["paradev_version"]),
        ("desktop_version", expected["desktop_version"]),
    )
    for field, expected_value in expected_values:
        actual_value = catalog.get(field)
        if not isinstance(actual_value, str) or actual_value != expected_value:
            raise ProjectArchiveError(f"project package catalog {field} is {actual_value!r}, expected {expected_value!r}")


def _catalog_row_differences(
    expected: ProjectPackageCatalogRow,
    actual: Mapping[object, object],
) -> list[str]:
    expected_fields = set(expected)
    actual_fields = set(actual)
    differences: list[str] = []
    missing = sorted(str(field) for field in expected_fields - actual_fields)
    unknown = sorted(str(field) for field in actual_fields - expected_fields)
    if missing:
        differences.append(f"missing fields {', '.join(missing)}")
    if unknown:
        differences.append(f"unsupported fields {', '.join(unknown)}")
    for field, expected_value in expected.items():
        if field not in actual:
            continue
        actual_value = actual[field]
        if type(actual_value) is not type(expected_value) or actual_value != expected_value:
            differences.append(f"{field} expected {expected_value!r}, found {actual_value!r}")
    return differences


def _write_project_package_catalog(
    catalog: ProjectPackageCatalog,
    catalog_path: Path,
) -> Path:
    unresolved = catalog_path.expanduser()
    if unresolved.is_symlink():
        raise ProjectArchiveError(f"project package catalog destination cannot be a symlink: {unresolved}")
    destination = unresolved.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = f"{dumps_json(catalog, indent=2).rstrip()}\n"
    temporary_path: Path | None = None
    try:
        descriptor, raw_temporary_path = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        os.close(descriptor)
        temporary_path = Path(raw_temporary_path)
        temporary_path.write_text(encoded, encoding="utf-8")
        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return destination


def package_project(
    project_root: Path = DEFAULT_PROJECT_ROOT,
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> ProjectArchive:
    """Package one ParaDev project into a deterministic portable archive.

    Args:
        project_root: Directory containing the project's ``paradev.yaml``.
        output_dir: Directory that receives the versioned project archive.

    Returns:
        Metadata describing the completed archive and its SHA-256 digest.

    Raises:
        ProjectArchiveError: If the source is invalid, unsafe, changes during
            packaging, or cannot be represented portably.
        OSError: If the destination cannot be created or written.
    """

    unresolved_root = project_root.expanduser()
    if unresolved_root.is_symlink():
        raise ProjectArchiveError(f"project root cannot be a symlink: {unresolved_root}")
    try:
        resolved_root = unresolved_root.resolve(strict=True)
    except OSError as exc:
        raise ProjectArchiveError(f"project root does not exist: {unresolved_root}") from exc
    if not resolved_root.is_dir():
        raise ProjectArchiveError(f"project root is not a directory: {resolved_root}")

    manifest_path = resolved_root / "paradev.yaml"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ProjectArchiveError(f"project root must contain a regular paradev.yaml: {resolved_root}")
    identity = _project_identity(manifest_path)
    tree = _scan_project(resolved_root)
    max_windows_archive_member_path_length = _validate_windows_path_budget(identity, tree)
    inventory = _inventory_project(tree)

    destination = output_dir.expanduser().resolve()
    try:
        destination.relative_to(resolved_root)
    except ValueError:
        pass
    else:
        raise ProjectArchiveError(f"output directory cannot be inside the packaged project: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    if not destination.is_dir():
        raise ProjectArchiveError(f"output path is not a directory: {destination}")
    archive_path = destination / identity.archive_name
    if archive_path.is_symlink():
        raise ProjectArchiveError(f"archive destination cannot be a symlink: {archive_path}")

    temporary_path: Path | None = None
    try:
        descriptor, raw_temporary_path = tempfile.mkstemp(prefix=f".{identity.archive_name}.", suffix=".tmp", dir=destination)
        os.close(descriptor)
        temporary_path = Path(raw_temporary_path)
        _write_archive(temporary_path, identity, inventory)
        final_tree = _scan_project(resolved_root)
        if _tree_paths(final_tree) != _inventory_paths(inventory):
            raise ProjectArchiveError("project contents changed while the archive was being created")
        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, archive_path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return ProjectArchive(
        archive_path=archive_path,
        archive_sha256=_sha256_file(archive_path),
        project_id=identity.project_id,
        version=identity.version,
        top_level_folder=identity.folder_name,
        file_count=len(inventory.files),
        normalized_directory_count=sum(item.source_relative_path.name != item.relative_path.name for item in inventory.directories),
        max_windows_archive_member_path_length=max_windows_archive_member_path_length,
    )


def _print_archive_result(result: ProjectArchive) -> None:
    print(f"archive: {result.archive_path}")
    print(f"sha256: {result.archive_sha256}")
    print(f"project: {result.project_id} {result.version} ({result.file_count} files)")
    print(f"portable folder normalizations: {result.normalized_directory_count}")
    print(
        f"Windows archive member path budget: {result.max_windows_archive_member_path_length}/"
        f"{WINDOWS_ARCHIVE_MEMBER_MAX_CODE_UNITS} UTF-16 code units "
        f"({WINDOWS_EXTRACTION_PREFIX_HEADROOM} code units reserved for the extraction destination)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "project",
        nargs="?",
        type=Path,
        help=f"ParaDev project directory; defaults to {DEFAULT_PROJECT_ROOT.relative_to(ROOT)}",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="archive destination directory")
    parser.add_argument("--archive", type=Path, help="derive or check release metadata from an existing archive without packaging a project")
    parser.add_argument("--catalog-output", type=Path, help="write the derived one-row project-package catalog atomically")
    parser.add_argument(
        "--check-catalog",
        nargs="?",
        type=Path,
        const=DEFAULT_PROJECT_PACKAGE_CATALOG,
        metavar="PATH",
        help=f"check an existing archive without mutation; defaults to {DEFAULT_PROJECT_PACKAGE_CATALOG.relative_to(ROOT)}",
    )
    parser.add_argument("--paradev-version", help="exact Python/backend release version for catalog generation or checking")
    parser.add_argument("--desktop-version", help="exact desktop release version for catalog generation or checking")
    arguments = parser.parse_args()

    if arguments.archive is not None and arguments.project is not None:
        parser.error("project and --archive are mutually exclusive")
    if arguments.check_catalog is not None and arguments.archive is None:
        parser.error("--check-catalog requires --archive so the check remains non-mutating")
    if arguments.check_catalog is not None and arguments.catalog_output is not None:
        parser.error("--check-catalog cannot be combined with --catalog-output")
    catalog_requested = arguments.archive is not None or arguments.catalog_output is not None or arguments.check_catalog is not None
    if catalog_requested and (arguments.paradev_version is None or arguments.desktop_version is None):
        parser.error("catalog generation and checking require --paradev-version and --desktop-version")
    if not catalog_requested and (arguments.paradev_version is not None or arguments.desktop_version is not None):
        parser.error("--paradev-version and --desktop-version require --archive or --catalog-output")

    if arguments.archive is not None:
        try:
            if arguments.check_catalog is not None:
                row = check_project_package_catalog(
                    arguments.archive,
                    arguments.check_catalog,
                    paradev_version=arguments.paradev_version,
                    desktop_version=arguments.desktop_version,
                )
                print(f"catalog check: {arguments.check_catalog.expanduser().resolve()}")
                print(f"package: {row['id']} ({row['archive_sha256']})")
                return
            catalog = derive_project_package_catalog(
                arguments.archive,
                paradev_version=arguments.paradev_version,
                desktop_version=arguments.desktop_version,
            )
            if arguments.catalog_output is None:
                print(dumps_json(catalog, indent=2).rstrip())
                return
            catalog_path = _write_project_package_catalog(catalog, arguments.catalog_output)
        except (OSError, ProjectArchiveError) as exc:
            raise SystemExit(f"error: could not derive project package catalog: {exc}") from exc
        print(f"catalog: {catalog_path}")
        return

    try:
        result = package_project(arguments.project or DEFAULT_PROJECT_ROOT, output_dir=arguments.output_dir)
        catalog_path: Path | None = None
        if arguments.catalog_output is not None:
            catalog = derive_project_package_catalog(
                result.archive_path,
                paradev_version=arguments.paradev_version,
                desktop_version=arguments.desktop_version,
            )
            catalog_path = _write_project_package_catalog(catalog, arguments.catalog_output)
    except (OSError, ProjectArchiveError) as exc:
        raise SystemExit(f"error: could not package ParaDev project: {exc}") from exc
    _print_archive_result(result)
    if catalog_path is not None:
        print(f"catalog: {catalog_path}")


if __name__ == "__main__":
    main()
