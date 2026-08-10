# 2026-06-13 11:53 HB/LSP/VS Code Integration

## Summary

- Extended the HeavenBase HOI4 catalog extension with first-class scanned `module`, `collection`, and `source-slot` rows in addition to build outputs, PDX documents/symbols, localization, sources, diagnostics, and HOI4 entities.
- Added catalog-backed PDX completion and semantic-token SDK payloads, REST routes, CLI commands, frontend API rows, and generated TypeScript/reference docs.
- Added a stdio JSON-RPC PDX language server at `paradev lsp serve` with initialize, text sync, diagnostics publish, symbols, hover, formatting, completion, and semantic-token requests.
- Wired the desktop CodeMirror editor to request PDX completions/highlighting through Tauri or REST helpers.
- Added a minimal VS Code extension package under `packages/vscode-paradev` that launches `paradev lsp serve --project <workspace>`.

## Verification

- `rtk bash scripts/test.bash tests/test_lsp.py tests/test_hb.py tests/test_cli.py tests/test_architecture.py -q` passed, 127 tests.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/pdxLsp.test.ts src/moduleEditor/model.test.ts src/data/frontendApi.test.ts src/data/frontendApiBindingIndex.test.ts src/data/frontendApiSummary.test.ts` passed, 27 tests.
- `rtk npm --prefix apps/desktop run build` passed.
- `rtk npm --prefix packages/vscode-paradev run compile` passed.
- `rtk bash -lc 'cd apps/desktop/src-tauri && cargo test'` passed, 8 tests. The bash shell printed existing zsh completion warnings from `.bash_profile`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py src/paradev/hb/hoi4.py src/paradev/sdk/lsp.py src/paradev/lsp src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/lsp.py src/paradev/surfaces/vscode.py tests/test_hb.py tests/test_lsp.py tests/test_architecture.py tests/test_cli.py` passed.
- `rtk bash scripts/flake.bash --ci` passed.
