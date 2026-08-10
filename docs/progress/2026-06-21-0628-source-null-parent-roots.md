# Source Null Parent Roots Progress

Date: 2026-06-21 06:28

Linear: TAL-000

## Done

- Updated the project-diagram adapter so source-backed focus records with explicit `parent: null` stay root nodes instead of falling back to prerequisite-derived tree parents.
- Kept dependency edges intact for those roots, so prerequisites still render as requirements without changing the canonical tree hierarchy.
- Added a C08-style regression test covering an explicit-root focus that still has a prerequisite in compiled focus metadata.

## Verification

- Red check first: `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/projectDiagram.test.ts -t "explicit null parent"'`
- `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/projectDiagram.test.ts -t "explicit null parent"'`
- `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts'`
- `rtk bash -lc 'cd apps/desktop && npm run build'`

## Risks Or Blockers

- The adapter still uses prerequisite fallback when no explicit parent/root information exists. That fallback remains useful for older focus metadata but should stay subordinate to source-backed layout records.
- The Vite build continues to report the existing large-chunk warning.

## Next

- Browser-check PIHC3 C08 source-backed focus trees to verify explicit roots and dependency edges read correctly in the rendered canvas.
