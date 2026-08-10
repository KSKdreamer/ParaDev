# PIHC3 Technology Previews

Date: 2026-07-01

## Summary

Added root `preview.png` support to the PIHC2 technology importer and applied it to PIHC3 technology modules with preserved PNG source images.

## Changes

- Reused each technology module's preserved legacy PNG as a root `preview.png`.
- Added `preview_image_path` and `preview_image_source` metadata for 277 technology modules.
- Kept technology `source_slot_counts` unchanged, so previews remain authoring/GUI metadata and do not add emitted HoI4 artifact slots.
- Avoided committing regenerated `def.txt`/`main.loc` churn from the migration run.

## Verification

- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k technology_importer_extracts_source_localization_and_image_metadata_contract`
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k 'technology_component_family_preserves_compiled_paths or technology_importer_preserves_compiled_pdx_contract or technology_importer_extracts_compiled_fields_contract'`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_technologies.py tests/test_pihc3_migration_contracts.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk git -C projects/PIHC3 diff --check`
- `rtk git diff --check`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47854` reached Vite ready, finished Cargo build, launched `target/debug/paradev-desktop`, and showed no late startup output before shutdown.
