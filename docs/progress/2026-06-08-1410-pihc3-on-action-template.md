# PIHC3 On-Action Template Slice

Timestamp: 2026-06-08 14:10 CST

## Scope

- Added the project-local `on_action` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:on_action/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` as a primary field.
- The template writes `meta.yaml` and `def.pdx` under `src/modules/on_action/{object_id}/`.
- The default body follows the local HOI4 on-action shape with an `on_actions = { ... }` wrapper, an `on_monthly` hook block, and an empty `effect = { }` block.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/on_actions/`, including `_documentation.md`, `00_on_actions.txt`, `00_testing_on_actions.txt`, `03_wtt_on_actions.txt`, and `15_mun_on_actions.txt`.
- Added SDK example coverage proving `Project.create_module("on_action", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/26-on-actions.md`.

## Verification

- Red checks: the new on-action test first failed with `KeyError: 'on_action'` and the primary-field metadata test failed with `KeyError: 'pihc3:on_action/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 36 tests.
- SDK template projection: `on_action ['title']`, with `hook` defaulting to advanced string `on_monthly`.
- Desktop-state template projection: `PIHC3 on_action ['title']`, with `hook` defaulting to advanced string `on_monthly`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/26-on-actions.md` confirmed both PIHC3 files remain under the ignored project-local tree.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 on-actions or attempt event/random-event routing, scope-specific hook presets, scripted-effect generation, DLC gating, or legacy parity review.
- The default hook is `on_monthly` because it is documented in the local HOI4 on-action reference and is less startup-sensitive than `on_startup`.
- Next slices can continue expanding GUI-visible PIHC3 families that still lack starters, such as doctrine, faction, scripted GUI, or resource shells, or begin mapping PIHC2 on-action source shapes for import.
