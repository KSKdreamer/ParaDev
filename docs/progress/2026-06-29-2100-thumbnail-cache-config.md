# 2026-06-29 21:00 Thumbnail Cache Config

## Summary

- Promoted the GUI thumbnail cache size from a UI-only module default into SDK-owned config key `paradev.desktop.thumbnail_cache.max_kb`.
- Added the key to `DEFAULT_CONFIG`, the desktop config-value allowlist, native-web REST config endpoints, and the React config-page load/write planning.
- Updated thumbnail cache read/write helpers to enforce the configured KB limit instead of a hard-coded byte constant.
- Kept the Module defaults UI visually unchanged while marking the thumbnail-cache input with `data-paradev-config-key`.
- Updated desktop architecture and GUI specs to document the SDK-backed cache size setting.

## Verification

- Red checks first failed on the hard-coded thumbnail limit, unsupported config key, missing package default, REST 400 response, and missing React row binding.
- `rtk bash scripts/test.bash tests/test_desktop_api_selection.py tests/test_native_web_bridge.py -q -k "thumbnail_cache or desktop_config_defaults_match_package_defaults or native_web_bridge_config_endpoints_are_browser_safe"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx src/services/paradev.test.ts`
- `rtk bash scripts/test.bash tests/test_desktop_api_selection.py tests/test_native_web_bridge.py tests/test_tauri_bridge.py -q`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx src/services/paradev.test.ts src/components/AppShell.test.tsx src/components/Workspace.moduleEditorConfig.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py`
- `rtk git diff --check -- src/paradev/config.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py apps/desktop/src/App.tsx apps/desktop/src/configPage/ConfigPage.tsx apps/desktop/src/App.test.ts apps/desktop/src/configPage/ConfigPage.test.tsx apps/desktop/src/services/paradev.test.ts docs/architecture/interfaces.md docs/techstack/ui/gui-spec.md`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5196`

## Notes

- The Vite production build still reports the existing large-chunk warning.
- Unrelated dirty PIHC/building-icon work remains outside this slice.
