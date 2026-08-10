# Localization Inspection Progress

Date: 2026-06-06 21:43 CST

Linear: TAL-294

## Done

- Added `Project.localization()` as a fresh dry-build projection of the localization manifest payload.
- Added `paradev localization <path> --json` so users and surfaces can inspect localization rows without knowing `.paradev/build/localization.json`.
- Covered the SDK helper and CLI command against the minimal demo project.
- Documented the localization inspection workflow.

## Verification

- `rtk bash scripts/test.bash tests/test_project.py::test_project_localization_returns_manifest_payload_without_writing tests/test_project.py::test_project_cli_outputs_localization_manifest_json -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_sdk_examples.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- `rtk uv run paradev localization demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- The helper returns the whole schema-bearing payload; filtered views can be added later when UI/MCP callers need them.
- Existing local desktop and README edits remain outside this SDK/CLI slice.

## Next

- Add a first project-level localization index or filter API once cross-module collision policy is defined.
