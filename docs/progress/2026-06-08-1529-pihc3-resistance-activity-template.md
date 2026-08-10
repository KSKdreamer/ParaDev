# PIHC3 Resistance Activity Template Slice

Timestamp: 2026-06-08 15:29 CST

## Scope

- Added the project-local `resistance_activity` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:resistance_activity/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` as the primary field.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/resistance_activity/{object_id}/`.
- The default body follows the local HOI4 resistance activity shape with availability, weight, max amount, duration, empty effect and state-modifier edit points, and a localized alert text.
- Refreshed the starter shape against current local HOI4 and PIHC legacy resistance activity files, including vanilla `common/resistance_activity/resistance_activity.txt`, PIHC2 `resources/copies/data/common/resistance_activity/resistance_activity.json`, and compiled PIHC_dev `common/resistance_activity/resistance_activity.txt`.
- Added SDK example coverage proving `Project.create_module("resistance_activity", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/34-resistance-activities.md`.

## Verification

- Red checks: the new resistance activity test first failed with `KeyError: 'resistance_activity'`, and the primary-field metadata test failed with `KeyError: 'pihc3:resistance_activity/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 44 tests.
- SDK template projection: `resistance_activity ['title']`, with `available` and `duration` defaulting to advanced values `always = no` and `10`.
- Desktop-state template projection: `The Pony In The High Castle resistance_activity ['title']`, with `available` and `max_amount` defaulting to advanced values `always = no` and `1`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `git -C projects/PIHC3 diff --check` passed.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 resistance activities or attempt targeted sabotage variables, building-specific damage effects, occupation-law balancing, alert text parity, or legacy parity review.
- The default `available = { always = no }` keeps generated activities inert until an author wires the triggers and effects deliberately.
- The copied legacy `common/resistance_activity/resistance_activity.txt` remains under the compatibility overlay until a later importer and parity review can replace the full activity pack.
