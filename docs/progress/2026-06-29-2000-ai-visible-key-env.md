# 2026-06-29 20:00 - Visible AI key env routing

## Done

- Made the Models page `paradev.ai.key_env` field affect the immediate LLM route test instead of waiting on persisted `CM_PARADEV` state.
- Made floating AI chat send the same visible key environment value through React, the TypeScript desktop service, Tauri, native-web REST, and the Python desktop facade.
- Kept fallback behavior intact: omitting `key_env` still uses the persisted `paradev.ai.key_env` config value.
- Updated the SDK-owned frontend API contract and regenerated the checked-in TypeScript and user-manual reference artifacts.

## Verification

- Red route test before implementation: `rtk bash scripts/test.bash tests/test_desktop_api_selection.py -q -k explicit_visible_key_env` failed on the missing `desktop_test_llm_route(..., key_env=...)` signature.
- Red chat test before implementation: `rtk bash scripts/test.bash tests/test_desktop_api_selection.py -q -k ai_chat_prefers_explicit_visible_key_env` failed on the missing `desktop_chat(..., key_env=...)` signature.
- Python desktop API: `rtk bash scripts/test.bash tests/test_desktop_api_selection.py -q` passed with 39 tests.
- Frontend targeted suite: `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/services/paradev.test.ts src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts` passed with 81 tests.
- SDK/REST/contract checks: targeted `tests/test_architecture.py` and `tests/test_cli.py` slices passed.
- Generated artifact checks: `frontend-api --typescript`, `--markdown`, and `--sdk-cli-markdown` all matched checked-in files.
- Heaven-style scan passed for changed Python paths.
- Desktop build, Rust check, and `rtk git diff --check` passed.
- Native smoke: `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5209` reached `target/debug/paradev-desktop`; stopped with Ctrl-C.

## Notes

- Godel reviewed the config/AI parity surface and identified the chat key-env gap; this slice includes that fix.
- Vite still reports the existing large-chunk warning.
- Unrelated building-icon work in ParaDev and PIHC3 remains intentionally unstaged.
