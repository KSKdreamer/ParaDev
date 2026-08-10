"""Project discovery and view model contracts for SDK-owned surfaces."""

from __future__ import annotations

import base64
import binascii
import errno
import hashlib
import json
import math
import os
import re
import shutil
import stat
import sys
import tempfile
import time
import unicodedata
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import ExitStack, contextmanager, nullcontext
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from functools import wraps
from inspect import signature
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, BinaryIO, Literal, cast
from uuid import UUID, uuid4

from typing_extensions import TypedDict

from heavenbase.utils import (
    CmdResult,
    cmd,
    delete_dir,
    delete_file,
    dumps_json,
    dumps_yaml,
    load_bin,
    load_txt,
    load_yaml,
    loads_json,
    loads_yaml,
    save_bin,
    save_txt,
    save_yaml,
    sha256hash,
)
from yaml import YAMLError

from paradev._api_table import append_index_entry
from paradev._api_table_markdown import (
    api_reference_markdown,
    api_summary_reference_sections,
    api_table_section,
    code_cell,
    code_list_cell,
    index_row,
    markdown_cell,
)
from paradev._win32_fs import (
    Win32DirectoryAuthority,
    Win32DisplacedRecoveryError,
    Win32FileMetadata,
    Win32FileSizeError,
    Win32FileSnapshot,
    Win32FilesystemUnavailable,
    Win32UnsafePathError,
)
from paradev.build._fs import open_anchored_directory
from paradev.build.slots import match_slot_paths
from paradev.config import CM_PARADEV
from paradev.localization import HOI4_LANGUAGE_ALIASES, canonical_language
from paradev.localization._authoring import (
    MAX_LOCALIZATION_WORKSPACE_ROWS,
    LocalizationSource,
    localization_workspace as project_localization_workspace,
    plan_localization_operation,
)
from paradev.localization._source import parse_source as parse_localization_source
from paradev.pdx import PDXBlock, PDXParseError, PDXScalar
from paradev.portable_paths import (
    portable_authoring_title,
    windows_portable_component_error,
)

from ._diagram_module_recovery import (
    DiagramModuleRecoveryFile,
    DiagramModuleRecoveryJournal,
    DiagramModuleRecoverySource,
    diagram_module_recovery_root,
    read_diagram_module_recovery,
    write_diagram_module_recovery,
)
from ._metadata_cleanup import (
    MODULE_METADATA_CLEANUP_POLICY,
    MetadataCleanupDraft,
    plan_inferred_type_cleanup,
)
from ._source_recovery import (
    SourceDraftRecoveryFile,
    SourceDraftRecoveryJournal,
    SourceDraftRecoveryRename,
    read_source_draft_recovery,
    source_draft_recovery_displaced_path,
    source_draft_recovery_root,
    write_source_draft_recovery,
)
from .architecture import get_architecture_spec
from .copy_roots import (
    CopyRootSpec,
    ProjectCopyRootSpecError,
    copy_root_artifacts,
    merge_copy_root_artifacts,
    project_copy_roots,
)
from .source_forms import (
    apply_source_form_values,
    is_loc_text_form_source,
    is_pdx_form_source,
    loc_text_source_form,
    normalize_source_form_query,
    normalize_source_form_patch,
    pdx_source_form,
    source_form_patch_operations,
)
from .templates import (
    TEMPLATES_SCHEMA,
    ModuleTemplate,
    ProjectTemplateSpecError,
    _module_scaffold_plan_with_system_files,
    collection_scaffold_plan,
    project_module_templates,
    template_index,
)

if os.name == "nt":
    import msvcrt
else:
    import fcntl

if TYPE_CHECKING:
    from paradev.build import (
        Artifact,
        BuildRegistry,
        BuildResult,
        Collection,
        CollectionDiscoveryResult,
        CollectionSourceBundle,
        Diagnostic,
        Module,
        ModuleDiagramModuleCreation,
        ModuleDiagramTextSource,
        ModuleDiscoveryResult,
        ModuleSourceBundle,
        ProjectFamilySpec,
        Slot,
    )
    from paradev.build._fs import AnchoredDirectory

PROJECT_MANIFEST = "paradev.yaml"
PROJECT_SYSTEM_MANIFEST = ".paradev.yaml"
PROJECT_SCHEMA_KEYS = (
    "project_id",
    "title",
    "game",
    "preferred_language",
    "source_roots",
    "output_root",
    "build_root",
)
PROJECT_REQUIRED_SCHEMA_KEYS = (
    "project_id",
    "title",
    "game",
    "source_roots",
    "build_root",
)
HOI4_MOD_ROOT_ENV = "PARADEV_HOI4_MOD_ROOT"
HOI4_MACOS_MOD_ROOT = "~/Documents/Paradox Interactive/Hearts of Iron IV/mod"
HOI4_MOD_ROOT_UNDER_DOCUMENTS = "Paradox Interactive/Hearts of Iron IV/mod"
WINDOWS_DOCUMENTS_FOLDER_ID = UUID("fdd39ad0-238f-46af-adb4-6c85480369c7")
WINDOWS_USER_SHELL_FOLDERS_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
HOI4_LAUNCHER_OWNER_SCHEMA = "paradev.hoi4.launcher-owner.v1"
PROJECT_INSPECTIONS_SCHEMA = "paradev.sdk.inspections.v1"
PROJECT_INSPECTION_INDEX_CATALOG: tuple[dict[str, str], ...] = (
    {
        "id": "kind",
        "contract_path": 'contract["index"]["kind"][kind]',
        "python_helper": "get_project_inspection_selection(kind=kind)",
        "usage": "Inspection kind to compact inspection row offset.",
    },
    {
        "id": "filter",
        "contract_path": 'contract["index"]["filter"][filter_name]',
        "python_helper": 'get_project_inspection_selection(index_name="filter", key=filter_name)',
        "usage": "Filter name to inspection kinds that accept it.",
    },
)
PROJECT_MANIFESTS_SCHEMA = "paradev.build.manifests.v1"
PROJECT_CREATE_SCHEMA = "paradev.project.create.v1"
PROJECT_FIND_SCHEMA = "paradev.project.find.v1"
_BUILD_MUTATION_LOCK_RETRY_SECONDS = 0.05
_BUILD_MUTATION_LOCK_CONTENTION_ERRNOS = frozenset({errno.EACCES, errno.EAGAIN, errno.EDEADLK})
_BUILD_MUTATION_SCOPE_ACTIVE: ContextVar[bool] = ContextVar("paradev_build_mutation_scope_active", default=False)
_SOURCE_DRAFT_TRANSACTION_ACTIVE: ContextVar[bool] = ContextVar(
    "paradev_source_draft_transaction_active",
    default=False,
)
_PROJECT_MUTATION_LOCK_IDENTITIES: ContextVar[frozenset[str]] = ContextVar(
    "paradev_project_mutation_lock_identities",
    default=frozenset(),
)
PROJECTS_SCHEMA = "paradev.sdk.projects.v1"
DESKTOP_STATE_SCHEMA = "paradev.desktop.state.v1"
PROJECT_BROWSER_SCHEMA = "paradev.sdk.project-browser.v1"
MODULE_RENAME_SCHEMA = "paradev.module.rename.v1"
PROJECT_PREFERRED_LANGUAGE_SCHEMA = "paradev.project.preferred-language.v1"
MODULE_REMOVE_SCHEMA = "paradev.module.remove.v1"
MODULE_FILE_SCHEMA = "paradev.module.file.v1"
MODULE_ASSET_SCHEMA = "paradev.module.asset.v1"
MODULE_DRAFT_SCHEMA = "paradev.rest.module_draft.v1"
MODULE_CREATE_BATCH_SCHEMA = "paradev.sdk.module_batch.v1"
MODULE_DUPLICATE_SCHEMA = "paradev.sdk.module_duplicate.v1"
MODULE_METADATA_CLEANUP_SCHEMA = "paradev.sdk.module_metadata_cleanup.v1"
MODULE_COLLECTION_UPDATE_SCHEMA = "paradev.sdk.module_collection_update.v1"
MODULE_ACTIVITY_UPDATE_SCHEMA = "paradev.sdk.module_activity_update.v1"
MODULE_DIAGRAM_SCHEMA = "paradev.sdk.module_diagram.v1"
MODULE_DIAGRAM_EDIT_SCHEMA = "paradev.sdk.module_diagram_edit.v1"
MAX_MODULE_CREATE_BATCH_SIZE = 256

_PROJECT_PREFERRED_LANGUAGE_BY_CANONICAL = {HOI4_LANGUAGE_ALIASES[alias]: alias for alias in ("en", "fr", "de", "ru", "es", "pl", "pt_br", "zh", "ja", "ko")}
MODULE_BATCH_EDIT_REQUEST_SCHEMA = "paradev.module.batch_edit_request.v1"
_ANCHORED_MODULE_MUTATION_SUPPORTED = (
    os.open in os.supports_dir_fd
    and os.mkdir in os.supports_dir_fd
    and os.stat in os.supports_dir_fd
    and os.rename in os.supports_dir_fd
    and shutil.rmtree.avoids_symlink_attacks
    and hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
)
_ANCHORED_SOURCE_DRAFT_MUTATION_SUPPORTED = (
    os.open in os.supports_dir_fd
    and os.stat in os.supports_dir_fd
    and os.unlink in os.supports_dir_fd
    and os.rename in os.supports_dir_fd
    and os.link in os.supports_dir_fd
    and hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
)


def _uses_win32_source_draft_authority() -> bool:
    """Return whether source-draft mutations use retained Win32 handles."""

    return os.name == "nt"


MODULE_BATCH_EDIT_SCHEMA = "paradev.module.batch_edit.v1"
PROJECT_SOURCE_TEXT_SCHEMA = "paradev.rest.source_text.v1"
PROJECT_SOURCE_BINARY_SCHEMA = "paradev.project.source-binary.v1"
PROJECT_SOURCE_FORM_SCHEMA = "paradev.source-form.v1"
PROJECT_SOURCE_FORM_UPDATE_SCHEMA = "paradev.source-form-update.v1"
PROJECT_SOURCE_FORM_UPDATE_BATCH_SCHEMA = "paradev.source-form-update-batch.v1"
PROJECT_DRAFT_APPLY_SCHEMA = "paradev.rest.draft_apply.v1"


def _serialize_project_build_mutation(
    method: Callable[..., object],
) -> Callable[..., object]:
    """Hold source and publication locks across one emitted build snapshot."""

    @wraps(method)
    def wrapped(project: "Project", *args: object, **kwargs: object) -> object:
        emit_artifacts = bool(kwargs.get("emit_artifacts", False))
        emit_manifests = bool(kwargs.get("emit_manifests", False))
        sync_launcher_descriptor = bool(kwargs.get("sync_launcher_descriptor", True))
        if _BUILD_MUTATION_SCOPE_ACTIVE.get() or _SOURCE_DRAFT_TRANSACTION_ACTIVE.get():
            return method(project, *args, **kwargs)
        if not (emit_artifacts or emit_manifests):
            with _project_source_mutation_lock(project):
                _recover_project_source_transactions(project)
                return method(project, *args, **kwargs)
        # Reject an invalid source/output overlap before attempting to acquire
        # both identities. The method validates again while holding the locks
        # so a concurrent path replacement still fails closed.
        _validate_project_build_roots(project)
        roots = _project_build_mutation_roots(
            project,
            include_launcher=emit_artifacts and sync_launcher_descriptor,
        )
        with (
            _project_source_mutation_lock(project),
            _project_build_mutation_lock(*roots),
        ):
            token = _BUILD_MUTATION_SCOPE_ACTIVE.set(True)
            try:
                _recover_project_source_transactions(project)
                return method(project, *args, **kwargs)
            finally:
                _BUILD_MUTATION_SCOPE_ACTIVE.reset(token)

    return wrapped


def _serialize_project_source_mutation(
    method: Callable[..., object],
) -> Callable[..., object]:
    """Serialize SDK source planning and writes against emitted builds."""

    @wraps(method)
    def wrapped(project: "Project", *args: object, **kwargs: object) -> object:
        if _BUILD_MUTATION_SCOPE_ACTIVE.get():
            raise RuntimeError("Project sources cannot be mutated from inside an active emitted build.")
        with _project_source_mutation_lock(project):
            diagram_recovery = Path(diagram_module_recovery_root(str(project.root))) / "recovery.json"
            if _path_entry_exists_lexically(diagram_recovery):
                _recover_project_source_transactions(project)
            return method(project, *args, **kwargs)

    return wrapped


MAX_PROJECT_SOURCE_TEXT_BYTES = 2 * 1024 * 1024
MAX_PROJECT_SOURCE_BINARY_BYTES = 20 * 1024 * 1024
MAX_PROJECT_SOURCE_NESTING_DEPTH = 256
MAX_PROJECT_SOURCE_REPLACEMENT_FILES = 64
MAX_PROJECT_SOURCE_REPLACEMENT_FILE_BYTES = 64 * 1024 * 1024
MAX_PROJECT_SOURCE_REPLACEMENT_TOTAL_BYTES = 128 * 1024 * 1024
MAX_PROJECT_SOURCE_DRAFT_FILES = 256
MAX_PROJECT_SOURCE_DRAFT_BACKUP_BYTES = 256 * 1024 * 1024
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_MODULE_ASSET_IMAGE_SUFFIXES = frozenset({".bmp", ".dds", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".tga", ".webp"})
_SOURCE_BINARY_MIME_TYPES = {
    ".bmp": "image/bmp",
    ".dds": "image/vnd.ms-dds",
    ".gif": "image/gif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".tga": "image/x-tga",
    ".webp": "image/webp",
}
_SOURCE_IMAGE_TARGET_FORMATS = frozenset({"bmp", "dds", "jpeg", "jpg", "tga", "webp"})
_SOURCE_IMAGE_PRIMARY_CONVERTER = "magick"
_SOURCE_IMAGE_LEGACY_CONVERTER = "convert"
_SOURCE_FORM_PROVIDER_FIELDS = frozenset({"contract", "label", "description", "coverage", "query", "sections"})
_SOURCE_FORM_SECTION_FIELDS = frozenset({"id", "label", "description", "controls", "sections"})
_SOURCE_FORM_COVERAGE_FIELDS = frozenset({"truncated", "shown_controls", "total_controls"})
_SOURCE_FORM_CONTROL_FIELDS = frozenset(
    {
        "id",
        "label",
        "description",
        "description_source",
        "control",
        "value",
        "choices",
        "min",
        "max",
        "step",
        "placeholder",
        "multiline",
        "patch",
    }
)
_SOURCE_DRAFT_EXPECTED_ABSENT = object()
_SOURCE_DRAFT_EDIT_FIELDS = frozenset({"path", "text", "expected_size", "expected_mtime_ns"})
_SOURCE_DRAFT_REMOVAL_FIELDS = frozenset({"path", "expected_size", "expected_mtime_ns"})
_SOURCE_DRAFT_REPLACEMENT_FIELDS = frozenset(
    {
        "path",
        "content_base64",
        "content_format",
        "target_format",
        "expected_size",
        "expected_mtime_ns",
        "expected_absent",
    }
)
_SOURCE_DRAFT_MODULE_RENAME_FIELDS = frozenset(
    {
        "module_id",
        "object_id",
        "source_root",
        "title",
    }
)
_SOURCE_FORM_CONTROL_KINDS = frozenset({"readonly", "text", "number", "boolean", "choice"})
_SOURCE_FORM_CHOICE_FIELDS = frozenset({"label", "value"})
COLLECTION_FILE_SCHEMA = "paradev.collection.file.v1"
COLLECTION_CREATE_SCHEMA = "paradev.collection.create.v1"
COLLECTION_RENAME_SCHEMA = "paradev.collection.rename.v1"
COLLECTION_REMOVE_SCHEMA = "paradev.collection.remove.v1"
PROJECT_DISCOVERY_EXCLUDED_ROOTS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
}


@dataclass(frozen=True)
class _SourceDraftBackup:
    path: Path
    backup_path: Path | None
    mode: int | None
    size: int
    content_sha256: str | None


@dataclass(frozen=True)
class _SourceDraftMutation:
    path: Path
    parent_identity: tuple[int, int]
    file_identity: tuple[int, int, int, int] | None
    content_sha256: str | None


@dataclass(frozen=True, slots=True)
class _PreparedModuleRename:
    """One fully validated module-folder rename awaiting its commit point."""

    source_root: Path
    previous_module: "Module"
    module: "Module"
    previous_root: Path
    root: Path
    target_object_id: str
    directory_identity: tuple[int, int]


@dataclass(frozen=True, slots=True)
class _PreparedCollectionRename:
    """One fully validated collection-folder rename awaiting its commit point."""

    source_root: Path
    previous_collection: "Collection"
    previous_root: Path
    root: Path
    target_object_id: str
    directory_identity: tuple[int, int]


@dataclass(frozen=True, slots=True)
class _PreparedCollectionRemoval:
    """One retained collection-folder removal awaiting its commit point."""

    source_root: Path
    previous_collection: "Collection"
    previous_root: Path
    root: Path
    target_object_id: str
    directory_identity: tuple[int, int]
    inventory_digest: str


_PreparedSourceRename = _PreparedModuleRename | _PreparedCollectionRename | _PreparedCollectionRemoval


class _SourceDraftRollbackIncomplete(ValueError):
    """Raised when a source transaction cannot restore every prior file."""

    def __init__(
        self,
        *,
        recovery_path: Path,
        mutation_error: BaseException,
        rollback_errors: Sequence[BaseException],
        possibly_modified_paths: Sequence[Path],
    ) -> None:
        self.recovery_path = recovery_path
        self.mutation_error = mutation_error
        self.rollback_errors = tuple(rollback_errors)
        self.possibly_modified_paths = tuple(possibly_modified_paths)
        rollback_detail = "; ".join(f"{type(error).__name__}: {error}" for error in rollback_errors)
        super().__init__(
            "Source draft transaction failed and rollback was incomplete; " f"recovery data remains at {recovery_path}. " f"Rollback errors: {rollback_detail}"
        )


class _SourceDraftDisplacedRecoveryIncomplete(ValueError):
    """Raised when a guarded mutation cannot restore a displaced target."""

    def __init__(
        self,
        message: str,
        *,
        target_path: Path,
        recovery_path: Path,
        destination_exists: bool,
    ) -> None:
        self.target_path = target_path
        self.recovery_path = recovery_path
        self.destination_exists = destination_exists
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class _ModuleMetadataCleanupEntry:
    """One snapshotted module metadata cleanup decision."""

    module_id: str
    family: str
    source_root: Path
    module_root: Path
    path: Path
    mutation_root: Path
    action: Literal["absent", "unchanged", "update", "remove", "blocked"]
    current_size: int | None = None
    current_mtime_ns: int | None = None
    current_sha256: str | None = None
    content_sha256: str | None = None
    target_exists: bool | None = None
    target_size: int | None = None
    target_sha256: str | None = None
    replacement: bytes | None = field(default=None, repr=False)
    removed_keys: tuple[str, ...] = ()
    diagnostics: tuple[Mapping[str, object], ...] = ()

    @property
    def changed(self) -> bool:
        """Return whether applying this entry mutates its metadata file."""

        return self.action in {"update", "remove"}

    @property
    def blocked(self) -> bool:
        """Return whether this entry prevents the cleanup transaction."""

        return self.action == "blocked"


@dataclass(frozen=True, slots=True)
class _ModuleMetadataCleanupCandidate:
    """One typed module folder found without parsing authored sources."""

    module_id: str
    family: str
    source_root: Path
    module_root: Path


PROJECT_BROWSER_EXCLUDED_ROOTS = {
    "modules",
    "collections",
    "assets",
    "build",
    ".paradev",
    "__pycache__",
}
PROJECT_INSPECTION_METHODS = {
    "inspections": "inspections",
    "assets": "assets",
    "artifacts": "artifacts",
    "build-explain": "build_explain",
    "build-graph": "build_graph",
    "catalog-preview": "catalog_preview",
    "catalog-query": "catalog_query",
    "collections": "collections",
    "dependencies": "dependencies",
    "diagnostics": "diagnostics",
    "families": "families",
    "localization": "localization",
    "manifests": "manifests",
    "modules": "modules",
    "source-map": "source_map",
    "source-slots": "source_slots",
    "sources": "sources",
    "sprites": "sprites",
    "summary": "summary",
}
PROJECT_INSPECTION_CLI_COMMANDS = {
    "catalog-preview": "hb catalog-preview",
    "catalog-query": "hb catalog-query",
}


class ProjectInspectionRow(TypedDict):
    """One project inspection kind row."""

    kind: str
    method: str
    cli_command: str
    filters: list[str]


class ProjectInspectionIndex(TypedDict):
    """Lookup indexes for project inspection rows."""

    kind: dict[str, list[int]]
    filter: dict[str, list[str]]


class ProjectInspectionIndexCatalogRow(TypedDict):
    """Documented index dimension for the project inspection contract."""

    id: str
    contract_path: str
    python_helper: str
    usage: str


class ProjectInspectionContract(TypedDict):
    """Project-independent inspection kind and filter contract."""

    schema: str
    inspections: list[ProjectInspectionRow]
    index: ProjectInspectionIndex


class ProjectInspectionProjectContract(ProjectInspectionContract, total=False):
    """Loaded-project inspection contract with optional project identity."""

    project_id: str


def get_project_inspection_contract(*, project_id: str | None = None) -> ProjectInspectionProjectContract:
    """Return the project inspection kind and filter contract.

    Args:
        project_id: Optional project id to include when the contract is tied to
            a loaded project. Omit it for static surface metadata.

    Returns:
        JSON-safe list of supported `Project.inspect(...)` kinds, direct SDK
        methods, CLI command names, public filters, and lookup indexes.
    """

    rows = _inspection_rows()
    payload = {
        "schema": PROJECT_INSPECTIONS_SCHEMA,
        "inspections": rows,
        "index": _inspection_index(rows),
    }
    if project_id is not None:
        payload["project_id"] = project_id
    return payload


def get_project_inspection_index_catalog() -> list[ProjectInspectionIndexCatalogRow]:
    """Return documented index dimensions for project inspections.

    Returns:
        Copied rows describing the contract path, Python helper, and intended
        lookup use for each project inspection index dimension.
    """

    return [dict(row) for row in PROJECT_INSPECTION_INDEX_CATALOG]


def get_project_inspection_kinds() -> list[str]:
    """Return stable project inspection kinds in contract order.

    Returns:
        Ordered inspection kind ids accepted by `Project.inspect(...)`.
    """

    return [row["kind"] for row in _inspection_rows()]


def get_project_inspection_row(kind: str) -> ProjectInspectionRow:
    """Return one project inspection contract row.

    Args:
        kind: Inspection kind such as `modules`, `sources`, or `build-graph`.

    Returns:
        Copied inspection row with SDK method, CLI command, and filter names.

    Raises:
        ValueError: If the kind is not part of the inspection contract.
    """

    normalized = _inspection_kind(kind)
    for row in _inspection_rows():
        if row["kind"] == normalized:
            return dict(row)
    raise AssertionError(f"inspection kind disappeared from contract: {normalized}")


def get_project_inspection_filter_kinds(filter_name: str) -> list[str]:
    """Return inspection kinds that accept one filter name.

    Args:
        filter_name: Public filter field such as `module_id` or `profile`.

    Returns:
        Copied ordered inspection kind ids that accept the filter.

    Raises:
        KeyError: If the filter is not present in the inspection contract.
    """

    filter_index = get_project_inspection_contract()["index"]["filter"]
    try:
        return list(filter_index[filter_name])
    except KeyError as error:
        known = ", ".join(sorted(filter_index))
        raise KeyError(f"unknown ParaDev project inspection filter {filter_name!r}; expected one of: {known}") from error


def get_project_inspection_selection(
    kind: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> ProjectInspectionProjectContract | ProjectInspectionRow | list[str]:
    """Return the project inspection contract, one row, or one index bucket.

    Args:
        kind: Optional inspection kind such as `modules`, `sources`, or
            `build-graph`.
        index_name: Optional inspection index name. Use `kind` for a row
            lookup or `filter` for the ordered inspection kinds accepting a
            filter.
        key: Optional key inside the selected index.

    Returns:
        A detached inspection contract when no selector is passed, a detached
        inspection row when `kind` is passed or `index_name="kind"`, or a
        copied list of inspection kinds when `index_name="filter"`.

    Raises:
        ValueError: If selectors are ambiguous, incomplete, or name an
            unsupported index.
        KeyError: If a requested filter key is not present.
    """

    index_lookup = index_name is not None or key is not None
    if kind is not None and index_lookup:
        raise ValueError("Pass only one project inspection selector: kind or index_name/key.")
    if index_lookup and (index_name is None or key is None):
        raise ValueError("index_name requires key, and key requires index_name.")
    if kind is not None:
        return get_project_inspection_row(kind)
    if index_name is None:
        return get_project_inspection_contract()
    if index_name == "kind":
        return get_project_inspection_row(key)
    if index_name == "filter":
        return get_project_inspection_filter_kinds(key)
    raise ValueError("Unsupported project inspection index {index!r}; expected one of: filter, kind.".format(index=index_name))


def render_project_inspection_reference_markdown() -> str:
    """Render the project inspection contract as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/project-inspection-reference.md`. The content is
        generated from `get_project_inspection_contract()` so project
        inspection SDK, CLI, REST, MCP, and GUI docs stay aligned.
    """

    contract = get_project_inspection_contract()
    filter_index = contract["index"]["filter"]
    return api_reference_markdown(
        title="Project Inspection Reference",
        source="paradev.sdk.get_project_inspection_contract()",
        regenerate_when="Regenerate this file whenever the project inspection contract changes:",
        command="rtk uv run paradev inspections --markdown > docs/user-manual/project-inspection-reference.md",
        sections=api_summary_reference_sections(
            [
                f"- Inspections / Inspection 数: {len(contract['inspections'])}",
                f"- Filters / Filter 数: {len(filter_index)}",
            ],
            (
                api_table_section(
                    "Index Catalog / Index 目录",
                    ("Index", "Contract Path", "Python Helper", "Use"),
                    _project_inspection_index_catalog_table_rows(),
                ),
                api_table_section(
                    "Inspection Kinds / Inspection Kind 表",
                    ("Kind", "SDK Method", "CLI Command", "Filters"),
                    _project_inspection_kind_table_rows(contract),
                ),
                api_table_section(
                    "Filter Index / Filter 索引",
                    ("Filter", "Inspections", "Kinds"),
                    _project_inspection_filter_index_table_rows(contract),
                ),
            ),
        ),
    )


class ProjectManifestError(ValueError):
    """Raised when a ParaDev project manifest cannot be discovered or loaded."""


class ProjectCreateError(ValueError):
    """Raised when a ParaDev starter project cannot be created."""


@dataclass(frozen=True)
class Project:
    """A loaded ParaDev project boundary.

    Args:
        root: Project root path.
        manifest_path: Path to `paradev.yaml`.
        project_id: Stable project identifier.
        title: Display title.
        game: Target game package identifier.
        preferred_language: Default language alias for authoring templates.
        source_roots: Authored source roots.
        output_root: Game-ready output root.
        build_root: ParaDev build metadata root.
        extension_modules: Project-local HeavenBase module folders.
        python_modules: Project-local Python registry modules.
        family_specs: Project-local declarative family specs.
        template_specs: Project-local source-module authoring templates.
        copy_roots: External or project-local file trees copied into outputs.
        descriptor_metadata: Optional HoI4 descriptor fields from the manifest.
    """

    root: Path
    manifest_path: Path
    project_id: str
    title: str
    game: str
    preferred_language: str
    source_roots: tuple[Path, ...]
    output_root: Path
    build_root: Path
    extension_modules: tuple[Path, ...] = ()
    python_modules: tuple[Path, ...] = ()
    family_specs: tuple["ProjectFamilySpec", ...] = ()
    template_specs: tuple[ModuleTemplate, ...] = ()
    copy_roots: tuple[CopyRootSpec, ...] = ()
    descriptor_metadata: Mapping[str, object] = field(default_factory=dict)

    @classmethod
    def find(cls, path: str | os.PathLike[str] = ".") -> dict[str, object]:
        """Find a ParaDev project from a root or nested path.

        Args:
            path: Project root path or nested path to search upward from.

        Returns:
            JSON-safe discovery payload. Missing or invalid projects return
            `found=False` with diagnostics instead of raising.
        """

        query_path = _query_path(path)
        try:
            project = cls.load(path)
        except ProjectManifestError as error:
            message = str(error)
            return _project_find_payload(
                query_path,
                diagnostics=[
                    {
                        "severity": "error",
                        "code": "project.manifest_missing" if message.startswith(f"Missing {PROJECT_MANIFEST}") else "project.manifest_invalid",
                        "message": message,
                    }
                ],
            )
        return _project_find_payload(query_path, project=project)

    @classmethod
    def create(
        cls,
        path: str | os.PathLike[str],
        *,
        project_id: str | None = None,
        title: str | None = None,
        game: str = "hoi4",
        force: bool = False,
    ) -> "Project":
        """Create and load a starter ParaDev project.

        Args:
            path: Target project root.
            project_id: Optional stable project id. Defaults to the folder name.
            title: Optional display title. Defaults to a title-cased folder name.
            game: Target game package. Only `hoi4` is supported by the starter.
            force: Allow writing into an existing non-empty directory.

        Returns:
            Loaded starter project.

        Raises:
            ProjectCreateError: If the target path or game is unsupported.
        """

        return create_project(path, project_id=project_id, title=title, game=game, force=force)

    @classmethod
    def load(
        cls,
        path: str | os.PathLike[str] = ".",
        *,
        game: str | None = None,
        title: str | None = None,
    ) -> "Project":
        """Discover and load a ParaDev project.

        Args:
            path: Project root or nested path inside a project.
            game: Optional game override for surface adapters.
            title: Optional display-title override for surface adapters.

        Returns:
            Loaded project.

        Raises:
            ProjectManifestError: If `paradev.yaml` is missing or invalid.
        """

        manifest_path = _find_manifest(path)
        root = manifest_path.parent
        manifest = _load_manifest(manifest_path)
        extension_modules = _load_extension_modules(root, manifest_path)
        python_modules = _load_python_modules(manifest, root, manifest_path)
        family_specs = _load_family_specs(manifest, manifest_path)
        template_specs = _load_template_specs(manifest, manifest_path)
        copy_roots = _load_copy_roots(manifest, root, manifest_path)
        descriptor_metadata = _load_descriptor_metadata(manifest, manifest_path)
        project_id = _require_project_id(manifest, manifest_path)
        project_game = game or _require_str(manifest, "game", manifest_path)
        return cls(
            root=root,
            manifest_path=manifest_path,
            project_id=project_id,
            title=title or _require_str(manifest, "title", manifest_path),
            game=project_game,
            preferred_language=_manifest_preferred_language(
                manifest,
                manifest_path,
            ),
            source_roots=tuple(_resolve_path(root, item, "source_roots", manifest_path) for item in _require_source_roots(manifest, manifest_path)),
            output_root=_manifest_output_root(manifest, root, manifest_path, project_id, project_game),
            build_root=_resolve_generated_path(root, _require_str(manifest, "build_root", manifest_path)),
            extension_modules=extension_modules,
            python_modules=python_modules,
            family_specs=family_specs,
            template_specs=template_specs,
            copy_roots=copy_roots,
            descriptor_metadata=descriptor_metadata,
        )

    def to_view(self) -> dict[str, object]:
        """Return a JSON-safe desktop/API view."""

        architecture = get_architecture_spec()
        version = _descriptor_version(self.descriptor_metadata)
        view: dict[str, object] = {
            "project_id": self.project_id,
            "title": self.title,
            "root": str(self.root),
            "manifest": str(self.manifest_path),
            "game": self.game,
            "preferred_language": self.preferred_language,
            "source_roots": [str(path) for path in self.source_roots],
            "output_root": str(self.output_root),
            "build_root": str(self.build_root),
            "extension_modules": [str(path) for path in self.extension_modules],
            "copy_roots": [copy_root.to_view() for copy_root in self.copy_roots],
            "descriptor": dict(self.descriptor_metadata),
            "sdk": {
                "status": "scaffold",
                "runtime": architecture.primary_runtime,
            },
            "surfaces": {
                surface.identifier: {
                    "title": surface.title,
                    "runtime": surface.runtime,
                    "status": surface.status,
                }
                for surface in architecture.surfaces
            },
        }
        if version is not None:
            view["version"] = version
        return view

    @_serialize_project_source_mutation
    def rename(self, title: str) -> "Project":
        """Update this project's display title in `paradev.yaml`.

        Args:
            title: New non-empty project display title. This does not rename
                the project folder, project id, source roots, output root, or
                build root.

        Returns:
            Reloaded project with the updated title.

        Raises:
            ValueError: If the title is empty.
            ProjectManifestError: If the manifest cannot be reloaded.
        """

        clean_title = title.strip() if isinstance(title, str) else ""
        if not clean_title:
            raise ValueError("Project title must be non-empty.")
        manifest, _source = _load_user_manifest(self.manifest_path)
        manifest["title"] = clean_title
        _write_user_manifest(self, manifest)
        return Project.load(self.root)

    @_serialize_project_source_mutation
    def set_preferred_language(
        self,
        preferred_language: str,
        *,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or apply the project's default module-authoring language.

        The preference is stored once in the visible `paradev.yaml`; it is not
        copied into module metadata. Planning is the default. Applying requires
        the exact `plan_hash` from the current plan, preventing a stale GUI,
        CLI, or agent request from overwriting an intervening manifest edit.

        Args:
            preferred_language (str): Supported HoI4 language alias such as
                `en`, `zh`, or `l_simp_chinese`.
            write (bool): Whether to atomically apply the reviewed manifest
                update. Defaults to `False`.
            plan_hash (str | None): Exact hash returned by the current dry
                plan. Required when `write=True`.

        Returns:
            dict[str, object]: JSON-safe plan with the normalized preference,
            manifest revision, diagnostics, plan hash, and reloaded project
            view after a successful apply.

        Raises:
            ProjectManifestError: If the visible manifest or language is
                invalid.
            ValueError: If safe descriptor-anchored replacement is unavailable.
        """

        return _set_project_preferred_language(
            self,
            preferred_language,
            write=write,
            plan_hash=plan_hash,
        )

    @_serialize_project_source_mutation
    def rename_module(
        self,
        module_id: str,
        object_id: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        title: str | None = None,
    ) -> dict[str, object]:
        """Rename a source module folder or synchronize its readable title.

        Args:
            module_id: Existing module id in `family/object_id` form.
            object_id: New source-module object id path segment.
            source_root: Optional configured source root used to disambiguate
                duplicate module ids across multiple source roots.
            title: Optional non-empty display title used to canonicalize the
                physical folder as `{object_id} - {portable_title}`. The
                caller remains responsible for updating the Registry-owned
                localization source before requesting this folder move. Use
                `apply_source_draft(module_rename=...)` when the localization
                edit and folder title must share one rollback boundary.

        Returns:
            JSON-safe rename payload with previous and current module paths.
            This method moves the source-module folder but does not rewrite
            in-game PDX identifiers or localization keys inside the files.
            The additive `catalog_mutation` field reports whether no Catalog
            was configured or an existing derived Catalog now requires refresh.

        Raises:
            ValueError: If the module id, target object id, source root, or
                destination folder is invalid.
        """

        from paradev.hb import _module_catalog_mutation_scope

        with _module_catalog_mutation_scope(self) as catalog_lock_held:
            return _rename_project_module(
                self,
                module_id,
                object_id,
                source_root=source_root,
                title=title,
                catalog_lock_held=catalog_lock_held,
            )

    @_serialize_project_source_mutation
    def duplicate_module(
        self,
        module_id: str,
        object_id: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        destination_source_root: str | os.PathLike[str] | None = None,
        identity: Literal["rewrite", "preserve"] = "rewrite",
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or create an independent copy of one source module.

        Planning is the default. Applying a duplicate requires the exact
        `plan_hash` returned by the current dry plan. By default the registered
        family rewrites owned identifier tokens in source paths and text while
        preserving binary assets. Use `identity="preserve"` for an explicit
        byte-preserving copy. Durable module settings in
        `.paradev/meta.yaml` are copied; transient import, evidence, diagram,
        and transaction state remains excluded. Existing destinations are
        never overwritten.

        Args:
            module_id (str): Existing source module in `family/object_id`
                form.
            object_id (str): New logical object id and destination folder.
            source_root (str | os.PathLike[str] | None): Optional configured
                source root used to disambiguate duplicate source module ids.
            destination_source_root (str | os.PathLike[str] | None): Optional
                configured destination source root. Defaults to the selected
                source module's root.
            identity (Literal["rewrite", "preserve"]): Identity handling.
                Supported values:
                - `rewrite`: Use the registered family's identity rewriter and
                  block when that capability is unavailable.
                - `preserve`: Copy all authored source paths and bytes exactly.
            write (bool): Whether to apply the current create-only plan.
            plan_hash (str | None): Exact hash returned by the current dry
                plan. Required when `write=True`.

        Returns:
            dict[str, object]: JSON-safe duplicate plan with stable file
            inventory, source and destination identities, diagnostics, totals,
            and apply status.

        Raises:
            ValueError: If module ids or configured source-root selectors are
                invalid or ambiguous.
        """

        from paradev.hb import _module_catalog_mutation_scope

        with _module_catalog_mutation_scope(self, enabled=write) as catalog_lock_held:
            return _duplicate_project_module(
                self,
                module_id,
                object_id,
                source_root=source_root,
                destination_source_root=destination_source_root,
                identity=identity,
                write=write,
                plan_hash=plan_hash,
                catalog_lock_held=catalog_lock_held,
            )

    @_serialize_project_source_mutation
    def clean_module_metadata(
        self,
        *,
        family: str | None = None,
        module_id: str | None = None,
        source_root: str | os.PathLike[str] | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or remove redundant path-derived module metadata.

        The initial cleanup policy removes only a direct top-level
        ``type: <family>`` entry when it exactly matches the family already
        inferred from ``modules/<family>/<object_id>``. Every other source
        byte is preserved. Planning is the default; applying requires the
        exact current ``plan_hash`` and uses the same revision-guarded,
        rollback-capable transaction as source-draft edits.

        Args:
            family: Optional exact module family to clean.
            module_id: Optional exact module in ``family/object_id`` form.
            source_root: Optional configured source root used to disambiguate
                or bound cleanup.
            write: Whether to apply the current cleanup plan.
            plan_hash: Exact hash returned by the current dry plan. Required
                when ``write=True``.

        Returns:
            JSON-safe cleanup plan with selectors, per-family counts, changed
            or blocked files, diagnostics, apply status, and Catalog
            invalidation status after a written mutation.

        Raises:
            ValueError: If selectors are invalid, contradictory, ambiguous,
                or do not identify the requested module.
        """

        return _clean_project_module_metadata(
            self,
            family=family,
            module_id=module_id,
            source_root=source_root,
            write=write,
            plan_hash=plan_hash,
        )

    @_serialize_project_source_mutation
    def set_module_collection(
        self,
        module_id: str,
        collection_id: str | None,
        *,
        source_root: str | os.PathLike[str] | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or atomically change one module's collection membership.

        Collection membership is system-maintained in
        ``.paradev/meta.yaml`` so a module's visible ``meta.yaml`` remains
        focused on author-facing content. Existing visible ``collection``
        keys are migrated into the hidden metadata layer by the same atomic
        transaction. Clearing the membership removes an empty hidden metadata
        file instead of leaving a placeholder behind.

        Args:
            module_id: Existing module id in ``family/object_id`` form.
            collection_id: Target collection id, or ``None`` to clear the
                current membership.
            source_root: Optional configured source root used to disambiguate
                duplicate module ids.
            write: Whether to apply the reviewed plan. Defaults to ``False``.
            plan_hash: Exact hash returned by the current dry plan. Required
                when ``write=True``.

        Returns:
            JSON-safe plan with exact source revisions, target membership,
            diagnostics, apply status, and Catalog mutation status.

        Raises:
            ValueError: If the module or collection is missing, ambiguous,
                belongs to another family/source root, or metadata is invalid.
        """

        return _set_project_module_collection(
            self,
            module_id,
            collection_id,
            source_root=source_root,
            write=write,
            plan_hash=plan_hash,
        )

    @_serialize_project_source_mutation
    def set_module_active(
        self,
        module_id: str,
        active: bool,
        *,
        source_root: str | os.PathLike[str] | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or atomically change whether one module participates in builds.

        Activity is represented by the minimal author-facing
        ``inactive: true`` key in ``meta.yaml``. Activating a module removes
        that key and removes the metadata file when it would otherwise be
        empty. Any obsolete hidden ``inactive`` key is cleaned by the same
        transaction, leaving one obvious source of truth.

        Args:
            module_id: Existing module id in ``family/object_id`` form.
            active: Whether the module should participate in subsequent
                full, cached, family-partial, and module-partial builds.
            source_root: Optional configured source root used to disambiguate
                duplicate module ids.
            write: Whether to apply the reviewed plan. Defaults to ``False``.
            plan_hash: Exact hash returned by the current dry plan. Required
                when ``write=True``.

        Returns:
            JSON-safe plan with exact metadata revisions, previous and target
            activity, diagnostics, apply status, and Catalog mutation status.

        Raises:
            ValueError: If the module is missing or ambiguous, ``active`` is
                not a boolean, or its metadata is invalid.
        """

        return _set_project_module_active(
            self,
            module_id,
            active,
            source_root=source_root,
            write=write,
            plan_hash=plan_hash,
        )

    def module_diagram(
        self,
        family: str,
        *,
        profile: str | None = None,
    ) -> dict[str, object]:
        """Project one source-backed module family into a diagram.

        The selected provider is resolved from the active build registry. It
        receives only guarded project-owned resources declared by its active
        source family. Generated metadata and legacy summaries are excluded
        from the graph contract.

        Args:
            family: Registered diagram provider id or alias. Discover active
                values from :meth:`browser` ``families[].diagram``.
            profile: Optional build profile. Defaults to this project's game.

        Returns:
            JSON-safe graph with source revisions, nodes, edges, diagnostics,
            and explicit editability.

        Raises:
            ValueError: If the family, profile, module source contract, or
                project-contained source path is unsupported or unsafe.
        """

        profile_id = profile or self.game
        registry = self._build_registry(profile=profile_id)
        resolved = registry.diagram_provider(
            family,
            editable=False,
        )
        context = _ProjectModuleDiagramContext(
            self,
            registry=registry,
            family=resolved.family,
            profile=profile_id,
        )
        projection = resolved.provider.project(context)
        return _module_diagram_payload(
            self,
            family=resolved.provider.identifier,
            profile=profile_id,
            projection=projection,
        )

    @_serialize_project_source_mutation
    def edit_module_diagram(
        self,
        family: str,
        *,
        position_intents: Sequence[Mapping[str, object]] = (),
        edge_intents: Sequence[Mapping[str, object]] = (),
        node_intents: Sequence[Mapping[str, object]] = (),
        profile: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or transactionally apply source-backed diagram edits.

        Planning is the default. Every intent carries the source revision
        exposed by :meth:`module_diagram`; applying requires the exact current
        plan hash. A write keeps durable backups until a family-scoped build
        succeeds, then refreshes affected HeavenBase Catalog projections.

        Args:
            family: Registered editable diagram provider id or alias. Discover
                active values from :meth:`browser` ``families[].diagram``.
            position_intents: Reviewed absolute node-position edits.
            edge_intents: Reviewed family-specific edge presence edits.
            node_intents: At most one provider-owned node creation request.
                Its fields are discovered from the browser diagram capability
                and cannot be combined with position or edge edits.
            profile: Optional build profile. Defaults to this project's game.
            write: Whether to apply the exact current plan.
            plan_hash: Hash returned by the reviewed dry plan. Required when
                ``write`` is true and the plan changes sources.

        Returns:
            JSON-safe plan/apply payload with exact replacements, diagnostics,
            build acceptance, write status, and optional Catalog mutation.

        Raises:
            ValueError: If the provider, source contract, or filesystem target
                is unsupported or unsafe. Expected stale-plan conflicts are
                returned as blocking diagnostics without writing.
        """

        profile_id = profile or self.game
        registry = self._build_registry(profile=profile_id)
        resolved = registry.diagram_provider(
            family,
            editable=False,
        )
        from paradev.sdk._module_diagram_api import (
            module_diagram_intents,
            module_diagram_node_intents,
        )

        positions, edges = module_diagram_intents(
            position_intents,
            edge_intents,
        )
        nodes = module_diagram_node_intents(node_intents)
        if nodes and (positions or edges):
            raise ValueError("Module diagram node creation cannot be combined with " "position or edge intents.")
        context = _ProjectModuleDiagramContext(
            self,
            registry=registry,
            family=resolved.family,
            profile=profile_id,
        )
        if nodes:
            node_planner = resolved.provider.node_plan
            if node_planner is None:
                raise ValueError(f"Module diagram family {family!r} has no node creation planner.")
            plan = node_planner(context, nodes[0])
        else:
            planner = resolved.provider.plan
            if planner is None:
                raise ValueError(f"Module diagram family {family!r} has no edit planner.")
            plan = planner(context, positions, edges)
        from paradev.build import ModuleDiagramModuleCreation

        if isinstance(plan, ModuleDiagramModuleCreation):
            return _apply_module_diagram_module_creation(
                self,
                family=resolved.family,
                profile=profile_id,
                plan=plan,
                write=write,
                plan_hash=plan_hash,
            )
        return _apply_module_diagram_plan(
            self,
            family=resolved.family,
            profile=profile_id,
            plan=plan,
            write=write,
            plan_hash=plan_hash,
        )

    @_serialize_project_source_mutation
    def remove_module(
        self,
        module_id: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        write: bool = False,
    ) -> dict[str, object]:
        """Plan or remove a discovered source module folder.

        Args:
            module_id: Existing module id in `family/object_id` form.
            source_root: Optional configured source root used to disambiguate
                duplicate module ids across multiple source roots.
            write: Whether to delete the module folder after planning.

        Returns:
            JSON-safe remove payload with module identity, source-root path,
            pre-removal file inventory, diagnostics, and removal status.
            Symlinked or noncanonical paths return blocked diagnostics, and a
            successful written removal may include additive `catalog_mutation`.

        Raises:
            ValueError: If the module id or source root is invalid.
        """

        from paradev.hb import _module_catalog_mutation_scope

        with _module_catalog_mutation_scope(self, enabled=write) as catalog_lock_held:
            return _remove_project_module(
                self,
                module_id,
                source_root=source_root,
                write=write,
                catalog_lock_held=catalog_lock_held,
            )

    def read_module_file(
        self,
        module_id: str,
        relative_path: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        encoding: str = "utf-8",
    ) -> dict[str, object]:
        """Read one text source file from a discovered module.

        Args:
            module_id: Existing module id in `family/object_id` form.
            relative_path: File path relative to the module root.
            source_root: Optional configured source root used to disambiguate
                duplicate module ids across multiple source roots.
            encoding: Text encoding used to decode the file.

        Returns:
            JSON-safe module file payload with text, path metadata, and paired
            ``size``/``mtime_ns`` values from one stable source snapshot.

        Raises:
            ValueError: If the module or relative path is invalid, or the file
                does not exist.
        """

        module = _find_project_module(self, module_id, source_root=source_root)
        path = _module_file_path(module, relative_path)
        if not path.is_file():
            raise ValueError(f"Module file does not exist: {_project_relative_path(self.root, path)}.")
        payload, revision = _read_project_source_snapshot(self.root, path)
        try:
            text = payload.decode(encoding)
        except LookupError as error:
            raise ValueError(f"Unknown module file encoding {encoding!r}: " f"{_project_relative_path(self.root, path)}.") from error
        except UnicodeDecodeError as error:
            raise ValueError(f"Module file is not valid {encoding} text: " f"{_project_relative_path(self.root, path)}.") from error
        return _module_file_payload(
            self,
            module=module,
            path=path,
            text=text,
            encoding=encoding,
            revision=revision,
        )

    def read_module_asset(
        self,
        module_id: str,
        relative_path: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        include_content: bool = False,
    ) -> dict[str, object]:
        """Read one Registry-owned module asset with a stable revision.

        The selected source must belong to a family-declared copy slot or use
        a supported image suffix. By default the payload contains only
        identity, slot ownership, content digest, and the exact revision guard
        accepted by :meth:`apply_source_draft`. Set ``include_content`` to add
        bounded base64 content for an MCP or SDK client that needs the bytes.

        Args:
            module_id (str): Existing module id in `family/object_id` form.
            relative_path (str): Asset path relative to the module folder.
            source_root (str | os.PathLike[str] | None): Optional configured
                source root used to disambiguate duplicate module ids.
            include_content (bool): Whether to include base64 source content.

        Returns:
            dict[str, object]: JSON-safe module asset payload with Registry
                source-slot ownership, SHA-256 digest, stable revision, and an
                additive ``content_base64`` field when requested.

        Raises:
            OSError: If a stable source snapshot cannot be read.
            ValueError: If the module, asset path, Registry ownership, or size
                is invalid.
        """

        module = _find_project_module(self, module_id, source_root=source_root)
        path = _module_file_path(module, relative_path)
        if not path.is_file():
            raise ValueError("Module asset does not exist: " f"{_project_relative_path(self.root, path)}.")
        module_root = Path(module.root).expanduser().resolve()
        module_relative_path = _project_relative_path(module_root, path)
        registry = self._build_registry(profile=self.game)
        slot_rows = _module_asset_slot_rows(
            module,
            module_relative_path,
            registry.source_slots_for(module.family),
        )
        if not slot_rows:
            raise ValueError("Module asset must be owned by a registered copy or image " f"source slot: {module.module_id}/{module_relative_path}.")
        content, revision = _read_project_source_snapshot(
            self.root,
            path,
            max_bytes=MAX_PROJECT_SOURCE_BINARY_BYTES,
        )
        return _module_asset_payload(
            self,
            module=module,
            path=path,
            content=content,
            revision=revision,
            source_slots=slot_rows,
            include_content=include_content,
        )

    @_serialize_project_source_mutation
    def write_module_file(
        self,
        module_id: str,
        relative_path: str,
        text: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        create: bool = False,
        encoding: str = "utf-8",
    ) -> dict[str, object]:
        """Write one text source file inside a discovered module.

        Args:
            module_id: Existing module id in `family/object_id` form.
            relative_path: File path relative to the module root.
            text: Replacement file text.
            source_root: Optional configured source root used to disambiguate
                duplicate module ids across multiple source roots.
            create: Whether to create a missing file and parent folders.
            encoding: Text encoding used to write the file.

        Returns:
            JSON-safe module file payload with the written text and path
            metadata.

        Raises:
            ValueError: If the module, relative path, target file, or text
                value is invalid.
        """

        if not isinstance(text, str):
            raise ValueError("Module file text must be a string.")
        module = _find_project_module(self, module_id, source_root=source_root)
        path = _module_file_path(module, relative_path)
        if path.exists() and not path.is_file():
            raise ValueError(f"Module file path is not a file: {_project_relative_path(self.root, path)}.")
        if not path.exists() and not create:
            raise ValueError(f"Module file does not exist: {_project_relative_path(self.root, path)}. Pass create=True to create it.")
        created = not path.exists()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding=encoding)
        return _module_file_payload(
            self,
            module=module,
            path=path,
            text=text,
            encoding=encoding,
            written=True,
            created=created,
        )

    def read_source_text(self, source_path: str | os.PathLike[str]) -> dict[str, object]:
        """Read one project-contained source file as UTF-8 text.

        Args:
            source_path: Absolute or project-relative source path.

        Returns:
            JSON-safe source text payload with UTF-8 text plus paired `size`
            and `mtime_ns` revision from the same stable file snapshot.

        Raises:
            ValueError: If the path is invalid, outside the project, missing,
                not a file, too large, or not UTF-8 text.
        """

        path = _project_source_path(
            self.root,
            _required_path_text(source_path, "path"),
            reject_symlinks=True,
        )
        payload, metadata = _read_project_source_snapshot(self.root, path)
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"Source file is not UTF-8 text: {path}") from error
        return {
            "schema": PROJECT_SOURCE_TEXT_SCHEMA,
            "project_id": self.project_id,
            "path": str(path),
            "relative_path": _project_relative_path(self.root, path),
            "encoding": "utf-8",
            "size": metadata.st_size,
            "mtime_ns": str(metadata.st_mtime_ns),
            "text": text,
        }

    def read_source_binary(
        self,
        source_path: str | os.PathLike[str],
        *,
        include_content: bool = True,
    ) -> dict[str, object]:
        """Read one project-contained binary source with a stable revision.

        Args:
            source_path (str | os.PathLike[str]): Absolute or project-relative
                source path.
            include_content (bool): Whether to include bounded base64 content.

        Returns:
            dict[str, object]: JSON-safe binary source payload with MIME type,
                SHA-256 digest, paired ``size``/``mtime_ns`` revision, and
                optional ``content_base64``.

        Raises:
            OSError: If a stable source snapshot cannot be read.
            ValueError: If the path is outside the project, missing, unsafe,
                not a regular file, or larger than the binary source limit.
        """

        path = _project_source_path(
            self.root,
            _required_path_text(source_path, "path"),
            reject_symlinks=True,
        )
        content, revision = _read_project_source_snapshot(
            self.root,
            path,
            max_bytes=MAX_PROJECT_SOURCE_BINARY_BYTES,
        )
        return _project_binary_source_payload(
            self,
            path=path,
            content=content,
            revision=revision,
            include_content=include_content,
        )

    def source_form(
        self,
        source_path: str | os.PathLike[str],
        *,
        text: str | None = None,
        query: str | None = None,
    ) -> dict[str, object] | None:
        """Return an optional guided form for one canonical module source.

        Args:
            source_path (str | os.PathLike[str]): Absolute or project-relative
                source file path.
            text (str | None): Optional current editor text. When omitted, the
                source file is read from disk. The method validates but never
                writes this text.
            query (str | None): Optional bounded search across Registry-owned
                PDX and localization fields. Empty text restores the default
                bounded projection.

        Returns:
            dict[str, object] | None: Validated JSON-safe
                `paradev.source-form.v1` payload, or `None` when the source is
                not a supported canonical module source. JSON forms remain
                family-owned; Registry-declared localization and PDX sources
                use generic lossless projections.

        Raises:
            ValueError: If the source path, editor text, family provider, or
                returned form contract is invalid.
            OSError: If source metadata or text cannot be read.
        """

        path = _project_source_path(self.root, _required_path_text(source_path, "path"))
        if not path.is_file():
            raise ValueError(f"Source path is not a file: {path}")
        suffix = path.suffix.casefold()
        module_path = _source_draft_module_path(self, path)
        if module_path is None:
            return None
        (
            source_root,
            family_id,
            object_id,
            _module_root,
            module_relative_path,
        ) = module_path
        registry = self._build_registry(profile=self.game)
        try:
            family = registry.family(family_id)
        except ValueError:
            return None
        project_relative_path = _project_relative_path(self.root, path)
        source_text = _project_source_form_text(self, path, text)
        normalized_query = normalize_source_form_query(query)
        module_id = f"{family_id}/{object_id}"
        try:
            if suffix == ".json":
                if normalized_query is not None:
                    raise ValueError("Guided source search is not supported by this JSON family form.")
                provider = getattr(family, "source_form", None)
                if provider is None:
                    return None
                if not callable(provider):
                    raise ValueError(f"build family {family_id!r} source_form must be callable")
                raw_form = provider(
                    module_id=module_id,
                    relative_path=module_relative_path,
                    text=source_text,
                )
                source_format = "json"
            elif is_pdx_form_source(family, module_relative_path):
                raw_form = pdx_source_form(
                    module_id=module_id,
                    text=source_text,
                    field_hints=getattr(family, "source_form_field_hints", None),
                    query=normalized_query,
                )
                source_format = "pdx"
            elif is_loc_text_form_source(family, module_relative_path):
                raw_form = loc_text_source_form(
                    module_id=module_id,
                    text=source_text,
                    query=normalized_query,
                )
                source_format = "loc"
            else:
                return None
            if raw_form is None:
                return None
            form = _source_form_provider_payload(raw_form)
            operations = source_form_patch_operations(form["sections"])
            expected_operations = {
                "json": frozenset({"replace-json-scalar"}),
                "loc": frozenset({"replace-loc-text"}),
                "pdx": frozenset(
                    {
                        "replace-pdx-scalar",
                        "replace-pdx-integer-list",
                        "replace-pdx-block-body",
                    }
                ),
            }[source_format]
            if operations - expected_operations:
                actual = ", ".join(sorted(operations))
                expected = ", ".join(repr(operation) for operation in sorted(expected_operations))
                raise ValueError(f"{source_format} source forms must use only {expected} patches, " f"got: {actual}")
        except Exception as error:
            raise ValueError(f"Invalid source form {project_relative_path!r}: {error}") from error

        return {
            "schema": PROJECT_SOURCE_FORM_SCHEMA,
            "project_id": self.project_id,
            "family": family_id,
            "module_id": module_id,
            "path": str(path),
            "relative_path": project_relative_path,
            "module_relative_path": module_relative_path,
            "source_root": str(source_root),
            "source_format": source_format,
            **form,
        }

    def plan_source_form_update(
        self,
        source_path: str | os.PathLike[str],
        values: Mapping[str, object],
        *,
        text: str | None = None,
        query: str | None = None,
    ) -> dict[str, object]:
        """Plan a guarded full-text edit from guided control values.

        The active Registry family remains authoritative for the form. This
        method reads one stable source snapshot, recomputes its form against
        either that text or an explicit unsaved editor draft, applies only
        requested editable control ids in memory, and returns an edit accepted
        by :meth:`apply_source_draft`. The edit always retains the stable disk
        snapshot's revision preconditions. This method never writes project
        files.

        Args:
            source_path: Absolute or project-relative canonical module source.
            values: Non-empty mapping of guided control ids to replacement
                string, finite number, or boolean values.
            text: Optional unsaved source text to use as the update base while
                retaining revision preconditions from the current disk source.
            query: Optional bounded form search used to resolve stable control
                ids outside the default projection window.

        Returns:
            JSON-safe ``paradev.source-form-update.v1`` plan containing exact
            changes and one paired revision-guarded ``source_edit``.

        Raises:
            ValueError: If the source has no guided form or a requested control,
                value, path, or exact PDX token is invalid.
            OSError: If the stable source snapshot cannot be read.
        """

        snapshot = self.read_source_text(source_path)
        path = str(snapshot["path"])
        if text is not None and not isinstance(text, str):
            raise ValueError("Guided source update text must be a string.")
        source_text = str(snapshot["text"]) if text is None else text
        form = self.source_form(path, text=source_text, query=query)
        if form is None:
            raise ValueError(f"Source does not provide a guided form: {path}")
        sections = form.get("sections")
        source_format = form.get("source_format")
        if not isinstance(sections, list) or not isinstance(source_format, str):
            raise ValueError("Guided source form payload is incomplete.")
        updated_text, changes = apply_source_form_values(
            text=source_text,
            source_format=source_format,
            sections=sections,
            values=values,
        )
        return {
            "schema": PROJECT_SOURCE_FORM_UPDATE_SCHEMA,
            "project_id": self.project_id,
            "family": form["family"],
            "module_id": form["module_id"],
            "path": path,
            "relative_path": snapshot["relative_path"],
            "source_format": source_format,
            "form_contract": form["contract"],
            "changed": bool(changes),
            "changes": list(changes),
            "source_edit": {
                "path": path,
                "text": updated_text,
                "expected_size": snapshot["size"],
                "expected_mtime_ns": snapshot["mtime_ns"],
            },
        }

    def plan_source_form_updates(
        self,
        updates: Sequence[Mapping[str, object]],
    ) -> dict[str, object]:
        """Plan several guided source updates as one atomic draft request.

        Each row traverses the same Registry-owned form provider and validation
        path as :meth:`plan_source_form_update`. The returned changed
        ``source_edits`` can be reviewed and passed directly to
        :meth:`apply_source_draft`, which validates every paired revision before
        writing any file. This method never writes project files.

        Args:
            updates (Sequence[Mapping[str, object]]): Ordered non-empty update
                rows. Each row must contain ``source_path`` and ``values``, plus
                optional unsaved base ``text`` and bounded form ``query``;
                ``values`` is a non-empty guided control-id mapping. At most
                256 distinct source files may be planned together.

        Returns:
            dict[str, object]: JSON-safe
            ``paradev.source-form-update-batch.v1`` plan with per-source plans,
            aggregate counts, and the changed revision-guarded ``source_edits``
            accepted by :meth:`apply_source_draft`.

        Raises:
            ValueError: If the batch is empty or too large, a row or field is
                invalid, two rows resolve to the same source, or any guided
                source update is invalid.
            OSError: If a stable source snapshot cannot be read.
        """

        if isinstance(updates, (str, bytes, bytearray)) or not isinstance(updates, Sequence):
            raise ValueError("Guided source update batch must be an array.")
        if not updates:
            raise ValueError("Guided source update batch must not be empty.")
        if len(updates) > MAX_PROJECT_SOURCE_DRAFT_FILES:
            raise ValueError("Guided source update batch must target at most " f"{MAX_PROJECT_SOURCE_DRAFT_FILES} source files.")

        plans: list[dict[str, object]] = []
        for index, update in enumerate(updates):
            if not isinstance(update, Mapping):
                raise ValueError(f"Guided source update row {index} must be an object.")
            unknown = sorted(str(key) for key in set(update) - {"source_path", "values", "text", "query"})
            if unknown:
                raise ValueError(f"Guided source update row {index} contains unsupported " f"fields: {', '.join(unknown)}.")
            raw_source_path = update.get("source_path")
            try:
                source_path = os.fspath(raw_source_path)
            except TypeError as error:
                raise ValueError(f"Guided source update row {index}.source_path must be a path.") from error
            if not isinstance(source_path, str) or not source_path:
                raise ValueError(f"Guided source update row {index}.source_path must be a " "non-empty text path.")
            values = update.get("values")
            if not isinstance(values, Mapping):
                raise ValueError(f"Guided source update row {index}.values must be an object.")
            text = update.get("text")
            if text is not None and not isinstance(text, str):
                raise ValueError(f"Guided source update row {index}.text must be a string.")
            query = update.get("query")
            if query is not None and not isinstance(query, str):
                raise ValueError(f"Guided source update row {index}.query must be a string.")
            plans.append(self.plan_source_form_update(source_path, values, text=text, query=query))

        _validate_unique_source_draft_paths(tuple(Path(str(plan["path"])) for plan in plans))
        source_edits = [cast(dict[str, object], plan["source_edit"]) for plan in plans if plan["changed"]]
        return {
            "schema": PROJECT_SOURCE_FORM_UPDATE_BATCH_SCHEMA,
            "project_id": self.project_id,
            "changed": bool(source_edits),
            "counts": {
                "requested": len(plans),
                "changed": len(source_edits),
                "unchanged": len(plans) - len(source_edits),
            },
            "updates": plans,
            "source_edits": source_edits,
        }

    def localization_workspace(
        self,
        target_id: str,
        *,
        target_kind: Literal["module", "collection"] = "module",
        family: str | None = None,
        source_root: str | os.PathLike[str] | None = None,
        drafts: Mapping[str, str] | None = None,
        limit: int = MAX_LOCALIZATION_WORKSPACE_ROWS,
    ) -> dict[str, object]:
        """Return one Registry-owned cross-language source-unit workspace.

        The active family Registry selects localization slots. Optional drafts
        replace only the in-memory text of those discovered files; every row
        still carries the stable disk revision used by the corresponding edit
        planner. Duplicate language/key identities and malformed sources fail
        closed instead of making a best-effort edit.

        Args:
            target_id: Canonical ``family/object_id`` module identity or
                collection id selected by ``target_kind``.
            target_kind: Whether ``target_id`` identifies a module or
                collection.
            family: Optional collection-family selector required only when a
                collection id is ambiguous. For modules, when supplied, it
                must match the family encoded by ``target_id``.
            source_root: Optional configured source root when the target is
                present in more than one root.
            drafts: Optional mapping from absolute or project-relative source
                paths to current unsaved text.
            limit: Maximum rows returned by the bounded table projection.

        Returns:
            JSON-safe ``paradev.localization-workspace.v2`` projection with
            sources, languages, rows, and explicit coverage.

        Raises:
            ValueError: If the target, Registry slots, drafts, source syntax,
                duplicate identities, or limit are invalid.
            OSError: If a stable localization source snapshot cannot be read.
        """

        identity, localization_sources, selected_source_root = _project_localization_sources(
            self,
            target_id,
            target_kind=target_kind,
            family=family,
            source_root=source_root,
            drafts=drafts,
        )
        return project_localization_workspace(
            localization_sources,
            project_id=self.project_id,
            target_kind=identity["kind"],
            target_id=identity["id"],
            family=identity["family"],
            object_id=identity["object_id"],
            source_root=str(selected_source_root),
            limit=limit,
        )

    def plan_localization_update(
        self,
        target_id: str,
        operation: Mapping[str, object],
        *,
        target_kind: Literal["module", "collection"] = "module",
        family: str | None = None,
        source_root: str | os.PathLike[str] | None = None,
        drafts: Mapping[str, str] | None = None,
        limit: int = MAX_LOCALIZATION_WORKSPACE_ROWS,
    ) -> dict[str, object]:
        """Plan one lossless source-unit localization operation without writing.

        Supported closed operations are ``set`` (edit or add one language
        cell), ``add`` (create one key across selected languages), ``rename``
        (all languages), and ``remove`` (all languages). Returned
        ``source_edits`` retain paired disk revisions and can be passed directly
        to :meth:`apply_source_draft` for atomic application.

        Args:
            target_id: Canonical module identity or collection id selected by
                ``target_kind``.
            operation: Closed operation mapping discriminated by ``op``.
            target_kind: Whether ``target_id`` identifies a module or
                collection.
            family: Optional collection-family disambiguator or module-family
                consistency check.
            source_root: Optional configured source root for an ambiguous
                target.
            drafts: Optional unsaved text keyed by owned localization path.
            limit: Maximum rows returned in the updated workspace projection.

        Returns:
            JSON-safe ``paradev.localization-update-plan.v2`` no-write plan.

        Raises:
            ValueError: If ownership, source syntax, operation fields, target,
                collision, ambiguity, or replacement text is invalid.
            OSError: If a stable localization source snapshot cannot be read.
        """

        if not isinstance(operation, Mapping):
            raise ValueError("Localization operation must be an object.")
        identity, localization_sources, selected_source_root = _project_localization_sources(
            self,
            target_id,
            target_kind=target_kind,
            family=family,
            source_root=source_root,
            drafts=drafts,
        )
        return plan_localization_operation(
            localization_sources,
            operation,
            project_id=self.project_id,
            target_kind=identity["kind"],
            target_id=identity["id"],
            family=identity["family"],
            object_id=identity["object_id"],
            source_root=str(selected_source_root),
            limit=limit,
        )

    @_serialize_project_source_mutation
    def apply_source_draft(
        self,
        *,
        source_edits: object = None,
        source_removals: object = None,
        source_replacements: object = None,
        module_rename: object = None,
    ) -> dict[str, object]:
        """Apply source-file drafts and an optional rename as one transaction.

        Text drafts are preflighted as one batch before mutation. The preflight
        enforces the editor reopen limit, parses JSON and YAML sources, and
        invokes an optional ``validate_source_text`` hook on the owning build
        family for project-specific source contracts. An optional module rename
        commits only after every file mutation succeeds. A rename failure rolls
        the completed file mutations back through the same guarded recovery
        transaction.

        Args:
            source_edits: Optional list of mappings with `path`, `text`, and
                paired `expected_size`/`expected_mtime_ns` revision guards.
            source_removals: Optional list of existing file paths or mappings
                with `path` and paired revision guards to remove.
            source_replacements: Optional list of mappings with `path` and
                base64-encoded `content_base64`. PNG uploads may also declare
                `content_format="png"` and a matching image `target_format`.
                Existing targets may use the same paired revision guards;
                new targets may use `expected_absent=True`.
            module_rename: Optional mapping with `module_id`, `object_id`, and
                optional `source_root` and `title`. This moves the canonical
                module folder after the file drafts succeed, allowing a
                Registry-owned localization edit and its readable folder title
                to commit through one SDK call.

        Returns:
            JSON-safe draft apply payload used by SDK, REST, CLI, and desktop
            editor adapters. Drafts contained by one canonical module include
            additive ``catalog_mutation`` invalidation/refresh status. A
            combined rename includes its standard payload as ``module_rename``.

        Raises:
            ValueError: If the draft request or any source target is invalid.
        """

        draft_root, draft_root_identity = _source_draft_root_identity(self.root)
        _recover_source_draft_transaction(
            draft_root,
            root_identity=draft_root_identity,
        )
        edits = _source_draft_edits(self, source_edits)
        removals = _source_draft_removals(draft_root, source_removals)
        replacements = _source_draft_replacements(draft_root, source_replacements)
        prepared_rename = _source_draft_module_rename(self, module_rename)
        if not edits and not removals and not replacements and prepared_rename is None:
            raise ValueError("Draft apply request must include source_edits, " "source_removals, source_replacements, or module_rename.")
        paths = (
            tuple(edit["path"] for edit in edits) + tuple(replacement["path"] for replacement in replacements) + tuple(removal["path"] for removal in removals)
        )
        if len(paths) > MAX_PROJECT_SOURCE_DRAFT_FILES:
            raise ValueError("Draft apply request must target at most " f"{MAX_PROJECT_SOURCE_DRAFT_FILES} source files.")
        _validate_unique_source_draft_paths(paths)
        module_targets = _source_draft_module_targets(self, paths)
        _validate_project_family_source_text_drafts(self, edits)
        _validate_source_draft_expected_revisions(
            edits,
            removals,
            replacements,
        )
        from paradev.hb import (
            _module_catalog_mutation_scope,
            _sync_module_catalog_projection,
        )

        with _module_catalog_mutation_scope(
            self,
            enabled=bool(module_targets or prepared_rename),
        ) as catalog_lock_held:
            _apply_source_draft_mutations(
                draft_root,
                edits=edits,
                replacements=replacements,
                removals=removals,
                root_identity=draft_root_identity,
                finalize=((lambda: _commit_prepared_module_rename(self, prepared_rename)) if prepared_rename is not None else None),
                prepared_rename=prepared_rename,
            )
            payload: dict[str, object] = {
                "schema": PROJECT_DRAFT_APPLY_SCHEMA,
                "project_id": self.project_id,
                "written": True,
                "files": [
                    {
                        "path": str(edit["path"]),
                        "relative_path": _project_relative_path(self.root, edit["path"]),
                        "operation": "write_text",
                        "encoding": "utf-8",
                    }
                    for edit in edits
                ]
                + [
                    {
                        "path": str(replacement["path"]),
                        "relative_path": _project_relative_path(self.root, replacement["path"]),
                        "operation": "replace_bytes",
                    }
                    for replacement in replacements
                ]
                + [
                    {
                        "path": str(path),
                        "relative_path": _project_relative_path(self.root, path),
                        "operation": "remove_file",
                    }
                    for removal in removals
                    for path in (removal["path"],)
                ],
            }
            if prepared_rename is not None:
                payload["module_rename"] = _prepared_module_rename_payload(
                    self,
                    prepared_rename,
                )
            catalog_mutations: list[dict[str, object]] = []
            renamed_target_seen = False
            for previous, source_root in module_targets:
                if (
                    prepared_rename is not None
                    and source_root == prepared_rename.source_root
                    and previous.get("module_id") == prepared_rename.previous_module.module_id
                ):
                    renamed_target_seen = True
                    catalog_mutations.append(
                        _sync_module_catalog_projection(
                            self,
                            previous=prepared_rename.previous_module.to_dict(),
                            current=prepared_rename.module.to_dict(),
                            _lock_held=catalog_lock_held,
                        )
                    )
                    continue
                try:
                    current = _find_project_module(self, str(previous["module_id"]), source_root=source_root)
                except Exception as error:
                    catalog_mutations.append(
                        _sync_module_catalog_projection(
                            self,
                            previous=previous,
                            current_error=error,
                            _lock_held=catalog_lock_held,
                        )
                    )
                else:
                    catalog_mutations.append(
                        _sync_module_catalog_projection(
                            self,
                            previous=previous,
                            current=current.to_dict(),
                            _lock_held=catalog_lock_held,
                        )
                    )
            if prepared_rename is not None and not renamed_target_seen:
                catalog_mutations.append(
                    _sync_module_catalog_projection(
                        self,
                        previous=prepared_rename.previous_module.to_dict(),
                        current=prepared_rename.module.to_dict(),
                        _lock_held=catalog_lock_held,
                    )
                )
            if catalog_mutations:
                catalog_mutation = _aggregate_source_draft_catalog_mutations(catalog_mutations)
                payload["catalog_mutation"] = catalog_mutation
                rename_payload = payload.get("module_rename")
                if isinstance(rename_payload, dict):
                    rename_payload["catalog_mutation"] = catalog_mutation
            return payload

    @_serialize_project_source_mutation
    def write_module_files(
        self,
        edits: Sequence[Mapping[str, object]],
        *,
        create: bool = False,
        encoding: str = "utf-8",
        write: bool = True,
    ) -> dict[str, object]:
        """Write multiple text source files inside discovered modules.

        Args:
            edits: Sequence of edit mappings with `module_id`, `relative_path`,
                and `text`. Optional per-edit `source_root`, `create`, and
                `encoding` override the method defaults.
            create: Whether missing files may be created by default.
            encoding: Text encoding used by default.
            write: Whether to write files. Set `False` to validate and preview
                the resolved batch without mutating project sources.

        Returns:
            JSON-safe batch payload with written module file rows and indexes.

        Raises:
            ValueError: If any edit is invalid. All edits are validated before
                any file is written.
        """

        rows = _module_file_edit_rows(self, edits, create=create, encoding=encoding)
        if write:
            for row in rows:
                path = row["path"]
                if not isinstance(path, Path):
                    raise ValueError("Module file edit path did not resolve to a filesystem path.")
                if not bool(row["changed"]):
                    continue
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(str(row["text"]), encoding=str(row["encoding"]))
        files = [
            _module_file_payload(
                self,
                module=row["module"],
                path=row["path"],
                text=str(row["text"]),
                encoding=str(row["encoding"]),
                written=write and bool(row["changed"]),
                created=bool(row["created"]),
                changed=bool(row["changed"]),
            )
            for row in rows
        ]
        return _module_batch_edit_payload(self, files, written=write)

    def module_batch_edit_request(
        self,
        edits: Sequence[Mapping[str, object]],
        *,
        create: bool = False,
        encoding: str = "utf-8",
    ) -> dict[str, object]:
        """Build a canonical JSON request for `write_module_files(...)`.

        Args:
            edits: Sequence of edit mappings with `module_id`, `relative_path`,
                and `text`. Optional per-edit `source_root`, `create`, and
                `encoding` override the request defaults.
            create: Whether missing files may be created by default when the
                request is applied.
            encoding: Default text encoding for request edits.

        Returns:
            JSON-safe request object accepted by `write_module_files(...)` and
            the `paradev module-batch-edit` CLI command.

        Raises:
            ValueError: If the request shape, edit target identifiers, text, or
                encodings are invalid.
        """

        return _module_batch_edit_request_payload(self, edits, create=create, encoding=encoding)

    def read_collection_file(
        self,
        collection_id: str,
        relative_path: str,
        *,
        family: str | None = None,
        source_root: str | os.PathLike[str] | None = None,
        encoding: str = "utf-8",
    ) -> dict[str, object]:
        """Read one text source file from a discovered collection descriptor.

        Args:
            collection_id: Existing collection id.
            relative_path: File path relative to the collection descriptor root.
            family: Optional collection family used to disambiguate duplicate
                collection ids.
            source_root: Optional configured source root used to disambiguate
                duplicate collection ids across multiple source roots.
            encoding: Text encoding used to decode the file.

        Returns:
            JSON-safe collection file payload with file text and path metadata.

        Raises:
            ValueError: If the collection or relative path is invalid, or the
                file does not exist.
        """

        collection = _find_project_collection(self, collection_id, family=family, source_root=source_root)
        path = _collection_file_path(collection, relative_path)
        if not path.is_file():
            raise ValueError(f"Collection file does not exist: {_project_relative_path(self.root, path)}.")
        payload, revision = _read_project_source_snapshot(self.root, path)
        try:
            text = payload.decode(encoding)
        except LookupError as error:
            raise ValueError(f"Unknown collection file encoding {encoding!r}: " f"{_project_relative_path(self.root, path)}.") from error
        except UnicodeDecodeError as error:
            raise ValueError(f"Collection file is not valid {encoding} text: " f"{_project_relative_path(self.root, path)}.") from error
        return _collection_file_payload(
            self,
            collection=collection,
            path=path,
            text=text,
            encoding=encoding,
            revision=revision,
        )

    @_serialize_project_source_mutation
    def write_collection_file(
        self,
        collection_id: str,
        relative_path: str,
        text: str,
        *,
        family: str | None = None,
        source_root: str | os.PathLike[str] | None = None,
        create: bool = False,
        encoding: str = "utf-8",
    ) -> dict[str, object]:
        """Write one text source file inside a collection descriptor root.

        Args:
            collection_id: Existing collection id.
            relative_path: File path relative to the collection descriptor root.
            text: Replacement file text.
            family: Optional collection family used to disambiguate duplicate
                collection ids.
            source_root: Optional configured source root used to disambiguate
                duplicate collection ids across multiple source roots.
            create: Whether to create a missing file and parent folders.
            encoding: Text encoding used to write the file.

        Returns:
            JSON-safe collection file payload with the written text and path
            metadata.

        Raises:
            ValueError: If the collection, relative path, target file, or text
                value is invalid.
        """

        if not isinstance(text, str):
            raise ValueError("Collection file text must be a string.")
        collection = _find_project_collection(self, collection_id, family=family, source_root=source_root)
        path = _collection_file_path(collection, relative_path)
        if path.exists() and not path.is_file():
            raise ValueError(f"Collection file path is not a file: {_project_relative_path(self.root, path)}.")
        if not path.exists() and not create:
            raise ValueError(f"Collection file does not exist: {_project_relative_path(self.root, path)}. Pass create=True to create it.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding=encoding)
        return _collection_file_payload(
            self,
            collection=collection,
            path=path,
            text=text,
            encoding=encoding,
            written=True,
        )

    @_serialize_project_source_mutation
    def create_collection(
        self,
        family: str,
        collection_id: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        metadata: Mapping[str, object] | None = None,
        write: bool = False,
        force: bool = False,
    ) -> dict[str, object]:
        """Plan or write a collection descriptor metadata scaffold.

        Args:
            family: Collection family path segment.
            collection_id: Collection descriptor folder id.
            source_root: Optional configured source root path. Relative values
                resolve from the project root. Defaults to the first source root.
            metadata: Optional YAML metadata written to `meta.yaml`.
            write: Whether to write `meta.yaml` when the plan is not blocked.
            force: Whether an existing `meta.yaml` may be overwritten.

        Returns:
            JSON-safe create payload with nested authoring-plan preflight.

        Raises:
            ValueError: If the family, collection id, source root, or metadata
                mapping is invalid.
        """

        metadata_payload = _collection_create_metadata(metadata)
        build_registry = self._build_registry(profile=self.game)
        selected_source_root = _select_source_root(self.root, self.source_roots, source_root)
        preflight = _project_authoring_plan(
            self,
            kind="collection",
            family=family,
            target_id=collection_id,
            source_root=selected_source_root,
            registry=build_registry,
            folder_name=collection_id,
        )
        authoring_path = preflight["authoring_path"]
        root = Path(str(authoring_path["root"]))
        metadata_path = root / "meta.yaml"
        diagnostics = _collection_create_diagnostics(self.root, root, metadata_path, force=force)
        blocked = any(item.get("severity") == "error" for item in diagnostics)
        written = False
        if write and not blocked:
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            save_yaml(metadata_payload, str(metadata_path), encoding="utf-8", sort_keys=False)
            written = True
        plan = (
            _project_authoring_plan(
                self,
                kind="collection",
                family=family,
                target_id=collection_id,
                source_root=selected_source_root,
                registry=build_registry,
                folder_name=collection_id,
            )
            if written
            else preflight
        )
        return _collection_create_payload(
            self,
            authoring_path=authoring_path,
            metadata_path=metadata_path,
            metadata=metadata_payload,
            diagnostics=diagnostics,
            blocked=blocked,
            written=written,
            force=force,
            authoring_plan=plan,
        )

    @_serialize_project_source_mutation
    def rename_collection(
        self,
        collection_id: str,
        target_id: str,
        *,
        family: str | None = None,
        source_root: str | os.PathLike[str] | None = None,
    ) -> dict[str, object]:
        """Atomically rename a collection and its explicit member references.

        Args:
            collection_id: Existing collection descriptor id.
            target_id: New collection descriptor id path segment.
            family: Optional collection family used to disambiguate duplicate
                collection ids.
            source_root: Optional configured source root used to disambiguate
                duplicate collection ids across multiple source roots.

        Returns:
            JSON-safe rename payload with previous and current collection paths.
            Registry-owned ``collection`` metadata pointers are rewritten in
            the same crash-recoverable transaction. Authored PDX identifiers
            and localization keys are not rewritten.

        Raises:
            ValueError: If the collection id, target id, family, source root,
                destination folder, member metadata, or retained source paths
                are invalid or changed concurrently.
        """

        draft_root, draft_root_identity = _source_draft_root_identity(self.root)
        recovered = _recover_source_draft_transaction(
            draft_root,
            root_identity=draft_root_identity,
        )
        project = Project.load(self.root) if recovered else self
        collection = _find_project_collection(
            project,
            collection_id,
            family=family,
            source_root=source_root,
        )
        collection_root = _collection_root(collection)
        selected_source_root = _collection_source_root(
            project.root,
            project.source_roots,
            collection_root,
        )
        prepared = _prepare_project_collection_rename(
            project,
            collection,
            target_id,
            source_root=selected_source_root,
        )
        discovered_members = tuple(
            module
            for module in project.discover_modules(
                family=collection.family,
                collection_id=collection.collection_id,
            ).modules
            if _module_source_root(
                project.root,
                project.source_roots,
                Path(module.root).expanduser().resolve(),
            )
            == selected_source_root
        )
        pointer_modules = _collection_member_pointer_modules(
            project,
            family=collection.family,
            collection_id=collection.collection_id,
            source_root=selected_source_root,
            effective_members=discovered_members,
        )
        members_by_id = {module.module_id: module for module in (*discovered_members, *pointer_modules)}
        member_modules = tuple(members_by_id[module_id] for module_id in sorted(members_by_id))
        edit_requests, removal_requests, files = _collection_member_rename_edits(
            project,
            modules=pointer_modules,
            previous_collection_id=collection.collection_id,
            collection_id=prepared.target_object_id,
        )
        if removal_requests:
            raise AssertionError("Collection rename cannot remove member metadata files.")
        edits = _source_draft_edits(project, list(edit_requests))
        if len(edits) > MAX_PROJECT_SOURCE_DRAFT_FILES:
            raise ValueError("Collection rename must update at most " f"{MAX_PROJECT_SOURCE_DRAFT_FILES} member metadata files.")
        _validate_unique_source_draft_paths(tuple(cast(Path, edit["path"]) for edit in edits))
        _validate_source_draft_expected_revisions(edits, (), ())
        from paradev.hb import (
            _module_catalog_mutation_scope,
            _sync_module_catalog_projection,
        )

        catalog_mutation: dict[str, object] | None = None
        with _module_catalog_mutation_scope(
            project,
            enabled=bool(member_modules),
        ) as catalog_lock_held:
            _apply_source_draft_mutations(
                draft_root,
                edits=edits,
                replacements=(),
                removals=(),
                root_identity=draft_root_identity,
                finalize=lambda: _commit_prepared_collection_rename(
                    project,
                    prepared,
                ),
                prepared_rename=prepared,
            )
            if member_modules:
                catalog_mutation = _sync_module_catalog_projection(
                    project,
                    current={
                        "module_ids": sorted(module.module_id for module in member_modules),
                        "families": [collection.family],
                    },
                    _lock_held=catalog_lock_held,
                )
        renamed = Project.load(project.root)
        renamed_collection = _find_project_collection(
            renamed,
            prepared.target_object_id,
            family=collection.family,
            source_root=selected_source_root,
        )
        for module in member_modules:
            current = _find_project_module(
                renamed,
                module.module_id,
                source_root=selected_source_root,
            )
            if current.collection_id != prepared.target_object_id:
                raise RuntimeError(f"Module {module.module_id!r} collection membership did not " "match the committed collection rename.")
        payload = _collection_rename_payload(
            project,
            previous_collection=collection,
            collection=renamed_collection,
            previous_root=prepared.previous_root,
            root=prepared.root,
            members=member_modules,
            files=files,
        )
        if catalog_mutation is not None:
            payload["catalog_mutation"] = catalog_mutation
        return payload

    @_serialize_project_source_mutation
    def remove_collection(
        self,
        collection_id: str,
        *,
        family: str | None = None,
        source_root: str | os.PathLike[str] | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or transactionally remove a collection grouping.

        Removing a collection preserves every member module. ParaDev clears
        each explicit Registry-owned ``collection`` pointer and quarantines
        the descriptor folder in one crash-recoverable transaction. Applying
        the reviewed plan requires its exact ``plan_hash``.

        Args:
            collection_id: Existing collection descriptor id.
            family: Optional collection family used to disambiguate duplicate
                collection ids.
            source_root: Optional configured source root used to disambiguate
                duplicate collection ids across multiple source roots.
            write: Whether to apply the current removal plan.
            plan_hash: Exact hash from a dry plan. Required with ``write=True``.

        Returns:
            JSON-safe remove payload with descriptor inventory, affected
            members, metadata mutations, diagnostics, and removal status.

        Raises:
            ValueError: If collection ownership or retained source paths are
                invalid, unsafe, or changed concurrently.
        """

        draft_root, draft_root_identity = _source_draft_root_identity(self.root)
        recovered = _recover_source_draft_transaction(
            draft_root,
            root_identity=draft_root_identity,
        )
        project = Project.load(self.root) if recovered else self
        collection = _find_project_collection(
            project,
            collection_id,
            family=family,
            source_root=source_root,
        )
        collection_root = _collection_root(collection)
        selected_source_root = _collection_source_root(
            project.root,
            project.source_roots,
            collection_root,
        )
        mutation_root = _module_metadata_cleanup_mutation_root(
            project,
            selected_source_root,
        )
        if mutation_root != draft_root:
            draft_root, draft_root_identity = _source_draft_root_identity(
                mutation_root,
            )
            recovered = _recover_source_draft_transaction(
                draft_root,
                root_identity=draft_root_identity,
            )
            if recovered:
                project = Project.load(project.root)
                collection = _find_project_collection(
                    project,
                    collection_id,
                    family=family,
                    source_root=source_root,
                )
                collection_root = _collection_root(collection)
        discovered_members = tuple(
            module
            for module in project.discover_modules(
                family=collection.family,
                collection_id=collection.collection_id,
            ).modules
            if _module_source_root(
                project.root,
                project.source_roots,
                Path(module.root).expanduser().resolve(),
            )
            == selected_source_root
        )
        pointer_modules = _collection_member_pointer_modules(
            project,
            family=collection.family,
            collection_id=collection.collection_id,
            source_root=selected_source_root,
            effective_members=discovered_members,
        )
        members_by_id = {module.module_id: module for module in (*discovered_members, *pointer_modules)}
        member_modules = tuple(members_by_id[module_id] for module_id in sorted(members_by_id))
        edit_requests, removal_requests, member_files = _collection_member_rename_edits(
            project,
            modules=pointer_modules,
            previous_collection_id=collection.collection_id,
            collection_id=None,
        )
        edits = _source_draft_edits(project, list(edit_requests))
        removals = _source_draft_removals(
            draft_root,
            list(removal_requests),
        )
        mutation_paths = tuple(cast(Path, item["path"]) for item in (*edits, *removals))
        if len(mutation_paths) > MAX_PROJECT_SOURCE_DRAFT_FILES:
            raise ValueError("Collection removal must update at most " f"{MAX_PROJECT_SOURCE_DRAFT_FILES} member metadata files.")
        _validate_unique_source_draft_paths(mutation_paths)
        _validate_source_draft_expected_revisions(edits, removals, ())
        diagnostics = _collection_remove_diagnostics(
            project.root,
            collection_root,
        )
        blocked = any(item.get("severity") == "error" for item in diagnostics)
        files = _collection_remove_files(
            project.root,
            collection_root,
            blocked=blocked,
        )
        current_plan_hash = _collection_remove_plan_hash(
            project,
            collection=collection,
            source_root=selected_source_root,
            root=collection_root,
            files=files,
            members=member_modules,
            member_files=member_files,
            edits=edits,
            removals=removals,
        )
        if write and (not isinstance(plan_hash, str) or not plan_hash):
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "collection_remove.plan_hash_required",
                    "message": ("Removing a collection requires the exact plan_hash " "returned by the current dry plan."),
                }
            )
            blocked = True
        elif write and plan_hash != current_plan_hash:
            diagnostics.append(
                {
                    "severity": "error",
                    "code": "collection_remove.plan_hash_mismatch",
                    "message": ("Collection files or member metadata changed after " "planning; review the current plan and apply its plan_hash."),
                    "expected_plan_hash": current_plan_hash,
                    "provided_plan_hash": plan_hash,
                }
            )
            blocked = True
        removed = False
        catalog_mutation: dict[str, object] | None = None
        if write and not blocked:
            prepared = _prepare_project_collection_removal(
                project,
                collection,
                source_root=selected_source_root,
                inventory_digest=_collection_remove_inventory_digest(files),
            )
            from paradev.hb import (
                _module_catalog_mutation_scope,
                _sync_module_catalog_projection,
            )

            with _module_catalog_mutation_scope(
                project,
                enabled=bool(member_modules),
            ) as catalog_lock_held:
                _apply_source_draft_mutations(
                    draft_root,
                    edits=edits,
                    replacements=(),
                    removals=removals,
                    root_identity=draft_root_identity,
                    finalize=lambda: _commit_prepared_collection_removal(
                        project,
                        prepared,
                    ),
                    prepared_rename=prepared,
                )
                if member_modules:
                    catalog_mutation = _sync_module_catalog_projection(
                        project,
                        current={
                            "module_ids": sorted(module.module_id for module in member_modules),
                            "families": [collection.family],
                        },
                        _lock_held=catalog_lock_held,
                    )
            current_project = Project.load(project.root)
            if current_project.discover_collections(
                family=collection.family,
            ).collections:
                matching = [
                    item
                    for item in current_project.discover_collections(
                        family=collection.family,
                    ).collections
                    if item.collection_id == collection.collection_id
                    and _collection_source_root(
                        current_project.root,
                        current_project.source_roots,
                        _collection_root(item),
                    )
                    == selected_source_root
                ]
                if matching:
                    raise RuntimeError("Collection descriptor remained after the committed removal.")
            for module in member_modules:
                current = _find_project_module(
                    current_project,
                    module.module_id,
                    source_root=selected_source_root,
                )
                if current.collection_id is not None:
                    raise RuntimeError(f"Module {module.module_id!r} remained assigned after " "the committed collection removal.")
            removed = True
        payload = _collection_remove_payload(
            project,
            collection=collection,
            source_root=selected_source_root,
            root=collection_root,
            diagnostics=diagnostics,
            blocked=blocked,
            removed=removed,
            files=files,
            members=member_modules,
            member_files=member_files,
            plan_hash=current_plan_hash,
            write=write,
        )
        if catalog_mutation is not None:
            payload["catalog_mutation"] = catalog_mutation
        return payload

    def templates(
        self,
        *,
        template_id: str | None = None,
        family: str | None = None,
        kind: Literal["module", "collection"] | None = None,
        source: str | None = None,
        authoring_ready: bool | None = None,
        diagnostic_code: str | None = None,
    ) -> dict[str, object]:
        """Return SDK authoring templates available to this project.

        Args:
            template_id: Optional exact template id filter.
            family: Optional exact family id filter.
            kind: Optional authoring target filter.
            source: Optional exact template source filter, such as `builtin`
                or `project`.
            authoring_ready: Optional scaffold-readiness filter.
            diagnostic_code: Optional diagnostic-code filter.

        Returns:
            JSON-safe built-in and project-local source-module template payload,
            including configured source roots that can receive scaffolded modules.
            Each template row reports whether its family is currently registered
            and therefore ready for authoring-plan preflight and scaffold writes.
        """

        from paradev.build import authoring_view

        templates = _project_template_index(self)
        build_registry = self._build_registry(profile=self.game)
        registered_families = _registered_family_ids(build_registry)
        family_filter = _canonical_browser_family(family, build_registry) if family is not None else None
        listing_templates = _template_listing_candidates(
            templates.values(),
            include_shadowed_builtin=(template_id is not None or source is not None),
        )
        template_rows = _filter_template_views(
            _template_views(
                listing_templates,
                registered_families,
                build_registry.default_assets_by_family(),
                build_registry,
            ),
            template_id=template_id,
            family=family_filter,
            kind=kind,
            source=source,
            authoring_ready=authoring_ready,
            diagnostic_code=diagnostic_code,
        )
        return {
            "schema": TEMPLATES_SCHEMA,
            "project_id": self.project_id,
            "profile": self.game,
            "preferred_language": self.preferred_language,
            "source_roots": authoring_view(self.root, self.source_roots)["source_roots"],
            "templates": template_rows,
            "index": _template_index(template_rows),
        }

    def authoring_path(
        self,
        kind: str,
        family: str,
        target_id: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
    ) -> dict[str, object]:
        """Return the canonical source folder for a module or collection.

        Args:
            kind: Authoring target kind, either `module` or `collection`.
            family: Registered or project-local family path segment.
            target_id: Module object id or collection id path segment.
            source_root: Optional configured source root path. Relative values
                resolve from the project root. Defaults to the first source root.

        Returns:
            JSON-safe authoring path payload. This method never writes files.

        Raises:
            ValueError: If the kind, family, target id, or source root is invalid.
        """

        from paradev.build import authoring_path_view

        return authoring_path_view(
            project_id=self.project_id,
            project_root=self.root,
            source_roots=self.source_roots,
            kind=kind,
            family=family,
            target_id=target_id,
            source_root=source_root,
        )

    def authoring_plan(
        self,
        kind: str,
        family: str,
        target_id: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
    ) -> dict[str, object]:
        """Return an authoring destination plus expected source-slot contracts.

        Args:
            kind: Authoring target kind, either `module` or `collection`.
            family: Registered or project-local family path segment.
            target_id: Module object id or collection id path segment.
            source_root: Optional configured source root path. Relative values
                resolve from the project root. Defaults to the first source root.
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.

        Returns:
            JSON-safe read-only preflight payload. This method never writes files.

        Raises:
            ValueError: If the authoring target or family is invalid.
        """

        return _project_authoring_plan(
            self,
            kind=kind,
            family=family,
            target_id=target_id,
            source_root=source_root,
            profile=profile,
            registry=registry,
        )

    @_serialize_project_source_mutation
    def scaffold_module(
        self,
        template_id: str,
        object_id: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        values: Mapping[str, object] | None = None,
        write: bool = False,
        force: bool = False,
    ) -> dict[str, object]:
        """Plan or write a source module from an SDK authoring template.

        Args:
            template_id: Template id from `Project.templates()`.
            object_id: New module folder/object id.
            source_root: Optional configured source root path. Relative values
                resolve from the project root. Defaults to the first source root.
            values: Template-specific scalar values.
            write: Whether to write files when the plan is not blocked.
            force: Whether existing files may be overwritten.

        Returns:
            JSON-safe scaffold plan with nested authoring-plan preflight.
            Blocked plans never write files. Written plans include additive
            `catalog_mutation` invalidation/refresh status for the derived Catalog.

        Raises:
            ValueError: If the requested template id is unknown or its family
                is not registered in the current build registry.
        """

        from paradev.hb import _module_catalog_mutation_scope

        selected_source_root = _select_source_root(self.root, self.source_roots, source_root)
        with _module_catalog_mutation_scope(self, enabled=write) as catalog_lock_held:
            return _scaffold_project_module(
                self,
                template_id,
                object_id,
                source_root=selected_source_root,
                values=values,
                write=write,
                force=force,
                catalog_lock_held=catalog_lock_held,
            )

    @_serialize_project_source_mutation
    def scaffold_collection(
        self,
        template_id: str,
        collection_id: str,
        *,
        source_root: str | os.PathLike[str] | None = None,
        values: Mapping[str, object] | None = None,
        write: bool = False,
        force: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or transactionally write a collection from a template.

        Applying a reviewed plan requires its exact ``plan_hash``. Collection
        templates are registered through the same HeavenBase extension records
        as module templates while retaining their distinct source container and
        collection source-slot contract.

        Args:
            template_id: Collection template id or unambiguous family.
            collection_id: Logical collection id.
            source_root: Optional configured source root.
            values: Template-specific scalar values.
            write: Whether to apply the current plan.
            force: Whether existing files may be overwritten.
            plan_hash: Exact hash from a dry plan. Required with ``write=True``.

        Returns:
            JSON-safe collection scaffold plan with authoring preflight.
        """

        selected_source_root = _select_source_root(
            self.root,
            self.source_roots,
            source_root,
        )
        return _scaffold_project_collection(
            self,
            template_id,
            collection_id,
            source_root=selected_source_root,
            values=values,
            write=write,
            force=force,
            plan_hash=plan_hash,
        )

    def create_module(
        self,
        family_or_template: str,
        object_id: str,
        *,
        values: Mapping[str, object] | None = None,
        write: bool = True,
        force: bool = False,
    ) -> dict[str, object]:
        """Plan or create a source module from an authoring template.

        `create_module` is the user-facing SDK verb for creating a new module
        instance. Pass a family such as `idea`, `focus`, or `technology` when
        that family has one matching template, or pass a full template id from
        `Project.templates()` when the family is ambiguous.

        Args:
            family_or_template: Module family shorthand or full template id.
            object_id: New module folder/object id.
            values: Template-specific scalar values.
            write: Whether to write files when the plan is not blocked.
                Defaults to `True` because this is the user-facing creation
                verb. Use `scaffold_module(...)` or pass `write=False` for a
                dry plan.
            force: Whether existing files may be overwritten.

        Returns:
            JSON-safe scaffold plan. Blocked plans never write files. Written
            plans include additive `catalog_mutation` invalidation/refresh status.

        Raises:
            ValueError: If the requested template id or family is unknown or
                ambiguous.
        """

        return self.scaffold_module(
            family_or_template,
            object_id,
            values=values,
            write=write,
            force=force,
        )

    @_serialize_project_source_mutation
    def create_modules(
        self,
        modules: Sequence[Mapping[str, object]],
        *,
        source_root: str | os.PathLike[str] | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        """Plan or atomically create several source modules.

        Each request row requires `object_id`, `values`, and exactly one of
        `family`, `template_id`, or `family_or_template`. Planning is the
        default. Applying a plan requires passing its exact `plan_hash`.
        Existing modules are idempotent only when their complete rendered file
        set already matches the requested template; partial or divergent
        modules block the entire batch.

        Args:
            modules: Ordered module requests for one configured source root.
            source_root: Optional configured source root. Defaults to the first.
            write: Whether to apply the current plan.
            plan_hash: Exact hash returned by a prior plan. Required with
                `write=True`.

        Returns:
            JSON-safe batch plan with per-module statuses, diagnostics, and
            Catalog invalidation/refresh results for modules created by a
            successful transaction.

        Raises:
            ValueError: If the request schema, source root, template, family,
                or batch size is invalid.
        """

        from paradev.hb import _module_catalog_mutation_scope

        selected_source_root = _select_source_root(self.root, self.source_roots, source_root)
        with _module_catalog_mutation_scope(self, enabled=write) as catalog_lock_held:
            return _create_project_modules(
                self,
                modules,
                source_root=selected_source_root,
                write=write,
                plan_hash=plan_hash,
                catalog_lock_held=catalog_lock_held,
            )

    def create_module_draft(
        self,
        family_id: str,
        object_id: str,
        *,
        template_id: str | None = None,
        values: Mapping[str, object] | None = None,
        write: bool = False,
        force: bool = False,
    ) -> dict[str, object]:
        """Plan or write a source-module draft from a browser family id.

        `create_module_draft` is the SDK-owned contract used by the desktop
        GUI when a user starts from a module browser family such as `ideas`.
        It resolves that browser family id to the canonical module template or
        family before delegating to `scaffold_module(...)`.

        Args:
            family_id: Browser family id, such as `ideas`, or a registered
                module family/template shorthand.
            object_id: New module folder/object id.
            template_id: Optional exact template id from `Project.templates()`.
                When omitted, the method resolves `family_id` through the
                project browser family rows.
            values: Template-specific scalar values.
            write: Whether to write files when the plan is not blocked.
            force: Whether existing files may be overwritten.

        Returns:
            JSON-safe module draft payload containing the scaffold plan. A
            written nested plan includes additive `catalog_mutation` status.

        Raises:
            ValueError: If the family, template, object id, or values are
                invalid.
        """

        clean_family_id = _module_path_token(family_id, "family_id")
        clean_object_id = _module_path_token(object_id, "object_id")
        template_ref = _module_draft_template_ref(self, clean_family_id, template_id)
        plan = self.scaffold_module(template_ref, clean_object_id, values=values, write=write, force=force)
        return {
            "schema": MODULE_DRAFT_SCHEMA,
            "project_id": self.project_id,
            "family_id": clean_family_id,
            "draft_id": f"{clean_family_id}:{plan['object_id']}",
            "plan": plan,
        }

    @_serialize_project_build_mutation
    def build(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        modules: tuple["Module", ...] = (),
        collections: tuple["Collection", ...] = (),
        diagnostics: tuple["Diagnostic", ...] = (),
        emit_artifacts: bool = False,
        emit_manifests: bool = False,
        family: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        full_rebuild: bool = False,
        sync_launcher_descriptor: bool = True,
        parallelism: int | None = None,
        strict_metadata: bool | str | None = None,
        progress: Callable[[dict[str, object]], None] | None = None,
    ) -> "BuildResult":
        """Plan this project and optionally publish artifacts or manifests.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            modules: Discovered modules to include in a non-targeted plan.
            collections: Discovered collections to include in a non-targeted plan.
            diagnostics: Existing diagnostics to carry into the plan.
            emit_artifacts: Whether to write planned artifacts under `output_root`.
            emit_manifests: Whether to write build manifest JSON files under `build_root`.
            family: Optional family selector or qualifier for targeted compilation.
            module_id: Optional module id selector. Its owning collection or
                family may be included when required for safe publication.
                When ``family`` is supplied, either ``family/object_id`` or the
                shorter ``object_id`` form is accepted.
            collection_id: Optional collection id selector. Pass ``family``
                when the id is ambiguous across families.
            full_rebuild: Whether to clean generated output/build roots before
                emission. Registered HOI4 output directories remain present so
                launcher playsets keep their on-disk identity.
            sync_launcher_descriptor: Whether artifact emission should also
                synchronize the generated HoI4 launcher descriptor outside the
                project output root. Disable this for project-only or GUI
                builds that must not depend on game-launcher ownership.
            parallelism: Optional worker count for independent family compilation.
                Defaults to `paradev.build.parallelism` from `CM_PARADEV`.
            strict_metadata: Whether unknown module or collection metadata keys
                should be blocking errors instead of loose-mode warnings.
                Defaults to `paradev.build.strict_metadata` from `CM_PARADEV`.
            progress: Optional callback for JSON-safe build progress events.

        Returns:
            Complete or safely scoped build result. ``dry_run`` remains true
            when no artifacts were emitted or blocking diagnostics prevented
            artifact publication.
        """

        from paradev.build.plan import _finalize_build_draft, _plan_build_draft
        from paradev.build.progress import emit_progress

        module_id = _normalize_build_module_selector(
            family=family,
            module_id=module_id,
        )
        targeted_request = any(target is not None for target in (family, module_id, collection_id))
        _validate_build_selector_shape(family=family, module_id=module_id, collection_id=collection_id)
        if emit_artifacts or emit_manifests:
            _validate_project_build_roots(self)
        if targeted_request and (modules or collections):
            raise ValueError("Targeted builds discover their complete safe scope and cannot accept injected modules or collections.")
        if full_rebuild and targeted_request:
            raise ValueError("A full rebuild cannot be combined with a family, collection, or module target.")
        profile_id = profile or self.game
        build_registry = self._build_registry(profile=profile_id, registry=registry)
        if family is not None and family not in _registered_family_ids(build_registry):
            raise ValueError(f"Unknown build family: {family}")
        build_parallelism = _build_parallelism(parallelism)
        build_strict_metadata = _build_strict_metadata(strict_metadata)
        discovery_family = None if targeted_request else family
        discovery_module_id = None if targeted_request else module_id
        discovery_collection_id = None if targeted_request else collection_id
        module_tuple = modules
        collection_tuple = collections
        diagnostic_tuple = diagnostics
        emit_progress(
            progress,
            "discover_modules",
            detail=(
                "Scanning every source module without cache reuse." if full_rebuild else "Checking source fingerprints and reusing unchanged parsed modules."
            ),
            label="Finding modules",
            percent=4,
        )
        module_cache_hits = 0
        module_cache_misses = 0
        module_cache_refreshes = 0
        cached_modules = 0
        module_cache_signature: str | None = None
        if not module_tuple:
            if full_rebuild:
                discovered = self._discover_modules(
                    registry=build_registry,
                    strict_metadata=build_strict_metadata,
                    family=discovery_family,
                    module_id=discovery_module_id,
                    collection_id=discovery_collection_id,
                    source_cache_read=False,
                    parallelism=build_parallelism,
                )
            else:
                discovered = self._discover_modules(
                    registry=build_registry,
                    strict_metadata=build_strict_metadata,
                    family=discovery_family,
                    module_id=discovery_module_id,
                    collection_id=discovery_collection_id,
                    source_cache_read=True,
                    parallelism=build_parallelism,
                )
            module_tuple = discovered.modules
            diagnostic_tuple = (*diagnostic_tuple, *discovered.diagnostics)
            module_cache_hits = discovered.cache_hits
            module_cache_misses = discovered.cache_misses
            module_cache_refreshes = discovered.cache_refreshes
            cached_modules = discovered.cached_records
            module_cache_signature = discovered.cache_signature
        module_discovery_counts = {"modules": len(module_tuple)}
        if module_cache_hits or module_cache_misses or module_cache_refreshes:
            module_discovery_counts.update(
                {
                    "cached_modules": cached_modules,
                    "source_cache_hits": module_cache_hits,
                    "source_cache_misses": module_cache_misses,
                    "source_cache_refreshes": module_cache_refreshes,
                }
            )
        module_discovery_detail = f"{len(module_tuple)} modules discovered."
        if module_cache_hits:
            module_discovery_detail = (
                f"{len(module_tuple)} modules discovered; reused {cached_modules} " f"parsed modules from {module_cache_hits} unchanged source families."
            )
        emit_progress(
            progress,
            "discover_modules",
            counts=module_discovery_counts,
            detail=module_discovery_detail,
            label="Finding modules",
            percent=12,
            total=len(module_tuple),
        )
        emit_progress(
            progress,
            "discover_collections",
            detail=(
                "Scanning every collection descriptor without cache reuse."
                if full_rebuild
                else "Checking source fingerprints and reusing unchanged collection descriptors."
            ),
            label="Finding collections",
            percent=14,
        )
        collection_cache_hits = 0
        collection_cache_misses = 0
        collection_cache_refreshes = 0
        cached_collections = 0
        collection_cache_signature: str | None = None
        if not collection_tuple:
            if full_rebuild:
                discovered_collections = self._discover_collections(
                    registry=build_registry,
                    strict_metadata=build_strict_metadata,
                    family=discovery_family,
                    collection_id=discovery_collection_id,
                    module_id=discovery_module_id,
                    source_cache_read=False,
                    parallelism=build_parallelism,
                )
            else:
                discovered_collections = self._discover_collections(
                    registry=build_registry,
                    strict_metadata=build_strict_metadata,
                    family=discovery_family,
                    collection_id=discovery_collection_id,
                    module_id=discovery_module_id,
                    source_cache_read=True,
                    parallelism=build_parallelism,
                )
            collection_tuple = discovered_collections.collections
            diagnostic_tuple = (*diagnostic_tuple, *discovered_collections.diagnostics)
            collection_cache_hits = discovered_collections.cache_hits
            collection_cache_misses = discovered_collections.cache_misses
            collection_cache_refreshes = discovered_collections.cache_refreshes
            cached_collections = discovered_collections.cached_records
            collection_cache_signature = discovered_collections.cache_signature
        collection_discovery_counts = {"collections": len(collection_tuple)}
        if collection_cache_hits or collection_cache_misses or collection_cache_refreshes:
            collection_discovery_counts.update(
                {
                    "cached_collections": cached_collections,
                    "source_cache_hits": collection_cache_hits,
                    "source_cache_misses": collection_cache_misses,
                    "source_cache_refreshes": collection_cache_refreshes,
                }
            )
        collection_discovery_detail = f"{len(collection_tuple)} collections discovered."
        if collection_cache_hits:
            collection_discovery_detail = (
                f"{len(collection_tuple)} collections discovered; reused "
                f"{cached_collections} descriptors from {collection_cache_hits} "
                "unchanged source families."
            )
        emit_progress(
            progress,
            "discover_collections",
            counts=collection_discovery_counts,
            detail=collection_discovery_detail,
            label="Finding collections",
            percent=24,
            total=len(collection_tuple),
        )
        if module_id is not None:
            inactive_target = next(
                (module for module in module_tuple if module.module_id == module_id and module.metadata.get("inactive") is True),
                None,
            )
            if inactive_target is not None:
                raise ValueError(f"Build module {module_id!r} is inactive. Activate it before " "requesting a module-partial build.")

        copy_artifacts, copy_diagnostics = copy_root_artifacts(self.copy_roots)
        diagnostic_tuple = (*diagnostic_tuple, *copy_diagnostics)
        emit_progress(
            progress,
            "basic_copy",
            counts={"artifacts": len(copy_artifacts)},
            detail=f"{len(copy_artifacts)} static copy artifacts planned.",
            label="Copying static files",
            percent=28,
            total=len(copy_artifacts),
        )
        plan_metadata: dict[str, object] = {
            **self.descriptor_metadata,
            "title": self.title,
            "game": self.game,
            "root": str(self.root),
            "output_root": str(self.output_root),
            "build_root": str(self.build_root),
            "emit_artifacts": emit_artifacts,
        }

        def build_artifact_plan() -> BuildResult:
            draft = _plan_build_draft(
                project_id=self.project_id,
                registry=build_registry,
                profile=profile_id,
                metadata=plan_metadata,
                modules=module_tuple,
                collections=collection_tuple,
                diagnostics=diagnostic_tuple,
                parallelism=build_parallelism,
                progress=progress,
            )
            active_copy_artifacts, shadow_diagnostics = merge_copy_root_artifacts(
                copy_artifacts,
                draft.artifacts,
            )
            return _finalize_build_draft(
                draft,
                build_registry,
                artifacts=(*active_copy_artifacts, *draft.artifacts),
                trailing_diagnostics=shadow_diagnostics,
                progress=progress,
            )

        artifact_cache_root = _project_artifact_plan_cache_root(self)
        manifest_plan_signature: str | None = None
        artifact_cache_eligible = (
            artifact_cache_root is not None
            and registry is None
            and not modules
            and not collections
            and not diagnostics
            and module_cache_signature is not None
            and collection_cache_signature is not None
        )
        if artifact_cache_eligible:
            assert artifact_cache_root is not None
            assert module_cache_signature is not None
            assert collection_cache_signature is not None
            from paradev.build.artifact_cache import (
                artifact_plan_signature,
                cached_artifact_plan,
            )

            def plan_signature() -> str | None:
                return artifact_plan_signature(
                    project_id=self.project_id,
                    profile=profile_id,
                    metadata=plan_metadata,
                    module_cache_signature=module_cache_signature,
                    collection_cache_signature=collection_cache_signature,
                    copy_artifacts=copy_artifacts,
                    copy_diagnostics=copy_diagnostics,
                    registry=build_registry,
                )

            cached_plan = cached_artifact_plan(
                artifact_cache_root,
                project_id=self.project_id,
                project_root=self.root,
                profile=profile_id,
                emit_artifacts=emit_artifacts,
                signature=plan_signature,
                source_modules=module_tuple,
                source_collections=collection_tuple,
                read=not full_rebuild,
                write=True,
                builder=build_artifact_plan,
            )
            result = cached_plan.result
            manifest_plan_signature = cached_plan.signature
            if cached_plan.status == "hit":
                emit_progress(
                    progress,
                    "collection_compile",
                    counts={
                        "artifact_plan_cache_hits": 1,
                        "collections": len(result.collections),
                        "modules": len(result.modules),
                    },
                    detail="Reused the unchanged validated artifact plan.",
                    label="Compiling collections",
                    percent=36,
                    total=len(result.collections),
                )
                emit_progress(
                    progress,
                    "entity_compile",
                    counts={
                        "artifact_plan_cache_hits": 1,
                        "artifacts": len(result.artifacts),
                    },
                    detail="Skipped unchanged family compilation.",
                    label="Compiling entities",
                    percent=72,
                )
                emit_progress(
                    progress,
                    "artifact_generation",
                    counts={
                        "artifact_plan_cache_hits": 1,
                        "artifacts": len(result.artifacts),
                    },
                    detail=f"{len(result.artifacts)} cached artifacts planned.",
                    label="Planning artifacts",
                    percent=74,
                    total=len(result.artifacts),
                )
        else:
            result = build_artifact_plan()
        planned_building_strip = None
        if profile_id == "hoi4":
            from paradev.games.hoi4.building_icons import (
                _planned_building_icon_strip,
            )

            planned_building_strip = _planned_building_icon_strip(result)
            if planned_building_strip is not None:
                result = _replace_build_artifact_deltas(
                    result,
                    (planned_building_strip,),
                )
        build_target = (
            _resolve_build_target(
                result,
                family=family,
                module_id=module_id,
                collection_id=collection_id,
            )
            if targeted_request
            else None
        )
        publication_target_families = build_target.families if build_target is not None else None
        publication_family_wide_families: set[str] = set()
        if build_target is not None and build_target.kind == "family":
            replaced_families = {
                replaced_family for active_family in build_target.families for replaced_family in build_registry.publication_replacements_for(active_family)
            }
            publication_target_families = build_target.families.union(replaced_families)
            publication_family_wide_families.update(replaced_families)
        emission_result = _targeted_build_result(result, target=build_target) if build_target is not None else result
        artifacts_emitted = False
        staged_pruned_count = 0
        projected_publication = None
        building_postprocess = profile_id == "hoi4" and (build_target is None or "building" in build_target.families)
        publication_plan = result
        planned_strip = planned_building_strip if building_postprocess else None
        artifact_stage_transform: Callable[[Artifact, Path], None] | None = None
        artifact_stage_transform_required: Callable[[Artifact], bool] | None = None
        if building_postprocess:
            from paradev.games.hoi4.building_icons import (
                _building_icon_stage_transform,
                _building_icon_stage_transform_required,
            )

            artifact_stage_transform = _building_icon_stage_transform(result)
            artifact_stage_transform_required = _building_icon_stage_transform_required
            if planned_strip is not None:
                publication_plan = _replace_planned_build_artifact(result, planned_strip)
        published_result = emission_result
        if planned_strip is not None:
            published_result = _replace_planned_build_artifact(published_result, planned_strip)
        if emit_artifacts and not emission_result.blocked:
            from paradev.build.publication import _project_artifact_publication

            artifact_count = len(emission_result.artifacts)
            emit_progress(
                progress,
                "validating_publication",
                counts={"artifacts": artifact_count},
                detail=f"Checking {artifact_count} planned artifacts against existing generated output.",
                label="Validating publication",
                percent=75,
                total=artifact_count,
            )
            projected_publication = _project_artifact_publication(
                published_result,
                planned_result=publication_plan,
            )
        if emit_artifacts or emit_manifests:
            include_launcher = emit_artifacts and sync_launcher_descriptor
            mutation_roots = _project_build_mutation_roots(
                self,
                include_launcher=include_launcher,
            )
            mutation_scope = nullcontext() if _BUILD_MUTATION_SCOPE_ACTIVE.get() else _project_build_mutation_lock(*mutation_roots)
            with mutation_scope:
                include_output = emit_artifacts and not emission_result.blocked
                with _project_publication_roots(
                    self,
                    include_output=include_output,
                    include_launcher=include_output and sync_launcher_descriptor,
                ) as (output_publication, build_publication, launcher_publication):
                    from paradev.build.publication import (
                        claim_publication_root,
                        inspect_publication_root,
                        load_build_root_ownership,
                        require_publishable_manifests,
                    )

                    build_root_state = inspect_publication_root(
                        build_publication,
                        root_name="build",
                        project_id=self.project_id,
                        project_root=self.root,
                    )
                    output_root_state = (
                        inspect_publication_root(
                            output_publication,
                            root_name="output",
                            project_id=self.project_id,
                            project_root=self.root,
                        )
                        if output_publication is not None
                        else None
                    )
                    legacy_build_root_owned = (
                        load_build_root_ownership(
                            build_publication,
                            project_id=self.project_id,
                            project_root=self.root,
                        )
                        if not build_root_state.claimed
                        else False
                    )
                    _preflight_hoi4_launcher_descriptor_anchored(
                        self,
                        launcher_root=launcher_publication,
                    )
                    if emit_manifests:
                        require_publishable_manifests(
                            build_publication,
                            root_claimed=build_root_state.claimed,
                            project_id=self.project_id,
                        )
                    build_root_claimed = build_root_state.claimed
                    output_root_claimed = output_root_state.claimed if output_root_state is not None else False
                    previous_publication_rows: tuple[dict[str, object], ...] = ()
                    full_clean_owned: dict[str, bool] = {
                        "build": False,
                        "output": False,
                    }
                    whole_project_baseline = False
                    if emit_artifacts and not emission_result.blocked:
                        if output_publication is None:
                            raise AssertionError("Artifact emission requires an output publication authority.")
                        from paradev.build.artifacts import _write_artifacts_anchored
                        from paradev.build.publication import (
                            _begin_publication_transaction,
                            PublicationWritePermissions,
                            clean_tracked_artifacts,
                            load_publication_state,
                            record_written_artifacts,
                            require_publishable_artifacts,
                            stage_emitted_artifacts,
                        )

                        if projected_publication is None:
                            raise AssertionError("Artifact emission requires a validated publication plan.")
                        publication_state = load_publication_state(
                            build_publication,
                            project_id=self.project_id,
                            project_root=self.root,
                            output_root=output_publication,
                        )
                        previous_publication_rows = publication_state.rows
                        whole_project_baseline = publication_state.whole_project_baseline
                        if output_root_state is None:
                            raise AssertionError("Artifact emission requires output-root ownership state.")
                        full_clean_owned = {
                            "build": build_root_state.full_clean_owned or (not build_root_state.claimed and publication_state.full_clean_owned["build"]),
                            "output": output_root_state.full_clean_owned or (not output_root_state.claimed and publication_state.full_clean_owned["output"]),
                        }
                        publication_transaction = _begin_publication_transaction(
                            projected_publication,
                            previous_rows=previous_publication_rows,
                            target_modules=build_target.modules if build_target is not None else None,
                            target_collections=build_target.collections if build_target is not None else None,
                            target_families=publication_target_families,
                            family_wide=build_target is not None and build_target.kind == "family",
                            family_wide_families=publication_family_wide_families,
                        )
                        publication_permissions: PublicationWritePermissions
                        if full_rebuild:
                            unowned_roots = [name for name in ("output", "build") if not full_clean_owned[name]]
                            ledger_cleanable = publication_state.complete and publication_state.whole_project_baseline
                            if unowned_roots and not ledger_cleanable:
                                names = ", ".join(unowned_roots)
                                raise ValueError(
                                    f"Full rebuild refuses to clean nonempty generated roots not owned by this project: {names}. "
                                    "Run one successful whole-project cached build first, or empty the roots before adopting them."
                                )
                            emit_progress(
                                progress,
                                "post_processing",
                                detail="Cleaning generated output roots while preserving untracked files.",
                                label="Full rebuild",
                                percent=75,
                            )
                            if unowned_roots:
                                clean_tracked_artifacts(
                                    result,
                                    project_root=self.root,
                                    output_root=output_publication,
                                    build_root=build_publication,
                                    previous_rows=previous_publication_rows,
                                    target_roots=frozenset(unowned_roots),
                                    full_clean_owned=full_clean_owned,
                                    whole_project_baseline=whole_project_baseline,
                                )
                            if full_clean_owned["output"]:
                                output_publication.clear()
                            if full_clean_owned["build"]:
                                build_publication.clear()
                            previous_publication_rows = ()
                            whole_project_baseline = False
                            publication_transaction = _begin_publication_transaction(
                                projected_publication,
                                previous_rows=previous_publication_rows,
                                target_modules=build_target.modules if build_target is not None else None,
                                target_collections=build_target.collections if build_target is not None else None,
                                target_families=publication_target_families,
                                family_wide=build_target is not None and build_target.kind == "family",
                                family_wide_families=publication_family_wide_families,
                            )
                            if full_clean_owned["output"]:
                                full_clean_owned["output"] = claim_publication_root(
                                    output_publication,
                                    root_name="output",
                                    project_id=self.project_id,
                                    project_root=self.root,
                                    full_clean_owned=True,
                                    require_empty_for_full_clean=True,
                                )
                            if full_clean_owned["build"]:
                                full_clean_owned["build"] = claim_publication_root(
                                    build_publication,
                                    root_name="build",
                                    project_id=self.project_id,
                                    project_root=self.root,
                                    full_clean_owned=True,
                                    require_empty_for_full_clean=True,
                                )
                            output_root_claimed = True
                            build_root_claimed = True
                            publication_permissions = PublicationWritePermissions(
                                replace_paths={
                                    "build": frozenset(),
                                    "output": frozenset(),
                                },
                                adopt_paths={
                                    "build": frozenset(),
                                    "output": frozenset(),
                                },
                                rename_paths={
                                    "build": {},
                                    "output": {},
                                },
                            )
                        else:
                            publication_permissions = require_publishable_artifacts(
                                published_result,
                                output_root=output_publication,
                                build_root=build_publication,
                                previous_rows=previous_publication_rows,
                                claimed_roots={
                                    "build": build_root_claimed,
                                    "output": output_root_claimed,
                                },
                                artifact_rows=projected_publication.current_by_key.values(),
                            )
                            if not output_root_claimed:
                                full_clean_owned["output"] = claim_publication_root(
                                    output_publication,
                                    root_name="output",
                                    project_id=self.project_id,
                                    project_root=self.root,
                                    full_clean_owned=full_clean_owned["output"],
                                    require_empty_for_full_clean=output_root_state.full_clean_owned,
                                )
                                output_root_claimed = True
                            if not build_root_claimed:
                                full_clean_owned["build"] = claim_publication_root(
                                    build_publication,
                                    root_name="build",
                                    project_id=self.project_id,
                                    project_root=self.root,
                                    full_clean_owned=full_clean_owned["build"],
                                    require_empty_for_full_clean=build_root_state.full_clean_owned,
                                )
                                build_root_claimed = True
                        staged_pruned_count = stage_emitted_artifacts(
                            published_result,
                            planned_result=publication_plan,
                            project_root=self.root,
                            output_root=output_publication,
                            build_root=build_publication,
                            previous_rows=previous_publication_rows,
                            target_modules=build_target.modules if build_target is not None else None,
                            target_collections=build_target.collections if build_target is not None else None,
                            target_families=publication_target_families,
                            family_wide=build_target is not None and build_target.kind == "family",
                            family_wide_families=publication_family_wide_families,
                            full_clean_owned=full_clean_owned,
                            whole_project_baseline=whole_project_baseline,
                            transaction=publication_transaction,
                        )
                        confirmed_artifacts: list[Artifact] = []

                        def confirm_artifact(artifact: Artifact, _path: Path) -> None:
                            confirmed_artifacts.append(artifact)

                        def persist_confirmed_artifacts() -> None:
                            if not confirmed_artifacts:
                                return
                            record_written_artifacts(
                                published_result,
                                artifacts=tuple(confirmed_artifacts),
                                project_root=self.root,
                                output_root=output_publication,
                                build_root=build_publication,
                                full_clean_owned=full_clean_owned,
                                whole_project_baseline=whole_project_baseline,
                                transaction=publication_transaction,
                            )
                            confirmed_artifacts.clear()

                        planned_strip_key = _build_artifact_key(planned_strip) if planned_strip is not None else None
                        output_artifacts = tuple(
                            artifact
                            for artifact in emission_result.artifacts
                            if artifact.target_root == "output" and (planned_strip_key is None or _build_artifact_key(artifact) != planned_strip_key)
                        )
                        build_artifacts = tuple(artifact for artifact in emission_result.artifacts if artifact.target_root == "build")
                        if output_artifacts:
                            try:
                                _write_artifacts_anchored(
                                    replace(emission_result, artifacts=output_artifacts),
                                    build_registry,
                                    output_publication,
                                    progress=progress,
                                    progress_start=76,
                                    progress_end=88,
                                    on_written=confirm_artifact,
                                    replace_paths=publication_permissions.replace_paths["output"],
                                    adopt_paths=publication_permissions.adopt_paths["output"],
                                    rename_paths=publication_permissions.rename_paths["output"],
                                    stage_transform=artifact_stage_transform,
                                    stage_transform_required=artifact_stage_transform_required,
                                )
                            finally:
                                persist_confirmed_artifacts()
                        if build_artifacts:
                            try:
                                _write_artifacts_anchored(
                                    replace(emission_result, artifacts=build_artifacts),
                                    build_registry,
                                    build_publication,
                                    progress=progress,
                                    progress_start=89,
                                    progress_end=94,
                                    on_written=confirm_artifact,
                                    replace_paths=publication_permissions.replace_paths["build"],
                                    adopt_paths=publication_permissions.adopt_paths["build"],
                                    rename_paths=publication_permissions.rename_paths["build"],
                                )
                            finally:
                                persist_confirmed_artifacts()
                        if building_postprocess:
                            from paradev.games.hoi4.building_icons import (
                                _postprocess_building_icon_strip_anchored,
                            )

                            postprocess_replace_paths = set(publication_permissions.replace_paths["output"])
                            postprocess_replace_paths.update(str(artifact.path).replace("\\", "/") for artifact in output_artifacts)
                            postprocess_adopt_paths = set(publication_permissions.adopt_paths["output"])
                            try:
                                building_icons = _postprocess_building_icon_strip_anchored(
                                    result,
                                    output_root=output_publication,
                                    on_written=confirm_artifact,
                                    replace_paths=frozenset(postprocess_replace_paths),
                                    adopt_paths=frozenset(postprocess_adopt_paths),
                                    rename_paths=publication_permissions.rename_paths["output"],
                                )
                            finally:
                                persist_confirmed_artifacts()
                            result = _replace_build_artifact_deltas(result, building_icons.artifacts)
                            if building_icons.frame_count:
                                emit_progress(
                                    progress,
                                    "post_processing",
                                    detail=f"Generated building icon strip with {building_icons.frame_count} frames.",
                                    label="Building icons",
                                    percent=95,
                                )
                        if sync_launcher_descriptor:
                            _sync_hoi4_launcher_descriptor_anchored(
                                self,
                                build_root=build_publication,
                                launcher_root=launcher_publication,
                            )
                            emit_progress(
                                progress,
                                "post_processing",
                                detail="Launcher descriptor synced.",
                                label="Post-processing",
                                percent=96,
                            )
                        else:
                            emit_progress(
                                progress,
                                "post_processing",
                                detail="Project artifacts published; game-launcher integration was skipped.",
                                label="Post-processing",
                                percent=96,
                            )
                        result = replace(result, dry_run=False)
                        artifacts_emitted = True
                    elif emit_artifacts:
                        emit_progress(
                            progress,
                            "post_processing",
                            detail="Artifact emission skipped because the build has blocking diagnostics.",
                            label="Build blocked",
                            percent=96,
                        )
                    if emit_manifests:
                        from paradev.build.manifest import _write_manifests_anchored

                        if not build_root_claimed:
                            claim_publication_root(
                                build_publication,
                                root_name="build",
                                project_id=self.project_id,
                                project_root=self.root,
                                full_clean_owned=build_root_state.full_clean_owned or legacy_build_root_owned,
                                require_empty_for_full_clean=build_root_state.full_clean_owned,
                            )
                            build_root_claimed = True
                        manifest_cache_path = _project_manifest_publication_cache_path(self) if manifest_plan_signature is not None else None
                        _write_manifests_anchored(
                            result,
                            build_publication,
                            cache_path=manifest_cache_path,
                            plan_signature=(manifest_plan_signature if manifest_cache_path is not None else None),
                        )
                        emit_progress(
                            progress,
                            "post_processing",
                            detail="Build manifests synchronized.",
                            label="Post-processing",
                            percent=98,
                        )
                    if artifacts_emitted:
                        from paradev.build.publication import (
                            reconcile_emitted_artifacts,
                        )

                        if output_publication is None:
                            raise AssertionError("Artifact reconciliation requires an output publication authority.")
                        output_publication.verify_path()
                        build_publication.verify_path()
                        published_result = _targeted_build_result(result, target=build_target) if build_target is not None else result
                        reconcile_emitted_artifacts(
                            published_result,
                            planned_result=result,
                            project_root=self.root,
                            output_root=output_publication,
                            build_root=build_publication,
                            previous_rows=previous_publication_rows,
                            target_modules=build_target.modules if build_target is not None else None,
                            target_collections=build_target.collections if build_target is not None else None,
                            target_families=publication_target_families,
                            family_wide=build_target is not None and build_target.kind == "family",
                            family_wide_families=publication_family_wide_families,
                            delete_stale=True,
                            full_clean_owned=full_clean_owned,
                            whole_project_baseline=whole_project_baseline or build_target is None,
                            transaction=publication_transaction,
                        )
                        if staged_pruned_count:
                            emit_progress(
                                progress,
                                "post_processing",
                                counts={"artifacts": staged_pruned_count},
                                detail=f"Removed {staged_pruned_count} stale generated artifacts.",
                                label="Reconciling outputs",
                                percent=99,
                                total=staged_pruned_count,
                            )
        emit_progress(
            progress,
            "complete",
            detail="Build complete.",
            label="Complete",
            percent=100,
        )
        if build_target is not None:
            return _targeted_build_result(result, target=build_target)
        return result

    def summary(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
    ) -> dict[str, object]:
        """Return the current build summary manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.

        Returns:
            JSON-safe summary manifest payload.
        """

        from paradev.build import summary_view

        result = self.build(profile=profile, registry=registry)
        return summary_view(result)

    def manifests(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
    ) -> dict[str, object]:
        """Return all current build manifest payloads without writing files.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.

        Returns:
            JSON-safe payload keyed by manifest file name.
        """

        from paradev.build import manifests_view

        result = self.build(profile=profile, registry=registry)
        return manifests_view(result)

    def inspections(self) -> dict[str, object]:
        """Return the read-only project inspection contract for adapters.

        Returns:
            JSON-safe list of supported `Project.inspect(...)` kinds, direct
            SDK methods, CLI command names, public filters, and lookup indexes.
        """

        return get_project_inspection_contract(project_id=self.project_id)

    def inspect(self, kind: str, /, **filters: object) -> dict[str, object]:
        """Return one JSON-safe project inspection payload.

        Args:
            kind: Inspection kind, such as `modules`, `artifacts`,
                `diagnostics`, `source-map`, `build-graph`, or `families`.
            **filters: Optional filters accepted by the selected inspection
                method. `None` values are ignored.

        Returns:
            JSON-safe inspection payload from the selected SDK method.

        Raises:
            ValueError: If `kind` is unknown or a filter is unsupported by the
                selected inspection method.
        """

        method_name = _inspection_method_name(kind)
        method = getattr(self, method_name)
        active_filters = {key: value for key, value in filters.items() if value is not None}
        if method_name == "catalog_query":
            from paradev._catalog import normalize_catalog_query_filters

            active_filters = normalize_catalog_query_filters(active_filters)
        unsupported = sorted(set(active_filters) - set(signature(method).parameters))
        if unsupported:
            names = ", ".join(unsupported)
            raise ValueError(f"Unsupported filters for project inspection kind {kind!r}: {names}.")
        return method(**active_filters)

    def browser(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        kind: str | None = None,
        family: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
    ) -> dict[str, object]:
        """Return a frontend-ready project browser payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            kind: Optional item kind filter, either `module` or `collection`.
            family: Optional module or collection family filter.
            module_id: Optional exact module id filter. Also filters
                collections that contain the module.
            collection_id: Optional collection id filter. Also filters modules
                assigned to that collection.

        Returns:
            JSON-safe read-only project browser payload with item rows,
            family groups, and lookup indexes for frontend adapters.
        """

        from paradev.build import (
            authoring_view,
            collections_view,
            module_collections,
            modules_view,
        )

        item_kind = _project_browser_kind(kind)
        profile_id = profile or self.game
        build_registry = self._build_registry(profile=profile_id, registry=registry)
        family_filter = _canonical_browser_family(family, build_registry) if family is not None else None
        module_filter = _project_browser_module_filter(family_filter, module_id)
        result = self._browser_build(
            profile=profile_id,
            registry=build_registry,
            family=family_filter,
            module_id=module_filter,
            collection_id=collection_id,
        )
        browser_modules = _project_browser_authoring_modules(
            self,
            registry=build_registry,
            result=result,
            family=family_filter,
            module_id=module_filter,
            collection_id=collection_id,
        )
        browser_result = replace(
            result,
            modules=browser_modules,
            collections=module_collections(browser_modules, result.collections),
        )
        modules_payload = modules_view(
            browser_result,
            family=family_filter,
            module_id=module_filter,
            collection_id=collection_id,
        )
        collections_payload = collections_view(
            browser_result,
            family=family_filter,
            collection_id=collection_id,
            module_id=module_filter,
        )
        collection_roots = _project_browser_collection_roots(result.collections)
        module_localized_titles = _project_browser_module_localized_titles(
            browser_modules,
            registry=build_registry,
        )
        module_title_keys = {
            module.module_id: _project_browser_module_title_keys(
                module,
                registry=build_registry,
            )
            for module in browser_modules
        }
        collection_localized_titles = _project_browser_collection_localized_titles(
            result.collections,
            registry=build_registry,
        )
        items: list[dict[str, object]] = []
        module_items: list[dict[str, object]] = []
        if item_kind in {None, "module"}:
            for row in _mapping_rows(modules_payload.get("modules")):
                module_id_key = _required_row_string(row, "module_id")
                module_items.append(
                    _project_browser_module_item(
                        self,
                        row,
                        declared_source_slots=build_registry.source_slots_for(_required_row_string(row, "family")),
                        registry=build_registry,
                        localized_titles=module_localized_titles.get(module_id_key, {}),
                        title_keys=module_title_keys.get(module_id_key, ()),
                    )
                )
            items.extend(module_items)
        if item_kind in {None, "collection"}:
            for row in _mapping_rows(collections_payload.get("collections")):
                collection_key = (
                    _required_row_string(row, "family"),
                    _required_row_string(row, "collection_id"),
                )
                items.append(
                    _project_browser_collection_item(
                        self,
                        row,
                        collection_roots,
                        declared_source_slots=build_registry.collection_source_slots_for(_required_row_string(row, "family")),
                        registry=build_registry,
                        localized_titles=collection_localized_titles.get(collection_key, {}),
                    )
                )
        if item_kind is None and module_id is None and collection_id is None:
            items.extend(
                _project_browser_family_root_items(
                    self,
                    registry=build_registry,
                    family=family_filter,
                    shadowed_modules=_project_browser_module_keys(module_items),
                )
            )
        items = sorted(items, key=_project_browser_item_key)
        return {
            "schema": PROJECT_BROWSER_SCHEMA,
            "project_id": self.project_id,
            "title": self.title,
            "game": self.game,
            "profile": profile_id,
            "root": str(self.root),
            "authoring": authoring_view(self.root, self.source_roots),
            "filters": _project_browser_filters(
                kind=item_kind,
                family=family,
                module_id=module_filter,
                collection_id=collection_id,
            ),
            "items": items,
            "families": _project_browser_families(
                items,
                registry=build_registry,
                diagram_by_family=build_registry.diagram_views_by_family(),
            ),
            "groups": _project_browser_groups(items),
            "index": _project_browser_index(items),
            "diagnostics": [diagnostic.to_dict() for diagnostic in result.diagnostics],
        }

    def browser_summary(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        kind: str | None = None,
        family: str | None = None,
    ) -> dict[str, object]:
        """Return a cheap project browser summary without parsing source files.

        The desktop shell uses this during startup so it can show persisted or
        freshly counted module totals without paying the full browser-item parse
        cost for every module in a large project.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            kind: Optional item kind filter, either `module` or `collection`.
            family: Optional module or collection family filter.

        Returns:
            JSON-safe family and group counts with explicit navigation visibility.
        """

        from paradev.build import authoring_view

        item_kind = _project_browser_kind(kind)
        profile_id = profile or self.game
        build_registry = self._build_registry(profile=profile_id, registry=registry)
        family_filter = _canonical_browser_family(family, build_registry) if family is not None else None
        families, groups = _project_browser_summary_families(
            self,
            registry=build_registry,
            kind=item_kind,
            family=family_filter,
            diagram_by_family=build_registry.diagram_views_by_family(),
        )
        return {
            "schema": PROJECT_BROWSER_SCHEMA,
            "project_id": self.project_id,
            "title": self.title,
            "game": self.game,
            "profile": profile_id,
            "root": str(self.root),
            "authoring": authoring_view(self.root, self.source_roots),
            "filters": _project_browser_filters(
                kind=item_kind,
                family=family,
                module_id=None,
                collection_id=None,
            ),
            "items": [],
            "families": families,
            "groups": groups,
            "index": {},
            "diagnostics": [],
        }

    def _browser_build(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        family: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
    ) -> "BuildResult":
        """Return a dry build result with scoped discovery for browser filters."""

        from paradev.build.plan import _finalize_build_draft, _plan_build_draft

        if family is None and module_id is None and collection_id is None:
            return self.build(profile=profile, registry=registry)

        profile_id = profile or self.game
        build_registry = self._build_registry(profile=profile_id, registry=registry)
        module_discovery_id = module_id if module_id and "/" in module_id else None
        discovered = self.discover_modules(
            registry=build_registry,
            family=family,
            module_id=module_discovery_id,
            collection_id=collection_id,
        )
        discovered_collections = self.discover_collections(
            registry=build_registry,
            family=family,
            collection_id=collection_id,
            module_id=module_discovery_id,
        )
        copy_artifacts, copy_diagnostics = copy_root_artifacts(self.copy_roots)
        draft = _plan_build_draft(
            project_id=self.project_id,
            registry=build_registry,
            profile=profile_id,
            metadata={
                **self.descriptor_metadata,
                "title": self.title,
                "game": self.game,
                "root": str(self.root),
                "output_root": str(self.output_root),
                "build_root": str(self.build_root),
            },
            modules=discovered.modules,
            collections=discovered_collections.collections,
            diagnostics=(
                *discovered.diagnostics,
                *discovered_collections.diagnostics,
                *copy_diagnostics,
            ),
        )
        active_copy_artifacts, shadow_diagnostics = merge_copy_root_artifacts(copy_artifacts, draft.artifacts)
        return _finalize_build_draft(
            draft,
            build_registry,
            artifacts=(*active_copy_artifacts, *draft.artifacts),
            trailing_diagnostics=shadow_diagnostics,
        )

    def catalog_preview(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
    ) -> dict[str, object]:
        """Return the current HeavenBase-ready catalog preview payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.

        Returns:
            JSON-safe HeavenBase catalog preview payload. This method does not
            write `.paradev/.cache/hb` files.
        """

        from paradev.hb import catalog_preview

        return catalog_preview(self, profile=profile, registry=registry)

    def catalog_status(
        self,
        *,
        database: str | Path | None = None,
    ) -> dict[str, object]:
        """Return the read-only status of the local HeavenBase Catalog.

        Args:
            database: Optional SQLite catalog path. Defaults to
                `.paradev/.cache/hb/catalog.sqlite` under the project root.

        Returns:
            JSON-safe Catalog status with a stable status and code. This
            method does not create project state or build the project.
        """

        from paradev.hb import catalog_status

        return catalog_status(self, database=database)

    def catalog_query(
        self,
        *,
        database: str | Path | None = None,
        entity: str | None = None,
        target_id: str | None = None,
        name: str | None = None,
        tag: str | None = None,
        limit: int | None = None,
        offset: int = 0,
        include_data: bool = True,
    ) -> dict[str, object]:
        """Read rows from a written local HeavenBase catalog database.

        Args:
            database: Optional SQLite catalog path. Defaults to
                `.paradev/.cache/hb/catalog.sqlite` under the project root.
            entity: Optional Catalog target entity filter.
            target_id: Optional exact target object identifier filter.
            name: Optional case-insensitive substring filter over Catalog names.
            tag: Optional exact tag filter.
            limit: Optional maximum row count.
            offset: Number of matching rows to skip before returning the page.
            include_data: Whether to hydrate target payloads for returned rows.

        Returns:
            JSON-safe HeavenBase catalog query payload.
        """

        from paradev.hb import catalog_query

        return catalog_query(
            self,
            database=database,
            entity=entity,
            target_id=target_id,
            name=name,
            tag=tag,
            limit=limit,
            offset=offset,
            include_data=include_data,
        )

    def modules(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        family: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        source_slot: str | None = None,
    ) -> dict[str, object]:
        """Return the current build modules manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            family: Optional module family filter.
            module_id: Optional exact module id filter.
            collection_id: Optional collection id filter.
            source_slot: Optional source slot filter.

        Returns:
            JSON-safe modules manifest payload.
        """

        from paradev.build import modules_view

        result = self.build(profile=profile, registry=registry)
        return modules_view(
            result,
            family=family,
            module_id=module_id,
            collection_id=collection_id,
            source_slot=source_slot,
        )

    def collections(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        family: str | None = None,
        collection_id: str | None = None,
        module_id: str | None = None,
        source_slot: str | None = None,
    ) -> dict[str, object]:
        """Return the current build collections manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            family: Optional collection family filter.
            collection_id: Optional exact collection id filter.
            module_id: Optional member module id filter.
            source_slot: Optional descriptor source slot filter.

        Returns:
            JSON-safe collections manifest payload.
        """

        from paradev.build import collections_view

        result = self.build(profile=profile, registry=registry)
        return collections_view(
            result,
            family=family,
            collection_id=collection_id,
            module_id=module_id,
            source_slot=source_slot,
        )

    def artifacts(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        artifact_type: str | None = None,
        target_root: str | None = None,
        owner: str | None = None,
        path: str | None = None,
        mode: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
    ) -> dict[str, object]:
        """Return the current build artifacts manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            artifact_type: Optional artifact type filter, such as `pdx`.
            target_root: Optional target root filter, such as `output`.
            owner: Optional exact artifact owner filter.
            path: Optional exact artifact path filter.
            mode: Optional artifact mode filter, such as `plan`.
            module_id: Optional source or owner module filter.
            collection_id: Optional source or owner collection filter.

        Returns:
            JSON-safe artifacts manifest payload.
        """

        from paradev.build import artifacts_view

        result = self.build(profile=profile, registry=registry)
        return artifacts_view(
            result,
            artifact_type=artifact_type,
            target_root=target_root,
            owner=owner,
            path=path,
            mode=mode,
            module_id=module_id,
            collection_id=collection_id,
        )

    def localization(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        language: str | None = None,
        key: str | None = None,
        key_prefix: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
    ) -> dict[str, object]:
        """Return the current build localization manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            language: Optional language id or alias filter, such as `l_english` or `en`.
            key: Optional exact localization key filter.
            key_prefix: Optional localization key prefix filter.
            module_id: Optional module id filter.
            collection_id: Optional collection id filter.

        Returns:
            JSON-safe localization manifest payload.
        """

        from paradev.build import localization_view

        result = self.build(profile=profile, registry=registry)
        return localization_view(
            result,
            language=language,
            key=key,
            key_prefix=key_prefix,
            module_id=module_id,
            collection_id=collection_id,
        )

    def assets(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        family: str | None = None,
        slot: str | None = None,
        file_format: str | None = None,
    ) -> dict[str, object]:
        """Return the current build asset manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            module_id: Optional module id filter.
            collection_id: Optional collection id filter.
            family: Optional module family filter.
            slot: Optional source slot filter.
            file_format: Optional lowercase asset format filter, such as `png`.

        Returns:
            JSON-safe asset manifest payload.
        """

        from paradev.build import assets_view

        result = self.build(profile=profile, registry=registry)
        return assets_view(
            result,
            module_id=module_id,
            collection_id=collection_id,
            family=family,
            slot=slot,
            file_format=file_format,
        )

    def sources(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        family: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        slot: str | None = None,
        loader: str | None = None,
        status: str | None = None,
        owner_kind: str | None = None,
    ) -> dict[str, object]:
        """Return the current build source inventory payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            family: Optional module or collection family filter.
            module_id: Optional module id filter.
            collection_id: Optional collection id filter.
            slot: Optional source slot filter.
            loader: Optional generic loader filter, such as `pdx`, `loc`, or `copy`.
            status: Optional source load status filter, such as `loaded`, `matched`, or `diagnostic`.
            owner_kind: Optional source owner kind filter, either `module` or
                `collection`.

        Returns:
            JSON-safe source inventory manifest payload.

        Raises:
            ValueError: If owner_kind is not `module` or `collection`.
        """

        from paradev.build import sources_view

        result = self.build(profile=profile, registry=registry)
        return sources_view(
            result,
            family=family,
            module_id=module_id,
            collection_id=collection_id,
            slot=slot,
            loader=loader,
            status=status,
            owner_kind=owner_kind,
        )

    def source_slots(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        family: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        slot: str | None = None,
        status: str | None = None,
    ) -> dict[str, object]:
        """Return expected source-slot contract status for discovered sources.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            family: Optional module or collection family filter.
            module_id: Optional module id filter.
            collection_id: Optional collection id filter.
            slot: Optional source slot filter.
            status: Optional slot status filter: `satisfied`, `missing`,
                `empty`, or `diagnostic`.

        Returns:
            JSON-safe source-slot status payload. This method does not write
            build manifests.
        """

        from paradev.build import source_slot_status

        profile_id = profile or self.game
        build_registry = self._build_registry(profile=profile_id, registry=registry)
        result = self.build(profile=profile_id, registry=build_registry)
        return source_slot_status(
            result,
            build_registry,
            family=family,
            module_id=module_id,
            collection_id=collection_id,
            slot=slot,
            status=status,
        )

    def sprites(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        family: str | None = None,
        slot: str | None = None,
        name: str | None = None,
    ) -> dict[str, object]:
        """Return the current build sprite declaration manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            module_id: Optional source module id filter.
            collection_id: Optional source collection id filter.
            family: Optional source family filter.
            slot: Optional source slot filter.
            name: Optional exact sprite name filter.

        Returns:
            JSON-safe sprite manifest payload.
        """

        from paradev.build import sprites_view

        result = self.build(profile=profile, registry=registry)
        return sprites_view(
            result,
            module_id=module_id,
            collection_id=collection_id,
            family=family,
            slot=slot,
            name=name,
        )

    def diagnostics(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        severity: str | None = None,
        code: str | None = None,
        family: str | None = None,
        owner: str | None = None,
        target_root: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        source_path: str | None = None,
        slot: str | None = None,
        strict_metadata: bool | str | None = None,
        published: bool | str = False,
    ) -> dict[str, object]:
        """Return the current build diagnostics manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            severity: Optional diagnostic severity filter.
            code: Optional exact diagnostic code filter.
            family: Optional module family filter.
            owner: Optional exact diagnostic owner filter.
            target_root: Optional diagnostic artifact target root filter.
            module_id: Optional module id filter.
            collection_id: Optional collection id filter.
            source_path: Optional source path filter.
            slot: Optional source slot filter.
            strict_metadata: Whether unknown metadata keys should be blocking
                errors in the build diagnostics source. Defaults to
                `paradev.build.strict_metadata` from `CM_PARADEV`.
            published: Read and validate the diagnostics manifest emitted by
                the most recent build instead of compiling the project again.

        Returns:
            JSON-safe diagnostics manifest payload.
        """

        from paradev.build.views import diagnostics_manifest_view

        if _bool_value(published):
            if registry is not None:
                raise ValueError("Published diagnostics do not accept a build registry override.")
            if strict_metadata is not None:
                raise ValueError("Published diagnostics already reflect the build's metadata mode; omit strict_metadata.")
            manifest = _load_published_diagnostics_manifest(self, profile=profile)
        else:
            from paradev.build import diagnostics_view

            result = self.build(profile=profile, registry=registry, strict_metadata=strict_metadata)
            return diagnostics_view(
                result,
                severity=severity,
                code=code,
                family=family,
                owner=owner,
                target_root=target_root,
                module_id=module_id,
                collection_id=collection_id,
                source_path=source_path,
                slot=slot,
            )
        return diagnostics_manifest_view(
            manifest,
            severity=severity,
            code=code,
            family=family,
            owner=owner,
            target_root=target_root,
            module_id=module_id,
            collection_id=collection_id,
            source_path=source_path,
            slot=slot,
        )

    def source_map(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        family: str | None = None,
        slot: str | None = None,
        artifact_type: str | None = None,
        target_root: str | None = None,
    ) -> dict[str, object]:
        """Return the current build source-map manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            module_id: Optional module id source filter.
            collection_id: Optional collection id source filter.
            family: Optional module family source filter.
            slot: Optional source slot filter.
            artifact_type: Optional artifact type filter, such as `pdx`.
            target_root: Optional artifact target root filter, such as `output`.

        Returns:
            JSON-safe source-map manifest payload.
        """

        from paradev.build import source_map_view

        result = self.build(profile=profile, registry=registry)
        return source_map_view(
            result,
            module_id=module_id,
            collection_id=collection_id,
            family=family,
            slot=slot,
            artifact_type=artifact_type,
            target_root=target_root,
        )

    def dependencies(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        source: str | None = None,
        target: str | None = None,
        kind: str | None = None,
        module_id: str | None = None,
    ) -> dict[str, object]:
        """Return the current build dependencies manifest payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            source: Optional exact dependency source filter.
            target: Optional exact dependency target filter.
            kind: Optional dependency kind filter, such as `requires`.
            module_id: Optional module id shorthand for `source="module:<id>"`.

        Returns:
            JSON-safe dependencies manifest payload.
        """

        from paradev.build import dependencies_view

        result = self.build(profile=profile, registry=registry)
        return dependencies_view(
            result,
            source=source,
            target=target,
            kind=kind,
            module_id=module_id,
        )

    def build_graph(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        family: str | None = None,
        slot: str | None = None,
        artifact_type: str | None = None,
        target_root: str | None = None,
        edge_kind: str | None = None,
    ) -> dict[str, object]:
        """Return the current build graph inspection payload.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            module_id: Optional module source filter.
            collection_id: Optional collection source filter.
            family: Optional module or collection family filter.
            slot: Optional source slot filter.
            artifact_type: Optional artifact type filter, such as `pdx`.
            target_root: Optional artifact target root filter, such as `output`.
            edge_kind: Optional edge kind filter, such as `emits` or `requires`.

        Returns:
            JSON-safe build graph payload.
        """

        from paradev.build import build_graph

        result = self.build(profile=profile, registry=registry)
        return build_graph(
            result,
            module_id=module_id,
            collection_id=collection_id,
            family=family,
            slot=slot,
            artifact_type=artifact_type,
            target_root=target_root,
            edge_kind=edge_kind,
        )

    def build_explain(
        self,
        *,
        module_id: str | None = None,
        collection_id: str | None = None,
        source_path: str | os.PathLike[str] | None = None,
        artifact_path: str | None = None,
        diagnostic_code: str | None = None,
        target_root: str | None = None,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
    ) -> dict[str, object]:
        """Return one module, collection, source file, artifact, or diagnostic's current build explanation payload.

        Args:
            module_id: Optional module id, with or without the `module:` prefix.
                Mutually exclusive with other targets.
            collection_id: Optional collection id, with or without the
                `collection:` prefix. Mutually exclusive with other targets.
            source_path: Optional source file path. Relative paths are resolved
                from the project root. Mutually exclusive with other targets.
            artifact_path: Optional artifact path under its target root. Mutually
                exclusive with other targets.
            diagnostic_code: Optional diagnostic code to explain.
            target_root: Optional artifact target root filter, such as `output`.
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.

        Returns:
            JSON-safe module, source, or artifact build explanation payload.

        Raises:
            ValueError: If the requested target is invalid or not part of the
                build result.
        """

        from paradev.build import build_explain

        module_id = _explain_target_text("--module", module_id)
        collection_id = _explain_target_text("--collection", collection_id)
        source_request = _explain_source_request(source_path)
        source_path = _explain_source_path(self.root, source_request)
        artifact_path = _explain_target_text("--artifact", artifact_path)
        diagnostic_code = _explain_target_text("--diagnostic-code", diagnostic_code)
        result = self.build(profile=profile, registry=registry)
        try:
            return build_explain(
                result,
                module_id=module_id,
                collection_id=collection_id,
                source_path=source_path,
                artifact_path=artifact_path,
                diagnostic_code=diagnostic_code,
                target_root=target_root,
            )
        except ValueError as error:
            if source_path and source_request and str(error) == f"Unknown build source: {source_path}":
                raise ValueError(f"Unknown build source: {source_request}") from error
            raise

    def families(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        family: str | None = None,
        kind: str | None = None,
        source_slot: str | None = None,
        collection_source_slot: str | None = None,
        sprite_slot: str | None = None,
        route: str | None = None,
        artifact_type: str | None = None,
    ) -> dict[str, object]:
        """Return build-family contracts for a profile.

        Args:
            profile: Optional build profile. Defaults to this project's `game`.
            registry: Optional build registry. Defaults to the selected profile registry.
            family: Optional exact family id filter.
            kind: Optional exact compiler kind filter.
            source_slot: Optional module source-slot filter.
            collection_source_slot: Optional collection descriptor source-slot filter.
            sprite_slot: Optional sprite source-slot filter.
            route: Optional routed-source route id filter.
            artifact_type: Optional output and writer artifact type filter.

        Returns:
            JSON-safe authoring, family, and artifact-writer capability payload.
        """

        from paradev.build import families_view

        profile_id = profile or self.game
        build_registry = self._build_registry(profile=profile_id, registry=registry)
        return families_view(
            build_registry,
            project_id=self.project_id,
            profile=profile_id,
            project_root=self.root,
            source_roots=self.source_roots,
            family=family,
            kind=kind,
            source_slot=source_slot,
            collection_source_slot=collection_source_slot,
            sprite_slot=sprite_slot,
            route=route,
            artifact_type=artifact_type,
        )

    def discover_modules(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        strict_metadata: bool | str | None = None,
        family: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
    ) -> "ModuleDiscoveryResult":
        """Discover source modules from this project's source roots.

        Args:
            profile: Optional build profile for source-slot declarations.
            registry: Optional build registry. Defaults to generic discovery slots
                unless a profile is supplied.
            strict_metadata: Whether unknown module metadata keys should be
                blocking errors instead of loose-mode warnings. Defaults to
                `paradev.build.strict_metadata` from `CM_PARADEV`.
            family: Optional exact module family filter.
            module_id: Optional exact module id filter.
            collection_id: Optional exact collection id filter.

        Returns:
            Discovered modules and diagnostics.
        """

        return self._discover_modules(
            profile=profile,
            registry=registry,
            strict_metadata=strict_metadata,
            family=family,
            module_id=module_id,
            collection_id=collection_id,
            source_cache_read=True,
        )

    def _discover_modules(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        strict_metadata: bool | str | None = None,
        family: str | None = None,
        module_id: str | None = None,
        collection_id: str | None = None,
        source_cache_read: bool,
        parallelism: int = 1,
    ) -> "ModuleDiscoveryResult":
        """Discover modules with an explicit internal cache-read policy."""

        from paradev.build import DEFAULT_MODULE_SLOTS, discover_modules

        if module_id is not None:
            _module_id_parts(module_id)
        clean_family = _optional_path_filter("family", family)
        clean_collection_id = _optional_path_filter("collection_id", collection_id)
        build_strict_metadata = _build_strict_metadata(strict_metadata)
        source_cache_root = _project_source_cache_root(self)
        if registry is None and profile is None and not self.extension_modules and not self.python_modules and not self.family_specs:
            return discover_modules(
                self.source_roots,
                strict_metadata=build_strict_metadata,
                family=clean_family,
                module_id=module_id,
                collection_id=clean_collection_id,
                _cache_root=source_cache_root,
                _cache_read=source_cache_read,
                _parallelism=parallelism,
            )
        build_registry = self._build_registry(profile=profile, registry=registry)
        return discover_modules(
            self.source_roots,
            slots=tuple(build_registry.source_slots) or DEFAULT_MODULE_SLOTS,
            slots_by_family=build_registry.source_slots_by_family(),
            metadata_keys_by_family=build_registry.metadata_keys_by_family(),
            strict_metadata=build_strict_metadata,
            family=clean_family,
            module_id=module_id,
            collection_id=clean_collection_id,
            _cache_root=source_cache_root,
            _cache_read=source_cache_read,
            _parallelism=parallelism,
        )

    def discover_collections(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        strict_metadata: bool | str | None = None,
        family: str | None = None,
        collection_id: str | None = None,
        module_id: str | None = None,
    ) -> "CollectionDiscoveryResult":
        """Discover collection descriptors from this project's source roots.

        Args:
            profile: Optional build profile for collection source-slot declarations.
            registry: Optional build registry. Defaults to generic discovery slots
                unless a profile is supplied.
            strict_metadata: Whether unknown collection metadata keys should be
                blocking errors instead of loose-mode warnings. Defaults to
                `paradev.build.strict_metadata` from `CM_PARADEV`.
            family: Optional exact collection family filter.
            collection_id: Optional exact collection id filter.
            module_id: Optional exact member module id filter.

        Returns:
            Discovered collection descriptors and diagnostics.
        """

        return self._discover_collections(
            profile=profile,
            registry=registry,
            strict_metadata=strict_metadata,
            family=family,
            collection_id=collection_id,
            module_id=module_id,
            source_cache_read=True,
        )

    def _discover_collections(
        self,
        *,
        profile: str | None = None,
        registry: "BuildRegistry | None" = None,
        strict_metadata: bool | str | None = None,
        family: str | None = None,
        collection_id: str | None = None,
        module_id: str | None = None,
        source_cache_read: bool,
        parallelism: int = 1,
    ) -> "CollectionDiscoveryResult":
        """Discover collections with an explicit internal cache-read policy."""

        from paradev.build import DEFAULT_COLLECTION_SLOTS, discover_collections

        if module_id is not None:
            _module_id_parts(module_id)
        clean_family = _optional_path_filter("family", family)
        clean_collection_id = _optional_path_filter("collection_id", collection_id)
        build_strict_metadata = _build_strict_metadata(strict_metadata)
        source_cache_root = _project_source_cache_root(self)
        if registry is None and profile is None and not self.extension_modules and not self.python_modules and not self.family_specs:
            return discover_collections(
                self.source_roots,
                strict_metadata=build_strict_metadata,
                family=clean_family,
                collection_id=clean_collection_id,
                module_id=module_id,
                _cache_root=source_cache_root,
                _cache_read=source_cache_read,
                _parallelism=parallelism,
            )
        build_registry = self._build_registry(profile=profile, registry=registry)
        return discover_collections(
            self.source_roots,
            slots=tuple(build_registry.collection_source_slots) or DEFAULT_COLLECTION_SLOTS,
            slots_by_family=build_registry.collection_source_slots_by_family(),
            metadata_keys_by_family=build_registry.metadata_keys_by_family(),
            strict_metadata=build_strict_metadata,
            family=clean_family,
            collection_id=clean_collection_id,
            module_id=module_id,
            _cache_root=source_cache_root,
            _cache_read=source_cache_read,
            _parallelism=parallelism,
        )

    def _build_registry(self, *, profile: str | None = None, registry: "BuildRegistry | None" = None) -> "BuildRegistry":
        from paradev.build import (
            ProjectFamilySpecError,
            apply_project_extension_modules,
            apply_project_families,
            apply_project_python_modules,
        )
        from paradev.games import registry_for_profile

        if registry is not None:
            return registry
        build_registry = registry_for_profile(profile or self.game)
        try:
            build_registry = apply_project_python_modules(build_registry, self.python_modules, self.root, self.manifest_path)
            build_registry = apply_project_families(build_registry, self.family_specs, self.manifest_path)
            return apply_project_extension_modules(
                build_registry,
                self.extension_modules,
                self.project_id,
                self.manifest_path,
            )
        except ProjectFamilySpecError as error:
            raise ProjectManifestError(str(error)) from error

    def _authoring_template_specs(self) -> tuple[ModuleTemplate, ...]:
        """Return manifest and registry-backed project authoring templates."""

        from paradev.build import ProjectFamilySpecError, project_extension_templates

        try:
            extension_templates = project_extension_templates(
                self.extension_modules,
                self.project_id,
                self.manifest_path,
            )
        except ProjectFamilySpecError as error:
            raise ProjectManifestError(str(error)) from error
        return (
            *self.template_specs,
            *cast(tuple[ModuleTemplate, ...], extension_templates),
        )


ParaDevProject = Project


def create_project(
    path: str | os.PathLike[str],
    *,
    project_id: str | None = None,
    title: str | None = None,
    game: str = "hoi4",
    force: bool = False,
) -> Project:
    """Create a buildable starter ParaDev project.

    Args:
        path: Target project root.
        project_id: Optional stable project id. Defaults to the folder name.
        title: Optional display title. Defaults to a title-cased folder name.
        game: Target game package. Only `hoi4` is supported by the starter.
        force: Allow writing into an existing non-empty directory.

    Returns:
        Loaded starter project.

    Raises:
        ProjectCreateError: If the target path or game is unsupported.
    """

    if game != "hoi4":
        raise ProjectCreateError("Starter project creation currently supports only game='hoi4'.")
    root = Path(path).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ProjectCreateError(f"Project path must be a directory: {root}")
    if root.exists() and any(root.iterdir()) and not force:
        raise ProjectCreateError(f"Project path is not empty: {root}. Use --force to write starter files anyway.")
    root.mkdir(parents=True, exist_ok=True)

    clean_project_id = _project_identifier(project_id or root.name)
    clean_title = title.strip() if isinstance(title, str) and title.strip() else _project_title(root.name)
    source_root = root / "src"
    output_root = _default_output_root(root, clean_project_id, game)
    build_root = root / ".paradev/.cache/build"
    starter_object_id = _starter_object_id(clean_project_id)
    module_root = source_root / "modules/modifier" / starter_object_id
    for directory in (source_root, output_root, build_root, module_root):
        directory.mkdir(parents=True, exist_ok=True)

    save_yaml(
        {
            "project_id": clean_project_id,
            "title": clean_title,
            "game": game,
            "source_roots": ["src"],
            "build_root": ".paradev/.cache/build",
        },
        str(root / PROJECT_MANIFEST),
        encoding="utf-8",
        sort_keys=False,
    )
    save_yaml(
        {"title": "Starter Modifier"},
        str(module_root / "meta.yaml"),
        encoding="utf-8",
        sort_keys=False,
    )
    save_txt(
        f"{starter_object_id} = {{\n\tstability_factor = 0.05\n}}\n",
        str(module_root / "def.txt"),
        encoding="utf-8",
    )
    save_txt(
        "\n".join(
            [
                f"[en.{starter_object_id}]",
                "Starter Modifier",
                "",
                f"[en.{starter_object_id}_desc]",
                "A small generated modifier for the first ParaDev build.",
                "",
            ]
        ),
        str(module_root / "main.loc"),
        encoding="utf-8",
    )
    return Project.load(root)


def open_project(
    path: str | os.PathLike[str] = ".",
    *,
    game: str | None = None,
    title: str | None = None,
) -> Project:
    """Open a local project view.

    Args:
        path: Project root path or nested project path.
        game: Optional game package override.
        title: Optional display title.

    Returns:
        Loaded project view model.
    """

    return Project.load(path, game=game, title=title)


def registered_projects(
    *,
    project_paths: Sequence[str | os.PathLike[str]] = (),
    search_roots: Sequence[str | os.PathLike[str]] = (),
) -> dict[str, object]:
    """Return loadable ParaDev projects known to the SDK.

    Args:
        project_paths: Explicit project roots, manifests, or nested paths.
        search_roots: Directories searched recursively for `paradev.yaml`.
            Defaults to local `projects/` and `demos/assets/projects/`
            folders when no explicit paths are supplied.

    Returns:
        JSON-safe project registry payload with deterministic rows,
        diagnostics, and row indexes.
    """

    projects: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for manifest_path in _registered_project_manifest_paths(project_paths=project_paths, search_roots=search_roots, diagnostics=diagnostics):
        try:
            projects.append(_project_registry_row(Project.load(manifest_path.parent)))
        except ProjectManifestError as error:
            diagnostics.append(_project_registry_diagnostic("project.load_failed", manifest_path, str(error)))
    return {
        "schema": PROJECTS_SCHEMA,
        "projects": projects,
        "diagnostics": diagnostics,
        "index": _project_registry_index(projects),
    }


def desktop_state(
    project_path: str | os.PathLike[str] | None = None,
    *,
    project_paths: Sequence[str | os.PathLike[str]] = (),
    search_roots: Sequence[str | os.PathLike[str]] = (),
    include_browser: bool = True,
) -> dict[str, object]:
    """Return SDK-owned project state for desktop and GUI shells.

    Args:
        project_path: Optional active project root, manifest, or nested path.
            When omitted, the first registered project is active if one exists.
        project_paths: Explicit project roots included in the registry.
        search_roots: Directories searched recursively for project manifests.
        include_browser: Whether to include the active project's browser
            payload. GUI shells can skip it during startup and request scoped
            browser payloads later.

    Returns:
        JSON-safe desktop state payload containing the project registry, active
        project row, active project view, and frontend browser/template
        payloads for the active project when one is available.
    """

    registry = registered_projects(project_paths=project_paths, search_roots=search_roots)
    projects = [row for row in registry["projects"] if isinstance(row, dict)]
    active_project = Project.load(project_path) if project_path is not None else _default_active_project(projects)
    active_project_row = _project_registry_row(active_project) if active_project is not None else None
    if active_project_row is not None and not any(row.get("root") == active_project_row["root"] for row in projects):
        projects = [active_project_row, *projects]
        registry = {
            **registry,
            "projects": projects,
            "index": _project_registry_index(projects),
        }
    return {
        "schema": DESKTOP_STATE_SCHEMA,
        "registry": registry,
        "projects": projects,
        "active_project": active_project_row,
        "active_view": active_project.to_view() if active_project is not None else None,
        "browser": active_project.browser() if active_project is not None and include_browser else None,
        "templates": active_project.templates() if active_project is not None else None,
        "diagnostics": registry["diagnostics"],
    }


def project_create_payload(project: Project) -> dict[str, object]:
    """Return the canonical starter-project create payload.

    Args:
        project: Loaded project returned by `Project.create(...)` or
            `create_project(...)`.

    Returns:
        JSON-safe payload shared by CLI, REST, and frontend-facing contracts.
    """

    project_id = project.project_id
    return {
        "schema": PROJECT_CREATE_SCHEMA,
        "project": project.to_view(),
        "starter_module": f"modifier/{project_id}_starter_modifier",
    }


def _project_browser_kind(kind: str | None) -> str | None:
    if kind is None:
        return None
    text = kind.strip()
    if not text:
        return None
    if text not in {"module", "collection"}:
        raise ValueError("Project browser kind must be module or collection.")
    return text


def _project_browser_collection_roots(
    collections: Sequence["Collection"],
) -> dict[tuple[str, str], Path]:
    roots: dict[tuple[str, str], Path] = {}
    for collection in collections:
        payload = getattr(collection, "payload", None)
        root = getattr(payload, "root", None)
        if isinstance(root, (str, Path)) and str(root):
            roots[(collection.family, collection.collection_id)] = Path(root).expanduser().resolve()
    return roots


def _project_browser_module_localized_titles(
    modules: Sequence["Module"],
    *,
    registry: "BuildRegistry",
) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for module in modules:
        object_id = _module_object_id(module.module_id)
        titles = _project_browser_payload_localized_titles(
            getattr(module, "payload", None),
            object_id,
            title_keys=_project_browser_module_title_keys(module, registry=registry),
        )
        rows[module.module_id] = titles
    return rows


def _project_browser_module_title_keys(
    module: "Module",
    *,
    registry: "BuildRegistry",
) -> tuple[str, ...]:
    object_id = _module_object_id(module.module_id)
    keys = _project_browser_family_title_keys(
        registry,
        family=module.family,
        object_id=object_id,
        module_id=module.module_id,
        collection_id=module.collection_id,
    )
    if keys is not None:
        return keys
    return _project_browser_payload_title_keys(
        getattr(module, "payload", None),
        object_id,
    )


def _project_browser_collection_localized_titles(
    collections: Sequence["Collection"],
    *,
    registry: "BuildRegistry",
) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    for collection in collections:
        titles = _project_browser_payload_localized_titles(
            getattr(collection, "payload", None),
            collection.collection_id,
            title_keys=_project_browser_family_title_keys(
                registry,
                family=collection.family,
                object_id=collection.collection_id,
                module_id="",
                collection_id=collection.collection_id,
            ),
        )
        rows[(collection.family, collection.collection_id)] = titles
    return rows


def _project_browser_payload_localized_titles(
    payload: object,
    object_id: str,
    *,
    title_keys: tuple[str, ...] | None,
) -> dict[str, str]:
    resolved_title_keys = _project_browser_payload_title_keys(payload, object_id) if title_keys is None else title_keys
    titles: dict[str, str] = {}
    for key in resolved_title_keys:
        for entry in getattr(payload, "loc_entries", ()):
            if getattr(entry, "key", None) != key:
                continue
            language = getattr(entry, "language", None)
            text = getattr(entry, "text", None)
            if not isinstance(language, str) or not isinstance(text, str) or not text.strip():
                continue
            titles.setdefault(language, text.strip())
    return titles


def _project_browser_family_title_keys(
    registry: "BuildRegistry",
    *,
    family: str,
    object_id: str,
    module_id: str,
    collection_id: str | None,
) -> tuple[str, ...] | None:
    raw = getattr(registry.family(family), "title_loc_keys", None)
    if raw is None:
        return None
    return tuple(
        template.format(
            family=family,
            module_id=module_id,
            collection_id=collection_id or "",
            object_id=object_id,
        )
        for template in raw
    )


def _project_browser_payload_title_keys(payload: object, object_id: str) -> tuple[str, ...]:
    keys = [object_id]
    for source in getattr(payload, "pdx_sources", ()):
        block = getattr(source, "block", None)
        if isinstance(block, PDXBlock):
            keys.extend(_project_browser_pdx_title_keys(block, object_id))
    return tuple(dict.fromkeys(key for key in keys if key))


def _project_browser_pdx_title_keys(block: PDXBlock, object_id: str) -> tuple[str, ...]:
    keys: list[str] = []
    for object_block in _project_browser_pdx_object_blocks(block, object_id):
        name_entry = object_block.find("name")
        name_key = _project_browser_pdx_text_value(name_entry.val if name_entry is not None else None)
        if name_key:
            keys.append(name_key)
    return tuple(keys)


def _project_browser_pdx_object_blocks(block: PDXBlock, object_id: str) -> tuple[PDXBlock, ...]:
    rows: list[PDXBlock] = []
    for entry in block.entries:
        value = entry.val
        if entry.key_str == object_id and isinstance(value, PDXBlock):
            rows.append(value)
        if isinstance(value, PDXBlock):
            rows.extend(_project_browser_pdx_object_blocks(value, object_id))
    return tuple(rows)


def _project_browser_pdx_text_value(value: object) -> str | None:
    if isinstance(value, PDXScalar) and value.val is not None:
        text = str(value.val).strip()
        return text or None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return None


def _project_browser_authoring_modules(
    project: Project,
    *,
    registry: "BuildRegistry",
    result: "BuildResult",
    family: str | None,
    module_id: str | None,
    collection_id: str | None,
) -> tuple["Module", ...]:
    """Return build modules plus inactive modules for the authoring browser.

    Build planning intentionally removes inactive modules before normalize,
    check, emit, diagnostics, dependency, and artifact work. The browser is an
    authoring surface, so it must retain those physical modules and mark their
    state instead of making reactivation require a manual YAML edit.
    """

    discovered = project.discover_modules(
        registry=registry,
        family=family,
        module_id=module_id,
        collection_id=collection_id,
    )
    active_keys = {_project_browser_module_identity(module) for module in result.modules}
    inactive = [
        module for module in discovered.modules if module.metadata.get("inactive") is True and _project_browser_module_identity(module) not in active_keys
    ]
    return tuple(
        sorted(
            (*result.modules, *inactive),
            key=lambda module: (
                module.module_id,
                str(Path(module.root).expanduser().resolve()),
            ),
        )
    )


def _project_browser_module_identity(module: "Module") -> tuple[str, str]:
    """Return one source-root-safe browser module identity."""

    return (
        module.module_id,
        str(Path(module.root).expanduser().resolve()),
    )


def _project_browser_module_item(
    project: Project,
    row: Mapping[str, object],
    *,
    registry: "BuildRegistry",
    declared_source_slots: Sequence["Slot"],
    localized_titles: Mapping[str, str],
    title_keys: Sequence[str],
) -> dict[str, object]:
    module_id = _required_row_string(row, "module_id")
    family = _required_row_string(row, "family")
    family_id = _browser_family_id(family, registry)
    object_id = _module_object_id(module_id)
    metadata = _mapping_data(row.get("metadata"))
    source_slots = _source_slot_paths(row.get("source_slots"))
    path_fields = _project_browser_path_fields(project, row.get("root"), kind="module")
    root = _optional_row_string(path_fields.get("root"))
    root_path = Path(root) if root is not None else None
    source_slots = _project_browser_authoring_source_slots(source_slots, root=root_path, kind="module")
    sources = _project_browser_slot_sources(
        project,
        source_slots,
        root=root_path,
        declared_source_slots=declared_source_slots,
    )
    image_targets = _project_browser_declared_image_targets(
        project,
        declared_source_slots,
        source_slots=source_slots,
        root=root_path,
    )
    folder_title = _project_browser_object_id_and_title(root_path.name)[1] if root_path is not None else object_id
    label = _project_browser_label(metadata, folder_title)
    item: dict[str, object] = {
        "id": f"module:{module_id}",
        "kind": "module",
        "layout": "canonical",
        "label": label,
        "title": label,
        "localized_titles": dict(localized_titles),
        "title_keys": list(title_keys),
        "family_id": family_id,
        "family": family,
        "object_id": object_id,
        "module_id": module_id,
        "active": metadata.get("inactive") is not True,
        "source_slots": source_slots,
        "source_count": len(sources),
        "sources": sources,
        "resource_slots": _project_browser_resource_slots(declared_source_slots),
        "metadata": metadata,
        "module": dict(row),
    }
    if image_targets:
        item["image_targets"] = image_targets
    collection_id = _optional_row_string(row.get("collection_id"))
    if collection_id is not None:
        item["collection_id"] = collection_id
    item.update(path_fields)
    return item


_PROJECT_BROWSER_IMAGE_TARGET_EXTENSIONS = frozenset({"bmp", "dds", "jpeg", "jpg", "png", "tga", "webp"})


def _project_browser_declared_image_targets(
    project: Project,
    declared_source_slots: Sequence["Slot"],
    *,
    source_slots: Mapping[str, Sequence[str | Path]],
    root: Path | None,
) -> list[dict[str, object]]:
    """Return exact absent image targets declared by one module family.

    Regex and glob slots are intentionally ignored. A target is exposed only
    when the family also declares one literal path, no source currently
    satisfies that logical slot, and no filesystem entry occupies the target.
    """

    if root is None:
        return []
    targets: dict[str, dict[str, object]] = {}
    for slot in declared_source_slots:
        slot_name = getattr(slot, "name", "")
        slot_kind = getattr(slot, "kind", None)
        if not isinstance(slot_name, str) or not slot_name or slot_kind not in {None, "copy"} or source_slots.get(slot_name):
            continue
        match = getattr(slot, "match", "")
        if not isinstance(match, str) or not match or bool(getattr(slot, "regex", False)) or any(character in match for character in "*?[]"):
            continue
        relative = PurePosixPath(match.replace("\\", "/"))
        if (
            relative.is_absolute()
            or any(part in {"", ".", ".."} for part in relative.parts)
            or relative.suffix.lower().lstrip(".") not in _PROJECT_BROWSER_IMAGE_TARGET_EXTENSIONS
        ):
            continue
        target = root.joinpath(*relative.parts)
        try:
            target.lstat()
        except FileNotFoundError:
            pass
        except OSError:
            continue
        else:
            continue
        relative_path = _project_relative_path(project.root, target)
        targets[relative_path] = {
            "slot": slot_name,
            "slot_kinds": _project_browser_slot_kinds(
                slot_name,
                declared_source_slots,
            ),
            "name": target.name,
            "path": str(target),
            "relative_path": relative_path,
            "extension": relative.suffix.lower().lstrip("."),
            "exists": False,
        }
    return [targets[path] for path in sorted(targets)]


def _project_browser_collection_item(
    project: Project,
    row: Mapping[str, object],
    collection_roots: Mapping[tuple[str, str], Path],
    *,
    declared_source_slots: Sequence["Slot"],
    registry: "BuildRegistry",
    localized_titles: Mapping[str, str],
) -> dict[str, object]:
    collection_id = _required_row_string(row, "collection_id")
    family = _required_row_string(row, "family")
    family_id = _browser_family_id(family, registry)
    metadata = _mapping_data(row.get("metadata"))
    source_slots = _source_slot_paths(row.get("source_slots"))
    module_ids = _string_sequence(row.get("module_ids"))
    root = collection_roots.get((family, collection_id))
    source_slots = _project_browser_authoring_source_slots(source_slots, root=root, kind="collection")
    sources = _project_browser_slot_sources(
        project,
        source_slots,
        root=root,
        declared_source_slots=declared_source_slots,
    )
    folder_title = _project_browser_object_id_and_title(root.name)[1] if root is not None else collection_id
    label = _project_browser_label(metadata, folder_title)
    item: dict[str, object] = {
        "id": f"collection:{family}/{collection_id}",
        "kind": "collection",
        "layout": "canonical",
        "label": label,
        "title": label,
        "localized_titles": dict(localized_titles),
        "family_id": family_id,
        "family": family,
        "object_id": collection_id,
        "collection_id": collection_id,
        "module_ids": module_ids,
        "module_count": len(module_ids),
        "source_count": len(sources),
        "sources": sources,
        "resource_slots": _project_browser_resource_slots(declared_source_slots),
        "metadata": metadata,
        "collection": dict(row),
    }
    if source_slots:
        item["source_slots"] = source_slots
    if root is not None:
        item.update(_project_browser_path_fields(project, root, kind="collection"))
    return item


def _project_browser_path_fields(project: Project, root: object, *, kind: str) -> dict[str, object]:
    if not isinstance(root, (str, Path)) or not str(root):
        return {}
    path = Path(root).expanduser().resolve()
    fields: dict[str, object] = {
        "root": str(path),
        "relative_path": _project_relative_path(project.root, path),
        "relative_root": _project_relative_path(project.root, path),
    }
    try:
        source_root = (
            _module_source_root(project.root, project.source_roots, path)
            if kind == "module"
            else _collection_source_root(project.root, project.source_roots, path)
        )
    except ValueError:
        return fields
    fields["source_root"] = str(source_root)
    fields["source_root_relative_path"] = _project_relative_path(project.root, source_root)
    return fields


def _project_browser_module_keys(
    items: Sequence[Mapping[str, object]],
) -> frozenset[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for item in items:
        family = _optional_row_string(item.get("family"))
        object_id = _optional_row_string(item.get("object_id"))
        if family is not None and object_id is not None:
            keys.add((_browser_family_name(family), object_id))
    return frozenset(keys)


def _project_browser_summary_families(
    project: Project,
    *,
    registry: "BuildRegistry",
    kind: str | None,
    family: str | None,
    diagram_by_family: Mapping[str, Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    families: dict[str, dict[str, object]] = {}
    family_names: dict[str, str] = {}
    groups: dict[str, dict[str, object]] = {}
    layouts: dict[str, set[str]] = {}
    module_keys: set[tuple[str, str]] = set()

    if kind in {None, "module"}:
        for source_root in project.source_roots:
            modules_root = source_root / "modules"
            if not modules_root.is_dir():
                continue
            for family_root in _project_browser_child_dirs(modules_root):
                family_name = _browser_family_name(family_root.name)
                canonical_family = _canonical_browser_family(family_name, registry)
                if family is not None and canonical_family != family:
                    continue
                family_id = _browser_family_id(family_root.name, registry)
                for item_root in _project_browser_child_dirs(family_root):
                    object_id, _title = _project_browser_object_id_and_title(item_root.name)
                    module_keys.add((canonical_family, object_id))
                    _add_project_browser_summary_row(
                        families,
                        family_names,
                        groups,
                        layouts,
                        family_id=family_id,
                        family=family_name,
                        kind="module",
                        layout="canonical",
                        source_count=_project_browser_summary_source_count(item_root),
                        presentation=_browser_family_presentation(family_name, registry),
                        visible=registry.visible_for(family_name),
                        diagram=diagram_by_family.get(family_name),
                    )

    if kind in {None, "collection"}:
        for source_root in project.source_roots:
            collections_root = source_root / "collections"
            if not collections_root.is_dir():
                continue
            for family_root in _project_browser_child_dirs(collections_root):
                family_name = _browser_family_name(family_root.name)
                canonical_family = _canonical_browser_family(family_name, registry)
                if family is not None and canonical_family != family:
                    continue
                family_id = _browser_family_id(family_root.name, registry)
                for item_root in _project_browser_child_dirs(family_root):
                    _add_project_browser_summary_row(
                        families,
                        family_names,
                        groups,
                        layouts,
                        family_id=family_id,
                        family=family_name,
                        kind="collection",
                        layout="canonical",
                        source_count=_project_browser_summary_source_count(item_root),
                        presentation=_browser_family_presentation(family_name, registry),
                        visible=registry.visible_for(family_name),
                        diagram=diagram_by_family.get(family_name),
                    )

    if kind is None:
        for source_root in project.source_roots:
            if not source_root.is_dir():
                continue
            for family_root in _project_browser_child_dirs(source_root):
                if family_root.name in PROJECT_BROWSER_EXCLUDED_ROOTS:
                    continue
                family_name = _browser_family_name(family_root.name)
                canonical_family = _canonical_browser_family(family_name, registry)
                if family is not None and canonical_family != family:
                    continue
                family_id = _browser_family_id(family_root.name, registry)
                for item_root in _project_browser_child_dirs(family_root):
                    object_id, _title = _project_browser_object_id_and_title(item_root.name)
                    if (canonical_family, object_id) in module_keys:
                        continue
                    source_count = _project_browser_summary_direct_source_count(item_root)
                    if source_count == 0:
                        continue
                    _add_project_browser_summary_row(
                        families,
                        family_names,
                        groups,
                        layouts,
                        family_id=family_id,
                        family=family_name,
                        kind="source_folder",
                        layout="family_root",
                        source_count=source_count,
                        presentation=_browser_family_presentation(family_name, registry),
                        visible=registry.visible_for(family_name),
                        diagram=diagram_by_family.get(family_name),
                    )

    for family_id, row in families.items():
        row["layouts"] = sorted(layouts.get(family_id, ()))
    _ensure_project_browser_registered_families(
        families,
        registry=registry,
        diagram_by_family=diagram_by_family,
    )
    family_rows = sorted(families.values(), key=lambda row: str(row["title"]).casefold())
    group_rows = [groups[family_id] for family_id in sorted(groups, key=lambda key: family_names.get(key, key))]
    return family_rows, group_rows


def _add_project_browser_summary_row(
    families: dict[str, dict[str, object]],
    family_names: dict[str, str],
    groups: dict[str, dict[str, object]],
    layouts: dict[str, set[str]],
    *,
    family_id: str,
    family: str,
    kind: str,
    layout: str,
    source_count: int,
    presentation: Mapping[str, object],
    visible: bool,
    diagram: Mapping[str, object] | None,
) -> None:
    family_names.setdefault(family_id, family)
    family_row = families.setdefault(
        family_id,
        {
            "id": family_id,
            "family": family,
            **presentation,
            "visible": visible,
            "item_count": 0,
            "source_count": 0,
            "layouts": [],
        },
    )
    if diagram is not None:
        family_row["diagram"] = dict(diagram)
    family_row["item_count"] = int(family_row["item_count"]) + 1
    family_row["source_count"] = int(family_row["source_count"]) + source_count
    layouts.setdefault(family_id, set()).add(layout)

    group = groups.setdefault(
        family_id,
        {
            "id": family_id,
            "family": family,
            "item_count": 0,
            "module_count": 0,
            "collection_count": 0,
        },
    )
    group["item_count"] = int(group["item_count"]) + 1
    if kind == "module":
        group["module_count"] = int(group["module_count"]) + 1
    elif kind == "collection":
        group["collection_count"] = int(group["collection_count"]) + 1


def _project_browser_summary_source_count(root: Path) -> int:
    count = 0
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            children = tuple(current.iterdir())
        except OSError:
            continue
        for child in children:
            if child.name.startswith(".") or child.name in {"__pycache__", "build"}:
                continue
            if child.is_dir():
                stack.append(child)
            elif child.is_file():
                count += 1
    return count


def _project_browser_summary_direct_source_count(root: Path) -> int:
    try:
        children = tuple(root.iterdir())
    except OSError:
        return 0
    return sum(1 for child in children if not child.name.startswith(".") and child.is_file())


def _project_browser_family_root_items(
    project: Project,
    *,
    registry: "BuildRegistry",
    family: str | None = None,
    shadowed_modules: frozenset[tuple[str, str]] = frozenset(),
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source_root in project.source_roots:
        if not source_root.is_dir():
            continue
        for family_root in _project_browser_child_dirs(source_root):
            if family_root.name in PROJECT_BROWSER_EXCLUDED_ROOTS:
                continue
            family_id = _browser_family_id(family_root.name, registry)
            family_name = _browser_family_name(family_root.name)
            canonical_family = _canonical_browser_family(family_name, registry)
            if family is not None and canonical_family != family:
                continue
            for item_root in _project_browser_child_dirs(family_root):
                object_id, title = _project_browser_object_id_and_title(item_root.name)
                if (canonical_family, object_id) in shadowed_modules:
                    continue
                sources = _project_browser_direct_sources(project, item_root)
                if not sources:
                    continue
                rows.append(
                    {
                        "id": f"{family_id}/{object_id}",
                        "kind": "source_folder",
                        "layout": "family_root",
                        "family_id": family_id,
                        "family": family_name,
                        "object_id": object_id,
                        "label": title,
                        "title": title,
                        "root": str(item_root),
                        "relative_path": _project_relative_path(project.root, item_root),
                        "relative_root": _project_relative_path(project.root, item_root),
                        "source_count": len(sources),
                        "sources": sources,
                    }
                )
    return rows


def _project_browser_child_dirs(root: Path) -> tuple[Path, ...]:
    try:
        return tuple(
            sorted(
                (path for path in root.iterdir() if path.is_dir() and not path.name.startswith(".")),
                key=lambda path: path.name.casefold(),
            )
        )
    except OSError:
        return ()


def _project_browser_slot_sources(
    project: Project,
    slots: Mapping[str, Sequence[str | Path]],
    *,
    root: Path | None = None,
    declared_source_slots: Sequence["Slot"] = (),
) -> list[dict[str, object]]:
    sources: list[dict[str, object]] = []
    for slot in sorted(slots):
        for path in sorted((Path(item) for item in slots[slot]), key=lambda item: str(item)):
            row = _project_browser_source_row(
                project,
                _project_browser_source_path(root, path),
                slot=slot,
            )
            row["slot_kinds"] = _project_browser_slot_kinds(
                slot,
                declared_source_slots,
            )
            sources.append(row)
    return sources


def _project_browser_resource_slots(
    declared_source_slots: Sequence["Slot"],
) -> list[dict[str, object]]:
    """Return JSON-safe Registry slot declarations for one browser item."""

    rows: list[dict[str, object]] = []
    for slot in declared_source_slots:
        row: dict[str, object] = {
            "name": str(slot.name),
            "match": str(slot.match),
            "required": bool(slot.required),
            "many": bool(slot.many),
            "regex": bool(slot.regex),
            "shared": bool(slot.shared),
        }
        if slot.kind:
            row["kind"] = slot.kind
        if slot.authoring_path:
            row["authoring_path"] = slot.authoring_path
        rows.append(row)
    return rows


def _project_browser_slot_kinds(
    slot_name: str,
    declared_source_slots: Sequence["Slot"],
) -> list[str]:
    """Return deterministic Registry kinds declared for one logical slot."""

    return sorted({slot.kind for slot in declared_source_slots if slot.name == slot_name and isinstance(slot.kind, str) and slot.kind})


def _project_browser_authoring_source_slots(
    slots: Mapping[str, Sequence[str | Path]],
    *,
    root: Path | None,
    kind: Literal["module", "collection"],
) -> dict[str, list[str | Path]]:
    authoring_slots = {slot: list(paths) for slot, paths in slots.items()}
    if root is None or authoring_slots.get("meta"):
        return authoring_slots
    metadata_names = ("meta.yaml",) if kind == "module" else ("meta.yaml", "collection.yaml")
    for name in metadata_names:
        metadata_path = root / name
        try:
            metadata_stat = metadata_path.lstat()
        except OSError:
            continue
        if stat.S_ISREG(metadata_stat.st_mode):
            authoring_slots["meta"] = [name]
            break
    return authoring_slots


def _project_browser_direct_sources(project: Project, root: Path) -> list[dict[str, object]]:
    try:
        files = sorted(
            (path for path in root.iterdir() if path.is_file() and not path.name.startswith(".")),
            key=lambda path: path.name.casefold(),
        )
    except OSError:
        return []
    return [_project_browser_source_row(project, path, slot=_project_browser_source_slot(path)) for path in files]


def _project_browser_source_row(project: Project, path: Path, *, slot: str) -> dict[str, object]:
    source_path = path.expanduser().resolve()
    row: dict[str, object] = {
        "slot": slot,
        "name": source_path.name,
        "path": str(source_path),
        "relative_path": _project_relative_path(project.root, source_path),
        "extension": source_path.suffix.lower().lstrip("."),
    }
    try:
        stat = source_path.stat()
    except OSError:
        return row
    row["size"] = stat.st_size
    row["mtime_ns"] = str(stat.st_mtime_ns)
    return row


def _project_browser_source_path(root: Path | None, path: Path) -> Path:
    if root is None or path.is_absolute():
        return path
    return root / path


def _project_browser_source_slot(path: Path) -> str:
    if path.name in {"def.pdx", "def.txt"}:
        return "def"
    if path.suffix.lower() == ".loc":
        return "loc"
    if path.suffix.lower() in {".dds", ".jpg", ".jpeg", ".png", ".tga", ".webp"}:
        return "asset"
    return path.stem or "source"


def _project_browser_object_id_and_title(name: str) -> tuple[str, str]:
    if " - " not in name:
        return name, name
    object_id, title = name.split(" - ", 1)
    return object_id.strip() or name, title.strip() or object_id.strip() or name


def _project_browser_label(metadata: Mapping[str, object], fallback: str) -> str:
    for key in ("title", "label", "name", "object_id"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _project_browser_filters(
    *,
    kind: str | None,
    family: str | None,
    module_id: str | None,
    collection_id: str | None,
) -> dict[str, str]:
    return {
        key: value
        for key, value in {
            "kind": kind,
            "family": family,
            "module_id": module_id,
            "collection_id": collection_id,
        }.items()
        if value is not None
    }


def _project_browser_module_filter(family: str | None, module_id: str | None) -> str | None:
    if module_id is None:
        return None
    text = module_id.strip()
    if not text:
        raise ValueError("Module id must be non-empty.")
    if "/" in text:
        module_family, object_id = _module_id_parts(text)
        return f"{module_family}/{object_id}"
    if family is None:
        return text
    return f"{family}/{_module_path_token(text, 'object_id')}"


def _project_browser_groups(
    items: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    groups: dict[str, dict[str, object]] = {}
    for item in items:
        family = _optional_row_string(item.get("family"))
        kind = _optional_row_string(item.get("kind"))
        if family is None or kind is None:
            continue
        group = groups.setdefault(
            family,
            {
                "id": _optional_row_string(item.get("family_id")) or _browser_family_id(family),
                "family": family,
                "item_count": 0,
                "module_count": 0,
                "collection_count": 0,
            },
        )
        group["item_count"] = int(group["item_count"]) + 1
        if kind == "module":
            group["module_count"] = int(group["module_count"]) + 1
        elif kind == "collection":
            group["collection_count"] = int(group["collection_count"]) + 1
    return [groups[family] for family in sorted(groups)]


def _project_browser_families(
    items: Sequence[Mapping[str, object]],
    *,
    registry: "BuildRegistry",
    diagram_by_family: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    families: dict[str, dict[str, object]] = {}
    layouts: dict[str, set[str]] = {}
    for item in items:
        family_id = _optional_row_string(item.get("family_id"))
        family = _optional_row_string(item.get("family"))
        if family_id is None or family is None:
            continue
        row = families.setdefault(
            family_id,
            {
                "family": family,
                **_browser_family_presentation(family, registry),
                "visible": registry.visible_for(family),
                "item_count": 0,
                "source_count": 0,
                "layouts": [],
                "resource_slots": _project_browser_resource_slots(registry.source_slots_for(family)),
            },
        )
        diagram = diagram_by_family.get(family)
        if diagram is not None:
            row["diagram"] = dict(diagram)
        row["item_count"] = int(row["item_count"]) + 1
        row["source_count"] = int(row["source_count"]) + int(item.get("source_count") or 0)
        layout = _optional_row_string(item.get("layout"))
        if layout is not None:
            layouts.setdefault(family_id, set()).add(layout)
    for family_id, row in families.items():
        row["layouts"] = sorted(layouts.get(family_id, ()))
    _ensure_project_browser_registered_families(
        families,
        registry=registry,
        diagram_by_family=diagram_by_family,
    )
    return sorted(families.values(), key=lambda row: str(row["title"]).casefold())


def _ensure_project_browser_registered_families(
    families: dict[str, dict[str, object]],
    *,
    registry: "BuildRegistry",
    diagram_by_family: Mapping[str, Mapping[str, object]],
) -> None:
    """Expose registered authoring capabilities even before their first module."""

    for registered in registry.families:
        family = str(getattr(registered, "family"))
        presentation = _browser_family_presentation(family, registry)
        family_id = str(presentation["id"])
        row = families.setdefault(
            family_id,
            {
                "family": family,
                **presentation,
                "visible": registry.visible_for(family),
                "item_count": 0,
                "source_count": 0,
                "layouts": [],
                "resource_slots": _project_browser_resource_slots(registry.source_slots_for(family)),
            },
        )
        diagram = diagram_by_family.get(family)
        if diagram is not None:
            row["diagram"] = dict(diagram)


def _browser_family_presentation(
    family: str,
    registry: "BuildRegistry",
) -> dict[str, object]:
    """Return one Registry-owned browser presentation with an external fallback."""

    try:
        return registry.presentation_for(family).to_view()
    except ValueError:
        family_id = _browser_family_id(family)
        return {
            "id": family_id,
            "title": family_id.replace("-", " ").title(),
            "group": "other",
        }


def _project_browser_index(
    items: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {
        "id": {},
        "kind": {},
        "family": {},
        "family_id": {},
        "module_id": {},
        "collection_id": {},
        "object_id": {},
    }
    for row_index, item in enumerate(items):
        for index_key in index:
            value = item.get(index_key)
            if isinstance(value, str):
                append_index_entry(index[index_key], value, row_index)
    return {field: bucket for field, bucket in index.items() if bucket}


def _project_browser_item_key(item: Mapping[str, object]) -> tuple[int, str, str, str]:
    kind_order = {"collection": 0, "module": 1, "source_folder": 2}
    kind = str(item.get("kind") or "")
    family = str(item.get("family") or "")
    collection_id = str(item.get("collection_id") or "")
    item_id = str(item.get("id") or "")
    return (kind_order.get(kind, 99), family, collection_id, item_id)


def _mapping_rows(value: object) -> list[Mapping[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def _mapping_data(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, Mapping) else {}


def _source_slot_paths(value: object) -> dict[str, list[str]]:
    if not isinstance(value, Mapping):
        return {}
    paths: dict[str, list[str]] = {}
    for slot, slot_paths in sorted(value.items(), key=lambda item: str(item[0])):
        if not isinstance(slot, str):
            continue
        paths[slot] = _string_sequence(slot_paths)
    return {slot: slot_paths for slot, slot_paths in paths.items() if slot_paths}


def _source_slot_count(source_slots: Mapping[str, Sequence[str]]) -> int:
    return sum(len(paths) for paths in source_slots.values())


def _string_sequence(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


def _required_row_string(row: Mapping[str, object], field: str) -> str:
    value = _optional_row_string(row.get(field))
    if value is None:
        raise ValueError(f"Project browser row is missing required field: {field}.")
    return value


def _optional_row_string(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _registered_project_manifest_paths(
    *,
    project_paths: Sequence[str | os.PathLike[str]],
    search_roots: Sequence[str | os.PathLike[str]],
    diagnostics: list[dict[str, object]],
) -> tuple[Path, ...]:
    manifests: list[Path] = []
    seen: set[Path] = set()
    explicit_paths = (*_env_project_paths(), *project_paths)
    for project_path in explicit_paths:
        try:
            manifest_path = _find_manifest(project_path).resolve()
        except ProjectManifestError as error:
            diagnostics.append(_project_registry_diagnostic("project.manifest_missing", Path(project_path), str(error)))
            continue
        if manifest_path not in seen:
            manifests.append(manifest_path)
            seen.add(manifest_path)

    roots = tuple(search_roots)
    if not roots and not explicit_paths:
        roots = _default_project_search_roots()
    for root in roots:
        root_path = Path(root).expanduser()
        if not root_path.exists():
            diagnostics.append(
                _project_registry_diagnostic(
                    "project.search_root_missing",
                    root_path,
                    f"Project search root does not exist: {root_path}",
                )
            )
            continue
        for manifest_path in _iter_project_manifests(root_path):
            resolved = manifest_path.resolve()
            if resolved not in seen:
                manifests.append(resolved)
                seen.add(resolved)
    return tuple(manifests)


def _env_project_paths() -> tuple[Path, ...]:
    value = os.environ.get("PARADEV_PROJECTS")
    if not value:
        return ()
    return tuple(Path(item).expanduser() for item in value.split(os.pathsep) if item)


def _default_project_search_roots() -> tuple[Path, ...]:
    return tuple(path for path in (Path("projects"), Path("demos/assets/projects")) if path.exists())


def _iter_project_manifests(root: Path) -> tuple[Path, ...]:
    root = root.expanduser()
    if root.is_file():
        return (root,) if root.name == PROJECT_MANIFEST else ()
    manifest = root / PROJECT_MANIFEST
    if manifest.is_file():
        return (manifest,)
    manifests: list[Path] = []
    try:
        children = sorted(root.iterdir(), key=lambda path: path.name)
    except OSError:
        return ()
    for child in children:
        if child.name in PROJECT_DISCOVERY_EXCLUDED_ROOTS or not child.is_dir():
            continue
        manifests.extend(_iter_project_manifests(child))
    return tuple(manifests)


def _project_registry_row(project: Project) -> dict[str, object]:
    version = _descriptor_version(project.descriptor_metadata)
    row: dict[str, object] = {
        "project_id": project.project_id,
        "title": project.title,
        "game": project.game,
        "root": str(project.root),
        "manifest": str(project.manifest_path),
        "source_roots": [str(path) for path in project.source_roots],
        "output_root": str(project.output_root),
        "build_root": str(project.build_root),
        "descriptor": dict(project.descriptor_metadata),
    }
    if version is not None:
        row["version"] = version
    return row


def _project_registry_index(
    projects: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {"project_id": {}, "root": {}, "game": {}}
    for row_index, row in enumerate(projects):
        for index_key in index:
            value = row.get(index_key)
            if isinstance(value, str):
                append_index_entry(index[index_key], value, row_index)
    return {field: bucket for field, bucket in index.items() if bucket}


def _project_registry_diagnostic(code: str, path: Path, message: str) -> dict[str, object]:
    return {
        "code": code,
        "severity": "error",
        "path": str(path.expanduser()),
        "message": message,
    }


def _default_active_project(projects: Sequence[Mapping[str, object]]) -> Project | None:
    for row in projects:
        root = row.get("root")
        if isinstance(root, str):
            return Project.load(root)
    return None


def _query_path(path: str | os.PathLike[str]) -> Path:
    return Path(path).expanduser().resolve()


def _project_find_payload(
    query_path: Path,
    *,
    project: Project | None = None,
    diagnostics: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": PROJECT_FIND_SCHEMA,
        "query_path": str(query_path),
        "found": project is not None,
    }
    if project is not None:
        payload["project"] = project.to_view()
    if diagnostics:
        payload["diagnostics"] = diagnostics
    return payload


def _project_authoring_plan(
    project: Project,
    *,
    kind: str,
    family: str,
    target_id: str,
    source_root: str | os.PathLike[str] | None = None,
    profile: str | None = None,
    registry: "BuildRegistry | None" = None,
    folder_name: str | None = None,
) -> dict[str, object]:
    """Return an authoring plan with an optional physical module folder."""

    from paradev.build import authoring_plan_view

    profile_id = profile or project.game
    return authoring_plan_view(
        project._build_registry(profile=profile_id, registry=registry),
        project_id=project.project_id,
        profile=profile_id,
        project_root=project.root,
        source_roots=project.source_roots,
        kind=kind,
        family=family,
        target_id=target_id,
        source_root=source_root,
        folder_name=folder_name,
    )


def _scaffold_project_module(
    project: Project,
    template_id: str,
    object_id: str,
    *,
    source_root: str | os.PathLike[str] | None,
    values: Mapping[str, object] | None,
    write: bool,
    force: bool,
    catalog_lock_held: bool,
) -> dict[str, object]:
    templates = _project_template_index(project)
    build_registry = project._build_registry(profile=project.game)
    template = _resolve_module_template(templates, template_id, build_registry)
    _require_template_authoring_ready(template, _registered_family_ids(build_registry))
    selected_source_root = _select_source_root(project.root, project.source_roots, source_root)
    plan = _module_scaffold_plan_with_system_files(
        project_id=project.project_id,
        project_root=project.root,
        source_root=selected_source_root,
        template=template,
        object_id=object_id,
        values=values,
        source_slots=build_registry.source_slots_for(template.family),
        write=write,
        force=force,
    )
    try:
        plan["authoring_plan"] = _project_authoring_plan(
            project,
            kind="module",
            family=template.family,
            target_id=str(plan["object_id"]),
            source_root=selected_source_root,
            registry=build_registry,
            folder_name=str(plan["folder_name"]),
        )
    except Exception:
        if plan.get("written") is not True and plan.get("blocked") is not True:
            raise
        plan["authoring_plan"] = _project_authoring_plan(
            project,
            kind="module",
            family=template.family,
            target_id=str(plan["object_id"]),
            source_root=selected_source_root,
            registry=build_registry,
            folder_name=str(plan["object_id"]),
        )
    if plan.get("written") is not True:
        return plan

    from paradev.hb import _sync_module_catalog_projection

    try:
        module = _find_project_module(project, str(plan["module_id"]), source_root=selected_source_root)
    except Exception as error:
        plan["catalog_mutation"] = _sync_module_catalog_projection(
            project,
            current={
                "module_id": plan["module_id"],
                "family": template.family,
                "root": plan["root"],
            },
            current_error=error,
            _lock_held=catalog_lock_held,
        )
    else:
        plan["catalog_mutation"] = _sync_module_catalog_projection(
            project,
            current=module.to_dict(),
            _lock_held=catalog_lock_held,
        )
    return plan


def _scaffold_project_collection(
    project: Project,
    template_id: str,
    collection_id: str,
    *,
    source_root: str | os.PathLike[str] | None,
    values: Mapping[str, object] | None,
    write: bool,
    force: bool,
    plan_hash: str | None,
) -> dict[str, object]:
    """Plan or apply one Registry-backed collection scaffold."""

    templates = _project_template_index(project)
    build_registry = project._build_registry(profile=project.game)
    template = _resolve_collection_template(templates, template_id, build_registry)
    _require_template_authoring_ready(
        template,
        _registered_family_ids(build_registry),
    )
    selected_source_root = _select_source_root(
        project.root,
        project.source_roots,
        source_root,
    )

    def plan_current(*, apply: bool) -> dict[str, object]:
        current = collection_scaffold_plan(
            project_id=project.project_id,
            project_root=project.root,
            source_root=selected_source_root,
            template=template,
            collection_id=collection_id,
            values=values,
            source_slots=build_registry.collection_source_slots_for(template.family),
            write=apply,
            force=force,
        )
        current["authoring_plan"] = _project_authoring_plan(
            project,
            kind="collection",
            family=template.family,
            target_id=str(current["collection_id"]),
            source_root=selected_source_root,
            registry=build_registry,
            folder_name=str(current["folder_name"]),
        )
        return current

    dry = plan_current(apply=False)
    current_hash = _collection_scaffold_plan_hash(
        project,
        dry,
        force=force,
    )
    dry["plan_hash"] = current_hash
    diagnostics = cast(list[dict[str, object]], dry["diagnostics"])
    if write and not isinstance(plan_hash, str):
        diagnostics.append(
            _collection_scaffold_diagnostic(
                "collection_scaffold.plan_hash_required",
                "Applying a collection scaffold requires the exact plan_hash " "returned by a dry plan.",
            )
        )
    elif write and plan_hash != current_hash:
        diagnostics.append(
            _collection_scaffold_diagnostic(
                "collection_scaffold.plan_hash_mismatch",
                "The collection scaffold changed after planning; review the " "current plan and apply its plan_hash.",
                expected_plan_hash=current_hash,
                provided_plan_hash=plan_hash,
            )
        )
    if any(item.get("severity") == "error" for item in diagnostics):
        dry["blocked"] = True
        if write:
            for file in cast(list[dict[str, object]], dry["files"]):
                file["action"] = "blocked"
        return dry
    if not write:
        return dry

    applied = plan_current(apply=True)
    applied["plan_hash"] = current_hash
    applied["applied"] = applied.get("written") is True
    return applied


def _collection_scaffold_plan_hash(
    project: Project,
    plan: Mapping[str, object],
    *,
    force: bool,
) -> str:
    """Hash one reviewed collection plan and its retained source authority."""

    source_root = Path(str(plan["source_root"]))
    canonical = {
        "schema": plan["schema"],
        "project_id": project.project_id,
        "project_root": str(project.root),
        "project_root_identity": _module_create_path_identity(project.root),
        "source_root": str(source_root),
        "source_root_identity": _module_create_path_identity(source_root),
        "template_id": plan["template_id"],
        "family": plan["family"],
        "collection_id": plan["collection_id"],
        "folder_name": plan["folder_name"],
        "root": plan["root"],
        "values": plan["values"],
        "force": force,
        "blocked": plan["blocked"],
        "diagnostics": plan["diagnostics"],
        "files": plan["files"],
    }
    payload = dumps_json(
        canonical,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        compact=True,
        adapt=False,
    )
    return sha256hash(payload)


def _collection_scaffold_diagnostic(
    code: str,
    message: str,
    **fields: object,
) -> dict[str, object]:
    return {
        "code": code,
        "severity": "error",
        "message": message,
        **fields,
    }


def _create_project_modules(
    project: Project,
    modules: Sequence[Mapping[str, object]],
    *,
    source_root: str | os.PathLike[str] | None,
    write: bool,
    plan_hash: str | None,
    catalog_lock_held: bool,
    profile: str | None = None,
    validate: Callable[[], None] | None = None,
    diagram_source_edits: Sequence[Mapping[str, object]] = (),
) -> dict[str, object]:
    from paradev.sdk.templates import (
        _AnchoredScaffoldUnavailable,
        _module_scaffold_draft,
        _normalized_scaffold_payload,
        _scaffold_module_matches_rendered_files,
        _ScaffoldRollbackIncomplete,
        _write_scaffold_batch_anchored,
    )

    requests = _module_create_batch_requests(modules)
    selected_source_root = _select_source_root(project.root, project.source_roots, source_root)
    templates = _project_template_index(project)
    build_registry = project._build_registry(profile=profile or project.game)
    registered_families = _registered_family_ids(build_registry)
    rows: list[dict[str, object]] = []
    rendered_by_index: list[list[dict[str, object]]] = []
    seen_module_paths: set[tuple[str, str]] = set()

    for index, request in enumerate(requests):
        template = _resolve_module_template(
            templates,
            request["family_or_template"],
            build_registry,
        )
        _require_template_authoring_ready(template, registered_families)
        row, rendered_files, _path_diagnostics = _module_scaffold_draft(
            project_id=project.project_id,
            project_root=project.root,
            source_root=selected_source_root,
            template=template,
            object_id=request["object_id"],
            values=request["values"],
            source_slots=build_registry.source_slots_for(template.family),
            force=False,
        )
        row.pop("project_root")
        row["index"] = index
        try:
            row["authoring_plan"] = _project_authoring_plan(
                project,
                kind="module",
                family=template.family,
                target_id=str(row["object_id"]),
                source_root=selected_source_root,
                registry=build_registry,
                folder_name=str(row["folder_name"]),
            )
        except ValueError:
            if row.get("blocked") is not True:
                raise
            row["authoring_plan"] = _project_authoring_plan(
                project,
                kind="module",
                family=template.family,
                target_id=str(row["object_id"]),
                source_root=selected_source_root,
                registry=build_registry,
                folder_name=str(row["object_id"]),
            )
        module_id = str(row["module_id"])
        module_root = Path(str(row["root"]))
        diagnostics = [diagnostic for diagnostic in cast(list[dict[str, object]], row["diagnostics"]) if diagnostic.get("code") != "scaffold.file_exists"]
        root_exists = _path_entry_exists_lexically(module_root)
        exact = root_exists and _scaffold_module_matches_rendered_files(module_root, rendered_files)
        module_path_key = (
            _normalize_build_mutation_lock_component(template.family),
            _normalize_build_mutation_lock_component(str(row["object_id"])),
        )
        if module_path_key in seen_module_paths:
            diagnostics = [diagnostic for diagnostic in diagnostics if diagnostic.get("severity") != "error"]
            diagnostics.append(
                _module_create_batch_diagnostic(
                    "module_batch.duplicate_module",
                    f"Module {module_id} is requested more than once in this batch.",
                    module_id=module_id,
                )
            )
        elif exact:
            row["status"] = "unchanged"
        elif root_exists:
            diagnostics.append(
                _module_create_batch_diagnostic(
                    "module_batch.module_conflict",
                    f"Module {module_id} already exists but does not exactly match this scaffold plan.",
                    module_id=module_id,
                    path=str(module_root),
                )
            )
            row["status"] = "blocked"
        else:
            row["status"] = "create"
        seen_module_paths.add(module_path_key)
        row["diagnostics"] = diagnostics
        row["blocked"] = any(diagnostic.get("severity") == "error" for diagnostic in diagnostics)
        if row["blocked"]:
            row["status"] = "blocked"
        for file in cast(list[dict[str, object]], row["files"]):
            file["action"] = "blocked" if row["blocked"] else "unchanged" if exact else "create"
        rows.append(row)
        rendered_by_index.append(rendered_files)

    current_plan_hash = _module_create_batch_plan_hash(
        project,
        selected_source_root,
        rows,
        rendered_by_index,
        payload_for=_normalized_scaffold_payload,
    )
    diagnostics: list[dict[str, object]] = []
    blocked = any(row.get("blocked") is True for row in rows)
    applied = False
    written = False
    diagram_recovery: DiagramModuleRecoveryJournal | None = None

    if write and not isinstance(plan_hash, str):
        diagnostics.append(
            _module_create_batch_diagnostic(
                "module_batch.plan_hash_required",
                "Applying a module batch requires the exact plan_hash returned by a dry plan.",
            )
        )
        blocked = True
    elif write and plan_hash != current_plan_hash:
        diagnostics.append(
            _module_create_batch_diagnostic(
                "module_batch.plan_hash_mismatch",
                "The module batch changed after planning; review the current plan and apply its plan_hash.",
                expected_plan_hash=current_plan_hash,
                provided_plan_hash=plan_hash,
            )
        )
        blocked = True

    if write and not blocked:
        scaffolds = [
            (
                str(row["family"]),
                str(row["object_id"]),
                str(row["folder_name"]),
                rendered_by_index[index],
            )
            for index, row in enumerate(rows)
            if row.get("status") == "create"
        ]
        if diagram_source_edits and scaffolds:
            try:
                diagram_recovery = _prepare_diagram_module_recovery(
                    project,
                    source_root=selected_source_root,
                    rows=rows,
                    rendered_by_index=rendered_by_index,
                    source_edits=diagram_source_edits,
                )
            except (OSError, ValueError) as error:
                diagnostics.append(
                    _module_create_batch_diagnostic(
                        "module_diagram.recovery_unavailable",
                        "The diagram child transaction could not start safely: " f"{error}",
                    )
                )
                blocked = True
        try:
            if not blocked:
                _write_scaffold_batch_anchored(
                    project_root=project.root,
                    source_root=selected_source_root,
                    scaffolds=scaffolds,
                    validate=validate,
                    transaction_id=(diagram_recovery.transaction_id if diagram_recovery is not None else None),
                )
        except _ModuleDiagramBuildRejected as error:
            diagnostics.append(
                _module_create_batch_diagnostic(
                    "module_diagram.build_rejected",
                    str(error),
                )
            )
            blocked = True
        except _ModuleDiagramSourceRejected as error:
            diagnostics.append(
                _module_create_batch_diagnostic(
                    error.code,
                    str(error),
                    **({"recovery_path": str(error.recovery_path)} if error.recovery_path is not None else {}),
                )
            )
            blocked = True
        except _AnchoredScaffoldUnavailable as error:
            diagnostics.append(
                _module_create_batch_diagnostic(
                    "module_batch.unsupported_platform",
                    f"Module batch creation was blocked to protect your files: {error}.",
                )
            )
            blocked = True
        except _ScaffoldRollbackIncomplete as error:
            diagnostics.append(
                _module_create_batch_diagnostic(
                    "module_batch.rollback_incomplete",
                    f"Module batch rollback was incomplete; recovery data remains at {error.recovery_path}: {error}.",
                    recovery_path=str(error.recovery_path),
                )
            )
            blocked = True
        except OSError as error:
            diagnostics.append(
                _module_create_batch_diagnostic(
                    "module_batch.concurrent_change",
                    f"Module source changed before the batch could be installed safely: {error}.",
                )
            )
            blocked = True
        else:
            if blocked:
                pass
            else:
                applied = True
                written = bool(scaffolds)
                for row in rows:
                    if row.get("status") != "create":
                        continue
                    row["status"] = "created"
                    row["written"] = True
                    row["authoring_plan"] = _project_authoring_plan(
                        project,
                        kind="module",
                        family=str(row["family"]),
                        target_id=str(row["object_id"]),
                        source_root=selected_source_root,
                        registry=build_registry,
                        folder_name=str(row["folder_name"]),
                    )
                    row["catalog_mutation"] = _created_module_catalog_projection(
                        project,
                        row,
                        source_root=selected_source_root,
                        catalog_lock_held=catalog_lock_held,
                    )
        if diagram_recovery is not None:
            try:
                _recover_diagram_module_transaction(project)
            except ValueError as error:
                diagnostics.append(
                    _module_create_batch_diagnostic(
                        "module_diagram.recovery_incomplete",
                        str(error),
                        recovery_path=diagram_module_recovery_root(str(project.root)),
                    )
                )
                blocked = True
        if blocked:
            for row in rows:
                if row.get("status") == "create":
                    row["status"] = "blocked"
                    row["blocked"] = True
                    for file in cast(list[dict[str, object]], row["files"]):
                        file["action"] = "blocked"

    counts = {status: sum(row.get("status") == status for row in rows) for status in ("create", "created", "unchanged", "blocked")}
    return {
        "schema": MODULE_CREATE_BATCH_SCHEMA,
        "project_id": project.project_id,
        "source_root": str(selected_source_root),
        "plan_hash": current_plan_hash,
        "blocked": blocked,
        "applied": applied,
        "written": written,
        "requested_count": len(rows),
        "counts": counts,
        "diagnostics": diagnostics,
        "modules": rows,
    }


def _module_create_batch_requests(
    modules: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    if isinstance(modules, (str, bytes)) or not isinstance(modules, Sequence):
        raise ValueError("Module batch must be a list of request mappings.")
    if not modules:
        raise ValueError("Module batch must contain at least one request.")
    if len(modules) > MAX_MODULE_CREATE_BATCH_SIZE:
        raise ValueError(f"Module batch cannot contain more than {MAX_MODULE_CREATE_BATCH_SIZE} requests.")

    allowed_fields = frozenset({"family", "template_id", "family_or_template", "object_id", "values"})
    requests: list[dict[str, object]] = []
    for index, request in enumerate(modules):
        if not isinstance(request, Mapping):
            raise ValueError(f"Module batch request {index} must be a mapping.")
        unknown_fields = sorted(str(field) for field in request if field not in allowed_fields)
        if unknown_fields:
            raise ValueError(f"Module batch request {index} has unknown fields: {', '.join(unknown_fields)}.")
        selectors = [
            request[field].strip()
            for field in ("family", "template_id", "family_or_template")
            if isinstance(request.get(field), str) and str(request[field]).strip()
        ]
        if len(selectors) != 1:
            raise ValueError(f"Module batch request {index} requires exactly one of family, template_id, or family_or_template.")
        object_id = request.get("object_id")
        if not isinstance(object_id, str) or not object_id.strip():
            raise ValueError(f"Module batch request {index} requires a non-empty object_id.")
        values = request.get("values")
        if values is not None and not isinstance(values, Mapping):
            raise ValueError(f"Module batch request {index} field values must be a mapping.")
        requests.append(
            {
                "family_or_template": selectors[0],
                "object_id": object_id.strip(),
                "values": dict(values) if isinstance(values, Mapping) else None,
            }
        )
    return requests


def _module_create_batch_plan_hash(
    project: Project,
    source_root: Path,
    rows: Sequence[Mapping[str, object]],
    rendered_by_index: Sequence[Sequence[Mapping[str, object]]],
    *,
    payload_for: Callable[[str], bytes],
) -> str:
    module_rows: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        files: list[dict[str, object]] = []
        file_views = cast(Sequence[Mapping[str, object]], row["files"])
        for file_index, rendered in enumerate(rendered_by_index[index]):
            relative_path = rendered.get("relative_module_path")
            content = rendered.get("content")
            if not isinstance(relative_path, str) or not isinstance(content, str):
                raise TypeError("Rendered module batch files require string paths and content.")
            payload = payload_for(content)
            file_view = file_views[file_index]
            files.append(
                {
                    "module_path": relative_path,
                    "relative_path": str(file_view["relative_path"]),
                    "action": str(file_view["action"]),
                    "sha256": sha256hash(payload.decode("utf-8")),
                    "size_bytes": len(payload),
                }
            )
        module_rows.append(
            {
                "index": index,
                "template_id": row["template_id"],
                "family": row["family"],
                "object_id": row["object_id"],
                "module_id": row["module_id"],
                "folder_name": row["folder_name"],
                "root": row["root"],
                "values": row["values"],
                "status": row["status"],
                "blocked": row["blocked"],
                "diagnostics": row["diagnostics"],
                "files": files,
            }
        )
    canonical = {
        "schema": MODULE_CREATE_BATCH_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "project_root_identity": _module_create_path_identity(project.root),
        "source_root": str(source_root),
        "source_root_identity": _module_create_path_identity(source_root),
        "source_root_relative_path": _project_relative_path(project.root, source_root),
        "modules": module_rows,
    }
    payload = dumps_json(
        canonical,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        compact=True,
        adapt=False,
    )
    return sha256hash(payload)


def _module_create_path_identity(path: Path) -> list[int] | None:
    """Return one stable path identity, or ``None`` while it is absent.

    A new project may not have created its configured source root yet.  Recording
    that absence in the reviewed-plan hash keeps first-use scaffolding safe: if
    another process creates the root before apply, the recomputed hash changes
    and the stale plan is rejected.
    """

    try:
        metadata = path.stat()
    except FileNotFoundError:
        return None
    return [metadata.st_dev, metadata.st_ino]


def _module_create_batch_diagnostic(
    code: str,
    message: str,
    **fields: object,
) -> dict[str, object]:
    return {
        "code": code,
        "severity": "error",
        "message": message,
        **fields,
    }


def _path_entry_exists_lexically(path: Path) -> bool:
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    return True


def _created_module_catalog_projection(
    project: Project,
    row: Mapping[str, object],
    *,
    source_root: Path,
    catalog_lock_held: bool,
) -> dict[str, object]:
    from paradev.hb import _sync_module_catalog_projection

    try:
        module = _find_project_module(project, str(row["module_id"]), source_root=source_root)
    except Exception as error:
        return _sync_module_catalog_projection(
            project,
            current={
                "module_id": row["module_id"],
                "family": row["family"],
                "root": row["root"],
            },
            current_error=error,
            _lock_held=catalog_lock_held,
        )
    return _sync_module_catalog_projection(
        project,
        current=module.to_dict(),
        _lock_held=catalog_lock_held,
    )


def _clean_project_module_metadata(
    project: Project,
    *,
    family: str | None,
    module_id: str | None,
    source_root: str | os.PathLike[str] | None,
    write: bool,
    plan_hash: str | None,
) -> dict[str, object]:
    """Plan and optionally apply one inferred-metadata cleanup transaction."""

    clean_family = _optional_path_filter("family", family)
    clean_module_id: str | None = None
    if module_id is not None:
        module_family, object_id = _module_id_parts(module_id)
        clean_module_id = f"{module_family}/{object_id}"
        if clean_family is not None and clean_family != module_family:
            raise ValueError(f"Module {clean_module_id!r} belongs to family {module_family!r}, " f"not {clean_family!r}.")
        clean_family = module_family
    selected_source_root = _select_source_root(project.root, project.source_roots, source_root) if source_root is not None else None
    candidates = _module_metadata_cleanup_candidates(
        project,
        family=clean_family,
        module_id=clean_module_id,
        source_root=selected_source_root,
    )
    build_registry = project._build_registry(profile=project.game)
    if clean_module_id is not None:
        exact_candidates = [
            candidate
            for candidate in candidates
            if candidate.module_id == clean_module_id
            and (
                _path_entry_exists_lexically(candidate.module_root / "meta.yaml")
                or _module_metadata_cleanup_has_authored_source(
                    candidate,
                    candidate.module_root,
                    source_slots=build_registry.source_slots_for(candidate.family),
                )
            )
        ]
        if not exact_candidates:
            raise ValueError(f"Unknown module: {clean_module_id}.")
        if len(exact_candidates) > 1:
            roots = {candidate.source_root for candidate in exact_candidates}
            if len(roots) > 1:
                raise ValueError(f"Module {clean_module_id} exists in multiple source roots. " "Pass source_root to choose one.")
            raise ValueError(f"Module {clean_module_id} has multiple source folders in " f"{next(iter(roots))}.")
        candidates = tuple(exact_candidates)

    entries = tuple(
        _module_metadata_cleanup_entry(
            project,
            candidate,
            source_slots=build_registry.source_slots_for(candidate.family),
        )
        for candidate in candidates
    )
    mutation_roots = tuple(
        sorted(
            {entry.mutation_root for entry in entries},
            key=str,
        )
    )
    root_identities = _module_metadata_cleanup_root_identities(
        project,
        mutation_roots,
    )
    diagnostics: list[dict[str, object]] = [dict(diagnostic) for entry in entries for diagnostic in entry.diagnostics]
    changed_roots = sorted(
        {entry.mutation_root for entry in entries if entry.changed},
        key=str,
    )
    if len(changed_roots) > 1:
        diagnostics.append(
            _module_metadata_cleanup_diagnostic(
                "module_metadata_cleanup.multi_root_transaction",
                ("One cleanup apply cannot atomically span independent source roots. " "Pass source_root and apply each returned plan separately."),
                mutation_roots=[str(path) for path in changed_roots],
            )
        )
    current_plan_hash = _module_metadata_cleanup_plan_hash(
        project,
        family=clean_family,
        module_id=clean_module_id,
        source_root=selected_source_root,
        entries=entries,
        diagnostics=diagnostics,
        root_identities=root_identities,
    )
    blocked = any(diagnostic.get("severity") == "error" for diagnostic in diagnostics)
    applied = False
    written = False
    catalog_mutation: dict[str, object] | None = None
    partial_state: str | None = None
    recovery: dict[str, object] | None = None

    if write and (not isinstance(plan_hash, str) or not plan_hash):
        diagnostics.append(
            _module_metadata_cleanup_diagnostic(
                "module_metadata_cleanup.plan_hash_required",
                ("Applying module metadata cleanup requires the exact " "plan_hash returned by a dry plan."),
            )
        )
        blocked = True
    elif write and plan_hash != current_plan_hash:
        diagnostics.append(
            _module_metadata_cleanup_diagnostic(
                "module_metadata_cleanup.plan_hash_mismatch",
                ("Module metadata changed after planning; review the current " "plan and apply its plan_hash."),
                expected_plan_hash=current_plan_hash,
                provided_plan_hash=plan_hash,
            )
        )
        blocked = True

    changed_entries = tuple(entry for entry in entries if entry.changed)
    if write and not blocked and not changed_entries:
        applied = True
    elif write and not blocked:
        mutation_root = changed_entries[0].mutation_root
        root_identity = root_identities[str(mutation_root)]["identity"]
        if not (isinstance(root_identity, tuple) and len(root_identity) == 2 and all(type(value) is int for value in root_identity)):
            raise AssertionError("Metadata cleanup root identity did not normalize.")
        from paradev.hb import (
            _module_catalog_mutation_scope,
            _sync_module_catalog_projection,
        )

        try:
            with _module_catalog_mutation_scope(project) as catalog_lock_held:
                try:
                    _apply_module_metadata_cleanup(
                        mutation_root,
                        changed_entries,
                        root_identity=root_identity,
                    )
                except _SourceDraftRollbackIncomplete as error:
                    partial_state = "unknown"
                    recovery = {
                        "schema": "paradev.source-draft-recovery.v1",
                        "status": "required",
                        "path": str(error.recovery_path),
                        "possibly_modified_paths": [str(path) for path in error.possibly_modified_paths],
                    }
                    if isinstance(
                        error.mutation_error,
                        _SourceDraftDisplacedRecoveryIncomplete,
                    ):
                        recovery["displaced_target"] = {
                            "path": str(error.mutation_error.target_path),
                            "recovery_path": str(error.mutation_error.recovery_path),
                            "destination_exists": (error.mutation_error.destination_exists),
                        }
                    diagnostics.append(
                        _module_metadata_cleanup_diagnostic(
                            "module_metadata_cleanup.rollback_incomplete",
                            (
                                "Module metadata cleanup failed and rollback "
                                "was incomplete. Do not continue editing these "
                                "modules until the recovery data is reviewed."
                            ),
                            recovery_path=str(error.recovery_path),
                            possibly_modified_paths=[str(path) for path in error.possibly_modified_paths],
                            error=str(error),
                        )
                    )
                    blocked = True
                    catalog_mutation = _sync_module_catalog_projection(
                        project,
                        current_error=error,
                        current={
                            "module_ids": sorted({entry.module_id for entry in changed_entries}),
                            "families": sorted({entry.family for entry in changed_entries}),
                        },
                        _lock_held=catalog_lock_held,
                    )
                except _SourceDraftDisplacedRecoveryIncomplete as error:
                    partial_state = "unknown"
                    recovery = {
                        "schema": "paradev.source-draft-displaced-recovery.v1",
                        "status": "required",
                        "path": str(error.recovery_path),
                        "target_path": str(error.target_path),
                        "destination_exists": error.destination_exists,
                        "possibly_modified_paths": [str(error.target_path)],
                    }
                    diagnostics.append(
                        _module_metadata_cleanup_diagnostic(
                            ("module_metadata_cleanup.displaced_recovery_incomplete"),
                            (
                                "Module metadata cleanup could not restore a "
                                "displaced target. Do not continue editing this "
                                "module until the recovery path is reviewed."
                            ),
                            recovery_path=str(error.recovery_path),
                            target_path=str(error.target_path),
                            destination_exists=error.destination_exists,
                            error=str(error),
                        )
                    )
                    blocked = True
                    catalog_mutation = _sync_module_catalog_projection(
                        project,
                        current_error=error,
                        current={
                            "module_ids": sorted({entry.module_id for entry in changed_entries}),
                            "families": sorted({entry.family for entry in changed_entries}),
                        },
                        _lock_held=catalog_lock_held,
                    )
                except Exception as error:
                    diagnostics.append(
                        _module_metadata_cleanup_diagnostic(
                            "module_metadata_cleanup.concurrent_change",
                            ("Module metadata cleanup did not complete; " "ParaDev rolled back its completed edits: " f"{error}"),
                        )
                    )
                    blocked = True
                    catalog_mutation = _sync_module_catalog_projection(
                        project,
                        current_error=error,
                        current={
                            "module_ids": sorted({entry.module_id for entry in changed_entries}),
                            "families": sorted({entry.family for entry in changed_entries}),
                        },
                        _lock_held=catalog_lock_held,
                    )
                else:
                    applied = True
                    written = True
                    catalog_mutation = _sync_module_catalog_projection(
                        project,
                        current={
                            "module_ids": sorted({entry.module_id for entry in changed_entries}),
                            "families": sorted({entry.family for entry in changed_entries}),
                        },
                        _lock_held=catalog_lock_held,
                    )
        except BlockingIOError as error:
            diagnostics.append(
                _module_metadata_cleanup_diagnostic(
                    "module_metadata_cleanup.catalog_busy",
                    ("The HeavenBase Catalog is being refreshed, so ParaDev " f"did not change module metadata: {error}"),
                )
            )
            blocked = True

    payload = _module_metadata_cleanup_payload(
        project,
        family=clean_family,
        module_id=clean_module_id,
        source_root=selected_source_root,
        entries=entries,
        diagnostics=diagnostics,
        plan_hash=current_plan_hash,
        blocked=blocked,
        applied=applied,
        written=written,
        partial_state=partial_state,
        recovery=recovery,
    )
    if catalog_mutation is not None:
        payload["catalog_mutation"] = catalog_mutation
    return payload


def _set_project_module_collection(
    project: Project,
    module_id: str,
    collection_id: str | None,
    *,
    source_root: str | os.PathLike[str] | None,
    write: bool,
    plan_hash: str | None,
) -> dict[str, object]:
    """Plan and optionally apply one canonical collection-membership edit."""

    module = _find_project_module(project, module_id, source_root=source_root)
    module_root = Path(module.root).expanduser().resolve()
    selected_source_root = _module_source_root(
        project.root,
        project.source_roots,
        module_root,
    )
    clean_collection_id: str | None
    collection: Collection | None = None
    if collection_id is None:
        clean_collection_id = None
    else:
        clean_collection_id = _collection_id_token(collection_id)
        collection = _find_project_collection(
            project,
            clean_collection_id,
            family=module.family,
            source_root=selected_source_root,
        )
        collection_root = _collection_root(collection)
        collection_source_root = _collection_source_root(
            project.root,
            project.source_roots,
            collection_root,
        )
        if collection.family != module.family:
            raise ValueError(f"Collection {clean_collection_id!r} belongs to family " f"{collection.family!r}, not {module.family!r}.")
        if collection_source_root != selected_source_root:
            raise ValueError(f"Collection {clean_collection_id!r} and module " f"{module.module_id!r} must use the same source root.")

    visible_path = module_root / "meta.yaml"
    hidden_path = module_root / ".paradev" / "meta.yaml"
    visible, visible_snapshot = _module_metadata_source(
        project,
        visible_path,
        label="visible module metadata",
    )
    hidden, hidden_snapshot = _module_metadata_source(
        project,
        hidden_path,
        label="hidden module metadata",
    )
    previous_collection_id = module.collection_id
    edits: list[dict[str, object]] = []
    removals: list[dict[str, object]] = []
    replacements: list[dict[str, object]] = []
    files: list[dict[str, object]] = []

    visible_after = dict(visible)
    visible_had_collection = "collection" in visible_after
    visible_after.pop("collection", None)
    if visible_had_collection and visible_snapshot is not None:
        _append_module_metadata_existing_mutation(
            project,
            path=visible_path,
            before=visible,
            after=visible_after,
            snapshot=visible_snapshot,
            edits=edits,
            removals=removals,
            files=files,
            layer="visible",
        )

    hidden_after = dict(hidden)
    if clean_collection_id is None:
        hidden_after.pop("collection", None)
    else:
        hidden_after["collection"] = clean_collection_id
    if hidden_snapshot is not None:
        _append_module_metadata_existing_mutation(
            project,
            path=hidden_path,
            before=hidden,
            after=hidden_after,
            snapshot=hidden_snapshot,
            edits=edits,
            removals=removals,
            files=files,
            layer="hidden",
        )
    elif hidden_after:
        hidden_text = _dump_module_metadata(hidden_after)
        replacements.append(
            {
                "path": str(hidden_path),
                "content_base64": base64.b64encode(hidden_text.encode("utf-8")).decode("ascii"),
                "expected_absent": True,
            }
        )
        files.append(
            _module_metadata_file_view(
                project,
                hidden_path,
                layer="hidden",
                action="create",
                before=None,
                after=hidden_text,
            )
        )

    changed = bool(edits or removals or replacements)
    current_hash = _module_collection_update_plan_hash(
        project,
        module=module,
        source_root=selected_source_root,
        previous_collection_id=previous_collection_id,
        collection_id=clean_collection_id,
        visible_path=visible_path,
        visible_snapshot=visible_snapshot,
        hidden_path=hidden_path,
        hidden_snapshot=hidden_snapshot,
        edits=edits,
        removals=removals,
        replacements=replacements,
    )
    diagnostics: list[dict[str, object]] = []
    if write and (not isinstance(plan_hash, str) or not plan_hash):
        diagnostics.append(
            {
                "code": "module_collection_update.plan_hash_required",
                "severity": "error",
                "message": ("Applying a module collection change requires the exact " "plan_hash returned by a dry plan."),
            }
        )
    elif write and plan_hash != current_hash:
        diagnostics.append(
            {
                "code": "module_collection_update.plan_hash_mismatch",
                "severity": "error",
                "message": ("Module metadata or collection ownership changed after " "planning; review the current plan and apply its plan_hash."),
                "expected_plan_hash": current_hash,
                "provided_plan_hash": plan_hash,
            }
        )
    blocked = bool(diagnostics)
    payload: dict[str, object] = {
        "schema": MODULE_COLLECTION_UPDATE_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "module_id": module.module_id,
        "family": module.family,
        "source_root": str(selected_source_root),
        "previous_collection_id": previous_collection_id,
        "collection_id": clean_collection_id,
        "changed": changed,
        "blocked": blocked,
        "applied": False,
        "written": False,
        "status": "blocked" if blocked else "planned",
        "plan_hash": current_hash,
        "diagnostics": diagnostics,
        "files": files,
    }
    if collection is not None:
        payload["collection"] = collection.to_dict()
    if blocked or not write:
        return payload
    if not changed:
        payload["applied"] = True
        payload["status"] = "unchanged"
        payload["module"] = module.to_dict()
        return payload

    created_hidden_parent = False
    if replacements and not hidden_path.parent.exists():
        hidden_path.parent.mkdir()
        created_hidden_parent = True
    try:
        applied = project.apply_source_draft(
            source_edits=edits or None,
            source_removals=removals or None,
            source_replacements=replacements or None,
        )
    except BaseException:
        if created_hidden_parent:
            try:
                hidden_path.parent.rmdir()
            except OSError:
                pass
        raise
    try:
        hidden_path.parent.rmdir()
    except OSError:
        pass
    current = _find_project_module(
        project,
        module.module_id,
        source_root=selected_source_root,
    )
    if current.collection_id != clean_collection_id:
        raise RuntimeError(f"Module {module.module_id!r} collection membership did not " "match the committed source transaction.")
    payload["applied"] = True
    payload["written"] = True
    payload["status"] = "updated"
    payload["module"] = current.to_dict()
    if "catalog_mutation" in applied:
        payload["catalog_mutation"] = applied["catalog_mutation"]
    return payload


def _set_project_module_active(
    project: Project,
    module_id: str,
    active: bool,
    *,
    source_root: str | os.PathLike[str] | None,
    write: bool,
    plan_hash: str | None,
) -> dict[str, object]:
    """Plan and optionally apply one canonical module-activity edit."""

    if not isinstance(active, bool):
        raise ValueError("Module active must be a boolean.")
    module = _find_project_module(project, module_id, source_root=source_root)
    module_root = Path(module.root).expanduser().resolve()
    selected_source_root = _module_source_root(
        project.root,
        project.source_roots,
        module_root,
    )
    visible_path = module_root / "meta.yaml"
    hidden_path = module_root / ".paradev" / "meta.yaml"
    visible, visible_snapshot = _module_metadata_source(
        project,
        visible_path,
        label="visible module metadata",
    )
    hidden, hidden_snapshot = _module_metadata_source(
        project,
        hidden_path,
        label="hidden module metadata",
    )
    previous_active = module.metadata.get("inactive") is not True
    edits: list[dict[str, object]] = []
    removals: list[dict[str, object]] = []
    replacements: list[dict[str, object]] = []
    files: list[dict[str, object]] = []

    hidden_after = dict(hidden)
    hidden_after.pop("inactive", None)
    if hidden_snapshot is not None:
        _append_module_metadata_existing_mutation(
            project,
            path=hidden_path,
            before=hidden,
            after=hidden_after,
            snapshot=hidden_snapshot,
            edits=edits,
            removals=removals,
            files=files,
            layer="hidden",
        )

    visible_after = dict(visible)
    if active:
        visible_after.pop("inactive", None)
    else:
        visible_after["inactive"] = True
    if visible_snapshot is not None:
        _append_module_metadata_existing_mutation(
            project,
            path=visible_path,
            before=visible,
            after=visible_after,
            snapshot=visible_snapshot,
            edits=edits,
            removals=removals,
            files=files,
            layer="visible",
        )
    elif visible_after:
        visible_text = _dump_module_metadata(visible_after)
        replacements.append(
            {
                "path": str(visible_path),
                "content_base64": base64.b64encode(visible_text.encode("utf-8")).decode("ascii"),
                "expected_absent": True,
            }
        )
        files.append(
            _module_metadata_file_view(
                project,
                visible_path,
                layer="visible",
                action="create",
                before=None,
                after=visible_text,
            )
        )

    changed = bool(edits or removals or replacements)
    current_hash = _module_activity_update_plan_hash(
        project,
        module=module,
        source_root=selected_source_root,
        previous_active=previous_active,
        active=active,
        visible_path=visible_path,
        visible_snapshot=visible_snapshot,
        hidden_path=hidden_path,
        hidden_snapshot=hidden_snapshot,
        edits=edits,
        removals=removals,
        replacements=replacements,
    )
    diagnostics: list[dict[str, object]] = []
    if write and (not isinstance(plan_hash, str) or not plan_hash):
        diagnostics.append(
            {
                "code": "module_activity_update.plan_hash_required",
                "severity": "error",
                "message": ("Applying a module activity change requires the exact " "plan_hash returned by a dry plan."),
            }
        )
    elif write and plan_hash != current_hash:
        diagnostics.append(
            {
                "code": "module_activity_update.plan_hash_mismatch",
                "severity": "error",
                "message": ("Module metadata changed after planning; review the " "current activity plan and apply its plan_hash."),
                "expected_plan_hash": current_hash,
                "provided_plan_hash": plan_hash,
            }
        )
    blocked = bool(diagnostics)
    payload: dict[str, object] = {
        "schema": MODULE_ACTIVITY_UPDATE_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "module_id": module.module_id,
        "family": module.family,
        "source_root": str(selected_source_root),
        "previous_active": previous_active,
        "active": active,
        "changed": changed,
        "blocked": blocked,
        "applied": False,
        "written": False,
        "status": "blocked" if blocked else "planned",
        "plan_hash": current_hash,
        "diagnostics": diagnostics,
        "files": files,
    }
    if blocked or not write:
        return payload
    if not changed:
        payload["applied"] = True
        payload["status"] = "unchanged"
        payload["module"] = module.to_dict()
        return payload

    applied = project.apply_source_draft(
        source_edits=edits or None,
        source_removals=removals or None,
        source_replacements=replacements or None,
    )
    try:
        hidden_path.parent.rmdir()
    except OSError:
        pass
    current = _find_project_module(
        project,
        module.module_id,
        source_root=selected_source_root,
    )
    current_active = current.metadata.get("inactive") is not True
    if current_active != active:
        raise RuntimeError(f"Module {module.module_id!r} activity did not match the " "committed source transaction.")
    payload["applied"] = True
    payload["written"] = True
    payload["status"] = "updated"
    payload["module"] = current.to_dict()
    if "catalog_mutation" in applied:
        payload["catalog_mutation"] = applied["catalog_mutation"]
    return payload


def _module_activity_update_plan_hash(
    project: Project,
    *,
    module: "Module",
    source_root: Path,
    previous_active: bool,
    active: bool,
    visible_path: Path,
    visible_snapshot: Mapping[str, object] | None,
    hidden_path: Path,
    hidden_snapshot: Mapping[str, object] | None,
    edits: Sequence[Mapping[str, object]],
    removals: Sequence[Mapping[str, object]],
    replacements: Sequence[Mapping[str, object]],
) -> str:
    """Hash requested activity and exact metadata-file revisions."""

    mutation_rows: list[dict[str, object]] = []
    for action, rows in (
        ("edit", edits),
        ("remove", removals),
        ("replace", replacements),
    ):
        for row in rows:
            canonical = {key: value for key, value in row.items() if key not in {"content_base64", "text"}}
            content = row.get("text")
            if isinstance(content, str):
                canonical["content_sha256"] = sha256hash(content.encode("utf-8"))
            content_base64 = row.get("content_base64")
            if isinstance(content_base64, str):
                canonical["content_sha256"] = sha256hash(base64.b64decode(content_base64))
            canonical["action"] = action
            mutation_rows.append(canonical)
    canonical_payload = {
        "schema": MODULE_ACTIVITY_UPDATE_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "project_root_identity": _module_create_path_identity(project.root),
        "module_id": module.module_id,
        "module_root": str(Path(module.root).expanduser().resolve()),
        "source_root": str(source_root),
        "previous_active": previous_active,
        "active": active,
        "metadata_sources": [
            _module_metadata_snapshot_hash_row(visible_path, visible_snapshot),
            _module_metadata_snapshot_hash_row(hidden_path, hidden_snapshot),
        ],
        "mutations": mutation_rows,
    }
    return sha256hash(
        dumps_json(
            canonical_payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            compact=True,
            adapt=False,
        )
    )


def _module_metadata_source(
    project: Project,
    path: Path,
    *,
    label: str,
) -> tuple[dict[str, object], dict[str, object] | None]:
    """Load one optional module metadata mapping and its stable revision."""

    if not path.exists():
        return {}, None
    snapshot = project.read_source_text(path)
    text = snapshot.get("text")
    if not isinstance(text, str):
        raise ValueError(f"{label.capitalize()} is not UTF-8 text: {path}.")
    try:
        value = loads_yaml(text)
    except YAMLError as error:
        raise ValueError(f"{label.capitalize()} is invalid YAML: {path}: {error}.") from error
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise ValueError(f"{label.capitalize()} must contain a YAML mapping: {path}.")
    if any(not isinstance(key, str) or not key for key in value):
        raise ValueError(f"{label.capitalize()} keys must be non-empty strings: {path}.")
    return cast(dict[str, object], value), snapshot


def _append_module_metadata_existing_mutation(
    project: Project,
    *,
    path: Path,
    before: Mapping[str, object],
    after: Mapping[str, object],
    snapshot: Mapping[str, object],
    edits: list[dict[str, object]],
    removals: list[dict[str, object]],
    files: list[dict[str, object]],
    layer: str,
) -> None:
    """Append one revision-guarded metadata edit or removal when changed."""

    if dict(before) == dict(after):
        return
    size = snapshot.get("size")
    mtime_ns = snapshot.get("mtime_ns")
    if isinstance(size, bool) or not isinstance(size, int) or not isinstance(mtime_ns, str):
        raise ValueError(f"Module metadata snapshot is incomplete: {path}.")
    before_text = snapshot.get("text")
    if not isinstance(before_text, str):
        raise ValueError(f"Module metadata snapshot is incomplete: {path}.")
    if after:
        after_text = _dump_module_metadata(after)
        edits.append(
            {
                "path": str(path),
                "text": after_text,
                "expected_size": size,
                "expected_mtime_ns": mtime_ns,
            }
        )
        action = "update"
    else:
        after_text = None
        removals.append(
            {
                "path": str(path),
                "expected_size": size,
                "expected_mtime_ns": mtime_ns,
            }
        )
        action = "remove"
    files.append(
        _module_metadata_file_view(
            project,
            path,
            layer=layer,
            action=action,
            before=before_text,
            after=after_text,
        )
    )


def _dump_module_metadata(metadata: Mapping[str, object]) -> str:
    """Serialize module metadata deterministically."""

    return (
        dumps_yaml(
            dict(metadata),
            sort_keys=False,
            indent=2,
            allow_unicode=True,
        ).rstrip("\n")
        + "\n"
    )


def _module_metadata_file_view(
    project: Project,
    path: Path,
    *,
    layer: str,
    action: str,
    before: str | None,
    after: str | None,
) -> dict[str, object]:
    """Return one compact, reviewable metadata-file mutation row."""

    return {
        "path": str(path),
        "relative_path": _project_relative_path(project.root, path),
        "layer": layer,
        "action": action,
        "before_sha256": sha256hash(before.encode("utf-8")) if before is not None else None,
        "after_sha256": sha256hash(after.encode("utf-8")) if after is not None else None,
    }


def _module_collection_update_plan_hash(
    project: Project,
    *,
    module: Module,
    source_root: Path,
    previous_collection_id: str | None,
    collection_id: str | None,
    visible_path: Path,
    visible_snapshot: Mapping[str, object] | None,
    hidden_path: Path,
    hidden_snapshot: Mapping[str, object] | None,
    edits: Sequence[Mapping[str, object]],
    removals: Sequence[Mapping[str, object]],
    replacements: Sequence[Mapping[str, object]],
) -> str:
    """Hash the requested membership and exact source-file revisions."""

    mutation_rows: list[dict[str, object]] = []
    for action, rows in (
        ("edit", edits),
        ("remove", removals),
        ("replace", replacements),
    ):
        for row in rows:
            canonical = {key: value for key, value in row.items() if key not in {"content_base64", "text"}}
            content = row.get("text")
            if isinstance(content, str):
                canonical["content_sha256"] = sha256hash(content.encode("utf-8"))
            content_base64 = row.get("content_base64")
            if isinstance(content_base64, str):
                canonical["content_sha256"] = sha256hash(base64.b64decode(content_base64))
            canonical["action"] = action
            mutation_rows.append(canonical)
    canonical_payload = {
        "schema": MODULE_COLLECTION_UPDATE_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "project_root_identity": _module_create_path_identity(project.root),
        "module_id": module.module_id,
        "module_root": str(Path(module.root).expanduser().resolve()),
        "source_root": str(source_root),
        "previous_collection_id": previous_collection_id,
        "collection_id": collection_id,
        "metadata_sources": [
            _module_metadata_snapshot_hash_row(visible_path, visible_snapshot),
            _module_metadata_snapshot_hash_row(hidden_path, hidden_snapshot),
        ],
        "mutations": mutation_rows,
    }
    return sha256hash(
        dumps_json(
            canonical_payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            compact=True,
            adapt=False,
        )
    )


def _module_metadata_snapshot_hash_row(
    path: Path,
    snapshot: Mapping[str, object] | None,
) -> dict[str, object]:
    """Return one exact metadata-source revision for a membership plan hash."""

    if snapshot is None:
        return {"path": str(path), "exists": False}
    text = snapshot.get("text")
    size = snapshot.get("size")
    mtime_ns = snapshot.get("mtime_ns")
    if not isinstance(text, str) or isinstance(size, bool) or not isinstance(size, int) or not isinstance(mtime_ns, str):
        raise ValueError(f"Module metadata snapshot is incomplete: {path}.")
    return {
        "path": str(path),
        "exists": True,
        "size": size,
        "mtime_ns": mtime_ns,
        "sha256": sha256hash(text.encode("utf-8")),
    }


def _module_metadata_cleanup_candidates(
    project: Project,
    *,
    family: str | None,
    module_id: str | None,
    source_root: Path | None,
) -> tuple[_ModuleMetadataCleanupCandidate, ...]:
    """Enumerate typed module folders without parsing their authored files."""

    object_id = _module_id_parts(module_id)[1] if module_id is not None else None
    roots = (source_root,) if source_root is not None else tuple(sorted(set(project.source_roots), key=str))
    candidates: list[_ModuleMetadataCleanupCandidate] = []
    seen_module_roots: set[Path] = set()
    for configured_root in roots:
        modules_root = configured_root / "modules"
        if modules_root.is_symlink():
            raise ValueError("Module metadata cleanup cannot traverse a symlinked modules " f"folder: {modules_root}.")
        if not modules_root.is_dir():
            continue
        if family is not None:
            family_roots = (modules_root / family,)
        else:
            try:
                family_roots = tuple(
                    sorted(
                        (path for path in modules_root.iterdir() if path.is_dir()),
                        key=lambda path: path.name,
                    )
                )
            except OSError as error:
                raise ValueError(f"Module families could not be listed safely: {modules_root}.") from error
        for family_root in family_roots:
            if family_root.is_symlink():
                raise ValueError("Module metadata cleanup cannot traverse a symlinked family " f"folder: {family_root}.")
            if not family_root.is_dir():
                continue
            try:
                module_roots = tuple(
                    sorted(
                        (path for path in family_root.iterdir() if path.is_dir()),
                        key=lambda path: path.name,
                    )
                )
            except OSError as error:
                raise ValueError(f"Module folders could not be listed safely: {family_root}.") from error
            for module_root in module_roots:
                candidate_object_id, _title = _project_browser_object_id_and_title(module_root.name)
                if object_id is not None and candidate_object_id != object_id:
                    continue
                if object_id is None and not _path_entry_exists_lexically(module_root / "meta.yaml"):
                    continue
                family_id = family_root.name
                absolute_module_root = _absolute_lexical_path(module_root)
                if absolute_module_root in seen_module_roots:
                    continue
                seen_module_roots.add(absolute_module_root)
                candidates.append(
                    _ModuleMetadataCleanupCandidate(
                        module_id=f"{family_id}/{candidate_object_id}",
                        family=family_id,
                        source_root=configured_root,
                        module_root=absolute_module_root,
                    )
                )
    return tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                str(candidate.module_root),
                candidate.module_id,
            ),
        )
    )


def _module_metadata_cleanup_entry(
    project: Project,
    module: _ModuleMetadataCleanupCandidate,
    *,
    source_slots: Sequence["Slot"],
) -> _ModuleMetadataCleanupEntry:
    """Snapshot and plan cleanup for one discovered module."""

    module_root = module.module_root
    source_root = module.source_root
    mutation_root = _module_metadata_cleanup_mutation_root(
        project,
        source_root,
    )
    path = module_root / "meta.yaml"
    source_path = _project_relative_path(project.root, path)
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return _ModuleMetadataCleanupEntry(
            module_id=module.module_id,
            family=module.family,
            source_root=source_root,
            module_root=module_root,
            path=path,
            mutation_root=mutation_root,
            action="absent",
        )
    except OSError as error:
        return _blocked_module_metadata_cleanup_entry(
            module,
            source_root=source_root,
            module_root=module_root,
            path=path,
            mutation_root=mutation_root,
            source_path=source_path,
            message=f"ParaDev could not inspect {source_path} safely: {error}",
        )
    if not stat.S_ISREG(metadata.st_mode):
        return _blocked_module_metadata_cleanup_entry(
            module,
            source_root=source_root,
            module_root=module_root,
            path=path,
            mutation_root=mutation_root,
            source_path=source_path,
            message=f"{source_path} must be a regular file before ParaDev can clean it.",
            current_size=metadata.st_size,
            current_mtime_ns=metadata.st_mtime_ns,
        )
    try:
        content, revision_metadata = _read_project_source_snapshot(
            mutation_root,
            path,
        )
    except ValueError as error:
        return _blocked_module_metadata_cleanup_entry(
            module,
            source_root=source_root,
            module_root=module_root,
            path=path,
            mutation_root=mutation_root,
            source_path=source_path,
            message=str(error),
            current_size=metadata.st_size,
            current_mtime_ns=metadata.st_mtime_ns,
        )
    current_size, current_mtime_ns = _module_metadata_cleanup_revision(revision_metadata)
    draft = plan_inferred_type_cleanup(
        content,
        module.family,
        source_path=source_path,
    )
    return _module_metadata_cleanup_entry_from_draft(
        module,
        source_root=source_root,
        module_root=module_root,
        path=path,
        mutation_root=mutation_root,
        content=content,
        current_size=current_size,
        current_mtime_ns=current_mtime_ns,
        draft=draft,
        source_slots=source_slots,
    )


def _module_metadata_cleanup_entry_from_draft(
    module: _ModuleMetadataCleanupCandidate,
    *,
    source_root: Path,
    module_root: Path,
    path: Path,
    mutation_root: Path,
    content: bytes,
    current_size: int,
    current_mtime_ns: int,
    draft: MetadataCleanupDraft,
    source_slots: Sequence["Slot"],
) -> _ModuleMetadataCleanupEntry:
    diagnostics: tuple[Mapping[str, object], ...] = tuple(
        {
            **diagnostic.to_view(),
            "module_id": module.module_id,
            "family": module.family,
            "path": str(path),
        }
        for diagnostic in draft.diagnostics
    )
    action = draft.action
    replacement = draft.replacement
    target_exists = draft.target_exists
    target_size = draft.target_size
    target_sha256 = draft.target_sha256
    if draft.action == "remove" and not _module_metadata_cleanup_has_authored_source(
        module,
        module_root,
        source_slots=source_slots,
    ):
        replacement = b"{}\n"
        action = "update"
        target_exists = True
        target_size = len(replacement)
        target_sha256 = sha256hash(replacement.decode("utf-8"))
        diagnostics = (
            *diagnostics,
            _module_metadata_cleanup_diagnostic(
                "module_metadata_cleanup.identity_marker_preserved",
                ("ParaDev retained a minimal empty metadata mapping because " f"{module.module_id} has no other authored source file yet."),
                severity="info",
                source_path=_project_relative_path(module_root, path),
                module_id=module.module_id,
                family=module.family,
                path=str(path),
            ),
        )
    return _ModuleMetadataCleanupEntry(
        module_id=module.module_id,
        family=module.family,
        source_root=source_root,
        module_root=module_root,
        path=path,
        mutation_root=mutation_root,
        action=action,
        current_size=current_size,
        current_mtime_ns=current_mtime_ns,
        current_sha256=draft.current_sha256,
        content_sha256=hashlib.sha256(content).hexdigest(),
        target_exists=target_exists,
        target_size=target_size,
        target_sha256=target_sha256,
        replacement=replacement,
        removed_keys=draft.removed_keys,
        diagnostics=diagnostics,
    )


def _module_metadata_cleanup_has_authored_source(
    module: _ModuleMetadataCleanupCandidate,
    module_root: Path,
    *,
    source_slots: Sequence["Slot"],
) -> bool:
    """Return whether module discovery survives without visible metadata."""

    from paradev.build.slots import match_slots

    try:
        matched = match_slots(
            module_root,
            source_slots,
            module_id=module.module_id,
        )
    except (OSError, ValueError):
        return False
    for source_paths in matched.source_slots.values():
        for source_path in source_paths:
            candidate = Path(source_path)
            if not candidate.is_absolute():
                candidate = module_root / candidate
            candidate = _absolute_lexical_path(candidate)
            try:
                relative = candidate.relative_to(module_root)
            except ValueError:
                continue
            if not relative.parts:
                continue
            if relative.parts[0] == ".paradev":
                continue
            if relative.as_posix() == "meta.yaml":
                continue
            return True
    return False


def _blocked_module_metadata_cleanup_entry(
    module: _ModuleMetadataCleanupCandidate,
    *,
    source_root: Path,
    module_root: Path,
    path: Path,
    mutation_root: Path,
    source_path: str,
    message: str,
    current_size: int | None = None,
    current_mtime_ns: int | None = None,
) -> _ModuleMetadataCleanupEntry:
    diagnostic = _module_metadata_cleanup_diagnostic(
        "module_metadata_cleanup.unsafe_source",
        message,
        source_path=source_path,
        module_id=module.module_id,
        family=module.family,
        path=str(path),
    )
    return _ModuleMetadataCleanupEntry(
        module_id=module.module_id,
        family=module.family,
        source_root=source_root,
        module_root=module_root,
        path=path,
        mutation_root=mutation_root,
        action="blocked",
        current_size=current_size,
        current_mtime_ns=current_mtime_ns,
        diagnostics=(diagnostic,),
    )


def _module_metadata_cleanup_mutation_root(
    project: Project,
    source_root: Path,
) -> Path:
    try:
        source_root.relative_to(project.root)
    except ValueError:
        return source_root
    return project.root


def _module_metadata_cleanup_revision(
    metadata: os.stat_result | Win32FileMetadata,
) -> tuple[int, int]:
    if isinstance(metadata, Win32FileMetadata):
        return metadata.size, metadata.mtime_ns
    return metadata.st_size, metadata.st_mtime_ns


def _module_metadata_cleanup_root_identities(
    project: Project,
    mutation_roots: Sequence[Path],
) -> dict[str, dict[str, object]]:
    roots = {project.root, *mutation_roots}
    identities: dict[str, dict[str, object]] = {}
    for candidate in sorted(roots, key=str):
        root, identity = _source_draft_root_identity(candidate)
        identities[str(candidate)] = {
            "path": str(root),
            "identity": identity,
        }
    return identities


def _module_metadata_cleanup_plan_hash(
    project: Project,
    *,
    family: str | None,
    module_id: str | None,
    source_root: Path | None,
    entries: Sequence[_ModuleMetadataCleanupEntry],
    diagnostics: Sequence[Mapping[str, object]],
    root_identities: Mapping[str, Mapping[str, object]],
) -> str:
    canonical = {
        "schema": MODULE_METADATA_CLEANUP_SCHEMA,
        "policy": MODULE_METADATA_CLEANUP_POLICY,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "selectors": {
            "family": family,
            "module_id": module_id,
            "source_root": str(source_root) if source_root is not None else None,
        },
        "root_identities": [
            {
                "root": root,
                "path": row["path"],
                "identity": list(cast(tuple[int, int], row["identity"])),
            }
            for root, row in sorted(root_identities.items())
        ],
        "entries": [
            {
                "module_id": entry.module_id,
                "family": entry.family,
                "source_root": str(entry.source_root),
                "module_root": str(entry.module_root),
                "path": str(entry.path),
                "mutation_root": str(entry.mutation_root),
                "action": entry.action,
                "current_size": entry.current_size,
                "current_mtime_ns": entry.current_mtime_ns,
                "current_sha256": entry.current_sha256,
                "content_sha256": entry.content_sha256,
                "target_exists": entry.target_exists,
                "target_size": entry.target_size,
                "target_sha256": entry.target_sha256,
                "replacement_base64": (base64.b64encode(entry.replacement).decode("ascii") if entry.replacement is not None else None),
                "removed_keys": list(entry.removed_keys),
                "diagnostics": [dict(item) for item in entry.diagnostics],
            }
            for entry in entries
        ],
        "diagnostics": [dict(item) for item in diagnostics],
    }
    payload = dumps_json(
        canonical,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        compact=True,
        adapt=False,
    )
    return sha256hash(payload)


def _apply_module_metadata_cleanup(
    mutation_root: Path,
    entries: Sequence[_ModuleMetadataCleanupEntry],
    *,
    root_identity: tuple[int, int],
) -> None:
    edits: list[dict[str, object]] = []
    removals: list[dict[str, object]] = []
    for entry in entries:
        if entry.current_size is None or entry.current_mtime_ns is None or entry.content_sha256 is None:
            raise AssertionError("Changed metadata cleanup entry has no exact source revision.")
        expected_revision = (
            entry.current_size,
            entry.current_mtime_ns,
        )
        if entry.action == "update":
            if entry.replacement is None:
                raise AssertionError("Metadata cleanup update has no replacement.")
            edits.append(
                {
                    "path": entry.path,
                    "text": entry.replacement.decode("utf-8"),
                    "expected_revision": expected_revision,
                    "expected_content_sha256": entry.content_sha256,
                }
            )
        elif entry.action == "remove":
            removals.append(
                {
                    "path": entry.path,
                    "expected_revision": expected_revision,
                    "expected_content_sha256": entry.content_sha256,
                }
            )
    _apply_source_draft_mutations(
        mutation_root,
        edits=edits,
        replacements=(),
        removals=removals,
        root_identity=root_identity,
    )


def _module_metadata_cleanup_payload(
    project: Project,
    *,
    family: str | None,
    module_id: str | None,
    source_root: Path | None,
    entries: Sequence[_ModuleMetadataCleanupEntry],
    diagnostics: Sequence[Mapping[str, object]],
    plan_hash: str,
    blocked: bool,
    applied: bool,
    written: bool,
    partial_state: str | None,
    recovery: Mapping[str, object] | None,
) -> dict[str, object]:
    changed_entries = [entry for entry in entries if entry.changed]
    visible_entries = [entry for entry in entries if entry.changed or entry.blocked]
    family_ids = sorted({entry.family for entry in entries})
    family_rows = [
        _module_metadata_cleanup_family_payload(
            family_id,
            [entry for entry in entries if entry.family == family_id],
        )
        for family_id in family_ids
    ]
    counts = _module_metadata_cleanup_counts(entries)
    if blocked:
        status = "blocked"
    elif written:
        status = "cleaned"
    elif applied:
        status = "unchanged"
    elif changed_entries:
        status = "planned"
    else:
        status = "clean"
    payload: dict[str, object] = {
        "schema": MODULE_METADATA_CLEANUP_SCHEMA,
        "policy": MODULE_METADATA_CLEANUP_POLICY,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "selectors": {
            "family": family,
            "module_id": module_id,
            "source_root": str(source_root) if source_root is not None else None,
        },
        "status": status,
        "blocked": blocked,
        "applied": applied,
        "written": written,
        "partially_written": partial_state is not None,
        "partial_state": partial_state,
        "plan_hash": plan_hash,
        "counts": counts,
        "families": family_rows,
        "diagnostics": [dict(item) for item in diagnostics],
        "files": [_module_metadata_cleanup_entry_payload(project, entry) for entry in visible_entries],
    }
    if recovery is not None:
        payload["recovery"] = dict(recovery)
    return payload


def _module_metadata_cleanup_counts(
    entries: Sequence[_ModuleMetadataCleanupEntry],
) -> dict[str, int]:
    update_count = sum(entry.action == "update" for entry in entries)
    remove_count = sum(entry.action == "remove" for entry in entries)
    blocked_count = sum(entry.blocked for entry in entries)
    return {
        "modules_scanned": len(entries),
        "metadata_files_scanned": sum(entry.action != "absent" for entry in entries),
        "update": update_count,
        "remove": remove_count,
        "unchanged": sum(entry.action in {"absent", "unchanged"} for entry in entries),
        "blocked": blocked_count,
        "changed": update_count + remove_count,
    }


def _module_metadata_cleanup_family_payload(
    family: str,
    entries: Sequence[_ModuleMetadataCleanupEntry],
) -> dict[str, object]:
    return {
        "family": family,
        "counts": _module_metadata_cleanup_counts(entries),
    }


def _module_metadata_cleanup_entry_payload(
    project: Project,
    entry: _ModuleMetadataCleanupEntry,
) -> dict[str, object]:
    planned: dict[str, object] | None = None
    if entry.target_exists is not None:
        planned = {"exists": entry.target_exists}
        if entry.target_exists:
            planned.update(
                {
                    "size_bytes": entry.target_size,
                    "sha256": entry.target_sha256,
                }
            )
    current: dict[str, object] = {
        "exists": entry.action != "absent",
        "size_bytes": entry.current_size,
        "mtime_ns": (str(entry.current_mtime_ns) if entry.current_mtime_ns is not None else None),
        "sha256": entry.current_sha256,
    }
    return {
        "module_id": entry.module_id,
        "family": entry.family,
        "source_root": str(entry.source_root),
        "root": str(entry.module_root),
        "path": str(entry.path),
        "relative_path": _project_relative_path(project.root, entry.path),
        "module_relative_path": "meta.yaml",
        "action": entry.action,
        "changed": entry.changed,
        "blocked": entry.blocked,
        "removed_keys": list(entry.removed_keys),
        "current": current,
        "planned": planned,
        "diagnostics": [dict(item) for item in entry.diagnostics],
    }


def _module_metadata_cleanup_diagnostic(
    code: str,
    message: str,
    *,
    severity: str = "error",
    **fields: object,
) -> dict[str, object]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        **fields,
    }


def _duplicate_project_module(
    project: Project,
    module_id: str,
    object_id: str,
    *,
    source_root: str | os.PathLike[str] | None,
    destination_source_root: str | os.PathLike[str] | None,
    identity: Literal["rewrite", "preserve"],
    write: bool,
    plan_hash: str | None,
    catalog_lock_held: bool,
) -> dict[str, object]:
    from paradev.sdk._module_copy import (
        ModuleCopyRollbackIncomplete,
        ModuleCopySafetyError,
        ModuleCopySnapshot,
        ModuleCopyUnavailable,
        inspect_module_copy,
        install_module_copy,
    )

    family, source_object_id = _module_id_parts(module_id)
    target_object_id = _module_path_token(object_id, "object_id")
    identity_mode = _module_duplicate_identity_mode(identity)
    if target_object_id == source_object_id:
        raise ValueError("Duplicated module object_id must differ from the source object id.")
    selected_source_root, source_module_root = _module_remove_location(
        project,
        family=family,
        object_id=source_object_id,
        source_root=source_root,
    )
    selected_destination_root = (
        selected_source_root
        if destination_source_root is None
        else _select_source_root(
            project.root,
            project.source_roots,
            destination_source_root,
        )
    )
    source_module_id = f"{family}/{source_object_id}"
    target_module_id = f"{family}/{target_object_id}"
    target_name = _module_duplicate_target_name(
        source_module_root.name,
        target_object_id,
    )
    target_root = selected_destination_root / "modules" / family / target_name
    diagnostics: list[dict[str, object]] = []
    snapshot: ModuleCopySnapshot | None = None
    identity_rewriter = None
    if identity_mode == "rewrite":
        registry = project._build_registry(profile=project.game)
        identity_rewriter = registry.identity_rewriter_for(family)
        if identity_rewriter is None:
            diagnostics.append(
                _module_duplicate_diagnostic(
                    project,
                    code="module_duplicate.identity_rewrite_unavailable",
                    message=(f"Build family {family!r} does not declare an identity " "rewriter. Choose identity='preserve' for an exact copy."),
                )
            )
    try:
        snapshot = inspect_module_copy(
            selected_source_root,
            selected_destination_root,
            family=family,
            source_object_id=source_object_id,
            source_name=source_module_root.name,
            target_name=target_name,
            target_object_id=target_object_id,
            identity_rewriter=identity_rewriter,
        )
    except ModuleCopyUnavailable as error:
        diagnostics.append(
            _module_duplicate_diagnostic(
                project,
                code="module_duplicate.unsupported_platform",
                message=(f"Module duplication was blocked to protect your files: {error}"),
            )
        )
    except ModuleCopySafetyError as error:
        diagnostics.append(
            _module_duplicate_diagnostic(
                project,
                code=f"module_duplicate.{error.code}",
                message=str(error),
                path=error.path,
            )
        )
    current_plan_hash = _module_duplicate_plan_hash(
        project,
        source_module_id=source_module_id,
        module_id=target_module_id,
        source_root=selected_source_root,
        destination_source_root=selected_destination_root,
        source_module_root=source_module_root,
        root=target_root,
        identity_mode=identity_mode,
        snapshot=snapshot,
        diagnostics=diagnostics,
    )
    blocked = bool(diagnostics)
    applied = False
    written = False
    target_identity: tuple[int, int] | None = None
    if write and not isinstance(plan_hash, str):
        diagnostics.append(
            _module_duplicate_diagnostic(
                project,
                code="module_duplicate.plan_hash_required",
                message=("Applying a module duplicate requires the exact plan_hash " "returned by a dry plan."),
            )
        )
        blocked = True
    elif write and plan_hash != current_plan_hash:
        diagnostics.append(
            _module_duplicate_diagnostic(
                project,
                code="module_duplicate.plan_hash_mismatch",
                message=("The module duplicate changed after planning; review the " "current plan and apply its plan_hash."),
                expected_plan_hash=current_plan_hash,
                provided_plan_hash=plan_hash,
            )
        )
        blocked = True
    if write and not blocked:
        if snapshot is None:
            raise AssertionError("Unblocked module duplicate has no filesystem snapshot.")
        try:
            installed = install_module_copy(
                selected_source_root,
                selected_destination_root,
                family=family,
                source_object_id=source_object_id,
                source_name=source_module_root.name,
                target_name=target_name,
                target_object_id=target_object_id,
                expected=snapshot,
                identity_rewriter=identity_rewriter,
            )
        except ModuleCopyRollbackIncomplete as error:
            diagnostics.append(
                _module_duplicate_diagnostic(
                    project,
                    code="module_duplicate.rollback_incomplete",
                    message=("Module duplication rollback was incomplete; recovery " f"data remains at {error.recovery_path}: {error}."),
                    path=error.recovery_path,
                    recovery_path=str(error.recovery_path),
                )
            )
            blocked = True
        except (ModuleCopyUnavailable, ModuleCopySafetyError, OSError) as error:
            diagnostics.append(
                _module_duplicate_diagnostic(
                    project,
                    code="module_duplicate.concurrent_change",
                    message=("Module source or destination changed before the " f"duplicate could be installed safely: {error}."),
                )
            )
            blocked = True
        else:
            target_identity = installed.target_identity
            applied = True
            written = True
            if installed.cleanup_path is not None:
                diagnostics.append(
                    _module_duplicate_diagnostic(
                        project,
                        code="module_duplicate.cleanup_pending",
                        message=(
                            "The module was duplicated, but ParaDev could not "
                            "finish removing its empty transaction folder. "
                            f"You can inspect and remove it later: "
                            f"{installed.cleanup_path}."
                        ),
                        path=installed.cleanup_path,
                        severity="warning",
                        recovery_path=str(installed.cleanup_path),
                    )
                )
    payload = _module_duplicate_payload(
        project,
        source_module_id=source_module_id,
        module_id=target_module_id,
        family=family,
        object_id=target_object_id,
        source_root=selected_source_root,
        destination_source_root=selected_destination_root,
        source_module_root=source_module_root,
        root=target_root,
        identity_mode=identity_mode,
        snapshot=snapshot,
        diagnostics=diagnostics,
        plan_hash=current_plan_hash,
        blocked=blocked,
        applied=applied,
        written=written,
        target_identity=target_identity,
    )
    if written:
        payload["catalog_mutation"] = _created_module_catalog_projection(
            project,
            payload,
            source_root=selected_destination_root,
            catalog_lock_held=catalog_lock_held,
        )
    return payload


def _module_duplicate_payload(
    project: Project,
    *,
    source_module_id: str,
    module_id: str,
    family: str,
    object_id: str,
    source_root: Path,
    destination_source_root: Path,
    source_module_root: Path,
    root: Path,
    identity_mode: Literal["rewrite", "preserve"],
    snapshot: object | None,
    diagnostics: list[dict[str, object]],
    plan_hash: str,
    blocked: bool,
    applied: bool,
    written: bool,
    target_identity: tuple[int, int] | None,
) -> dict[str, object]:
    from paradev.sdk._module_copy import ModuleCopySnapshot

    typed_snapshot = snapshot if isinstance(snapshot, ModuleCopySnapshot) else None
    directories = typed_snapshot.directory_views() if typed_snapshot is not None else []
    files = typed_snapshot.file_views() if typed_snapshot is not None else []
    exclusions = [item.to_view() for item in typed_snapshot.exclusions] if typed_snapshot is not None else []
    source: dict[str, object] = {
        "module_id": source_module_id,
        "source_root": str(source_root),
        "root": str(source_module_root),
        "relative_path": _project_relative_path(
            project.root,
            source_module_root,
        ),
        "root_identity": None,
        "modules_identity": None,
        "family_identity": None,
        "module_identity": None,
        "tree_digest": None,
        "content_digest": None,
        "identity_rewriter": None,
    }
    destination: dict[str, object] = {
        "module_id": module_id,
        "source_root": str(destination_source_root),
        "root": str(root),
        "relative_path": _project_relative_path(project.root, root),
        "root_identity": None,
        "modules_identity": None,
        "family_identity": None,
        "target_identity": (list(target_identity) if target_identity is not None else None),
        "entry_count": 0,
        "entry_names_digest": None,
        "content_digest": None,
    }
    if typed_snapshot is not None:
        source.update(typed_snapshot.source_view())
        destination.update(
            typed_snapshot.destination_view(
                target_identity=target_identity,
            )
        )
    totals = {
        "directory_count": len(directories),
        "file_count": len(files),
        "excluded_count": len(exclusions),
        "size_bytes": (typed_snapshot.size_bytes if typed_snapshot is not None else 0),
        "target_size_bytes": (typed_snapshot.target_size_bytes if typed_snapshot is not None else 0),
        "rewritten_file_count": (typed_snapshot.rewritten_file_count if typed_snapshot is not None else 0),
        "renamed_path_count": (typed_snapshot.renamed_path_count if typed_snapshot is not None else 0),
    }
    return {
        "schema": MODULE_DUPLICATE_SCHEMA,
        "project_id": project.project_id,
        "source_module_id": source_module_id,
        "module_id": module_id,
        "family": family,
        "object_id": object_id,
        "source_root": str(source_root),
        "destination_source_root": str(destination_source_root),
        "source_module_root": str(source_module_root),
        "root": str(root),
        "source_relative_path": _project_relative_path(
            project.root,
            source_module_root,
        ),
        "relative_path": _project_relative_path(project.root, root),
        "status": ("duplicated" if written else "blocked" if blocked else "planned"),
        "blocked": blocked,
        "applied": applied,
        "written": written,
        "plan_hash": plan_hash,
        "identity_mode": identity_mode,
        "identity_rewriter": (typed_snapshot.identity_rewriter if typed_snapshot is not None else None),
        "content_rewritten": bool(typed_snapshot is not None and typed_snapshot.rewritten_file_count > 0),
        "paths_rewritten": bool(typed_snapshot is not None and typed_snapshot.renamed_path_count > 0),
        "diagnostics": diagnostics,
        "directories": directories,
        "files": files,
        "exclusions": exclusions,
        "totals": totals,
        "source": source,
        "destination": destination,
    }


def _module_duplicate_plan_hash(
    project: Project,
    *,
    source_module_id: str,
    module_id: str,
    source_root: Path,
    destination_source_root: Path,
    source_module_root: Path,
    root: Path,
    identity_mode: Literal["rewrite", "preserve"],
    snapshot: object | None,
    diagnostics: Sequence[Mapping[str, object]],
) -> str:
    from paradev.sdk._module_copy import ModuleCopySnapshot

    typed_snapshot = snapshot if isinstance(snapshot, ModuleCopySnapshot) else None
    canonical = {
        "schema": MODULE_DUPLICATE_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "project_root_identity": _module_create_path_identity(project.root),
        "source_module_id": source_module_id,
        "module_id": module_id,
        "source_root": str(source_root),
        "destination_source_root": str(destination_source_root),
        "source_module_root": str(source_module_root),
        "root": str(root),
        "identity_mode": identity_mode,
        "identity_rewriter": (typed_snapshot.identity_rewriter if typed_snapshot is not None else None),
        "content_rewritten": bool(typed_snapshot is not None and typed_snapshot.rewritten_file_count > 0),
        "paths_rewritten": bool(typed_snapshot is not None and typed_snapshot.renamed_path_count > 0),
        "source": (typed_snapshot.source_view() if typed_snapshot is not None else None),
        "destination": (typed_snapshot.destination_view() if typed_snapshot is not None else None),
        "directories": (typed_snapshot.directory_views() if typed_snapshot is not None else []),
        "files": (typed_snapshot.file_views() if typed_snapshot is not None else []),
        "exclusions": ([item.to_view() for item in typed_snapshot.exclusions] if typed_snapshot is not None else []),
        "diagnostics": [dict(item) for item in diagnostics],
    }
    payload = dumps_json(
        canonical,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        compact=True,
        adapt=False,
    )
    return sha256hash(payload)


def _module_duplicate_diagnostic(
    project: Project,
    *,
    code: str,
    message: str,
    path: Path | None = None,
    **fields: object,
) -> dict[str, object]:
    diagnostic: dict[str, object] = {
        "code": code,
        "severity": "error",
        "message": message,
        **fields,
    }
    if path is not None:
        diagnostic["path"] = str(path)
        diagnostic["relative_path"] = _project_relative_path(
            project.root,
            path,
        )
    return diagnostic


def _module_duplicate_identity_mode(
    value: object,
) -> Literal["rewrite", "preserve"]:
    if value not in {"rewrite", "preserve"}:
        raise ValueError("Module duplicate identity must be 'rewrite' or 'preserve'.")
    return cast(Literal["rewrite", "preserve"], value)


def _module_duplicate_target_name(
    source_name: str,
    target_object_id: str,
) -> str:
    _source_object_id, separator, source_title = source_name.partition(" - ")
    if separator != " - " or not source_title.strip():
        return target_object_id
    title = portable_authoring_title(
        source_title,
        object_id=target_object_id,
    )
    return f"{target_object_id} - {title}"


def _rename_project_module(
    project: Project,
    module_id: str,
    object_id: str,
    *,
    source_root: str | os.PathLike[str] | None,
    title: str | None,
    catalog_lock_held: bool,
) -> dict[str, object]:
    prepared = _prepare_project_module_rename(
        project,
        module_id,
        object_id,
        source_root=source_root,
        title=title,
    )
    _commit_prepared_module_rename(project, prepared)
    payload = _prepared_module_rename_payload(project, prepared)
    from paradev.hb import _sync_module_catalog_projection

    payload["catalog_mutation"] = _sync_module_catalog_projection(
        project,
        previous=prepared.previous_module.to_dict(),
        current=prepared.module.to_dict(),
        _lock_held=catalog_lock_held,
    )
    return payload


def _prepare_project_collection_rename(
    project: Project,
    collection: "Collection",
    target_id: str,
    *,
    source_root: Path,
) -> _PreparedCollectionRename:
    """Validate and retain one collection rename without changing source."""

    target_object_id = _collection_id_token(target_id)
    if target_object_id == collection.collection_id:
        raise ValueError(f"Collection {collection.collection_id} already has collection id " f"{target_object_id!r}.")
    previous_root = _collection_root(collection)
    target = project.authoring_path(
        "collection",
        collection.family,
        target_object_id,
        source_root=source_root,
    )
    root = Path(str(target["root"]))
    _previous_object_id, separator, previous_title = previous_root.name.partition(" - ")
    if separator and previous_title.strip():
        root = root.with_name(f"{target_object_id} - " f"{portable_authoring_title(previous_title.strip(), object_id=target_object_id)}")
    if root.exists():
        raise ValueError("Collection target already exists: " f"{_project_relative_path(project.root, root)}.")
    directory_identity = _module_directory_identity(
        source_root,
        family=collection.family,
        module_name=previous_root.name,
        container="collections",
    )
    return _PreparedCollectionRename(
        source_root=source_root,
        previous_collection=collection,
        previous_root=previous_root,
        root=root,
        target_object_id=target_object_id,
        directory_identity=directory_identity,
    )


def _commit_prepared_collection_rename(
    project: Project,
    prepared: _PreparedCollectionRename,
) -> None:
    """Commit one retained collection-folder rename at a transaction boundary."""

    try:
        _rename_module_directory(
            prepared.source_root,
            family=prepared.previous_collection.family,
            source_name=prepared.previous_root.name,
            target_name=prepared.root.name,
            target_object_id=prepared.target_object_id,
            container="collections",
            expected_source_identity=prepared.directory_identity,
        )
    except FileExistsError as error:
        raise ValueError("Collection target already exists: " f"{_project_relative_path(project.root, prepared.root)}.") from error
    except _AnchoredModuleMutationUnavailable as error:
        raise ValueError(f"Collection rename was blocked to protect your files: {error}.") from error
    except OSError as error:
        raise ValueError(f"Collection rename path changed before it could be moved: {error}.") from error


def _prepare_project_collection_removal(
    project: Project,
    collection: "Collection",
    *,
    source_root: Path,
    inventory_digest: str,
) -> _PreparedCollectionRemoval:
    """Retain one collection folder and choose a private quarantine name."""

    previous_root = _collection_root(collection)
    target_object_id = f".paradev-remove-{uuid4().hex}"
    root = previous_root.with_name(target_object_id)
    if root.exists():
        raise ValueError("Collection removal quarantine already exists: " f"{_project_relative_path(project.root, root)}.")
    directory_identity = _module_directory_identity(
        source_root,
        family=collection.family,
        module_name=previous_root.name,
        container="collections",
    )
    return _PreparedCollectionRemoval(
        source_root=source_root,
        previous_collection=collection,
        previous_root=previous_root,
        root=root,
        target_object_id=target_object_id,
        directory_identity=directory_identity,
        inventory_digest=inventory_digest,
    )


def _commit_prepared_collection_removal(
    project: Project,
    prepared: _PreparedCollectionRemoval,
) -> None:
    """Atomically quarantine one collection folder at the commit boundary."""

    current_files = _collection_remove_files(
        project.root,
        prepared.previous_root,
        blocked=False,
    )
    current_digest = _collection_remove_inventory_digest(current_files)
    if current_digest != prepared.inventory_digest:
        raise ValueError("Collection descriptor files changed after planning; review a new " "removal plan before applying it.")
    try:
        _rename_module_directory(
            prepared.source_root,
            family=prepared.previous_collection.family,
            source_name=prepared.previous_root.name,
            target_name=prepared.root.name,
            target_object_id=prepared.target_object_id,
            container="collections",
            expected_source_identity=prepared.directory_identity,
        )
    except FileExistsError as error:
        raise ValueError("Collection removal quarantine already exists: " f"{_project_relative_path(project.root, prepared.root)}.") from error
    except _AnchoredModuleMutationUnavailable as error:
        raise ValueError(f"Collection removal was blocked to protect your files: {error}.") from error
    except OSError as error:
        raise ValueError(f"Collection removal path changed before it could be moved: {error}.") from error


def _collection_member_pointer_modules(
    project: Project,
    *,
    family: str,
    collection_id: str,
    source_root: Path,
    effective_members: Sequence["Module"],
) -> tuple["Module", ...]:
    """Find every module whose visible or hidden metadata owns a pointer."""

    effective_ids = {module.module_id for module in effective_members}
    pointer_modules: list["Module"] = []
    for module in project.discover_modules(family=family).modules:
        module_root = Path(module.root).expanduser().resolve()
        if (
            _module_source_root(
                project.root,
                project.source_roots,
                module_root,
            )
            != source_root
        ):
            continue
        explicit_values: list[object] = []
        for layer, path in (
            ("visible", module_root / "meta.yaml"),
            ("hidden", module_root / ".paradev" / "meta.yaml"),
        ):
            metadata, _snapshot = _module_metadata_source(
                project,
                path,
                label=f"{layer} module metadata",
            )
            if "collection" in metadata:
                explicit_values.append(metadata["collection"])
        if collection_id in explicit_values or (module.module_id in effective_ids and explicit_values):
            pointer_modules.append(module)
    return tuple(sorted(pointer_modules, key=lambda item: item.module_id))


def _collection_member_rename_edits(
    project: Project,
    *,
    modules: Sequence["Module"],
    previous_collection_id: str,
    collection_id: str | None,
) -> tuple[
    tuple[dict[str, object], ...],
    tuple[dict[str, object], ...],
    tuple[dict[str, object], ...],
]:
    """Return exact edits/removals for explicit collection pointers."""

    edits: list[dict[str, object]] = []
    removals: list[dict[str, object]] = []
    files: list[dict[str, object]] = []
    for module in sorted(modules, key=lambda item: item.module_id):
        module_root = Path(module.root).expanduser().resolve()
        layers = (
            ("visible", module_root / "meta.yaml"),
            ("hidden", module_root / ".paradev" / "meta.yaml"),
        )
        found = False
        for layer, path in layers:
            metadata, snapshot = _module_metadata_source(
                project,
                path,
                label=f"{layer} module metadata",
            )
            if "collection" not in metadata:
                continue
            found = True
            current = metadata["collection"]
            if current != previous_collection_id:
                raise ValueError(
                    f"Module {module.module_id!r} has conflicting {layer} "
                    f"collection metadata {current!r}; expected "
                    f"{previous_collection_id!r}. Clean the duplicate metadata "
                    "before renaming the collection."
                )
            if snapshot is None:
                raise ValueError(f"Module {module.module_id!r} {layer} collection metadata " "disappeared during collection planning.")
            after = dict(metadata)
            if collection_id is None:
                after.pop("collection")
            else:
                after["collection"] = collection_id
            _append_module_metadata_existing_mutation(
                project,
                path=path,
                before=metadata,
                after=after,
                snapshot=snapshot,
                edits=edits,
                removals=removals,
                files=files,
                layer=layer,
            )
        if not found:
            raise ValueError(
                f"Module {module.module_id!r} belongs to collection "
                f"{previous_collection_id!r}, but no editable collection "
                "pointer exists in meta.yaml or .paradev/meta.yaml."
            )
    if removals and collection_id is not None:
        raise AssertionError("Collection rename must not remove metadata files.")
    return tuple(edits), tuple(removals), tuple(files)


def _prepare_project_module_rename(
    project: Project,
    module_id: str,
    object_id: str,
    *,
    source_root: str | os.PathLike[str] | None,
    title: str | None,
) -> _PreparedModuleRename:
    """Validate and snapshot one module rename without changing source files."""

    family, previous_object_id = _module_id_parts(module_id)
    selected_source_root, module_root = _module_remove_location(
        project,
        family=family,
        object_id=previous_object_id,
        source_root=source_root,
    )
    _raise_module_rename_path_error(
        project.root,
        selected_source_root,
        module_root,
        family=family,
        object_id=previous_object_id,
    )
    scoped_project = replace(project, source_roots=(selected_source_root,))
    module = _find_project_module(
        scoped_project,
        f"{family}/{previous_object_id}",
        source_root=selected_source_root,
    )
    target_object_id = _module_path_token(object_id, "object_id")
    target_module_id = f"{module.family}/{target_object_id}"
    target_folder_name = _renamed_module_folder_name(
        module_root.name,
        previous_object_id=previous_object_id,
        target_object_id=target_object_id,
        title=title,
    )
    target_root = selected_source_root / "modules" / module.family / target_folder_name
    if target_folder_name == module_root.name:
        raise ValueError(f"Module {module.module_id} already has object id {target_object_id!r}.")
    directory_identity = _module_directory_identity(
        selected_source_root,
        family=module.family,
        module_name=module_root.name,
    )
    renamed_module = _renamed_module_record(
        module,
        module_id=target_module_id,
        previous_root=module_root,
        root=target_root,
    )
    return _PreparedModuleRename(
        source_root=selected_source_root,
        previous_module=module,
        module=renamed_module,
        previous_root=module_root,
        root=target_root,
        target_object_id=target_object_id,
        directory_identity=directory_identity,
    )


def _commit_prepared_module_rename(
    project: Project,
    prepared: _PreparedModuleRename,
) -> None:
    """Commit one preflighted module rename at a transaction boundary."""

    try:
        _rename_module_directory(
            prepared.source_root,
            family=prepared.previous_module.family,
            source_name=prepared.previous_root.name,
            target_name=prepared.root.name,
            target_object_id=prepared.target_object_id,
            expected_source_identity=prepared.directory_identity,
        )
    except FileExistsError as error:
        raise ValueError("Module target already exists: " f"{_project_relative_path(project.root, prepared.root)}.") from error
    except _AnchoredModuleMutationUnavailable as error:
        raise ValueError(f"Module rename was blocked to protect your files: {error}.") from error
    except OSError as error:
        raise ValueError(f"Module rename path changed before it could be moved: {error}.") from error


def _prepared_module_rename_payload(
    project: Project,
    prepared: _PreparedModuleRename,
) -> dict[str, object]:
    """Return the standard rename payload for a committed rename draft."""

    return _module_rename_payload(
        project,
        previous_module=prepared.previous_module,
        module=prepared.module,
        previous_root=prepared.previous_root,
        root=prepared.root,
    )


def _renamed_module_folder_name(
    source_name: str,
    *,
    previous_object_id: str,
    target_object_id: str,
    title: str | None = None,
) -> str:
    """Return a renamed physical folder with a canonical readable suffix."""

    if title is not None:
        clean_title = title.strip() if isinstance(title, str) else ""
        if not clean_title:
            raise ValueError("Module title must be non-empty when provided.")
        portable_title = portable_authoring_title(
            clean_title,
            object_id=target_object_id,
        )
        return f"{target_object_id} - {portable_title}"

    titled_prefix = f"{previous_object_id} - "
    if source_name.startswith(titled_prefix) and len(source_name) > len(titled_prefix):
        return f"{target_object_id}{source_name[len(previous_object_id) :]}"
    return target_object_id


def _remove_project_module(
    project: Project,
    module_id: str,
    *,
    source_root: str | os.PathLike[str] | None,
    write: bool,
    catalog_lock_held: bool,
) -> dict[str, object]:
    family, object_id = _module_id_parts(module_id)
    selected_source_root, module_root = _module_remove_location(
        project,
        family=family,
        object_id=object_id,
        source_root=source_root,
    )
    diagnostics = _module_remove_diagnostics(
        project.root,
        selected_source_root,
        module_root,
        family=family,
        object_id=object_id,
    )
    blocked = any(item.get("severity") == "error" for item in diagnostics)
    if blocked:
        from paradev.build import Module

        module = Module(module_id=f"{family}/{object_id}", family=family, root=module_root)
    else:
        scoped_project = replace(project, source_roots=(selected_source_root,))
        module = _find_project_module(scoped_project, f"{family}/{object_id}", source_root=selected_source_root)
    files = _module_remove_files(project.root, module_root, blocked=blocked)
    removed = False
    removal_quarantine: _ModuleRemovalQuarantine | None = None
    if write and not blocked:
        try:
            removal_quarantine = _remove_module_directory(
                selected_source_root,
                family=family,
                module_name=module_root.name,
            )
            removed = True
        except _AnchoredModuleMutationUnavailable as error:
            diagnostics = [
                _module_remove_diagnostic(
                    project.root,
                    module_root,
                    code="module_remove.unsupported_platform",
                    message=f"Module removal was blocked to protect your files: {error}.",
                )
            ]
            blocked = True
            files = _module_remove_files(project.root, module_root, blocked=True)
        except OSError as error:
            diagnostics = [
                _module_remove_diagnostic(
                    project.root,
                    module_root,
                    code="module_remove.concurrent_change",
                    message=f"Module source changed before removal and was not deleted: {error}.",
                )
            ]
            blocked = True
            files = _module_remove_files(project.root, module_root, blocked=True)
    payload = _module_remove_payload(
        project,
        module=module,
        source_root=selected_source_root,
        root=module_root,
        diagnostics=diagnostics,
        blocked=blocked,
        removed=removed,
        files=files,
    )
    if removed:
        from paradev.hb import _sync_module_catalog_projection

        payload["catalog_mutation"] = _sync_module_catalog_projection(
            project,
            previous=module.to_dict(),
            _lock_held=catalog_lock_held,
        )
    if removal_quarantine is not None:
        removal_cleanup = _cleanup_module_quarantine(selected_source_root, removal_quarantine)
        if removal_cleanup.pending_path is not None:
            message = (
                "The module was removed, but ParaDev could not finish deleting its project-local quarantine copy. "
                f"You can remove it later after checking that no other process is using it: {removal_cleanup.error}."
            )
            diagnostics.append(
                _module_remove_diagnostic(
                    project.root,
                    removal_cleanup.pending_path,
                    code="module_remove.cleanup_pending",
                    message=message,
                    severity="warning",
                )
            )
            payload["diagnostics"] = diagnostics
            payload["cleanup"] = {
                "schema": "paradev.module.remove-cleanup.v1",
                "status": "pending",
                "code": "module_remove.cleanup_pending",
                "path": str(removal_cleanup.pending_path),
                "relative_path": _project_relative_path(project.root, removal_cleanup.pending_path),
                "message": message,
            }
    return payload


def _module_rename_payload(
    project: Project,
    *,
    previous_module: "Module",
    module: "Module",
    previous_root: Path,
    root: Path,
) -> dict[str, object]:
    return {
        "schema": MODULE_RENAME_SCHEMA,
        "project_id": project.project_id,
        "previous_module_id": previous_module.module_id,
        "module_id": module.module_id,
        "family": module.family,
        "previous_root": str(previous_root),
        "root": str(root),
        "previous_relative_path": _project_relative_path(project.root, previous_root),
        "relative_path": _project_relative_path(project.root, root),
        "content_rewritten": False,
        "module": module.to_dict(),
    }


def _module_remove_payload(
    project: Project,
    *,
    module: "Module",
    source_root: Path,
    root: Path,
    diagnostics: list[dict[str, object]],
    blocked: bool,
    removed: bool,
    files: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "schema": MODULE_REMOVE_SCHEMA,
        "project_id": project.project_id,
        "module_id": module.module_id,
        "family": module.family,
        "source_root": str(source_root),
        "root": str(root),
        "relative_path": _project_relative_path(project.root, root),
        "blocked": blocked,
        "removed": removed,
        "diagnostics": diagnostics,
        "files": files,
        "module": module.to_dict(),
    }


def _module_remove_location(
    project: Project,
    *,
    family: str,
    object_id: str,
    source_root: str | os.PathLike[str] | None,
) -> tuple[Path, Path]:
    roots = (_select_source_root(project.root, project.source_roots, source_root),) if source_root is not None else project.source_roots
    candidates = [(root, candidate) for root in roots for candidate in _module_remove_candidates(root, family=family, object_id=object_id)]
    module_id = f"{family}/{object_id}"
    if not candidates:
        raise ValueError(f"Unknown module: {module_id}.")
    if len(candidates) > 1:
        raise ValueError(f"Module {module_id} exists in multiple source roots. Pass source_root to choose one.")
    return candidates[0]


def _module_remove_candidates(source_root: Path, *, family: str, object_id: str) -> tuple[Path, ...]:
    modules_root = source_root / "modules"
    family_root = modules_root / family
    for component in (modules_root, family_root):
        if component.is_symlink():
            return (family_root / object_id,)
        if not component.exists():
            return ()
        if not component.is_dir():
            return (family_root / object_id,)
    try:
        children = tuple(family_root.iterdir())
    except OSError:
        return (family_root / object_id,)
    return tuple(
        sorted(
            (child for child in children if _project_browser_object_id_and_title(child.name)[0] == object_id and (child.is_symlink() or child.exists())),
            key=lambda child: child.name,
        )
    )


def _module_remove_diagnostics(
    project_root: Path,
    source_root: Path,
    module_root: Path,
    *,
    family: str,
    object_id: str,
) -> list[dict[str, object]]:
    modules_root = source_root / "modules"
    family_root = modules_root / family
    if module_root.parent != family_root or _project_browser_object_id_and_title(module_root.name)[0] != object_id:
        return [
            _module_remove_diagnostic(
                project_root,
                module_root,
                code="module_remove.path_not_canonical",
                message="Module source path is not a direct child of its configured source root and family.",
            )
        ]
    for component in (modules_root, family_root, module_root):
        if component.is_symlink():
            code = "module_remove.path_symlink" if component == module_root else "module_remove.path_component_symlink"
            return [
                _module_remove_diagnostic(
                    project_root,
                    component,
                    code=code,
                    message="Module removal cannot use a symbolic link or a path beneath one.",
                )
            ]
        if component.exists() and not component.is_dir():
            return [
                _module_remove_diagnostic(
                    project_root,
                    component,
                    code="module_remove.path_not_directory",
                    message="Module source path or one of its parent components is not a directory.",
                )
            ]
    return []


def _module_remove_diagnostic(
    project_root: Path,
    path: Path,
    *,
    code: str,
    message: str,
    severity: str = "error",
) -> dict[str, object]:
    return {
        "severity": severity,
        "code": code,
        "message": message,
        "path": str(path),
        "relative_path": _project_relative_path(project_root, path),
    }


def _raise_module_rename_path_error(
    project_root: Path,
    source_root: Path,
    module_root: Path,
    *,
    family: str,
    object_id: str,
) -> None:
    diagnostics = _module_remove_diagnostics(
        project_root,
        source_root,
        module_root,
        family=family,
        object_id=object_id,
    )
    if diagnostics:
        diagnostic = diagnostics[0]
        raise ValueError(f"Module rename path is unsafe: {diagnostic['message']} ({diagnostic['path']}).")


class _AnchoredModuleMutationUnavailable(OSError):
    """Raised when the host cannot guarantee no-follow folder mutation."""


_SHUTIL_RMTREE_SUPPORTS_DIR_FD = "dir_fd" in signature(shutil.rmtree).parameters


def _remove_directory_tree_at(parent_fd: int, name: str) -> None:
    """Remove one directory below an open parent without following links."""

    if _SHUTIL_RMTREE_SUPPORTS_DIR_FD:
        shutil.rmtree(name, dir_fd=parent_fd)
        return
    _remove_directory_tree_at_legacy(parent_fd, name)


def _remove_directory_tree_at_legacy(parent_fd: int, name: str) -> None:
    """Provide the descriptor-anchored deletion missing from Python 3.10."""

    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    child_fd = os.open(name, flags, dir_fd=parent_fd)
    opened = os.fstat(child_fd)
    try:
        linked = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not os.path.samestat(opened, linked):
            raise OSError(errno.ESTALE, "Directory changed while it was being opened", name)
        for child_name in os.listdir(child_fd):
            child = os.stat(child_name, dir_fd=child_fd, follow_symlinks=False)
            if stat.S_ISDIR(child.st_mode):
                if child.st_dev != opened.st_dev:
                    raise OSError(errno.EXDEV, "Directory tree crosses a filesystem boundary", child_name)
                _remove_directory_tree_at_legacy(child_fd, child_name)
            else:
                os.unlink(child_name, dir_fd=child_fd)
        linked = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not os.path.samestat(opened, linked):
            raise OSError(errno.ESTALE, "Directory changed before it could be removed", name)
    finally:
        _close_module_descriptor(child_fd)
    os.rmdir(name, dir_fd=parent_fd)


@dataclass(frozen=True, slots=True)
class _ModuleRemovalQuarantine:
    """Project-local tombstone created by an atomic canonical removal."""

    name: str
    path: Path


@dataclass(frozen=True, slots=True)
class _ModuleRemovalCleanup:
    """Best-effort deletion state for a quarantined module."""

    pending_path: Path | None = None
    error: str = ""


def _uses_win32_module_mutation_authority() -> bool:
    """Return whether folder mutations require the retained Win32 adapter."""

    return os.name == "nt"


def _rename_module_directory_win32(
    source_root: Path,
    *,
    family: str,
    source_name: str,
    target_name: str,
    target_object_id: str,
    container: Literal["modules", "collections"] = "modules",
    expected_source_identity: tuple[int, int] | None = None,
) -> None:
    """Dispatch one Registry-container rename through the Win32 adapter."""

    from paradev.sdk._module_fs_windows import (
        WindowsModuleMutationUnavailable,
        rename_module_directory_windows,
    )

    try:
        rename_module_directory_windows(
            source_root,
            family=family,
            source_name=source_name,
            target_name=target_name,
            target_object_id=target_object_id,
            container=container,
            expected_source_identity=expected_source_identity,
        )
    except WindowsModuleMutationUnavailable as error:
        raise _AnchoredModuleMutationUnavailable(str(error)) from error


def _remove_module_directory_win32(
    source_root: Path,
    *,
    family: str,
    module_name: str,
) -> _ModuleRemovalQuarantine:
    """Move one module to private trash through the Win32 adapter."""

    from paradev.sdk._module_fs_windows import (
        WindowsModuleMutationUnavailable,
        remove_module_directory_windows,
    )

    try:
        quarantine_name, quarantine_path = remove_module_directory_windows(
            source_root,
            family=family,
            module_name=module_name,
        )
    except WindowsModuleMutationUnavailable as error:
        raise _AnchoredModuleMutationUnavailable(str(error)) from error
    return _ModuleRemovalQuarantine(
        name=quarantine_name,
        path=quarantine_path,
    )


def _cleanup_module_quarantine_win32(
    source_root: Path,
    quarantine: _ModuleRemovalQuarantine,
) -> _ModuleRemovalCleanup:
    """Best-effort cleanup for one retained Win32 module quarantine."""

    from paradev.sdk._module_fs_windows import cleanup_module_quarantine_windows

    pending_path, error = cleanup_module_quarantine_windows(
        source_root,
        quarantine_name=quarantine.name,
        quarantine_path=quarantine.path,
    )
    return _ModuleRemovalCleanup(
        pending_path=pending_path,
        error=error,
    )


def _rename_module_directory(
    source_root: Path,
    *,
    family: str,
    source_name: str,
    target_name: str,
    target_object_id: str,
    container: Literal["modules", "collections"] = "modules",
    expected_source_identity: tuple[int, int] | None = None,
) -> None:
    """Rename one Registry-container folder without following replacements."""

    if _uses_win32_module_mutation_authority():
        rename_kwargs: dict[str, object] = {}
        if expected_source_identity is not None:
            rename_kwargs["expected_source_identity"] = expected_source_identity
        if container != "modules":
            rename_kwargs["container"] = container
        _rename_module_directory_win32(
            source_root,
            family=family,
            source_name=source_name,
            target_name=target_name,
            target_object_id=target_object_id,
            **rename_kwargs,
        )
        return
    if _supports_anchored_module_mutation():
        family_fd = (
            _open_module_family_fd(source_root, family)
            if container == "modules"
            else _open_registry_family_fd(
                source_root,
                family,
                container=container,
            )
        )
        try:
            source_entry = _require_module_directory_entry(family_fd, source_name)
            source_identity = (source_entry.st_dev, source_entry.st_ino)
            if expected_source_identity is not None and source_identity != expected_source_identity:
                raise OSError(
                    errno.EAGAIN,
                    f"Module rename source identity changed: {source_name}",
                )
            _require_no_module_directory_alias(
                family_fd,
                object_id=target_object_id,
                allowed_names=(source_name,),
            )
            _require_missing_module_entry(family_fd, target_name)
            os.rename(source_name, target_name, src_dir_fd=family_fd, dst_dir_fd=family_fd)
            try:
                _require_module_directory_identity(
                    family_fd,
                    target_name,
                    expected=source_identity,
                )
                _require_no_module_directory_alias(
                    family_fd,
                    object_id=target_object_id,
                    allowed_names=(target_name,),
                )
                _fsync_source_draft_directory(family_fd)
            except Exception as error:
                try:
                    _rollback_module_directory_rename(
                        family_fd,
                        source_name=source_name,
                        target_name=target_name,
                        expected=source_identity,
                    )
                except Exception as rollback_error:
                    raise OSError(
                        errno.EAGAIN,
                        f"Module rename changed concurrently and rollback was incomplete: {rollback_error}",
                    ) from error
                raise OSError(
                    errno.EAGAIN,
                    f"Module rename changed concurrently and was rolled back: {error}",
                ) from error
        finally:
            _close_module_descriptor(family_fd)
        return
    raise _AnchoredModuleMutationUnavailable("Safe descriptor-anchored module rename is unavailable on this platform")


def _module_directory_identity(
    source_root: Path,
    *,
    family: str,
    module_name: str,
    container: Literal["modules", "collections"] = "modules",
) -> tuple[int, int]:
    """Return one retained Registry-folder identity for transaction recovery."""

    if _uses_win32_module_mutation_authority():
        try:
            authority = Win32DirectoryAuthority.open(source_root, create=False)
        except (
            OSError,
            Win32FilesystemUnavailable,
            Win32UnsafePathError,
        ) as error:
            raise ValueError(f"Module rename source could not be retained safely: {source_root}.") from error
        try:
            metadata = authority.entry_metadata(
                (container, family, module_name),
            )
            if metadata is None or not metadata.is_directory:
                raise ValueError(f"Module rename source is not a directory: {module_name}.")
            return metadata.identity
        finally:
            authority.close()
    family_fd = (
        _open_module_family_fd(source_root, family)
        if container == "modules"
        else _open_registry_family_fd(
            source_root,
            family,
            container=container,
        )
    )
    try:
        metadata = _require_module_directory_entry(family_fd, module_name)
        return (metadata.st_dev, metadata.st_ino)
    finally:
        _close_module_descriptor(family_fd)


def _remove_module_directory(
    source_root: Path,
    *,
    family: str,
    module_name: str,
) -> _ModuleRemovalQuarantine:
    """Atomically move one canonical module into project-local quarantine."""

    if _uses_win32_module_mutation_authority():
        return _remove_module_directory_win32(
            source_root,
            family=family,
            module_name=module_name,
        )
    if _supports_anchored_module_mutation():
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        source_fd = os.open(source_root, flags)
        modules_fd: int | None = None
        family_fd: int | None = None
        quarantine_parent_fd: int | None = None
        quarantine_fd: int | None = None
        try:
            modules_fd = os.open("modules", flags, dir_fd=source_fd)
            family_fd = os.open(family, flags, dir_fd=modules_fd)
            quarantine_parent_fd = _open_or_create_module_directory(source_fd, ".paradev")
            quarantine_fd = _open_or_create_module_directory(quarantine_parent_fd, "module-trash")
        except BaseException:
            for descriptor in (
                quarantine_fd,
                quarantine_parent_fd,
                family_fd,
                modules_fd,
                source_fd,
            ):
                if isinstance(descriptor, int):
                    _close_module_descriptor(descriptor)
            raise
        assert modules_fd is not None
        assert family_fd is not None
        assert quarantine_parent_fd is not None
        assert quarantine_fd is not None
        quarantine_name = f"{family}-{module_name}-{uuid4().hex}"
        quarantine_path = source_root / ".paradev" / "module-trash" / quarantine_name
        try:
            _require_module_directory_entry(family_fd, module_name)
            _require_missing_module_entry(quarantine_fd, quarantine_name)
            os.rename(
                module_name,
                quarantine_name,
                src_dir_fd=family_fd,
                dst_dir_fd=quarantine_fd,
            )
        finally:
            for descriptor in (
                quarantine_fd,
                quarantine_parent_fd,
                family_fd,
                modules_fd,
                source_fd,
            ):
                _close_module_descriptor(descriptor)
        return _ModuleRemovalQuarantine(name=quarantine_name, path=quarantine_path)
    raise _AnchoredModuleMutationUnavailable("Safe descriptor-anchored module removal is unavailable on this platform")


def _cleanup_module_quarantine(source_root: Path, quarantine: _ModuleRemovalQuarantine) -> _ModuleRemovalCleanup:
    if _uses_win32_module_mutation_authority():
        return _cleanup_module_quarantine_win32(source_root, quarantine)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    source_fd: int | None = None
    quarantine_parent_fd: int | None = None
    quarantine_fd: int | None = None
    cleanup_error: Exception | None = None
    cleanup_pending = False
    try:
        source_fd = os.open(source_root, flags)
        quarantine_parent_fd = os.open(".paradev", flags, dir_fd=source_fd)
        quarantine_fd = os.open("module-trash", flags, dir_fd=quarantine_parent_fd)
        _remove_directory_tree_at(quarantine_fd, quarantine.name)
    except Exception as error:
        cleanup_error = error
        cleanup_pending = True
        if quarantine_fd is not None:
            try:
                os.stat(quarantine.name, dir_fd=quarantine_fd, follow_symlinks=False)
            except FileNotFoundError:
                cleanup_pending = False
            except OSError:
                pass
    finally:
        for descriptor in (quarantine_fd, quarantine_parent_fd, source_fd):
            if isinstance(descriptor, int):
                _close_module_descriptor(descriptor)
    if cleanup_error is None or not cleanup_pending:
        return _ModuleRemovalCleanup()
    return _ModuleRemovalCleanup(pending_path=quarantine.path, error=str(cleanup_error))


def _open_or_create_module_directory(parent_fd: int, name: str) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    try:
        os.mkdir(name, dir_fd=parent_fd)
    except FileExistsError:
        pass
    return os.open(name, flags, dir_fd=parent_fd)


def _supports_anchored_module_mutation() -> bool:
    return _ANCHORED_MODULE_MUTATION_SUPPORTED


def _open_registry_family_fd(
    source_root: Path,
    family: str,
    *,
    container: Literal["modules", "collections"],
) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    source_fd = os.open(source_root, flags)
    try:
        modules_fd = os.open(container, flags, dir_fd=source_fd)
    finally:
        _close_module_descriptor(source_fd)
    try:
        return os.open(family, flags, dir_fd=modules_fd)
    finally:
        _close_module_descriptor(modules_fd)


def _open_module_family_fd(source_root: Path, family: str) -> int:
    """Open one module-family folder through retained no-follow descriptors."""

    return _open_registry_family_fd(
        source_root,
        family,
        container="modules",
    )


def _close_module_descriptor(descriptor: int) -> None:
    """Release an anchor without masking the source operation's outcome."""

    try:
        os.close(descriptor)
    except OSError:
        pass


def _require_module_directory_entry(family_fd: int, name: str) -> os.stat_result:
    entry = os.stat(name, dir_fd=family_fd, follow_symlinks=False)
    if not stat.S_ISDIR(entry.st_mode):
        raise NotADirectoryError(f"Module entry is not a directory: {name}")
    return entry


def _require_module_directory_identity(
    family_fd: int,
    name: str,
    *,
    expected: tuple[int, int],
) -> None:
    entry = _require_module_directory_entry(family_fd, name)
    if (entry.st_dev, entry.st_ino) != expected:
        raise OSError(f"Module entry identity changed: {name}")


def _require_no_module_directory_alias(
    family_fd: int,
    *,
    object_id: str,
    allowed_names: Sequence[str] = (),
) -> None:
    """Reject case, Unicode, and display-title aliases for one logical module."""

    logical_key = _portable_module_directory_key(object_id)
    allowed = set(allowed_names)
    aliases = sorted(
        name
        for name in os.listdir(family_fd)
        if name not in allowed and _portable_module_directory_key(_project_browser_object_id_and_title(name)[0]) == logical_key
    )
    if aliases:
        raise FileExistsError(f"Module {object_id!r} has a conflicting physical folder: {', '.join(aliases)}.")


def _portable_module_directory_key(value: str) -> str:
    """Return the portable identity key for one logical module folder."""

    return unicodedata.normalize("NFC", value).casefold()


def _rollback_module_directory_rename(
    family_fd: int,
    *,
    source_name: str,
    target_name: str,
    expected: tuple[int, int],
) -> None:
    """Restore a renamed directory only while it retains the planned identity."""

    _require_missing_module_entry(family_fd, source_name)
    _require_module_directory_identity(family_fd, target_name, expected=expected)
    os.rename(target_name, source_name, src_dir_fd=family_fd, dst_dir_fd=family_fd)
    _require_module_directory_identity(family_fd, source_name, expected=expected)
    _fsync_source_draft_directory(family_fd)


def _require_missing_module_entry(family_fd: int, name: str) -> None:
    try:
        os.stat(name, dir_fd=family_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise FileExistsError(f"Module entry already exists: {name}")


def _renamed_module_record(
    module: "Module",
    *,
    module_id: str,
    previous_root: Path,
    root: Path,
) -> "Module":
    source_slots = {slot: tuple(_moved_module_source_path(path, previous_root, root) for path in paths) for slot, paths in module.source_slots.items()}
    return replace(module, module_id=module_id, root=root, source_slots=source_slots)


def _moved_module_source_path(path: str | os.PathLike[str], previous_root: Path, root: Path) -> Path:
    source = Path(path)
    try:
        return root / source.relative_to(previous_root)
    except ValueError:
        return source


def _module_remove_files(project_root: Path, module_root: Path, *, blocked: bool) -> list[dict[str, object]]:
    if blocked or not module_root.is_dir():
        return []
    return [
        _module_remove_file_view(project_root, module_root, path, blocked=blocked)
        for path in sorted(
            (item for item in module_root.rglob("*") if item.is_file()),
            key=lambda item: _project_relative_path(module_root, item),
        )
    ]


def _module_remove_file_view(project_root: Path, module_root: Path, path: Path, *, blocked: bool) -> dict[str, object]:
    return {
        "path": str(path),
        "relative_path": _project_relative_path(project_root, path),
        "module_relative_path": _project_relative_path(module_root, path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size,
        "will_remove": not blocked,
    }


def _module_file_payload(
    project: Project,
    *,
    module: "Module",
    path: Path,
    text: str,
    encoding: str,
    revision: os.stat_result | Win32FileMetadata | None = None,
    written: bool | None = None,
    created: bool | None = None,
    changed: bool | None = None,
) -> dict[str, object]:
    module_root = Path(module.root).expanduser().resolve()
    payload: dict[str, object] = {
        "schema": MODULE_FILE_SCHEMA,
        "project_id": project.project_id,
        "module_id": module.module_id,
        "family": module.family,
        "source_root": str(_module_source_root(project.root, project.source_roots, module_root)),
        "root": str(module_root),
        "path": str(path),
        "relative_path": _project_relative_path(project.root, path),
        "module_relative_path": _project_relative_path(module_root, path),
        "encoding": encoding,
        "exists": path.is_file(),
        "size_bytes": len(text.encode(encoding)),
        "text": text,
        "module": module.to_dict(),
    }
    if revision is not None:
        payload["size"] = revision.st_size
        payload["mtime_ns"] = str(revision.st_mtime_ns)
    if written is not None:
        payload["written"] = written
    if created is not None:
        payload["created"] = created
    if changed is not None:
        payload["changed"] = changed
    return payload


def _module_asset_slot_rows(
    module: "Module",
    module_relative_path: str,
    declarations: Sequence["Slot"],
) -> tuple[dict[str, object], ...]:
    """Return Registry slot rows that make one module source an asset."""

    module_root = Path(module.root).expanduser().resolve()
    matched_names: set[str] = set()
    for slot_name, source_paths in module.source_slots.items():
        for source_path in source_paths:
            candidate = Path(source_path)
            if candidate.is_absolute():
                try:
                    candidate_text = candidate.resolve().relative_to(module_root).as_posix()
                except (OSError, RuntimeError, ValueError):
                    continue
            else:
                candidate_text = candidate.as_posix()
            if candidate_text == module_relative_path:
                matched_names.add(str(slot_name))
                break
    if not matched_names:
        return ()

    declarations_by_name: dict[str, list["Slot"]] = {}
    for declaration in declarations:
        declarations_by_name.setdefault(declaration.name, []).append(declaration)
    image_source = Path(module_relative_path).suffix.casefold() in _MODULE_ASSET_IMAGE_SUFFIXES
    asset_names = {name for name in matched_names if image_source or any(declaration.kind == "copy" for declaration in declarations_by_name.get(name, ()))}
    return tuple(
        {
            "name": name,
            "kinds": sorted({declaration.kind for declaration in declarations_by_name.get(name, ()) if declaration.kind is not None}),
        }
        for name in sorted(asset_names)
    )


def _module_asset_payload(
    project: Project,
    *,
    module: "Module",
    path: Path,
    content: bytes,
    revision: os.stat_result | Win32FileMetadata,
    source_slots: Sequence[Mapping[str, object]],
    include_content: bool,
) -> dict[str, object]:
    """Return one JSON-safe Registry-owned module asset snapshot."""

    module_root = Path(module.root).expanduser().resolve()
    relative_path = _project_relative_path(project.root, path)
    payload: dict[str, object] = {
        "schema": MODULE_ASSET_SCHEMA,
        "project_id": project.project_id,
        "module_id": module.module_id,
        "family": module.family,
        "source_root": str(_module_source_root(project.root, project.source_roots, module_root)),
        "root": str(module_root),
        "path": str(path),
        "relative_path": relative_path,
        "module_relative_path": _project_relative_path(module_root, path),
        "file_format": path.suffix.casefold().removeprefix("."),
        "mime_type": _source_binary_mime_type(path),
        "source_slots": [dict(row) for row in source_slots],
        "size": revision.st_size,
        "mtime_ns": str(revision.st_mtime_ns),
        "sha256": hashlib.sha256(content).hexdigest(),
        "content_included": include_content,
        "draft_guard": {
            "path": relative_path,
            "expected_size": revision.st_size,
            "expected_mtime_ns": str(revision.st_mtime_ns),
        },
    }
    if include_content:
        payload["content_base64"] = base64.b64encode(content).decode("ascii")
    return payload


def _project_binary_source_payload(
    project: Project,
    *,
    path: Path,
    content: bytes,
    revision: os.stat_result | Win32FileMetadata,
    include_content: bool,
) -> dict[str, object]:
    """Return one JSON-safe project binary source snapshot."""

    relative_path = _project_relative_path(project.root, path)
    payload: dict[str, object] = {
        "schema": PROJECT_SOURCE_BINARY_SCHEMA,
        "project_id": project.project_id,
        "path": str(path),
        "relative_path": relative_path,
        "file_format": path.suffix.casefold().removeprefix("."),
        "mime_type": _source_binary_mime_type(path),
        "size": revision.st_size,
        "mtime_ns": str(revision.st_mtime_ns),
        "sha256": hashlib.sha256(content).hexdigest(),
        "content_included": include_content,
        "draft_guard": {
            "path": relative_path,
            "expected_size": revision.st_size,
            "expected_mtime_ns": str(revision.st_mtime_ns),
        },
    }
    if include_content:
        payload["content_base64"] = base64.b64encode(content).decode("ascii")
    return payload


def _source_binary_mime_type(path: str | os.PathLike[str]) -> str:
    """Return the deterministic MIME type for one binary source path."""

    return _SOURCE_BINARY_MIME_TYPES.get(
        Path(path).suffix.casefold(),
        "application/octet-stream",
    )


def _module_file_edit_rows(
    project: Project,
    edits: Sequence[Mapping[str, object]],
    *,
    create: bool,
    encoding: str,
) -> tuple[dict[str, object], ...]:
    if not isinstance(edits, Sequence) or isinstance(edits, str | bytes):
        raise ValueError("Module file edits must be an array.")
    if not edits:
        raise ValueError("Module file edits must include at least one edit.")
    default_create = _bool_value(create)
    default_encoding = _module_file_edit_encoding(encoding, "encoding")
    rows: list[dict[str, object]] = []
    targets: dict[Path, int] = {}
    for index, edit in enumerate(edits):
        if not isinstance(edit, Mapping):
            raise ValueError(f"Module file edit {index} must be an object.")
        text = edit.get("text")
        if not isinstance(text, str):
            raise ValueError(f"Module file edit {index} text must be a string.")
        source_root = edit.get("source_root")
        if source_root is not None and not isinstance(source_root, (str, os.PathLike)):
            raise ValueError(f"Module file edit {index} source_root must be a path string.")
        item_create = _module_file_edit_create(edit.get("create"), default_create, index)
        item_encoding = _module_file_edit_encoding(edit.get("encoding", default_encoding), f"edits[{index}].encoding")
        module = _find_project_module(project, edit.get("module_id"), source_root=source_root)
        path = _module_file_path(module, edit.get("relative_path"))
        _validate_module_file_edit_target(project, path, text, create=item_create, encoding=item_encoding, index=index)
        created = not path.exists()
        changed = created or path.read_bytes() != text.encode(item_encoding)
        previous_index = targets.get(path)
        if previous_index is not None:
            relative_path = _project_relative_path(project.root, path)
            raise ValueError(f"Module file edit {index} duplicates edit {previous_index}: {relative_path}.")
        targets[path] = index
        rows.append(
            {
                "module": module,
                "path": path,
                "text": text,
                "encoding": item_encoding,
                "created": created,
                "changed": changed,
            }
        )
    return tuple(rows)


def _module_batch_edit_request_payload(
    project: Project,
    edits: Sequence[Mapping[str, object]],
    *,
    create: bool,
    encoding: str,
) -> dict[str, object]:
    if not isinstance(edits, Sequence) or isinstance(edits, str | bytes):
        raise ValueError("Module batch edit request edits must be an array.")
    if not edits:
        raise ValueError("Module batch edit request edits must include at least one edit.")
    default_create = _bool_value(create)
    default_encoding = _module_file_edit_encoding(encoding, "encoding")
    rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    targets: dict[tuple[str, str, str], int] = {}
    module_ids: set[str] = set()
    source_roots: set[str] = set()
    encodings: set[str] = set()
    existing_target_count = 0
    missing_target_count = 0
    changed_target_count = 0
    unchanged_target_count = 0
    create_enabled_count = 0
    for index, edit in enumerate(edits):
        if not isinstance(edit, Mapping):
            raise ValueError(f"Module batch edit request edit {index} must be an object.")
        module_id = "/".join(_module_id_parts(edit.get("module_id")))
        relative_path = _module_file_edit_relative_path(edit.get("relative_path"), index)
        text = edit.get("text")
        if not isinstance(text, str):
            raise ValueError(f"Module batch edit request edit {index} text must be a string.")
        source_root = _module_file_edit_source_root(edit.get("source_root"), index)
        module = _find_project_module(project, module_id, source_root=source_root)
        path = _module_file_path(module, relative_path)
        item_create = _module_file_edit_create(edit.get("create"), default_create, index)
        item_encoding = _module_file_edit_encoding(edit.get("encoding", default_encoding), f"edits[{index}].encoding")
        _validate_module_file_edit_target(project, path, text, create=item_create, encoding=item_encoding, index=index)
        target_changed = not path.exists() or path.read_bytes() != text.encode(item_encoding)
        target_created = not path.exists()
        if target_changed:
            changed_target_count += 1
        else:
            unchanged_target_count += 1
        if path.exists():
            existing_target_count += 1
        else:
            missing_target_count += 1
        if item_create:
            create_enabled_count += 1
        module_ids.add(module_id)
        if source_root is not None:
            source_roots.add(source_root)
        encodings.add(item_encoding)
        target_key = (module_id, source_root or "", relative_path)
        previous_index = targets.get(target_key)
        if previous_index is not None:
            raise ValueError(f"Module batch edit request edit {index} duplicates edit {previous_index}: {module_id}/{relative_path}.")
        targets[target_key] = index
        row: dict[str, object] = {
            "module_id": module_id,
            "relative_path": relative_path,
            "text": text,
        }
        if source_root is not None:
            row["source_root"] = source_root
        if "create" in edit:
            row["create"] = item_create
        if "encoding" in edit:
            row["encoding"] = item_encoding
        rows.append(row)
        target_rows.append(
            {
                "edit_index": index,
                "module_id": module_id,
                "family": module.family,
                "object_id": module_id.rsplit("/", 1)[-1],
                "relative_path": relative_path,
                "target_relative_path": _project_relative_path(project.root, path),
                "exists": not target_created,
                "created": target_created,
                "changed": target_changed,
                "create": item_create,
                "encoding": item_encoding,
                "size_bytes": len(text.encode(item_encoding)),
            }
        )
        if source_root is not None:
            target_rows[-1]["source_root"] = source_root
    return {
        "schema": MODULE_BATCH_EDIT_REQUEST_SCHEMA,
        "project_id": project.project_id,
        "create": default_create,
        "encoding": default_encoding,
        "edit_count": len(rows),
        "summary": {
            "edit_count": len(rows),
            "module_count": len(module_ids),
            "source_root_count": len(source_roots),
            "existing_target_count": existing_target_count,
            "missing_target_count": missing_target_count,
            "changed_target_count": changed_target_count,
            "unchanged_target_count": unchanged_target_count,
            "create_enabled_count": create_enabled_count,
            "encoding_count": len(encodings),
        },
        "edits": rows,
        "index": _module_batch_edit_request_index(rows),
        "targets": target_rows,
        "target_index": _module_batch_edit_request_target_index(target_rows),
    }


def _module_file_edit_relative_path(value: object, index: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Module batch edit request edit {index} relative_path must be a non-empty relative path.")
    text = value.strip()
    if "\\" in text:
        raise ValueError(f"Module batch edit request edit {index} relative_path must use forward slashes.")
    candidate = Path(text)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"Module batch edit request edit {index} relative_path must stay inside module root.")
    return candidate.as_posix()


def _module_file_edit_source_root(value: object, index: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, (str, os.PathLike)):
        raise ValueError(f"Module batch edit request edit {index} source_root must be a path string.")
    source_root = os.fspath(value)
    if not isinstance(source_root, str):
        raise ValueError(f"Module batch edit request edit {index} source_root must be a path string.")
    text = source_root.strip()
    if not text:
        raise ValueError(f"Module batch edit request edit {index} source_root must be a non-empty path string.")
    return text


def _module_file_edit_create(value: object, default: bool, index: int) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return _bool_value(value)
    raise ValueError(f"Module file edit {index} create must be a boolean.")


def _module_file_edit_encoding(value: object, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Module file edit {key} must be a non-empty string.")
    return value.strip()


def _validate_module_file_edit_target(project: Project, path: Path, text: str, *, create: bool, encoding: str, index: int) -> None:
    if path.exists() and not path.is_file():
        raise ValueError(f"Module file path is not a file: {_project_relative_path(project.root, path)}.")
    if not path.exists() and not create:
        raise ValueError(f"Module file does not exist: {_project_relative_path(project.root, path)}. Pass create=True to create it.")
    _validate_module_file_edit_text(text, encoding, index)


def _validate_module_file_edit_text(text: str, encoding: str, index: int) -> None:
    try:
        text.encode(encoding)
    except LookupError as error:
        raise ValueError(f"Module file edit {index} encoding is unknown: {encoding}.") from error
    except UnicodeEncodeError as error:
        raise ValueError(f"Module file edit {index} text cannot be encoded with {encoding}.") from error


def _module_batch_edit_payload(project: Project, files: Sequence[Mapping[str, object]], *, written: bool) -> dict[str, object]:
    created_count = sum(1 for row in files if row.get("created") is True)
    changed_count = sum(1 for row in files if row.get("changed") is True)
    return {
        "schema": MODULE_BATCH_EDIT_SCHEMA,
        "project_id": project.project_id,
        "written": written,
        "file_count": len(files),
        "created_count": created_count,
        "updated_count": len(files) - created_count,
        "changed_count": changed_count,
        "unchanged_count": len(files) - changed_count,
        "files": list(files),
        "index": _module_batch_edit_index(files),
    }


def _module_batch_edit_index(
    files: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {
        "module_id": {},
        "family": {},
        "relative_path": {},
        "module_relative_path": {},
    }
    for row_index, row in enumerate(files):
        for key, bucket in index.items():
            value = row.get(key)
            if isinstance(value, str) and value:
                append_index_entry(bucket, value, row_index)
    return {key: {bucket_key: bucket[bucket_key] for bucket_key in sorted(bucket)} for key, bucket in index.items() if bucket}


def _module_batch_edit_request_index(
    edits: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {
        "module_id": {},
        "relative_path": {},
        "source_root": {},
    }
    for row_index, row in enumerate(edits):
        for key, bucket in index.items():
            value = row.get(key)
            if isinstance(value, str) and value:
                append_index_entry(bucket, value, row_index)
    return {key: {bucket_key: bucket[bucket_key] for bucket_key in sorted(bucket)} for key, bucket in index.items() if bucket}


def _module_batch_edit_request_target_index(
    targets: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {
        "module_id": {},
        "family": {},
        "relative_path": {},
        "target_relative_path": {},
        "source_root": {},
        "created": {},
        "changed": {},
    }
    for row_index, row in enumerate(targets):
        for key, bucket in index.items():
            value = row.get(key)
            if isinstance(value, str) and value:
                append_index_entry(bucket, value, row_index)
            elif isinstance(value, bool):
                append_index_entry(bucket, str(value).lower(), row_index)
    return {key: {bucket_key: bucket[bucket_key] for bucket_key in sorted(bucket)} for key, bucket in index.items() if bucket}


def _collection_file_payload(
    project: Project,
    *,
    collection: "Collection",
    path: Path,
    text: str,
    encoding: str,
    revision: os.stat_result | Win32FileMetadata | None = None,
    written: bool | None = None,
) -> dict[str, object]:
    collection_root = _collection_root(collection)
    payload: dict[str, object] = {
        "schema": COLLECTION_FILE_SCHEMA,
        "project_id": project.project_id,
        "collection_id": collection.collection_id,
        "family": collection.family,
        "source_root": str(_collection_source_root(project.root, project.source_roots, collection_root)),
        "root": str(collection_root),
        "path": str(path),
        "relative_path": _project_relative_path(project.root, path),
        "collection_relative_path": _project_relative_path(collection_root, path),
        "encoding": encoding,
        "exists": path.is_file(),
        "size_bytes": len(text.encode(encoding)),
        "text": text,
        "collection": collection.to_dict(),
    }
    if revision is not None:
        payload["size"] = revision.st_size
        payload["mtime_ns"] = str(revision.st_mtime_ns)
    if written is not None:
        payload["written"] = written
    return payload


def _collection_rename_payload(
    project: Project,
    *,
    previous_collection: "Collection",
    collection: "Collection",
    previous_root: Path,
    root: Path,
    members: Sequence["Module"] = (),
    files: Sequence[Mapping[str, object]] = (),
) -> dict[str, object]:
    return {
        "schema": COLLECTION_RENAME_SCHEMA,
        "project_id": project.project_id,
        "previous_collection_id": previous_collection.collection_id,
        "collection_id": collection.collection_id,
        "family": collection.family,
        "source_root": str(_collection_source_root(project.root, project.source_roots, root)),
        "previous_root": str(previous_root),
        "root": str(root),
        "previous_relative_path": _project_relative_path(project.root, previous_root),
        "relative_path": _project_relative_path(project.root, root),
        "content_rewritten": bool(files),
        "member_count": len(members),
        "members": [module.module_id for module in members],
        "files": [dict(file) for file in files],
        "collection": collection.to_dict(),
    }


def _collection_create_payload(
    project: Project,
    *,
    authoring_path: Mapping[str, object],
    metadata_path: Path,
    metadata: Mapping[str, object],
    diagnostics: list[dict[str, object]],
    blocked: bool,
    written: bool,
    force: bool,
    authoring_plan: dict[str, object],
) -> dict[str, object]:
    root = Path(str(authoring_path["root"]))
    return {
        "schema": COLLECTION_CREATE_SCHEMA,
        "project_id": project.project_id,
        "family": str(authoring_path["family"]),
        "collection_id": str(authoring_path["collection_id"]),
        "source_root": str(authoring_path["source_root"]),
        "root": str(root),
        "relative_path": str(authoring_path["relative_path"]),
        "metadata": dict(metadata),
        "blocked": blocked,
        "written": written,
        "diagnostics": diagnostics,
        "files": [_collection_create_file_view(project.root, root, metadata_path, blocked=blocked, force=force)],
        "authoring_plan": authoring_plan,
    }


def _collection_create_file_view(
    project_root: Path,
    collection_root: Path,
    path: Path,
    *,
    blocked: bool,
    force: bool,
) -> dict[str, object]:
    return {
        "role": "metadata",
        "path": str(path),
        "relative_path": _project_relative_path(project_root, path),
        "collection_relative_path": _project_relative_path(collection_root, path),
        "exists": path.exists(),
        "will_write": not blocked,
        "force": force,
    }


def _collection_create_metadata(
    metadata: Mapping[str, object] | None,
) -> dict[str, object]:
    if metadata is None:
        return {}
    if not isinstance(metadata, Mapping):
        raise ValueError("Collection metadata must be a mapping.")
    payload: dict[str, object] = {}
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Collection metadata keys must be non-empty strings.")
        payload[key.strip()] = value
    return payload


def _collection_create_diagnostics(
    project_root: Path,
    root: Path,
    metadata_path: Path,
    *,
    force: bool,
) -> list[dict[str, object]]:
    for candidate in _collection_create_path_candidates(root, project_root):
        if candidate.exists() and not candidate.is_dir():
            message = "Collection descriptor path exists and is not a directory."
            if candidate != root:
                message = "Collection descriptor path ancestor exists and is not a directory."
            return [
                {
                    "severity": "error",
                    "code": "collection_create.path_not_directory",
                    "message": message,
                    "path": str(candidate),
                    "relative_path": _project_relative_path(project_root, candidate),
                }
            ]
    if metadata_path.exists() and not force:
        return [
            {
                "severity": "error",
                "code": "collection_create.file_exists",
                "message": "Collection metadata file already exists.",
                "path": str(metadata_path),
                "relative_path": _project_relative_path(project_root, metadata_path),
            }
        ]
    return []


def _collection_create_path_candidates(root: Path, project_root: Path) -> tuple[Path, ...]:
    candidates: list[Path] = []
    for candidate in (root, *root.parents):
        candidates.append(candidate)
        if candidate == project_root:
            break
    return tuple(candidates)


def _collection_remove_payload(
    project: Project,
    *,
    collection: "Collection",
    source_root: Path,
    root: Path,
    diagnostics: list[dict[str, object]],
    blocked: bool,
    removed: bool,
    files: list[dict[str, object]],
    members: Sequence["Module"],
    member_files: Sequence[Mapping[str, object]],
    plan_hash: str,
    write: bool,
) -> dict[str, object]:
    return {
        "schema": COLLECTION_REMOVE_SCHEMA,
        "project_id": project.project_id,
        "collection_id": collection.collection_id,
        "family": collection.family,
        "source_root": str(source_root),
        "root": str(root),
        "relative_path": _project_relative_path(project.root, root),
        "status": "blocked" if blocked else "removed" if removed else "planned",
        "write": write,
        "blocked": blocked,
        "applied": removed,
        "written": removed,
        "removed": removed,
        "plan_hash": plan_hash,
        "diagnostics": diagnostics,
        "files": files,
        "members": [module.module_id for module in members],
        "member_files": [dict(item) for item in member_files],
        "counts": {
            "members_preserved": len(members),
            "member_metadata_files": len(member_files),
            "descriptor_files": len(files),
        },
        "collection": collection.to_dict(),
    }


def _collection_remove_diagnostics(project_root: Path, collection_root: Path) -> list[dict[str, object]]:
    try:
        metadata = collection_root.lstat()
    except FileNotFoundError:
        metadata = None
    if metadata is not None and not stat.S_ISDIR(metadata.st_mode):
        return [
            {
                "severity": "error",
                "code": "collection_remove.path_not_directory",
                "message": "Collection descriptor path exists and is not a directory.",
                "path": str(collection_root),
                "relative_path": _project_relative_path(project_root, collection_root),
            }
        ]
    return []


def _collection_remove_files(project_root: Path, collection_root: Path, *, blocked: bool) -> list[dict[str, object]]:
    try:
        root_metadata = collection_root.lstat()
    except FileNotFoundError:
        return []
    if not stat.S_ISDIR(root_metadata.st_mode):
        return []
    files: list[dict[str, object]] = []
    for current_root, directory_names, file_names in os.walk(
        collection_root,
        topdown=True,
        followlinks=False,
    ):
        directory_names.sort()
        file_names.sort()
        current = Path(current_root)
        for directory_name in directory_names:
            directory = current / directory_name
            metadata = directory.lstat()
            if not stat.S_ISDIR(metadata.st_mode):
                raise ValueError("Collection removal cannot traverse a symlink or special " f"directory entry: {directory}.")
        for file_name in file_names:
            path = current / file_name
            files.append(
                _collection_remove_file_view(
                    project_root,
                    collection_root,
                    path,
                    blocked=blocked,
                )
            )
    return sorted(
        files,
        key=lambda item: str(item["collection_relative_path"]),
    )


def _collection_remove_file_view(project_root: Path, collection_root: Path, path: Path, *, blocked: bool) -> dict[str, object]:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"Collection removal cannot include a symlink or special file: {path}.")
    if _uses_win32_module_mutation_authority():
        try:
            authority = Win32DirectoryAuthority.open(collection_root, create=False)
        except (
            OSError,
            Win32FilesystemUnavailable,
            Win32UnsafePathError,
        ) as error:
            raise ValueError(f"Collection descriptor could not be retained safely: {path}.") from error
        try:
            relative_parts = tuple(path.relative_to(collection_root).parts)
            snapshot = authority.read_file_snapshot(relative_parts)
        finally:
            authority.close()
        if snapshot is None or snapshot.metadata.is_directory or snapshot.content_sha256 is None:
            raise ValueError(f"Collection descriptor file changed during planning: {path}.")
        return {
            "path": str(path),
            "relative_path": _project_relative_path(project_root, path),
            "collection_relative_path": _project_relative_path(collection_root, path),
            "exists": True,
            "size_bytes": snapshot.metadata.size,
            "mtime_ns": str(snapshot.metadata.mtime_ns),
            "mode": stat.S_IMODE(metadata.st_mode),
            "sha256": snapshot.content_sha256,
            "will_remove": not blocked,
        }
    descriptor = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        opened = os.fstat(descriptor)
        identity = (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
        expected = (
            metadata.st_dev,
            metadata.st_ino,
            metadata.st_size,
            metadata.st_mtime_ns,
        )
        if identity != expected or not stat.S_ISREG(opened.st_mode):
            raise ValueError(f"Collection descriptor file changed during planning: {path}.")
        digest = hashlib.sha256()
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
        after = os.fstat(descriptor)
        if (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ) != identity:
            raise ValueError(f"Collection descriptor file changed during planning: {path}.")
    finally:
        _close_module_descriptor(descriptor)
    return {
        "path": str(path),
        "relative_path": _project_relative_path(project_root, path),
        "collection_relative_path": _project_relative_path(collection_root, path),
        "exists": True,
        "size_bytes": metadata.st_size,
        "mtime_ns": str(metadata.st_mtime_ns),
        "mode": stat.S_IMODE(metadata.st_mode),
        "sha256": digest.hexdigest(),
        "will_remove": not blocked,
    }


def _collection_remove_inventory_digest(
    files: Sequence[Mapping[str, object]],
) -> str:
    """Hash one canonical collection descriptor file inventory."""

    canonical = [
        {
            key: row.get(key)
            for key in (
                "collection_relative_path",
                "size_bytes",
                "mtime_ns",
                "mode",
                "sha256",
            )
        }
        for row in files
    ]
    return sha256hash(
        dumps_json(
            canonical,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            compact=True,
            adapt=False,
        )
    )


def _collection_remove_plan_hash(
    project: Project,
    *,
    collection: "Collection",
    source_root: Path,
    root: Path,
    files: Sequence[Mapping[str, object]],
    members: Sequence["Module"],
    member_files: Sequence[Mapping[str, object]],
    edits: Sequence[Mapping[str, object]],
    removals: Sequence[Mapping[str, object]],
) -> str:
    """Hash exact descriptor and member-metadata removal revisions."""

    mutations: list[dict[str, object]] = []
    for operation, rows in (("edit", edits), ("remove", removals)):
        for row in rows:
            path = row.get("path")
            if not isinstance(path, Path):
                raise ValueError("Collection removal mutation has no retained path.")
            mutation: dict[str, object] = {
                "operation": operation,
                "path": str(path),
                "expected_revision": row.get("expected_revision"),
            }
            text = row.get("text")
            if isinstance(text, str):
                mutation["after_sha256"] = sha256hash(text.encode("utf-8"))
            mutations.append(mutation)
    canonical = {
        "schema": COLLECTION_REMOVE_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "project_root_identity": _module_create_path_identity(project.root),
        "collection_id": collection.collection_id,
        "family": collection.family,
        "source_root": str(source_root),
        "source_root_identity": _module_create_path_identity(source_root),
        "root": str(root),
        "root_identity": _module_create_path_identity(root),
        "inventory_digest": _collection_remove_inventory_digest(files),
        "members": [
            {
                "module_id": module.module_id,
                "root": str(Path(module.root).expanduser().resolve()),
                "collection_id": module.collection_id,
            }
            for module in members
        ],
        "member_files": [dict(row) for row in member_files],
        "mutations": mutations,
    }
    return sha256hash(
        dumps_json(
            canonical,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            compact=True,
            adapt=False,
        )
    )


def _find_project_module(
    project: Project,
    module_id: str,
    *,
    source_root: str | os.PathLike[str] | None = None,
) -> "Module":
    clean_module_id = "/".join(_module_id_parts(module_id))
    selected_source_root = _select_source_root(project.root, project.source_roots, source_root) if source_root is not None else None
    matches = []
    for module in project.discover_modules(module_id=clean_module_id).modules:
        if module.module_id != clean_module_id:
            continue
        module_root = Path(module.root).expanduser().resolve()
        if selected_source_root is not None and _module_source_root(project.root, project.source_roots, module_root) != selected_source_root:
            continue
        matches.append(module)
    if not matches:
        raise ValueError(f"Unknown module: {clean_module_id}.")
    if len(matches) > 1:
        raise ValueError(f"Module {clean_module_id} exists in multiple source roots. Pass source_root to choose one.")
    return matches[0]


def _project_localization_sources(
    project: Project,
    target_id: str,
    *,
    target_kind: Literal["module", "collection"],
    family: str | None,
    source_root: str | os.PathLike[str] | None,
    drafts: Mapping[str, str] | None,
) -> tuple[dict[str, str], tuple[LocalizationSource, ...], Path]:
    if target_kind == "module":
        module = _find_project_module(project, target_id, source_root=source_root)
        unit_root = Path(module.root).expanduser().resolve()
        selected_source_root = _module_source_root(
            project.root,
            project.source_roots,
            unit_root,
        )
        target_family, object_id = _module_id_parts(module.module_id)
        if family is not None and _module_path_token(family, "family") != target_family:
            raise ValueError(f"Module {module.module_id!r} does not belong to family {family!r}.")
        canonical_target_id = module.module_id
        source_slots = module.source_slots
    elif target_kind == "collection":
        collection = _find_project_collection(
            project,
            target_id,
            family=family,
            source_root=source_root,
        )
        unit_root = _collection_root(collection)
        selected_source_root = _collection_source_root(
            project.root,
            project.source_roots,
            unit_root,
        )
        target_family = collection.family
        object_id = collection.collection_id
        canonical_target_id = collection.collection_id
        source_slots = collection.source_slots
    else:
        raise ValueError("Localization target_kind must be 'module' or 'collection'.")

    registry = project._build_registry(profile=project.game)
    loc_slots = tuple(slot for slot in registry.source_slots_for(target_family) if getattr(slot, "kind", None) == "loc")
    owned: list[tuple[str, Path, str]] = []
    seen_paths: set[Path] = set()
    for slot in loc_slots:
        slot_name = getattr(slot, "name", None)
        if not isinstance(slot_name, str) or not slot_name:
            raise ValueError(f"Build family {target_family!r} has an invalid localization slot name.")
        for raw_path in source_slots.get(slot_name, ()):
            try:
                relative_path = Path(os.fspath(raw_path))
            except TypeError as error:
                raise ValueError(f"Localization slot {slot_name!r} contains a non-path source.") from error
            path = relative_path if relative_path.is_absolute() else unit_root / relative_path
            path = path.expanduser().resolve()
            try:
                unit_relative_path = path.relative_to(unit_root).as_posix()
            except ValueError as error:
                raise ValueError(f"Localization slot {slot_name!r} resolves outside " f"{target_kind} {canonical_target_id!r}.") from error
            if path in seen_paths:
                continue
            matched = match_slot_paths(
                (unit_relative_path,),
                loc_slots,
                module_id=f"{target_kind}/{canonical_target_id}",
            )
            if not any(unit_relative_path in paths for paths in matched.source_slots.values()):
                raise ValueError(f"Localization source {unit_relative_path!r} is not owned by " f"the active Registry family {target_family!r}.")
            seen_paths.add(path)
            owned.append((slot_name, path, unit_relative_path))

    draft_texts: dict[Path, str] = {}
    if drafts is not None:
        if not isinstance(drafts, Mapping):
            raise ValueError("Localization drafts must be an object keyed by source path.")
        for raw_path, text in drafts.items():
            if not isinstance(raw_path, str) or not raw_path.strip():
                raise ValueError("Localization draft paths must be non-empty strings.")
            if not isinstance(text, str):
                raise ValueError(f"Localization draft {raw_path!r} must contain text.")
            path = _project_source_path(project.root, raw_path, reject_symlinks=True)
            if path not in seen_paths:
                raise ValueError(f"Localization draft {raw_path!r} is not owned by " f"{target_kind} {canonical_target_id!r}.")
            if path in draft_texts:
                raise ValueError(f"Localization draft path is repeated: {raw_path!r}.")
            _validate_source_draft_text(project, path, text)
            draft_texts[path] = text

    sources: list[LocalizationSource] = []
    for slot_name, path, unit_relative_path in owned:
        snapshot = project.read_source_text(path)
        disk_text = snapshot.get("text")
        size = snapshot.get("size")
        mtime_ns = snapshot.get("mtime_ns")
        if not isinstance(disk_text, str) or isinstance(size, bool) or not isinstance(size, int) or not isinstance(mtime_ns, str):
            raise ValueError(f"Localization source snapshot is incomplete: {path}.")
        sources.append(
            LocalizationSource(
                path=str(path),
                relative_path=str(snapshot["relative_path"]),
                unit_relative_path=unit_relative_path,
                slot=slot_name,
                text=draft_texts.get(path, disk_text),
                size=size,
                mtime_ns=mtime_ns,
            )
        )
    return (
        {
            "kind": target_kind,
            "id": canonical_target_id,
            "family": target_family,
            "object_id": object_id,
        },
        tuple(sources),
        selected_source_root,
    )


def _find_project_collection(
    project: Project,
    collection_id: str,
    *,
    family: str | None = None,
    source_root: str | os.PathLike[str] | None = None,
) -> "Collection":
    clean_collection_id = _collection_id_token(collection_id)
    clean_family = _module_path_token(family, "family") if family is not None else None
    selected_source_root = _select_source_root(project.root, project.source_roots, source_root) if source_root is not None else None
    matches = []
    for collection in project.discover_collections().collections:
        if collection.collection_id != clean_collection_id:
            continue
        collection_root = _collection_root(collection)
        if clean_family is not None and collection.family != clean_family:
            continue
        if selected_source_root is not None and _collection_source_root(project.root, project.source_roots, collection_root) != selected_source_root:
            continue
        matches.append(collection)
    if not matches:
        raise ValueError(f"Unknown collection: {clean_collection_id}.")
    if len(matches) > 1:
        raise ValueError(f"Collection {clean_collection_id} is ambiguous. Pass family or source_root to choose one.")
    return matches[0]


def _module_file_path(module: "Module", relative_path: object) -> Path:
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("Module file path must be a non-empty relative path.")
    text = relative_path.strip()
    if "\\" in text:
        raise ValueError("Module file path must use forward slashes.")
    candidate = Path(text)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError("Module file path must stay inside module root.")
    module_root = Path(module.root).expanduser().resolve()
    path = (module_root / candidate).resolve()
    try:
        path.relative_to(module_root)
    except ValueError as error:
        raise ValueError("Module file path must stay inside module root.") from error
    if path == module_root:
        raise ValueError("Module file path must point to a file inside module root.")
    return path


def _collection_file_path(collection: "Collection", relative_path: object) -> Path:
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("Collection file path must be a non-empty relative path.")
    text = relative_path.strip()
    if "\\" in text:
        raise ValueError("Collection file path must use forward slashes.")
    candidate = Path(text)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError("Collection file path must stay inside collection root.")
    collection_root = _collection_root(collection)
    path = (collection_root / candidate).resolve()
    try:
        path.relative_to(collection_root)
    except ValueError as error:
        raise ValueError("Collection file path must stay inside collection root.") from error
    if path == collection_root:
        raise ValueError("Collection file path must point to a file inside collection root.")
    return path


def _required_path_text(value: object, name: str) -> str:
    if isinstance(value, os.PathLike):
        text = os.fspath(value)
    elif isinstance(value, str):
        text = value
    else:
        raise ValueError(f"Request field {name!r} must be a non-empty string.")
    if not text.strip():
        raise ValueError(f"Request field {name!r} must be a non-empty string.")
    return text.strip()


def _project_source_path(
    project_root: Path,
    source_path: str,
    *,
    must_exist: bool = True,
    reject_symlinks: bool = False,
) -> Path:
    try:
        root = project_root.expanduser().resolve()
    except (OSError, RuntimeError) as error:
        raise ValueError(f"Source project root could not be resolved safely: {project_root}.") from error
    path = Path(source_path).expanduser()
    lexical = Path(os.path.abspath(path if path.is_absolute() else root / path))
    alias_suffix = _project_root_alias_suffix(root, lexical)
    try:
        candidate = (root / alias_suffix if alias_suffix is not None else lexical).resolve()
    except (OSError, RuntimeError) as error:
        raise ValueError(f"Source path could not be resolved safely: {lexical}.") from error
    try:
        candidate.relative_to(root)
    except ValueError:
        resolved_alias_suffix = _project_root_alias_suffix(root, candidate)
        if resolved_alias_suffix is None:
            raise ValueError("Source path is outside the project root.") from None
        candidate = root / resolved_alias_suffix
    if reject_symlinks:
        _validate_source_draft_symlink_path(root, lexical)
    if must_exist and not candidate.exists():
        raise ValueError(f"Source path does not exist: {candidate}")
    if not must_exist and not candidate.exists() and not candidate.parent.is_dir():
        raise ValueError(f"Source path parent does not exist: {candidate.parent}")
    return candidate


def _read_project_source_snapshot(
    project_root: Path,
    path: Path,
    *,
    max_bytes: int = MAX_PROJECT_SOURCE_TEXT_BYTES,
) -> tuple[bytes, os.stat_result | Win32FileMetadata]:
    """Read one regular source and return a revision from the same stable file."""

    if max_bytes <= 0:
        raise ValueError("Source snapshot byte limit must be greater than zero.")

    if _uses_win32_source_draft_authority():
        root, root_identity = _source_draft_root_identity(project_root)
        parts = _win32_source_draft_parts(root, path)
        try:
            with _open_win32_source_draft_authority(root, root_identity=root_identity) as authority:
                snapshot = authority.read_file_snapshot(
                    parts,
                    max_bytes=max_bytes,
                )
        except Win32FileSizeError as error:
            raise ValueError(f"Source file is larger than {max_bytes} bytes: {path}") from error
        except Win32UnsafePathError as error:
            raise ValueError(f"Source file changed before it could be read: {path}") from error
        except OSError as error:
            raise ValueError(f"Source file changed before it could be read: {path}") from error
        if snapshot is None:
            raise ValueError(f"Source file changed before it could be read: {path}")
        if snapshot.metadata.is_directory or snapshot.content is None:
            raise ValueError(f"Source path is not a stable regular file: {path}")
        return snapshot.content, snapshot.metadata

    parent_fd: int | None = None
    descriptor: int | None = None
    try:
        if _ANCHORED_SOURCE_DRAFT_MUTATION_SUPPORTED:
            root, root_identity = _source_draft_root_identity(project_root)
            parent_fd = _open_source_draft_parent_fd(
                root,
                path,
                root_identity=root_identity,
            )
            expected = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
            descriptor = os.open(
                path.name,
                os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0),
                dir_fd=parent_fd,
            )
        else:
            expected = path.lstat()
            descriptor = os.open(
                path,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0),
            )
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(expected.st_mode) or not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino):
            raise ValueError(f"Source path is not a stable regular file: {path}")
        if opened.st_size > max_bytes:
            raise ValueError(f"Source file is larger than {max_bytes} bytes: {path}")
        content = bytearray()
        while chunk := os.read(descriptor, 1024 * 1024):
            content.extend(chunk)
            if len(content) > max_bytes:
                raise ValueError(f"Source file is larger than {max_bytes} bytes: {path}")
        after = os.fstat(descriptor)
        if parent_fd is not None:
            rebound = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        else:
            rebound = path.lstat()
        identity = (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
        )
        after_identity = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        )
        rebound_identity = (
            rebound.st_dev,
            rebound.st_ino,
            rebound.st_size,
            rebound.st_mtime_ns,
        )
        if after_identity != identity or rebound_identity != identity or len(content) != opened.st_size:
            raise ValueError(f"Source file changed while it was read: {path}")
        return bytes(content), after
    except ValueError:
        raise
    except (FileNotFoundError, OSError) as error:
        raise ValueError(f"Source file changed before it could be read: {path}") from error
    finally:
        if descriptor is not None:
            _close_module_descriptor(descriptor)
        if parent_fd is not None:
            _close_module_descriptor(parent_fd)


def _project_root_alias_suffix(project_root: Path, path: Path) -> Path | None:
    """Return a root-relative suffix using filesystem identity, if available."""

    cursor = path
    while True:
        try:
            if os.path.samefile(cursor, project_root):
                return path.relative_to(cursor)
        except OSError:
            pass
        parent = cursor.parent
        if parent == cursor:
            return None
        cursor = parent


def _validate_source_draft_symlink_path(project_root: Path, path: Path) -> None:
    root = Path(os.path.abspath(project_root.expanduser()))
    cursor = Path(path.anchor)
    entered_project = False
    for part in path.parts[1:]:
        cursor /= part
        try:
            resolved_cursor = cursor.resolve()
        except (OSError, RuntimeError) as error:
            raise ValueError(f"Source path could not be resolved safely: {cursor}.") from error
        alias_suffix = _project_root_alias_suffix(root, cursor)
        try:
            resolved_cursor.relative_to(root)
        except ValueError:
            inside_project = alias_suffix is not None
        else:
            inside_project = True
        try:
            aliases_root = os.path.samefile(cursor, root)
        except OSError:
            aliases_root = False
        if cursor.is_symlink() and (entered_project or (inside_project and not aliases_root)):
            raise ValueError(f"Source draft path must not traverse a symlink: {cursor}.")
        if inside_project:
            entered_project = True
        if not cursor.exists():
            break


def _validate_unique_source_draft_paths(paths: Sequence[object]) -> None:
    seen: dict[str, Path] = {}
    for value in paths:
        if not isinstance(value, Path):
            raise ValueError("Source draft path did not resolve to a filesystem path.")
        identity = unicodedata.normalize("NFC", value.as_posix()).casefold()
        previous = seen.get(identity)
        if previous is not None:
            raise ValueError(f"Draft apply request targets the same filesystem path more than once: {previous} and {value}.")
        seen[identity] = value


def _source_draft_expected_revision(
    item: Mapping[object, object],
    *,
    field: str,
    allow_absent: bool = False,
) -> object:
    expected_size = item.get("expected_size")
    expected_mtime_ns = item.get("expected_mtime_ns")
    expected_absent = item.get("expected_absent")
    if expected_absent is not None:
        if not allow_absent:
            raise ValueError(f"Request field '{field}.expected_absent' is not supported.")
        if type(expected_absent) is not bool:
            raise ValueError(f"Request field '{field}.expected_absent' must be a boolean.")
        if expected_absent:
            if expected_size is not None or expected_mtime_ns is not None:
                raise ValueError(f"Request field '{field}' cannot combine expected_absent with an expected revision.")
            return _SOURCE_DRAFT_EXPECTED_ABSENT
    if expected_size is None and expected_mtime_ns is None:
        return None
    if expected_size is None or expected_mtime_ns is None:
        raise ValueError(f"Request field '{field}' must provide expected_size and expected_mtime_ns together.")
    if type(expected_size) is not int or expected_size < 0:
        raise ValueError(f"Request field '{field}.expected_size' must be a non-negative integer.")
    if isinstance(expected_mtime_ns, str):
        if not expected_mtime_ns.isascii() or not expected_mtime_ns.isdecimal():
            raise ValueError(f"Request field '{field}.expected_mtime_ns' must be a non-negative integer string.")
        normalized_mtime_ns = int(expected_mtime_ns)
    elif type(expected_mtime_ns) is int and expected_mtime_ns >= 0:
        normalized_mtime_ns = expected_mtime_ns
    else:
        raise ValueError(f"Request field '{field}.expected_mtime_ns' must be a non-negative integer string.")
    return expected_size, normalized_mtime_ns


def _validate_source_draft_item_fields(
    item: Mapping[object, object],
    *,
    allowed: frozenset[str],
    field: str,
) -> None:
    unknown = sorted((repr(key) for key in item if not isinstance(key, str) or key not in allowed))
    if unknown:
        raise ValueError(f"Request field '{field}' contains unsupported fields: {', '.join(unknown)}.")


def _validate_source_draft_expected_revision(path: Path, expected_revision: object) -> None:
    if expected_revision is None:
        return
    if expected_revision is _SOURCE_DRAFT_EXPECTED_ABSENT:
        try:
            path.lstat()
        except FileNotFoundError:
            return
        except OSError as error:
            raise ValueError(f"Source draft conflict: {path} could not be checked safely.") from error
        raise ValueError(f"Source draft conflict: {path} appeared after the draft was opened. " "Refresh or restore the draft before applying.")
    if not isinstance(expected_revision, tuple) or len(expected_revision) != 2 or any(type(value) is not int for value in expected_revision):
        raise ValueError("Source draft expected revision did not normalize correctly.")
    try:
        metadata = path.stat()
    except OSError as error:
        raise ValueError(f"Source draft conflict: {path} changed or disappeared after the draft was opened.") from error
    if not stat.S_ISREG(metadata.st_mode) or (metadata.st_size, metadata.st_mtime_ns) != expected_revision:
        raise ValueError(f"Source draft conflict: {path} changed after the draft was opened. Refresh or restore the draft before applying.")


def _validate_source_draft_expected_content_sha256(value: object) -> str:
    """Return one normalized exact-content guard or fail closed."""

    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("Source draft expected content SHA-256 did not normalize correctly.")
    return value


def _validate_source_draft_expected_revisions(
    edits: Sequence[Mapping[str, object]],
    removals: Sequence[Mapping[str, object]],
    replacements: Sequence[Mapping[str, object]],
) -> None:
    for item in (*edits, *removals, *replacements):
        path = item.get("path")
        if not isinstance(path, Path):
            raise ValueError("Source draft path did not resolve to a filesystem path.")
        _validate_source_draft_expected_revision(path, item.get("expected_revision"))


def _source_draft_edits(project: Project, value: object) -> tuple[dict[str, object], ...]:
    project_root = project.root
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("Request field 'source_edits' must be an array.")
    edits: list[dict[str, object]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"Request field 'source_edits[{index}]' must be an object.")
        _validate_source_draft_item_fields(
            item,
            allowed=_SOURCE_DRAFT_EDIT_FIELDS,
            field=f"source_edits[{index}]",
        )
        source_path = _project_source_path(
            project_root,
            _required_path_text(item.get("path"), f"source_edits[{index}].path"),
            reject_symlinks=True,
        )
        if not source_path.is_file():
            raise ValueError(f"Source edit path is not a file: {source_path}")
        text = item.get("text")
        if not isinstance(text, str):
            raise ValueError(f"Request field 'source_edits[{index}].text' must be a string.")
        _validate_source_draft_text(project, source_path, text)
        edits.append(
            {
                "path": source_path,
                "text": text,
                "expected_revision": _source_draft_expected_revision(
                    item,
                    field=f"source_edits[{index}]",
                ),
            }
        )
    return tuple(edits)


def _validate_source_draft_text(project: Project, path: Path, text: str) -> None:
    project_root = project.root
    relative_path = _project_relative_path(project_root, path)
    byte_size = len(text.encode("utf-8"))
    if byte_size > MAX_PROJECT_SOURCE_TEXT_BYTES:
        raise ValueError(f"Source draft is larger than the {MAX_PROJECT_SOURCE_TEXT_BYTES}-byte editor limit: {relative_path}.")

    suffix = path.suffix.casefold()
    if suffix == ".json":
        try:
            value = loads_json(
                text,
                restore=False,
                parse_constant=lambda constant: _reject_source_draft_json_constant(constant),
                parse_float=_source_draft_json_float,
                parse_int=_source_draft_json_int,
                object_pairs_hook=_source_draft_json_object,
            )
            _validate_source_draft_nesting(value)
        except (RecursionError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid JSON source draft {relative_path!r}: {error}") from error
        return
    if suffix not in {".yaml", ".yml"}:
        return
    module_path = _source_draft_module_path(project, path)
    if module_path is not None:
        _source_root, family_id, _object_id, _module_root, relative_path = module_path
        registry = project._build_registry(profile=project.game)
        try:
            family = registry.family(family_id)
        except ValueError:
            family = None
        if family is not None and is_loc_text_form_source(family, relative_path):
            document = parse_localization_source(text)
            if document.issues:
                issue = document.issues[0]
                raise ValueError(f"Invalid localization source draft {relative_path!r} line " f"{issue.line}: {issue.code.replace('_', ' ')}.")
            return
    try:
        value = loads_yaml(text)
        _validate_source_draft_nesting(value)
    except (RecursionError, TypeError, ValueError, YAMLError) as error:
        raise ValueError(f"Invalid YAML source draft {relative_path!r}: {error}") from error


def _validate_source_draft_nesting(value: object) -> None:
    """Bound structured editor payload depth without recursive traversal."""

    stack: list[tuple[object, int, bool]] = [(value, 0, False)]
    active: set[int] = set()
    deepest: dict[int, int] = {}
    while stack:
        item, depth, leaving = stack.pop()
        if not isinstance(item, dict | list | tuple | set):
            continue
        identity = id(item)
        if leaving:
            active.remove(identity)
            continue
        if identity in active:
            raise ValueError("recursive structured-data aliases are not allowed")
        if depth > MAX_PROJECT_SOURCE_NESTING_DEPTH:
            raise ValueError(f"structured-data nesting exceeds the {MAX_PROJECT_SOURCE_NESTING_DEPTH}-level editor limit")
        if deepest.get(identity, -1) >= depth:
            continue
        deepest[identity] = depth
        active.add(identity)
        stack.append((item, depth, True))
        children = (*item.keys(), *item.values()) if isinstance(item, dict) else tuple(item)
        stack.extend((child, depth + 1, False) for child in reversed(children))


def _reject_source_draft_json_constant(constant: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant {constant!r} is not allowed")


def _source_draft_json_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise ValueError(f"non-finite JSON number {token!r} is not allowed")
    return value


def _source_draft_json_int(token: str) -> int:
    value = int(token)
    if not math.isfinite(float(token)):
        raise ValueError(f"non-finite JSON number {token!r} is not allowed")
    return value


def _source_draft_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON object key {key!r} is not allowed")
        value[key] = item
    return value


def _source_draft_removals(
    project_root: Path,
    value: object,
) -> tuple[dict[str, object], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("Request field 'source_removals' must be an array.")
    removals: list[dict[str, object]] = []
    for index, item in enumerate(value):
        if isinstance(item, Mapping):
            _validate_source_draft_item_fields(
                item,
                allowed=_SOURCE_DRAFT_REMOVAL_FIELDS,
                field=f"source_removals[{index}]",
            )
            path_value = item.get("path")
            expected_revision = _source_draft_expected_revision(
                item,
                field=f"source_removals[{index}]",
            )
        else:
            path_value = item
            expected_revision = None
        source_path = _project_source_path(
            project_root,
            _required_path_text(path_value, f"source_removals[{index}].path"),
            reject_symlinks=True,
        )
        if not source_path.is_file():
            raise ValueError(f"Source removal path is not a file: {source_path}")
        removals.append(
            {
                "path": source_path,
                "expected_revision": expected_revision,
            }
        )
    return tuple(removals)


def _source_draft_replacements(project_root: Path, value: object) -> tuple[dict[str, object], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("Request field 'source_replacements' must be an array.")
    if len(value) > MAX_PROJECT_SOURCE_REPLACEMENT_FILES:
        raise ValueError(f"Request field 'source_replacements' must contain at most {MAX_PROJECT_SOURCE_REPLACEMENT_FILES} files.")
    replacements: list[dict[str, object]] = []
    total_bytes = 0
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"Request field 'source_replacements[{index}]' must be an object.")
        _validate_source_draft_item_fields(
            item,
            allowed=_SOURCE_DRAFT_REPLACEMENT_FIELDS,
            field=f"source_replacements[{index}]",
        )
        source_path = _project_source_path(
            project_root,
            _required_path_text(item.get("path"), f"source_replacements[{index}].path"),
            must_exist=False,
            reject_symlinks=True,
        )
        if source_path.exists() and not source_path.is_file():
            raise ValueError(f"Source replacement path is not a file: {source_path}")
        content_base64 = _required_path_text(item.get("content_base64"), f"source_replacements[{index}].content_base64")
        try:
            content = base64.b64decode(content_base64, validate=True)
        except binascii.Error as error:
            raise ValueError(f"Request field 'source_replacements[{index}].content_base64' must be valid base64.") from error
        if len(content) > MAX_PROJECT_SOURCE_REPLACEMENT_FILE_BYTES:
            raise ValueError(
                f"Request field 'source_replacements[{index}].content_base64' exceeds the " f"{MAX_PROJECT_SOURCE_REPLACEMENT_FILE_BYTES}-byte file limit."
            )
        total_bytes += len(content)
        if total_bytes > MAX_PROJECT_SOURCE_REPLACEMENT_TOTAL_BYTES:
            raise ValueError(f"Request field 'source_replacements' exceeds the {MAX_PROJECT_SOURCE_REPLACEMENT_TOTAL_BYTES}-byte total limit.")
        content_format, target_format = _source_replacement_formats(
            item,
            index=index,
            path=source_path,
            content=content,
        )
        replacements.append(
            {
                "path": source_path,
                "content": content,
                "content_format": content_format,
                "target_format": target_format,
                "index": index,
                "expected_revision": _source_draft_expected_revision(
                    item,
                    field=f"source_replacements[{index}]",
                    allow_absent=True,
                ),
            }
        )
    _validate_unique_source_draft_paths(tuple(replacement["path"] for replacement in replacements))
    for replacement in replacements:
        content_format = replacement["content_format"]
        target_format = replacement["target_format"]
        if content_format is None or target_format is None:
            continue
        path = replacement["path"]
        content = replacement["content"]
        index = replacement["index"]
        if not isinstance(path, Path) or not isinstance(content, bytes) or not isinstance(index, int):
            raise ValueError("Source replacement did not normalize into a conversion-ready payload.")
        converted = _convert_source_replacement_png(
            content,
            project_root=project_root,
            path=path,
            target_format=str(target_format),
            index=index,
        )
        if len(converted) > MAX_PROJECT_SOURCE_REPLACEMENT_FILE_BYTES:
            raise ValueError(f"Converted source replacement at index {index} exceeds the {MAX_PROJECT_SOURCE_REPLACEMENT_FILE_BYTES}-byte file limit.")
        replacement["content"] = converted
    if sum(len(bytes(replacement["content"])) for replacement in replacements) > MAX_PROJECT_SOURCE_REPLACEMENT_TOTAL_BYTES:
        raise ValueError(f"Converted source replacements exceed the {MAX_PROJECT_SOURCE_REPLACEMENT_TOTAL_BYTES}-byte total limit.")
    return tuple(replacements)


def _source_draft_module_rename(
    project: Project,
    value: object,
) -> _PreparedModuleRename | None:
    """Normalize and preflight the optional module rename in a source draft."""

    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("Request field 'module_rename' must be an object.")
    _validate_source_draft_item_fields(
        value,
        allowed=_SOURCE_DRAFT_MODULE_RENAME_FIELDS,
        field="module_rename",
    )
    module_id = _required_path_text(
        value.get("module_id"),
        "module_rename.module_id",
    )
    object_id = _required_path_text(
        value.get("object_id"),
        "module_rename.object_id",
    )
    source_root = value.get("source_root")
    if source_root is not None and not isinstance(source_root, str | os.PathLike):
        raise ValueError("Request field 'module_rename.source_root' must be a path string or null.")
    title = value.get("title")
    if title is not None and not isinstance(title, str):
        raise ValueError("Request field 'module_rename.title' must be a string or null.")
    return _prepare_project_module_rename(
        project,
        module_id,
        object_id,
        source_root=source_root,
        title=title,
    )


def _source_replacement_formats(
    item: Mapping[object, object],
    *,
    index: int,
    path: Path,
    content: bytes,
) -> tuple[str | None, str | None]:
    content_format = item.get("content_format")
    target_format = item.get("target_format")
    if content_format is None and target_format is None:
        return None, None
    if content_format is None or target_format is None:
        raise ValueError(f"Request field 'source_replacements[{index}]' must provide content_format and target_format together.")
    if content_format != "png":
        raise ValueError(f"Request field 'source_replacements[{index}].content_format' must be 'png'.")
    if not isinstance(target_format, str) or target_format not in _SOURCE_IMAGE_TARGET_FORMATS:
        allowed = ", ".join(sorted(_SOURCE_IMAGE_TARGET_FORMATS))
        raise ValueError(f"Request field 'source_replacements[{index}].target_format' must be one of: {allowed}.")
    if not path.is_file():
        raise ValueError(f"Request field 'source_replacements[{index}].path' must name an existing file for format conversion: {path}")
    if path.suffix.lower() != f".{target_format}":
        raise ValueError(
            f"Request field 'source_replacements[{index}].target_format' value {target_format!r} must match target suffix {path.suffix.lower()!r}."
        )
    if not content.startswith(_PNG_SIGNATURE):
        raise ValueError(f"Request field 'source_replacements[{index}].content_base64' must contain PNG bytes when content_format is 'png'.")
    return content_format, target_format


def _convert_source_replacement_png(content: bytes, *, project_root: Path, path: Path, target_format: str, index: int) -> bytes:
    with tempfile.TemporaryDirectory(prefix="paradev-source-image-") as scratch_directory:
        scratch_root = Path(scratch_directory).resolve()
        try:
            scratch_root.relative_to(project_root.expanduser().resolve())
        except ValueError:
            pass
        else:
            raise ValueError("Image conversion scratch directory must stay outside the project root.")
        input_path = scratch_root / "source.png"
        output_path = scratch_root / f"converted.{target_format}"
        save_bin(content, str(input_path))
        converter_found = False
        failures: list[str] = []
        for converter in _source_image_converter_candidates():
            if converter == _SOURCE_IMAGE_LEGACY_CONVERTER and not _legacy_convert_is_imagemagick():
                continue
            delete_file(output_path)
            args = _source_image_conversion_args(
                converter,
                input_path=input_path,
                output_path=output_path,
                target_format=target_format,
            )
            try:
                result = cmd(args, shell=False)
            except FileNotFoundError:
                continue
            except OSError as error:
                converter_found = True
                failures.append(f"{converter}: {error}")
                continue
            converter_found = True
            if not isinstance(result, CmdResult):
                failures.append(f"{converter}: returned an unsupported command result")
                continue
            if not result.ok:
                result_detail = result.err or result.out or f"exit code {result.code}"
                failures.append(f"{converter}: {result_detail}")
                continue
            if not output_path.is_file():
                failures.append(f"{converter}: conversion did not produce an output file")
                continue
            try:
                converted = load_bin(str(output_path), strict=True)
            except OSError as error:
                failures.append(f"{converter}: conversion output could not be read: {error}")
                continue
            output_error = _converted_source_image_error(converted, target_format=target_format)
            if output_error is None:
                return converted
            failures.append(f"{converter}: {output_error}")
        if not converter_found:
            raise ValueError("Image conversion requires ImageMagick; 'magick' was unavailable and no ImageMagick-provided legacy 'convert' was available.")
        detail = "; ".join(failures) or "unknown ImageMagick failure"
        raise ValueError(
            f"Request field 'source_replacements[{index}]' PNG-to-{target_format.upper()} conversion failed without changing the source: {detail}."
        )


def _source_image_converter_candidates() -> tuple[str, ...]:
    if sys.platform == "win32":
        return (_SOURCE_IMAGE_PRIMARY_CONVERTER,)
    return (_SOURCE_IMAGE_PRIMARY_CONVERTER, _SOURCE_IMAGE_LEGACY_CONVERTER)


def _legacy_convert_is_imagemagick() -> bool:
    try:
        result = cmd([_SOURCE_IMAGE_LEGACY_CONVERTER, "-version"], shell=False)
    except OSError:
        return False
    if not isinstance(result, CmdResult) or not result.ok:
        return False
    identity = "\n".join(part for part in (result.out, result.err) if part)
    return "imagemagick" in identity.casefold()


def _source_image_conversion_args(converter: str, *, input_path: Path, output_path: Path, target_format: str) -> list[str]:
    args = [converter, str(input_path)]
    if target_format == "dds":
        args.extend(["-define", "dds:compression=dxt5"])
    elif target_format == "tga":
        args.extend(["-compress", "none"])
    args.append(str(output_path))
    return args


def _converted_source_image_error(content: bytes, *, target_format: str) -> str | None:
    if not content:
        return f"conversion produced an empty {target_format.upper()} file"
    if target_format == "dds":
        if len(content) < 128 or not content.startswith(b"DDS "):
            return "conversion did not produce a valid DDS header"
        if content[84:88] != b"DXT5":
            return "conversion did not produce DXT5 DDS compression"
        return None
    if target_format in {"jpg", "jpeg"}:
        return None if content.startswith(b"\xff\xd8\xff") else "conversion did not produce a JPEG header"
    if target_format == "webp":
        return None if len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP" else "conversion did not produce a WebP header"
    if target_format == "bmp":
        return None if content.startswith(b"BM") else "conversion did not produce a BMP header"
    if target_format == "tga":
        if len(content) < 18:
            return "conversion did not produce a complete TGA header"
        width = int.from_bytes(content[12:14], "little")
        height = int.from_bytes(content[14:16], "little")
        if content[2] not in {2, 3} or width < 1 or height < 1:
            return "conversion did not produce an uncompressed TGA image header"
        return None
    return f"conversion used unsupported target format {target_format!r}"


class _ModuleDiagramBuildRejected(ValueError):
    """Raised inside a source transaction when build acceptance fails."""


class _ModuleDiagramSourceRejected(ValueError):
    """Raised when a companion diagram source transaction cannot commit."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "module_diagram.source_conflict",
        recovery_path: Path | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.recovery_path = recovery_path


class _ProjectModuleDiagramContext:
    """Guarded project-resource adapter for registered diagram providers."""

    def __init__(
        self,
        project: Project,
        *,
        registry: "BuildRegistry",
        family: str,
        profile: str,
    ) -> None:
        self._project = project
        self._registry = registry
        self._family = family
        self._profile = profile
        self._modules = _module_diagram_bundles(
            project,
            family=family,
            profile=profile,
            registry=registry,
        )
        self._collections: tuple["Collection", ...] | None = None

    @property
    def family(self) -> str:
        """Return the active registered source family."""

        return self._family

    @property
    def profile(self) -> str:
        """Return the active build profile."""

        return self._profile

    @property
    def preferred_language(self) -> str:
        """Return the project's preferred authoring-language alias."""

        return self._project.preferred_language

    @property
    def registered_family(self) -> object:
        """Return the active registered family compiler."""

        return self._registry.family(self._family)

    @property
    def modules(self) -> tuple["ModuleSourceBundle", ...]:
        """Return normalized modules discovered for the active family."""

        return self._modules

    def collections(self) -> tuple["Collection", ...]:
        """Return normalized collections discovered for the active family."""

        if self._collections is not None:
            return self._collections
        discovered = self._project.discover_collections(
            profile=self._profile,
            registry=self._registry,
            family=self._family,
        )
        blocking = [diagnostic for diagnostic in discovered.diagnostics if diagnostic.severity == "error"]
        if blocking:
            details = "; ".join(f"{diagnostic.code}: {diagnostic.message}" for diagnostic in blocking[:3])
            if len(blocking) > 3:
                details += f"; and {len(blocking) - 3} more"
            raise ValueError(f"Cannot project the {self._family!r} diagram while " f"collection discovery has blocking diagnostics: {details}")
        self._collections = tuple(
            sorted(
                discovered.collections,
                key=lambda row: row.collection_id,
            )
        )
        return self._collections

    def module_source_path(
        self,
        module: "ModuleSourceBundle",
        relative_path: str,
    ) -> str:
        """Validate and return one module-owned project-relative path."""

        path = self._owned_source_path(
            module.root,
            relative_path,
            label=f"Module {module.module_id!r}",
            must_exist=False,
        )
        return _project_relative_path(self._project.root, path)

    def read_module_text(
        self,
        module: "ModuleSourceBundle",
        relative_path: str,
    ) -> "ModuleDiagramTextSource":
        """Safely read one exact module-owned UTF-8 source."""

        path = self._owned_source_path(
            module.root,
            relative_path,
            label=f"Module {module.module_id!r}",
            must_exist=True,
        )
        return self._read_text(path)

    def read_optional_module_text(
        self,
        module: "ModuleSourceBundle",
        relative_path: str,
    ) -> "ModuleDiagramTextSource | None":
        """Safely read one optional module-owned UTF-8 source."""

        path = self._owned_source_path(
            module.root,
            relative_path,
            label=f"Module {module.module_id!r}",
            must_exist=False,
        )
        if not _path_entry_exists_lexically(path):
            return None
        return self._read_text(path)

    def module_source_inventory(
        self,
        module: "ModuleSourceBundle",
        *,
        maximum: int,
    ) -> tuple[str, ...]:
        """Return a bounded inventory without following source symlinks."""

        if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum < 1:
            raise ValueError("Module diagram source inventory maximum must be a positive integer.")
        root = _project_source_path(
            self._project.root,
            module.root,
            reject_symlinks=True,
        )
        if not root.is_dir():
            raise ValueError(f"Module {module.module_id!r} root is not a directory: {root}.")
        paths: list[str] = []
        for current, directory_names, file_names in os.walk(
            root,
            topdown=True,
            followlinks=False,
        ):
            current_root = Path(current)
            directory_names.sort()
            file_names.sort()
            for name in (*directory_names, *file_names):
                path = current_root / name
                if path.is_symlink():
                    raise ValueError(f"Module {module.module_id!r} source inventory cannot include a symlink: {path}.")
                path = _project_source_path(
                    self._project.root,
                    path,
                    reject_symlinks=True,
                )
                try:
                    path.relative_to(root)
                except ValueError as error:
                    raise ValueError(f"Module {module.module_id!r} source inventory escapes its root: {path}.") from error
                mode = os.lstat(path).st_mode
                if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                    raise ValueError(f"Module {module.module_id!r} source inventory entry is not a regular file or directory: {path}.")
                paths.append(_project_relative_path(self._project.root, path))
                if len(paths) > maximum:
                    raise ValueError(f"Module {module.module_id!r} source inventory exceeds the {maximum}-entry safety limit.")
        return tuple(paths)

    def collection_source_path(
        self,
        collection: "CollectionSourceBundle",
        relative_path: str,
    ) -> str:
        """Validate and return one collection-owned project-relative path."""

        path = self._owned_source_path(
            collection.root,
            relative_path,
            label=f"Collection {collection.collection_id!r}",
            must_exist=True,
        )
        return _project_relative_path(self._project.root, path)

    def _owned_source_path(
        self,
        owner_root: str,
        relative_path: str,
        *,
        label: str,
        must_exist: bool,
    ) -> Path:
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError(f"{label} diagram source path must be non-empty.")
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"{label} diagram source must stay inside its source root: " f"{relative_path!r}.")
        root = _project_source_path(
            self._project.root,
            owner_root,
            reject_symlinks=True,
        )
        lexical = Path(os.path.abspath(root / relative))
        if must_exist or lexical.exists() or lexical.parent.is_dir():
            path = _project_source_path(
                self._project.root,
                lexical,
                must_exist=must_exist,
                reject_symlinks=True,
            )
        else:
            _validate_source_draft_symlink_path(
                self._project.root,
                lexical,
            )
            path = lexical
        try:
            path.relative_to(root)
        except ValueError as error:
            raise ValueError(f"{label} diagram source escapes its source root: {path}.") from error
        return path

    def _read_text(self, path: Path) -> "ModuleDiagramTextSource":
        from paradev.build import ModuleDiagramTextSource

        payload, _metadata = _read_project_source_snapshot(
            self._project.root,
            path,
        )
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("Module diagram source is not UTF-8 text: " f"{_project_relative_path(self._project.root, path)}") from error
        return ModuleDiagramTextSource(
            path=_project_relative_path(self._project.root, path),
            text=text,
        )


def _module_diagram_bundles(
    project: Project,
    *,
    family: str,
    profile: str,
    registry: "BuildRegistry | None" = None,
) -> tuple[ModuleSourceBundle, ...]:
    from paradev.build import ModuleSourceBundle

    discovered = project.discover_modules(
        profile=profile,
        registry=registry,
        family=family,
    )
    blocking_discovery = [diagnostic for diagnostic in discovered.diagnostics if diagnostic.severity == "error"]
    if blocking_discovery:
        details = "; ".join(f"{diagnostic.code}: {diagnostic.message}" for diagnostic in blocking_discovery[:3])
        if len(blocking_discovery) > 3:
            details += f"; and {len(blocking_discovery) - 3} more"
        raise ValueError(f"Cannot project the {family!r} diagram while module discovery has " f"blocking diagnostics: {details}")

    rows: list[ModuleSourceBundle] = []
    for module in sorted(discovered.modules, key=lambda row: row.module_id):
        bundle = module.payload
        if not isinstance(bundle, ModuleSourceBundle):
            raise ValueError(f"Module {module.module_id!r} has no normalized source bundle " "for diagram projection.")
        rows.append(bundle)
    return tuple(rows)


def _module_diagram_sources(
    project: Project,
    *,
    family: str,
    profile: str,
    bundles: Sequence[ModuleSourceBundle] | None = None,
) -> tuple[dict[str, str], ...]:
    rows: list[dict[str, str]] = []
    source_bundles = (
        tuple(bundles)
        if bundles is not None
        else _module_diagram_bundles(
            project,
            family=family,
            profile=profile,
        )
    )
    for bundle in source_bundles:
        def_paths = tuple(bundle.source_slots.get("def", ()))
        if len(def_paths) != 1:
            raise ValueError(f"Module {bundle.module_id!r} must own exactly one canonical " f"'def' source for diagram editing; found {len(def_paths)}.")
        module_root = Path(bundle.root)
        path = _project_source_path(
            project.root,
            module_root / def_paths[0],
            reject_symlinks=True,
        )
        payload, _metadata = _read_project_source_snapshot(project.root, path)
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"{family.replace('_', ' ').title()} definition is not UTF-8 " f"text: {_project_relative_path(project.root, path)}") from error
        rows.append(
            {
                "path": _project_relative_path(project.root, path),
                "text": text,
            }
        )
    return tuple(rows)


def _module_diagram_payload(
    project: Project,
    *,
    family: str,
    profile: str,
    projection: Mapping[str, object],
) -> dict[str, object]:
    payload = dict(projection)
    provider_schema = payload.pop("schema", None)
    nodes = payload.get("nodes")
    if not isinstance(nodes, list):
        nodes = []
    diagnostics = [dict(row) for row in payload.get("diagnostics", []) if isinstance(row, Mapping)]
    if not nodes:
        payload["editable"] = False
        diagnostics.append(
            {
                "code": "module_diagram.no_nodes",
                "message": (f"No canonical {family} definitions were found. Create a " "module from a project template before editing this diagram."),
                "severity": "warning",
            }
        )
    payload["diagnostics"] = diagnostics
    return {
        "schema": MODULE_DIAGRAM_SCHEMA,
        "provider_schema": provider_schema,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "profile": profile,
        "family": family,
        **payload,
    }


def _module_diagram_companion_source_plan(
    value: Mapping[str, object] | None,
) -> dict[str, object]:
    """Validate one provider plan coupled to standalone module creation."""

    if value is None:
        return {}
    payload = dict(value)
    schema = payload.get("schema")
    status = payload.get("status")
    plan_hash = payload.get("plan_hash")
    if not isinstance(schema, str) or not schema.strip():
        raise ValueError("Companion diagram source plan requires a schema.")
    if status not in {"blocked", "planned", "unchanged"}:
        raise ValueError("Companion diagram source plan status must be blocked, planned, or unchanged.")
    if not isinstance(plan_hash, str) or re.fullmatch(r"[0-9a-f]{64}", plan_hash) is None:
        raise ValueError("Companion diagram source plan requires a canonical SHA-256 plan_hash.")
    for field_name in ("diagnostics", "drafts", "source_replacements"):
        rows = payload.get(field_name, [])
        if not isinstance(rows, list) or any(not isinstance(row, Mapping) for row in rows):
            raise ValueError(f"Companion diagram source plan {field_name} must be an array of objects.")
    drafts = cast(list[Mapping[str, object]], payload.get("drafts", []))
    if status == "planned" and not drafts:
        raise ValueError("A planned companion diagram source plan must contain at least one draft.")
    if status != "planned" and drafts:
        raise ValueError("Only a planned companion diagram source plan may contain drafts.")
    return payload


def _module_diagram_source_edits(
    project: Project,
    drafts: Sequence[Mapping[str, object]],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    tuple[tuple[dict[str, object], Path], ...],
]:
    """Preflight exact provider drafts for a guarded diagram transaction."""

    edits: list[dict[str, object]] = []
    files: list[dict[str, object]] = []
    for index, draft in enumerate(drafts):
        relative_path = draft.get("path")
        text = draft.get("text")
        expected_sha256 = draft.get("expected_sha256")
        if not isinstance(relative_path, str) or not isinstance(text, str) or not isinstance(expected_sha256, str):
            raise ValueError(f"Module diagram draft {index} has an invalid path, text, " "or expected SHA-256 revision.")
        expected_sha256 = _validate_source_draft_expected_content_sha256(expected_sha256)
        path = _project_source_path(
            project.root,
            relative_path,
            reject_symlinks=True,
        )
        edits.append(
            {
                "path": path,
                "text": text,
                "expected_content_sha256": expected_sha256,
            }
        )
        files.append(
            {
                "path": str(path),
                "relative_path": _project_relative_path(project.root, path),
                "operation": "write_text",
                "encoding": "utf-8",
            }
        )
    paths = tuple(cast(Path, edit["path"]) for edit in edits)
    _validate_unique_source_draft_paths(paths)
    module_targets = _source_draft_module_targets(project, paths)
    _validate_project_family_source_text_drafts(project, edits)
    return edits, files, module_targets


def _sync_module_diagram_source_targets(
    project: Project,
    module_targets: Sequence[tuple[dict[str, object], Path]],
    *,
    catalog_lock_held: bool,
) -> dict[str, object] | None:
    """Refresh Catalog projections for existing modules edited by a diagram."""

    from paradev.hb import _sync_module_catalog_projection

    mutations: list[dict[str, object]] = []
    for previous, source_root in module_targets:
        try:
            current = _find_project_module(
                project,
                str(previous["module_id"]),
                source_root=source_root,
            )
        except Exception as error:
            mutations.append(
                _sync_module_catalog_projection(
                    project,
                    previous=previous,
                    current_error=error,
                    _lock_held=catalog_lock_held,
                )
            )
        else:
            mutations.append(
                _sync_module_catalog_projection(
                    project,
                    previous=previous,
                    current=current.to_dict(),
                    _lock_held=catalog_lock_held,
                )
            )
    if not mutations:
        return None
    return _aggregate_source_draft_catalog_mutations(mutations)


def _apply_module_diagram_module_creation(
    project: Project,
    *,
    family: str,
    profile: str,
    plan: "ModuleDiagramModuleCreation",
    write: bool,
    plan_hash: str | None,
) -> dict[str, object]:
    """Plan or atomically scaffold one provider-owned diagram node module."""

    source_plan = _module_diagram_companion_source_plan(plan.source_plan)
    source_diagnostics = [dict(row) for row in source_plan.get("diagnostics", []) if isinstance(row, Mapping)]
    source_drafts = [dict(row) for row in source_plan.get("drafts", []) if isinstance(row, Mapping)]
    source_replacements = [dict(row) for row in source_plan.get("source_replacements", []) if isinstance(row, Mapping)]
    source_blocked = source_plan.get("status") == "blocked" or any(row.get("severity") == "error" for row in source_diagnostics)
    source_edits: list[dict[str, object]] = []
    source_files: list[dict[str, object]] = []
    source_targets: tuple[tuple[dict[str, object], Path], ...] = ()
    if source_drafts and not source_blocked:
        source_edits, source_files, source_targets = _module_diagram_source_edits(
            project,
            source_drafts,
        )

    build_results: list["BuildResult"] = []

    def validate_family_build() -> None:
        result = project.build(profile=profile, family=family)
        build_results.append(result)
        if not result.blocked:
            return
        errors = [f"{diagnostic.code}: {diagnostic.message}" for diagnostic in result.diagnostics if diagnostic.severity == "error"]
        detail = "; ".join(errors[:3]) or "unknown blocking diagnostic"
        if len(errors) > 3:
            detail += f"; and {len(errors) - 3} more"
        raise _ModuleDiagramBuildRejected(f"The created {family} module did not pass a family build and was " f"rolled back: {detail}")

    def validate_created_module() -> None:
        if not source_edits:
            validate_family_build()
            return
        draft_root, draft_root_identity = _source_draft_root_identity(project.root)
        try:
            _apply_source_draft_mutations(
                draft_root,
                edits=source_edits,
                replacements=(),
                removals=(),
                root_identity=draft_root_identity,
                validate=validate_family_build,
            )
        except _ModuleDiagramBuildRejected:
            raise
        except _SourceDraftRollbackIncomplete as error:
            raise _ModuleDiagramSourceRejected(
                "The companion diagram source rollback was incomplete; recovery " f"data remains at {error.recovery_path}: {error}.",
                code="module_diagram.source_rollback_incomplete",
                recovery_path=error.recovery_path,
            ) from error
        except (OSError, ValueError) as error:
            raise _ModuleDiagramSourceRejected("The companion diagram source changed before the new module could " f"be committed safely: {error}.") from error

    from paradev.hb import _module_catalog_mutation_scope

    selected_source_root = _select_source_root(
        project.root,
        project.source_roots,
        None,
    )
    request = {
        "family_or_template": plan.family_or_template,
        "object_id": plan.object_id,
        "values": dict(plan.values),
    }
    source_catalog_mutation: dict[str, object] | None = None
    with _module_catalog_mutation_scope(project, enabled=write) as catalog_lock_held:
        preview = _create_project_modules(
            project,
            [request],
            source_root=selected_source_root,
            write=False,
            plan_hash=None,
            catalog_lock_held=catalog_lock_held,
            profile=profile,
        )
        from paradev.games.hoi4._diagram_source import stable_payload_hash

        current_plan_hash = stable_payload_hash(
            {
                "schema": MODULE_DIAGRAM_EDIT_SCHEMA,
                "provider_schema": plan.schema,
                "profile": profile,
                "family": family,
                "intent": dict(plan.intent),
                "request": request,
                "module_plan_hash": preview.get("plan_hash"),
                "source_plan": source_plan,
            }
        )
        preview_diagnostics = [dict(row) for row in preview.get("diagnostics", []) if isinstance(row, Mapping)]
        batch = {
            **preview,
            "blocked": preview.get("blocked") is True or source_blocked,
            "diagnostics": [*preview_diagnostics, *source_diagnostics],
        }
        if write and plan_hash != current_plan_hash:
            diagnostics = [dict(row) for row in batch.get("diagnostics", []) if isinstance(row, Mapping)]
            diagnostics.append(
                {
                    "code": ("module_diagram.plan_hash_required" if not isinstance(plan_hash, str) or not plan_hash else "module_diagram.plan_hash_mismatch"),
                    "message": (
                        "Applying diagram node creation requires the exact plan_hash returned by the current dry plan."
                        if not isinstance(plan_hash, str) or not plan_hash
                        else "Diagram sources or node inputs changed after planning; review the current plan and apply its plan_hash."
                    ),
                    "severity": "error",
                    "expected_plan_hash": current_plan_hash,
                    **({"provided_plan_hash": plan_hash} if isinstance(plan_hash, str) else {}),
                }
            )
            batch = {
                **batch,
                "blocked": True,
                "diagnostics": diagnostics,
            }
        elif write and batch.get("blocked") is not True:
            created_batch = _create_project_modules(
                project,
                [request],
                source_root=selected_source_root,
                write=True,
                plan_hash=str(preview["plan_hash"]),
                catalog_lock_held=catalog_lock_held,
                profile=profile,
                validate=validate_created_module,
                diagram_source_edits=source_edits,
            )
            batch = {
                **created_batch,
                "diagnostics": [
                    *[dict(row) for row in created_batch.get("diagnostics", []) if isinstance(row, Mapping)],
                    *source_diagnostics,
                ],
            }
            if batch.get("applied") is True and source_targets:
                source_catalog_mutation = _sync_module_diagram_source_targets(
                    project,
                    source_targets,
                    catalog_lock_held=catalog_lock_held,
                )
    modules = [dict(row) for row in batch.get("modules", []) if isinstance(row, Mapping)]
    module = modules[0] if modules else {}
    drafts = [dict(row) for row in module.get("files", []) if isinstance(row, Mapping)]
    diagnostics = [dict(row) for row in batch.get("diagnostics", []) if isinstance(row, Mapping)]
    diagnostics.extend(dict(row) for row in module.get("diagnostics", []) if isinstance(row, Mapping))
    blocked = batch.get("blocked") is True
    applied = batch.get("applied") is True
    written = batch.get("written") is True
    validation = build_results[-1].summary() if build_results else None
    catalog_mutations = [
        mutation
        for mutation in (
            module.get("catalog_mutation"),
            source_catalog_mutation,
        )
        if isinstance(mutation, Mapping)
    ]
    catalog_mutation = _aggregate_source_draft_catalog_mutations(catalog_mutations) if catalog_mutations else None
    return {
        "schema": MODULE_DIAGRAM_EDIT_SCHEMA,
        "provider_schema": plan.schema,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "profile": profile,
        "family": family,
        "status": "blocked" if blocked else "applied" if applied else "planned",
        "write": write,
        "blocked": blocked,
        "applied": applied,
        "written": written,
        "plan_hash": current_plan_hash,
        "intent": dict(plan.intent),
        "module": module,
        "batch": batch,
        "drafts": drafts,
        "source_plan": source_plan,
        "source_drafts": source_drafts,
        "source_replacements": source_replacements,
        "diagnostics": diagnostics,
        "files": [*drafts, *source_files] if written else [],
        **(
            {
                "validation": {
                    "profile": profile,
                    "family": family,
                    **validation,
                }
            }
            if validation is not None
            else {}
        ),
        **({"catalog_mutation": catalog_mutation} if catalog_mutation is not None else {}),
        **({"source_catalog_mutation": source_catalog_mutation} if source_catalog_mutation is not None else {}),
        **({"created_node_id": plan.object_id} if applied and not blocked else {}),
    }


def _apply_module_diagram_plan(
    project: Project,
    *,
    family: str,
    profile: str,
    plan: Mapping[str, object],
    write: bool,
    plan_hash: str | None,
) -> dict[str, object]:
    payload = dict(plan)
    provider_schema = payload.pop("schema", None)
    diagnostics = [dict(row) for row in payload.get("diagnostics", []) if isinstance(row, Mapping)]
    drafts = [dict(row) for row in payload.get("drafts", []) if isinstance(row, Mapping)]
    current_plan_hash = payload.get("plan_hash")
    blocked = payload.get("status") == "blocked" or any(row.get("severity") == "error" for row in diagnostics)
    applied = False
    written = False
    validation: dict[str, object] | None = None
    catalog_mutation: dict[str, object] | None = None
    files: list[dict[str, object]] = []

    if write and drafts and (not isinstance(plan_hash, str) or not plan_hash):
        diagnostics.append(
            {
                "code": "module_diagram.plan_hash_required",
                "message": ("Applying diagram edits requires the exact plan_hash " "returned by the current dry plan."),
                "severity": "error",
            }
        )
        blocked = True
    elif write and drafts and plan_hash != current_plan_hash:
        diagnostics.append(
            {
                "code": "module_diagram.plan_hash_mismatch",
                "message": ("Diagram sources or intents changed after planning; review " "the current plan and apply its plan_hash."),
                "severity": "error",
                "expected_plan_hash": current_plan_hash,
                "provided_plan_hash": plan_hash,
            }
        )
        blocked = True

    if write and not blocked and not drafts:
        applied = True
    elif write and not blocked:
        draft_root, draft_root_identity = _source_draft_root_identity(project.root)
        edits, files, module_targets = _module_diagram_source_edits(project, drafts)
        build_results: list["BuildResult"] = []

        def validate_written_sources() -> None:
            result = project.build(profile=profile, family=family)
            build_results.append(result)
            if result.blocked:
                errors = [f"{diagnostic.code}: {diagnostic.message}" for diagnostic in result.diagnostics if diagnostic.severity == "error"]
                detail = "; ".join(errors[:3]) or "unknown blocking diagnostic"
                if len(errors) > 3:
                    detail += f"; and {len(errors) - 3} more"
                raise _ModuleDiagramBuildRejected(f"The edited {family} sources did not pass a family build: {detail}")

        from paradev.hb import _module_catalog_mutation_scope

        try:
            with _module_catalog_mutation_scope(
                project,
                enabled=bool(module_targets),
            ) as catalog_lock_held:
                _apply_source_draft_mutations(
                    draft_root,
                    edits=edits,
                    replacements=(),
                    removals=(),
                    root_identity=draft_root_identity,
                    validate=validate_written_sources,
                )
                catalog_mutation = _sync_module_diagram_source_targets(
                    project,
                    module_targets,
                    catalog_lock_held=catalog_lock_held,
                )
        except _ModuleDiagramBuildRejected as error:
            diagnostics.append(
                {
                    "code": "module_diagram.build_rejected",
                    "message": str(error),
                    "severity": "error",
                }
            )
            blocked = True
            files = []
        else:
            result = build_results[0]
            validation = {
                "profile": profile,
                "family": family,
                **result.summary(),
            }
            applied = True
            written = True

    status = "blocked" if blocked else "applied" if applied else str(payload.get("status") or "planned")
    return {
        "schema": MODULE_DIAGRAM_EDIT_SCHEMA,
        "provider_schema": provider_schema,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "profile": profile,
        "family": family,
        **payload,
        "status": status,
        "write": write,
        "blocked": blocked,
        "applied": applied,
        "written": written,
        "diagnostics": diagnostics,
        "files": files,
        **({"validation": validation} if validation is not None else {}),
        **({"catalog_mutation": catalog_mutation} if catalog_mutation is not None else {}),
    }


@dataclass(frozen=True, slots=True)
class _SourceDraftFileState:
    """Exact bounded content state used by crash recovery."""

    exists: bool
    size: int = 0
    content_sha256: str | None = None
    file_identity: tuple[int, int, int, int] | None = None


def _source_draft_file_state(
    project_root: Path,
    path: Path,
    *,
    root_identity: tuple[int, int],
) -> _SourceDraftFileState:
    """Read one no-follow source state for journal ownership checks."""

    if _uses_win32_source_draft_authority():
        parts = _win32_source_draft_parts(project_root, path)
        try:
            with _open_win32_source_draft_authority(
                project_root,
                root_identity=root_identity,
            ) as authority:
                snapshot = authority.read_file_snapshot(
                    parts,
                    max_bytes=MAX_PROJECT_SOURCE_DRAFT_BACKUP_BYTES,
                )
        except Win32FileSizeError as error:
            raise ValueError(f"Source draft recovery target is too large to verify: {path}.") from error
        if snapshot is None:
            return _SourceDraftFileState(exists=False)
        if snapshot.metadata.is_directory or snapshot.content_sha256 is None:
            raise ValueError(f"Source draft recovery target is not a regular file: {path}.")
        return _SourceDraftFileState(
            exists=True,
            size=snapshot.metadata.size,
            content_sha256=snapshot.content_sha256,
            file_identity=_win32_source_draft_file_identity(
                snapshot.metadata,
            ),
        )

    parent_fd = _open_source_draft_parent_fd(
        project_root,
        path,
        root_identity=root_identity,
    )
    descriptor: int | None = None
    try:
        try:
            expected = os.stat(
                path.name,
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return _SourceDraftFileState(exists=False)
        if not stat.S_ISREG(expected.st_mode):
            raise ValueError(f"Source draft recovery target is not a regular file: {path}.")
        if expected.st_size > MAX_PROJECT_SOURCE_DRAFT_BACKUP_BYTES:
            raise ValueError(f"Source draft recovery target is too large to verify: {path}.")
        descriptor = os.open(
            path.name,
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
        opened = os.fstat(descriptor)
        opened_identity = (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
        )
        if not stat.S_ISREG(opened.st_mode) or opened_identity != (
            expected.st_dev,
            expected.st_ino,
            expected.st_size,
            expected.st_mtime_ns,
        ):
            raise ValueError(f"Source draft recovery target changed before verification: {path}.")
        digest = hashlib.sha256()
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
        after = os.fstat(descriptor)
        if (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ) != opened_identity:
            raise ValueError(f"Source draft recovery target changed during verification: {path}.")
        return _SourceDraftFileState(
            exists=True,
            size=opened.st_size,
            content_sha256=digest.hexdigest(),
            file_identity=opened_identity,
        )
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source draft recovery target could not be verified safely: {path}.") from error
    finally:
        if descriptor is not None:
            _close_module_descriptor(descriptor)
        _close_module_descriptor(parent_fd)


def _source_draft_state_matches_before(
    state: _SourceDraftFileState,
    item: SourceDraftRecoveryFile,
) -> bool:
    if item.backup is None:
        return not state.exists
    return state.exists and state.size == item.size and state.content_sha256 == item.before_sha256


def _source_draft_state_matches_after(
    state: _SourceDraftFileState,
    item: SourceDraftRecoveryFile,
) -> bool:
    if not item.after_exists:
        return not state.exists
    return state.exists and state.size == item.after_size and state.content_sha256 == item.after_sha256


def _source_draft_recovery_state_owned(
    state: _SourceDraftFileState,
    item: SourceDraftRecoveryFile,
) -> bool:
    """Return whether a private displacement matches either journal state."""

    return _source_draft_state_matches_before(state, item) or _source_draft_state_matches_after(state, item)


def _unlink_source_draft_recovery_owned_file(
    project_root: Path,
    path: Path,
    state: _SourceDraftFileState,
    *,
    root_identity: tuple[int, int],
) -> None:
    """Delete one exact journal-owned private file without touching replacements."""

    if not state.exists or state.file_identity is None:
        return
    if _uses_win32_source_draft_authority():
        raise ValueError("Windows source recovery does not use adjacent displacement files.")
    parent_fd = _open_source_draft_parent_fd(
        project_root,
        path,
        root_identity=root_identity,
    )
    try:
        try:
            current = os.stat(
                path.name,
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return
        identity = (
            current.st_dev,
            current.st_ino,
            current.st_size,
            current.st_mtime_ns,
        )
        if not stat.S_ISREG(current.st_mode) or identity != state.file_identity:
            raise ValueError(f"Source draft recovery displacement changed before cleanup: {path}.")
        os.unlink(path.name, dir_fd=parent_fd)
        _fsync_source_draft_directory(parent_fd)
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source draft recovery displacement could not be cleaned: {path}.") from error
    finally:
        _close_module_descriptor(parent_fd)


def _module_directory_state(
    source_root: Path,
    *,
    family: str,
    module_name: str,
    container: Literal["modules", "collections"] = "modules",
) -> tuple[int, int] | None:
    """Return a safe Registry-folder identity, or ``None`` when absent."""

    if _uses_win32_module_mutation_authority():
        try:
            authority = Win32DirectoryAuthority.open(source_root, create=False)
        except (
            OSError,
            Win32FilesystemUnavailable,
            Win32UnsafePathError,
        ) as error:
            raise ValueError(f"Source recovery cannot retain module root: {source_root}.") from error
        try:
            metadata = authority.entry_metadata(
                (container, family, module_name),
            )
            if metadata is None:
                return None
            if not metadata.is_directory:
                raise ValueError(f"Source recovery module path is not a directory: {module_name}.")
            return metadata.identity
        finally:
            authority.close()
    family_fd = (
        _open_module_family_fd(source_root, family)
        if container == "modules"
        else _open_registry_family_fd(
            source_root,
            family,
            container=container,
        )
    )
    try:
        try:
            metadata = os.stat(
                module_name,
                dir_fd=family_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return None
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"Source recovery module path is not a directory: {module_name}.")
        return (metadata.st_dev, metadata.st_ino)
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source recovery module path changed: {module_name}.") from error
    finally:
        _close_module_descriptor(family_fd)


def _recover_source_draft_rename(
    project_root: Path,
    rename: SourceDraftRecoveryRename,
) -> None:
    """Reverse one safely identified interrupted Registry-folder rename."""

    source_root = project_root if rename.source_root == "." else project_root / PurePosixPath(rename.source_root)
    previous_identity = _module_directory_state(
        source_root,
        family=rename.family,
        module_name=rename.previous_name,
        container=rename.container,
    )
    target_identity = _module_directory_state(
        source_root,
        family=rename.family,
        module_name=rename.target_name,
        container=rename.container,
    )
    expected = rename.directory_identity
    if previous_identity == expected and target_identity is None:
        return
    if previous_identity is None and target_identity == expected and rename.state in {"applying", "applied"}:
        _rename_module_directory(
            source_root,
            family=rename.family,
            source_name=rename.target_name,
            target_name=rename.previous_name,
            target_object_id=rename.previous_object_id,
            container=rename.container,
            expected_source_identity=expected,
        )
        return
    raise ValueError("Source draft crash recovery stopped because the Registry folder changed " "outside ParaDev. The existing folders were preserved.")


def _remove_registry_directory_tree(
    source_root: Path,
    *,
    family: str,
    name: str,
    container: Literal["modules", "collections"],
    expected_identity: tuple[int, int],
) -> None:
    """Remove one exact quarantined Registry directory without following it."""

    if _uses_win32_module_mutation_authority():
        try:
            authority = Win32DirectoryAuthority.open(source_root, create=False)
        except (
            OSError,
            Win32FilesystemUnavailable,
            Win32UnsafePathError,
        ) as error:
            raise ValueError(f"Source recovery cannot retain collection root: {source_root}.") from error
        try:
            metadata = authority.entry_metadata((container, family, name))
            if metadata is None:
                return
            if not metadata.is_directory or metadata.identity != expected_identity:
                raise ValueError("Source recovery quarantine changed outside ParaDev; it was preserved.")
            authority.remove_directory_tree(
                (container, family, name),
                expected_identity=expected_identity,
            )
        finally:
            authority.close()
        return
    family_fd = _open_registry_family_fd(
        source_root,
        family,
        container=container,
    )
    try:
        try:
            metadata = os.stat(name, dir_fd=family_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        if (
            not stat.S_ISDIR(metadata.st_mode)
            or (
                metadata.st_dev,
                metadata.st_ino,
            )
            != expected_identity
        ):
            raise ValueError("Source recovery quarantine changed outside ParaDev; it was preserved.")
        _remove_directory_tree_at(family_fd, name)
        _fsync_source_draft_directory(family_fd)
    except ValueError:
        raise
    except OSError as error:
        raise ValueError("Source recovery could not finish removing its collection quarantine.") from error
    finally:
        _close_module_descriptor(family_fd)


def _finalize_committed_source_draft_rename(
    project_root: Path,
    rename: SourceDraftRecoveryRename | None,
) -> None:
    """Finish irreversible cleanup owned by a committed source transaction."""

    if rename is None or rename.operation == "rename":
        return
    source_root = project_root if rename.source_root == "." else project_root / PurePosixPath(rename.source_root)
    previous_identity = _module_directory_state(
        source_root,
        family=rename.family,
        module_name=rename.previous_name,
        container=rename.container,
    )
    target_identity = _module_directory_state(
        source_root,
        family=rename.family,
        module_name=rename.target_name,
        container=rename.container,
    )
    if previous_identity is not None:
        raise ValueError("Committed collection removal found the original descriptor again; " "ParaDev preserved both paths.")
    if target_identity is None:
        return
    if target_identity != rename.directory_identity:
        raise ValueError("Committed collection removal quarantine changed outside ParaDev; " "it was preserved.")
    _remove_registry_directory_tree(
        source_root,
        family=rename.family,
        name=rename.target_name,
        container=rename.container,
        expected_identity=rename.directory_identity,
    )


def _restore_source_draft_recovery_file(
    project_root: Path,
    item: SourceDraftRecoveryFile,
    *,
    recovery_authority: "AnchoredDirectory",
    root_identity: tuple[int, int],
) -> None:
    """Restore one journal-owned after-state to its exact before-state."""

    path = project_root / PurePosixPath(item.path)
    displaced_path = project_root / PurePosixPath(item.displaced) if item.displaced is not None else None
    displaced = (
        _source_draft_file_state(
            project_root,
            displaced_path,
            root_identity=root_identity,
        )
        if displaced_path is not None
        else _SourceDraftFileState(exists=False)
    )
    if displaced.exists and not _source_draft_recovery_state_owned(
        displaced,
        item,
    ):
        raise ValueError("Source draft crash recovery stopped because its private " f"displacement changed outside ParaDev: {displaced_path}.")
    current = _source_draft_file_state(
        project_root,
        path,
        root_identity=root_identity,
    )
    if item.state == "pending":
        if displaced.exists or not _source_draft_state_matches_before(
            current,
            item,
        ):
            raise ValueError("Source draft crash recovery stopped because a pending file " f"changed outside ParaDev: {path}.")
        return
    if _source_draft_state_matches_before(current, item):
        if displaced_path is not None:
            _unlink_source_draft_recovery_owned_file(
                project_root,
                displaced_path,
                displaced,
                root_identity=root_identity,
            )
        return
    current_matches_after = _source_draft_state_matches_after(
        current,
        item,
    )
    interrupted_displacement = not current.exists and item.backup is not None and displaced.exists
    if not current_matches_after and not interrupted_displacement:
        raise ValueError("Source draft crash recovery stopped because a file changed outside " f"ParaDev: {path}. The newer file was preserved.")
    if item.backup is None:
        if current.exists and displaced_path is not None and displaced.exists:
            _unlink_source_draft_recovery_owned_file(
                project_root,
                displaced_path,
                displaced,
                root_identity=root_identity,
            )
        _remove_source_draft_file(
            project_root,
            path,
            root_identity=root_identity,
            expected_content_sha256=item.after_sha256,
            displaced_name=(displaced_path.name if displaced_path is not None else None),
        )
        return
    backup = recovery_authority.read_bytes(item.backup)
    if backup is None or len(backup) != item.size or hashlib.sha256(backup).hexdigest() != item.before_sha256:
        raise ValueError(f"Source draft crash recovery backup is missing or changed: {item.backup}.")
    if current.exists and displaced_path is not None and displaced.exists:
        _unlink_source_draft_recovery_owned_file(
            project_root,
            displaced_path,
            displaced,
            root_identity=root_identity,
        )
        displaced = _SourceDraftFileState(exists=False)
    _write_source_draft_content(
        project_root,
        path,
        backup,
        require_existing=False,
        root_identity=root_identity,
        expected_revision=(_SOURCE_DRAFT_EXPECTED_ABSENT if not current.exists else None),
        expected_content_sha256=(current.content_sha256 if current.exists else None),
        mode=item.mode,
        displaced_name=(displaced_path.name if displaced_path is not None else None),
    )
    if displaced_path is not None and displaced.exists:
        _unlink_source_draft_recovery_owned_file(
            project_root,
            displaced_path,
            displaced,
            root_identity=root_identity,
        )


def _clear_source_draft_recovery(
    authority: "AnchoredDirectory",
    journal: SourceDraftRecoveryJournal,
) -> None:
    """Delete only files named and owned by one validated journal."""

    for item in journal.files:
        if item.backup is not None:
            authority.delete_file(item.backup, exact_spelling=True)
    authority.delete_file(
        "recovery.json",
        exact_spelling=True,
    )
    if not authority.is_empty():
        raise ValueError("Source draft recovery contains unowned files; ParaDev preserved " f"them at {authority.requested_path}.")


def _require_source_draft_recovery_displacements_absent(
    project_root: Path,
    journal: SourceDraftRecoveryJournal,
    *,
    root_identity: tuple[int, int],
) -> None:
    """Reject a pre-mutation collision with any journal-owned private name."""

    for item in journal.files:
        if item.displaced is None:
            continue
        path = project_root / PurePosixPath(item.displaced)
        state = _source_draft_file_state(
            project_root,
            path,
            root_identity=root_identity,
        )
        if not state.exists:
            continue
        raise ValueError(f"Source draft recovery found a displacement before mutation: {path}.")


@contextmanager
def _open_source_draft_recovery_directory(
    recovery_root: Path,
    *,
    create: bool = True,
) -> Iterator["AnchoredDirectory"]:
    """Open hidden recovery storage with source-authoring diagnostics."""

    try:
        with open_anchored_directory(
            recovery_root,
            create=create,
        ) as authority:
            yield authority
    except ValueError as error:
        message = str(error)
        if message.startswith(
            (
                "Generated publication root crosses",
                "Generated publication root changed",
            )
        ):
            raise ValueError("Source draft project root changed or traverses a symlink while " f"ParaDev retained recovery data: {recovery_root}.") from error
        raise


def _recover_source_draft_transaction(
    project_root: Path,
    *,
    root_identity: tuple[int, int],
) -> bool:
    """Recover one interrupted hidden source transaction when safely owned."""

    recovery_root = Path(source_draft_recovery_root(str(project_root)))
    try:
        authority_context = _open_source_draft_recovery_directory(
            recovery_root,
            create=False,
        )
        with authority_context as authority:
            journal = read_source_draft_recovery(authority)
            if journal is None:
                if authority.is_empty():
                    return False
                raise ValueError("Source draft recovery data is incomplete. ParaDev preserved " f"the private transaction at {recovery_root}.")
            if journal.project_root_identity != root_identity:
                raise ValueError("Source draft recovery belongs to a different project-root " f"identity. ParaDev preserved it at {recovery_root}.")
            if journal.phase in {"preparing", "committed"}:
                if journal.phase == "preparing":
                    _require_source_draft_recovery_displacements_absent(
                        project_root,
                        journal,
                        root_identity=root_identity,
                    )
                else:
                    _finalize_committed_source_draft_rename(
                        project_root,
                        journal.rename,
                    )
                _clear_source_draft_recovery(authority, journal)
                return journal.phase == "committed"
            if journal.rename is not None:
                _recover_source_draft_rename(project_root, journal.rename)
            for item in reversed(journal.files):
                _restore_source_draft_recovery_file(
                    project_root,
                    item,
                    recovery_authority=authority,
                    root_identity=root_identity,
                )
            _clear_source_draft_recovery(authority, journal)
            return True
    except FileNotFoundError:
        return False
    except ValueError:
        raise
    except OSError as error:
        raise ValueError("Source draft recovery data could not be retained safely at " f"{recovery_root}.") from error


@contextmanager
def _open_diagram_module_recovery_directory(
    recovery_root: Path,
    *,
    create: bool = True,
) -> Iterator["AnchoredDirectory"]:
    """Open the fixed compound-module recovery directory without following links."""

    try:
        with open_anchored_directory(recovery_root, create=create) as authority:
            yield authority
    except ValueError as error:
        message = str(error)
        if message.startswith(
            (
                "Generated publication root crosses",
                "Generated publication root changed",
            )
        ):
            raise ValueError("Diagram module project root changed or traverses a symlink while " f"ParaDev retained recovery data: {recovery_root}.") from error
        raise


def _prepare_diagram_module_recovery(
    project: Project,
    *,
    source_root: Path,
    rows: Sequence[Mapping[str, object]],
    rendered_by_index: Sequence[Sequence[Mapping[str, object]]],
    source_edits: Sequence[Mapping[str, object]],
) -> DiagramModuleRecoveryJournal | None:
    """Persist exact ownership before a compound child-module transaction starts."""

    created = [(index, row) for index, row in enumerate(rows) if row.get("status") == "create"]
    if not source_edits or not created:
        return None
    if len(created) != 1:
        raise ValueError("Compound diagram authoring must create exactly one standalone module.")
    index, row = created[0]
    root, root_identity = _source_draft_root_identity(project.root)
    try:
        relative_source_root = source_root.relative_to(root).as_posix()
    except ValueError as error:
        raise ValueError("Compound diagram source root must be inside the project root.") from error
    relative_source_root = relative_source_root or "."

    from paradev.sdk.templates import _normalized_scaffold_payload

    files: list[DiagramModuleRecoveryFile] = []
    seen_files: set[str] = set()
    for item in rendered_by_index[index]:
        relative_path = item.get("relative_module_path")
        content = item.get("content")
        if not isinstance(relative_path, str) or not isinstance(content, str):
            raise ValueError("Compound diagram scaffold files require string paths and content.")
        if relative_path in seen_files:
            raise ValueError(f"Compound diagram scaffold repeats a file path: {relative_path}.")
        seen_files.add(relative_path)
        payload = _normalized_scaffold_payload(content)
        files.append(
            DiagramModuleRecoveryFile(
                path=relative_path,
                size=len(payload),
                sha256=hashlib.sha256(payload).hexdigest(),
            )
        )

    sources: list[DiagramModuleRecoverySource] = []
    changed = False
    for item in source_edits:
        path = item.get("path")
        text = item.get("text")
        expected_digest = item.get("expected_content_sha256")
        if not isinstance(path, Path) or not isinstance(text, str) or not isinstance(expected_digest, str):
            raise ValueError("Compound diagram source edits require a path, text, and expected digest.")
        try:
            relative_path = path.relative_to(root).as_posix()
        except ValueError as error:
            raise ValueError(f"Compound diagram source is outside the project root: {path}.") from error
        before = _source_draft_file_state(
            root,
            path,
            root_identity=root_identity,
        )
        if not before.exists or before.content_sha256 != expected_digest:
            raise ValueError(f"Compound diagram source changed before recovery was prepared: {path}.")
        payload = text.encode("utf-8")
        after_digest = hashlib.sha256(payload).hexdigest()
        changed = changed or (before.size != len(payload) or before.content_sha256 != after_digest)
        sources.append(
            DiagramModuleRecoverySource(
                path=relative_path,
                before_size=before.size,
                before_sha256=expected_digest,
                after_size=len(payload),
                after_sha256=after_digest,
            )
        )
    if not changed:
        return None

    recovery_root = Path(diagram_module_recovery_root(str(root)))
    journal = DiagramModuleRecoveryJournal(
        transaction_id=uuid4().hex,
        project_root_identity=root_identity,
        source_root=relative_source_root,
        family=str(row["family"]),
        object_id=str(row["object_id"]),
        folder_name=str(row["folder_name"]),
        files=tuple(files),
        sources=tuple(sources),
    )
    with _open_diagram_module_recovery_directory(recovery_root) as authority:
        existing = read_diagram_module_recovery(authority)
        if existing is not None or not authority.is_empty():
            raise ValueError("A previous diagram module transaction still requires recovery at " f"{recovery_root}.")
        write_diagram_module_recovery(authority, journal)
    return journal


def _diagram_module_source_state(
    root: Path,
    journal: DiagramModuleRecoveryJournal,
) -> Literal["before", "after"]:
    """Classify every guarded parent source as one atomic journal state."""

    before = True
    after = True
    for item in journal.sources:
        state = _source_draft_file_state(
            root,
            root / PurePosixPath(item.path),
            root_identity=journal.project_root_identity,
        )
        before = before and (state.exists and state.size == item.before_size and state.content_sha256 == item.before_sha256)
        after = after and (state.exists and state.size == item.after_size and state.content_sha256 == item.after_sha256)
    if after and not before:
        return "after"
    if before:
        return "before"
    raise ValueError("Diagram module recovery found mixed or externally changed parent sources.")


def _clear_diagram_module_recovery(
    authority: "AnchoredDirectory",
    recovery_root: Path,
) -> None:
    authority.delete_file("recovery.json", exact_spelling=True)
    if not authority.is_empty():
        raise ValueError("Diagram module recovery contains unowned files; ParaDev preserved " f"them at {recovery_root}.")


def _recover_diagram_module_transaction(project: Project) -> bool:
    """Reconcile an interrupted compound child-module transaction fail closed."""

    root, root_identity = _source_draft_root_identity(project.root)
    recovery_root = Path(diagram_module_recovery_root(str(root)))
    try:
        with _open_diagram_module_recovery_directory(
            recovery_root,
            create=False,
        ) as authority:
            journal = read_diagram_module_recovery(authority)
            if journal is None:
                if authority.is_empty():
                    return False
                raise ValueError("Diagram module recovery data is incomplete. ParaDev preserved " f"the private transaction at {recovery_root}.")
            if journal.project_root_identity != root_identity:
                raise ValueError("Diagram module recovery belongs to a different project-root " f"identity. ParaDev preserved it at {recovery_root}.")
            source_state = _diagram_module_source_state(root, journal)
            from paradev.sdk.templates import _recover_scaffold_batch_anchored

            _recover_scaffold_batch_anchored(
                project_root=root,
                source_root=root / PurePosixPath(journal.source_root),
                family=journal.family,
                folder_name=journal.folder_name,
                files=tuple((item.path, item.size, item.sha256) for item in journal.files),
                transaction_id=journal.transaction_id,
                keep_module=source_state == "after",
            )
            _clear_diagram_module_recovery(authority, recovery_root)
            return True
    except FileNotFoundError:
        return False
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(
            "Diagram module recovery could not safely reconcile the child module; " f"ParaDev preserved recovery data at {recovery_root}: {error}."
        ) from error


def _recover_project_source_transactions(project: Project) -> bool:
    """Recover interrupted authoring roots before any project build reads them."""

    recovered = False
    roots = {
        project.root,
        *(source_root for source_root in project.source_roots if not _build_path_contains(project.root, source_root)),
    }
    for candidate in sorted(roots, key=str):
        root, identity = _source_draft_root_identity(candidate)
        recovered = (
            _recover_source_draft_transaction(
                root,
                root_identity=identity,
            )
            or recovered
        )
    return _recover_diagram_module_transaction(project) or recovered


def _source_draft_recovery_rename(
    project_root: Path,
    prepared: _PreparedSourceRename | None,
) -> SourceDraftRecoveryRename | None:
    if prepared is None:
        return None
    try:
        source_root = prepared.source_root.relative_to(project_root).as_posix()
    except ValueError as error:
        raise ValueError("Folder rename source root is outside the source transaction root.") from error
    if not source_root:
        source_root = "."
    operation: Literal["rename", "remove"] = "rename"
    if isinstance(prepared, _PreparedModuleRename):
        _family, previous_object_id = _module_id_parts(
            prepared.previous_module.module_id,
        )
        family = prepared.previous_module.family
        container: Literal["modules", "collections"] = "modules"
    else:
        previous_object_id = prepared.previous_collection.collection_id
        family = prepared.previous_collection.family
        container = "collections"
        if isinstance(prepared, _PreparedCollectionRemoval):
            operation = "remove"
    return SourceDraftRecoveryRename(
        source_root=source_root,
        family=family,
        previous_name=prepared.previous_root.name,
        target_name=prepared.root.name,
        previous_object_id=previous_object_id,
        target_object_id=prepared.target_object_id,
        directory_identity=prepared.directory_identity,
        operation=operation,
        container=container,
    )


def _source_draft_recovery_journal(
    project_root: Path,
    *,
    root_identity: tuple[int, int],
    backups: Mapping[Path, _SourceDraftBackup],
    edits: Sequence[Mapping[str, object]],
    replacements: Sequence[Mapping[str, object]],
    removals: Sequence[Mapping[str, object]],
    prepared_rename: _PreparedSourceRename | None,
) -> SourceDraftRecoveryJournal:
    transaction_id = uuid4().hex
    after: dict[Path, _SourceDraftFileState] = {}
    for item in edits:
        path = cast(Path, item["path"])
        payload = str(item["text"]).encode("utf-8")
        after[path] = _SourceDraftFileState(
            exists=True,
            size=len(payload),
            content_sha256=hashlib.sha256(payload).hexdigest(),
        )
    for item in replacements:
        path = cast(Path, item["path"])
        payload = bytes(item["content"])
        after[path] = _SourceDraftFileState(
            exists=True,
            size=len(payload),
            content_sha256=hashlib.sha256(payload).hexdigest(),
        )
    for item in removals:
        path = cast(Path, item["path"])
        after[path] = _SourceDraftFileState(exists=False)
    files: list[SourceDraftRecoveryFile] = []
    for index, backup in enumerate(backups.values()):
        intended = after[backup.path]
        relative_path = backup.path.relative_to(project_root).as_posix()
        files.append(
            SourceDraftRecoveryFile(
                path=relative_path,
                backup=(f"backups/{index:04d}.backup" if backup.backup_path is not None else None),
                displaced=(
                    None
                    if _uses_win32_source_draft_authority()
                    else source_draft_recovery_displaced_path(
                        relative_path,
                        transaction_id,
                        index,
                    )
                ),
                mode=backup.mode,
                size=backup.size,
                before_sha256=backup.content_sha256,
                after_exists=intended.exists,
                after_size=intended.size,
                after_sha256=intended.content_sha256,
            )
        )
    return SourceDraftRecoveryJournal(
        transaction_id=transaction_id,
        project_root_identity=root_identity,
        phase="preparing",
        files=tuple(files),
        rename=_source_draft_recovery_rename(
            project_root,
            prepared_rename,
        ),
    )


def _source_draft_recovery_displaced_name(
    project_root: Path,
    path: Path,
    item: SourceDraftRecoveryFile,
) -> str | None:
    """Return one validated journal-owned adjacent displacement filename."""

    if item.displaced is None:
        return None
    displaced = project_root / PurePosixPath(item.displaced)
    if displaced.parent != path.parent:
        raise ValueError("Source draft recovery displacement is not adjacent to its target.")
    return displaced.name


def _apply_source_draft_mutations(
    project_root: Path,
    *,
    edits: Sequence[Mapping[str, object]],
    replacements: Sequence[Mapping[str, object]],
    removals: Sequence[Mapping[str, object]],
    root_identity: tuple[int, int],
    validate: Callable[[], None] | None = None,
    finalize: Callable[[], None] | None = None,
    prepared_rename: _PreparedSourceRename | None = None,
) -> None:
    """Apply one draft request through a durable guarded transaction."""

    mutation_paths: list[Path] = []
    for item in (*edits, *replacements):
        path = item.get("path")
        if not isinstance(path, Path):
            raise ValueError("Source draft path did not resolve to a filesystem path.")
        mutation_paths.append(path)
    for removal in removals:
        path = removal.get("path")
        if not isinstance(path, Path):
            raise ValueError("Source removal path did not resolve to a filesystem path.")
        mutation_paths.append(path)
    _recover_source_draft_transaction(
        project_root,
        root_identity=root_identity,
    )
    staging_root = Path(tempfile.mkdtemp(prefix="paradev-source-draft-")).resolve()
    transaction_token = _SOURCE_DRAFT_TRANSACTION_ACTIVE.set(True)
    recovery_root = Path(source_draft_recovery_root(str(project_root)))
    backups: dict[Path, _SourceDraftBackup] = {}
    mutations: list[_SourceDraftMutation] = []
    try:
        backup_bytes = 0
        for index, path in enumerate(mutation_paths):
            backup = _backup_source_draft_path(
                project_root,
                path,
                backup_root=staging_root,
                index=index,
                root_identity=root_identity,
                max_bytes=MAX_PROJECT_SOURCE_DRAFT_BACKUP_BYTES - backup_bytes,
            )
            backups[path] = backup
            backup_bytes += backup.size
        journal = _source_draft_recovery_journal(
            project_root,
            root_identity=root_identity,
            backups=backups,
            edits=edits,
            replacements=replacements,
            removals=removals,
            prepared_rename=prepared_rename,
        )
        with _open_source_draft_recovery_directory(recovery_root) as authority:
            if not authority.is_empty():
                raise ValueError("Source draft recovery directory is not empty after recovery: " f"{recovery_root}.")
            write_source_draft_recovery(authority, journal)
            for index, backup in enumerate(backups.values()):
                if backup.backup_path is not None:
                    authority.publish_file(
                        f"backups/{index:04d}.backup",
                        backup.backup_path,
                        replace=False,
                    )
            journal = replace(journal, phase="applying")
            write_source_draft_recovery(authority, journal)
        for index, edit in enumerate(edits):
            journal = journal.with_file_state(index, "applying")
            with _open_source_draft_recovery_directory(
                recovery_root,
                create=False,
            ) as authority:
                write_source_draft_recovery(authority, journal)
            path = edit["path"]
            if not isinstance(path, Path):
                raise ValueError("Source edit path did not resolve to a filesystem path.")
            mutation = _write_source_draft_content(
                project_root,
                path,
                str(edit["text"]).encode("utf-8"),
                require_existing=True,
                root_identity=root_identity,
                expected_revision=edit.get("expected_revision"),
                expected_content_sha256=edit.get("expected_content_sha256"),
                displaced_name=_source_draft_recovery_displaced_name(
                    project_root,
                    path,
                    journal.files[index],
                ),
            )
            mutations.append(mutation)
            journal = journal.with_file_state(index, "applied")
            with _open_source_draft_recovery_directory(
                recovery_root,
                create=False,
            ) as authority:
                write_source_draft_recovery(authority, journal)
        replacement_offset = len(edits)
        for replacement_index, replacement in enumerate(replacements):
            index = replacement_offset + replacement_index
            journal = journal.with_file_state(index, "applying")
            with _open_source_draft_recovery_directory(
                recovery_root,
                create=False,
            ) as authority:
                write_source_draft_recovery(authority, journal)
            path = replacement["path"]
            if not isinstance(path, Path):
                raise ValueError("Source replacement path did not resolve to a filesystem path.")
            mutation = _write_source_draft_content(
                project_root,
                path,
                bytes(replacement["content"]),
                require_existing=False,
                root_identity=root_identity,
                expected_revision=replacement.get("expected_revision"),
                expected_content_sha256=replacement.get("expected_content_sha256"),
                displaced_name=_source_draft_recovery_displaced_name(
                    project_root,
                    path,
                    journal.files[index],
                ),
            )
            mutations.append(mutation)
            journal = journal.with_file_state(index, "applied")
            with _open_source_draft_recovery_directory(
                recovery_root,
                create=False,
            ) as authority:
                write_source_draft_recovery(authority, journal)
        removal_offset = len(edits) + len(replacements)
        for removal_index, removal in enumerate(removals):
            index = removal_offset + removal_index
            journal = journal.with_file_state(index, "applying")
            with _open_source_draft_recovery_directory(
                recovery_root,
                create=False,
            ) as authority:
                write_source_draft_recovery(authority, journal)
            path = removal.get("path")
            if not isinstance(path, Path):
                raise ValueError("Source removal path did not resolve to a filesystem path.")
            mutations.append(
                _remove_source_draft_file(
                    project_root,
                    path,
                    root_identity=root_identity,
                    expected_revision=removal.get("expected_revision"),
                    expected_content_sha256=removal.get("expected_content_sha256"),
                    displaced_name=_source_draft_recovery_displaced_name(
                        project_root,
                        path,
                        journal.files[index],
                    ),
                )
            )
            journal = journal.with_file_state(index, "applied")
            with _open_source_draft_recovery_directory(
                recovery_root,
                create=False,
            ) as authority:
                write_source_draft_recovery(authority, journal)
        if validate is not None:
            validate()
        if finalize is not None:
            if journal.rename is not None:
                journal = journal.with_rename_state("applying")
                with _open_source_draft_recovery_directory(
                    recovery_root,
                    create=False,
                ) as authority:
                    write_source_draft_recovery(authority, journal)
            finalize()
            if journal.rename is not None:
                journal = journal.with_rename_state("applied")
                with _open_source_draft_recovery_directory(
                    recovery_root,
                    create=False,
                ) as authority:
                    write_source_draft_recovery(authority, journal)
        journal = replace(journal, phase="committed")
        with _open_source_draft_recovery_directory(
            recovery_root,
            create=False,
        ) as authority:
            write_source_draft_recovery(authority, journal)
    except Exception as mutation_error:
        if "journal" in locals():
            try:
                journal = replace(journal, phase="recovery_required")
                with _open_source_draft_recovery_directory(
                    recovery_root,
                    create=False,
                ) as authority:
                    write_source_draft_recovery(authority, journal)
            except Exception:
                pass
        rollback_errors: list[Exception] = []
        if "journal" in locals() and journal.rename is not None:
            try:
                _recover_source_draft_rename(project_root, journal.rename)
            except Exception as rollback_error:
                rollback_errors.append(rollback_error)
        recovery_files = {project_root / PurePosixPath(item.path): item for item in journal.files} if "journal" in locals() else {}
        for mutation in reversed(mutations):
            backup = backups[mutation.path]
            recovery_file = recovery_files.get(mutation.path)
            displaced_name = (
                _source_draft_recovery_displaced_name(
                    project_root,
                    mutation.path,
                    recovery_file,
                )
                if recovery_file is not None
                else None
            )
            try:
                if backup.backup_path is None:
                    _remove_source_draft_file(
                        project_root,
                        mutation.path,
                        root_identity=root_identity,
                        missing_ok=True,
                        expected_mutation=mutation,
                        displaced_name=displaced_name,
                    )
                else:
                    _write_source_draft_content(
                        project_root,
                        mutation.path,
                        backup.backup_path,
                        require_existing=False,
                        root_identity=root_identity,
                        mode=backup.mode,
                        expected_mutation=mutation,
                        displaced_name=displaced_name,
                    )
            except Exception as rollback_error:
                rollback_errors.append(rollback_error)
        if isinstance(
            mutation_error,
            _SourceDraftDisplacedRecoveryIncomplete,
        ):
            rollback_errors.append(mutation_error)
        if rollback_errors:
            raise _SourceDraftRollbackIncomplete(
                recovery_path=recovery_root,
                mutation_error=mutation_error,
                rollback_errors=rollback_errors,
                possibly_modified_paths=[mutation.path for mutation in mutations],
            ) from mutation_error
        if "journal" in locals():
            with _open_source_draft_recovery_directory(
                recovery_root,
                create=False,
            ) as authority:
                _clear_source_draft_recovery(authority, journal)
        raise
    else:
        _finalize_committed_source_draft_rename(
            project_root,
            journal.rename,
        )
        with _open_source_draft_recovery_directory(
            recovery_root,
            create=False,
        ) as authority:
            _clear_source_draft_recovery(authority, journal)
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
        _SOURCE_DRAFT_TRANSACTION_ACTIVE.reset(transaction_token)


def _win32_source_draft_file_identity(
    metadata: Win32FileMetadata,
) -> tuple[int, int, int, int]:
    return (
        metadata.volume_serial,
        metadata.file_id,
        metadata.size,
        metadata.mtime_ns,
    )


def _validate_win32_source_draft_mutation(
    parent_identity: tuple[int, int],
    path: Path,
    mutation: _SourceDraftMutation,
    snapshot: Win32FileSnapshot | None,
) -> None:
    """Reject Windows rollback when a target no longer matches ParaDev's write."""

    if mutation.path != path:
        raise ValueError("Source draft mutation token targets a different path.")
    if parent_identity != mutation.parent_identity:
        raise ValueError(f"Source draft rollback conflict: the parent directory changed after ParaDev updated {path}.")
    if snapshot is None:
        if mutation.file_identity is None:
            return
        raise ValueError(f"Source draft rollback conflict: {path} was removed after ParaDev updated it.")
    if mutation.file_identity is None:
        raise ValueError(f"Source draft rollback conflict: {path} was recreated after ParaDev removed it.")
    if snapshot.metadata.is_directory or _win32_source_draft_file_identity(snapshot.metadata) != mutation.file_identity:
        raise ValueError(f"Source draft rollback conflict: {path} changed after ParaDev updated it.")
    if snapshot.content_sha256 != mutation.content_sha256:
        raise ValueError(f"Source draft rollback conflict: {path} changed while it was verified.")


def _validate_win32_source_draft_guard(
    parent_identity: tuple[int, int],
    snapshot: Win32FileSnapshot | None,
    *,
    path: Path,
    require_existing: bool,
    removal: bool,
    expected_revision: object,
    expected_content_sha256: object,
    expected_mutation: _SourceDraftMutation | None,
) -> None:
    if expected_mutation is not None:
        _validate_win32_source_draft_mutation(
            parent_identity,
            path,
            expected_mutation,
            snapshot,
        )
        return
    if snapshot is None:
        if expected_revision is _SOURCE_DRAFT_EXPECTED_ABSENT:
            return
        if expected_revision is not None or expected_content_sha256 is not None:
            raise ValueError(f"Source draft conflict: {path} changed or disappeared after the draft was opened.")
        if require_existing:
            if removal:
                return
            raise ValueError(f"Source draft target changed before it could be written: {path}.")
        return
    if snapshot.metadata.is_directory:
        label = "removal target" if removal else "target"
        raise ValueError(f"Source draft {label} is not a regular file: {path}.")
    if expected_revision is not None:
        if (
            expected_revision is _SOURCE_DRAFT_EXPECTED_ABSENT
            or not isinstance(expected_revision, tuple)
            or len(expected_revision) != 2
            or (snapshot.metadata.size, snapshot.metadata.mtime_ns) != expected_revision
        ):
            raise ValueError(f"Source draft conflict: {path} changed after the draft was " "opened. Refresh or restore the draft before applying.")
    if expected_content_sha256 is not None:
        _validate_source_draft_expected_content_sha256(expected_content_sha256)
        if snapshot.content_sha256 != expected_content_sha256:
            raise ValueError(f"Source draft conflict: {path} content changed after the " "draft was opened. Refresh or restore the draft before applying.")


def _win32_source_draft_recovery_path(path: Path, error: Win32DisplacedRecoveryError) -> Path:
    return path.parent / error.displaced_path.name


def _backup_win32_source_draft_path(
    project_root: Path,
    path: Path,
    *,
    backup_root: Path,
    index: int,
    root_identity: tuple[int, int],
    max_bytes: int,
) -> _SourceDraftBackup:
    parts = _win32_source_draft_parts(project_root, path)
    try:
        with _open_win32_source_draft_authority(project_root, root_identity=root_identity) as authority:
            snapshot = authority.read_file_snapshot(
                parts,
                max_bytes=max_bytes,
            )
    except Win32FileSizeError as error:
        raise ValueError("Source draft recovery data would exceed the " f"{MAX_PROJECT_SOURCE_DRAFT_BACKUP_BYTES}-byte transaction limit.") from error
    except Win32UnsafePathError as error:
        raise ValueError(f"Source draft target could not be backed up safely: {path}.") from error
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source draft target could not be backed up safely: {path}.") from error
    if snapshot is None:
        return _SourceDraftBackup(
            path=path,
            backup_path=None,
            mode=None,
            size=0,
            content_sha256=None,
        )
    if snapshot.metadata.is_directory or snapshot.content is None:
        raise ValueError(f"Source draft target is not a regular file: {path}.")
    if snapshot.metadata.size > max_bytes:
        raise ValueError("Source draft recovery data would exceed the " f"{MAX_PROJECT_SOURCE_DRAFT_BACKUP_BYTES}-byte transaction limit.")
    backup_path = backup_root / f"{index:04d}.backup"
    try:
        with backup_path.open("wb") as target:
            target.write(snapshot.content)
            target.flush()
            os.fsync(target.fileno())
    except OSError as error:
        raise ValueError(f"Source draft target could not be backed up safely: {path}.") from error
    return _SourceDraftBackup(
        path=path,
        backup_path=backup_path,
        mode=None,
        size=snapshot.metadata.size,
        content_sha256=snapshot.content_sha256,
    )


def _write_win32_source_draft_content(
    project_root: Path,
    path: Path,
    content: bytes | Path,
    *,
    require_existing: bool,
    root_identity: tuple[int, int],
    expected_revision: object,
    expected_content_sha256: object,
    expected_mutation: _SourceDraftMutation | None,
) -> _SourceDraftMutation:
    parts = _win32_source_draft_parts(project_root, path)
    try:
        payload = content.read_bytes() if isinstance(content, Path) else content
    except OSError as error:
        raise ValueError(f"Source draft path changed before it could be written safely: {path}.") from error

    def guard(
        parent_identity: tuple[int, int],
        snapshot: Win32FileSnapshot | None,
    ) -> None:
        _validate_win32_source_draft_guard(
            parent_identity,
            snapshot,
            path=path,
            require_existing=require_existing,
            removal=False,
            expected_revision=expected_revision,
            expected_content_sha256=expected_content_sha256,
            expected_mutation=expected_mutation,
        )

    try:
        with _open_win32_source_draft_authority(project_root, root_identity=root_identity) as authority:
            if expected_mutation is not None or expected_revision is not None or expected_content_sha256 is not None:
                parent_identity, written = authority.guarded_write_bytes(
                    parts,
                    payload,
                    guard=guard,
                )
            else:
                existing = authority.entry_metadata(parts)
                if require_existing and existing is None:
                    raise ValueError(f"Source draft target changed before it could be written: {path}.")
                if existing is not None and existing.is_directory:
                    raise ValueError(f"Source draft target is not a regular file: {path}.")
                parent_identity, written = authority.write_bytes_snapshot(
                    parts,
                    payload,
                    replace=True,
                )
    except Win32DisplacedRecoveryError as error:
        recovery_path = _win32_source_draft_recovery_path(path, error)
        if error.destination_exists:
            raise _SourceDraftDisplacedRecoveryIncomplete(
                (f"Source draft conflict: a newer file was preserved at {path}; " f"the displaced source remains at {recovery_path}."),
                target_path=path,
                recovery_path=recovery_path,
                destination_exists=True,
            ) from error
        raise _SourceDraftDisplacedRecoveryIncomplete(
            ("Source draft conflict recovery could not restore the " f"displaced target; it remains at {recovery_path}."),
            target_path=path,
            recovery_path=recovery_path,
            destination_exists=False,
        ) from error
    except Win32UnsafePathError as error:
        raise ValueError(f"Source draft path changed before it could be written safely: {path}.") from error
    except ValueError:
        raise
    except FileExistsError as error:
        raise ValueError(f"Source draft conflict: {path} changed while ParaDev was applying the draft.") from error
    except OSError as error:
        raise ValueError(f"Source draft path changed before it could be written safely: {path}.") from error
    return _SourceDraftMutation(
        path=path,
        parent_identity=parent_identity,
        file_identity=_win32_source_draft_file_identity(written.metadata),
        content_sha256=written.content_sha256,
    )


def _remove_win32_source_draft_file(
    project_root: Path,
    path: Path,
    *,
    root_identity: tuple[int, int],
    missing_ok: bool,
    expected_mutation: _SourceDraftMutation | None,
    expected_revision: object,
    expected_content_sha256: object,
) -> _SourceDraftMutation:
    parts = _win32_source_draft_parts(project_root, path)

    def guard(
        parent_identity: tuple[int, int],
        snapshot: Win32FileSnapshot | None,
    ) -> None:
        _validate_win32_source_draft_guard(
            parent_identity,
            snapshot,
            path=path,
            require_existing=not missing_ok,
            removal=True,
            expected_revision=expected_revision,
            expected_content_sha256=expected_content_sha256,
            expected_mutation=expected_mutation,
        )

    try:
        with _open_win32_source_draft_authority(project_root, root_identity=root_identity) as authority:
            parent_identity, _snapshot = authority.guarded_remove_file(
                parts,
                guard=guard,
                missing_ok=missing_ok,
            )
    except Win32DisplacedRecoveryError as error:
        recovery_path = _win32_source_draft_recovery_path(path, error)
        if error.destination_exists:
            raise _SourceDraftDisplacedRecoveryIncomplete(
                (f"Source draft conflict: a newer file was preserved at {path}; " f"the displaced source remains at {recovery_path}."),
                target_path=path,
                recovery_path=recovery_path,
                destination_exists=True,
            ) from error
        raise _SourceDraftDisplacedRecoveryIncomplete(
            ("Source draft removal failed and the displaced source " f"remains at {recovery_path}."),
            target_path=path,
            recovery_path=recovery_path,
            destination_exists=False,
        ) from error
    except Win32UnsafePathError as error:
        raise ValueError(f"Source draft path changed before it could be removed safely: {path}.") from error
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source draft path changed before it could be removed safely: {path}.") from error
    return _SourceDraftMutation(
        path=path,
        parent_identity=parent_identity,
        file_identity=None,
        content_sha256=None,
    )


def _backup_source_draft_path(
    project_root: Path,
    path: Path,
    *,
    backup_root: Path,
    index: int,
    root_identity: tuple[int, int],
    max_bytes: int,
) -> _SourceDraftBackup:
    """Copy one no-follow-verified source into a private recovery directory."""

    if _uses_win32_source_draft_authority():
        return _backup_win32_source_draft_path(
            project_root,
            path,
            backup_root=backup_root,
            index=index,
            root_identity=root_identity,
            max_bytes=max_bytes,
        )
    parent_fd = _open_source_draft_parent_fd(project_root, path, root_identity=root_identity)
    source_fd: int | None = None
    try:
        try:
            metadata = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return _SourceDraftBackup(
                path=path,
                backup_path=None,
                mode=None,
                size=0,
                content_sha256=None,
            )
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"Source draft target is not a regular file: {path}.")
        source_fd = os.open(
            path.name,
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
        opened = os.fstat(source_fd)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (
            metadata.st_dev,
            metadata.st_ino,
        ):
            raise ValueError(f"Source draft target changed before backup: {path}.")
        if opened.st_size > max_bytes:
            raise ValueError("Source draft recovery data would exceed the " f"{MAX_PROJECT_SOURCE_DRAFT_BACKUP_BYTES}-byte transaction limit.")
        backup_path = backup_root / f"{index:04d}.backup"
        digest = hashlib.sha256()
        with os.fdopen(source_fd, "rb", closefd=True) as source:
            source_fd = None
            with backup_path.open("wb") as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
                    digest.update(chunk)
                target.flush()
                os.fsync(target.fileno())
            after = os.fstat(source.fileno())
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
        ):
            raise ValueError(f"Source draft target changed while it was backed up: {path}.")
        return _SourceDraftBackup(
            path=path,
            backup_path=backup_path,
            mode=stat.S_IMODE(opened.st_mode),
            size=opened.st_size,
            content_sha256=digest.hexdigest(),
        )
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source draft target could not be backed up safely: {path}.") from error
    finally:
        if source_fd is not None:
            _close_module_descriptor(source_fd)
        _close_module_descriptor(parent_fd)


def _validate_source_draft_mutation(
    parent_fd: int,
    path: Path,
    mutation: _SourceDraftMutation,
    *,
    entry_name: str | None = None,
) -> None:
    """Reject rollback when a target no longer matches ParaDev's write."""

    if mutation.path != path:
        raise ValueError("Source draft mutation token targets a different path.")
    parent_metadata = os.fstat(parent_fd)
    if (parent_metadata.st_dev, parent_metadata.st_ino) != mutation.parent_identity:
        raise ValueError(f"Source draft rollback conflict: the parent directory changed after ParaDev updated {path}.")
    name = entry_name or path.name
    try:
        metadata = os.stat(
            name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        if mutation.file_identity is None:
            return
        raise ValueError(f"Source draft rollback conflict: {path} was removed after ParaDev updated it.") from None
    if mutation.file_identity is None:
        raise ValueError(f"Source draft rollback conflict: {path} was recreated after ParaDev removed it.")
    identity = (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
    )
    if not stat.S_ISREG(metadata.st_mode) or identity != mutation.file_identity:
        raise ValueError(f"Source draft rollback conflict: {path} changed after ParaDev updated it.")
    descriptor: int | None = None
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
        opened = os.fstat(descriptor)
        opened_identity = (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
        )
        if not stat.S_ISREG(opened.st_mode) or opened_identity != mutation.file_identity:
            raise ValueError(f"Source draft rollback conflict: {path} changed before it could be verified.")
        digest = hashlib.sha256()
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
        after = os.fstat(descriptor)
        after_identity = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        )
        if after_identity != mutation.file_identity or digest.hexdigest() != mutation.content_sha256:
            raise ValueError(f"Source draft rollback conflict: {path} changed while it was verified.")
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source draft rollback conflict: {path} could not be verified safely.") from error
    finally:
        if descriptor is not None:
            _close_module_descriptor(descriptor)


def _validate_source_draft_expected_state_at_parent(
    parent_fd: int,
    path: Path,
    expected_revision: object,
) -> None:
    if expected_revision is None:
        return
    try:
        metadata = os.stat(
            path.name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        if expected_revision is _SOURCE_DRAFT_EXPECTED_ABSENT:
            return
        raise ValueError(f"Source draft conflict: {path} changed or disappeared after the draft was opened.") from None
    if expected_revision is _SOURCE_DRAFT_EXPECTED_ABSENT:
        raise ValueError(f"Source draft conflict: {path} appeared after the draft was opened. " "Refresh or restore the draft before applying.")
    if (
        not stat.S_ISREG(metadata.st_mode)
        or not isinstance(expected_revision, tuple)
        or len(expected_revision) != 2
        or (metadata.st_size, metadata.st_mtime_ns) != expected_revision
    ):
        raise ValueError(f"Source draft conflict: {path} changed after the draft was opened. " "Refresh or restore the draft before applying.")


def _write_source_draft_chunk(descriptor: int, content: bytes) -> None:
    remaining = memoryview(content)
    while remaining:
        written = os.write(descriptor, remaining)
        if written < 1:
            raise OSError("Source draft write made no progress")
        remaining = remaining[written:]


def _fsync_source_draft_directory(descriptor: int) -> None:
    """Persist directory entries when the host filesystem supports it."""

    try:
        os.fsync(descriptor)
    except OSError as error:
        if error.errno not in {
            errno.EBADF,
            errno.EINVAL,
            getattr(errno, "ENOTSUP", errno.EINVAL),
        }:
            raise


def _validate_source_draft_expected_content_at_parent(
    parent_fd: int,
    path: Path,
    expected_content_sha256: object,
    *,
    entry_name: str | None = None,
) -> None:
    """Verify exact displaced source bytes through a retained parent."""

    if expected_content_sha256 is None:
        return
    expected = _validate_source_draft_expected_content_sha256(expected_content_sha256)
    name = entry_name or path.name
    descriptor: int | None = None
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError(f"Source draft conflict: {path} is not a regular file.")
        digest = hashlib.sha256()
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
        after = os.fstat(descriptor)
        if (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise ValueError(f"Source draft conflict: {path} changed while its exact " "content was verified.")
        if digest.hexdigest() != expected:
            raise ValueError(f"Source draft conflict: {path} content changed after the " "draft was opened. Refresh or restore the draft before applying.")
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source draft conflict: {path} exact content could not be verified safely.") from error
    finally:
        if descriptor is not None:
            _close_module_descriptor(descriptor)


def _require_source_draft_same_entry(
    parent_fd: int,
    path: Path,
    *,
    left_name: str,
    right_name: str,
) -> None:
    """Require two retained names to identify the same regular file."""

    try:
        left = os.stat(
            left_name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        right = os.stat(
            right_name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
    except OSError as error:
        raise ValueError(f"Source draft displacement changed before verification: {path}.") from error
    if not stat.S_ISREG(left.st_mode) or not stat.S_ISREG(right.st_mode) or (left.st_dev, left.st_ino) != (right.st_dev, right.st_ino):
        raise ValueError(f"Source draft displacement no longer owns its target: {path}.")


def _restore_source_draft_displacement(
    parent_fd: int,
    path: Path,
    *,
    quarantine_name: str,
    source_unlinked: bool,
    operation: str,
) -> None:
    """Restore one same-directory displacement without clobbering a newer file."""

    recovery_path = path.parent / quarantine_name
    if source_unlinked:
        try:
            os.link(
                quarantine_name,
                path.name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise _SourceDraftDisplacedRecoveryIncomplete(
                (f"Source draft {operation} preserved a newer file at {path}; " f"the displaced source remains at {recovery_path}."),
                target_path=path,
                recovery_path=recovery_path,
                destination_exists=True,
            ) from error
        except OSError as error:
            raise _SourceDraftDisplacedRecoveryIncomplete(
                (f"Source draft {operation} could not restore its target; " f"the displaced source remains at {recovery_path}."),
                target_path=path,
                recovery_path=recovery_path,
                destination_exists=False,
            ) from error
    try:
        _require_source_draft_same_entry(
            parent_fd,
            path,
            left_name=path.name,
            right_name=quarantine_name,
        )
        os.unlink(quarantine_name, dir_fd=parent_fd)
        _fsync_source_draft_directory(parent_fd)
    except _SourceDraftDisplacedRecoveryIncomplete:
        raise
    except Exception as error:
        raise _SourceDraftDisplacedRecoveryIncomplete(
            (f"Source draft {operation} preserved its displaced source at " f"{recovery_path}: {error}"),
            target_path=path,
            recovery_path=recovery_path,
            destination_exists=True,
        ) from error


def _install_guarded_source_draft_temporary(
    parent_fd: int,
    path: Path,
    temporary_name: str,
    *,
    expected_revision: object,
    expected_content_sha256: object,
    expected_mutation: _SourceDraftMutation | None,
    displaced_name: str | None,
) -> None:
    """Install a staged file without replacing a concurrently changed name."""

    quarantine_name = displaced_name or f".paradev-draft-{uuid4().hex}.previous"
    if quarantine_name in {"", ".", ".."} or "/" in quarantine_name or "\\" in quarantine_name:
        raise ValueError("Source draft displacement must be one exact filename.")
    quarantined = False
    source_unlinked = False
    try:
        try:
            os.link(
                path.name,
                quarantine_name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
            quarantined = True
        except FileNotFoundError:
            pass
        except FileExistsError as error:
            raise ValueError("Source draft recovery displacement is already occupied: " f"{path.parent / quarantine_name}.") from error

        if expected_mutation is not None:
            if expected_mutation.file_identity is None:
                if quarantined:
                    raise ValueError(f"Source draft rollback conflict: {path} was recreated after ParaDev removed it.")
            else:
                if not quarantined:
                    raise ValueError(f"Source draft rollback conflict: {path} was removed after ParaDev updated it.")
                _validate_source_draft_mutation(
                    parent_fd,
                    path,
                    expected_mutation,
                    entry_name=quarantine_name,
                )
        elif expected_revision is _SOURCE_DRAFT_EXPECTED_ABSENT:
            if quarantined:
                raise ValueError(f"Source draft conflict: {path} appeared after the draft was opened. " "Refresh or restore the draft before applying.")
        else:
            if not quarantined:
                raise ValueError(f"Source draft conflict: {path} changed or disappeared after the draft was opened.")
            metadata = os.stat(
                quarantine_name,
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError(f"Source draft conflict: {path} is not a regular file.")
            if expected_revision is not None and (
                not isinstance(expected_revision, tuple) or len(expected_revision) != 2 or (metadata.st_size, metadata.st_mtime_ns) != expected_revision
            ):
                raise ValueError(f"Source draft conflict: {path} changed after the draft was opened. " "Refresh or restore the draft before applying.")
            _validate_source_draft_expected_content_at_parent(
                parent_fd,
                path,
                expected_content_sha256,
                entry_name=quarantine_name,
            )

        if quarantined:
            _require_source_draft_same_entry(
                parent_fd,
                path,
                left_name=path.name,
                right_name=quarantine_name,
            )
            os.unlink(path.name, dir_fd=parent_fd)
            source_unlinked = True
        try:
            os.link(
                temporary_name,
                path.name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise ValueError(f"Source draft conflict: {path} changed while ParaDev was applying the draft.") from error
    except Exception:
        if quarantined:
            _restore_source_draft_displacement(
                parent_fd,
                path,
                quarantine_name=quarantine_name,
                source_unlinked=source_unlinked,
                operation="conflict recovery",
            )
        raise
    else:
        if quarantined:
            try:
                os.unlink(quarantine_name, dir_fd=parent_fd)
            except OSError as error:
                recovery_path = path.parent / quarantine_name
                raise _SourceDraftDisplacedRecoveryIncomplete(
                    ("Source draft write completed, but its displaced source " f"could not be cleaned at {recovery_path}."),
                    target_path=path,
                    recovery_path=recovery_path,
                    destination_exists=True,
                ) from error


def _write_source_draft_content(
    project_root: Path,
    path: Path,
    content: bytes | Path,
    *,
    require_existing: bool,
    root_identity: tuple[int, int],
    expected_revision: object = None,
    expected_content_sha256: object = None,
    expected_mutation: _SourceDraftMutation | None = None,
    mode: int | None = None,
    displaced_name: str | None = None,
) -> _SourceDraftMutation:
    """Atomically write one draft without following a replaced directory."""

    if _uses_win32_source_draft_authority():
        return _write_win32_source_draft_content(
            project_root,
            path,
            content,
            require_existing=require_existing,
            root_identity=root_identity,
            expected_revision=expected_revision,
            expected_content_sha256=expected_content_sha256,
            expected_mutation=expected_mutation,
        )
    parent_fd = _open_source_draft_parent_fd(project_root, path, root_identity=root_identity)
    parent_metadata = os.fstat(parent_fd)
    parent_identity = (parent_metadata.st_dev, parent_metadata.st_ino)
    temporary_name = f".paradev-draft-{uuid4().hex}.tmp"
    temporary_fd: int | None = None
    temporary_exists = False
    try:
        if expected_mutation is not None:
            _validate_source_draft_mutation(
                parent_fd,
                path,
                expected_mutation,
            )
        existing_mode = mode
        try:
            existing = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            if require_existing:
                raise ValueError(f"Source draft target changed before it could be written: {path}.") from None
        else:
            if not stat.S_ISREG(existing.st_mode):
                raise ValueError(f"Source draft target is not a regular file: {path}.")
            if expected_revision is not None:
                if (
                    expected_revision is _SOURCE_DRAFT_EXPECTED_ABSENT
                    or not isinstance(expected_revision, tuple)
                    or len(expected_revision) != 2
                    or (existing.st_size, existing.st_mtime_ns) != expected_revision
                ):
                    raise ValueError(f"Source draft conflict: {path} changed after the draft was opened. " "Refresh or restore the draft before applying.")
            if existing_mode is None:
                existing_mode = stat.S_IMODE(existing.st_mode)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        temporary_fd = os.open(temporary_name, flags, 0o666, dir_fd=parent_fd)
        temporary_exists = True
        if existing_mode is not None:
            os.fchmod(temporary_fd, existing_mode)
        digest = hashlib.sha256()
        if isinstance(content, Path):
            with content.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    _write_source_draft_chunk(
                        temporary_fd,
                        chunk,
                    )
                    digest.update(chunk)
        else:
            _write_source_draft_chunk(temporary_fd, content)
            digest.update(content)
        os.fsync(temporary_fd)
        written_metadata = os.fstat(temporary_fd)
        os.close(temporary_fd)
        temporary_fd = None
        if expected_mutation is not None:
            _validate_source_draft_mutation(
                parent_fd,
                path,
                expected_mutation,
            )
        elif expected_revision is not None:
            _validate_source_draft_expected_state_at_parent(
                parent_fd,
                path,
                expected_revision,
            )
        if expected_mutation is not None or expected_revision is not None or expected_content_sha256 is not None:
            _install_guarded_source_draft_temporary(
                parent_fd,
                path,
                temporary_name,
                expected_revision=expected_revision,
                expected_content_sha256=expected_content_sha256,
                expected_mutation=expected_mutation,
                displaced_name=displaced_name,
            )
        else:
            os.rename(
                temporary_name,
                path.name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
            )
            temporary_exists = False
        _fsync_source_draft_directory(parent_fd)
        return _SourceDraftMutation(
            path=path,
            parent_identity=parent_identity,
            file_identity=(
                written_metadata.st_dev,
                written_metadata.st_ino,
                written_metadata.st_size,
                written_metadata.st_mtime_ns,
            ),
            content_sha256=digest.hexdigest(),
        )
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"Source draft path changed before it could be written safely: {path}.") from error
    finally:
        if temporary_fd is not None:
            _close_module_descriptor(temporary_fd)
        if temporary_exists:
            try:
                os.unlink(temporary_name, dir_fd=parent_fd)
            except OSError:
                pass
        _close_module_descriptor(parent_fd)


def _remove_source_draft_file(
    project_root: Path,
    path: Path,
    *,
    root_identity: tuple[int, int],
    missing_ok: bool = False,
    expected_mutation: _SourceDraftMutation | None = None,
    expected_revision: object = None,
    expected_content_sha256: object = None,
    displaced_name: str | None = None,
) -> _SourceDraftMutation:
    """Remove one draft file without following a replaced directory."""

    if _uses_win32_source_draft_authority():
        return _remove_win32_source_draft_file(
            project_root,
            path,
            root_identity=root_identity,
            missing_ok=missing_ok,
            expected_mutation=expected_mutation,
            expected_revision=expected_revision,
            expected_content_sha256=expected_content_sha256,
        )
    parent_fd = _open_source_draft_parent_fd(project_root, path, root_identity=root_identity)
    parent_metadata = os.fstat(parent_fd)
    parent_identity = (parent_metadata.st_dev, parent_metadata.st_ino)
    quarantine_name = displaced_name or f".paradev-draft-{uuid4().hex}.removed"
    if quarantine_name in {"", ".", ".."} or "/" in quarantine_name or "\\" in quarantine_name:
        raise ValueError("Source draft displacement must be one exact filename.")
    quarantined = False
    source_unlinked = False
    try:
        try:
            os.link(
                path.name,
                quarantine_name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
            quarantined = True
        except FileNotFoundError:
            if missing_ok:
                return _SourceDraftMutation(
                    path=path,
                    parent_identity=parent_identity,
                    file_identity=None,
                    content_sha256=None,
                )
            raise
        except FileExistsError as error:
            raise ValueError("Source draft recovery displacement is already occupied: " f"{path.parent / quarantine_name}.") from error
        entry = os.stat(
            quarantine_name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        if not stat.S_ISREG(entry.st_mode):
            raise ValueError(f"Source draft removal target is not a regular file: {path}.")
        if expected_mutation is not None:
            _validate_source_draft_mutation(
                parent_fd,
                path,
                expected_mutation,
                entry_name=quarantine_name,
            )
        elif expected_revision is not None:
            if (
                expected_revision is _SOURCE_DRAFT_EXPECTED_ABSENT
                or not isinstance(expected_revision, tuple)
                or len(expected_revision) != 2
                or (entry.st_size, entry.st_mtime_ns) != expected_revision
            ):
                raise ValueError(f"Source draft conflict: {path} changed after the draft was opened. " "Refresh or restore the draft before applying.")
        _validate_source_draft_expected_content_at_parent(
            parent_fd,
            path,
            expected_content_sha256,
            entry_name=quarantine_name,
        )
        _require_source_draft_same_entry(
            parent_fd,
            path,
            left_name=path.name,
            right_name=quarantine_name,
        )
        os.unlink(path.name, dir_fd=parent_fd)
        source_unlinked = True
        os.unlink(quarantine_name, dir_fd=parent_fd)
        quarantined = False
        _fsync_source_draft_directory(parent_fd)
        return _SourceDraftMutation(
            path=path,
            parent_identity=parent_identity,
            file_identity=None,
            content_sha256=None,
        )
    except ValueError:
        if quarantined:
            _restore_source_draft_displacement(
                parent_fd,
                path,
                quarantine_name=quarantine_name,
                source_unlinked=source_unlinked,
                operation="removal conflict",
            )
        raise
    except OSError as error:
        if quarantined:
            _restore_source_draft_displacement(
                parent_fd,
                path,
                quarantine_name=quarantine_name,
                source_unlinked=source_unlinked,
                operation="removal",
            )
        raise ValueError(f"Source draft path changed before it could be removed safely: {path}.") from error
    finally:
        _close_module_descriptor(parent_fd)


def _open_source_draft_root_fd(project_root: Path) -> int:
    """Open a canonical project root component by component without symlinks."""

    if not _ANCHORED_SOURCE_DRAFT_MUTATION_SUPPORTED:
        raise ValueError("Safe descriptor-anchored source draft mutation is unavailable on this platform.")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    descriptor: int | None = None
    try:
        descriptor = os.open(project_root.anchor, flags)
        for part in project_root.parts[1:]:
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            _close_module_descriptor(descriptor)
            descriptor = next_descriptor
    except OSError as error:
        if descriptor is not None:
            _close_module_descriptor(descriptor)
        raise ValueError(f"Source draft project root changed or traverses a symlink: {project_root}.") from error
    return descriptor


@contextmanager
def _open_win32_source_draft_authority(
    project_root: Path,
    *,
    root_identity: tuple[int, int] | None = None,
) -> Iterator[Win32DirectoryAuthority]:
    """Retain and verify one Windows source-draft project root."""

    root = Path(os.path.abspath(project_root.expanduser()))
    try:
        authority = Win32DirectoryAuthority.open(root, create=False)
    except (
        FileNotFoundError,
        OSError,
        Win32FilesystemUnavailable,
        Win32UnsafePathError,
    ) as error:
        raise ValueError(f"Source draft project root changed or traverses a reparse point: {root}.") from error
    if root_identity is not None and authority.identity != root_identity:
        authority.close()
        raise ValueError(f"Source draft project root changed before mutation: {root}.")
    succeeded = False
    try:
        yield authority
        succeeded = True
    finally:
        try:
            if succeeded:
                try:
                    authority.verify_path()
                except (
                    OSError,
                    Win32FilesystemUnavailable,
                    Win32UnsafePathError,
                ) as error:
                    raise ValueError(f"Source draft project root changed before mutation: {root}.") from error
        finally:
            authority.close()


def _win32_source_draft_parts(project_root: Path, path: Path) -> tuple[str, ...]:
    """Return one validated root-relative Windows source-draft path."""

    root = Path(os.path.abspath(project_root.expanduser()))
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError("Source draft path is outside the project root.") from error
    if not relative.parts:
        raise ValueError("Source draft path must point to a file inside the project root.")
    for component in relative.parts:
        if portability_error := windows_portable_component_error(component):
            raise ValueError(f"Source draft path component {component!r} is unsafe on Windows because it {portability_error}: {path}.")
    return relative.parts


def _source_draft_root_identity(project_root: Path) -> tuple[Path, tuple[int, int]]:
    """Resolve a source-draft root and capture a no-follow-verified identity."""

    initial_root = Path(os.path.abspath(project_root.expanduser()))
    if _uses_win32_source_draft_authority():
        with _open_win32_source_draft_authority(initial_root) as authority:
            return authority.path, authority.identity
    initial_descriptor = _open_source_draft_root_fd(initial_root)
    try:
        initial_metadata = os.fstat(initial_descriptor)
    finally:
        _close_module_descriptor(initial_descriptor)
    identity = (initial_metadata.st_dev, initial_metadata.st_ino)
    try:
        root = initial_root.resolve()
    except (OSError, RuntimeError) as error:
        raise ValueError(f"Source draft project root is unavailable: {initial_root}.") from error
    descriptor = _open_source_draft_root_fd(root)
    try:
        opened_metadata = os.fstat(descriptor)
    finally:
        _close_module_descriptor(descriptor)
    if (opened_metadata.st_dev, opened_metadata.st_ino) != identity:
        raise ValueError(f"Source draft project root changed before validation: {root}.")
    return root, identity


def _open_source_draft_parent_fd(
    project_root: Path,
    path: Path,
    *,
    root_identity: tuple[int, int],
) -> int:
    """Open a no-follow descriptor chain to one draft target's parent."""

    if not _ANCHORED_SOURCE_DRAFT_MUTATION_SUPPORTED:
        raise ValueError("Safe descriptor-anchored source draft mutation is unavailable on this platform.")
    root = Path(os.path.abspath(project_root.expanduser()))
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError("Source draft path is outside the project root.") from error
    if not relative.parts:
        raise ValueError("Source draft path must point to a file inside the project root.")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    descriptor = _open_source_draft_root_fd(root)
    try:
        root_metadata = os.fstat(descriptor)
        if (root_metadata.st_dev, root_metadata.st_ino) != root_identity:
            raise ValueError(f"Source draft project root changed before mutation: {root}.")
        for part in relative.parts[:-1]:
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            _close_module_descriptor(descriptor)
            descriptor = next_descriptor
    except ValueError:
        _close_module_descriptor(descriptor)
        raise
    except OSError as error:
        _close_module_descriptor(descriptor)
        raise ValueError(f"Source draft path changed or traverses a symlink before mutation: {path}.") from error
    return descriptor


def _source_draft_module_targets(
    project: Project,
    paths: Sequence[object],
) -> tuple[tuple[dict[str, object], Path], ...]:
    targets: dict[tuple[Path, str, str, Path], None] = {}
    for value in paths:
        if not isinstance(value, Path):
            continue
        module_path = _source_draft_module_path(project, value)
        if module_path is None:
            continue
        (
            source_root,
            family,
            object_id,
            module_root,
            _relative_path,
        ) = module_path
        targets[(source_root, family, object_id, module_root)] = None
    rows: list[tuple[dict[str, object], Path]] = []
    for source_root, family, object_id, module_root in targets:
        module_id = f"{family}/{object_id}"
        lookup: dict[str, object] = {
            "module_id": module_id,
            "family": family,
            "root": str(module_root),
        }
        try:
            module = _find_project_module(
                replace(project, source_roots=(source_root,)),
                module_id,
                source_root=source_root,
            )
        except Exception:
            pass
        else:
            lookup = module.to_dict()
        rows.append((lookup, source_root))
    return tuple(rows)


def _aggregate_source_draft_catalog_mutations(
    mutations: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    if not mutations:
        raise ValueError("Source draft Catalog mutation aggregation requires at least one result.")
    failed = next(
        (dict(mutation) for mutation in mutations if mutation.get("status") == "failed"),
        None,
    )
    if failed is not None:
        return failed
    statuses = {mutation.get("status") for mutation in mutations}
    if len(statuses) == 1:
        return dict(mutations[0])
    first = mutations[0]
    return {
        "schema": "paradev.hb.catalog-mutation.v1",
        "status": "failed",
        "code": "catalog.mutation.failed",
        "database": str(first.get("database") or ""),
        "message": "Catalog invalidation returned inconsistent statuses across the modules changed by one source draft.",
    }


def _project_source_form_text(project: Project, path: Path, text: str | None) -> str:
    if text is None:
        loaded = project.read_source_text(path).get("text")
        if not isinstance(loaded, str):
            raise ValueError("Project source text payload did not contain text.")
        source_text = loaded
    else:
        if not isinstance(text, str):
            raise ValueError("Source form text must be a string or null.")
        source_text = text
    _validate_source_draft_text(project, path, source_text)
    return source_text


def _source_form_provider_payload(value: object) -> dict[str, object]:
    payload = _source_form_mapping(value, "source form provider result")
    _source_form_validate_fields(payload, _SOURCE_FORM_PROVIDER_FIELDS, "source form provider result")
    normalized: dict[str, object] = {
        "contract": _source_form_required_string(payload.get("contract"), "source form contract"),
    }
    if "label" in payload:
        normalized["label"] = _source_form_localized_text(payload["label"], "source form label")
    if "description" in payload:
        normalized["description"] = _source_form_localized_text(payload["description"], "source form description")
    if "coverage" in payload:
        normalized["coverage"] = _source_form_coverage(payload["coverage"])
    if "query" in payload:
        raw_query = payload["query"]
        if not isinstance(raw_query, str):
            raise TypeError("source form query must be a string.")
        query = normalize_source_form_query(raw_query)
        if query is None:
            raise ValueError("source form query must not be empty when present.")
        normalized["query"] = query
    section_ids: set[str] = set()
    control_ids: set[str] = set()
    normalized["sections"] = _source_form_sections(
        payload.get("sections"),
        "source form sections",
        section_ids=section_ids,
        control_ids=control_ids,
        allow_empty="query" in normalized,
    )
    coverage = normalized.get("coverage")
    if isinstance(coverage, Mapping) and coverage["shown_controls"] != len(control_ids):
        raise ValueError("source form coverage shown_controls must match the projected control count.")
    return normalized


def _source_form_coverage(value: object) -> dict[str, object]:
    coverage = _source_form_mapping(value, "source form coverage")
    _source_form_validate_fields(coverage, _SOURCE_FORM_COVERAGE_FIELDS, "source form coverage")
    truncated = coverage.get("truncated")
    if not isinstance(truncated, bool):
        raise TypeError("source form coverage.truncated must be a boolean.")
    shown = _source_form_non_negative_integer(coverage.get("shown_controls"), "source form coverage.shown_controls")
    total = _source_form_non_negative_integer(coverage.get("total_controls"), "source form coverage.total_controls")
    if shown > total:
        raise ValueError("source form coverage.shown_controls must not exceed total_controls.")
    if truncated != (shown < total):
        raise ValueError("source form coverage.truncated must match whether controls were omitted.")
    return {
        "truncated": truncated,
        "shown_controls": shown,
        "total_controls": total,
    }


def _source_form_sections(
    value: object,
    label: str,
    *,
    section_ids: set[str],
    control_ids: set[str],
    allow_empty: bool = False,
) -> list[dict[str, object]]:
    rows = _source_form_sequence(value, label)
    if not rows:
        if allow_empty:
            return []
        raise ValueError(f"{label} must be a non-empty list.")
    return [
        _source_form_section(
            row,
            f"{label}[{index}]",
            section_ids=section_ids,
            control_ids=control_ids,
        )
        for index, row in enumerate(rows)
    ]


def _source_form_section(
    value: object,
    label: str,
    *,
    section_ids: set[str],
    control_ids: set[str],
) -> dict[str, object]:
    section = _source_form_mapping(value, label)
    _source_form_validate_fields(section, _SOURCE_FORM_SECTION_FIELDS, label)
    section_id = _source_form_unique_id(section.get("id"), f"{label}.id", section_ids)
    normalized: dict[str, object] = {
        "id": section_id,
        "label": _source_form_localized_text(section.get("label"), f"{label}.label"),
    }
    if "description" in section:
        normalized["description"] = _source_form_localized_text(section["description"], f"{label}.description")
    if "controls" in section:
        normalized["controls"] = _source_form_controls(
            section["controls"],
            f"{label}.controls",
            control_ids=control_ids,
        )
    if "sections" in section:
        normalized["sections"] = _source_form_sections(
            section["sections"],
            f"{label}.sections",
            section_ids=section_ids,
            control_ids=control_ids,
        )
    if "controls" not in normalized and "sections" not in normalized:
        raise ValueError(f"{label} must define controls or nested sections.")
    return normalized


def _source_form_controls(value: object, label: str, *, control_ids: set[str]) -> list[dict[str, object]]:
    rows = _source_form_sequence(value, label)
    if not rows:
        raise ValueError(f"{label} must be a non-empty list.")
    return [_source_form_control(row, f"{label}[{index}]", control_ids=control_ids) for index, row in enumerate(rows)]


def _source_form_control(value: object, label: str, *, control_ids: set[str]) -> dict[str, object]:
    control = _source_form_mapping(value, label)
    _source_form_validate_fields(control, _SOURCE_FORM_CONTROL_FIELDS, label)
    control_id = _source_form_unique_id(control.get("id"), f"{label}.id", control_ids)
    control_kind = _source_form_required_string(control.get("control"), f"{label}.control")
    if control_kind not in _SOURCE_FORM_CONTROL_KINDS:
        supported = ", ".join(sorted(_SOURCE_FORM_CONTROL_KINDS))
        raise ValueError(f"{label}.control must be one of: {supported}.")
    scalar = _source_form_scalar(control.get("value"), f"{label}.value")
    _source_form_validate_control_value(control_kind, scalar, f"{label}.value")
    normalized: dict[str, object] = {
        "id": control_id,
        "label": _source_form_localized_text(control.get("label"), f"{label}.label"),
        "control": control_kind,
        "value": scalar,
    }
    if "description" in control:
        normalized["description"] = _source_form_localized_text(control["description"], f"{label}.description")
    if "description_source" in control:
        description_source = control["description_source"]
        if description_source not in {"declared", "generated"}:
            raise ValueError(f"{label}.description_source must be 'declared' or 'generated'.")
        if "description" not in normalized:
            raise ValueError(f"{label}.description_source requires description.")
        normalized["description_source"] = description_source
    _source_form_normalize_control_choices(control, normalized, label, control_kind, scalar)
    _source_form_normalize_control_numbers(control, normalized, label, control_kind)
    if "placeholder" in control:
        if control_kind not in {"text", "number", "choice"}:
            raise ValueError(f"{label}.placeholder is only valid for text, number, or choice controls.")
        normalized["placeholder"] = _source_form_localized_text(control["placeholder"], f"{label}.placeholder")
    if "multiline" in control:
        multiline = control["multiline"]
        if not isinstance(multiline, bool):
            raise TypeError(f"{label}.multiline must be a boolean.")
        if control_kind != "text":
            raise ValueError(f"{label}.multiline is only valid for text controls.")
        normalized["multiline"] = multiline
    if control_kind == "readonly":
        if "patch" in control:
            raise ValueError(f"{label}.patch must be omitted for readonly controls.")
    else:
        if "patch" not in control:
            raise ValueError(f"{label}.patch is required for editable controls.")
        normalized["patch"] = _source_form_patch(control["patch"], f"{label}.patch")
    return normalized


def _source_form_normalize_control_choices(
    control: Mapping[object, object],
    normalized: dict[str, object],
    label: str,
    control_kind: str,
    value: object,
) -> None:
    if "choices" not in control:
        if control_kind == "choice":
            raise ValueError(f"{label}.choices is required for choice controls.")
        return
    if control_kind != "choice":
        raise ValueError(f"{label}.choices is only valid for choice controls.")
    choices = _source_form_choices(control["choices"], f"{label}.choices")
    value_kind = _source_form_scalar_kind(value)
    if any(_source_form_scalar_kind(choice["value"]) != value_kind for choice in choices):
        raise ValueError(f"{label}.choices must use the same JSON scalar kind as {label}.value.")
    if not any(_source_form_same_scalar(value, choice["value"]) for choice in choices):
        raise ValueError(f"{label}.value must match one of its choices.")
    normalized["choices"] = choices


def _source_form_choices(value: object, label: str) -> list[dict[str, object]]:
    rows = _source_form_sequence(value, label)
    if not rows:
        raise ValueError(f"{label} must be a non-empty list.")
    choices: list[dict[str, object]] = []
    seen: set[tuple[str, object]] = set()
    for index, raw_choice in enumerate(rows):
        choice_label = f"{label}[{index}]"
        choice = _source_form_mapping(raw_choice, choice_label)
        _source_form_validate_fields(choice, _SOURCE_FORM_CHOICE_FIELDS, choice_label)
        scalar = _source_form_scalar(choice.get("value"), f"{choice_label}.value")
        identity = (_source_form_scalar_kind(scalar), scalar)
        if identity in seen:
            raise ValueError(f"{label} must not contain duplicate values.")
        seen.add(identity)
        choices.append(
            {
                "label": _source_form_localized_text(choice.get("label"), f"{choice_label}.label"),
                "value": scalar,
            }
        )
    return choices


def _source_form_normalize_control_numbers(
    control: Mapping[object, object],
    normalized: dict[str, object],
    label: str,
    control_kind: str,
) -> None:
    numeric_fields = tuple(field for field in ("min", "max", "step") if field in control)
    if numeric_fields and control_kind != "number":
        fields = ", ".join(numeric_fields)
        raise ValueError(f"{label} fields {fields} are only valid for number controls.")
    for field_name in numeric_fields:
        normalized[field_name] = _source_form_number(control[field_name], f"{label}.{field_name}")
    step = normalized.get("step")
    if isinstance(step, int | float) and step <= 0:
        raise ValueError(f"{label}.step must be greater than zero.")
    minimum = normalized.get("min")
    maximum = normalized.get("max")
    if isinstance(minimum, int | float) and isinstance(maximum, int | float) and minimum > maximum:
        raise ValueError(f"{label}.min must not be greater than {label}.max.")


def _source_form_patch(value: object, label: str) -> dict[str, object]:
    return normalize_source_form_patch(value, label)


def _source_form_localized_text(value: object, label: str) -> str | dict[str, str]:
    if isinstance(value, str) and value.strip():
        return value
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a non-empty string or localized text mapping.")
    normalized: dict[str, str] = {}
    for locale, text in value.items():
        if not isinstance(locale, str) or not locale.strip():
            raise ValueError(f"{label} locale keys must be non-empty strings.")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"{label}.{locale} must be a non-empty string.")
        normalized[locale] = text
    if "default" not in normalized:
        raise ValueError(f"{label} localized text must define a non-empty default value.")
    return normalized


def _source_form_validate_control_value(control: str, value: object, label: str) -> None:
    if control == "text" and not isinstance(value, str):
        raise ValueError(f"{label} must be a string for text controls.")
    if control == "number" and (isinstance(value, bool) or not isinstance(value, int | float)):
        raise ValueError(f"{label} must be a number for number controls.")
    if control == "boolean" and not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean for boolean controls.")


def _source_form_scalar(value: object, label: str) -> str | int | float | bool:
    if isinstance(value, str | bool | int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise ValueError(f"{label} must be a finite JSON string, number, or boolean scalar.")


def _source_form_number(value: object, label: str) -> int | float:
    if type(value) is int:
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise ValueError(f"{label} must be a finite number.")


def _source_form_non_negative_integer(value: object, label: str) -> int:
    if type(value) is int and value >= 0:
        return value
    raise ValueError(f"{label} must be a non-negative integer.")


def _source_form_same_scalar(left: object, right: object) -> bool:
    return _source_form_scalar_kind(left) == _source_form_scalar_kind(right) and left == right


def _source_form_scalar_kind(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    return "number"


def _source_form_unique_id(value: object, label: str, seen: set[str]) -> str:
    identifier = _source_form_required_string(value, label)
    if identifier in seen:
        raise ValueError(f"{label} duplicates source form id {identifier!r}.")
    seen.add(identifier)
    return identifier


def _source_form_required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    return value.strip()


def _source_form_mapping(value: object, label: str) -> Mapping[object, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object.")
    return value


def _source_form_sequence(value: object, label: str) -> list[object]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise ValueError(f"{label} must be a list.")
    return list(value)


def _source_form_validate_fields(value: Mapping[object, object], allowed: frozenset[str], label: str) -> None:
    unknown = sorted(str(field) for field in value if not isinstance(field, str) or field not in allowed)
    if unknown:
        raise ValueError(f"{label} contains unsupported fields: {', '.join(unknown)}.")


def _validate_project_family_source_text_drafts(project: Project, edits: Sequence[Mapping[str, object]]) -> None:
    module_edits: list[tuple[str, str, str, str, str]] = []
    for edit in edits:
        path = edit.get("path")
        text = edit.get("text")
        if not isinstance(path, Path) or not isinstance(text, str):
            raise ValueError("Source edit did not preserve its validated path and text.")
        module_path = _source_draft_module_path(project, path)
        if module_path is None:
            continue
        (
            _source_root,
            family_id,
            object_id,
            _module_root,
            relative_path,
        ) = module_path
        module_edits.append(
            (
                family_id,
                f"{family_id}/{object_id}",
                relative_path,
                _project_relative_path(project.root, path),
                text,
            )
        )
    if not module_edits:
        return

    registry = project._build_registry(profile=project.game)
    families: dict[str, object | None] = {}
    for family_id, module_id, relative_path, source_path, text in module_edits:
        if family_id not in families:
            try:
                families[family_id] = registry.family(family_id)
            except ValueError:
                families[family_id] = None
        family = families[family_id]
        if family is None:
            continue
        validate_source_text = getattr(family, "validate_source_text", None)
        if validate_source_text is None:
            continue
        if not callable(validate_source_text):
            raise ValueError(f"Build family {family_id!r} validate_source_text must be callable.")
        try:
            validate_source_text(module_id=module_id, relative_path=relative_path, text=text)
        except (OSError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid source draft {source_path!r}: {error}") from error


def _source_draft_module_path(
    project: Project,
    path: Path,
) -> tuple[Path, str, str, Path, str] | None:
    for source_root in project.source_roots:
        try:
            relative = path.relative_to(source_root)
        except ValueError:
            continue
        if len(relative.parts) < 4 or relative.parts[0] != "modules":
            continue
        family, folder_name = relative.parts[1:3]
        object_id, _title = _project_browser_object_id_and_title(folder_name)
        module_root = source_root / "modules" / family / folder_name
        module_relative_path = Path(*relative.parts[3:]).as_posix()
        return source_root, family, object_id, module_root, module_relative_path
    return None


def _collection_root(collection: "Collection") -> Path:
    root = getattr(collection.payload, "root", "")
    if not isinstance(root, (str, Path)) or not str(root):
        raise ValueError(f"Collection {collection.collection_id} does not have a source root.")
    return Path(root).expanduser().resolve()


def _collection_source_root(project_root: Path, source_roots: tuple[Path, ...], collection_root: Path) -> Path:
    for source_root in source_roots:
        resolved = source_root.expanduser().resolve()
        try:
            collection_root.relative_to(resolved / "collections")
        except ValueError:
            continue
        return resolved
    raise ValueError(f"Collection root is outside configured source roots: {_project_relative_path(project_root, collection_root)}.")


def _collection_id_token(value: object) -> str:
    return _module_path_token(value, "collection_id")


def _module_draft_template_ref(project: Project, family_id: str, template_id: str | None) -> str:
    if template_id is not None:
        if not isinstance(template_id, str) or not template_id.strip():
            raise ValueError("Module template_id must be a non-empty string.")
        return template_id.strip()
    browser = project.browser()
    for bucket_name in ("families", "groups"):
        rows = browser.get(bucket_name, ())
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, Mapping) and row.get("id") == family_id and isinstance(row.get("family"), str):
                return row["family"]
    return family_id


def _module_id_parts(module_id: object) -> tuple[str, str]:
    if not isinstance(module_id, str) or not module_id.strip():
        raise ValueError("Module id must use family/object_id form.")
    parts = module_id.strip().split("/")
    if len(parts) != 2:
        raise ValueError("Module id must use family/object_id form.")
    family, object_id = (
        _module_path_token(parts[0], "family"),
        _module_path_token(parts[1], "object_id"),
    )
    return family, object_id


def _module_object_id(module_id: str) -> str:
    return module_id.split("/", 1)[1] if "/" in module_id else module_id


def _module_path_token(value: object, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Module {key} must be a non-empty path segment.")
    text = value.strip()
    if text in {".", ".."} or "/" in text or "\\" in text or any(char.isspace() for char in text):
        raise ValueError(f"Module {key} must be one path segment.")
    if portability_error := windows_portable_component_error(text):
        raise ValueError(f"Module {key} is not portable to Windows because it {portability_error}: {text!r}.")
    return text


def _optional_path_filter(key: str, value: object) -> str | None:
    return None if value is None else _module_path_token(value, key)


def _module_source_root(project_root: Path, source_roots: tuple[Path, ...], module_root: Path) -> Path:
    for source_root in source_roots:
        resolved = source_root.expanduser().resolve()
        try:
            module_root.relative_to(resolved / "modules")
        except ValueError:
            continue
        return resolved
    raise ValueError(f"Module root is outside configured source roots: {_project_relative_path(project_root, module_root)}.")


def _find_manifest(path: str | os.PathLike[str]) -> Path:
    start = Path(path).expanduser().resolve()
    cursor = start.parent if start.exists() and start.is_file() else start
    for candidate_root in (cursor, *cursor.parents):
        manifest = candidate_root / PROJECT_MANIFEST
        if manifest.is_file():
            return manifest
    raise ProjectManifestError(f"Missing {PROJECT_MANIFEST} while discovering project from {start}.")


def _project_identifier(value: str) -> str:
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
    return "_".join(parts) or "paradev_project"


def _project_title(value: str) -> str:
    return _project_identifier(value).replace("_", " ").title() or "ParaDev Project"


def _starter_object_id(project_id: str) -> str:
    return f"{project_id}_starter_modifier"


def _load_manifest(path: Path) -> dict[str, object]:
    user_data = load_yaml(str(path), strict=True)
    if not isinstance(user_data, dict):
        raise ProjectManifestError(f"{path} must contain a YAML mapping with keys: {', '.join(PROJECT_REQUIRED_SCHEMA_KEYS)}.")
    system_path = path.parent / PROJECT_SYSTEM_MANIFEST
    system_data: dict[str, object] = {}
    if system_path.is_file():
        loaded_system_data = load_yaml(str(system_path), strict=True)
        if not isinstance(loaded_system_data, dict):
            raise ProjectManifestError(f"{system_path} must contain a YAML mapping.")
        system_data = loaded_system_data
    data = {**system_data, **user_data}
    missing = [key for key in PROJECT_REQUIRED_SCHEMA_KEYS if key not in data]
    if missing:
        raise ProjectManifestError(f"{path} is missing required key(s): {', '.join(missing)}.")
    return data


def _load_user_manifest(path: Path) -> tuple[dict[str, object], bytes]:
    """Load only the visible user manifest and retain its exact revision."""

    try:
        source = path.read_bytes()
    except OSError as error:
        raise ProjectManifestError(f"Cannot read project manifest {path}: {error}.") from error
    try:
        loaded = loads_yaml(source.decode("utf-8"))
    except (UnicodeDecodeError, YAMLError) as error:
        raise ProjectManifestError(f"{path} must contain valid UTF-8 YAML.") from error
    if not isinstance(loaded, dict):
        raise ProjectManifestError(f"{path} must contain a YAML mapping.")
    return cast(dict[str, object], loaded), source


def _write_user_manifest(
    project: Project,
    manifest: Mapping[str, object],
) -> bytes:
    """Atomically replace the visible project manifest under root authority."""

    payload = _dump_user_manifest(manifest)
    metadata = project.manifest_path.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise ProjectManifestError(f"Project manifest must be a regular file: {project.manifest_path}.")
    with open_anchored_directory(project.root, create=False) as authority:
        authority.write_bytes(
            PROJECT_MANIFEST,
            payload,
            mode=stat.S_IMODE(metadata.st_mode),
        )
    return payload


def _dump_user_manifest(manifest: Mapping[str, object]) -> bytes:
    """Serialize one visible user manifest deterministically."""

    return (
        dumps_yaml(
            dict(manifest),
            sort_keys=False,
            indent=2,
            allow_unicode=True,
        ).rstrip("\n")
        + "\n"
    ).encode("utf-8")


def _manifest_preferred_language(
    manifest: Mapping[str, object],
    path: Path,
) -> str:
    """Return one validated project authoring-language alias."""

    value = manifest.get("preferred_language", "en")
    if not isinstance(value, str) or not value.strip():
        raise ProjectManifestError(f"{path} key 'preferred_language' must be a non-empty HoI4 " "language alias such as 'en', 'zh', or 'l_simp_chinese'.")
    normalized = value.strip().lower().replace("-", "_")
    canonical = canonical_language(normalized)
    if canonical not in _PROJECT_PREFERRED_LANGUAGE_BY_CANONICAL:
        raise ProjectManifestError(
            f"{path} key 'preferred_language' must resolve to a supported HoI4 "
            f"language id, got {value!r}. Supported aliases include: "
            "en, fr, de, ru, es, pl, pt_br, zh, ja, ko."
        )
    return _PROJECT_PREFERRED_LANGUAGE_BY_CANONICAL[canonical]


def _set_project_preferred_language(
    project: Project,
    preferred_language: str,
    *,
    write: bool,
    plan_hash: str | None,
) -> dict[str, object]:
    """Plan or publish one guarded visible-manifest language update."""

    normalized = _manifest_preferred_language(
        {"preferred_language": preferred_language},
        project.manifest_path,
    )
    manifest, before = _load_user_manifest(project.manifest_path)
    updated = dict(manifest)
    updated["preferred_language"] = normalized
    current_user_language = manifest.get("preferred_language")
    unchanged_default = current_user_language is None and normalized == "en" and project.preferred_language == "en"
    if current_user_language == normalized or unchanged_default:
        after = before
    else:
        after = _dump_user_manifest(updated)
    changed = before != after
    diagnostics: list[dict[str, object]] = []
    current_hash = _project_preferred_language_plan_hash(
        project,
        preferred_language=normalized,
        before=before,
        after=after,
    )
    if write and not isinstance(plan_hash, str):
        diagnostics.append(
            {
                "code": "project_preferred_language.plan_hash_required",
                "severity": "error",
                "message": ("Applying a project language change requires the exact " "plan_hash returned by a dry plan."),
            }
        )
    elif write and plan_hash != current_hash:
        diagnostics.append(
            {
                "code": "project_preferred_language.plan_hash_mismatch",
                "severity": "error",
                "message": ("The project manifest changed after planning; review the " "current language plan and apply its plan_hash."),
                "expected_plan_hash": current_hash,
                "provided_plan_hash": plan_hash,
            }
        )
    blocked = bool(diagnostics)
    payload: dict[str, object] = {
        "schema": PROJECT_PREFERRED_LANGUAGE_SCHEMA,
        "project_id": project.project_id,
        "manifest": str(project.manifest_path),
        "previous_language": project.preferred_language,
        "preferred_language": normalized,
        "changed": changed,
        "written": False,
        "blocked": blocked,
        "diagnostics": diagnostics,
        "plan_hash": current_hash,
        "revision": {
            "size": len(before),
            "sha256": sha256hash(before),
        },
    }
    if blocked or not write:
        return payload
    if changed:
        published = _write_user_manifest(project, updated)
        if published != after:
            raise AssertionError("Published project manifest differs from its reviewed plan.")
    reloaded = Project.load(project.root)
    payload["written"] = changed
    payload["project"] = reloaded.to_view()
    return payload


def _project_preferred_language_plan_hash(
    project: Project,
    *,
    preferred_language: str,
    before: bytes,
    after: bytes,
) -> str:
    """Hash one preferred-language update and exact manifest revisions."""

    canonical = {
        "schema": PROJECT_PREFERRED_LANGUAGE_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root),
        "project_root_identity": _module_create_path_identity(project.root),
        "manifest": str(project.manifest_path),
        "preferred_language": preferred_language,
        "before_size": len(before),
        "before_sha256": sha256hash(before),
        "after_size": len(after),
        "after_sha256": sha256hash(after),
    }
    return sha256hash(
        dumps_json(
            canonical,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            compact=True,
            adapt=False,
        )
    )


def _manifest_output_root(manifest: dict[str, object], root: Path, path: Path, project_id: str, game: str) -> Path:
    value = manifest.get("output_root")
    if value is None:
        return _default_output_root(root, project_id, game)
    if not isinstance(value, str) or not value.strip():
        raise ProjectManifestError(f"{path} key 'output_root' must be a non-empty string.")
    return _resolve_generated_path(root, value.strip())


def _default_output_root(root: Path, project_id: str, game: str) -> Path:
    mod_root = _hoi4_user_mod_root(game)
    if mod_root is not None:
        return _absolute_lexical_path(mod_root / project_id)
    return _absolute_lexical_path(root / "build/mod")


def _hoi4_user_mod_root(game: str) -> Path | None:
    if game != "hoi4":
        return None
    configured = os.environ.get(HOI4_MOD_ROOT_ENV)
    if configured:
        return _absolute_lexical_path(Path(configured))
    if sys.platform == "darwin":
        return _absolute_lexical_path(Path(HOI4_MACOS_MOD_ROOT))
    if sys.platform == "win32":
        return _absolute_lexical_path(_windows_documents_directory() / HOI4_MOD_ROOT_UNDER_DOCUMENTS)
    return None


def _windows_documents_directory() -> Path:
    """Resolve the redirected Windows Documents directory.

    Returns:
        Absolute Documents directory reported by Windows or a deterministic
        user-profile fallback.

    Raises:
        ProjectManifestError: If Windows exposes no usable Documents or user
            profile path.
    """

    failures: list[str] = []
    lookups = (
        ("Known Folder API", _windows_documents_from_known_folder),
        ("User Shell Folders registry", _windows_documents_from_registry),
        ("user profile", _windows_documents_from_profile),
    )
    for label, lookup in lookups:
        try:
            candidate = lookup().expanduser()
            if not candidate.is_absolute():
                raise OSError(f"returned a non-absolute path: {candidate}")
        except (OSError, RuntimeError) as error:
            detail = str(error).strip() or type(error).__name__
            failures.append(f"{label}: {detail}")
            continue
        return candidate
    details = "; ".join(failures)
    raise ProjectManifestError(
        "Unable to locate the Windows Documents folder for the Hearts of Iron IV mod output. "
        f"Set {HOI4_MOD_ROOT_ENV} to the full writable HoI4 'mod' directory and restart ParaDev. "
        f"Windows lookup attempts failed ({details})."
    )


def _windows_documents_from_known_folder() -> Path:
    """Return FOLDERID_Documents through the Windows Known Folder API."""

    import ctypes

    loader = getattr(ctypes, "WinDLL", None)
    if loader is None:
        raise OSError("Windows DLL loading is unavailable")

    class _Guid(ctypes.Structure):
        _fields_ = (
            ("data1", ctypes.c_uint32),
            ("data2", ctypes.c_uint16),
            ("data3", ctypes.c_uint16),
            ("data4", ctypes.c_ubyte * 8),
        )

    try:
        shell32 = loader("shell32", use_last_error=True)
        ole32 = loader("ole32", use_last_error=True)
    except OSError as error:
        raise OSError(f"cannot load the Windows shell libraries: {error}") from error

    try:
        get_known_folder_path = shell32.SHGetKnownFolderPath
        free_memory = ole32.CoTaskMemFree
    except AttributeError as error:
        raise OSError(f"a required Windows shell function is unavailable: {error}") from error
    get_known_folder_path.argtypes = (
        ctypes.POINTER(_Guid),
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    )
    get_known_folder_path.restype = ctypes.c_int32
    free_memory.argtypes = (ctypes.c_void_p,)
    free_memory.restype = None

    folder_id = _Guid.from_buffer_copy(WINDOWS_DOCUMENTS_FOLDER_ID.bytes_le)
    path_pointer = ctypes.c_void_p()
    hresult = get_known_folder_path(ctypes.byref(folder_id), 0, None, ctypes.byref(path_pointer))
    if hresult != 0:
        if path_pointer.value is not None:
            free_memory(path_pointer)
        raise OSError(f"SHGetKnownFolderPath failed with HRESULT 0x{hresult & 0xFFFFFFFF:08X}")
    if path_pointer.value is None:
        raise OSError("SHGetKnownFolderPath returned no path")
    try:
        value = ctypes.wstring_at(path_pointer.value)
    finally:
        free_memory(path_pointer)
    if not value.strip():
        raise OSError("SHGetKnownFolderPath returned an empty path")
    return Path(value)


def _windows_documents_from_registry() -> Path:
    """Return the per-user Documents path from Windows Explorer settings."""

    try:
        import winreg
    except ImportError as error:
        raise OSError("the Windows registry module is unavailable") from error

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WINDOWS_USER_SHELL_FOLDERS_KEY) as key:
            value, _value_type = winreg.QueryValueEx(key, "Personal")
    except OSError as error:
        raise OSError(f"cannot read the 'Personal' User Shell Folders value: {error}") from error
    if not isinstance(value, str) or not value.strip():
        raise OSError("the 'Personal' User Shell Folders value is empty")
    return Path(os.path.expandvars(value.strip()))


def _windows_documents_from_profile() -> Path:
    """Return the conventional Documents directory below the Windows profile."""

    profile = os.environ.get("USERPROFILE", "").strip()
    if not profile:
        drive = os.environ.get("HOMEDRIVE", "").strip()
        home_path = os.environ.get("HOMEPATH", "").strip()
        if drive and home_path:
            profile = f"{drive}{home_path}"
    if profile:
        return Path(profile) / "Documents"
    try:
        return Path.home() / "Documents"
    except (OSError, RuntimeError) as error:
        raise OSError(f"cannot resolve the current user profile: {error}") from error


def _delete_generated_root(path: Path) -> bool:
    """Delete an emitted build root, retrying transient filesystem races."""

    for attempt in range(4):
        try:
            return delete_dir(path)
        except FileExistsError:
            raise
        except OSError:
            if not path.exists():
                return True
            if attempt == 3:
                raise
            time.sleep(0.1)
    return False


def _project_source_cache_root(project: Project) -> Path | None:
    cache_root = project.root / ".paradev" / "cache" / "source-families"
    if any(_build_paths_overlap(cache_root, generated_root) for generated_root in (project.output_root, project.build_root)):
        return None
    return cache_root


def _project_artifact_plan_cache_root(project: Project) -> Path | None:
    cache_root = project.root / ".paradev" / "cache" / "artifact-plans"
    if any(_build_paths_overlap(cache_root, generated_root) for generated_root in (project.output_root, project.build_root)):
        return None
    return cache_root


def _project_manifest_publication_cache_path(project: Project) -> Path | None:
    cache_root = project.root / ".paradev" / "cache" / "manifest-publications"
    if any(_build_paths_overlap(cache_root, generated_root) for generated_root in (project.output_root, project.build_root)):
        return None
    build_identity = hashlib.sha256(str(project.build_root.expanduser().resolve(strict=False)).encode("utf-8")).hexdigest()
    return cache_root / f"{build_identity}.json"


def _validate_project_build_roots(project: Project) -> None:
    """Reject generated roots that overlap authored or system-owned paths."""

    generated = {
        "output_root": project.output_root,
        "build_root": project.build_root,
    }
    protected = {
        "project root": project.root,
        **{f"source root {index}": source_root for index, source_root in enumerate(project.source_roots)},
        **{f"copy root {spec.copy_id!r}": spec.source for spec in project.copy_roots},
    }
    for label, path in generated.items():
        resolved = path.expanduser().resolve(strict=False)
        if resolved.parent == resolved:
            raise ValueError(f"Generated {label} cannot be a filesystem root: {path}.")
        if _build_paths_overlap(path, project.root) and _build_path_contains(path, project.root):
            raise ValueError(f"Generated {label} cannot contain the project root: {path}.")
        for protected_label, protected_path in protected.items():
            if protected_label == "project root":
                continue
            if _build_paths_overlap(path, protected_path):
                raise ValueError(f"Generated {label} cannot overlap {protected_label}: {path} and {protected_path}.")
    if _build_paths_overlap(project.output_root, project.build_root):
        raise ValueError("Generated output_root and build_root must be disjoint: " f"{project.output_root} and {project.build_root}.")


def _build_path_contains(parent: Path, child: Path) -> bool:
    parent_parts = _normalized_build_path_parts(parent)
    child_parts = _normalized_build_path_parts(child)
    return len(parent_parts) <= len(child_parts) and child_parts[: len(parent_parts)] == parent_parts


def _build_paths_overlap(left: Path, right: Path) -> bool:
    return _build_path_contains(left, right) or _build_path_contains(right, left)


def _normalized_build_path_parts(path: Path) -> tuple[str, ...]:
    try:
        resolved = path.expanduser().resolve(strict=False)
    except (OSError, RuntimeError):
        resolved = Path(os.path.abspath(path.expanduser()))
    return tuple(_normalize_build_mutation_lock_component(part) for part in resolved.parts)


def _clean_generated_output_root(project: Project) -> None:
    """Clean output while preserving a registered HOI4 directory identity."""

    if _hoi4_launcher_descriptor_target(project) is None:
        _delete_generated_root(project.output_root)
        return
    project.output_root.mkdir(parents=True, exist_ok=True)
    for child in sorted(project.output_root.iterdir(), key=lambda path: path.name):
        if child.is_symlink():
            child.unlink()
        elif child.is_dir():
            _delete_generated_root(child)
        else:
            delete_file(child)


@contextmanager
def _project_build_mutation_lock(*roots: Path) -> Iterator[None]:
    """Serialize artifact and manifest writes for filesystem-equivalent roots."""

    identities = {_build_mutation_root_identity(root) for root in roots}
    with _project_mutation_identity_lock(identities):
        yield


@contextmanager
def _project_source_mutation_lock(project: Project) -> Iterator[None]:
    """Serialize one canonical project source snapshot without resolving it."""

    with project_source_mutation_lock(project.root):
        yield


@contextmanager
def project_source_mutation_lock(
    project_root: str | os.PathLike[str],
) -> Iterator[None]:
    """Serialize an external whole-project source mutation with ParaDev.

    Importers and other transactional source writers should hold this lock
    from their first source snapshot through their final publication rename.
    It coordinates with SDK/GUI edits and emitted builds for the same lexical
    project root without resolving a potentially replaced path first.
    """

    identity = _build_mutation_root_identity(Path(project_root), resolve=False)
    with _project_mutation_identity_lock({identity}):
        yield


@contextmanager
def _project_mutation_identity_lock(identities: Iterable[str]) -> Iterator[None]:
    """Acquire deterministic operating-system locks for normalized identities."""

    requested = frozenset(identities)
    held = _PROJECT_MUTATION_LOCK_IDENTITIES.get()
    pending = requested - held
    if not pending:
        yield
        return

    lock_root = Path(tempfile.gettempdir()) / "paradev-build-locks"
    lock_root.mkdir(parents=True, exist_ok=True)
    handles: list[BinaryIO] = []
    token = None
    try:
        for identity in sorted(pending):
            digest = sha256hash(identity)
            handle = (lock_root / f"{digest}.lock").open("a+b")
            try:
                handle.seek(0, os.SEEK_END)
                if handle.tell() == 0:
                    handle.write(b"\0")
                    handle.flush()
                handle.seek(0)
                _lock_build_mutation_handle(handle)
            except BaseException:
                handle.close()
                raise
            handles.append(handle)
        token = _PROJECT_MUTATION_LOCK_IDENTITIES.set(held | requested)
        yield
    finally:
        if token is not None:
            _PROJECT_MUTATION_LOCK_IDENTITIES.reset(token)
        for handle in reversed(handles):
            try:
                handle.seek(0)
                _unlock_build_mutation_handle(handle)
            except OSError:
                pass
            finally:
                handle.close()


def _project_build_mutation_roots(project: Project, *, include_launcher: bool) -> tuple[Path, ...]:
    """Return every generated path locked by one artifact/manifest build."""

    roots = [project.output_root, project.build_root]
    if include_launcher and (launcher_target := _hoi4_launcher_descriptor_target(project)) is not None:
        roots.append(launcher_target)
    return tuple(roots)


@contextmanager
def _project_publication_roots(
    project: Project,
    *,
    include_output: bool,
    include_launcher: bool,
) -> Iterator[tuple[AnchoredDirectory | None, AnchoredDirectory, AnchoredDirectory | None]]:
    """Retain generated-root authorities across one publication transaction."""

    from paradev.build._fs import open_anchored_directory

    with ExitStack() as stack:
        build_root = stack.enter_context(open_anchored_directory(project.build_root))
        output_root = stack.enter_context(open_anchored_directory(project.output_root)) if include_output else None
        launcher_target = _hoi4_launcher_descriptor_target(project) if include_launcher else None
        launcher_root = stack.enter_context(open_anchored_directory(launcher_target.parent)) if launcher_target is not None else None
        yield output_root, build_root, launcher_root


def _build_mutation_root_identity(root: Path, *, resolve: bool = True) -> str:
    """Return a deletion-stable lock identity for one filesystem root."""

    expanded = root.expanduser()
    if resolve:
        try:
            resolved = expanded.resolve(strict=False)
        except (OSError, RuntimeError):
            resolved = Path(os.path.abspath(expanded))
    else:
        resolved = expanded if expanded.is_absolute() else Path(os.path.abspath(expanded))
    anchor = resolved.parent
    suffix = [resolved.name] if resolved.name else []
    while True:
        try:
            metadata = anchor.stat()
        except (FileNotFoundError, NotADirectoryError):
            parent = anchor.parent
            if parent == anchor:
                break
            if anchor.name:
                suffix.append(anchor.name)
            anchor = parent
        except OSError:
            break
        else:
            normalized_suffix = "/".join(_normalize_build_mutation_lock_component(part) for part in reversed(suffix))
            return f"{metadata.st_dev}:{metadata.st_ino}:{normalized_suffix}"
    return f"path:{_normalize_build_mutation_lock_path(resolved)}"


def _normalize_build_mutation_lock_component(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    if os.name == "nt" or sys.platform == "darwin":
        return normalized.casefold()
    return normalized


def _normalize_build_mutation_lock_path(path: Path) -> str:
    parts = [_normalize_build_mutation_lock_component(part) for part in path.parts]
    return os.path.normcase(str(Path(*parts)))


def _lock_build_mutation_handle(handle: BinaryIO) -> None:
    if os.name == "nt":
        _lock_windows_build_mutation_file_descriptor(handle.fileno(), msvcrt.locking, msvcrt.LK_NBLCK)
    else:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def _lock_windows_build_mutation_file_descriptor(
    file_descriptor: int,
    locking: Callable[[int, int, int], object],
    nonblocking_mode: int,
) -> None:
    """Retry Windows byte-range contention until the owning build releases it."""

    while True:
        try:
            locking(file_descriptor, nonblocking_mode, 1)
        except OSError as error:
            if error.errno not in _BUILD_MUTATION_LOCK_CONTENTION_ERRNOS:
                raise
            time.sleep(_BUILD_MUTATION_LOCK_RETRY_SECONDS)
        else:
            return


def _unlock_build_mutation_handle(handle: BinaryIO) -> None:
    if os.name == "nt":
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _replace_build_artifact_deltas(result: "BuildResult", deltas: Sequence["Artifact"]) -> "BuildResult":
    if not deltas:
        return result
    delta_by_key = {_build_artifact_key(artifact): artifact for artifact in deltas}
    shadowed_copy_artifacts = tuple(
        artifact
        for artifact in result.artifacts
        if artifact.owner.startswith("copy_root:")
        and _build_artifact_key(artifact) in delta_by_key
        and delta_by_key[_build_artifact_key(artifact)].owner != artifact.owner
    )
    _active_copy_artifacts, shadow_diagnostics = merge_copy_root_artifacts(shadowed_copy_artifacts, tuple(deltas))
    merged = [delta_by_key.get(_build_artifact_key(artifact), artifact) for artifact in result.artifacts]
    existing_keys = {_build_artifact_key(artifact) for artifact in result.artifacts}
    merged.extend(artifact for artifact in deltas if _build_artifact_key(artifact) not in existing_keys)
    return replace(
        result,
        artifacts=tuple(merged),
        diagnostics=(*result.diagnostics, *shadow_diagnostics),
    )


def _replace_planned_build_artifact(result: "BuildResult", artifact: "Artifact") -> "BuildResult":
    """Replace one planned path without publishing its superseded writer."""

    key = _build_artifact_key(artifact)
    replaced = False
    artifacts: list[Artifact] = []
    for candidate in result.artifacts:
        if _build_artifact_key(candidate) != key:
            artifacts.append(candidate)
            continue
        if not replaced:
            artifacts.append(artifact)
            replaced = True
    if not replaced:
        artifacts.append(artifact)
    return replace(result, artifacts=tuple(artifacts))


def _build_artifact_key(artifact: "Artifact") -> tuple[str, str]:
    return artifact.target_root, str(artifact.path).replace("\\", "/")


@dataclass(frozen=True, slots=True)
class _ResolvedBuildTarget:
    """One validated build selector expanded to its safe ownership boundary."""

    kind: Literal["family", "module", "collection"]
    modules: frozenset[str]
    collections: frozenset[tuple[str, str]]
    families: frozenset[str]


def _normalize_build_module_selector(
    *,
    family: str | None,
    module_id: str | None,
) -> str | None:
    """Qualify the intuitive bare module selector when its family is explicit."""

    if module_id is None or family is None or "/" in module_id:
        return module_id
    return f"{family}/{module_id}"


def _validate_build_selector_shape(
    *,
    family: str | None,
    module_id: str | None,
    collection_id: str | None,
) -> None:
    if module_id is not None and collection_id is not None:
        raise ValueError("Pass only one targeted build selector: module_id or collection_id.")
    if module_id is None or family is None:
        return
    module_family = module_id.split("/", 1)[0]
    if module_family != family:
        raise ValueError(f"Build module {module_id!r} belongs to family {module_family!r}, not {family!r}.")


def _resolve_build_target(
    result: "BuildResult",
    *,
    family: str | None,
    module_id: str | None,
    collection_id: str | None,
) -> _ResolvedBuildTarget:
    """Validate and expand one selector against a complete build graph."""

    if module_id is not None:
        matches = tuple(module for module in result.modules if module.module_id == module_id and (family is None or module.family == family))
        if not matches:
            raise ValueError(f"Unknown build module: {module_id}")
        target_module = matches[0]
        if target_module.family == "building":
            return _ResolvedBuildTarget(
                kind="module",
                modules=frozenset(module.module_id for module in result.modules if module.family == "building"),
                collections=frozenset((collection.family, collection.collection_id) for collection in result.collections if collection.family == "building"),
                families=frozenset({"building"}),
            )
        collection_keys = {
            (collection.family, collection.collection_id)
            for collection in result.collections
            if collection.family == target_module.family
            and (
                target_module.module_id in collection.module_ids
                or (target_module.collection_id is not None and collection.collection_id == target_module.collection_id)
            )
        }
        module_ids = {target_module.module_id}
        for collection in result.collections:
            if (collection.family, collection.collection_id) in collection_keys:
                module_ids.update(collection.module_ids)
        return _ResolvedBuildTarget(
            kind="module",
            modules=frozenset(module_ids),
            collections=frozenset(collection_keys),
            families=frozenset({target_module.family}),
        )

    if collection_id is not None:
        matches = tuple(
            collection for collection in result.collections if collection.collection_id == collection_id and (family is None or collection.family == family)
        )
        if not matches:
            label = f"{family}/{collection_id}" if family is not None else collection_id
            raise ValueError(f"Unknown build collection: {label}")
        matched_families = {collection.family for collection in matches}
        if family is None and len(matched_families) > 1:
            choices = ", ".join(f"{item}/{collection_id}" for item in sorted(matched_families))
            raise ValueError(f"Build collection {collection_id!r} is ambiguous; pass family as one of: {choices}.")
        collection_keys = {(collection.family, collection.collection_id) for collection in matches}
        module_ids = {module_id for collection in matches for module_id in collection.module_ids}
        module_ids.update(
            module.module_id for module in result.modules if module.collection_id is not None and (module.family, module.collection_id) in collection_keys
        )
        return _ResolvedBuildTarget(
            kind="collection",
            modules=frozenset(module_ids),
            collections=frozenset(collection_keys),
            families=frozenset(matched_families),
        )

    if family is None:
        raise ValueError("A targeted build requires family, module_id, or collection_id.")
    return _ResolvedBuildTarget(
        kind="family",
        modules=frozenset(module.module_id for module in result.modules if module.family == family),
        collections=frozenset((collection.family, collection.collection_id) for collection in result.collections if collection.family == family),
        families=frozenset({family}),
    )


def _targeted_build_result(
    result: "BuildResult",
    *,
    target: _ResolvedBuildTarget,
) -> "BuildResult":
    """Project a full build plan to one safe artifact-emission boundary."""

    from paradev.build import artifact_collection_ids, artifact_module_ids

    selected_modules = set(target.modules)
    selected_collection_keys = set(target.collections)
    selected_collection_ids = {collection_id for _family, collection_id in selected_collection_keys}
    modules = tuple(module for module in result.modules if module.module_id in target.modules)
    collections = tuple(collection for collection in result.collections if (collection.family, collection.collection_id) in target.collections)
    collection_families_by_id: dict[str, set[str]] = {}
    for collection in result.collections:
        collection_families_by_id.setdefault(collection.collection_id, set()).add(collection.family)

    artifacts = tuple(
        artifact
        for artifact in result.artifacts
        if _artifact_in_build_target(
            artifact,
            selected_modules=selected_modules,
            selected_collections=selected_collection_keys,
            selected_families=set(target.families),
            collection_families_by_id=collection_families_by_id,
            artifact_module_ids=artifact_module_ids,
            artifact_collection_ids=artifact_collection_ids,
        )
    )
    artifact_keys = {_build_artifact_key(artifact) for artifact in artifacts}
    diagnostics = tuple(
        diagnostic
        for diagnostic in result.diagnostics
        if _diagnostic_in_build_target(
            diagnostic,
            selected_modules=selected_modules,
            selected_collections=selected_collection_keys,
            selected_families=set(target.families),
            family_wide=target.kind == "family",
            artifact_keys=artifact_keys,
        )
    )
    dependencies = tuple(
        dependency
        for dependency in result.dependencies
        if _build_owner_in_target(
            dependency.source,
            selected_modules=selected_modules,
            selected_collections=selected_collection_ids,
        )
    )
    return replace(
        result,
        modules=modules,
        collections=collections,
        dependencies=dependencies,
        artifacts=artifacts,
        diagnostics=diagnostics,
    )


def _artifact_in_build_target(
    artifact: "Artifact",
    *,
    selected_modules: set[str],
    selected_collections: set[tuple[str, str]],
    selected_families: set[str],
    collection_families_by_id: Mapping[str, set[str]],
    artifact_module_ids: Callable[[object], tuple[str, ...]],
    artifact_collection_ids: Callable[[object], tuple[str, ...]],
) -> bool:
    if artifact.metadata.get("publication_scope") == "project":
        return True
    row = artifact.to_dict()
    if selected_modules.intersection(artifact_module_ids(row)):
        return True
    artifact_collection_ids_found = artifact_collection_ids(row)
    artifact_family = artifact.metadata.get("family")
    if isinstance(artifact_family, str):
        if any((artifact_family, collection_id) in selected_collections for collection_id in artifact_collection_ids_found):
            return True
    else:
        for collection_id in artifact_collection_ids_found:
            families = collection_families_by_id.get(collection_id, set())
            if len(families) == 1 and (next(iter(families)), collection_id) in selected_collections:
                return True
    if artifact.owner.startswith(("project:", "copy_root:")):
        return not isinstance(artifact_family, str) or artifact_family in selected_families
    return False


def _diagnostic_in_build_target(
    diagnostic: "Diagnostic",
    *,
    selected_modules: set[str],
    selected_collections: set[tuple[str, str]],
    selected_families: set[str],
    family_wide: bool,
    artifact_keys: set[tuple[str, str]],
) -> bool:
    if diagnostic.module_id in selected_modules:
        return True
    if diagnostic.collection_id is not None and diagnostic.family is not None and (diagnostic.family, diagnostic.collection_id) in selected_collections:
        return True
    if diagnostic.family in selected_families and (family_wide or (diagnostic.module_id is None and diagnostic.collection_id is None)):
        return True
    if any(
        _build_owner_in_target(
            owner,
            selected_modules=selected_modules,
            selected_collections={collection_id for _family, collection_id in selected_collections},
        )
        for owner in diagnostic.owners
    ):
        return True
    if diagnostic.artifact_path is not None:
        path = str(diagnostic.artifact_path).replace("\\", "/")
        if diagnostic.target_root is None:
            return any(artifact_path == path for _target_root, artifact_path in artifact_keys)
        return (diagnostic.target_root, path) in artifact_keys
    return diagnostic.module_id is None and diagnostic.collection_id is None and diagnostic.family is None and not diagnostic.owners


def _build_owner_in_target(
    owner: str,
    *,
    selected_modules: set[str],
    selected_collections: set[str],
) -> bool:
    if owner.startswith("module:"):
        return owner.removeprefix("module:") in selected_modules
    if owner.startswith("collection:"):
        return owner.removeprefix("collection:") in selected_collections
    return owner.startswith(("project:", "copy_root:"))


def _sync_hoi4_launcher_descriptor_anchored(
    project: Project,
    *,
    build_root: AnchoredDirectory,
    launcher_root: AnchoredDirectory | None,
) -> None:
    if launcher_root is None:
        return
    source = build_root.read_bytes(f"launcher/{project.project_id}.mod")
    if source is None:
        return
    target_name = f"{project.project_id}.mod"
    marker_name = f".paradev-{project.project_id}.launcher.json"
    marker_claimed = _hoi4_launcher_marker_claimed(
        project,
        launcher_root=launcher_root,
        marker_name=marker_name,
        target_name=target_name,
    )
    target = launcher_root.read_bytes(target_name)
    if target is None:
        launcher_root.write_bytes(target_name, source, replace=False)
        if not marker_claimed:
            _claim_hoi4_launcher_descriptor(
                project,
                launcher_root=launcher_root,
                marker_name=marker_name,
                target_name=target_name,
            )
        return
    if _hoi4_launcher_descriptor_payloads_equal(source, target):
        if not marker_claimed:
            _claim_and_revalidate_hoi4_launcher_descriptor(
                project,
                launcher_root=launcher_root,
                marker_name=marker_name,
                target_name=target_name,
                expected_target=target,
            )
        return
    if not marker_claimed and not _hoi4_launcher_descriptor_owned_by_project(target, project):
        raise ValueError(f"HoI4 launcher descriptor is not owned by this ParaDev project: {launcher_root.requested_path / target_name}.")
    if not marker_claimed:
        _claim_and_revalidate_hoi4_launcher_descriptor(
            project,
            launcher_root=launcher_root,
            marker_name=marker_name,
            target_name=target_name,
            expected_target=target,
        )
    launcher_root.write_bytes(target_name, source)


def _preflight_hoi4_launcher_descriptor_anchored(
    project: Project,
    *,
    launcher_root: AnchoredDirectory | None,
) -> None:
    if launcher_root is None:
        return
    target_name = f"{project.project_id}.mod"
    marker_name = f".paradev-{project.project_id}.launcher.json"
    if _hoi4_launcher_marker_claimed(
        project,
        launcher_root=launcher_root,
        marker_name=marker_name,
        target_name=target_name,
    ):
        return
    target = launcher_root.read_bytes(target_name)
    if target is not None and not _hoi4_launcher_descriptor_owned_by_project(target, project):
        raise ValueError(f"HoI4 launcher descriptor is not owned by this ParaDev project: {launcher_root.requested_path / target_name}.")


def _hoi4_launcher_marker_claimed(
    project: Project,
    *,
    launcher_root: AnchoredDirectory,
    marker_name: str,
    target_name: str,
) -> bool:
    encoded = launcher_root.read_bytes(marker_name)
    if encoded is None:
        return False
    try:
        payload = loads_json(encoded.decode("utf-8"))
    except (UnicodeError, ValueError) as error:
        raise ValueError(f"Invalid ParaDev HoI4 launcher ownership marker: {launcher_root.requested_path / marker_name}.") from error
    expected = _hoi4_launcher_marker_payload(project, target_name=target_name)
    if payload == expected:
        return True
    if _migrate_relocated_hoi4_launcher_marker(
        project,
        launcher_root=launcher_root,
        marker_name=marker_name,
        target_name=target_name,
        encoded_marker=encoded,
        payload=payload,
        expected=expected,
    ):
        return True
    raise ValueError("HoI4 launcher descriptor is already claimed by another ParaDev project: " f"{launcher_root.requested_path / target_name}.")


def _migrate_relocated_hoi4_launcher_marker(
    project: Project,
    *,
    launcher_root: AnchoredDirectory,
    marker_name: str,
    target_name: str,
    encoded_marker: bytes,
    payload: object,
    expected: Mapping[str, str],
) -> bool:
    """Update a stale project path after current output ownership is proven."""

    stable_keys = ("schema", "project_id", "target")
    if not isinstance(payload, Mapping) or any(payload.get(key) != expected[key] for key in stable_keys):
        return False
    old_project_root = payload.get("project_root")
    if not isinstance(old_project_root, str) or not old_project_root or old_project_root == expected["project_root"]:
        return False
    target = launcher_root.read_bytes(target_name)
    if target is None or not _hoi4_launcher_descriptor_owned_by_project(target, project):
        return False

    from paradev.build.publication import inspect_publication_root

    try:
        with open_anchored_directory(project.output_root, create=False) as output_root:
            output_state = inspect_publication_root(
                output_root,
                root_name="output",
                project_id=project.project_id,
                project_root=project.root,
            )
    except (OSError, RuntimeError, ValueError):
        return False
    if not output_state.claimed:
        return False
    if launcher_root.read_bytes(marker_name) != encoded_marker or launcher_root.read_bytes(target_name) != target:
        raise ValueError(f"HoI4 launcher ownership changed during relocation validation: {launcher_root.requested_path / target_name}.")
    launcher_root.write_bytes(
        marker_name,
        dumps_json(expected, sort_keys=True, indent=2).encode("utf-8"),
    )
    return True


def _claim_hoi4_launcher_descriptor(
    project: Project,
    *,
    launcher_root: AnchoredDirectory,
    marker_name: str,
    target_name: str,
) -> None:
    payload = _hoi4_launcher_marker_payload(project, target_name=target_name)
    launcher_root.write_bytes(
        marker_name,
        dumps_json(payload, sort_keys=True, indent=2).encode("utf-8"),
        replace=False,
    )


def _claim_and_revalidate_hoi4_launcher_descriptor(
    project: Project,
    *,
    launcher_root: AnchoredDirectory,
    marker_name: str,
    target_name: str,
    expected_target: bytes,
) -> None:
    _claim_hoi4_launcher_descriptor(
        project,
        launcher_root=launcher_root,
        marker_name=marker_name,
        target_name=target_name,
    )
    current_target = launcher_root.read_bytes(target_name)
    if current_target == expected_target:
        return
    launcher_root.delete_file(marker_name)
    raise ValueError(f"HoI4 launcher descriptor changed while ParaDev was claiming it: {launcher_root.requested_path / target_name}.")


def _hoi4_launcher_marker_payload(project: Project, *, target_name: str) -> dict[str, str]:
    return {
        "schema": HOI4_LAUNCHER_OWNER_SCHEMA,
        "project_id": project.project_id,
        "project_root": str(project.root.resolve(strict=False)),
        "target": target_name,
    }


def _hoi4_launcher_descriptor_payloads_equal(source: bytes, target: bytes) -> bool:
    """Return whether two launcher descriptors contain the same PDX data."""

    try:
        source_descriptor = PDXBlock.from_str(source.decode("utf-8-sig")).to_dict()
        target_descriptor = PDXBlock.from_str(target.decode("utf-8-sig")).to_dict()
    except (UnicodeError, PDXParseError):
        return False
    return source_descriptor == target_descriptor


def _hoi4_launcher_descriptor_owned_by_project(payload: bytes, project: Project) -> bool:
    try:
        descriptor = PDXBlock.from_str(payload.decode("utf-8-sig")).to_dict()
    except (UnicodeError, PDXParseError):
        return False
    if not isinstance(descriptor, Mapping):
        return False
    target = descriptor.get("path")
    if not isinstance(target, str) or not target:
        return False
    try:
        target_path = Path(target).expanduser()
        if target_path.resolve(strict=False) == project.output_root.resolve(strict=False):
            return True
        from paradev.build._fs import open_anchored_directory
        from paradev.build.publication import inspect_publication_root

        with open_anchored_directory(target_path, create=False) as old_output_root:
            state = inspect_publication_root(
                old_output_root,
                root_name="output",
                project_id=project.project_id,
                project_root=project.root,
            )
        return state.claimed
    except (OSError, RuntimeError, ValueError):
        return False


def _hoi4_launcher_descriptor_target(project: Project) -> Path | None:
    """Return the external launcher descriptor path mutated by a build."""

    mod_root = _hoi4_user_mod_root(project.game)
    if mod_root is None:
        return None
    try:
        if project.output_root.parent.resolve() != mod_root:
            return None
    except (OSError, RuntimeError):
        return None
    return mod_root / f"{project.project_id}.mod"


def _load_family_specs(manifest: dict[str, object], path: Path) -> tuple["ProjectFamilySpec", ...]:
    from paradev.build import ProjectFamilySpecError, project_family_specs

    try:
        return project_family_specs(manifest.get("families"), path)
    except ProjectFamilySpecError as error:
        raise ProjectManifestError(str(error)) from error


def _load_extension_modules(root: Path, path: Path) -> tuple[Path, ...]:
    from paradev.build import ProjectFamilySpecError, project_extension_modules

    try:
        return project_extension_modules(root)
    except ProjectFamilySpecError as error:
        raise ProjectManifestError(f"{path}: {error}") from error


def _load_template_specs(manifest: dict[str, object], path: Path) -> tuple[ModuleTemplate, ...]:
    try:
        return project_module_templates(manifest.get("templates"), path)
    except ProjectTemplateSpecError as error:
        raise ProjectManifestError(str(error)) from error


def _load_copy_roots(manifest: dict[str, object], root: Path, path: Path) -> tuple[CopyRootSpec, ...]:
    try:
        return project_copy_roots(manifest.get("copy_roots"), root, path)
    except ProjectCopyRootSpecError as error:
        raise ProjectManifestError(str(error)) from error


def _load_descriptor_metadata(manifest: dict[str, object], path: Path) -> dict[str, object]:
    metadata: dict[str, object] = {}
    for key in ("mod_version", "supported_version", "picture"):
        value = manifest.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            raise ProjectManifestError(f"{path} key {key!r} must be a non-empty string.")
        metadata[key] = value.strip()
    remote_file_id = manifest.get("remote_file_id")
    if remote_file_id is not None:
        if isinstance(remote_file_id, int):
            remote_file_id = str(remote_file_id)
        if not isinstance(remote_file_id, str) or not remote_file_id.strip().isdigit() or int(remote_file_id.strip()) < 1:
            raise ProjectManifestError(f"{path} key 'remote_file_id' must be a positive integer string.")
        metadata["remote_file_id"] = remote_file_id.strip()
    for key in ("tags", "replace_path", "replace_paths"):
        value = manifest.get(key)
        if value is None:
            continue
        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
            raise ProjectManifestError(f"{path} key {key!r} must be a list of non-empty strings.")
        metadata[key] = [item.strip() for item in value]
    return metadata


def _descriptor_version(metadata: Mapping[str, object]) -> str | None:
    version = metadata.get("mod_version")
    if not isinstance(version, str):
        return None
    text = version.strip()
    if not text:
        return None
    if len(text) > 1 and text[0] in {"v", "V"} and text[1].isdigit():
        return text[1:]
    return text


def _project_template_index(project: Project) -> dict[str, ModuleTemplate]:
    """Return templates with project-owned authoring defaults resolved once."""

    templates = template_index(project.game, project._authoring_template_specs())
    return {
        template_id: _template_with_preferred_language(
            template,
            project.preferred_language,
        )
        for template_id, template in templates.items()
    }


def _template_with_preferred_language(
    template: ModuleTemplate,
    preferred_language: str,
) -> ModuleTemplate:
    """Project one template's language default without mutating its descriptor."""

    preferred_canonical = canonical_language(preferred_language)
    args = []
    for arg in template.args:
        if arg.name != "language":
            args.append(arg)
            continue
        default = preferred_language
        if arg.choices:
            matching_choice = next(
                (choice for choice in arg.choices if canonical_language(choice) == preferred_canonical),
                None,
            )
            if matching_choice is None:
                default = arg.default
            else:
                default = matching_choice
        args.append(replace(arg, default=default))
    return replace(template, args=tuple(args))


def _browser_family_id(
    family: str,
    registry: "BuildRegistry | None" = None,
) -> str:
    if registry is not None:
        try:
            return registry.presentation_for(family).id
        except ValueError:
            pass
    return family.strip().casefold().replace("_", "-")


def _browser_family_name(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def _canonical_browser_family(
    family: str,
    registry: "BuildRegistry | None" = None,
) -> str:
    if registry is not None:
        try:
            return registry.resolve_family(family)
        except ValueError:
            pass
    return _browser_family_name(family)


def _resolve_module_template(
    templates: Mapping[str, ModuleTemplate],
    template_id: str,
    registry: "BuildRegistry",
) -> ModuleTemplate:
    direct = templates.get(template_id)
    if direct is not None and direct.kind == "module":
        return direct
    if direct is not None:
        raise ValueError(f"Template {template_id!r} creates a collection, not a module.")
    family = _canonical_browser_family(template_id, registry)
    matches = [template for template in templates.values() if template.family == family and template.kind == "module"]
    if not matches:
        raise ValueError(f"Unknown module template or family: {template_id}")
    project_matches = [template for template in matches if template.source == "project"]
    selected = project_matches or matches
    if len(selected) > 1:
        ids = ", ".join(template.template_id for template in selected)
        raise ValueError(f"Module family {template_id!r} is ambiguous; use one of: {ids}")
    return selected[0]


def _resolve_collection_template(
    templates: Mapping[str, ModuleTemplate],
    template_id: str,
    registry: "BuildRegistry",
) -> ModuleTemplate:
    """Resolve one explicit or unambiguous collection template."""

    direct = templates.get(template_id)
    if direct is not None and direct.kind == "collection":
        return direct
    if direct is not None:
        raise ValueError(f"Template {template_id!r} creates a module, not a collection.")
    family = _canonical_browser_family(template_id, registry)
    matches = [template for template in templates.values() if template.family == family and template.kind == "collection"]
    if not matches:
        raise ValueError(f"Unknown collection template or family: {template_id}")
    project_matches = [template for template in matches if template.source == "project"]
    selected = project_matches or matches
    if len(selected) > 1:
        ids = ", ".join(template.template_id for template in selected)
        raise ValueError(f"Collection family {template_id!r} is ambiguous; use one of: {ids}")
    return selected[0]


def _registered_family_ids(registry: "BuildRegistry") -> frozenset[str]:
    return frozenset(str(getattr(family, "family")) for family in registry.families if str(getattr(family, "family", "")).strip())


def _template_listing_candidates(
    templates: Iterable[ModuleTemplate],
    *,
    include_shadowed_builtin: bool,
) -> tuple[ModuleTemplate, ...]:
    """Hide generic fallback choices superseded by project-owned templates."""

    rows = tuple(templates)
    if include_shadowed_builtin:
        return rows
    project_targets = {(template.family, template.kind) for template in rows if template.source == "project"}
    return tuple(template for template in rows if template.source != "builtin" or (template.family, template.kind) not in project_targets)


def _template_views(
    templates: Iterable[ModuleTemplate],
    registered_families: frozenset[str],
    default_assets_by_family: Mapping[str, Mapping[str, Mapping[str, object]]],
    registry: "BuildRegistry",
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for template in templates:
        row = template.to_view()
        row["family_id"] = _browser_family_id(template.family, registry)
        default_assets = default_assets_by_family.get(template.family, {})
        row["default_assets"] = {slot: dict(asset) for slot, asset in default_assets.items()}
        ready = template.family in registered_families
        row["authoring_ready"] = ready
        if not ready:
            row["diagnostic_codes"] = ["template.unknown_family"]
        rows.append(row)
    return rows


def _filter_template_views(
    rows: list[dict[str, object]],
    *,
    template_id: str | None,
    family: str | None,
    kind: Literal["module", "collection"] | None,
    source: str | None,
    authoring_ready: bool | None,
    diagnostic_code: str | None,
) -> list[dict[str, object]]:
    return [
        row
        for row in rows
        if _template_row_matches(
            row,
            template_id=template_id,
            family=family,
            kind=kind,
            source=source,
            authoring_ready=authoring_ready,
            diagnostic_code=diagnostic_code,
        )
    ]


def _template_row_matches(
    row: dict[str, object],
    *,
    template_id: str | None,
    family: str | None,
    kind: Literal["module", "collection"] | None,
    source: str | None,
    authoring_ready: bool | None,
    diagnostic_code: str | None,
) -> bool:
    return (
        _matches_template_value(row.get("id"), template_id)
        and _matches_template_value(row.get("family"), family)
        and _matches_template_value(row.get("kind"), kind)
        and _matches_template_value(row.get("source"), source)
        and (authoring_ready is None or row.get("authoring_ready") is authoring_ready)
        and _matches_template_diagnostic(row.get("diagnostic_codes"), diagnostic_code)
    )


def _matches_template_value(value: object, expected: str | None) -> bool:
    return expected is None or value == expected


def _matches_template_diagnostic(value: object, expected: str | None) -> bool:
    if expected is None:
        return True
    return expected in value if isinstance(value, list) else False


def _template_index(rows: list[dict[str, object]]) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {
        "id": {},
        "family": {},
        "family_id": {},
        "kind": {},
        "source": {},
        "authoring_ready": {},
        "diagnostic_code": {},
    }
    for row_index, row in enumerate(rows):
        _append_template_index(index["id"], row.get("id"), row_index)
        _append_template_index(index["family"], row.get("family"), row_index)
        _append_template_index(index["family_id"], row.get("family_id"), row_index)
        _append_template_index(index["kind"], row.get("kind"), row_index)
        _append_template_index(index["source"], row.get("source"), row_index)
        ready = row.get("authoring_ready")
        if isinstance(ready, bool):
            _append_template_index(index["authoring_ready"], str(ready).lower(), row_index)
        for code in (row.get("diagnostic_codes") if isinstance(row.get("diagnostic_codes"), list) else ()):
            _append_template_index(index["diagnostic_code"], code, row_index)
    return {name: {key: bucket[key] for key in sorted(bucket)} for name, bucket in index.items() if bucket}


def _append_template_index(bucket: dict[str, list[int]], value: object, row_index: int) -> None:
    if isinstance(value, str) and value:
        append_index_entry(bucket, value, row_index)


def _require_template_authoring_ready(template: ModuleTemplate, registered_families: frozenset[str]) -> None:
    if template.family in registered_families:
        return
    raise ValueError(
        f"Template {template.template_id!r} targets unknown build family {template.family!r}. "
        "Declare the family under paradev.yaml 'families' before scaffolding."
    )


def _load_python_modules(manifest: dict[str, object], root: Path, path: Path) -> tuple[Path, ...]:
    value = manifest.get("python_modules")
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ProjectManifestError(f"{path} key 'python_modules' must be a list of Python module paths.")
    modules: list[Path] = []
    for index, item in enumerate(value):
        key = f"python_modules[{index}]"
        if not isinstance(item, str) or not item.strip():
            raise ProjectManifestError(f"{path} key {key!r} must be a non-empty Python module path.")
        module_path = _resolve_path(root, item.strip(), key, path)
        try:
            module_path.relative_to(root)
        except ValueError as error:
            raise ProjectManifestError(f"{path} key {key!r} must stay under the project root.") from error
        if module_path.suffix != ".py":
            raise ProjectManifestError(f"{path} key {key!r} must point to a .py file.")
        if not module_path.is_file():
            raise ProjectManifestError(f"{path} key {key!r} does not exist: {item.strip()}")
        modules.append(module_path)
    return tuple(modules)


def _require_str(data: dict[str, object], key: str, path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProjectManifestError(f"{path} key {key!r} must be a non-empty string.")
    return value.strip()


def _require_project_id(data: dict[str, object], path: Path) -> str:
    project_id = _require_str(data, "project_id", path)
    if project_id in {".", ".."} or "/" in project_id or "\\" in project_id or any(not (char.isalnum() or char in "._-") for char in project_id):
        raise ProjectManifestError(f"{path} key 'project_id' must be one safe filename segment using letters, numbers, '.', '_', or '-'.")
    return project_id


def _require_source_roots(data: dict[str, object], path: Path) -> list[str]:
    value = data.get("source_roots")
    if not isinstance(value, list) or not value:
        raise ProjectManifestError(f"{path} key 'source_roots' must be a non-empty list of paths.")
    roots: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ProjectManifestError(f"{path} key 'source_roots' must contain only non-empty path strings.")
        roots.append(item.strip())
    return roots


def _resolve_path(root: Path, value: str, key: str, path: Path) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve()
    except OSError as error:
        raise ProjectManifestError(f"{path} key {key!r} cannot be resolved: {value}") from error


def _resolve_generated_path(root: Path, value: str) -> Path:
    """Return a lexical absolute generated path without following symlinks."""

    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return _absolute_lexical_path(candidate)


def _absolute_lexical_path(path: Path) -> Path:
    absolute = Path(os.path.abspath(path.expanduser()))
    if sys.platform == "darwin" and len(absolute.parts) > 1 and absolute.parts[1] in {"etc", "tmp", "var"}:
        return Path("/private").joinpath(*absolute.parts[1:])
    return absolute


def _select_source_root(
    project_root: Path,
    source_roots: tuple[Path, ...],
    source_root: str | os.PathLike[str] | None,
) -> Path:
    if not source_roots:
        raise ValueError("Project has no configured source roots.")
    if source_root is None:
        return source_roots[0]
    candidate = Path(source_root).expanduser()
    if not candidate.is_absolute():
        candidate = project_root / candidate
    resolved = candidate.resolve()
    for configured in source_roots:
        if configured == resolved:
            return configured
    available = ", ".join(_project_relative_path(project_root, configured) for configured in source_roots)
    raise ValueError(f"Unknown source root {source_root!s}. Available source roots: {available}.")


def _project_relative_path(root: Path, target: Path) -> str:
    try:
        return target.relative_to(root).as_posix()
    except ValueError:
        return str(target)


def _build_parallelism(value: int | None) -> int:
    raw = CM_PARADEV.get("paradev.build.parallelism", default=1) if value is None else value
    try:
        parallelism = int(raw)
    except (TypeError, ValueError) as error:
        raise ValueError("paradev.build.parallelism must be a positive integer.") from error
    if parallelism < 1:
        raise ValueError("paradev.build.parallelism must be a positive integer.")
    return parallelism


def _build_strict_metadata(value: bool | str | None) -> bool:
    raw = CM_PARADEV.get("paradev.build.strict_metadata", default=False) if value is None else value
    try:
        return _bool_value(raw)
    except ValueError as error:
        raise ValueError("paradev.build.strict_metadata must be a boolean.") from error


def _load_published_diagnostics_manifest(
    project: Project,
    *,
    profile: str | None,
) -> dict[str, object]:
    """Load the last emitted diagnostics manifest through its owned build root."""

    from paradev.build._fs import open_anchored_directory
    from paradev.build.manifest import (
        MANIFEST_SCHEMAS,
        diagnostic_family_index,
        diagnostic_index,
    )

    path = project.build_root / "diagnostics.json"
    try:
        with open_anchored_directory(project.build_root, create=False) as build_root:
            encoded = build_root.read_bytes("diagnostics.json")
    except FileNotFoundError as error:
        raise ValueError(f"No published build diagnostics are available for project {project.project_id!r}: {path}.") from error
    if encoded is None:
        raise ValueError(f"No published build diagnostics are available for project {project.project_id!r}: {path}.")
    try:
        payload = json.loads(encoded)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Published build diagnostics are not valid UTF-8 JSON: {path}.") from error
    if not isinstance(payload, dict):
        raise ValueError(f"Published build diagnostics must be a JSON object: {path}.")
    if payload.get("schema") != MANIFEST_SCHEMAS["diagnostics.json"]:
        raise ValueError(f"Published build diagnostics use an unsupported schema: {path}.")
    if payload.get("project_id") != project.project_id:
        raise ValueError(f"Published build diagnostics belong to a different project: {path}.")
    if profile is not None and payload.get("profile") != profile:
        raise ValueError(f"Published build diagnostics do not match profile {profile!r}: {path}.")
    rows = payload.get("diagnostics")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"Published build diagnostics contain an invalid diagnostics list: {path}.")
    if payload.get("index") != diagnostic_index(rows):
        raise ValueError(f"Published build diagnostics contain an invalid severity/code index: {path}.")
    if payload.get("family_index") != diagnostic_family_index(rows):
        raise ValueError(f"Published build diagnostics contain an invalid family index: {path}.")
    return payload


def _inspection_rows() -> list[ProjectInspectionRow]:
    return [
        {
            "kind": kind,
            "method": f"Project.{method_name}",
            "cli_command": PROJECT_INSPECTION_CLI_COMMANDS.get(kind, kind),
            "filters": _inspection_filters(getattr(Project, method_name)),
        }
        for kind, method_name in PROJECT_INSPECTION_METHODS.items()
    ]


def _inspection_filters(method: object) -> list[str]:
    return [name for name in signature(method).parameters if name not in {"self", "registry"}]


def _inspection_index(rows: list[ProjectInspectionRow]) -> ProjectInspectionIndex:
    kind_index: dict[str, list[int]] = {}
    filter_index: dict[str, list[str]] = {}
    for index, row in enumerate(rows):
        kind = row.get("kind")
        if isinstance(kind, str):
            kind_index[kind] = [index]
        filters = row.get("filters")
        for filter_name in filters if isinstance(filters, list) else ():
            if isinstance(filter_name, str):
                append_index_entry(filter_index, filter_name, kind)
    return {"kind": kind_index, "filter": filter_index}


def _project_inspection_index_catalog_table_rows() -> list[str]:
    return [
        "| "
        + " | ".join(
            [
                code_cell(row["id"]),
                code_cell(row["contract_path"]),
                code_cell(row["python_helper"]),
                markdown_cell(row["usage"]),
            ]
        )
        + " |"
        for row in get_project_inspection_index_catalog()
    ]


def _project_inspection_kind_table_rows(
    contract: ProjectInspectionContract,
) -> list[str]:
    return [
        "| "
        + " | ".join(
            [
                code_cell(row["kind"]),
                code_cell(row["method"]),
                code_cell(row["cli_command"]),
                code_list_cell(row["filters"]),
            ]
        )
        + " |"
        for row in contract["inspections"]
    ]


def _project_inspection_filter_index_table_rows(
    contract: ProjectInspectionContract,
) -> list[str]:
    return [index_row(filter_name, kinds) for filter_name, kinds in contract["index"]["filter"].items()]


def _inspection_kind(kind: str) -> str:
    text = kind.strip().lower().replace("_", "-") if isinstance(kind, str) else ""
    if text in PROJECT_INSPECTION_METHODS:
        return text
    available = ", ".join(sorted(PROJECT_INSPECTION_METHODS))
    raise ValueError(f"Unknown project inspection kind: {kind}. Available kinds: {available}.")


def _inspection_method_name(kind: str) -> str:
    return PROJECT_INSPECTION_METHODS[_inspection_kind(kind)]


def _bool_value(value: bool | str) -> bool:
    if type(value) is bool:
        return value
    text = value.strip().lower() if isinstance(value, str) else ""
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"", "0", "false", "no", "off"}:
        return False
    raise ValueError(f"Expected boolean value, got {value!r}.")


def _explain_source_path(root: Path, source_path: str | os.PathLike[str] | None) -> str | None:
    if source_path is None:
        return None
    candidate = Path(source_path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return str(candidate.resolve())


def _explain_source_request(
    source_path: str | os.PathLike[str] | None,
) -> str | os.PathLike[str] | None:
    if isinstance(source_path, str):
        return _explain_target_text("--source", source_path)
    return source_path


def _explain_target_text(flag: str, value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        raise ValueError(f"{flag} must be non-empty.")
    return text
