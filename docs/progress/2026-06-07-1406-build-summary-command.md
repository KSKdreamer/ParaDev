# Build Summary Command Progress

Date: 2026-06-07 14:06 CST

Linear: TAL-293

## Done

- Added a dry-run `Project.summary()` SDK helper that returns the existing `summary.json` manifest payload.
- Added `paradev summary <project> --json` for a compact blocked/status count view.
- Documented the summary inspection path in `docs/workflows/build-flow.md`.
- Added regression tests proving the SDK and CLI summary views do not materialize `.paradev/build/summary.json`.

## Verification

- `rtk uv run pytest tests/test_project.py::test_project_summary_returns_manifest_payload_without_writing tests/test_project.py::test_project_cli_outputs_summary_manifest_json_without_writing`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv run paradev summary demos/assets/projects/minimal --json`

## Risks Or Blockers

- Linear sync is still blocked by expired authentication.

## Next

- Continue hardening generic compiler inspection surfaces before the next first-slot compiler slice.
