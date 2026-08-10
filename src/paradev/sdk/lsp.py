"""SDK helpers for LSP-shaped payloads."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from typing_extensions import TypedDict

from paradev._api_table import api_symbol_indexes, api_table_selection
from paradev._api_table_markdown import api_surface_reference_markdown
from paradev.pdx import SCALAR_NUM, SCALAR_STR, SCALAR_VAR, PDXBlock, PDXEntry, PDXParseError, PDXScalar

from .pdx import format_pdx_text

if TYPE_CHECKING:
    from paradev.sdk import Project

LSP_COMPLETION_SCHEMA = "paradev.lsp.completion.v1"
LSP_DIAGNOSTICS_SCHEMA = "paradev.lsp.diagnostics.v1"
LSP_FORMATTING_SCHEMA = "paradev.lsp.formatting.v1"
LSP_HOVER_SCHEMA = "paradev.lsp.hover.v1"
LSP_SEMANTIC_TOKENS_SCHEMA = "paradev.lsp.semantic-tokens.v1"
LSP_SYMBOLS_SCHEMA = "paradev.lsp.symbols.v1"
LSP_API_TABLE_SCHEMA = "paradev.sdk.lsp-api-table.v1"
_LSP_API_INDEX_NAMES = ("surface_index", "feature_index")
_LSP_API_STANDARD_FIELDS = (
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


class LspApiRow(TypedDict):
    """One public LSP editor API table row."""

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


class LspApiTable(TypedDict):
    """Generated API-standard table for LSP editor capabilities."""

    schema: str
    row_count: int
    surface_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    rows: list[LspApiRow]


LSP_API_TABLE_ROWS: tuple[LspApiRow, ...] = (
    {
        "symbol": "LSP_DIAGNOSTICS_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "diagnostics",
        "inputs": "none",
        "returns": LSP_DIAGNOSTICS_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_DIAGNOSTICS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LSP_SYMBOLS_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "symbols",
        "inputs": "none",
        "returns": LSP_SYMBOLS_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_SYMBOLS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LSP_HOVER_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "hover",
        "inputs": "none",
        "returns": LSP_HOVER_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_HOVER_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LSP_FORMATTING_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "formatting",
        "inputs": "none",
        "returns": LSP_FORMATTING_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_FORMATTING_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LSP_COMPLETION_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "completion",
        "inputs": "none",
        "returns": LSP_COMPLETION_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_COMPLETION_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LSP_SEMANTIC_TOKENS_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "semantic_tokens",
        "inputs": "none",
        "returns": LSP_SEMANTIC_TOKENS_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_SEMANTIC_TOKENS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LSP_API_TABLE_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": LSP_API_TABLE_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LSP_API_TABLE_ROWS",
        "kind": "constant",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "tuple[LspApiRow, ...]",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LspApiRow",
        "kind": "TypedDict",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "symbol, kind, layer, feature, inputs, returns, raises, registry_seam, surface, payload_schema, doc_page, test_anchor",
        "returns": "LSP API table row schema",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "LspApiTable",
        "kind": "TypedDict",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "schema, row_count, surface_index, feature_index, rows",
        "returns": "LSP API table schema",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "get_lsp_api_selection",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "LspApiTable | LspApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_lsp_api_selection.py::test_lsp_api_selection_returns_table_row_and_index_projection",
    },
    {
        "symbol": "diagnose_pdx_lsp_text",
        "kind": "function",
        "layer": "sdk",
        "feature": "diagnostics",
        "inputs": "text, uri=None, path=None",
        "returns": "LSP diagnostics payload",
        "raises": "ValueError on unsupported text, uri, or path",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_DIAGNOSTICS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_lsp_diagnostics_cli_outputs_lsp_payload",
    },
    {
        "symbol": "document_symbols_pdx_lsp_text",
        "kind": "function",
        "layer": "sdk",
        "feature": "symbols",
        "inputs": "text, uri=None, path=None",
        "returns": "LSP document-symbol payload",
        "raises": "ValueError on unsupported text, uri, or path",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_SYMBOLS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "hover_pdx_lsp_text",
        "kind": "function",
        "layer": "sdk",
        "feature": "hover",
        "inputs": "text, line, character, uri=None, path=None",
        "returns": "LSP hover payload",
        "raises": "ValueError on unsupported text, position, uri, or path",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_HOVER_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "format_pdx_lsp_text",
        "kind": "function",
        "layer": "sdk",
        "feature": "formatting",
        "inputs": 'text, uri=None, path=None, indent="\\t", comments=True',
        "returns": "LSP formatting payload",
        "raises": "ValueError on unsupported text, uri, path, or indent",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_FORMATTING_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_lsp_formatting_cli_reads_text_file",
    },
    {
        "symbol": "complete_pdx_lsp_text",
        "kind": "function",
        "layer": "sdk",
        "feature": "completion",
        "inputs": "text, line, character, uri=None, path=None, project=None, database=None, game_root=None, limit=100, offset=None",
        "returns": "LSP completion payload",
        "raises": "ValueError on unsupported request fields; FileNotFoundError when project catalog is missing",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_COMPLETION_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "semantic_tokens_pdx_lsp_text",
        "kind": "function",
        "layer": "sdk",
        "feature": "semantic_tokens",
        "inputs": "text, uri=None, path=None",
        "returns": "LSP semantic-token payload",
        "raises": "ValueError on unsupported text, uri, or path",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_SEMANTIC_TOKENS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "get_lsp_api_table",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "LspApiTable",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "render_lsp_api_reference_markdown",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "Markdown LSP API reference",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "paradev lsp-api",
        "kind": "command",
        "layer": "cli",
        "feature": "api-table",
        "inputs": "--json",
        "returns": "LspApiTable",
        "raises": "typer.BadParameter when combined selectors are invalid",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_lsp_api_cli_outputs_table_json",
    },
    {
        "symbol": "paradev lsp-api --markdown",
        "kind": "command projection",
        "layer": "cli",
        "feature": "api-table",
        "inputs": "none",
        "returns": "Markdown LSP API reference",
        "raises": "typer.BadParameter when combined with --json",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_lsp_api_cli_outputs_reference_markdown",
    },
    {
        "symbol": "paradev lsp serve",
        "kind": "command",
        "layer": "cli",
        "feature": "server",
        "inputs": "project_path, database, game_root, limit, change_diagnostics_max_bytes",
        "returns": "stdio JSON-RPC LSP process",
        "raises": "",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": "",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods",
    },
    {
        "symbol": "paradev lsp diagnostics",
        "kind": "command",
        "layer": "cli",
        "feature": "diagnostics",
        "inputs": "text or text_file, uri=None, path=None, --json",
        "returns": "LSP diagnostics payload",
        "raises": "typer.BadParameter on unsupported text source",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": LSP_DIAGNOSTICS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_lsp_diagnostics_cli_outputs_lsp_payload",
    },
    {
        "symbol": "paradev lsp symbols",
        "kind": "command",
        "layer": "cli",
        "feature": "symbols",
        "inputs": "text or text_file, uri=None, path=None, --json",
        "returns": "LSP document-symbol payload",
        "raises": "typer.BadParameter on unsupported text source",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": LSP_SYMBOLS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "paradev lsp hover",
        "kind": "command",
        "layer": "cli",
        "feature": "hover",
        "inputs": "line, character, text or text_file, uri=None, path=None, --json",
        "returns": "LSP hover payload",
        "raises": "typer.BadParameter on unsupported text source or position",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": LSP_HOVER_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "paradev lsp formatting",
        "kind": "command",
        "layer": "cli",
        "feature": "formatting",
        "inputs": "text or text_file, uri=None, path=None, indent, comments, --json",
        "returns": "LSP formatting payload",
        "raises": "typer.BadParameter on unsupported text source",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": LSP_FORMATTING_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_lsp_formatting_cli_reads_text_file",
    },
    {
        "symbol": "paradev lsp completion",
        "kind": "command",
        "layer": "cli",
        "feature": "completion",
        "inputs": "line, character, offset, text or text_file, uri=None, path=None, project_path=None, database=None, game_root=None, limit=100, --json",
        "returns": "LSP completion payload",
        "raises": "typer.BadParameter on unsupported text source, project, catalog, or position",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": LSP_COMPLETION_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "paradev lsp semantic-tokens",
        "kind": "command",
        "layer": "cli",
        "feature": "semantic_tokens",
        "inputs": "text or text_file, uri=None, path=None, --json",
        "returns": "LSP semantic-token payload",
        "raises": "typer.BadParameter on unsupported text source",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": LSP_SEMANTIC_TOKENS_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces",
    },
    {
        "symbol": "POST /lsp/diagnostics",
        "kind": "REST route",
        "layer": "rest",
        "feature": "diagnostics",
        "inputs": "text, uri=None, path=None",
        "returns": "LSP diagnostics payload",
        "raises": "",
        "registry_seam": "OpenAPI path /lsp/diagnostics",
        "surface": "rest",
        "payload_schema": LSP_DIAGNOSTICS_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "POST /lsp/symbols",
        "kind": "REST route",
        "layer": "rest",
        "feature": "symbols",
        "inputs": "text, uri=None, path=None",
        "returns": "LSP document-symbol payload",
        "raises": "",
        "registry_seam": "OpenAPI path /lsp/symbols",
        "surface": "rest",
        "payload_schema": LSP_SYMBOLS_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "POST /lsp/hover",
        "kind": "REST route",
        "layer": "rest",
        "feature": "hover",
        "inputs": "text, line, character, uri=None, path=None",
        "returns": "LSP hover payload",
        "raises": "",
        "registry_seam": "OpenAPI path /lsp/hover",
        "surface": "rest",
        "payload_schema": LSP_HOVER_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "POST /lsp/formatting",
        "kind": "REST route",
        "layer": "rest",
        "feature": "formatting",
        "inputs": 'text, uri=None, path=None, indent="\\t", comments=True',
        "returns": "LSP formatting payload",
        "raises": "",
        "registry_seam": "OpenAPI path /lsp/formatting",
        "surface": "rest",
        "payload_schema": LSP_FORMATTING_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "POST /lsp/completion",
        "kind": "REST route",
        "layer": "rest",
        "feature": "completion",
        "inputs": "text, line, character, offset, uri=None, path=None, project_path=None, database=None, game_root=None, limit=100",
        "returns": "LSP completion payload",
        "raises": "",
        "registry_seam": "OpenAPI path /lsp/completion",
        "surface": "rest",
        "payload_schema": LSP_COMPLETION_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "POST /lsp/semantic-tokens",
        "kind": "REST route",
        "layer": "rest",
        "feature": "semantic_tokens",
        "inputs": "text, uri=None, path=None",
        "returns": "LSP semantic-token payload",
        "raises": "",
        "registry_seam": "OpenAPI path /lsp/semantic-tokens",
        "surface": "rest",
        "payload_schema": LSP_SEMANTIC_TOKENS_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "GET /lsp-api",
        "kind": "REST route",
        "layer": "rest",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "LspApiTable | LspApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "OpenAPI path /lsp-api",
        "surface": "rest",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_lsp_api_surface_selectors.py::test_lsp_api_table_lists_rest_and_mcp_selector_surfaces",
    },
    {
        "symbol": "lsp_api",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "LspApiTable | LspApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "payload_schema": LSP_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/lsp-api-reference.md",
        "test_anchor": "tests/test_lsp_api_surface_selectors.py::test_lsp_api_table_lists_rest_and_mcp_selector_surfaces",
    },
    {
        "symbol": "textDocument/publishDiagnostics",
        "kind": "LSP method",
        "layer": "lsp",
        "feature": "diagnostics",
        "inputs": "text document content and identity",
        "returns": "LSP diagnostics payload",
        "raises": "",
        "registry_seam": "LSP method contract",
        "surface": "lsp",
        "payload_schema": LSP_DIAGNOSTICS_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods",
    },
    {
        "symbol": "textDocument/documentSymbol",
        "kind": "LSP method",
        "layer": "lsp",
        "feature": "symbols",
        "inputs": "text document content and identity",
        "returns": "LSP document-symbol payload",
        "raises": "",
        "registry_seam": "LSP method contract",
        "surface": "lsp",
        "payload_schema": LSP_SYMBOLS_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods",
    },
    {
        "symbol": "textDocument/hover",
        "kind": "LSP method",
        "layer": "lsp",
        "feature": "hover",
        "inputs": "text document content, line, character, and identity",
        "returns": "LSP hover payload",
        "raises": "",
        "registry_seam": "LSP method contract",
        "surface": "lsp",
        "payload_schema": LSP_HOVER_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods",
    },
    {
        "symbol": "textDocument/formatting",
        "kind": "LSP method",
        "layer": "lsp",
        "feature": "formatting",
        "inputs": "text document content, identity, indent, and comment policy",
        "returns": "LSP formatting payload",
        "raises": "",
        "registry_seam": "LSP method contract",
        "surface": "lsp",
        "payload_schema": LSP_FORMATTING_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods",
    },
    {
        "symbol": "textDocument/completion",
        "kind": "LSP method",
        "layer": "lsp",
        "feature": "completion",
        "inputs": "text document content, line, character, offset, identity, catalog, game root, and limit",
        "returns": "LSP completion payload",
        "raises": "",
        "registry_seam": "LSP method contract",
        "surface": "lsp",
        "payload_schema": LSP_COMPLETION_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods",
    },
    {
        "symbol": "textDocument/semanticTokens/full",
        "kind": "LSP method",
        "layer": "lsp",
        "feature": "semantic_tokens",
        "inputs": "text document content and identity",
        "returns": "LSP semantic-token payload",
        "raises": "",
        "registry_seam": "LSP method contract",
        "surface": "lsp",
        "payload_schema": LSP_SEMANTIC_TOKENS_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods",
    },
)


def get_lsp_api_table() -> LspApiTable:
    """Return the API-standard table for LSP editor capabilities.

    Returns:
        JSON-safe API table with copied rows, plus grouped indexes for surface
        and capability audits.
    """

    rows = [dict(row) for row in LSP_API_TABLE_ROWS]
    surface_index, feature_index = api_symbol_indexes(rows, "surface", "feature")
    return {
        "schema": LSP_API_TABLE_SCHEMA,
        "row_count": len(rows),
        "surface_index": surface_index,
        "feature_index": feature_index,
        "rows": rows,
    }


def get_lsp_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> LspApiTable | LspApiRow | list[str]:
    """Return the full LSP API table, one row, or one index bucket.

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
        LspApiTable | LspApiRow | list[str],
        api_table_selection(
            get_lsp_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_LSP_API_INDEX_NAMES,
        ),
    )


