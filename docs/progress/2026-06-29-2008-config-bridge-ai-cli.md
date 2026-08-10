# Config Bridge AI CLI Progress

Date: 2026-06-29 20:08

Linear: TAL-000

## Done

- Extended desktop service bridge tests so Tauri and native-web wrappers cover `paradev.cli.output`, `paradev.ai.key_env`, and `paradev.ai.model` in addition to build and HoI4 keys.
- Extended the native-web REST config endpoint test so browser-safe CORS requests round-trip CLI output and every AI route value through `CM_PARADEV` with cleanup.
- Added Tauri static coverage that pins config-value commands to the Python desktop facade.
- Added a drift test comparing desktop-exposed config defaults with package `DEFAULT_CONFIG`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/services/paradev.test.ts`
- `rtk bash scripts/test.bash tests/test_native_web_bridge.py tests/test_desktop_api_selection.py tests/test_tauri_bridge.py -q`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_native_web_bridge.py tests/test_desktop_api_selection.py tests/test_tauri_bridge.py`
- `rtk git diff --check -- apps/desktop/src/services/paradev.test.ts tests/test_native_web_bridge.py tests/test_desktop_api_selection.py tests/test_tauri_bridge.py docs/progress/2026-06-29-2008-config-bridge-ai-cli.md`

## Risks Or Blockers

- This is a contract-coverage slice only; it does not change the rendered config page or AI chat behavior.
- The worktree still contains unrelated building-icon and PIHC3 migration changes from other work.

## Next

- Continue GUI usability work with real PIHC3 Tauri checks, or add another small SDK-backed config/action bridge contract where the GUI still depends on local assumptions.
