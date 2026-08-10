# 2026-06-30 03:38 - AI chat source-kind catalog

## Summary

- Moved the AI chat supported source-kind list into the Python desktop SDK payload returned by `desktop_chat_profiles()`.
- Added SDK validation so `desktop_write_chat_profile()` rejects unknown `sourceKinds` values before they can persist in `CM_PARADEV`.
- Updated the desktop service and Config page plumbing so source toggles render from the SDK payload, with the local list only used as a fallback for offline/mock mode.
- Added OpenAPI enum metadata for profile write `sourceKinds`.

## Verification

```bash
rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_ai_chat_profiles_describe_managed_roles tests/test_desktop_api_selection.py::test_desktop_ai_chat_profile_write_rejects_unknown_roles tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server -q
rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts src/configPage/ConfigPage.test.tsx src/aiChatProfileText.test.ts
rtk npm --prefix apps/desktop run test:unit
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py src/paradev/surfaces/rest.py tests/test_desktop_api_selection.py tests/test_architecture.py
rtk git diff --check
rtk npm --prefix apps/desktop run build
rtk bash scripts/flake.bash --ci
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` cleanly and showed no additional runtime output during the smoke window before shutdown.
- The desktop build still reports the existing Vite large-chunk warning.