def render_lsp_api_reference_markdown() -> str:
    """Render the LSP editor API table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/lsp-api-reference.md`. The content is generated from
        `get_lsp_api_table()` so SDK, CLI, REST, MCP, and LSP editor docs stay
        aligned.
    """

    table = get_lsp_api_table()
    return api_surface_reference_markdown(
        title="LSP API Reference",
        source="paradev.sdk.get_lsp_api_table()",
        regenerate_when="Regenerate this file whenever the LSP API table changes:",
        command="rtk uv run paradev lsp-api --markdown > docs/user-manual/lsp-api-reference.md",
        table=table,
        fields=_LSP_API_STANDARD_FIELDS,
    )


_SYMBOL_KIND_PROPERTY = 7
_SYMBOL_KIND_OBJECT = 19
_SYMBOL_KIND_KEY = 20
_SEMANTIC_TOKEN_TYPES = ("property", "class", "enum", "string", "number", "variable")
_SEMANTIC_TOKEN_TYPE_INDEX = {token_type: index for index, token_type in enumerate(_SEMANTIC_TOKEN_TYPES)}
_SEMANTIC_TOKEN_MODIFIERS: tuple[str, ...] = ()
_MODIFIER_CONTEXT_KEYS = frozenset({"modifier", "modifiers"})
_TRIGGER_CONTEXT_KEYS = frozenset(
    {
        "abort_trigger",
        "allow",
        "allowed",
        "available",
        "bypass",
        "cancel_trigger",
        "custom_trigger_tooltip",
        "limit",
        "potential",
        "prerequisite",
        "target_trigger",
        "trigger",
        "visible",
    }
)
_EFFECT_CONTEXT_KEYS = frozenset(
    {
        "ai_will_do",
        "complete_effect",
        "completion_reward",
        "effect",
        "effects",
        "else",
        "hidden_effect",
        "if",
        "immediate",
        "option",
        "random_effect",
        "reward",
    }
)

