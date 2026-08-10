"""SDK helpers for PDX parse payloads."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from typing_extensions import TypedDict

from paradev._api_table import api_symbol_indexes, api_table_selection
from paradev._api_table_markdown import api_surface_reference_markdown
from paradev.pdx import PDXBlock, PDXParseError, PDXTokenizer, TokenType

PDX_PARSE_SCHEMA = "paradev.pdx.parse.v1"
PDX_FORMAT_SCHEMA = "paradev.pdx.format.v1"
PDX_API_TABLE_SCHEMA = "paradev.sdk.pdx-api-table.v1"
_PDX_API_INDEX_NAMES = ("surface_index", "feature_index")
_PDX_API_STANDARD_FIELDS = (
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


class PdxApiRow(TypedDict):
    """One public PDX parse/format API table row."""

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


class PdxApiTable(TypedDict):
    """Generated API-standard table for PDX parse and format surfaces."""

    schema: str
    row_count: int
    surface_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    rows: list[PdxApiRow]


PDX_API_TABLE_ROWS: tuple[PdxApiRow, ...] = (
    {
        "symbol": "PDX_PARSE_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "parse",
        "inputs": "none",
        "returns": PDX_PARSE_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_PARSE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "PDX_FORMAT_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "format",
        "inputs": "none",
        "returns": PDX_FORMAT_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_FORMAT_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "PDX_API_TABLE_SCHEMA",
        "kind": "constant",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": PDX_API_TABLE_SCHEMA,
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "PDX_API_TABLE_ROWS",
        "kind": "constant",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "tuple[PdxApiRow, ...]",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "PdxApiRow",
        "kind": "TypedDict",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "symbol, kind, layer, feature, inputs, returns, raises, registry_seam, surface, payload_schema, doc_page, test_anchor",
        "returns": "PDX API table row schema",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "PdxApiTable",
        "kind": "TypedDict",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "schema, row_count, surface_index, feature_index, rows",
        "returns": "PDX API table schema",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "get_pdx_api_selection",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "PdxApiTable | PdxApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_pdx_api_selection.py::test_pdx_api_selection_returns_table_row_and_index_projection",
    },
    {
        "symbol": "parse_pdx_file",
        "kind": "function",
        "layer": "sdk",
        "feature": "parse",
        "inputs": "path, include_dump=False, include_tokens=False",
        "returns": "PDX parse payload",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_PARSE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_parse_outputs_pdx_projection_json",
    },
    {
        "symbol": "format_pdx_text",
        "kind": "function",
        "layer": "sdk",
        "feature": "format",
        "inputs": 'text, path=None, indent="\\t", comments=True',
        "returns": "PDX format payload",
        "raises": "ValueError on non-string text or indent",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_FORMAT_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "format_pdx_file",
        "kind": "function",
        "layer": "sdk",
        "feature": "format",
        "inputs": 'path, indent="\\t", comments=True, write=False',
        "returns": "PDX format payload",
        "raises": "ValueError on non-string indent",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_FORMAT_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_format_cli_previews_and_writes_pdx_file",
    },
    {
        "symbol": "get_pdx_api_table",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "PdxApiTable",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "render_pdx_api_reference_markdown",
        "kind": "function",
        "layer": "sdk",
        "feature": "api-table",
        "inputs": "none",
        "returns": "Markdown PDX API reference",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "paradev pdx-api",
        "kind": "command",
        "layer": "cli",
        "feature": "api-table",
        "inputs": "--json",
        "returns": "PdxApiTable",
        "raises": "typer.BadParameter when combined selectors are invalid",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_pdx_api_cli_outputs_table_json",
    },
    {
        "symbol": "paradev pdx-api --markdown",
        "kind": "command projection",
        "layer": "cli",
        "feature": "api-table",
        "inputs": "none",
        "returns": "Markdown PDX API reference",
        "raises": "typer.BadParameter when combined with --json",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_pdx_api_cli_outputs_reference_markdown",
    },
    {
        "symbol": "paradev parse",
        "kind": "command",
        "layer": "cli",
        "feature": "parse",
        "inputs": "path, --dump, --tokens, --json",
        "returns": "PDX parse payload",
        "raises": "exit 1 when diagnostics are returned",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": PDX_PARSE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_parse_outputs_pdx_projection_json",
    },
    {
        "symbol": "paradev format",
        "kind": "command",
        "layer": "cli",
        "feature": "format",
        "inputs": "path, --indent, --comments/--no-comments, --write, --json",
        "returns": "formatted text or PDX format payload",
        "raises": "exit 1 when diagnostics are returned",
        "registry_seam": "Typer command registry",
        "surface": "cli",
        "payload_schema": PDX_FORMAT_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_format_cli_previews_and_writes_pdx_file",
    },
    {
        "symbol": "GET /pdx/parse",
        "kind": "REST route",
        "layer": "rest",
        "feature": "parse",
        "inputs": "path, include_dump=False, include_tokens=False",
        "returns": "PDX parse payload",
        "raises": "",
        "registry_seam": "OpenAPI path /pdx/parse",
        "surface": "rest",
        "payload_schema": PDX_PARSE_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "POST /pdx/format",
        "kind": "REST route",
        "layer": "rest",
        "feature": "format",
        "inputs": 'path, indent="\\t", comments=True, write=False',
        "returns": "PDX format payload",
        "raises": "",
        "registry_seam": "OpenAPI path /pdx/format",
        "surface": "rest",
        "payload_schema": PDX_FORMAT_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "GET /pdx-api",
        "kind": "REST route",
        "layer": "rest",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "PdxApiTable | PdxApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "OpenAPI path /pdx-api",
        "surface": "rest",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_pdx_api_surface_selectors.py::test_pdx_api_table_lists_rest_and_mcp_selector_surfaces",
    },
    {
        "symbol": "pdx_parse",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "parse",
        "inputs": "path, include_dump=False, include_tokens=False",
        "returns": "PDX parse payload",
        "raises": "",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "payload_schema": PDX_PARSE_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "pdx_format",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "format",
        "inputs": 'path, indent="\\t", comments=True, write=False',
        "returns": "PDX format payload",
        "raises": "",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "payload_schema": PDX_FORMAT_SCHEMA,
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces",
    },
    {
        "symbol": "pdx_api",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "api-table",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "PdxApiTable | PdxApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "payload_schema": PDX_API_TABLE_SCHEMA,
        "doc_page": "docs/user-manual/pdx-api-reference.md",
        "test_anchor": "tests/test_pdx_api_surface_selectors.py::test_pdx_api_table_lists_rest_and_mcp_selector_surfaces",
    },
)


def get_pdx_api_table() -> PdxApiTable:
    """Return the API-standard table for PDX parse and format surfaces.

    Returns:
        JSON-safe API table with copied rows, plus grouped indexes for surface
        and feature audits.
    """

    rows = [dict(row) for row in PDX_API_TABLE_ROWS]
    surface_index, feature_index = api_symbol_indexes(rows, "surface", "feature")
    return {
        "schema": PDX_API_TABLE_SCHEMA,
        "row_count": len(rows),
        "surface_index": surface_index,
        "feature_index": feature_index,
        "rows": rows,
    }


def get_pdx_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> PdxApiTable | PdxApiRow | list[str]:
    """Return the full PDX API table, one row, or one index bucket.

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
        PdxApiTable | PdxApiRow | list[str],
        api_table_selection(
            get_pdx_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_PDX_API_INDEX_NAMES,
        ),
    )


