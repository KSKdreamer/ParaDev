# 2026-06-29 08:23 - HOI4 Game Root Config

## Slice

- Added `paradev.hoi4.game_root` to `CM_PARADEV` defaults as an empty optional override.
- Exposed the game root through the desktop config-value bridge with trim-and-clear behavior.
- Made Python `desktop_run_hoi4(...)` and `desktop_hoi4_launch_command(...)` use the configured root when callers omit `game_root`.
- Added a translated Config page field under Projects -> Project paths for `paradev.hoi4.game_root`.
- Loaded the same config value in the Build page and passed it into `runHoi4Game(...)` so Tauri and native-web launch requests share the SDK-backed setting.

## Verification

- Red checks first:
  - `rtk uv run pytest tests/test_desktop_api_selection.py tests/test_native_web_bridge.py -k "hoi4 or config"`
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/buildPageModel.test.ts src/configPage/ConfigPage.test.tsx src/App.test.ts src/services/paradev.test.ts`
- Green/final checks:
  - `rtk uv run pytest tests/test_desktop_api_selection.py tests/test_native_web_bridge.py -k "hoi4 or config"`
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/buildPageModel.test.ts src/configPage/ConfigPage.test.tsx src/App.test.ts src/services/paradev.test.ts`
  - `rtk npm --prefix apps/desktop run build`
  - `rtk npm --prefix apps/desktop run test:unit -- --run`
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config.py src/paradev/desktop/local.py src/paradev/desktop/shell.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py`
  - `rtk bash scripts/flake.bash --ci`
  - `rtk bash scripts/test.bash`
  - `rtk git diff --check`

## Tauri Smoke

- Ran `rtk bash scripts/run.bash --tauri` against the real PIHC3 project.
- Verified Settings -> Projects shows the translated HOI4 game root field with `paradev.hoi4.game_root`.
- Verified the native Build page loads PIHC3 and keeps the HOI4 launch mode dropdown and Run button aligned after config hydration.
- Screenshots:
  - `/tmp/paradev-tauri-hoi4-root-projects.png`
  - `/tmp/paradev-tauri-hoi4-root-build.png`
