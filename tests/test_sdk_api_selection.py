import paradev.sdk as sdk
from api_selection_contracts import assert_api_selection_projection, assert_api_selection_rejects_invalid_selectors
from paradev.sdk.api import get_sdk_api_selection, get_sdk_api_table


def test_sdk_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_sdk_api_table()
    assert_api_selection_projection(
        get_sdk_api_selection,
        table,
        symbol="Project",
        index_cases=(
            ("module_index", "project"),
            ("feature_index", "projects"),
            ("kind_index", "function"),
        ),
    )


def test_sdk_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_sdk_api_selection,
        symbol="Project",
        index_name="module_index",
        key="project",
    )


def test_sdk_api_selection_is_public_sdk_facade_export() -> None:
    assert "get_sdk_api_selection" in sdk.__all__
    assert sdk.get_sdk_api_selection is get_sdk_api_selection
    assert sdk.get_sdk_api_selection(symbol="Project") == get_sdk_api_selection(symbol="Project")
