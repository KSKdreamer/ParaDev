# 2026-06-29 13:56 - Tauri Build Planner Facade

## Slice

- Routed Tauri build command-token planning through the Python desktop helper `desktop_project_build_command`.
- Kept Rust ownership of build process lifecycle: run ids, child process handles, stdout/stderr/progress files, status polling, duplicate-run checks, and interrupt behavior.
- Removed duplicated Rust build CLI argument construction for mode, target, profile, strict metadata, parallelism, full rebuild, progress, and JSON output flags.
- Preserved pre-spawn Rust mode validation for lifecycle metadata so unsupported modes fail before a child process can be started.

## Native PIHC3 Smoke

- Launched the native Tauri app with `rtk bash scripts/run.bash --tauri`.
- Confirmed the real PIHC3 project loaded and captured `/tmp/paradev-tauri-build-planner-facade.png`.
- Opened the localized Build page through the native Tauri shell and captured `/tmp/paradev-tauri-build-planner-facade-build-page.png`.
- Did not click Build, Run, or Run HOI4 actions; the smoke verified rendering and controls only.

## Verification

- Red first: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_build_command_planning_uses_python_desktop_facade -q` failed before the Rust bridge called the Python desktop planner.
- Lifecycle red: the same test failed while mode normalization happened after `.spawn()`, proving the static assertion caught the child-process tracking risk.
- Green focused: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_build_command_planning_uses_python_desktop_facade -q` passed.
- Bridge contracts: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py -q` passed, 8 tests.
- Python build planner behavior: `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_project_build_command_matches_tauri_build_flags tests/test_desktop_api_selection.py::test_desktop_project_build_command_rejects_tauri_invalid_requests -q` passed, 2 tests.
- Rust full: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture` passed, 19 tests.
- Rust compile/format: `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` and `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check` passed.
- Frontend: `rtk npm --prefix apps/desktop test` passed, 617 tests.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed with the existing chunk-size warning.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py` passed.
- Python lint: `rtk bash scripts/flake.bash --ci` passed.
- Fast gate: `rtk bash scripts/test.bash` passed, 1182 tests, 2 warnings.

## Follow-Up Queue

- Route module draft creation through the Python REST/SDK helper instead of shaping module draft payloads in Rust.
- Normalize Rust build target lifecycle comparisons so whitespace-equivalent target ids cannot bypass duplicate-run detection.
- Add stable native-smoke selectors for build/config controls so future PIHC3 smoke checks can validate more than rendering without coordinate or localization coupling.
