# PIHC3 Operation Phase Template Slice

Timestamp: 2026-06-08 16:02 CST

## Scope

- Added the project-local `operation_phase` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:operation_phase/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` and `description` as primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/operation_phase/{object_id}/`.
- The default body follows the local HOI4 and PIHC operation-phase shape with one phase id, localized name/description/outcome keys, picture, icon, and an empty equipment edit point.
- Refreshed the starter shape against vanilla `common/operation_phases/00_operation_phases.txt`, vanilla `common/operation_phases/lar_infiltration.txt`, vanilla `common/operation_phases/_documentation.md`, vanilla `localisation/english/lar_operations_l_english.yml`, PIHC2 `resources/copies/data/common/operation_phases/00_operation_phases.json`, and compiled PIHC_dev operation phase files.
- Added SDK example coverage proving `Project.create_module("operation_phase", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/38-operation-phases.md`.

## Verification

- Red checks: the new operation phase test first failed with `KeyError: 'operation_phase'`, and the primary-field metadata test failed with `KeyError: 'pihc3:operation_phase/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 48 tests.
- SDK template projection: `operation_phase ['title', 'description']`, with `icon` and `picture` defaulting to advanced values `GFX_phase_infiltration_diplomatic_small` and `GFX_phase_infiltration_diplomatic`.
- Desktop-state template projection: `The Pony In The High Castle operation_phase ['title', 'description']`, with `icon` and `outcome` defaulting to advanced values `GFX_phase_infiltration_diplomatic_small` and `The phase completes cleanly.`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `git -C projects/PIHC3 diff --check` passed.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 operation phases or attempt operation definitions, phase-selection weights, phase requirements, return-on-complete behavior, equipment presets, map icons, outcome-extra text, image asset generation, multi-language parity, or legacy parity review.
- The copied legacy operation phase baselines remain under the compatibility overlay until a later importer and parity review can replace the full phase set.
