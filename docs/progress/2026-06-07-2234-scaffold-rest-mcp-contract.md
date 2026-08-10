# 2026-06-07 22:34 CST - Scaffold REST/MCP Contract

## Scope

- Added `/projects/scaffold` to the OpenAPI seed as a write-capable `POST` route over `Project.scaffold_module(...)`.
- Added the optional FastAPI `/projects/scaffold` route behind the existing `rest` extra.
- Added `project_scaffold` to the MCP surface contract with `read_only: false`.
- Updated the English and Chinese developer manual, SDK manual, architecture boundary, and build workflow docs so GUI, MCP, REST, and importer agents can route scaffold plans/writes through the SDK instead of copying CLI behavior.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because `/projects/scaffold` and `project_scaffold` were absent.
- Green focused: same command
  - `2 passed in 0.28s`.
- Architecture surface suite:
  - `rtk bash scripts/test.bash tests/test_architecture.py -q`
  - `5 passed in 0.37s`.
- Surface probe:
  - `rtk uv run python - <<'PY' ... get_openapi_seed(); get_mcp_contract() ... PY`
  - Confirmed the `/projects/scaffold` summary and `project_scaffold` contract.

## Gates

- `rtk uv run black src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - 3 files left unchanged.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - OK: 3 files, no banned imports.
- `rtk rg -n "/projects/scaffold|project_scaffold|Project.scaffold_module|authoring-plan" docs/architecture docs/user-manual docs/workflows src/paradev/surfaces tests/test_architecture.py`
  - Confirmed code and docs coverage.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - 52 files would be left unchanged.
- `rtk bash scripts/test.bash`
  - 391 passed in 77.39s.
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- Heaven-style review target: current uncommitted diff against `origin/codex/scaffold-source-root-selection`.
- Findings: none blocking.
- Residual risk: FastAPI is not installed in the current dev environment, so the optional runtime route was not exercised through `TestClient`; OpenAPI seed, contract tests, imports, lint, full tests, and package build passed.

## Linear

- TAL-294 updated with comment `5d99d136-f004-4067-8313-c52152e7948c`.
- TAL-295 updated with comment `90c5380f-d885-445d-ae8e-c7409cd4ffb8`.

## Next

- Continue stabilizing shared SDK surfaces by making GUI/importer-facing flows consume the same scaffold and authoring-plan payloads, then continue deeper generic compiler slices.
