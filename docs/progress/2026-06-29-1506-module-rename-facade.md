# Module Rename Facade Progress

Date: 2026-06-29 15:06

Linear: TAL-000

## Done

- Routed Tauri `paradev_rename_module` through the embedded Python helper and SDK `Project.rename_module(...)`.
- Removed the Rust-owned `uv run paradev module-rename ...` subprocess path for this GUI mutation.
- Preserved old bridge behavior by rejecting blank project/module/object fields and treating blank `sourceRoot` as omitted.
- Added a static bridge regression that locks the Python helper route and `sourceRoot` normalization.

## Verification

- `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py::test_tauri_module_rename_uses_python_sdk_facade -q`
- `rtk bash scripts/test.bash --serial tests/test_project.py::test_module_rename_moves_source_module_without_rewriting_content tests/test_project.py::test_module_rename_rejects_existing_destination tests/test_project.py::test_module_rename_can_select_duplicate_module_id_source_root tests/test_cli.py::test_module_rename_cli_moves_source_module -q`
- `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml`
- `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml -- --nocapture`
- `rtk bash scripts/test.bash --serial tests/test_tauri_bridge.py -q`
- `rtk npm --prefix apps/desktop test`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_tauri_bridge.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- Native Tauri smoke: `rtk bash scripts/run.bash --tauri --port 5194`, captured `/tmp/paradev-tauri-module-rename-facade.png`.
- `projects/PIHC3` remained clean.

## Risks Or Blockers

- `npm run build` still reports the existing large-chunk warning.
- The TypeScript service type still names the module rename payload schema differently from the SDK payload; existing runtime behavior already returned the SDK schema, so this was left for a separate API-alignment slice.

## Next

- Continue moving remaining native bridge commands that still own SDK behavior into Python helpers.
- Follow up on module rename TypeScript payload schema naming and broader GUI API alignment.
