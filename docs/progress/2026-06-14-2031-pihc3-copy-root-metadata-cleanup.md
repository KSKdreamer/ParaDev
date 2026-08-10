# PIHC3 Copy-Root Metadata Cleanup

## Slice

Removed non-game metadata and helper files from the PIHC_dev compatibility copy root:

- `.DS_Store` at any depth;
- Python helper scripts at any depth;
- `common/**/_documentation.md`;
- `common/**/documentation.md`.

This is a shared overlay hygiene rule rather than a new module family. It keeps generated PIHC3 output from shipping Finder metadata, local helper scripts, or HOI4 documentation markdown.

## Changes

- Added the copy-root exclusion contract `test_pihc3_copy_overlay_excludes_non_game_metadata_and_helper_files`.
- Added broad copy-root excludes in `projects/PIHC3/paradev.yaml`.
- Updated migration design, copy overlay, support-component, and shared legacy inventory docs with the current build counts and 17-file support-component source shape.

## Verification

- Red check before the manifest change:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k copy_overlay_excludes_non_game_metadata`
  - Failed on `common/.DS_Store` still being copy-root planned.
- Green check after the manifest change:
  - `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k copy_overlay_excludes_non_game_metadata`
  - `1 passed, 148 deselected`.
- Emit build:
  - `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-copy-root-metadata-cleanup-build.json`
  - Summary: 16,569 modules, 62 collections, 36,179 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
  - Active copy-root artifacts: 1,415.
  - Copy-root-owned `.DS_Store` artifacts: 0.
  - Copy-root-owned common documentation markdown artifacts: 0.
  - Copy-root-owned Python helper script artifacts: 0.

## Next

Continue with non-map copy-root leftovers that are real game assets. Map shaders, border meshes, map arrows, minimap files, state history, state categories, and terrain should remain skipped until the map migration slice.
