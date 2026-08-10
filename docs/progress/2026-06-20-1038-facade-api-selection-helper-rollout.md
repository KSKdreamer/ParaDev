# 2026-06-20 10:38 Facade API selection helper rollout

## Summary

- Migrated config, GUI, desktop, games, and project facade API selection tests to the shared selector-contract helper.
- Preserved each facade test's row-count, index inventory, selection-helper metadata, and generated-reference assertions.
- Kept behavior unchanged; this is a test-maintainability slice for the documented API table surfaces.

## Verification

- `rtk bash scripts/flake.bash --all --paths tests/test_config_api_selection.py tests/test_gui_api_selection.py tests/test_desktop_api_selection.py tests/test_games_api_selection.py tests/test_project_facade_api_selection.py`
- `rtk uv run pytest tests/test_config_api_selection.py tests/test_gui_api_selection.py tests/test_desktop_api_selection.py tests/test_games_api_selection.py tests/test_project_facade_api_selection.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_config_api_selection.py tests/test_gui_api_selection.py tests/test_desktop_api_selection.py tests/test_games_api_selection.py tests/test_project_facade_api_selection.py`
- `rtk git diff --check`
