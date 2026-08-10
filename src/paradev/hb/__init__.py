"""HeavenBase-facing catalog preview helpers."""

from __future__ import annotations

import inspect
import json
import logging
import os
import re
import sqlite3
import stat
from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

import heavenbase as hb
from heavenbase.execution import RowOp
from heavenbase.utils import delete_file, dumps_json, path_to_file_uri, sha256hash
from typing_extensions import TypedDict

from paradev._api_table import api_symbol_indexes, api_table_selection
from paradev._api_table_markdown import api_surface_reference_markdown
from paradev._catalog import CATALOG_QUERY_DEFAULT_INCLUDE_DATA, CATALOG_QUERY_DEFAULT_LIMIT, CATALOG_QUERY_DEFAULT_OFFSET
from paradev.hb.api import HB_API_TABLE_SCHEMA, HbApiRow, HbApiTable, get_hb_api_selection, get_hb_api_table, render_hb_api_reference_markdown
from paradev.hb.hoi4 import (
    HOI4_ENTITY_TYPES,
    HOI4_EXTENSION_ID,
    PDX_SYMBOL_DATA_FIELDS,
    PDX_SYMBOL_FIELD_STORAGE,
    entity_table,
    entity_type_from_identifier,
    hoi4_entities,
    normalize_entity_identifier,
    register_hoi4_extension,
)
from paradev.pdx import PDXBlock, PDXEntry, PDXScalar

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from paradev.build import Artifact, BuildRegistry, BuildResult, Collection, Module
    from paradev.sdk import Project

CATALOG_SCHEMA = "paradev.hb.catalog-preview.v1"
SMOKE_SCHEMA = "paradev.hb.catalog-smoke.v1"
WRITE_SCHEMA = "paradev.hb.catalog-write.v1"
REFRESH_SCHEMA = "paradev.hb.catalog-refresh.v1"
QUERY_SCHEMA = "paradev.hb.catalog-query.v1"
STATUS_SCHEMA = "paradev.hb.catalog-status.v1"
_CATALOG_MUTATION_SCHEMA = "paradev.hb.catalog-mutation.v1"
CATALOG_API_TABLE_SCHEMA = "paradev.hb.catalog-api-table.v1"
_CATALOG_API_INDEX_NAMES = ("surface_index", "feature_index")
_CATALOG_API_STANDARD_FIELDS = (
    "symbol",
    "kind",
    "layer",
    "feature",
    "surface",
    "inputs",
    "returns",
    "raises",
    "registry_seam",
    "payload_schema",
    "doc_page",
    "test_anchor",
)
_FRESH_BULK_UPSERT_THRESHOLD = 1_000
_FRESH_BULK_UPSERT_CHUNK_SIZE = 1_000
_CATALOG_MUTATION_LOCK_TIMEOUT_SECONDS = 30 * 60
_CATALOG_STALE_SCHEMA = "paradev.hb.catalog-stale.v1"
ENTITY_TYPES = (*HOI4_ENTITY_TYPES,)
_COMPLETION_KIND_CLASS = 7
_COMPLETION_KIND_PROPERTY = 10
_COMPLETION_KIND_VALUE = 12
_COMPLETION_KIND_REFERENCE = 18
_CATALOG_COMPLETION_CACHE_SIZE = 8
_CATALOG_API_REFERENCE_PAGE = "docs/user-manual/catalog-api-reference.md"
_CATALOG_API_TEST_ANCHOR = "tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces"


class CatalogApiRow(TypedDict):
    """One public HeavenBase catalog API table row."""

    symbol: str
    kind: str
    layer: str
    feature: str
    inputs: str
    returns: str
    raises: str
    registry_seam: str
    surface: str
    payload_schema: str
    doc_page: str
    test_anchor: str


class CatalogApiTable(TypedDict):
    """Generated API-standard table for HeavenBase catalog surfaces."""

    schema: str
    row_count: int
    surface_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    rows: list[CatalogApiRow]


