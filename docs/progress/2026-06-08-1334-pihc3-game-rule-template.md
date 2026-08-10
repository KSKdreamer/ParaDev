# PIHC3 Game Rule Template Progress

Date: 2026-06-08 13:34 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `game_rule` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:game_rule/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/game_rule/{object_id}/`.
- The default body follows the local HOI4 game-rule shape with a rule name/description, group, icon, one default option, and one alternate option.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/game_rules/`, including `00_game_rules.txt`, and checked `localisation/english/game_rules_l_english.yml` plus `interface/game_rules.gfx`.
- Added SDK example coverage proving `Project.create_module("game_rule", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/22-game-rules.md`.

## Verification

- Red checks: the new game rule test first failed with `KeyError: 'game_rule'` and the primary-field metadata test failed with `KeyError: 'pihc3:game_rule/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 32 passed.
- SDK template projection: `game_rule ['title', 'description']`, with `group` defaulting to advanced string `RULE_GROUP_GENERAL_UI`.
- Desktop-state template projection: `PIHC3 game_rule ['title', 'description']`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/22-game-rules.md`: both paths remain ignored by `.gitignore:85`.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 game rule importer.
- AI behavior presets, country-specific rule packs, scripted effects that consume rule choices, icon asset generation, and legacy parity review remain future slices.
- The starter template only creates one editable game rule definition; authors still need later templates or importers for a full rule-driven gameplay workflow.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as autonomous-state, strategic-region, or doctrine shells, or begin mapping PIHC2 game rule source shapes for import.
