# 2026-06-20 03:33 +0800 - LSP server API selector helper

## Slice

- Added `get_lsp_server_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.lsp` facade API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.lsp` and regenerated `docs/user-manual/lsp-server-api-reference.md`, increasing the LSP server API row count to 11.
- Added `tests/test_lsp_server_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_lsp_server_api_selection.py` failed on missing `get_lsp_server_api_selection`.
- Green: `rtk uv run pytest -q tests/test_lsp_server_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/lsp/api.py src/paradev/lsp/__init__.py tests/test_lsp_server_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/lsp/api.py src/paradev/lsp/__init__.py tests/test_lsp_server_api_selection.py` -> clean.

## Notes

- Regenerated the LSP server reference from `render_lsp_server_api_reference_markdown()` directly to avoid relying on dirty CLI files.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the LSP server API table module, package facade export, generated LSP server reference, the focused test, and this note.
