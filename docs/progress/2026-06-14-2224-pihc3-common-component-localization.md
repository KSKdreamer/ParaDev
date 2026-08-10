# 2026-06-14 22:24 PIHC3 common component localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by extending `common_component` from PDX-only preservation to shared PDX plus localization slots. The slice keeps module-specific code minimal by using the generic optional `main.loc` slot and importer-side key extraction only for reviewed common support files whose localization keys are directly derivable from compiled PDX.

## Changes

- Added a shared optional loc slot to `common_component`.
- Added `compiled_common_component_locs`.
- Loaded current-game localization first and overlaid PIHC_dev localization rows.
- Derived leader ability localization from `name`, `desc`, `tooltip`, and explicit localization fields in `common/abilities/generic_leader_abilities.txt`.
- Derived state-category localization from `state_categories = { <id> = ... }` records as `STATE_CATEGORY_<id>`.
- Kept other common support domains PDX-only for now to avoid duplicate localization ownership churn.
- Regenerated 48 common component modules.
- Wrote `main.loc` for 13 common modules: the leader abilities file and all 12 state-category files.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_family or common_component_importer"` failed with missing `loc` family slot and missing `compiled_common_component_locs`.
- Green contract: `2 passed, 147 deselected in 49.89s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated coverage: 13 modules with `main.loc`; 220 localized leader-ability rows and 10 localized rows for each state-category module.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-localization-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,340 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 130 `common_component` localization artifacts.

## Follow-Up

- Common support domains remain compiled support preservation. Split them into editable records only when GUI authoring needs domain-specific workflows.
- Technology-sharing localization remains intentionally untouched in this slice because the `continuous_tech_share` key is already owned by native continuous-focus/localization-component output.
