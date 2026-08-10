from api_selection_contracts import assert_api_selection_projection, assert_api_selection_rejects_invalid_selectors
from paradev.surfaces.cli import get_cli_api_selection, get_cli_api_table


def test_cli_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_cli_api_table()
    assert_api_selection_projection(
        get_cli_api_selection,
        table,
        symbol="paradev build",
        index_cases=(
            ("feature_index", "build"),
            ("kind_index", "command"),
            ("adapter_index", "Project.build"),
        ),
        mutation_field="returns",
    )


def test_cli_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_cli_api_selection,
        symbol="paradev build",
        index_name="feature_index",
        key="build",
    )
