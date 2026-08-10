# PIHC3 Faction Template Slice

Timestamp: 2026-06-08 14:46 CST

## Scope

- Added the project-local `faction` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:faction/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` and `description` as primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/faction/{object_id}/`.
- The default body follows the local HOI4 faction-template shape with a loc-backed name, manifest, icon, leader-join setting, visible and available triggers, one starter goal, and two default rules.
- Refreshed the starter shape against current local HOI4 faction files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/factions/`, including `_documentation.md`, `templates/generic_factions.txt`, and `templates/allies.txt`.
- Added SDK example coverage proving `Project.create_module("faction", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/30-factions.md`.

## Verification

- Red checks: the new faction test first failed with `KeyError: 'faction'`, and the primary-field metadata test failed with `KeyError: 'pihc3:faction/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 40 tests.
- SDK template projection: `faction ['title', 'description']`, with `manifest`, `visible`, and `goal` defaulting to advanced values `faction_manifest_strength_in_unity`, `no`, and `faction_goal_a_military_base`.
- Desktop-state template projection: `PIHC3 faction ['title', 'description']`, with `manifest` and `visible` defaulting to advanced values `faction_manifest_strength_in_unity` and `no`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/30-factions.md` confirmed both PIHC3 files remain under the ignored project-local tree.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 factions or attempt faction goals, manifests, rule groups, rules, upgrades, member upgrades, icon pools, AI initiative strategy, country creation effects, or legacy parity review.
- The default `visible = { always = no }` keeps the generated template from becoming selectable before an author wires the faction into a deliberate creation flow.
- Next slices can continue expanding GUI-visible PIHC3 families that still lack starters, such as scripted GUI, raid, or military industrial organization shells, or begin mapping PIHC2 faction source shapes for import.
