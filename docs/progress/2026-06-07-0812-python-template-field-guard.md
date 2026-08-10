# Python Template Field Guard Progress

Date: 2026-06-07 08:12 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added registry-time validation for Python-backed artifact template placeholders.
- Python-backed simple, routed, collection, sprite, and view templates now use the same supported field sets as declarative project-local family declarations.
- Added a regression test through the trusted `python_modules` path with `SimpleSourceFamily(..., pdx_path_template="common/notices/{unknown_field}.txt")`.
- Documented that Python-backed templates are validated before they appear in family inspection or build payloads.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_unknown_template_field -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_unknown_template_field -q`
- Valid family view checks: `rtk uv run pytest tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project.py::test_project_families_returns_asset_contracts -q`
- Profile family contract check: `rtk uv run pytest tests/test_project.py::test_project_families_returns_profile_family_contracts -q`
- Broader project/build tests: `rtk uv run pytest tests/test_project.py tests/test_project_build.py -q` passed with 128 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 243 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The registry now rejects unsupported Python-backed template fields before family inspection, discovery, build planning, or artifact emission.
- The field sets mirror the manifest validator and render helpers: module templates, collection templates, collection-member templates, sprite GFX templates, and sprite names each get the matching allowed placeholders.
- Existing profile family contracts and valid custom family views still pass.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue moving compiler-author mistakes into contextual SDK validation where the user can fix a project or plugin without reading build internals.
- After the registered-family contract is consistently early-failing, shift back toward PDX parser and generic build graph behavior.
