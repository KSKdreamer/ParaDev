# Desktop Language Metadata Progress

Date: 2026-06-30 07:13

Linear: active goal

## Done

- Reproduced the module editor accessibility mismatch from a native Tauri run: visible UI was Chinese while Computer Use reported stale English names for module-editor structural labels.
- Isolated a source-level accessibility gap: the desktop document still started as `lang="en"` and React never updated the document language when the GUI locale was Chinese.
- Added `htmlLangForLocale(...)` and `applyDocumentLocale(...)`, then applied the selected GUI locale to `document.documentElement.lang`.
- Added `lang` metadata to the app shell plus the module entity list/details regions so localized accessible names carry an explicit language tag in static and runtime renders.
- Added regression coverage for the document language mapping and Chinese module-editor region language tags.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/moduleEditor/ModuleEntityList.test.tsx src/moduleEditor/ModuleEntityDetails.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- Fresh Computer Use snapshots timed out after closing the stale native bundle, so the final native verification for this slice is startup-only rather than a fresh AX tree diff.
- The Vite production build still reports the existing large chunk warning.

## Next

- Re-run a native AX snapshot once Computer Use can read the fresh Tauri window reliably, then continue PIHC3 workflow testing around source editing and create/apply tasks.
