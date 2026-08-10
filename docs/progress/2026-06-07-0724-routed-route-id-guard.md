# Routed Route Id Guard Progress

Date: 2026-06-07 07:24 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added a registry-time guard for Python-backed routed family route ids.
- Project-local Python modules now fail with a contextual `ProjectManifestError` when a routed family uses an empty route id.
- Added a regression test through the trusted `python_modules` path with `RoutedSourceFamily(..., routes={"": SourceRoute(...)})`.
- Documented that Python-backed routed family route ids must be non-empty strings.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family_route_id -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family_route tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family_route_id -q`
- Related project/registry tests: `rtk uv run pytest tests/test_project.py tests/test_build_manifest.py -q` passed with 73 tests.
- Routed-source focused tests: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_simple_source_family.py::test_routed_source_family_emits_templates_from_settings_route tests/test_simple_source_family.py::test_routed_source_family_blocks_missing_or_unknown_settings_route -q`
- Full suite: `rtk bash scripts/test.bash` passed with 233 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The route-id guard runs before sorting route entries, so non-string route ids are also rejected before they can trigger less helpful comparison errors.
- This keeps declarative and Python-backed routed family contracts aligned at registration time.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening route settings and generic family declarations before moving deeper into generic module compilation.
- Keep focusing on SDK-facing errors that help plugin authors fix compiler declarations before users hit build-time surprises.
