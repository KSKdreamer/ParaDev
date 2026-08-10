# 2026-06-29 05:26 - AI Chat Profile Catalog

## Scope

- Added SDK-owned desktop AI chat profile catalog via `desktop_chat_profiles()` and `GET /desktop/ai/profiles`.
- Updated Tauri, REST, frontend API metadata, generated TypeScript contracts, and API reference docs for `ai.profiles`.
- Added a floating chat task selector with Chat, Explain HoI4 code, Create module plan, and Build/debug project roles.
- Kept `desktop_chat()` responsible for role validation and prompt composition before LLM calls.

## Validation

- `rtk bash scripts/test.bash` - 1161 passed, 1 warning.
- `rtk bash scripts/flake.bash --ci` - passed.
- `rtk npm --prefix apps/desktop run test:unit` - 45 files, 586 tests passed.
- `rtk npm --prefix apps/desktop run build` - passed with existing large chunk warnings.
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` - 24 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...` - passed.
- Native Tauri smoke with PIHC3 showed the floating chat role dropdown and all four task options.

## PIHC3

- Used `/Users/magolor/Utils/ParaDev-3/projects/PIHC3` for the native GUI smoke.
- No PIHC3 files changed.
