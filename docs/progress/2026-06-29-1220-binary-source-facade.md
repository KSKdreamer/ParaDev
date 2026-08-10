# 2026-06-29 12:20 - Tauri Binary Source Facade

## Slice

- Routed the Tauri `paradev_read_binary_source` command through the Python desktop helper `desktop_read_binary_source`.
- Kept binary source ownership in the Python SDK layer: project path containment, max payload checks, MIME inference, byte encoding, and error shape now share the same implementation as native-web and direct SDK callers.
- Removed the now-dead Rust `project_source_path` and `mime_type_for_path` helpers after both text and binary source reads moved behind the desktop facade.

## Native PIHC3 Smoke

- Launched the native Tauri app with `rtk bash scripts/run.bash --tauri`.
- Confirmed the real PIHC3 project loaded in the native app and captured `/tmp/paradev-tauri-binary-source-facade.png`.
- The GUI smoke verified app boot/project visibility after the bridge change. Direct image thumbnail selection was not reached through native automation because the current search field filters module categories/settings rather than module ids, so the binary command path is covered by Rust/Python bridge tests for this slice.

## Verification

- Red first: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_binary_source_reads_use_python_desktop_facade -q` failed before the Rust command was patched.
- Green focused: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_binary_source_reads_use_python_desktop_facade -q` passed after the patch.
- Rust focused: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml binary_source_reader -- --nocapture` passed, 1 test.
- Rust full: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture` passed, 24 tests.
- Rust compile/format: `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` and `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check` passed.
- Python focused: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py tests/test_desktop_api_selection.py::test_desktop_read_text_and_binary_source_payloads -q` passed, 4 tests.
- Frontend: `rtk npm --prefix apps/desktop test` passed, 617 tests.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed with the existing chunk-size warning.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py` passed.
- Python lint: `rtk bash scripts/flake.bash --ci` passed.
- Fast gate: `rtk bash scripts/test.bash` passed, 1177 tests, 1 warning.

## Follow-Up Queue

- Continue moving Tauri-only source/cache operations behind Python desktop helpers, especially thumbnail cache reads/writes.
- Use Russell's read-only PIHC3 findings for the next PIHC3 slice: clarify country flag ownership, add browser-friendly PNG country previews, then trim verbose flag asset metadata from modder-facing `meta.yaml`.
