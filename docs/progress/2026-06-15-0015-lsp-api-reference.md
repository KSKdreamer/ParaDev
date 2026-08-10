# LSP API Reference Progress

Date: 2026-06-15 00:15

Linear: none

## Done

- Added the SDK-owned LSP API table with typed rows, feature/surface indexes, and a deterministic Markdown renderer.
- Exposed the table through `paradev lsp-api --json` and `paradev lsp-api --markdown`.
- Generated `docs/user-manual/lsp-api-reference.md` and linked it from the manual, SDK, developer, and architecture docs.
- Updated the CLI surface contract so static adapter audits list `lsp-api` and its `markdown` projection.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces tests/test_architecture.py::test_lsp_surface_contract_lists_sdk_owned_methods tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_lsp_api_cli_outputs_table_json tests/test_cli.py::test_lsp_api_cli_outputs_reference_markdown tests/test_cli.py::test_lsp_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_lsp_diagnostics_cli_outputs_lsp_payload tests/test_cli.py::test_lsp_formatting_cli_reads_text_file -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/lsp.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full-suite tests stayed deferred to avoid competing with PIHC3 and desktop workers.
- Existing unrelated dirty files, generated desktop assets, and `node_modules/` remain unstaged.

## Next

- Continue extracting generated API tables for the next clean SDK surface after checking the live dirty tree.
