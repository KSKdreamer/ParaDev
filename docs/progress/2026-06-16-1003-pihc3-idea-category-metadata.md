# 2026-06-16 10:03 PIHC3 idea-category metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching native `idea_category` metadata. The family still keeps nested `IDEA_ERA_*` laws embedded inside six parent category modules and uses existing `def`, `loc`, and `icons` slots.

## Changes

- Added a red metadata contract for generated `idea_category` `meta.yaml` settings.
- Added importer metadata for category ids, source slot counts, PIHC2 source evidence, `info.json` keys, level policy, folded localization languages and keys, ordered nested child ids, parent scalar fields, child field keys, default/on-add/on-remove child ids, picture keys, costs/removal costs/levels, modifier keys, available/allowed-civil-war roots, compiled icon paths, and DDS header/size summaries.
- Copied PIHC2 category and child `info.json`, `locs.txt`, and `default.png` files under each module's non-emitted `legacy/idea_categories/...` tree.
- Regenerated all 6 native idea-category modules under `projects/PIHC3/src/modules/idea_category/`.
- Updated the idea-category migration note, PIHC3 design summary, and legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k idea_category_importer_extracts_metadata_contract` failed with `KeyError: 'category_id'`.
- Green focused contract before regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k idea_category_importer_extracts_metadata_contract` passed with 1 test and 223 deselected.
- Regeneration: `Migrated idea categories: 6`.
- Metadata coverage: 6 idea-category modules now have 49 settings keys each. The regenerated set covers 33 nested laws, 33 compiled DDS icons, and 111 non-emitted PIHC2 source-evidence files.
- Formatting: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_idea_categories.py tests/test_pihc3_migration_contracts.py` reformatted the test file; the importer was already formatted.
- Green focused group after regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k idea_category` passed with 1 test and 223 deselected.
- Black check: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_idea_categories.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-idea-category-metadata-build.json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 51 `module:idea_category/...` artifacts: 6 `common/ideas/IDEA_CATEGORY_*.txt`, 12 localization YAML files, and 33 `gfx/interface/ideas/idea_ERA_*.dds` icons, with 0 idea-category-owned `copy_root` artifacts.

## Follow-Up

Nested `IDEA_ERA_*` law splitting remains unnecessary until GUI workflows need child-level editing. Source-image regeneration for category icons, balance review, and broader multi-language parity review remain future slices.
