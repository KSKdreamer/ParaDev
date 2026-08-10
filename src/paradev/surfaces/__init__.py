"""Surface adapter contracts for ParaDev."""

from collections.abc import Callable
from typing import Literal, TypeAlias, cast

from typing_extensions import TypedDict

from paradev._api_table import api_value_indexes
from paradev._api_table_markdown import (
    api_reference_markdown,
    api_summary_reference_sections,
    api_table_section,
    code_cell,
    code_list_cell,
    index_row,
    markdown_cell,
)

from .api import (
    SURFACES_API_TABLE_SCHEMA,
    SurfacesApiRow,
    SurfacesApiTable,
    get_surfaces_api_selection,
    get_surfaces_api_table,
    render_surfaces_api_reference_markdown,
)
from .api_catalog import (
    API_CATALOG_INDEX_CATALOG,
    API_CATALOG_SCHEMA,
    API_CATALOG_SOURCE_ROWS,
    ApiCatalogIndexCatalogRow,
    ApiCatalogReferenceGroupRow,
    ApiCatalogRow,
    ApiCatalogSourceRow,
    ApiCatalogSummary,
    ApiCatalogTable,
    get_api_catalog_group_reference_ids,
    get_api_catalog_reference_group,
    get_api_catalog_reference_groups,
    get_api_catalog_index_catalog,
    get_api_catalog_reference,
    get_api_catalog_reference_ids,
    get_api_catalog_selection,
    get_api_catalog_summary,
    get_api_catalog_table,
    render_api_catalog_reference_markdown,
)
from .bundle import get_bundle_contract
from .cli import get_cli_api_table, get_cli_contract, render_cli_api_reference_markdown
from .lsp import get_lsp_contract
from .mcp import get_mcp_api_selection, get_mcp_api_table, get_mcp_contract, render_mcp_api_reference_markdown
from .rest import get_openapi_seed, get_rest_api_selection, get_rest_api_table, render_rest_api_reference_markdown
from .vscode import get_vscode_contract

SurfaceContractIdentifier: TypeAlias = Literal["bundle", "cli", "lsp", "mcp", "openapi", "vscode"]
SurfaceContractPayload: TypeAlias = dict[str, object]
_SurfaceContractBuilder: TypeAlias = Callable[[], SurfaceContractPayload]

SURFACE_CONTRACT_IDS: tuple[SurfaceContractIdentifier, ...] = ("bundle", "cli", "lsp", "mcp", "openapi", "vscode")
SURFACE_CONTRACT_SUMMARY_SCHEMA = "paradev.surface-contract-summary.v1"
SURFACE_CONTRACT_INDEX_CATALOG: tuple[dict[str, str], ...] = (
    {
        "id": "identifier",
        "contract_path": 'summary["index"][identifier]',
        "python_helper": "get_surface_contract_summary_row(identifier)",
        "usage": "Surface identifier to compact summary row.",
    },
    {
        "id": "status",
        "contract_path": 'summary["status_index"][status]',
        "python_helper": "get_surface_contract_status_ids(status)",
        "usage": "Contract status to ordered surface ids.",
    },
)

_SURFACE_CONTRACT_BUILDERS: tuple[tuple[SurfaceContractIdentifier, _SurfaceContractBuilder], ...] = (
    ("bundle", get_bundle_contract),
    ("cli", get_cli_contract),
    ("lsp", get_lsp_contract),
    ("mcp", get_mcp_contract),
    ("openapi", get_openapi_seed),
    ("vscode", get_vscode_contract),
)


class SurfaceContractSummaryRow(TypedDict):
    """Compact table row for one static surface contract."""

    identifier: SurfaceContractIdentifier
    status: str
    runtime: str
    sdk_owned: bool
    top_level_keys: list[str]


class SurfaceContractIndexCatalogRow(TypedDict):
    """Documented index dimension for the static surface contract catalog."""

    id: str
    contract_path: str
    python_helper: str
    usage: str


class SurfaceContractSummary(TypedDict):
    """Compact table projection for the static surface contract catalog."""

    schema: str
    surface_count: int
    sdk_owned_count: int
    status_counts: dict[str, int]
    status_index: dict[str, list[SurfaceContractIdentifier]]
    index: dict[SurfaceContractIdentifier, int]
    rows: list[SurfaceContractSummaryRow]


def get_surface_contract_ids() -> list[SurfaceContractIdentifier]:
    """Return stable identifiers for the static surface contract catalog.

    Returns:
        Ordered surface identifiers accepted by `get_surface_contract`.
    """

    return list(SURFACE_CONTRACT_IDS)


def get_surface_contract_index_catalog() -> list[SurfaceContractIndexCatalogRow]:
    """Return documented index dimensions for the static surface catalog.

    Returns:
        Copied rows describing the contract path, Python helper, and intended
        lookup use for each static surface contract index dimension.
    """

    return [dict(row) for row in SURFACE_CONTRACT_INDEX_CATALOG]


