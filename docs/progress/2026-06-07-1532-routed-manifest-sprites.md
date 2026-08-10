# Routed Manifest Sprite Declarations Progress

Date: 2026-06-07 15:32 +0800

Linear: TAL-294

## Done

- Added regression coverage for declarative `routed_source` sprite aggregation in `paradev.yaml`.
- Extended project-local routed family specs so top-level `templates.sprite_gfx`, `templates.sprite_name`, and `sprite_slots` feed the generic `RoutedSourceFamily`.
- Kept route output templates scoped to each route; top-level `templates.pdx`, `templates.loc`, and `templates.copy` remain invalid for `routed_source`.
- Updated the build-flow documentation with the YAML shape for route-specific copied textures plus one shared sprite declaration artifact.

## Verification

- `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_sprite_templates` failed before implementation because routed family declarations rejected `templates`.
- `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_sprite_templates` passed after implementation.
- `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_sprite_templates tests/test_project_build.py::test_project_build_uses_manifest_declared_setting_normalizers` passed.
- `rtk uv run pytest tests/test_project.py::test_project_manifest_rejects_top_level_route_templates_for_routed_family tests/test_project.py::test_project_manifest_rejects_routed_family_without_routes tests/test_project.py::test_project_manifest_rejects_incomplete_sprite_templates` passed.
- `rtk uv run pytest tests/test_project_build.py` passed: 69 tests.
- `rtk uv run pytest tests/test_project.py -k "families or routed or sprite"` passed: 28 selected tests.
- `rtk uv run pytest tests/test_simple_source_family.py::test_routed_source_family_emits_aggregate_sprite_gfx_for_declared_sprite_slots tests/test_build_registry.py` passed: 3 tests.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/extensions.py tests/test_project.py tests/test_project_build.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 326 tests.

## Linear Sync

- TAL-294 read/update attempt failed with `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Risks Or Blockers

- Linear sync may require re-authentication before issue comments can be posted.
- Routed declarative sprites now have parity with Python-backed routed sprites, but route-specific sprite properties beyond `name` and `texturefile` remain future family-code territory.

## Next

- Continue moving project-local compiler declarations toward reusable module family parity while preserving route-specific output ownership.
