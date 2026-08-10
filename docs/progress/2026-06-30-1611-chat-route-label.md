# Chat Route Label Progress

Date: 2026-06-30 16:11

Linear: ongoing usability goal

## Done

- Made the floating AI chat route show gateway, provider, and model instead of the old provider/model-only string.
- Added readable labels for common DeepSeek, OpenAI, and OpenRouter route ids so the chat chrome does not expose raw backend ids in normal flows.
- Localized the route template and empty route fallback in English and Chinese.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/FloatingChatShell.test.tsx src/components/AppShell.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Route labels are still a small frontend label map; future SDK-owned route metadata can replace it when available.

## Next

- Replace the chat role dropdown with the shared compact `SelectField` primitive, or localize the remaining preview-tab tooltip gap.
