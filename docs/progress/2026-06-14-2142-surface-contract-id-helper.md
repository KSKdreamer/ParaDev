# Surface Contract Id Helper

Date: 2026-06-14 21:42 Asia/Shanghai

## Summary

- Added `paradev.surfaces.get_surface_contract_ids()` as the ordered public identifier list for the static surface contract catalog.
- Kept `get_surface_contracts()` and `get_surface_contract(identifier)` behavior unchanged while giving audits a lighter read-only path when they only need stable ids.
- Updated architecture and developer-manual guidance in English and Chinese.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/__init__.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/__init__.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/surfaces/__init__.py tests/test_architecture.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries`
- Direct `get_surface_contract_ids()` / `get_surface_contract(...)` probe for ordered identifiers and VS Code lookup.

## Notes

- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
- Existing desktop generated-contract changes and `node_modules` were left unstaged.
