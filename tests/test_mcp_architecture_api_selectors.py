from __future__ import annotations

from heavenbase.utils import load_txt

from paradev.surfaces.mcp import (
    get_mcp_api_selection,
    get_mcp_contract,
    render_mcp_api_reference_markdown,
)


def test_mcp_contract_exposes_architecture_api_selector_tool() -> None:
    contract = get_mcp_contract()
    tools = {tool["name"]: tool for tool in contract["tool_contracts"]}

    assert "architecture_api" in contract["tools"]
    assert tools["architecture_api"] == {
        "name": "architecture_api",
        "sdk_method": "get_architecture_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }


def test_mcp_api_table_lists_architecture_api_selector_tool() -> None:
    row = get_mcp_api_selection(symbol="architecture_api")

    assert row["feature"] == "architecture"
    assert row["mode"] == "read"
    assert row["sdk_method"] == "get_architecture_api_selection"
    assert row["inputs"] == "symbol, index_name, key"
    assert row["returns"] == "Architecture API table, row, or index lookup payload"
    assert row["raises"] == "ValueError or KeyError on invalid architecture API selector"

    assert get_mcp_api_selection(index_name="feature_index", key="architecture") == [
        "list_surfaces",
        "describe_architecture",
        "architecture_api",
    ]


def test_mcp_api_reference_documents_architecture_api_selector_tool() -> None:
    reference = render_mcp_api_reference_markdown()

    assert "| `architecture` | 3 | `list_surfaces`, `describe_architecture`, `architecture_api` |" in reference
    assert (
        "| `architecture_api` | `MCP tool` | `mcp` | `architecture` | `read` | "
        "`get_architecture_api_selection` | `symbol, index_name, key` | "
        "`Architecture API table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid architecture API selector` |"
    ) in reference
    assert load_txt("docs/user-manual/mcp-api-reference.md", encoding="utf-8") == reference


def test_architecture_interface_docs_describe_mcp_architecture_api_selector() -> None:
    content = load_txt("docs/architecture/interfaces.md", encoding="utf-8")

    assert "MCP exposes it through the read-only `architecture_api` selector tool" in content
