"""SDK authoring templates for source-module scaffolding."""

from __future__ import annotations

import hashlib
import inspect
import logging
import math
import os
import stat
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, is_dataclass
from pathlib import Path, PurePosixPath
from string import Formatter
from typing import Any, Literal, cast
from uuid import uuid4

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import (
    api_annotation_text,
    api_standard_table,
    api_table_selection,
)
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)
from paradev.portable_paths import (
    portable_authoring_title,
    windows_portable_component_error,
)

logger = logging.getLogger(__name__)

TEMPLATES_SCHEMA = "paradev.sdk.templates.v1"
MODULE_SCAFFOLD_SCHEMA = "paradev.sdk.module_scaffold.v1"
COLLECTION_SCAFFOLD_SCHEMA = "paradev.sdk.collection_scaffold.v1"
TEMPLATES_API_TABLE_SCHEMA = "paradev.sdk.templates.api-table.v1"
_TEMPLATES_API_REFERENCE_PAGE = "docs/user-manual/templates-api-reference.md"
_TEMPLATES_API_TEST_ANCHOR = "tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract"
_TEMPLATES_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")
TemplateRenderer = Callable[[Mapping[str, str]], Sequence["TemplateFile"]]
_ARG_TYPES = {"asset", "boolean", "choice", "number", "string", "text"}
_TEMPLATE_LABEL_WORDS = {
    "ai": "AI",
    "dds": "DDS",
    "dlc": "DLC",
    "gfx": "GFX",
    "gui": "GUI",
    "hoi4": "HoI4",
    "id": "ID",
    "mio": "MIO",
    "pdx": "PDX",
    "ui": "UI",
    "url": "URL",
    "xp": "XP",
}
_ANCHORED_SCAFFOLD_SUPPORTED = (
    os.open in os.supports_dir_fd
    and os.mkdir in os.supports_dir_fd
    and os.rmdir in os.supports_dir_fd
    and os.stat in os.supports_dir_fd
    and os.rename in os.supports_dir_fd
    and os.unlink in os.supports_dir_fd
    and os.link in os.supports_dir_fd
    and os.link in os.supports_follow_symlinks
    and os.listdir in os.supports_fd
    and hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
)

__all__ = [
    "TEMPLATES_SCHEMA",
    "MODULE_SCAFFOLD_SCHEMA",
    "COLLECTION_SCAFFOLD_SCHEMA",
    "ProjectTemplateSpecError",
    "TemplateArg",
    "TemplateFile",
    "ModuleTemplate",
    "builtin_module_templates",
    "project_module_templates",
    "template_index",
    "module_scaffold_plan",
    "collection_scaffold_plan",
    "TEMPLATES_API_TABLE_SCHEMA",
    "TemplatesApiRow",
    "TemplatesApiTable",
    "get_templates_api_selection",
    "get_templates_api_table",
    "render_templates_api_reference_markdown",
]


class ProjectTemplateSpecError(ValueError):
    """Raised when project-local SDK templates are invalid."""


class _AnchoredScaffoldUnavailable(OSError):
    """Raised when safe no-follow scaffold writes are unavailable."""


class _ScaffoldRollbackIncomplete(OSError):
    """Raised when recovery data must be retained after an incomplete rollback."""

    def __init__(self, message: str, recovery_path: Path) -> None:
        super().__init__(message)
        self.recovery_path = recovery_path


def _uses_win32_scaffold_authority() -> bool:
    """Return whether module scaffolds require the retained Win32 backend."""

    return os.name == "nt"


def _write_scaffold_files_win32(
    *,
    project_root: Path,
    source_root: Path,
    container: str = "modules",
    family: str,
    object_id: str,
    folder_name: str,
    rendered_files: list[dict[str, object]],
    force: bool,
) -> None:
    """Dispatch one scaffold through the private retained Win32 adapter."""

    from paradev.sdk._module_fs_windows import (
        WindowsModuleMutationUnavailable,
        WindowsScaffoldRollbackIncomplete,
        write_scaffold_files_windows,
    )

    try:
        if container == "modules":
            write_scaffold_files_windows(
                project_root=project_root,
                source_root=source_root,
                family=family,
                object_id=object_id,
                folder_name=folder_name,
                rendered_files=rendered_files,
                force=force,
            )
        else:
            write_scaffold_files_windows(
                project_root=project_root,
                source_root=source_root,
                container=container,
                family=family,
                object_id=object_id,
                folder_name=folder_name,
                rendered_files=rendered_files,
                force=force,
            )
    except WindowsModuleMutationUnavailable as error:
        raise _AnchoredScaffoldUnavailable(str(error)) from error
    except WindowsScaffoldRollbackIncomplete as error:
        raise _ScaffoldRollbackIncomplete(str(error), error.recovery_path) from error


def _write_scaffold_batch_win32(
    *,
    project_root: Path,
    source_root: Path,
    scaffolds: Sequence[tuple[str, str, str, list[dict[str, object]]]],
    validate: Callable[[], None] | None = None,
) -> None:
    """Dispatch one scaffold batch through the retained Win32 adapter."""

    from paradev.sdk._module_fs_windows import (
        WindowsModuleMutationUnavailable,
        WindowsScaffoldRollbackIncomplete,
        write_scaffold_batch_windows,
    )

    try:
        write_scaffold_batch_windows(
            project_root=project_root,
            source_root=source_root,
            scaffolds=scaffolds,
            validate=validate,
        )
    except WindowsModuleMutationUnavailable as error:
        raise _AnchoredScaffoldUnavailable(str(error)) from error
    except WindowsScaffoldRollbackIncomplete as error:
        raise _ScaffoldRollbackIncomplete(str(error), error.recovery_path) from error


@dataclass(slots=True)
class _ScaffoldInstall:
    """One staged scaffold file and its reversible install state."""

    parent_fd: int
    target_name: str
    stage_name: str
    backup_name: str
    target_existed: bool
    backup_moved: bool = False
    backup_identity: tuple[int, int] | None = None
    backup_size: int | None = None
    backup_digest: str | None = None
    installed: bool = False
    installed_identity: tuple[int, int] | None = None
    installed_size: int | None = None
    installed_digest: str | None = None


@dataclass(slots=True)
class _ScaffoldCreatedDirectory:
    """A newly created directory retained by an anchored parent descriptor."""

    parent_fd: int
    name: str
    identity: tuple[int, int]
    quarantine_name: str


@dataclass(slots=True)
class _ScaffoldBatchModule:
    """One create-only module participating in an anchored batch write."""

    family: str
    object_id: str
    folder_name: str
    rendered_files: list[dict[str, object]]
    family_fd: int | None = None
    module_fd: int | None = None
    module_identity: tuple[int, int] | None = None
    module_created: bool = False
    created_directories: list[_ScaffoldCreatedDirectory] | None = None
    quarantine_name: str = ""


@dataclass(slots=True)
class _ScaffoldRecoveryTree:
    """Exact descriptor-anchored subset owned by an interrupted scaffold."""

    identity: tuple[int, int]
    files: dict[str, tuple[tuple[int, int], int, str]]
    directories: dict[str, "_ScaffoldRecoveryTree"]


@dataclass(frozen=True, slots=True)
class TemplateArgReference:
    """Project-browser identity suggested for one template argument."""

    kind: Literal["module", "collection"]
    family: str

    def to_view(self) -> dict[str, str]:
        """Return the transport-neutral reference selector contract."""

        return {
            "kind": self.kind,
            "family": self.family,
        }


@dataclass(frozen=True, slots=True)
class TemplateArg:
    """One user-supplied authoring-template argument.

    Attributes:
        name: Stable placeholder name used by the template renderer.
        required: Whether the user must provide a value.
        default: Scalar value used when the user leaves the field unchanged.
        type: GUI and validation type for the value.
        label: Optional extension-owned human-readable field label.
        description: Optional extension-owned domain guidance.
        choices: Optional closed set of accepted scalar values.
        reference: Optional project-browser identity used to suggest existing
            modules or collections without restricting free-form compatibility.
        advanced: Optional progressive-disclosure override. ``None`` preserves
            the compatibility default of hiding fields with non-empty defaults.
    """

    name: str
    required: bool = False
    default: str = ""
    type: str = "string"
    label: str = ""
    description: str = ""
    choices: tuple[str, ...] = ()
    reference: TemplateArgReference | None = None
    advanced: bool | None = None

    def to_view(self) -> dict[str, object]:
        """Return a JSON-safe argument view."""

        view: dict[str, object] = {
            "required": self.required,
            "default": self.default,
            "advanced": (bool(self.default) if self.advanced is None else self.advanced),
            "type": self.type,
        }
        if self.label:
            view["label"] = self.label
        if self.description:
            view["description"] = self.description
        if self.choices:
            view["choices"] = list(self.choices)
        if self.reference is not None:
            view["reference"] = self.reference.to_view()
        return view

    def to_form_field(self) -> dict[str, object]:
        """Return a GUI-ready form-field projection for this argument."""

        view = {
            "name": self.name,
            "target": "values",
            "label": self.label or _template_arg_label(self.name),
        }
        view.update(self.to_view())
        return view


@dataclass(frozen=True, slots=True)
class TemplateFile:
    """One relative source file produced by an authoring template."""

    path: str
    content: str


@dataclass(frozen=True, slots=True)
class ModuleTemplate:
    """One Registry-backed module or collection authoring template.

    The historical class name remains as a compatibility alias for extension
    packages. ``kind`` is the authoritative target contract.
    """

    template_id: str
    family: str
    title: str
    args: tuple[TemplateArg, ...]
    files: tuple[TemplateFile, ...]
    system_files: tuple[TemplateFile, ...] = ()
    directory: str = "{object_id}"
    source: str = "project"
    renderer: TemplateRenderer | None = None
    kind: Literal["module", "collection"] = "module"

    def to_view(self) -> dict[str, object]:
        """Return a JSON-safe template view."""

        arg_views: dict[str, dict[str, object]] = {}
        form_fields: list[dict[str, object]] = []
        for arg in self.args:
            description = arg.description or _generated_template_arg_description(
                self,
                arg,
            )
            description_source = "declared" if arg.description else "generated"
            arg_view = arg.to_view()
            arg_view["description"] = description
            arg_view["description_source"] = description_source
            arg_views[arg.name] = arg_view

            form_field = arg.to_form_field()
            form_field["description"] = description
            form_field["description_source"] = description_source
            form_fields.append(form_field)

        return {
            "id": self.template_id,
            "title": self.title,
            "family": self.family,
            "kind": self.kind,
            "source": self.source,
            "directory": self.directory,
            "args": arg_views,
            "form": {"fields": form_fields},
            "files": [file.path for file in self.files],
            "renderer": "python" if self.renderer is not None else "files",
        }


def _generated_template_arg_description(
    template: ModuleTemplate,
    arg: TemplateArg,
) -> str:
    """Describe an undeclared template argument from its real render usage."""

    destinations = _template_arg_destinations(template, arg.name)
    target = _joined_help_targets(destinations)
    if arg.name == "title":
        if target:
            return f"Preferred-language display name used by {target}."
        return "Preferred-language display name for the new source unit."
    if arg.name == "description":
        if target:
            return f"Preferred-language explanatory text written to {target}."
        return "Preferred-language explanatory text for the new source unit."
    if arg.name == "language":
        if target:
            return f"Localization language code, such as `zh` or `en`, used by {target}."
        return "Localization language code, such as `zh` or `en`."

    label = arg.label or _template_arg_label(arg.name)
    inline_label = _inline_template_arg_label(label)
    if arg.type == "asset":
        subject = f"Source asset for {inline_label}"
    elif arg.type == "boolean":
        subject = f"Whether {inline_label} is enabled"
    elif arg.type == "choice":
        subject = f"Selected {inline_label}"
    elif arg.type == "number":
        subject = f"Numeric {inline_label}"
    elif arg.type == "text":
        subject = f"PDX or text content for {inline_label}"
    else:
        subject = label
    if target:
        return f"{subject} used by {target}."
    if template.renderer is not None:
        return f"{subject} passed to this template's renderer."
    return f"{subject} used by this authoring template."


def _template_arg_destinations(
    template: ModuleTemplate,
    arg_name: str,
) -> tuple[str, ...]:
    """Return concise generated destinations that reference one argument."""

    destinations: list[str] = []
    if arg_name in _format_field_names(template.directory, strict=False):
        destinations.append("the readable collection folder name" if template.kind == "collection" else "the readable module folder name")
    for file in (*template.files, *template.system_files):
        fields = _format_field_names(file.path, strict=False)
        fields.update(_format_field_names(file.content, strict=False))
        if arg_name in fields:
            destinations.append(f"`{file.path}`")
    return tuple(dict.fromkeys(destinations))


def _joined_help_targets(destinations: Sequence[str]) -> str:
    """Join a short destination list for generated user-facing help."""

    if not destinations:
        return ""
    if len(destinations) == 1:
        return destinations[0]
    if len(destinations) == 2:
        return f"{destinations[0]} and {destinations[1]}"
    return f"{', '.join(destinations[:-1])}, and {destinations[-1]}"


class TemplatesApiRow(TypedDict):
    """One public `paradev.sdk.templates` API row."""

    symbol: str
    kind: str
    layer: str
    module: str
    feature: str
    import_path: str
    returns: str
    value: str
    registry_seam: str
    surface: str
    doc_page: str
    test_anchor: str


