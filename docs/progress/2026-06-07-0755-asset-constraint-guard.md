# Asset Constraint Guard Progress

Date: 2026-06-07 07:55 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added registry-time validation for Python-backed family `asset_constraints`.
- Python-backed asset constraints now reject malformed mappings, empty slot names, non-mapping slot constraints, invalid formats, non-positive dimensions, and empty constraint blocks before family inspection or build planning.
- Added a regression test through the trusted `python_modules` path with `SimpleSourceFamily(..., asset_constraints={"icon": {"width": 0}})`.
- Documented that Python-backed asset constraints use the same slot, format, and dimension rules as declarative project-local families.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_asset_constraints -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_asset_constraints -q`
- Valid asset contract view: `rtk uv run pytest tests/test_project.py::test_project_families_returns_asset_contracts -q`
- Asset diagnostics: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_asset_constraints tests/test_simple_source_family.py::test_simple_source_family_reports_asset_constraint_diagnostics -q`
- Broader project/build/source-family tests: `rtk uv run pytest tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py -q` passed with 145 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 239 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The new registry guard mirrors the manifest-side asset constraint contract while keeping view rendering focused on normalized family payloads.
- Existing valid asset contract views and asset validation diagnostics still pass.
- The change preserves the single registered-family path for built-in, project-local Python, and explicit SDK registries.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening Python-backed generic family declarations around source-slot contracts.
- Keep compiler-author mistakes explicit at registry load time before expanding the generic module compilation layer.
