"""Project-local build and authoring extension helpers."""

from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import inspect
import logging
import re
import shutil
import sqlite3
import sys
import tempfile
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path, PurePosixPath
from string import Formatter
from threading import RLock
from types import ModuleType
from typing import TYPE_CHECKING
from uuid import uuid4

from .families import (
    CollectionSourceFamily,
    RoutedSourceFamily,
    SimpleSourceFamily,
    SourceRoute,
)
from .registry import BuildRegistry
from .presentation import FamilyPresentation, family_presentation_from_mapping
from .slots import Slot, slot_match_escapes_root

if TYPE_CHECKING:
    from heavenbase.modules import InstallReceipt, ModuleService

logger = logging.getLogger(__name__)


class ProjectFamilySpecError(ValueError):
    """Raised when a project-local family declaration is invalid."""


_FORMATTER = Formatter()
_MODULE_TEMPLATE_FIELDS = frozenset(
    {
        "family",
        "module_id",
        "object_id",
        "source_path",
        "source_name",
        "source_stem",
        "source_suffix",
        "source_slot",
        "slot",
        "language",
        "language_folder",
    }
)
_COLLECTION_TEMPLATE_FIELDS = frozenset(
    {
        "family",
        "collection_id",
        "object_id",
        "source_path",
        "source_name",
        "source_stem",
        "source_suffix",
        "source_slot",
        "slot",
        "language",
        "language_folder",
    }
)
_COLLECTION_MEMBER_TEMPLATE_FIELDS = _MODULE_TEMPLATE_FIELDS & _COLLECTION_TEMPLATE_FIELDS
_SPRITE_NAME_TEMPLATE_FIELDS = _MODULE_TEMPLATE_FIELDS - frozenset({"language", "language_folder"})
_SPRITE_GFX_TEMPLATE_FIELDS = _SPRITE_NAME_TEMPLATE_FIELDS | frozenset({"project_id"})
_REQUIRED_LOC_TEMPLATE_FIELDS = frozenset({"family", "module_id", "collection_id", "object_id"})
_MISSING_MODULE = object()
_PROJECT_MODULE_IMPORT_LOCK = RLock()
_PROJECT_EXTENSION_INSTALL_LOCK = RLock()
_PROJECT_EXTENSION_INSTALL_RETRY_LIMIT = 16
_PROJECT_EXTENSION_LOCK_TIMEOUT_SECONDS = 300
_PROJECT_EXTENSION_CACHE_SCHEMA = "paradev.project-extension-install-cache.v1"
_PROJECT_EXTENSION_HIDDEN_DESCRIPTOR = Path(".paradev/meta.yaml")
PROJECT_BUILD_FAMILY_KIND = "paradev_build_family"
PROJECT_BUILD_POSTPROCESSOR_KIND = "paradev_build_postprocessor"
PROJECT_BUILD_WRITER_KIND = "paradev_build_writer"
PROJECT_AUTHORING_TEMPLATE_KIND = "paradev_authoring_template"
PROJECT_DIAGRAM_PROVIDER_KIND = "paradev_diagram_provider"
_PROJECT_RUNTIME_KINDS = frozenset(
    {
        PROJECT_BUILD_FAMILY_KIND,
        PROJECT_BUILD_POSTPROCESSOR_KIND,
        PROJECT_BUILD_WRITER_KIND,
        PROJECT_DIAGRAM_PROVIDER_KIND,
    }
)
_PROJECT_EXTENSION_FOLDER_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@dataclass(frozen=True, slots=True)
class _ProjectExtensionInstall:
    """One cached desired install set with Registry publication identities."""

    keys: tuple[tuple[str, str], ...]
    publications: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...]


_PROJECT_EXTENSION_INSTALL_CACHE: dict[
    tuple[str, tuple[tuple[str, str], ...]],
    _ProjectExtensionInstall,
] = {}


@dataclass(frozen=True, slots=True)
class ProjectFamilySpec:
    """One declarative project-local build family."""

    family: str
    kind: str = "simple_source"
    source_slots: tuple[Slot, ...] = ()
    collection_source_slots: tuple[Slot, ...] = ()
    metadata_keys: tuple[str, ...] = ()
    settings_keys: tuple[str, ...] = ()
    settings_values: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    required_settings: tuple[str, ...] = ()
    required_loc_keys: tuple[str, ...] = ()
    title_loc_keys: tuple[str, ...] | None = None
    asset_constraints: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    default_assets: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    settings_normalizers: Mapping[str, Callable[[object], object]] = field(default_factory=dict)
    route_setting: str = "subtype"
    default_route: str | None = None
    routes: Mapping[str, SourceRoute] = field(default_factory=dict)
    pdx_path_template: str | None = None
    module_pdx_path_template: str | None = None
    loc_path_template: str | None = None
    copy_path_template: str | None = None
    sprite_gfx_path_template: str | None = None
    sprite_name_template: str | None = None
    sprite_slots: tuple[str, ...] = ()
    visible: bool = True
    presentation: FamilyPresentation | None = None
    replaces_registered_family: bool = False


def project_family_specs(raw: object, source: str | Path) -> tuple[ProjectFamilySpec, ...]:
    """Return validated project-local family specs from manifest data."""

    if raw is None:
        return ()
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} key 'families' must be a mapping of family id to family declaration.")

    specs: list[ProjectFamilySpec] = []
    for family, declaration in sorted(raw.items()):
        label = f"families.{family}"
        if not isinstance(family, str) or not family.strip():
            raise ProjectFamilySpecError(f"{source} {label} must use a non-empty string family id.")
        if not isinstance(declaration, Mapping):
            raise ProjectFamilySpecError(f"{source} {label} must be a mapping.")
        specs.append(_family_spec(family.strip(), declaration, source))
    return tuple(specs)


def apply_project_families(
    registry: BuildRegistry,
    specs: Sequence[ProjectFamilySpec],
    source: str | Path,
    *,
    presentations: Mapping[str, FamilyPresentation] | None = None,
) -> BuildRegistry:
    """Register project-local families into a profile registry."""

    for spec in specs:
        registered = any(str(getattr(family, "family", "")) == spec.family for family in registry.families)
        if registered and not spec.replaces_registered_family:
            raise ProjectFamilySpecError(f"{source} families.{spec.family} duplicates a registered profile family.")
        try:
            family = _family(spec, source)
            presentation = presentations.get(spec.family) if presentations is not None else None
            if registered:
                registry.replace_family(family, presentation=presentation)
            else:
                registry.add_family(family, presentation=presentation)
        except ValueError as error:
            raise ProjectFamilySpecError(f"{source} families.{spec.family} is invalid: {error}") from error
    return registry


def project_extension_modules(project_root: Path) -> tuple[Path, ...]:
    """Discover conventional project-local HeavenBase module folders.

    A project extension is one direct child of ``extensions/`` containing the
    implementation ``__init__.py`` and exactly one descriptor. ParaDev projects
    may keep the generated descriptor at ``.paradev/meta.yaml``; ParaDev stages
    that source as an exact standard HeavenBase module folder before
    installation. A root-level ``meta.yaml`` remains supported for ordinary
    external HeavenBase modules. Discovery only inspects paths and never
    imports extension code.

    Args:
        project_root: ParaDev project root.

    Returns:
        Deterministically ordered extension module folders.

    Raises:
        ProjectFamilySpecError: If an extension folder is malformed.
    """

    extension_root = project_root / "extensions"
    if not extension_root.exists():
        return ()
    if not extension_root.is_dir():
        raise ProjectFamilySpecError(f"{extension_root} must be a directory.")
    modules: list[Path] = []
    for candidate in sorted(extension_root.iterdir(), key=lambda path: path.name):
        if candidate.name.startswith("."):
            continue
        if not candidate.is_dir():
            raise ProjectFamilySpecError(f"{candidate} must be a HeavenBase module folder or be removed.")
        if _PROJECT_EXTENSION_FOLDER_RE.fullmatch(candidate.name) is None:
            raise ProjectFamilySpecError(f"{candidate} must use a lowercase extension id containing only letters, numbers, '_' or '-'.")
        initializer = candidate / "__init__.py"
        _project_extension_descriptor_path(candidate)
        if not initializer.is_file():
            raise ProjectFamilySpecError(f"{candidate} must contain __init__.py.")
        modules.append(candidate.resolve())
    return tuple(modules)


