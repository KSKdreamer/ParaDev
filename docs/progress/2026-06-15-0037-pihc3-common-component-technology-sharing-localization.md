# 2026-06-15 00:37 PIHC3 common component technology-sharing localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for compiled technology-sharing support. This keeps the sharing-group PDX file in the shared path-preserving common-component family and avoids adding a dedicated module type.

## Changes

- Added path-gated localization extraction for `common/technology_sharing/PIHC_tech_sharing_groups.txt`.
- Reused the generic scalar loc-key extractor for sharing-group `name` and `desc` fields.
- Excluded the shared `continuous_tech_share` and `continuous_tech_share_desc` rows because `continuous_focus/generic_focus` already owns those focus localization keys.
- Regenerated 48 common component modules.
- Generated `main.loc` for `COMMON_COMPONENT_TECHNOLOGY_SHARING_PIHC_TECH_SHARING_GROUPS` with PIHC-specific English and Simplified Chinese sharing-group rows.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/technology_sharing/PIHC_tech_sharing_groups.txt`.
- Green contract after adding scalar extraction: `1 passed, 165 deselected in 262.25s`.
- Debugging dry build caught duplicate ownership: the initial technology-sharing localization emitted 20 `loc.project_duplicate_key` errors for `continuous_tech_share` and `continuous_tech_share_desc`, all duplicated with `continuous_focus/generic_focus`.
- Red duplicate-prevention contract: the focused test then failed because `continuous_tech_share` remained in technology-sharing loc rows.
- Green contract after excluding the focus-owned key pair: `1 passed, 165 deselected in 262.96s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: technology-sharing now has `loc_key_count: 12`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-technology-sharing-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,446 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 236 `common_component` localization artifacts from 26 localized common-component modules.

## Follow-Up

- Candidate remaining common-component localization slice: technology tags.
- Keep future common-component loc extraction scoped to source-owned display keys so shared keys remain with their existing native owners.
