from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.sdk.architecture import (
    ARCHITECTURE_API_TABLE_ROWS,
    get_architecture_api_selection,
    get_architecture_api_table,
    render_architecture_api_reference_markdown,
)


def test_architecture_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_architecture_api_table()
    assert_api_selection_projection(
        get_architecture_api_selection,
        table,
        symbol="ArchitectureSpec.surface",
        index_cases=(("surface_index", "sdk"),),
        mutation_field="raises",
    )


def test_architecture_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_architecture_api_selection,
        symbol="ArchitectureSpec.surface",
        index_name="surface_index",
        key="sdk",
    )


def test_architecture_api_table_lists_selection_helper() -> None:
    table = get_architecture_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(ARCHITECTURE_API_TABLE_ROWS)
    assert table["surface_index"]["sdk"] == [
        "SurfaceSpec",
        "SurfaceSpec.to_dict",
        "ArchitectureSpec",
        "ArchitectureSpec.surface",
        "ArchitectureSpec.path_chains",
        "ArchitectureSpec.to_dict",
        "get_architecture_spec",
        "get_architecture_api_selection",
        "get_architecture_api_table",
        "render_architecture_api_reference_markdown",
    ]
    assert row_by_symbol["get_architecture_api_selection"]["returns"] == "ArchitectureApiTable | ArchitectureApiRow | list[str]"
    assert row_by_symbol["get_architecture_api_selection"]["registry_seam"] == "none"
    assert table["surface_index"]["mcp"] == [
        "list_surfaces",
        "describe_architecture",
        "architecture_api",
    ]
    assert row_by_symbol["architecture_api"]["inputs"] == "symbol=None, index_name=None, key=None"
    assert row_by_symbol["architecture_api"]["returns"] == "ArchitectureApiTable | ArchitectureApiRow | list[str]"
    assert row_by_symbol["architecture_api"]["raises"] == "ValueError or KeyError on unsupported selectors"


def test_architecture_api_reference_documents_selection_helper() -> None:
    reference = render_architecture_api_reference_markdown()

    assert "`get_architecture_api_selection`" in reference
    assert "| `mcp` | 3 | `list_surfaces`, `describe_architecture`, `architecture_api` |" in reference
    assert load_txt("docs/user-manual/architecture-api-reference.md", encoding="utf-8") == reference
