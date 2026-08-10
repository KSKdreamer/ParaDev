# AI Source Kind Rows UI Progress

Date: 2026-06-30 11:53 CST
Linear: active usability goal

## Done

- Threaded SDK `sourceKindRows` from the desktop AI profile payload through `App`, `AppShell`, `Workspace`, `ConfigPage`, and `FloatingChatShell`.
- Made the config AI profile source toggles derive their available kinds and labels from SDK-owned rows when present, including runtime rows outside the generated default contract.
- Made the floating chat source-selection defaults use each SDK row's `frontendKinds`, so new profile source kinds can map to frontend context sources without component-local tables.
- Kept generated desktop contract rows as the fallback for empty or unavailable runtime payloads.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx src/components/FloatingChatShell.test.tsx` failed because runtime source-kind rows were dropped by the UI flow.
- Focused GUI checks: `rtk npm --prefix apps/desktop run test:unit -- src/aiChatProfileText.test.ts src/configPage/ConfigPage.test.tsx src/components/FloatingChatShell.test.tsx` passed, 63 tests.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed, 716 tests.
- Desktop production build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large-chunk warning.
- Native PIHC3 smoke: `rtk bash -lc 'PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5194 ...'` reached Vite, built `paradev-desktop`, launched the app, and was stopped after stable startup without runtime error markers.

## Risks Or Blockers

- The Tauri smoke is still startup-level; the next rendered check should navigate to the config models page and inspect source toggles in the actual native window.
- Runtime rows with only `frontendKinds` and no `label` still fall back to their raw SDK id for labels.

## Next

- Add a deeper native GUI smoke for AI profile config and floating-chat source toggles against `projects/PIHC3`.
- Continue replacing GUI-held AI assumptions with Python SDK contract data.
