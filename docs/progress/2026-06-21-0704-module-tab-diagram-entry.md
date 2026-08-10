# Module Tab Diagram Entry Progress

Date: 2026-06-21 07:04

Linear: TAL-000

## Done

- Added a compact `Open <module> diagram` action above normal focus/technology module tabs.
- Wired the action to the existing dedicated diagram tab path, so opening a focus tree diagram keeps the normal module tab open.
- Updated the diagram-tab smoke instructions to cover the normal-module entry point as well as the separate Diagrams section.

## Verification

- `rtk npm run test:unit -- src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- Browser QA on `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: clicking `National Focuses`, then `Open National Focuses diagram`, produced open tabs `focuses,diagram:focuses`, selected kind `diagram`, 2 focus images, and 0 placeholders.
- `rtk npm run build`

## Risks Or Blockers

- Vite still reports the existing large-chunk warning.
- The full PIHC3 normal-app focus tree still needs broader interaction QA beyond the smoke fixture.

## Next

- Continue tightening the normal PIHC3 focus-tree workflow around source-backed edits, image hydration, and apply review.
