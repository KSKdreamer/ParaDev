# Frontend Binding Lookup SDK/CLI Slice

Date: 2026-06-08 18:37 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `6dda7007-839b-44d3-83f2-e3baab882287`, `TAL-295` comment `c9aa7021-3c12-4f2a-8b3a-72e536d850e9`

## Summary

This slice turns the frontend API binding index from an internal generated map into a maintained Python SDK and CLI feature. The previous guard proved every SDK, CLI, REST, MCP, and LSP binding is indexed; this change gives Python adapters, GUI bridges, docs tooling, and command-line users a stable reverse lookup payload for mapping one surface call key back to canonical frontend operation ids.

From a HoI4 mod developer's perspective, this keeps the mental model small: inspect the frontend API once, then ask `paradev frontend-api --binding-surface rest --binding-key ...` when a route or command needs to be mapped back to workbench actions. From a developer's perspective, the lookup stays derived from row-level `bindings`, so adding or fixing one canonical operation row updates SDK helpers, CLI output, generated TypeScript, OpenAPI annotations, and bilingual manuals together.

## Changes

- Added SDK helpers `get_frontend_api_binding_lookup(...)`, `get_frontend_api_binding_operation_ids(...)`, `build_frontend_api_rest_index_key(...)`, and `get_frontend_api_rest_operation_ids(...)`.
- Added the canonical `surface.frontend_api.binding_lookup` operation row, payload schema `paradev.sdk.frontend-api.binding-lookup.v1`, and workspace section membership.
- Added CLI `frontend-api --binding-surface ... --binding-key ... --json` output with selector validation and conflict checks.
- Added `binding-surface` and `binding-key` to the SDK-owned CLI surface contract projection.
- Regenerated `docs/user-manual/frontend-api-reference.md` and `apps/desktop/src/generated/frontendApi.ts`.
- Updated English and Chinese frontend API, Python SDK, developer manual, and architecture guidance so clients use the helper instead of raw `contract["index"]["binding"]` indexing.
- Updated desktop summary coverage so `surface.frontend_api.binding_lookup` is part of the maintained generated contract family.

## Verification

- Red SDK gate first: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids -q` failed before implementation because the helper import did not exist.
- Red CLI gate first: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_binding_lookup_json -q` failed before implementation because `--binding-surface` did not exist.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids -q`: passed.
- `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_binding_lookup_json -q`: passed.
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiSummary.test.ts src/data/frontendApiBindingIndex.test.ts`: passed, 8 tests.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file -q`: passed, 5 tests.
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`: passed, 20 tests.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q`: passed, 84 tests.
- `rtk npm --prefix apps/desktop run test:unit`: passed, 16 tests across 5 files.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed, 69 files.
- `rtk bash scripts/flake.bash --ci`: passed after formatting `src/paradev/cli.py` with `rtk bash scripts/flake.bash --black`.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py tests/test_sdk_examples.py -q`: passed, 104 tests after formatting.
- `rtk bash scripts/test.bash`: passed, 505 tests after formatting and progress-note updates.
- `rtk uv build`: passed.
- `rtk git diff --check`: passed.

## Alignment Review Notes

- The 10:44 review's TAL-299 planning-doc gap is already closed in this worktree: `docs/plans/linear.md` lists `TAL-299` and points to the frontend API docs plus branch-reconciliation warning.
- The 10:44 browser source-path contract was addressed before this slice in the same branch; this slice does not touch PIHC3 or browser source loading.
- The 15:45 repo-line warning still applies. This branch remains the TAL-299 frontend API line and should be reconciled with `master` deliberately, not blind-merged.
- PIHC3 migration/status work remains out of scope because another agent owns that line; this commit only changes generic SDK, CLI, frontend API, docs, and tests.

## Review Notes

- The binding lookup payload returns a defensive operation-id list so callers cannot mutate the canonical contract through helper output.
- REST lookup keys are built through `build_frontend_api_rest_index_key(...)` to avoid hard-coded query-string ordering in clients.
- CLI selector conflicts prevent mixing binding reverse lookup with operation, group, workspace, markdown, TypeScript, action, option, normalization, or REST-plan projections.

## Next Work

- Keep adding frontend API rows from the canonical SDK table, then regenerate the TypeScript and Markdown artifacts in the same commit.
- Add frontend-facing API helpers only where they reduce duplicate GUI or adapter logic; keep raw generated contract reads as a last resort for tools that need the whole table.
- Reconcile `codex/scaffold-source-root-selection` with `master` explicitly before merge, as both 2026-06-08 alignment reviews warned.
