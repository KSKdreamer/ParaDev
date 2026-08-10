# AI Chat Source Selection Progress

Date: 2026-06-30 09:47 CST
Linear: active usability goal

## Done

- Preserved manual floating-chat context-source choices across workspace context refreshes.
- Carried selected source kinds to refreshed source ids when the active file or workspace source changes.
- Still auto-select newly available context kinds when the active SDK profile enables them by default.
- Removed the frontend hard-coded AI chat role id list so SDK-provided future profiles can become the default role without being dropped by app/settings normalization.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/components/FloatingChatShell.test.tsx -t "source"` failed because the source-selection policy helper did not exist.
- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx -t "future AI chat roles"` failed because the config page snapped a future SDK role back to `chat`.
- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "merges SDK-backed desktop config values"` failed because SDK-backed default-role reads rejected a future role id.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/components/FloatingChatShell.test.tsx` passed, 13 tests.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx` passed, 40 tests.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts` passed, 44 tests.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed, 709 tests.
- Desktop production build: `rtk npm --prefix apps/desktop run build` passed.
- Fast repo gate: `rtk bash scripts/test.bash` passed, 1227 tests with 2 warnings.
- Diff hygiene: `rtk git diff --check` passed.
- Native PIHC3 smoke: `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5202` launched the Tauri dev app and was manually stopped after stable startup.

## Risks Or Blockers

- The desktop build still reports the existing Vite large-chunk warning.
- The Tauri smoke was startup-level only; deeper rendered interaction checks remain needed.
- An explorer flagged larger AI contract follow-ups: promote or document the desktop AI SDK boundary, decide CLI executable AI commands, centralize source-kind aliases, and surface backend profile-load errors instead of falling back in all cases.

## Next

- Add an SDK/API-table test for AI frontend operation bindings so the `desktop_chat*` API boundary is explicit.
- Centralize AI source-kind alias metadata so Python profiles and React context descriptors cannot drift.
