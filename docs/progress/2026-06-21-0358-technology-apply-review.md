# Technology Apply Review Progress

Date: 2026-06-21 03:58

Linear: TAL-000

## Done

- Added technology changed-row coverage so moving a PIHC3 technology icon maps to its writable `src/modules/technology/*/meta.yaml` metadata path.
- Changed the diagram apply UX to require review-first for any changed metadata rows, including the common all-writable case from technology moves.
- Added a technology apply-review smoke fixture that uses real PIHC3 `legacy/default.png` icons, moves `TECHNOLOGY_FIREARM_I`, computes the `meta.yaml` draft, and exercises the two-click review/apply flow.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk git diff --check`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-technology-apply-review-smoke.html` reported 2 compact icon nodes, 2 hydrated image nodes, 48 px grid, 34 x 34 px images, no placeholders, no console warnings/errors, review-first after moving `TECHNOLOGY_FIREARM_I`, draft `folder.position` updated to `x: 5`, `y: 2`, and apply count incremented after the second click.

## Risks Or Blockers

- The smoke proves the metadata draft and review path with a mocked Tauri binary-source bridge. The full desktop write path still depends on the normal `applyProjectDraft` backend command, which is covered by existing apply wiring but not invoked by this browser-only fixture.

## Next

- Continue tightening the technology/focus canvas toward bulk PIHC3 editing: dependency edge manipulation, subtree movement affordances for technology-like graphs, and clearer draft text preview inside the app proper.
