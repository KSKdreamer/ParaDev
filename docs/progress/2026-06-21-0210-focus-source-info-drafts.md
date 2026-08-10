# Focus Source Info Drafts Progress

Date: 2026-06-21 02:10

Linear: TAL-000

## Done

- Carried migrated `source_focuses[*].source_path` into focus diagram node payloads as `sourceFocusPath`.
- Added source-backed metadata drafts for migrated focus `legacy/<source_path>/info.json` files when the GUI can read the source text.
- Kept module `meta.yaml` summary writes as the immediate-refresh fallback while also writing the original PIHC source JSON for position, legacy offsets, parent, and layout hints.
- Wired diagram apply in the desktop editor to read changed legacy source info files before building source edits.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx`.
- `rtk npm --prefix apps/desktop run build`.
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: focus preview PNGs rendered as visible SVG images, no console warnings/errors, zoom control changed state and reset to 100%.

## Risks Or Blockers

- Source JSON drafts intentionally cover the layout fields needed by the current focus-tree editor, not every possible HOI4 focus relationship shape.
- If a migrated `info.json` file is missing or unreadable, the GUI falls back to the existing `meta.yaml` summary edit instead of blocking apply.

## Next

- Extend source JSON draft coverage to dependency/reference edits after the editor interaction model for relationship editing settles.
