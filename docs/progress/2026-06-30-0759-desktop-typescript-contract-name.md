# Desktop TypeScript Contract Name Progress

Date: 2026-06-30 07:59

Linear: active goal

## Done

- Renamed the public desktop TypeScript renderer from `render_desktop_config_keys_typescript` to `render_desktop_typescript` so the Python facade name matches the broader generated contract.
- Renamed the generated desktop artifact from `apps/desktop/src/generated/desktopConfigKeys.ts` to `apps/desktop/src/generated/desktopContract.ts`.
- Updated GUI imports, CLI adapter metadata, desktop API docs, CLI API docs, and tests to use the general contract name.
- Added a regression test that rejects the stale config-key-only public renderer and artifact path.

## Verification

- Red first: `rtk uv run pytest tests/test_desktop_api_selection.py::test_desktop_typescript_contract_uses_general_renderer_and_artifact -q` failed on the missing `render_desktop_typescript`.
- `rtk uv run pytest tests/test_desktop_api_selection.py::test_desktop_typescript_contract_uses_general_renderer_and_artifact -q`
- `rtk uv run pytest tests/test_desktop_api_selection.py::test_desktop_typescript_matches_generated_file tests/test_desktop_api_selection.py::test_desktop_typescript_contract_uses_general_renderer_and_artifact tests/test_desktop_api_selection.py::test_desktop_typescript_contract_exports_open_path_catalog tests/test_desktop_api_selection.py::test_desktop_api_reference_documents_selection_helper tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_desktop_api_cli_outputs_table_json tests/test_cli.py::test_desktop_api_cli_outputs_reference_markdown tests/test_cli.py::test_desktop_api_cli_outputs_typescript_config_keys -q`
- `rtk npm --prefix apps/desktop run test:unit -- src/openPathTargets.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py src/paradev/desktop/api.py src/paradev/desktop/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_desktop_api_selection.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- This intentionally breaks the stale renderer/file names instead of keeping aliases, matching the SDK-first single-contract model.
- The Vite production build still reports the existing large chunk warning.

## Next

- Use the translation audit findings to localize AI-chat prompts/context and continue improving the Chinese PIHC3 editing experience.
