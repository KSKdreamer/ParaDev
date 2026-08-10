# PIHC3 Continuous Focus Template Slice

Timestamp: 2026-06-08 15:37 CST

## Scope

- Added the project-local `continuous_focus` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:continuous_focus/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` and `description` as primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/continuous_focus/{object_id}/`.
- The default body follows the local PIHC continuous focus shape with one `continuous_focus_palette`, country factor, default/reset flags, position, one focus block, availability/enable triggers, empty modifier/select/cancel edit points, AI weight, strategy support, daily cost, and capitulation availability.
- Refreshed the starter shape against PIHC2 `resources/copies/data/common/continuous_focus/generic.json` and compiled PIHC_dev `common/continuous_focus/generic.txt`.
- Added SDK example coverage proving `Project.create_module("continuous_focus", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/35-continuous-focuses.md`.

## Verification

- Red checks: the new continuous focus test first failed with `KeyError: 'continuous_focus'`, and the primary-field metadata test failed with `KeyError: 'pihc3:continuous_focus/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 45 tests.
- SDK template projection: `continuous_focus ['title', 'description']`, with `available` and `icon` defaulting to advanced values `always = no` and `GFX_goal_generic_propaganda`.
- Desktop-state template projection: `The Pony In The High Castle continuous_focus ['title', 'description']`, with `available` and `daily_cost` defaulting to advanced values `always = no` and `1`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `git -C projects/PIHC3 diff --check` passed.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 continuous focuses or attempt generic palette parity, country-specific unlocks, balancing, effects, AI strategy tuning, focus tree integration, icon art, or legacy localization parity.
- The default `available = { always = no }` keeps generated continuous focuses inert until an author wires unlock logic deliberately.
- The copied legacy `common/continuous_focus/generic.txt` baseline remains under the compatibility overlay until a later importer and parity review can replace the full palette.