def apply_project_extension_modules(
    registry: BuildRegistry,
    module_roots: Sequence[Path],
    project_id: str,
    source: str | Path,
) -> BuildRegistry:
    """Resolve project build plugins through the HeavenBase module Registry.

    Installation validates and captures all module folders without importing
    them. Only after every installation succeeds are build-family, writer, and
    postprocessor records materialized through ``ModuleService.resolve``.

    Args:
        registry: Runtime build registry receiving resolved plugins.
        module_roots: Conventional HeavenBase module folders.
        project_id: Stable ParaDev project identifier.
        source: Project manifest path used in contextual errors.

    Returns:
        Runtime build registry with project plugins applied.

    Raises:
        ProjectFamilySpecError: If installation, resolution, or plugin contract
            validation fails.
    """

    keys = _install_project_extension_modules(module_roots, project_id, source)
    if not keys:
        return registry
    from paradev.config import _CONTEXT_PARADEV

    resolver = _CONTEXT_PARADEV.modules()
    for kind, identifier in keys:
        if kind not in _PROJECT_RUNTIME_KINDS:
            continue
        rows = resolver.inspect(kind, identifier)
        if not rows:
            continue
        try:
            publication_replacements = (
                _project_extension_publication_replacements(
                    rows,
                    kind=kind,
                    identifier=identifier,
                    source=source,
                )
                if kind == PROJECT_BUILD_FAMILY_KIND
                else ()
            )
            presentation = (
                _project_extension_family_presentation(
                    rows,
                    kind=kind,
                    identifier=identifier,
                    source=source,
                )
                if kind == PROJECT_BUILD_FAMILY_KIND
                else None
            )
            resolved = resolver.resolve(kind, identifier)
            item = _resolved_build_item(kind, identifier, resolved, source)
            if isinstance(item, ProjectFamilySpec):
                apply_project_families(
                    registry,
                    (item,),
                    source,
                    presentations=({item.family: presentation} if presentation is not None else None),
                )
            elif (
                kind == PROJECT_DIAGRAM_PROVIDER_KIND
                and getattr(
                    item,
                    "replaces_registered_provider",
                    False,
                )
                is True
            ):
                registry.replace_diagram_provider(item)
            elif (
                getattr(item, "family", None)
                and getattr(item, "replaces_registered_family", False) is True
                and any(str(getattr(family, "family", "")) == str(getattr(item, "family", "")) for family in registry.families)
            ):
                registry.replace_family(item, presentation=presentation)
            elif getattr(item, "family", None):
                registry.add_family(item, presentation=presentation)
            else:
                registry.add(item)
            if publication_replacements:
                registry.add_publication_replacements(
                    str(getattr(item, "family", "")),
                    publication_replacements,
                )
        except (ImportError, KeyError, TypeError, ValueError) as error:
            raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} cannot be activated: {error}") from error
    return registry


def _project_extension_family_presentation(
    rows: Sequence[Mapping[str, object]],
    *,
    kind: str,
    identifier: str,
    source: str | Path,
) -> FamilyPresentation | None:
    """Read inert presentation capability metadata from one Registry record."""

    record = _project_extension_registry_record(
        rows,
        kind=kind,
        identifier=identifier,
        source=source,
    )
    meta = record.get("meta")
    assert isinstance(meta, Mapping)
    presentation = meta.get("presentation")
    if presentation is None:
        return None
    if not isinstance(presentation, Mapping):
        raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} " "meta.presentation must be a mapping.")
    try:
        return family_presentation_from_mapping(presentation)
    except (TypeError, ValueError) as error:
        raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} " f"meta.presentation is invalid: {error}") from error


def _project_extension_publication_replacements(
    rows: Sequence[Mapping[str, object]],
    *,
    kind: str,
    identifier: str,
    source: str | Path,
) -> tuple[str, ...]:
    """Read inert publication migration state from one Registry record."""

    record = _project_extension_registry_record(
        rows,
        kind=kind,
        identifier=identifier,
        source=source,
    )
    meta = record.get("meta")
    assert isinstance(meta, Mapping)
    publication = meta.get("publication")
    if publication is None:
        return ()
    if not isinstance(publication, Mapping):
        raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} " "meta.publication must be a mapping.")
    unknown = set(publication) - {"replaces_families"}
    if unknown:
        raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} " "meta.publication has unsupported fields " f"{sorted(unknown)!r}.")
    raw = publication.get("replaces_families")
    if not isinstance(raw, list) or not raw:
        raise ProjectFamilySpecError(
            f"{source} project extension {kind}:{identifier} " "meta.publication.replaces_families must be a non-empty list of " "strings."
        )
    replacements: list[str] = []
    for index, value in enumerate(raw):
        if not isinstance(value, str) or not value.strip():
            raise ProjectFamilySpecError(
                f"{source} project extension {kind}:{identifier} " "meta.publication.replaces_families" f"[{index}] must be a non-empty string."
            )
        replacements.append(value)
    return tuple(replacements)


def _project_extension_registry_record(
    rows: Sequence[Mapping[str, object]],
    *,
    kind: str,
    identifier: str,
    source: str | Path,
) -> Mapping[str, object]:
    """Return one exact Registry record with typed metadata."""

    if len(rows) != 1:
        raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} must resolve to " "one Registry inspection row.")
    record = rows[0].get("record")
    if not isinstance(record, Mapping):
        raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} has no Registry record.")
    meta = record.get("meta")
    if not isinstance(meta, Mapping):
        raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} has no Registry metadata.")
    return {**record, "meta": meta}


def project_extension_templates(
    module_roots: Sequence[Path],
    project_id: str,
    source: str | Path,
) -> tuple[object, ...]:
    """Resolve project authoring templates through HeavenBase.

    Args:
        module_roots: Conventional HeavenBase module folders.
        project_id: Stable ParaDev project identifier.
        source: Project manifest path used in contextual errors.

    Returns:
        Project-local ``ModuleTemplate`` objects in deterministic record order.

    Raises:
        ProjectFamilySpecError: If a template record is invalid.
    """

    keys = _install_project_extension_modules(module_roots, project_id, source)
    if not keys:
        return ()
    from paradev.config import _CONTEXT_PARADEV
    from paradev.sdk.templates import (
        ModuleTemplate,
        ProjectTemplateSpecError,
        project_module_templates,
    )

    resolver = _CONTEXT_PARADEV.modules()
    templates: list[ModuleTemplate] = []
    for kind, identifier in keys:
        if kind != PROJECT_AUTHORING_TEMPLATE_KIND:
            continue
        rows = resolver.inspect(kind, identifier)
        if not rows:
            continue
        try:
            resolved = resolver.resolve(kind, identifier)
            if callable(resolved) and not isinstance(resolved, type):
                resolved = resolved()
            if isinstance(resolved, ModuleTemplate):
                template = resolved
            elif isinstance(resolved, Mapping):
                template_id = resolved.get("template_id")
                declaration = resolved.get("declaration")
                if not isinstance(template_id, str) or not template_id.strip() or not isinstance(declaration, Mapping):
                    raise ProjectTemplateSpecError("inline authoring templates require template_id and declaration mappings")
                template = project_module_templates({template_id: dict(declaration)}, source)[0]
            else:
                raise ProjectTemplateSpecError(f"resolved {type(resolved).__name__}; expected ModuleTemplate, factory, or inline definition")
        except (
            ImportError,
            KeyError,
            TypeError,
            ValueError,
            ProjectTemplateSpecError,
        ) as error:
            raise ProjectFamilySpecError(f"{source} project extension {kind}:{identifier} cannot load its authoring template: {error}") from error
        templates.append(template)
    return tuple(templates)


