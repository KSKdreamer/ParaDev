# App Config Facade

## Slice

- Routed Tauri `paradev_read_app_config` and `paradev_write_app_config` through the embedded Python desktop helper.
- Removed the Rust-side `paradev config get/set paradev.desktop.gui` subprocess helper.
- Added a source contract test so app-config commands cannot drift back to CLI-owned config plumbing.

## Native PIHC3 Smoke

- Ran `rtk bash scripts/run.bash --tauri` against the real PIHC3 project.
- Verified the native app compiled, booted, loaded the PIHC3 project, restored the Chinese locale from persisted app settings, and did not show a startup/runtime error.
- Config rail clicking remained opaque through macOS accessibility coordinates, so write-path confidence comes from the Python facade and Tauri bridge tests.

Screenshot kept outside the repo:

- `/tmp/paradev-tauri-app-config-facade-after-click.png`

## Verification

- Red first:
  - `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py -q`
- Green checks:
  - `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py tests/test_desktop_api_selection.py::test_desktop_app_config_uses_paradev_config_manager -q`
  - `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml`
  - `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check`
  - `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts src/configPage/ConfigPage.test.tsx`
  - `rtk npm --prefix apps/desktop run build`
  - `rtk npm --prefix apps/desktop test`
  - `rtk bash scripts/test.bash`
  - `rtk bash scripts/flake.bash --ci`
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py`

## Next

- Huygens queued the next SDK-bedrock slices: route Tauri source/cache reads through Python desktop helpers, replace Tauri CLI subprocess authoring bridges with Python facade calls, and move native-web canonical source/draft/module operations onto the frontend API REST bindings.
