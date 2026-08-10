# Config Route Label Progress

Date: 2026-06-30 16:39

Linear: ongoing usability goal

## Done

- Shared the AI route label formatter between the floating chat and the Models config page.
- Updated live LLM route test status to show readable gateway/provider/model labels instead of raw ids like `openrouter / deepseek-reasoner`.
- Preserved legacy running-status normalization so stale in-flight status payloads render through the new readable label.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx -t "LLM route test running"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/components/FloatingChatShell.test.tsx src/App.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- This is a desktop UI text normalization only; no SDK, bridge, or LLM routing behavior changed.

## Next

- Use the latest GUI audit findings to improve AI source chip path clarity, source picker consistency, or localization language labels in separate commits.
