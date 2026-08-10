# Action Run-State Helper Slice

Date: 2026-06-08 16:39 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `a8c0fb5e-87eb-4d68-984d-51fa19158f63`, `TAL-295` comment `aa6503cc-0ef3-474b-846c-c120e559e9be`

## Summary

This slice continued the frontend API stabilization line by moving selected-action Run readiness and result text out of `Workspace.tsx` and into the canonical desktop helper. The SDK still owns `execution.confirmation`; React owns local state; `apps/desktop/src/data/frontendApi.ts` now owns the reusable interpretation of disabled/detail/status state for Run controls.

## Changes

- Added `FrontendApiActionRunState` and `getFrontendApiActionRunState(...)` to the desktop frontend API helper.
- Updated `Workspace.tsx` to render Run `disabled`, `detail`, and `status` from the helper while keeping request construction and fetch resolution on the existing helper path.
- Extended architecture tests so future desktop panels keep confirmation, loading, REST-plan readiness, and REST result text centralized in the helper.
- Updated `docs/architecture/interfaces.md`, `docs/techstack/ui/gui-spec.md`, and English/Chinese user manuals with the new helper contract.

## Verification

- Red test first: focused architecture tests failed before implementation because `FrontendApiActionRunState`, `getFrontendApiActionRunState(...)`, and Workspace consumption were missing.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_workspace_actions tests/test_architecture.py::test_desktop_workspace_executes_ready_rest_plan_through_helper -q`: passed, 2 tests.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 41 tests.
- `rtk bash scripts/test.bash tests/test_cli.py tests/test_project.py -q`: passed, 199 tests.
- `rtk bash scripts/test.bash`: passed, 501 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=action-run-state`: loaded the desktop shell with 0 browser console errors.

## Review Notes

From the mod developer's perspective, this preserves a minimal model: a Run button is either disabled with a useful reason or available after the selected action is planned and confirmed. From the GUI developer's perspective, the generalizable surface is now one helper call that consumes operation id, confirmation policy, REST-plan state, REST-execution state, and the local confirmation map.

## Next Work

- Continue moving selected-action panel derivations from React into `apps/desktop/src/data/frontendApi.ts`.
- Add direct TypeScript unit tests for the helper once the desktop package has a stable test command beyond build/model checks.
- Keep extending the frontend API list only through SDK-owned operation rows and helper projections.