_LSP_SEVERITY = {
    "error": 1,
    "warning": 2,
    "info": 3,
    "information": 3,
    "hint": 4,
}
_PARSED_LSP_CACHE_SIZE = 8
_PARSED_LSP_CACHE_MAX_BYTES = 2_000_000
_COMPLETION_CONTEXT_SCAN_LIMIT = 50_000
_COMPLETION_CONTEXT_MAX_DEPTH = 12


def complete_pdx_lsp_text(
    text: str,
    line: int,
    character: int,
    *,
    uri: str | None = None,
    path: str | Path | None = None,
    project: "Project | None" = None,
    database: str | Path | None = None,
    game_root: str | Path | None = None,
    limit: int | None = 100,
    offset: int | None = None,
) -> dict[str, object]:
    """Return LSP `textDocument/completion` rows for PDX text.

    Args:
        text: Current document text from the editor buffer.
        line: Zero-based document line.
        character: Zero-based UTF-16/LSP character offset for the line.
        uri: Optional LSP document URI.
        path: Optional display path used for file extension metadata.
        project: Optional loaded project used for HeavenBase catalog-backed
            completions.
        database: Optional SQLite catalog path. Defaults to the project's
            `.paradev/.cache/hb/catalog.sqlite` when `project` is provided.
        game_root: Optional Hearts of Iron IV install path used for built-in
            HOI4 modifier, effect, and trigger keyword completions. When
            omitted, `paradev.hoi4.game_root` is used before platform defaults.
        limit: Optional maximum completion count.
        offset: Optional zero-based document offset for the cursor. Editor
            adapters should pass it when available so completion does not need
            to scan from the beginning of large documents.

    Returns:
        JSON-safe LSP completion payload.

    Raises:
        ValueError: If request fields have unsupported types.
        FileNotFoundError: If a project is provided and the catalog database
            does not exist.
    """

    if not isinstance(text, str):
        raise ValueError("PDX LSP document text must be a string.")
    _validate_lsp_position(line=line, character=character)
    _validate_lsp_document(uri=uri, path=path)
    _validate_lsp_offset(offset=offset, text=text)
    if limit is not None and type(limit) is not int:
        raise ValueError("LSP completion limit must be an integer when provided.")

    prefix, context_stack = _completion_context(text, line=line, character=character, offset=offset)
    items: list[dict[str, object]] = []
    keyword_kind = _completion_keyword_kind(context_stack, path=path)
    if keyword_kind is not None:
        from paradev.games.hoi4.keywords import hoi4_keyword_completion_items

        items.extend(hoi4_keyword_completion_items(kind=keyword_kind, prefix=prefix, game_root=game_root, limit=limit))
    if project is not None:
        from paradev.hb import catalog_completion_items

        remaining_limit = _remaining_completion_limit(limit, len(items))
        if remaining_limit is None or remaining_limit > 0:
            items.extend(catalog_completion_items(project, database=database, prefix=prefix, limit=remaining_limit))
    return _lsp_completion_payload(
        uri=uri,
        path=path,
        line=line,
        character=character,
        prefix=prefix,
        items=_dedupe_completion_items(items, limit=limit),
        diagnostics=[],
    )


