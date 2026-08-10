# Draft Apply Facade Progress

Date: 2026-06-29 14:36

Linear: TAL-000

## Done

- Routed Tauri `paradev_apply_project_draft` through the Python REST facade `apply_project_draft` instead of the Rust-owned temp request file and `uv run paradev draft-apply` path.
- Added a stdin-backed desktop helper payload path so large binary source replacements do not hit the macOS argv limit.
- Kept binary replacement normalization explicit by mapping Tauri `contentBase64` to SDK `content_base64`.
- Added bridge and Rust command regressions, including a >1 MB base64 replacement payload.

## Verification

- `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_project_draft_apply_uses_python_rest_facade -q`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml apply_project_draft -- --nocapture`
- `rtk bash scripts/test.bash --serial tests/test_architecture.py::test_rest_apply_project_draft_writes_validated_project_text tests/test_architecture.py::test_rest_apply_project_draft_can_write_new_png_replacements -q`
- `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check`
- `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture`
- `rtk npm --prefix apps/desktop test`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- Native Tauri smoke: `rtk bash scripts/run.bash --tauri --port 5192`, opened the real PIHC3 project panel and captured `/tmp/paradev-tauri-pihc3-country-section.png`.
- `projects/PIHC3` remained clean.

## Risks Or Blockers

- The PIHC3 project selector title is truncated, so the visible title can obscure that the selected root is the real PIHC3 path.
- Clicking a family row highlights it but leaves the workspace empty in this smoke path; this is a UX follow-up, not a blocker for the draft-apply bridge.
- `npm run build` still reports the existing large-chunk warning.

## Next

- Continue moving remaining native Tauri mutation bridges behind Python SDK or REST facade helpers.
- Add a later GUI usability pass for the PIHC3 family-selection-to-workspace flow.
