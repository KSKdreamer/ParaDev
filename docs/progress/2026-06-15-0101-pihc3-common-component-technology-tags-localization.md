# 2026-06-15 01:01 PIHC3 common component technology-tags localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for compiled PIHC technology category support. This keeps `common/technology_tags/00_technology.txt` in the shared path-preserving common-component family instead of adding a dedicated tag module type.

## Changes

- Added path-gated localization extraction for `common/technology_tags/*.txt`.
- Extraction now reads `technology_categories = { ... }` and owns PIHC-specific `pihc_*` category rows plus matching `_research` modifier rows.
- Vanilla technology-folder labels remain with current-game localization.
- The compiled PDX category `pihc_commu_tech` has no matching PIHC_dev localization row, so no module-local row is invented for it.
- Regenerated 48 common component modules.
- Generated `main.loc` for `COMMON_COMPONENT_TECHNOLOGY_TAGS_00_TECHNOLOGY`.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/technology_tags/00_technology.txt`.
- Green contract after the path-gated extractor change: `1 passed, 165 deselected in 278.02s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: technology tags now have `loc_key_count: 288`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-technology-tags-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,448 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 238 `common_component` localization artifacts from 27 localized common-component modules.

## Follow-Up

- Continue common-component localization only where display keys are clearly source-owned by compiled PDX.
- Keep map-adjacent terrain support out of this family until the skipped-map slice resumes.
