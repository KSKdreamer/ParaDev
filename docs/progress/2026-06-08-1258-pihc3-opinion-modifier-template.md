# PIHC3 Opinion Modifier Template Progress

Date: 2026-06-08 12:58 CST

Linear: TAL-298, TAL-297

## Done

- Added the `pihc3:opinion_modifier/basic` authoring template to `projects/PIHC3/paradev.yaml`.
- Reused the existing generic HoI4 `opinion_modifier` simple-source family instead of adding a duplicate project-local family.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/opinion_modifier/{object_id}/`.
- The default body follows the local HOI4 `opinion_modifiers = { ... }` shape with `value = 25` and `decay = 1`.
- Refreshed the starter shape against current local HOI4 opinion modifier files under `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/opinion_modifiers/`.
- Added SDK example coverage proving `Project.create_module("opinion_modifier", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual, added `projects/PIHC3/docs/migration/17-opinion-modifiers.md`, and corrected `10-modifiers.md` to point opinion modifiers to the new note.

## Verification

- Red checks: the new opinion modifier test first failed with `KeyError: 'pihc3:opinion_modifier/basic'`, and the primary-field metadata test failed with the same missing template id.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_opinion_modifier_template_scaffolds_basic_opinion_modifier tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 27 passed.
- SDK template projection: `opinion_modifier ['title', 'description']`, with `value` defaulting to advanced string `25`.
- Desktop-state template projection: `PIHC3 opinion_modifier ['title', 'description']`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 opinion modifier importer.
- Trade-specific variants, trust bounds, timed decay presets, balancing helpers, and legacy parity review remain future slices.
- The starter template only creates one editable diplomatic opinion modifier; authors still need later templates or importers for richer diplomatic systems.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, such as ideology or special-project shells, or begin mapping PIHC2 opinion modifier source shapes for import.
