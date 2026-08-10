# Surface Contract Catalog

Date: 2026-06-14 21:26 Asia/Shanghai

## Summary

- Added `paradev.surfaces.get_surface_contracts()` as an ordered table of static surface contract payloads.
- Covered bundle, CLI, LSP, MCP, OpenAPI, and VS Code contracts without changing the individual payload builders.
- Updated the architecture boundary docs and developer manual so audits and adapter tooling use one catalog helper instead of importing each contract separately.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/__init__.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/__init__.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/surfaces/__init__.py tests/test_architecture.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries`
- Direct `get_surface_contracts()` probe for catalog keys and OpenAPI/frontend API coverage.

## Notes

- This is a behavior-preserving public surface discoverability helper.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
- Existing PIHC3 migration, desktop, skill, logo, frontend generated, and `node_modules` worktree changes were left untouched.
