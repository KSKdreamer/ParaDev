# 2026-07-01 07:13 - Desktop config metadata

## Summary

Confirmed ParaDev is already aligned to HeavenBase 0.1.1.5: `requirements.txt` pins `heavenbase==0.1.1.5`, the active environment reports `heavenbase` module and distribution version `0.1.1.5`, and the ParaDev-used public route `hb.LLM(model="deepseek-v4-flash", provider="deepseek", gateway="openai")` still materializes. No dependency pin change was needed.

Moved desktop config defaults and choice lists further into the Python SDK contract. `src/paradev/desktop/local.py` now owns `DESKTOP_CONFIG_ROWS`, derives `DESKTOP_CONFIG_KEYS` and defaults from those rows, validates choice/number/boolean/chat-profile values through the row metadata, and emits generated TypeScript config rows/defaults.

The desktop config page now consumes generated SDK metadata for config-backed defaults and select choices instead of duplicating YAML/JSON, Steam/local, AI preset, and DeepSeek default values in React. Local-only GUI preview defaults remain local. Added tests that assert the Config page defaults and rendered choice controls come from the generated contract and that raw metadata is not shown to users.

## Verification

- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py`
- `rtk bash scripts/sync-env.bash --check`
- `rtk uv run pytest tests/test_desktop_api_selection.py::test_desktop_config_rows_define_defaults_and_ordered_choices tests/test_desktop_api_selection.py::test_desktop_typescript_matches_generated_file tests/test_desktop_api_selection.py::test_desktop_typescript_contract_uses_general_renderer_and_artifact -q`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/App.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47847` reached Vite ready, Cargo finished, and `target/debug/paradev-desktop` started without late startup output before manual stop.
