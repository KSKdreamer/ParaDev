# 2026-06-29 13:38 - Tauri Open Path Facade

## Slice

- Routed Tauri `paradev_open_path` through the Python desktop helper `desktop_open_path`.
- Removed duplicated Rust open-path validation, default target selection, Finder/Explorer/editor/terminal command mapping, and direct spawn logic.
- Kept the TypeScript-facing Tauri command unchanged while Python owns local path opener behavior.

## Native PIHC3 Smoke

- Launched the native Tauri app with `rtk bash scripts/run.bash --tauri`.
- Confirmed the real PIHC3 project loaded in the localized shell and captured `/tmp/paradev-tauri-open-path-facade.png`.
- Verified the accessible search field can be focused and updates the real project module list; captured `/tmp/paradev-tauri-open-path-facade-accessible-search.png` and `/tmp/paradev-tauri-open-path-facade-clear-attempt.png`.
- Did not click Run Game or any destructive action. A deeper module-open smoke remains brittle because list rows still lack durable native-smoke selectors; this matches the GUI-smoke explorer's finding.

## Verification

- Red first: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_open_path_uses_python_desktop_facade -q` failed before the Rust command was patched because the body did not call `desktop_open_path`.
- Green focused: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_open_path_uses_python_desktop_facade -q` passed.
- Bridge contracts: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py -q` passed, 7 tests.
- Python open-path behavior: `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_open_path_command_matches_tauri_targets -q` passed.
- Rust full: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture` passed, 21 tests.
- Rust compile/format: `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` and `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check` passed.
- Frontend: `rtk npm --prefix apps/desktop test` passed, 617 tests.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed with the existing chunk-size warning.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py` passed.
- Python lint: `rtk bash scripts/flake.bash --ci` passed.
- Fast gate: `rtk bash scripts/test.bash` passed, 1181 tests.

## Follow-Up Queue

- Route Tauri build command-token planning through `desktop_project_build_command` while keeping Rust build process handles/status/interrupt.
- Add stable native-smoke selectors for rail ids, search, option ids, workspace tabs, entity rows, build actions, and config controls so PIHC3 module-open/build/config smoke can avoid localization and coordinate coupling.
