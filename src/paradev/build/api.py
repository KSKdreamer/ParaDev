"""Generated facade API table for public build exports."""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import (
    api_annotation_text,
    api_standard_table,
    api_table_selection,
)
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)

BUILD_API_TABLE_SCHEMA = "paradev.build.api-table.v1"
_BUILD_API_REFERENCE_PAGE = "docs/user-manual/build-api-reference.md"
_BUILD_API_TEST_ANCHOR = "tests/test_architecture.py::test_build_api_table_lists_public_build_facade"
_BUILD_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")


class BuildApiRow(TypedDict):
    """One public `paradev.build` facade API row."""

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


class BuildApiTable(TypedDict):
    """Generated API-standard table for the build facade."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[BuildApiRow]


def get_build_api_table() -> BuildApiTable:
    """Return the API-standard table for the public build facade.

    Returns:
        JSON-safe table derived from `paradev.build.__all__`, with copied rows
        and indexes for build module, feature, and symbol-kind audits.
    """

    return cast(BuildApiTable, api_standard_table(BUILD_API_TABLE_SCHEMA, _build_api_rows()))


def get_build_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> BuildApiTable | BuildApiRow | list[str]:
    """Return the full build API table, one row, or one index bucket.

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
        BuildApiTable | BuildApiRow | list[str],
        api_table_selection(
            get_build_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_BUILD_API_INDEX_NAMES,
        ),
    )


def render_build_api_reference_markdown() -> str:
    """Render the public build facade table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/build-api-reference.md`. The content is generated
        from `get_build_api_table()` so build records, families, loaders,
        views, writers, and compiler extension APIs stay aligned with the
        public import facade.
    """

    table = get_build_api_table()
    return api_standard_reference_markdown(
        title="Build API Reference",
        source="paradev.build.get_build_api_table()",
        regenerate_when="Regenerate this file whenever the public `paradev.build` facade changes:",
        command="rtk uv run paradev build-api --markdown > docs/user-manual/build-api-reference.md",
        table=table,
        module_label="Build",
    )


def _build_api_rows() -> list[BuildApiRow]:
    from paradev import build

    rows: list[BuildApiRow] = []
    for symbol in build.__all__:
        value = getattr(build, symbol)
        module = _build_api_module(symbol, value)
        feature = _build_api_feature(module)
        rows.append(
            {
                "symbol": symbol,
                "kind": _build_api_kind(symbol, value),
                "layer": "build",
                "module": module,
                "feature": feature,
                "import_path": f"paradev.build.{symbol}",
                "returns": _build_api_returns(symbol, value),
                "value": _build_api_value(symbol, value),
                "registry_seam": _build_api_registry_seam(module),
                "surface": "sdk",
                "doc_page": _build_api_doc_page(module, feature),
                "test_anchor": _BUILD_API_TEST_ANCHOR,
            }
        )
    return rows


def _build_api_module(symbol: str, value: object) -> str:
    if symbol.startswith("BUILD_API") or symbol in {
        "BuildApiRow",
        "BuildApiTable",
        "get_build_api_selection",
        "get_build_api_table",
        "render_build_api_reference_markdown",
    }:
        return "api"
    if symbol in {"AUTHORING_PATH_SCHEMA", "AUTHORING_PLAN_SCHEMA", "FAMILIES_SCHEMA", "MANIFESTS_SCHEMA"}:
        return "views"
    if symbol == "EXPLAIN_SCHEMA":
        return "explain"
    if symbol == "GRAPH_SCHEMA":
        return "graph"
    if symbol == "SOURCE_SLOTS_SCHEMA":
        return "source_slots"
    if symbol in {"DEFAULT_COLLECTION_SLOTS", "DEFAULT_MODULE_SLOTS"}:
        return "discovery"
    if symbol == "SettingNormalizer":
        return "families"
    if symbol in {
        "ModuleDiagramContext",
        "ModuleDiagramNodeAuthoring",
        "ModuleDiagramNodeField",
        "ModuleDiagramNodePlanner",
        "ModuleDiagramPlanner",
        "ModuleDiagramProjector",
        "ModuleDiagramProvider",
        "ModuleDiagramRelationship",
        "ModuleDiagramSelectionDefault",
        "ModuleDiagramTextSource",
        "ResolvedModuleDiagramProvider",
    }:
        return "diagrams"
    if symbol == "PROJECT_DIAGRAM_PROVIDER_KIND":
        return "extensions"
    module = getattr(value, "__module__", "")
    if module.startswith("paradev.build."):
        return module.removeprefix("paradev.build.")
    return "build"


