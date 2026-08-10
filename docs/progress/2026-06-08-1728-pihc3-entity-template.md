# 2026-06-08 17:28 PIHC3 Entity Template

## Scope

- Added a project-local PIHC3 `entity` routed family and `pihc3:entity/basic` template.
- The SDK now supports `Project.create_module("entity", "ENTITY_TEST_FRIENDSHIP", values={"title": "Friendship Model"})`.
- The starter writes `mesh.gfx` and `entity.asset` sources and builds per-module `gfx/models/<object_id>.gfx` plus `gfx/models/<object_id>.asset` artifacts.
- Documented the PIHC2/HOI4DEV model-entity evidence and the user-facing create flow.

## Legacy Evidence

- PIHC2 builds model entities in `scripts/C16_add_entities.py`.
- HOI4DEV `AddModels(...)` scans asset-heavy folders under `resources/entities/` and emits `00_hoi4dev_meshes.gfx`, `z_hoi4dev_entities.asset`, and `zz_hoi4dev_units_entities.asset`.
- Checked representative PIHC2 folders under `resources/entities/viento/air/airship`, `resources/entities/viento/pony/imperial`, and `resources/entities/viento/weapon/rifle`.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_sdk_examples.py -q -k 'entity_template or template_args_mark'` failed on missing `entity` family/template.
- Green focused: `rtk bash scripts/test.bash tests/test_sdk_examples.py -q -k 'entity_template or template_args_mark'` passed with 2 tests.
- SDK examples: `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 55 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py` passed.
- Targeted flake: `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py` passed.
- PIHC3 build: `rtk uv run python -c "from paradev.project import Project; print(Project.load('projects/PIHC3').build().summary())"` reported `blocked: False` and `diagnostic_count: 0`.
- PIHC3 diagnostics: `rtk uv run paradev diagnostics projects/PIHC3 --json` returned no diagnostics.
- Whitespace checks: `rtk git diff --check` passed in the parent repo and `projects/PIHC3`.

## Unfinished Jobs

- Import PIHC2 entity folders into PIHC3 source modules.
- Copy binary mesh, texture, and animation files into generated output.
- Preserve PIHC2 variant folders and `info.json` entity/state fields.
- Rebuild aggregate `00_hoi4dev_meshes.gfx`, `z_hoi4dev_entities.asset`, and `zz_hoi4dev_units_entities.asset` parity.
- Import `resources/entities.json` tag/type mapping and unit clone assignment rules.
- Decide whether autodiffuse remains a project script or becomes a reusable asset-pipeline helper.
