"""Generated Project object API table."""

from __future__ import annotations

import inspect
from collections.abc import Mapping, Sequence
from dataclasses import fields
from typing import cast

from typing_extensions import TypedDict

from paradev._api_table import api_annotation_text, api_indexed_table, api_table_selection, api_value_indexes
from paradev._api_table_markdown import api_indexed_reference_sections, api_reference_markdown

from .project import Project, get_project_inspection_contract

PROJECT_API_TABLE_SCHEMA = "paradev.sdk.project-api-table.v1"
_PROJECT_API_REFERENCE_PAGE = "docs/user-manual/project-api-reference.md"
_PROJECT_API_TEST_ANCHOR = "tests/test_architecture.py::test_project_api_table_lists_project_object_surface"
_PROJECT_API_INDEX_NAMES = (
    "feature_index",
    "kind_index",
    "cli_command_index",
    "frontend_operation_index",
    "inspection_kind_index",
)
_PROJECT_API_STANDARD_FIELDS = (
    "symbol",
    "kind",
    "layer",
    "feature",
    "inputs",
    "returns",
    "raises",
    "cli_commands",
    "frontend_operation_ids",
    "inspection_kinds",
    "registry_seam",
    "surface",
    "doc_page",
    "test_anchor",
)


class ProjectApiRow(TypedDict):
    """One public `Project` object API row."""

    symbol: str
    kind: str
    layer: str
    feature: str
    inputs: str
    returns: str
    raises: str
    cli_commands: list[str]
    frontend_operation_ids: list[str]
    inspection_kinds: list[str]
    registry_seam: str
    surface: str
    doc_page: str
    test_anchor: str


class ProjectApiTable(TypedDict):
    """Generated API-standard table for the public `Project` object."""

    schema: str
    row_count: int
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    cli_command_index: dict[str, list[str]]
    frontend_operation_index: dict[str, list[str]]
    inspection_kind_index: dict[str, list[str]]
    rows: list[ProjectApiRow]


def get_project_api_table() -> ProjectApiTable:
    """Return the API-standard table for the public `Project` object.

    Returns:
        JSON-safe table with public `Project` dataclass fields, classmethods,
        and instance methods plus indexes for features, row kinds, CLI
        commands, frontend operations, and inspection kinds.
    """

    return cast(
        ProjectApiTable,
        api_indexed_table(
            PROJECT_API_TABLE_SCHEMA,
            _project_api_rows(),
            (
                ("feature_index", "feature"),
                ("kind_index", "kind"),
                ("cli_command_index", "cli_commands"),
                ("frontend_operation_index", "frontend_operation_ids"),
                ("inspection_kind_index", "inspection_kinds"),
            ),
            index_list_fields=("cli_commands", "frontend_operation_ids", "inspection_kinds"),
            row_list_fields=("cli_commands", "frontend_operation_ids", "inspection_kinds"),
        ),
    )


