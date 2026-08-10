# 2026-07-01 05:53 - AI chat SDK operation cards

## Summary

Continued the SDK-first AI chat pass by making create-module and build roles visibly tied to generated frontend API operations without letting chat execute them. The Python desktop profile catalog now owns managed operation ids and compact operation card metadata derived from `get_frontend_api_action(...)`.

## Changes

- Added managed `operationIds` for `create-module` (`module.draft`) and `build` (`build.plan`, `build.start`).
- Added compact `operationCards` to runtime desktop AI profile payloads and the generated desktop TypeScript fallback contract.
- Rendered passive SDK action cards in the floating chat with `data-paradev-chat-operation-id` and `data-paradev-chat-operation-passive="true"`.
- Rendered non-editable managed SDK action strips in Config Models profile rows.
- Added EN/ZH translations, CSS, service normalization, and Python/React tests for the new metadata.
- Avoided statically importing the full generated frontend API contract into the chat shell; the large `frontendApi` chunk remains split after build.

## Verification

- `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_typescript_contract_exports_ai_chat_profile_catalog tests/test_desktop_api_selection.py::test_desktop_ai_chat_profiles_describe_managed_roles tests/test_desktop_api_selection.py::test_desktop_ai_chat_profile_operation_ids_resolve_to_sdk_owned_frontend_rows -q`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts src/services/paradev.test.ts`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/sync-env.bash --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47842`

## Notes

The PIHC3 native Tauri smoke reached `target/debug/paradev-desktop` with no terminal-side startup errors and was stopped after a short idle window. The cards are intentionally passive: chat can explain or plan SDK actions, but file writes and builds still require the existing explicit editor/build-page flows.
