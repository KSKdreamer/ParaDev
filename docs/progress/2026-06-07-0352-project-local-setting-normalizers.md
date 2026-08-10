# 2026-06-07 03:52 CST - Project-Local Setting Normalizers

## Done

- Added declarative `settings_normalizers` parsing for project-local generic families.
- Introduced the safe named strategy `lower_snake`, which strips and lowercases string settings and turns separator runs into underscores.
- Wired parsed normalizers into existing `SimpleSourceFamily`, `RoutedSourceFamily`, and `CollectionSourceFamily` constructors.
- Added SDK/build coverage for a manifest-declared routed family that normalizes `settings.subtype: Advisor Role` before route validation and artifact planning.
- Added manifest validation for unsupported normalizer names.
- Updated the build-flow guide with the routed-family normalizer field.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_setting_normalizers tests/test_project.py::test_project_manifest_rejects_unknown_setting_normalizer -q` failed because settings were not normalized and unknown normalizer names were accepted.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_setting_normalizers tests/test_project_build.py::test_project_build_uses_manifest_declared_asset_constraints tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_project_build.py::test_project_build_uses_manifest_declared_collection_family tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project.py::test_project_manifest_rejects_unknown_setting_normalizer tests/test_project.py::test_project_manifest_rejects_invalid_asset_constraints tests/test_project.py::test_project_manifest_rejects_unsupported_family_kind tests/test_project.py::test_project_manifest_rejects_module_pdx_template_for_simple_family tests/test_project.py::test_project_manifest_rejects_collection_slots_for_simple_family tests/test_project.py::test_project_manifest_rejects_routed_family_without_routes tests/test_project.py::test_project_manifest_rejects_templates_for_routed_family -q` passed 12 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_records.py tests/test_build_manifest.py -q` passed 108 tests.
- Full suite: `rtk bash scripts/test.bash` passed 181 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/extensions.py tests/test_project.py tests/test_project_build.py`
- SDK smoke: `rtk uv run python - <<'PY' ...` loaded a temporary routed family, normalized `Advisor Role` to `advisor_role`, and planned `common/advisors/GER_advisor.txt`.

## Review

- Reviewed the intentional diff for manifest normalizer validation, generic family wiring, SDK/build coverage, and build-flow docs; no blocking findings.

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Declarative normalizers are intentionally limited to named safe strategies; arbitrary Python hooks still require registry/plugin loading.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Define the project-local Python compiler loading contract, now that manifest-only generic helpers cover simple, routed, collection, localization, assets, and safe setting normalization.
