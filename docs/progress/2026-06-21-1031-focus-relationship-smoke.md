# Focus Relationship Smoke Progress

Date: 2026-06-21 10:31

Linear: TAL-000

## Done

- Added a source-backed PIHC focus relationship fixture for `FOCUS_C08_THE_RISING_FIRE`.
- Extended the apply-review smoke page so inspector prerequisite/reference/unlock controls mutate the focus document and generate migrated `legacy/<focus>/info.json` drafts.
- Documented the rendered relationship-edit smoke path in the desktop e2e README.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` selected `FOCUS_C08_THE_RISING_FIRE`, added prerequisite `FOCUS_C08_CANTERLOT_MIND`, added reference `FOCUS_C08_PLAN_TWILIGHT`, produced `data-paradev-diagram-apply-relationship-draft="1"`, completed the review/apply gate with `Apply calls: 1`, kept nine 34 x 34 image nodes, and reported no console warnings or errors.

## Risks Or Blockers

- The UI still uses compact inspector forms for relationships; final HOI4-style editing should make connect/reconnect gestures more direct on the canvas.

## Next

- Continue moving relationship editing from smoke coverage toward the normal Tauri project path and keep the focus-tree command lane compact in normal windows.
