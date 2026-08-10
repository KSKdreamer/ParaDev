# PIHC3 Technology Metadata Extraction

Status: completed slice

## Scope

- Updated `projects/PIHC3/scripts/migrate_pihc2_technologies.py` so native technology modules expose compiled PDX data in `meta.yaml` settings.
- Regenerated all 300 `src/modules/technology/TECHNOLOGY_<TAG>` modules.
- Kept the project-local `technology` family on shared `def` and `loc` slots; no family-specific compiler code was added.

## Details

- Technology metadata now records `technology_keys`, folder positions, categories, equipment and subunit unlocks, dependencies, path blocks, research cost, and start year from the compiled PIHC_dev body.
- Repeated PDX keys such as multi-edge `path` entries are preserved as lists in metadata instead of being collapsed.
- PIHC2 root GUI source fields are recorded under `legacy_root_gui` when `is_root` appears in `resources/technologies/<TAG>/info.json`.
- PDX `yes` and `no` scalar values are normalized to booleans for cleaner GUI browsing.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_technology_importer_extracts_compiled_technology_contract -q` failed on missing `technology_keys`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_technology_importer_extracts_compiled_technology_contract -q` passed.
- Focused suite: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'technology_importer or technology_family or technology_component or technology_asset_component'` passed with 6 tests and 145 deselected.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_technologies.py --clean` imported 300 technology modules.
- Build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-technology-metadata-build.json` exited 0 and reported 16,581 modules, 62 collections, 37,370 artifacts, 713 diagnostics, 0 errors, `blocked: false`.

## Remaining

- Root technology GUI fragments are still emitted through legacy copy paths, not rebuilt from structured native source.
- Technology icon DDS/GFX generation from `default.png` source evidence remains future work.
- Equipment/module unlock side effects, doctrine coordination, and full parity review against PIHC_dev remain open.
