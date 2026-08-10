# 2026-06-20 03:40 +0800 - Config API selector helper

## Slice

- Added `get_config_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.config` facade API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.config` and regenerated `docs/user-manual/config-api-reference.md`, increasing the config API row count to 9.
- Added `tests/test_config_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_config_api_selection.py` failed on missing `get_config_api_selection`.
- Green: `rtk uv run pytest -q tests/test_config_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config_api.py src/paradev/config.py tests/test_config_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/config_api.py src/paradev/config.py tests/test_config_api_selection.py` -> clean.

## Notes

- Regenerated the config reference from `render_config_api_reference_markdown()` directly to avoid relying on dirty CLI files.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the config API table module, config facade export, generated config reference, the focused test, and this note.
