# AI Chat Default Role Config

Date: 2026-06-30

## Summary

Made the floating AI chat default role a real SDK-backed desktop config value.
`paradev.ai.chat.default_role` now round-trips through `CM_PARADEV`, is
validated against the managed chat roles, and drives the `defaultRole` returned
by the SDK-owned chat profile catalog.

## Changes

- Added `paradev.ai.chat.default_role` to the desktop config-value bridge with
  the default role `chat`.
- Treated HeavenBase remove markers as unset values when reading desktop config
  values, so unset config keys fall back cleanly to defaults.
- Added a Config > Models "Default chat role" select above the AI profile
  editor. The options come from the available managed profiles and writes use
  the same config-value bridge as CLI/Python-facing settings.
- Synced App settings normalization, config persistence writes, frontend
  service tests, native bridge tests, and English/Chinese locale keys.
- Updated the GUI spec/style docs to list the chat default role as a real
  runtime config key.

## Verification

```bash
rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_ai_chat_profiles_describe_managed_roles tests/test_desktop_api_selection.py::test_desktop_ai_chat_default_role_is_sdk_configured tests/test_native_web_bridge.py::test_native_web_bridge_config_endpoints_are_browser_safe -q
rtk npm --prefix apps/desktop run test:unit
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py
rtk npm --prefix apps/desktop run build
rtk bash scripts/flake.bash --ci
rtk git diff --check
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

The Tauri smoke reached the Vite dev server and launched the native
`paradev-desktop` binary against `projects/PIHC3`; no additional startup errors
appeared before shutdown.
