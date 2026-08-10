import paradev as paradev_package
from heavenbase.utils import load_txt

from api_selection_contracts import assert_api_selection_projection, assert_api_selection_rejects_invalid_selectors
from paradev import get_package_api_selection, get_package_api_table, render_package_api_reference_markdown


def test_package_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_package_api_table()
    assert_api_selection_projection(
        get_package_api_selection,
        table,
        symbol="Project",
        index_cases=(
            ("module_index", "package_api"),
            ("feature_index", "projects"),
            ("kind_index", "function"),
        ),
    )


def test_package_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_package_api_selection,
        symbol="Project",
        index_name="module_index",
        key="package_api",
    )


def test_package_api_table_lists_selection_helper() -> None:
    table = get_package_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(paradev_package.__all__)
    assert table["module_index"]["package_api"] == [
        "PACKAGE_API_TABLE_SCHEMA",
        "PackageApiRow",
        "PackageApiTable",
        "get_package_api_selection",
        "get_package_api_table",
        "render_package_api_reference_markdown",
    ]
    assert table["feature_index"]["package-api"] == table["module_index"]["package_api"]
    assert row_by_symbol["get_package_api_selection"]["returns"] == "PackageApiTable | PackageApiRow | list[str]"
    assert row_by_symbol["get_package_api_selection"]["registry_seam"] == "none"


def test_package_api_reference_documents_selection_helper() -> None:
    reference = render_package_api_reference_markdown()

    assert "`get_package_api_selection`" in reference
    assert load_txt("docs/user-manual/package-api-reference.md") == reference
