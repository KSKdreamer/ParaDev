# AI Profile List Reset REST Planning Progress

Date: 2026-06-29 17:13

Linear: N/A

## Done

- Routed native-web AI profile listing through the SDK-owned frontend REST planner for `ai.profiles`.
- Routed native-web AI profile resets through the SDK-owned frontend REST planner for `ai.profile.reset`.
- Kept the Tauri `paradev_ai_profiles` and `paradev_reset_ai_profile` command paths unchanged.
- Added planner assertions for the `ai.profiles` and `ai.profile.reset` query/body contracts.
- Ran a focused review subagent; it found no issues in this diff.

## Verification

- `rtk npm --prefix apps/desktop test -- --run src/services/paradev.test.ts -t "AI chat profiles through the native web bridge"`
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

- No live Tauri smoke was run for this wrapper-only slice; the Tauri branches were intentionally left unchanged.

## Next

- Use the same generated-planner pattern for the next direct native-web desktop operations outside the AI chat/profile group.
