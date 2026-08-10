# PIHC3 Wargoal Template Slice

Timestamp: 2026-06-08 14:26 CST

## Scope

- Added the project-local `wargoal` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:wargoal/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` and `description` as primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/wargoal/{object_id}/`.
- The default body follows the local HOI4 wargoal shape with a `wargoal_types = { ... }` wrapper, one wargoal id, localized war-name key, locked-off `allowed` trigger, empty `available` and `take_states` blocks, generation costs, state limits/costs, expiry, and threat.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/wargoals/00_invasion.txt`, and checked `localisation/english/war_l_english.yml` plus `localisation/english/diplomacy_l_english.yml`.
- Added SDK example coverage proving `Project.create_module("wargoal", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/28-wargoals.md`.

## Verification

- Red checks: the new wargoal test first failed with `KeyError: 'wargoal'` and the primary-field metadata test failed with `KeyError: 'pihc3:wargoal/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 38 tests.
- SDK template projection: `wargoal ['title', 'description']`, with `war_name` defaulting to advanced string `{object_id}_WAR_NAME`, `expire` defaulting to advanced string `730`, and `threat` defaulting to advanced string `2`.
- Desktop-state template projection: `PIHC3 wargoal ['title', 'description']`, with `war_name` defaulting to advanced string `{object_id}_WAR_NAME`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/28-wargoals.md` confirmed both PIHC3 files remain under the ignored project-local tree.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 wargoals or attempt focus/event unlock logic, peace-conference behavior, claim/core state presets, puppet/liberation variants, AI balancing, or legacy parity review.
- The default `allowed = { always = no }` follows vanilla focus-only and special-purpose wargoal patterns so the shell is not accidentally player-usable before an author wires unlock logic.
- Next slices can continue expanding GUI-visible PIHC3 families that still lack starters, such as doctrine, faction, scripted GUI, or raid shells, or begin mapping PIHC2 wargoal source shapes for import.
