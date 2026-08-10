# PIHC3 Division Import

Date: 2026-06-14 08:18 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_divisions.py` to import PIHC2 compiled division/OOB outputs.
- Updated the project-local `division` family to use generic path-preserving PDX slots:
  - `history`: `history/units/*.txt`
  - `names`: `common/units/names_divisions/*.txt`
- Regenerated 73 grouped `src/modules/division` modules.
- The native division modules now own 159 `history/units` artifacts and 66 `common/units/names_divisions` artifacts.
- Updated migration docs and copy-overlay exclusions for the division cutover.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'division'` failed on missing division slots and missing importer.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'division'` passed `2 passed, 58 deselected`.
- Full migration contract suite: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q` passed `60 passed in 436.69s`.
- Formatting/style: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_divisions.py tests/test_pihc3_migration_contracts.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_divisions.py tests/test_pihc3_migration_contracts.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_divisions.py --clean` imported 73 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 11,840 modules, 62 collections, 36,147 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 225 division-owned artifacts and 0 diagnostics on `history/units` or `common/units/names_divisions` paths.

## Notes

- `projects/PIHC3/scripts/build.py` still imports the obsolete `paradev.mod` wrapper. The supported build path is the `paradev build` CLI or `Project.load(...).build(...)`; this slice did not change the stale wrapper.
- The importer preserves compiled PIHC_dev PDX. Reconstructing editable fielded OOB templates, country setup helpers, and structured air/naval/stockpile authoring remains future work.
