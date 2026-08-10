# Static Copy Emission Errors Progress

Date: 2026-06-07 14:33

Linear: TAL-294

## Done

- Added regression coverage for static copy artifacts whose planned source becomes unreadable during hash revalidation.
- Added regression coverage for static copy artifacts whose final copy operation fails during emission.
- Wrapped those filesystem failures in contextual `ValueError` messages that include the artifact path, source path, and target path when available.
- Updated the build workflow docs to describe emission-time static copy revalidation.

## Verification

- `rtk uv run pytest tests/test_artifact_writers.py::test_static_copy_writer_reports_unreadable_hashed_source` failed before the fix with raw `OSError`, then passed after the fix.
- `rtk uv run pytest tests/test_artifact_writers.py::test_static_copy_writer_reports_copy_failure` failed before the fix with raw `OSError`, then passed after the fix.
- `rtk uv run pytest tests/test_artifact_writers.py` passed: 12 tests.
- `rtk git diff --check` passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/artifacts.py tests/test_artifact_writers.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
- `rtk bash scripts/test.bash` passed: 320 tests.

## Risks Or Blockers

- Linear API access is still blocked by an expired session, so TAL-294 could not be updated from this loop until re-authentication.
- The direct `rtk python` scanner invocation misses project dependencies in this environment; the scanner passes through `rtk uv run python`.

## Next

- Continue TAL-294 by tightening user-facing artifact emission behavior and then move toward the generic module compilation system slices.
