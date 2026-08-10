"""Architecture contracts for ParaDev surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from typing_extensions import TypedDict

from paradev._api_table import api_symbol_indexes, api_table_selection
from paradev._api_table_markdown import api_surface_reference_markdown

ARCHITECTURE_API_TABLE_SCHEMA = "paradev.sdk.architecture-api-table.v1"
_ARCHITECTURE_API_INDEX_NAMES = ("surface_index",)
_ARCHITECTURE_API_STANDARD_FIELDS = (
    "symbol",
    "kind",
    "layer",
    "surface",
    "inputs",
    "returns",
    "raises",
    "registry_seam",
    "doc_page",
    "test_anchor",
)


class ArchitectureApiRow(TypedDict):
    """One public architecture API table row."""

    symbol: str
    kind: str
    layer: str
    inputs: str
    returns: str
    raises: str
    registry_seam: str
    surface: str
    doc_page: str
    test_anchor: str


class ArchitectureApiTable(TypedDict):
    """Generated API-standard table for the architecture graph surface."""

    schema: str
    row_count: int
    surface_index: dict[str, list[str]]
    rows: list[ArchitectureApiRow]


ARCHITECTURE_API_TABLE_ROWS: tuple[ArchitectureApiRow, ...] = (
    {
        "symbol": "SurfaceSpec",
        "kind": "dataclass",
        "layer": "sdk",
        "inputs": "identifier, title, runtime, path, role, status, depends_on",
        "returns": "immutable surface descriptor",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface",
    },
    {
        "symbol": "SurfaceSpec.to_dict",
        "kind": "method",
        "layer": "sdk",
        "inputs": "self",
        "returns": "JSON-safe surface row",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface",
    },
    {
        "symbol": "ArchitectureSpec",
        "kind": "dataclass",
        "layer": "sdk",
        "inputs": "product, primary_runtime, surfaces, paths",
        "returns": "immutable architecture graph",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface",
    },
    {
        "symbol": "ArchitectureSpec.surface",
        "kind": "method",
        "layer": "sdk",
        "inputs": "identifier: str",
        "returns": "SurfaceSpec",
        "raises": "KeyError on unknown surface id",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths",
    },
    {
        "symbol": "ArchitectureSpec.path_chains",
        "kind": "method",
        "layer": "sdk",
        "inputs": "self",
        "returns": "list[list[str]]",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths",
    },
    {
        "symbol": "ArchitectureSpec.to_dict",
        "kind": "method",
        "layer": "sdk",
        "inputs": "self",
        "returns": "JSON-safe architecture graph",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths",
    },
    {
        "symbol": "get_architecture_spec",
        "kind": "function",
        "layer": "sdk",
        "inputs": "none",
        "returns": "ArchitectureSpec",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_surfaces_cover_requested_paths",
    },
    {
        "symbol": "get_architecture_api_selection",
        "kind": "function",
        "layer": "sdk",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "ArchitectureApiTable | ArchitectureApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/user-manual/architecture-api-reference.md",
        "test_anchor": "tests/test_architecture_api_selection.py::test_architecture_api_selection_returns_table_row_and_index_projection",
    },
    {
        "symbol": "get_architecture_api_table",
        "kind": "function",
        "layer": "sdk",
        "inputs": "none",
        "returns": "ArchitectureApiTable",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/user-manual/architecture-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface",
    },
    {
        "symbol": "render_architecture_api_reference_markdown",
        "kind": "function",
        "layer": "sdk",
        "inputs": "none",
        "returns": "Markdown architecture API reference",
        "raises": "",
        "registry_seam": "none",
        "surface": "sdk",
        "doc_page": "docs/user-manual/architecture-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface",
    },
    {
        "symbol": "paradev architecture",
        "kind": "command",
        "layer": "cli",
        "inputs": "--json",
        "returns": "ArchitectureSpec.to_dict()",
        "raises": "typer.BadParameter on invalid selector combinations",
        "registry_seam": "none",
        "surface": "cli",
        "doc_page": "docs/user-manual/architecture-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_architecture_cli_outputs_api_table_json",
    },
    {
        "symbol": "paradev architecture --api-table",
        "kind": "command projection",
        "layer": "cli",
        "inputs": "--json",
        "returns": "ArchitectureApiTable",
        "raises": "typer.BadParameter on invalid selector combinations",
        "registry_seam": "none",
        "surface": "cli",
        "doc_page": "docs/user-manual/architecture-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_architecture_cli_outputs_api_table_json",
    },
    {
        "symbol": "paradev architecture --api-table-markdown",
        "kind": "command projection",
        "layer": "cli",
        "inputs": "none",
        "returns": "Markdown architecture API reference",
        "raises": "typer.BadParameter when combined with selectors or --json",
        "registry_seam": "none",
        "surface": "cli",
        "doc_page": "docs/user-manual/architecture-api-reference.md",
        "test_anchor": "tests/test_cli.py::test_architecture_cli_outputs_api_table_markdown",
    },
    {
        "symbol": "GET /architecture",
        "kind": "REST route",
        "layer": "rest",
        "inputs": "none",
        "returns": "ArchitectureSpec.to_dict()",
        "raises": "",
        "registry_seam": "OpenAPI path /architecture",
        "surface": "rest",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server",
    },
    {
        "symbol": "list_surfaces",
        "kind": "MCP tool",
        "layer": "mcp",
        "inputs": "none",
        "returns": "ArchitectureSpec.to_dict()",
        "raises": "",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface",
    },
    {
        "symbol": "describe_architecture",
        "kind": "MCP tool",
        "layer": "mcp",
        "inputs": "none",
        "returns": "ArchitectureSpec.to_dict()",
        "raises": "",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "doc_page": "docs/architecture/interfaces.md",
        "test_anchor": "tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface",
    },
    {
        "symbol": "architecture_api",
        "kind": "MCP tool",
        "layer": "mcp",
        "inputs": "symbol=None, index_name=None, key=None",
        "returns": "ArchitectureApiTable | ArchitectureApiRow | list[str]",
        "raises": "ValueError or KeyError on unsupported selectors",
        "registry_seam": "MCP tool registry",
        "surface": "mcp",
        "doc_page": "docs/user-manual/architecture-api-reference.md",
        "test_anchor": "tests/test_mcp_architecture_api_selectors.py::test_mcp_contract_exposes_architecture_api_selector_tool",
    },
)


@dataclass(frozen=True)
class SurfaceSpec:
    """One ParaDev integration surface.

    Args:
        identifier: Stable machine identifier.
        title: Human-readable name.
        runtime: Runtime family for this surface.
        path: Repository path that owns the surface scaffold.
        role: Short responsibility summary.
        status: Current maturity label.
        depends_on: Surface identifiers this surface depends on.
    """

    identifier: str
    title: str
    runtime: str
    path: str
    role: str
    status: str = "scaffold"
    depends_on: tuple[str, ...] = ("sdk",)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe projection."""

        return {
            "identifier": self.identifier,
            "title": self.title,
            "runtime": self.runtime,
            "path": self.path,
            "role": self.role,
            "status": self.status,
            "depends_on": list(self.depends_on),
        }


