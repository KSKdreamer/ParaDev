# 2026-06-29 05:50 - AI Chat Source Context

## Scope

- Added optional `sources` descriptors to SDK-owned `desktop_chat(...)`.
- Kept source path validation, text reads, truncation metadata, and prompt source-context assembly inside the Python desktop facade.
- Forwarded `sources` through REST, Tauri, and `chatWithParaDevAi(...)` without GUI-side file reads.
- Added floating chat context checkboxes derived from the active workspace tab or selected source path.
- Updated generated frontend API contracts and user-manual references for `ai.chat` inputs.

## Validation

- `rtk bash scripts/test.bash` - 1163 passed, 1 warning.
- `rtk bash scripts/flake.bash --ci` - passed.
- `rtk npm --prefix apps/desktop run test:unit` - 45 files, 588 tests passed.
- `rtk npm --prefix apps/desktop run build` - passed with existing large chunk warnings.
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml` - 24 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...` - passed.
- Native Tauri smoke with PIHC3 opened the `国家` module and showed the floating chat context row with `国家` attached.

## PIHC3

- Used `/Users/magolor/Utils/ParaDev-3/projects/PIHC3` for the native GUI smoke.
- Screenshots: `/tmp/paradev-tauri-ai-sources-open.png`, `/tmp/paradev-tauri-ai-sources-context.png`.
- No PIHC3 files changed.
