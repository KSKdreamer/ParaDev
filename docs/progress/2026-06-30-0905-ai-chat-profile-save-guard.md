# AI Chat Profile Save Guard Progress

Date: 2026-06-30 09:05 CST
Linear: active usability goal

## Done

- Disabled AI chat profile Save buttons when the draft would produce an empty SDK write payload.
- Added `hasAiChatProfileDraftChanges(...)` so the UI and tests share the same normalized save-draft comparison used by profile persistence.
- Preserved localized built-in profile labels, details, and prompts as display-only defaults unless the user actually changes them.
- Fixed CLI API-reference projection checks so `--markdown` and generated TypeScript output are not rejected merely because `paradev.cli.output` is configured as `json`.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/aiChatProfileText.test.ts -t "detects whether a profile draft would change the SDK payload"` failed because `hasAiChatProfileDraftChanges` was missing.
- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx -t "disables AI chat profile saves when the draft has no SDK changes"` failed because the Save button was still enabled.
- Red first: `rtk uv run pytest tests/test_cli.py -q -k "pdx_api_markdown_ignores_configured_json_default"` failed because configured JSON output caused `pdx-api --markdown` to reject.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/aiChatProfileText.test.ts` passed, 6 tests.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx` passed, 39 tests.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed, 702 tests.
- Desktop production build: `rtk npm --prefix apps/desktop run build` passed.
- CLI targeted regression: `rtk uv run pytest tests/test_cli.py -q -k "pdx_api_markdown_ignores_configured_json_default or pdx_api_cli_rejects_markdown_json_combo or pdx_api_cli_outputs_reference_markdown or pdx_core_api_cli_outputs_reference_markdown or lsp_api_cli_outputs_reference_markdown or lsp_server_api_cli_outputs_reference_markdown or catalog_api_cli_outputs_reference_markdown or hb_api_cli_outputs_reference_markdown or rest_api_cli_outputs_reference_markdown"` passed, 9 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/cli.py tests/test_cli.py` passed.
- Flake: `rtk bash scripts/flake.bash --ci` passed.
- Fast repo gate: `rtk bash scripts/test.bash` passed, 1227 tests with 1 warning.
- Diff hygiene: `rtk git diff --check` passed.
- Native PIHC3 smoke: `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5198` launched the Tauri dev app and was manually stopped after stable startup.

## Risks Or Blockers

- The desktop build still reports the existing Vite large-chunk warning.
- The Tauri smoke was startup-level only; deeper rendered interaction checks remain needed.

## Next

- Fix the read-only explorer finding that the default Project AI chat profile can attach no project context from config or empty workspace views.
- Add a focused test for `aiChatSourcesForWorkspace(null, null, browser, t, templates)` to include a project-level `workspace` source before templates and diagnostics.
