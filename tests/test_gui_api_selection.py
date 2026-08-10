import paradev.gui as gui
from heavenbase.utils import load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.gui import (
    get_gui_api_selection,
    get_gui_api_table,
    render_gui_api_reference_markdown,
)


def test_gui_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_gui_api_table()
    assert_api_selection_projection(
        get_gui_api_selection,
        table,
        symbol="build_parser",
        index_cases=(
            ("module_index", "gui_api"),
            ("feature_index", "launcher"),
            ("kind_index", "function"),
        ),
    )


def test_gui_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_gui_api_selection,
        symbol="build_parser",
        index_name="module_index",
        key="gui_api",
    )


def test_gui_api_table_lists_selection_helper() -> None:
    table = get_gui_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(gui.__all__)
    assert table["module_index"]["gui_api"] == [
        "GUI_API_TABLE_SCHEMA",
        "GuiApiRow",
        "GuiApiTable",
        "get_gui_api_selection",
        "get_gui_api_table",
        "render_gui_api_reference_markdown",
    ]
    assert table["feature_index"]["gui-api"] == table["module_index"]["gui_api"]
    assert row_by_symbol["get_gui_api_selection"]["returns"] == "GuiApiTable | GuiApiRow | list[str]"
    assert row_by_symbol["get_gui_api_selection"]["registry_seam"] == "GUI facade API table"


def test_gui_api_reference_documents_selection_helper() -> None:
    reference = render_gui_api_reference_markdown()

    assert "`get_gui_api_selection`" in reference
    assert load_txt("docs/user-manual/gui-api-reference.md") == reference