def semantic_tokens_pdx_lsp_text(
    text: str,
    *,
    uri: str | None = None,
    path: str | Path | None = None,
) -> dict[str, object]:
    """Return LSP `textDocument/semanticTokens/full` rows for PDX text.

    Args:
        text: Current document text from the editor buffer.
        uri: Optional LSP document URI.
        path: Optional display path used for file extension metadata.

    Returns:
        JSON-safe semantic-token payload. `tokens` is an expanded row view for
        adapters that do not consume LSP's encoded integer stream directly.

    Raises:
        ValueError: If `text`, `uri`, or `path` have unsupported types.
    """

    if not isinstance(text, str):
        raise ValueError("PDX LSP document text must be a string.")
    _validate_lsp_document(uri=uri, path=path)
    try:
        block = _parse_pdx_lsp_block(text, path=path)
    except PDXParseError as error:
        return _lsp_semantic_tokens_payload(
            uri=uri,
            path=path,
            tokens=[],
            data=[],
            diagnostics=_lsp_diagnostics([diagnostic.to_dict() for diagnostic in error.diagnostics]),
        )

    tokens = _semantic_tokens(block)
    return _lsp_semantic_tokens_payload(uri=uri, path=path, tokens=tokens, data=_encode_semantic_tokens(tokens), diagnostics=[])


