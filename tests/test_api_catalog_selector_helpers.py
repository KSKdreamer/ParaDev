from importlib import import_module

from paradev.surfaces.api_catalog import get_api_catalog_selection, get_api_catalog_table

SELECTABLE_REFERENCE_HELPERS = {
    "api-catalog": "get_api_catalog_selection",
    "sdk-api": "get_sdk_api_selection",
    "package-api": "get_package_api_selection",
    "config-api": "get_config_api_selection",
    "gui-api": "get_gui_api_selection",
    "desktop-api": "get_desktop_api_selection",
    "games-api": "get_games_api_selection",
    "surfaces-api": "get_surfaces_api_selection",
    "project-api": "get_project_api_selection",
    "templates-api": "get_templates_api_selection",
    "copy-roots-api": "get_copy_roots_api_selection",
    "project-facade-api": "get_project_facade_api_selection",
    "localization-api": "get_localization_api_selection",
    "build-api": "get_build_api_selection",
    "frontend-api": "get_frontend_api_selection",
    "sdk-cli-reference": "get_frontend_api_selection",
    "project-inspection-reference": "get_project_inspection_selection",
    "architecture-api": "get_architecture_api_selection",
    "pdx-api": "get_pdx_api_selection",
    "pdx-core-api": "get_pdx_core_api_selection",
    "lsp-api": "get_lsp_api_selection",
    "lsp-server-api": "get_lsp_server_api_selection",
    "catalog-api": "get_catalog_api_selection",
    "hb-api": "get_hb_api_selection",
    "rest-api": "get_rest_api_selection",
    "rest-facade-api": "get_rest_facade_api_selection",
    "mcp-api": "get_mcp_api_selection",
    "cli-api": "get_cli_api_selection",
    "surface-contract-reference": "get_surface_contract_selection",
}


def test_api_catalog_lists_callable_selector_helpers() -> None:
    table = get_api_catalog_table()
    rows_by_id = {row["id"]: row for row in table["rows"]}

    for reference_id, helper_name in SELECTABLE_REFERENCE_HELPERS.items():
        row = rows_by_id[reference_id]
        owner_module = import_module(row["owner_module"])

        assert row["selector_helper"] == helper_name
        assert callable(getattr(owner_module, helper_name))
        assert reference_id in get_api_catalog_selection(index_name="selector_helper", key=helper_name)
