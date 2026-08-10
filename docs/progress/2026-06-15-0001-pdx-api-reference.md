# PDX API Reference Progress

Date: 2026-06-15 00:01

Linear: none

## Done

- Added the SDK-owned PDX API table with typed rows, feature/surface indexes, and a deterministic Markdown renderer.
- Exposed the table through `paradev pdx-api --json` and `paradev pdx-api --markdown`.
- Generated `docs/user-manual/pdx-api-reference.md` and linked it from the manual, SDK, developer, and architecture docs.
- Updated the CLI surface contract so static adapter audits list `pdx-api` and its `markdown` projection.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_pdx_api_cli_outputs_table_json tests/test_cli.py::test_pdx_api_cli_outputs_reference_markdown tests/test_cli.py::test_pdx_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_parse_outputs_pdx_projection_json tests/test_cli.py::test_format_cli_previews_and_writes_pdx_file -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/pdx.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/pdx.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full-suite tests stayed deferred to avoid competing with PIHC3 and desktop workers.
- Existing unrelated dirty files, generated desktop assets, and `node_modules/` remain unstaged.

## Next

- Continue extracting generated API tables for the next clean SDK surface, likely LSP or catalog, after checking the live dirty tree.
