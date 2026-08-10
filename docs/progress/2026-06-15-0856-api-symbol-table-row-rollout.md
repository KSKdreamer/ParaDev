# API Symbol Table Row Rollout Progress

Date: 2026-06-15 08:56 CST

Linear: none

## Done

- Migrated the localization, SDK, surfaces, and build API reference renderers to the shared `api_symbol_table_row()` helper.
- Preserved the generated Markdown for all four API references exactly.
- Kept the slice away from dirty PIHC3 migration, build loader internals, and desktop app files.

## Verification

- `rtk uv run python - <<'PY' ... PY` old-vs-current renderer comparison for localization, SDK, surfaces, and build API references
- `rtk uv run black src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py`
- `rtk uv run python -m py_compile src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py`
- `rtk uv run pytest tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_build_api_table_lists_public_build_facade tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_build_api_cli_outputs_reference_markdown tests/test_cli.py::test_localization_api_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py`
- `rtk git diff --check -- src/paradev/localization/api.py src/paradev/sdk/api.py src/paradev/surfaces/api.py src/paradev/build/api.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating package-style API renderers to shared table helpers in small groups with exact renderer comparisons.
- Keep avoiding build loader internals, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
