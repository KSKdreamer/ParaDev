# Routed Trait Family Progress

Date: 2026-06-06 22:14 CST

Linear: TAL-294

## Done

- Added `SourceRoute` and `RoutedSourceFamily` so simple families can select artifact templates from a module `settings` value.
- Registered HOI4 `trait` modules with `settings.subtype` routes for `country_leader`, `unit_leader`, and `scientist`.
- Routed trait PDX outputs to `common/country_leader/<object_id>.txt`, `common/unit_leader/<object_id>.txt`, and `common/scientist_traits/<object_id>.txt`.
- Added blocking diagnostics for missing or unsupported routed settings before artifact emission.
- Updated the build-flow workflow with the `trait` subtype contract.

## Verification

- `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_routed_source_family_emits_templates_from_settings_route tests/test_simple_source_family.py::test_routed_source_family_blocks_missing_or_unknown_settings_route tests/test_project_build.py::test_hoi4_profile_routes_trait_artifacts_by_subtype tests/test_project_build.py::test_hoi4_profile_blocks_trait_without_subtype -q`
- `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py tests/test_sdk_examples.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/build/__init__.py src/paradev/games/hoi4/__init__.py tests/test_simple_source_family.py tests/test_project_build.py`
- `rtk rg --files '/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common' | rtk rg '/(country_leader|unit_leader)/.*traits|traits\\.txt|_traits\\.txt'`
- `rtk rg --files '/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/common' | rtk rg 'trait|operative|advisor|scientist'`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Trait routing is intentionally path-level only; semantic subtype validation and role-specific trait rules remain later work.
- Unsupported operative-related files were observed only as AI/operation/codename data, not trait roots, so no `operative` route was registered.
- Existing local desktop and README edits remain outside this routed trait slice.

## Next

- Add profile/family inspection so SDK, CLI, MCP, and desktop clients can list registered families and route requirements without hard-coding profile details.
