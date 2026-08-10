# LLM Route Detail Progress

Date: 2026-06-30 15:42

Linear: TAL-000

## Done

- Replaced the desktop LLM empty-response diagnostic detail with a route-derived `provider / model` label instead of the old DeepSeek v4 Flash literal.
- Tightened the Python desktop facade test to exercise an OpenRouter/DeepSeek Reasoner route and assert the exact route-specific empty-response detail.
- Updated desktop frontend service and config-page fixtures so tests no longer preserve the old hard-coded backend sentence.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_desktop_api_selection.py -q` failed on `test_desktop_llm_route_reports_route_specific_empty_response` because the backend still emitted `DeepSeek v4 Flash route returned an empty response.`
- Targeted Python green: `rtk bash scripts/test.bash tests/test_desktop_api_selection.py -q`
- Targeted desktop green: `rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts src/configPage/ConfigPage.test.tsx`
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- Literal cleanup check: `rtk rg -n "DeepSeek v4 Flash route returned an empty response" src tests apps/desktop/src docs`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 1433`

## Risks Or Blockers

- The GUI still masks backend empty-response details in normal localized flows, which is intentional; the route-derived detail remains available for SDK/REST/Tauri diagnostics.

## Next

- Continue GUI usability work from the config and AI chat surfaces, prioritizing modder-facing copy and interaction clarity.