def get_project_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> ProjectApiTable | ProjectApiRow | list[str]:
    """Return the full Project API table, one row, or one index bucket.

    Args:
        symbol: Optional public Project symbol to select from the table rows.
        index_name: Optional index name, such as `feature_index`,
            `kind_index`, `cli_command_index`, `frontend_operation_index`, or
            `inspection_kind_index`.
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
        ProjectApiTable | ProjectApiRow | list[str],
        api_table_selection(
            get_project_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_PROJECT_API_INDEX_NAMES,
        ),
    )


def render_project_api_reference_markdown() -> str:
    """Render the public `Project` object API table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/project-api-reference.md`. The content is generated
        from `get_project_api_table()` so the object API, CLI commands,
        frontend operation ids, project inspection kinds, and docs stay
        aligned.
    """

    table = get_project_api_table()
    return api_reference_markdown(
        title="Project API Reference",
        source="paradev.sdk.get_project_api_table()",
        regenerate_when="Regenerate this file whenever the public `Project` object API changes:",
        command="rtk uv run paradev project-api --markdown > docs/user-manual/project-api-reference.md",
        sections=api_indexed_reference_sections(
            summary_lines=[
                f"- API rows / API 行数: {table['row_count']}",
                f"- Features / Feature 数: {len(table['feature_index'])}",
                f"- Row kinds / 行类型数: {len(table['kind_index'])}",
                f"- CLI commands / CLI 命令数: {len(table['cli_command_index'])}",
                f"- Frontend operations / 前端操作数: {len(table['frontend_operation_index'])}",
                f"- Inspection kinds / Inspection 类型数: {len(table['inspection_kind_index'])}",
            ],
            table=table,
            index_specs=(
                ("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", "Project APIs"),
                ("Kind Index / 行类型索引", "kind_index", "Kind", "Symbols", "Project APIs"),
                ("CLI Command Index / CLI 命令索引", "cli_command_index", "CLI Command", "Symbols", "Project APIs"),
                ("Frontend Operation Index / 前端操作索引", "frontend_operation_index", "Operation", "Symbols", "Project APIs"),
                (
                    "Inspection Kind Index / Inspection 类型索引",
                    "inspection_kind_index",
                    "Inspection Kind",
                    "Symbols",
                    "Project APIs",
                ),
            ),
            fields=_PROJECT_API_STANDARD_FIELDS,
            list_fields=("cli_commands", "frontend_operation_ids", "inspection_kinds"),
        ),
    )


def _project_api_rows() -> list[ProjectApiRow]:
    cli_commands = _project_api_cli_commands()
    frontend_operation_ids = _project_api_frontend_operation_ids()
    inspection_kinds = _project_api_inspection_kinds()
    rows: list[ProjectApiRow] = []
    for field in fields(Project):
        symbol = f"Project.{field.name}"
        rows.append(
            {
                "symbol": symbol,
                "kind": "field",
                "layer": "sdk",
                "feature": "project-state",
                "inputs": "constructor",
                "returns": api_annotation_text(field.type),
                "raises": "",
                "cli_commands": [],
                "frontend_operation_ids": [],
                "inspection_kinds": [],
                "registry_seam": _project_api_registry_seam(symbol, "project-state"),
                "surface": "sdk",
                "doc_page": "docs/user-manual/sdk-python.md",
                "test_anchor": _PROJECT_API_TEST_ANCHOR,
            }
        )
    for name, raw in Project.__dict__.items():
        if name.startswith("_"):
            continue
        method = getattr(Project, name, None)
        if not callable(method):
            continue
        symbol = f"Project.{name}"
        signature = inspect.signature(method)
        feature = _project_api_feature(symbol, inspection_kinds.get(symbol, []), frontend_operation_ids.get(symbol, []))
        rows.append(
            {
                "symbol": symbol,
                "kind": _project_api_kind(raw),
                "layer": "sdk",
                "feature": feature,
                "inputs": _signature_inputs(signature),
                "returns": api_annotation_text(signature.return_annotation),
                "raises": _project_api_raises(symbol),
                "cli_commands": list(cli_commands.get(symbol, [])),
                "frontend_operation_ids": list(frontend_operation_ids.get(symbol, [])),
                "inspection_kinds": list(inspection_kinds.get(symbol, [])),
                "registry_seam": _project_api_registry_seam(symbol, feature),
                "surface": "sdk",
                "doc_page": _project_api_doc_page(feature, bool(inspection_kinds.get(symbol))),
                "test_anchor": _PROJECT_API_TEST_ANCHOR,
            }
        )
    return rows


def _project_api_kind(raw: object) -> str:
    if isinstance(raw, classmethod):
        return "classmethod"
    if isinstance(raw, staticmethod):
        return "staticmethod"
    return "method"


def _project_api_cli_commands() -> dict[str, list[str]]:
    from paradev.surfaces.cli import get_cli_contract

    rows: list[dict[str, str]] = []
    adapters = get_cli_contract().get("adapters", {})
    if isinstance(adapters, Mapping):
        for command, adapter in adapters.items():
            command_text = str(command)
            symbol = _project_api_cli_command_symbol(command_text, str(adapter))
            if symbol:
                rows.append({"symbol": symbol, "command": f"paradev {command_text}"})
    (commands,) = api_value_indexes(rows, "symbol", value_field="command")
    return commands


def _project_api_frontend_operation_ids() -> dict[str, list[str]]:
    from .frontend_api import get_frontend_api_contract

    rows: list[dict[str, str]] = []
    operations = get_frontend_api_contract().get("operations", [])
    if not isinstance(operations, Sequence):
        return {}
    for operation in operations:
        if not isinstance(operation, Mapping):
            continue
        operation_id = operation.get("id")
        if not isinstance(operation_id, str):
            continue
        symbol = _project_api_operation_symbol(operation)
        if symbol:
            rows.append({"symbol": symbol, "operation_id": operation_id})
    (operation_ids,) = api_value_indexes(rows, "symbol", value_field="operation_id")
    return operation_ids


def _project_api_cli_command_symbol(command: str, adapter: str) -> str | None:
    if command == "inspections" and adapter == "get_project_inspection_selection":
        return "Project.inspections"
    return _project_api_adapter_symbol(adapter)


def _project_api_inspection_kinds() -> dict[str, list[str]]:
    rows: list[dict[str, str]] = []
    for inspection in get_project_inspection_contract()["inspections"]:
        kind = str(inspection["kind"])
        rows.extend(
            (
                {"symbol": str(inspection["method"]), "kind": kind},
                {"symbol": "Project.inspect", "kind": kind},
            )
        )
    (inspection_kinds,) = api_value_indexes(rows, "symbol", value_field="kind")
    return inspection_kinds


def _project_api_operation_symbol(operation: Mapping[object, object]) -> str | None:
    bindings = operation.get("bindings")
    if not isinstance(bindings, Mapping):
        return None
    sdk = bindings.get("sdk")
    if not isinstance(sdk, Mapping):
        return None
    call = sdk.get("call")
    if not isinstance(call, str):
        return None
    return _project_api_adapter_symbol(call)


def _project_api_adapter_symbol(adapter: str) -> str | None:
    if adapter.startswith("Project.inspect("):
        kind = adapter.removeprefix("Project.inspect(").removesuffix(")").strip("'\"")
        return _inspection_method_symbol(kind)
    if adapter.startswith("Project."):
        return adapter
    return None


def _inspection_method_symbol(kind: str) -> str:
    method = kind.replace("-", "_")
    return f"Project.{method}"


def _project_api_feature(symbol: str, inspection_kinds: list[str], frontend_operation_ids: list[str]) -> str:
    if symbol in {
        "Project.root",
        "Project.manifest_path",
        "Project.project_id",
        "Project.title",
        "Project.game",
        "Project.source_roots",
        "Project.output_root",
        "Project.build_root",
    }:
        return "project-state"
    if symbol in {
        "Project.extension_modules",
        "Project.python_modules",
        "Project.family_specs",
        "Project.template_specs",
        "Project.copy_roots",
        "Project.descriptor_metadata",
    }:
        return "project-extension"
    if symbol in {"Project.find", "Project.create", "Project.load", "Project.to_view", "Project.rename"}:
        return "projects"
    if symbol in {
        "Project.templates",
        "Project.authoring_path",
        "Project.authoring_plan",
        "Project.scaffold_module",
        "Project.create_module",
        "Project.create_modules",
        "Project.create_module_draft",
        "Project.localization_workspace",
        "Project.plan_localization_update",
    }:
        return "authoring"
    if "module" in symbol:
        return "modules"
    if "collection" in symbol:
        return "collections"
    if symbol in {"Project.build"}:
        return "build"
    if symbol in {"Project.catalog_preview", "Project.catalog_query", "Project.catalog_status"}:
        return "catalog"
    if symbol in {"Project.inspections", "Project.inspect"}:
        return "inspections"
    if inspection_kinds or any(operation_id.startswith("build.") for operation_id in frontend_operation_ids):
        return "build"
    return "projects"


def _project_api_registry_seam(symbol: str, feature: str) -> str:
    if feature in {"authoring", "modules", "collections", "build"}:
        return "project build registry"
    if feature == "catalog":
        return "HeavenBase catalog registry"
    if symbol == "Project.inspect" or feature == "inspections":
        return "Project inspection dispatcher"
    if feature == "project-extension":
        return "project manifest extension declarations"
    return "none"


def _project_api_doc_page(feature: str, inspection_bound: bool) -> str:
    if inspection_bound:
        return "docs/user-manual/project-inspection-reference.md"
    if feature == "authoring":
        return "docs/user-manual/modules-and-collections.md"
    if feature in {"modules", "collections"}:
        return "docs/user-manual/modules-and-collections.md"
    if feature in {"build", "catalog"}:
        return "docs/user-manual/build-and-diagnostics.md"
    return "docs/user-manual/sdk-python.md"


def _project_api_raises(symbol: str) -> str:
    if symbol == "Project.create":
        return "ProjectCreateError"
    if symbol == "Project.load":
        return "ProjectManifestError"
    if symbol in {"Project.find"}:
        return "returns diagnostics instead of raising"
    return ""


def _signature_inputs(signature: inspect.Signature) -> str:
    params = [str(param) for param in signature.parameters.values() if param.name not in {"self", "cls"}]
    return ", ".join(params) if params else "none"
