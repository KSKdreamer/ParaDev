# AI Chat Profile Contract Progress

Date: 2026-06-30 08:22

Linear: active goal

## Done

- Exported the SDK-owned AI chat source-kind order and built-in profile catalog through `render_desktop_typescript()`.
- Regenerated `apps/desktop/src/generated/desktopContract.ts` from `rtk uv run paradev desktop-api --typescript`.
- Removed the hand-maintained TypeScript fallback profile prompt copy from the desktop service and projected fallback profiles from the generated Python-owned catalog instead.
- Pointed the desktop AI chat profile helper at the generated source-kind order so config-page source toggles share the SDK-owned order.

## Verification

- Red first: `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_typescript_contract_exports_ai_chat_profile_catalog -q` failed on the missing generated AI chat catalog exports.
- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts -t "keeps SDK-compatible AI chat role options when the Tauri profile bridge is unavailable"` failed on the stale short TypeScript fallback prompt.
- `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py::test_desktop_typescript_contract_exports_ai_chat_profile_catalog -q`
- `rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts -t "keeps SDK-compatible AI chat role options when the Tauri profile bridge is unavailable"`
- `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py -q -k "desktop_typescript_contract or desktop_chat_profile or ai_chat_profile"`
- `rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts src/aiChatProfileText.test.ts src/openPathTargets.test.ts`
- `rtk bash scripts/test.bash --serial tests/test_cli.py::test_desktop_api_cli_outputs_typescript_config_keys -q`
- `rtk bash scripts/test.bash --serial tests/test_desktop_api_selection.py -q -k "desktop_typescript_contract or desktop_typescript_matches_generated_file"`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- The desktop build still reports the existing large chunk warning.
- The standard fast test gate reported two existing warnings.

## Next

- Follow up on the GUI-translation audit: add prompt translation keys for built-in AI profiles and a localized unknown source-kind fallback instead of showing raw internal ids.
