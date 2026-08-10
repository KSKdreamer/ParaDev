# Frontend Summary Registry Unit-Test Slice

Date: 2026-06-08 17:39 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `3a72ad80-b588-4f86-9cb7-62f5b6ccb468`, `TAL-295` comment `f4e72846-c742-432b-b458-0eb4cdd25906`

## Summary

This slice tightened the frontend-facing API contract guardrail after the 10:44 and 15:45 alignment reviews called out TAL-299 as the active generic frontend API line. The generated contract already exposes 71 operations across projects, modules, collections, build, PDX, LSP, catalog, and surface contracts; this change adds direct TypeScript coverage proving the desktop helper's exported summary registry, group ids, workspace sections, and derived helper slices stay aligned with the checked-in generated SDK contract.

From a mod developer's perspective, this keeps the workbench navigation and action list stable: project management, module authoring, PDX parsing, LSP diagnostics, build, and catalog actions continue to come from one SDK-owned operation list. From a GUI developer's perspective, this keeps React code on the canonical exported helpers instead of recreating operation counts, workspace sections, or REST/input slices locally.

## Changes

- Added `apps/desktop/src/data/frontendApiSummary.test.ts`.
- Covered generated operation ids, group ids, workspace section ids, status values, summary counts, group counts, read/write counts, and status counts.
- Covered the required frontend-facing families named by the API contract work: project create/find/rename/activate/view, module list/create/edit/view, collection create/edit, build plan/emit, PDX parse/format, LSP diagnostics/hover/formatting, and frontend API meta actions.
- Covered workspace helper alignment through `getFrontendApiSectionActions(...)`, `getFrontendApiSectionOperations(...)`, `getFrontendApiDefaultSectionAction(...)`, and `getFrontendApiOperation(...)`.
- Covered derived `frontendApiInputOperations` and `frontendApiRestOperations` slices against the generated operation rows.
- Updated the UI spec and English/Chinese manuals so the desktop helper unit gate now includes summary/group registry alignment.

## Verification

- Red gate first: `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiSummary.test.ts` failed before implementation because the summary-registry test file was absent.
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiSummary.test.ts`: passed, 4 tests.
- `rtk npm --prefix apps/desktop run test:unit`: passed, 12 tests across 4 files.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed, 69 files.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 42 tests.
- `rtk bash scripts/test.bash`: passed, 502 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=summary-unit-tests`: loaded the ParaDev workbench, found workspace sections and the Run button, and reported 0 browser console errors.

## Review Notes

- This is test and docs coverage only; no generated contract rows or production helper behavior changed.
- The slice directly addresses the TAL-299/frontend API maintenance risk from the alignment reviews by making generated summary/group drift fail in desktop unit tests.
- The work stays generic and does not touch the PIHC3 migration line assigned to another agent.
- Full Python, desktop, package, and browser checks passed after the edit.

## Next Work

- Continue maintaining the frontend API list from `src/paradev/sdk/frontend_api.py` and regenerate the TypeScript/manual artifacts when the SDK contract changes.
- Add more TypeScript helper tests only where they protect user-visible workbench state or prevent GUI-only duplicate registries.
- Keep `codex/scaffold-source-root-selection` reconciled with `master` explicitly before merge, as noted in the 15:45 alignment review.