CATALOG_API_TABLE_ROWS: tuple[CatalogApiRow, ...] = (
    {
        "symbol": "CATALOG_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "preview",
        "inputs": "none",
        "returns": CATALOG_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": CATALOG_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "SMOKE_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "smoke",
        "inputs": "none",
        "returns": SMOKE_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": SMOKE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "WRITE_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "write",
        "inputs": "none",
        "returns": WRITE_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": WRITE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "REFRESH_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "refresh",
        "inputs": "none",
        "returns": REFRESH_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": REFRESH_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "QUERY_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "query",
        "inputs": "none",
        "returns": QUERY_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": QUERY_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "STATUS_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "status",
        "inputs": "none",
        "returns": STATUS_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": STATUS_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_status_missing_is_side_effect_free",
    },
    {
        "symbol": "CATALOG_API_TABLE_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": CATALOG_API_TABLE_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "CATALOG_API_TABLE_ROWS",
        "kind": "constant",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "tuple[CatalogApiRow, ...]",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "CatalogApiRow",
        "kind": "TypedDict",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "symbol, kind, layer, feature, inputs, returns, raises, registry_seam, surface, payload_schema, doc_page, test_anchor",
        "returns": "Catalog API table row schema",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "CatalogApiTable",
        "kind": "TypedDict",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "schema, row_count, surface_index, feature_index, rows",
        "returns": "Catalog API table schema",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "get_catalog_api_selection",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "CatalogApiTable | CatalogApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_catalog_api_selection.py::test_catalog_api_selection_returns_table_row_and_index_projection",
    },
    {
        "symbol": "ENTITY_TYPES",
        "kind": "constant",
        "layer": "sdk",
        "feature": "entities",
        "inputs": "none",
        "returns": "tuple[str, ...]",
        "raises": "",
        "registry_seam": "HOI4 HeavenBase extension registry",
        "surface": "sdk",
        "payload_schema": CATALOG_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "catalog_preview",
        "kind": "function",
        "layer": "sdk",
        "feature": "preview",
        "inputs": "project, profile=None, registry=None, result=None",
        "returns": "catalog preview payload",
        "raises": "",
        "registry_seam": "Project build registry",
        "surface": "sdk",
        "payload_schema": CATALOG_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_preview_projects_build_rows_without_writing",
    },
    {
        "symbol": "catalog_smoke",
        "kind": "function",
        "layer": "sdk",
        "feature": "smoke",
        "inputs": "project, profile=None, registry=None, preview=None",
        "returns": "catalog smoke payload",
        "raises": "",
        "registry_seam": "HeavenBase in-memory workspace",
        "surface": "sdk",
        "payload_schema": SMOKE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_smoke_registers_preview_rows_without_writing",
    },
    {
        "symbol": "catalog_write",
        "kind": "function",
        "layer": "sdk",
        "feature": "write",
        "inputs": "project, profile=None, registry=None, preview=None, database=None",
        "returns": "catalog write payload",
        "raises": "FileExistsError on existing database path",
        "registry_seam": "HeavenBase SQLite backend",
        "surface": "sdk",
        "payload_schema": WRITE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_write_creates_sqlite_database_without_build_output",
    },
    {
        "symbol": "catalog_refresh",
        "kind": "function",
        "layer": "sdk",
        "feature": "refresh",
        "inputs": "project, profile=None, registry=None, preview=None, database=None",
        "returns": "catalog refresh payload",
        "raises": "OSError on database replacement failure",
        "registry_seam": "HeavenBase SQLite backend",
        "surface": "sdk",
        "payload_schema": REFRESH_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_refresh_replaces_existing_database_files",
    },
    {
        "symbol": "catalog_query",
        "kind": "function",
        "layer": "sdk",
        "feature": "query",
        "inputs": ("project, database=None, entity=None, target_id=None, name=None, tag=None, " "limit=None, offset=0, include_data=True"),
        "returns": "catalog query payload",
        "raises": ("FileNotFoundError on missing database; RuntimeError on stale database; " "ValueError on invalid paging arguments"),
        "registry_seam": "HeavenBase SQLite catalog",
        "surface": "sdk",
        "payload_schema": QUERY_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_query_reads_written_sqlite_catalog",
    },
    {
        "symbol": "catalog_status",
        "kind": "function",
        "layer": "sdk",
        "feature": "status",
        "inputs": "project, database=None",
        "returns": "catalog status payload",
        "raises": "",
        "registry_seam": "HeavenBase SQLite catalog",
        "surface": "sdk",
        "payload_schema": STATUS_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_status_missing_is_side_effect_free",
    },
    {
        "symbol": "catalog_completion_items",
        "kind": "function",
        "layer": "sdk",
        "feature": "completion",
        "inputs": "project, database=None, prefix=None, limit=100",
        "returns": "LSP CompletionItem rows",
        "raises": "FileNotFoundError on missing database; RuntimeError on stale database; ValueError on non-positive limit",
        "registry_seam": "HeavenBase SQLite catalog",
        "surface": "sdk",
        "payload_schema": "LSP CompletionItem[]",
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_lsp.py::test_catalog_completion_reuses_cached_database_rows",
    },
    {
        "symbol": "get_catalog_api_table",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "CatalogApiTable",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "render_catalog_api_reference_markdown",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "Markdown catalog API reference",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": _CATALOG_API_TEST_ANCHOR,
    },
    {
        "symbol": "paradev catalog-api",
        "kind": "command",
        "layer": "cli",
        "feature": "api-table",
        "inputs": "--json",
        "returns": "CatalogApiTable",
        "raises": "typer.BadParameter when combined selectors are invalid",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_cli.py::test_catalog_api_cli_outputs_table_json",
    },
    {
        "symbol": "paradev catalog-api --markdown",
        "kind": "command projection",
        "layer": "cli",
        "feature": "api-table",
        "inputs": "none",
        "returns": "Markdown catalog API reference",
        "raises": "typer.BadParameter when combined with --json",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_cli.py::test_catalog_api_cli_outputs_reference_markdown",
    },
    {
        "symbol": "paradev hb catalog-preview",
        "kind": "command",
        "layer": "cli",
        "feature": "preview",
        "inputs": "path, --profile, --json",
        "returns": "catalog preview payload",
        "raises": "typer.BadParameter on project load failure",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": CATALOG_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_preview_cli_outputs_json",
    },
    {
        "symbol": "paradev hb catalog-smoke",
        "kind": "command",
        "layer": "cli",
        "feature": "smoke",
        "inputs": "path, --profile, --json",
        "returns": "catalog smoke payload",
        "raises": "typer.BadParameter on project load failure",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": SMOKE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_smoke_cli_outputs_json",
    },
    {
        "symbol": "paradev hb catalog-write",
        "kind": "command",
        "layer": "cli",
        "feature": "write",
        "inputs": "path, --profile, --database, --json",
        "returns": "catalog write payload",
        "raises": "typer.BadParameter on project load or existing database failure",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": WRITE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_write_cli_outputs_json",
    },
    {
        "symbol": "paradev hb catalog-refresh",
        "kind": "command",
        "layer": "cli",
        "feature": "refresh",
        "inputs": "path, --profile, --database, --json",
        "returns": "catalog refresh payload",
        "raises": "typer.BadParameter on project load or replacement failure",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": REFRESH_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_refresh_cli_outputs_json",
    },
    {
        "symbol": "paradev hb catalog-query",
        "kind": "command",
        "layer": "cli",
        "feature": "query",
        "inputs": (
            "path, --database, --entity, --target-id, --name, --tag, "
            f"--limit={CATALOG_QUERY_DEFAULT_LIMIT}, --offset={CATALOG_QUERY_DEFAULT_OFFSET}, "
            f"--data={str(CATALOG_QUERY_DEFAULT_INCLUDE_DATA).lower()}, --json"
        ),
        "returns": "catalog query payload",
        "raises": "typer.BadParameter on project load, missing or stale database, or invalid paging",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": QUERY_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_hb.py::test_hb_catalog_query_cli_outputs_json",
    },
    {
        "symbol": "GET /projects/inspect?kind=catalog-preview",
        "kind": "REST route",
        "layer": "rest",
        "feature": "preview",
        "inputs": "path, kind=catalog-preview, profile=None",
        "returns": "catalog preview payload",
        "raises": "",
        "registry_seam": "OpenAPI path /projects/inspect",
        "surface": "rest",
        "payload_schema": CATALOG_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "GET /projects/inspect?kind=catalog-query",
        "kind": "REST route",
        "layer": "rest",
        "feature": "query",
        "inputs": (
            "path, kind=catalog-query, database=None, entity=None, target_id=None, name=None, tag=None, "
            f"limit={CATALOG_QUERY_DEFAULT_LIMIT}, offset={CATALOG_QUERY_DEFAULT_OFFSET}, "
            f"include_data={str(CATALOG_QUERY_DEFAULT_INCLUDE_DATA).lower()}"
        ),
        "returns": "catalog query payload",
        "raises": "HTTP 400 on missing or stale database or invalid bounded paging",
        "registry_seam": "OpenAPI path /projects/inspect",
        "surface": "rest",
        "payload_schema": QUERY_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces",
    },
    {
        "symbol": "GET /projects/catalog",
        "kind": "REST route",
        "layer": "rest",
        "feature": "status",
        "inputs": "path",
        "returns": "catalog status payload",
        "raises": "",
        "registry_seam": "OpenAPI path /projects/catalog",
        "surface": "rest",
        "payload_schema": STATUS_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_native_web_bridge.py::test_native_web_bridge_catalog_status_uses_the_read_only_project_resource",
    },
    {
        "symbol": "POST /projects/catalog",
        "kind": "REST route",
        "layer": "rest",
        "feature": "write",
        "inputs": "path, profile=None, database=None",
        "returns": "catalog write payload",
        "raises": "",
        "registry_seam": "OpenAPI path /projects/catalog",
        "surface": "rest",
        "payload_schema": WRITE_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_hb.py::test_hb_catalog_write_and_refresh_rest_routes_output_json",
    },
    {
        "symbol": "PUT /projects/catalog",
        "kind": "REST route",
        "layer": "rest",
        "feature": "refresh",
        "inputs": "path, profile=None, database=None",
        "returns": "catalog refresh payload",
        "raises": "",
        "registry_seam": "OpenAPI path /projects/catalog",
        "surface": "rest",
        "payload_schema": REFRESH_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_hb.py::test_hb_catalog_write_and_refresh_rest_routes_output_json",
    },
    {
        "symbol": "GET /catalog-api",
        "kind": "REST route",
        "layer": "rest",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "CatalogApiTable | CatalogApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "OpenAPI path /catalog-api",
        "surface": "rest",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_catalog_api_surface_selectors.py::test_catalog_api_table_lists_rest_and_mcp_selector_surfaces",
    },
    {
        "symbol": "project_inspect kind=catalog-preview",
        "kind": "MCP tool projection",
        "layer": "mcp",
        "feature": "preview",
        "inputs": "path, kind=catalog-preview, profile=None",
        "returns": "catalog preview payload",
        "raises": "",
        "registry_seam": "MCP project_inspect dispatcher",
        "surface": "mcp",
        "payload_schema": CATALOG_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces",
    },
    {
        "symbol": "project_inspect kind=catalog-query",
        "kind": "MCP tool projection",
        "layer": "mcp",
        "feature": "query",
        "inputs": (
            "path, kind=catalog-query, database=None, entity=None, target_id=None, name=None, tag=None, "
            f"limit={CATALOG_QUERY_DEFAULT_LIMIT}, offset={CATALOG_QUERY_DEFAULT_OFFSET}, "
            f"include_data={str(CATALOG_QUERY_DEFAULT_INCLUDE_DATA).lower()}"
        ),
        "returns": "catalog query payload",
        "raises": "FileNotFoundError or RuntimeError on missing or stale database; ValueError on invalid bounded paging",
        "registry_seam": "MCP project_inspect dispatcher",
        "surface": "mcp",
        "payload_schema": QUERY_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces",
    },
    {
        "symbol": "catalog_api",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "CatalogApiTable | CatalogApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "payload_schema": CATALOG_API_TABLE_SCHEMA,
        "doc_page": _CATALOG_API_REFERENCE_PAGE,
        "test_anchor": "tests/test_catalog_api_surface_selectors.py::test_catalog_api_table_lists_rest_and_mcp_selector_surfaces",
    },
)


def get_catalog_api_table() -> CatalogApiTable:
    """Return the API-standard table for HeavenBase catalog surfaces.

    Returns:
        JSON-safe API table with copied rows, plus grouped indexes for surface
        and feature audits.
    """

    rows = [dict(row) for row in CATALOG_API_TABLE_ROWS]
    surface_index, feature_index = api_symbol_indexes(rows, "surface", "feature")
    return {
        "schema": CATALOG_API_TABLE_SCHEMA,
        "row_count": len(rows),
        "surface_index": surface_index,
        "feature_index": feature_index,
        "rows": rows,
    }


