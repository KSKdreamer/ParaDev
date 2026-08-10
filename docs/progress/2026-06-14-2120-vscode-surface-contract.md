# VS Code Surface Contract Constants

Date: 2026-06-14 21:20 Asia/Shanghai

## Summary

- Named the VS Code LSP launch command and dependent surface list inside `src/paradev/surfaces/vscode.py`.
- Added architecture-test assertions that the VS Code surface remains SDK-owned and explicitly depends on LSP, CLI, REST, and OpenAPI contracts.
- Kept the emitted `get_vscode_contract()` payload unchanged for existing adapter consumers.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/vscode.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/vscode.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/surfaces/vscode.py tests/test_architecture.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_vscode_surface_contract_launches_pdx_lsp`
- Direct `get_vscode_contract()` probe for launch command, uses, and `sdk_owned`.

## Notes

- This is a behavior-preserving surface-contract cleanup.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
- Existing PIHC3 migration, desktop, skill, logo, and `node_modules` worktree changes were left untouched.
