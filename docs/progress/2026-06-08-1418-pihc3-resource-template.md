# PIHC3 Resource Template Slice

Timestamp: 2026-06-08 14:18 CST

## Scope

- Added the project-local `resource` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:resource/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` and `description` as primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/resource/{object_id}/`.
- The default body follows the local HOI4 resource shape with a `resources = { ... }` wrapper, one resource id, `icon_frame`, `cic`, and `convoys`.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/resources/`, including `_documentation.md` and `00_resources.txt`, and checked `localisation/english/core_l_english.yml` for resource localization conventions.
- Added SDK example coverage proving `Project.create_module("resource", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/27-resources.md`.

## Verification

- Red checks: the new resource test first failed with `KeyError: 'resource'` and the primary-field metadata test failed with `KeyError: 'pihc3:resource/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 37 tests.
- SDK template projection: `resource ['title', 'description']`, with `icon_frame` defaulting to advanced string `7`, `cic` defaulting to advanced string `0.125`, and `convoys` defaulting to advanced string `0.1`.
- Desktop-state template projection: `PIHC3 resource ['title', 'description']`, with `icon_frame` defaulting to advanced string `7`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/27-resources.md` confirmed both PIHC3 files remain under the ignored project-local tree.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 resources or attempt state resource placement, market and AI balancing, resource-strip art, define updates, map validation, or legacy parity review.
- The default `icon_frame` is `7`, matching the last currently local resource frame used by `coal`; authors should adjust art and ordering during balancing work.
- Next slices can continue expanding GUI-visible PIHC3 families that still lack starters, such as doctrine, faction, scripted GUI, or resource placement/state workflows, or begin mapping PIHC2 resource source shapes for import.
