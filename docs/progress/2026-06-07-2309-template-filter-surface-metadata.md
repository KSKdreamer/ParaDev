# Template Filter Surface Metadata

Date: 2026-06-07 23:09

Issues: TAL-294, TAL-295

## Summary

- Exposed the `Project.templates(...)` filter names in the static CLI surface contract via `get_cli_contract()["filters"]["templates"]`.
- Exposed the same filter names on the MCP `project_templates` tool contract via `get_mcp_contract()`.
- Updated English and Chinese developer manual text plus the architecture boundary so adapter agents can discover filter support from surface metadata instead of reading Typer or REST route code.
- Kept the runtime filtering implementation unchanged; this slice only aligns static adapter contracts with the SDK/CLI/REST template filters.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because the CLI contract did not expose `filters`, and the MCP `project_templates` contract did not list the template filters.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `2 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - `OK: 3 file(s) - no banned imports`
- `rtk rg -n 'filters|Project\.templates|project_templates|template_id|authoring_ready|diagnostic_code|get_cli_contract|get_mcp_contract' docs/user-manual/developer-manual.md docs/architecture/interfaces.md src/paradev/surfaces tests/test_architecture.py`
  - Confirmed CLI, MCP, REST, architecture, manual, and tests expose or reference the template filter metadata.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `397 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The change is additive metadata on static contracts. Existing CLI, MCP, REST, and SDK runtime behavior remains compatible.
- The filter list is intentionally exact and mirrors `Project.templates(...)`, `paradev templates`, and `/projects/templates`.
- No PIHC3 migration or GUI implementation code was added.

## Linear

- `TAL-295` updated with comment `f6438116-a28b-4847-88d3-bf6f19392952`.
- `TAL-294` updated with comment `c1d91b23-cf2b-4ed6-b8fd-675be3749223`.
