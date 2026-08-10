# AI Key Env Route

## Slice

- Made the desktop SDK AI route honor `paradev.ai.key_env` instead of deriving the key source only from the provider name.
- Passed the selected environment secret into `heavenbase.LLM(..., api_key=...)` for both route testing and floating chat.
- Kept frontend request contracts unchanged: the GUI persists the key env through `CM_PARADEV`, while chat/test requests continue sending provider, model, and gateway.

## Verification

- Red first:
  - `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_llm_route_uses_configured_key_env tests/test_desktop_api_selection.py::test_desktop_ai_chat_uses_configured_key_env -q`
- Green checks:
  - `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_llm_route_uses_configured_key_env tests/test_desktop_api_selection.py::test_desktop_ai_chat_uses_configured_key_env -q`
  - `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py -q`
  - `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py`
  - `rtk bash scripts/flake.bash --ci`
  - `rtk bash scripts/test.bash`

## Notes

- No Tauri smoke was run for this commit because the visible GUI control already existed; this slice changed only the SDK/backend route behavior behind that control.
- PIHC3 worktree stayed clean.
