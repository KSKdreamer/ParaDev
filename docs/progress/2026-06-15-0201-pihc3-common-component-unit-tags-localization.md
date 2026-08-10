# 2026-06-15 02:01 PIHC3 common component unit-tags localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for compiled unit-category support. This keeps `common/unit_tags/00_categories.txt` in the shared path-preserving common-component family instead of adding a dedicated module type for one category-list file.

## Changes

- Added path-gated localization extraction for `common/unit_tags/*.txt`.
- Extraction now reads `sub_unit_categories = { ... }` and owns top-level `category_*` display rows.
- Unprefixed unit names such as `infantry_traditional` remain outside the unit-tag component.
- Regenerated 48 common component modules.
- Generated `main.loc` for `COMMON_COMPONENT_UNIT_TAGS_00_CATEGORIES`.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/unit_tags/00_categories.txt`.
- Green contract after the path-gated extractor change and exact-header assertion fix: `1 passed, 165 deselected in 311.41s`.
- Post-format focused contract: `1 passed, 165 deselected in 309.62s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: unit tags now have `loc_key_count: 100`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-unit-tags-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,460 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 250 `common_component` localization artifacts from 29 localized common-component modules.

## Follow-Up

- Continue common-component localization only where display keys are directly and safely derivable from compiled PDX.
- Keep map-adjacent terrain support out of this family until the skipped-map slice resumes.