def render_pdx_api_reference_markdown() -> str:
    """Render the PDX parse/format API table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/pdx-api-reference.md`. The content is generated from
        `get_pdx_api_table()` so SDK, CLI, REST, and MCP parse/format and
        selector docs stay aligned.
    """

    table = get_pdx_api_table()
    return api_surface_reference_markdown(
        title="PDX API Reference",
        source="paradev.sdk.get_pdx_api_table()",
        regenerate_when="Regenerate this file whenever the PDX API table changes:",
        command="rtk uv run paradev pdx-api --markdown > docs/user-manual/pdx-api-reference.md",
        table=table,
        fields=_PDX_API_STANDARD_FIELDS,
    )


def parse_pdx_file(
    path: str | Path,
    *,
    include_dump: bool = False,
    include_tokens: bool = False,
) -> dict[str, object]:
    """Return a JSON-safe PDX parse payload for one source file.

    Args:
        path: PDX source file path.
        include_dump: Include the lossless `PDXBlock.dump()` payload on success.
        include_tokens: Include lexer token rows on success.

    Returns:
        JSON-safe parse payload with data or diagnostics.
    """

    source = Path(path).expanduser().resolve()
    try:
        text = source.read_text(encoding="utf-8-sig", errors="replace")
        block = PDXBlock.from_str(text)
        block.file_ext = source.suffix or None
    except FileNotFoundError:
        return _pdx_parse_payload(
            source,
            diagnostics=[_pdx_sdk_diagnostic("pdx.source_not_found", f"PDX source file not found: {source}.")],
        )
    except OSError as error:
        message = f"PDX source file cannot be read: {source}."
        reason = error.strerror or str(error)
        if reason:
            message = f"{message} {reason}."
        return _pdx_parse_payload(source, diagnostics=[_pdx_sdk_diagnostic("pdx.source_unreadable", message)])
    except PDXParseError as error:
        return _pdx_parse_payload(source, diagnostics=[diagnostic.to_dict() for diagnostic in error.diagnostics])
    tokens = None
    if include_tokens:
        token_rows = PDXTokenizer(text).tokenize()
        tokens = [token.to_dict() for token in token_rows if token.type is not TokenType.EOF]
    return _pdx_parse_payload(
        source,
        data=block.to_dict(),
        dump=block.dump() if include_dump else None,
        tokens=tokens,
    )


