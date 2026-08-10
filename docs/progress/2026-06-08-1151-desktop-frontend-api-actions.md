# Desktop Frontend API Actions Progress

Date: 2026-06-08 11:51 CST

Linear: TAL-295

## Done

- Added typed `FrontendApiAction` and `FrontendApiActionExecution` views to `apps/desktop/src/data/frontendApi.ts`.
- Exposed `frontendApiWorkspaceActions`, `getFrontendApiAction(...)`, `getFrontendApiSectionActions(...)`, and `getFrontendApiDefaultSectionAction(...)` so desktop panels can consume SDK-owned workspace action rows without scanning generated JSON or keeping a second action registry.
- Added architecture coverage proving the desktop helper publishes the action types and action lookup helpers.
- Updated English and Chinese frontend API, SDK, and developer manuals plus the architecture boundary and GUI spec so TypeScript clients use the helper for workspace action rows.
- Self-reviewed the diff for duplicate GUI action routing, generated-contract drift, TypeScript type safety, bundle impact, docs consistency, and accidental PIHC3 coupling; no blocking findings remained.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_workspace_actions -q` -> 1 passed after the expected red failure.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_architecture.py::test_desktop_frontend_api_helper_consumes_generated_contract tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_workspace_actions -q` -> 3 passed.
- `rtk npm --prefix apps/desktop run build` -> TypeScript check and Vite build passed.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 66 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` -> 20 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py` -> OK, no banned imports.
- `rtk bash scripts/flake.bash --ci` -> OK, 54 files unchanged.
- `rtk git diff --check` -> clean.
- `rtk bash scripts/test.bash` -> 487 passed.
- `rtk uv build` -> source distribution and wheel built.

## Risks Or Blockers

- Linear update is still blocked by expired authentication in this environment; `_save_comment` on TAL-295 has been returning `UNAUTHORIZED` / session expired.
- Importing the helper still pulls the full generated frontend API contract into the desktop bundle. Current Vite output remains acceptable for the scaffold, but a future lightweight summary/action-index split may be useful if GUI shell-only imports grow.

## Next

- Continue moving real desktop/workbench panels onto `getFrontendApiSectionActions(...)`, action execution hints, derived forms, option-source resolution, and REST request planning.
- Keep generated TypeScript, the typed helper, and bilingual manuals synchronized whenever a frontend-visible operation or helper view changes.
