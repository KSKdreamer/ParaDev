# 2026-06-14 22:45 PIHC3 common component collection and medal localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership beyond abilities and state categories. This slice keeps the family generic: collections and medals still use the shared PDX slot plus optional `main.loc`, with importer-side key extraction from explicit compiled PDX localization fields.

## Changes

- Added common-component localization extraction for `common/collections/*.txt` from explicit `name = COLLECTION_*` fields.
- Added common-component localization extraction for `common/medals/00_medals.txt` from explicit career-profile `name`, `description`, and `tooltip` fields.
- Kept extraction path-gated to collections and medals to avoid broad duplicate localization ownership.
- Filtered per-language section-style `.loc` values that begin with `[` because the ParaDev loader parses leading brackets as headers.
- Normalized trailing whitespace from imported multiline localization values before writing generated `.loc` files.
- Regenerated 48 common component modules.
- Wrote `main.loc` for 16 common modules: leader abilities, 2 collection modules, medals, and all 12 state-category modules.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with no `l_english` rows for `common/collections/collections.txt`.
- Green contract after extractor and bracket-start filtering: `1 passed, 150 deselected in 99.17s`.
- Whitespace regression: the focused contract failed until generated medal localization stripped trailing spaces from vanilla multiline rows.
- Intermediate dry build caught the root cause of unsafe collection rows: 5 `loc.invalid_line` errors from `COMMON_COMPONENT_COLLECTIONS_COLLECTIONS/main.loc` values beginning with `[ROOT.GetCountryContinent]`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated coverage: 18 source modules have `main.loc` files on disk; 16 common-component modules produce localization artifacts in the dry-build manifest.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-collection-medal-loc-final-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,370 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 160 `common_component` localization artifacts.

## Follow-Up

- Intelligence-agency upgrades and occupation laws have direct display-key conventions and can be localized in a later path-gated common-component slice.
- Common support domains remain compiled support preservation. Split them into editable records only when GUI authoring needs domain-specific workflows.
