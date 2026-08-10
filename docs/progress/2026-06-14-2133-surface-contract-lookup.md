# Surface Contract Lookup

Date: 2026-06-14 21:33 Asia/Shanghai

## Summary

- Added `paradev.surfaces.get_surface_contract(identifier)` for exact static surface contract lookup.
- Expanded the surface catalog docstring to describe returned payloads and added error-path coverage for unknown identifiers.
- Updated architecture and developer-manual guidance so adapter audits use the catalog helper and focused tools use the exact lookup helper.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/__init__.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/__init__.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/surfaces/__init__.py tests/test_architecture.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries`
- Direct `get_surface_contract(...)` probe for VS Code/OpenAPI lookup and unknown identifier failure.

## Notes

- This is a behavior-preserving public API refinement over the static surface contract catalog.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
- Existing staged frontend API progress note, PIHC3 migration, desktop, skill, logo, frontend generated, and `node_modules` worktree changes were left untouched.
