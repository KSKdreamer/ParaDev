# PIHC3 Doctrine Template Slice

Timestamp: 2026-06-08 14:37 CST

## Scope

- Added the project-local `doctrine` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:doctrine/grand-basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` and `description` as primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/doctrine/{object_id}/`.
- The default body follows the local post-1.17 HOI4 grand-doctrine shape with a folder, loc-backed name/description, icon, available trigger, XP cost/type, AI base weight, track reference, one starter activation modifier, and an empty milestones block.
- Refreshed the starter shape against current local HOI4 doctrine files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/doctrines/`, including folder, grand-doctrine, track, and land subdoctrine examples.
- Added SDK example coverage proving `Project.create_module("doctrine", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/29-doctrines.md`.

## Verification

- Red checks: the new doctrine test first failed with `KeyError: 'doctrine'`, and the primary-field metadata test failed with `KeyError: 'pihc3:doctrine/grand-basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 39 tests.
- SDK template projection: `doctrine ['title', 'description']`, with `folder`, `xp_type`, and `track` defaulting to advanced values `land`, `army`, and `infantry`.
- Desktop-state template projection: `PIHC3 doctrine ['title', 'description']`, with `folder` and `track` defaulting to advanced values `land` and `infantry`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/29-doctrines.md` confirmed both PIHC3 files remain under the ignored project-local tree.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 doctrines or attempt folder authoring, track definitions, subdoctrine templates, milestone reward generation, doctrine UI balancing, AI strategy, technology integration, or legacy parity review.
- The default `folder = land`, `track = infantry`, and `planning_speed = 0.05` keep the generated file recognizable while leaving doctrine balance and full tree design to future slices.
- Next slices can continue expanding GUI-visible PIHC3 families that still lack starters, such as faction, scripted GUI, raid, or military industrial organization shells, or begin mapping PIHC2 doctrine source shapes for import.
