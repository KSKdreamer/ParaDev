# AI Chat SDK Facade Progress

Date: 2026-06-30 10:02 CST
Linear: active usability goal

## Done

- Promoted the desktop AI chat profile/read/write/reset/chat operations into the public `paradev.sdk` facade.
- Classified the promoted AI operations in the generated SDK API table as the `ai-chat` feature under `desktop.local`.
- Kept the existing frontend operation ids (`ai.profiles`, `ai.profile.write`, `ai.profile.reset`, and `ai.chat`) tied to public SDK facade symbols instead of desktop-only implementation symbols.
- Regenerated the SDK API reference and aggregate API catalog reference after the facade grew from 131 to 135 symbols.
- Removed the import cycle exposed by the facade export by making `paradev.desktop` import `desktop_state` from `paradev.sdk.project`.

## Verification

- Red first: `rtk uv run pytest tests/test_architecture.py -q -k "ai_frontend_sdk_bindings_resolve"` failed because `desktop_chat_profiles` was not in `paradev.sdk.__all__`.
- Focused green: `rtk uv run pytest tests/test_architecture.py -q -k "sdk_api_table_lists_facade_exports or ai_frontend_sdk_bindings_resolve_to_public_sdk_facade"` passed, 2 tests.
- Architecture suite: `rtk uv run pytest tests/test_architecture.py -q` passed, 91 tests.
- SDK CLI/selector checks: `rtk uv run pytest tests/test_sdk_api_selection.py tests/test_cli_api_reference_selectors.py tests/test_cli.py -q -k "sdk_api or sdk-api"` passed, 6 tests.
- Broader affected checks: `rtk uv run pytest tests/test_architecture.py tests/test_sdk_api_selection.py tests/test_cli_api_reference_selectors.py tests/test_cli.py -q -k "sdk_api or sdk-api or api_catalog_lists_generated_references"` passed, 8 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk src/paradev/desktop tests/test_architecture.py tests/test_cli.py` passed, 16 files.
- Flake gate: `rtk bash scripts/flake.bash --ci` passed.
- Diff hygiene: `rtk git diff --check` passed.
- Fast repo gate: `rtk bash scripts/test.bash` passed, 1228 tests with 3 warnings.
- Native PIHC3 smoke: `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5203` built and launched the Tauri dev app, then was manually stopped after stable startup.

## Risks Or Blockers

- The native PIHC3 smoke was startup-level only; deeper AI chat interaction checks still need rendered GUI coverage.
- AI operations are now public SDK functions, but dedicated CLI commands for chat/profile operations still need a product decision.

## Next

- Add rendered floating-chat checks that exercise a PIHC3 source context through the Tauri GUI.
- Decide whether AI chat/profile operations should get direct CLI commands or stay exposed through the SDK and desktop frontend APIs.