def get_surface_contract_selection(
    identifier: str | None = None,
    status: str | None = None,
) -> "SurfaceContractSummary | SurfaceContractPayload | list[SurfaceContractIdentifier]":
    """Return a static surface contract payload for one optional selector shape.

    Args:
        identifier: Optional stable surface identifier such as `openapi`.
        status: Optional contract status such as `implemented` or `scaffold`.

    Returns:
        Full surface contract summary when no selector is passed, one contract
        payload for `identifier`, or one ordered surface id list for `status`.

    Raises:
        ValueError: If selector arguments are ambiguous.
        KeyError: If `identifier` or `status` is not listed in the static
            surface contract catalog.
    """

    if identifier is not None and status is not None:
        raise ValueError("Pass only one surface contract selector: identifier or status.")
    if identifier is not None:
        return get_surface_contract(identifier)
    if status is not None:
        return get_surface_contract_status_ids(status)
    return get_surface_contract_summary()


def _surface_contract_builder(identifier: str) -> tuple[SurfaceContractIdentifier, _SurfaceContractBuilder]:
    for surface, builder in _SURFACE_CONTRACT_BUILDERS:
        if surface == identifier:
            return surface, builder
    known = ", ".join(SURFACE_CONTRACT_IDS)
    raise KeyError(f"unknown ParaDev surface contract {identifier!r}; expected one of: {known}")


def _surface_contract_summary_row(identifier: SurfaceContractIdentifier, contract: SurfaceContractPayload) -> SurfaceContractSummaryRow:
    runtime = contract.get("runtime")
    if not isinstance(runtime, str):
        openapi_version = contract.get("openapi")
        runtime = f"openapi-{openapi_version}" if isinstance(openapi_version, str) else ""
    status = contract.get("status")
    return {
        "identifier": identifier,
        "status": status if isinstance(status, str) else "implemented",
        "runtime": runtime,
        "sdk_owned": bool(contract.get("sdk_owned", True)),
        "top_level_keys": sorted(contract),
    }


def _surface_contract_status_index(rows: list[SurfaceContractSummaryRow]) -> dict[str, list[SurfaceContractIdentifier]]:
    (status_index,) = api_value_indexes(rows, "status", value_field="identifier")
    return cast(dict[str, list[SurfaceContractIdentifier]], status_index)


def get_surface_contract_summary() -> SurfaceContractSummary:
    """Return a compact table projection for the static surface catalog.

    Returns:
        JSON-safe summary payload with ordered surface rows, index positions,
        status indexes, and status/sdk-ownership counts.
    """

    contracts = get_surface_contracts()
    rows = [_surface_contract_summary_row(identifier, contracts[identifier]) for identifier in get_surface_contract_ids()]
    status_index = _surface_contract_status_index(rows)
    status_counts: dict[str, int] = {}
    for status, identifiers in status_index.items():
        status_counts[status] = len(identifiers)
    return {
        "schema": SURFACE_CONTRACT_SUMMARY_SCHEMA,
        "surface_count": len(rows),
        "sdk_owned_count": sum(1 for row in rows if row["sdk_owned"]),
        "status_counts": status_counts,
        "status_index": status_index,
        "index": {row["identifier"]: index for index, row in enumerate(rows)},
        "rows": rows,
    }


def get_surface_contract_status_ids(status: str) -> list[SurfaceContractIdentifier]:
    """Return static surface identifiers assigned to one contract status.

    Args:
        status: Surface contract status such as `implemented` or `scaffold`.

    Returns:
        Copied ordered list of stable surface identifiers with that status.

    Raises:
        KeyError: If the status is not present in the static surface contract catalog.
    """

    status_index = get_surface_contract_summary()["status_index"]
    try:
        return list(status_index[status])
    except KeyError as error:
        known = ", ".join(status_index)
        raise KeyError(f"unknown ParaDev surface contract status {status!r}; expected one of: {known}") from error


def get_surface_contract_summary_row(identifier: str) -> SurfaceContractSummaryRow:
    """Return one compact static surface contract summary row.

    Args:
        identifier: Stable surface identifier.

    Returns:
        Compact summary row for the requested surface.

    Raises:
        KeyError: If the identifier is not part of the static surface contract catalog.
    """

    surface, builder = _surface_contract_builder(identifier)
    return _surface_contract_summary_row(surface, dict(builder()))


def get_surface_contracts() -> dict[str, SurfaceContractPayload]:
    """Return static surface contracts keyed by stable surface identifier.

    Returns:
        Fresh contract payloads for the bundle, CLI, LSP, MCP, OpenAPI, and VS Code surfaces.
    """

    return {identifier: dict(builder()) for identifier, builder in _SURFACE_CONTRACT_BUILDERS}


