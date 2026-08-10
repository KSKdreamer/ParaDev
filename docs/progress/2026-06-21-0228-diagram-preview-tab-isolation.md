# Diagram Preview Tab Isolation Progress

Date: 2026-06-21 02:28

Linear: TAL-000

## Done

- Split workspace preview-tab replacement by tab kind so unpinned focus/technology diagram previews no longer get replaced by normal module previews.
- Kept normal module preview behavior intact: opening another normal module still replaces the unpinned module preview.
- Kept diagram preview behavior scoped: opening another diagram still replaces the existing unpinned diagram preview.
- Kept module and config previews in the same regular preview slot so the new diagram isolation does not change existing non-diagram tab behavior.
- Added a pure tab-state helper so the behavior is tested without relying on browser timing.

## Verification

- Red: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "keeps unpinned diagram previews separate"` failed before the tab-state helper existed.
- Green: same command passed after adding the helper.
- Red: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "keeps module and config previews"` failed while the helper over-separated non-diagram tab kinds.
- Green: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "previews"` passed after narrowing the helper to diagram versus regular preview groups.
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx`.

## Risks Or Blockers

- This is a state-management slice only; it does not redesign the visual diagram option list.

## Next

- Add rendered browser smoke coverage for opening a focus-tree diagram tab from the project panel when the full shell fixture is stable enough to drive through the browser.