def format_pdx_text(
    text: str,
    *,
    path: str | Path | None = None,
    indent: str = "\t",
    comments: bool = True,
) -> dict[str, object]:
    """Format PDX source text without reading or writing a file.

    Args:
        text: PDX source text to format.
        path: Optional display path used for file extension metadata.
        indent: Indentation unit passed to the AST formatter.
        comments: Whether comments should be retained in formatted output.

    Returns:
        JSON-safe formatter payload with formatted text or diagnostics.

    Raises:
        ValueError: If `text` or `indent` are not strings.
    """

    if not isinstance(text, str):
        raise ValueError("PDX format text must be a string.")
    if not isinstance(indent, str):
        raise ValueError("PDX format indent must be a string.")
    try:
        block = PDXBlock.from_str(text)
        if path is not None:
            block.file_ext = Path(path).suffix or None
        formatted = block.to_str(indent=indent, comments=comments)
    except PDXParseError as error:
        return _pdx_format_payload(
            path,
            formatted_text=None,
            changed=False,
            written=False,
            indent=indent,
            comments=comments,
            diagnostics=[diagnostic.to_dict() for diagnostic in error.diagnostics],
        )
    return _pdx_format_payload(
        path,
        formatted_text=formatted,
        changed=formatted != text,
        written=False,
        indent=indent,
        comments=comments,
    )


def format_pdx_file(
    path: str | Path,
    *,
    indent: str = "\t",
    comments: bool = True,
    write: bool = False,
) -> dict[str, object]:
    """Format one PDX source file and optionally write the result.

    Args:
        path: PDX source file path.
        indent: Indentation unit passed to the AST formatter.
        comments: Whether comments should be retained in formatted output.
        write: Whether to replace the file with formatted text when parsing
            succeeds and the formatter changes the text.

    Returns:
        JSON-safe formatter payload with formatted text, write status, and
        diagnostics.

    Raises:
        ValueError: If `indent` is not a string.
    """

    if not isinstance(indent, str):
        raise ValueError("PDX format indent must be a string.")
    source = Path(path).expanduser().resolve()
    try:
        text = source.read_text(encoding="utf-8-sig", errors="replace")
    except FileNotFoundError:
        return _pdx_format_payload(
            source,
            formatted_text=None,
            changed=False,
            written=False,
            indent=indent,
            comments=comments,
            diagnostics=[_pdx_sdk_diagnostic("pdx.source_not_found", f"PDX source file not found: {source}.")],
        )
    except OSError as error:
        message = f"PDX source file cannot be read: {source}."
        reason = error.strerror or str(error)
        if reason:
            message = f"{message} {reason}."
        return _pdx_format_payload(
            source,
            formatted_text=None,
            changed=False,
            written=False,
            indent=indent,
            comments=comments,
            diagnostics=[_pdx_sdk_diagnostic("pdx.source_unreadable", message)],
        )
    payload = format_pdx_text(text, path=source, indent=indent, comments=comments)
    written = False
    if write and payload["ok"] and payload["changed"]:
        try:
            source.write_text(str(payload["formatted_text"]), encoding="utf-8")
            written = True
        except OSError as error:
            message = f"PDX source file cannot be written: {source}."
            reason = error.strerror or str(error)
            if reason:
                message = f"{message} {reason}."
            return _pdx_format_payload(
                source,
                formatted_text=None,
                changed=False,
                written=False,
                indent=indent,
                comments=comments,
                diagnostics=[_pdx_sdk_diagnostic("pdx.source_unwritable", message)],
            )
    payload["written"] = written
    return payload


def _pdx_parse_payload(
    path: Path,
    *,
    data: object = None,
    dump: object = None,
    tokens: object = None,
    diagnostics: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    diagnostic_rows = diagnostics or []
    payload: dict[str, object] = {
        "schema": PDX_PARSE_SCHEMA,
        "path": str(path),
        "file_ext": path.suffix,
        "ok": not diagnostic_rows,
        "data": data if not diagnostic_rows else None,
        "diagnostics": diagnostic_rows,
    }
    if dump is not None and not diagnostic_rows:
        payload["dump"] = dump
    if tokens is not None and not diagnostic_rows:
        payload["tokens"] = tokens
    return payload


def _pdx_format_payload(
    path: str | Path | None,
    *,
    formatted_text: str | None,
    changed: bool,
    written: bool,
    indent: str,
    comments: bool,
    diagnostics: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    diagnostic_rows = diagnostics or []
    path_text = str(path) if path is not None else None
    suffix = Path(path_text).suffix if path_text else ""
    return {
        "schema": PDX_FORMAT_SCHEMA,
        "path": path_text,
        "file_ext": suffix,
        "ok": not diagnostic_rows,
        "formatted_text": formatted_text if not diagnostic_rows else None,
        "changed": changed if not diagnostic_rows else False,
        "written": written if not diagnostic_rows else False,
        "indent": indent,
        "comments": comments,
        "diagnostics": diagnostic_rows,
    }


def _pdx_sdk_diagnostic(code: str, message: str) -> dict[str, Any]:
    return {"code": code, "message": message, "severity": "error"}
