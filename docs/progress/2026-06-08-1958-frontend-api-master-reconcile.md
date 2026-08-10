# Frontend API Master Reconcile

Date: 2026-06-08 19:58 CST

Branch: `codex/frontend-api-master-reconcile`

Reviewed: `docs/progress/2026-06-08-1044-five-hour-alignment-review.md`, `docs/progress/2026-06-08-1545-five-hour-alignment-review.md`

## Summary

This loop addressed the two alignment reviews by reconciling the TAL-299 frontend-facing API line with the current master-line PIHC3/template/manual work while keeping shared ParaDev core generic. The reconciled branch preserves master GUI and PIHC3 progress, keeps PIHC3 migration ownership out of shared SDK assumptions, and fixes the SDK/browser contract that was blocking desktop source loading.

The most important SDK fix is the `Project.browser()` source row contract. Canonical modules, collections, and direct family-root source folders now expose absolute `path` values plus project-relative `relative_path` values, with stable `family_id`, `object_id`, `title`, `layout`, `sources`, `families`, `groups`, and `diagnostics` fields for frontend consumers. `desktop_state(...)` now includes the active project's browser and template payloads so the Tauri/React shell can load one SDK-owned state bundle.

The bridge surface now has the first edit path for the module editor: REST helpers and routes for project-contained source reads, SDK-backed module draft creation, and validated draft apply; CLI `draft-apply`; Tauri commands for desktop state, module draft creation, source text reads, source apply, and path opening; and TypeScript model tests for the canonical browser schema. The Rust tests now create temporary projects instead of depending on an ignored `projects/PIHC3` checkout.

Planning drift from the reviews is also resolved locally. `docs/plans/linear.md` has one continuous stewardship section with `TAL-299`, the missing initial progress anchor exists locally, and the current drift note names `codex/frontend-api-master-reconcile` as the reviewed TAL-299 reconciliation branch. `TAL-297` remains a PIHC3 migration/status issue owned by that line.

## Verification

- `rtk python -m py_compile src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/sdk/project.py`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/surfaces/rest.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/sdk/copy_roots.py src/paradev/sdk/templates.py src/paradev/games/hoi4/__init__.py tests/test_project.py tests/test_architecture.py tests/test_cli.py tests/test_project_build.py`: passed, `OK: 11 file(s) - no banned imports`.
- `rtk bash scripts/flake.bash --ci`: passed after renaming local `field` loop variables in SDK index helpers.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_project.py tests/test_cli.py tests/test_sdk_examples.py -q`: passed, 269 passed and 3 skipped because optional `fastapi.testclient` is not installed.
- `rtk bash scripts/test.bash tests/test_project.py tests/test_cli.py -q`: passed, 204 passed.
- `rtk bash scripts/test.bash -q`: passed, 512 passed and 4 skipped because optional `fastapi.testclient` is not installed.
- `rtk npm --prefix apps/desktop run test:model`: passed, 14 passed.
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`: passed, 8 passed.
- `rtk uv build`: passed, built source distribution and wheel.
- `rtk git diff --check`: passed.
- `rtk rg -n '<<<<<<<|=======|>>>>>>>' README.md README.en.md docs tests src apps/desktop/src apps/desktop/src-tauri/src`: no conflict markers.

## Review

No blocking findings remain from the final diff review. One documentation issue was found during review: `docs/plans/linear.md` had duplicate continuous stewardship sections after the branch reconciliation. It is fixed in this loop, and the file now has one `TAL-295`/`TAL-299` stewardship table plus a current branch drift note.

Residual risks are explicit. The FastAPI endpoint smoke tests are still skipped in this local environment because `fastapi.testclient` is absent, although REST helper coverage runs. I did not mutate Linear issue statuses in this loop. The ignored nested `projects/PIHC3` repository remains separate from this parent ParaDev commit and should continue to be handled by the PIHC3 migration agent.

## Next Work

- Review and merge `codex/frontend-api-master-reconcile` deliberately into `master` after human review.
- Keep `Project.browser()`, REST/Tauri source editing, and desktop module editor payloads stable as the next module families are generalized.
- Continue TAL-299 API maintenance through SDK-owned operation rows and generated bindings, not local React-only action tables.
