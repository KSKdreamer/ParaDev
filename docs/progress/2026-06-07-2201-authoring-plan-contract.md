# 2026-06-07 22:01 CST - Authoring Plan Contract

## Scope

- Added the read-only `paradev.sdk.authoring_plan.v1` contract for preflight authoring flows.
- Added `paradev.build.authoring_plan_view(...)`, exported it from `paradev.build`, and wired `Project.authoring_plan(...)` over the selected build registry.
- Added `paradev authoring-plan <path> <module|collection> <family> <target_id> --json`.
- Added REST/OpenAPI `/projects/authoring-plan` and MCP `project_authoring_plan` contract rows.
- Updated the English and Chinese user manual, developer manual, architecture boundary, and build workflow docs.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_authoring_views.py tests/test_project.py::test_project_authoring_plan_returns_project_local_family_slots tests/test_cli.py::test_authoring_plan_cli_lists_expected_source_slots tests/test_architecture.py -q`
  - Failed before implementation because `authoring_plan_view` was not exported.
- Green focused: same command
  - `14 passed in 0.51s`.
- Focused surface suite: `rtk bash scripts/test.bash tests/test_authoring_views.py tests/test_architecture.py tests/test_cli.py -q`
  - `27 passed in 0.79s`.
- Live CLI probe: `rtk uv run paradev authoring-plan demos/assets/projects/minimal module idea GER_industry_spirit --json`
  - Returned `paradev.sdk.authoring_plan.v1` with nested authoring path and `def`, `icon`, `loc` source-slot rows.

## Gates

- `rtk uv run black src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_authoring_views.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - 11 files left unchanged.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_authoring_views.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - OK: 11 files, no banned imports.
- `rtk rg -n "authoring-plan|Project.authoring_plan|authoring_plan_view|project_authoring_plan|/projects/authoring-plan" docs/user-manual docs/architecture/interfaces.md docs/workflows/build-flow.md src/paradev tests`
  - Confirmed code and docs coverage.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - 52 files would be left unchanged.
- `rtk bash scripts/test.bash`
  - 389 passed in 78.30s.
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- Heaven-style review target: current uncommitted diff against `origin/codex/scaffold-source-root-selection`.
- Findings: none blocking.
- Residual risk: REST/MCP remain contract scaffolds; production server/tool registration is still future work.

## Linear

- TAL-294 updated with comment `be889f89-bb8c-4cdf-a9bc-d97a7337820d`.
- TAL-295 updated with comment `5a451be4-44c0-4231-9f18-50b4804d3cb3`.

## Next

- Continue generic compilation support by exposing more registry-owned preflight and build payloads that GUI, MCP, REST, importer, and CLI clients can share without family-specific path logic.
