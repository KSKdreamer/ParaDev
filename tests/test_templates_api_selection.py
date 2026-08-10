import paradev.sdk.templates as templates
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.sdk.templates import (
    get_templates_api_selection,
    get_templates_api_table,
    render_templates_api_reference_markdown,
)


def test_templates_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_templates_api_table()
    assert_api_selection_projection(
        get_templates_api_selection,
        table,
        symbol="module_scaffold_plan",
        index_cases=(
            ("module_index", "sdk.templates"),
            ("feature_index", "templates-api"),
            ("kind_index", "function"),
        ),
    )


def test_templates_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_templates_api_selection,
        symbol="module_scaffold_plan",
        index_name="module_index",
        key="sdk.templates",
    )


def test_templates_api_table_lists_selection_helper() -> None:
    table = get_templates_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(templates.__all__)
    assert table["feature_index"]["templates-api"] == [
        "TEMPLATES_API_TABLE_SCHEMA",
        "TemplatesApiRow",
        "TemplatesApiTable",
        "get_templates_api_selection",
        "get_templates_api_table",
        "render_templates_api_reference_markdown",
    ]
    assert table["module_index"]["sdk.templates"][-6:] == table["feature_index"]["templates-api"]
    assert row_by_symbol["get_templates_api_selection"]["returns"] == "TemplatesApiTable | TemplatesApiRow | list[str]"
    assert row_by_symbol["get_templates_api_selection"]["registry_seam"] == "authoring templates API table"


def test_templates_api_reference_documents_selection_helper() -> None:
    reference = render_templates_api_reference_markdown()

    assert "`get_templates_api_selection`" in reference
    assert load_txt("docs/user-manual/templates-api-reference.md") == reference
