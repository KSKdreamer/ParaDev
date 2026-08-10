# 2026-06-29 07:27 - AI Chat Diagnostics Context

## Slice

- Added compact project diagnostics as a selectable floating AI chat context source.
- Kept diagnostics source routing SDK-owned by allowing metadata source `content` through `desktop_chat(...)`.
- Added stable chat source selectors so future GUI smoke tests can target diagnostics without relying on source order.

## Validation

- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/components/FloatingChatShell.test.tsx src/services/paradev.test.ts`
- `rtk uv run pytest tests/test_desktop_api_selection.py -k "metadata_source_content or project_source_context or chat_profiles"`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk uv run pytest tests/test_desktop_api_selection.py -k "desktop_ai_chat"`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py`
- `rtk bash scripts/test.bash`

## GUI Smoke

- Launched `rtk bash scripts/run.bash --tauri`.
- Verified the native Tauri window loaded the real PIHC3 project (`The Pony In The High Castle`) with populated module counts.
