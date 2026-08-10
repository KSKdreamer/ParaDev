# Routed Route Template Guard Progress

Date: 2026-06-07 07:19 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added a registry-time guard for Python-backed routed family route entries.
- Project-local Python modules now fail with a contextual `ProjectManifestError` when a route exists but has no artifact templates.
- Added a regression test through the trusted `python_modules` path with `RoutedSourceFamily(..., routes={"advisor": SourceRoute()})`.
- Documented that Python-backed routed families must declare at least one route and at least one artifact template per route.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family_route -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family_route -q`
- Related project/registry tests: `rtk uv run pytest tests/test_project.py tests/test_build_manifest.py -q` passed with 72 tests.
- Routed-source focused tests: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_simple_source_family.py::test_routed_source_family_emits_templates_from_settings_route tests/test_simple_source_family.py::test_routed_source_family_blocks_missing_or_unknown_settings_route -q`
- Full suite: `rtk bash scripts/test.bash` passed with 232 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The route-entry guard uses the registry's existing template projection helper, so it checks the same artifact template surface exposed by family inspection.
- This keeps declarative and Python-backed generic routed family authoring aligned.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening Python-backed generic family contracts, especially invalid route ids and route settings before moving deeper into generic module compilation.
- Keep SDK-facing errors contextual so plugin authors find bad compiler declarations before users hit build-time surprises.