def _install_project_extension_modules(
    module_roots: Sequence[Path],
    project_id: str,
    source: str | Path,
) -> tuple[tuple[str, str], ...]:
    if not module_roots:
        return ()
    from paradev.config import _CONTEXT_PARADEV

    resolver = _CONTEXT_PARADEV.modules()
    clean_project_id = _project_coordinate_part(project_id)
    roots = tuple(Path(root).resolve() for root in module_roots)
    signatures = tuple((str(root), _module_folder_digest(root)) for root in roots)
    cache_key = (str(resolver.authority_token), signatures)
    persistent = _extension_resolver_is_persistent(resolver)
    cache_path = _project_extension_install_cache_path(roots) if persistent else None
    expected_keys = _project_extension_descriptor_keys(roots) if cache_path is not None else None
    with _PROJECT_EXTENSION_INSTALL_LOCK:
        cached = _verified_project_extension_install(
            resolver,
            cache_key,
            cache_path,
            signatures,
            expected_keys,
            refresh=persistent,
        )
        if cached is not None:
            return cached.keys
        publication_lock = _project_extension_registry_lock() if persistent else nullcontext()
        with publication_lock:
            cached = _verified_project_extension_install(
                resolver,
                cache_key,
                cache_path,
                signatures,
                expected_keys,
                refresh=persistent,
            )
            if cached is not None:
                return cached.keys
            installed_keys: list[tuple[str, str]] = []
            publications: list[tuple[str, str, tuple[tuple[str, str], ...]]] = []
            for root in roots:
                expected_coordinate = f"paradev-projects/{clean_project_id}/{root.name}"
                try:
                    receipt = _install_project_extension_module(
                        resolver,
                        root,
                        publisher=f"paradev-project:{clean_project_id}",
                        expected_coordinate=expected_coordinate,
                    )
                except ProjectFamilySpecError:
                    raise
                except (OSError, TypeError, ValueError) as error:
                    raise ProjectFamilySpecError(f"{source} extension folder {root} is not an " f"installable HeavenBase module: {error}") from error
                installed_keys.extend(receipt.keys)
                publications.append(
                    (
                        receipt.coordinate,
                        receipt.manifest_fingerprint,
                        receipt.keys,
                    )
                )
            result = tuple(dict.fromkeys(installed_keys))
            installed = _ProjectExtensionInstall(
                keys=result,
                publications=tuple(publications),
            )
            _PROJECT_EXTENSION_INSTALL_CACHE[cache_key] = installed
            if cache_path is not None:
                try:
                    _write_project_extension_install_cache(
                        cache_path,
                        signatures,
                        installed,
                    )
                except OSError as error:
                    logger.warning(
                        "Could not cache verified project extensions at %s: %s",
                        cache_path,
                        error,
                    )
            return result


def _install_project_extension_module(
    resolver: "ModuleService",
    root: Path,
    *,
    publisher: str,
    expected_coordinate: str,
) -> "InstallReceipt":
    """Install one extension while honoring HeavenBase CAS refresh semantics."""

    from heavenbase import RegistryConflictError

    last_conflict: RegistryConflictError | None = None
    with _installable_project_extension(root) as install_root:
        for _attempt in range(_PROJECT_EXTENSION_INSTALL_RETRY_LIMIT):
            try:
                return resolver.install(
                    install_root,
                    publisher=publisher,
                    expected_coordinate=expected_coordinate,
                )
            except RegistryConflictError as error:
                last_conflict = error
                if not resolver.refresh():
                    break
    raise ProjectFamilySpecError(
        f"Extension registry changed concurrently while installing {root}; "
        f"ParaDev could not publish it after "
        f"{_PROJECT_EXTENSION_INSTALL_RETRY_LIMIT} refresh attempts."
    ) from last_conflict


def _extension_resolver_is_persistent(resolver: "ModuleService") -> bool:
    """Return whether the resolver uses HeavenBase durable catalog storage."""

    return resolver.catalog.persistent


def _verified_project_extension_install(
    resolver: "ModuleService",
    cache_key: tuple[str, tuple[tuple[str, str], ...]],
    cache_path: Path | None,
    signatures: tuple[tuple[str, str], ...],
    expected_keys: tuple[tuple[str, str], ...] | None,
    *,
    refresh: bool,
) -> _ProjectExtensionInstall | None:
    """Return an exact current receipt without acquiring the writer lock."""

    if refresh:
        resolver.refresh()
    cached = _PROJECT_EXTENSION_INSTALL_CACHE.get(cache_key)
    if cached is not None and _extension_install_is_current(resolver, cached):
        return cached
    if cache_path is None:
        return None
    cached = _load_project_extension_install_cache(
        cache_path,
        signatures,
        expected_keys,
    )
    if cached is None or not _extension_install_is_current(resolver, cached):
        return None
    _PROJECT_EXTENSION_INSTALL_CACHE[cache_key] = cached
    return cached


@contextmanager
def _project_extension_registry_lock() -> Iterator[None]:
    """Serialize ParaDev writers targeting HeavenBase's durable module catalog."""

    path = Path(tempfile.gettempdir()) / "paradev-heavenbase-system-modules.lock"
    connection = sqlite3.connect(
        path,
        timeout=_PROJECT_EXTENSION_LOCK_TIMEOUT_SECONDS,
        isolation_level=None,
    )
    try:
        try:
            connection.execute("begin immediate")
        except sqlite3.OperationalError as error:
            error_code = getattr(error, "sqlite_errorcode", None)
            lock_messages = {"database is locked", "database table is locked"}
            if error_code in {
                getattr(sqlite3, "SQLITE_BUSY", 5),
                getattr(sqlite3, "SQLITE_LOCKED", 6),
            } or (error_code is None and str(error).casefold() in lock_messages):
                raise ProjectFamilySpecError(
                    "Another ParaDev process has been registering project " "extensions for more than five minutes; retry after it " "finishes."
                ) from error
            raise
        yield
    finally:
        if connection.in_transaction:
            connection.rollback()
        connection.close()


def _project_extension_install_cache_path(roots: Sequence[Path]) -> Path:
    """Return the ignored project cache path for one extension set."""

    if any(root.parent.name != "extensions" for root in roots):
        raise ProjectFamilySpecError("Project extensions must share one direct extensions/ folder.")
    project_roots = {root.parent.parent for root in roots}
    if len(project_roots) != 1:
        raise ProjectFamilySpecError("Project extensions must share one direct extensions/ folder.")
    project_root = next(iter(project_roots))
    return project_root / ".paradev" / "cache" / "extension-install.json"


