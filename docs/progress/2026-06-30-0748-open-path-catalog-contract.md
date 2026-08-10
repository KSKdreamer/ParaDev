# Open Path Catalog Contract Progress

Date: 2026-06-30 07:48

Linear: active goal

## Done

- Added `paradev.desktop.desktop_open_path_targets(...)` as the SDK-owned catalog for desktop open-path targets, normalized platforms, platform-compatible target ids, and default target ids.
- Reused the same Python target rows for command validation/defaults and for the generated desktop TypeScript contract, so the GUI no longer owns duplicated target ids, platform support, label keys, or default target logic.
- Kept Vite-only icon imports in `apps/desktop/src/openPathTargets.ts`, where they belong, and reduced the frontend wrapper to generated catalog rows plus local icon metadata.
- Regenerated the desktop TypeScript contract, desktop API reference, and aggregate API catalog reference.

## Verification

- Red first: `rtk uv run pytest tests/test_desktop_api_selection.py -k 'open_path_targets_catalog or typescript_contract_exports_open_path_catalog'` failed on the missing Python catalog and generated TS exports.
- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/openPathTargets.test.ts` failed because the frontend wrapper was not reading generated catalog rows.
- `rtk uv run pytest tests/test_desktop_api_selection.py -k 'open_path_targets_catalog or typescript_contract_exports_open_path_catalog'`
- `rtk npm --prefix apps/desktop run test:unit -- src/openPathTargets.test.ts`
- `rtk uv run pytest tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_desktop_api_selection.py::test_desktop_api_reference_documents_selection_helper tests/test_desktop_api_selection.py::test_desktop_open_path_targets_catalog_matches_gui_platform_contract tests/test_desktop_api_selection.py::test_desktop_typescript_contract_exports_open_path_catalog -q`
- `rtk uv run pytest tests/test_cli.py::test_desktop_api_cli_outputs_table_json tests/test_cli.py::test_desktop_api_cli_outputs_reference_markdown tests/test_cli.py::test_desktop_api_cli_outputs_typescript_config_keys tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/shell.py src/paradev/desktop/local.py src/paradev/desktop/api.py tests/test_desktop_api_selection.py`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- The checked-in generated TypeScript file still lives at `desktopConfigKeys.ts` for compatibility, even though it now also exports open-path catalog constants.
- The Vite production build still reports the existing large chunk warning.

## Next

- Continue moving GUI-owned operation/catalog knowledge into Python-owned generated contracts, especially around build/open-path workflow controls that still need modder-facing polish.
