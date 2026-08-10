# AI Chat REST Planning Progress

Date: 2026-06-29 17:02

Linear: N/A

## Done

- Routed native-web AI chat prompts through the SDK-owned frontend REST planner for `ai.chat`.
- Kept the Tauri `paradev_chat` command path unchanged while making browser-debug/native-web execution follow the generated REST request contract.
- Added planner coverage proving `ai.chat` sends provider, model, gateway, prompt, role, project root, and sources in the REST JSON body.
- Ran an alignment audit subagent; the remaining direct AI native-web calls are `ai.profiles` and `ai.profile.reset`.

## Verification

- `rtk npm --prefix apps/desktop test -- --run src/services/paradev.test.ts -t "sends AI chat prompts through the native web bridge"`
- `rtk uv run pytest tests/test_architecture.py -k frontend_api_rest_request_planner_maps_values_to_query_and_body`
- `rtk npm --prefix apps/desktop test -- --run src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_architecture.py`
- `rtk npm --prefix apps/desktop test -- --run`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_architecture.py`
- `rtk git diff --check`
- `rtk bash scripts/test.bash`

## Risks Or Blockers

- `ai.profiles` and `ai.profile.reset` still use direct native-web REST calls and should be the next small SDK-planner alignment slice.

## Next

- Add generated-plan helpers for native-web AI profile list/reset to complete the current AI chat/profile bridge alignment pass.
