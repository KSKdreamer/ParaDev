# 2026-07-01 07:36 - PIHC3 C08 decision titles

## Summary

Cleaned two PIHC3 decision collections that still showed `TODO` as editor-facing metadata and English localization. `DECISION_CATEGORY_C08_WASTELAND_DEVELOP` now uses `Wasteland Development`, and `DECISION_CATEGORY_C08_EAST_ROUTE` now uses `East Route`, with matching English descriptions in `main.loc`.

A read-only asset check found no target-specific `icon.png`, `legacy/icon.png`, `default.png`, `.dds`, `.gfx`, or generated decision asset component for either category id. Nearby C08 decision categories do have migrated category icons, so the image gap remains a good follow-up, but this commit avoids inventing or borrowing artwork without source evidence.

Added a ParaDev regression test so these two PIHC3 categories do not drift back to `TODO` titles.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_c08_decision_categories_replace_todo_editor_titles -q`
- `rtk bash projects/PIHC3/compile.bash --plan-only --json` completed with `blocked: false`, `error_count: 0`, and `diagnostic_count: 0`.
- `rtk bash scripts/flake.bash --ci`
- `rtk git diff --check && rtk git -C projects/PIHC3 diff --check`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47849` reached Vite ready, Cargo finished, and `target/debug/paradev-desktop` started without late startup output before manual stop.
