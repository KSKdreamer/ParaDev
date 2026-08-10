# 2026-06-29 19:38 - AI profile source toggles

## Done

- Made AI chat profile context sources editable from the Models config page.
- Reused the SDK-persisted `sourceKinds` field so the GUI continues to save through the existing profile API.
- Added localized source toggles for Project, Selection, Diagnostics, and Templates.
- Added an explicit localized empty-source state instead of showing the generic pending label.
- Canonicalized source-kind ordering before saving so a toggle cycle does not create noisy profile payloads.

## Verification

- Red check before implementation: `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx` failed on the missing source controls.
- Focused check after review fixes: `rtk npm --prefix apps/desktop run test:unit -- --run src/aiChatProfileText.test.ts src/configPage/ConfigPage.test.tsx` passed with 27 tests.
- Targeted frontend suite: `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/aiChatProfileText.test.ts src/components/FloatingChatShell.test.tsx src/i18n/locales.test.ts src/services/paradev.test.ts` passed with 67 tests.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed. Vite still reports the existing large-chunk warning.
- Whitespace gate: `rtk git diff --check` passed.
- Native smoke: `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5207` reached `target/debug/paradev-desktop`; stopped with Ctrl-C.

## Notes

- Dalton reviewed the slice and found the source-order and empty-source-label issues; both were fixed before this checkpoint.
- Unrelated building-icon work in ParaDev and PIHC3 is still intentionally unstaged.
