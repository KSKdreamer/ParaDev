# 2026-06-07 03:41 CST - Project-Local Routed Families

## Done

- Extended `paradev.yaml` project-local declarations to support generic `routed_source` families.
- Added declarative `route_setting` and `routes` parsing, then registered the existing `RoutedSourceFamily` instead of adding a new compiler path.
- Added SDK/build coverage for a manifest-declared `character` family that routes PDX and localization artifacts by `settings.subtype`.
- Added manifest validation for missing routed routes and copied top-level `templates` on routed families.
- Updated the build-flow guide with a copyable routed-family example and the user-facing routing behavior.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family -q` failed because `routed_source` was not an allowed project-local family kind.
- Validation red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_project.py::test_project_manifest_rejects_routed_family_without_routes tests/test_project.py::test_project_manifest_rejects_templates_for_routed_family -q` failed with the same unsupported-kind boundary before route validation existed.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_routed_family tests/test_project_build.py::test_project_build_uses_manifest_declared_collection_family tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project.py::test_project_manifest_rejects_unsupported_family_kind tests/test_project.py::test_project_manifest_rejects_module_pdx_template_for_simple_family tests/test_project.py::test_project_manifest_rejects_collection_slots_for_simple_family tests/test_project.py::test_project_manifest_rejects_routed_family_without_routes tests/test_project.py::test_project_manifest_rejects_templates_for_routed_family -q` passed 8 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_records.py tests/test_build_manifest.py -q` passed 104 tests.
- Full suite: `rtk bash scripts/test.bash` passed 177 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/extensions.py tests/test_project.py tests/test_project_build.py`
- SDK smoke: `rtk uv run python - <<'PY' ...` loaded a temporary project with a manifest-declared `character` routed family and planned `common/advisors/GER_advisor.txt` plus `localisation/english/GER_advisor_l_english.yml`.

## Review

- Reviewed the intentional diff for route manifest validation, routed-family registration, SDK/build coverage, and build-flow docs; no blocking findings.

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Declarative project-local families now cover generic `simple_source`, `routed_source`, and `collection_source`; custom Python-backed compilers remain a later registry/plugin loading slice.
- `route_setting` is stored as a setting key and projected as `settings.<key>` in family inspection payloads.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Define the project-local Python compiler loading contract, or add a small route-setting normalization declaration if generic manifest-only routing needs author-friendly aliases.
