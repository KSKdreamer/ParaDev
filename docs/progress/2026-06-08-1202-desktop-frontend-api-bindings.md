# Desktop Frontend API Bindings Progress

Date: 2026-06-08 12:02 CST

Linear: TAL-295

## Done

- Added typed frontend binding views to `apps/desktop/src/data/frontendApi.ts`: `FrontendApiBinding`, `FrontendApiRestBinding`, and `FrontendApiBindings`.
- Exposed `frontendApiRestOperations`, `getFrontendApiBindings(...)`, and `getFrontendApiRestBinding(...)` so desktop panels can consume SDK-owned callable metadata without parsing human-readable `rest`, `cli`, `sdk`, `mcp`, or `lsp` strings.
- Added focused architecture coverage proving the helper exposes typed surface binding helpers.
- Updated English and Chinese frontend API, SDK, and developer manuals plus the architecture boundary and GUI spec to make the typed binding helper path canonical for TypeScript clients.
- Self-reviewed the diff for duplicate REST parsing, unsafe optional binding handling, generated-contract drift, TypeScript build behavior, bundle impact, docs consistency, and PIHC3 coupling; no blocking findings remained.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_surface_bindings -q` -> 1 passed after the expected red failure.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_architecture.py::test_desktop_frontend_api_helper_consumes_generated_contract tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_workspace_actions tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_surface_bindings -q` -> 4 passed.
- `rtk npm --prefix apps/desktop run build` -> TypeScript check and Vite build passed.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 67 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` -> 20 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py` -> OK, no banned imports.
- `rtk bash scripts/flake.bash --ci` -> OK, 54 files unchanged.
- `rtk git diff --check` -> clean.
- `rtk bash scripts/test.bash` -> 488 passed.
- `rtk uv build` -> source distribution and wheel built.

## Risks Or Blockers

- Linear update remains blocked by expired/revoked authentication in this environment; recent TAL-295 comment attempts returned session-expired errors.
- The desktop helper still imports the full generated contract. The Vite build remains acceptable for the scaffold, but a later lightweight action/binding index split may be useful if shell-only imports become performance-sensitive.

## Next

- Move the first real workbench panels from static shell data onto `getFrontendApiSectionActions(...)`, `getFrontendApiRestBinding(...)`, option sources, and REST request planning.
- Keep generated TypeScript, typed helpers, and bilingual manuals synchronized whenever frontend-visible operations or binding shapes change.
