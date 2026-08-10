# Text Source Facade

## Slice

- Routed Tauri `paradev_read_text_source` through the embedded Python desktop helper.
- Kept text-source path containment, file validation, UTF-8 decoding, and size limits owned by `paradev.desktop.local.desktop_read_text_source`.
- Tightened Python desktop-helper subprocess errors so Tauri receives concise facade error messages instead of Python tracebacks.
- Extended the Tauri bridge source-contract test to prevent text-source reads from drifting back to Rust filesystem logic.

## Native PIHC3 Smoke

- Ran `rtk bash scripts/run.bash --tauri` against the real PIHC3 project.
- Opened the PIHC3 Equipment module and selected `EQUIPMENT_MAGICAL_RANGED_SNIPER`.
- Verified the source-backed editor and bilingual localization rows rendered without a startup/runtime error.

Screenshot kept outside the repo:

- `/tmp/paradev-tauri-text-source-facade.png`

## Verification

- Red first:
  - `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_text_source_reads_use_python_desktop_facade -q`
- Green checks:
  - `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py tests/test_desktop_api_selection.py::test_desktop_read_text_and_binary_source_payloads -q`
  - `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml text_source_reader -- --nocapture`
  - `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture`
  - `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml`
  - `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check`
  - `rtk npm --prefix apps/desktop test`
  - `rtk npm --prefix apps/desktop run build`
  - `rtk bash scripts/flake.bash --ci`
  - `rtk bash scripts/test.bash`
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py`

## Next

- Continue moving source/cache Tauri commands through Python desktop helpers: binary source, thumbnail cache, and project browser cache.
- Parfit queued GUI/user smoke scenarios for PIHC3 modders: idea creation plus localization edit, C08 country/flag inspection, and a rendered Build-page lifecycle smoke.
