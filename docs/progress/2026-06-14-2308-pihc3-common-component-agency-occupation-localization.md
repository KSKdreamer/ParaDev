# 2026-06-14 23:08 PIHC3 common component agency and occupation localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for two current-format support files that already have stable display-key conventions. This keeps the family generic: intelligence-agency upgrades and occupation laws still use the shared path-preserving PDX slot plus optional `main.loc`, with only importer-side key extraction rules.

## Changes

- Added path-gated localization extraction for `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`.
- Agency extraction now owns branch IDs, upgrade IDs, matching upgrade `_desc` rows, and explicit loc-bearing scalar references such as `unlock_decision_category_tooltip`.
- Added path-gated localization extraction for `common/occupation_laws/occupation_laws.txt`.
- Occupation-law extraction now owns top-level law IDs and explicit loc-bearing scalar references such as `custom_modifier_tooltip`.
- Reused the existing section-style `.loc` safety filter for localized values that begin with `[`.
- Regenerated 48 common component modules.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt`.
- Green contract after the path-gated extractor changes: `1 passed, 152 deselected in 133.24s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: agency upgrades now have `loc_key_count: 480`, and occupation laws now have `loc_key_count: 170`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-agency-occupation-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,390 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 180 `common_component` localization artifacts from 18 localized common-component modules.

## Follow-Up

- Common support domains remain compiled support preservation. Split them into editable records only when GUI authoring needs domain-specific workflows.
- Continue harvesting path-gated generic localization rules from support files with clear PDX display-key conventions before adding module-specific families.
