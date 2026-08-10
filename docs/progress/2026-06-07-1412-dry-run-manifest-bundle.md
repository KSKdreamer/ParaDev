# Dry-Run Manifest Bundle Progress

Date: 2026-06-07 14:12 CST

Linear: TAL-293

## Done

- Added a dry-run `Project.manifests()` SDK helper that returns all current build manifest payloads keyed by manifest file name.
- Added `paradev manifests <project> --json` for CLI, script, desktop, and future MCP clients that need the whole manifest bundle without writing files.
- Documented the aggregate manifest inspection path in `docs/workflows/build-flow.md`.
- Added regression tests proving the SDK and CLI aggregate view does not materialize `.paradev/build/*.json`.

## Verification

- `rtk uv run pytest tests/test_project.py::test_project_manifests_returns_all_manifest_payloads_without_writing tests/test_project.py::test_project_cli_outputs_all_manifest_payloads_without_writing`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv run paradev manifests demos/assets/projects/minimal --json`

## Risks Or Blockers

- Linear sync failed again with `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening generic compiler inspection surfaces and first-slot compiler ergonomics.
