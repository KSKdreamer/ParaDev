# Desktop Open Path REST Contract

Date: 2026-07-01

## Summary

Published the existing desktop open-path native route in the REST/OpenAPI API table so the GUI, native bridge, and generated REST reference all expose the same public contract.

## Changes

- Added `POST /desktop/open-path` to `paradev.surfaces.rest.get_openapi_seed()`.
- Extended OpenAPI seed and REST API table architecture coverage for the route.
- Regenerated the REST API and API catalog manual pages.

## Verification

- `rtk uv run python -c 'import heavenbase, paradev; ...'` reported `heavenbase 0.1.1.5`.
- `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_native_web_bridge.py::test_native_web_bridge_opens_paths_and_runs_hoi4 -q`
- `rtk uv run pytest tests/test_hb.py::test_hb_catalog_preview_projects_build_rows_without_writing tests/test_hb.py::test_hb_catalog_smoke_registers_preview_rows_without_writing tests/test_config_api_selection.py tests/test_desktop_api_selection.py::test_desktop_llm_route_passes_configured_preset_to_heavenbase tests/test_desktop_api_selection.py::test_desktop_ai_chat_passes_explicit_preset_to_heavenbase -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_native_web_bridge.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk git diff --check`

## Notes

The broader `tests/test_hb.py` run was interrupted after several minutes because it was too broad for this REST slice; the focused HeavenBase 0.1.1.5 compatibility paths above passed.