def document_symbols_pdx_lsp_text(
    text: str,
    *,
    uri: str | None = None,
    path: str | Path | None = None,
) -> dict[str, object]:
    """Return LSP `textDocument/documentSymbol` rows for PDX text.

    Args:
        text: Current document text from the editor buffer.
        uri: Optional LSP document URI.
        path: Optional display path used for file extension metadata.

    Returns:
        JSON-safe LSP document-symbol payload.

    Raises:
        ValueError: If `text`, `uri`, or `path` have unsupported types.
    """

    if not isinstance(text, str):
        raise ValueError("PDX LSP document text must be a string.")
    _validate_lsp_document(uri=uri, path=path)
    try:
        block = _parse_pdx_lsp_block(text, path=path)
    except PDXParseError as error:
        return _lsp_symbols_payload(
            uri=uri,
            path=path,
            symbols=[],
            diagnostics=_lsp_diagnostics([diagnostic.to_dict() for diagnostic in error.diagnostics]),
        )
    return _lsp_symbols_payload(uri=uri, path=path, symbols=_block_symbols(block), diagnostics=[])


def diagnose_pdx_lsp_text(
    text: str,
    *,
    uri: str | None = None,
    path: str | Path | None = None,
) -> dict[str, object]:
    """Return LSP `textDocument/publishDiagnostics` rows for PDX text.

    Args:
        text: Current document text from the editor buffer.
        uri: Optional LSP document URI.
        path: Optional display path used for file extension metadata.

    Returns:
        JSON-safe LSP diagnostics payload.

    Raises:
        ValueError: If `text`, `uri`, or `path` have unsupported types.
    """

    if not isinstance(text, str):
        raise ValueError("PDX LSP document text must be a string.")
    _validate_lsp_document(uri=uri, path=path)
    try:
        _parse_pdx_lsp_block(text, path=path)
    except PDXParseError as error:
        diagnostics = _lsp_diagnostics([diagnostic.to_dict() for diagnostic in error.diagnostics])
    else:
        diagnostics = []
    return _lsp_diagnostics_payload(uri=uri, path=path, diagnostics=diagnostics)


def hover_pdx_lsp_text(
    text: str,
    line: int,
    character: int,
    *,
    uri: str | None = None,
    path: str | Path | None = None,
) -> dict[str, object]:
    """Return LSP `textDocument/hover` details for a PDX key position.

    Args:
        text: Current document text from the editor buffer.
        line: Zero-based document line.
        character: Zero-based UTF-16/LSP character offset for the line.
        uri: Optional LSP document URI.
        path: Optional display path used for file extension metadata.

    Returns:
        JSON-safe LSP hover payload. `hover` is `None` when the position does
        not land on a parsed key span.

    Raises:
        ValueError: If `text`, `line`, `character`, `uri`, or `path` have
            unsupported types.
    """

    if not isinstance(text, str):
        raise ValueError("PDX LSP document text must be a string.")
    _validate_lsp_position(line=line, character=character)
    _validate_lsp_document(uri=uri, path=path)
    try:
        block = _parse_pdx_lsp_block(text, path=path)
    except PDXParseError as error:
        return _lsp_hover_payload(
            uri=uri,
            path=path,
            line=line,
            character=character,
            hover=None,
            diagnostics=_lsp_diagnostics([diagnostic.to_dict() for diagnostic in error.diagnostics]),
        )

    entry = _hover_entry(block, line=line, character=character)
    hover = _entry_hover(entry) if entry is not None else None
    return _lsp_hover_payload(uri=uri, path=path, line=line, character=character, hover=hover, diagnostics=[])


