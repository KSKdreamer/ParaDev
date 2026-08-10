# 2026-06-29 08:04 - HOI4 Launch Mode Config

## Slice

- Added `paradev.hoi4.launch_mode` to `CM_PARADEV` defaults.
- Exposed the launch mode through the desktop config-value bridge with `steam` / `local` validation.
- Made Python `desktop_run_hoi4(...)` and `desktop_hoi4_launch_command(...)` honor the configured default when callers omit `mode`.
- Moved the Build page launch dropdown away from frontend-local persistence and into `readConfigValue(...)` / `writeConfigValue(...)`.
- Removed stale legacy `paradev.build.launchMode` localStorage state when Build page settings are written.
- Guarded the Run HOI4 action until desktop launch-mode config hydration finishes.

## Verification

- Red checks first:
  - `rtk uv run pytest tests/test_desktop_api_selection.py tests/test_native_web_bridge.py -k "launch_mode or config_endpoints"`
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/buildPageModel.test.ts src/services/paradev.test.ts`
- Green/final checks:
  - `rtk uv run pytest tests/test_desktop_api_selection.py tests/test_native_web_bridge.py -k "hoi4 or config"`
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/buildPageModel.test.ts src/services/paradev.test.ts src/buildPage/BuildPage.test.tsx`
  - `rtk npm --prefix apps/desktop run build`
  - `rtk npm --prefix apps/desktop run test:unit -- --run`
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config.py src/paradev/desktop/local.py src/paradev/desktop/shell.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py`
  - `rtk bash scripts/flake.bash --ci`
  - `rtk bash scripts/test.bash`
  - `rtk git diff --check`

## Tauri Smoke

- Ran `rtk bash scripts/run.bash --tauri` against the real PIHC3 project.
- Verified the native Build page loads PIHC3 and shows the HOI4 launch mode dropdown next to the build mode selector.
- Screenshot: `/tmp/paradev-smoke/hoi4-launch-mode-build-page.png`
