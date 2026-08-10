# 2026-06-14 21:53 PIHC3 MIO component localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by extending `military_industrial_organization_component` from PDX-only preservation to shared PDX plus localization slots. The slice keeps module-specific code minimal by using the generic optional `main.loc` slot and importer-side key extraction for compiled MIO organization and policy files.

## Changes

- Added a shared optional loc slot to `military_industrial_organization_component`.
- Added `compiled_military_industrial_organization_component_locs`.
- Loaded current-game localization first and overlaid PIHC_dev localization rows.
- Extracted MIO display keys from top-level records plus `name`, `text`, `token`, and `localization_key` fields.
- Assigned reused loc keys to one module only, preferring custom organization files before policies, generic organizations, and debug support, to avoid duplicate localization diagnostics.
- Regenerated 7 MIO component modules.
- Wrote `main.loc` for 6 modules; the AI bonus-weight module remains PDX-only.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "military_industrial_organization_component_family or military_industrial_organization_component_importer"` failed with missing `loc` family slot and missing `compiled_military_industrial_organization_component_locs`.
- First dry build after adding loc rows found 170 `loc.project_duplicate_key` errors from reused MIO keys across modules.
- Green contract after key assignment fix: `2 passed, 147 deselected in 48.44s`.
- Final combined MIO and peace-conference contract: `4 passed, 145 deselected in 85.41s (0:01:25)`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_military_industrial_organization_components.py` passed.
- Formatting: `rtk uv run black --check --line-ranges 2041-2138 tests/test_pihc3_migration_contracts.py` passed.
- Final Heaven-style scan: `OK: 3 file(s) - no banned imports`.
- Regeneration: `Imported 7 PIHC2 MIO component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/military_industrial_organization_component`.
- Generated coverage: 6 modules with `main.loc`; the module now named `MIO_ORGANIZATIONS_C01` owns 170 localized rows; `MIO_00_GENERIC_ORGANIZATION` owns 4,550 localized rows after duplicate-key assignment. Each concise folder keeps the established compiled localization filename through its explicit `game_id`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-mio-localization-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,170 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build ownership: 7 `military_industrial_organization_component` PDX artifacts, 60 `military_industrial_organization_component` localization artifacts, and 0 copy-owned files under `common/military_industrial_organization/`.

## Follow-Up

- MIO trait trees and policy authoring remain compiled support preservation. Split them into editable records only when GUI authoring needs MIO-specific workflows.
