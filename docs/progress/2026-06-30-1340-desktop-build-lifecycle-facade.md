# Desktop Build Lifecycle Facade Progress

Date: 2026-06-30 13:40

Linear: TAL-000

## Done

- Moved native-web build start/status/interrupt ownership out of the REST module and into `paradev.desktop`.
- Added `DesktopBuildRegistry`, `desktop_start_build`, `desktop_build_status`, and `desktop_interrupt_build` as public desktop facade APIs.
- Kept REST `/desktop/builds*` routes stable while delegating to a per-app desktop registry instance.
- Added lifecycle tests for completion, interruption, conflicting active builds, and native-web registry isolation.
- Regenerated desktop API and aggregate API catalog reference docs.

## Verification

- `rtk uv run pytest tests/test_desktop_api_selection.py tests/test_native_web_bridge.py tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_cli.py::test_desktop_api_cli_outputs_table_json tests/test_cli.py::test_desktop_api_cli_outputs_reference_markdown tests/test_tauri_bridge.py`
- `rtk uv run pytest tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli_api_rest_mcp_selectors.py::test_api_catalog_tracks_cli_api_rest_mcp_surfaces tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/builds.py src/paradev/desktop/__init__.py src/paradev/desktop/api.py src/paradev/surfaces/rest.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py tests/test_architecture.py tests/test_cli.py`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47913`

## Risks Or Blockers

- Tauri still owns its Rust child-process registry because the current Python helper is a per-command subprocess; moving that lifecycle fully to Python needs a persistent Python bridge or sidecar.

## Next

- Decide whether the Tauri desktop shell should use the native-web bridge or a long-lived Python supervisor for build lifecycle state.
