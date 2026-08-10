# Required Localization Key Guard Progress

Date: 2026-06-07 07:45 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added registry-time validation for Python-backed family `required_loc_keys`.
- Python-backed localization key templates now reject unsupported fields during `project.families()` instead of failing later when diagnostics render.
- Matched the declarative manifest contract: Python-backed `required_loc_keys` may use only `{family}`, `{module_id}`, and `{object_id}`.
- Added a regression test through the trusted `python_modules` path with `SimpleSourceFamily(..., required_loc_keys=("{unknown_field}",))`.
- Documented the Python-backed localization template contract in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_unknown_required_loc_key_field -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_unknown_required_loc_key_field -q`
- Adjacent registry checks: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_required_settings tests/test_project.py::test_project_families_rejects_python_module_with_invalid_setting_values -q`
- Required localization diagnostic check: `rtk uv run pytest tests/test_simple_source_family.py::test_simple_source_family_reports_missing_required_localization_keys -q`
- Related project/family tests: `rtk uv run pytest tests/test_project.py tests/test_simple_source_family.py -q` passed with 89 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 237 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The new registry helper uses `string.Formatter` so invalid Python format strings, positional fields, unsupported compound fields, and unknown named fields are rejected before family inspection or build planning.
- Existing settings validation still uses the same string-list contract after the helper refactor.
- Valid required-localization diagnostics still render the supported fields correctly for generic simple-source families.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening Python-backed generic family declarations around metadata and asset contracts.
- Keep moving compiler-author mistakes into early SDK errors before generic module compilation expands.
