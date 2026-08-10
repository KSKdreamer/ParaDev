# PIHC3 Equipment Template Progress

Date: 2026-06-08 12:34 CST

Linear: TAL-298, TAL-297

## Done

- Added the project-local `equipment` simple-source family to `projects/PIHC3/paradev.yaml`.
- Added the `pihc3:equipment/basic` authoring template for one-call SDK or compact GUI creation.
- Kept the compact create form minimal: `title` and `description` are the only primary fields.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/equipment/{object_id}/`.
- The default equipment body is a small `equipments = { ... }` block with `year = 1936`, `archetype = infantry_equipment`, `is_archetype = no`, `picture = {object_id}`, and `active = yes`.
- Refreshed the starter shape against the local HOI4 install at `/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common/units/equipment/infantry.txt` and existing PIHC3 equipment source examples under `projects/PIHC3/src/general/equipments/`.
- Added SDK example coverage proving `Project.create_module("equipment", ...)` resolves the PIHC3 template, writes source files, and builds cleanly.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/13-equipment.md`.

## Verification

- Red checks: the new equipment test first failed with `KeyError: 'equipment'` and the primary-field metadata test failed with `KeyError: 'pihc3:equipment/basic'`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_equipment_template_scaffolds_basic_equipment tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q`: 2 passed.
- SDK template projection: `equipment ['title', 'description']`, with `active` and `is_archetype` defaulting to string `yes` and `no`.
- Desktop-state template projection: `PIHC3 equipment ['title', 'description']`.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: 23 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- This is a starter authoring template, not a PIHC2 equipment importer.
- Archetype-specific presets, equipment modules, upgrades, icon wiring, designer UI metadata, and balancing helpers remain future slices.
- The starter template only creates a minimal `equipments = { ... }` definition; authors still refine gameplay stats in `def.pdx` after scaffolding.
- `projects/PIHC3/` is ignored by the current `.gitignore`, so the PIHC3 manifest and migration-note changes are local project-state changes rather than normal tracked diff entries.

## Next

- Continue expanding GUI-visible PIHC3 families that still lack starters, especially `state`, `country`, and `division`, or begin mapping PIHC2 equipment source shapes for import.
