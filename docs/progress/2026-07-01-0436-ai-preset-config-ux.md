# AI Preset Config UX Progress

Date: 2026-07-01 04:36

Linear: N/A

## Done

- Made the Config Models page preset-first: `paradev.ai.preset` is the primary route control, while `paradev.ai.model`, `paradev.ai.provider`, and `paradev.ai.gateway` are grouped as advanced route overrides.
- Added visible preset plus effective-route copy so a preset/model mismatch is explicit for modders.
- Added AI-specific config helper text and kept shared build/CLI helper text off the Models tab.
- Added preset-aware floating AI chat route labels without changing the flat SDK/API route contract.
- Updated the config smoke README to exercise `paradev.ai.preset` as the primary LLM setting.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/components/FloatingChatShell.test.tsx src/components/AppShell.test.tsx src/App.test.ts src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/sync-env.bash --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47842` reached Vite ready, Cargo finished, and `target/debug/paradev-desktop` started without errors before manual stop.

## Risks Or Blockers

- The backend LLM test status payload still does not carry `preset`, so persisted test-result fallback copy remains gateway/provider/model-based unless the status schema is extended.

## Next

- Continue with rendered PIHC3 GUI checks around Config Models and the floating chat panel, then decide whether the LLM test status payload should include preset for complete route observability.