def _load_project_extension_install_cache(
    path: Path,
    signatures: tuple[tuple[str, str], ...],
    expected_keys: tuple[tuple[str, str], ...] | None,
) -> _ProjectExtensionInstall | None:
    """Load one exact derived install receipt, or ignore stale cache data."""

    from heavenbase.utils import loads_json

    try:
        payload = loads_json(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return None
    if not isinstance(payload, Mapping):
        return None
    if payload.get("schema") != _PROJECT_EXTENSION_CACHE_SCHEMA:
        return None
    cached_signatures = _extension_cache_pairs(payload.get("signatures"))
    keys = _extension_cache_pairs(payload.get("keys"))
    publications_raw = payload.get("publications")
    if expected_keys is None or cached_signatures != signatures or keys is None or keys != expected_keys or not isinstance(publications_raw, list):
        return None
    publications: list[tuple[str, str, tuple[tuple[str, str], ...]]] = []
    for row in publications_raw:
        if not isinstance(row, Mapping):
            return None
        coordinate = row.get("coordinate")
        fingerprint = row.get("manifest_fingerprint")
        publication_keys = _extension_cache_pairs(row.get("keys"))
        if not isinstance(coordinate, str) or not coordinate or not isinstance(fingerprint, str) or not fingerprint or publication_keys is None:
            return None
        publications.append((coordinate, fingerprint, publication_keys))
    verified_keys = tuple(dict.fromkeys(key for _coordinate, _fingerprint, publication_keys in publications for key in publication_keys))
    if verified_keys != keys:
        return None
    return _ProjectExtensionInstall(
        keys=keys,
        publications=tuple(publications),
    )


def _project_extension_descriptor_keys(
    roots: Sequence[Path],
) -> tuple[tuple[str, str], ...] | None:
    """Read exact manifest keys used only to validate derived cache receipts."""

    from heavenbase.utils import load_yaml

    keys: list[tuple[str, str]] = []
    try:
        for root in roots:
            payload = load_yaml(
                str(_project_extension_descriptor_path(root)),
                strict=True,
            )
            if not isinstance(payload, Mapping):
                return None
            items = payload.get("items")
            if not isinstance(items, list) or not items:
                return None
            for item in items:
                if not isinstance(item, Mapping):
                    return None
                kind = item.get("kind")
                identifier = item.get("identifier")
                if not isinstance(kind, str) or not kind or not isinstance(identifier, str) or not identifier:
                    return None
                keys.append((kind, identifier))
    except (OSError, TypeError, ValueError):
        return None
    return tuple(keys)


def _write_project_extension_install_cache(
    path: Path,
    signatures: tuple[tuple[str, str], ...],
    installed: _ProjectExtensionInstall,
) -> None:
    """Atomically publish one non-authoritative extension install receipt."""

    from heavenbase.utils import dumps_json

    payload = {
        "schema": _PROJECT_EXTENSION_CACHE_SCHEMA,
        "signatures": [list(row) for row in signatures],
        "keys": [list(row) for row in installed.keys],
        "publications": [
            {
                "coordinate": coordinate,
                "manifest_fingerprint": manifest_fingerprint,
                "keys": [list(key) for key in keys],
            }
            for coordinate, manifest_fingerprint, keys in installed.publications
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(
            f"{dumps_json(payload, sort_keys=True, indent=2).rstrip()}\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _extension_cache_pairs(
    value: object,
) -> tuple[tuple[str, str], ...] | None:
    """Decode exact two-string cache rows without trusting derived state."""

    if not isinstance(value, list):
        return None
    rows: list[tuple[str, str]] = []
    for row in value:
        if not isinstance(row, list) or len(row) != 2 or not all(isinstance(item, str) and bool(item) for item in row):
            return None
        rows.append((row[0], row[1]))
    return tuple(rows)


def _extension_install_is_current(
    resolver: object,
    cached: _ProjectExtensionInstall,
) -> bool:
    inspect_records = getattr(resolver, "inspect", None)
    if not callable(inspect_records):
        return False
    for coordinate, manifest_fingerprint, keys in cached.publications:
        if not keys:
            return False
        for kind, identifier in keys:
            rows = inspect_records(
                kind,
                identifier,
                include_inactive=True,
            )
            if not rows:
                return False
            record = rows[0].get("record")
            meta = record.get("meta") if isinstance(record, Mapping) else None
            installation = meta.get("installation") if isinstance(meta, Mapping) else None
            if not isinstance(installation, Mapping):
                return False
            if installation.get("coordinate") != coordinate:
                return False
            if installation.get("manifest_fingerprint") != manifest_fingerprint:
                return False
    return True


def _project_coordinate_part(project_id: str) -> str:
    value = re.sub(r"[^a-z0-9_-]+", "-", project_id.strip().lower()).strip("-_")
    if not value:
        raise ProjectFamilySpecError(f"Project id {project_id!r} cannot form a HeavenBase module coordinate.")
    return value


def _module_folder_digest(root: Path) -> str:
    if not root.is_dir():
        raise ProjectFamilySpecError(f"Project extension folder does not exist: {root}")
    descriptor = _project_extension_descriptor_path(root)
    files: list[tuple[str, Path]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise ProjectFamilySpecError(f"Project extension folders must not contain symbolic links: {path}")
        if not path.is_file():
            continue
        relative_path = path.relative_to(root)
        if relative_path.parts and relative_path.parts[0] == ".paradev":
            if path != descriptor:
                continue
            relative = "meta.yaml"
        else:
            relative = relative_path.as_posix()
        files.append((relative, path))
    digest = sha256()
    for relative, path in sorted(files, key=lambda item: item[0]):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _project_extension_descriptor_path(root: Path) -> Path:
    """Return one unambiguous visible or hidden extension descriptor."""

    visible = root / "meta.yaml"
    hidden = root / _PROJECT_EXTENSION_HIDDEN_DESCRIPTOR
    visible_exists = visible.is_file()
    hidden_exists = hidden.is_file()
    if visible_exists and hidden_exists:
        raise ProjectFamilySpecError(
            f"{root} contains both meta.yaml and " f"{_PROJECT_EXTENSION_HIDDEN_DESCRIPTOR.as_posix()}; keep exactly " "one extension descriptor."
        )
    if hidden_exists:
        return hidden
    if visible_exists:
        return visible
    raise ProjectFamilySpecError(f"{root} must contain either meta.yaml or " f"{_PROJECT_EXTENSION_HIDDEN_DESCRIPTOR.as_posix()}.")


@contextmanager
def _installable_project_extension(root: Path) -> Iterator[Path]:
    """Yield an exact HeavenBase module folder for one project extension."""

    descriptor = _project_extension_descriptor_path(root)
    if descriptor.parent == root:
        yield root
        return

    expected_digest = _module_folder_digest(root)
    with tempfile.TemporaryDirectory(prefix="paradev-extension-") as temporary:
        staged = Path(temporary) / root.name
        shutil.copytree(
            root,
            staged,
            symlinks=True,
            ignore=shutil.ignore_patterns(".paradev"),
        )
        shutil.copy2(descriptor, staged / "meta.yaml")
        source_digest = _module_folder_digest(root)
        staged_digest = _module_folder_digest(staged)
        if source_digest != expected_digest or staged_digest != expected_digest:
            raise ProjectFamilySpecError(f"Project extension {root} changed while ParaDev staged its " "hidden descriptor for HeavenBase installation.")
        yield staged


def _resolved_build_item(
    kind: str,
    identifier: str,
    resolved: object,
    source: str | Path,
) -> object:
    if kind == PROJECT_BUILD_FAMILY_KIND and isinstance(resolved, Mapping):
        family = resolved.get("family")
        declaration = resolved.get("declaration")
        if not isinstance(family, str) or not family.strip() or not isinstance(declaration, Mapping):
            raise ProjectFamilySpecError(f"{source} inline build family {identifier!r} requires family and declaration mappings.")
        return project_family_specs({family: dict(declaration)}, source)[0]
    item = resolved
    if inspect.isclass(item):
        item = item()
    elif callable(item) and not any(getattr(item, attribute, None) for attribute in ("family", "artifact_type", "postprocessor_id")):
        item = item()
    if kind == PROJECT_BUILD_FAMILY_KIND and not getattr(item, "family", None):
        raise ProjectFamilySpecError(f"{source} build family {identifier!r} does not define family.")
    if kind == PROJECT_BUILD_WRITER_KIND and not getattr(item, "artifact_type", None):
        raise ProjectFamilySpecError(f"{source} build writer {identifier!r} does not define artifact_type.")
    if kind == PROJECT_BUILD_POSTPROCESSOR_KIND and not getattr(item, "postprocessor_id", None):
        raise ProjectFamilySpecError(f"{source} build postprocessor {identifier!r} does not define postprocessor_id.")
    if kind == PROJECT_DIAGRAM_PROVIDER_KIND:
        from .diagrams import ModuleDiagramProvider

        if not isinstance(item, ModuleDiagramProvider):
            raise ProjectFamilySpecError(f"{source} diagram provider {identifier!r} must resolve to " "ModuleDiagramProvider.")
    return item


def apply_project_python_modules(
    registry: BuildRegistry,
    module_paths: Sequence[Path],
    project_root: Path,
    source: str | Path,
) -> BuildRegistry:
    """Register project-local Python modules in an isolated import namespace.

    Project modules can use package-relative imports for sibling dependencies.
    The project root remains temporarily importable for older absolute imports,
    but matching absolute module names are quarantined between project loads.

    Args:
        registry (BuildRegistry): Registry receiving project family declarations.
        module_paths (Sequence[Path]): Python registration modules under the project root.
        project_root (Path): Root used to isolate project package identities.
        source (str | Path): Manifest source used in contextual validation errors.

    Returns:
        BuildRegistry: Registry returned by the final registration module.

    Raises:
        ProjectFamilySpecError: If a module cannot load or register its families.
    """

    if not module_paths:
        return registry
    root = project_root.resolve()
    with _PROJECT_MODULE_IMPORT_LOCK, _without_project_bytecode():
        namespace = _project_module_namespace(root)
        absolute_roots = _project_absolute_module_roots(module_paths, root)
        previous_absolute_modules = _detach_absolute_project_modules(absolute_roots)
        root_text = str(root)
        inserted = root_text not in sys.path
        if inserted:
            sys.path.insert(0, root_text)
        _clear_project_module_namespace(namespace)
        _register_project_module_namespace(namespace, root)
        try:
            for index, module_path in enumerate(module_paths):
                registry = _apply_project_python_module(registry, module_path, index, source, root, namespace)
        except Exception:
            _clear_project_module_namespace(namespace)
            raise
        finally:
            _restore_absolute_project_modules(absolute_roots, previous_absolute_modules)
            if inserted and root_text in sys.path:
                sys.path.remove(root_text)
    return registry


@contextmanager
def _without_project_bytecode() -> Iterator[None]:
    """Keep temporary project imports from polluting the project source tree."""

    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        yield
    finally:
        sys.dont_write_bytecode = previous


def _apply_project_python_module(
    registry: BuildRegistry,
    path: Path,
    index: int,
    source: str | Path,
    project_root: Path,
    namespace: str,
) -> BuildRegistry:
    module = _import_project_python_module(path, index, source, project_root, namespace)
    register = getattr(module, "register", None)
    if not callable(register):
        raise ProjectFamilySpecError(f"{source} python_modules[{index}] {path} must define callable register(registry).")
    try:
        result = register(registry)
    except Exception as error:
        raise ProjectFamilySpecError(f"{source} python_modules[{index}] {path} register(registry) failed: {error}") from error
    if result is None:
        return registry
    if isinstance(result, BuildRegistry):
        return result
    raise ProjectFamilySpecError(f"{source} python_modules[{index}] {path} register(registry) must return None or BuildRegistry.")


def _import_project_python_module(
    path: Path,
    index: int,
    source: str | Path,
    project_root: Path,
    namespace: str,
) -> ModuleType:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(project_root)
    except ValueError as error:
        raise ProjectFamilySpecError(f"{source} python_modules[{index}] {path} must stay under the project root.") from error
    parts = relative.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    module_name = ".".join((namespace, *parts))
    root_package = not parts
    cached = sys.modules.get(module_name)
    if isinstance(cached, ModuleType) and not root_package:
        return cached
    parent_name = module_name.rpartition(".")[0]
    if parent_name:
        importlib.import_module(parent_name)
    cached = sys.modules.get(module_name)
    if isinstance(cached, ModuleType) and not root_package:
        return cached
    search_locations = [str(resolved.parent)] if relative.name == "__init__.py" else None
    spec = importlib.util.spec_from_file_location(module_name, resolved, submodule_search_locations=search_locations)
    if spec is None or spec.loader is None:
        raise ProjectFamilySpecError(f"{source} python_modules[{index}] {path} cannot be imported.")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(spec.name, _MISSING_MODULE)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        if previous is _MISSING_MODULE:
            sys.modules.pop(spec.name, None)
        else:
            sys.modules[spec.name] = previous  # type: ignore[assignment]
        raise ProjectFamilySpecError(f"{source} python_modules[{index}] {path} cannot be imported: {error}") from error
    return module


def _project_module_namespace(project_root: Path) -> str:
    root_key = sha256(str(project_root).encode("utf-8")).hexdigest()[:16]
    return f"_paradev_project_{root_key}"


def _clear_project_module_namespace(namespace: str) -> None:
    for module_name in tuple(sys.modules):
        if module_name == namespace or module_name.startswith(f"{namespace}."):
            sys.modules.pop(module_name, None)
    importlib.invalidate_caches()


def _register_project_module_namespace(namespace: str, project_root: Path) -> None:
    spec = importlib.machinery.ModuleSpec(namespace, loader=None, is_package=True)
    spec.submodule_search_locations = [str(project_root)]
    sys.modules[namespace] = importlib.util.module_from_spec(spec)


def _project_absolute_module_roots(module_paths: Sequence[Path], project_root: Path) -> tuple[str, ...]:
    roots: set[str] = set()
    relatives: list[Path] = []
    for path in module_paths:
        try:
            relative = path.resolve().relative_to(project_root)
        except ValueError:
            continue
        relatives.append(relative)
        if len(relative.parts) > 1 and relative.parts[0].isidentifier():
            roots.add(relative.parts[0])
    if any(len(relative.parts) == 1 for relative in relatives):
        roots.update(path.stem for path in project_root.glob("*.py") if path.stem.isidentifier())
    return tuple(sorted(roots))


def _detach_absolute_project_modules(
    roots: Sequence[str],
) -> dict[str, ModuleType | None]:
    previous: dict[str, ModuleType | None] = {}
    for module_name in tuple(sys.modules):
        if any(module_name == root or module_name.startswith(f"{root}.") for root in roots):
            previous[module_name] = sys.modules.pop(module_name)
    return previous


def _restore_absolute_project_modules(roots: Sequence[str], previous: Mapping[str, ModuleType | None]) -> None:
    for module_name in tuple(sys.modules):
        if any(module_name == root or module_name.startswith(f"{root}.") for root in roots):
            sys.modules.pop(module_name, None)
    sys.modules.update(previous)


def _family_spec(family: str, declaration: Mapping[object, object], source: str | Path) -> ProjectFamilySpec:
    label = f"families.{family}"
    if "retired_families" in declaration:
        raise ProjectFamilySpecError(
            f"{source} {label}.retired_families is no longer a compiler "
            "setting; project extensions declare publication replacements in "
            "hidden Registry metadata."
        )
    kind = _optional_string(declaration.get("kind"), f"{label}.kind", source) or "simple_source"
    visible = _optional_bool(declaration.get("visible"), True, f"{label}.visible", source)
    presentation = _declared_family_presentation(
        declaration.get("presentation"),
        label,
        source,
    )
    replaces_registered_family = _optional_bool(
        declaration.get("replaces_registered_family"),
        False,
        f"{label}.replaces_registered_family",
        source,
    )
    if kind not in {"simple_source", "collection_source", "routed_source"}:
        raise ProjectFamilySpecError(f"{source} {label}.kind must be one of: collection_source, routed_source, simple_source.")
    if kind == "routed_source":
        if "collection_source_slots" in declaration:
            raise ProjectFamilySpecError(f"{source} {label}.collection_source_slots is only valid for collection_source families.")
        templates = _templates(declaration.get("templates"), label, source) if "templates" in declaration else {}
        sprite_slots = _strings(declaration.get("sprite_slots", ()), f"{label}.sprite_slots", source)
        _validate_routed_family_templates(templates, label, source)
        routes = _routes(declaration.get("routes"), label, source)
        default_route = _optional_string(
            declaration.get("default_route"),
            f"{label}.default_route",
            source,
        )
        if default_route is not None and default_route not in routes:
            raise ProjectFamilySpecError(f"{source} {label}.default_route names unknown route {default_route!r}.")
        _validate_sprite_templates(kind, templates, sprite_slots, label, source, routes=routes)
        return ProjectFamilySpec(
            family=family,
            kind=kind,
            visible=visible,
            presentation=presentation,
            replaces_registered_family=replaces_registered_family,
            source_slots=_source_slots(declaration.get("source_slots", ()), label, "source_slots", source),
            metadata_keys=_strings(declaration.get("metadata_keys", ()), f"{label}.metadata_keys", source),
            settings_keys=_strings(declaration.get("settings_keys", ()), f"{label}.settings_keys", source),
            settings_values=_settings_values(
                declaration.get("settings_values", {}),
                f"{label}.settings_values",
                source,
            ),
            required_settings=_strings(
                declaration.get("required_settings", ()),
                f"{label}.required_settings",
                source,
            ),
            required_loc_keys=_required_loc_keys(
                declaration.get("required_loc_keys", ()),
                f"{label}.required_loc_keys",
                source,
            ),
            title_loc_keys=_optional_title_loc_keys(
                declaration,
                label,
                source,
            ),
            asset_constraints=_asset_constraints(declaration.get("asset_constraints"), label, source),
            default_assets=_default_assets(declaration.get("default_assets"), label, source),
            settings_normalizers=_settings_normalizers(declaration.get("settings_normalizers"), label, source),
            route_setting=_route_setting(declaration.get("route_setting"), label, source),
            default_route=default_route,
            routes=routes,
            sprite_gfx_path_template=templates.get("sprite_gfx"),
            sprite_name_template=templates.get("sprite_name"),
            sprite_slots=sprite_slots,
        )
    templates = _templates(declaration.get("templates"), label, source)
    sprite_slots = _strings(declaration.get("sprite_slots", ()), f"{label}.sprite_slots", source)
    if "routes" in declaration:
        raise ProjectFamilySpecError(f"{source} {label}.routes is only valid for routed_source families.")
    if kind == "simple_source" and "module_pdx" in templates:
        raise ProjectFamilySpecError(f"{source} {label}.templates.module_pdx is only valid for collection_source families.")
    if kind == "simple_source" and "collection_source_slots" in declaration:
        raise ProjectFamilySpecError(f"{source} {label}.collection_source_slots is only valid for collection_source families.")
    _validate_sprite_templates(kind, templates, sprite_slots, label, source)
    if kind == "collection_source" and "pdx" not in templates:
        raise ProjectFamilySpecError(f"{source} {label}.templates.pdx must be defined for collection_source families.")
    _validate_family_templates(kind, templates, label, source)
    return ProjectFamilySpec(
        family=family,
        kind=kind,
        visible=visible,
        presentation=presentation,
        replaces_registered_family=replaces_registered_family,
        source_slots=_source_slots(declaration.get("source_slots", ()), label, "source_slots", source),
        collection_source_slots=_source_slots(
            declaration.get("collection_source_slots", ()),
            label,
            "collection_source_slots",
            source,
        ),
        metadata_keys=_strings(declaration.get("metadata_keys", ()), f"{label}.metadata_keys", source),
        settings_keys=_strings(declaration.get("settings_keys", ()), f"{label}.settings_keys", source),
        settings_values=_settings_values(declaration.get("settings_values", {}), f"{label}.settings_values", source),
        required_settings=_strings(
            declaration.get("required_settings", ()),
            f"{label}.required_settings",
            source,
        ),
        required_loc_keys=_required_loc_keys(
            declaration.get("required_loc_keys", ()),
            f"{label}.required_loc_keys",
            source,
        ),
        title_loc_keys=_optional_title_loc_keys(
            declaration,
            label,
            source,
        ),
        asset_constraints=_asset_constraints(declaration.get("asset_constraints"), label, source),
        default_assets=_default_assets(declaration.get("default_assets"), label, source),
        settings_normalizers=_settings_normalizers(declaration.get("settings_normalizers"), label, source),
        pdx_path_template=templates.get("pdx"),
        module_pdx_path_template=templates.get("module_pdx"),
        loc_path_template=templates.get("loc"),
        copy_path_template=templates.get("copy"),
        sprite_gfx_path_template=templates.get("sprite_gfx"),
        sprite_name_template=templates.get("sprite_name"),
        sprite_slots=sprite_slots,
    )


def _family(spec: ProjectFamilySpec, source: str | Path) -> SimpleSourceFamily | CollectionSourceFamily | RoutedSourceFamily:
    if spec.kind == "simple_source":
        return SimpleSourceFamily(
            family=spec.family,
            pdx_path_template=spec.pdx_path_template,
            loc_path_template=spec.loc_path_template,
            copy_path_template=spec.copy_path_template,
            sprite_gfx_path_template=spec.sprite_gfx_path_template,
            sprite_name_template=spec.sprite_name_template,
            sprite_slots=spec.sprite_slots,
            source_slots=spec.source_slots,
            metadata_keys=spec.metadata_keys,
            settings_keys=spec.settings_keys,
            settings_values=spec.settings_values,
            required_settings=spec.required_settings,
            required_loc_keys=spec.required_loc_keys,
            title_loc_keys=spec.title_loc_keys,
            asset_constraints=spec.asset_constraints,
            default_assets=spec.default_assets,
            settings_normalizers=spec.settings_normalizers,
            visible=spec.visible,
            presentation=spec.presentation,
        )
    if spec.kind == "routed_source":
        return RoutedSourceFamily(
            family=spec.family,
            routes=spec.routes,
            settings_key=spec.route_setting,
            default_route=spec.default_route,
            source_slots=spec.source_slots,
            metadata_keys=spec.metadata_keys,
            settings_keys=spec.settings_keys,
            settings_values=spec.settings_values,
            required_settings=spec.required_settings,
            required_loc_keys=spec.required_loc_keys,
            title_loc_keys=spec.title_loc_keys,
            asset_constraints=spec.asset_constraints,
            default_assets=spec.default_assets,
            settings_normalizers=spec.settings_normalizers,
            sprite_gfx_path_template=spec.sprite_gfx_path_template,
            sprite_name_template=spec.sprite_name_template,
            sprite_slots=spec.sprite_slots,
            visible=spec.visible,
            presentation=spec.presentation,
        )
    if spec.kind == "collection_source" and spec.pdx_path_template:
        return CollectionSourceFamily(
            family=spec.family,
            pdx_path_template=spec.pdx_path_template,
            module_pdx_path_template=spec.module_pdx_path_template,
            loc_path_template=spec.loc_path_template,
            copy_path_template=spec.copy_path_template,
            source_slots=spec.source_slots,
            collection_source_slots=spec.collection_source_slots,
            metadata_keys=spec.metadata_keys,
            settings_keys=spec.settings_keys,
            settings_values=spec.settings_values,
            required_settings=spec.required_settings,
            required_loc_keys=spec.required_loc_keys,
            title_loc_keys=spec.title_loc_keys,
            asset_constraints=spec.asset_constraints,
            default_assets=spec.default_assets,
            settings_normalizers=spec.settings_normalizers,
            visible=spec.visible,
            presentation=spec.presentation,
        )
    raise ProjectFamilySpecError(f"{source} families.{spec.family}.kind must be one of: collection_source, routed_source, simple_source.")


def _declared_family_presentation(
    raw: object,
    label: str,
    source: str | Path,
) -> FamilyPresentation | None:
    """Decode optional manifest-local family presentation metadata."""

    if raw is None:
        return None
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label}.presentation must be a mapping.")
    try:
        return family_presentation_from_mapping(raw)
    except (TypeError, ValueError) as error:
        raise ProjectFamilySpecError(f"{source} {label}.presentation is invalid: {error}") from error


def _routes(raw: object, label: str, source: str | Path) -> dict[str, SourceRoute]:
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label}.routes must be a mapping of route id to artifact templates.")
    routes: dict[str, SourceRoute] = {}
    for route, templates in sorted(raw.items()):
        route_id = _required_string(route, f"{label}.routes key", source)
        route_templates, emits_artifacts = _route_templates(templates, f"{label}.routes.{route_id}", source)
        routes[route_id] = SourceRoute(
            pdx_path_template=route_templates.get("pdx"),
            loc_path_template=route_templates.get("loc"),
            copy_path_template=route_templates.get("copy"),
            emits_artifacts=emits_artifacts,
        )
    if not routes:
        raise ProjectFamilySpecError(f"{source} {label}.routes must define at least one route.")
    return routes


def _route_templates(raw: object, label: str, source: str | Path) -> tuple[dict[str, str], bool]:
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label} must be a mapping.")
    emits_artifacts = raw.get("emits_artifacts", True)
    if type(emits_artifacts) is not bool:
        raise ProjectFamilySpecError(f"{source} {label}.emits_artifacts must be a boolean.")
    templates: dict[str, str] = {}
    for key in ("pdx", "loc", "copy"):
        value = raw.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            raise ProjectFamilySpecError(f"{source} {label}.{key} must be a non-empty string.")
        template = value.strip()
        _validate_template_fields(template, f"{label}.{key}", _MODULE_TEMPLATE_FIELDS, source)
        templates[key] = template
    if emits_artifacts and not templates:
        raise ProjectFamilySpecError(f"{source} {label} must define at least one of: pdx, loc, copy.")
    if not emits_artifacts and templates:
        raise ProjectFamilySpecError(f"{source} {label} cannot define artifact templates when emits_artifacts is false.")
    return templates, emits_artifacts


def _route_setting(raw: object, label: str, source: str | Path) -> str:
    value = _optional_string(raw, f"{label}.route_setting", source) or "settings.subtype"
    if value.startswith("settings."):
        value = value.removeprefix("settings.")
    if "." in value or not value:
        raise ProjectFamilySpecError(f"{source} {label}.route_setting must name a key under settings.")
    return value


def _validate_sprite_templates(
    kind: str,
    templates: Mapping[str, str],
    sprite_slots: tuple[str, ...],
    label: str,
    source: str | Path,
    *,
    routes: Mapping[str, SourceRoute] | None = None,
) -> None:
    sprite_keys = {"sprite_gfx", "sprite_name"} & set(templates)
    if kind not in {"simple_source", "routed_source"}:
        if sprite_keys:
            key = sorted(sprite_keys)[0]
            raise ProjectFamilySpecError(f"{source} {label}.templates.{key} is only valid for simple_source and routed_source families.")
        if sprite_slots:
            raise ProjectFamilySpecError(f"{source} {label}.sprite_slots is only valid for simple_source and routed_source families.")
        return
    if not sprite_keys and not sprite_slots:
        return
    if "copy" not in templates:
        if kind == "simple_source":
            raise ProjectFamilySpecError(f"{source} {label}.templates.copy must be defined when sprite templates are declared.")
        if not _routes_have_copy_template(routes or {}):
            raise ProjectFamilySpecError(f"{source} {label}.routes must define at least one copy template when sprite templates are declared.")
    if "sprite_gfx" not in templates:
        raise ProjectFamilySpecError(f"{source} {label}.templates.sprite_gfx must be defined when sprite slots are declared.")
    if "sprite_name" not in templates:
        raise ProjectFamilySpecError(f"{source} {label}.templates.sprite_name must be defined when sprite slots are declared.")
    if not sprite_slots:
        raise ProjectFamilySpecError(f"{source} {label}.sprite_slots must define at least one slot when sprite templates are declared.")


def _routes_have_copy_template(routes: Mapping[str, SourceRoute]) -> bool:
    return any(bool(route.copy_path_template) for route in routes.values())


def _validate_routed_family_templates(templates: Mapping[str, str], label: str, source: str | Path) -> None:
    for key in templates:
        if key in {"sprite_gfx", "sprite_name"}:
            continue
        raise ProjectFamilySpecError(f"{source} {label}.templates.{key} is only valid inside routed_source routes.")
    for key, template in templates.items():
        allowed_fields = _SPRITE_GFX_TEMPLATE_FIELDS if key == "sprite_gfx" else _SPRITE_NAME_TEMPLATE_FIELDS
        _validate_template_fields(template, f"{label}.templates.{key}", allowed_fields, source)


def _validate_family_templates(kind: str, templates: Mapping[str, str], label: str, source: str | Path) -> None:
    if kind == "simple_source":
        fields_by_key = {
            "pdx": _MODULE_TEMPLATE_FIELDS,
            "loc": _MODULE_TEMPLATE_FIELDS,
            "copy": _MODULE_TEMPLATE_FIELDS,
            "sprite_gfx": _SPRITE_GFX_TEMPLATE_FIELDS,
            "sprite_name": _SPRITE_NAME_TEMPLATE_FIELDS,
        }
    else:
        fields_by_key = {
            "pdx": _COLLECTION_TEMPLATE_FIELDS,
            "module_pdx": _MODULE_TEMPLATE_FIELDS,
            "loc": _COLLECTION_MEMBER_TEMPLATE_FIELDS,
            "copy": _COLLECTION_MEMBER_TEMPLATE_FIELDS,
        }
    for key, template in templates.items():
        allowed_fields = fields_by_key.get(key)
        if allowed_fields is None:
            continue
        _validate_template_fields(template, f"{label}.templates.{key}", allowed_fields, source)


def _validate_template_fields(template: str, label: str, allowed_fields: frozenset[str], source: str | Path) -> None:
    for template_field in _template_fields(template, label, source):
        if template_field in allowed_fields:
            continue
        allowed = ", ".join(sorted(allowed_fields))
        raise ProjectFamilySpecError(f"{source} {label} uses unknown template field {template_field!r}; supported fields: {allowed}.")


def _template_fields(template: str, label: str, source: str | Path) -> tuple[str, ...]:
    fields: list[str] = []
    try:
        parsed = tuple(_FORMATTER.parse(template))
    except ValueError as error:
        raise ProjectFamilySpecError(f"{source} {label} must use valid Python format fields: {error}.") from error
    for _literal, field_name, format_spec, _conversion in parsed:
        if field_name is not None:
            if not field_name:
                raise ProjectFamilySpecError(f"{source} {label} must use named template fields.")
            if not field_name.isidentifier():
                raise ProjectFamilySpecError(f"{source} {label} uses unsupported template field {field_name!r}.")
            fields.append(field_name)
        if format_spec:
            fields.extend(_template_fields(format_spec, label, source))
    return tuple(fields)


def _asset_constraints(raw: object, label: str, source: str | Path) -> dict[str, dict[str, object]]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label}.asset_constraints must be a mapping.")
    constraints: dict[str, dict[str, object]] = {}
    for slot, raw_constraint in sorted(raw.items()):
        slot_name = _required_string(slot, f"{label}.asset_constraints key", source)
        if not isinstance(raw_constraint, Mapping):
            raise ProjectFamilySpecError(f"{source} {label}.asset_constraints.{slot_name} must be a mapping.")
        constraint = _asset_constraint(raw_constraint, f"{label}.asset_constraints.{slot_name}", source)
        constraints[slot_name] = constraint
    return constraints


