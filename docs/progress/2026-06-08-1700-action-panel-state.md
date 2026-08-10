# Action Panel-State Helper Slice

Date: 2026-06-08 17:00 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `ee3be11a-1346-48d6-ae0a-c117153ae72e`, `TAL-295` comment `065e9e5f-0e15-4d6a-b6e4-8c49baa6a047`

## Summary

This slice addressed the frontend API follow-up from the 2026-06-08 10:44 and 15:45 alignment reviews by continuing the TAL-299 branch rather than mixing PIHC3 migration work into ParaDev core. The branch now keeps selected-action panel composition behind a single desktop helper, so React panels can consume one stable view model instead of rebuilding defaults, controls, option requests, REST requests, confirmation state, and Run state locally.

From a HoI4 mod developer's perspective, this keeps the visible model small: choose an SDK action, fill the generated fields, confirm only when required, and run the planned operation. From a ParaDev developer's perspective, the generalizable surface is `getFrontendApiActionPanelState(...)`, backed by SDK-owned operation metadata and reusable helper projections.

## Changes

- Added `FrontendApiActionPanelStateInput`, `FrontendApiActionPanelState`, and `getFrontendApiActionPanelState(...)` to `apps/desktop/src/data/frontendApi.ts`.
- Updated `Workspace.tsx` to derive the selected action detail, fields, controls, option requests, normalize/REST-plan requests, confirmation state, Run state, stable request keys, and default counts from the panel-state helper.
- Extended `tests/test_architecture.py` so Workspace assertions require the panel-state boundary while helper tests still cover the individual lower-level projections.
- Updated `docs/architecture/interfaces.md`, `docs/techstack/ui/gui-spec.md`, and the English/Chinese user-manual pages with the selected-action panel-state helper contract.

## Verification

- Red test first: `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_selected_action_panel_state -q` failed before implementation because the panel-state helper types were absent.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_selected_action_panel_state -q`: passed, 1 test.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 42 tests.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_cli.py tests/test_project.py -q`: passed, 199 tests.
- `rtk bash scripts/test.bash`: passed, 502 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=action-panel-state`: loaded the ParaDev workbench, found the Run panel and Run button, and reported 0 browser console errors.

## Review Notes

- The 10:44 source-path and Linear TAL-299 sync risks have already been handled on this branch before this slice; `docs/plans/linear.md` now lists TAL-299 and warns about branch reconciliation.
- The 15:45 branch-divergence warning remains valid. This branch is reviewable and pushed as its own line; it should still be reconciled deliberately with `master`.
- PIHC3 parity/status work remains out of scope for this branch because another agent owns that migration line. This slice keeps ParaDev core generic and frontend-facing.

## Next Work

- Continue moving desktop selected-action panel logic toward SDK-owned operation metadata and helper projections.
- Add TypeScript unit coverage for `getFrontendApiActionPanelState(...)` when the desktop package has a stable helper-test command beyond production build/model checks.
- Keep `docs/user-manual/frontend-api.md` and `docs/user-manual/frontend-api-reference.md` maintained as the canonical frontend API list grows across project, module, PDX, LSP, REST, MCP, VS Code, and desktop surfaces.
