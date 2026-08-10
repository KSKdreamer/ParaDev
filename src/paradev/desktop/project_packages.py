"""Verified project-package installation for desktop and automation surfaces."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import tempfile
import unicodedata
import zipfile
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import BinaryIO, cast

from typing_extensions import TypedDict

from heavenbase.utils import dumps_json, loads_json

from paradev.sdk.project import Project
from paradev.version import __version__

PROJECT_PACKAGE_CATALOG_SCHEMA = "paradev.release.project-package-catalog.v1"
PROJECT_PACKAGE_INSTALL_SCHEMA = "paradev.desktop.project-package-install.v1"
PROJECT_PACKAGE_PROVENANCE_SCHEMA = "paradev.project-package.provenance.v1"

_CATALOG_RESOURCE = ("release", "project-packages.json")
_CONTENT_MANIFEST_NAME = "SHA256SUMS"
_PROVENANCE_RELATIVE_PATH = PurePosixPath(".paradev/release-package.json")
_READ_CHUNK_SIZE = 1024 * 1024
_CONTENT_MANIFEST_MAX_BYTES = 32 * 1024 * 1024
_WINDOWS_MAX_PATH_CODE_UNITS = 260
_WINDOWS_MAX_COMPONENT_CODE_UNITS = 255
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_SUPPORTED_COMPRESSION = frozenset({zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})
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


class ProjectPackageError(ValueError):
    """Raised when a project package is unknown, unsafe, corrupt, or conflicting."""


class ProjectPackageCatalogRow(TypedDict):
    """One immutable project package accepted by this ParaDev release."""

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
    """Bundled catalog binding ParaDev to accepted project archives."""

    schema: str
    paradev_version: str
    desktop_version: str
    packages: list[ProjectPackageCatalogRow]


class ProjectPackageInstallPayload(TypedDict):
    """Result returned after installing or reopening a verified project package."""

    schema: str
    status: str
    installed: bool
    project_root: str
    package: ProjectPackageCatalogRow
    project: dict[str, object]


def desktop_project_package_catalog() -> ProjectPackageCatalog:
    """Return the verified project-package catalog bundled with ParaDev.

    Returns:
        A detached, JSON-safe catalog whose ParaDev version matches this
        backend.

    Raises:
        ProjectPackageError: If the catalog is missing, malformed, duplicated,
            or belongs to another ParaDev backend version.
    """

    resource = files("paradev.resources")
    for part in _CATALOG_RESOURCE:
        resource = resource.joinpath(part)
    try:
        encoded = resource.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ProjectPackageError(f"ParaDev's bundled project-package catalog is unavailable: {exc}") from exc
    try:
        decoded = loads_json(encoded)
    except (TypeError, ValueError) as exc:
        raise ProjectPackageError(f"Project-package catalog is not valid JSON: {exc}") from exc
    return _validate_catalog(decoded)


def desktop_install_project_package(
    archive_path: str | os.PathLike[str],
    destination_root: str | os.PathLike[str] | None = None,
) -> ProjectPackageInstallPayload:
    """Install one publisher-verified project archive transactionally.

    The selected archive must match an exact row in ParaDev's bundled catalog.
    Extraction occurs in a private sibling directory, verifies every file
    against the archive's ``SHA256SUMS``, and publishes the complete project
    with one directory rename. Existing package-managed projects are reopened
    without overwriting user edits.

    Args:
        archive_path (str | os.PathLike[str]): Selected `.zip` project
            package.
        destination_root (str | os.PathLike[str] | None): Writable directory
            that owns installed project folders. Defaults to the current
            user's `Documents/ParaDev/Projects` directory.

    Returns:
        ProjectPackageInstallPayload: Versioned payload containing the
        installed project root, package row, and canonical SDK project view.

    Raises:
        ProjectPackageError: If the archive is unknown, unsafe, corrupt,
            changes during installation, conflicts with an existing folder,
            or does not load as the cataloged project.
        OSError: If the destination cannot be created or written.
    """

    return _install_project_package(
        archive_path,
        (_default_project_package_destination_root() if destination_root is None else destination_root),
        catalog=desktop_project_package_catalog(),
    )


def _default_project_package_destination_root() -> Path:
    """Return the user-owned default directory for installed projects."""

    return Path.home() / "Documents" / "ParaDev" / "Projects"


def _load_project_package_catalog(catalog_path: str | os.PathLike[str]) -> ProjectPackageCatalog:
    """Load an explicit catalog for isolated tests and release tooling."""

    path = Path(catalog_path).expanduser()
    try:
        encoded = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ProjectPackageError(f"Could not read project-package catalog {path}: {exc}") from exc
    try:
        decoded = loads_json(encoded)
    except (TypeError, ValueError) as exc:
        raise ProjectPackageError(f"Project-package catalog is not valid JSON: {exc}") from exc
    return _validate_catalog(decoded)


def _install_project_package(
    archive_path: str | os.PathLike[str],
    destination_root: str | os.PathLike[str],
    *,
    catalog: ProjectPackageCatalog,
) -> ProjectPackageInstallPayload:
    """Install against an injected, already-validated catalog."""

    archive = Path(archive_path).expanduser()
    before = _regular_archive_stat(archive)

    temporary_root: Path | None = None
    try:
        with archive.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if _stat_identity(opened) != _stat_identity(before):
                raise ProjectPackageError(f"Project package changed while being opened: {archive}")
            digest = _stream_sha256(stream)
            hashed = os.fstat(stream.fileno())
            current = archive.lstat()
            if _stat_identity(hashed) != _stat_identity(before) or _stat_identity(current) != _stat_identity(before):
                raise ProjectPackageError(f"Project package changed while its publisher checksum was being verified: {archive}")
            package = _catalog_package_for_archive(catalog, archive.name, before.st_size, digest)
            destination = Path(destination_root).expanduser()
            destination.mkdir(parents=True, exist_ok=True)
            destination = destination.resolve(strict=True)
            if not destination.is_dir():
                raise ProjectPackageError(f"Project package destination is not a directory: {destination}")
            project_root = destination / package["top_level_folder"]
            existing = _existing_install(project_root, package)
            if existing is not None:
                return existing
            free_bytes = shutil.disk_usage(destination).free
            if free_bytes < package["uncompressed_size"]:
                raise ProjectPackageError(
                    f"Installing {package['label']} needs at least {package['uncompressed_size']} free bytes, "
                    f"but {destination} has {free_bytes}. Free disk space or choose another destination."
                )

            temporary_root = Path(tempfile.mkdtemp(prefix=".p-", dir=destination))
            stream.seek(0)
            with zipfile.ZipFile(stream) as package_archive:
                inventory, content_hashes = _validate_archive(
                    package_archive,
                    package,
                    project_root=project_root,
                    staging_root=temporary_root,
                )
                _extract_archive(package_archive, inventory, content_hashes, temporary_root, package)
            after = os.fstat(stream.fileno())
        current = archive.lstat()
        if _stat_identity(after) != _stat_identity(before) or _stat_identity(current) != _stat_identity(before):
            raise ProjectPackageError(f"Project package changed during installation: {archive}")

        _validated_project_view(temporary_root, package)
        _write_provenance(temporary_root, package)
        if project_root.exists() or project_root.is_symlink():
            raise ProjectPackageError(
                f"A project folder appeared while ParaDev was importing the package: {project_root}. "
                "Open that folder or choose a different project destination."
            )
        os.rename(temporary_root, project_root)
        project = _validated_project_view(project_root, package)
        return _install_payload("installed", True, project_root, package, project)
    except (
        EOFError,
        NotImplementedError,
        OSError,
        ProjectPackageError,
        RuntimeError,
        zipfile.BadZipFile,
        zipfile.LargeZipFile,
    ) as exc:
        if isinstance(exc, ProjectPackageError):
            raise
        raise ProjectPackageError(f"Could not install project package {archive}: {exc}") from exc
    finally:
        if temporary_root is not None:
            shutil.rmtree(temporary_root, ignore_errors=True)


def _validate_catalog(value: object) -> ProjectPackageCatalog:
    if not isinstance(value, Mapping):
        raise ProjectPackageError("Project-package catalog must be a JSON object.")
    expected_fields = {"schema", "paradev_version", "desktop_version", "packages"}
    _require_exact_fields(value, expected_fields, "Project-package catalog")
    schema = _required_string(value, "schema", "Project-package catalog")
    if schema != PROJECT_PACKAGE_CATALOG_SCHEMA:
        raise ProjectPackageError(f"Unsupported project-package catalog schema: {schema!r}.")
    paradev_version = _required_string(value, "paradev_version", "Project-package catalog")
    if paradev_version != __version__:
        raise ProjectPackageError(
            f"Project-package catalog targets ParaDev {paradev_version}, but the bundled backend is {__version__}. " "Reinstall a matching ParaDev release."
        )
    desktop_version = _required_string(value, "desktop_version", "Project-package catalog")
    raw_packages = value["packages"]
    if not isinstance(raw_packages, list) or not raw_packages:
        raise ProjectPackageError("Project-package catalog packages must be a non-empty JSON array.")

    package_fields = set(ProjectPackageCatalogRow.__required_keys__)
    packages: list[ProjectPackageCatalogRow] = []
    ids: set[str] = set()
    archive_names: set[str] = set()
    archive_digests: set[str] = set()
    for index, raw_package in enumerate(raw_packages):
        context = f"Project-package catalog packages[{index}]"
        if not isinstance(raw_package, Mapping):
            raise ProjectPackageError(f"{context} must be a JSON object.")
        _require_exact_fields(raw_package, package_fields, context)
        row = cast(
            ProjectPackageCatalogRow,
            {
                field: (
                    _required_nonnegative_integer(raw_package, field, context)
                    if field
                    in {
                        "archive_size",
                        "entry_count",
                        "file_count",
                        "directory_count",
                        "uncompressed_size",
                        "compressed_size",
                        "max_member_path_code_units",
                    }
                    else _required_string(raw_package, field, context)
                )
                for field in ProjectPackageCatalogRow.__required_keys__
            },
        )
        if not _SHA256_PATTERN.fullmatch(row["archive_sha256"]):
            raise ProjectPackageError(f"{context}.archive_sha256 must be a lowercase SHA-256 digest.")
        if Path(row["archive_name"]).name != row["archive_name"] or not row["archive_name"].endswith(".zip"):
            raise ProjectPackageError(f"{context}.archive_name must be one portable .zip file name.")
        _validate_portable_component(row["archive_name"], context=f"{context}.archive_name")
        if PurePosixPath(row["top_level_folder"]).name != row["top_level_folder"]:
            raise ProjectPackageError(f"{context}.top_level_folder must be one portable folder name.")
        _validate_portable_component(row["top_level_folder"], context=f"{context}.top_level_folder")
        if row["entry_count"] != row["file_count"] + row["directory_count"]:
            raise ProjectPackageError(f"{context} entry_count must equal file_count plus directory_count.")
        if row["id"] in ids:
            raise ProjectPackageError(f"Project-package catalog contains duplicate id: {row['id']}.")
        if row["archive_name"].casefold() in archive_names:
            raise ProjectPackageError(f"Project-package catalog contains duplicate archive name: {row['archive_name']}.")
        if row["archive_sha256"] in archive_digests:
            raise ProjectPackageError(f"Project-package catalog contains duplicate archive checksum: {row['archive_sha256']}.")
        ids.add(row["id"])
        archive_names.add(row["archive_name"].casefold())
        archive_digests.add(row["archive_sha256"])
        packages.append(row)
    return {
        "schema": schema,
        "paradev_version": paradev_version,
        "desktop_version": desktop_version,
        "packages": packages,
    }


def _validate_archive(
    archive: zipfile.ZipFile,
    package: ProjectPackageCatalogRow,
    *,
    project_root: Path,
    staging_root: Path,
) -> tuple[tuple[zipfile.ZipInfo, ...], dict[str, str]]:
    infos = tuple(archive.infolist())
    file_count = sum(not info.is_dir() for info in infos)
    directory_count = len(infos) - file_count
    facts = {
        "entry_count": len(infos),
        "file_count": file_count,
        "directory_count": directory_count,
        "uncompressed_size": sum(info.file_size for info in infos),
        "compressed_size": sum(info.compress_size for info in infos),
        "max_member_path_code_units": max((_windows_path_length(info.filename) for info in infos), default=0),
    }
    for field, actual in facts.items():
        expected = package[field]  # type: ignore[literal-required]
        if actual != expected:
            raise ProjectPackageError(
                f"{package['archive_name']} {field} is {actual}, but the bundled catalog expects {expected}. "
                "The archive is incomplete or belongs to another release."
            )

    top = package["top_level_folder"]
    names: set[str] = set()
    portable_names: set[str] = set()
    file_paths: set[tuple[str, ...]] = set()
    directory_paths: set[tuple[str, ...]] = set()
    has_top_directory = False
    has_project_manifest = False
    for info in infos:
        if info.flag_bits & 0x1:
            raise ProjectPackageError(f"Project package contains an encrypted member: {info.filename}")
        if info.compress_type not in _SUPPORTED_COMPRESSION:
            raise ProjectPackageError(
                f"Project package uses unsupported compression for {info.filename}. " "Re-download the publisher package instead of recompressing it."
            )
        parts = _safe_member_parts(info.filename, directory=info.is_dir())
        if not parts or parts[0] != top:
            raise ProjectPackageError(f"Project package member is outside the cataloged {top}/ folder: {info.filename}")
        if len(parts) == 1 and info.is_dir():
            has_top_directory = True
        if parts == (top, "paradev.yaml") and not info.is_dir():
            has_project_manifest = True
        if info.filename in names:
            raise ProjectPackageError(f"Project package contains a duplicate member: {info.filename}")
        names.add(info.filename)
        portable_name = "/".join(unicodedata.normalize("NFD", part).casefold() for part in parts)
        if portable_name in portable_names:
            raise ProjectPackageError(f"Project package contains paths that collide on Windows or macOS: {info.filename}")
        portable_names.add(portable_name)
        relative_parts = parts[1:]
        if info.is_dir():
            if relative_parts in file_paths or any(relative_parts[:index] in file_paths for index in range(1, len(relative_parts))):
                raise ProjectPackageError(f"Project package contains a file/directory path conflict: {info.filename}")
            directory_paths.add(relative_parts)
        else:
            if relative_parts in directory_paths or any(relative_parts[:index] in file_paths for index in range(1, len(relative_parts))):
                raise ProjectPackageError(f"Project package contains a file/directory path conflict: {info.filename}")
            file_paths.add(relative_parts)
        _validate_member_mode(info)
        if os.name == "nt":
            final_path = project_root.joinpath(*relative_parts)
            staged_path = staging_root.joinpath(*relative_parts)
            if max(_windows_path_length(str(final_path)), _windows_path_length(str(staged_path))) >= _WINDOWS_MAX_PATH_CODE_UNITS:
                raise ProjectPackageError(
                    f"Project package cannot fit under {project_root.parent} without Windows long-path support. " "Choose a shorter project destination."
                )
    if not has_top_directory or not has_project_manifest:
        raise ProjectPackageError(f"Project package must contain {top}/ and {top}/paradev.yaml.")

    manifest_name = f"{top}/{_CONTENT_MANIFEST_NAME}"
    try:
        manifest_info = archive.getinfo(manifest_name)
    except KeyError as exc:
        raise ProjectPackageError(f"Project package is missing {manifest_name}.") from exc
    if manifest_info.file_size > _CONTENT_MANIFEST_MAX_BYTES:
        raise ProjectPackageError(f"Project package content manifest exceeds {_CONTENT_MANIFEST_MAX_BYTES} bytes.")
    content_hashes = _content_manifest_hashes(archive.read(manifest_info), top)
    expected_files = {info.filename[len(top) + 1 :] for info in infos if not info.is_dir() and info.filename != manifest_name}
    if set(content_hashes) != expected_files:
        missing = sorted(expected_files - set(content_hashes))
        extra = sorted(set(content_hashes) - expected_files)
        detail = []
        if missing:
            detail.append(f"missing entries: {', '.join(missing[:3])}")
        if extra:
            detail.append(f"unknown entries: {', '.join(extra[:3])}")
        raise ProjectPackageError(f"Project package content manifest does not match the archive ({'; '.join(detail)}).")
    return tuple(sorted(infos, key=lambda info: info.filename)), content_hashes


def _extract_archive(
    archive: zipfile.ZipFile,
    infos: tuple[zipfile.ZipInfo, ...],
    content_hashes: Mapping[str, str],
    temporary_root: Path,
    package: ProjectPackageCatalogRow,
) -> None:
    top = package["top_level_folder"]
    manifest_name = f"{top}/{_CONTENT_MANIFEST_NAME}"
    for info in infos:
        parts = _safe_member_parts(info.filename, directory=info.is_dir())
        relative_parts = parts[1:]
        if not relative_parts:
            continue
        target = temporary_root.joinpath(*relative_parts)
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=False)
            os.chmod(target, 0o755)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        with archive.open(info, "r") as source, target.open("xb") as sink:
            while chunk := source.read(_READ_CHUNK_SIZE):
                sink.write(chunk)
                if info.filename != manifest_name:
                    digest.update(chunk)
        relative_name = info.filename[len(top) + 1 :]
        if info.filename != manifest_name and digest.hexdigest() != content_hashes[relative_name]:
            raise ProjectPackageError(f"Project package content checksum failed for {relative_name}.")
        mode = (info.external_attr >> 16) & 0o777
        os.chmod(target, mode or 0o644)


def _content_manifest_hashes(encoded: bytes, top: str) -> dict[str, str]:
    try:
        text = encoded.decode("utf-8")
    except UnicodeError as exc:
        raise ProjectPackageError(f"{top}/{_CONTENT_MANIFEST_NAME} must be UTF-8: {exc}") from exc
    hashes: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if len(line) < 67 or line[64:66] != "  " or not _SHA256_PATTERN.fullmatch(line[:64]):
            raise ProjectPackageError(f"{top}/{_CONTENT_MANIFEST_NAME} line {number} is malformed.")
        relative_name = line[66:]
        parts = _safe_member_parts(relative_name, directory=False)
        normalized = PurePosixPath(*parts).as_posix()
        if normalized == _CONTENT_MANIFEST_NAME or normalized == _PROVENANCE_RELATIVE_PATH.as_posix():
            raise ProjectPackageError(f"{top}/{_CONTENT_MANIFEST_NAME} line {number} uses a reserved path.")
        if normalized in hashes:
            raise ProjectPackageError(f"{top}/{_CONTENT_MANIFEST_NAME} contains duplicate path: {normalized}")
        hashes[normalized] = line[:64]
    return hashes


def _safe_member_parts(name: str, *, directory: bool) -> tuple[str, ...]:
    if not name or "\x00" in name or "\\" in name or name.startswith("/"):
        raise ProjectPackageError(f"Project package contains an unsafe path: {name!r}")
    path_name = name[:-1] if directory and name.endswith("/") else name
    if directory and not name.endswith("/"):
        raise ProjectPackageError(f"Project package directory is missing its trailing slash: {name}")
    if not directory and name.endswith("/"):
        raise ProjectPackageError(f"Project package file has a directory path: {name}")
    parts = tuple(path_name.split("/"))
    if not parts or any(not part or part in {".", ".."} for part in parts):
        raise ProjectPackageError(f"Project package contains an unsafe path: {name}")
    if PurePosixPath(*parts).is_absolute():
        raise ProjectPackageError(f"Project package contains an absolute path: {name}")
    for part in parts:
        _validate_portable_component(part, context=f"Project package path {name!r}")
    return parts


def _validate_portable_component(component: str, *, context: str) -> None:
    if (
        any(ord(character) < 32 or ord(character) == 127 for character in component)
        or any(character in _WINDOWS_INVALID_CHARACTERS for character in component)
        or component.endswith((" ", "."))
    ):
        raise ProjectPackageError(f"{context} contains a path component unsupported on Windows: {component!r}")
    stem = component.split(".", 1)[0].upper()
    if stem in _WINDOWS_RESERVED_NAMES:
        raise ProjectPackageError(f"{context} uses a Windows-reserved path component: {component!r}")
    if _windows_path_length(component) > _WINDOWS_MAX_COMPONENT_CODE_UNITS:
        raise ProjectPackageError(f"{context} exceeds the portable {_WINDOWS_MAX_COMPONENT_CODE_UNITS}-code-unit component limit: " f"{component!r}")


def _validate_member_mode(info: zipfile.ZipInfo) -> None:
    mode = info.external_attr >> 16
    if info.create_system != 3 or mode == 0:
        raise ProjectPackageError(f"Project package member lacks portable Unix file metadata: {info.filename}")
    kind = stat.S_IFMT(mode)
    expected = stat.S_IFDIR if info.is_dir() else stat.S_IFREG
    if kind != expected:
        raise ProjectPackageError(f"Project package contains an unsupported file type: {info.filename}")


def _existing_install(
    project_root: Path,
    package: ProjectPackageCatalogRow,
) -> ProjectPackageInstallPayload | None:
    if not project_root.exists() and not project_root.is_symlink():
        return None
    if project_root.is_symlink() or not project_root.is_dir():
        raise ProjectPackageError(f"Project package destination already exists and is not a managed project folder: {project_root}")
    provenance_path = project_root / _PROVENANCE_RELATIVE_PATH
    try:
        provenance = loads_json(provenance_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, TypeError, ValueError) as exc:
        raise ProjectPackageError(
            f"Project folder already exists and ParaDev cannot prove it came from this package: {project_root}. "
            "Open it as an existing project, move it, or choose another destination."
        ) from exc
    if not isinstance(provenance, Mapping) or any(
        provenance.get(field) != expected
        for field, expected in {
            "schema": PROJECT_PACKAGE_PROVENANCE_SCHEMA,
            "package_id": package["id"],
            "archive_sha256": package["archive_sha256"],
            "project_id": package["project_id"],
            "project_version": package["project_version"],
        }.items()
    ):
        raise ProjectPackageError(
            f"Project folder already exists but belongs to another package release: {project_root}. "
            "Open it as an existing project, move it, or choose another destination."
        )
    project = _validated_project_view(project_root, package)
    return _install_payload("existing", False, project_root, package, project)


def _validated_project_view(project_root: Path, package: ProjectPackageCatalogRow) -> dict[str, object]:
    try:
        view = Project.load(project_root).to_view()
    except (OSError, ValueError) as exc:
        raise ProjectPackageError(f"Installed package is not a usable ParaDev project: {exc}") from exc
    if view.get("project_id") != package["project_id"] or str(view.get("version", "")) != package["project_version"] or view.get("game") != package["game"]:
        raise ProjectPackageError(
            f"Installed package identifies project {view.get('project_id')!r} version {view.get('version')!r} "
            f"for {view.get('game')!r}, but the bundled catalog expects {package['project_id']!r} "
            f"version {package['project_version']!r} for {package['game']!r}."
        )
    return cast(dict[str, object], view)


def _write_provenance(project_root: Path, package: ProjectPackageCatalogRow) -> None:
    provenance_path = project_root / _PROVENANCE_RELATIVE_PATH
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    provenance = {
        "schema": PROJECT_PACKAGE_PROVENANCE_SCHEMA,
        "package_id": package["id"],
        "archive_name": package["archive_name"],
        "archive_sha256": package["archive_sha256"],
        "project_id": package["project_id"],
        "project_version": package["project_version"],
        "paradev_version": __version__,
    }
    provenance_path.write_text(f"{dumps_json(provenance, sort_keys=True, indent=2).rstrip()}\n", encoding="utf-8")
    os.chmod(provenance_path, 0o644)


def _install_payload(
    status: str,
    installed: bool,
    project_root: Path,
    package: ProjectPackageCatalogRow,
    project: dict[str, object],
) -> ProjectPackageInstallPayload:
    return {
        "schema": PROJECT_PACKAGE_INSTALL_SCHEMA,
        "status": status,
        "installed": installed,
        "project_root": str(project_root),
        "package": dict(package),
        "project": dict(project),
    }


def _catalog_package_for_archive(
    catalog: ProjectPackageCatalog,
    archive_name: str,
    archive_size: int,
    archive_sha256: str,
) -> ProjectPackageCatalogRow:
    digest_matches = [row for row in catalog["packages"] if row["archive_sha256"] == archive_sha256]
    if digest_matches:
        package = digest_matches[0]
        if package["archive_size"] != archive_size:
            raise ProjectPackageError(
                f"{archive_name} matches a publisher checksum but has size {archive_size}; "
                f"the bundled catalog expects {package['archive_size']}. Re-download the package."
            )
        return package

    named = [row for row in catalog["packages"] if row["archive_name"].casefold() == archive_name.casefold()]
    expected = ", ".join(row["archive_name"] for row in catalog["packages"])
    if named:
        package = named[0]
        raise ProjectPackageError(
            f"{archive_name} does not match the publisher checksum for {package['label']}. "
            "Re-download the package; ParaDev will not install modified or incomplete bytes."
        )
    raise ProjectPackageError(
        f"{archive_name} is not a verified project package for this ParaDev release. "
        f"Select the publisher archive ({expected}); browser-renamed downloads are accepted when their checksum matches. "
        "Use Open existing project for an unpackaged folder."
    )


def _regular_archive_stat(path: Path) -> os.stat_result:
    try:
        value = path.lstat()
    except OSError as exc:
        raise ProjectPackageError(f"Project package does not exist or cannot be read: {path}") from exc
    if stat.S_ISLNK(value.st_mode) or not stat.S_ISREG(value.st_mode):
        raise ProjectPackageError(f"Project package must be a regular local .zip file: {path}")
    if path.suffix.casefold() != ".zip":
        raise ProjectPackageError(f"Project package must be a local .zip file: {path}")
    return value


def _stream_sha256(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    while chunk := stream.read(_READ_CHUNK_SIZE):
        digest.update(chunk)
    return digest.hexdigest()


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        stat.S_IMODE(value.st_mode),
    )


def _windows_path_length(path: str) -> int:
    return len(path.encode("utf-16-le")) // 2


def _required_string(value: Mapping[object, object], field: str, context: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or not item.strip():
        raise ProjectPackageError(f"{context}.{field} must be a non-empty string.")
    return item.strip()


def _required_nonnegative_integer(value: Mapping[object, object], field: str, context: str) -> int:
    item = value.get(field)
    if not isinstance(item, int) or isinstance(item, bool) or item < 0:
        raise ProjectPackageError(f"{context}.{field} must be a nonnegative integer.")
    return item


def _require_exact_fields(value: Mapping[object, object], expected: set[str], context: str) -> None:
    fields = {field for field in value if isinstance(field, str)}
    non_string_fields = [field for field in value if not isinstance(field, str)]
    if non_string_fields:
        raise ProjectPackageError(f"{context} contains non-string fields.")
    missing = sorted(expected - fields)
    unknown = sorted(fields - expected)
    if missing:
        raise ProjectPackageError(f"{context} is missing fields: {', '.join(missing)}.")
    if unknown:
        raise ProjectPackageError(f"{context} contains unsupported fields: {', '.join(unknown)}.")
