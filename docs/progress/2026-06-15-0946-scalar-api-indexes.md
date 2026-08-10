# Scalar API Indexes Progress

Date: 2026-06-15 09:46

Linear: not linked

## Done

- Reused `api_symbol_indexes()` for scalar symbol indexes in SDK template, copy-root, PDX, LSP, architecture, and HeavenBase catalog API table builders.
- Preserved generated API-reference Markdown output for all touched renderers.
- Left PIHC3 migration, desktop, logo, and `node_modules/` worktree changes untouched.

## Verification

- `rtk uv run python - <<'PY' ...` renderer comparison against `HEAD`: all six Markdown renderers matched byte-for-byte.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces -q`
- `rtk uv run python -m py_compile src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/hb/__init__.py src/paradev/_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/hb/__init__.py src/paradev/_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/hb/__init__.py src/paradev/_api_table.py`
- `rtk git diff --check -- src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/hb/__init__.py src/paradev/_api_table.py`

## Risks Or Blockers

- Full-suite tests skipped to keep CPU free for PIHC3 migration workers.
- `gh pr status` reported no open PRs for this checkout, so there were no GitHub review comments to address in this pass.

## Next

- Generalize list-valued API table indexes only after another narrow behavior-equivalence pass.
