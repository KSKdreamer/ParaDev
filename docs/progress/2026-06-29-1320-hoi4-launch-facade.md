# 2026-06-29 13:20 - Tauri HOI4 Launch Facade

## Slice

- Routed Tauri `paradev_run_hoi4` through the Python desktop helper `desktop_run_hoi4`.
- Removed duplicated Rust HOI4 launch mode parsing, Steam URL construction, default macOS game-root discovery, local launcher target selection, platform command construction, and direct spawn logic.
- Kept the TypeScript-facing Tauri command unchanged while Python owns CM_PARADEV launch defaults and game-root behavior.

## Native PIHC3 Smoke

- Launched the native Tauri app with `rtk bash scripts/run.bash --tauri`.
- Confirmed the real PIHC3 project loaded and captured `/tmp/paradev-tauri-hoi4-launch-facade.png`.
- Avoided clicking the Build page Run Game action so the smoke did not launch HOI4. The filtered-row smoke reached a stable filtered module list in `/tmp/paradev-tauri-hoi4-launch-facade-filtered.png`, but the follow-up row click still hit the project picker; UI automation remains a separate ergonomics task.

## Verification

- Red first: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_hoi4_launch_uses_python_desktop_facade -q` failed before the Rust command was patched because the body did not call `desktop_run_hoi4`.
- Green focused: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_hoi4_launch_uses_python_desktop_facade -q` passed.
- Python launch behavior: `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_hoi4_launch_payload_matches_tauri_command_rules tests/test_desktop_api_selection.py::test_desktop_hoi4_launch_uses_configured_default_mode tests/test_desktop_api_selection.py::test_desktop_hoi4_launch_uses_configured_game_root -q` passed, 3 tests.
- Bridge contracts: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py -q` passed, 6 tests.
- Rust full: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture` passed, 22 tests.
- Rust compile/format: `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` and `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check` passed.
- Frontend: `rtk npm --prefix apps/desktop test` passed, 617 tests.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed with the existing chunk-size warning.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py` passed.
- Python lint: `rtk bash scripts/flake.bash --ci` passed.
- Fast gate: `rtk bash scripts/test.bash` passed, 1180 tests, 1 warning.

## Follow-Up Queue

- Route remaining Tauri-only platform effects through Python: build command planning and open-path command planning.
- Add stable automation selectors or a non-drag row click affordance so native PIHC3 smoke tests can open module workspaces reliably.
