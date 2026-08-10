# Boot Progress Animation Progress

Date: 2026-06-21 01:35

Linear: TAL-000

## Done

- Added an active animated flow to the desktop boot progress track so long SDK/project loads do not look stalled when the numeric progress value is stable.
- Added a Vite-rendered `boot-progress-smoke.html` fixture that mounts the real `AppShell` in a PIHC3 project-loading state.
- Documented the boot progress smoke route and expected checks in the desktop e2e fixture README.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/services/nativeProgress.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/boot-progress-smoke.html`: expected page title, PIHC3 loading detail, `aria-busy="true"`, inert shell surfaces, `animation-name: boot-progress-track-flow`, and no console warnings/errors.

## Risks Or Blockers

- This improves visible async progress in the existing shell. It does not change backend startup duration or add per-step SDK progress events.

## Next

- Continue with larger focus-tree usability and PIHC3 cleanup slices.
