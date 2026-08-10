# PIHC3 Operation Import

## Scope

- Added `projects/PIHC3/scripts/migrate_pihc2_operations.py` to split the compiled PIHC_dev `common/operations/00_operations.txt` file into individual PIHC3 `operation` modules.
- Regenerated `projects/PIHC3/src/modules/operation` as 18 native modules, each with `meta.yaml`, `def.txt`, `main.loc`, and `legacy/source.yaml`.
- Kept the existing generic `operation` family shape in `paradev.yaml`; no new family-specific build code was needed.
- Loaded vanilla HOI4 localization for operation-owned `name` and `desc` rows, with PIHC_dev replacement localization overriding those rows where present.
- Avoided re-declaring shared risk, outcome, cost, and phase localization keys in operation modules.
- Serialized operation `main.loc` files with `[language]` plus `key=value` rows so values beginning with HOI4 scope macros such as `[From.GetNameDefCap]` do not parse as invalid section headers.
- Updated `projects/PIHC3/docs/migration/39-operations.md` to describe the split import instead of the previous aggregate/starter-only state.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "operation and not resistance"`
  - `3 passed, 24 deselected`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_operations.py --clean`
  - Imported 18 PIHC2 operation modules.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q`
  - `27 passed`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_operations.py tests/test_pihc3_migration_contracts.py`
  - `OK: 2 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- PIHC3 build via `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)`
  - `dry_run: False`
  - `modules: 3237`
  - `collections: 62`
  - `artifacts: 26557`
  - `warnings: 3842`
  - `errors: 0`
  - `blocked: False`

## Notes

- The first PIHC3 build after splitting operations was blocked by section-style `.loc` rows whose values started with `[From...]` scope macros. Operation import now writes source loc files in language-section `key=value` form.
- `rtk bash scripts/test.bash` was run as a broad sanity check and failed outside this migration slice: `tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer` reports that `docs/user-manual/frontend-api-reference.md` does not match the SDK-rendered frontend API reference.
- Remaining non-map aggregate work with visible compiled data is now concentrated in operation phases.