def _default_assets(raw: object, label: str, source: str | Path) -> dict[str, dict[str, object]]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label}.default_assets must be a mapping.")
    assets: dict[str, dict[str, object]] = {}
    for slot, declaration in sorted(raw.items()):
        if not isinstance(slot, str) or not slot.strip():
            raise ProjectFamilySpecError(f"{source} {label}.default_assets keys must be non-empty slot names.")
        slot_name = slot.strip()
        assets[slot_name] = _default_asset(declaration, f"{label}.default_assets.{slot_name}", source)
    return assets


def _default_asset(raw: object, label: str, source: str | Path) -> dict[str, object]:
    if isinstance(raw, str):
        path = _default_asset_path(raw, f"{label}.path", source)
        return {"path": path}
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label} must be a string path or mapping.")
    asset: dict[str, object] = {}
    title = raw.get("title")
    if title is not None:
        asset["title"] = _required_string(title, f"{label}.title", source)
    path = raw.get("path")
    if path is not None:
        asset["path"] = _default_asset_path(path, f"{label}.path", source)
    source_value = raw.get("source")
    if source_value is not None:
        asset["source"] = _required_string(source_value, f"{label}.source", source)
    asset_id = raw.get("asset_id")
    if asset_id is not None:
        asset["asset_id"] = _required_string(asset_id, f"{label}.asset_id", source)
    editable = raw.get("editable")
    if editable is not None:
        if type(editable) is not bool:
            raise ProjectFamilySpecError(f"{source} {label}.editable must be a boolean.")
        asset["editable"] = editable
    if "path" not in asset and "asset_id" not in asset:
        raise ProjectFamilySpecError(f"{source} {label} must define path or asset_id.")
    return asset


