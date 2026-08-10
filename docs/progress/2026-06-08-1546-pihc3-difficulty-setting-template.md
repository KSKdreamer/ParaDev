# PIHC3 Difficulty Setting Template Slice

Timestamp: 2026-06-08 15:46 CST

## Scope

- Added the project-local `difficulty_setting` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:difficulty_setting/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` as the primary field.
- The template writes `meta.yaml` and `def.pdx` under `src/modules/difficulty_setting/{object_id}/`.
- The default body follows the local HOI4 and PIHC difficulty setting shape with a `difficulty_settings` wrapper, one `difficulty_setting` entry, key, AI modifier, target country list, and multiplier.
- Refreshed the starter shape against vanilla `common/difficulty_settings/00_difficulty.txt`, PIHC2 `resources/copies/data/common/difficulty_settings/00_difficulty.json`, and compiled PIHC_dev `common/difficulty_settings/00_difficulty.txt`.
- Added SDK example coverage proving `Project.create_module("difficulty_setting", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/36-difficulty-settings.md`.

## Verification

- Red checks: the new difficulty setting test first failed with `KeyError: 'difficulty_setting'`, and the primary-field metadata test failed with `KeyError: 'pihc3:difficulty_setting/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 46 tests.
- SDK template projection: `difficulty_setting ['title']`, with `countries` and `multiplier` defaulting to advanced values `C01` and `2.0`.
- Desktop-state template projection: `The Pony In The High Castle difficulty_setting ['title']`, with `countries` and `modifier` defaulting to advanced values `C01` and `diff_strong_ai_generic`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `git -C projects/PIHC3 diff --check` passed.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 difficulty settings or attempt per-country roster generation, custom difficulty modifier definitions, UI/localization review, balancing, or legacy parity review.
- The copied legacy `common/difficulty_settings/00_difficulty.txt` baseline remains under the compatibility overlay until a later importer and parity review can replace the full difficulty pack.
