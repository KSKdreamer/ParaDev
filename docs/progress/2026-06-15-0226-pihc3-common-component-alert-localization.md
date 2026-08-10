# 2026-06-15 02:26 PIHC3 common component alert localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for compiled alert support. This keeps `common/alerts.txt` in the shared path-preserving common-component family instead of adding an alert-specific module type for the current support list.

## Changes

- Added path-gated localization extraction for root `common/alerts.txt`.
- Extraction now reads declared alert ids under `alerts = { ... }` and owns localization rows whose keys start with the declared alert id plus a suffix.
- PIHC_dev localization still overlays current-game localization, so PIHC manpower alert wording is preserved.
- Undeclared alert rows such as `alert_no_research_instant` remain outside the alert component.
- Regenerated 48 common component modules.
- Generated `main.loc` for `COMMON_COMPONENT_ALERTS`.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/alerts.txt`.
- Green contract after the path-gated extractor change: `1 passed, 165 deselected in 343.71s`.
- Post-format focused contract: `1 passed, 165 deselected in 343.09s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: alerts now have `loc_key_count: 1080`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-alerts-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,470 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 260 `common_component` localization artifacts from 30 localized common-component modules.

## Follow-Up

- Continue common-component localization only where display keys are directly and safely derivable from compiled PDX.
- Keep map-adjacent terrain support out of this family until the skipped-map slice resumes.