def get_surface_contract(identifier: str) -> SurfaceContractPayload:
    """Return one static surface contract payload.

    Args:
        identifier: Stable surface identifier.

    Returns:
        Fresh contract payload for the requested surface.

    Raises:
        KeyError: If the identifier is not part of the static surface contract catalog.
    """

    _surface, builder = _surface_contract_builder(identifier)
    return dict(builder())


def render_surface_contract_reference_markdown() -> str:
    """Render the static surface contract catalog as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/surface-contract-reference.md`. The content is
        generated from `get_surface_contract_summary()` so public docs stay
        aligned with the SDK-owned surface catalog.
    """

    summary = get_surface_contract_summary()
    return api_reference_markdown(
        title="Surface Contract Reference",
        source="paradev.surfaces.get_surface_contract_summary()",
        regenerate_when="Regenerate this file whenever the static surface contract catalog changes:",
        command="rtk uv run paradev architecture --surface-contracts-markdown > docs/user-manual/surface-contract-reference.md",
        sections=api_summary_reference_sections(
            [
                f"- Surfaces / Surface 数: {summary['surface_count']}",
                f"- SDK-owned / SDK 拥有: {summary['sdk_owned_count']}",
            ],
            (
                api_table_section(
                    "Index Catalog / Index 目录",
                    ("Index", "Contract Path", "Python Helper", "Use"),
                    _surface_contract_index_catalog_table_rows(),
                ),
                api_table_section(
                    "Status Index / Status 索引",
                    ("Status", "Surfaces", "Surface IDs"),
                    _surface_contract_status_index_table_rows(summary),
                ),
                api_table_section(
                    "Surface Contracts / Surface Contract 表",
                    ("Surface", "Status", "Runtime", "SDK-owned", "Top-Level Keys"),
                    _surface_contract_reference_table_rows(summary),
                ),
            ),
        ),
    )


def _surface_contract_index_catalog_table_rows() -> list[str]:
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
        for row in get_surface_contract_index_catalog()
    ]


def _surface_contract_status_index_table_rows(summary: SurfaceContractSummary) -> list[str]:
    return [index_row(status, identifiers) for status, identifiers in summary["status_index"].items()]


def _surface_contract_reference_table_rows(summary: SurfaceContractSummary) -> list[str]:
    return [
        "| "
        + " | ".join(
            [
                code_cell(row["identifier"]),
                code_cell(row["status"]),
                code_cell(row["runtime"]),
                markdown_cell("yes" if row["sdk_owned"] else "no"),
                code_list_cell(row["top_level_keys"]),
            ]
        )
        + " |"
        for row in summary["rows"]
    ]


__all__ = [
    "API_CATALOG_INDEX_CATALOG",
    "API_CATALOG_SCHEMA",
    "API_CATALOG_SOURCE_ROWS",
    "SURFACES_API_TABLE_SCHEMA",
    "SURFACE_CONTRACT_IDS",
    "SURFACE_CONTRACT_INDEX_CATALOG",
    "SURFACE_CONTRACT_SUMMARY_SCHEMA",
    "ApiCatalogIndexCatalogRow",
    "ApiCatalogReferenceGroupRow",
    "ApiCatalogRow",
    "ApiCatalogSourceRow",
    "ApiCatalogSummary",
    "ApiCatalogTable",
    "SurfacesApiRow",
    "SurfacesApiTable",
    "SurfaceContractIdentifier",
    "SurfaceContractIndexCatalogRow",
    "SurfaceContractPayload",
    "SurfaceContractSummary",
    "SurfaceContractSummaryRow",
    "get_api_catalog_group_reference_ids",
    "get_api_catalog_reference_group",
    "get_api_catalog_reference_groups",
    "get_api_catalog_index_catalog",
    "get_api_catalog_reference",
    "get_api_catalog_reference_ids",
    "get_api_catalog_selection",
    "get_api_catalog_summary",
    "get_api_catalog_table",
    "get_bundle_contract",
    "get_cli_api_table",
    "get_cli_contract",
    "get_lsp_contract",
    "get_mcp_api_selection",
    "get_mcp_api_table",
    "get_mcp_contract",
    "get_openapi_seed",
    "get_rest_api_selection",
    "get_rest_api_table",
    "get_surface_contract",
    "get_surface_contract_ids",
    "get_surface_contract_index_catalog",
    "get_surface_contract_selection",
    "get_surface_contract_summary",
    "get_surface_contract_summary_row",
    "get_surface_contract_status_ids",
    "get_surface_contracts",
    "get_surfaces_api_selection",
    "get_surfaces_api_table",
    "get_vscode_contract",
    "render_api_catalog_reference_markdown",
    "render_cli_api_reference_markdown",
    "render_mcp_api_reference_markdown",
    "render_rest_api_reference_markdown",
    "render_surface_contract_reference_markdown",
    "render_surfaces_api_reference_markdown",
]
