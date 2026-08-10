# AI preset route passthrough

## Summary

- Adapted the desktop AI route to HeavenBase 0.1.1.5's public `LLM(preset=...)` argument.
- Added `preset` to `desktop_test_llm_route(...)` and `desktop_chat(...)`, including SDK payloads, REST/native-web routing, Tauri request structs, and desktop TypeScript service requests.
- Wired `configPageSettings.llm.preset` into route testing and the floating chat send path so the Config page value affects the active AI route.
- Updated frontend API metadata plus generated TypeScript and user-manual references for `ai.chat`.
- Cleaned the PR checklist in `CONTRIBUTING.md` to use the current `rtk bash scripts/sync-env.bash --check` command and no legacy HeavenBase override flag.

## Verification

- Red first:
  - `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py -q -k "configured_preset or explicit_preset"` failed on the missing payload/signature.
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/services/paradev.test.ts -t "HeavenBase LLM routes|AI chat prompts through the Tauri|AI chat prompts through the native"` failed because request bodies dropped `preset`.
- Focused checks:
  - `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py tests/test_architecture.py tests/test_native_web_bridge.py -q -k "configured_preset or explicit_preset or rest_routes_forward_dependency_and_llm_requests or openapi_seed_renders_without_runtime_server or frontend_api_contract_lists_canonical_operations or frontend_api_rest_request_planner_maps_values_to_query_and_body or frontend_api_typescript_renderer_matches_desktop_contract_file or frontend_api_reference_manual_matches_sdk_renderer or native_web_bridge_config_endpoints_are_browser_safe"` passed.
  - `rtk npm --prefix apps/desktop run test:unit -- --run src/services/paradev.test.ts src/App.test.ts src/data/frontendApiSummary.test.ts` passed, 96 tests.
  - `rtk cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` passed.
  - `rtk npm --prefix apps/desktop run build` passed with the pre-existing Vite chunk-size warning.
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py src/paradev/surfaces/rest.py src/paradev/sdk/frontend_api.py tests/test_desktop_api_selection.py tests/test_architecture.py` passed.
  - `rtk bash scripts/sync-env.bash --check` passed.
  - `rtk bash scripts/flake.bash --ci` passed.
  - `rtk bash scripts/test.bash` passed: 1237 passed, 289 warnings.
- Native GUI smoke:
  - `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47841` reached `target/debug/paradev-desktop` with PIHC3 selected and showed no startup errors during the smoke window.

## Follow-ups

- The preset now reaches HeavenBase, but the GUI still exposes provider/model/gateway as explicit overrides. A later UX slice should make the interaction clearer for modders, likely by separating "preset" from "advanced route overrides" visually.