def _build_api_feature(module: str) -> str:
    if module == "api":
        return "api-table"
    if module in {"authoring", "registry", "extensions", "families"}:
        return "families"
    if module in {"discovery", "slots", "source_slots"}:
        return "source-discovery"
    if module == "loaders":
        return "source-loading"
    if module == "plan":
        return "planning"
    if module == "records":
        return "records"
    if module == "artifacts":
        return "artifacts"
    if module == "diagrams":
        return "diagrams"
    if module == "manifest":
        return "manifests"
    if module == "views":
        return "views"
    if module in {"graph", "explain"}:
        return "graph"
    return "build"


def _build_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if is_dataclass(value):
        return "dataclass"
    if symbol.startswith("DEFAULT_"):
        return "tuple constant"
    if symbol in {
        "ModuleDiagramNodePlanner",
        "ModuleDiagramPlanner",
        "ModuleDiagramProjector",
        "SettingNormalizer",
    }:
        return "type alias"
    if is_typeddict(value):
        return "TypedDict"
    if inspect.isclass(value):
        return "class"
    if inspect.isfunction(value):
        return "function"
    return type(value).__name__


def _build_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol == "DEFAULT_IDENTITY_REWRITER":
        return "TokenIdentityRewriter"
    if symbol.startswith("DEFAULT_"):
        try:
            return f"tuple[{len(value)}]"
        except TypeError:
            return "tuple"
    if symbol == "ModuleDiagramPlanner":
        return "Callable[[ModuleDiagramContext], ModuleDiagramEditPlan]"
    if symbol == "ModuleDiagramNodePlanner":
        return "Callable[[ModuleDiagramContext, Mapping[str, object]], ModuleDiagramNodePlan]"
    if symbol == "ModuleDiagramProjector":
        return "Callable[[ModuleDiagramContext], ModuleDiagramProjection]"
    if symbol == "SettingNormalizer":
        return "Callable[[str, object], object]"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, drop_collections_abc=True)
    if is_typeddict(value):
        return "TypedDict schema"
    if inspect.isclass(value):
        return "class"
    return type(value).__name__


def _build_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol.startswith("DEFAULT_"):
        try:
            return f"{len(value)} slots"
        except TypeError:
            return "tuple"
    return ""


def _build_api_registry_seam(module: str) -> str:
    if module in {"authoring", "registry", "extensions", "families"}:
        return "BuildRegistry family registry"
    if module == "diagrams":
        return "BuildRegistry diagram provider registry"
    if module == "artifacts":
        return "BuildRegistry artifact writer registry"
    if module in {"discovery", "slots", "source_slots", "loaders"}:
        return "source slot contract"
    if module in {"manifest", "views", "graph", "explain"}:
        return "build manifest/view contracts"
    if module in {"records", "plan"}:
        return "Project.build pipeline"
    return "none"


def _build_api_doc_page(module: str, feature: str) -> str:
    if feature == "api-table":
        return _BUILD_API_REFERENCE_PAGE
    if module in {
        "diagrams",
        "discovery",
        "slots",
        "source_slots",
        "loaders",
        "registry",
        "extensions",
        "families",
        "authoring",
    }:
        return "docs/user-manual/modules-and-collections.md"
    return "docs/user-manual/build-and-diagnostics.md"
