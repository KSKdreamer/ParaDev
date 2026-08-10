# PIHC3 Define Component Import Progress

Date: 2026-06-14 16:37

Linear: TAL-000

## Done

- Added a simple `define_component` family with one path-preserving copy slot for `common/defines/*.lua`.
- Added `scripts/migrate_pihc2_define_components.py` and generated 6 PIHC3 modules under `src/modules/define_component/`.
- Added copy-root excludes and `replace_path` coverage for `common/defines`.
- Updated migration notes and legacy inventory docs for define components.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k define_component`
- `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_define_components.py tests/test_pihc3_migration_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_define_components.py tests/test_pihc3_migration_contracts.py`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-define-component-build.json`
- Build summary: 16,480 modules, 62 collections, 36,212 artifacts, 1,857 diagnostics, 0 errors, `blocked: false`.
- Ownership check: 6 reviewed define paths are `define_component`-owned, 0 copy-owned, 0 missing.

## Risks Or Blockers

- This slice preserves compiled Lua bytes; it does not create editable define-assignment records.
- Define value balance still needs current-version gameplay validation.

## Next

- Continue with another small non-map copy-owned support domain, likely AI root files, country/leader support, unit/equipment support, or scripted-localisation/UI support after separate review.
