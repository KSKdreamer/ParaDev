# 2026-06-29 06:33 - AI Chat Profile Editor

## Scope

- Added SDK-owned editable AI chat profile overrides under `CM_PARADEV`.
- Added `desktop_write_chat_profile(...)` and kept prompt validation/merge behavior in the Python desktop facade.
- Forwarded profile writes through REST, Tauri, and the frontend service without moving profile logic into the GUI.
- Added a Config -> Models editor for the built-in floating chat roles: `chat`, `explain`, `create-module`, and `build`.
- Regenerated frontend/API reference docs for the new `ai.profile.write` operation.

## Validation

- `rtk bash scripts/test.bash` - 1165 passed, 2 warnings.
- `rtk bash scripts/flake.bash --ci` - passed after Black formatting.
- `rtk npm --prefix apps/desktop run test:unit` - 45 files, 591 tests passed.
- `rtk npm --prefix apps/desktop run build` - passed with existing large chunk warnings.
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` - 24 passed.
- `rtk uv run pytest tests/test_architecture.py -k "openapi_seed or desktop_api_table or rest_api_table or frontend_api"` - 38 passed.
- `rtk uv run pytest tests/test_cli.py -k "api_catalog or desktop_api_cli or rest_api_cli or frontend_api"` - 28 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop src/paradev/surfaces/rest.py src/paradev/sdk/frontend_api.py tests/test_desktop_api_selection.py tests/test_architecture.py tests/test_cli.py` - passed.

## PIHC3

- Ran `rtk bash scripts/run.bash --tauri`; the live Tauri dev process loaded `/Users/magolor/Utils/ParaDev-3/projects/PIHC3`.
- Native screenshot confirmed the real project selector showed "The Pony In The High Castle" and PIHC3 module counts.
- Browser DOM smoke on the same dev server confirmed Config -> Models renders Chinese `聊天配置`, `提示词`, four profile textareas, and four save buttons.
- Computer Use could only attach to the packaged bundle because the dev Tauri process has no bundle identifier, so the editor interaction was verified through Playwright rather than native accessibility.
- No PIHC3 files changed.
