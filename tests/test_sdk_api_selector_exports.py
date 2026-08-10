import paradev.sdk as sdk
from paradev.sdk.architecture import get_architecture_api_selection
from paradev.sdk.lsp import get_lsp_api_selection
from paradev.sdk.pdx import get_pdx_api_selection
from paradev.sdk.project_api import get_project_api_selection

SDK_MODULE_API_SELECTION_HELPERS = {
    "get_architecture_api_selection": get_architecture_api_selection,
    "get_project_api_selection": get_project_api_selection,
    "get_pdx_api_selection": get_pdx_api_selection,
    "get_lsp_api_selection": get_lsp_api_selection,
}


def test_sdk_facade_exports_module_api_selection_helpers() -> None:
    for name, helper in SDK_MODULE_API_SELECTION_HELPERS.items():
        assert name in sdk.__all__
        assert getattr(sdk, name) is helper

    assert sdk.get_architecture_api_selection(symbol="SurfaceSpec") == get_architecture_api_selection(symbol="SurfaceSpec")
    assert sdk.get_project_api_selection(symbol="Project.build") == get_project_api_selection(symbol="Project.build")
    assert sdk.get_pdx_api_selection(symbol="format_pdx_text") == get_pdx_api_selection(symbol="format_pdx_text")
    assert sdk.get_lsp_api_selection(symbol="complete_pdx_lsp_text") == get_lsp_api_selection(symbol="complete_pdx_lsp_text")
