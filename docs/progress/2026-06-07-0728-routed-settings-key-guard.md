# Routed Settings Key Guard Progress

Date: 2026-06-07 07:28 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added a registry-time guard for Python-backed routed family `settings_key` values.
- Project-local Python modules now fail with a contextual `ProjectManifestError` when a routed family uses an empty or dotted settings key.
- Added a regression test through the trusted `python_modules` path with `RoutedSourceFamily(..., settings_key="")`.
- Documented that Python-backed routed families use a non-empty unprefixed `settings_key`.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_settings_key -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family_route tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_family_route_id tests/test_project.py::test_project_families_rejects_python_module_with_empty_routed_settings_key -q`
- Related project/registry tests: `rtk uv run pytest tests/test_project.py tests/test_build_manifest.py -q` passed with 74 tests.
- Routed-source focused tests: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_simple_source_family.py::test_routed_source_family_emits_templates_from_settings_route tests/test_simple_source_family.py::test_routed_source_family_blocks_missing_or_unknown_settings_route -q`
- Full suite: `rtk bash scripts/test.bash` passed with 234 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- Python-backed routed families now match the manifest parser's core route-setting invariant: one key under `settings`, not an empty key or nested path.
- The guard runs at registration time, before invalid families can reach family inspection, discovery, or build diagnostics.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening generic family declarations around Python-backed settings values and normalizer contracts.
- Keep moving toward generic module compilation with early, contextual SDK errors for compiler authors.