def _lsp_symbols_payload(
    *,
    uri: str | None,
    path: str | Path | None,
    symbols: list[dict[str, object]],
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    path_text = str(path) if path is not None else None
    suffix = Path(path_text).suffix if path_text else ""
    return {
        "schema": LSP_SYMBOLS_SCHEMA,
        "method": "textDocument/documentSymbol",
        "language": "pdx",
        "uri": uri,
        "path": path_text,
        "file_ext": suffix,
        "ok": not diagnostics,
        "symbols": symbols if not diagnostics else [],
        "diagnostics": diagnostics,
    }


def _block_symbols(block: PDXBlock) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for entry in block.entries:
        symbol = _entry_symbol(entry)
        if symbol is not None:
            rows.append(symbol)
    return rows


def _entry_symbol(entry: PDXEntry) -> dict[str, object] | None:
    if entry.key is None:
        return None
    name = str(entry.key.val)
    symbol_range = _key_range(entry)
    symbol: dict[str, object] = {
        "name": name,
        "kind": _symbol_kind(entry),
        "range": symbol_range,
        "selectionRange": symbol_range,
    }
    if entry.op is not None:
        symbol["detail"] = entry.op
    if isinstance(entry.val, PDXBlock):
        children = _block_symbols(entry.val)
        if children:
            symbol["children"] = children
    return symbol


def _key_range(entry: PDXEntry) -> dict[str, object]:
    span = entry.key.anno.get("span", {}) if entry.key is not None else {}
    line = max(int(span.get("line", 1)) - 1, 0)
    character = max(int(span.get("column", 1)) - 1, 0)
    name = str(entry.key.val) if entry.key is not None else ""
    end_character = character + max(len(name), 1)
    return {
        "start": {"line": line, "character": character},
        "end": {"line": line, "character": end_character},
    }


def _symbol_kind(entry: PDXEntry) -> int:
    if isinstance(entry.val, PDXBlock):
        return _SYMBOL_KIND_OBJECT
    if entry.op is not None:
        return _SYMBOL_KIND_PROPERTY
    return _SYMBOL_KIND_KEY


def _hover_entry(block: PDXBlock, *, line: int, character: int) -> PDXEntry | None:
    for entry in block.entries:
        if isinstance(entry.val, PDXBlock):
            child = _hover_entry(entry.val, line=line, character=character)
            if child is not None:
                return child
        if entry.key is not None and _position_in_range(line, character, _key_range(entry)):
            return entry
    return None


def _position_in_range(line: int, character: int, row: dict[str, object]) -> bool:
    start = row["start"]
    end = row["end"]
    if not isinstance(start, dict) or not isinstance(end, dict):
        return False
    return (
        line == start.get("line")
        and line == end.get("line")
        and isinstance(start.get("character"), int)
        and isinstance(end.get("character"), int)
        and start["character"] <= character < end["character"]
    )


def _entry_hover(entry: PDXEntry) -> dict[str, object]:
    name = str(entry.key.val) if entry.key is not None else ""
    range_ = _key_range(entry)
    if isinstance(entry.val, PDXBlock):
        count = len(entry.val.entries)
        noun = "entry" if count == 1 else "entries"
        value = f"`{name}` {entry.op or '='} `{{ ... }}`\n\nPDX block entry with {count} child {noun}."
    elif isinstance(entry.val, PDXScalar):
        value = f"`{name}` {entry.op or '='} `{entry.val.to_str()}`\n\nPDX scalar entry."
    else:
        value = f"`{name}`\n\nPDX bare entry."
    return {
        "contents": {"kind": "markdown", "value": value},
        "range": range_,
    }


def format_pdx_lsp_text(
    text: str,
    *,
    uri: str | None = None,
    path: str | Path | None = None,
    indent: str = "\t",
    comments: bool = True,
) -> dict[str, object]:
    """Return LSP `textDocument/formatting` edits for PDX source text.

    Args:
        text: Current document text from the editor buffer.
        uri: Optional LSP document URI.
        path: Optional display path used for file extension metadata.
        indent: Indentation unit passed to the PDX formatter.
        comments: Whether comments should be retained in formatted output.

    Returns:
        JSON-safe LSP formatting payload with `TextEdit` rows or diagnostics.

    Raises:
        ValueError: If `text`, `uri`, `path`, or `indent` have unsupported types.
    """

    _validate_lsp_document(uri=uri, path=path)
    formatted = format_pdx_text(text, path=path, indent=indent, comments=comments)
    if not formatted["ok"]:
        return _lsp_formatting_payload(
            uri=uri,
            path=path,
            changed=False,
            edits=[],
            diagnostics=_lsp_diagnostics(formatted["diagnostics"]),
        )

    changed = bool(formatted["changed"])
    edits: list[dict[str, object]] = []
    if changed:
        edits.append(
            {
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": _document_end(text),
                },
                "newText": formatted["formatted_text"],
            }
        )
    return _lsp_formatting_payload(uri=uri, path=path, changed=changed, edits=edits, diagnostics=[])


