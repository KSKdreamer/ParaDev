# 2026-06-29 14:16 - Tauri Module Draft Facade

## Slice

- Routed Tauri `paradev_create_module_draft` through the Python REST/SDK helper `create_module_draft`.
- Removed duplicated Rust CLI scaffold invocation, value-to-`--value` conversion, and REST wrapper payload shaping.
- Kept the Tauri command request shape unchanged while Python owns project loading, browser-family template resolution, scaffold planning, write blocking, and `paradev.rest.module_draft.v1` payload construction.
- Added REST helper coverage for blocked `write=true` drafts so a blocked plan returns a normal payload with diagnostics instead of becoming a failed CLI command.

## Native PIHC3 Smoke

- Launched the native Tauri app with `rtk bash scripts/run.bash --tauri`.
- Confirmed the real PIHC3 project loaded and captured `/tmp/paradev-tauri-module-draft-facade.png`.
- Opened the localized editor rail against PIHC3 families and captured `/tmp/paradev-tauri-module-draft-facade-editor.png`.
- Did not click Apply, Write, Build, or Run actions. Deeper row-opening/editor automation still needs stable selectors to avoid coordinate and localization coupling.

## Verification

- Red first: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_module_draft_uses_python_rest_facade -q` failed before the Tauri command delegated to `create_module_draft`.
- Green focused: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_module_draft_uses_python_rest_facade -q` passed.
- Bridge contracts: `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py -q` passed, 9 tests.
- REST helper behavior: `rtk bash scripts/test.bash --serial tests/test_architecture.py::test_rest_create_module_draft_uses_sdk_family_resolution tests/test_architecture.py::test_rest_create_module_draft_returns_blocked_write_payload -q` passed, 2 tests.
- Rust draft behavior: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml create_module_draft -- --nocapture` passed, 2 tests.
- Rust full: `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture` passed, 19 tests.
- Rust compile/format: `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` and `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check` passed.
- Frontend: `rtk npm --prefix apps/desktop test` passed, 617 tests.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed with the existing chunk-size warning.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py tests/test_architecture.py` passed.
- Python lint: `rtk bash scripts/flake.bash --ci` passed.
- Fast gate: `rtk bash scripts/test.bash` passed, 1184 tests, 1 warning.

## Follow-Up Queue

- Route project draft apply and module batch request through Python helpers instead of Rust temp-file request plumbing.
- Add stable native-smoke selectors for module/family rows and editor actions so PIHC3 module-open/create flows can be validated without coordinate or localization coupling.
- Decide whether blocked module-draft payload behavior needs frontend copy changes now that the Tauri path matches REST instead of failing the command.
