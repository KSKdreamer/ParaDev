# 2026-06-30 19:53 - AI profile load errors

## Slice

Made AI chat profile load failures visible in the floating chat and config page, while preserving usable fallback AI roles and source kinds when the backend profile load fails.

## Red

- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "fallback AI chat profiles"` failed because `App.tsx` did not use `fallbackParaDevAiChatProfilesPayload` after profile load failures.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "fallback AI chat profiles"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/configPage/ConfigPage.test.tsx src/components/AppShell.test.tsx src/components/Workspace.test.tsx src/i18n/locales.test.ts src/App.test.ts src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Notes

- Desktop unit suite passed with 757 tests.
- Fast repo gate passed with `1235 passed, 2 warnings`.
- Vite build passed with the existing large-chunk warning.
- PIHC3 Tauri smoke reached `Running target/debug/paradev-desktop`; it still logged `Failed to load ParaDev AI chat profiles. project root contains unsupported characters.` The UI now keeps fallback chat profiles and displays the load error instead of silently emptying profile controls.
- No Python paths changed in this slice, so the heaven-style Python scanner was not applicable.