def _default_asset_path(raw: object, label: str, source: str | Path) -> str:
    value = _required_string(raw, label, source)
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ProjectFamilySpecError(f"{source} {label} must be relative and stay inside the project.")
    return path.as_posix()


def _asset_constraint(raw: Mapping[object, object], label: str, source: str | Path) -> dict[str, object]:
    constraint: dict[str, object] = {}
    formats = _asset_formats(raw.get("formats", raw.get("format")), f"{label}.formats", source)
    if formats:
        constraint["formats"] = formats
    for key in ("width", "height"):
        value = raw.get(key)
        if value is None:
            continue
        if type(value) is not int or value <= 0:
            raise ProjectFamilySpecError(f"{source} {label}.{key} must be a positive integer.")
        constraint[key] = value
    if not constraint:
        raise ProjectFamilySpecError(f"{source} {label} must define at least one of: formats, width, height.")
    return constraint


def _asset_formats(raw: object, label: str, source: str | Path) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, str):
        values = (raw,)
    elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        values = tuple(raw)
    else:
        raise ProjectFamilySpecError(f"{source} {label} must be a string or list of strings.")
    formats: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ProjectFamilySpecError(f"{source} {label}[{index}] must be a non-empty string.")
        formats.append(value.strip().lower().lstrip("."))
    return tuple(sorted(set(formats)))