class TemplatesApiTable(TypedDict):
    """Generated API-standard table for SDK authoring-template helpers."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[TemplatesApiRow]


def builtin_module_templates(game: str) -> tuple[ModuleTemplate, ...]:
    """Return built-in authoring templates for a game profile.

    Args:
        game: Project game profile.

    Returns:
        Built-in source-module authoring templates.
    """

    if game != "hoi4":
        return ()
    return (
        ModuleTemplate(
            template_id="hoi4:idea/basic",
            title="Basic HoI4 Idea",
            family="idea",
            source="builtin",
            args=(
                TemplateArg("title"),
                TemplateArg("description", type="text"),
                TemplateArg("category", default="country"),
                TemplateArg("language", default="en"),
            ),
            files=(
                TemplateFile("meta.yaml", "title: {title}\n"),
                TemplateFile(
                    "def.txt",
                    "ideas = {{\n" "\t{category} = {{\n" "\t\t{object_id} = {{\n" "\t\t\tpicture = {object_id}\n" "\t\t}}\n" "\t}}\n" "}}\n",
                ),
                TemplateFile(
                    "main.loc",
                    "[{language}.{object_id}]\n" "{title}\n\n" "[{language}.{object_id}_desc]\n" "{description}\n",
                ),
            ),
        ),
    )


def project_module_templates(value: object, path: Path) -> tuple[ModuleTemplate, ...]:
    """Parse project-local authoring templates from a manifest value.

    Args:
        value: Raw `templates` manifest value.
        path: Manifest path for diagnostics.

    Returns:
        Parsed project-local templates.

    Raises:
        ProjectTemplateSpecError: If a template declaration is invalid.
    """

    if value is None:
        return ()
    if not isinstance(value, dict):
        raise ProjectTemplateSpecError(f"{path} key 'templates' must be a mapping of template ids.")
    specs: list[ModuleTemplate] = []
    seen: set[str] = set()
    for template_id, raw_spec in value.items():
        key = f"templates.{template_id}"
        clean_id = _require_template_id(template_id, key, path)
        if clean_id in seen:
            raise ProjectTemplateSpecError(f"{path} key {key!r} is declared more than once.")
        seen.add(clean_id)
        if not isinstance(raw_spec, dict):
            raise ProjectTemplateSpecError(f"{path} key {key!r} must be a mapping.")
        family = _require_path_token(raw_spec.get("family"), f"{key}.family", path)
        kind = _template_kind(raw_spec.get("kind"), f"{key}.kind", path)
        title = _optional_string(raw_spec.get("title"), clean_id, f"{key}.title", path)
        directory = _optional_string(
            raw_spec.get("directory"),
            "{object_id}",
            f"{key}.directory",
            path,
        )
        args = _template_args(raw_spec.get("args"), key, path)
        files = _template_files(raw_spec.get("files"), key, path)
        system_files = _template_system_files(
            raw_spec.get("system_files"),
            key,
            path,
        )
        specs.append(
            ModuleTemplate(
                template_id=clean_id,
                title=title,
                family=family,
                args=args,
                files=files,
                system_files=system_files,
                directory=directory,
                kind=kind,
            )
        )
    return tuple(specs)


def template_index(game: str, project_templates: tuple[ModuleTemplate, ...]) -> dict[str, ModuleTemplate]:
    """Return built-in templates with project-local overrides applied."""

    templates = {template.template_id: template for template in builtin_module_templates(game)}
    for template in project_templates:
        templates[template.template_id] = template
    return dict(sorted(templates.items()))


def _module_scaffold_draft(
    *,
    project_id: str,
    project_root: Path,
    source_root: Path,
    template: ModuleTemplate,
    object_id: str,
    values: Mapping[str, object] | None = None,
    source_slots: Sequence[object] = (),
    system_files: Sequence[tuple[str, str]] = (),
    force: bool = False,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    """Render one scaffold once and return its JSON plan plus private files."""

    if template.kind != "module":
        raise ValueError(f"Template {template.template_id!r} targets a collection; " "use collection_scaffold_plan().")
    project_root = project_root.absolute()
    source_root = source_root.absolute()
    clean_object_id = _require_path_token(object_id, "object_id", project_root)
    module_id = f"{template.family}/{clean_object_id}"
    diagnostics: list[dict[str, object]] = []
    render_values = _render_values(template, clean_object_id, values, diagnostics)
    requested_folder_name = _render_module_folder_name(
        template,
        clean_object_id,
        render_values,
        diagnostics,
    )
    folder_name = _resolve_scaffold_module_folder_name(
        template,
        source_root=source_root,
        object_id=clean_object_id,
        requested_folder_name=requested_folder_name,
        diagnostics=diagnostics,
    )
    module_root = source_root / "modules" / template.family / folder_name
    rendered_files = _render_files(template, module_root, render_values, diagnostics)
    path_diagnostics = _scaffold_path_diagnostics(
        template,
        project_root=project_root,
        source_root=source_root,
        rendered_files=rendered_files,
    )
    diagnostics.extend(path_diagnostics)
    if not path_diagnostics and not any(item.get("severity") == "error" for item in diagnostics):
        diagnostics.extend(
            _scaffold_source_slot_diagnostics(
                template,
                module_id=module_id,
                rendered_files=rendered_files,
                source_slots=source_slots,
            )
        )
    template_system_files = _render_template_system_files(
        template,
        values=render_values,
        diagnostics=diagnostics,
    )
    system_rendered, system_diagnostics = _render_system_files(
        template,
        module_root=module_root,
        files=(*template_system_files, *system_files),
    )
    diagnostics.extend(system_diagnostics)
    rendered_files.extend(system_rendered)
    if not path_diagnostics:
        diagnostics.extend(_existing_file_diagnostics(template, rendered_files, force=force))
    blocked = any(item.get("severity") == "error" for item in diagnostics)
    plan: dict[str, object] = {
        "schema": MODULE_SCAFFOLD_SCHEMA,
        "project_id": project_id,
        "project_root": str(project_root),
        "template_id": template.template_id,
        "family": template.family,
        "object_id": clean_object_id,
        "module_id": module_id,
        "folder_name": folder_name,
        "source_root": str(source_root),
        "root": str(module_root),
        "values": render_values,
        "renderer": "python" if template.renderer is not None else "files",
        "blocked": blocked,
        "written": False,
        "diagnostics": diagnostics,
        "files": [_file_view(project_root, item, force=force, unsafe=bool(path_diagnostics)) for item in rendered_files],
    }
    return plan, rendered_files, path_diagnostics


def _collection_scaffold_draft(
    *,
    project_id: str,
    project_root: Path,
    source_root: Path,
    template: ModuleTemplate,
    collection_id: str,
    values: Mapping[str, object] | None = None,
    source_slots: Sequence[object] = (),
    force: bool = False,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    """Render one collection scaffold and retain private file contents."""

    if template.kind != "collection":
        raise ValueError(f"Template {template.template_id!r} targets a module; " "use module_scaffold_plan().")
    project_root = project_root.absolute()
    source_root = source_root.absolute()
    clean_collection_id = _require_path_token(
        collection_id,
        "collection_id",
        project_root,
    )
    diagnostics: list[dict[str, object]] = []
    render_values = _render_values(
        template,
        clean_collection_id,
        values,
        diagnostics,
    )
    render_values["collection_id"] = clean_collection_id
    requested_folder_name = _render_module_folder_name(
        template,
        clean_collection_id,
        render_values,
        diagnostics,
    )
    folder_name = _resolve_scaffold_module_folder_name(
        template,
        source_root=source_root,
        object_id=clean_collection_id,
        requested_folder_name=requested_folder_name,
        diagnostics=diagnostics,
        container="collections",
        target_label="Collection",
    )
    collection_root = source_root / "collections" / template.family / folder_name
    rendered_files = _render_files(
        template,
        collection_root,
        render_values,
        diagnostics,
    )
    path_diagnostics = _scaffold_path_diagnostics(
        template,
        project_root=project_root,
        source_root=source_root,
        rendered_files=rendered_files,
    )
    diagnostics.extend(path_diagnostics)
    if not path_diagnostics and not any(item.get("severity") == "error" for item in diagnostics):
        diagnostics.extend(
            _scaffold_source_slot_diagnostics(
                template,
                module_id=f"{template.family}/{clean_collection_id}",
                rendered_files=rendered_files,
                source_slots=source_slots,
            )
        )
    template_system_files = _render_template_system_files(
        template,
        values=render_values,
        diagnostics=diagnostics,
    )
    system_rendered, system_diagnostics = _render_system_files(
        template,
        module_root=collection_root,
        files=template_system_files,
    )
    diagnostics.extend(system_diagnostics)
    rendered_files.extend(system_rendered)
    if not path_diagnostics:
        diagnostics.extend(
            _existing_file_diagnostics(
                template,
                rendered_files,
                force=force,
            )
        )
    blocked = any(item.get("severity") == "error" for item in diagnostics)
    plan: dict[str, object] = {
        "schema": COLLECTION_SCAFFOLD_SCHEMA,
        "project_id": project_id,
        "project_root": str(project_root),
        "template_id": template.template_id,
        "kind": "collection",
        "family": template.family,
        "object_id": clean_collection_id,
        "collection_id": clean_collection_id,
        "folder_name": folder_name,
        "source_root": str(source_root),
        "root": str(collection_root),
        "values": render_values,
        "renderer": "python" if template.renderer is not None else "files",
        "blocked": blocked,
        "written": False,
        "diagnostics": diagnostics,
        "files": [
            _file_view(
                project_root,
                item,
                force=force,
                unsafe=bool(path_diagnostics),
                target_kind="collection",
            )
            for item in rendered_files
        ],
    }
    return plan, rendered_files, path_diagnostics


def module_scaffold_plan(
    *,
    project_id: str,
    project_root: Path,
    source_root: Path,
    template: ModuleTemplate,
    object_id: str,
    values: Mapping[str, object] | None = None,
    source_slots: Sequence[object] = (),
    write: bool = False,
    force: bool = False,
) -> dict[str, object]:
    """Return or apply a JSON-safe source-module scaffold plan.

    Args:
        project_id: Owning project id.
        project_root: Project root path.
        source_root: Source root that receives the module.
        template: Template to render.
        object_id: New module object id.
        values: User-supplied template values.
        source_slots: Family source-slot declarations used to validate the
            prospective rendered files before anything is written.
        write: Whether to write files when the plan is not blocked.
        force: Whether existing files may be overwritten.

    Returns:
        JSON-safe scaffold plan.
    """

    return _module_scaffold_plan_with_system_files(
        project_id=project_id,
        project_root=project_root,
        source_root=source_root,
        template=template,
        object_id=object_id,
        values=values,
        source_slots=source_slots,
        write=write,
        force=force,
    )


def collection_scaffold_plan(
    *,
    project_id: str,
    project_root: Path,
    source_root: Path,
    template: ModuleTemplate,
    collection_id: str,
    values: Mapping[str, object] | None = None,
    source_slots: Sequence[object] = (),
    write: bool = False,
    force: bool = False,
) -> dict[str, object]:
    """Return or apply a JSON-safe source-collection scaffold plan."""

    plan, rendered_files, path_diagnostics = _collection_scaffold_draft(
        project_id=project_id,
        project_root=project_root,
        source_root=source_root,
        template=template,
        collection_id=collection_id,
        values=values,
        source_slots=source_slots,
        force=force,
    )
    project_root = Path(str(plan["project_root"]))
    source_root = Path(str(plan["source_root"]))
    collection_root = Path(str(plan["root"]))
    clean_collection_id = str(plan["collection_id"])
    folder_name = str(plan["folder_name"])
    diagnostics = cast(list[dict[str, object]], plan["diagnostics"])
    blocked = bool(plan["blocked"])
    written = False
    write_failed = False

    if write and not blocked:
        try:
            _write_scaffold_files_anchored(
                project_root=project_root,
                source_root=source_root,
                container="collections",
                family=template.family,
                object_id=clean_collection_id,
                folder_name=folder_name,
                rendered_files=rendered_files,
                force=force,
            )
        except _AnchoredScaffoldUnavailable as error:
            diagnostics.append(
                _scaffold_write_diagnostic(
                    template,
                    collection_root,
                    code="scaffold.unsupported_platform",
                    message=("Collection creation was blocked to protect your " f"files: {error}."),
                )
            )
            write_failed = True
        except _ScaffoldRollbackIncomplete as error:
            diagnostic = _scaffold_write_diagnostic(
                template,
                collection_root,
                code="scaffold.rollback_incomplete",
                message=("Collection creation could not restore every original " "file. Recovery data was preserved at " f"{error.recovery_path}: {error}."),
            )
            diagnostic["recovery_path"] = str(error.recovery_path)
            diagnostics.append(diagnostic)
            write_failed = True
        except OSError as error:
            diagnostics.append(
                _scaffold_write_diagnostic(
                    template,
                    collection_root,
                    code="scaffold.concurrent_change",
                    message=("Collection source changed before the scaffold could " f"be written safely: {error}."),
                )
            )
            write_failed = True
        else:
            written = True
        blocked = any(item.get("severity") == "error" for item in diagnostics)

    plan.pop("project_root")
    plan["blocked"] = blocked
    plan["written"] = written
    plan["files"] = [
        _file_view(
            project_root,
            item,
            force=force,
            unsafe=bool(path_diagnostics) or write_failed,
            target_kind="collection",
        )
        for item in rendered_files
    ]
    return plan


def _module_scaffold_plan_with_system_files(
    *,
    project_id: str,
    project_root: Path,
    source_root: Path,
    template: ModuleTemplate,
    object_id: str,
    values: Mapping[str, object] | None = None,
    source_slots: Sequence[object] = (),
    system_files: Sequence[tuple[str, str]] = (),
    write: bool = False,
    force: bool = False,
) -> dict[str, object]:
    """Apply one scaffold with trusted SDK-owned hidden state."""

    plan, rendered_files, path_diagnostics = _module_scaffold_draft(
        project_id=project_id,
        project_root=project_root,
        source_root=source_root,
        template=template,
        object_id=object_id,
        values=values,
        source_slots=source_slots,
        system_files=system_files,
        force=force,
    )
    project_root = Path(str(plan["project_root"]))
    source_root = Path(str(plan["source_root"]))
    module_root = Path(str(plan["root"]))
    clean_object_id = str(plan["object_id"])
    folder_name = str(plan["folder_name"])
    diagnostics = cast(list[dict[str, object]], plan["diagnostics"])
    blocked = bool(plan["blocked"])
    written = False
    write_failed = False

    if write and not blocked:
        try:
            _write_scaffold_files_anchored(
                project_root=project_root,
                source_root=source_root,
                family=template.family,
                object_id=clean_object_id,
                folder_name=folder_name,
                rendered_files=rendered_files,
                force=force,
            )
        except _AnchoredScaffoldUnavailable as error:
            diagnostics.append(
                _scaffold_write_diagnostic(
                    template,
                    module_root,
                    code="scaffold.unsupported_platform",
                    message=f"Module creation was blocked to protect your files: {error}.",
                )
            )
            write_failed = True
        except _ScaffoldRollbackIncomplete as error:
            diagnostic = _scaffold_write_diagnostic(
                template,
                module_root,
                code="scaffold.rollback_incomplete",
                message=("Module creation could not restore every original file. " f"Recovery data was preserved at {error.recovery_path}: {error}."),
            )
            diagnostic["recovery_path"] = str(error.recovery_path)
            diagnostics.append(diagnostic)
            write_failed = True
        except OSError as error:
            diagnostics.append(
                _scaffold_write_diagnostic(
                    template,
                    module_root,
                    code="scaffold.concurrent_change",
                    message=f"Module source changed before the scaffold could be written safely: {error}.",
                )
            )
            write_failed = True
        else:
            written = True
        blocked = any(item.get("severity") == "error" for item in diagnostics)

    plan.pop("project_root")
    plan["blocked"] = blocked
    plan["written"] = written
    plan["files"] = [
        _file_view(
            project_root,
            item,
            force=force,
            unsafe=bool(path_diagnostics) or write_failed,
        )
        for item in rendered_files
    ]
    return plan


def get_templates_api_table() -> TemplatesApiTable:
    """Return the API-standard table for SDK authoring-template helpers.

    Returns:
        JSON-safe table derived from `paradev.sdk.templates.__all__`, with
        copied rows and indexes for template schemas, models, registry helpers,
        scaffold planning, and this reference-table helper.
    """

    return cast(
        TemplatesApiTable,
        api_standard_table(TEMPLATES_API_TABLE_SCHEMA, _templates_api_rows()),
    )


def get_templates_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> TemplatesApiTable | TemplatesApiRow | list[str]:
    """Return the full templates API table, one row, or one index bucket.

    Args:
        symbol: Optional public symbol to select from the table rows.
        index_name: Optional index name, such as `module_index`,
            `feature_index`, or `kind_index`.
        key: Optional key inside the selected index.

    Returns:
        A detached table copy when no selector is passed, a detached row copy
        when `symbol` is passed, or a copied list of symbols for an index
        bucket when `index_name` and `key` are passed.

    Raises:
        ValueError: If selectors are ambiguous, incomplete, or name an
            unsupported index.
        KeyError: If the requested symbol or index key is not present.
    """

    return cast(
        TemplatesApiTable | TemplatesApiRow | list[str],
        api_table_selection(
            get_templates_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_TEMPLATES_API_INDEX_NAMES,
        ),
    )


def render_templates_api_reference_markdown() -> str:
    """Render the SDK authoring-template helper table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/templates-api-reference.md`. The content is generated
        from `get_templates_api_table()` so template schema, model, registry,
        scaffold, CLI command, and manual-page audits stay aligned.
    """

    table = get_templates_api_table()
    return api_standard_reference_markdown(
        title="Authoring Templates API Reference",
        source="paradev.sdk.templates.get_templates_api_table()",
        regenerate_when="Regenerate this file whenever SDK authoring-template helpers change:",
        command="rtk uv run paradev templates-api --markdown > docs/user-manual/templates-api-reference.md",
        table=table,
        module_label="Template",
        markdown_value=True,
    )


def _templates_api_rows() -> list[TemplatesApiRow]:
    rows: list[TemplatesApiRow] = []
    for symbol in __all__:
        value = globals()[symbol]
        feature = _templates_api_feature(symbol)
        rows.append(
            {
                "symbol": symbol,
                "kind": _templates_api_kind(symbol, value),
                "layer": "sdk",
                "module": "sdk.templates",
                "feature": feature,
                "import_path": f"paradev.sdk.templates.{symbol}",
                "returns": _templates_api_returns(symbol, value),
                "value": _templates_api_value(symbol, value),
                "registry_seam": _templates_api_registry_seam(feature),
                "surface": "sdk",
                "doc_page": _TEMPLATES_API_REFERENCE_PAGE,
                "test_anchor": _TEMPLATES_API_TEST_ANCHOR,
            }
        )
    return rows


def _templates_api_feature(symbol: str) -> str:
    if symbol in {
        "TEMPLATES_SCHEMA",
        "MODULE_SCAFFOLD_SCHEMA",
        "COLLECTION_SCAFFOLD_SCHEMA",
    }:
        return "schemas"
    if symbol == "ProjectTemplateSpecError":
        return "errors"
    if symbol in {"TemplateArg", "TemplateFile", "ModuleTemplate"}:
        return "models"
    if symbol in {
        "builtin_module_templates",
        "project_module_templates",
        "template_index",
    }:
        return "registry"
    if symbol in {"module_scaffold_plan", "collection_scaffold_plan"}:
        return "scaffold"
    if symbol in {
        "TEMPLATES_API_TABLE_SCHEMA",
        "TemplatesApiRow",
        "TemplatesApiTable",
        "get_templates_api_selection",
        "get_templates_api_table",
        "render_templates_api_reference_markdown",
    }:
        return "templates-api"
    return "authoring"


def _templates_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_typeddict(value):
        return "TypedDict"
    if is_dataclass(value):
        return "dataclass"
    if inspect.isfunction(value):
        return "function"
    if inspect.isclass(value) and issubclass(value, Exception):
        return "exception"
    return type(value).__name__


def _templates_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if is_typeddict(value):
        return "TypedDict schema"
    if is_dataclass(value):
        return f"{symbol} dataclass"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, strip_string_quotes=True)
    if inspect.isclass(value) and issubclass(value, Exception):
        return f"{symbol} exception"
    return type(value).__name__


def _templates_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    return ""


def _templates_api_registry_seam(feature: str) -> str:
    if feature == "schemas":
        return "authoring template payload schemas"
    if feature == "errors":
        return "authoring template validation"
    if feature == "models":
        return "authoring template model registry"
    if feature == "registry":
        return "authoring template registry"
    if feature == "scaffold":
        return "resource scaffold planner"
    if feature == "templates-api":
        return "authoring templates API table"
    return "SDK authoring templates"


def _template_args(value: object, key: str, path: Path) -> tuple[TemplateArg, ...]:
    if value is None:
        return ()
    if not isinstance(value, dict):
        raise ProjectTemplateSpecError(f"{path} key {key}.args must be a mapping.")
    args: list[TemplateArg] = []
    for name, raw_arg in value.items():
        arg_key = f"{key}.args.{name}"
        clean_name = _require_template_field(name, arg_key, path)
        if raw_arg is None:
            args.append(TemplateArg(clean_name))
            continue
        if not isinstance(raw_arg, dict):
            raise ProjectTemplateSpecError(f"{path} key {arg_key!r} must be a mapping.")
        required = raw_arg.get("required", False)
        if not isinstance(required, bool):
            raise ProjectTemplateSpecError(f"{path} key {arg_key}.required must be a boolean.")
        advanced = raw_arg.get("advanced")
        if advanced is not None and not isinstance(advanced, bool):
            raise ProjectTemplateSpecError(f"{path} key {arg_key}.advanced must be a boolean.")
        default = raw_arg.get("default", "")
        if default is None:
            default = ""
        if not isinstance(default, (str, int, float, bool)):
            raise ProjectTemplateSpecError(f"{path} key {arg_key}.default must be a scalar value.")
        arg_type = _template_arg_type(raw_arg.get("type"), arg_key, path)
        label = _optional_string(raw_arg.get("label"), "", f"{arg_key}.label", path)
        description = _optional_string(raw_arg.get("description"), "", f"{arg_key}.description", path)
        choices = _template_arg_choices(raw_arg.get("choices"), arg_key, path)
        reference = _template_arg_reference(raw_arg.get("reference"), arg_key, path)
        args.append(
            TemplateArg(
                clean_name,
                required=required,
                default=str(default),
                type=arg_type,
                label=label,
                description=description,
                choices=choices,
                reference=reference,
                advanced=advanced,
            )
        )
    return tuple(args)


def _template_arg_type(value: object, key: str, path: Path) -> str:
    if value is None:
        return "string"
    if not isinstance(value, str) or not value.strip():
        raise ProjectTemplateSpecError(f"{path} key {key}.type must be a non-empty string.")
    text = value.strip()
    if text not in _ARG_TYPES:
        allowed = ", ".join(sorted(_ARG_TYPES))
        raise ProjectTemplateSpecError(f"{path} key {key}.type must be one of: {allowed}.")
    return text


def _template_arg_choices(value: object, key: str, path: Path) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise ProjectTemplateSpecError(f"{path} key {key}.choices must be a list of scalar values.")
    choices: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, (str, int, float, bool)):
            raise ProjectTemplateSpecError(f"{path} key {key}.choices[{index}] must be a scalar value.")
        choices.append(str(item))
    return tuple(choices)


def _template_arg_reference(
    value: object,
    key: str,
    path: Path,
) -> TemplateArgReference | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ProjectTemplateSpecError(f"{path} key {key}.reference must be a mapping.")
    unknown = sorted(set(value) - {"family", "kind"})
    if unknown:
        names = ", ".join(unknown)
        raise ProjectTemplateSpecError(f"{path} key {key}.reference has unknown fields: {names}.")
    kind = value.get("kind")
    if kind not in {"module", "collection"}:
        raise ProjectTemplateSpecError(f"{path} key {key}.reference.kind must be 'module' or 'collection'.")
    family = value.get("family")
    if not isinstance(family, str) or not family.strip():
        raise ProjectTemplateSpecError(f"{path} key {key}.reference.family must be a non-empty string.")
    return TemplateArgReference(kind=kind, family=family.strip())


def _template_files(value: object, key: str, path: Path) -> tuple[TemplateFile, ...]:
    if not isinstance(value, dict) or not value:
        raise ProjectTemplateSpecError(f"{path} key {key}.files must be a non-empty mapping.")
    files: list[TemplateFile] = []
    ordered_files = sorted(
        value.items(),
        key=lambda item: (
            str(item[0]).strip() != "meta.yaml",
            str(item[0]).casefold(),
        ),
    )
    for raw_path, raw_content in ordered_files:
        file_key = f"{key}.files.{raw_path}"
        clean_path = _safe_file_path(raw_path, file_key, path)
        if not isinstance(raw_content, str):
            raise ProjectTemplateSpecError(f"{path} key {file_key!r} must be a string.")
        files.append(TemplateFile(clean_path, raw_content))
    return tuple(files)


def _template_system_files(
    value: object,
    key: str,
    path: Path,
) -> tuple[TemplateFile, ...]:
    """Parse trusted hidden metadata declared by a project extension template."""

    if value is None:
        return ()
    if not isinstance(value, dict) or not value:
        raise ProjectTemplateSpecError(f"{path} key {key}.system_files must be a non-empty mapping.")
    files: list[TemplateFile] = []
    for raw_path, raw_content in sorted(
        value.items(),
        key=lambda item: str(item[0]).casefold(),
    ):
        file_key = f"{key}.system_files.{raw_path}"
        clean_path = _safe_system_template_file_path(raw_path, file_key, path)
        if not isinstance(raw_content, str):
            raise ProjectTemplateSpecError(f"{path} key {file_key!r} must be a string.")
        files.append(TemplateFile(clean_path, raw_content))
    return tuple(files)


def _safe_system_template_file_path(
    value: object,
    key: str,
    path: Path,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be a non-empty relative file path.")
    if "\\" in value:
        raise ProjectTemplateSpecError(f"{path} key {key!r} must stay under .paradev/.")
    pure_path = PurePosixPath(value.strip())
    if pure_path.is_absolute() or len(pure_path.parts) < 2 or ".." in pure_path.parts or _portable_name_key(pure_path.parts[0]) != ".paradev":
        raise ProjectTemplateSpecError(f"{path} key {key!r} must stay under .paradev/.")
    return str(pure_path)


def _safe_file_path(value: object, key: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be a non-empty relative file path.")
    if "\\" in value:
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be relative and stay inside module root.")
    pure_path = PurePosixPath(value.strip())
    if pure_path.is_absolute() or pure_path == PurePosixPath(".") or ".." in pure_path.parts:
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be relative and stay inside module root.")
    if _portable_name_key(pure_path.parts[0]) == ".paradev":
        raise ProjectTemplateSpecError(f"{path} key {key!r} cannot write reserved module metadata under .paradev/.")
    return str(pure_path)


def _require_template_id(value: object, key: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be a non-empty template id.")
    text = value.strip()
    if any(char.isspace() for char in text):
        raise ProjectTemplateSpecError(f"{path} key {key!r} must not contain whitespace.")
    return text


def _require_template_field(value: object, key: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be a non-empty argument name.")
    text = value.strip()
    if not text.isidentifier():
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be a valid Python-style placeholder name.")
    return text


def _require_path_token(value: object, key: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be a non-empty path token.")
    text = value.strip()
    if text in {".", ".."} or "/" in text or "\\" in text or any(char.isspace() for char in text):
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be one path segment.")
    return text


def _optional_string(value: object, default: str, key: str, path: Path) -> str:
    if value is None:
        return default
    if not isinstance(value, str) or not value.strip():
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be a non-empty string.")
    return value.strip()


def _template_kind(
    value: object,
    key: str,
    path: Path,
) -> Literal["module", "collection"]:
    """Return the explicit authoring target kind for one template."""

    if value is None:
        return "module"
    if value not in {"module", "collection"}:
        raise ProjectTemplateSpecError(f"{path} key {key!r} must be one of: collection, module.")
    return cast(Literal["module", "collection"], value)


def _render_values(
    template: ModuleTemplate,
    object_id: str,
    values: Mapping[str, object] | None,
    diagnostics: list[dict[str, object]],
) -> dict[str, str]:
    supplied = {str(key): _scalar_text(value) for key, value in (values or {}).items()}
    render_values: dict[str, str] = {
        "object_id": object_id,
        "family": template.family,
        "family_tag": _family_tag(template.family, object_id),
        "module_id": f"{template.family}/{object_id}",
        "title": _title_from_id(object_id),
        "description": "",
        "category": "country",
        "language": "en",
    }
    arg_names: set[str] = set()
    for arg in template.args:
        arg_names.add(arg.name)
        if arg.name in supplied:
            render_values[arg.name] = supplied[arg.name]
        elif arg.default:
            default_value = _render_arg_default(template, arg, render_values, diagnostics)
            if default_value is not None:
                render_values[arg.name] = default_value
        elif arg.required:
            diagnostics.append(_missing_value_diagnostic(template.template_id, arg.name))
        else:
            render_values[arg.name] = ""
        if arg.name in render_values:
            diagnostic = _template_arg_value_diagnostic(
                template.template_id,
                arg,
                render_values[arg.name],
            )
            if diagnostic is not None:
                diagnostics.append(diagnostic)
    for key, value in supplied.items():
        if key not in arg_names:
            render_values[key] = value
    return render_values


def _template_arg_value_diagnostic(
    template_id: str,
    arg: TemplateArg,
    value: str,
) -> dict[str, object] | None:
    """Return one blocking diagnostic for an invalid rendered argument."""

    text = value.strip()
    if arg.required and not text:
        return _missing_value_diagnostic(template_id, arg.name)
    if not text:
        return None
    if arg.choices and value not in arg.choices:
        choices = ", ".join(arg.choices)
        return _invalid_template_value_diagnostic(
            template_id,
            arg.name,
            "scaffold.invalid_choice",
            f"must be one of: {choices}",
        )
    if arg.type == "number":
        try:
            number = float(text)
        except ValueError:
            number = math.nan
        if not math.isfinite(number):
            return _invalid_template_value_diagnostic(
                template_id,
                arg.name,
                "scaffold.invalid_number",
                "must be a finite number",
            )
    if arg.type == "boolean" and text.casefold() not in {
        "0",
        "1",
        "false",
        "no",
        "true",
        "yes",
    }:
        return _invalid_template_value_diagnostic(
            template_id,
            arg.name,
            "scaffold.invalid_boolean",
            "must be true, false, yes, no, 1, or 0",
        )
    return None


def _invalid_template_value_diagnostic(
    template_id: str,
    field: str,
    code: str,
    requirement: str,
) -> dict[str, object]:
    """Return one contextual authoring-template value diagnostic."""

    diagnostic = _scaffold_error_diagnostic(
        template_id,
        code,
        f"Template {template_id} value '{field}' {requirement}.",
    )
    diagnostic["field"] = field
    return diagnostic


def _render_module_folder_name(
    template: ModuleTemplate,
    object_id: str,
    values: Mapping[str, str],
    diagnostics: list[dict[str, object]],
) -> str:
    """Render and validate one portable physical module directory name."""

    try:
        missing_fields = _missing_format_fields(template.directory, values)
    except ValueError as error:
        diagnostics.append(
            _scaffold_error_diagnostic(
                template.template_id,
                "scaffold.invalid_directory",
                f"Template directory format is invalid: {error}",
            )
        )
        return object_id
    for field in sorted(missing_fields):
        diagnostics.append(_missing_value_diagnostic(template.template_id, field))
    if missing_fields:
        return object_id
    try:
        directory_values = dict(values)
        title = directory_values.get("title")
        if isinstance(title, str):
            directory_values["title"] = portable_authoring_title(
                title,
                object_id=object_id,
            )
        rendered = template.directory.format(**directory_values)
        return _safe_module_folder_name(rendered, object_id=object_id)
    except (IndexError, KeyError, ProjectTemplateSpecError, ValueError) as error:
        diagnostics.append(
            _scaffold_error_diagnostic(
                template.template_id,
                "scaffold.invalid_directory",
                str(error),
            )
        )
        return object_id


def _safe_module_folder_name(value: str, *, object_id: str) -> str:
    """Return a normalized, portable module folder name for one logical id."""

    normalized = unicodedata.normalize("NFC", value)
    if not normalized or normalized != normalized.strip():
        raise ProjectTemplateSpecError("Rendered module directory must be a non-empty path segment without surrounding whitespace.")
    if normalized in {".", ".."} or "/" in normalized or "\\" in normalized:
        raise ProjectTemplateSpecError("Rendered module directory must be exactly one path segment.")
    if portability_error := windows_portable_component_error(normalized):
        raise ProjectTemplateSpecError(f"Rendered module directory is not portable to Windows because it {portability_error}: {normalized!r}.")
    if len(os.fsencode(normalized)) > 255:
        raise ProjectTemplateSpecError("Rendered module directory exceeds the portable 255-byte filename limit.")
    folder_object_id = _module_folder_object_id(normalized)
    if folder_object_id != object_id:
        raise ProjectTemplateSpecError(
            f"Rendered module directory must begin with the exact logical object id {object_id!r}, " "optionally followed by ' - title'."
        )
    return normalized


def _resolve_scaffold_module_folder_name(
    template: ModuleTemplate,
    *,
    source_root: Path,
    object_id: str,
    requested_folder_name: str,
    diagnostics: list[dict[str, object]],
    container: str = "modules",
    target_label: str = "Module",
) -> str:
    """Reuse one existing logical resource root and reject portable aliases."""

    family_root = source_root / container / template.family
    try:
        family_entry = family_root.lstat()
    except FileNotFoundError:
        return requested_folder_name
    except OSError as error:
        diagnostics.append(
            _scaffold_write_diagnostic(
                template,
                family_root,
                code="scaffold.path_unreadable",
                message=f"{target_label} family directory could not be inspected safely: {error}.",
            )
        )
        return requested_folder_name
    if stat.S_ISLNK(family_entry.st_mode) or not stat.S_ISDIR(family_entry.st_mode):
        return requested_folder_name

    logical_key = _portable_name_key(object_id)
    try:
        matches = sorted(
            (entry.name for entry in os.scandir(family_root) if _portable_name_key(_module_folder_object_id(entry.name)) == logical_key),
            key=_portable_name_key,
        )
    except OSError as error:
        diagnostics.append(
            _scaffold_write_diagnostic(
                template,
                family_root,
                code="scaffold.path_unreadable",
                message=f"Module family directory could not be inspected safely: {error}.",
            )
        )
        return requested_folder_name
    if not matches:
        return requested_folder_name
    if len(matches) > 1:
        diagnostics.append(
            _scaffold_write_diagnostic(
                template,
                family_root,
                code=("scaffold.module_alias_ambiguous" if target_label == "Module" else "scaffold.collection_alias_ambiguous"),
                message=(f"{target_label} {template.family}/{object_id} has multiple " f"physical folders: {', '.join(matches)}."),
            )
        )
        return requested_folder_name

    existing_name = matches[0]
    if _module_folder_object_id(existing_name) != object_id:
        diagnostics.append(
            _scaffold_write_diagnostic(
                template,
                family_root / existing_name,
                code=("scaffold.module_alias_collision" if target_label == "Module" else "scaffold.collection_alias_collision"),
                message=(f"{target_label} folder {existing_name!r} collides with " f"logical object id {object_id!r} by case or Unicode normalization."),
            )
        )
    try:
        _safe_module_folder_name(existing_name, object_id=object_id)
    except ProjectTemplateSpecError as error:
        diagnostics.append(
            _scaffold_write_diagnostic(
                template,
                family_root / existing_name,
                code="scaffold.invalid_existing_directory",
                message=str(error),
            )
        )
    return existing_name


def _module_folder_object_id(folder_name: str) -> str:
    """Return the logical id prefix from an optional ``ID - title`` folder."""

    return folder_name.split(" - ", 1)[0].strip()


def _portable_name_key(value: str) -> str:
    """Return a portable comparison key for one filesystem name."""

    return unicodedata.normalize("NFC", value).casefold()


def _render_arg_default(
    template: ModuleTemplate,
    arg: TemplateArg,
    values: Mapping[str, str],
    diagnostics: list[dict[str, object]],
) -> str | None:
    missing_fields = _missing_format_fields(arg.default, values)
    for field in sorted(missing_fields):
        diagnostics.append(_missing_value_diagnostic(template.template_id, field))
    if missing_fields:
        return None
    return arg.default.format(**values)


def _render_files(
    template: ModuleTemplate,
    module_root: Path,
    values: Mapping[str, str],
    diagnostics: list[dict[str, object]],
) -> list[dict[str, object]]:
    rendered: list[dict[str, object]] = []
    format_files = template.renderer is None
    try:
        files = _renderer_files(template, values)
    except ProjectTemplateSpecError as error:
        diagnostics.append(_scaffold_error_diagnostic(template.template_id, "scaffold.renderer_failed", str(error)))
        return []
    for file in files:
        missing_fields = _missing_format_fields(file.path, values) if format_files else set()
        if format_files:
            missing_fields |= _missing_format_fields(file.content, values)
        for field in sorted(missing_fields):
            diagnostics.append(_missing_value_diagnostic(template.template_id, field))
        if missing_fields:
            continue
        relative_path = file.path.format(**values) if format_files else file.path
        try:
            clean_path = _safe_rendered_path(relative_path, template.template_id)
        except ProjectTemplateSpecError as error:
            diagnostics.append(_scaffold_error_diagnostic(template.template_id, "scaffold.invalid_file", str(error)))
            continue
        rendered.append(
            {
                "relative_module_path": clean_path,
                "target": module_root / clean_path,
                "content": file.content.format(**values) if format_files else file.content,
            }
        )
    return rendered


def _renderer_files(template: ModuleTemplate, values: Mapping[str, str]) -> tuple[TemplateFile, ...]:
    if template.renderer is None:
        return template.files
    try:
        rendered = template.renderer(values)
    except Exception as error:
        raise ProjectTemplateSpecError(f"Template {template.template_id} renderer failed: {error}") from error
    if isinstance(rendered, (str, bytes)) or not isinstance(rendered, Sequence):
        raise ProjectTemplateSpecError(f"Template {template.template_id} renderer must return TemplateFile values.")
    files: list[TemplateFile] = []
    for index, file in enumerate(rendered):
        if not isinstance(file, TemplateFile):
            raise ProjectTemplateSpecError(f"Template {template.template_id} renderer result {index} must be a TemplateFile.")
        files.append(file)
    return tuple(files)


def _safe_rendered_path(value: str, template_id: str) -> str:
    pure_path = PurePosixPath(value)
    if pure_path.is_absolute() or pure_path == PurePosixPath(".") or ".." in pure_path.parts:
        raise ProjectTemplateSpecError(f"Template {template_id} rendered unsafe file path {value!r}.")
    for component in pure_path.parts:
        if portability_error := windows_portable_component_error(component):
            raise ProjectTemplateSpecError(
                f"Template {template_id} rendered file path {value!r}, whose component {component!r} "
                f"is not portable to Windows because it {portability_error}."
            )
    if _portable_name_key(pure_path.parts[0]) == ".paradev":
        raise ProjectTemplateSpecError(f"Template {template_id} cannot write reserved module metadata under .paradev/.")
    return str(pure_path)


def _render_system_files(
    template: ModuleTemplate,
    *,
    module_root: Path,
    files: Sequence[tuple[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Validate trusted SDK-owned module metadata for one scaffold.

    Project templates cannot write ``.paradev``. The Project SDK may attach
    small system-owned files to the same guarded transaction so fresh modules
    are immediately usable without exposing those files as template inputs.
    """

    rendered: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, row in enumerate(files):
        if not isinstance(row, tuple) or len(row) != 2 or not isinstance(row[0], str) or not isinstance(row[1], str):
            diagnostics.append(
                _scaffold_error_diagnostic(
                    template.template_id,
                    "scaffold.invalid_system_file",
                    f"System scaffold file {index} must be a path/content pair.",
                )
            )
            continue
        relative_path, content = row
        pure_path = PurePosixPath(relative_path)
        invalid = (
            pure_path.is_absolute()
            or pure_path == PurePosixPath(".")
            or len(pure_path.parts) < 2
            or ".." in pure_path.parts
            or _portable_name_key(pure_path.parts[0]) != ".paradev"
        )
        portability_error = next(
            (error for component in pure_path.parts if (error := windows_portable_component_error(component))),
            None,
        )
        clean_path = str(pure_path)
        if invalid or portability_error or clean_path in seen:
            detail = f"System scaffold file {index} has an unsafe, duplicate, " f"or non-portable path: {relative_path!r}."
            diagnostics.append(
                _scaffold_error_diagnostic(
                    template.template_id,
                    "scaffold.invalid_system_file",
                    detail,
                )
            )
            continue
        seen.add(clean_path)
        rendered.append(
            {
                "relative_module_path": clean_path,
                "target": module_root / clean_path,
                "content": content,
                "system": True,
            }
        )
    return rendered, diagnostics


def _render_template_system_files(
    template: ModuleTemplate,
    *,
    values: Mapping[str, str],
    diagnostics: list[dict[str, object]],
) -> tuple[tuple[str, str], ...]:
    rendered: list[tuple[str, str]] = []
    for file in template.system_files:
        missing_fields = _missing_format_fields(file.path, values)
        missing_fields |= _missing_format_fields(file.content, values)
        for field in sorted(missing_fields):
            diagnostics.append(_missing_value_diagnostic(template.template_id, field))
        if missing_fields:
            continue
        rendered.append(
            (
                file.path.format(**values),
                file.content.format(**values),
            )
        )
    return tuple(rendered)


def _scaffold_source_slot_diagnostics(
    template: ModuleTemplate,
    *,
    module_id: str,
    rendered_files: Sequence[Mapping[str, object]],
    source_slots: Sequence[object],
) -> list[dict[str, object]]:
    if not source_slots:
        return []
    from paradev.build.slots import match_slot_paths

    paths: list[str] = []
    for item in rendered_files:
        relative_path = item.get("relative_module_path")
        if isinstance(relative_path, str):
            paths.append(relative_path)
    try:
        result = match_slot_paths(tuple(paths), tuple(cast(Any, source_slots)), module_id=module_id)
    except (AttributeError, TypeError, ValueError) as error:
        return [_scaffold_error_diagnostic(template.template_id, "scaffold.invalid_source_slots", str(error))]
    return [diagnostic.to_dict() for diagnostic in result.diagnostics]


def _missing_format_fields(template: str, values: Mapping[str, str]) -> set[str]:
    return {field for field in _format_field_names(template) if field not in values}


def _format_field_names(
    template: str,
    *,
    strict: bool = True,
) -> set[str]:
    """Return root placeholder names from one safe format template."""

    fields: set[str] = set()
    try:
        parsed = Formatter().parse(template)
        rows = tuple(parsed)
    except ValueError:
        if strict:
            raise
        return fields
    for _, field_name, _, _ in rows:
        if not field_name:
            continue
        root_field = field_name.split(".", 1)[0].split("[", 1)[0]
        fields.add(root_field)
    return fields


def _scaffold_path_diagnostics(
    template: ModuleTemplate,
    *,
    project_root: Path,
    source_root: Path,
    rendered_files: list[dict[str, object]],
) -> list[dict[str, object]]:
    diagnostics: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    try:
        source_root.relative_to(project_root)
    except ValueError:
        return [
            _scaffold_write_diagnostic(
                template,
                source_root,
                code="scaffold.source_outside_project",
                message="Module creation requires a source root inside the project root.",
            )
        ]

    for item in rendered_files:
        target = item.get("target")
        if not isinstance(target, Path):
            continue
        try:
            relative = target.relative_to(project_root)
        except ValueError:
            diagnostic = _scaffold_write_diagnostic(
                template,
                target,
                code="scaffold.path_outside_project",
                message="Template output must stay inside the project root.",
            )
            key = (str(diagnostic["code"]), str(diagnostic["path"]))
            if key not in seen:
                diagnostics.append(diagnostic)
                seen.add(key)
            continue
        current = project_root
        for index, component in enumerate(relative.parts):
            current /= component
            try:
                entry = current.lstat()
            except FileNotFoundError:
                continue
            except OSError as error:
                diagnostic = _scaffold_write_diagnostic(
                    template,
                    current,
                    code="scaffold.path_unreadable",
                    message=f"Template output path could not be inspected safely: {error}.",
                )
            else:
                is_target = index == len(relative.parts) - 1
                if stat.S_ISLNK(entry.st_mode):
                    diagnostic = _scaffold_write_diagnostic(
                        template,
                        current,
                        code="scaffold.path_symlink",
                        message="Module creation cannot write through a symbolic link.",
                    )
                elif not is_target and not stat.S_ISDIR(entry.st_mode):
                    diagnostic = _scaffold_write_diagnostic(
                        template,
                        current,
                        code="scaffold.path_not_directory",
                        message="Template output path has a non-directory parent component.",
                    )
                elif is_target and not stat.S_ISREG(entry.st_mode):
                    diagnostic = _scaffold_write_diagnostic(
                        template,
                        current,
                        code="scaffold.path_not_file",
                        message="Template output target exists but is not a regular file.",
                    )
                else:
                    continue
            key = (str(diagnostic["code"]), str(diagnostic["path"]))
            if key not in seen:
                diagnostics.append(diagnostic)
                seen.add(key)
            break
    return diagnostics


def _write_scaffold_files_anchored(
    *,
    project_root: Path,
    source_root: Path,
    container: str = "modules",
    family: str,
    object_id: str,
    folder_name: str,
    rendered_files: list[dict[str, object]],
    force: bool,
) -> None:
    if _uses_win32_scaffold_authority():
        if container == "modules":
            _write_scaffold_files_win32(
                project_root=project_root,
                source_root=source_root,
                family=family,
                object_id=object_id,
                folder_name=folder_name,
                rendered_files=rendered_files,
                force=force,
            )
        else:
            _write_scaffold_files_win32(
                project_root=project_root,
                source_root=source_root,
                container=container,
                family=family,
                object_id=object_id,
                folder_name=folder_name,
                rendered_files=rendered_files,
                force=force,
            )
        return
    if not _ANCHORED_SCAFFOLD_SUPPORTED:
        raise _AnchoredScaffoldUnavailable("Safe descriptor-anchored scaffold writes are unavailable on this platform")
    try:
        source_parts = source_root.relative_to(project_root).parts
    except ValueError as error:
        raise OSError("Scaffold source root is outside the project root") from error

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    project_fd = os.open(project_root, directory_flags)
    source_fd: int | None = None
    container_fd: int | None = None
    family_fd: int | None = None
    module_fd: int | None = None
    metadata_fd: int | None = None
    transactions_fd: int | None = None
    transaction_fd: int | None = None
    transaction_identity: tuple[int, int] | None = None
    module_created = False
    module_identity: tuple[int, int] | None = None
    transaction_name = ""
    preserve_transaction = False
    installs: list[_ScaffoldInstall] = []
    created_directories: list[_ScaffoldCreatedDirectory] = []
    stage_fingerprints: dict[str, tuple[tuple[int, int], int, str]] = {}
    try:
        source_fd = _open_scaffold_directory_chain(project_fd, source_parts)
        container_fd = _open_or_create_scaffold_directory(source_fd, container)
        family_fd = _open_or_create_scaffold_directory(container_fd, family)
        metadata_fd = _open_or_create_scaffold_directory(source_fd, ".paradev")
        transactions_fd = _open_or_create_scaffold_directory(metadata_fd, "module-transactions")
        transaction_name = f"{family}-{object_id}-{uuid4().hex}.txn"
        os.mkdir(transaction_name, 0o700, dir_fd=transactions_fd)
        transaction_fd = os.open(transaction_name, directory_flags, dir_fd=transactions_fd)
        transaction_metadata = os.fstat(transaction_fd)
        transaction_identity = (
            transaction_metadata.st_dev,
            transaction_metadata.st_ino,
        )
        _require_no_scaffold_module_alias(
            family_fd,
            object_id=object_id,
            folder_name=folder_name,
        )
        try:
            os.mkdir(folder_name, dir_fd=family_fd)
            module_created = True
        except FileExistsError:
            pass
        module_fd = os.open(folder_name, directory_flags, dir_fd=family_fd)
        module_metadata = os.fstat(module_fd)
        module_identity = (module_metadata.st_dev, module_metadata.st_ino)

        staged_paths: list[tuple[str, str]] = []
        seen_paths: set[str] = set()
        for index, item in enumerate(rendered_files):
            relative_path = item.get("relative_module_path")
            content = item.get("content")
            if not isinstance(relative_path, str) or not isinstance(content, str):
                raise TypeError("Rendered scaffold files require string paths and content")
            if relative_path in seen_paths:
                raise OSError(f"Scaffold rendered duplicate target path: {relative_path}")
            seen_paths.add(relative_path)
            stage_name = f"{index:04d}.stage"
            _write_scaffold_file_anchored(transaction_fd, stage_name, content, force=False)
            stage_fingerprints[stage_name] = _scaffold_regular_file_fingerprint(
                transaction_fd,
                stage_name,
            )
            staged_paths.append((relative_path, stage_name))

        _require_scaffold_target_identity(
            project_fd,
            source_parts,
            family,
            folder_name,
            container=container,
            expected_family_fd=family_fd,
            expected_module_fd=module_fd,
        )
        _require_no_scaffold_module_alias(
            family_fd,
            object_id=object_id,
            folder_name=folder_name,
        )

        for index, (relative_path, stage_name) in enumerate(staged_paths):
            parts = PurePosixPath(relative_path).parts
            parent_fd = _open_scaffold_directory_chain_tracked(
                module_fd,
                parts[:-1],
                created_directories=created_directories,
            )
            installs.append(
                _ScaffoldInstall(
                    parent_fd=parent_fd,
                    target_name=parts[-1],
                    stage_name=stage_name,
                    backup_name=f"{index:04d}.backup",
                    target_existed=False,
                )
            )

        for install in installs:
            (
                install.installed_identity,
                install.installed_size,
                install.installed_digest,
            ) = stage_fingerprints[install.stage_name]
            try:
                (
                    install.backup_identity,
                    install.backup_size,
                    install.backup_digest,
                ) = _scaffold_regular_file_fingerprint(
                    install.parent_fd,
                    install.target_name,
                )
            except FileNotFoundError:
                continue
            if not force:
                raise FileExistsError(f"Scaffold target appeared before installation: {install.target_name}")
            install.target_existed = True

        for install in installs:
            if install.target_existed:
                backup_fd = _quarantine_scaffold_entry(
                    parent_fd=install.parent_fd,
                    name=install.target_name,
                    transaction_fd=transaction_fd,
                    quarantine_name=install.backup_name,
                )
                install.backup_moved = True
                try:
                    backup = _scaffold_regular_file_fingerprint(
                        backup_fd,
                        _SCAFFOLD_QUARANTINE_ENTRY,
                    )
                    if backup != (
                        install.backup_identity,
                        install.backup_size,
                        install.backup_digest,
                    ):
                        restored = _restore_scaffold_quarantined_file(
                            quarantine_fd=backup_fd,
                            parent_fd=install.parent_fd,
                            target_name=install.target_name,
                        )
                        disposition = "restored without overwrite" if restored else "preserved for recovery"
                        raise OSError(f"Scaffold original changed while it was quarantined " f"({disposition}): " f"{install.target_name}")
                finally:
                    _close_scaffold_descriptor(backup_fd)
            os.link(
                install.stage_name,
                install.target_name,
                src_dir_fd=transaction_fd,
                dst_dir_fd=install.parent_fd,
                follow_symlinks=False,
            )
            install.installed = True
            _require_scaffold_install_identity(install)

        _require_scaffold_target_identity(
            project_fd,
            source_parts,
            family,
            folder_name,
            container=container,
            expected_family_fd=family_fd,
            expected_module_fd=module_fd,
        )
        _require_no_scaffold_module_alias(
            family_fd,
            object_id=object_id,
            folder_name=folder_name,
        )
        for created_directory in created_directories:
            _require_scaffold_directory_identity(created_directory)
        for install in installs:
            _require_scaffold_install_identity(install)
        backup_cleanup_errors = _discard_scaffold_backups(installs, transaction_fd)
        if backup_cleanup_errors:
            preserve_transaction = True
            details = "; ".join(str(cleanup_error) for cleanup_error in backup_cleanup_errors)
            logger.warning(
                "Committed scaffold retained original-file recovery data: %s",
                details,
            )
    except BaseException as error:
        rollback_errors = _rollback_scaffold_installs(installs, transaction_fd)
        if module_created and family_fd is not None:
            if isinstance(module_fd, int):
                _close_scaffold_descriptor(module_fd)
                module_fd = None
            if created_directories:
                rollback_errors.extend(
                    _rollback_scaffold_directories(
                        created_directories,
                        transaction_fd,
                    )
                )
            if module_identity is None:
                rollback_errors.append(OSError(f"Scaffold rollback lost the created module identity: {folder_name}"))
            else:
                rollback_errors.extend(
                    _rollback_scaffold_directories(
                        [
                            _ScaffoldCreatedDirectory(
                                parent_fd=family_fd,
                                name=folder_name,
                                identity=module_identity,
                                quarantine_name="module.rollback",
                            )
                        ],
                        transaction_fd,
                    )
                )
        else:
            rollback_errors.extend(
                _rollback_scaffold_directories(
                    created_directories,
                    transaction_fd,
                )
            )
        if rollback_errors:
            details = "; ".join(str(rollback_error) for rollback_error in rollback_errors)
            if transaction_name:
                preserve_transaction = True
                recovery_path = source_root / ".paradev" / "module-transactions" / transaction_name
                raise _ScaffoldRollbackIncomplete(details, recovery_path) from error
            raise OSError(f"Scaffold write failed and rollback was incomplete: {details}") from error
        raise
    finally:
        for install in installs:
            _close_scaffold_descriptor(install.parent_fd)
        for created_directory in created_directories:
            _close_scaffold_descriptor(created_directory.parent_fd)
        if transaction_fd is not None:
            if not preserve_transaction:
                cleanup_errors = _cleanup_scaffold_transaction(
                    transaction_fd,
                    stage_fingerprints,
                )
                if cleanup_errors:
                    preserve_transaction = True
                    logger.warning(
                        "Scaffold transaction cleanup preserved unexpected data: %s",
                        "; ".join(str(cleanup_error) for cleanup_error in cleanup_errors),
                    )
            _close_scaffold_descriptor(transaction_fd)
            transaction_fd = None
        if transaction_name and transactions_fd is not None:
            transaction_path = source_root / ".paradev" / "module-transactions" / transaction_name
            if preserve_transaction:
                logger.error(
                    "Scaffold transaction preserved for recovery at %s",
                    transaction_path,
                )
            else:
                try:
                    if transaction_identity is None:
                        raise OSError("Scaffold transaction lost its directory identity")
                    _remove_scaffold_transaction_directory(
                        transactions_fd,
                        transaction_name,
                        transaction_identity,
                    )
                except FileNotFoundError:
                    pass
                except Exception:
                    logger.warning(
                        "Scaffold transaction cleanup remains pending at %s",
                        transaction_path,
                        exc_info=True,
                    )
        for descriptor in (
            transactions_fd,
            metadata_fd,
            module_fd,
            family_fd,
            container_fd,
            source_fd,
            project_fd,
        ):
            if isinstance(descriptor, int):
                _close_scaffold_descriptor(descriptor)


def _write_scaffold_batch_anchored(
    *,
    project_root: Path,
    source_root: Path,
    scaffolds: Sequence[tuple[str, str, str, list[dict[str, object]]]],
    validate: Callable[[], None] | None = None,
    transaction_id: str | None = None,
) -> None:
    """Create several new modules as one staged, reversible transaction."""

    if not scaffolds:
        return
    if _uses_win32_scaffold_authority():
        _write_scaffold_batch_win32(
            project_root=project_root,
            source_root=source_root,
            scaffolds=scaffolds,
            validate=validate,
        )
        return
    if not _ANCHORED_SCAFFOLD_SUPPORTED:
        raise _AnchoredScaffoldUnavailable("Safe descriptor-anchored scaffold writes are unavailable on this platform")
    try:
        source_parts = source_root.relative_to(project_root).parts
    except ValueError as error:
        raise OSError("Scaffold source root is outside the project root") from error

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    project_fd = os.open(project_root, directory_flags)
    source_fd: int | None = None
    modules_fd: int | None = None
    metadata_fd: int | None = None
    transactions_fd: int | None = None
    transaction_fd: int | None = None
    transaction_identity: tuple[int, int] | None = None
    transaction_name = ""
    preserve_transaction = False
    installs: list[_ScaffoldInstall] = []
    stage_fingerprints: dict[str, tuple[tuple[int, int], int, str]] = {}
    states = [
        _ScaffoldBatchModule(
            family=family,
            object_id=object_id,
            folder_name=folder_name,
            rendered_files=rendered_files,
            created_directories=[],
            quarantine_name=f"module-{index:06d}.rollback",
        )
        for index, (family, object_id, folder_name, rendered_files) in enumerate(scaffolds)
    ]
    try:
        source_fd = _open_scaffold_directory_chain(project_fd, source_parts)
        modules_fd = _open_or_create_scaffold_directory(source_fd, "modules")
        metadata_fd = _open_or_create_scaffold_directory(source_fd, ".paradev")
        transactions_fd = _open_or_create_scaffold_directory(metadata_fd, "module-transactions")
        transaction_token = transaction_id or uuid4().hex
        if len(transaction_token) != 32 or any(character not in "0123456789abcdef" for character in transaction_token):
            raise ValueError("Scaffold batch transaction_id must be 32 lowercase hexadecimal characters")
        transaction_name = f"batch-{transaction_token}.txn"
        os.mkdir(transaction_name, 0o700, dir_fd=transactions_fd)
        transaction_fd = os.open(transaction_name, directory_flags, dir_fd=transactions_fd)
        transaction_metadata = os.fstat(transaction_fd)
        transaction_identity = (
            transaction_metadata.st_dev,
            transaction_metadata.st_ino,
        )

        staged_paths: list[tuple[_ScaffoldBatchModule, str, str]] = []
        stage_index = 0
        for state in states:
            seen_paths: set[str] = set()
            for item in state.rendered_files:
                relative_path = item.get("relative_module_path")
                content = item.get("content")
                if not isinstance(relative_path, str) or not isinstance(content, str):
                    raise TypeError("Rendered scaffold files require string paths and content")
                if relative_path in seen_paths:
                    raise OSError(f"Scaffold rendered duplicate target path: {relative_path}")
                seen_paths.add(relative_path)
                stage_name = f"{stage_index:06d}.stage"
                stage_index += 1
                _write_scaffold_file_anchored(transaction_fd, stage_name, content, force=False)
                stage_fingerprints[stage_name] = _scaffold_regular_file_fingerprint(
                    transaction_fd,
                    stage_name,
                )
                staged_paths.append((state, relative_path, stage_name))

        for state in states:
            state.family_fd = _open_or_create_scaffold_directory(modules_fd, state.family)
            _require_no_scaffold_module_alias(
                state.family_fd,
                object_id=state.object_id,
                folder_name=state.folder_name,
            )
            os.mkdir(state.folder_name, dir_fd=state.family_fd)
            state.module_created = True
            state.module_fd = os.open(state.folder_name, directory_flags, dir_fd=state.family_fd)
            module_metadata = os.fstat(state.module_fd)
            state.module_identity = (module_metadata.st_dev, module_metadata.st_ino)
            _require_scaffold_target_identity(
                project_fd,
                source_parts,
                state.family,
                state.folder_name,
                expected_family_fd=state.family_fd,
                expected_module_fd=state.module_fd,
            )
            _require_no_scaffold_module_alias(
                state.family_fd,
                object_id=state.object_id,
                folder_name=state.folder_name,
            )

        for index, (state, relative_path, stage_name) in enumerate(staged_paths):
            if state.module_fd is None or state.created_directories is None:
                raise OSError("Scaffold batch lost its anchored module directory")
            parts = PurePosixPath(relative_path).parts
            parent_fd = _open_scaffold_directory_chain_tracked(
                state.module_fd,
                parts[:-1],
                created_directories=state.created_directories,
            )
            installs.append(
                _ScaffoldInstall(
                    parent_fd=parent_fd,
                    target_name=parts[-1],
                    stage_name=stage_name,
                    backup_name=f"{index:06d}.backup",
                    target_existed=False,
                )
            )

        for install in installs:
            try:
                os.stat(install.target_name, dir_fd=install.parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise FileExistsError(f"Scaffold target appeared before installation: {install.target_name}")

        for install in installs:
            (
                install.installed_identity,
                install.installed_size,
                install.installed_digest,
            ) = stage_fingerprints[install.stage_name]
            os.link(
                install.stage_name,
                install.target_name,
                src_dir_fd=transaction_fd,
                dst_dir_fd=install.parent_fd,
                follow_symlinks=False,
            )
            install.installed = True
            _require_scaffold_install_identity(install)

        for state in states:
            if state.family_fd is None or state.module_fd is None:
                raise OSError("Scaffold batch lost its anchored target identity")
            _require_scaffold_target_identity(
                project_fd,
                source_parts,
                state.family,
                state.folder_name,
                expected_family_fd=state.family_fd,
                expected_module_fd=state.module_fd,
            )
            _require_no_scaffold_module_alias(
                state.family_fd,
                object_id=state.object_id,
                folder_name=state.folder_name,
            )
            for created_directory in state.created_directories or ():
                _require_scaffold_directory_identity(created_directory)
        for install in installs:
            _require_scaffold_install_identity(install)
        if validate is not None:
            validate()
    except BaseException as error:
        rollback_errors = _rollback_scaffold_batch_installs(installs, transaction_fd)
        for state in reversed(states):
            if state.module_created and state.family_fd is not None:
                if state.created_directories:
                    rollback_errors.extend(
                        _rollback_scaffold_directories(
                            state.created_directories,
                            transaction_fd,
                        )
                    )
                if state.module_fd is not None:
                    _close_scaffold_descriptor(state.module_fd)
                    state.module_fd = None
                if state.module_identity is None:
                    rollback_errors.append(OSError(f"Scaffold rollback lost the created module identity: {state.folder_name}"))
                else:
                    rollback_errors.extend(
                        _rollback_scaffold_directories(
                            [
                                _ScaffoldCreatedDirectory(
                                    parent_fd=state.family_fd,
                                    name=state.folder_name,
                                    identity=state.module_identity,
                                    quarantine_name=state.quarantine_name,
                                )
                            ],
                            transaction_fd,
                        )
                    )
            elif state.created_directories:
                rollback_errors.extend(
                    _rollback_scaffold_directories(
                        state.created_directories,
                        transaction_fd,
                    )
                )
        if rollback_errors:
            details = "; ".join(str(rollback_error) for rollback_error in rollback_errors)
            if transaction_name:
                preserve_transaction = True
                recovery_path = source_root / ".paradev" / "module-transactions" / transaction_name
                raise _ScaffoldRollbackIncomplete(details, recovery_path) from error
            raise OSError(f"Scaffold batch failed and rollback was incomplete: {details}") from error
        raise
    finally:
        for install in installs:
            _close_scaffold_descriptor(install.parent_fd)
        for state in states:
            for created_directory in state.created_directories or ():
                _close_scaffold_descriptor(created_directory.parent_fd)
        if transaction_fd is not None:
            if not preserve_transaction:
                cleanup_errors = _cleanup_scaffold_transaction(
                    transaction_fd,
                    stage_fingerprints,
                )
                if cleanup_errors:
                    preserve_transaction = True
                    logger.warning(
                        "Scaffold batch transaction cleanup preserved unexpected data: %s",
                        "; ".join(str(cleanup_error) for cleanup_error in cleanup_errors),
                    )
            _close_scaffold_descriptor(transaction_fd)
            transaction_fd = None
        if transaction_name and transactions_fd is not None:
            transaction_path = source_root / ".paradev" / "module-transactions" / transaction_name
            if preserve_transaction:
                logger.error(
                    "Scaffold batch transaction preserved for recovery at %s",
                    transaction_path,
                )
            else:
                try:
                    if transaction_identity is None:
                        raise OSError("Scaffold batch transaction lost its directory identity")
                    _remove_scaffold_transaction_directory(
                        transactions_fd,
                        transaction_name,
                        transaction_identity,
                    )
                except FileNotFoundError:
                    pass
                except Exception:
                    logger.warning(
                        "Scaffold batch transaction cleanup remains pending at %s",
                        transaction_path,
                        exc_info=True,
                    )
        for state in states:
            for descriptor in (state.module_fd, state.family_fd):
                if isinstance(descriptor, int):
                    _close_scaffold_descriptor(descriptor)
        for descriptor in (
            transactions_fd,
            metadata_fd,
            modules_fd,
            source_fd,
            project_fd,
        ):
            if isinstance(descriptor, int):
                _close_scaffold_descriptor(descriptor)


def _recover_scaffold_batch_anchored(
    *,
    project_root: Path,
    source_root: Path,
    family: str,
    folder_name: str,
    files: Sequence[tuple[str, int, str]],
    transaction_id: str,
    keep_module: bool,
) -> None:
    """Reconcile one interrupted create-only scaffold from exact ownership data."""

    if _uses_win32_scaffold_authority() or not _ANCHORED_SCAFFOLD_SUPPORTED:
        raise _AnchoredScaffoldUnavailable("Safe diagram-module recovery is unavailable on this platform")
    if len(transaction_id) != 32 or any(character not in "0123456789abcdef" for character in transaction_id):
        raise ValueError("Scaffold recovery transaction_id must be 32 lowercase hexadecimal characters")
    try:
        source_parts = source_root.relative_to(project_root).parts
    except ValueError as error:
        raise OSError("Scaffold recovery source root is outside the project root") from error

    expected_files: dict[str, tuple[int, str]] = {}
    expected_directories: set[str] = set()
    for relative_path, size, digest in files:
        pure_path = PurePosixPath(relative_path)
        if (
            not relative_path
            or pure_path.is_absolute()
            or str(pure_path) != relative_path
            or any(part in {"", ".", ".."} for part in pure_path.parts)
            or relative_path in expected_files
        ):
            raise ValueError(f"Scaffold recovery contains an unsafe or duplicate file path: {relative_path!r}")
        expected_files[relative_path] = (size, digest)
        for index in range(1, len(pure_path.parts)):
            expected_directories.add(PurePosixPath(*pure_path.parts[:index]).as_posix())

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    project_fd = os.open(project_root, directory_flags)
    source_fd: int | None = None
    modules_fd: int | None = None
    family_fd: int | None = None
    module_fd: int | None = None
    try:
        source_fd = _open_existing_scaffold_directory_chain(project_fd, source_parts)
        module_tree: _ScaffoldRecoveryTree | None = None
        try:
            modules_fd = os.open("modules", directory_flags, dir_fd=source_fd)
            family_fd = os.open(family, directory_flags, dir_fd=modules_fd)
            module_fd = os.open(folder_name, directory_flags, dir_fd=family_fd)
        except FileNotFoundError:
            for descriptor in (module_fd, family_fd, modules_fd):
                if isinstance(descriptor, int):
                    _close_scaffold_descriptor(descriptor)
            module_fd = None
            family_fd = None
            modules_fd = None
        else:
            module_tree = _inspect_scaffold_recovery_tree(
                module_fd,
                prefix="",
                expected_files=expected_files,
                expected_directories=expected_directories,
            )
        actual_files = set() if module_tree is None else _scaffold_recovery_tree_files(module_tree)
        complete = module_tree is not None and actual_files == set(expected_files)
        if keep_module and not complete:
            raise OSError("Committed diagram source references a missing or partial child module")
        if not keep_module and module_tree is not None:
            if family_fd is None:
                raise OSError("Scaffold recovery lost its family directory authority")
            _remove_scaffold_recovery_tree(
                family_fd,
                folder_name,
                module_tree,
            )
            _close_scaffold_descriptor(module_fd)
            module_fd = None

        _remove_scaffold_recovery_transaction(
            source_fd,
            transaction_id=transaction_id,
            files=files,
        )
    finally:
        for descriptor in (module_fd, family_fd, modules_fd, source_fd, project_fd):
            if isinstance(descriptor, int):
                _close_scaffold_descriptor(descriptor)


def _inspect_scaffold_recovery_tree(
    directory_fd: int,
    *,
    prefix: str,
    expected_files: Mapping[str, tuple[int, str]],
    expected_directories: set[str],
) -> _ScaffoldRecoveryTree:
    metadata = os.fstat(directory_fd)
    identity = (metadata.st_dev, metadata.st_ino)
    files: dict[str, tuple[tuple[int, int], int, str]] = {}
    directories: dict[str, _ScaffoldRecoveryTree] = {}
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    for name in os.listdir(directory_fd):
        relative_path = f"{prefix}/{name}" if prefix else name
        entry = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISREG(entry.st_mode) and relative_path in expected_files:
            fingerprint = _scaffold_regular_file_fingerprint(directory_fd, name)
            expected_size, expected_digest = expected_files[relative_path]
            if fingerprint[1:] != (expected_size, expected_digest):
                raise OSError(f"Scaffold recovery preserved a changed module file: {relative_path}")
            files[name] = fingerprint
            continue
        if stat.S_ISDIR(entry.st_mode) and relative_path in expected_directories:
            child_fd = os.open(name, directory_flags, dir_fd=directory_fd)
            try:
                directories[name] = _inspect_scaffold_recovery_tree(
                    child_fd,
                    prefix=relative_path,
                    expected_files=expected_files,
                    expected_directories=expected_directories,
                )
            finally:
                _close_scaffold_descriptor(child_fd)
            continue
        raise OSError(f"Scaffold recovery preserved an unowned module entry: {relative_path}")
    return _ScaffoldRecoveryTree(
        identity=identity,
        files=files,
        directories=directories,
    )


def _scaffold_recovery_tree_files(
    tree: _ScaffoldRecoveryTree,
    *,
    prefix: str = "",
) -> set[str]:
    paths = {f"{prefix}/{name}" if prefix else name for name in tree.files}
    for name, child in tree.directories.items():
        child_prefix = f"{prefix}/{name}" if prefix else name
        paths.update(_scaffold_recovery_tree_files(child, prefix=child_prefix))
    return paths


def _remove_scaffold_recovery_tree(
    parent_fd: int,
    name: str,
    tree: _ScaffoldRecoveryTree,
) -> None:
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    directory_fd = os.open(name, directory_flags, dir_fd=parent_fd)
    try:
        metadata = os.fstat(directory_fd)
        if (metadata.st_dev, metadata.st_ino) != tree.identity:
            raise OSError(f"Scaffold recovery preserved a replaced directory: {name}")
        for file_name, fingerprint in tree.files.items():
            if _scaffold_regular_file_fingerprint(directory_fd, file_name) != fingerprint:
                raise OSError(f"Scaffold recovery preserved a changed module file: {file_name}")
        for child_name, child in tree.directories.items():
            _remove_scaffold_recovery_tree(directory_fd, child_name, child)
        for file_name in tree.files:
            os.unlink(file_name, dir_fd=directory_fd)
        if os.listdir(directory_fd):
            raise OSError(f"Scaffold recovery preserved concurrent data in directory: {name}")
    finally:
        _close_scaffold_descriptor(directory_fd)
    current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != tree.identity:
        raise OSError(f"Scaffold recovery preserved a replaced directory: {name}")
    os.rmdir(name, dir_fd=parent_fd)


def _remove_scaffold_recovery_transaction(
    source_fd: int,
    *,
    transaction_id: str,
    files: Sequence[tuple[str, int, str]],
) -> None:
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    metadata_fd: int | None = None
    transactions_fd: int | None = None
    transaction_fd: int | None = None
    transaction_name = f"batch-{transaction_id}.txn"
    try:
        try:
            metadata_fd = os.open(".paradev", directory_flags, dir_fd=source_fd)
            transactions_fd = os.open(
                "module-transactions",
                directory_flags,
                dir_fd=metadata_fd,
            )
            transaction_fd = os.open(
                transaction_name,
                directory_flags,
                dir_fd=transactions_fd,
            )
        except FileNotFoundError:
            return
        transaction_metadata = os.fstat(transaction_fd)
        transaction_identity = (
            transaction_metadata.st_dev,
            transaction_metadata.st_ino,
        )
        expected = {f"{index:06d}.stage": (size, digest) for index, (_path, size, digest) in enumerate(files)}
        fingerprints: dict[str, tuple[tuple[int, int], int, str]] = {}
        for stage_name in os.listdir(transaction_fd):
            if stage_name not in expected:
                raise OSError(f"Scaffold recovery preserved unowned transaction data: {stage_name}")
            fingerprint = _scaffold_regular_file_fingerprint(
                transaction_fd,
                stage_name,
            )
            if fingerprint[1:] != expected[stage_name]:
                raise OSError(f"Scaffold recovery preserved changed transaction data: {stage_name}")
            fingerprints[stage_name] = fingerprint
        for stage_name, fingerprint in fingerprints.items():
            if _scaffold_regular_file_fingerprint(transaction_fd, stage_name) != fingerprint:
                raise OSError(f"Scaffold recovery preserved changed transaction data: {stage_name}")
        for stage_name in fingerprints:
            os.unlink(stage_name, dir_fd=transaction_fd)
        if os.listdir(transaction_fd):
            raise OSError("Scaffold recovery preserved concurrent transaction data")
        _close_scaffold_descriptor(transaction_fd)
        transaction_fd = None
        if transactions_fd is None:
            raise OSError("Scaffold recovery lost its transaction authority")
        _remove_scaffold_transaction_directory(
            transactions_fd,
            transaction_name,
            transaction_identity,
        )
    finally:
        for descriptor in (transaction_fd, transactions_fd, metadata_fd):
            if isinstance(descriptor, int):
                _close_scaffold_descriptor(descriptor)


def _open_scaffold_directory_chain(parent_fd: int, parts: Sequence[str]) -> int:
    current_fd = os.dup(parent_fd)
    try:
        for part in parts:
            next_fd = _open_or_create_scaffold_directory(current_fd, part)
            _close_scaffold_descriptor(current_fd)
            current_fd = next_fd
    except BaseException:
        _close_scaffold_descriptor(current_fd)
        raise
    return current_fd


def _open_scaffold_directory_chain_tracked(
    parent_fd: int,
    parts: Sequence[str],
    *,
    created_directories: list[_ScaffoldCreatedDirectory],
) -> int:
    current_fd = os.dup(parent_fd)
    try:
        for part in parts:
            parent_anchor = os.dup(current_fd)
            created = False
            try:
                os.mkdir(part, dir_fd=current_fd)
            except FileExistsError:
                _close_scaffold_descriptor(parent_anchor)
            else:
                created = True
                metadata = os.stat(part, dir_fd=current_fd, follow_symlinks=False)
                created_directories.append(
                    _ScaffoldCreatedDirectory(
                        parent_fd=parent_anchor,
                        name=part,
                        identity=(metadata.st_dev, metadata.st_ino),
                        quarantine_name=f"directory-{uuid4().hex}.rollback",
                    )
                )
            next_fd = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
                dir_fd=current_fd,
            )
            if created:
                metadata = os.fstat(next_fd)
                if (metadata.st_dev, metadata.st_ino) != created_directories[-1].identity:
                    _close_scaffold_descriptor(next_fd)
                    raise OSError(f"Scaffold directory changed while it was being opened: {part}")
            _close_scaffold_descriptor(current_fd)
            current_fd = next_fd
    except BaseException:
        _close_scaffold_descriptor(current_fd)
        raise
    return current_fd


def _rollback_scaffold_installs(
    installs: Sequence[_ScaffoldInstall],
    transaction_fd: int | None,
) -> list[BaseException]:
    if transaction_fd is None:
        return [OSError("Scaffold rollback lost its transaction directory")]
    errors = _rollback_scaffold_batch_installs(installs, transaction_fd)
    for install in reversed(installs):
        if not install.backup_moved:
            continue
        backup_fd: int | None = None
        try:
            backup_fd = _open_scaffold_quarantine(
                transaction_fd,
                install.backup_name,
            )
            identity, size, digest = _scaffold_regular_file_fingerprint(
                backup_fd,
                _SCAFFOLD_QUARANTINE_ENTRY,
            )
            if (
                install.backup_identity is None
                or install.backup_size is None
                or install.backup_digest is None
                or identity != install.backup_identity
                or size != install.backup_size
                or digest != install.backup_digest
            ):
                raise OSError(f"Scaffold rollback preserved a changed original for recovery: " f"{install.target_name}")
            if not _restore_scaffold_quarantined_file(
                quarantine_fd=backup_fd,
                parent_fd=install.parent_fd,
                target_name=install.target_name,
            ):
                raise OSError(f"Scaffold rollback refused to overwrite a changed target while " f"restoring: {install.target_name}")
            os.unlink(_SCAFFOLD_QUARANTINE_ENTRY, dir_fd=backup_fd)
            install.backup_moved = False
            _close_scaffold_descriptor(backup_fd)
            backup_fd = None
            os.rmdir(install.backup_name, dir_fd=transaction_fd)
        except BaseException as error:
            errors.append(error)
        finally:
            if backup_fd is not None:
                _close_scaffold_descriptor(backup_fd)
    return errors


def _discard_scaffold_backups(
    installs: Sequence[_ScaffoldInstall],
    transaction_fd: int | None,
) -> list[BaseException]:
    """Discard verified force-write originals after the new files fully commit."""

    if transaction_fd is None:
        return [OSError("Scaffold cleanup lost its transaction directory")]
    errors: list[BaseException] = []
    for install in installs:
        if not install.backup_moved:
            continue
        backup_fd: int | None = None
        try:
            backup_fd = _open_scaffold_quarantine(
                transaction_fd,
                install.backup_name,
            )
            backup = _scaffold_regular_file_fingerprint(
                backup_fd,
                _SCAFFOLD_QUARANTINE_ENTRY,
            )
            if backup != (
                install.backup_identity,
                install.backup_size,
                install.backup_digest,
            ):
                raise OSError(f"Scaffold cleanup preserved a changed original for recovery: " f"{install.target_name}")
            os.unlink(_SCAFFOLD_QUARANTINE_ENTRY, dir_fd=backup_fd)
            install.backup_moved = False
            _close_scaffold_descriptor(backup_fd)
            backup_fd = None
            os.rmdir(install.backup_name, dir_fd=transaction_fd)
        except BaseException as error:
            errors.append(error)
        finally:
            if backup_fd is not None:
                _close_scaffold_descriptor(backup_fd)
    return errors


def _require_scaffold_install_identity(install: _ScaffoldInstall) -> None:
    if install.installed_identity is None or install.installed_size is None or install.installed_digest is None:
        raise OSError(f"Scaffold install lost its staged fingerprint: {install.target_name}")
    identity, size, digest = _scaffold_regular_file_fingerprint(
        install.parent_fd,
        install.target_name,
    )
    if identity != install.installed_identity:
        raise OSError(f"Scaffold install target changed during batch commit: {install.target_name}")
    if size != install.installed_size or digest != install.installed_digest:
        raise OSError(f"Scaffold install target content changed during batch commit: {install.target_name}")


def _require_scaffold_directory_identity(
    directory: _ScaffoldCreatedDirectory,
) -> None:
    current = os.stat(
        directory.name,
        dir_fd=directory.parent_fd,
        follow_symlinks=False,
    )
    if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != directory.identity:
        raise OSError(f"Scaffold directory changed during commit: {directory.name}")


def _rollback_scaffold_batch_installs(
    installs: Sequence[_ScaffoldInstall],
    transaction_fd: int | None,
) -> list[BaseException]:
    if transaction_fd is None:
        return [OSError("Scaffold rollback lost its transaction directory")]
    errors: list[BaseException] = []
    for install in reversed(installs):
        if not install.installed:
            continue
        quarantine_fd: int | None = None
        quarantine_name = f"{install.backup_name}.rollback"
        try:
            try:
                identity, size, digest = _scaffold_regular_file_fingerprint(
                    install.parent_fd,
                    install.target_name,
                )
            except FileNotFoundError:
                install.installed = False
                continue
            if (
                install.installed_identity is None
                or install.installed_size is None
                or install.installed_digest is None
                or identity != install.installed_identity
                or size != install.installed_size
                or digest != install.installed_digest
            ):
                raise OSError(f"Scaffold rollback refused to remove a changed target: {install.target_name}")
            quarantine_fd = _quarantine_scaffold_entry(
                parent_fd=install.parent_fd,
                name=install.target_name,
                transaction_fd=transaction_fd,
                quarantine_name=quarantine_name,
            )
            (
                quarantined_identity,
                quarantined_size,
                quarantined_digest,
            ) = _scaffold_regular_file_fingerprint(
                quarantine_fd,
                _SCAFFOLD_QUARANTINE_ENTRY,
            )
            if (
                quarantined_identity != install.installed_identity
                or quarantined_size != install.installed_size
                or quarantined_digest != install.installed_digest
            ):
                restored = _restore_scaffold_quarantined_file(
                    quarantine_fd=quarantine_fd,
                    parent_fd=install.parent_fd,
                    target_name=install.target_name,
                )
                disposition = "restored without overwrite" if restored else "preserved for recovery"
                raise OSError(f"Scaffold rollback quarantined a changed target " f"({disposition}): {install.target_name}")
            os.unlink(_SCAFFOLD_QUARANTINE_ENTRY, dir_fd=quarantine_fd)
            install.installed = False
            _close_scaffold_descriptor(quarantine_fd)
            quarantine_fd = None
            os.rmdir(quarantine_name, dir_fd=transaction_fd)
        except FileNotFoundError:
            install.installed = False
        except BaseException as error:
            errors.append(error)
        finally:
            if quarantine_fd is not None:
                _close_scaffold_descriptor(quarantine_fd)
    return errors


def _rollback_scaffold_directories(
    created_directories: Sequence[_ScaffoldCreatedDirectory],
    transaction_fd: int | None,
) -> list[BaseException]:
    if transaction_fd is None:
        return [OSError("Scaffold rollback lost its transaction directory")]
    errors: list[BaseException] = []
    for created_directory in reversed(created_directories):
        current_fd: int | None = None
        quarantine_fd: int | None = None
        try:
            try:
                current_fd = os.open(
                    created_directory.name,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=created_directory.parent_fd,
                )
            except FileNotFoundError:
                continue
            current = os.fstat(current_fd)
            if (current.st_dev, current.st_ino) != created_directory.identity:
                raise OSError(f"Scaffold rollback refused to remove a changed directory: {created_directory.name}")
            if os.listdir(current_fd):
                raise OSError(f"Scaffold rollback refused to remove a non-empty directory: " f"{created_directory.name}")
            _close_scaffold_descriptor(current_fd)
            current_fd = None
            quarantine_fd = _quarantine_scaffold_entry(
                parent_fd=created_directory.parent_fd,
                name=created_directory.name,
                transaction_fd=transaction_fd,
                quarantine_name=created_directory.quarantine_name,
            )
            quarantined = os.stat(
                _SCAFFOLD_QUARANTINE_ENTRY,
                dir_fd=quarantine_fd,
                follow_symlinks=False,
            )
            if not stat.S_ISDIR(quarantined.st_mode) or (quarantined.st_dev, quarantined.st_ino) != created_directory.identity:
                raise OSError(f"Scaffold rollback quarantined a changed directory " f"for recovery: {created_directory.name}")
            os.rmdir(_SCAFFOLD_QUARANTINE_ENTRY, dir_fd=quarantine_fd)
            _close_scaffold_descriptor(quarantine_fd)
            quarantine_fd = None
            os.rmdir(created_directory.quarantine_name, dir_fd=transaction_fd)
        except FileNotFoundError:
            continue
        except BaseException as error:
            errors.append(error)
        finally:
            if current_fd is not None:
                _close_scaffold_descriptor(current_fd)
            if quarantine_fd is not None:
                _close_scaffold_descriptor(quarantine_fd)
    return errors


_SCAFFOLD_QUARANTINE_ENTRY = "entry"


def _quarantine_scaffold_entry(
    *,
    parent_fd: int,
    name: str,
    transaction_fd: int,
    quarantine_name: str,
) -> int:
    """Atomically move one rollback candidate into a private transaction directory."""

    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    os.mkdir(quarantine_name, 0o700, dir_fd=transaction_fd)
    quarantine_fd = os.open(quarantine_name, flags, dir_fd=transaction_fd)
    try:
        os.rename(
            name,
            _SCAFFOLD_QUARANTINE_ENTRY,
            src_dir_fd=parent_fd,
            dst_dir_fd=quarantine_fd,
        )
    except BaseException:
        _close_scaffold_descriptor(quarantine_fd)
        try:
            os.rmdir(quarantine_name, dir_fd=transaction_fd)
        except OSError:
            pass
        raise
    return quarantine_fd


def _restore_scaffold_quarantined_file(
    *,
    quarantine_fd: int,
    parent_fd: int,
    target_name: str,
) -> bool:
    """Restore a quarantined non-directory without overwriting a new target."""

    try:
        os.link(
            _SCAFFOLD_QUARANTINE_ENTRY,
            target_name,
            src_dir_fd=quarantine_fd,
            dst_dir_fd=parent_fd,
            follow_symlinks=False,
        )
    except FileExistsError:
        try:
            quarantined = _scaffold_regular_file_fingerprint(
                quarantine_fd,
                _SCAFFOLD_QUARANTINE_ENTRY,
            )
            current = _scaffold_regular_file_fingerprint(parent_fd, target_name)
        except OSError:
            return False
        return current[0] == quarantined[0]
    except OSError:
        return False
    return True


def _open_scaffold_quarantine(
    transaction_fd: int,
    quarantine_name: str,
) -> int:
    """Open an existing private transaction quarantine without following links."""

    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    return os.open(quarantine_name, flags, dir_fd=transaction_fd)


def _scaffold_regular_file_fingerprint(
    parent_fd: int,
    name: str,
) -> tuple[tuple[int, int], int, str]:
    """Return a stable identity, size, and digest for one anchored regular file."""

    flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
    file_fd = os.open(name, flags, dir_fd=parent_fd)
    try:
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise OSError(f"Scaffold target is not a regular file: {name}")
        digest = hashlib.sha256()
        while chunk := os.read(file_fd, 1024 * 1024):
            digest.update(chunk)
        after = os.fstat(file_fd)
        before_state = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        after_state = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if after_state != before_state:
            raise OSError(f"Scaffold target changed while it was being fingerprinted: {name}")
        return (
            (after.st_dev, after.st_ino),
            after.st_size,
            digest.hexdigest(),
        )
    finally:
        _close_scaffold_descriptor(file_fd)


def _cleanup_scaffold_transaction(
    transaction_fd: int,
    stage_fingerprints: Mapping[str, tuple[tuple[int, int], int, str]],
) -> list[BaseException]:
    """Remove only the exact staged files owned by one private transaction."""

    errors: list[BaseException] = []
    try:
        actual_names = set(os.listdir(transaction_fd))
    except BaseException as error:
        return [error]
    expected_names = set(stage_fingerprints)
    if actual_names != expected_names:
        unexpected = sorted(actual_names - expected_names)
        missing = sorted(expected_names - actual_names)
        return [OSError("Scaffold transaction contains unexpected recovery data " f"(unexpected={unexpected}, missing={missing})")]
    for stage_name in sorted(expected_names):
        try:
            current = _scaffold_regular_file_fingerprint(
                transaction_fd,
                stage_name,
            )
            if current != stage_fingerprints[stage_name]:
                raise OSError(f"Scaffold transaction stage changed before cleanup: {stage_name}")
        except BaseException as error:
            errors.append(error)
    if errors:
        return errors
    for stage_name in sorted(expected_names):
        try:
            os.unlink(stage_name, dir_fd=transaction_fd)
        except BaseException as error:
            errors.append(error)
    return errors


def _remove_scaffold_transaction_directory(
    transactions_fd: int,
    transaction_name: str,
    expected_identity: tuple[int, int],
) -> None:
    """Remove one empty transaction without rmdir-by-stale-name races."""

    current_fd = _open_scaffold_quarantine(
        transactions_fd,
        transaction_name,
    )
    try:
        current = os.fstat(current_fd)
        if (current.st_dev, current.st_ino) != expected_identity:
            raise OSError(f"Scaffold cleanup preserved a replaced transaction: {transaction_name}")
    finally:
        _close_scaffold_descriptor(current_fd)

    cleanup_name = f"{transaction_name}.cleanup-{uuid4().hex}.rollback"
    os.rename(
        transaction_name,
        cleanup_name,
        src_dir_fd=transactions_fd,
        dst_dir_fd=transactions_fd,
    )
    moved = os.stat(
        cleanup_name,
        dir_fd=transactions_fd,
        follow_symlinks=False,
    )
    if not stat.S_ISDIR(moved.st_mode) or (moved.st_dev, moved.st_ino) != expected_identity:
        raise OSError(f"Scaffold cleanup quarantined a replaced transaction for recovery: " f"{cleanup_name}")
    os.rmdir(cleanup_name, dir_fd=transactions_fd)


def _open_or_create_scaffold_directory(parent_fd: int, name: str) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    try:
        os.mkdir(name, dir_fd=parent_fd)
    except FileExistsError:
        pass
    return os.open(name, flags, dir_fd=parent_fd)


def _require_no_scaffold_module_alias(
    family_fd: int,
    *,
    object_id: str,
    folder_name: str,
) -> None:
    """Reject a concurrent case/Unicode/title alias for one logical module."""

    logical_key = _portable_name_key(object_id)
    aliases = sorted(name for name in os.listdir(family_fd) if _portable_name_key(_module_folder_object_id(name)) == logical_key and name != folder_name)
    if aliases:
        raise OSError(f"Module {object_id!r} has a conflicting physical folder: " f"{', '.join(aliases)}.")


def _require_scaffold_target_identity(
    project_fd: int,
    source_parts: Sequence[str],
    family: str,
    folder_name: str,
    *,
    container: str = "modules",
    expected_family_fd: int,
    expected_module_fd: int,
) -> None:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    source_fd = _open_existing_scaffold_directory_chain(project_fd, source_parts)
    container_fd: int | None = None
    family_fd: int | None = None
    module_fd: int | None = None
    try:
        container_fd = os.open(container, flags, dir_fd=source_fd)
        family_fd = os.open(family, flags, dir_fd=container_fd)
        module_fd = os.open(folder_name, flags, dir_fd=family_fd)
        for label, expected_fd, current_fd in (
            ("family", expected_family_fd, family_fd),
            ("module", expected_module_fd, module_fd),
        ):
            expected = os.fstat(expected_fd)
            current = os.fstat(current_fd)
            if (current.st_dev, current.st_ino) != (expected.st_dev, expected.st_ino):
                raise OSError(f"Scaffold {label} path changed while files were being written")
    finally:
        for descriptor in (module_fd, family_fd, container_fd, source_fd):
            if isinstance(descriptor, int):
                _close_scaffold_descriptor(descriptor)


def _open_existing_scaffold_directory_chain(parent_fd: int, parts: Sequence[str]) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    current_fd = os.dup(parent_fd)
    try:
        for part in parts:
            next_fd = os.open(part, flags, dir_fd=current_fd)
            _close_scaffold_descriptor(current_fd)
            current_fd = next_fd
    except BaseException:
        _close_scaffold_descriptor(current_fd)
        raise
    return current_fd


def _write_scaffold_file_anchored(module_fd: int, relative_path: str, content: str, *, force: bool) -> None:
    parts = PurePosixPath(relative_path).parts
    parent_fd = _open_scaffold_directory_chain(module_fd, parts[:-1])
    target_name = parts[-1]
    temporary_name = f".paradev-scaffold-{uuid4().hex}.tmp" if force else target_name
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    file_fd: int | None = None
    installed = False
    try:
        file_fd = os.open(temporary_name, file_flags, 0o666, dir_fd=parent_fd)
        _write_scaffold_bytes(file_fd, _normalized_scaffold_payload(content))
        os.fsync(file_fd)
        _close_scaffold_descriptor(file_fd)
        file_fd = None
        if force:
            os.rename(temporary_name, target_name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        installed = True
    finally:
        if file_fd is not None:
            _close_scaffold_descriptor(file_fd)
        if not installed:
            try:
                os.unlink(temporary_name, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
        _close_scaffold_descriptor(parent_fd)


def _write_scaffold_bytes(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("Scaffold file write made no progress")
        view = view[written:]


def _close_scaffold_descriptor(descriptor: int) -> None:
    try:
        os.close(descriptor)
    except OSError:
        pass


def _existing_file_diagnostics(
    template: ModuleTemplate,
    rendered_files: list[dict[str, object]],
    *,
    force: bool,
) -> list[dict[str, object]]:
    if force:
        return []
    diagnostics: list[dict[str, object]] = []
    for item in rendered_files:
        target = item.get("target")
        if isinstance(target, Path) and _path_entry_exists(target):
            diagnostics.append(
                {
                    "code": "scaffold.file_exists",
                    "severity": "error",
                    "message": f"Template {template.template_id} would overwrite existing file: {target}.",
                    "template_id": template.template_id,
                    "path": str(target),
                }
            )
    return diagnostics


def _scaffold_module_matches_rendered_files(
    module_root: Path,
    rendered_files: Sequence[Mapping[str, object]],
) -> bool:
    """Return whether a module directory exactly matches rendered scaffold files."""

    try:
        root_entry = module_root.lstat()
    except FileNotFoundError:
        return False
    if not stat.S_ISDIR(root_entry.st_mode) or stat.S_ISLNK(root_entry.st_mode):
        return False

    expected: dict[str, bytes] = {}
    for item in rendered_files:
        if item.get("system") is True:
            continue
        relative_path = item.get("relative_module_path")
        content = item.get("content")
        if not isinstance(relative_path, str) or not isinstance(content, str):
            return False
        if relative_path in expected:
            return False
        expected[relative_path] = _normalized_scaffold_payload(content)

    actual: dict[str, Path] = {}
    try:
        for current_root, directory_names, file_names in os.walk(module_root, followlinks=False):
            current = Path(current_root)
            metadata_names = [name for name in directory_names if _portable_name_key(name) == ".paradev"] if current == module_root else []
            if len(metadata_names) > 1:
                return False
            if metadata_names:
                metadata_name = metadata_names[0]
                metadata_root = current / metadata_name
                metadata_entry = metadata_root.lstat()
                if stat.S_ISLNK(metadata_entry.st_mode) or not stat.S_ISDIR(metadata_entry.st_mode):
                    return False
                directory_names.remove(metadata_name)
            for name in directory_names:
                entry = (current / name).lstat()
                if stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode):
                    return False
            for name in file_names:
                path = current / name
                entry = path.lstat()
                if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
                    return False
                relative_path = path.relative_to(module_root).as_posix()
                actual[relative_path] = path
    except OSError:
        return False
    if set(actual) != set(expected):
        return False
    try:
        return all(actual[path].read_bytes() == payload for path, payload in expected.items())
    except OSError:
        return False


def _normalized_scaffold_payload(content: str) -> bytes:
    normalized_content = content.rstrip("\n")
    return f"{normalized_content}\n".encode("utf-8", errors="ignore")


def _file_view(
    project_root: Path,
    item: dict[str, object],
    *,
    force: bool,
    unsafe: bool = False,
    target_kind: Literal["module", "collection"] = "module",
) -> dict[str, object]:
    target = item["target"]
    if not isinstance(target, Path):
        raise TypeError("Scaffold file target must be a Path.")
    exists = False if unsafe else _path_entry_exists(target)
    action = "blocked" if unsafe else "overwrite" if exists and force else "exists" if exists else "create"
    resource_path_key = "collection_path" if target_kind == "collection" else "module_path"
    return {
        "path": str(target),
        "relative_path": _relative_path(project_root, target),
        resource_path_key: item["relative_module_path"],
        "action": action,
        **({"system": True} if item.get("system") is True else {}),
    }


def _path_entry_exists(path: Path) -> bool:
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    return True


def _relative_path(root: Path, target: Path) -> str:
    try:
        return str(target.relative_to(root))
    except ValueError:
        return str(target)


def _missing_value_diagnostic(template_id: str, field: str) -> dict[str, object]:
    return {
        "code": "scaffold.missing_value",
        "severity": "error",
        "message": f"Template {template_id} requires value '{field}'.",
        "template_id": template_id,
        "field": field,
    }


def _scaffold_error_diagnostic(template_id: str, code: str, message: str) -> dict[str, object]:
    return {
        "code": code,
        "severity": "error",
        "message": message,
        "template_id": template_id,
    }


def _scaffold_write_diagnostic(
    template: ModuleTemplate,
    path: Path,
    *,
    code: str,
    message: str,
) -> dict[str, object]:
    return {
        "code": code,
        "severity": "error",
        "message": message,
        "template_id": template.template_id,
        "path": str(path),
    }


def _scalar_text(value: object) -> str:
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    raise ProjectTemplateSpecError(f"Template values must be scalar strings, numbers, or booleans, got {type(value).__name__}.")


def _title_from_id(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def _template_arg_label(value: str) -> str:
    """Return a readable field label while preserving common domain acronyms."""

    parts = [part for part in value.replace("-", "_").split("_") if part]
    return " ".join(
        _TEMPLATE_LABEL_WORDS.get(
            part.casefold(),
            part.capitalize() if index == 0 else part.casefold(),
        )
        for index, part in enumerate(parts)
    )


def _inline_template_arg_label(value: str) -> str:
    """Return a label embedded after another word without damaging acronyms."""

    first_word = value.split(" ", 1)[0]
    if len(first_word) > 1 and first_word.isupper():
        return value
    return f"{value[:1].lower()}{value[1:]}"


def _family_tag(family: str, object_id: str) -> str:
    prefix = f"{family.upper()}_"
    if object_id.upper().startswith(prefix):
        return object_id[len(prefix) :]
    return object_id
