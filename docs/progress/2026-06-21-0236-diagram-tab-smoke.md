# Diagram Tab Smoke Progress

Date: 2026-06-21 02:36

Linear: TAL-000

## Done

- Added a rendered `AppShell` smoke fixture for the separate Diagrams section in the project panel.
- The fixture opens `National Focuses` as a normal module tab, then opens `National Focuses diagram` as a separate diagram tab.
- Exposed HTML dataset markers for open tab ids, active tab id, selected tab kind, module tab count, and diagram tab count.
- Documented the smoke flow in the desktop e2e README.

## Verification

- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html` loaded without console warnings.
- Browser interaction: after clicking `National Focuses`, the dataset reported `openTabs=focuses` and `selectedKind=module`.
- Browser interaction: after clicking `National Focuses diagram`, the dataset reported `openTabs=focuses,diagram:focuses`, `selectedKind=diagram`, one module tab, one diagram tab, two focus nodes, and two focus icon images.
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx`.
- `rtk npm --prefix apps/desktop run build`.
- `git diff --check`.

## Risks Or Blockers

- This smoke uses a compact fixture payload and verifies shell routing; larger PIHC3 source-backed focus tree rendering remains covered by the dedicated diagram source-backed smoke.

## Next

- Continue polishing the focus-tree editing controls and apply path now that the shell has rendered coverage for separate module and diagram tabs.
