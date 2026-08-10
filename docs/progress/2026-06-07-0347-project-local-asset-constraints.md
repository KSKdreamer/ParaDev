# 2026-06-07 03:47 CST - Project-Local Asset Constraints

## Done

- Added `asset_constraints` parsing for project-local `simple_source`, `routed_source`, and `collection_source` declarations.
- Wired parsed constraints into the existing generic family helpers instead of adding a separate asset compiler path.
- Added SDK/build coverage for a manifest-declared `badge` family that exposes an asset contract and reports copy-slot format and dimension diagnostics.
- Added manifest validation for invalid asset constraint dimensions.
- Updated the build-flow guide with a copy-slot asset constraint example.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_asset_constraints -q` failed because the manifest-declared family did not expose an `assets` contract.
- Validation red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_asset_constraints tests/test_project.py::test_project_manifest_rejects_invalid_asset_constraints -q` failed because asset constraints were ignored and invalid dimensions were accepted.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_asset_constraints tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_project_build.py::test_project_build_uses_manifest_declared_collection_family tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project.py::test_project_manifest_rejects_invalid_asset_constraints tests/test_project.py::test_project_manifest_rejects_unsupported_family_kind tests/test_project.py::test_project_manifest_rejects_module_pdx_template_for_simple_family tests/test_project.py::test_project_manifest_rejects_collection_slots_for_simple_family tests/test_project.py::test_project_manifest_rejects_routed_family_without_routes tests/test_project.py::test_project_manifest_rejects_templates_for_routed_family -q` passed 10 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_records.py tests/test_build_manifest.py -q` passed 106 tests.
- Full suite: `rtk bash scripts/test.bash` passed 179 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/extensions.py tests/test_project.py tests/test_project_build.py`
- SDK smoke: `rtk uv run python - <<'PY' ...` loaded a temporary project with manifest-declared asset constraints, inspected the family asset contract, and observed `badge.asset_format` plus `badge.asset_dimensions`.

## Review

- Reviewed the intentional diff for asset constraint manifest validation, family registration wiring, SDK/build coverage, and build-flow docs; no blocking findings.

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Declarative asset constraints cover static copy sources that expose loader metadata; non-image copy sources still report metadata-missing diagnostics when constrained by image format or dimensions.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Add a project-local setting normalization or alias declaration so manifest-only routed families can accept author-friendly values without Python hooks.
