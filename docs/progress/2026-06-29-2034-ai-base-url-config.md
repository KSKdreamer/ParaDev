# AI Base URL Config Progress

## Summary

- Added the optional `paradev.ai.base_url` config key to the Python defaults and desktop config facade.
- Routed the value through the SDK-owned desktop LLM test and AI chat APIs, REST endpoints, Tauri commands, native-web bridge, and frontend service wrapper.
- Exposed the field on the Models config page and kept the runtime/materialized URL visible as a separate resolved value.
- Regenerated the frontend API TypeScript contract and user manual reference so `ai.chat` documents the optional `base_url` input.

## Verification

- `rtk bash scripts/test.bash tests/test_desktop_api_selection.py tests/test_native_web_bridge.py tests/test_architecture.py -q -k "desktop_config_defaults_match_package_defaults or desktop_config_value_round_trips_ai_route or desktop_llm_route_uses_configured_base_url or desktop_ai_chat_uses_configured_base_url or native_web_bridge_config_endpoints_are_browser_safe or openapi_seed or frontend_api_contract_exposes_ai_chat or frontend_api_rest_planner"`: 7 passed.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx src/services/paradev.test.ts`: 80 passed.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/data/frontendApi.test.ts src/data/frontendApiBindingIndex.test.ts src/data/frontendApiBridge.test.ts src/data/frontendApiResolvers.test.ts src/data/frontendApiSummary.test.ts`: 27 passed.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml -- --check`: passed.
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`: 20 passed.
- `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml`: passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config.py src/paradev/desktop/local.py src/paradev/surfaces/rest.py src/paradev/sdk/frontend_api.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py tests/test_architecture.py`: passed.
- `rtk zsh -lc 'uv run paradev frontend-api --typescript | diff -u apps/desktop/src/generated/frontendApi.ts -'`: no diff.
- `rtk zsh -lc 'uv run paradev frontend-api --markdown | diff -u docs/user-manual/frontend-api-reference.md -'`: no diff.
- `rtk git diff --check -- <changed files>`: passed.
- Native GUI smoke: `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5194` compiled and launched `target/debug/paradev-desktop` with no terminal-side startup errors before manual stop.

## Notes

- Existing unrelated dirty work remains in `src/paradev/sdk/project.py`, `tests/test_pihc3_migration_contracts.py`, and the PIHC3 building-icon planning/source files. This slice does not stage or modify them.
