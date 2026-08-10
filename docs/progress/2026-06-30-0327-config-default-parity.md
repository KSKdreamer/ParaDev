# Config Default Parity

Date: 2026-06-30

## Summary

Aligned the root Python config facade with the newly exposed AI chat default
role. `DEFAULT_CONFIG` now contains `paradev.ai.chat.default_role`, and merged
`config_get` / `config_list` reads fill packaged defaults when a key is missing
from the active stored layer.

## Changes

- Added the nested default `DEFAULT_CONFIG["paradev"]["ai"]["chat"]["default_role"]`.
- Updated the public config facade so `merged=True` consistently exposes
  package defaults for missing keys and config-list rows.
- Tightened tests so desktop-exposed config defaults must match package
  defaults, including the AI chat default role.

## Verification

```bash
rtk bash scripts/test.bash --serial tests/test_config_api_selection.py tests/test_desktop_api_selection.py::test_desktop_config_defaults_match_package_defaults tests/test_desktop_api_selection.py::test_desktop_ai_chat_default_role_is_sdk_configured -q
rtk bash scripts/test.bash --serial tests/test_cli.py::test_config_list_accepts_local_json_option tests/test_cli.py::test_config_get_serializes_scalar_json_option -q
rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config.py tests/test_config_api_selection.py tests/test_desktop_api_selection.py
rtk npm --prefix apps/desktop run test:unit
rtk npm --prefix apps/desktop run build
rtk bash scripts/flake.bash --ci
rtk git diff --check
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

The Tauri smoke reached the dev server and launched the native
`paradev-desktop` binary against `projects/PIHC3`; no additional runtime errors
appeared before shutdown.
