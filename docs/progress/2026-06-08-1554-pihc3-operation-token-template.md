# PIHC3 Operation Token Template Slice

Timestamp: 2026-06-08 15:54 CST

## Scope

- Added the project-local `operation_token` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:operation_token/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` and `description` as primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/operation_token/{object_id}/`.
- The default body follows the local HOI4 and PIHC operation-token shape with one token id, localized name/description keys, icon, text icon, intel source, and intel gain.
- Refreshed the starter shape against vanilla `common/operation_tokens/00_OperationTokens.txt`, vanilla `common/operation_tokens/_documentation.md`, vanilla `localisation/english/operatives_l_english.yml`, PIHC2 `resources/copies/data/common/operation_tokens/00_OperationTokens.json`, and compiled PIHC_dev `common/operation_tokens/00_OperationTokens.txt`.
- Added SDK example coverage proving `Project.create_module("operation_token", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/37-operation-tokens.md`.

## Verification

- Red checks: the new operation token test first failed with `KeyError: 'operation_token'`, and the primary-field metadata test failed with `KeyError: 'pihc3:operation_token/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 47 tests.
- SDK template projection: `operation_token ['title', 'description']`, with `intel_source` and `icon` defaulting to advanced values `civilian` and `GFX_infiltrate_civilian_bg`.
- Desktop-state template projection: `The Pony In The High Castle operation_token ['title', 'description']`, with `intel_source` and `intel_gain` defaulting to advanced values `civilian` and `10`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `git -C projects/PIHC3 diff --check` passed.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 operation tokens or attempt operation definitions, operation phases, token-awarding effects, targeted modifiers, icon asset generation, multi-language parity, or legacy parity review.
- The copied legacy `common/operation_tokens/00_OperationTokens.txt` baseline remains under the compatibility overlay until a later importer and parity review can replace the full operation-token pack.
- The goal completion threshold is not met yet. Many starter-template slices are present and stably build, but the progress notes still list broad PIHC2 parity/import work as future scope, so this thread should remain active.
