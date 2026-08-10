# 2026-06-20 09:56 Facade API selection source alignment

## Summary

- Updated the small facade API selection tests for config, GUI, desktop, games, localization, project, package, and authoring templates to source row counts from the owning public `__all__` export list.
- Replaced direct `Path.read_text()` reference checks with `heavenbase.utils.load_txt()` so generated manual parity tests follow the shared file utility policy.
- Kept the slice test-only and outside PIHC3 migration paths; no API behavior changed.

## Verification

- `rtk uv run pytest tests/test_config_api_selection.py tests/test_gui_api_selection.py tests/test_desktop_api_selection.py tests/test_games_api_selection.py tests/test_localization_api_selection.py tests/test_project_facade_api_selection.py tests/test_package_api_selection.py tests/test_templates_api_selection.py -q`
