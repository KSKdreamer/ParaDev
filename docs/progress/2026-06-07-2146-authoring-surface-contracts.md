# 2026-06-07 21:46 CST - Authoring Surface Contracts

## Scope

- Exposed SDK-owned authoring reads through every planned automation surface.
- Added REST/OpenAPI seed paths for `/projects/templates` and `/projects/authoring-path`.
- Added MCP read-only tool contracts for `project_templates` and `project_authoring_path`.
- Added CLI contract adapter rows for `templates`, `authoring-path`, `scaffold`, and `families`.
- Updated architecture, build-flow, and bilingual user/developer manuals so GUI, MCP, REST, and importer agents use the SDK contract instead of inferring paths from CLI examples.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py -q`
  - Failed before implementation because the OpenAPI seed, CLI adapter map, and MCP tool list did not expose authoring template/path contracts.
- Green focused: `rtk bash scripts/test.bash tests/test_architecture.py -q`
  - `5 passed in 0.44s`
- Focused surface/CLI regression: `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q`
  - `19 passed in 0.81s`

## Gates

- `rtk uv run black src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - 4 files left unchanged.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - OK: 4 files, no banned imports.
- `rtk git diff --check`
  - Passed.
- `rtk rg -n "Project.templates|Project.authoring_path|/projects/templates|/projects/authoring-path|project_templates|project_authoring_path" docs/user-manual docs/architecture/interfaces.md docs/workflows/build-flow.md`
  - Confirmed manual and architecture coverage.
- `rtk bash scripts/flake.bash --ci`
  - 52 files would be left unchanged.
- `rtk bash scripts/test.bash`
  - 384 passed in 80.70s.
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- Heaven-style review target: current uncommitted diff against `origin/codex/scaffold-source-root-selection`.
- Findings: none blocking.
- Residual risk: REST/MCP routes are still scaffold contracts; production server/tool registration is future work.

## Linear

- TAL-294 updated with comment `879ed20b-02c5-4813-a15e-91f60d81f2e0`.
- TAL-295 updated with comment `77307355-0b3e-4e8a-b1ee-d7fee0b3c29a`.
- Note: the Codex Apps Linear fetch connector reported an expired session, so issue re-read was not available in this loop. The standalone Linear comment endpoint succeeded.

## Next

- Continue from generic module compilation, prioritizing SDK-owned contracts that help CLI, GUI, MCP, REST, and importer agents share the same family/source-slot/build payloads.
