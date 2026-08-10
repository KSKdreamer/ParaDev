# PIHC3 Manual Source Policy Cleanup

## Summary

Aligned the PIHC3 user manual with the current minimal project layout and build model.

## Changes

- Replaced stale manual references to a local `copies/` overlay and `extensions/` folder with the current `copy_roots` declaration in `paradev.yaml`.
- Documented the active PIHC3 folder roles for `src/`, `system/`, `scripts/`, `scripts/review/`, and `docs/migration/`.
- Added a PIHC3 migration contract that checks the current project root shape after ignoring local generated/runtime folders.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'manual_source_policy or source_root or generated_runtime_directories'`
- `rtk uv run black --check tests/test_pihc3_migration_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py`
