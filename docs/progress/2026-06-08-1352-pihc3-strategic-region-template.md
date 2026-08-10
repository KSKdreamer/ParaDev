# PIHC3 Strategic Region Template Progress

Date: 2026-06-08 13:52 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `strategic_region` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:strategic_region/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/strategic_region/{object_id}/`.
- The default body follows the local HOI4 strategic-region shape with one `strategic_region={ ... }` record, numeric region id, localized name key, province list, and one all-year weather period.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/map/strategicregions/`, including `1-Southern England.txt`, `100-Red Sea.txt`, and `120-Central USA.txt`, and checked `localisation/english/strategic_region_names_l_english.yml`.
- Added SDK example coverage proving `Project.create_module("strategic_region", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/24-strategic-regions.md`.

## Verification

- Red checks: the new strategic region test first failed with `KeyError: 'strategic_region'` and the primary-field metadata test failed with `KeyError: 'pihc3:strategic_region/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 34 passed.
- SDK template projection: `strategic_region ['title', 'description']`, with `region_id` defaulting to advanced string `999` and `province_ids` defaulting to advanced string `1`.
- Desktop-state template projection: `PIHC3 strategic_region ['title', 'description']`, with `region_id` defaulting to advanced string `999`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/24-strategic-regions.md`: both paths remain ignored by `.gitignore:85`.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 strategic-region importer.
- Province-map validation, naval terrain, static modifiers, twelve-month weather profiles, air/naval region balancing, and legacy parity review remain future slices.
- The starter template only creates one editable strategic region; authors still need later templates or importers for complete map-region workflows.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as doctrine, bookmark, faction, or on-action shells, or begin mapping PIHC2 strategic-region source shapes for import.
