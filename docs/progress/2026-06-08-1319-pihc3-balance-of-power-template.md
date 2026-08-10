# PIHC3 Balance Of Power Template Progress

Date: 2026-06-08 13:19 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `balance_of_power` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:balance_of_power/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/balance_of_power/{object_id}/`.
- The default body follows the local HOI4 balance-of-power shape with an initial value, a neutral range, one left side, and one right side.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/bop/`, including `ITA.txt` and `_test.txt`.
- Added SDK example coverage proving `Project.create_module("balance_of_power", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/20-balance-of-power.md`.

## Verification

- Red checks: the new balance-of-power test first failed with `KeyError: 'balance_of_power'` and the primary-field metadata test failed with `KeyError: 'pihc3:balance_of_power/basic'`.
- Intermediate manifest validation caught that `required_loc_keys` cannot reference template args such as `{left_range_id}`; the final family requires only `{object_id}` and `{object_id}_desc`, while the template still emits side and range localization rows.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 30 passed.
- SDK template projection: `balance_of_power ['title', 'description']`, with `left_side_id` defaulting to advanced string `{object_id}_left_side`.
- Desktop-state template projection: `PIHC3 balance_of_power ['title', 'description']`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/20-balance-of-power.md`: both paths remain ignored by `.gitignore:85`.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 balance-of-power importer.
- Decision-category wiring, side-specific decisions/events, dynamic side graphics, extra ranges, scripted state changes, balancing helpers, and legacy parity review remain future slices.
- The starter template only creates one editable BOP definition; authors still need later templates or importers for a complete national BOP workflow.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as intelligence-agency, game-rule, or autonomous-state shells, or begin mapping PIHC2 balance-of-power source shapes for import.
