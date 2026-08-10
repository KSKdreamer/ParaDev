# PIHC3 Operative Codename Template Slice

Timestamp: 2026-06-08 15:20 CST

## Scope

- Added the project-local `operative_codename` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:operative_codename/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` as the primary field.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/operative_codename/{object_id}/`.
- The default body follows the local HOI4 operative codename theme shape with a localized theme name, target country list, `type = codename`, fallback name pattern, and two starter unique codenames.
- Refreshed the starter shape against current local HOI4 and PIHC legacy codename files, including vanilla `generic_opertive_codenames.txt`, vanilla `GER_operative_codenames.txt`, PIHC2 `resources/copies/data/common/units/codenames_operatives/generic_opertive_codenames.json`, and compiled PIHC_dev `common/units/codenames_operatives/generic_opertive_codenames.txt`.
- Added SDK example coverage proving `Project.create_module("operative_codename", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/33-operative-codenames.md`.

## Verification

- Red checks: the new operative codename test first failed with `KeyError: 'operative_codename'`, and the primary-field metadata test failed with `KeyError: 'pihc3:operative_codename/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 43 tests.
- SDK template projection: `operative_codename ['title']`, with `countries`, `fallback_name`, and `codename_one` defaulting to advanced values `C01`, `Agent %d`, and `Friendship`.
- Desktop-state template projection: `The Pony In The High Castle operative_codename ['title']`, with `countries` and `codename_two` defaulting to advanced values `C01` and `Harmony`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `git -C projects/PIHC3 diff --check` passed.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 operative codenames or attempt multilingual codename lists, country coverage review, non-codename name-theme variants, or legacy parity review.
- The copied legacy `common/units/codenames_operatives/generic_opertive_codenames.txt` remains under the compatibility overlay until a later importer and parity review can replace the full codename pack.
- Next slices can continue expanding copy-root areas that still lack native starters, such as raids, military industrial organizations, scripted diplomatic actions, or peace-conference shells.
