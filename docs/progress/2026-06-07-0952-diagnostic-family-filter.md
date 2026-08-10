# Diagnostic Family Filter Progress

Date: 2026-06-07 09:52 CST

Linear: connector discovered, but `_save_comment` on `TAL-293` failed with `UNAUTHORIZED`; the session needs re-authentication.

## Done

- Added a `family` filter to `Project.diagnostics(...)`.
- Added `--family` to `paradev diagnostics`.
- Made the filter match both direct diagnostic rows and resolved `source.family` metadata.
- Updated diagnostics workflow docs and SDK/CLI tests.

## Verification

- Red SDK check: `rtk uv run pytest tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing -q` failed because `Project.diagnostics(...)` did not accept `family`.
- Red CLI check: `rtk uv run pytest tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q` failed because `--family` was not a known option.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json tests/test_project.py::test_project_diagnostics_filters_slot_collision_by_collided_slot -q` passed 3 tests.
- CLI smoke: `paradev diagnostics --family focus --code focus.missing_localization --json` against a temporary project returned the expected row and severity/code index.
- Related project/CLI suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_cli.py -q` passed 86 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 263 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/project.py tests/test_project.py`

## Review

- The change extends the existing diagnostics filter model instead of adding a parallel query path.
- Family matching mirrors module/source/slot matching by checking both the row field and resolved source metadata.
- This makes hook diagnostics and source-anchored diagnostics filterable through one CLI/SDK option.
- Unrelated desktop, README, and runner-script work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated because the connector session is expired.

## Next

- Consider whether diagnostic indexes should include family once callers start depending on this filter.
