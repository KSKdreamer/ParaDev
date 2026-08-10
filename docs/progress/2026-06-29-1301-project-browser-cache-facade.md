# 2026-06-29 13:01 - Tauri Project Browser Cache Facade

## Slice

- Routed Tauri `paradev_read_project_browser_cache` and `paradev_write_project_browser_cache` through the Python desktop helper layer.
- Removed Tauri-side project-browser cache pathing, schema/root validation, stale-cache deletion, size checks, JSON reads, and JSON writes for this command pair.
- Kept the TypeScript-facing Tauri command names unchanged while moving cache behavior behind `read_project_browser_cache` and `desktop_write_browser_cache`.

## Native PIHC3 Smoke

- Launched the native Tauri app with `rtk bash scripts/run.bash --tauri`.
- Confirmed the real PIHC3 project loaded after the cache routing change and captured `/tmp/paradev-tauri-project-browser-cache-facade.png`.
- Epicurus found that previous category-row clicks were unreliable because search/filter state changes row positions and reorderable rows can suppress slightly drag-like clicks. The better native smoke path is to filter to a stable module id such as `focuses`, then click the first visible module row.

## Verification

- Red first: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_project_browser_cache_commands_use_python_desktop_facade -q` failed before the Rust command was patched because the body used `project_browser_cache_path`.
- Green focused: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_project_browser_cache_commands_use_python_desktop_facade -q` passed.
- Desktop API: `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py -q` passed, 37 tests.
- Bridge contracts: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py -q` passed, 5 tests.
- Rust focused: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml project_browser_cache -- --nocapture` passed, 1 test.
- Rust full: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture` passed, 24 tests.
- Rust compile/format: `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` and `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check` passed after removing a dead helper.
- Frontend: `rtk npm --prefix apps/desktop test` passed, 617 tests.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed with the existing chunk-size warning.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py` passed.
- Python lint: `rtk bash scripts/flake.bash --ci` passed.
- Fast gate: `rtk bash scripts/test.bash` passed, 1179 tests, 2 warnings.

## Follow-Up Queue

- Use the filtered first-row native smoke path for the next GUI run.
- Route the next Tauri-only platform effects through Python: HOI4 launch, build command planning, and open-path command planning.
