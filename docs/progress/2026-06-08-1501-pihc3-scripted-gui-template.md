# PIHC3 Scripted GUI Template Slice

Timestamp: 2026-06-08 15:01 CST

## Scope

- Added the project-local `scripted_gui` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:scripted_gui/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` as the primary field.
- The template writes `meta.yaml` and `def.pdx` under `src/modules/scripted_gui/{object_id}/`.
- The default body follows the local HOI4 scripted GUI shape with `scripted_gui = { ... }`, `context_type`, `window_name`, `parent_window_token`, a default-off visible trigger, and empty `effects`, `triggers`, and `properties` blocks.
- Refreshed the starter shape against current local HOI4 scripted GUI files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/scripted_guis/`, including `_documentation.md`, `USA_congress_scripted_gui.txt`, and `war_escalation_scripted_gui.txt`.
- Added SDK example coverage proving `Project.create_module("scripted_gui", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/31-scripted-guis.md`.

## Verification

- Red checks: the new scripted GUI test first failed with `KeyError: 'scripted_gui'`, and the primary-field metadata test failed with `KeyError: 'pihc3:scripted_gui/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 41 tests.
- SDK template projection: `scripted_gui ['title']`, with `context_type`, `window_name`, and `visible` defaulting to advanced values `player_context`, `pihc3_placeholder_container`, and `no`.
- Desktop-state template projection: `The Pony In The High Castle scripted_gui ['title']`, with `context_type` and `visible` defaulting to advanced values `player_context` and `no`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `git -C projects/PIHC3 diff --check` passed.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 scripted GUIs or attempt `.gui` interface authoring, decision-category wiring, dynamic lists, button effects, AI behavior, scripted localisation, or legacy parity review.
- The default `visible = { always = no }` keeps the generated scripted GUI inert until an author wires it to a deliberate UI entry point and interaction flow.
- Next slices can continue expanding GUI-visible PIHC3 families that still lack starters, such as raids or military industrial organization shells, or begin mapping PIHC2 scripted GUI source shapes for import.
