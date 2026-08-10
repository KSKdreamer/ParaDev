# PIHC3 Bookmark Template Slice

Timestamp: 2026-06-08 14:01 CST

## Scope

- Added the project-local `bookmark` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:bookmark/basic` authoring template for one-call SDK or compact GUI creation.
- The compact create form keeps only `title` and `description` as primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/bookmark/{object_id}/`.
- The default body follows the local HOI4 bookmark shape with a `bookmarks = { bookmark = { ... } }` wrapper, localized name/description keys, date, picture, default country, one country setup block, an other-countries description block, and a `randomize_weather` effect.
- Refreshed the starter shape against current local HOI4 files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/bookmarks/`, including `the_gathering_storm.txt` and `blitzkrieg.txt`, and checked `localisation/english/bookmarks_l_english.yml`.
- Added SDK example coverage proving `Project.create_module("bookmark", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/25-bookmarks.md`.

## Verification

- Red checks: the new bookmark test first failed with `KeyError: 'bookmark'` and the primary-field metadata test failed with `KeyError: 'pihc3:bookmark/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 35 tests.
- SDK template projection: `bookmark ['title', 'description']`, with `date` defaulting to advanced string `1936.1.1.12` and `randomize_weather` defaulting to advanced string `12345`.
- Desktop-state template projection: `PIHC3 bookmark ['title', 'description']`, with `date` defaulting to advanced string `1936.1.1.12`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 SDK build summary stayed unblocked: `{'module_count': 529, 'collection_count': 0, 'dependency_count': 0, 'artifact_count': 26892, 'diagnostic_count': 0, 'error_count': 0, 'blocked': False}`.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json` returned no diagnostics.
- `rtk git diff --check` passed.
- `rtk git check-ignore -v projects/PIHC3/paradev.yaml projects/PIHC3/docs/migration/25-bookmarks.md` confirmed both PIHC3 files remain under the ignored project-local tree.

## Notes

- The starter is intentionally conservative. It does not import PIHC2 bookmarks or attempt full country rosters, portrait and leader setup, DLC gating, per-country idea/focus setup, bookmark picture assets, or map validation.
- The default country is `TAG` so the generated shell is visibly incomplete but structurally editable.
- Next slices can continue expanding GUI-visible PIHC3 families that still lack starters, such as doctrine, faction, or on-action shells, or begin mapping PIHC2 bookmark source shapes for import.
