# PIHC3 Autonomous State Template Progress

Date: 2026-06-08 13:44 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `autonomous_state` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:autonomous_state/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/autonomous_state/{object_id}/`.
- The default body follows the local HOI4 autonomous-state shape with one `autonomy_state = { ... }` record, freedom/manpower influence fields, rule/modifier blocks, AI desire blocks, `allowed`, and empty take/lose trigger shells.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/autonomous_states/`, including `puppet.txt`, `dominion.txt`, `colony.txt`, and `integrated_puppet.txt`, and checked `localisation/english/autonomy_l_english.yml`.
- Added SDK example coverage proving `Project.create_module("autonomous_state", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/23-autonomous-states.md`.

## Verification

- Red checks: the new autonomous state test first failed with `KeyError: 'autonomous_state'` and the primary-field metadata test failed with `KeyError: 'pihc3:autonomous_state/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 33 passed.
- SDK template projection: `autonomous_state ['title', 'description']`, with `allowed` and `ai_subject_wants_higher_factor` defaulting to advanced fields.
- Desktop-state template projection: `PIHC3 autonomous_state ['title', 'description']`, with `min_freedom_level` defaulting to advanced string `0.4`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/23-autonomous-states.md`: both paths remain ignored by `.gitignore:85`.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 autonomous state importer.
- Autonomy-level chains, focus/event unlock logic, peace-conference weighting, country-specific restrictions, balancing helpers, and legacy parity review remain future slices.
- The starter template only creates one editable autonomy level; authors still need later templates or importers for a complete subject-system workflow.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as strategic-region, doctrine, bookmark, or faction shells, or begin mapping PIHC2 autonomous-state source shapes for import.