def _settings_normalizers(raw: object, label: str, source: str | Path) -> dict[str, Callable[[object], object]]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label}.settings_normalizers must be a mapping.")
    normalizers: dict[str, Callable[[object], object]] = {}
    for key, name in sorted(raw.items()):
        setting = _required_string(key, f"{label}.settings_normalizers key", source)
        strategy = _required_string(name, f"{label}.settings_normalizers.{setting}", source)
        if strategy != "lower_snake":
            raise ProjectFamilySpecError(f"{source} {label}.settings_normalizers.{setting} must be one of: lower_snake.")
        normalizers[setting] = _lower_snake_setting
    return normalizers


def _lower_snake_setting(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("must be a string")
    parts: list[str] = []
    current: list[str] = []
    for char in value.strip().lower():
        if char.isalnum():
            current.append(char)
            continue
        if current:
            parts.append("".join(current))
            current = []
    if current:
        parts.append("".join(current))
    return "_".join(parts)


def _templates(raw: object, label: str, source: str | Path) -> dict[str, str]:
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label}.templates must be a mapping.")
    templates: dict[str, str] = {}
    for key in ("pdx", "module_pdx", "loc", "copy", "sprite_gfx", "sprite_name"):
        value = raw.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            raise ProjectFamilySpecError(f"{source} {label}.templates.{key} must be a non-empty string.")
        templates[key] = value.strip()
    if not templates:
        raise ProjectFamilySpecError(f"{source} {label}.templates must define at least one of: pdx, loc, copy, sprite_gfx, sprite_name.")
    return templates


