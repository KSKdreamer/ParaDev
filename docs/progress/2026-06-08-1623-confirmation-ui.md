# Confirmation UI Acceptance Slice

Date: 2026-06-08 16:23 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `ee7aca95-ae01-4082-856e-cc2e8bb5c4b7`, `TAL-295` comment `f0505599-5af6-4ed0-9608-c586457059e7`

## Summary

This slice addressed the next frontend-facing API gap from the 10:44 and 15:45 alignment reviews after the confirmation policy metadata landed: the desktop shell now has a first-class acceptance control for SDK-owned `execution.confirmation` policy instead of permanently disabling Run for mutating actions.

## Changes

- Added `FrontendApiActionConfirmationStates` and `isFrontendApiActionConfirmationSatisfied(...)` to `apps/desktop/src/data/frontendApi.ts` so confirmation acceptance has a canonical TypeScript helper shape.
- Updated `apps/desktop/src/components/Workspace.tsx` to store operation-keyed confirmation acceptance, render the SDK confirmation title/summary/scope/style/fields, enable Run only after the selected action's confirmation is accepted, and reset accepted state when submitted action values change.
- Added `.confirmation-control` styles for the confirmation checkbox state without introducing a new policy surface in component code.
- Extended architecture tests so future desktop work keeps helper-owned confirmation state, Workspace gating, and visible confirmation UI wired together.
- Updated the architecture docs, GUI spec, frontend API manual, developer manual, and SDK Python manual in English and Chinese.

## Verification

- Red test first: focused architecture tests failed before the helper/UI implementation because the confirmation state helper and Workspace acceptance state were missing.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_workspace_actions tests/test_architecture.py::test_desktop_workspace_executes_ready_rest_plan_through_helper -q`: passed, 2 tests.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 41 tests.
- `rtk bash scripts/test.bash tests/test_cli.py tests/test_project.py -q`: passed, 199 tests.
- `rtk bash scripts/test.bash`: passed, 501 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=confirmation-ui`: loaded the desktop shell with 0 browser console errors.

## Review Notes

The implementation keeps the user's mental model minimal: mutating actions expose one visible confirmation checkbox whose text comes from the SDK contract, and Run remains disabled until the checkbox is accepted. Developer-facing policy remains general: SDK metadata decides whether confirmation is required; the frontend helper only records local acceptance and evaluates the policy. This keeps the path usable for project/module/catalog actions without encoding PIHC-specific or one-off destructive rules in React.

## Next Work

- Continue reducing duplicated frontend execution policy in components by routing more UI state through `apps/desktop/src/data/frontendApi.ts`.
- Add higher-level desktop interaction tests once the shell has a stable browser automation harness for clicking generated forms and Run controls.
- Keep `docs/plans/linear.md`, `docs/user-manual/`, and `docs/architecture/interfaces.md` synchronized whenever new frontend operation families or execution surfaces are added.
