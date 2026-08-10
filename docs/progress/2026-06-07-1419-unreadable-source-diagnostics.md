# Unreadable Source Diagnostics Progress

Date: 2026-06-07 14:19 CST

Linear: TAL-294

## Done

- Added structured `pdx.unreadable_source`, `loc.unreadable_source`, and `copy.unreadable_source` diagnostics for matched files that exist but fail during read.
- Kept module id, collection id, slot, and relative source path context on those diagnostics.
- Added regression tests for PDX, localization, and static copy loader read failures.
- Documented unreadable matched source behavior in `docs/workflows/build-flow.md`.

## Verification

- `rtk uv run pytest tests/test_build_loaders.py::test_pdx_loader_reports_unreadable_source_as_diagnostic tests/test_build_loaders.py::test_copy_loader_reports_unreadable_source_as_diagnostic tests/test_localization_loader.py::test_loc_loader_reports_unreadable_source_as_diagnostic`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py tests/test_build_loaders.py tests/test_localization_loader.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- Python loader smoke confirmed `copy.unreadable_source` from `load_copy_sources`.

## Risks Or Blockers

- Linear sync failed again with `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening first-slot compiler diagnostics and artifact emission ergonomics.
