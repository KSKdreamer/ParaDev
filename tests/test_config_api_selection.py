from pathlib import Path
from heavenbase.utils import load_txt

import paradev.config as config
from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.config import (
    CM_PARADEV,
    DEFAULT_CONFIG,
    config_get,
    config_list,
    config_set,
    config_unset,
    get_config_api_selection,
    get_config_api_table,
    render_config_api_reference_markdown,
)


def test_config_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_config_api_table()
    assert_api_selection_projection(
        get_config_api_selection,
        table,
        symbol="CM_PARADEV",
        index_cases=(
            ("module_index", "config_api"),
            ("feature_index", "defaults"),
            ("kind_index", "function"),
        ),
    )


def test_config_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_config_api_selection,
        symbol="CM_PARADEV",
        index_name="module_index",
        key="config_api",
    )


def test_config_facade_helpers_round_trip_cm_paradev(tmp_path: Path, cm_paradev_lock) -> None:
    key = f"paradev.test.sdk_config_{tmp_path.name}"

    try:
        assert config_set(key, "42", parse="auto") is True
        assert config_get(key) == 42
        assert {"key": key, "value": 42} in config_list(prefix="paradev.test")
        assert config_unset(key) is True
    finally:
        CM_PARADEV.unset(key)


def test_config_defaults_expose_ai_chat_default_role(tmp_path: Path, cm_paradev_lock) -> None:
    scope = f"test_ai_chat_default_role_{tmp_path.name}"

    assert DEFAULT_CONFIG["paradev"]["ai"]["chat"]["default_role"] == "chat"
    assert config_get("paradev.ai.chat.default_role", scope=scope) == "chat"
    assert {"key": "paradev.ai.chat.default_role", "value": "chat"} in config_list(prefix="paradev.ai.chat", scope=scope)


def test_config_api_table_lists_selection_helper() -> None:
    table = get_config_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(config.__all__)
    assert table["module_index"]["config_api"] == [
        "CONFIG_API_TABLE_SCHEMA",
        "ConfigApiRow",
        "ConfigApiTable",
        "get_config_api_selection",
        "get_config_api_table",
        "render_config_api_reference_markdown",
    ]
    assert table["feature_index"]["config-api"] == table["module_index"]["config_api"]
    assert row_by_symbol["get_config_api_selection"]["returns"] == "ConfigApiTable | ConfigApiRow | list[str]"
    assert row_by_symbol["get_config_api_selection"]["registry_seam"] == "config facade API table"


def test_config_api_reference_documents_selection_helper() -> None:
    reference = render_config_api_reference_markdown()

    assert "`get_config_api_selection`" in reference
    assert load_txt("docs/user-manual/config-api-reference.md") == reference
