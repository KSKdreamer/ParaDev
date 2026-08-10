# Frontend Source Bridge API Rows

Date: 2026-06-08 20:23 CST

Issues: TAL-299, TAL-295

Linear comments: TAL-299 `dc9d477e-6af2-4596-b0dd-a6eb32259451`, TAL-295 `32f3e6fa-e321-4f5c-acc7-5614828038b1`

## Summary

This slice closes the frontend API follow-up from the 2026-06-08 10:44 and 15:45 alignment reviews without taking over the separate PIHC3 migration line.

The first desktop/browser source-edit bridge routes are now canonical frontend API operations instead of undocumented REST-only endpoints:

- `project.source_text` for `GET /projects/{project_id}/sources`
- `module.draft` for `POST /projects/{project_id}/modules/{family_id}/drafts`
- `project.draft_apply` for `POST /projects/{project_id}/drafts/apply`

The public frontend form shape uses the existing project `path` mental model and maps it to the bridge payload key `project_root` where needed. `source_path` maps to the REST query key `path`, so GUI code can work with browser source rows without learning a second route-specific vocabulary. The dynamic option sources for `source_path`, `family_id`, and `template_id` now have a visible `path` input available to satisfy their provider requirements.

The REST request planner now fills path-template parameters such as `{project_id}` and `{family_id}` from normalized submitted values, URL-encoding those path segments and removing them from the planned query/body. GUI clients can ask the SDK for the executable request plan instead of reimplementing route-template substitution.

## Alignment Review Follow-Up

- The 10:44 browser source-path finding was already fixed on this branch before this slice. I rechecked the current code path and ran the focused Python browser test; canonical source rows now carry loadable absolute `path` values and project-relative `relative_path` values.
- The 10:44/15:45 TAL-299 planning gap is already closed on this branch. `docs/plans/linear.md` lists TAL-299, restores the missing `docs/progress/2026-06-07-2345-frontend-api-contract.md` anchor, and records `codex/frontend-api-master-reconcile` as the reconciliation branch.
- The 15:45 branch-reconciliation concern remains operationally real, but the current branch now contains the master-line TAL-299 sync plus the frontend API branch work. PIHC3 status and importer parity remain owned by the PIHC3 migration line.

## Files Changed

- Extended `src/paradev/sdk/frontend_api.py` with the three source-editor bridge rows, path-template filling for REST plans, and field descriptions for the new source/draft payloads.
- Updated `tests/test_architecture.py` to lock the new operation counts, workspace placement, CLI binding, REST binding index, OpenAPI linkage, and REST planner output.
- Regenerated `apps/desktop/src/generated/frontendApi.ts` and `docs/user-manual/frontend-api-reference.md`.
- Updated the English/Chinese frontend API manual, developer manual, and architecture boundary docs so users see the new operations as part of the canonical list.

## Verification

- `rtk python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 86 passed, 3 skipped because `fastapi.testclient` is optional and absent.
- `rtk npm --prefix apps/desktop run test:unit` -> 7 files passed, 31 tests passed.
- `rtk bash scripts/test.bash tests/test_project.py::test_project_browser_returns_frontend_ready_items_without_writing -q` -> 1 passed.
- `rtk uv run paradev frontend-api --operation project.source_text --rest-request --values-json ... --json`
- `rtk uv run paradev frontend-api --operation module.draft --rest-request --values-json ... --json`
- `rtk uv run paradev frontend-api --operation project.draft_apply --rest-request --values-json ... --json`
- `rtk uv run paradev frontend-api --operation module.draft --form --json`
- `rtk uv run paradev frontend-api --operation project.source_text --form --json`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py` -> no banned imports.
- `rtk bash scripts/flake.bash --ci` -> 55 files would be left unchanged.

## Review Notes

- Draft apply is correctly treated as a mutating action with `execution.confirmation.required=true`.
- The route-template filler is intentionally limited to `{name}` placeholders in SDK-owned REST bindings; it raises if a binding references a missing path parameter.
- The new bridge rows use `path` as the user-facing project root input and keep `project_root` as an internal REST payload key. This keeps option-provider requirements and the existing frontend project mental model aligned.

## Residual Risk

- The default environment still skips FastAPI endpoint tests when `fastapi.testclient` is not installed. REST helper and planner coverage passed, but live optional endpoint coverage remains environment-dependent.
- I did not run a Tauri live smoke in this slice. Desktop generated-helper unit tests passed, and the focused Python browser-path test covers the earlier source-row regression.
- I did not mutate TAL-297; PIHC3 status remains a separate migration-line decision.
