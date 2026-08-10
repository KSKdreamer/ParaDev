# 2026-06-29 12:41 - Tauri Thumbnail Cache Facade

## Slice

- Routed Tauri `paradev_read_thumbnail_cache` and `paradev_write_thumbnail_cache` through the Python desktop helper layer.
- Removed Tauri-side thumbnail cache pathing, FNV hashing, size checks, filesystem reads/writes, and PNG payload construction for this command pair.
- Kept the TypeScript-facing Tauri command names unchanged while moving the local cache behavior behind `desktop_read_thumbnail_cache` and `desktop_write_thumbnail_cache`.

## Native PIHC3 Smoke

- Launched the native Tauri app with `rtk bash scripts/run.bash --tauri`.
- Confirmed the real PIHC3 project loaded and captured `/tmp/paradev-tauri-thumbnail-cache-countries-open-3.png`.
- Attempted to open the country module workspace through native coordinate clicks, but the webview automation stayed on the category screen. Treat this as a boot/project visibility smoke for this slice; the exact thumbnail cache command path is covered by the Tauri Rust and Python bridge tests.

## Verification

- Red first: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_thumbnail_cache_commands_use_python_desktop_facade -q` failed before the Rust command was patched because the body did not call `desktop_read_thumbnail_cache`.
- Green focused: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py tests/test_desktop_api_selection.py::test_desktop_thumbnail_cache_matches_tauri_path_and_payload -q` passed, 5 tests.
- Rust focused: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml thumbnail_cache_writes_and_reads_project_cache_pngs -- --nocapture` passed, 1 test.
- Rust full: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture` passed, 24 tests.
- Rust compile/format: `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` and `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check` passed.
- Frontend: `rtk npm --prefix apps/desktop test` passed, 617 tests.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed with the existing chunk-size warning.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py` passed.
- Python lint: `rtk bash scripts/flake.bash --ci` passed.
- Fast gate: `rtk bash scripts/test.bash` passed, 1178 tests.

## Follow-Up Queue

- Route Tauri project browser cache read/write through the existing Python helpers next.
- Then consider HOI4 launch, build command planning, and open-path command planning from Banach's read-only boundary scan.
- Improve native GUI smoke ergonomics so a scripted PIHC3 category-row click reliably opens the corresponding module workspace.