def _lsp_diagnostics_payload(
    *,
    uri: str | None,
    path: str | Path | None,
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    path_text = str(path) if path is not None else None
    suffix = Path(path_text).suffix if path_text else ""
    return {
        "schema": LSP_DIAGNOSTICS_SCHEMA,
        "method": "textDocument/publishDiagnostics",
        "language": "pdx",
        "uri": uri,
        "path": path_text,
        "file_ext": suffix,
        "ok": not diagnostics,
        "diagnostics": diagnostics,
    }


def _lsp_formatting_payload(
    *,
    uri: str | None,
    path: str | Path | None,
    changed: bool,
    edits: list[dict[str, object]],
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    path_text = str(path) if path is not None else None
    suffix = Path(path_text).suffix if path_text else ""
    return {
        "schema": LSP_FORMATTING_SCHEMA,
        "method": "textDocument/formatting",
        "language": "pdx",
        "uri": uri,
        "path": path_text,
        "file_ext": suffix,
        "ok": not diagnostics,
        "changed": changed if not diagnostics else False,
        "edits": edits if not diagnostics else [],
        "diagnostics": diagnostics,
    }


def _lsp_hover_payload(
    *,
    uri: str | None,
    path: str | Path | None,
    line: int,
    character: int,
    hover: dict[str, object] | None,
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    path_text = str(path) if path is not None else None
    suffix = Path(path_text).suffix if path_text else ""
    return {
        "schema": LSP_HOVER_SCHEMA,
        "method": "textDocument/hover",
        "language": "pdx",
        "uri": uri,
        "path": path_text,
        "file_ext": suffix,
        "ok": not diagnostics,
        "position": {"line": line, "character": character},
        "hover": hover if not diagnostics else None,
        "diagnostics": diagnostics,
    }


def _lsp_completion_payload(
    *,
    uri: str | None,
    path: str | Path | None,
    line: int,
    character: int,
    prefix: str,
    items: list[dict[str, object]],
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    path_text = str(path) if path is not None else None
    suffix = Path(path_text).suffix if path_text else ""
    return {
        "schema": LSP_COMPLETION_SCHEMA,
        "method": "textDocument/completion",
        "language": "pdx",
        "uri": uri,
        "path": path_text,
        "file_ext": suffix,
        "ok": not diagnostics,
        "position": {"line": line, "character": character},
        "prefix": prefix,
        "isIncomplete": False,
        "items": items if not diagnostics else [],
        "diagnostics": diagnostics,
    }


def _lsp_semantic_tokens_payload(
    *,
    uri: str | None,
    path: str | Path | None,
    tokens: list[dict[str, object]],
    data: list[int],
    diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    path_text = str(path) if path is not None else None
    suffix = Path(path_text).suffix if path_text else ""
    return {
        "schema": LSP_SEMANTIC_TOKENS_SCHEMA,
        "method": "textDocument/semanticTokens/full",
        "language": "pdx",
        "uri": uri,
        "path": path_text,
        "file_ext": suffix,
        "ok": not diagnostics,
        "legend": {"tokenTypes": list(_SEMANTIC_TOKEN_TYPES), "tokenModifiers": list(_SEMANTIC_TOKEN_MODIFIERS)},
        "data": data if not diagnostics else [],
        "tokens": tokens if not diagnostics else [],
        "diagnostics": diagnostics,
    }


def _completion_context(text: str, *, line: int, character: int, offset: int | None) -> tuple[str, tuple[str, ...]]:
    if offset is not None:
        return _completion_context_at_offset(text, offset=offset)
    return _completion_context_from_position(text, line=line, character=character)


def _completion_context_at_offset(text: str, *, offset: int) -> tuple[str, tuple[str, ...]]:
    cursor = min(offset, len(text))
    line_start = text.rfind("\n", 0, cursor) + 1
    token = text[line_start:cursor]
    index = len(token)
    while index > 0 and _is_completion_char(token[index - 1]):
        index -= 1
    prefix = token[index:]
    stack = _completion_context_stack_before_offset(text, offset=cursor)
    return prefix, stack


def _completion_context_stack_before_offset(text: str, *, offset: int) -> tuple[str, ...]:
    ancestors: list[str] = []
    depth = 0
    index = min(offset, len(text)) - 1
    scanned = 0
    while index >= 0 and scanned < _COMPLETION_CONTEXT_SCAN_LIMIT:
        char = text[index]
        if char == "}":
            depth += 1
        elif char == "{":
            if depth > 0:
                depth -= 1
            else:
                key = _key_before_open_brace(text, index)
                if key:
                    ancestors.append(key)
                    if _completion_keyword_kind(tuple(reversed(ancestors)), path=None) is not None:
                        break
                    if len(ancestors) >= _COMPLETION_CONTEXT_MAX_DEPTH:
                        break
        index -= 1
        scanned += 1
    return tuple(reversed(ancestors))


def _key_before_open_brace(text: str, brace_index: int) -> str:
    index = brace_index - 1
    while index >= 0 and text[index].isspace():
        index -= 1
    while index >= 0 and text[index] in {"=", "!", "<", ">"}:
        index -= 1
    while index >= 0 and text[index].isspace():
        index -= 1
    end = index + 1
    while index >= 0 and _is_completion_char(text[index]):
        index -= 1
    return text[index + 1 : end].lower()


def _completion_context_from_position(text: str, *, line: int, character: int) -> tuple[str, tuple[str, ...]]:
    stack: list[str] = []
    token = ""
    last_token = ""
    pending_key: str | None = None
    in_comment = False
    in_string = False
    escape = False
    current_line = 0
    current_character = 0
    reached_position = False
    for char in text:
        if current_line == line and (current_character >= character or char == "\n"):
            reached_position = True
            break
        if in_comment:
            if char == "\n":
                in_comment = False
        elif in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
        elif char == "#":
            last_token = token.strip().lower() or last_token
            token = ""
            in_comment = True
        elif char == '"':
            last_token = token.strip().lower() or last_token
            token = ""
            in_string = True
        elif _is_completion_char(char):
            token += char
        elif char == "=":
            pending_key = token.strip().lower() or last_token or pending_key
            token = ""
            last_token = ""
        elif char == "{":
            key = (pending_key or token or last_token).strip().lower()
            if key:
                stack.append(key)
            pending_key = None
            token = ""
            last_token = ""
        elif char == "}":
            if stack:
                stack.pop()
            pending_key = None
            token = ""
            last_token = ""
        elif char.isspace():
            last_token = token.strip().lower() or last_token
            token = ""
        else:
            pending_key = None
            last_token = ""
            token = ""
        if char == "\n":
            current_line += 1
            current_character = 0
        else:
            current_character += 1
    if not reached_position and current_line == line:
        reached_position = True
    prefix = token if all(_is_completion_char(char) for char in token) else ""
    return (prefix if reached_position else ""), tuple(stack)


def _is_completion_char(char: str) -> bool:
    return char.isalnum() or char in {"_", "-", ".", ":", "@"}


def _completion_keyword_kind(stack: tuple[str, ...], *, path: str | Path | None) -> str | None:
    if any(key in _MODIFIER_CONTEXT_KEYS for key in stack) or (_path_implies_modifier_context(path) and stack):
        return "modifier"
    if any(key in _TRIGGER_CONTEXT_KEYS for key in reversed(stack)):
        return "trigger"
    if any(key in _EFFECT_CONTEXT_KEYS for key in reversed(stack)):
        return "effect"
    return None


def _path_implies_modifier_context(path: str | Path | None) -> bool:
    if path is None:
        return False
    normalized = str(path).replace("\\", "/")
    return "/common/modifiers/" in normalized or "/modules/modifier/" in normalized or normalized.startswith("common/modifiers/")


def _remaining_completion_limit(limit: int | None, used: int) -> int | None:
    if limit is None:
        return None
    return max(limit - used, 0)


def _dedupe_completion_items(items: list[dict[str, object]], *, limit: int | None) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for item in items:
        label = item.get("label")
        if not isinstance(label, str) or label in seen:
            continue
        seen.add(label)
        rows.append(item)
        if limit is not None and len(rows) >= limit:
            break
    return rows


def _semantic_tokens(block: PDXBlock) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    _append_block_semantic_tokens(block, rows)
    return sorted(rows, key=lambda row: (int(row["line"]), int(row["character"]), int(row["length"])))


def _append_block_semantic_tokens(block: PDXBlock, rows: list[dict[str, object]]) -> None:
    for entry in block.entries:
        if entry.key is not None:
            token_type = "class" if isinstance(entry.val, PDXBlock) else "property"
            row = _semantic_token_row(entry.key, token_type)
            if row is not None:
                rows.append(row)
        if isinstance(entry.val, PDXScalar):
            row = _semantic_token_row(entry.val, _scalar_semantic_token_type(entry.val))
            if row is not None:
                rows.append(row)
        elif isinstance(entry.val, PDXBlock):
            _append_block_semantic_tokens(entry.val, rows)


def _semantic_token_row(scalar: PDXScalar, token_type: str) -> dict[str, object] | None:
    span = scalar.anno.get("span", {})
    if not isinstance(span, dict):
        return None
    line = int(span.get("line", 0)) - 1
    character = int(span.get("column", 0)) - 1
    if line < 0 or character < 0:
        return None
    return {
        "line": line,
        "character": character,
        "length": max(len(scalar.to_str()), 1),
        "token_type": token_type,
        "token_modifiers": [],
    }


def _scalar_semantic_token_type(scalar: PDXScalar) -> str:
    if scalar.type == SCALAR_NUM:
        return "number"
    if scalar.type == SCALAR_STR:
        return "string"
    if scalar.type == SCALAR_VAR:
        return "variable"
    return "enum"


def _encode_semantic_tokens(tokens: list[dict[str, object]]) -> list[int]:
    data: list[int] = []
    prev_line = 0
    prev_character = 0
    for token in tokens:
        line = int(token["line"])
        character = int(token["character"])
        delta_line = line - prev_line
        delta_character = character - prev_character if delta_line == 0 else character
        token_type = str(token["token_type"])
        data.extend(
            [
                delta_line,
                delta_character,
                int(token["length"]),
                _SEMANTIC_TOKEN_TYPE_INDEX[token_type],
                0,
            ]
        )
        prev_line = line
        prev_character = character
    return data


def _validate_lsp_document(*, uri: str | None, path: str | Path | None) -> None:
    if uri is not None and not isinstance(uri, str):
        raise ValueError("LSP document URI must be a string when provided.")
    if path is not None and not isinstance(path, (str, Path)):
        raise ValueError("LSP document path must be a string or Path when provided.")


def _validate_lsp_position(*, line: int, character: int) -> None:
    if type(line) is not int or line < 0:
        raise ValueError("LSP hover line must be a non-negative integer.")
    if type(character) is not int or character < 0:
        raise ValueError("LSP hover character must be a non-negative integer.")


def _validate_lsp_offset(*, offset: int | None, text: str) -> None:
    if offset is None:
        return
    if type(offset) is not int or offset < 0 or offset > len(text):
        raise ValueError("LSP completion offset must be an integer within the document text bounds when provided.")


def _document_end(text: str) -> dict[str, int]:
    line = 0
    character = 0
    for char in text:
        if char == "\n":
            line += 1
            character = 0
        else:
            character += 1
    return {"line": line, "character": character}


def _lsp_diagnostics(diagnostics: object) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for diagnostic in diagnostics if isinstance(diagnostics, list) else []:
        if not isinstance(diagnostic, dict):
            continue
        line = max(int(diagnostic.get("line", 1)) - 1, 0)
        character = max(int(diagnostic.get("column", 1)) - 1, 0)
        rows.append(
            {
                "range": {
                    "start": {"line": line, "character": character},
                    "end": {"line": line, "character": character + 1},
                },
                "severity": _severity(diagnostic.get("severity")),
                "code": diagnostic.get("code"),
                "source": "paradev.pdx",
                "message": diagnostic.get("message", ""),
            }
        )
    return rows


def _severity(severity: Any) -> int:
    if isinstance(severity, str):
        return _LSP_SEVERITY.get(severity.lower(), 1)
    return 1


def _parse_pdx_lsp_block(text: str, *, path: str | Path | None) -> PDXBlock:
    path_text = str(path) if path is not None else None
    if len(text) > _PARSED_LSP_CACHE_MAX_BYTES:
        block = PDXBlock.from_str(text)
        if path_text is not None:
            block.file_ext = Path(path_text).suffix or None
        return block
    return _cached_pdx_lsp_block(text, path_text)


@lru_cache(maxsize=_PARSED_LSP_CACHE_SIZE)
def _cached_pdx_lsp_block(text: str, path_text: str | None) -> PDXBlock:
    block = PDXBlock.from_str(text)
    if path_text is not None:
        block.file_ext = Path(path_text).suffix or None
    return block
