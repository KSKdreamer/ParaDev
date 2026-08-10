# Frontend Chinese Binding Reference Sections Progress

Date: 2026-06-15 16:17

Linear: Not updated

## Done

- Converted the Chinese frontend SDK, MCP, CLI, LSP, binding, and group binding summary reference tables in `src/paradev/sdk/frontend_api.py` to `_frontend_api_table_section`.
- Preserved the generated frontend API reference output while removing another cluster of hand-written Markdown headers.
- Confirmed the remaining manual Chinese reference tables now begin at the payload and workspace summary cluster.

## Verification

- `rtk uv run black src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python - <<'PY' ...` checked all 29 generated API references against checked-in docs.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Risks Or Blockers

- Full-suite tests were deferred to keep CPU available for concurrent PIHC migration work.
- Existing unrelated workspace changes were left untouched.

## Next

- Continue with the payload, workspace, surface, form, control, option source, input target, and validation summary reference tables in small parity-checked slices.
