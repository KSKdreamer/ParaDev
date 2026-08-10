# Required Settings Guard Progress

Date: 2026-06-07 07:38 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added registry-time validation for Python-backed family `settings_keys` and `required_settings`.
- Project-local Python modules now fail with a contextual `ProjectManifestError` when `required_settings` contains non-string entries.
- Added a regression test through the trusted `python_modules` path with `SimpleSourceFamily(..., required_settings=("picture", 7))`.
- Documented that Python-backed setting key declarations must be strings or string lists.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_required_settings -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_required_settings -q`
- Existing settings checks: `rtk uv run pytest tests/test_project_build.py::test_project_build_validates_registered_family_setting_values tests/test_project_build.py::test_project_build_requires_registered_family_settings tests/test_project_build.py::test_project_build_normalizes_family_settings_before_check_and_emit tests/test_project_build.py::test_project_build_reports_family_setting_normalization_errors -q`
- Related project/registry tests: `rtk uv run pytest tests/test_project.py tests/test_build_manifest.py -q` passed with 76 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 236 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The new shared string-list validator keeps `settings_keys` and `required_settings` from being silently filtered out by registry views and build diagnostics.
- Existing valid Python-backed settings contracts still work.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening Python-backed generic family declarations around localization-key and metadata-key contracts.
- Keep moving compiler-author mistakes into early SDK errors before generic module compilation expands.
