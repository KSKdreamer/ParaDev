# Normalizer Error Boundary Progress

Date: 2026-06-07 09:14 CST

Linear: unavailable; tool discovery exposed no Linear connector and `rtk which linear` returned no executable.

## Done

- Continued generic module compiler hardening after validating Python-backed normalizer contracts.
- Found that `ValueError` from a settings normalizer became a `family.invalid_setting` diagnostic, but other normalizer exceptions escaped `Project.build(...)`.
- Changed generic family settings normalization so unexpected normalizer exceptions also produce `family.invalid_setting` diagnostics with module metadata context.
- Preserved the existing `ValueError` diagnostic message shape and included the exception type for unexpected failures.
- Documented that normalizer failures are build diagnostics rather than SDK-level crashes.

## Verification

- Red check: `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_unexpected_family_setting_normalization_errors -q` failed because `TypeError` escaped from the normalizer.
- Focused green: `rtk uv run pytest tests/test_project_build.py::test_project_build_reports_family_setting_normalization_errors tests/test_project_build.py::test_project_build_reports_unexpected_family_setting_normalization_errors -q` passed 2 tests.
- Related project/build suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py -q` passed 162 tests.
- Smoke probe: `Project.build(...)` with a normalizer raising `TypeError` returned `blocked=True` and a `family.invalid_setting` diagnostic.
- Full suite: `rtk bash scripts/test.bash` passed with 256 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py tests/test_project_build.py`

## Review

- The change stays inside the generic family helper and uses the existing diagnostic code, so SDK, CLI, and future GUI/MCP surfaces receive the same build result shape.
- Registry validation still rejects non-callable normalizers before build; this slice covers callable normalizers that fail at runtime on module metadata.
- Black reformatted a few existing long expressions in `src/paradev/build/families.py`; those are formatter-owned changes in the touched file.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- Other family hooks such as custom `emit` or `check` can still raise directly; deciding whether those should become diagnostics needs a separate compiler boundary slice.

## Next

- Continue hardening generic family hook boundaries or shift to user-facing compiler inspection payloads once the extension contracts are stable enough.
