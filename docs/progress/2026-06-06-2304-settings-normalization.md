# Settings Normalization Progress

Date: 2026-06-06 23:04 CST

Linear: TAL-294 local continuation; live Linear sync unavailable

## Done

- Added TDD coverage for family settings normalization before route validation and artifact planning.
- Added TDD coverage for `family.invalid_setting` diagnostics when a normalizer rejects a value.
- Added the optional family `normalize` stage to `plan_build`.
- Added `FamilyNormalizeResult` and exported it for project-local custom families.
- Added per-key `settings_normalizers` to generic simple, routed, and collection family helpers.
- Guarded custom normalize hooks so they cannot drop modules or change module families.
- Documented the normalize stage and settings normalizer contract in the architecture and build-flow docs.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_normalizes_family_settings_before_check_and_emit tests/test_project_build.py::test_project_build_reports_family_setting_normalization_errors -q`
- Green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_normalizes_family_settings_before_check_and_emit tests/test_project_build.py::test_project_build_reports_family_setting_normalization_errors -q`
- Guard: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_normalizes_family_settings_before_check_and_emit tests/test_project_build.py::test_project_build_reports_family_setting_normalization_errors tests/test_project_build.py::test_project_build_rejects_normalize_hooks_that_drop_modules -q`
- Related: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_simple_source_family.py tests/test_project.py tests/test_build_manifest.py tests/test_build_slots.py tests/test_module_sources.py -q`
- Full: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/__init__.py src/paradev/build/families.py src/paradev/build/plan.py tests/test_project_build.py`
- CLI family smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- CLI build smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Linear probe: `rtk command -v linear`
- Whitespace: `rtk git diff --check src/paradev/build/__init__.py src/paradev/build/families.py src/paradev/build/plan.py tests/test_project_build.py docs/goals/final-architecture.md docs/workflows/build-flow.md docs/progress/2026-06-06-2304-settings-normalization.md`

## Risks Or Blockers

- Live Linear sync is still blocked because no Linear MCP tool is exposed and `linear` is not available on `PATH`.
- Normalizers intentionally catch `ValueError` as source diagnostics; unexpected programming errors still fail loudly.
- Existing local desktop, README, and script edits remain outside this slice.

## Next

- Add a first small reusable normalizer in the HOI4 profile if a concrete family needs forgiving aliases, or move to collection-aware event namespace compilation.