def get_catalog_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> CatalogApiTable | CatalogApiRow | list[str]:
    """Return the full catalog API table, one row, or one index bucket.

    Args:
        symbol: Optional public symbol to select from the table rows.
        index_name: Optional index name, such as `surface_index` or
            `feature_index`.
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
        CatalogApiTable | CatalogApiRow | list[str],
        api_table_selection(
            get_catalog_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_CATALOG_API_INDEX_NAMES,
        ),
    )


def render_catalog_api_reference_markdown() -> str:
    """Render the HeavenBase catalog API table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/catalog-api-reference.md`. The content is generated
        from `get_catalog_api_table()` so SDK, CLI, REST, MCP, and catalog
        completion seams stay aligned.
    """

    table = get_catalog_api_table()
    return api_surface_reference_markdown(
        title="Catalog API Reference",
        source="paradev.hb.get_catalog_api_table()",
        regenerate_when="Regenerate this file whenever the Catalog API table changes:",
        command="rtk uv run paradev catalog-api --markdown > docs/user-manual/catalog-api-reference.md",
        table=table,
        fields=_CATALOG_API_STANDARD_FIELDS,
    )


def catalog_completion_items(
    project: "Project",
    *,
    database: str | Path | None = None,
    prefix: str | None = None,
    limit: int | None = 100,
) -> list[dict[str, object]]:
    """Return LSP completion items from a written HeavenBase catalog.

    Args:
        project: Loaded ParaDev project.
        database: Optional SQLite catalog path. Defaults to
            `.paradev/.cache/hb/catalog.sqlite` under the project root.
        prefix: Optional case-insensitive label prefix filter.
        limit: Optional maximum item count. Defaults to 100; pass ``None``
            explicitly to request every matching completion.

    Returns:
        JSON-safe LSP `CompletionItem` rows derived from persisted catalog
        entities.

    Raises:
        FileNotFoundError: If the SQLite catalog database does not exist.
        RuntimeError: If newer project sources invalidated the Catalog.
        ValueError: If the row limit is not positive.
    """

    if limit is not None and limit < 1:
        raise ValueError("Catalog completion limit must be a positive integer.")
    database_path = _catalog_database_path(project, database)
    if not database_path.exists():
        raise FileNotFoundError(f"HeavenBase catalog database does not exist: {database_path}")
    _require_current_catalog(database_path)

    normalized_prefix = prefix.lower() if prefix else ""
    if limit is None or any(sidecar.exists() for sidecar in _database_sidecars(database_path)):
        return _query_catalog_completion_items(database_path, prefix=normalized_prefix, limit=limit)
    cache_key = (*_catalog_completion_cache_key(database_path), normalized_prefix, limit)
    return [deepcopy(item) for item in _cached_catalog_completion_items(*cache_key)]


def catalog_status(
    project: "Project",
    *,
    database: str | Path | None = None,
) -> dict[str, object]:
    """Return the filesystem status of a project's local Catalog database.

    This inspection is read-only. It does not create project state, acquire a
    refresh lock, open SQLite, or build the project.

    Args:
        project: Loaded ParaDev project.
        database: Optional SQLite catalog path. Defaults to
            `.paradev/.cache/hb/catalog.sqlite` under the project root.

    Returns:
        JSON-safe Catalog status with the project id, resolved database path,
        and one stable status/code pair.
    """

    database_path = _catalog_database_path(project, database)
    states = tuple(_catalog_path_state(path) for path in (database_path, *_database_sidecars(database_path)))
    stale_state = _catalog_path_state(_catalog_stale_path(database_path))
    if "unreadable" in (*states, stale_state):
        status, code = "unreadable", "catalog.unreadable"
    elif stale_state != "missing" or "incomplete" in states or (states[0] == "missing" and any(state != "missing" for state in states[1:])):
        status, code = "incomplete", "catalog.incomplete"
    elif states[0] == "missing":
        status, code = "missing", "catalog.missing"
    else:
        status, code = "present", "catalog.present"
    return {
        "schema": STATUS_SCHEMA,
        "project_id": project.project_id,
        "database": str(database_path),
        "status": status,
        "code": code,
    }


def _paradev_context() -> hb.Context:
    """Return the isolated HeavenBase Context owned by ParaDev."""

    from paradev.config import _CONTEXT_PARADEV

    return _CONTEXT_PARADEV


def _detached_workspace(
    workspace_id: str,
    *,
    backends: Mapping[str, object],
) -> hb.HeavenBase:
    """Create a caller-owned workspace through HeavenBase's public lifecycle."""

    return hb.HeavenBase(
        workspace_id,
        context=_paradev_context(),
        backends=backends,
        detached=True,
    )


def _sync_module_catalog_projection(
    project: "Project",
    *,
    previous: Mapping[str, object] | None = None,
    current: Mapping[str, object] | None = None,
    current_error: BaseException | None = None,
    _lock_held: bool = False,
) -> dict[str, object]:
    """Invalidate a persisted Catalog after one module source mutation.

    The source filesystem mutation has already succeeded when this private
    helper is called. A module edit can change modules, HOI4 entities,
    localization, PDX symbols, source rows, graph rows, and artifacts together.
    ParaDev therefore marks the complete derived Catalog stale instead of
    claiming that a module-only row delta synchronized those dependent views.

    Catalog invalidation is returned as the existing additive failed-mutation
    payload so current desktop clients retain an actionable refresh warning
    without confusing source-side success with Catalog coherence.
    """

    if previous is None and current is None and current_error is None:
        raise ValueError("Module Catalog invalidation requires a previous/current module row or projection error.")
    database = _catalog_database_path(project, None)
    if not _lock_held:
        status = catalog_status(project)
        lock_path = _catalog_refresh_lock_path(database)
        if status["status"] == "missing" and not lock_path.exists():
            return _catalog_mutation_payload(database, "not_configured")
        if status["status"] != "present" and not lock_path.exists():
            return _catalog_mutation_payload(
                database,
                "failed",
                message=_catalog_refresh_required_message(f"Catalog status is {status['status']} ({status['code']})."),
            )

    try:
        if _lock_held:
            return _invalidate_module_catalog(project, database, current_error=current_error)
        with _catalog_refresh_lock(database, timeout=_CATALOG_MUTATION_LOCK_TIMEOUT_SECONDS):
            return _invalidate_module_catalog(project, database, current_error=current_error)
    except Exception as error:
        message = str(error).strip()
        detail = f"{type(error).__name__}: {message}" if message else type(error).__name__
        return _catalog_mutation_payload(database, "failed", message=detail)


def _invalidate_module_catalog(
    project: "Project",
    database: Path,
    *,
    current_error: BaseException | None,
) -> dict[str, object]:
    """Mark one configured Catalog stale while its writer lock is held."""

    locked_status = catalog_status(project)
    if locked_status["status"] == "missing":
        return _catalog_mutation_payload(database, "not_configured")
    stale_state = _catalog_path_state(_catalog_stale_path(database))
    if locked_status["status"] != "present" and stale_state == "missing":
        return _catalog_mutation_payload(
            database,
            "failed",
            message=_catalog_refresh_required_message(f"Catalog status is {locked_status['status']} ({locked_status['code']})."),
        )

    _mark_catalog_stale(database)
    detail: str | None = None
    if current_error is not None:
        message = str(current_error).strip()
        error_text = f"{type(current_error).__name__}: {message}" if message else type(current_error).__name__
        detail = f"Written module could not be materialized after the source mutation ({error_text})."
    return _catalog_mutation_payload(
        database,
        "failed",
        message=_catalog_refresh_required_message(detail),
    )


def _catalog_mutation_payload(
    database: Path,
    status: str,
    *,
    message: str | None = None,
) -> dict[str, object]:
    codes = {
        "applied": "catalog.mutation.applied",
        "not_configured": "catalog.mutation.not_configured",
        "failed": "catalog.mutation.failed",
    }
    if status not in codes:
        raise ValueError(f"Unsupported Catalog mutation status: {status!r}.")
    payload: dict[str, object] = {
        "schema": _CATALOG_MUTATION_SCHEMA,
        "status": status,
        "code": codes[status],
        "database": str(database),
    }
    if status == "failed" and message:
        payload["message"] = message
    return payload


def catalog_query(
    project: "Project",
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
    """Read catalog rows from a written SQLite HeavenBase database.

    Args:
        project: Loaded ParaDev project.
        database: Optional SQLite catalog path. Defaults to
            `.paradev/.cache/hb/catalog.sqlite` under the project root.
        entity: Optional Catalog target entity filter. Accepts either
            `pdx-symbol` or `hoi4-pdx-symbol` style identifiers.
        target_id: Optional exact target object identifier filter.
        name: Optional case-insensitive substring filter over Catalog names.
        tag: Optional exact tag filter.
        limit: Optional maximum row count.
        offset: Number of matching rows to skip before returning the page.
        include_data: Whether to hydrate target payloads for returned rows.

    Returns:
        JSON-safe query result.

    Raises:
        FileNotFoundError: If the SQLite catalog database does not exist.
        RuntimeError: If newer project sources invalidated the Catalog.
        ValueError: If paging arguments are invalid.
    """

    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 1):
        raise ValueError("Catalog query limit must be a positive integer.")
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("Catalog query offset must be a non-negative integer.")
    if not isinstance(include_data, bool):
        raise ValueError("Catalog query include_data must be a boolean.")
    database_path = _catalog_database_path(project, database)
    if not database_path.exists():
        raise FileNotFoundError(f"HeavenBase catalog database does not exist: {database_path}")
    _require_current_catalog(database_path)

    target_entity = _target_entity(entity) if entity else None
    filters = _query_filters(
        entity=target_entity,
        target_id=target_id,
        name=name,
        tag=tag,
        limit=limit,
        offset=offset,
        include_data=include_data,
    )
    total_count, filtered_count, rows = _query_catalog_rows(
        database_path,
        target_entity=target_entity,
        target_id=target_id,
        name=name,
        tag=tag,
        limit=limit,
        offset=offset,
        include_data=include_data,
    )

    has_more = offset + len(rows) < filtered_count
    return {
        "schema": QUERY_SCHEMA,
        "project_id": project.project_id,
        "database": str(database_path),
        "filters": filters,
        "total_count": total_count,
        "filtered_count": filtered_count,
        "count": len(rows),
        "data_included": include_data,
        "page": {
            "offset": offset,
            "limit": limit,
            "has_more": has_more,
            "next_offset": offset + len(rows) if has_more else None,
        },
        "rows": rows,
    }


def catalog_write(
    project: "Project",
    *,
    profile: str | None = None,
    registry: "BuildRegistry | None" = None,
    preview: Mapping[str, object] | None = None,
    database: str | Path | None = None,
) -> dict[str, object]:
    """Write catalog preview rows to a new local SQLite HeavenBase database.

    Args:
        project: Loaded ParaDev project.
        profile: Optional build profile. Defaults to the project game.
        registry: Optional build registry for tests and project-local previews.
        preview: Optional precomputed :func:`catalog_preview` payload.
        database: Optional SQLite database path. Defaults to
            `.paradev/.cache/hb/catalog.sqlite` under the project root.

    Returns:
        JSON-safe write summary with registered entity and Catalog counts.

    Raises:
        FileExistsError: If the target database, WAL, or SHM file exists.
    """

    database_path = _catalog_database_path(project, database)
    with _catalog_refresh_lock(database_path):
        return _catalog_write_unlocked(
            project,
            profile=profile,
            registry=registry,
            preview=preview,
            database=database_path,
        )


def _catalog_write_unlocked(
    project: "Project",
    *,
    profile: str | None,
    registry: "BuildRegistry | None",
    preview: Mapping[str, object] | None,
    database: Path,
) -> dict[str, object]:
    """Write one new Catalog while the caller owns its writer ordering."""

    database_path = database
    conflicts = _database_conflicts(database_path)
    if conflicts:
        raise FileExistsError(f"HeavenBase catalog database path already exists: {conflicts[0]}")
    payload = dict(preview) if preview is not None else None
    if payload is None:
        profile_id = profile or project.game
        build_registry = project._build_registry(profile=profile_id, registry=registry)
        build_result = project.build(profile=profile_id, registry=build_registry)
        profile_id = build_result.profile or profile_id
        workspace_id = _streaming_write_workspace_id(project.project_id, profile_id)
    else:
        workspace_id = _write_workspace_id(payload)
    _mark_catalog_stale(database_path)
    try:
        workspace = _detached_workspace(
            workspace_id,
            backends={"main": {"type": "sqlite", "database": path_to_file_uri(database_path)}},
        )
        summary = (
            _catalog_workspace_summary(payload, workspace)
            if payload is not None
            else _streaming_catalog_workspace_summary(
                project,
                profile=profile_id,
                registry=build_registry,
                result=build_result,
                workspace=workspace,
                database=database_path,
            )
        )
        if payload is None and not summary.get("ok"):
            raise RuntimeError("HeavenBase catalog materialization counts do not match the projected rows.")
        _ensure_catalog_query_indexes(database_path)
        _checkpoint_database_file(database_path)
        for sidecar in _database_sidecars(database_path):
            delete_file(sidecar)
    except BaseException:
        for cleanup in (
            lambda: _remove_database_files(database_path),
            lambda: _clear_catalog_stale(database_path),
        ):
            try:
                cleanup()
            except Exception as cleanup_error:
                logger.warning("Catalog write cleanup failed for %s: %s", database_path, cleanup_error)
        raise
    _clear_catalog_stale(database_path)
    return {"schema": WRITE_SCHEMA, **summary, "database": str(database_path)}


def catalog_refresh(
    project: "Project",
    *,
    profile: str | None = None,
    registry: "BuildRegistry | None" = None,
    preview: Mapping[str, object] | None = None,
    database: str | Path | None = None,
) -> dict[str, object]:
    """Replace the local SQLite HeavenBase catalog database.

    The replacement preview is computed and written to a sibling staging
    database before the final database is replaced, so a failed project build
    leaves the previous catalog intact.

    Args:
        project: Loaded ParaDev project.
        profile: Optional build profile. Defaults to the project game.
        registry: Optional build registry for tests and project-local previews.
        preview: Optional precomputed :func:`catalog_preview` payload.
        database: Optional SQLite database path. Defaults to
            `.paradev/.cache/hb/catalog.sqlite` under the project root.

    Returns:
        JSON-safe refresh summary with removed database paths and Catalog counts.
    """

    database_path = _catalog_database_path(project, database)
    payload = dict(preview) if preview is not None else None
    refresh_identity = payload or {
        "project_id": project.project_id,
        "game": project.game,
        "profile": profile or project.game,
    }
    with _catalog_refresh_lock(database_path):
        initial_conflicts = _database_conflicts(database_path)
        recovered = _remove_stale_refresh_databases(database_path)
        staging_path = _refresh_database_path(database_path, refresh_identity)
        _remove_database_files(staging_path)
        try:
            result = _catalog_write_unlocked(
                project,
                profile=profile,
                registry=registry,
                preview=payload,
                database=staging_path,
            )
            replaced_conflicts = _replace_database_file(staging_path, database_path)
            _clear_catalog_stale(database_path)
        finally:
            _remove_database_files(staging_path)
        return {
            "schema": REFRESH_SCHEMA,
            **{key: value for key, value in result.items() if key != "schema"},
            "database": str(database_path),
            "removed": [str(path) for path in dict.fromkeys([*initial_conflicts, *replaced_conflicts])],
            "recovered": [str(path) for path in recovered],
        }


def catalog_smoke(
    project: "Project",
    *,
    profile: str | None = None,
    registry: "BuildRegistry | None" = None,
    preview: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Validate catalog preview rows in an in-memory HeavenBase workspace.

    Args:
        project: Loaded ParaDev project.
        profile: Optional build profile. Defaults to the project game.
        registry: Optional build registry for tests and project-local previews.
        preview: Optional precomputed :func:`catalog_preview` payload.

    Returns:
        JSON-safe smoke summary with registered entity and Catalog counts.
    """

    payload = dict(preview or catalog_preview(project, profile=profile, registry=registry))
    workspace = _detached_workspace(
        _smoke_workspace_id(payload),
        backends={"main": {"type": "inmem"}},
    )
    return {"schema": SMOKE_SCHEMA, **_catalog_workspace_summary(payload, workspace)}


def _catalog_workspace_summary(payload: Mapping[str, object], workspace: hb.HeavenBase) -> dict[str, object]:
    register_hoi4_extension()
    extension_spec = workspace.enable_extension(HOI4_EXTENSION_ID)
    entity_classes = {entity_type: workspace.entities[normalize_entity_identifier(entity_type)] for entity_type in ENTITY_TYPES}

    entities = payload["entities"] if isinstance(payload.get("entities"), Mapping) else {}
    row_counts: dict[str, int] = {}
    for entity_type in ENTITY_TYPES:
        rows = entities.get(entity_type, ()) if isinstance(entities, Mapping) else ()
        normalized_rows = [_catalog_row(entity_type, row) for row in rows if isinstance(row, Mapping)]
        row_counts[entity_type] = len(normalized_rows)
        if normalized_rows:
            _upsert_catalog_rows(workspace, entity_classes[entity_type], normalized_rows)

    catalog_rows = workspace.query(hb.Catalog).execute().rows()
    catalog_counts: dict[str, int] = {}
    for row in catalog_rows:
        target_entity = str(row["target_entity"])
        catalog_counts[target_entity] = catalog_counts.get(target_entity, 0) + 1
    metaschema_entity_rows = workspace.query(hb.MetaSchema).where({"kind": "entity"}).execute().rows()
    return {
        "project_id": payload["project_id"],
        "game": payload["game"],
        "profile": payload["profile"],
        "workspace_id": workspace.id,
        "registered_entities": [entity_classes[entity_type].identifier for entity_type in ENTITY_TYPES],
        "enabled_extensions": {HOI4_EXTENSION_ID: extension_spec.to_dict()},
        "preview_counts": dict(payload["counts"]),
        "row_counts": row_counts,
        "catalog_count": len(catalog_rows),
        "catalog_counts": catalog_counts,
        "metaschema_entity_count": len(metaschema_entity_rows),
        "ok": row_counts == dict(payload["counts"]) and len(catalog_rows) == sum(row_counts.values()),
    }


def _streaming_catalog_workspace_summary(
    project: "Project",
    *,
    profile: str,
    registry: "BuildRegistry",
    result: "BuildResult",
    workspace: hb.HeavenBase,
    database: Path,
) -> dict[str, object]:
    from paradev.build import build_graph, source_slot_status
    from paradev.sdk.project import _project_browser_authoring_modules

    register_hoi4_extension()
    extension_spec = workspace.enable_extension(HOI4_EXTENSION_ID)
    entity_classes = {entity_type: workspace.entities[normalize_entity_identifier(entity_type)] for entity_type in ENTITY_TYPES}
    authoring_modules = _project_browser_authoring_modules(
        project,
        registry=registry,
        result=result,
        family=None,
        module_id=None,
        collection_id=None,
    )
    graph: Mapping[str, object] = {}
    source_slots: Mapping[str, object] = {}
    row_counts: dict[str, int] = {}
    for entity_type in ENTITY_TYPES:
        if entity_type == "build-graph-edge":
            graph = build_graph(result)
        elif entity_type == "source-slot":
            source_slots = source_slot_status(result, registry)
        rows = _streaming_catalog_entity_rows(
            project,
            profile=profile,
            result=result,
            graph=graph,
            source_slots=source_slots,
            authoring_modules=authoring_modules,
            entity_type=entity_type,
        )
        row_counts[entity_type] = _upsert_streaming_catalog_rows(workspace, entity_classes[entity_type], rows)
        if entity_type == "build-graph-node":
            graph = {}
        elif entity_type == "source-slot":
            source_slots = {}

    catalog_counts = _catalog_database_counts(database)
    catalog_count = sum(catalog_counts.values())
    expected_catalog_counts = {entity_classes[entity_type].identifier: count for entity_type, count in row_counts.items() if count}
    metaschema_entity_rows = workspace.query(hb.MetaSchema).where({"kind": "entity"}).execute().rows()
    return {
        "project_id": project.project_id,
        "game": project.game,
        "profile": profile,
        "workspace_id": workspace.id,
        "registered_entities": [entity_classes[entity_type].identifier for entity_type in ENTITY_TYPES],
        "enabled_extensions": {HOI4_EXTENSION_ID: extension_spec.to_dict()},
        "preview_counts": dict(row_counts),
        "row_counts": row_counts,
        "catalog_count": catalog_count,
        "catalog_counts": catalog_counts,
        "metaschema_entity_count": len(metaschema_entity_rows),
        "ok": catalog_counts == expected_catalog_counts and catalog_count == sum(row_counts.values()),
    }


def _streaming_catalog_entity_rows(
    project: "Project",
    *,
    profile: str,
    result: "BuildResult",
    graph: Mapping[str, object],
    source_slots: Mapping[str, object],
    authoring_modules: Sequence["Module"],
    entity_type: str,
) -> Iterable[Mapping[str, object]]:
    from paradev.build.manifest import manifest_rows

    if entity_type == "asset":
        return manifest_rows(result, "assets.json")
    if entity_type == "build-artifact":
        return _build_artifacts(result.artifacts)
    if entity_type == "build-dependency":
        return (dependency.to_dict() for dependency in result.dependencies)
    if entity_type == "build-graph-edge":
        return _build_graph_edges(graph.get("edges"))
    if entity_type == "build-graph-node":
        return _build_graph_nodes(graph.get("nodes"))
    if entity_type == "collection":
        return (collection.to_dict() for collection in result.collections)
    if entity_type == "diagnostic":
        return manifest_rows(result, "diagnostics.json")
    if entity_type == "hoi4-entity":
        return _iter_hoi4_entities(result.modules) if profile == "hoi4" else ()
    if entity_type == "loc-entry":
        return manifest_rows(result, "localization.json")
    if entity_type == "module":
        return _modules(authoring_modules)
    if entity_type == "pdx-document":
        return _iter_pdx_documents(result)
    if entity_type == "pdx-symbol":
        return _iter_pdx_symbols(result)
    if entity_type == "project":
        return (_project_row(project),)
    if entity_type == "source-file":
        return manifest_rows(result, "sources.json")
    if entity_type == "source-slot":
        return _source_slots(source_slots)
    if entity_type == "sprite":
        return manifest_rows(result, "sprites.json")
    raise ValueError(f"Unsupported streaming Catalog entity type: {entity_type!r}.")


def _upsert_streaming_catalog_rows(
    workspace: hb.HeavenBase,
    entity: type[hb.Entity],
    rows: Iterable[Mapping[str, object]],
) -> int:
    entity_cls = workspace.register(entity)
    count = 0
    chunk: list[dict[str, object]] = []
    for row in rows:
        chunk.append(_catalog_row(entity_cls.schema().entity_id.removeprefix("hoi4-"), row))
        if len(chunk) < _FRESH_BULK_UPSERT_CHUNK_SIZE:
            continue
        _write_fresh_catalog_chunk(workspace, entity_cls, chunk)
        count += len(chunk)
        chunk = []
    if chunk:
        _write_fresh_catalog_chunk(workspace, entity_cls, chunk)
        count += len(chunk)
    return count


def _catalog_database_counts(database: Path) -> dict[str, int]:
    uri = f"{database.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        rows = connection.execute("select target_entity, count(*) from sys_catalog group by target_entity order by target_entity").fetchall()
    return {str(target_entity): int(count) for target_entity, count in rows}


def _upsert_catalog_rows(workspace: hb.HeavenBase, entity: type[hb.Entity], rows: list[dict[str, object]]) -> None:
    if len(rows) < _FRESH_BULK_UPSERT_THRESHOLD:
        workspace.upsert_many(entity, rows)
        return
    _fresh_bulk_upsert_many(workspace, entity, rows)


def _fresh_bulk_upsert_many(workspace: hb.HeavenBase, entity: type[hb.Entity], rows: list[dict[str, object]]) -> None:
    entity_cls = workspace.register(entity)
    seen: set[tuple[str, str]] = set()
    for offset in range(0, len(rows), _FRESH_BULK_UPSERT_CHUNK_SIZE):
        chunk = [dict(row) for row in rows[offset : offset + _FRESH_BULK_UPSERT_CHUNK_SIZE]]
        object_ids = _write_fresh_catalog_chunk(workspace, entity_cls, chunk)
        for object_id in object_ids:
            key = (entity_cls.schema().entity_id, object_id)
            if key in seen:
                raise ValueError(f"{entity_cls.schema().entity_id} batch contains duplicate object_id {object_id!r}")
            seen.add(key)


def _write_fresh_catalog_chunk(
    workspace: hb.HeavenBase,
    entity_cls: type[hb.Entity],
    rows: Sequence[Mapping[str, object]],
) -> list[str]:
    """Publish one validated chunk without probing a known-empty database.

    This follows HeavenBase's registered-schema encoding and Catalog derivation
    path for ParaDev's flat, non-system HOI4 entities, but intentionally omits
    existing-row and graph-mutation lookups because ``catalog_write`` always
    targets a newly created database. Chunk-local duplicates are rejected before
    either entity or Catalog operations are committed.
    """

    if _heavenbase_fresh_catalog_mode_supported():
        public_upsert_many = cast(Any, workspace.upsert_many)
        return [str(object_id) for object_id in public_upsert_many(entity_cls, [dict(row) for row in rows], catalog_mode="fresh")]

    schema = entity_cls.schema()
    if schema.entity_id in workspace._catalog.system_entity_ids():
        raise ValueError(f"Fresh Catalog writes cannot target system entity {schema.entity_id!r}")
    catalog_schema = hb.Catalog.schema()
    object_ids: list[str] = []
    seen: set[str] = set()
    entity_ops: dict[str, list[RowOp]] = {}
    catalog_ops: dict[str, list[RowOp]] = {}
    for source_row in rows:
        data = dict(source_row)
        workspace._materializer.materialize(entity_cls, data)
        object_id = str(data[schema.pk_name])
        if object_id in seen:
            raise ValueError(f"{schema.entity_id} batch contains duplicate object_id {object_id!r}")
        seen.add(object_id)
        object_ids.append(object_id)
        for backend_name in workspace._row_store.routed_backend_names(schema.entity_id):
            encoded = workspace._row_codec.encode_for_backend(schema, backend_name, data)
            entity_ops.setdefault(backend_name, []).append(RowOp(schema.entity_id, object_id, encoded))
        catalog_row = workspace._catalog.row(entity_cls, schema, object_id, data, existing=None)
        catalog_id = str(catalog_row[catalog_schema.pk_name])
        for backend_name in workspace._row_store.routed_backend_names(catalog_schema.entity_id):
            catalog_ops.setdefault(backend_name, []).append(RowOp(catalog_schema.entity_id, catalog_id, catalog_row))
    workspace._writer.write_ops(entity_ops)
    workspace._writer.write_ops(catalog_ops)
    workspace._crud._invalidate_mcp_registry_metadata_if_needed([entity_cls])
    return object_ids


@lru_cache(maxsize=1)
def _heavenbase_fresh_catalog_mode_supported() -> bool:
    """Return whether the active HeavenBase owns fresh Catalog batch writes."""

    return "catalog_mode" in inspect.signature(hb.HeavenBase.upsert_many).parameters


def catalog_preview(
    project: "Project",
    *,
    profile: str | None = None,
    registry: "BuildRegistry | None" = None,
    result: "BuildResult | None" = None,
) -> dict[str, object]:
    """Return deterministic HeavenBase-ready rows without writing a workspace.

    Args:
        project: Loaded ParaDev project.
        profile: Optional build profile. Defaults to the project game.
        registry: Optional build registry for tests and project-local previews.
        result: Optional precomputed build result.

    Returns:
        JSON-safe catalog preview grouped by future HeavenBase entity type.
    """

    from paradev.build import build_graph, manifest_payloads, source_slot_status
    from paradev.sdk.project import _project_browser_authoring_modules

    profile_id = profile or project.game
    build_registry = project._build_registry(profile=profile_id, registry=registry)
    build_result = result or project.build(profile=profile_id, registry=build_registry)
    profile_id = build_result.profile or profile or project.game
    authoring_modules = _project_browser_authoring_modules(
        project,
        registry=build_registry,
        result=build_result,
        family=None,
        module_id=None,
        collection_id=None,
    )
    manifests = manifest_payloads(build_result)
    graph = build_graph(build_result)
    entities = {
        "asset": list(manifests["assets.json"]["assets"]),
        "build-artifact": _build_artifacts(build_result.artifacts),
        "build-dependency": [dependency.to_dict() for dependency in build_result.dependencies],
        "build-graph-edge": _build_graph_edges(graph.get("edges")),
        "build-graph-node": _build_graph_nodes(graph.get("nodes")),
        "collection": _collections(build_result.collections),
        "diagnostic": list(manifests["diagnostics.json"]["diagnostics"]),
        "hoi4-entity": _hoi4_entities(build_result.modules) if profile_id == "hoi4" else [],
        "loc-entry": list(manifests["localization.json"]["localization"]),
        "module": _modules(authoring_modules),
        "pdx-document": _pdx_documents(build_result),
        "pdx-symbol": _pdx_symbols(build_result),
        "project": [_project_row(project)],
        "source-file": _source_files(manifests["sources.json"].get("sources")),
        "source-slot": _source_slots(source_slot_status(build_result, build_registry)),
        "sprite": list(manifests["sprites.json"]["sprites"]),
    }
    return {
        "schema": CATALOG_SCHEMA,
        "project_id": project.project_id,
        "game": project.game,
        "profile": profile_id,
        "counts": {entity_type: len(entities[entity_type]) for entity_type in ENTITY_TYPES},
        "entities": {entity_type: entities[entity_type] for entity_type in ENTITY_TYPES},
    }


def _catalog_row(entity_type: str, row: Mapping[str, object]) -> dict[str, object]:
    data = _module_catalog_authoring_row(row) if entity_type == "module" else dict(row)
    if entity_type == "pdx-symbol":
        unsupported = sorted(set(data).difference(PDX_SYMBOL_DATA_FIELDS))
        if unsupported:
            raise ValueError(f"Unsupported pdx-symbol fields: {', '.join(unsupported)}")
        return {
            "object_id": _catalog_object_id(entity_type, data),
            **{storage_name: data.get(field_name) for field_name, storage_name in PDX_SYMBOL_FIELD_STORAGE},
        }
    return {
        "object_id": _catalog_object_id(entity_type, data),
        "name": _catalog_name(entity_type, data),
        "description": _catalog_desc(entity_type, data),
        "tags": _catalog_tags(entity_type, data),
        "data": data,
    }


def _module_catalog_authoring_row(row: Mapping[str, object]) -> dict[str, object]:
    data = dict(row)
    source_slots: dict[str, list[str]] = {}
    raw_source_slots = data.get("source_slots")
    if isinstance(raw_source_slots, Mapping):
        for slot, paths in raw_source_slots.items():
            if isinstance(slot, str) and isinstance(paths, Sequence) and not isinstance(paths, str | bytes):
                source_slots[slot] = [str(path) for path in paths]
    if source_slots.get("meta"):
        data["source_slots"] = source_slots
        return data
    root = data.get("root")
    if not isinstance(root, str | Path) or not str(root):
        data["source_slots"] = source_slots
        return data
    metadata_path = Path(root) / "meta.yaml"
    try:
        metadata_stat = metadata_path.lstat()
    except OSError:
        pass
    else:
        if stat.S_ISREG(metadata_stat.st_mode):
            source_slots["meta"] = ["meta.yaml"]
    data["source_slots"] = source_slots
    return data


def _catalog_object_id(entity_type: str, row: Mapping[str, object]) -> str:
    digest = sha256hash(dumps_json(row, sort_keys=True, compact=True))[:16]
    return f"{entity_type}:{digest}"


def _catalog_name(entity_type: str, row: Mapping[str, object]) -> str:
    if entity_type == "source-slot":
        owner = row.get("module_id") or row.get("collection_id")
        slot = row.get("slot")
        if isinstance(owner, str) and owner and isinstance(slot, str) and slot:
            return f"{owner}:{slot}"
    for key in _name_keys(entity_type):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return entity_type


def _catalog_desc(entity_type: str, row: Mapping[str, object]) -> str:
    for key in ("path", "text", "message", "desc", "description"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _catalog_tags(entity_type: str, row: Mapping[str, object]) -> list[str]:
    tags = [entity_type]
    for key in ("family", "module_id", "collection_id", "slot", "owner_kind", "status"):
        value = row.get(key)
        if isinstance(value, str) and value:
            tags.append(value)
    for key in ("module_ids", "collection_ids"):
        values = row.get(key)
        if isinstance(values, Sequence) and not isinstance(values, str | bytes):
            tags.extend(value for value in values if isinstance(value, str))
    if entity_type == "build-graph-edge":
        for key in ("kind", "source", "target"):
            value = row.get(key)
            if isinstance(value, str) and value:
                tags.append(value)
    if entity_type == "build-graph-node":
        value = row.get("type")
        if isinstance(value, str) and value:
            tags.append(value)
    if entity_type == "source-file":
        tags.extend(_source_file_tags(row))
    source_tags = row.get("tags")
    if isinstance(source_tags, Sequence) and not isinstance(source_tags, str | bytes):
        tags.extend(tag for tag in source_tags if isinstance(tag, str))
    return list(dict.fromkeys(tags))


def _source_file_tags(row: Mapping[str, object]) -> list[str]:
    tags: list[str] = []
    for key in ("owner_kind", "family", "slot", "loader", "status"):
        value = row.get(key)
        if isinstance(value, str) and value:
            tag_key = "owner" if key == "owner_kind" else key
            tags.append(f"{tag_key}:{value}")
    for key in ("module_id", "collection_id"):
        value = row.get(key)
        if isinstance(value, str) and value:
            tags.append(f"{key.removesuffix('_id')}:{value}")
    return tags


def _name_keys(entity_type: str) -> tuple[str, ...]:
    keys = {
        "build-artifact": ("path",),
        "build-dependency": ("target", "source"),
        "build-graph-edge": ("edge_id", "target", "source"),
        "build-graph-node": ("label", "id"),
        "collection": ("collection_id",),
        "diagnostic": ("code",),
        "hoi4-entity": ("title", "entity_id"),
        "loc-entry": ("key",),
        "module": ("module_id",),
        "pdx-document": ("document_id", "path"),
        "pdx-symbol": ("path", "symbol_id"),
        "project": ("title", "project_id"),
        "source-file": ("path",),
        "source-slot": ("slot",),
        "sprite": ("name",),
    }
    return keys.get(entity_type, ("name", "path", "object_id"))


def _smoke_workspace_id(payload: Mapping[str, object]) -> str:
    project_id = str(payload.get("project_id") or "project")
    slug = "".join(char if char.isalnum() else "-" for char in project_id.lower()).strip("-") or "project"
    digest = sha256hash(dumps_json(payload, sort_keys=True, compact=True))[:8]
    return f"paradev-smoke-{slug}-{digest}"


def _write_workspace_id(payload: Mapping[str, object]) -> str:
    project_id = str(payload.get("project_id") or "project")
    slug = "".join(char if char.isalnum() else "-" for char in project_id.lower()).strip("-") or "project"
    digest = sha256hash(dumps_json(payload, sort_keys=True, compact=True))[:8]
    return f"paradev-catalog-{slug}-{digest}"


def _streaming_write_workspace_id(project_id: str, profile: str) -> str:
    slug = "".join(char if char.isalnum() else "-" for char in project_id.lower()).strip("-") or "project"
    digest = sha256hash(f"{project_id}:{profile}:{uuid4().hex}")[:8]
    return f"paradev-catalog-{slug}-{digest}"


def _database_conflicts(database: Path) -> list[Path]:
    paths = [database, *_database_sidecars(database)]
    return [path for path in paths if path.exists()]


def _remove_database_files(database: Path) -> list[Path]:
    paths = [database, *_database_sidecars(database)]
    existing = [path for path in paths if path.exists()]
    for path in _database_sidecars(database):
        delete_file(path)
    _dispose_database_engine(database)
    delete_file(database)
    return existing


def _replace_database_file(source: Path, target: Path) -> list[Path]:
    existing = _database_conflicts(target)
    _checkpoint_database_file(source)
    for path in _database_sidecars(target):
        delete_file(path)
    _dispose_database_engine(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    source.replace(target)
    return existing


@contextmanager
def _module_catalog_mutation_scope(project: "Project", *, enabled: bool = True) -> Iterator[bool]:
    """Invalidate and order one written module mutation with Catalog writers.

    A configured Catalog is marked stale before control returns to the source
    mutator. This ordering closes the crash window in which project files
    could change before their derived Catalog was made unreadable.
    """

    if not enabled:
        yield False
        return
    database = _catalog_database_path(project, None)
    with _catalog_refresh_lock(database, timeout=_CATALOG_MUTATION_LOCK_TIMEOUT_SECONDS):
        if catalog_status(project)["status"] != "missing":
            _mark_catalog_stale(database)
        yield True


@contextmanager
def _catalog_refresh_lock(database: Path, *, timeout: float = 0) -> Iterator[None]:
    """Serialize Catalog writers for one target while leaving reads free.

    Args:
        database: Catalog database whose refresh lock owns writer ordering.
        timeout: Maximum seconds to wait for the current writer. Defaults to an
            immediate conflict so interactive refresh requests fail fast.
    """

    lock_path = _catalog_refresh_lock_path(database)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(lock_path, timeout=timeout, isolation_level=None)
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
                raise BlockingIOError(f"HeavenBase catalog refresh already in progress: {database}") from error
            raise
        yield
    finally:
        if connection.in_transaction:
            try:
                connection.rollback()
            except Exception as error:
                logger.warning("Catalog writer-lock rollback failed for %s: %s", database, error)
        try:
            connection.close()
        except Exception as error:
            logger.warning("Catalog writer-lock close failed for %s: %s", database, error)


def _catalog_refresh_lock_path(database: Path) -> Path:
    resolved = database.expanduser().resolve(strict=False)
    return resolved.with_name(f"{resolved.name}.refresh.lock")


def _refresh_staging_databases(database: Path) -> list[Path]:
    parent = database.parent
    if not parent.exists():
        return []
    pattern = re.compile(rf"{re.escape(database.name)}\.refresh-[0-9a-f]{{8}}-[0-9a-f]{{8}}\.sqlite")
    staging: set[Path] = set()
    for candidate in parent.iterdir():
        base_name = candidate.name
        for suffix in ("-wal", "-shm"):
            if base_name.endswith(suffix):
                base_name = base_name[: -len(suffix)]
                break
        if pattern.fullmatch(base_name):
            staging.add(parent / base_name)
    return sorted(staging, key=lambda path: path.name)


def _remove_stale_refresh_databases(database: Path) -> list[Path]:
    removed: list[Path] = []
    for staging in _refresh_staging_databases(database):
        removed.extend(_remove_database_files(staging))
    return list(dict.fromkeys(removed))


def _checkpoint_database_file(database: Path) -> None:
    _dispose_database_engine(database)
    with sqlite3.connect(database) as connection:
        connection.execute("pragma wal_checkpoint(truncate)")


def _refresh_database_path(database: Path, payload: Mapping[str, object]) -> Path:
    digest = sha256hash(dumps_json(payload, sort_keys=True, compact=True))[:8]
    return database.with_name(f"{database.name}.refresh-{digest}-{uuid4().hex[:8]}.sqlite")


def _ensure_catalog_query_indexes(database: Path) -> None:
    with sqlite3.connect(database) as connection:
        connection.execute("create index if not exists paradev_sys_catalog_browse " "on sys_catalog (target_entity, name, target_id, object_id)")


def _database_sidecars(database: Path) -> tuple[Path, Path]:
    return (Path(f"{database}-wal"), Path(f"{database}-shm"))


def _dispose_database_engine(database: Path) -> None:
    context = _paradev_context()
    resolver = context.modules()
    if not resolver.inspect("database_dialect", "sqlite"):
        return
    hb.Database(
        database=path_to_file_uri(database),
        provider="sqlite",
        resolver=resolver,
        config=context.config,
    ).dispose()


def _catalog_database_path(project: "Project", database: str | Path | None) -> Path:
    database_path = Path(database) if database is not None else Path(project.root) / ".paradev/.cache/hb/catalog.sqlite"
    return database_path.expanduser().absolute()


def _catalog_stale_path(database: Path) -> Path:
    """Return the fail-closed invalidation marker for one derived Catalog."""

    return database.with_name(f"{database.name}.stale.json")


def _mark_catalog_stale(database: Path) -> Path:
    """Durably invalidate one Catalog before returning source-mutation success."""

    marker = _catalog_stale_path(database)
    marker.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        _fsync_catalog_directory(marker.parent)
        return marker
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(
            dumps_json(
                {
                    "schema": _CATALOG_STALE_SCHEMA,
                    "reason": "project_sources_changed",
                    "refresh": "catalog_refresh",
                },
                sort_keys=True,
                compact=True,
            )
            + "\n"
        )
        stream.flush()
        os.fsync(stream.fileno())
    _fsync_catalog_directory(marker.parent)
    return marker


def _fsync_catalog_directory(directory: Path) -> None:
    """Persist a Catalog marker directory entry on supporting hosts."""

    if not hasattr(os, "O_DIRECTORY"):
        return
    descriptor = os.open(
        directory,
        os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _clear_catalog_stale(database: Path) -> None:
    """Clear one derived-Catalog invalidation only after a coherent write."""

    delete_file(_catalog_stale_path(database))


def _require_current_catalog(database: Path) -> None:
    """Reject reads from a Catalog invalidated by newer project sources."""

    if _catalog_path_state(_catalog_stale_path(database)) != "missing":
        raise RuntimeError(_catalog_refresh_required_message())


def _catalog_refresh_required_message(detail: str | None = None) -> str:
    """Return one actionable stale-Catalog message shared by SDK surfaces."""

    prefix = f"{detail.rstrip()} " if detail and detail.strip() else ""
    return (
        f"{prefix}Project sources changed, so the derived HeavenBase Catalog is stale. "
        "Refresh the project Catalog before using Catalog queries or completions."
    )


def _catalog_path_state(path: Path) -> str:
    """Classify one Catalog database path without opening or mutating it."""

    try:
        path_stat = path.lstat()
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "unreadable"
    if stat.S_ISLNK(path_stat.st_mode):
        try:
            path_stat = path.stat()
        except FileNotFoundError:
            return "incomplete"
        except OSError:
            return "unreadable"
    if not stat.S_ISREG(path_stat.st_mode):
        return "incomplete"
    read_bits = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
    if not path_stat.st_mode & read_bits or not os.access(path, os.R_OK):
        return "unreadable"
    return "file"


def _target_entity(entity: str) -> str:
    return normalize_entity_identifier(entity)


def _query_filters(
    *,
    entity: str | None,
    target_id: str | None,
    name: str | None,
    tag: str | None,
    limit: int | None,
    offset: int,
    include_data: bool,
) -> dict[str, object]:
    filters: dict[str, object] = {}
    if entity is not None:
        filters["entity"] = entity
    if target_id is not None:
        filters["target_id"] = target_id
    if name is not None:
        filters["name"] = name
    if tag is not None:
        filters["tag"] = tag
    if limit is not None:
        filters["limit"] = limit
    if offset:
        filters["offset"] = offset
    if not include_data:
        filters["include_data"] = include_data
    return filters


def _query_catalog_rows(
    database: Path,
    *,
    target_entity: str | None,
    target_id: str | None,
    name: str | None,
    tag: str | None,
    limit: int | None,
    offset: int,
    include_data: bool,
) -> tuple[int, int, list[dict[str, object]]]:
    clauses: list[str] = []
    parameters: list[object] = []
    if target_entity is not None:
        clauses.append("target_entity = ?")
        parameters.append(target_entity)
    if target_id is not None:
        clauses.append("target_id = ?")
        parameters.append(target_id)
    if name is not None:
        clauses.append("instr(paradev_lower(name), paradev_lower(?)) > 0")
        parameters.append(name)
    if tag is not None:
        clauses.append(
            "exists (" "select 1 from json_each(case when json_valid(sys_catalog.tags) then sys_catalog.tags else '[]' end) " "where json_each.value = ?" ")"
        )
        parameters.append(tag)
    where = f" where {' and '.join(clauses)}" if clauses else ""
    uri = _catalog_read_uri(database)
    with sqlite3.connect(uri, uri=True) as connection:
        connection.row_factory = sqlite3.Row
        connection.create_function("paradev_lower", 1, _catalog_name_lower, deterministic=True)
        connection.execute("begin")
        total_count = int(connection.execute("select count(*) from sys_catalog").fetchone()[0])
        filtered_count = int(connection.execute(f"select count(*) from sys_catalog{where}", parameters).fetchone()[0])
        page_query = (
            "select object_id, target_id, target_entity, name, desc, tags, active, ws "
            f"from sys_catalog{where} "
            "order by target_entity, name, target_id, object_id"
        )
        page_parameters = [*parameters]
        if limit is not None:
            page_query += " limit ? offset ?"
            page_parameters.extend((limit, offset))
        elif offset:
            page_query += " limit -1 offset ?"
            page_parameters.append(offset)
        page_rows = connection.execute(page_query, page_parameters).fetchall()
        rows = [
            _catalog_query_row(
                row,
                data=_catalog_target_data(connection, row) if include_data else None,
                include_data=include_data,
            )
            for row in page_rows
        ]
    return total_count, filtered_count, rows


def _catalog_name_lower(value: object) -> str:
    return str(value).lower() if value is not None else ""


def _catalog_completion_cache_key(database: Path) -> tuple[str, int, int]:
    resolved = database.resolve()
    stat = resolved.stat()
    return str(resolved), stat.st_mtime_ns, stat.st_size


def _catalog_read_uri(database: Path) -> str:
    """Return a read-only URI that preserves legacy WAL-backed Catalog data."""

    resolved_uri = database.resolve().as_uri()
    if any(sidecar.exists() for sidecar in _database_sidecars(database)):
        return f"{resolved_uri}?mode=ro"
    return f"{resolved_uri}?mode=ro&immutable=1"


@lru_cache(maxsize=_CATALOG_COMPLETION_CACHE_SIZE)
def _cached_catalog_completion_items(
    database: str,
    mtime_ns: int,
    size: int,
    prefix: str,
    limit: int | None,
) -> tuple[dict[str, object], ...]:
    del mtime_ns, size
    return tuple(_query_catalog_completion_items(Path(database), prefix=prefix, limit=limit))


def _query_catalog_completion_items(
    database: Path,
    *,
    prefix: str,
    limit: int | None,
) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    seen: set[str] = set()
    uri = _catalog_read_uri(database)
    with sqlite3.connect(uri, uri=True) as connection:
        connection.row_factory = sqlite3.Row
        connection.create_function("paradev_lower", 1, _catalog_name_lower, deterministic=True)
        for entity_type, label_fields in (
            ("hoi4-entity", ("object_id",)),
            ("loc-entry", ("key",)),
            ("pdx-symbol", ("key", "value")),
        ):
            target_entity = _target_entity(entity_type)
            table = entity_table(entity_type)
            typed_pdx_symbols = entity_type == "pdx-symbol" and _has_typed_pdx_symbol_table(connection)
            if typed_pdx_symbols:
                storage_by_field = dict(PDX_SYMBOL_FIELD_STORAGE)
                expressions = [f'target."{storage_by_field[field_name]}"' for field_name in label_fields]
                target_projection = ", " + ", ".join(
                    f'target."{storage_name}" as "target_{field_name}"' for field_name, storage_name in PDX_SYMBOL_FIELD_STORAGE
                )
            else:
                expressions = [f"json_extract(json_extract(target.data, '$'), '$.{field_name}')" for field_name in label_fields]
                target_projection = ", target.data as target_data"
            prefix_clause = ""
            parameters: list[object] = [target_entity]
            if prefix:
                prefix_clause = " and (" + " or ".join(f"instr(paradev_lower(cast({expression} as text)), ?) = 1" for expression in expressions) + ")"
                parameters.extend(prefix for _expression in expressions)
            rows = connection.execute(
                "select catalog.object_id, catalog.target_id, catalog.target_entity, "
                "catalog.name, catalog.desc, catalog.tags, catalog.active, catalog.ws"
                f"{target_projection} "
                "from sys_catalog as catalog "
                f"join {table} as target on target.object_id = catalog.target_id "
                f"where catalog.target_entity = ?{prefix_clause} "
                "order by catalog.name, catalog.target_id, catalog.object_id",
                parameters,
            )
            for result in rows:
                data = _typed_pdx_symbol_data(result, prefix="target_") if typed_pdx_symbols else _catalog_query_data(result["target_data"])
                row = _catalog_query_row(result, data=data)
                for item in _completion_items(entity_type, row):
                    label = str(item["label"])
                    if prefix and not label.lower().startswith(prefix):
                        continue
                    if label in seen:
                        continue
                    seen.add(label)
                    items.append(item)
                    if limit is not None and len(items) >= limit:
                        return items
    return items


def _catalog_query_row(
    row: sqlite3.Row,
    *,
    data: Mapping[str, object] | None = None,
    include_data: bool = True,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "object_id": str(row["object_id"]),
        "target_id": str(row["target_id"]),
        "target_entity": str(row["target_entity"]),
        "name": str(row["name"]),
        "desc": str(row["desc"]),
        "tags": _catalog_query_tags(row["tags"]),
        "active": bool(row["active"]),
        "workspace_id": str(row["ws"]),
    }
    if include_data:
        payload["data"] = dict(data or {})
    return payload


def _catalog_target_data(connection: sqlite3.Connection, row: sqlite3.Row) -> dict[str, object]:
    entity_type = entity_type_from_identifier(str(row["target_entity"]))
    table = _target_entity_table(str(row["target_entity"]))
    if table is None:
        return {}
    if entity_type == "pdx-symbol":
        target = connection.execute(f"select * from {table} where object_id = ?", (str(row["target_id"]),)).fetchone()
        if target is None:
            return {}
        if "data" not in target.keys():
            return _stored_pdx_symbol_data(target)
        return _catalog_query_data(target["data"])
    target = connection.execute(f"select data from {table} where object_id = ?", (str(row["target_id"]),)).fetchone()
    if target is None:
        return {}
    return _catalog_query_data(target["data"])


def _has_typed_pdx_symbol_table(connection: sqlite3.Connection) -> bool:
    columns = {str(row[1]) for row in connection.execute(f"pragma table_info({entity_table('pdx-symbol')})")}
    return {storage_name for _field_name, storage_name in PDX_SYMBOL_FIELD_STORAGE}.issubset(columns)


def _typed_pdx_symbol_data(row: sqlite3.Row, *, prefix: str = "") -> dict[str, object]:
    return {field_name: row[f"{prefix}{field_name}"] for field_name in PDX_SYMBOL_DATA_FIELDS if row[f"{prefix}{field_name}"] is not None}


def _stored_pdx_symbol_data(row: sqlite3.Row) -> dict[str, object]:
    return {field_name: row[storage_name] for field_name, storage_name in PDX_SYMBOL_FIELD_STORAGE if row[storage_name] is not None}


def _target_entity_table(target_entity: str) -> str | None:
    entity_type = entity_type_from_identifier(target_entity)
    if entity_type is None:
        return None
    return entity_table(entity_type)


def _catalog_query_data(value: object) -> dict[str, object]:
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        if isinstance(parsed, Mapping):
            return {key: item for key, item in parsed.items() if isinstance(key, str)}
    return {}


def _catalog_query_tags(value: object) -> list[str]:
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [tag for tag in parsed if isinstance(tag, str)]
    return []


def _completion_items(entity_type: str, row: Mapping[str, object]) -> list[dict[str, object]]:
    data = row.get("data")
    if not isinstance(data, Mapping):
        return []
    if entity_type == "hoi4-entity":
        return _hoi4_entity_completion_items(row, data)
    if entity_type == "loc-entry":
        return _loc_entry_completion_items(row, data)
    if entity_type == "pdx-symbol":
        return _pdx_symbol_completion_items(row, data)
    return []


def _hoi4_entity_completion_items(row: Mapping[str, object], data: Mapping[str, object]) -> list[dict[str, object]]:
    object_id = data.get("object_id")
    if not isinstance(object_id, str) or not object_id:
        return []
    detail = data.get("entity_id")
    title = data.get("title")
    return [
        _completion_item(
            object_id,
            kind=_COMPLETION_KIND_CLASS,
            detail=detail if isinstance(detail, str) else None,
            documentation=title if isinstance(title, str) else None,
            source="hoi4-entity",
            row=row,
        )
    ]


def _loc_entry_completion_items(row: Mapping[str, object], data: Mapping[str, object]) -> list[dict[str, object]]:
    key = data.get("key")
    if not isinstance(key, str) or not key:
        return []
    language = data.get("language")
    text = data.get("text")
    return [
        _completion_item(
            key,
            kind=_COMPLETION_KIND_REFERENCE,
            detail=language if isinstance(language, str) else None,
            documentation=text if isinstance(text, str) else None,
            source="loc-entry",
            row=row,
        )
    ]


def _pdx_symbol_completion_items(row: Mapping[str, object], data: Mapping[str, object]) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    key = data.get("key")
    path = data.get("path")
    if isinstance(key, str) and key:
        items.append(
            _completion_item(
                key,
                kind=_COMPLETION_KIND_PROPERTY,
                detail=path if isinstance(path, str) else None,
                source="pdx-symbol",
                row=row,
            )
        )
    value = data.get("value")
    if isinstance(value, str) and value:
        items.append(
            _completion_item(
                value,
                kind=_COMPLETION_KIND_VALUE,
                detail=path if isinstance(path, str) else None,
                source="pdx-symbol",
                row=row,
            )
        )
    return items


def _completion_item(
    label: str,
    *,
    kind: int,
    source: str,
    row: Mapping[str, object],
    detail: str | None = None,
    documentation: str | None = None,
) -> dict[str, object]:
    item: dict[str, object] = {
        "label": label,
        "kind": kind,
        "data": {
            "source": source,
            "target_entity": row.get("target_entity"),
            "target_id": row.get("target_id"),
        },
    }
    if detail:
        item["detail"] = detail
    if documentation:
        item["documentation"] = {"kind": "markdown", "value": documentation}
    return item


def _project_row(project: "Project") -> dict[str, object]:
    return {
        "project_id": project.project_id,
        "title": project.title,
        "game": project.game,
        "root": str(project.root),
        "manifest": str(project.manifest_path),
        "output_root": str(project.output_root),
        "build_root": str(project.build_root),
    }


def _build_artifacts(artifacts: Sequence["Artifact"]) -> list[dict[str, object]]:
    from paradev.build import artifact_collection_ids, artifact_module_ids

    rows: list[dict[str, object]] = []
    for artifact in artifacts:
        row = artifact.to_dict()
        module_ids = artifact_module_ids(row)
        collection_ids = artifact_collection_ids(row)
        if module_ids:
            row["module_ids"] = list(module_ids)
        if collection_ids:
            row["collection_ids"] = list(collection_ids)
        rows.append(row)
    return rows


def _build_graph_nodes(rows: object) -> list[dict[str, object]]:
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _build_graph_edges(rows: object) -> list[dict[str, object]]:
    edges: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        source = row.get("source")
        target = row.get("target")
        kind = row.get("kind")
        if not isinstance(source, str) or not isinstance(target, str) or not isinstance(kind, str):
            continue
        edges.append({"edge_id": f"{source}:{kind}:{target}", **dict(row)})
    return edges


def _collections(collections: Sequence["Collection"]) -> list[dict[str, object]]:
    return [collection.to_dict() for collection in collections]


def _modules(modules: Sequence["Module"]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for module in modules:
        active = module.metadata.get("inactive") is not True
        rows.append(
            {
                **module.to_dict(),
                "active": active,
                "status": "active" if active else "inactive",
            }
        )
    return rows


def _source_files(rows: object) -> list[dict[str, object]]:
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _source_slots(payload: Mapping[str, object]) -> list[dict[str, object]]:
    rows = payload.get("source_slots")
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, Mapping)]


def _hoi4_entities(modules: Sequence["Module"]) -> list[dict[str, object]]:
    return list(_iter_hoi4_entities(modules))


def _iter_hoi4_entities(modules: Sequence["Module"]) -> Iterable[dict[str, object]]:
    for module in modules:
        metadata = module.metadata if isinstance(module.metadata, Mapping) else {}
        row: dict[str, object] = {
            "entity_id": module.module_id,
            "family": module.family,
            "object_id": _metadata_text(metadata, "object_id") or Path(str(module.root)).name,
            "module_id": module.module_id,
        }
        if module.collection_id:
            row["collection_id"] = module.collection_id
        for key in ("title", "owner"):
            value = _metadata_text(metadata, key)
            if value:
                row[key] = value
        tags = metadata.get("tags")
        if isinstance(tags, Sequence) and not isinstance(tags, str | bytes):
            row["tags"] = [tag for tag in tags if isinstance(tag, str)]
        yield row


def _pdx_documents(result: "BuildResult") -> list[dict[str, object]]:
    return list(_iter_pdx_documents(result))


def _iter_pdx_documents(result: "BuildResult") -> Iterable[dict[str, object]]:
    for source in _pdx_sources(result):
        yield {
            "document_id": source["document_id"],
            **source["owner"],
            "slot": source["slot"],
            "path": source["path"],
            "file_ext": source["block"].file_ext or Path(str(source["source_path"])).suffix,
            "entry_count": len(source["block"].entries),
            "ast_hash": sha256hash(dumps_json(source["block"].dump(), sort_keys=True, compact=True)),
        }


def _pdx_symbols(result: "BuildResult") -> list[dict[str, object]]:
    return list(_iter_pdx_symbols(result))


def _iter_pdx_symbols(result: "BuildResult") -> Iterable[dict[str, object]]:
    for source in _pdx_sources(result):
        seen_paths: dict[str, int] = {}
        for index, (path, entry) in enumerate(source["block"].walk()):
            row = _pdx_symbol_row(source=source, entry=entry, path=_deduped_path(path, seen_paths), index=index)
            if row:
                yield row


def _pdx_sources(result: "BuildResult") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for module in result.modules:
        payload = getattr(module, "payload", None)
        for source in getattr(payload, "pdx_sources", ()):
            document_id = f"{module.module_id}:{source.slot}:{source.path}"
            rows.append(
                {
                    "document_id": document_id,
                    "owner": {"module_id": module.module_id, "family": module.family},
                    "slot": source.slot,
                    "source_path": source.path,
                    "path": str(Path(module.root) / source.path),
                    "block": source.block,
                }
            )
    for collection in result.collections:
        payload = getattr(collection, "payload", None)
        root = getattr(payload, "root", None)
        if root is None:
            continue
        for source in getattr(payload, "pdx_sources", ()):
            document_id = f"collection:{collection.collection_id}:{source.slot}:{source.path}"
            rows.append(
                {
                    "document_id": document_id,
                    "owner": {"collection_id": collection.collection_id, "family": collection.family},
                    "slot": source.slot,
                    "source_path": source.path,
                    "path": str(Path(root) / source.path),
                    "block": source.block,
                }
            )
    return rows


def _pdx_symbol_row(*, source: Mapping[str, Any], entry: PDXEntry, path: str, index: int) -> dict[str, object] | None:
    if entry.key is None:
        return None
    kind = _pdx_symbol_kind(entry)
    row: dict[str, object] = {
        "symbol_id": f"{source['document_id']}:{index}",
        "document_id": source["document_id"],
        **source["owner"],
        "slot": source["slot"],
        "path": path,
        "key": str(entry.key.val),
        "kind": kind,
    }
    if entry.op:
        row["op"] = entry.op
    if isinstance(entry.val, PDXScalar):
        row["value"] = str(entry.val.val)
        row["value_type"] = entry.val.type
    span = entry.key.anno.get("span")
    if isinstance(span, Mapping):
        line = span.get("line")
        column = span.get("column")
        if isinstance(line, int) and isinstance(column, int):
            row["line"] = line
            row["column"] = column
    return row


def _pdx_symbol_kind(entry: PDXEntry) -> str:
    if isinstance(entry.val, PDXBlock):
        return "block"
    if isinstance(entry.val, PDXScalar):
        return "scalar"
    if entry.op:
        return "operator"
    return "bare"


def _deduped_path(path: Sequence[str], seen_paths: dict[str, int]) -> str:
    base = "/".join(path)
    count = seen_paths.get(base, 0)
    seen_paths[base] = count + 1
    if count == 0:
        return base
    return f"{base}__D{count}"


def _metadata_text(metadata: Mapping[str, Any], key: str) -> str | None:
    value = metadata.get(key)
    return value if isinstance(value, str) and value else None


__all__ = [
    "CATALOG_API_TABLE_ROWS",
    "CATALOG_API_TABLE_SCHEMA",
    "CATALOG_SCHEMA",
    "CatalogApiRow",
    "CatalogApiTable",
    "ENTITY_TYPES",
    "HB_API_TABLE_SCHEMA",
    "HbApiRow",
    "HbApiTable",
    "QUERY_SCHEMA",
    "REFRESH_SCHEMA",
    "SMOKE_SCHEMA",
    "STATUS_SCHEMA",
    "WRITE_SCHEMA",
    "catalog_completion_items",
    "catalog_preview",
    "catalog_query",
    "catalog_refresh",
    "catalog_smoke",
    "catalog_status",
    "catalog_write",
    "get_catalog_api_selection",
    "get_catalog_api_table",
    "get_hb_api_selection",
    "get_hb_api_table",
    "render_hb_api_reference_markdown",
    "render_catalog_api_reference_markdown",
]
