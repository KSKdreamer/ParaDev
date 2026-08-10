# 2026-06-14 12:38 Frontend API Index Row Helpers

## Focus

- Continue modularizing the SDK-owned frontend API reference renderer without changing generated API tables.
- Keep the work isolated from desktop shell changes, PIHC3 migration files, generated frontend assets, and `node_modules`.

## Changes

- Extracted binding index row construction into `_frontend_api_binding_index_row`.
- Extracted workspace-section index row construction into `_frontend_api_workspace_section_index_row`.
- Preserved binding surface order, sorted binding keys, workspace section order, default operation cells, and operation-id detail cells.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests remain deferred to reduce CPU contention with active PIHC2-to-PIHC3 migration work.
- Commit staging is limited to `src/paradev/sdk/frontend_api.py` and this progress note; `node_modules` remains unstaged.
