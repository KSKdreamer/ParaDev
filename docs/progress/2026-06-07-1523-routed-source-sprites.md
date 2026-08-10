# Routed Source Sprite Aggregation Progress

Date: 2026-06-07 15:23 +0800

Linear: TAL-294

## Done

- Added regression coverage for Python-backed `RoutedSourceFamily` sprite aggregation across route-specific copy templates.
- Extended routed source families with `sprite_gfx_path_template`, `sprite_name_template`, and `sprite_slots`.
- Updated registry validation and family inspection so routed sprite capabilities are exposed to SDK, CLI, GUI, and future MCP consumers.
- Updated build workflow docs for Python-backed routed sprite declarations.

## Verification

- `rtk uv run pytest tests/test_simple_source_family.py::test_routed_source_family_emits_aggregate_sprite_gfx_for_declared_sprite_slots` failed before implementation because `RoutedSourceFamily` did not accept sprite template fields.
- `rtk uv run pytest tests/test_simple_source_family.py::test_routed_source_family_emits_aggregate_sprite_gfx_for_declared_sprite_slots` passed after implementation.
- `rtk uv run pytest tests/test_simple_source_family.py` passed.
- `rtk uv run pytest tests/test_build_registry.py` passed.
- `rtk uv run pytest tests/test_project.py -k "families or python_module"` passed: 24 selected tests.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/registry.py tests/test_simple_source_family.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 325 tests.

## Linear Sync

- Comment attempt on TAL-294 failed with `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Risks Or Blockers

- Declarative YAML routed families still keep the narrower route-template schema; routed sprite aggregation is available through Python-backed registrations.
- Linear sync may require re-authentication before issue comments can be posted.

## Next

- Continue moving routed and project-local compiler capabilities toward parity with simple source families while keeping the beginner mental model small.
