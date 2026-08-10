# AI Source Kind Contract Progress

Date: 2026-06-30 10:32 CST
Linear: active usability goal

## Done

- Moved AI chat profile source-kind labels and profile-kind-to-frontend-context-kind mappings into the Python desktop contract.
- Regenerated the checked-in desktop TypeScript contract so React consumes `PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS` and `PARADEV_DESKTOP_AI_CHAT_PROFILE_SOURCE_KIND_FRONTEND_KINDS`.
- Removed the duplicated `project` -> `workspace` and `selection` -> `source` mapping from the floating chat component.
- Made config-page profile source labels derive from generated source-kind rows instead of a separate TypeScript table.
- Added OpenAPI response schemas for all desktop AI profile routes so REST clients can discover `sourceKindRows[].frontendKinds`.
- Removed stale UI-only `project-index` source-kind translation entries.

## Verification

- Red first: `rtk uv run pytest tests/test_desktop_api_selection.py -q -k "ai_chat_profile_catalog or ai_chat_profiles_describe_managed_roles"` failed because `sourceKindRows` and generated source-kind mappings did not exist.
- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/aiChatProfileText.test.ts` failed because `frontendAiChatContextKindsForProfileKind` did not exist.
- Red first: `rtk uv run pytest tests/test_architecture.py -q -k "openapi_seed_renders_without_runtime_server"` failed because AI profile responses had no `content.application/json.schema`.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed, 710 tests.
- Desktop production build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large-chunk warning.
- Focused Python checks: `rtk uv run pytest tests/test_architecture.py tests/test_desktop_api_selection.py tests/test_cli.py -q -k "ai_chat or openapi_seed_renders_without_runtime_server or rest_api_table_lists_openapi_routes or rest_api_cli"` passed, 21 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop src/paradev/surfaces/rest.py tests/test_desktop_api_selection.py tests/test_architecture.py` passed, 7 files.
- Flake gate: `rtk bash scripts/flake.bash --ci` passed.
- Diff hygiene: `rtk git diff --check` passed.
- Fast repo gate: `rtk bash scripts/test.bash` passed, 1228 tests with 2 warnings.
- Native PIHC3 smoke: `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5204` built and launched the Tauri dev app, then was manually stopped after stable startup.

## Risks Or Blockers

- The native PIHC3 smoke was startup-level only; deeper rendered checks should still exercise the config page and floating chat source toggles inside the actual Tauri window.
- OpenAPI now publishes the profile response schema, but the user manual still only lists the route-level generated REST table.

## Next

- Add a rendered PIHC3/Tauri smoke that opens the AI profile config panel and verifies source toggles are populated from the SDK profile payload.
- Consider generating a small user-manual table from `desktop_chat_profiles()` if the source-kind mapping becomes a user-facing extension point.
