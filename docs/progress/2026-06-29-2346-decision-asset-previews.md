# Decision Asset Previews

Time: 2026-06-29 23:46 CST

Continued the PIHC3 usability loop by making compiled decision asset components visible in the module browser/editor.

- Moved the existing focus DDS-to-PNG preview conversion into a shared HOI4 Python helper.
- Wired decision asset migration to emit `preview.png` for DDS-backed modules and record `preview_image_path` / `preview_image_source` in metadata.
- Regenerated PIHC3 decision asset components: 464 modules, 462 DDS-backed previews, 463 GFX files.
- Updated the desktop module editor model so metadata previews are used for thumbnails without adding `preview.png` to editable runtime source slots.
- Refreshed the API catalog reference row count for the current desktop API table.

Validation:

- Red first: targeted decision asset migration tests failed on missing `preview.png` and missing preview metadata.
- Green focused: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'decision_asset_component_importer_groups_decision_sprites_and_icons or decision_asset_component_importer_extracts_metadata_contract'`: 2 passed.
- Focus regression: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'focus_asset_component_importer_groups_focus_sprites_and_icons or focus_asset_component_importer_extracts_metadata_contract'`: 2 passed.
- Runtime output check: `Project.load("projects/PIHC3").build(family="decision_asset_component")` produced 925 output artifacts and 0 `preview.png` output artifacts.
- Desktop model: `rtk npm run test -- src/moduleEditor/model.test.ts` in `apps/desktop`: 30 passed.
- Desktop build: `rtk npm run build` in `apps/desktop`: passed with the existing large-chunk warning.
- Desktop unit suite: `rtk npm run test` in `apps/desktop`: 50 files, 651 tests passed.
- API catalog drift checks: 6 targeted tests passed after regenerating `docs/user-manual/api-catalog-reference.md`.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/images.py tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_decision_asset_components.py projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk git diff --check`: passed in both ParaDev and PIHC3.
- `rtk bash scripts/test.bash`: 1201 passed.
- Native Tauri smoke: `rtk env PARADEV_ROOT=/tmp/paradev-decision-preview-smoke PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5224` compiled and launched `target/debug/paradev-desktop` before shutdown.

Risks:

- The smoke launch verified native startup with PIHC3 configured, but did not capture an inspected native screenshot.
- Decision previews are editor/provenance assets and intentionally do not emit to the HOI4 output mod.
