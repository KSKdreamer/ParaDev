# 2026-06-30 05:08 - Desktop config key contract

## Summary

- Added public `paradev.desktop.DESKTOP_CONFIG_KEYS` as the SDK-owned allowlist for desktop-exposed `CM_PARADEV` values.
- Derived desktop config defaults from `paradev.config.DEFAULT_CONFIG` instead of manually copying the same values in `desktop.local`.
- Regenerated the desktop API and API catalog references so the new public config key list appears in the SDK facade docs.

## Verification

```bash
rtk bash scripts/test.bash tests/test_desktop_api_selection.py -k "desktop_config_defaults"
rtk bash scripts/test.bash tests/test_architecture.py -k "desktop_api_table_lists_public_desktop_facade"
rtk bash scripts/test.bash tests/test_cli.py -k "desktop_api_cli_outputs or api_catalog_cli_outputs"
rtk bash scripts/test.bash tests/test_architecture.py -k "desktop_api_table_lists_public_desktop_facade or api_catalog_lists_generated_references"
rtk bash scripts/test.bash tests/test_cli_api_rest_mcp_selectors.py -k "api_catalog_tracks_cli_api_rest_mcp_surfaces" tests/test_api_table_contracts.py -k "api_catalog_references_match_generated_manual_pages or api_reference_markdown_matches_renderers"
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py src/paradev/desktop/__init__.py src/paradev/desktop/api.py tests/test_desktop_api_selection.py tests/test_architecture.py
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The new defaults-derivation test failed first because `DESKTOP_CONFIG_KEYS` was not public.
- The standard fast gate passed with `1219 passed, 1 warning`.
- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` successfully.
- Follow-up: the React desktop shell still maintains its own TypeScript config-key map and load list; a later slice should add a generated or audited contract tying that list back to `paradev.desktop.DESKTOP_CONFIG_KEYS`.
