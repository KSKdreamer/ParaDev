# 2026-06-29 07:44 - AI Route Config Page

## Slice

- Promoted the desktop AI route defaults to `CM_PARADEV` keys: `paradev.ai.preset`, `paradev.ai.provider`, `paradev.ai.gateway`, `paradev.ai.model`, and `paradev.ai.key_env`.
- Extended the desktop config-value bridge so Tauri, native-web, CLI tests, and Python scripts read and write the same AI route values.
- Changed the Models config page from read-only route chips to editable config-backed controls.
- Localized AI chat profile source-kind labels so the Chinese UI no longer shows raw `project / selection / diagnostics` ids.

## Verification

- Red checks first:
  - `rtk uv run pytest tests/test_desktop_api_selection.py -k "ai_route"`
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx`
- Green/final checks:
  - `rtk uv run pytest tests/test_desktop_api_selection.py -k "ai_route"`
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx`
  - `rtk npm --prefix apps/desktop run build`
  - `rtk npm --prefix apps/desktop run test:unit -- --run`
  - `rtk uv run pytest tests/test_desktop_api_selection.py tests/test_native_web_bridge.py -k "config"`
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py`
  - `rtk bash scripts/flake.bash --ci`
  - `rtk bash scripts/test.bash`
  - `rtk git diff --check`

## Tauri Smoke

- Ran `rtk bash scripts/run.bash --tauri` against the real PIHC3 project.
- Verified the native Models config page shows editable `paradev.ai.*` controls and PIHC3 project state.
- Screenshot: `/tmp/paradev-smoke/ai-route-config-models-tauri.png`

## Follow-Up

- Maxwell found a separate SDK-first config gap: HOI4 launch mode is still stored as frontend local state. Keep that as the next small config slice rather than mixing it into this AI route commit.
