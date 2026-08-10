# Generic PDX guided scalar forms

Date: 2026-07-28

## Outcome

ParaDev can now project canonical simple-source `def.txt` files into a bounded
Guided form without adding family-specific desktop code. The generic SDK
projection was proven against representative idea, character, event, and
equipment definitions. It exposes only unambiguous existing scalar
assignments; all structural authoring remains in Code mode.

No source file is written by projection or field editing. A Guided change
produces the complete updated text through the existing draft callback, and
the existing apply transaction remains the only write path.

## Safety and UX contract

- PDX patches carry duplicate-key occurrence paths, exact UTF-16 token spans,
  the reviewed token, scalar kind, and whole-source length.
- The desktop rejects stale source length or token content, malformed or
  overlapping spans, unsafe identifiers, invalid decimal values, and type
  mismatches.
- Only the reviewed token changes; comments, whitespace, CRLF/LF choice, and
  unedited quoting remain intact.
- PDX text and identifier fields buffer locally, commit on blur or Enter, and
  revert on Escape. One multi-character edit causes one bridge reprojection.
- After a committed PDX edit, the previous form is visible but disabled until
  the SDK returns fresh spans. Immediate and deferred bridge responses are both
  covered so the editor cannot misclassify its own draft as stale.
- The projection is capped at 96 controls, 32 sections, and depth 12. Sources
  beyond those limits stay in Code mode.

## Evidence

- Python source-form gate: `23 passed`.
- Scoped Python SDK, REST, desktop backend, and Tauri source-form surfaces:
  `26 passed` (`125 deselected`).
- Focused desktop source-form, bridge, lifecycle, and hydration gate:
  `192 passed`.
- Full desktop Vitest suite: `83` files / `1,375` tests passed.
- Desktop TypeScript and production Vite build: passed.
- Read-only real PIHC3 projection probe:
  - idea: 2 sections / 3 controls;
  - character: 5 sections / 10 controls;
  - event: 10 sections / 14 controls;
  - equipment: 1 section / 5 controls.

No PIHC3 file was modified or compiled for this slice.
