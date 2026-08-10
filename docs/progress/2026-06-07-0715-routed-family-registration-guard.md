# Routed Family Registration Guard Progress

Date: 2026-06-07 07:15 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added a registry-time contract check for generic routed build families.
- Project-local Python modules now fail with a contextual `ProjectManifestError` when they register a routed family without any routes.
- Added a regression test that exercises the trusted `python_modules` path rather than only direct registry construction.
- Documented that Python-backed generic routed families must declare at least one route, matching the declarative manifest contract.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family -q`
- Related project/registry tests: `rtk uv run pytest tests/test_project.py tests/test_build_manifest.py -q` passed with 71 tests.
- Routed-source focused tests: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_simple_source_family.py::test_routed_source_family_emits_templates_from_settings_route tests/test_simple_source_family.py::test_routed_source_family_blocks_missing_or_unknown_settings_route -q`
- Full suite: `rtk bash scripts/test.bash` passed with 231 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The guard lives at `BuildRegistry.add_family(...)`, so direct SDK registries and project-local Python modules share the same extension contract.
- Duplicate built-in families are still rejected before family-contract checks, preserving the existing duplicate-key diagnostic.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue tightening Python-backed generic family contracts, especially route entries with no artifact templates.
- Keep moving toward the generic module compilation system by making plugin-author failures early, contextual, and visible through SDK surfaces.
