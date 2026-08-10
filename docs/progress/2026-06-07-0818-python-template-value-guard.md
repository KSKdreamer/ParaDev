# Python Template Value Guard Progress

Date: 2026-06-07 08:18 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added registry-time validation for Python-backed artifact template values.
- Python-backed simple and routed family template attributes now reject non-string or blank values before family inspection or build payload rendering.
- Added a regression test through the trusted `python_modules` path with `SimpleSourceFamily(..., pdx_path_template=7)`.
- Documented that Python-backed artifact templates must be non-empty strings before placeholder validation runs.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_template_value -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_template_value tests/test_project.py::test_project_families_rejects_python_module_with_unknown_template_field -q`
- Manifest template checks: `rtk uv run pytest tests/test_project.py::test_project_manifest_rejects_unknown_family_template_fields tests/test_project.py::test_project_manifest_rejects_incomplete_sprite_templates -q`
- Valid family view checks: `rtk uv run pytest tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project.py::test_project_families_returns_asset_contracts -q`
- Broader project/build tests: `rtk uv run pytest tests/test_project.py tests/test_project_build.py -q` passed with 129 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 244 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The registry now uses a validation-only template extractor for project/plugin errors and keeps the existing view helper as a renderer for validated families.
- Routed family routes now validate malformed template values before checking placeholder fields or route completeness.
- Existing valid template and family view flows still pass.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue moving plugin/compiler author mistakes to early contextual SDK errors.
- Revisit remaining template-family invariants such as sprite template completeness before moving back to parser and build graph work.
