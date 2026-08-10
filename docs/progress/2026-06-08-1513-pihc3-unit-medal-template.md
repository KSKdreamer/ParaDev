# PIHC3 Unit Medal Template Slice

Timestamp: 2026-06-08 15:13 CST

## Scope

- Added the project-local `unit_medal` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:unit_medal/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` as the primary field.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/unit_medal/{object_id}/`.
- The default body follows the local HOI4 `unit_medals = { ... }` shape with a shared cost variable, government availability trigger, frame, icon, one unit modifier, and one divisional commander XP effect.
- Refreshed the starter shape against the current local HOI4 and PIHC legacy medal files, including vanilla `common/unit_medals/00_default.txt`, vanilla `localisation/english/unit_medals_l_english.yml`, PIHC2 `resources/copies/data/common/unit_medals/00_default.json`, and compiled PIHC_dev `common/unit_medals/00_default.txt`.
- Added SDK example coverage proving `Project.create_module("unit_medal", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/32-unit-medals.md`.

## Verification

- Red checks: the new unit medal test first failed with `KeyError: 'unit_medal'`, and the primary-field metadata test failed with `KeyError: 'pihc3:unit_medal/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 42 tests.
- SDK template projection: `unit_medal ['title']`, with `icon`, `modifier`, and `one_time_xp` defaulting to advanced values `GFX_medal_icon_democratic`, `army_morale_factor`, and `100`.
- Desktop-state template projection: `The Pony In The High Castle unit_medal ['title']`, with `icon` and `cost` defaulting to advanced values `GFX_medal_icon_democratic` and `30`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `git -C projects/PIHC3 diff --check` passed.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 unit medals or attempt country-specific medal packs, icon atlas work, modifier balancing, award unlock effects, custom scripted triggers, or legacy parity review.
- The copied legacy `common/unit_medals/00_default.txt` remains under the compatibility overlay until a later importer and parity review can replace the full medal pack.
- Next slices can continue expanding copy-root areas that still lack native starters, such as raids, military industrial organizations, operative codenames, or other common-script shells.