def _source_slots(raw: object, label: str, key: str, source: str | Path) -> tuple[Slot, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ProjectFamilySpecError(f"{source} {label}.{key} must be a list of slot mappings.")
    slots: list[Slot] = []
    for index, item in enumerate(raw):
        slot_label = f"{label}.{key}[{index}]"
        if not isinstance(item, Mapping):
            raise ProjectFamilySpecError(f"{source} {slot_label} must be a mapping.")
        name = _required_string(item.get("name"), f"{slot_label}.name", source)
        match = _required_string(item.get("match"), f"{slot_label}.match", source)
        regex = _optional_bool(item.get("regex"), False, f"{slot_label}.regex", source)
        if regex:
            _validate_regex(match, f"{slot_label}.match", source)
        if slot_match_escapes_root(match, regex=regex):
            raise ProjectFamilySpecError(f"{source} {slot_label}.match must be relative and stay under the source root.")
        kind = _optional_string(item.get("kind"), f"{slot_label}.kind", source)
        authoring_path = _optional_string(
            item.get("authoring_path"),
            f"{slot_label}.authoring_path",
            source,
        )
        if authoring_path is not None:
            if kind != "copy":
                raise ProjectFamilySpecError(f"{source} {slot_label}.authoring_path requires kind: copy.")
            _validate_slot_authoring_path(
                authoring_path,
                f"{slot_label}.authoring_path",
                source,
            )
        slots.append(
            Slot(
                name=name,
                match=match,
                required=_optional_bool(item.get("required"), False, f"{slot_label}.required", source),
                many=_optional_bool(item.get("many"), False, f"{slot_label}.many", source),
                regex=regex,
                kind=kind,
                shared=_optional_bool(item.get("shared"), False, f"{slot_label}.shared", source),
                authoring_path=authoring_path,
            )
        )
    return tuple(slots)


def _validate_slot_authoring_path(
    value: str,
    label: str,
    source: str | Path,
) -> None:
    allowed_fields = {"extension", "filename", "object_id", "stem"}
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ProjectFamilySpecError(f"{source} {label} must be relative and stay under the module root.")
    try:
        fields = {field_name for _literal, field_name, _format_spec, _conversion in Formatter().parse(value) if field_name is not None}
    except ValueError as error:
        raise ProjectFamilySpecError(f"{source} {label} must use valid format placeholders: {error}.") from error
    unknown = sorted(fields - allowed_fields)
    if unknown:
        raise ProjectFamilySpecError(f"{source} {label} uses unsupported fields: {', '.join(unknown)}. " f"Expected only: {', '.join(sorted(allowed_fields))}.")


def _validate_regex(pattern: str, label: str, source: str | Path) -> None:
    try:
        re.compile(pattern)
    except re.error as error:
        raise ProjectFamilySpecError(f"{source} {label} must be a valid regex: {error}.") from error


def _settings_values(raw: object, label: str, source: str | Path) -> dict[str, tuple[str, ...]]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ProjectFamilySpecError(f"{source} {label} must be a mapping.")
    values: dict[str, tuple[str, ...]] = {}
    for key, raw_values in raw.items():
        if not isinstance(key, str) or not key.strip():
            raise ProjectFamilySpecError(f"{source} {label} keys must be non-empty strings.")
        values[key.strip()] = _strings(raw_values, f"{label}.{key}", source)
    return values


def _required_loc_keys(raw: object, label: str, source: str | Path) -> tuple[str, ...]:
    key_templates = _strings(raw, label, source)
    for template in key_templates:
        _validate_template_fields(template, label, _REQUIRED_LOC_TEMPLATE_FIELDS, source)
    return key_templates


def _optional_title_loc_keys(
    declaration: Mapping[object, object],
    label: str,
    source: str | Path,
) -> tuple[str, ...] | None:
    if "title_loc_keys" not in declaration:
        return None
    raw = declaration["title_loc_keys"]
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ProjectFamilySpecError(f"{source} {label}.title_loc_keys must be a list of strings.")
    keys: list[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, str) or not item.strip():
            raise ProjectFamilySpecError(f"{source} {label}.title_loc_keys[{index}] must be a non-empty string.")
        key = item.strip()
        _validate_template_fields(
            key,
            f"{label}.title_loc_keys",
            _REQUIRED_LOC_TEMPLATE_FIELDS,
            source,
        )
        if key in keys:
            raise ProjectFamilySpecError(f"{source} {label}.title_loc_keys must not contain duplicate templates.")
        keys.append(key)
    return tuple(keys)


def _strings(raw: object, label: str, source: str | Path) -> tuple[str, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ProjectFamilySpecError(f"{source} {label} must be a list of strings.")
    values: list[str] = []
    for index, item in enumerate(raw):
        if not isinstance(item, str) or not item.strip():
            raise ProjectFamilySpecError(f"{source} {label}[{index}] must be a non-empty string.")
        values.append(item.strip())
    return tuple(sorted(set(values)))


def _required_string(raw: object, label: str, source: str | Path) -> str:
    value = _optional_string(raw, label, source)
    if value is None:
        raise ProjectFamilySpecError(f"{source} {label} must be a non-empty string.")
    return value


def _optional_string(raw: object, label: str, source: str | Path) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise ProjectFamilySpecError(f"{source} {label} must be a non-empty string.")
    return raw.strip()


def _optional_bool(raw: object, default: bool, label: str, source: str | Path) -> bool:
    if raw is None:
        return default
    if type(raw) is not bool:
        raise ProjectFamilySpecError(f"{source} {label} must be a boolean.")
    return raw
