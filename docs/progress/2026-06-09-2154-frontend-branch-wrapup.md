# Frontend Branch Wrap-Up

Date: 2026-06-09 21:54 CST

Scope: minimal-effort wrap-up of active frontend API draft branches back onto current `master`.

## Branch Review

- `codex/frontend-api-master-reconcile` / PR #2 remains a draft and is still GitHub-conflicting with `master`. Local evidence: `master...codex/frontend-api-master-reconcile` is 7 commits behind and 119 ahead, with about 41k insertions and 12k deletions.
- `codex/scaffold-source-root-selection` / PR #1 remains a draft archive branch and is more stale. Local evidence: `master...codex/scaffold-source-root-selection` is 32 commits behind and 113 ahead.
- A dry `git merge-tree master codex/frontend-api-master-reconcile` still reports conflicts in `docs/architecture/interfaces.md`, `docs/plans/linear.md`, `docs/user-manual/*`, `src/paradev/cli.py`, `src/paradev/sdk/frontend_api.py`, `src/paradev/sdk/lsp.py`, `src/paradev/surfaces/lsp.py`, and tests.

## Ported Slice

- Kept the current compact SDK-owned frontend API catalog on `master`.
- Added `render_frontend_api_sdk_cli_markdown()` and `paradev frontend-api --sdk-cli-markdown`.
- Generated `docs/user-manual/sdk-cli-reference.md` from the master catalog.
- Linked the generated SDK/CLI matrix from the user manual, frontend API guide, SDK page, and developer manual.
- Added tests proving the generated manual matches the SDK renderer and the CLI flag emits the expected matrix.

## Deferred

- Did not merge either draft PR directly.
- Did not port branch-only generated TypeScript, desktop helper, binding lookup, workspace action, REST planner, or form framework changes. Those still need a dedicated reconciliation slice against current `master`.
- Left `module.sources` and `collection.sources` as planned rows because current `master` does not expose the branch's full `Project.inspect('sources')` contract.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_catalog_lists_master_line_operations tests/test_cli.py::test_frontend_api_cli_outputs_contract_json tests/test_cli.py::test_frontend_api_cli_selects_operation_group_and_markdown -q`: 3 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash -q`: 431 passed.
- `rtk uv build`: passed.
