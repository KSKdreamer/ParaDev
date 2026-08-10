# 2026-06-29 07:09 - AI Chat Profile Reset

## Slice

- Added SDK-owned AI chat profile reset so GUI and REST delete a profile override instead of rewriting defaults.
- Exposed the reset path through Python desktop API, REST, generated frontend operation contracts, Tauri command, and TypeScript service wrapper.
- Added Config > Models reset buttons for each editable chat profile with English and Chinese strings.

## Validation

- `rtk uv run pytest tests/test_desktop_api_selection.py -k "chat_profile or config_rest_routes"`
- `rtk uv run pytest tests/test_architecture.py -k "desktop_api_table or openapi_seed or rest_api_table or frontend_api or api_catalog"`
- `rtk uv run pytest tests/test_cli.py -k "api_catalog or desktop_api_cli or rest_api_cli or frontend_api"`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop src/paradev/surfaces/rest.py src/paradev/sdk/frontend_api.py tests/test_desktop_api_selection.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash`

## GUI Smoke

- Launched `rtk bash scripts/run.bash --tauri`; the native Tauri window loaded the real PIHC3 project (`The Pony In The High Castle`) with populated module counts.
- Native accessibility did not expose a useful webview tree, so the interaction smoke used the same running dev build in the browser DOM to verify the localized Models page and profile reset controls.
- Captured the Models page with `重置` and `保存` actions visible in the chat profile editor.
