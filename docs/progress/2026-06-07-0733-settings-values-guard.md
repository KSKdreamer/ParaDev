# Settings Values Guard Progress

Date: 2026-06-07 07:33 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added a registry-time guard for Python-backed family `settings_values` contracts.
- Project-local Python modules now fail with a contextual `ProjectManifestError` when `settings_values` contains non-string allowed values.
- Added a regression test through the trusted `python_modules` path with `SimpleSourceFamily(..., settings_values={"picture": ("news", 7)})`.
- Documented that Python-backed `settings_values` must map setting keys to strings or string lists.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_setting_values -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_setting_values -q`
- Existing settings checks: `rtk uv run pytest tests/test_project_build.py::test_project_build_validates_registered_family_setting_values tests/test_project_build.py::test_project_build_requires_registered_family_settings tests/test_project_build.py::test_project_build_reports_family_setting_normalization_errors -q`
- Related project/registry tests: `rtk uv run pytest tests/test_project.py tests/test_build_manifest.py -q` passed with 75 tests.
- Focused settings suite: `rtk uv run pytest tests/test_project_build.py::test_project_build_validates_registered_family_setting_values tests/test_project_build.py::test_project_build_requires_registered_family_settings tests/test_project_build.py::test_project_build_normalizes_family_settings_before_check_and_emit tests/test_project_build.py::test_project_build_reports_family_setting_normalization_errors -q`
- Full suite: `rtk bash scripts/test.bash` passed with 235 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The guard prevents malformed settings contracts from being silently dropped by family views and build diagnostics.
- Existing valid Python-backed settings constraints still work.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening Python-backed generic family declarations around required settings and normalizer contracts.
- Keep pushing compiler-author mistakes toward early SDK errors instead of late or silent build behavior.
