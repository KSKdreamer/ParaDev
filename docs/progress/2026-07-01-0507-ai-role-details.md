# AI Role Details

Status: complete

Date: 2026-07-01 05:07

## Scope

- Verified ParaDev is already adapted to HeavenBase 0.1.1.5: `requirements.txt`, `uv.lock`, the embedded heaven-style skill, and the runtime import all report `0.1.1.5`.
- Kept the current GUI slice small by improving the floating AI chat role selector instead of adding new prompt behavior.
- Rendered the selected SDK-owned AI chat profile detail below the floating chat role selector, localized through `aiChatProfileDetail(...)`, with `aria-describedby` tying the select to the visible detail.
- Switched floating chat tests to the generated SDK profile catalog so the create-module role, default template context, build detail, Chinese detail, and custom future-profile fallback are covered.
- Added GUI spec and smoke checklist notes for SDK-owned floating chat role labels/details/prompts/source defaults.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/configPage/ConfigPage.test.tsx src/services/paradev.test.ts src/aiChatProfileText.test.ts src/i18n/locales.test.ts`
- `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_typescript_contract_exports_ai_chat_profile_catalog tests/test_desktop_api_selection.py::test_desktop_ai_chat_profiles_describe_managed_roles tests/test_desktop_api_selection.py::test_desktop_ai_chat_default_role_is_sdk_configured tests/test_desktop_api_selection.py::test_desktop_ai_chat_profile_overrides_persist_and_feed_chat -q`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/sync-env.bash --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47844` booted Vite and the Tauri Rust app without startup errors, then was stopped manually.
