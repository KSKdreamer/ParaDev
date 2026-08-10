from api_selection_contracts import assert_api_selection_projection, assert_api_selection_rejects_invalid_selectors
from paradev.sdk.project_api import get_project_api_selection, get_project_api_table


def test_project_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_project_api_table()
    assert_api_selection_projection(
        get_project_api_selection,
        table,
        symbol="Project.build",
        index_cases=(
            ("feature_index", "build"),
            ("kind_index", "method"),
            ("cli_command_index", "paradev build"),
        ),
        mutation_field="raises",
    )


def test_project_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_project_api_selection,
        symbol="Project.build",
        index_name="feature_index",
        key="build",
    )