@dataclass(frozen=True)
class ArchitectureSpec:
    """SDK-owned architecture graph for all ParaDev surfaces.

    Args:
        product: Product name.
        primary_runtime: Runtime that owns domain logic.
        surfaces: Supported surfaces.
        paths: Requested runtime dependency chains.
    """

    product: str
    primary_runtime: str
    surfaces: tuple[SurfaceSpec, ...]
    paths: tuple[tuple[str, ...], ...]

    def surface(self, identifier: str) -> SurfaceSpec:
        """Load one surface by identifier.

        Args:
            identifier: Surface identifier.

        Returns:
            Matching surface spec.

        Raises:
            KeyError: If the identifier is not part of the architecture graph.
        """

        for surface in self.surfaces:
            if surface.identifier == identifier:
                return surface
        known = ", ".join(surface.identifier for surface in self.surfaces)
        raise KeyError(f"unknown ParaDev surface {identifier!r}; expected one of: {known}")

    def path_chains(self) -> list[list[str]]:
        """Return requested runtime paths as JSON-safe lists."""

        return [list(path) for path in self.paths]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe projection."""

        return {
            "product": self.product,
            "primary_runtime": self.primary_runtime,
            "surfaces": [surface.to_dict() for surface in self.surfaces],
            "paths": self.path_chains(),
        }


SURFACES = (
    SurfaceSpec(
        identifier="sdk",
        title="SDK API",
        runtime="python",
        path="src/paradev/sdk",
        role="Common Python API, architecture graph, project view models, and future domain entry points.",
        depends_on=(),
    ),
    SurfaceSpec(
        identifier="pdx",
        title="PDX Core",
        runtime="python",
        path="src/paradev/pdx",
        role="Future parser, AST, formatter, diagnostics, and syntax utilities.",
    ),
    SurfaceSpec(
        identifier="project",
        title="Project System",
        runtime="python",
        path="src/paradev/project",
        role="Future project discovery, manifests, local workspace boundary, and source ownership.",
    ),
    SurfaceSpec(
        identifier="build",
        title="Build Graph",
        runtime="python",
        path="src/paradev/build",
        role="Future deterministic build graph, validation stages, and artifact manifests.",
    ),
    SurfaceSpec(
        identifier="hoi4",
        title="HOI4 Game Package",
        runtime="python",
        path="src/paradev/games/hoi4",
        role="Future HOI4 entity families, game profiles, asset rules, and map contracts.",
    ),
    SurfaceSpec(
        identifier="hb",
        title="HeavenBase Workspace",
        runtime="python-heavenbase",
        path="src/paradev/hb",
        role="Future structured metadata, search, memory, and HeavenBase-backed indexes.",
    ),
    SurfaceSpec(
        identifier="mcp",
        title="MCP Toolkit",
        runtime="heavenbase-mcp",
        path="src/paradev/surfaces/mcp.py",
        role="HeavenBase-provided MCP tools over SDK operations.",
    ),
    SurfaceSpec(
        identifier="cli",
        title="Typer + Rich CLI",
        runtime="python-typer-rich",
        path="src/paradev/cli.py",
        role="Human and script entry point over the SDK API.",
    ),
    SurfaceSpec(
        identifier="rest",
        title="REST API",
        runtime="python-fastapi",
        path="src/paradev/surfaces/rest.py",
        role="Optional local HTTP API for desktop and external clients.",
    ),
    SurfaceSpec(
        identifier="openapi",
        title="OpenAPI Contract",
        runtime="openapi-json",
        path="src/paradev/api",
        role="REST contract export for generated clients and frontend integration.",
    ),
    SurfaceSpec(
        identifier="bundle",
        title="Wheel-hosted Python Application",
        runtime="python-wheel-loopback",
        path="src/paradev/gui.py",
        role="Installed Python application host for the loopback API and packaged frontend assets.",
    ),
    SurfaceSpec(
        identifier="frontend",
        title="TypeScript Frontend",
        runtime="typescript-react",
        path="apps/desktop/src",
        role="Code-native desktop GUI shell and future generated SDK/REST clients.",
    ),
    SurfaceSpec(
        identifier="desktop",
        title="ParaDev Desktop App",
        runtime="python-loopback-system-webview",
        path="src/paradev/gui.py",
        role="System-WebView desktop app over the wheel-hosted Python loopback service.",
        depends_on=("sdk", "rest", "openapi", "bundle", "frontend"),
    ),
    SurfaceSpec(
        identifier="lsp",
        title="PDX LSP",
        runtime="python-lsp",
        path="src/paradev/lsp",
        role="Stdio JSON-RPC language server for PDX diagnostics, symbols, hovers, formatting, completion, and semantic tokens.",
    ),
    SurfaceSpec(
        identifier="vscode",
        title="VS Code Extension",
        runtime="typescript-vscode",
        path="packages/vscode-paradev",
        role="Thin editor client that launches the ParaDev PDX LSP and can reuse CLI and REST contracts.",
        depends_on=("sdk", "lsp", "cli", "rest"),
    ),
)

PATHS = (
    ("python-backend", "sdk-api"),
    ("python-backend", "sdk-api", "mcp"),
    ("python-backend", "sdk-api", "typer-rich-cli"),
    ("python-backend", "sdk-api", "vscode-plugin", "lsp"),
    (
        "python-backend",
        "sdk-api",
        "rest-api",
        "openapi-contract",
        "python-wheel-loopback-host",
        "typescript-frontend",
        "system-webview",
        "desktop-app",
    ),
)

ARCHITECTURE = ArchitectureSpec(
    product="ParaDev",
    primary_runtime="python-sdk",
    surfaces=SURFACES,
    paths=PATHS,
)


def get_architecture_spec() -> ArchitectureSpec:
    """Return the SDK-owned ParaDev architecture graph."""

    return ARCHITECTURE


def get_architecture_api_table() -> ArchitectureApiTable:
    """Return the API-standard table for the architecture graph surface.

    Returns:
        JSON-safe API table with copied rows and a surface-to-symbol index for
        SDK, CLI, REST, and MCP consumers.
    """

    rows = [dict(row) for row in ARCHITECTURE_API_TABLE_ROWS]
    (surface_index,) = api_symbol_indexes(rows, "surface")
    return {
        "schema": ARCHITECTURE_API_TABLE_SCHEMA,
        "row_count": len(rows),
        "surface_index": surface_index,
        "rows": rows,
    }


def get_architecture_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> ArchitectureApiTable | ArchitectureApiRow | list[str]:
    """Return the full architecture API table, one row, or one index bucket.

    Args:
        symbol: Optional public symbol to select from the table rows.
        index_name: Optional index name. The architecture table currently
            supports `surface_index`.
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
        ArchitectureApiTable | ArchitectureApiRow | list[str],
        api_table_selection(
            get_architecture_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_ARCHITECTURE_API_INDEX_NAMES,
        ),
    )


def render_architecture_api_reference_markdown() -> str:
    """Render the architecture graph API table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/architecture-api-reference.md`. The content is
        generated from `get_architecture_api_table()` so public SDK, CLI, REST,
        and MCP architecture docs stay aligned.
    """

    table = get_architecture_api_table()
    return api_surface_reference_markdown(
        title="Architecture API Reference",
        source="paradev.sdk.get_architecture_api_table()",
        regenerate_when="Regenerate this file whenever the architecture graph API table changes:",
        command="rtk uv run paradev architecture --api-table-markdown > docs/user-manual/architecture-api-reference.md",
        table=table,
        fields=_ARCHITECTURE_API_STANDARD_FIELDS,
        include_feature_index=False,
    )
