# 2026-06-30 05:27 - Desktop config key TypeScript contract

## Summary

- Added `paradev.desktop.render_desktop_config_keys_typescript()` and `paradev desktop-api --typescript` as the public regeneration path for the desktop GUI config-key tuple.
- Replaced the React boot-time config read list with the generated SDK-owned `PARADEV_DESKTOP_CONFIG_KEYS` tuple.
- Added contract coverage so the checked-in TypeScript file, named React config map, CLI API table, desktop API docs, and API catalog stay aligned.

## Verification

```bash
rtk bash scripts/test.bash tests/test_cli.py -k "desktop_api_cli_outputs or cli_api_cli_outputs_table_json or frontend_api_cli_outputs_typescript_contract or api_catalog_cli_outputs"
rtk bash scripts/test.bash tests/test_architecture.py -k "cli_api_table_lists_command_contract or desktop_api_table_lists_public_desktop_facade or api_catalog_lists_generated_references or frontend_api_typescript_renderer"
rtk bash scripts/test.bash tests/test_desktop_api_selection.py -k "desktop_config_keys_typescript"
rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "named desktop config map"
rtk npm --prefix apps/desktop run test:unit
rtk npm --prefix apps/desktop run build
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/desktop/local.py src/paradev/desktop/__init__.py src/paradev/desktop/api.py src/paradev/surfaces/cli.py tests/test_cli.py tests/test_architecture.py tests/test_desktop_api_selection.py
rtk git diff --check
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The desktop config-key TypeScript artifact is now regenerated with `rtk uv run paradev desktop-api --typescript`.
- The full Python gate passed with `1221 passed, 1 warning`.
- The desktop unit suite passed with `682 passed`; the production build passed with the existing large-chunk warning.
- The PIHC3 Tauri smoke reached the Vite-ready and `target/debug/paradev-desktop` running state, then was stopped with Ctrl-C after a quiet startup window.
- Follow-up: `apps/desktop/src/buildPage/BuildPage.tsx` and `apps/desktop/src/buildPage/buildPageModel.ts` still hard-code HOI4 config keys separately from the generated desktop config-key tuple.
