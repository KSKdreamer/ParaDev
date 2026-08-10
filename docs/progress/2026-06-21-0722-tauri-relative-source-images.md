# Tauri Relative Source Images Progress

Date: 2026-06-21 07:22

Linear: TAL-000

## Done

- Added Rust command coverage for project-relative source paths in the real Tauri bridge.
- Updated `paradev_read_text_source` and `paradev_read_binary_source` to resolve relative source paths under `project_root`, canonicalize them, and keep the outside-project guard.
- Verified the binary-source command can read PIHC-style `src/modules/focus_asset_component/.../preview.png` paths with `image/png` metadata and byte payloads.

## Verification

- `rtk cargo test source_reader_resolves_project_relative`
- `rtk cargo test text_source_reader_rejects_paths_outside_project_root`
- `rtk cargo test thumbnail_cache_writes_and_reads_project_cache_pngs`
- `rtk cargo test`

## Risks Or Blockers

- This strengthens the real Tauri command path but does not replace a packaged app visual smoke against PIHC3.

## Next

- Continue closing the gap between mocked browser smokes and a normal Tauri PIHC3 focus-tree editing session.
