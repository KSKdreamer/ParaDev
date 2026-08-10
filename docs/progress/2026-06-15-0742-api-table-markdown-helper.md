# API Table Markdown Helper Progress

Date: 2026-06-15 07:42 +0800

Linear: none

## Done

- Added `paradev._api_table_markdown` as the shared Markdown table helper for generated API reference rows.
- Migrated the SDK authoring-template API renderer to use the shared helper.
- Migrated the SDK copy-root API renderer to use the shared helper.
- Kept the generated table schemas, docs content, CLI behavior, and public SDK exports unchanged.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`
- `rtk uv run pytest tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract tests/test_cli.py::test_templates_api_cli_outputs_reference_markdown tests/test_cli.py::test_templates_api_cli_outputs_table_json tests/test_cli.py::test_copy_roots_api_cli_outputs_reference_markdown tests/test_cli.py::test_copy_roots_api_cli_outputs_table_json`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, PIHC3, Heaven-style skill, logo, and loader changes from other workers.
- `node_modules/` remains untracked and must not be staged.

## Next

- Continue consolidating duplicated API-reference table rendering once neighboring modules are quiet.
- Add more generated API reference pages only when the owning surface has a stable contract.
