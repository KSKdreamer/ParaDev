# LLM Test Preset Status Progress

Date: 2026-07-01 04:48

Linear: N/A

## Done

- Made the desktop LLM test status contract treat `preset` as a required normalized field on the frontend.
- Added `preset` to default and error Config LLM status objects so route-test UI state stays preset-aware before and after SDK responses.
- Updated Config Models route summaries and route-test running copy to display preset, gateway, provider, and model together.
- Added full `title` text to the floating chat route label so clipped labels remain inspectable.
- Updated GUI spec and config smoke instructions to check the preset-aware route summary and floating chat label.

## Verification

- `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py -q -k "llm_route"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/components/FloatingChatShell.test.tsx src/services/paradev.test.ts src/App.test.ts src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/test.bash tests/test_architecture.py -q -k "openapi_seed_renders_without_runtime_server or frontend_api_contract_lists_canonical_operations or frontend_api_typescript_renderer_matches_desktop_contract_file"`
- `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_desktop_api_selection.py`
- `rtk bash scripts/sync-env.bash --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47843` reached Vite ready, Cargo finished, and `target/debug/paradev-desktop` started without errors before manual stop.

## Risks Or Blockers

- The backend still returns the requested model, not a materialized HeavenBase preset-resolved model. If HeavenBase later exposes a resolved model in `llm.spec.materialize()`, the SDK route-test payload should surface it explicitly.

## Next

- Continue PIHC3-backed GUI checks around Config Models and AI chat, then consider a dedicated route-result row if users need to compare configured route versus materialized runtime route.
