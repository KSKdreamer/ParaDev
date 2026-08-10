# Desktop Frontend API Helper Progress

Date: 2026-06-08 11:40 CST

Linear: TAL-295

## Done

- Added `apps/desktop/src/data/frontendApi.ts` as the desktop typed helper over the generated SDK frontend API contract.
- Exposed TypeScript-friendly operation, group, status, and workspace-section ids plus operation/group/section lookup helpers and a compact `frontendApiSummary`.
- Wired the desktop shell API status copy to `frontendApiSummary`, so the shell consumes SDK-owned API metadata instead of a static frontend contract description.
- Added focused architecture coverage proving the helper consumes `apps/desktop/src/generated/frontendApi.ts` and shell data imports the helper.
- Updated English and Chinese SDK/developer manuals, frontend API docs, architecture docs, and GUI spec to make the helper import path canonical while keeping the generated file machine-owned.
- Self-reviewed the diff for duplicate frontend action registries, generated-contract drift, docs consistency, TypeScript build impact, and accidental PIHC3 coupling; no blocking findings remained.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_architecture.py::test_desktop_frontend_api_helper_consumes_generated_contract -q` -> 2 passed.
- `rtk npm --prefix apps/desktop run build` -> TypeScript check and Vite build passed.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 65 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` -> 20 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py` -> OK, no banned imports.
- `rtk bash scripts/flake.bash --ci` -> OK, 54 files unchanged.
- `rtk git diff --check` -> clean.
- `rtk bash scripts/test.bash` -> 486 passed.
- `rtk uv build` -> source distribution and wheel built.

## Risks Or Blockers

- Linear update is still blocked by expired authentication in this environment; `_save_comment` on TAL-295 returned `UNAUTHORIZED` / session expired.
- Importing `frontendApiSummary` currently brings the generated contract into the desktop bundle through the typed helper. The Vite build remains small enough for this scaffold, but a future shell-only summary module may be worthwhile if the contract grows sharply.

## Next

- Continue frontend API stabilization by making actual workbench panels consume `frontendApiOperations`, section lookups, form payloads, option-source payloads, and REST request plans from the same helper/SDK contract.
- Keep `apps/desktop/src/generated/frontendApi.ts`, `apps/desktop/src/data/frontendApi.ts`, and the bilingual user manual updated in the same change whenever the canonical operation table or typed helper views change.
