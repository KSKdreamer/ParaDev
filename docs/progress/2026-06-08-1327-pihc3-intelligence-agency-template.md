# PIHC3 Intelligence Agency Template Progress

Date: 2026-06-08 13:27 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `intelligence_agency` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:intelligence_agency/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/intelligence_agency/{object_id}/`.
- The default body follows the local HOI4 intelligence-agency shape with one `intelligence_agency = { ... }` record, a picture, localized name key, default trigger, and available trigger.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/intelligence_agencies/`, including `00_intelligence_agencies.txt`, and checked `localisation/english/intelligence_agencies_l_english.yml` for localized agency names.
- Added SDK example coverage proving `Project.create_module("intelligence_agency", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/21-intelligence-agencies.md`.

## Verification

- Red checks: the new intelligence agency test first failed with `KeyError: 'intelligence_agency'` and the primary-field metadata test failed with `KeyError: 'pihc3:intelligence_agency/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 31 passed.
- SDK template projection: `intelligence_agency ['title', 'description']`, with `picture` defaulting to advanced string `GFX_intelligence_agency_logo_generic_1`.
- Desktop-state template projection: `PIHC3 intelligence_agency ['title', 'description']`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/21-intelligence-agencies.md`: both paths remain ignored by `.gitignore:85`.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 intelligence agency importer.
- Agency upgrades, country-focus creation effects, logo asset generation, multiple alternate names, country-specific availability presets, and legacy parity review remain future slices.
- The starter template only creates one editable agency definition; authors still need later templates or importers for a complete national intelligence agency workflow.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as game-rule, autonomous-state, or strategic-region shells, or begin mapping PIHC2 intelligence agency source shapes for import.
