# Surface Contract Schema Anchors

Date: 2026-06-14 22:37 Asia/Shanghai

## Summary

- Added `SURFACE_CONTRACT_IDS` and `SURFACE_CONTRACT_SUMMARY_SCHEMA` as fixed SDK anchors for static surface contract table code.
- Tightened the surface summary row/index annotations to use `SurfaceContractIdentifier` literals.
- Updated architecture and developer-manual guidance in English and Chinese.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/__init__.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/__init__.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/surfaces/__init__.py tests/test_architecture.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries`
- Direct probe for `SURFACE_CONTRACT_IDS`, `SURFACE_CONTRACT_SUMMARY_SCHEMA`, `SurfaceContractIdentifier`, and summary index order.

## Notes

- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
- Existing skill, desktop, PIHC3, logo, frontend generated, and `node_modules` worktree changes were left untouched.
