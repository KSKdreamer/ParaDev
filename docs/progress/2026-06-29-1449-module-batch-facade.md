# Module Batch Facade Progress

Date: 2026-06-29 14:49

Linear: TAL-000

## Done

- Routed Tauri `paradev_module_batch_request` through the Python SDK method `Project.module_batch_edit_request(...)`.
- Removed the old Rust-owned temp request file and `uv run paradev module-batch-request --request ...` bridge.
- Reused the stdin-backed Python helper payload path so large edit batches do not depend on argv limits.
- Removed the now-unused `temp_json_request_path` helper from the Tauri bridge.
- Added a static Tauri bridge regression proving the command no longer owns the CLI/temp-file path.

## Verification

- `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_module_batch_request_uses_python_sdk_facade -q`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml module_batch_request_command_returns_target_preview -- --nocapture`
- `rtk bash scripts/test.bash --serial tests/test_project.py::test_module_batch_edit_request_builds_pihc3_style_request tests/test_project.py::test_module_batch_edit_request_rejects_unknown_pihc3_module_targets tests/test_project.py::test_module_batch_edit_request_rejects_missing_pihc3_file_targets_without_create tests/test_cli.py::test_module_batch_request_cli_emits_canonical_json_request tests/test_cli.py::test_module_batch_request_cli_rejects_missing_targets_without_create tests/test_cli.py::test_module_batch_request_cli_output_feeds_batch_edit_stdin -q`
- `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check`
- `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture`
- `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py -q`
- `rtk npm --prefix apps/desktop test`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- Native Tauri smoke: `rtk bash scripts/run.bash --tauri --port 5193`, captured `/tmp/paradev-tauri-module-batch-facade.png`.
- `projects/PIHC3` remained clean.

## Risks Or Blockers

- `npm run build` still reports the existing large-chunk warning.
- Follow-up coverage should add REST parity for `/desktop/modules/batch-request` and a large module-batch stdin payload regression.

## Next

- Continue removing remaining GUI-side Rust ownership of SDK behaviors.
- Use a later GUI usability slice to make PIHC3 family selection open an obvious workspace view.
