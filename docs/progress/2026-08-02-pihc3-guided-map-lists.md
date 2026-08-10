# PIHC3 Guided Map Lists

This checkpoint makes the most common State and Strategic Region membership
edits available without raw PDX editing while preserving the extension-owned
architecture.

## Outcome

- The generic PDX guided-form contract now supports a Registry-declared
  `integer-list` control beside exact scalar controls. The projector accepts
  only pure anonymous integer blocks and emits an exact UTF-16 interior span,
  expected text, row width, minimum value, and whitespace layout.
- Planning and apply reparse the current source, reject stale spans, comments,
  mixed syntax, unsafe numbers, incomplete rows, and overlapping patches, and
  validate the final document as PDX before returning a full-text draft.
- The desktop validates the same closed patch operation, buffers multiline
  edits until blur or Command/Ctrl+Enter, and leaves the SDK planner
  write-authoritative. No State or Strategic Region branch exists in React,
  Rust, the generic SDK projector, REST, or MCP.
- PIHC3's project-local State extension declares `provinces` as one positive
  integer per row and `victory_points` as one province/score pair per row.
  Strategic Region declares its positive province list through the same
  extension hint contract.
- The live source audit covered all 902 States and 330 Strategic Regions:
  15,142 State province ids, 1,820 State victory-point integers, and 17,988
  Strategic Region province ids projected with zero failures.
- Doctrine's shared localization copy slot now declares its authoring path,
  keeping the visible-family authoring-capability contract complete without
  changing emitted artifacts.

## Rendered desktop proof

A fresh unsigned debug `ParaDev.app` from this checkout reopened the cleaned
PIHC3 project with hidden extension descriptors. The stale extension-layout
error came from another worktree's already-running app, not the current
backend. The tested artifact is
`apps/desktop/src-tauri/target/debug/bundle/macos/ParaDev.app`. In the rebuilt
native app:

- States loaded 902 objects and 1,804 source files;
- State 199 showed Guided Province and Victory-point text areas with its live
  values;
- Strategic Regions loaded 330 objects and 660 source files; and
- Strategic Region 106 showed its Guided Province text area with its live
  values.

The smoke made no project-source edits.

## Verification

- Focused Python/SDK/MCP/PIHC3 tests: 69 passed.
- Closing guided-map/Doctrine regression set: 108 passed.
- Standard Python gate: 2,370 passed and 9 native-Windows-only skips.
- Focused desktop guided-form/client tests: 194 passed.
- Full desktop gate: 89 files and 1,458 tests passed.
- TypeScript and Vite production build passed; the existing large-chunk
  warning remains.
- State module 199 and Strategic Region module 106 partial builds each
  completed with one selected module, 9,298 artifacts, and zero diagnostics or
  errors.
- Doctrine module `DOCTRINE_AIR_0_0_OPEN_SKY` also completed with one selected
  module, 9,298 artifacts, and zero diagnostics or errors after the authoring
  slot repair.
- The exhaustive source-form audit projected all 1,232 live State/Strategic
  Region `def.txt` files with zero failures.
- The canonical PIHC3 tree currently has 14,665 direct source-unit folders,
  zero malformed `id - preferred title` names, zero `_component`,
  `_asset_component`, `legacy`, or `inactive_modules` folders, one intentional
  visible module `meta.yaml`, and 847 generated hidden grouping descriptors.
- Targeted Black/flake, the core Heaven-style scan, and `git diff --check`
  passed. The style scanner still reports the existing project-extension
  `pathlib.Path` imports in State and Strategic Region as HeavenBase utility
  advisories; this slice did not replace working extension path handling.
