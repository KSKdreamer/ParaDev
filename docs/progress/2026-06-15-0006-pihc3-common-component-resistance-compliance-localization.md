# 2026-06-15 00:06 PIHC3 common component resistance and compliance localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for compiled resistance and compliance threshold modifier support files. This keeps the files in the shared path-preserving common-component family instead of adding type-specific authoring code.

## Changes

- Added path-gated localization extraction for `common/resistance_compliance_modifiers/*.txt`.
- Extraction now owns top-level `compliance_*` and `resistance_*` PDX records only.
- Regenerated 48 common component modules.
- Generated `main.loc` for `COMMON_COMPONENT_RESISTANCE_COMPLIANCE_MODIFIERS_COMPLIANCE_MODIFIERS` and `COMMON_COMPONENT_RESISTANCE_COMPLIANCE_MODIFIERS_RESISTANCE_MODIFIERS`.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/resistance_compliance_modifiers/compliance_modifiers.txt`.
- Green contract after the path-gated extractor change: `1 passed, 162 deselected in 249.09s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: compliance modifiers now have `loc_key_count: 50`, and resistance modifiers now have `loc_key_count: 40`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-resistance-compliance-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,444 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 234 `common_component` localization artifacts from 25 localized common-component modules.

## Follow-Up

- Candidate remaining common-component localization slices include technology tags and technology sharing.
- Keep future extractors path-gated to clear current-game PDX conventions before considering new editable module families.
